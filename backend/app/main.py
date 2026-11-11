from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import os
import logging
from dotenv import load_dotenv
from google import genai
import re

from app.retrieval import search_documents

load_dotenv()

app = FastAPI(
    title="BiztelAI Manufacturing Copilot",
    description="AI-powered Manufacturing SOP Assistant",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://192.168.1.5:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SearchRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)
    top_k: int = Field(default=4, ge=1, le=10)


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)
    top_k: int = Field(default=8, ge=1, le=10)


@app.get("/")
def home():
    return {
        "message": "BiztelAI Manufacturing Copilot is running!"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/search")
def search(request: SearchRequest):
    try:
        matches = search_documents(request.question, top_k=request.top_k)
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Document search is temporarily unavailable. Check that ingestion has completed."
        )

    return {
        "question": request.question,
        "matches": matches,
        "count": len(matches)
    }


@app.post("/ask")
def ask(request: AskRequest):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=503, detail="Gemini API key is not configured.")

    try:
        matches = search_documents(request.question, top_k=request.top_k)
        # Prefer the latest revision for each SOP document. Older revisions
        # may contain conflicting procedures and must not override the current SOP.
        latest_revision_by_document = {}
        for match in matches:
            document_number = match.get("document_number") or match["source"]
            revision = match.get("revision", 0)
            latest_revision_by_document[document_number] = max(
                latest_revision_by_document.get(document_number, revision),
                revision,
            )

        matches = [
            match for match in matches
            if match.get("revision", 0)
            == latest_revision_by_document.get(
                match.get("document_number") or match["source"]
            )
        ]

        if not matches:
            return {
                "question": request.question,
                "answer": "I couldn't find sufficient information in the provided SOP documents.",
                "sources": []
            }

        context_parts = []
        source_by_id = {}

        for index, match in enumerate(matches, start=1):
            source_id = f"S{index}"
            source_by_id[source_id] = {
                "document": match["source"],
                "page": match["page"],
                "revision": match["revision"]
            }
            context_parts.append(
                f"[{source_id}] Source: {match['source']} | "
                f"Page: {match['page']} | Revision: {match['revision']}\n"
                f"Content: {match['text']}"
            )

        prompt = f'''You are a careful manufacturing SOP assistant. Answer the user's question using only the supplied document excerpts. Treat the excerpts as the sole source of truth.

Rules:
- Do not use outside knowledge or guess.
- If the excerpts do not clearly contain enough information to answer, say exactly: "I couldn't find sufficient information in the provided SOP documents."
- For machine alarm questions, always include:
  1. The alarm meaning.
  2. Every documented operator action, in the correct order.
  3. The documented machine status after the action, if available.
- Never omit important procedural steps from the supplied excerpts.
- For lockout/tagout lock-removal questions, carefully check the full retrieved procedure and include the complete absent-owner exception in its documented order: the Shift Supervisor attempts to contact the lock owner; if the owner cannot be reached, both the Production Manager and Safety Officer must authorise the removal; include the required machine inspection step wherever it appears in the excerpts.
- Do not treat authorisation alone as completion of the lock-removal procedure; include all documented checks and actions before stating that removal is complete.
- For incoming material inspection or dimensional-tolerance questions, include every relevant field present in the excerpts: component identifier, nominal dimension, tolerance (including units and ± notation), measuring instrument, and inspection classification or severity. Do not omit a field just because the question asks only about tolerance or the instrument.
- Do not invent document names, page numbers, revisions, limits, or procedures.
- Do not claim a machine is safe to operate unless the excerpts explicitly say so.
- Cite every factual statement using the source ID(s) that support it, in square brackets, for example [S2].
- Only cite source IDs that are present in the supplied excerpts.
- Do not add a separate bibliography; source IDs are used by the application to display source details.

DOCUMENT EXCERPTS:
{chr(10).join(context_parts)}

USER QUESTION: {request.question}

ANSWER:'''

        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt
        )
        answer = (response.text or "").strip()
        logging.info("Gemini raw answer: %r", answer)
        logging.info("Retrieved source IDs: %s", list(source_by_id.keys()))
        if not answer:
            raise RuntimeError("Gemini returned an empty response.")

        abstention = "I couldn't find sufficient information in the provided SOP documents."
        if abstention in answer:
            return {
                "question": request.question,
                "answer": abstention,
                "sources": []
            }

        cited_ids = set(re.findall(r"\[(S\d+)\]", answer))
        valid_cited_ids = [
            source_id for source_id in source_by_id
            if source_id in cited_ids
        ]

        # If Gemini gives an answer without valid source citations, fail closed.
        if not valid_cited_ids:
            return {
                "question": request.question,
                "answer": abstention,
                "sources": []
            }

        cited_sources = []
        seen_sources = set()
        for source_id in valid_cited_ids:
            source = source_by_id[source_id]
            source_key = (
                source["document"],
                source["page"],
                source["revision"]
            )
            if source_key not in seen_sources:
                seen_sources.add(source_key)
                cited_sources.append(source)

        return {
            "question": request.question,
            "answer": answer,
            "sources": cited_sources
        }

    except HTTPException:
        raise
    except Exception as exc:
        logging.exception("Copilot /ask request failed")
        error_text = str(exc).lower()

        if any(marker in error_text for marker in (
            "resource_exhausted",
            "quota exceeded",
            "rate limit",
            "429",
        )):
            raise HTTPException(
                status_code=503,
                detail=(
                    "The AI service has reached its Gemini API quota. "
                    "Please wait for the quota to reset and try again."
                ),
            ) from exc

        if "unavailable" in error_text or "503" in error_text:
            raise HTTPException(
                status_code=503,
                detail="The AI service is temporarily unavailable. Please try again shortly.",
            ) from exc

        raise HTTPException(
            status_code=500,
            detail="The copilot could not generate an answer. Check the backend terminal for details.",
        ) from exc
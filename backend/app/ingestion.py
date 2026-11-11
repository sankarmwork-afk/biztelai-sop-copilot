import pymupdf as fitz
import re
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

from pathlib import Path


DOCUMENTS_DIR = Path(__file__).parent.parent / "documents"
CHROMA_DIR = Path(__file__).parent.parent / "chroma_db"
COLLECTION_NAME = "manufacturing_sops"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


def store_chunks(chunks):
    """Generate embeddings and persist document chunks in ChromaDB."""
    if not chunks:
        raise ValueError("No PDF text chunks were extracted. Check the documents folder.")

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    embedding_function = SentenceTransformerEmbeddingFunction(
        model_name=EMBEDDING_MODEL
    )

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_function,
        metadata={"description": "Manufacturing SOP and maintenance manual chunks"}
    )

    ids = []
    documents = []
    metadatas = []

    for chunk_index, chunk in enumerate(chunks):
        metadata = chunk["metadata"]
        chunk_id = (
            f"{metadata['source']}"
            f"-page-{metadata['page']}"
            f"-chunk-{chunk_index}"
        )

        ids.append(chunk_id)
        documents.append(chunk["text"])
        metadatas.append(metadata)

    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )

    return collection.count()


def extract_pdf_text(pdf_path):
    document = fitz.open(pdf_path)
    pages = []

    for page_number, page in enumerate(document, start=1):
        text = page.get_text("text")
        if text.strip():
            pages.append({"text": text, "page": page_number})

    document.close()
    return pages


def get_document_metadata(pdf_path):
    filename = pdf_path.name

    doc_match = re.search(
        r"([A-Z]+-SOP-\d+|[A-Z]+-MAN-[A-Z]+-\d+)",
        filename
    )

    # Prefer the revision printed inside the PDF; fall back to the filename.
    revision_match = None
    with fitz.open(pdf_path) as document:
        if len(document) > 0:
            first_page_text = document[0].get_text("text")
            revision_match = re.search(
                r"\bRev(?:ision)?\s*0*(\d+)\b",
                first_page_text,
                re.IGNORECASE
            )

    if not revision_match:
        revision_match = re.search(r"Rev\s*0*(\d+)", filename, re.IGNORECASE)

    if not revision_match:
        raise ValueError(
            f"Could not determine the document revision from the PDF or filename: {filename}"
        )

    return {
        "source": filename,
        "document_number": doc_match.group(1) if doc_match else "UNKNOWN",
        "revision": int(revision_match.group(1)),
    }


def chunk_text(text, chunk_size=1000, overlap=150):
    paragraphs = text.split("\n")
    chunks = []
    current_chunk = ""

    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue

        if len(current_chunk) + len(paragraph) > chunk_size:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = current_chunk[-overlap:] + " " + paragraph
        else:
            current_chunk += " " + paragraph

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks


def ingest_documents():
    all_chunks = []

    print(f"Looking for PDF files in: {DOCUMENTS_DIR.resolve()}")
    pdf_files = sorted(DOCUMENTS_DIR.glob("*.pdf"))

    if not pdf_files:
        raise FileNotFoundError(
            f"No PDF files found in {DOCUMENTS_DIR.resolve()}. "
            "Copy the four BiztelAI sample PDFs into backend/documents/."
        )

    for pdf_path in pdf_files:
        print(f"Processing: {pdf_path.name}")
        pages = extract_pdf_text(pdf_path)
        metadata = get_document_metadata(pdf_path)

        for page_data in pages:
            chunks = chunk_text(page_data["text"])
            for chunk in chunks:
                all_chunks.append({
                    "text": chunk,
                    "metadata": {
                        **metadata,
                        "page": page_data["page"],
                    },
                })

    return all_chunks


if __name__ == "__main__":
    chunks = ingest_documents()

    print("\nPDF extraction completed!")
    print(f"Extracted chunks: {len(chunks)}")

    total_stored = store_chunks(chunks)

    print("ChromaDB storage completed!")
    print(f"Total chunks in collection: {total_stored}")

    for chunk in chunks[:3]:
        print("\n--------------------")
        print("Metadata:", chunk["metadata"])
        print("Text:", chunk["text"][:200])
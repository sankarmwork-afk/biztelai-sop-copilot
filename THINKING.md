# THINKING.md — Manufacturing SOP AI Copilot

## 1. Understand the user

### Primary user

I assume the primary user is a shop-floor supervisor working in a manufacturing plant. The supervisor may oversee operators, coordinate production during a shift, respond to machine or quality issues, and make sure that work follows the plant's approved procedures. They may be using a shared workstation, tablet, or phone while moving around the production area rather than sitting at a desk.

This is an assumption for the assignment, not something I validated through an interview with a real supervisor. I do not have manufacturing-floor experience, so I used the scenario and the supplied SOP examples to form an initial understanding.

### What the supervisor is trying to do

The supervisor needs to find a reliable instruction quickly while production is running. Examples include checking what a machine alarm means, confirming a maintenance step, checking an inspection tolerance, or finding a safety procedure. They need to know not only the answer, but also which approved document and revision supports it so they can verify the instruction or pass it to an operator.

### What may frustrate them today

I assume the current process may involve opening several PDFs, searching for a code or phrase, scrolling through long documents, or asking a more experienced colleague. This can take time, especially when the supervisor is under pressure or using a phone. Another risk is finding an old document or an outdated revision. A further frustration is not knowing whether a search result actually answers the question.

These are hypotheses to validate with real supervisors. I would not assume that every plant uses the same document-control process or that every supervisor has permission to act on every procedure.

## 2. User journey — initial draft

This is my initial, assumption-based journey for the assignment. The assignment asked me to write this first draft before asking AI to challenge it. I did not conduct user interviews, so the journey describes my own initial thinking rather than observed user behaviour.

1. **A problem occurs during a shift.** An operator reports a machine alarm, an inspection result is unclear, or the supervisor needs to check a safety or maintenance instruction.
2. **The supervisor opens the copilot.** They use a phone or tablet and type a question in everyday language, for example, “What should I do if alarm AL-104 appears?”
3. **The copilot searches the plant documents.** It retrieves relevant passages from the supplied SOP PDFs rather than relying only on the language model's general knowledge.
4. **The supervisor reads the answer.** The answer should be short and actionable, and show the source document, revision, and page so the supervisor can check the original instruction.
5. **The supervisor verifies important instructions.** If the issue involves safety, machine isolation, quality disposition, or an action requiring authorisation, the supervisor checks the controlled procedure and follows the plant's approval process rather than treating the AI response as permission to act.
6. **The supervisor asks a follow-up question if needed.** They may ask for a particular alarm, component, or inspection requirement.
7. **If the documents do not contain the answer, the copilot says so.** It should not invent a temperature, tolerance, maintenance step, or safety instruction. The supervisor then consults the approved document owner, maintenance, quality, or safety team.

### What could go wrong

- The question may be vague or use a machine nickname or alarm code that is not in the documents.
- PDF extraction or chunking may miss a table, diagram, warning, or important sentence.
- Retrieval may return a similar but incorrect procedure.
- Two revisions may contain conflicting instructions, and the older one may be retrieved.
- The model may add details that are not present in the retrieved passages.
- A citation may point to the wrong page or fail to support the answer.
- The system may abstain even though the answer exists, or answer when the evidence is insufficient.
- Wi-Fi, the phone, the backend, or the hosted model API may be unavailable during a shift.
- A supervisor may interpret an answer as authorisation to perform work that requires a qualified person or a formal approval.

For these reasons, I treated source visibility and abstention as core behaviours, not optional interface features.

## 3. AI challenge — critique and reflection

### Skeptical critique

I asked AI to challenge the proposed journey from the perspective of a skeptical shop-floor user and product reviewer. The key challenge was that a quick answer is not automatically a safe or useful answer in a manufacturing setting.

Key points from that critique:

> “How does the supervisor know the answer is from the current approved SOP rather than an obsolete revision?”

> “What happens if the PDF contains a table, warning, or diagram that text extraction does not capture correctly?”

> “Could an operator mistake an AI-generated instruction for permission to bypass a safety or authorisation step?”

> “What should happen when the retrieved passages are relevant but do not actually answer the question?”

These are concise paraphrased excerpts of the critique, not a verbatim transcript. The discussion highlighted that the journey needed to include verification, revision awareness, clear abstention, and a fallback to the responsible human team.

### What I agreed with

I agreed that the current approved revision matters as much as semantic relevance. A search result can look relevant and still be unsafe if it comes from a superseded document. I also agreed that the answer must show its evidence and that the application should not imply that it replaces a supervisor's judgement, an authorised safety role, or a controlled plant procedure.

### What I disagreed with or treated as out of scope

For this time-limited assignment, I did not try to build a complete plant document-control platform, role-based approval workflow, audit trail, or production-grade safety system. Those would need customer requirements, integration with the plant's existing document-management system, and security review. I treated them as important future requirements rather than pretending they were solved by this prototype.

### What I changed after the critique

I made source document, revision, and page information visible in the answer flow; retained a clear abstention response when the supplied documents do not support an answer; and added latest-revision preference in the `/ask` path. I also included phone access in the test journey because the scenario describes supervisors working away from a desk.

## 4. The improvement I added and why I chose it

### Revision-aware retrieval for answers

The most meaningful improvement I added was preferring the latest retrieved revision for a document number when preparing context for `/ask`.

I found a concrete issue while testing the incoming-material-inspection question. The search results included both Revision 03 and Revision 04 of `QC-SOP-014`. The older revision referred to paper form QF-07 and a two-year retention period, while Revision 04 superseded it and specified digital form QF-07A in the QMS app with a five-year retention period. Mixing both revisions could confuse the language model or lead to an outdated answer.

I checked retrieval separately using `/search`, identified the revision conflict, and added a latest-revision preference to the `/ask` path. I then retested the question and verified that the frontend returned the Revision 04 answer and citation.

I chose this improvement because it addresses a realistic risk in the scenario: a supervisor needs the current instruction, not merely a semantically similar passage. This is a prototype-level rule. A real deployment should use authoritative document-control metadata, approval status, effective dates, and the plant's rules for superseded documents rather than assuming that the numerically highest revision is always valid.

## 5. Development challenges and how I handled them

### Python environment and server startup

I initially ran the backend with the wrong Python interpreter, which meant the process could not find ChromaDB even though it was installed in the project's virtual environment. I activated the backend virtual environment and checked that the correct interpreter was being used. I also corrected the Uvicorn import path to `app.main:app`.

I encountered a port 8000 address-in-use error because an earlier Uvicorn process was still running. I inspected the process using `lsof -i :8000`, stopped the relevant old backend process, and restarted the server.

### Gemini quota and model availability

The original Gemini model request hit the free-tier daily request limit and returned a `RESOURCE_EXHAUSTED` error. I checked the model usage and quota information in Google AI Studio and changed the configured model to `gemini-3.5-flash-lite`, which worked during subsequent tests. This taught me to distinguish a model-provider quota problem from a failure in my own retrieval code.

### Retrieval and revision conflict

The incoming-inspection form question initially abstained even though the answer was present in the supplied documents. I tested `/search` independently from `/ask` and found that both Revision 03 and Revision 04 were being retrieved. After adding the latest-revision preference in the answer path, I retested the question and confirmed that the answer used Revision 04.

### Mobile access

I ran the backend and frontend so they could accept connections on the local network, checked the Mac's LAN IP, and opened the frontend from a phone on the same Wi-Fi. I had to ensure that the frontend API address and FastAPI CORS configuration used the current LAN IP. This helped me understand that a page loading on a phone does not by itself prove that the phone can reach the backend API.

## 6. Testing and verification

I tested the five official sample questions supplied for the assignment:

1. TX-200 coolant concentration.
2. Meaning and action for alarm AL-104.
3. Lockout lock removal when the owner is absent.
4. BH-220 outer diameter tolerance and measurement method.
5. Spindle runout frequency, responsible person, instrument, and limit.

I also tested five questions of my own:

1. Repeated AL-210 chuck-clamp alarm.
2. AL-305 spindle overload.
3. Hydraulic pressure remaining below 3.5 MPa.
4. Incoming inspection form and record-retention period.
5. TX-200 hydraulic oil operating temperature, which is not specified in the supplied SOPs.

The supported questions returned answers with source references during testing. The incoming-inspection question exposed the revision conflict and passed after the revision-aware change. The unsupported hydraulic-oil temperature question correctly returned the application's insufficient-information response. I also separately tested an unsupported air-compressor operating-temperature question and confirmed that the application abstained.

I tested the application from a phone on the same local Wi-Fi network. This verified local-network access for the demonstration; it is not a public deployment.

## 7. Final reflection

The biggest challenge was not connecting a language model. It was making sure that the model received the right evidence. The incoming-inspection question showed me that semantic retrieval can return relevant but conflicting content from different revisions. Testing `/search` separately from `/ask` helped me isolate the issue, and the revision-aware change improved the answer for that case.

I also learned that the whole RAG pipeline matters: PDF extraction, chunking, embeddings, retrieval, context selection, generation, citations, and abstention. A polished chat interface cannot compensate for poor evidence selection. External model quotas and local-network configuration are also practical reliability concerns.

### What I would build next

- Connect to a real document-management system and use its approved/current status, effective dates, and revision metadata.
- Add automated evaluation for retrieval relevance, citation correctness, revision conflicts, and abstention.
- Improve extraction and indexing of tables, diagrams, scanned PDFs, and warning boxes.
- Add authentication, role-based access, audit logs, and secure deployment suitable for a plant environment.
- Provide a clear way to escalate unanswered questions to the responsible maintenance, quality, or safety contact.
- Test usability with actual supervisors and operators in realistic shift conditions.

### What I am unsure about

I do not yet know how a particular plant approves and distributes SOP revisions, whether supervisors can access every procedure, how often documents change, or what connectivity is available across the shop floor. I also have not validated whether the answer format is short enough to use during a busy shift or whether the citations are easy to open on a phone.

### Questions I would ask the customer

1. Where are the official SOPs stored, and how do you identify the currently approved revision?
2. Who is allowed to view, use, or act on each type of procedure?
3. What should the copilot do when a document is missing, outdated, unclear, or conflicts with another document?
4. Do supervisors need offline access or must the system work in areas with weak Wi-Fi?
5. Which languages, devices, and accessibility requirements should be supported on the shop floor?
6. Should unanswered questions be routed to a supervisor, maintenance engineer, quality engineer, or safety officer?
7. What level of logging, auditability, and security is required before the system can be used in production?

### How I used AI assistance

I used AI assistance to understand errors, explore debugging steps, critique the user journey, and help reason about retrieval and revision handling. I checked suggestions against terminal output, API responses, retrieved passages, the supplied PDFs, and the running application. I did not treat an AI suggestion as proof that a change worked; I retested the relevant question in the app. The implementation and tests were carried out in my project environment, while AI was used as a support tool.

This project helped me see that an enterprise AI copilot must be designed around the user's actual task, the trustworthiness of its sources, and the consequences of a wrong answer—not just the ability to generate fluent text.

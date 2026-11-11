# Manufacturing SOP AI Copilot

A retrieval-augmented question-answering application for manufacturing Standard Operating Procedures (SOPs). Users can ask questions in a chat interface and receive answers grounded in the supplied PDF documents, with document, revision, and page references. When the supplied documents do not contain enough information, the copilot should abstain rather than invent an answer.

## Features

- Extracts text from the supplied SOP PDFs.
- Uses Sentence Transformers (`all-MiniLM-L6-v2`) to create embeddings.
- Stores and retrieves document chunks with ChromaDB.
- Uses a Gemini model to generate answers from retrieved SOP context.
- Displays source citations with document name, revision, and page.
- Abstains when the supplied documents do not contain sufficient information.
- Provides a FastAPI backend and a React/Vite frontend.
- Supports access from a phone on the same local Wi-Fi network.
- Prefers the latest retrieved revision for a document number in the `/ask` endpoint.

## Technology stack

**Backend:** Python, FastAPI, PyMuPDF, Sentence Transformers, ChromaDB, Google GenAI SDK, python-dotenv.

**Frontend:** React, Vite, Tailwind CSS.

**Generation model tested:** `gemini-3.5-flash-lite`.

## Project structure

```text
biztelai-copilot/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── ingestion.py
│   │   └── retrieval.py
│   ├── documents/       # Supplied SOP PDF files
│   ├── chroma_db/       # Generated vector database; do not commit
│   ├── venv/            # Python virtual environment; do not commit
│   ├── requirements.txt
│   └── .env             # Gemini API key; do not commit
├── frontend/
│   ├── src/
│   ├── package.json
│   └── ...
├── README.md
└── THINKING.md
```

## SOP documents

The application was tested with these four supplied PDFs:

1. `MNT-MAN-CNC-02_TX-200_Preventive_Maintenance.pdf`
2. `QC-SOP-014_Rev03_Incoming_Material_Inspection.pdf`
3. `QC-SOP-014_Rev04_Incoming_Material_Inspection.pdf`
4. `SAF-SOP-003_Lockout_Tagout_Procedure.pdf`

Revision 04 of `QC-SOP-014` supersedes Revision 03. The `/ask` endpoint prefers the highest retrieved revision for a document number to avoid using obsolete instructions when both revisions are retrieved.

## Prerequisites

- Python compatible with the packages in `backend/requirements.txt`.
- Node.js and npm.
- A Gemini API key with access and available quota for the configured model.

## Setup and run

### 1. Set up the backend

Open a terminal:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
```

Create `backend/.env` and add your own Gemini API key:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

Keep this key private. Do not commit `.env` or include the real key in screenshots or documentation.

Place the four supplied PDF files in `backend/documents/`.

### 2. Ingest the PDFs

From the `backend` directory, with the virtual environment activated, run the ingestion module:

```bash
python -m app.ingestion
```

The initial project ingestion processed 19 chunks. Verify that the command above matches the entry point implemented in your local `app/ingestion.py`; if that module uses a different command, use its actual entry point. Run ingestion again when the source PDFs or ingestion logic change.

### 3. Start the backend

From the `backend` directory, with the virtual environment activated:

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Useful backend URLs:

- API documentation: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

### 4. Start the frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0
```

Open the Vite URL shown in the terminal, normally `http://localhost:5173`.

### 5. Open the application on a phone

Connect the phone and Mac to the same Wi-Fi network. On the Mac, find its local IP address:

```bash
ipconfig getifaddr en0
```

On the phone, open:

```text
http://<MAC-LAN-IP>:5173
```

The backend must be running with `--host 0.0.0.0`. The frontend API base URL and FastAPI CORS allow-list must also contain the current Mac LAN IP. Update these values if the IP address changes. This provides local-network access, not public internet deployment.

## API endpoints

- `GET /` — basic service response.
- `GET /health` — backend health check.
- `POST /search` — returns semantically retrieved document excerpts and metadata.
- `POST /ask` — retrieves SOP context, generates an answer using the configured Gemini model, and returns answer/source information.

Example `/ask` request body:

```json
{
  "question": "What is the recommended coolant concentration for TX-200?",
  "top_k": 8
}
```

## Testing and results

The following five official sample questions and five additional questions were tested during development.

### Official sample questions

| # | Question | Expected answer from the SOPs | Result |
|---|---|---|---|
| 1 | What is the recommended coolant concentration for TX-200? | 6–8%; check using a refractometer reading multiplied by 1.0. | Passed; MNT-MAN-CNC-02, Rev 02, page 1. |
| 2 | What does alarm AL-104 mean and what should the operator do? | Way lube oil level low. Top up ISO VG 68 oil to the MAX mark, then press RESET. | Passed; MNT-MAN-CNC-02, Rev 02, page 2. |
| 3 | Who may remove a lockout lock if its owner is absent? | The Shift Supervisor contacts the owner. If the owner is unavailable, the Production Manager and Safety Officer authorise removal. Inspect the machine before re-energising, complete SF-12, and inform the owner before the next shift. | Passed; SAF-SOP-003, Rev 05, pages 1–2. |
| 4 | What is the acceptable BH-220 outer diameter tolerance and how is it measured? | 90.000 ± 0.050 mm, measured using a digital caliper; classification Major. | Passed; QC-SOP-014, Rev 04, page 2. |
| 5 | How often is spindle runout checked, who checks it, and what is the maximum? | Monthly by a maintenance technician using a dial indicator; maximum 0.005 mm. | Passed; MNT-MAN-CNC-02, Rev 02, page 1. |

### Additional questions

| # | Question | Expected answer from the SOPs | Result |
|---|---|---|---|
| 1 | What should an operator do if alarm AL-210 (Chuck clamp not confirmed) appears repeatedly? | Do not start the cycle; check chuck pressure and part seating; call maintenance if the alarm repeats. | Passed; MNT-MAN-CNC-02, Rev 02, page 2. |
| 2 | What should the operator do when alarm AL-305 (Spindle overload) occurs? | Stop the cycle; check tool wear and cutting parameters; inform the Shift Supervisor. | Passed; MNT-MAN-CNC-02, Rev 02, page 2. |
| 3 | What should the operator do if hydraulic pressure remains below 3.5 MPa? | Stop the cycle, check oil level and pressure gauge, and call maintenance if pressure remains below 3.5 MPa. | Passed; MNT-MAN-CNC-02, Rev 02, page 1. |
| 4 | Which form records incoming material inspection results, and how long must records be retained? | Digital form QF-07A in the QMS app; retain for 5 years. Revision 04 supersedes Revision 03. | Passed after latest-revision filtering; QC-SOP-014, Rev 04, page 2. |
| 5 | What is the recommended operating temperature range for TX-200 hydraulic oil? | The supplied SOPs do not specify this temperature. The application should respond: “I couldn't find sufficient information in the provided SOP documents.” | Passed; correctly abstained. |

An additional unsupported question about the air-compressor operating temperature was also tested, and the copilot correctly abstained.

## Implementation notes

- `/search` can show matching chunks from multiple revisions for diagnostic purposes.
- `/ask` applies the latest-revision preference when preparing context for answer generation.
- Gemini model access and quotas depend on the Google AI Studio project. A quota error can interrupt generation even when the backend retrieval and frontend are running correctly.
- A Hugging Face unauthenticated Hub warning during embedding-model download is separate from Gemini API quota errors.

## Security and limitations

- Store the Gemini API key only in `backend/.env` and never commit it.
- Do not commit `venv/`, `chroma_db/`, Python cache files, or local environment files.
- If an API key is exposed, revoke it and create a replacement.
- Phone access is limited to the same reachable local network unless the application is separately deployed.
- Answer generation depends on the configured Gemini model and available API quota.
- Retrieval quality depends on PDF extraction, chunking, embeddings, and the supplied document content.
- This application is a demonstration assistant; it does not replace approved plant procedures or authorised safety personnel.

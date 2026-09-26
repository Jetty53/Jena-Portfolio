# Jena Portfolio

Recruiter-facing RAG for [Jeet Nath](https://github.com/Jetty53): ingest documents into Postgres + pgvector, retrieve with hybrid search, and answer in chat as **Jena**.

| Folder | Role | Default URL |
| --- | --- | --- |
| `frontend/` | React (Vite) chat + site | http://127.0.0.1:5173 |
| `ingestor/` | FastAPI upload → parse → chunk → embed → R2 | http://127.0.0.1:8000 |
| `retriever/` | FastAPI ask / SSE stream | http://127.0.0.1:8001 |

Copy each `*.env.example` to `.env` and fill Gemini (and R2 for ingest). Do not commit `.env`.

## Stack

- Embeddings: `gemini-embedding-001` (768-d)
- Generate: `gemini-flash-latest`
- Store: Postgres + pgvector (`chunks.embedding`)
- Blobs: Cloudflare R2 (`in-progress` → `succeeded` / `failed`)

## Ingestor

```powershell
cd ingestor
python -m pip install -r requirements.txt
# start Postgres+pgvector (see docker-compose.yml)
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

```http
POST /v1/ingest/upload
Authorization: Bearer change-me
Content-Type: multipart/form-data
```

Form fields: `files` (PDF / DOCX / JPG / PNG, 10MB, max 10), `source_type` (`cv`, `github`, `academic`, `project`, `preferences`, `other`).

Returns **202** + `request_id`. Poll `GET /v1/ingest/{id}`.

Pipeline: stage R2 → SHA-256 dedup → parse → semantic chunks (filename prefix) → embed → pgvector → promote R2.

## Retriever

```powershell
cd retriever
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```

Same `DATABASE_URL` and `GEMINI_API_KEY` as ingest.

**Sync**

```http
POST /v1/ask
Authorization: Bearer change-me
Content-Type: application/json
```

```json
{
  "question": "Which languages does Jake list?",
  "session_id": "optional-uuid",
  "history": [
    {"role": "user", "content": "Where did Jake Ryan go to college?"},
    {"role": "assistant", "content": "..."}
  ]
}
```

Follow-ups like “what are his hobbies?” need `history` and/or the previous `session_id`. A bare question is stateless.

**Stream** (what the UI uses)

```http
POST /v1/ask/stream
```

SSE: `meta` (sources, session), `token`, `done`, `error`.

Retrieval: query embed → cosine + keyword (RRF) → top 5 → generate with citations `(filename.pdf)`. Stream skips the extra judge loop so the first tokens arrive sooner.

## Frontend

```powershell
cd frontend
copy .env.example .env
npm install
npm run dev
```

Endpoints live in `src/app/config/services.ts` (`VITE_INGESTOR_URL`, `VITE_RETRIEVER_URL`, tokens). Chat calls `/v1/ask/stream` only through `src/app/api/retriever.ts`.

```powershell
npm test
```

## Tests

```powershell
cd ingestor; python -m pytest -q
cd retriever; python -m pytest -q
```

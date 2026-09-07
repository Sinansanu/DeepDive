# DeepDive

DeepDive is an AI-powered research assistant scaffold. It accepts a research topic, automatically searches for source pages when URLs are not supplied, scrapes readable content, extracts metadata, generates a concise report, stores source embeddings locally, and keeps report history in SQLite.

## Run

```powershell
cd deepdive
python -m backend.api.server
```

Open `http://127.0.0.1:8000`.

## API

- `GET /api/health` checks service health.
- `POST /api/research` accepts `{ "query": "...", "urls": ["https://..."] }`. Leave `urls` empty to discover sources automatically.
- `POST /api/report/from-text` accepts pasted source text for offline report generation.
- `GET /api/reports` lists saved reports.
- `GET /api/memory?q=...` searches the local vector memory.

## Notes

The current implementation uses only Python standard library modules so it can run without dependency installation. The embedding layer is a local hashed vector implementation intended for development and demos; it can later be replaced with a hosted embedding model and a production vector database.

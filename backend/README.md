# LeetTrack Backend

The backend is a FastAPI application. It owns API contracts, validation, external integrations, and will eventually own authentication, persistence, scheduled jobs, email reports, and AI-assisted coaching endpoints.

Current endpoints:

- `GET /health`
- `POST /leetcode/sync`

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/health
```

Expected response:

```json
{
  "status": "ok",
  "service": "leettrack-api"
}
```

## LeetCode Sync

`POST /leetcode/sync` fetches recent accepted submissions for a LeetCode username through LeetCode's GraphQL endpoint.

Example request:

```json
{
  "username": "kprashanth01",
  "limit": 10
}
```

The response includes normalized submission data that later database and dashboard features can reuse.

This endpoint does not persist data yet. Database persistence will be introduced in a separate migration-backed feature.

## API Docs

FastAPI automatically provides OpenAPI docs at:

```text
http://127.0.0.1:8000/docs
```

## Tests

Run backend tests from the `backend/` directory:

```bash
.venv\Scripts\python -m pytest -q
```

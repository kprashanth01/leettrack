# LeetTrack Backend

The backend is a FastAPI application. It will eventually own authentication, problem logs, analytics APIs, email scheduling, and AI-assisted coaching endpoints.

For the foundation milestone, it exposes only a health endpoint.

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

## API Docs

FastAPI automatically provides OpenAPI docs at:

```text
http://127.0.0.1:8000/docs
```

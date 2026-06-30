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

Create a local environment file:

```bash
copy .env.example .env
```

Set the `SUPABASE_DB_*` values in `.env` from your Supabase Postgres connection details. This is preferred over a single URL because it handles special characters in passwords safely.

## Run

Apply database migrations before using endpoints that persist data:

```bash
alembic upgrade head
```

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

`POST /leetcode/sync` fetches recent accepted submissions for a LeetCode username through LeetCode's GraphQL endpoint and saves new submissions to the database.

Example request:

```json
{
  "username": "kprashanth01",
  "limit": 10
}
```

The response includes normalized submission data plus `fetched_count` and `saved_count`.

Repeated syncs are deduplicated by LeetCode account, problem, and submission timestamp.

## Database

The backend reads `DATABASE_URL` when connecting to the database. If `DATABASE_URL` is not set, it uses a local SQLite file named `leettrack.db`.

Supabase PostgreSQL connection strings should be provided through `DATABASE_URL` in local or deployment environment variables.

Schema changes are managed with Alembic migrations:

```bash
alembic upgrade head
```

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

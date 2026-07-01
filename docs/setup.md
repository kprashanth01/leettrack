# Setup Guide

This guide explains how to run the LeetTrack foundation locally.

## Prerequisites

- Node.js for the frontend.
- Python 3.11 or newer for the backend.
- Git for version control.

## Frontend

```bash
cd frontend
npm install
copy .env.example .env.local
npm run dev
```

Set `VITE_API_BASE_URL` in `frontend/.env.local` if your backend is not running on `http://127.0.0.1:8000`.

Set these values to enable Supabase GitHub login:

```text
VITE_SUPABASE_URL=https://[PROJECT_REF].supabase.co
VITE_SUPABASE_PUBLISHABLE_KEY=[PUBLISHABLE_KEY]
```

In Supabase, enable the GitHub auth provider and configure the GitHub OAuth callback URL:

```text
https://[PROJECT_REF].supabase.co/auth/v1/callback
```

The Vite dev server prints a local URL, usually:

```text
http://localhost:5173
```

## Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

Edit `backend/.env` and set the `SUPABASE_DB_*` values from your Supabase Postgres connection details before running migrations against Supabase.

Health check:

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

API docs:

```text
http://127.0.0.1:8000/docs
```

Database configuration:

```text
SUPABASE_DB_HOST=db.[PROJECT_REF].supabase.co
SUPABASE_DB_PORT=5432
SUPABASE_DB_NAME=postgres
SUPABASE_DB_USER=postgres
SUPABASE_DB_PASSWORD=...
```

Backend auth verification:

```text
SUPABASE_URL=https://[PROJECT_REF].supabase.co
SUPABASE_PUBLISHABLE_KEY=...
```

If `DATABASE_URL` is not set, the backend uses a local SQLite file named `leettrack.db` for development.

Run backend tests from the `backend/` directory:

```bash
.venv\Scripts\python -m pytest -q
```

## Common Issues

If a port is already in use, stop the other server or choose a different port.

If Python dependencies are missing, confirm the virtual environment is activated before running `pip install`.

If frontend dependencies are missing, run `npm install` inside `frontend/`, not at the repository root.

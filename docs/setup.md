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
npm run dev
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
uvicorn app.main:app --reload
```

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

## Common Issues

If a port is already in use, stop the other server or choose a different port.

If Python dependencies are missing, confirm the virtual environment is activated before running `pip install`.

If frontend dependencies are missing, run `npm install` inside `frontend/`, not at the repository root.

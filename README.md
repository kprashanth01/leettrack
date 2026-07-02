# LeetTrack

LeetTrack is an AI-powered competitive programming tracker for logging solved LeetCode problems, reviewing notes, analyzing progress, and eventually receiving personalized coaching reports.

This repository is being built incrementally as a professional full-stack portfolio project. Each milestone is scoped through a GitHub issue, design notes, an implementation plan, code review, and a focused commit.

## Current Status

The project is in its early product foundation:

- `frontend/` contains the React + Vite + TypeScript app with Supabase Auth, analytics views, notes, review, and settings.
- `backend/` contains the FastAPI API for syncing LeetCode submissions, persisting notes, and sending weekly email summaries.
- `extension/` contains the Manifest V3 browser extension for detecting LeetCode problem pages and opening/saving them in LeetTrack.
- `docs/` contains architecture, setup, and workflow documentation.

Product features such as deeper browser extension sync, richer revision scheduling, and AI coaching will be added in later milestones.

## Repository Structure

```text
leettrack/
  frontend/   React + Vite + TypeScript application
  backend/    FastAPI application
  extension/  Manifest V3 browser extension
  docs/       Architecture, setup, and development workflow notes
```

## Local Development

Read the setup guide first:

```text
docs/setup.md
```

Quick commands:

```bash
cd frontend
npm install
npm run dev
```

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Development Workflow

Each feature should follow this sequence:

1. Explain the objective and architecture.
2. Create or reference a GitHub issue.
3. Write a development plan.
4. Create a `feature/`, `fix/`, `refactor/`, `docs/`, or `chore/` branch.
5. Implement one logical unit of work.
6. Verify manually and with tests where applicable.
7. Review the code.
8. Commit using Conventional Commits.
9. Merge only after review.

## Documentation

- `docs/architecture.md` explains the high-level system boundaries.
- `docs/setup.md` explains local setup.
- `docs/deployment.md` explains the production deployment checklist.
- `docs/development-workflow.md` explains how changes should move from idea to merge.

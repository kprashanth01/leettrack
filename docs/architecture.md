# LeetTrack Architecture

LeetTrack is organized as a monorepo with independent frontend and backend applications.

```mermaid
flowchart LR
  User["User"] --> Frontend["frontend/ React + Vite"]
  Frontend --> Backend["backend/ FastAPI"]
  Backend --> LeetCode["LeetCode GraphQL"]
  Backend --> FutureDatabase["Future: Supabase PostgreSQL"]
  Backend --> FutureEmail["Future: Resend"]
  Backend --> FutureAI["Future: AI coaching services"]

  Extension["Future: Browser Extension"] --> Backend
```

## Current Foundation

The current backend milestone includes:

- a React + Vite frontend shell;
- a FastAPI backend shell;
- a `/health` endpoint;
- a `POST /leetcode/sync` endpoint that fetches recent accepted LeetCode submissions;
- documentation for setup and workflow.

## Boundaries

The frontend owns presentation, routing, UI state, and API calls.

The backend owns API contracts, validation, authentication, persistence, scheduled jobs, and external integrations. LeetCode communication is isolated behind a client/service boundary so the rest of the application does not depend directly on LeetCode's GraphQL response shape.

The database will be introduced through migrations when we build the first persistent feature. We will not modify the database manually.

## Why This Structure

Keeping the apps independent makes each layer easier to test, deploy, and reason about. Keeping them in one repository keeps the portfolio story, documentation, and pull requests easy to follow.

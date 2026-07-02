# Deployment Guide

This guide prepares LeetTrack for production deployment with:

- Frontend on Vercel.
- Backend on Render or Railway.
- Database on Supabase Postgres.
- Email delivery through Resend.
- Manual weekly email reports, with optional scheduled dispatch through the backend scheduler endpoint.

## Deployment Architecture

```mermaid
flowchart LR
  User["Browser"] --> Vercel["Vercel frontend"]
  Vercel --> SupabaseAuth["Supabase Auth"]
  Vercel --> Backend["Render/Railway FastAPI backend"]
  Backend --> SupabaseDb["Supabase Postgres"]
  Backend --> LeetCode["LeetCode GraphQL"]
  Backend --> Resend["Resend"]
  OptionalCron["Optional cron provider"] --> Backend
```

## 1. Supabase

Run database migrations before sending production traffic to the backend:

```bash
cd backend
alembic upgrade head
```

Use the Supabase pooler connection string for hosted backends when possible:

```text
DATABASE_URL=postgresql://postgres.[PROJECT_REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
```

Keep these Supabase Auth URLs aligned:

- Site URL: your Vercel production URL.
- Additional redirect URLs:
  - `http://localhost:5173`
  - your Vercel preview URL pattern, if you use preview auth testing
  - your Vercel production URL

The backend talks to Postgres through SQLAlchemy using a direct database connection. New backend-owned tables do not need browser-facing Supabase Data API grants unless the frontend later reads them through `supabase-js`.

## 2. Backend: Render or Railway

Set the backend root directory to:

```text
backend
```

Use these commands:

```text
Build command: pip install -r requirements.txt
Start command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

The included `backend/Procfile` contains the same web process command for hosts that detect Procfiles.

Required production environment variables:

```text
APP_ENV=production
DATABASE_URL=postgresql://...
SUPABASE_URL=https://[PROJECT_REF].supabase.co
SUPABASE_PUBLISHABLE_KEY=[PUBLISHABLE_KEY]
CORS_ALLOWED_ORIGINS=https://[FRONTEND_PROJECT].vercel.app
RESEND_API_KEY=re_...
EMAIL_FROM=LeetTrack <hello@your-verified-domain.com>
SCHEDULER_SECRET=[LONG_RANDOM_SECRET]
```

After deploy, verify:

```text
https://[BACKEND_HOST]/health
```

Expected response:

```json
{
  "status": "ok",
  "service": "leettrack-api"
}
```

## 3. Frontend: Vercel

Create a Vercel project with:

```text
Root Directory: frontend
Build Command: npm run build
Output Directory: dist
Install Command: npm install
```

Set these Vercel environment variables:

```text
VITE_API_BASE_URL=https://[BACKEND_HOST]
VITE_SUPABASE_URL=https://[PROJECT_REF].supabase.co
VITE_SUPABASE_PUBLISHABLE_KEY=[PUBLISHABLE_KEY]
```

The included `frontend/vercel.json` rewrites all routes to `index.html` so React Router paths such as `/dashboard`, `/notes`, and `/settings` work after refresh.

## 4. Weekly Emails

The free-tier production path is:

1. the user signs in and opens LeetTrack;
2. the frontend loads the saved LeetCode username;
3. the frontend asks the backend to sync the latest public accepted submissions;
4. the user sends the weekly summary manually from Settings.

This keeps reports fresh while avoiding a paid cron dependency.

Optional automation can be added later with a cron provider. The scheduled job should send a weekly `POST` request to:

```text
https://[BACKEND_HOST]/emails/weekly-summary/dispatch
```

Required header:

```text
X-LeetTrack-Scheduler-Secret: [SCHEDULER_SECRET]
```

The optional dispatch endpoint:

- checks the scheduler secret;
- skips users already emailed for the current UTC week;
- syncs each opted-in user's saved LeetCode username;
- sends the weekly report with Resend;
- records delivery and sync outcomes.

## Production Checklist

- [ ] Supabase migrations are applied with `alembic upgrade head`.
- [ ] Supabase GitHub Auth provider is enabled.
- [ ] Supabase Site URL and redirect URLs include the Vercel frontend URL.
- [ ] Backend is deployed with `APP_ENV=production`.
- [ ] Backend `DATABASE_URL` points to Supabase Postgres or pooler.
- [ ] Backend `CORS_ALLOWED_ORIGINS` contains the exact Vercel frontend origin.
- [ ] Backend `/health` returns `{"status":"ok","service":"leettrack-api"}`.
- [ ] Frontend Vercel env vars point to the production backend and Supabase project.
- [ ] Resend sender uses a verified domain before public use.
- [ ] If using scheduled email automation, scheduler secret is set on the backend and the cron provider.
- [ ] If using scheduled email automation, weekly dispatch endpoint is tested once manually with the scheduler header.
- [ ] No `.env`, `.env.local`, API keys, database passwords, or scheduler secrets are committed.

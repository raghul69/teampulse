# TeamPulse Leave Management System

TeamPulse is a leave management system built with a free, simple stack:

- FastAPI backend
- Streamlit frontend/admin panel
- Supabase Auth
- Supabase PostgreSQL
- SQLAlchemy + Alembic

Authentication is handled by Supabase Auth. TeamPulse roles and profile data are stored in `public.users`, mapped to Supabase `auth.users` through `public.users.auth_user_id`. The application does not use custom JWT/password authentication and does not use paid admin panel tools.

## Features

- Supabase email/password login
- Supabase session refresh through refresh tokens
- Role-based dashboards for Admin, Manager, and Employee
- Admin user, department, leave balance, leave request, audit log, and report pages
- Manager team request approval/rejection, conflict warnings, team members, and team calendar
- Employee leave application, balance, history/status, and notifications
- FastAPI API docs through OpenAPI

## Tech Stack

```text
Backend:   FastAPI, SQLAlchemy, Alembic, PyJWT, httpx
Frontend:  Streamlit
Auth:      Supabase Auth
Database:  Supabase PostgreSQL
CI:        GitHub Actions
```

## Project Structure

```text
backend/
  main.py
  app/
    api/                  FastAPI routes and dependencies
    core/                 settings, enums, exceptions, Supabase JWT validation
    db/                   SQLAlchemy session and metadata
    middleware/           Supabase auth middleware
    models/               SQLAlchemy models
    schemas/              Pydantic schemas
    services/             business logic
frontend/
  streamlit_app.py        Streamlit role-based admin panel
docs/
  supabase-auth-schema.sql
  production-checklist.md
  deployment.md
alembic/
  env.py
  versions/
```

## Local Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` with your real Supabase and database values. Keep `.env` private; it is ignored by git.

## Required Environment Values

```env
PROJECT_NAME="TeamPulse Leave Management API"
API_VERSION="1.0.0"
API_V1_PREFIX="/api/v1"
DATABASE_URL="postgresql+psycopg://<db-user>:<db-password>@<db-host>:5432/<db-name>"
SUPABASE_URL="https://your-project-ref.supabase.co"
SUPABASE_PUBLISHABLE_KEY="sb_publishable_replace_me"
SUPABASE_SERVICE_ROLE_KEY=""
SUPABASE_JWT_AUDIENCE="authenticated"
SUPABASE_AUTH_VERIFY_TIMEOUT_SECONDS=5
REQUIRE_EMAIL_VERIFICATION=true
```

Use `SUPABASE_SERVICE_ROLE_KEY` only on trusted backend servers if a future feature needs it. Never expose a service-role key to Streamlit clients, browsers, or public repositories.

## Supabase Setup

1. Create a Supabase project.
2. Enable Email provider in Supabase Auth.
3. Configure email confirmation and password reset redirect URLs.
4. Copy your Supabase project URL into `SUPABASE_URL`.
5. Copy your publishable key into `SUPABASE_PUBLISHABLE_KEY`.
6. Copy the Supabase PostgreSQL connection string into `DATABASE_URL`.
7. Run the starter schema and RLS SQL in [docs/supabase-auth-schema.sql](docs/supabase-auth-schema.sql).
8. Create Supabase Auth users for Admin, Manager, and Employee accounts.
9. Insert matching rows in `public.users` and set `auth_user_id` to each Supabase `auth.users.id`.

Roles must come from `public.users.role`, not from user-editable metadata.

## First Admin Setup

After creating the first Supabase Auth admin user, insert or update a matching TeamPulse profile:

```sql
insert into public.users (auth_user_id, full_name, email, role, is_active)
values (
  '<supabase-auth-user-id>',
  'TeamPulse Admin',
  'admin@example.com',
  'admin',
  true
);
```

Then sign in from the Streamlit panel with that Supabase Auth email/password.

## Run Backend

```powershell
uvicorn backend.main:app --host 127.0.0.1 --port 8002 --reload
```

Backend health:

```text
http://127.0.0.1:8002/api/v1/health
```

API docs:

```text
http://127.0.0.1:8002/docs
```

## Run Streamlit Admin Panel

Open a second terminal:

```powershell
.\.venv\Scripts\Activate.ps1
$env:TEAMPULSE_API_URL="http://127.0.0.1:8002/api/v1"
streamlit run frontend/streamlit_app.py --server.address 127.0.0.1 --server.port 8503
```

Frontend/admin panel:

```text
http://127.0.0.1:8503
```

## GitHub Push Steps

This repository is already initialized locally with an initial commit on `main`.

Install GitHub CLI on Windows:

```powershell
winget install GitHub.cli
```

Log in:

```powershell
gh auth login
```

Create and push a private GitHub repository:

```powershell
gh repo create teampulse --private --source . --remote origin --push
```

Create and push a public GitHub repository:

```powershell
gh repo create teampulse --public --source . --remote origin --push
```

Manual GitHub website method:

1. Go to `https://github.com/new`.
2. Create an empty repository named `teampulse`.
3. Do not initialize it with a README, license, or `.gitignore`.
4. Run:

```powershell
git remote add origin <repo-url>
git push -u origin main
```

## Deployment Notes

Recommended free/low-cost deployment:

- Supabase for PostgreSQL and Auth
- Render or Railway for FastAPI
- Streamlit Community Cloud or Render for the Streamlit frontend

Production requirements:

- Set all production environment variables in the hosting provider.
- Configure CORS for the deployed Streamlit URL.
- Keep Supabase service-role keys server-only.
- Verify `GET /api/v1/health` after deploy.
- Test Admin, Manager, and Employee login flows after deploy.

Detailed deployment guide: [docs/deployment.md](docs/deployment.md)

Production checklist: [docs/production-checklist.md](docs/production-checklist.md)

# TeamPulse Leave Management System

AI-powered employee leave management starter project using FastAPI, Streamlit, and PostgreSQL.

## Features

- Role based login: Employee, Manager, Admin
- Employee dashboard with leave balance, leave application, status, and history
- Manager dashboard with team requests, approve/reject actions, conflict checks, and team analytics
- Admin dashboard with user overview, balances, leave requests, and reports
- SQLite database with seeded demo users
- Smart suggestions for leave type, balance warnings, workload conflict detection, and reporting insights

## Project Structure

```text
backend/
  main.py                    FastAPI compatibility entrypoint
  app/
    main.py                  App factory
    api/
      deps.py                Dependency injection for DB, auth, RBAC
      v1/
        router.py            API v1 router composition
        routes/              Route modules by domain
    core/
      config.py              Environment settings
      enums.py               Shared domain enums
      exceptions.py          Global error strategy
      security.py            Supabase JWT validation helpers
    db/
      session.py             SQLAlchemy engine/session
      base.py                Alembic model metadata import
    models/                  SQLAlchemy models
    schemas/                 Pydantic request/response schemas
    services/                Business logic layer
alembic/
  env.py                     Migration environment
  versions/                  Generated migrations
frontend/
  streamlit_app.py
requirements.txt
```

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and set `DATABASE_URL`, `SUPABASE_URL`, and `SUPABASE_PUBLISHABLE_KEY`.
Use `SUPABASE_SERVICE_ROLE_KEY` only on trusted backend servers; never expose it to Streamlit or browser clients.

## Supabase Auth

TeamPulse uses Supabase Auth for email/password login, email verification, password reset, logout, and session refresh.
The local `public.users` table stores application profile and authorization data and maps to `auth.users` through `users.auth_user_id`.
Roles are loaded from `public.users.role`, not from user-editable metadata.

Useful backend auth endpoints:

```text
POST /api/v1/auth/signup
POST /api/v1/auth/login
POST /api/v1/auth/refresh
POST /api/v1/auth/password-reset
POST /api/v1/auth/resend-verification
POST /api/v1/auth/logout
GET  /api/v1/users/me
```

Schema and RLS starter SQL: `docs/supabase-auth-schema.sql`

## Database Migrations

```powershell
alembic revision --autogenerate -m "initial schema"
alembic upgrade head
```

## Run Backend

```powershell
uvicorn backend.main:app --reload
```

Backend API: `http://127.0.0.1:8000`

OpenAPI docs: `http://127.0.0.1:8000/docs`

## Run Frontend

Open a second terminal:

```powershell
.\.venv\Scripts\Activate.ps1
streamlit run frontend/streamlit_app.py
```

## Demo Logins

Create users through Supabase Auth, then ensure `public.users.auth_user_id` maps each Supabase user to a TeamPulse role.

## Notes

This starter uses rule-based AI helpers so it works locally without paid API keys. The `backend/ai.py` module is intentionally isolated so a real LLM or ML model can be added later.

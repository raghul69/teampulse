# TeamPulse Deployment Guide

This guide keeps TeamPulse on a free or low-cost stack.

## Recommended Hosting

- Supabase: PostgreSQL and Auth
- Render or Railway: FastAPI backend
- Streamlit Community Cloud or Render: Streamlit frontend/admin panel

## Production Environment Variables

Set these for the FastAPI backend:

```env
PROJECT_NAME="TeamPulse Leave Management API"
API_VERSION="1.0.0"
API_V1_PREFIX="/api/v1"
SUPABASE_URL="https://your-project-ref.supabase.co"
SUPABASE_PUBLISHABLE_KEY="sb_publishable_replace_me"
NEXT_PUBLIC_SUPABASE_URL="https://your-project-ref.supabase.co"
NEXT_PUBLIC_SUPABASE_ANON_KEY="sb_publishable_replace_me"
SUPABASE_SERVICE_ROLE_KEY=""
DATABASE_URL="postgresql+psycopg://<db-user>:<db-password>@<db-host>:5432/<db-name>"
SUPABASE_JWT_AUDIENCE="authenticated"
SUPABASE_AUTH_VERIFY_TIMEOUT_SECONDS=5
REQUIRE_EMAIL_VERIFICATION=true
```

Set this for the Streamlit frontend:

```env
TEAMPULSE_API_URL="https://your-backend-domain.example.com/api/v1"
```

## Supabase Setup

1. Create a Supabase project.
2. Enable Email provider under Authentication.
3. Configure Site URL and Redirect URLs for your Streamlit domain.
4. Run `npx supabase db push` to apply migrations from `supabase/migrations/`.
5. Create Auth users.
6. Map each Auth user to `public.users.auth_user_id`.
7. Confirm roles in `public.users.role`.
8. Confirm `leave_types`, `leave_policies`, and `holidays` are present.
9. Configure yearly employee leave balances before live use.

## FastAPI Backend

Install/build command:

```bash
pip install -r requirements.txt
```

Start command:

```bash
uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

Health check URL:

```text
/api/v1/health
```

Full health check after deploy:

```text
https://your-backend-domain.example.com/api/v1/health
```

API docs:

```text
https://your-backend-domain.example.com/docs
```

## Streamlit Frontend

Install/build command:

```bash
pip install -r requirements.txt
```

Start command:

```bash
streamlit run frontend/streamlit_app.py --server.address 0.0.0.0 --server.port $PORT
```

Set `TEAMPULSE_API_URL` to the deployed backend API prefix, for example:

```text
https://your-backend-domain.example.com/api/v1
```

## CORS Setup

Before production, configure backend CORS to allow the deployed Streamlit URL and local development URLs.

Recommended allowed origins:

```text
http://127.0.0.1:8503
http://localhost:8503
https://your-streamlit-domain.example.com
```

Avoid `allow_origins=["*"]` in production if credentials or sensitive browser flows are added later.

## Testing After Deployment

1. Open the backend health URL.
2. Open API docs and confirm routes load.
3. Open Streamlit frontend.
4. Log in as Admin.
5. Log in as Manager.
6. Log in as Employee.
7. Submit a leave request as Employee.
8. Confirm duplicate/overlapping employee requests are blocked.
9. Confirm insufficient paid balance requests are blocked.
10. Approve/reject it as Manager and verify balance-before-approval.
11. Verify notifications.
12. Verify audit logs.
13. Verify reports summary and AI insights.
14. Ask the AI assistant about balance, policy, and request status.
15. Let an access token expire or force a `401` and confirm refresh-token retry works.

## Production Leave Setup

In the Streamlit Admin dashboard:

1. Create departments.
2. Create manager and employee profiles mapped to Supabase Auth users.
3. Assign each employee to a manager.
4. Review the default leave types: casual, sick, earned, unpaid.
5. Add leave policies for allowances, notice periods, and carry-forward rules.
6. Add company holidays and department holidays.
7. Create current-year leave balances for all employees.

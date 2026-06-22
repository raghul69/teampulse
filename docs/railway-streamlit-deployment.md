# TeamPulse Production Deployment — Railway + Streamlit Community Cloud + Supabase

This is the step-by-step playbook for deploying TeamPulse to real production:

- **Backend (FastAPI)** → Railway
- **Frontend panels (Streamlit ×2: User + Admin)** → Streamlit Community Cloud
- **Database + Auth** → Supabase (already hosted)
- **Source** → GitHub

> The Niteshift sandbox `*.preview.niteshift.dev` URLs are temporary demo links, **not** production. The production API base URL is the Railway URL produced below.

---

## 0. Prerequisites (accounts you must own)

- GitHub repo for this project (push access).
- Railway account (https://railway.app) — Hobby plan is fine.
- Streamlit Community Cloud account (https://share.streamlit.io), linked to GitHub.
- Supabase project (already created): ref `cgnygmgtemwpeuddsccg`.

---

## 1. Push the code to GitHub

The repo already contains the production artifacts added for this deployment:
- `Procfile` — Railway start command.
- CORS middleware in `backend/app/main.py` driven by `ALLOWED_ORIGINS`.
- `frontend/streamlit_app.py` reads config from env **or** `st.secrets` (Streamlit Cloud).

```bash
git push origin main         # or your chosen branch
```

No secrets are committed (`.env` is git-ignored). Verify with `git ls-files | grep -i env` → only `.env.example`.

---

## 2. Backend on Railway

1. **New Project → Deploy from GitHub repo** → pick this repo.
2. Railway auto-detects Python + `requirements.txt`. The `Procfile` provides the start command:
   ```
   web: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
   ```
   (Railway injects `$PORT`; do not hardcode it.)
3. **Variables** tab → add the environment variables below.
4. Deploy. When it's live, open **Settings → Networking → Generate Domain** to get a public URL like `https://teampulse-api-production.up.railway.app`.
5. Confirm:
   - `https://<railway-domain>/api/v1/health` → `{"status":"ok"}`
   - `https://<railway-domain>/docs` → Swagger UI loads.

### Railway environment variables

| Variable | Value | Notes |
|----------|-------|-------|
| `SUPABASE_URL` | `https://cgnygmgtemwpeuddsccg.supabase.co` | Supabase project URL |
| `SUPABASE_PUBLISHABLE_KEY` | *(anon/publishable key)* | from Supabase → Project Settings → API |
| `SUPABASE_SERVICE_ROLE_KEY` | *(service_role key)* | **backend only — never in Streamlit** |
| `DATABASE_URL` | `postgresql+psycopg://postgres.cgnygmgtemwpeuddsccg:<URL-ENCODED-PW>@aws-1-ap-southeast-1.pooler.supabase.com:5432/postgres?sslmode=require` | **IPv4 Supavisor pooler** (the direct `db.<ref>.supabase.co` host is IPv6-only) |
| `ALLOWED_ORIGINS` | `https://<user-panel>.streamlit.app,https://<admin-panel>.streamlit.app` | comma-separated; fill in after Step 3 |
| `REQUIRE_EMAIL_VERIFICATION` | `true` | recommended in production |
| `SUPABASE_JWT_AUDIENCE` | `authenticated` | default |
| `PROJECT_NAME` / `API_VERSION` / `API_V1_PREFIX` | optional | sensible defaults exist |
| `JWT_SECRET` | *(any value — see note)* | **Not used by the app.** TeamPulse uses Supabase Auth, not custom JWT. The setting layer ignores unknown vars, so setting it does no harm, but it is not required. Do **not** add custom JWT auth. |

> Password encoding: the DB password must be URL-encoded in the connection string (e.g. `@` → `%40`).

---

## 3. Streamlit Community Cloud — two apps from one repo

Deploy the **same repo** twice, changing only the `PANEL` secret.

### A. User Panel
1. https://share.streamlit.io → **New app** → select repo + branch.
2. **Main file path:** `frontend/streamlit_app.py`
3. **Advanced settings → Secrets** (TOML):
   ```toml
   PANEL = "user"
   TEAMPULSE_API_URL = "https://<railway-domain>/api/v1"
   SUPABASE_URL = "https://cgnygmgtemwpeuddsccg.supabase.co"
   SUPABASE_PUBLISHABLE_KEY = "<publishable key>"
   ```
4. Deploy → note the URL, e.g. `https://teampulse-user.streamlit.app`.

### B. Admin / Manager Panel
Same steps, but secrets:
```toml
PANEL = "admin"
TEAMPULSE_API_URL = "https://<railway-domain>/api/v1"
SUPABASE_URL = "https://cgnygmgtemwpeuddsccg.supabase.co"
SUPABASE_PUBLISHABLE_KEY = "<publishable key>"
```
Deploy → e.g. `https://teampulse-admin.streamlit.app`.

> **Never** put `SUPABASE_SERVICE_ROLE_KEY` in Streamlit secrets — it stays in Railway only.

After both URLs exist, go back to **Railway → `ALLOWED_ORIGINS`** and set them, then redeploy the backend.

---

## 4. Supabase production settings

In the Supabase dashboard:
1. **Authentication → URL Configuration**
   - **Site URL:** the User Panel URL (`https://teampulse-user.streamlit.app`).
   - **Redirect URLs:** add both panel URLs (and `/**` if you use email confirm/reset links):
     - `https://teampulse-user.streamlit.app`
     - `https://teampulse-admin.streamlit.app`
2. **Auth providers:** Email provider enabled.
3. **RLS:** already enabled on all tables via migrations in `supabase/migrations/`. Confirm under Table Editor → each table shows "RLS enabled".
4. Migrations are already applied to this project; for a fresh project run `npx supabase db push`.

> CORS for the Data API isn't needed here — the app talks to Postgres via the backend's `DATABASE_URL`, and to Supabase Auth via REST (no browser CORS).

---

## 5. Security

- No secrets committed to GitHub (`.env` git-ignored; only `.env.example` placeholders tracked).
- All keys live in **Railway** (backend) and **Streamlit Cloud secrets** (panels).
- `SUPABASE_SERVICE_ROLE_KEY` is **Railway-only**, never exposed to the browser/Streamlit.
- No custom JWT/password auth — Supabase Auth is the only identity source; roles come from `public.users.role` via `auth_user_id`.

---

## 6. Final production smoke test

Against the **production** URLs:
1. Backend `/api/v1/health` → 200; `/docs` loads.
2. User signup (if enabled) / **User login** on the User Panel.
3. Employee: dashboard loads, **apply a leave request**, view balance, notifications.
4. Manager: log in to User Panel, see team requests, **approve/reject**, confirm balance updates.
5. Admin: log in to **Admin Panel**, view Reports / Users / Audit Logs.
6. Confirm Employee/Manager are **denied** on the Admin Panel.
7. Logout clears the session.

---

## 7. What I still need from you to actually deploy

Deployment requires logging into your accounts, which I cannot do from the sandbox:
- Confirm the **GitHub repo** to push to (and that I may push / open a PR).
- A **Railway** project (or authorize the Railway CLI/token if you want me to script it).
- A **Streamlit Community Cloud** account linked to that GitHub repo.
- Decision on `REQUIRE_EMAIL_VERIFICATION` for production (recommended `true`).

Everything in the codebase is ready; these are external account actions.

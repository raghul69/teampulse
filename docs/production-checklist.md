# TeamPulse Production Readiness Checklist

Use this checklist before pushing to production.

## Supabase

- [ ] Supabase project created
- [ ] Supabase Email Auth provider enabled
- [ ] Email verification configured
- [ ] Password reset redirect URL configured
- [ ] `SUPABASE_URL` added to backend environment
- [ ] `SUPABASE_PUBLISHABLE_KEY` added to backend environment
- [ ] `DATABASE_URL` added to backend environment
- [ ] `docs/supabase-auth-schema.sql` run
- [ ] Row Level Security enabled on exposed public tables
- [ ] Supabase Auth users created
- [ ] `public.users.auth_user_id` mapping completed
- [ ] Admin user mapped with `role = 'admin'`
- [ ] Manager user mapped with `role = 'manager'`
- [ ] Employee user mapped with `role = 'employee'`

## Application

- [ ] Admin login tested
- [ ] Manager login tested
- [ ] Employee login tested
- [ ] Admin user management tested
- [ ] Department management tested
- [ ] Leave balance management tested
- [ ] Employee leave application tested
- [ ] Manager approval/rejection tested
- [ ] Notifications tested
- [ ] Audit logs verified
- [ ] Reports summary verified
- [ ] Expired access token refresh tested

## Security

- [ ] `.env` is not committed
- [ ] `.env.local` is not committed
- [ ] `.streamlit/secrets.toml` is not committed
- [ ] Supabase service-role key is not exposed to Streamlit/browser clients
- [ ] No custom JWT/password auth reintroduced
- [ ] CORS configured for production frontend URL
- [ ] Production secrets stored only in hosting provider env vars

## Deployment

- [ ] Backend deployed
- [ ] Streamlit deployed
- [ ] Production env vars added
- [ ] Backend health check verified
- [ ] Logs verified
- [ ] API docs reachable or intentionally disabled
- [ ] Error monitoring/log review process defined

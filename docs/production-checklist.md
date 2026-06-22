# TeamPulse Production Readiness Checklist

Use this checklist before pushing to production.

## Supabase

- [ ] Supabase project created
- [ ] Supabase Email Auth provider enabled
- [ ] Email verification configured
- [ ] Password reset redirect URL configured
- [ ] `SUPABASE_URL` added to backend environment
- [ ] `SUPABASE_PUBLISHABLE_KEY` added to backend environment
- [ ] `NEXT_PUBLIC_SUPABASE_URL` placeholder/client value configured if needed
- [ ] `NEXT_PUBLIC_SUPABASE_ANON_KEY` placeholder/client value configured if needed
- [ ] `DATABASE_URL` added to backend environment
- [ ] Supabase CLI project linked
- [ ] Supabase migrations pushed with `npx supabase db push`
- [ ] Row Level Security enabled on exposed public tables
- [ ] `leave_types`, `leave_policies`, and `holidays` tables created
- [ ] RLS policies active for leave type, policy, and holiday tables
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
- [ ] Leave type and policy setup tested
- [ ] Holiday setup tested
- [ ] Leave balance management tested
- [ ] Employee leave application tested
- [ ] Insufficient balance prevention tested
- [ ] Duplicate overlapping employee leave prevention tested
- [ ] Manager approval/rejection tested
- [ ] Manager balance-before-approval view tested
- [ ] Team calendar and conflict warnings tested
- [ ] Notifications tested
- [ ] Audit logs verified
- [ ] Reports summary verified
- [ ] AI leave recommendation tested
- [ ] AI assistant tested for balance, policy, and request status
- [ ] AI trend insights verified
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

## First Admin And Role Setup

- [ ] First Supabase Auth admin user created
- [ ] Matching `public.users` row inserted with `role = 'admin'`
- [ ] Manager Auth users mapped to `public.users` with `role = 'manager'`
- [ ] Employee Auth users mapped to `public.users` with `role = 'employee'`
- [ ] Employees assigned to managers through `public.users.manager_id`
- [ ] Departments assigned through `public.users.department_id`
- [ ] Yearly leave balances created for employees

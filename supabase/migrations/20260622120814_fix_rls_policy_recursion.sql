-- Fix recursive RLS policies by moving role/profile checks into private
-- security-definer helpers. The helpers live outside the exposed public schema.

create schema if not exists app_private;
revoke all on schema app_private from public;
grant usage on schema app_private to authenticated;

create or replace function app_private.current_profile_id()
returns bigint
language sql
stable
security definer
set search_path = public
as $$
  select id
  from public.users
  where auth_user_id = auth.uid()
    and is_active = true
  limit 1
$$;

create or replace function app_private.current_profile_role()
returns text
language sql
stable
security definer
set search_path = public
as $$
  select role
  from public.users
  where auth_user_id = auth.uid()
    and is_active = true
  limit 1
$$;

create or replace function app_private.is_admin()
returns boolean
language sql
stable
security definer
set search_path = public
as $$
  select coalesce(app_private.current_profile_role() = 'admin', false)
$$;

create or replace function app_private.is_manager()
returns boolean
language sql
stable
security definer
set search_path = public
as $$
  select coalesce(app_private.current_profile_role() = 'manager', false)
$$;

create or replace function app_private.can_manage_user(target_user_id bigint)
returns boolean
language sql
stable
security definer
set search_path = public
as $$
  select coalesce(
    app_private.is_manager()
    and exists (
      select 1
      from public.users target_profile
      where target_profile.id = target_user_id
        and target_profile.manager_id = app_private.current_profile_id()
    ),
    false
  )
$$;

grant execute on function app_private.current_profile_id() to authenticated;
grant execute on function app_private.current_profile_role() to authenticated;
grant execute on function app_private.is_admin() to authenticated;
grant execute on function app_private.is_manager() to authenticated;
grant execute on function app_private.can_manage_user(bigint) to authenticated;

drop policy if exists "managers read team profiles" on public.users;
drop policy if exists "admins read all profiles" on public.users;
drop policy if exists "employees read own leave balances" on public.leave_balances;
drop policy if exists "managers read team leave balances" on public.leave_balances;
drop policy if exists "admins read all leave balances" on public.leave_balances;
drop policy if exists "employees read own leave requests" on public.leave_requests;
drop policy if exists "employees create own leave requests" on public.leave_requests;
drop policy if exists "managers read team leave requests" on public.leave_requests;
drop policy if exists "admins read all leave requests" on public.leave_requests;
drop policy if exists "users read own notifications" on public.notifications;
drop policy if exists "users update own notifications" on public.notifications;
drop policy if exists "admins read audit logs" on public.audit_logs;

create policy "managers read team profiles"
on public.users for select
to authenticated
using (
  app_private.is_manager()
  and users.manager_id = app_private.current_profile_id()
);

create policy "admins read all profiles"
on public.users for select
to authenticated
using (app_private.is_admin());

create policy "employees read own leave balances"
on public.leave_balances for select
to authenticated
using (leave_balances.user_id = app_private.current_profile_id());

create policy "managers read team leave balances"
on public.leave_balances for select
to authenticated
using (app_private.can_manage_user(leave_balances.user_id));

create policy "admins read all leave balances"
on public.leave_balances for select
to authenticated
using (app_private.is_admin());

create policy "employees read own leave requests"
on public.leave_requests for select
to authenticated
using (leave_requests.employee_id = app_private.current_profile_id());

create policy "employees create own leave requests"
on public.leave_requests for insert
to authenticated
with check (leave_requests.employee_id = app_private.current_profile_id());

create policy "managers read team leave requests"
on public.leave_requests for select
to authenticated
using (
  app_private.is_manager()
  and leave_requests.manager_id = app_private.current_profile_id()
);

create policy "admins read all leave requests"
on public.leave_requests for select
to authenticated
using (app_private.is_admin());

create policy "users read own notifications"
on public.notifications for select
to authenticated
using (notifications.recipient_id = app_private.current_profile_id());

create policy "users update own notifications"
on public.notifications for update
to authenticated
using (notifications.recipient_id = app_private.current_profile_id())
with check (notifications.recipient_id = app_private.current_profile_id());

create policy "admins read audit logs"
on public.audit_logs for select
to authenticated
using (app_private.is_admin());

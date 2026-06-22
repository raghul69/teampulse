from __future__ import annotations

from datetime import date
import os
from typing import Any

import requests
import streamlit as st

API_URL = os.getenv("TEAMPULSE_API_URL", "http://127.0.0.1:8002/api/v1")

# Which panel this Streamlit instance serves: "user" or "admin".
# One codebase, two deployments — selected via the PANEL env var.
# (The Community panel was retired from active deployment; any other value
# falls back to the User Panel so a stale PANEL=community never serves.)
PANEL = os.getenv("PANEL", "user").strip().lower()
if PANEL not in {"user", "admin"}:
    PANEL = "user"

PANEL_META = {
    "user": {"label": "User Panel", "roles": {"employee", "manager"}},
    "admin": {"label": "Admin Panel", "roles": {"admin"}},
}

st.set_page_config(page_title=f"TeamPulse {PANEL_META[PANEL]['label']}", page_icon="TP", layout="wide")


def session() -> dict[str, Any]:
    return st.session_state.get("session") or {}


def user() -> dict[str, Any]:
    return st.session_state.get("user") or {}


def auth_headers() -> dict[str, str]:
    access_token = session().get("access_token")
    return {"Authorization": f"Bearer {access_token}"} if access_token else {}


def refresh_session() -> bool:
    refresh_token = session().get("refresh_token")
    if not refresh_token:
        return False
    response = requests.post(
        f"{API_URL}/auth/refresh",
        json={"refresh_token": refresh_token},
        timeout=15,
    )
    if response.status_code >= 400:
        return False
    st.session_state.session = response.json()
    return True


def api(method: str, path: str, *, protected: bool = True, retry: bool = True, **kwargs):
    headers = kwargs.pop("headers", {})
    if protected:
        headers.update(auth_headers())

    response = requests.request(method, f"{API_URL}{path}", headers=headers, timeout=15, **kwargs)
    if response.status_code == 401 and protected and retry and refresh_session():
        headers.update(auth_headers())
        response = requests.request(method, f"{API_URL}{path}", headers=headers, timeout=15, **kwargs)

    if response.status_code >= 400:
        try:
            detail = response.json().get("detail", response.text)
        except ValueError:
            detail = response.text
        raise RuntimeError(detail)

    return response.json() if response.content else {}


def require_login() -> bool:
    if st.session_state.get("user") and st.session_state.get("session"):
        return True
    login_page()
    return False


def login_page() -> None:
    st.title(f"TeamPulse · {PANEL_META[PANEL]['label']}")
    st.caption("Sign in with your Supabase Auth credentials")

    login_tab, reset_tab, verify_tab = st.tabs(["Login", "Password Reset", "Email Verification"])

    with login_tab:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login", use_container_width=True)
        if submitted:
            try:
                result = api("POST", "/auth/login", protected=False, json={"email": email, "password": password})
                st.session_state.user = result["user"]
                st.session_state.session = result["session"]
                st.rerun()
            except RuntimeError as exc:
                st.error(str(exc))

    with reset_tab:
        with st.form("reset_form"):
            email = st.text_input("Email", key="reset_email")
            submitted = st.form_submit_button("Send Reset Link", use_container_width=True)
        if submitted:
            try:
                api("POST", "/auth/password-reset", protected=False, json={"email": email})
                st.success("Password reset email requested.")
            except RuntimeError as exc:
                st.error(str(exc))

    with verify_tab:
        with st.form("verify_form"):
            email = st.text_input("Email", key="verify_email")
            submitted = st.form_submit_button("Resend Verification", use_container_width=True)
        if submitted:
            try:
                api("POST", "/auth/resend-verification", protected=False, json={"email": email})
                st.success("Verification email requested.")
            except RuntimeError as exc:
                st.error(str(exc))


def logout() -> None:
    try:
        api("POST", "/auth/logout")
    except RuntimeError:
        pass
    st.session_state.clear()
    st.rerun()


def panel_pages(role: str) -> list[str]:
    """Pages available for the given role within the current PANEL."""
    if PANEL == "admin":
        return [
            "Reports Summary",
            "User Management",
            "Department Management",
            "Leave Balance Management",
            "All Leave Requests",
            "Audit Logs",
        ]
    # PANEL == "user": employee + manager self-service pages.
    if role == "manager":
        return ["Team Leave Requests", "Team Members", "Team Leave Calendar"]
    return ["Apply Leave", "Leave Balance", "Leave History", "Notifications"]


def page_shell() -> str | None:
    current_user = user()
    role = current_user.get("role", "")
    label = PANEL_META[PANEL]["label"]

    st.sidebar.markdown(f"### TeamPulse · {label}")
    st.sidebar.caption(f"{current_user.get('full_name', 'User')} · {role.title()}")
    if st.sidebar.button("Logout", use_container_width=True):
        logout()

    # Enforce panel access by role. A user with the wrong role for this panel is
    # authenticated but not authorized here (the backend enforces this too).
    if role not in PANEL_META[PANEL]["roles"]:
        allowed = ", ".join(sorted(PANEL_META[PANEL]["roles"]))
        st.error(f"Your role ({role or 'unknown'}) cannot access the {label}.")
        st.info(f"This panel is for: {allowed}. Use the panel that matches your role.")
        return None

    pages = panel_pages(role)
    return st.sidebar.radio("Dashboard", pages, label_visibility="collapsed")


def metrics_row(items: list[tuple[str, Any]]) -> None:
    cols = st.columns(len(items))
    for col, (label, value) in zip(cols, items):
        col.metric(label, value)


def admin_reports() -> None:
    st.header("Reports Summary")
    summary = api("GET", "/reports/summary")
    metrics_row(
        [
            ("Total Requests", summary["total_requests"]),
            ("Pending", summary["pending_requests"]),
            ("Approved", summary["approved_requests"]),
            ("Approval Rate", f"{summary['approval_rate']}%"),
        ]
    )
    st.caption(f"Popular leave type: {summary['popular_leave_type'].title()} · Generated {summary['generated_on']}")
    st.bar_chart(summary.get("monthly_days", {}))


def admin_users() -> None:
    st.header("User Management")
    users = api("GET", "/users")
    st.dataframe(users, use_container_width=True, hide_index=True)

    with st.expander("Link Supabase user to TeamPulse profile", expanded=False):
        with st.form("create_user"):
            auth_user_id = st.text_input("Supabase auth.users id")
            full_name = st.text_input("Full name")
            email = st.text_input("Email")
            role = st.selectbox("Role", ["employee", "manager", "admin"])
            manager_id = st.number_input("Manager ID", min_value=0, step=1)
            department_id = st.number_input("Department ID", min_value=0, step=1)
            submitted = st.form_submit_button("Create Profile", use_container_width=True)
        if submitted:
            payload = {
                "auth_user_id": auth_user_id,
                "full_name": full_name,
                "email": email,
                "role": role,
                "manager_id": manager_id or None,
                "department_id": department_id or None,
            }
            try:
                api("POST", "/users", json=payload)
                st.success("User profile created.")
                st.rerun()
            except RuntimeError as exc:
                st.error(str(exc))

    with st.expander("Update user", expanded=False):
        user_ids = [item["id"] for item in users]
        if user_ids:
            with st.form("update_user"):
                user_id = st.selectbox("User ID", user_ids)
                full_name = st.text_input("Full name")
                role = st.selectbox("Role", ["", "employee", "manager", "admin"])
                is_active = st.selectbox("Active", ["", "true", "false"])
                submitted = st.form_submit_button("Update User", use_container_width=True)
            if submitted:
                payload: dict[str, Any] = {}
                if full_name:
                    payload["full_name"] = full_name
                if role:
                    payload["role"] = role
                if is_active:
                    payload["is_active"] = is_active == "true"
                try:
                    api("PATCH", f"/users/{user_id}", json=payload)
                    st.success("User updated.")
                    st.rerun()
                except RuntimeError as exc:
                    st.error(str(exc))


def admin_departments() -> None:
    st.header("Department Management")
    departments = api("GET", "/departments")
    st.dataframe(departments, use_container_width=True, hide_index=True)

    left, right = st.columns(2)
    with left:
        st.subheader("Create Department")
        with st.form("create_department"):
            name = st.text_input("Name")
            code = st.text_input("Code")
            manager_id = st.number_input("Manager ID", min_value=0, step=1)
            submitted = st.form_submit_button("Create", use_container_width=True)
        if submitted:
            try:
                api("POST", "/departments", json={"name": name, "code": code, "manager_id": manager_id or None})
                st.success("Department created.")
                st.rerun()
            except RuntimeError as exc:
                st.error(str(exc))

    with right:
        st.subheader("Update Department")
        ids = [item["id"] for item in departments]
        if ids:
            with st.form("update_department"):
                department_id = st.selectbox("Department ID", ids)
                name = st.text_input("New name")
                code = st.text_input("New code")
                manager_id = st.number_input("New manager ID", min_value=0, step=1)
                submitted = st.form_submit_button("Update", use_container_width=True)
            if submitted:
                payload = {key: value for key, value in {"name": name, "code": code}.items() if value}
                payload["manager_id"] = manager_id or None
                try:
                    api("PATCH", f"/departments/{department_id}", json=payload)
                    st.success("Department updated.")
                    st.rerun()
                except RuntimeError as exc:
                    st.error(str(exc))


def admin_balances() -> None:
    st.header("Leave Balance Management")
    balances = api("GET", "/leave-balances")
    st.dataframe(balances, use_container_width=True, hide_index=True)

    left, right = st.columns(2)
    with left:
        st.subheader("Create Balance")
        with st.form("create_balance"):
            user_id = st.number_input("User ID", min_value=1, step=1)
            year = st.number_input("Year", min_value=2020, max_value=2100, value=date.today().year, step=1)
            casual = st.number_input("Casual total", min_value=0, value=12, step=1)
            sick = st.number_input("Sick total", min_value=0, value=10, step=1)
            earned = st.number_input("Earned total", min_value=0, value=15, step=1)
            submitted = st.form_submit_button("Create", use_container_width=True)
        if submitted:
            try:
                api(
                    "POST",
                    "/leave-balances",
                    json={"user_id": user_id, "year": year, "casual_total": casual, "sick_total": sick, "earned_total": earned},
                )
                st.success("Leave balance created.")
                st.rerun()
            except RuntimeError as exc:
                st.error(str(exc))

    with right:
        st.subheader("Update Balance")
        ids = [item["id"] for item in balances]
        if ids:
            with st.form("update_balance"):
                balance_id = st.selectbox("Balance ID", ids)
                casual = st.number_input("Casual total", min_value=0, value=12, step=1, key="upd_casual")
                sick = st.number_input("Sick total", min_value=0, value=10, step=1, key="upd_sick")
                earned = st.number_input("Earned total", min_value=0, value=15, step=1, key="upd_earned")
                submitted = st.form_submit_button("Update", use_container_width=True)
            if submitted:
                try:
                    api("PATCH", f"/leave-balances/{balance_id}", json={"casual_total": casual, "sick_total": sick, "earned_total": earned})
                    st.success("Leave balance updated.")
                    st.rerun()
                except RuntimeError as exc:
                    st.error(str(exc))


def admin_leave_requests() -> None:
    st.header("All Leave Requests")
    requests_data = api("GET", "/leave-requests")
    st.dataframe(requests_data, use_container_width=True, hide_index=True)


def admin_audit_logs() -> None:
    st.header("Audit Logs")
    logs = api("GET", "/audit-logs")
    st.dataframe(logs, use_container_width=True, hide_index=True)


def manager_requests() -> None:
    st.header("Team Leave Requests")
    requests_data = api("GET", "/leave-requests")
    pending = [item for item in requests_data if item["status"] == "pending"]
    metrics_row([("Pending", len(pending)), ("Total Team Requests", len(requests_data))])

    for item in pending:
        with st.container(border=True):
            st.markdown(f"**Request #{item['id']}** · Employee `{item['employee_id']}` · {item['leave_type'].title()}")
            st.write(f"{item['start_date']} to {item['end_date']} · {item['days']} day(s)")
            st.caption(item["reason"])
            try:
                conflicts = api("GET", f"/leave-requests/{item['id']}/conflicts")["warnings"]
                for warning in conflicts:
                    if warning == "No conflicts detected.":
                        st.success(warning)
                    else:
                        st.warning(warning)
            except RuntimeError as exc:
                st.error(str(exc))

            comment = st.text_input("Manager comment", key=f"comment_{item['id']}")
            approve, reject = st.columns(2)
            if approve.button("Approve", key=f"approve_{item['id']}", use_container_width=True):
                api("PATCH", f"/leave-requests/{item['id']}/decision", json={"status": "approved", "manager_comment": comment})
                st.rerun()
            if reject.button("Reject", key=f"reject_{item['id']}", use_container_width=True):
                api("PATCH", f"/leave-requests/{item['id']}/decision", json={"status": "rejected", "manager_comment": comment})
                st.rerun()

    st.subheader("All Team Requests")
    st.dataframe(requests_data, use_container_width=True, hide_index=True)


def manager_team_members() -> None:
    st.header("Team Members")
    st.dataframe(api("GET", "/users/team"), use_container_width=True, hide_index=True)


def manager_calendar() -> None:
    st.header("Team Leave Calendar")
    calendar = api("GET", "/leave-requests/calendar")
    st.dataframe(calendar, use_container_width=True, hide_index=True)


def employee_apply_leave() -> None:
    st.header("Apply Leave")
    with st.form("apply_leave"):
        leave_type = st.selectbox("Leave Type", ["casual", "sick", "earned", "unpaid"])
        start_date = st.date_input("Start Date", min_value=date.today())
        end_date = st.date_input("End Date", min_value=start_date)
        reason = st.text_area("Reason")
        st.info(f"Total days: {(end_date - start_date).days + 1}")
        submitted = st.form_submit_button("Submit Leave Request", use_container_width=True)
    if submitted:
        try:
            api(
                "POST",
                "/leave-requests",
                json={"leave_type": leave_type, "start_date": start_date.isoformat(), "end_date": end_date.isoformat(), "reason": reason},
            )
            st.success("Leave request submitted.")
        except RuntimeError as exc:
            st.error(str(exc))


def employee_balance() -> None:
    st.header("Leave Balance")
    balance = api("GET", "/leave-balances/me")
    metrics_row(
        [
            ("Casual", balance["casual_available"]),
            ("Sick", balance["sick_available"]),
            ("Earned", balance["earned_available"]),
            ("Unpaid Used", balance["unpaid_used"]),
        ]
    )
    st.dataframe([balance], use_container_width=True, hide_index=True)


def employee_history() -> None:
    st.header("Leave History & Status")
    requests_data = api("GET", "/leave-requests")
    metrics_row(
        [
            ("Total", len(requests_data)),
            ("Pending", len([item for item in requests_data if item["status"] == "pending"])),
            ("Approved", len([item for item in requests_data if item["status"] == "approved"])),
        ]
    )
    st.dataframe(requests_data, use_container_width=True, hide_index=True)


def employee_notifications() -> None:
    st.header("Notifications")
    notifications = api("GET", "/notifications")
    unread = [item for item in notifications if not item["is_read"]]
    metrics_row([("Unread", len(unread)), ("Total", len(notifications))])
    for item in notifications:
        with st.container(border=True):
            st.markdown(f"**{item['title']}**")
            st.write(item["message"])
            st.caption(item["created_at"])
            if not item["is_read"] and st.button("Mark read", key=f"read_{item['id']}"):
                api("PATCH", f"/notifications/{item['id']}/read")
                st.rerun()


def main() -> None:
    if not require_login():
        return

    page = page_shell()
    if page is None:
        return
    try:
        if page == "Reports Summary":
            admin_reports()
        elif page == "User Management":
            admin_users()
        elif page == "Department Management":
            admin_departments()
        elif page == "Leave Balance Management":
            admin_balances()
        elif page == "All Leave Requests":
            admin_leave_requests()
        elif page == "Audit Logs":
            admin_audit_logs()
        elif page == "Team Leave Requests":
            manager_requests()
        elif page == "Team Members":
            manager_team_members()
        elif page == "Team Leave Calendar":
            manager_calendar()
        elif page == "Apply Leave":
            employee_apply_leave()
        elif page == "Leave Balance":
            employee_balance()
        elif page == "Leave History":
            employee_history()
        elif page == "Notifications":
            employee_notifications()
    except RuntimeError as exc:
        st.error(str(exc))


if __name__ == "__main__":
    main()

from fastapi import APIRouter

from backend.app.api.v1.routes import announcements, audit_logs, auth, departments, leave_balances, leave_requests, notifications, reports, users

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(departments.router, prefix="/departments", tags=["departments"])
api_router.include_router(leave_balances.router, prefix="/leave-balances", tags=["leave-balances"])
api_router.include_router(leave_requests.router, prefix="/leave-requests", tags=["leave-requests"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(announcements.router, prefix="/announcements", tags=["announcements"])
api_router.include_router(audit_logs.router, prefix="/audit-logs", tags=["audit-logs"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])


@api_router.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}

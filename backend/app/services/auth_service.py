from typing import Any
from uuid import UUID

import httpx
from sqlalchemy.orm import Session

from backend.app.core.enums import AuditAction
from backend.app.core.config import settings
from backend.app.core.exceptions import AppError, UnauthorizedError
from backend.app.models.user import User
from backend.app.schemas.auth import SignupRequest, SupabaseSession
from backend.app.schemas.user import UserCreate
from backend.app.services.audit_service import AuditService
from backend.app.services.user_service import UserService


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserService(db)
        self.audit = AuditService(db)

    def login(self, email: str, password: str) -> tuple[User, SupabaseSession]:
        data = self._auth_request(
            "POST",
            "/token?grant_type=password",
            json={"email": email, "password": password},
            use_service_key=False,
        )
        auth_user = data["user"]
        if settings.REQUIRE_EMAIL_VERIFICATION and not auth_user.get("email_confirmed_at"):
            raise UnauthorizedError("Email verification is required before login")

        user = self.users.get_by_auth_user_id(auth_user["id"])
        if not user:
            raise UnauthorizedError("TeamPulse profile is not linked to this Supabase user")
        if not user.is_active:
            raise UnauthorizedError("Inactive account")
        self.audit.record(actor_id=user.id, action=AuditAction.LOGIN, entity_type="users", entity_id=user.id)
        return user, self._session_from_auth_response(data)

    def signup(self, payload: SignupRequest) -> User:
        data = self._auth_request(
            "POST",
            "/signup",
            json={
                "email": str(payload.email),
                "password": payload.password,
                "data": {"full_name": payload.full_name},
            },
            use_service_key=False,
        )
        auth_user_id = data["user"]["id"]
        user = self.users.create_user(
            UserCreate(
                auth_user_id=UUID(auth_user_id),
                full_name=payload.full_name,
                email=payload.email,
                role=payload.role,
                manager_id=payload.manager_id,
                department_id=payload.department_id,
            )
        )
        self.audit.record(actor_id=user.id, action=AuditAction.CREATE, entity_type="users", entity_id=user.id)
        return user

    def refresh(self, refresh_token: str) -> SupabaseSession:
        data = self._auth_request(
            "POST",
            "/token?grant_type=refresh_token",
            json={"refresh_token": refresh_token},
            use_service_key=False,
        )
        return self._session_from_auth_response(data)

    def send_password_reset(self, email: str, redirect_to: str | None = None) -> None:
        payload: dict[str, Any] = {"email": email}
        if redirect_to:
            payload["redirect_to"] = redirect_to
        self._auth_request("POST", "/recover", json=payload, use_service_key=False)

    def resend_email_verification(self, email: str) -> None:
        self._auth_request(
            "POST",
            "/resend",
            json={"type": "signup", "email": email},
            use_service_key=False,
        )

    def logout(self, access_token: str) -> None:
        self._auth_request(
            "POST",
            "/logout",
            json={},
            bearer_token=access_token,
            use_service_key=False,
        )

    def _auth_request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any],
        use_service_key: bool,
        bearer_token: str | None = None,
    ) -> dict[str, Any]:
        api_key = settings.SUPABASE_SERVICE_ROLE_KEY if use_service_key else settings.SUPABASE_PUBLISHABLE_KEY
        if not api_key:
            raise AppError("Supabase API key is not configured", 500)
        headers = {"apikey": api_key, "Content-Type": "application/json"}
        if bearer_token:
            headers["Authorization"] = f"Bearer {bearer_token}"
        else:
            headers["Authorization"] = f"Bearer {api_key}"

        response = httpx.request(
            method,
            f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1{path}",
            headers=headers,
            json=json,
            timeout=settings.SUPABASE_AUTH_VERIFY_TIMEOUT_SECONDS,
        )
        if response.status_code >= 400:
            detail = response.json().get("msg") if response.headers.get("content-type", "").startswith("application/json") else response.text
            raise UnauthorizedError(detail or "Supabase authentication failed")
        return response.json() if response.content else {}

    def _session_from_auth_response(self, data: dict[str, Any]) -> SupabaseSession:
        return SupabaseSession(
            access_token=data["access_token"],
            refresh_token=data["refresh_token"],
            token_type=data.get("token_type", "bearer"),
            expires_in=data.get("expires_in"),
        )

from __future__ import annotations

from collections.abc import Awaitable, Callable

from fastapi import Request, Response

from backend.app.core.security import verify_supabase_access_token
from backend.app.db.session import SessionLocal
from backend.app.services.user_service import UserService


async def supabase_auth_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    request.state.auth_payload = None
    request.state.current_user = None

    authorization = request.headers.get("Authorization", "")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() == "bearer" and token:
        try:
            payload = verify_supabase_access_token(token)
            request.state.auth_payload = payload
            with SessionLocal() as db:
                request.state.current_user = UserService(db).get_by_auth_user_id(payload["sub"])
        except Exception:
            request.state.auth_payload = None
            request.state.current_user = None

    return await call_next(request)

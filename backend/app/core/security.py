from __future__ import annotations

import time
from typing import Any

import httpx
import jwt
from jwt import PyJWKClient

from backend.app.core.config import settings
from backend.app.core.exceptions import UnauthorizedError

JWKS_CACHE_SECONDS = 600

_jwks_client: PyJWKClient | None = None
_jwks_client_loaded_at = 0.0


def _auth_base_url() -> str:
    return f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1"


def _get_jwks_client() -> PyJWKClient:
    global _jwks_client, _jwks_client_loaded_at
    now = time.time()
    if _jwks_client is None or now - _jwks_client_loaded_at > JWKS_CACHE_SECONDS:
        _jwks_client = PyJWKClient(f"{_auth_base_url()}/.well-known/jwks.json")
        _jwks_client_loaded_at = now
    return _jwks_client


def verify_supabase_access_token(access_token: str) -> dict[str, Any]:
    try:
        signing_key = _get_jwks_client().get_signing_key_from_jwt(access_token)
        return jwt.decode(
            access_token,
            signing_key.key,
            algorithms=["RS256", "ES256"],
            audience=settings.SUPABASE_JWT_AUDIENCE,
            issuer=_auth_base_url(),
            options={"require": ["exp", "sub", "iss"]},
        )
    except Exception:
        return _verify_with_auth_server(access_token)


def _verify_with_auth_server(access_token: str) -> dict[str, Any]:
    try:
        response = httpx.get(
            f"{_auth_base_url()}/user",
            headers={
                "apikey": settings.SUPABASE_PUBLISHABLE_KEY,
                "Authorization": f"Bearer {access_token}",
            },
            timeout=settings.SUPABASE_AUTH_VERIFY_TIMEOUT_SECONDS,
        )
    except httpx.HTTPError as exc:
        raise UnauthorizedError("Unable to validate Supabase session") from exc

    if response.status_code != 200:
        raise UnauthorizedError("Invalid or expired Supabase session")

    user = response.json()
    return {
        "sub": user["id"],
        "email": user.get("email"),
        "aud": settings.SUPABASE_JWT_AUDIENCE,
        "email_confirmed_at": user.get("email_confirmed_at"),
        "raw_app_meta_data": user.get("app_metadata", {}),
    }

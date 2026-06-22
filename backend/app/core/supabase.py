from functools import lru_cache

from supabase import Client, create_client

from backend.app.core.config import settings
from backend.app.core.exceptions import AppError


def _publishable_key() -> str:
    return settings.SUPABASE_PUBLISHABLE_KEY or settings.NEXT_PUBLIC_SUPABASE_ANON_KEY or ""


def _supabase_url() -> str:
    return settings.SUPABASE_URL or settings.NEXT_PUBLIC_SUPABASE_URL or ""


@lru_cache
def get_supabase_client() -> Client:
    url = _supabase_url()
    key = _publishable_key()
    if not url or not key:
        raise AppError("Supabase client is not configured", 500)
    return create_client(url, key)


@lru_cache
def get_supabase_admin_client() -> Client:
    url = _supabase_url()
    if not settings.SUPABASE_SERVICE_ROLE_KEY:
        raise AppError("Supabase service role key is not configured", 500)
    return create_client(url, settings.SUPABASE_SERVICE_ROLE_KEY)

from pydantic import BaseModel, EmailStr

from backend.app.core.enums import UserRole
from backend.app.schemas.user import UserRead


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class SignupRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.EMPLOYEE
    manager_id: int | None = None
    department_id: int | None = None


class SupabaseSession(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int | None = None


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class PasswordResetRequest(BaseModel):
    email: EmailStr
    redirect_to: str | None = None


class AuthResponse(BaseModel):
    user: UserRead
    session: SupabaseSession


class MessageResponse(BaseModel):
    message: str

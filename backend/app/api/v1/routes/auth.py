from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from backend.app.schemas.auth import (
    AuthResponse,
    LoginRequest,
    MessageResponse,
    PasswordResetRequest,
    RefreshTokenRequest,
    SignupRequest,
    SupabaseSession,
)
from backend.app.schemas.user import UserRead
from backend.app.services.auth_service import AuthService

router = APIRouter()
bearer_scheme = HTTPBearer(auto_error=False)


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> AuthResponse:
    service = AuthService(db)
    user, session = service.login(str(payload.email), payload.password)
    db.commit()
    return AuthResponse(user=UserRead.model_validate(user), session=session)


@router.post("/signup", response_model=UserRead)
def signup(payload: SignupRequest, db: Session = Depends(get_db)) -> UserRead:
    user = AuthService(db).signup(payload)
    db.commit()
    db.refresh(user)
    return UserRead.model_validate(user)


@router.post("/refresh", response_model=SupabaseSession)
def refresh(payload: RefreshTokenRequest, db: Session = Depends(get_db)) -> SupabaseSession:
    return AuthService(db).refresh(payload.refresh_token)


@router.post("/password-reset", response_model=MessageResponse)
def password_reset(payload: PasswordResetRequest, db: Session = Depends(get_db)) -> MessageResponse:
    AuthService(db).send_password_reset(str(payload.email), payload.redirect_to)
    return MessageResponse(message="Password reset email requested")


@router.post("/resend-verification", response_model=MessageResponse)
def resend_verification(payload: PasswordResetRequest, db: Session = Depends(get_db)) -> MessageResponse:
    AuthService(db).resend_email_verification(str(payload.email))
    return MessageResponse(message="Verification email requested")


@router.post("/logout", response_model=MessageResponse)
def logout(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> MessageResponse:
    if credentials:
        AuthService(db).logout(credentials.credentials)
    return MessageResponse(message="Logged out")

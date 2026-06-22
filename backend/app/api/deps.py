from collections.abc import Callable

from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.enums import UserRole
from backend.app.core.exceptions import ForbiddenError, UnauthorizedError
from backend.app.core.security import verify_supabase_access_token
from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.services.user_service import UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/login")


def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    if getattr(request.state, "current_user", None):
        return request.state.current_user

    payload = verify_supabase_access_token(token)
    auth_user_id = payload.get("sub")
    if not auth_user_id:
        raise UnauthorizedError("Invalid Supabase token subject")

    user = UserService(db).get_by_auth_user_id(auth_user_id)
    if not user or not user.is_active:
        raise UnauthorizedError("User is inactive or no longer exists")
    return user


def require_roles(*roles: UserRole) -> Callable[[User], User]:
    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise ForbiddenError()
        return current_user

    return dependency


def require_employee(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.EMPLOYEE:
        raise ForbiddenError("Employee access required")
    return current_user


def require_manager(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role not in {UserRole.MANAGER, UserRole.ADMIN}:
        raise ForbiddenError("Manager access required")
    return current_user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.ADMIN:
        raise ForbiddenError("Admin access required")
    return current_user


CurrentUser = Depends(get_current_user)
EmployeeUser = Depends(require_employee)
AdminUser = Depends(require_admin)
ManagerUser = Depends(require_manager)

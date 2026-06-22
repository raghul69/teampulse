from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr

from backend.app.core.enums import UserRole
from backend.app.schemas.base import ORMModel


class UserCreate(BaseModel):
    auth_user_id: UUID
    full_name: str
    email: EmailStr
    role: UserRole = UserRole.EMPLOYEE
    manager_id: int | None = None
    department_id: int | None = None


class UserUpdate(BaseModel):
    full_name: str | None = None
    role: UserRole | None = None
    manager_id: int | None = None
    department_id: int | None = None
    is_active: bool | None = None


class UserRead(ORMModel):
    id: int
    auth_user_id: UUID
    full_name: str
    email: EmailStr
    role: UserRole
    is_active: bool
    manager_id: int | None
    department_id: int | None
    created_at: datetime

from datetime import datetime

from pydantic import BaseModel, Field

from backend.app.core.enums import UserRole
from backend.app.schemas.base import ORMModel


class LeavePolicyCreate(BaseModel):
    leave_type_code: str
    department_id: int | None = None
    role: UserRole | None = None
    annual_allowance: int = Field(default=0, ge=0)
    carry_forward_allowed: bool = False
    max_carry_forward: int = Field(default=0, ge=0)
    min_notice_days: int = Field(default=0, ge=0)
    allow_half_day: bool = False
    is_active: bool = True


class LeavePolicyUpdate(BaseModel):
    annual_allowance: int | None = Field(default=None, ge=0)
    carry_forward_allowed: bool | None = None
    max_carry_forward: int | None = Field(default=None, ge=0)
    min_notice_days: int | None = Field(default=None, ge=0)
    allow_half_day: bool | None = None
    is_active: bool | None = None


class LeavePolicyRead(ORMModel):
    id: int
    leave_type_code: str
    department_id: int | None
    role: str | None
    annual_allowance: int
    carry_forward_allowed: bool
    max_carry_forward: int
    min_notice_days: int
    allow_half_day: bool
    is_active: bool
    created_at: datetime

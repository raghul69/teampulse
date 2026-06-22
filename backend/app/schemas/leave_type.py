from datetime import datetime

from pydantic import BaseModel, Field

from backend.app.schemas.base import ORMModel


class LeaveTypeCreate(BaseModel):
    code: str = Field(min_length=2, max_length=40)
    name: str = Field(min_length=2, max_length=120)
    description: str | None = None
    is_paid: bool = True
    requires_balance: bool = True
    requires_approval: bool = True
    max_days_per_request: int | None = Field(default=None, ge=1)
    is_active: bool = True


class LeaveTypeUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    description: str | None = None
    is_paid: bool | None = None
    requires_balance: bool | None = None
    requires_approval: bool | None = None
    max_days_per_request: int | None = Field(default=None, ge=1)
    is_active: bool | None = None


class LeaveTypeRead(ORMModel):
    id: int
    code: str
    name: str
    description: str | None
    is_paid: bool
    requires_balance: bool
    requires_approval: bool
    max_days_per_request: int | None
    is_active: bool
    created_at: datetime

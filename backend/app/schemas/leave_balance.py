from datetime import datetime

from pydantic import BaseModel, Field

from backend.app.schemas.base import ORMModel


class LeaveBalanceCreate(BaseModel):
    user_id: int
    year: int
    casual_total: int = Field(default=12, ge=0)
    sick_total: int = Field(default=10, ge=0)
    earned_total: int = Field(default=15, ge=0)


class LeaveBalanceUpdate(BaseModel):
    casual_total: int | None = Field(default=None, ge=0)
    sick_total: int | None = Field(default=None, ge=0)
    earned_total: int | None = Field(default=None, ge=0)


class LeaveBalanceRead(ORMModel):
    id: int
    user_id: int
    year: int
    casual_total: int
    casual_used: int
    sick_total: int
    sick_used: int
    earned_total: int
    earned_used: int
    unpaid_used: int
    casual_available: int
    sick_available: int
    earned_available: int
    created_at: datetime

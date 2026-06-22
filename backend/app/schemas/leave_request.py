from datetime import date, datetime

from pydantic import BaseModel, Field, model_validator

from backend.app.core.enums import LeaveStatus, LeaveType
from backend.app.schemas.base import ORMModel


class LeaveRequestCreate(BaseModel):
    leave_type: LeaveType
    start_date: date
    end_date: date
    reason: str = Field(min_length=3, max_length=1000)

    @model_validator(mode="after")
    def validate_date_range(self) -> "LeaveRequestCreate":
        if self.end_date < self.start_date:
            raise ValueError("end_date must be greater than or equal to start_date")
        return self


class LeaveDecision(BaseModel):
    status: LeaveStatus
    manager_comment: str | None = Field(default=None, max_length=1000)

    @model_validator(mode="after")
    def validate_decision_status(self) -> "LeaveDecision":
        if self.status not in {LeaveStatus.APPROVED, LeaveStatus.REJECTED}:
            raise ValueError("Only approved or rejected decisions are allowed")
        return self


class LeaveRequestRead(ORMModel):
    id: int
    employee_id: int
    manager_id: int | None
    leave_type: LeaveType
    status: LeaveStatus
    start_date: date
    end_date: date
    days: int
    reason: str
    manager_comment: str | None
    created_at: datetime
    decided_at: datetime | None

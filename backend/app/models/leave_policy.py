from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.session import Base


class LeavePolicy(Base):
    __tablename__ = "leave_policies"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    leave_type_code: Mapped[str] = mapped_column(ForeignKey("leave_types.code"), nullable=False, index=True)
    department_id: Mapped[int | None] = mapped_column(ForeignKey("departments.id"), nullable=True, index=True)
    role: Mapped[str | None] = mapped_column(String(40), nullable=True)
    annual_allowance: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    carry_forward_allowed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    max_carry_forward: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    min_notice_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    allow_half_day: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

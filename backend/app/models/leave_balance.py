from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.session import Base

if TYPE_CHECKING:
    from backend.app.models.user import User


class LeaveBalance(Base):
    __tablename__ = "leave_balances"
    __table_args__ = (UniqueConstraint("user_id", "year", name="uq_leave_balance_user_year"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    casual_total: Mapped[int] = mapped_column(Integer, default=12, nullable=False)
    casual_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    sick_total: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    sick_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    earned_total: Mapped[int] = mapped_column(Integer, default=15, nullable=False)
    earned_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    unpaid_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user: Mapped[User] = relationship("User", back_populates="leave_balance")

    @property
    def casual_available(self) -> int:
        return self.casual_total - self.casual_used

    @property
    def sick_available(self) -> int:
        return self.sick_total - self.sick_used

    @property
    def earned_available(self) -> int:
        return self.earned_total - self.earned_used

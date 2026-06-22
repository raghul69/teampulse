from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.enums import LeaveType
from backend.app.models.leave_balance import LeaveBalance
from backend.app.schemas.leave_balance import LeaveBalanceCreate, LeaveBalanceUpdate


class LeaveBalanceService:
    def __init__(self, db: Session):
        self.db = db

    def get_for_user(self, user_id: int, year: int | None = None) -> LeaveBalance | None:
        balance_year = year or date.today().year
        return self.db.scalar(
            select(LeaveBalance).where(LeaveBalance.user_id == user_id, LeaveBalance.year == balance_year)
        )

    def list_balances(self, year: int | None = None) -> list[LeaveBalance]:
        statement = select(LeaveBalance).order_by(LeaveBalance.user_id)
        if year:
            statement = statement.where(LeaveBalance.year == year)
        return list(self.db.scalars(statement))

    def create_balance(self, payload: LeaveBalanceCreate) -> LeaveBalance:
        balance = LeaveBalance(**payload.model_dump())
        self.db.add(balance)
        self.db.flush()
        return balance

    def update_balance(self, balance: LeaveBalance, payload: LeaveBalanceUpdate) -> LeaveBalance:
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(balance, field, value)
        self.db.flush()
        return balance

    def consume(self, balance: LeaveBalance, leave_type: LeaveType, days: int) -> None:
        if leave_type == LeaveType.CASUAL:
            balance.casual_used += days
        elif leave_type == LeaveType.SICK:
            balance.sick_used += days
        elif leave_type == LeaveType.EARNED:
            balance.earned_used += days
        else:
            balance.unpaid_used += days
        self.db.flush()

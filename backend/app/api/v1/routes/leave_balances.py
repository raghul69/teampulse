from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.api.deps import AdminUser, get_current_user
from backend.app.core.exceptions import ForbiddenError, NotFoundError
from backend.app.db.session import get_db
from backend.app.models.leave_balance import LeaveBalance
from backend.app.models.user import User
from backend.app.schemas.leave_balance import LeaveBalanceCreate, LeaveBalanceRead, LeaveBalanceUpdate
from backend.app.services.leave_balance_service import LeaveBalanceService

router = APIRouter()


@router.get("/me", response_model=LeaveBalanceRead)
def my_balance(
    year: int = date.today().year,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    balance = LeaveBalanceService(db).get_for_user(current_user.id, year)
    if not balance:
        raise NotFoundError("Leave balance not found")
    return balance


@router.get("", response_model=list[LeaveBalanceRead], dependencies=[AdminUser])
def list_balances(year: int | None = None, db: Session = Depends(get_db)):
    return LeaveBalanceService(db).list_balances(year)


@router.get("/users/{user_id}", response_model=LeaveBalanceRead)
def user_balance(
    user_id: int,
    year: int = date.today().year,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.id != user_id and current_user.role.value not in {"manager", "admin"}:
        raise ForbiddenError()
    balance = LeaveBalanceService(db).get_for_user(user_id, year)
    if not balance:
        raise NotFoundError("Leave balance not found")
    return balance


@router.post("", response_model=LeaveBalanceRead, dependencies=[AdminUser])
def create_balance(payload: LeaveBalanceCreate, db: Session = Depends(get_db)):
    balance = LeaveBalanceService(db).create_balance(payload)
    db.commit()
    db.refresh(balance)
    return balance


@router.patch("/{balance_id}", response_model=LeaveBalanceRead, dependencies=[AdminUser])
def update_balance(balance_id: int, payload: LeaveBalanceUpdate, db: Session = Depends(get_db)):
    service = LeaveBalanceService(db)
    balance = db.get(LeaveBalance, balance_id)
    if not balance:
        raise NotFoundError("Leave balance not found")
    updated = service.update_balance(balance, payload)
    db.commit()
    db.refresh(updated)
    return updated

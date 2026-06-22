from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.api.deps import AdminUser
from backend.app.core.exceptions import NotFoundError
from backend.app.db.session import get_db
from backend.app.models.holiday import Holiday
from backend.app.models.leave_policy import LeavePolicy
from backend.app.models.leave_type import LeaveTypeConfig
from backend.app.schemas.holiday import HolidayCreate, HolidayRead
from backend.app.schemas.leave_policy import LeavePolicyCreate, LeavePolicyRead, LeavePolicyUpdate
from backend.app.schemas.leave_type import LeaveTypeCreate, LeaveTypeRead, LeaveTypeUpdate
from backend.app.services.policy_service import PolicyService

router = APIRouter()


@router.get("/leave-types", response_model=list[LeaveTypeRead])
def list_leave_types(db: Session = Depends(get_db)) -> list[LeaveTypeConfig]:
    return PolicyService(db).list_leave_types()


@router.post("/leave-types", response_model=LeaveTypeRead, dependencies=[AdminUser])
def create_leave_type(payload: LeaveTypeCreate, db: Session = Depends(get_db)) -> LeaveTypeConfig:
    item = PolicyService(db).create_leave_type(payload)
    db.commit()
    db.refresh(item)
    return item


@router.patch("/leave-types/{code}", response_model=LeaveTypeRead, dependencies=[AdminUser])
def update_leave_type(code: str, payload: LeaveTypeUpdate, db: Session = Depends(get_db)) -> LeaveTypeConfig:
    service = PolicyService(db)
    item = service.get_leave_type(code)
    if not item:
        raise NotFoundError("Leave type not found")
    updated = service.update_leave_type(item, payload)
    db.commit()
    db.refresh(updated)
    return updated


@router.get("/leave-policies", response_model=list[LeavePolicyRead])
def list_policies(db: Session = Depends(get_db)) -> list[LeavePolicy]:
    return PolicyService(db).list_policies()


@router.post("/leave-policies", response_model=LeavePolicyRead, dependencies=[AdminUser])
def create_policy(payload: LeavePolicyCreate, db: Session = Depends(get_db)) -> LeavePolicy:
    policy = PolicyService(db).create_policy(payload)
    db.commit()
    db.refresh(policy)
    return policy


@router.patch("/leave-policies/{policy_id}", response_model=LeavePolicyRead, dependencies=[AdminUser])
def update_policy(policy_id: int, payload: LeavePolicyUpdate, db: Session = Depends(get_db)) -> LeavePolicy:
    service = PolicyService(db)
    policy = db.get(LeavePolicy, policy_id)
    if not policy:
        raise NotFoundError("Leave policy not found")
    updated = service.update_policy(policy, payload)
    db.commit()
    db.refresh(updated)
    return updated


@router.get("/holidays", response_model=list[HolidayRead])
def list_holidays(db: Session = Depends(get_db)) -> list[Holiday]:
    return PolicyService(db).list_holidays()


@router.post("/holidays", response_model=HolidayRead, dependencies=[AdminUser])
def create_holiday(payload: HolidayCreate, db: Session = Depends(get_db)) -> Holiday:
    holiday = PolicyService(db).create_holiday(payload)
    db.commit()
    db.refresh(holiday)
    return holiday

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.api.deps import ManagerUser, get_current_user
from backend.app.core.enums import UserRole
from backend.app.core.exceptions import ForbiddenError, NotFoundError
from backend.app.db.session import get_db
from backend.app.models.leave_request import LeaveRequest
from backend.app.models.user import User
from backend.app.schemas.leave_request import LeaveDecision, LeaveRequestCreate, LeaveRequestRead
from backend.app.services.leave_request_service import LeaveRequestService

router = APIRouter()


@router.get("", response_model=list[LeaveRequestRead])
def list_leave_requests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[LeaveRequest]:
    service = LeaveRequestService(db)
    if current_user.role == UserRole.ADMIN:
        return service.list_all()
    if current_user.role == UserRole.MANAGER:
        return service.list_for_manager(current_user)
    return service.list_for_user(current_user)


@router.get("/calendar")
def team_leave_calendar(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[dict]:
    service = LeaveRequestService(db)
    if current_user.role == UserRole.ADMIN:
        return [
            {
                "id": item.id,
                "employee_id": item.employee_id,
                "leave_type": item.leave_type,
                "status": item.status,
                "start_date": item.start_date,
                "end_date": item.end_date,
                "days": item.days,
            }
            for item in service.list_all()
        ]
    if current_user.role != UserRole.MANAGER:
        raise ForbiddenError("Manager access required")
    return service.team_calendar(current_user)


@router.get("/{request_id}/conflicts")
def leave_request_conflicts(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, list[str]]:
    request = db.get(LeaveRequest, request_id)
    if not request:
        raise NotFoundError("Leave request not found")
    if current_user.role != UserRole.ADMIN and request.manager_id != current_user.id and request.employee_id != current_user.id:
        raise ForbiddenError()
    return {"warnings": LeaveRequestService(db).conflict_warnings(request)}


@router.post("", response_model=LeaveRequestRead)
def apply_leave(
    payload: LeaveRequestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> LeaveRequest:
    request = LeaveRequestService(db).create(current_user, payload)
    db.commit()
    db.refresh(request)
    return request


@router.patch("/{request_id}/decision", response_model=LeaveRequestRead, dependencies=[ManagerUser])
def decide_leave_request(
    request_id: int,
    payload: LeaveDecision,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> LeaveRequest:
    request = LeaveRequestService(db).decide(request_id, current_user, payload)
    db.commit()
    db.refresh(request)
    return request

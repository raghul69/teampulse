from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.api.deps import AdminUser
from backend.app.db.session import get_db
from backend.app.services.leave_request_service import LeaveRequestService

router = APIRouter()


@router.get("/summary", dependencies=[AdminUser])
def reports_summary(db: Session = Depends(get_db)) -> dict:
    return LeaveRequestService(db).reports_summary()

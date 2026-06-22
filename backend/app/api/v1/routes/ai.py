from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.api.deps import get_current_user
from backend.app.core.enums import UserRole
from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.services.ai_service import LeaveAIService
from backend.app.services.leave_balance_service import LeaveBalanceService
from backend.app.services.leave_request_service import LeaveRequestService

router = APIRouter()


class RecommendationRequest(BaseModel):
    reason: str


class AssistantRequest(BaseModel):
    question: str


@router.post("/recommend-leave")
def recommend_leave(payload: RecommendationRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    history = LeaveRequestService(db).list_for_user(current_user)
    balance = LeaveBalanceService(db).get_for_user(current_user.id)
    return LeaveAIService().recommend_leave_type(payload.reason, balance, history)


@router.get("/insights")
def insights(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    service = LeaveRequestService(db)
    requests = service.list_all() if current_user.role == UserRole.ADMIN else service.list_for_manager(current_user) if current_user.role == UserRole.MANAGER else service.list_for_user(current_user)
    return LeaveAIService().trend_insights(requests)


@router.post("/assistant")
def assistant(payload: AssistantRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    requests = LeaveRequestService(db).list_for_user(current_user)
    balance = LeaveBalanceService(db).get_for_user(current_user.id)
    return {"answer": LeaveAIService().assistant_answer(payload.question, balance, requests)}

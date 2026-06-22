from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.api.deps import get_current_user
from backend.app.core.exceptions import ForbiddenError, NotFoundError
from backend.app.db.session import get_db
from backend.app.models.notification import Notification
from backend.app.models.user import User
from backend.app.schemas.notification import NotificationRead
from backend.app.services.notification_service import NotificationService

router = APIRouter()


@router.get("", response_model=list[NotificationRead])
def list_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Notification]:
    return NotificationService(db).list_for_user(current_user.id)


@router.patch("/{notification_id}/read", response_model=NotificationRead)
def mark_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Notification:
    notification = db.get(Notification, notification_id)
    if not notification:
        raise NotFoundError("Notification not found")
    if notification.recipient_id != current_user.id:
        raise ForbiddenError()
    updated = NotificationService(db).mark_read(notification)
    db.commit()
    db.refresh(updated)
    return updated

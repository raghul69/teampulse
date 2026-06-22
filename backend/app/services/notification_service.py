from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.notification import Notification
from backend.app.schemas.notification import NotificationCreate


class NotificationService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, payload: NotificationCreate) -> Notification:
        notification = Notification(**payload.model_dump())
        self.db.add(notification)
        self.db.flush()
        return notification

    def list_for_user(self, user_id: int) -> list[Notification]:
        return list(
            self.db.scalars(
                select(Notification)
                .where(Notification.recipient_id == user_id)
                .order_by(Notification.created_at.desc())
            )
        )

    def mark_read(self, notification: Notification) -> Notification:
        notification.is_read = True
        self.db.flush()
        return notification

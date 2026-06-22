from datetime import datetime

from pydantic import BaseModel

from backend.app.core.enums import NotificationType
from backend.app.schemas.base import ORMModel


class NotificationCreate(BaseModel):
    recipient_id: int
    notification_type: NotificationType = NotificationType.INFO
    title: str
    message: str


class NotificationRead(ORMModel):
    id: int
    recipient_id: int
    notification_type: NotificationType
    title: str
    message: str
    is_read: bool
    created_at: datetime

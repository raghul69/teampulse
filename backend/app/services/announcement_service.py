from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from backend.app.models.announcement import Announcement
from backend.app.schemas.announcement import AnnouncementCreate, AnnouncementUpdate


class AnnouncementService:
    def __init__(self, db: Session):
        self.db = db

    def list_announcements(self, *, active_only: bool) -> list[Announcement]:
        statement = select(Announcement).options(joinedload(Announcement.author))
        if active_only:
            statement = statement.where(Announcement.is_active.is_(True))
        statement = statement.order_by(Announcement.created_at.desc())
        return list(self.db.scalars(statement))

    def create(self, payload: AnnouncementCreate, *, author_id: int) -> Announcement:
        announcement = Announcement(**payload.model_dump(), author_id=author_id)
        self.db.add(announcement)
        self.db.flush()
        return announcement

    def update(self, announcement: Announcement, payload: AnnouncementUpdate) -> Announcement:
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(announcement, field, value)
        self.db.flush()
        return announcement

    def delete(self, announcement: Announcement) -> None:
        self.db.delete(announcement)
        self.db.flush()

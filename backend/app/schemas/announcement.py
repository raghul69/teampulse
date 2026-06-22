from datetime import datetime

from pydantic import BaseModel

from backend.app.schemas.base import ORMModel


class AnnouncementCreate(BaseModel):
    title: str
    content: str
    is_active: bool = True


class AnnouncementUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    is_active: bool | None = None


class AnnouncementRead(ORMModel):
    id: int
    title: str
    content: str
    author_id: int
    author_name: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime | None = None

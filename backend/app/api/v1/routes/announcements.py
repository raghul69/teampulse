from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.api.deps import get_current_user, require_admin
from backend.app.core.enums import AuditAction, UserRole
from backend.app.core.exceptions import NotFoundError
from backend.app.db.session import get_db
from backend.app.models.announcement import Announcement
from backend.app.models.user import User
from backend.app.schemas.announcement import AnnouncementCreate, AnnouncementRead, AnnouncementUpdate
from backend.app.services.announcement_service import AnnouncementService
from backend.app.services.audit_service import AuditService

router = APIRouter()


def _to_read(announcement: Announcement) -> AnnouncementRead:
    data = AnnouncementRead.model_validate(announcement)
    if announcement.author is not None:
        data.author_name = announcement.author.full_name
    return data


@router.get("", response_model=list[AnnouncementRead])
def list_announcements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[AnnouncementRead]:
    # Admins see every announcement (including deactivated); everyone else sees active ones.
    active_only = current_user.role != UserRole.ADMIN
    announcements = AnnouncementService(db).list_announcements(active_only=active_only)
    return [_to_read(item) for item in announcements]


@router.post("", response_model=AnnouncementRead, dependencies=[Depends(require_admin)])
def create_announcement(
    payload: AnnouncementCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AnnouncementRead:
    service = AnnouncementService(db)
    announcement = service.create(payload, author_id=current_user.id)
    AuditService(db).record(
        actor_id=current_user.id,
        action=AuditAction.CREATE,
        entity_type="announcements",
        entity_id=announcement.id,
    )
    db.commit()
    db.refresh(announcement)
    return _to_read(announcement)


@router.patch("/{announcement_id}", response_model=AnnouncementRead, dependencies=[Depends(require_admin)])
def update_announcement(
    announcement_id: int,
    payload: AnnouncementUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AnnouncementRead:
    service = AnnouncementService(db)
    announcement = db.get(Announcement, announcement_id)
    if not announcement:
        raise NotFoundError("Announcement not found")
    updated = service.update(announcement, payload)
    AuditService(db).record(
        actor_id=current_user.id,
        action=AuditAction.UPDATE,
        entity_type="announcements",
        entity_id=updated.id,
    )
    db.commit()
    db.refresh(updated)
    return _to_read(updated)


@router.delete("/{announcement_id}", dependencies=[Depends(require_admin)])
def delete_announcement(
    announcement_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    service = AnnouncementService(db)
    announcement = db.get(Announcement, announcement_id)
    if not announcement:
        raise NotFoundError("Announcement not found")
    service.delete(announcement)
    AuditService(db).record(
        actor_id=current_user.id,
        action=AuditAction.DELETE,
        entity_type="announcements",
        entity_id=announcement_id,
    )
    db.commit()
    return {"detail": "Announcement deleted"}

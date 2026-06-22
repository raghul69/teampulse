from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.api.deps import AdminUser
from backend.app.db.session import get_db
from backend.app.models.audit_log import AuditLog
from backend.app.schemas.audit_log import AuditLogRead
from backend.app.services.audit_service import AuditService

router = APIRouter()


@router.get("", response_model=list[AuditLogRead], dependencies=[AdminUser])
def list_audit_logs(limit: int = 100, db: Session = Depends(get_db)) -> list[AuditLog]:
    return AuditService(db).list_logs(limit=limit)

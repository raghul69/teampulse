from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.enums import AuditAction
from backend.app.models.audit_log import AuditLog


class AuditService:
    def __init__(self, db: Session):
        self.db = db

    def record(
        self,
        *,
        actor_id: int | None,
        action: AuditAction,
        entity_type: str,
        entity_id: int | None = None,
        old_values: dict[str, Any] | None = None,
        new_values: dict[str, Any] | None = None,
        ip_address: str | None = None,
    ) -> AuditLog:
        log = AuditLog(
            actor_id=actor_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
        )
        self.db.add(log)
        self.db.flush()
        return log

    def list_logs(self, limit: int = 100) -> list[AuditLog]:
        return list(self.db.scalars(select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit)))

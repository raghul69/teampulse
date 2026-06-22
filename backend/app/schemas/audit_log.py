from datetime import datetime
from typing import Any

from backend.app.core.enums import AuditAction
from backend.app.schemas.base import ORMModel


class AuditLogRead(ORMModel):
    id: int
    actor_id: int | None
    action: AuditAction
    entity_type: str
    entity_id: int | None
    old_values: dict[str, Any] | None
    new_values: dict[str, Any] | None
    ip_address: str | None
    created_at: datetime

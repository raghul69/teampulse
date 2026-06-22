from datetime import datetime

from pydantic import BaseModel

from backend.app.schemas.base import ORMModel


class DepartmentCreate(BaseModel):
    name: str
    code: str
    manager_id: int | None = None


class DepartmentUpdate(BaseModel):
    name: str | None = None
    code: str | None = None
    manager_id: int | None = None


class DepartmentRead(ORMModel):
    id: int
    name: str
    code: str
    manager_id: int | None
    created_at: datetime

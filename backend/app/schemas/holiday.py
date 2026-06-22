from datetime import date, datetime

from pydantic import BaseModel

from backend.app.schemas.base import ORMModel


class HolidayCreate(BaseModel):
    name: str
    holiday_date: date
    department_id: int | None = None
    is_optional: bool = False


class HolidayRead(ORMModel):
    id: int
    name: str
    holiday_date: date
    department_id: int | None
    is_optional: bool
    created_at: datetime

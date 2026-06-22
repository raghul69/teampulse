from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.department import Department
from backend.app.schemas.department import DepartmentCreate, DepartmentUpdate


class DepartmentService:
    def __init__(self, db: Session):
        self.db = db

    def list_departments(self) -> list[Department]:
        return list(self.db.scalars(select(Department).order_by(Department.name)))

    def create_department(self, payload: DepartmentCreate) -> Department:
        department = Department(**payload.model_dump())
        self.db.add(department)
        self.db.flush()
        return department

    def update_department(self, department: Department, payload: DepartmentUpdate) -> Department:
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(department, field, value)
        self.db.flush()
        return department

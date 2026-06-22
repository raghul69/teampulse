from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.api.deps import AdminUser
from backend.app.core.exceptions import NotFoundError
from backend.app.db.session import get_db
from backend.app.models.department import Department
from backend.app.schemas.department import DepartmentCreate, DepartmentRead, DepartmentUpdate
from backend.app.services.department_service import DepartmentService

router = APIRouter()


@router.get("", response_model=list[DepartmentRead])
def list_departments(db: Session = Depends(get_db)) -> list[Department]:
    return DepartmentService(db).list_departments()


@router.post("", response_model=DepartmentRead, dependencies=[AdminUser])
def create_department(payload: DepartmentCreate, db: Session = Depends(get_db)) -> Department:
    department = DepartmentService(db).create_department(payload)
    db.commit()
    db.refresh(department)
    return department


@router.patch("/{department_id}", response_model=DepartmentRead, dependencies=[AdminUser])
def update_department(department_id: int, payload: DepartmentUpdate, db: Session = Depends(get_db)) -> Department:
    service = DepartmentService(db)
    department = db.get(Department, department_id)
    if not department:
        raise NotFoundError("Department not found")
    updated = service.update_department(department, payload)
    db.commit()
    db.refresh(updated)
    return updated

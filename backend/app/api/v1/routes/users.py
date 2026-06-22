from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.api.deps import AdminUser, get_current_user
from backend.app.core.exceptions import NotFoundError
from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.schemas.user import UserCreate, UserRead, UserUpdate
from backend.app.services.user_service import UserService

router = APIRouter()


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.get("", response_model=list[UserRead], dependencies=[AdminUser])
def list_users(db: Session = Depends(get_db)) -> list[User]:
    return UserService(db).list_users()


@router.get("/team", response_model=list[UserRead])
def list_team_members(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[User]:
    if current_user.role.value == "admin":
        return UserService(db).list_users()
    if current_user.role.value != "manager":
        return []
    return UserService(db).list_team_members(current_user.id)


@router.post("", response_model=UserRead, dependencies=[AdminUser])
def create_user(payload: UserCreate, db: Session = Depends(get_db)) -> User:
    user = UserService(db).create_user(payload)
    db.commit()
    db.refresh(user)
    return user


@router.patch("/{user_id}", response_model=UserRead, dependencies=[AdminUser])
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)) -> User:
    service = UserService(db)
    user = service.get_user(user_id)
    if not user:
        raise NotFoundError("User not found")
    updated = service.update_user(user, payload)
    db.commit()
    db.refresh(updated)
    return updated

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.user import User
from backend.app.schemas.user import UserCreate, UserUpdate


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_user(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        return self.db.scalar(select(User).where(User.email == email))

    def get_by_auth_user_id(self, auth_user_id: str | UUID) -> User | None:
        return self.db.scalar(select(User).where(User.auth_user_id == UUID(str(auth_user_id))))

    def list_users(self) -> list[User]:
        return list(self.db.scalars(select(User).order_by(User.id)))

    def list_team_members(self, manager_id: int) -> list[User]:
        return list(
            self.db.scalars(
                select(User)
                .where(User.manager_id == manager_id)
                .order_by(User.full_name)
            )
        )

    def create_user(self, payload: UserCreate) -> User:
        user = User(
            auth_user_id=payload.auth_user_id,
            full_name=payload.full_name,
            email=str(payload.email),
            role=payload.role,
            manager_id=payload.manager_id,
            department_id=payload.department_id,
        )
        self.db.add(user)
        self.db.flush()
        return user

    def update_user(self, user: User, payload: UserUpdate) -> User:
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(user, field, value)
        self.db.flush()
        return user

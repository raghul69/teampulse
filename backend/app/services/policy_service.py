from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.holiday import Holiday
from backend.app.models.leave_policy import LeavePolicy
from backend.app.models.leave_type import LeaveTypeConfig
from backend.app.schemas.holiday import HolidayCreate
from backend.app.schemas.leave_policy import LeavePolicyCreate, LeavePolicyUpdate
from backend.app.schemas.leave_type import LeaveTypeCreate, LeaveTypeUpdate


class PolicyService:
    def __init__(self, db: Session):
        self.db = db

    def list_leave_types(self, active_only: bool = False) -> list[LeaveTypeConfig]:
        statement = select(LeaveTypeConfig).order_by(LeaveTypeConfig.name)
        if active_only:
            statement = statement.where(LeaveTypeConfig.is_active.is_(True))
        return list(self.db.scalars(statement))

    def get_leave_type(self, code: str) -> LeaveTypeConfig | None:
        return self.db.scalar(select(LeaveTypeConfig).where(LeaveTypeConfig.code == code))

    def create_leave_type(self, payload: LeaveTypeCreate) -> LeaveTypeConfig:
        item = LeaveTypeConfig(**payload.model_dump())
        self.db.add(item)
        self.db.flush()
        return item

    def update_leave_type(self, item: LeaveTypeConfig, payload: LeaveTypeUpdate) -> LeaveTypeConfig:
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(item, field, value)
        self.db.flush()
        return item

    def list_policies(self) -> list[LeavePolicy]:
        return list(self.db.scalars(select(LeavePolicy).order_by(LeavePolicy.leave_type_code, LeavePolicy.id)))

    def get_applicable_policy(self, leave_type_code: str, department_id: int | None, role: str) -> LeavePolicy | None:
        policies = list(
            self.db.scalars(
                select(LeavePolicy)
                .where(
                    LeavePolicy.leave_type_code == leave_type_code,
                    LeavePolicy.is_active.is_(True),
                )
                .order_by(LeavePolicy.department_id.desc().nulls_last(), LeavePolicy.role.desc().nulls_last())
            )
        )
        for policy in policies:
            department_matches = policy.department_id in {None, department_id}
            role_matches = policy.role in {None, role}
            if department_matches and role_matches:
                return policy
        return None

    def create_policy(self, payload: LeavePolicyCreate) -> LeavePolicy:
        data = payload.model_dump()
        if data.get("role"):
            data["role"] = data["role"].value
        policy = LeavePolicy(**data)
        self.db.add(policy)
        self.db.flush()
        return policy

    def update_policy(self, policy: LeavePolicy, payload: LeavePolicyUpdate) -> LeavePolicy:
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(policy, field, value)
        self.db.flush()
        return policy

    def list_holidays(self) -> list[Holiday]:
        return list(self.db.scalars(select(Holiday).order_by(Holiday.holiday_date)))

    def create_holiday(self, payload: HolidayCreate) -> Holiday:
        holiday = Holiday(**payload.model_dump())
        self.db.add(holiday)
        self.db.flush()
        return holiday

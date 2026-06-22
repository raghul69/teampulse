from collections import Counter, defaultdict
from datetime import date, datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.enums import AuditAction, LeaveStatus, NotificationType
from backend.app.core.exceptions import ForbiddenError, NotFoundError
from backend.app.models.leave_request import LeaveRequest
from backend.app.models.user import User
from backend.app.schemas.leave_request import LeaveDecision, LeaveRequestCreate
from backend.app.schemas.notification import NotificationCreate
from backend.app.services.audit_service import AuditService
from backend.app.services.leave_balance_service import LeaveBalanceService
from backend.app.services.notification_service import NotificationService


class LeaveRequestService:
    def __init__(self, db: Session):
        self.db = db
        self.balances = LeaveBalanceService(db)
        self.audit = AuditService(db)
        self.notifications = NotificationService(db)

    def list_for_user(self, user: User) -> list[LeaveRequest]:
        return list(
            self.db.scalars(
                select(LeaveRequest)
                .where(LeaveRequest.employee_id == user.id)
                .order_by(LeaveRequest.created_at.desc())
            )
        )

    def list_for_manager(self, manager: User) -> list[LeaveRequest]:
        return list(
            self.db.scalars(
                select(LeaveRequest)
                .where(LeaveRequest.manager_id == manager.id)
                .order_by(LeaveRequest.created_at.desc())
            )
        )

    def list_all(self) -> list[LeaveRequest]:
        return list(self.db.scalars(select(LeaveRequest).order_by(LeaveRequest.created_at.desc())))

    def team_calendar(self, manager: User) -> list[dict]:
        return [
            {
                "id": item.id,
                "employee_id": item.employee_id,
                "leave_type": item.leave_type,
                "status": item.status,
                "start_date": item.start_date,
                "end_date": item.end_date,
                "days": item.days,
            }
            for item in self.list_for_manager(manager)
            if item.status in {LeaveStatus.PENDING, LeaveStatus.APPROVED}
        ]

    def conflict_warnings(self, request: LeaveRequest) -> list[str]:
        warnings: list[str] = []
        if not request.manager_id:
            return ["Employee has no assigned manager."]

        overlapping = list(
            self.db.scalars(
                select(LeaveRequest)
                .where(
                    LeaveRequest.manager_id == request.manager_id,
                    LeaveRequest.id != request.id,
                    LeaveRequest.status.in_([LeaveStatus.PENDING, LeaveStatus.APPROVED]),
                    LeaveRequest.start_date <= request.end_date,
                    LeaveRequest.end_date >= request.start_date,
                )
                .order_by(LeaveRequest.start_date)
            )
        )
        if overlapping:
            warnings.append(f"{len(overlapping)} overlapping team leave request(s) found.")

        balance = self.balances.get_for_user(request.employee_id, request.start_date.year)
        if balance:
            available = {
                "casual": balance.casual_available,
                "sick": balance.sick_available,
                "earned": balance.earned_available,
                "unpaid": 9999,
            }.get(request.leave_type.value, 0)
            if available < request.days:
                warnings.append("Requested days exceed available leave balance.")

        return warnings or ["No conflicts detected."]

    def reports_summary(self) -> dict:
        requests = self.list_all()
        status_counts = Counter(item.status.value for item in requests)
        type_counts = Counter(item.leave_type.value for item in requests)
        monthly_days: dict[str, int] = defaultdict(int)

        for item in requests:
            monthly_days[item.start_date.strftime("%Y-%m")] += item.days

        total = len(requests)
        approved = status_counts.get("approved", 0)
        return {
            "total_requests": total,
            "pending_requests": status_counts.get("pending", 0),
            "approved_requests": approved,
            "rejected_requests": status_counts.get("rejected", 0),
            "approval_rate": round((approved / total) * 100, 1) if total else 0,
            "popular_leave_type": type_counts.most_common(1)[0][0] if type_counts else "none",
            "monthly_days": dict(sorted(monthly_days.items())),
            "generated_on": date.today().isoformat(),
        }

    def create(self, employee: User, payload: LeaveRequestCreate) -> LeaveRequest:
        days = (payload.end_date - payload.start_date).days + 1
        request = LeaveRequest(
            employee_id=employee.id,
            manager_id=employee.manager_id,
            leave_type=payload.leave_type,
            start_date=payload.start_date,
            end_date=payload.end_date,
            days=days,
            reason=payload.reason,
        )
        self.db.add(request)
        self.db.flush()
        self.audit.record(
            actor_id=employee.id,
            action=AuditAction.CREATE,
            entity_type="leave_requests",
            entity_id=request.id,
            new_values={"status": request.status, "days": days},
        )
        if employee.manager_id:
            self.notifications.create(
                NotificationCreate(
                    recipient_id=employee.manager_id,
                    notification_type=NotificationType.APPROVAL,
                    title="New leave request",
                    message=f"{employee.full_name} requested {days} leave day(s).",
                )
            )
        return request

    def decide(self, request_id: int, manager: User, payload: LeaveDecision) -> LeaveRequest:
        request = self.db.get(LeaveRequest, request_id)
        if not request:
            raise NotFoundError("Leave request not found")
        if request.status != LeaveStatus.PENDING:
            raise ForbiddenError("Only pending leave requests can be decided")
        if request.manager_id != manager.id and manager.role.value != "admin":
            raise ForbiddenError("Only assigned manager or admin can decide this request")

        request.status = payload.status
        request.manager_comment = payload.manager_comment
        request.decided_at = datetime.now(timezone.utc)
        if payload.status == LeaveStatus.APPROVED:
            balance = self.balances.get_for_user(request.employee_id, request.start_date.year)
            if balance:
                self.balances.consume(balance, request.leave_type, request.days)

        self.audit.record(
            actor_id=manager.id,
            action=AuditAction.APPROVE if payload.status == LeaveStatus.APPROVED else AuditAction.REJECT,
            entity_type="leave_requests",
            entity_id=request.id,
            new_values={"status": request.status},
        )
        self.notifications.create(
            NotificationCreate(
                recipient_id=request.employee_id,
                notification_type=NotificationType.APPROVAL if payload.status == LeaveStatus.APPROVED else NotificationType.REJECTION,
                title=f"Leave request {payload.status}",
                message=f"Your leave request from {request.start_date} to {request.end_date} was {payload.status}.",
            )
        )
        self.db.flush()
        return request

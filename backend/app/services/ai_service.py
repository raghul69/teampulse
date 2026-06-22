from collections import Counter
from datetime import date
from typing import Any

from backend.app.models.leave_balance import LeaveBalance
from backend.app.models.leave_request import LeaveRequest


class LeaveAIService:
    def recommend_leave_type(self, reason: str, balance: LeaveBalance | None, history: list[LeaveRequest]) -> dict[str, Any]:
        text = reason.lower()
        if any(word in text for word in ["sick", "fever", "doctor", "medical", "hospital"]):
            code = "sick"
        elif any(word in text for word in ["vacation", "travel", "family", "personal"]):
            code = "casual"
        elif balance and balance.earned_available > balance.casual_available:
            code = "earned"
        else:
            code = "casual"
        counts = Counter(item.leave_type.value for item in history)
        return {
            "recommended_type": code,
            "confidence": "high" if code in {"sick", "casual"} else "medium",
            "history_signal": dict(counts),
            "message": f"{code.title()} leave looks like the best fit based on reason, balance, and request history.",
        }

    def trend_insights(self, requests: list[LeaveRequest]) -> dict[str, Any]:
        monthly: dict[str, int] = {}
        leave_types = Counter()
        for item in requests:
            key = item.start_date.strftime("%Y-%m")
            monthly[key] = monthly.get(key, 0) + item.days
            leave_types[item.leave_type.value] += item.days
        peak_month = max(monthly, key=monthly.get) if monthly else "none"
        return {
            "peak_month": peak_month,
            "leave_type_mix": dict(leave_types),
            "forecast_note": "Expect higher absence risk around the peak month." if peak_month != "none" else "No leave trend data yet.",
            "generated_on": date.today().isoformat(),
        }

    def assistant_answer(self, question: str, balance: LeaveBalance | None, requests: list[LeaveRequest]) -> str:
        text = question.lower()
        if "balance" in text:
            if not balance:
                return "No leave balance is configured for your profile yet."
            return (
                f"Available balance: casual {balance.casual_available}, "
                f"sick {balance.sick_available}, earned {balance.earned_available}. "
                f"Unpaid leave used: {balance.unpaid_used}."
            )
        if "status" in text or "request" in text:
            if not requests:
                return "You do not have leave requests yet."
            latest = requests[0]
            return f"Your latest leave request is {latest.status.value} for {latest.days} day(s), from {latest.start_date} to {latest.end_date}."
        if "policy" in text:
            return "TeamPulse supports casual, sick, earned, and unpaid leave. Paid leave is deducted after manager approval."
        return "I can help with leave balance, leave policy, and leave request status."

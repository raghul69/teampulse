from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date, datetime
from typing import Any


def _parse_day(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def recommend_leave_type(reason: str, balances: dict[str, int]) -> dict[str, Any]:
    text = reason.lower()
    if any(word in text for word in ["fever", "sick", "doctor", "hospital", "medical"]):
        leave_type = "sick"
    elif any(word in text for word in ["vacation", "family", "personal", "travel"]):
        leave_type = "casual"
    else:
        leave_type = max(balances, key=lambda key: balances[key])

    return {
        "recommended_type": leave_type,
        "confidence": "high" if leave_type in {"sick", "casual"} else "medium",
        "message": f"Recommended {leave_type} leave based on reason and current balance.",
    }


def analyze_request(
    request: dict[str, Any],
    employee_balance: dict[str, int],
    team_requests: list[dict[str, Any]],
) -> dict[str, Any]:
    warnings: list[str] = []
    suggestions: list[str] = []
    leave_type = request["leave_type"]
    requested_days = int(request["days"])

    if employee_balance.get(leave_type, 0) < requested_days:
        warnings.append("Requested days exceed available leave balance.")
        suggestions.append("Ask employee to reduce days or choose another leave type.")

    start = _parse_day(request["start_date"])
    end = _parse_day(request["end_date"])
    overlaps = []
    for item in team_requests:
        if item["status"] not in {"pending", "approved"}:
            continue
        item_start = _parse_day(item["start_date"])
        item_end = _parse_day(item["end_date"])
        if start <= item_end and end >= item_start and item["employee_id"] != request["employee_id"]:
            overlaps.append(item)

    if overlaps:
        warnings.append(f"{len(overlaps)} team leave overlap detected.")
        suggestions.append("Review team coverage before approval.")

    if not warnings:
        suggestions.append("No balance or team conflict risks detected.")

    return {
        "risk": "high" if len(warnings) > 1 else "medium" if warnings else "low",
        "warnings": warnings,
        "suggestions": suggestions,
    }


def generate_insights(requests: list[dict[str, Any]]) -> dict[str, Any]:
    if not requests:
        return {
            "total_requests": 0,
            "approval_rate": 0,
            "popular_leave_type": "none",
            "monthly_trend": {},
            "summary": "No leave activity yet.",
        }

    status_counts = Counter(item["status"] for item in requests)
    type_counts = Counter(item["leave_type"] for item in requests)
    monthly = defaultdict(int)

    for item in requests:
        month = item["start_date"][:7]
        monthly[month] += int(item["days"])

    approval_rate = round((status_counts["approved"] / len(requests)) * 100, 1)
    popular_type = type_counts.most_common(1)[0][0]

    peak_month = max(monthly, key=monthly.get)
    return {
        "total_requests": len(requests),
        "approval_rate": approval_rate,
        "popular_leave_type": popular_type,
        "monthly_trend": dict(sorted(monthly.items())),
        "summary": f"{popular_type.title()} leave is most common. Peak leave demand is {peak_month}.",
    }

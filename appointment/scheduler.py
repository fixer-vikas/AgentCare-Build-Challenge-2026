from datetime import date, timedelta
from typing import Optional, Tuple


def infer_appointment(request: str) -> Tuple[Optional[str], Optional[str]]:
    if "2026-" in request:
        date_part = None
        for fragment in request.split():
            if len(fragment) == 10 and fragment.count("-") == 2:
                date_part = fragment
                break
        if date_part:
            try:
                date.fromisoformat(date_part)
            except ValueError:
                date_part = None
            if date_part:
                time_part = None
                for fragment in request.split():
                    if ":" in fragment and len(fragment) <= 5:
                        time_part = fragment
                        break
                return date_part, time_part or "09:00"
    if "next week" in request.lower():
        return (date.today() + timedelta(days=7)).strftime("%Y-%m-%d"), "10:00"
    if "next monday" in request.lower():
        today = date.today()
        weekday = today.weekday()
        delta = 7 - weekday + 0
        return (today + timedelta(days=delta)).strftime("%Y-%m-%d"), "10:00"
    return None, None

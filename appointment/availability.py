from datetime import date, timedelta
from typing import Dict, List


def generate_doctor_holidays(doctor_id: int) -> List[Dict[str, str]]:
    base = date.today()
    holidays: List[Dict[str, str]] = []
    if doctor_id % 2 == 0:
        holidays.append({"date": (base + timedelta(days=3)).isoformat(), "title": "Training day"})
    if doctor_id % 3 == 0:
        holidays.append({"date": (base + timedelta(days=6)).isoformat(), "title": "Hospital closed"})
    return holidays

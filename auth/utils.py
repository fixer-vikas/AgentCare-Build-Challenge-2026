from typing import Optional

from flask import session


def get_session_user_id() -> Optional[int]:
    user_id = session.get("user_id")
    return user_id if user_id is not None else None

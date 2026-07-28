from typing import Any, Dict, Optional


def auth_payload(payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return dict(payload or {})

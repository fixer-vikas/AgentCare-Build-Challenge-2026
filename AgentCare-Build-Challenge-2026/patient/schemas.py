from typing import Any, Dict, Optional


def patient_request_payload(payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return dict(payload or {})

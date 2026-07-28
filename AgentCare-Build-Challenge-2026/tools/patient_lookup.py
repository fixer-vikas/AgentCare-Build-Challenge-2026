from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from repositories.patient_repository import PatientRepository
from repositories.user_repository import UserRepository

from .audit_tool import AuditTool


class PatientLookupTool:
    def __init__(self, db_path: Optional[str] = None, audit_tool: Optional[AuditTool] = None):
        self.user_repo = UserRepository(db_path)
        self.patient_repo = PatientRepository(db_path)
        self.audit_tool = audit_tool or AuditTool(db_path)

    def ensure_patient_profile(
        self,
        patient_name: str,
        patient_email: Optional[str],
        patient_age: Optional[str],
        patient_phone: Optional[str],
        patient_id: Optional[int],
    ) -> Dict[str, Any]:
        if patient_id is not None:
            row = self.patient_repo.get_patient_by_id(patient_id)
            if row is None:
                raise ValueError("Patient not found")
            return {"patient_id": patient_id}

        if patient_email:
            user = self.user_repo.get_user_by_email(patient_email)
            if user is not None:
                patient = self.patient_repo.get_patient_by_user_id(user["id"])
                if patient is not None:
                    return {"patient_id": patient["id"]}

        email = patient_email or f"{patient_name.lower().replace(' ', '')}@agentcare.local"
        name = patient_name or "Patient"
        created = self.user_repo.register_user("patient", name, email, "changeme", patient_age, patient_phone)
        patient_id = created.get("patient_id") or created["id"]
        self.audit_tool.log_audit("patient", patient_id, "registered", f"Patient registered for {name}")
        return {"id": patient_id, "patient_id": patient_id}

    def _now(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

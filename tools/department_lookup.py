from __future__ import annotations

from typing import List


class DepartmentLookupTool:
    def department_agent(self, request: str) -> str:
        lowered = request.lower()
        if "cardio" in lowered or "heart" in lowered or "ecg" in lowered:
            return "Cardiology"
        if "ortho" in lowered or "bone" in lowered or "joint" in lowered:
            return "Orthopedics"
        if "neuro" in lowered or "neurology" in lowered:
            return "Neurology"
        if "ent" in lowered or "ear" in lowered or "throat" in lowered:
            return "ENT"
        return "General Medicine"

    def required_documents_for_department(self, department_name: str) -> List[str]:
        lower = department_name.lower()
        if "cardio" in lower or "heart" in lower:
            return ["ecg", "insurance_card"]
        if "ortho" in lower or "bone" in lower or "joint" in lower:
            return ["insurance_card", "medical_history"]
        if "neuro" in lower or "neurology" in lower:
            return ["medical_history", "insurance_card"]
        if "ent" in lower or "ear" in lower or "throat" in lower:
            return ["id_proof", "medical_history"]
        return ["id_proof", "insurance_card"]

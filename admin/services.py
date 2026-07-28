from typing import Any, Dict, List

from app.agentcare import AgentCareService


class AdminService:
    def __init__(self, service=None):
        self.service = service or AgentCareService()

    def get_audit_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        return self.service.get_audit_events(limit)

    def get_departments(self) -> List[Dict[str, Any]]:
        return self.service.get_departments()

    def get_departments_response(self):
        return self.get_departments(), 200

    def get_audit_logs_response(self, session):
        if "user_id" not in session:
            return {"ok": False, "error": "Not authenticated"}, 401
        return self.get_audit_events(), 200

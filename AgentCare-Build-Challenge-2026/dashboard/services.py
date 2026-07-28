from typing import Any, Dict

from app.agentcare import AgentCareService


class DashboardService:
    def __init__(self, service=None):
        self.service = service or AgentCareService()

    def get_dashboard(self, user_id: int) -> Dict[str, Any]:
        user = self.service.get_user(user_id)
        if user is None:
            return {"ok": False, "error": "User not found"}
        if user["role"] == "patient":
            dashboard = self.service.get_patient_dashboard(user_id)
        else:
            dashboard = self.service.get_staff_dashboard()
            dashboard["user"] = user
        return {"ok": True, "dashboard": dashboard}

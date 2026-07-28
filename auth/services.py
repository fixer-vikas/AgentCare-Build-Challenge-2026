from app.agentcare import AgentCareService


class AuthService:
    def __init__(self, service=None):
        self.service = service or AgentCareService()

    def register_user(self, role, name, email, password, age=None, phone=None):
        return self.service.register_user(role, name, email, password, age, phone)

    def login_user(self, email, password):
        return self.service.login_user(email, password)

    def get_user(self, user_id):
        return self.service.get_user(user_id)

    def patient_exists(self, email):
        return self.service.patient_exists(email)

    def logout(self, session):
        session.pop("user_id", None)
        return {"ok": True}

    def register(self, payload, session):
        result = self.register_user(
            payload.get("role", "patient"),
            payload.get("name", ""),
            payload.get("email", ""),
            payload.get("password", ""),
            payload.get("age"),
            payload.get("phone"),
        )
        session["user_id"] = result["id"]
        return {"ok": True, "user": result}, 200

    def login(self, payload, session):
        user = self.login_user(payload.get("email", ""), payload.get("password", ""))
        if not user:
            return {"ok": False, "error": "Invalid credentials"}, 401
        session["user_id"] = user["id"]
        return {"ok": True, "user": user}, 200

from app.agentcare import AgentCareService


class AuthRepository:
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

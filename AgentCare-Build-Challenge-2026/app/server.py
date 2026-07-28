import sys
from pathlib import Path

from flask import Flask, jsonify, render_template_string

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.agentcare import AgentCareService
from app.templates import LANDING_PAGE
from admin.routes import register_admin_routes
from appointment.routes import register_appointment_routes
from auth.routes import register_auth_routes
from dashboard.routes import register_dashboard_routes
from document.routes import register_document_routes
from patient.routes import register_patient_routes
from workflow.routes import register_workflow_routes


def create_app() -> Flask:
    app = Flask(__name__)
    app.secret_key = "agentcare-secret"
    service = AgentCareService()

    register_auth_routes(app, service=service)
    register_patient_routes(app, service=service)
    register_appointment_routes(app, service=service)
    register_document_routes(app, service=service)
    register_dashboard_routes(app, service=service)
    register_admin_routes(app, service=service)
    register_workflow_routes(app, service=service)

    @app.route("/", methods=["GET"])
    def index():
        return render_template_string(LANDING_PAGE)

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok"})

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

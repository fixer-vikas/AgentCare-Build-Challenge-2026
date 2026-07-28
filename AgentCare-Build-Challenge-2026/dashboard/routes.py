from flask import Blueprint, jsonify, redirect, render_template_string, session

from app.templates import DASHBOARD_PAGE
from .services import DashboardService


def register_dashboard_routes(app, service=None):
    if service is None:
        dashboard_service = DashboardService()
    elif isinstance(service, DashboardService):
        dashboard_service = service
    else:
        dashboard_service = DashboardService(service=service)
    blueprint = Blueprint("dashboard", __name__)

    @blueprint.route("/dashboard-page", methods=["GET"])
    @blueprint.route("/dashboard", methods=["GET"])
    def dashboard_page():
        if "user_id" not in session:
            return redirect("/login")
        return render_template_string(DASHBOARD_PAGE)

    @blueprint.route("/api/dashboard", methods=["GET"])
    def api_dashboard():
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"ok": False, "error": "Not authenticated"}), 401
        result = dashboard_service.get_dashboard(user_id)
        if result.get("ok"):
            return jsonify(result)
        return jsonify(result), 404

    app.register_blueprint(blueprint)
    return blueprint

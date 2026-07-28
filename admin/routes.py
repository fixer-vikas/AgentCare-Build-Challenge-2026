from flask import Blueprint, jsonify, session

from .services import AdminService


def register_admin_routes(app, service=None):
    admin_service = service or AdminService()
    blueprint = Blueprint("admin", __name__)

    @blueprint.route("/api/departments", methods=["GET"])
    def api_get_departments():
        response, status_code = admin_service.get_departments_response()
        return jsonify(response), status_code

    @blueprint.route("/api/audit-logs", methods=["GET"])
    def api_get_audit_logs():
        response, status_code = admin_service.get_audit_logs_response(session)
        return jsonify(response), status_code

    app.register_blueprint(blueprint)
    return blueprint

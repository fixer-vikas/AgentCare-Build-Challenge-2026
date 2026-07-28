from flask import Blueprint, jsonify, render_template_string, request, session

from app.templates import AUTH_PAGE
from .services import AuthService


def register_auth_routes(app, service=None):
    if service is None:
        auth_service = AuthService()
    elif isinstance(service, AuthService):
        auth_service = service
    else:
        auth_service = AuthService(service=service)
    blueprint = Blueprint("auth", __name__)

    @blueprint.route("/login", methods=["GET"])
    def login_page():
        return render_template_string(AUTH_PAGE)

    @blueprint.route("/logout", methods=["GET", "POST"])
    def logout_user():
        response = auth_service.logout(session)
        return jsonify(response)

    @blueprint.route("/register", methods=["POST"])
    def register_user():
        payload = request.get_json(silent=True) or {}
        try:
            response, status_code = auth_service.register(payload, session)
            return jsonify(response), status_code
        except ValueError as exc:
            return jsonify({"ok": False, "error": str(exc)}), 400

    @blueprint.route("/login", methods=["POST"])
    def login_user():
        payload = request.get_json(silent=True) or {}
        response, status_code = auth_service.login(payload, session)
        return jsonify(response), status_code

    app.register_blueprint(blueprint)
    return blueprint

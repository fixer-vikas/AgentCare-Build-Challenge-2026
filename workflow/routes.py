from flask import Blueprint, jsonify, request, session

from .services import WorkflowService


def register_workflow_routes(app, service=None):
    workflow_service = service or WorkflowService()
    blueprint = Blueprint("workflow", __name__)

    @blueprint.route("/workflows/<workflow_id>", methods=["GET"])
    def workflow_get_workflow(workflow_id: str):
        return jsonify(workflow_service.get_workflow(workflow_id))

    @blueprint.route("/api/escalation-queue", methods=["GET"])
    def workflow_api_escalation_queue():
        response, status_code = workflow_service.get_escalation_queue_response(session)
        return jsonify(response), status_code

    @blueprint.route("/api/workflows/<workflow_id>/action", methods=["POST"])
    def workflow_api_update_workflow_status(workflow_id: str):
        payload = request.get_json(silent=True) or {}
        response, status_code = workflow_service.update_workflow_status_response(session, workflow_id, payload)
        return jsonify(response), status_code

    @blueprint.route("/api/staff-ai", methods=["POST"])
    def workflow_api_staff_ai_request():
        payload = request.get_json(silent=True) or {}
        response, status_code = workflow_service.staff_ai_request_response(session, payload)
        return jsonify(response), status_code

    @blueprint.route("/api/system/reset", methods=["POST"])
    def workflow_api_system_reset():
        payload = request.get_json(silent=True) or {}
        response, status_code = workflow_service.system_reset_response(session, payload)
        return jsonify(response), status_code

    @blueprint.route("/api/escalations", methods=["GET"])
    def workflow_api_get_escalations():
        response, status_code = workflow_service.get_escalations_response(session)
        return jsonify(response), status_code

    app.register_blueprint(blueprint)
    return blueprint

from flask import Blueprint, jsonify, request, session

from .services import AppointmentService


def register_appointment_routes(app, service=None):
    appointment_service = service or AppointmentService()
    blueprint = Blueprint("appointment", __name__)

    @blueprint.route("/api/appointments", methods=["GET"])
    def api_get_appointments():
        response, status_code = appointment_service.get_appointments_response(session)
        return jsonify(response), status_code

    @blueprint.route("/api/doctors", methods=["GET", "POST"])
    def api_doctors():
        payload = request.get_json(silent=True) or {}
        response, status_code = appointment_service.handle_doctors_request(request.method, session, payload)
        return jsonify(response), status_code

    @blueprint.route("/api/doctors/<int:doctor_id>", methods=["PUT"])
    def api_update_doctor(doctor_id: int):
        payload = request.get_json(silent=True) or {}
        response, status_code = appointment_service.update_doctor_response(session, doctor_id, payload)
        return jsonify(response), status_code

    @blueprint.route("/api/doctors/<int:doctor_id>/schedule", methods=["GET"])
    def api_doctor_schedule(doctor_id: int):
        response, status_code = appointment_service.get_doctor_schedule_response(session, doctor_id)
        return jsonify(response), status_code

    @blueprint.route("/api/departments/<int:department_id>/schedule", methods=["GET"])
    def api_department_schedule(department_id: int):
        response, status_code = appointment_service.get_department_schedule_response(session, department_id)
        return jsonify(response), status_code

    @blueprint.route("/api/escalation-queue", methods=["GET"])
    def api_escalation_queue():
        response, status_code = appointment_service.get_escalation_queue_response(session)
        return jsonify(response), status_code

    @blueprint.route("/api/workflows/<workflow_id>/action", methods=["POST"])
    def api_update_workflow_status(workflow_id: str):
        payload = request.get_json(silent=True) or {}
        response, status_code = appointment_service.update_workflow_status_response(session, workflow_id, payload)
        return jsonify(response), status_code

    @blueprint.route("/api/staff-ai", methods=["POST"])
    def api_staff_ai_request():
        payload = request.get_json(silent=True) or {}
        response, status_code = appointment_service.staff_ai_request_response(session, payload)
        return jsonify(response), status_code

    @blueprint.route("/api/system/reset", methods=["POST"])
    def api_system_reset():
        payload = request.get_json(silent=True) or {}
        response, status_code = appointment_service.system_reset_response(session, payload)
        return jsonify(response), status_code

    @blueprint.route("/api/escalations", methods=["GET"])
    def api_get_escalations():
        response, status_code = appointment_service.get_escalations_response(session)
        return jsonify(response), status_code

    app.register_blueprint(blueprint)
    return blueprint

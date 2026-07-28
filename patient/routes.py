from flask import Blueprint, jsonify, request, session

from .services import PatientService
from .validators import validate_patient_payload


def register_patient_routes(app, service=None):
    if service is None:
        patient_service = PatientService()
    elif isinstance(service, PatientService):
        patient_service = service
    else:
        patient_service = PatientService(service=service)
    blueprint = Blueprint("patient", __name__)

    @blueprint.route("/requests", methods=["POST"])
    def legacy_create_request():
        payload = request.get_json(silent=True) or {}
        payload = validate_patient_payload(payload)
        response, status_code = patient_service.create_request(payload, session)
        return jsonify(response), status_code

    @blueprint.route("/api/requests", methods=["POST"])
    def api_create_request():
        payload = request.get_json(silent=True) or {}
        payload = validate_patient_payload(payload)
        response, status_code = patient_service.create_authenticated_request(payload, session)
        return jsonify(response), status_code

    @blueprint.route("/api/requests", methods=["GET"])
    def api_get_requests():
        response, status_code = patient_service.list_requests(session)
        return jsonify(response), status_code

    @blueprint.route("/api/patients", methods=["GET"])
    def api_get_patients():
        response, status_code = patient_service.list_patients(session)
        return jsonify(response), status_code

    @blueprint.route("/api/documents", methods=["GET"])
    def api_get_documents():
        response, status_code = patient_service.list_documents(session)
        return jsonify(response), status_code

    @blueprint.route("/api/patient-exists", methods=["GET"])
    def api_patient_exists():
        email = request.args.get("email", "").strip()
        if not email:
            return jsonify({"ok": False, "error": "Email is required"}), 400
        response, status_code = patient_service.patient_exists_response(email)
        return jsonify(response), status_code

    @blueprint.route("/api/documents/upload", methods=["POST"])
    def api_upload_document():
        file = request.files.get("file")
        document_name = request.form.get("document_name")
        response, status_code = patient_service.upload_document(session, file, document_name)
        return jsonify(response), status_code

    @blueprint.route("/workflows/<workflow_id>", methods=["GET"])
    def get_workflow(workflow_id: str):
        response, status_code = patient_service.get_workflow_response(workflow_id)
        return jsonify(response), status_code

    app.register_blueprint(blueprint)
    return blueprint

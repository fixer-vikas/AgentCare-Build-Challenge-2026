from flask import Blueprint, jsonify, request, session

from .services import DocumentService


def register_document_routes(app, service=None):
    document_service = service or DocumentService()
    blueprint = Blueprint("document", __name__)

    @blueprint.route("/api/documents", methods=["GET"])
    def document_api_get_documents():
        response, status_code = document_service.get_documents_response(session)
        return jsonify(response), status_code

    @blueprint.route("/api/documents/upload", methods=["POST"])
    def document_api_upload_document():
        file = request.files.get("file")
        document_name = request.form.get("document_name")
        response, status_code = document_service.upload_document_response(session, file, document_name)
        return jsonify(response), status_code

    app.register_blueprint(blueprint)
    return blueprint

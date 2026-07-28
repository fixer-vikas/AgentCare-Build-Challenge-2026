import os
import sys
import tempfile
from pathlib import Path

from flask import Flask

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.agentcare import AgentCareService
from auth.routes import register_auth_routes


def test_patient_registration_and_appointment_flow_persists_state():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "agentcare.sqlite3")
        service = AgentCareService(db_path=db_path)

        result = service.handle_request(
            "Register John Doe as a new patient and book a cardiology follow-up appointment for 2026-08-05 at 10:00.",
            patient_name="John Doe",
        )

        assert result["status"] == "completed"
        assert result["patient_name"] == "John Doe"
        assert result["department"] == "Cardiology"
        assert result["appointment_status"] == "booked"
        assert result["workflow_id"] is not None

        workflow = service.get_workflow(result["workflow_id"])
        assert workflow["status"] == "completed"
        assert len(workflow["steps"]) >= 3


def test_document_collection_and_follow_up_are_added_for_admin_requests():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "agentcare.sqlite3")
        service = AgentCareService(db_path=db_path)

        result = service.handle_request(
            "Please collect the insurance card and arrange a follow-up reminder for Mary Chen after her neurology visit.",
            patient_name="Mary Chen",
        )

        assert result["status"] == "completed"
        assert result["department"] == "Neurology"
        assert result["document_count"] >= 1
        assert result["follow_up_created"] is True


def test_ui_endpoint_serves_form_page():
    from app.server import app as flask_app

    client = flask_app.test_client()
    response = client.get("/")

    assert response.status_code == 200
    assert b"AgentCare" in response.data
    assert b"Login / Register" in response.data


def test_safety_guard_blocks_diagnostic_requests():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "agentcare.sqlite3")
        service = AgentCareService(db_path=db_path)

        result = service.handle_request(
            "Please diagnose diabetes and prescribe insulin for Sarah Kim.",
            patient_name="Sarah Kim",
        )

        assert result["status"] == "blocked"
        assert "medical" in result["safety_reason"].lower()


def test_user_repository_registers_and_fetches_patient_profile():
    from repositories.user_repository import UserRepository

    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "agentcare.sqlite3")
        repo = UserRepository(db_path=db_path)

        created = repo.register_user("patient", "Jane Doe", "jane@example.com", "secret123", age="30", phone="111")

        assert created["id"] is not None
        assert repo.get_user_by_email("jane@example.com")["name"] == "Jane Doe"
        assert repo.get_patient_profile(created["id"])["phone"] == "111"


def test_staff_ai_request_blocks_clinical_diagnosis_or_prescription():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "agentcare.sqlite3")
        service = AgentCareService(db_path=db_path)
        service.register_user("patient", "Test Patient", "patient@example.com", "secret123")

        patient_profile = service.get_all_patients()[0]
        result = service.handle_staff_ai_request(
            "Please diagnose diabetes and prescribe insulin for a patient.",
            patient_id=patient_profile["id"],
            staff_user_id=1,
        )

        assert result["summary"].lower().startswith("blocked")
        assert "administrative" in result["summary"].lower() or "clinical" in result["summary"].lower()


def test_auth_routes_support_login_and_registration_via_service_instance():
    with tempfile.TemporaryDirectory() as tmpdir:
        app = Flask(__name__)
        app.secret_key = "test-secret"
        service = AgentCareService(db_path=os.path.join(tmpdir, "agentcare.sqlite3"))
        register_auth_routes(app, service=service)
        client = app.test_client()

        register_response = client.post(
            "/register",
            json={"role": "patient", "name": "New Patient", "email": "newpatient@example.com", "password": "secret123"},
        )
        assert register_response.status_code == 200

        login_response = client.post(
            "/login",
            json={"email": "newpatient@example.com", "password": "secret123"},
        )
        data = login_response.get_json()
        assert login_response.status_code == 200
        assert data["ok"] is True

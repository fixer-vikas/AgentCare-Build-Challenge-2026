# AgentCare architecture

## Overview
AgentCare is a small Flask-based healthcare administration assistant. It accepts patient requests in plain English, routes them to departments and doctors, manages appointments and documents, and stores workflow state in SQLite.

## Main components
- app/server.py: Flask app factory and route registration.
- app/agentcare.py: core service layer that orchestrates the workflow.
- auth/, patient/, appointment/, document/, dashboard/, admin/, workflow/: feature modules with Flask blueprints and services.
- repositories/: SQLite-backed repositories for users, patients, appointments, documents, workflows, and audit trails.
- tools/: reusable helpers for lookup, reminder, document, appointment, escalation, and workflow operations.

## Agents and tools
- Coordinator agent: interprets the incoming request and decides the next action.
- Department routing agent: maps the request to the appropriate specialty.
- Appointment agent: finds available doctors and books or updates appointments.
- Document agent: classifies uploaded patient documents and tracks missing items.
- Safety and escalation agent: blocks unsafe medical requests and escalates edge cases.

Each agent uses the shared tools layer to interact with repositories instead of embedding raw SQL directly in the route or service handlers.

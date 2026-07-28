# AgentCare – AI-Powered Healthcare Administration Assistant

AgentCare is a modular Flask-based healthcare administration assistant that accepts plain-English patient requests, routes them to the right department, manages appointments and documents, and stores workflow history in SQLite.

> AgentCare supports administrative healthcare workflows only. It does not diagnose conditions, prescribe treatment, or replace qualified medical professionals.

## Features
- Secure authentication and user management
- Patient registration and profile management
- Appointment scheduling and availability checking
- Department routing and doctor lookup
- Document upload and tracking
- Workflow history and reminders
- Staff dashboard and audit logging
- Persistent SQLite storage
- Modular service, repository, and tool architecture
- OpenAI SDK integration ready for future LLM-driven workflows

## Project architecture
The project is organized into feature modules and shared infrastructure:
- app/server.py creates the Flask app and registers blueprints.
- app/agentcare.py contains the core service layer and schema initialization logic.
- auth/, patient/, appointment/, document/, dashboard/, admin/, and workflow/ expose the route and service layers.
- repositories/ contains SQLite-backed data access classes.
- tools/ contains reusable helpers for patients, departments, doctors, appointments, documents, reminders, escalation, and workflow tracking.
- migrations/ stores SQL schema snapshots, and scripts/ contains seed utilities.

## Suggested folder layout
```text
AgentCare/
├── admin/
├── app/
├── appointment/
├── auth/
├── dashboard/
├── document/
├── patient/
├── workflow/
├── repositories/
├── tools/
├── migrations/
├── scripts/
├── tests/
├── docs/
├── README.md
├── requirements.txt
├── .env.example
└── .gitignore
```

## Agent workflow
AgentCare uses a lightweight multi-agent-style workflow:
- Coordinator agent: interprets the incoming request and decides the next action.
- Department routing agent: maps the request to the relevant specialty.
- Appointment agent: checks doctor availability and books or updates appointments.
- Document agent: classifies uploaded documents and tracks missing items.
- Safety and escalation agent: blocks unsafe medical instructions and escalates edge cases.

The shared tools layer enables these agents to interact with repositories rather than hard-coding database logic into routes.

## Local setup
1. Create and activate a virtual environment.
2. Install dependencies:
   `pip install -r requirements.txt`
3. Copy the environment template:
   `copy .env.example .env`
4. Start the Flask app:
   `python app/server.py`
5. Open the UI at:
   - `http://127.0.0.1:5000/`
   - `http://127.0.0.1:5000/login`
6. Seed example data if needed:
   `python scripts/seed_sample_data.py`

## Database
AgentCare uses SQLite as its persistent database.

Major entities include:
- Users
- Patients
- Departments
- Doctors
- Appointment slots
- Appointments
- Patient documents
- Workflow runs
- Reminders
- Escalations
- Audit events

The system persists workflow state and supports auditability.

## Tests
Run the regression suite with:
`pytest tests/`

## Technology stack
- Python 3.11+
- Flask
- SQLite
- OpenAI Python SDK
- Pytest
- Git and GitHub Actions

## Design principles
- Modular feature-based architecture
- Separation of concerns
- Repository pattern
- Service layer pattern
- Reusable tool layer
- Persistent workflow state
- AI-ready architecture
- Extensible design

## Future enhancements
- Full OpenAI-powered conversational workflow
- LangGraph-style orchestration
- Vector database integration
- OCR for document processing
- Email and SMS notifications
- REST API versioning
- PostgreSQL deployment
- Docker support
- Cloud deployment

## Challenge compliance
This project includes:
- Modular source code
- requirements.txt
- README.md
- .env.example
- .gitignore
- GitHub Actions workflow
- SQLite persistent database
- Automated tests
- Migration scripts
- Sample seed data
- OpenAI SDK dependency for LLM integration

## Disclaimer
AgentCare is intended for healthcare administration and workflow automation only. It does not diagnose, prescribe treatment, or replace qualified healthcare professionals. All medical decisions remain under human supervision.

## Author
Vikas Panwar
Developed as a submission for the AgentCare Build Challenge 2026. 

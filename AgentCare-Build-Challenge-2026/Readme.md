# AgentCare

AgentCare is a local Flask-based healthcare administration assistant that accepts plain-English patient requests, routes them to the right department, manages appointments and documents, and stores workflow history in SQLite.

## What it does
- Parses a patient administration request
- Routes the request to a department
- Books or skips an appointment based on the request
- Collects required documents
- Creates a follow-up reminder when requested
- Persists workflow state and patient data in SQLite

## Local setup
1. Create and activate a virtual environment.
2. Install dependencies:
   `pip install -r Hackathon/1_AgentCare/requirements.txt`
3. Copy the environment template:
   `copy Hackathon/1_AgentCare/.env.example Hackathon/1_AgentCare/.env`
4. Start the Flask app:
   `python Hackathon/1_AgentCare/app/server.py`
5. Open the UI at:
   - `http://127.0.0.1:5000/`
   - `http://127.0.0.1:5000/login`
6. Seed example data if needed:
   `python Hackathon/1_AgentCare/scripts/seed_sample_data.py`

## Architecture
The project is organized into feature modules and shared infrastructure:
- app/server.py creates the Flask app and registers blueprints.
- app/agentcare.py contains the core service layer and schema initialization logic.
- auth/, patient/, appointment/, document/, dashboard/, admin/, and workflow/ expose the route and service layers.
- repositories/ contains SQLite-backed data access classes.
- tools/ contains reusable helpers for patients, departments, doctors, appointments, documents, reminders, escalation, and workflow tracking.
- migrations/ stores SQL schema snapshots, and scripts/ contains seed utilities.

## Agents and tools
AgentCare uses a small multi-agent style workflow:
- Coordinator agent: interprets the incoming request and decides the next action.
- Department routing agent: maps the request to the relevant specialty.
- Appointment agent: checks doctor availability and books or updates appointments.
- Document agent: classifies uploaded documents and tracks missing items.
- Safety and escalation agent: blocks unsafe medical instructions and escalates edge cases.

The shared tools layer enables these agents to interact with repositories rather than hard-coding database logic into routes.

## Database models and initialization
The service layer creates the SQLite schema on startup and uses migration-style SQL files in the migrations folder as a reference for the base structure.

## Sample data
The script in scripts/seed_sample_data.py inserts sample departments, doctors, and a staff account for local demos.

## Tests
Run the regression suite with:
`pytest Hackathon/1_AgentCare/tests`

These tools must perform real logic and interact with persistent data. 

# Database Requirements
Persistent SQL database (SQLite/MySQL/PostgreSQL) with entities for:
* Users
* Patient Profiles
* Departments
* Doctors
* Appointment Slots
* Appointments
* Patient Documents
* Workflow Runs
* Reminders
* Escalations
* Audit Events

The system must persist workflow state and support auditability. 

# Overall Goal
The application should function as an AI Healthcare Administration Assistant that automates non-clinical patient workflows. It should accept natural-language requests, coordinate multiple specialized AI agents, invoke real backend tools, update a persistent SQL database, maintain workflow state, and provide both patients and hospital staff with a complete interface to manage registrations, appointments, documents, reminders, and escalations—while ensuring that all medical decisions remain under human supervision. 

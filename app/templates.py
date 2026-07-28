LANDING_PAGE = """
<!doctype html>
<html>
<head>
  <meta charset='utf-8'>
  <title>AgentCare</title>
  <style>
    body { margin: 0; font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f4f7fb; color: #1f2937; }
    header { background: #2563eb; color: white; padding: 36px 24px; text-align: center; }
    header h1 { margin: 0 0 12px; font-size: 2.6rem; }
    header p { margin: 0; max-width: 760px; margin-inline: auto; opacity: .88; }
    .shell { max-width: 1180px; margin: 0 auto; padding: 32px 24px; }
    .section { display: grid; gap: 24px; margin-top: 40px; }
    .card { background: white; border-radius: 18px; box-shadow: 0 18px 40px rgba(15, 23, 42, .08); padding: 28px; }
    .button { display: inline-flex; align-items: center; justify-content: center; gap: 8px; padding: 14px 22px; border: none; border-radius: 12px; text-decoration: none; font-weight: 600; cursor: pointer; }
    .button-primary { background: #2563eb; color: white; }
    .button-secondary { background: #e5e7eb; color: #111827; }
    .feature-grid { display: grid; gap: 18px; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); }
    .feature-card { border: 1px solid #e5e7eb; border-radius: 16px; padding: 18px; background: white; }
    .feature-card h3 { margin-top: 0; }
    footer { margin-top: 48px; text-align: center; color: #6b7280; }
    a { color: inherit; }
  </style>
</head>
<body>
  <header>
    <h1>AgentCare</h1>
    <p>AI Healthcare Administration Assistant for patient workflows, routing, appointment booking, document management, reminders, escalations, and audit history.</p>
  </header>
  <main class='shell'>
    <div class='section'>
      <div class='card'>
        <h2>Delivering non-clinical patient administration at scale</h2>
        <p>Submit a patient request in plain English and the assistant will identify or register the patient, route to the right department, find doctors and slots, book appointments, classify documents, detect missing files, create follow-ups, and save the entire workflow.</p>
        <p><a href='/login' class='button button-primary'>Login / Register</a></p>
      </div>
      <div class='feature-grid'>
        <div class='feature-card'><h3>Patient workflow</h3><p>Book appointments, upload documents, track reminders, and review workflow history.</p></div>
        <div class='feature-card'><h3>Staff operations</h3><p>View requests, manage departments, monitor escalations, and audit every action.</p></div>
        <div class='feature-card'><h3>AI orchestration</h3><p>Coordinator, department, appointment, document, follow-up, and safety agents work together to automate requests.</p></div>
        <div class='feature-card'><h3>Persistent data</h3><p>Users, patients, doctors, appointments, documents, workflows, reminders, escalations, and audit logs are stored in SQLite.</p></div>
      </div>
    </div>
    <div class='section'>
      <div class='card'>
        <h2>How it works</h2>
        <ul>
          <li>1. Patient submits a plain-English request</li>
          <li>2. System identifies or registers patient</li>
          <li>3. Request is routed to the right department</li>
          <li>4. Appointment slots are found and booked</li>
          <li>5. Documents are classified and missing items detected</li>
          <li>6. Follow-ups and reminders are created</li>
          <li>7. Emergency or uncertain requests escalate to staff</li>
          <li>8. Full workflow and audit history are persisted</li>
        </ul>
      </div>
    </div>
    <div class='section'>
      <div class='card'>
        <h2>Contact</h2>
        <p>For local testing, use the login page to create a patient or staff account and explore the dashboard.</p>
      </div>
    </div>
  </main>
  <footer><p>AgentCare • Local Flask app • SQLite persistence</p></footer>
</body>
</html>
"""

AUTH_PAGE = """
<!doctype html>
<html>
<head>
  <meta charset='utf-8'>
  <title>AgentCare Login</title>
  <style>
    body { margin: 0; font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f4f7fb; color: #111827; }
    .shell { max-width: 520px; margin: 0 auto; padding: 28px; }
    .card { background: white; border-radius: 22px; box-shadow: 0 18px 40px rgba(15, 23, 42, .08); padding: 32px; }
    h1 { margin-top: 0; }
    label { display: block; margin-top: 18px; font-weight: 600; }
    input { width: 100%; border: 1px solid #d1d5db; border-radius: 12px; padding: 12px; margin-top: 8px; }
    .button { margin-top: 22px; width: 100%; border: none; border-radius: 12px; padding: 14px; color: white; background: #2563eb; cursor: pointer; font-weight: 700; }
    .toggle { display: flex; gap: 12px; margin-top: 16px; }
    .toggle button { flex: 1; border: 1px solid #d1d5db; background: white; padding: 12px; border-radius: 12px; cursor: pointer; }
    .toggle button.active { background: #2563eb; color: white; border-color: #2563eb; }
    .notice { margin-top: 16px; color: #4b5563; }
    .link { color: #2563eb; text-decoration: none; }
  </style>
</head>
<body>
  <div class='shell'>
    <div class='card'>
      <h1>AgentCare</h1>
      <div class='toggle'>
        <button id='loginTab' class='active'>Login</button>
        <button id='registerTab'>Register</button>
      </div>
      <div id='forms'>
        <form id='loginForm'>
          <label>Email</label><input type='email' id='loginEmail' required>
          <p id='emailStatus' class='notice'></p>
          <label>Password</label><input type='password' id='loginPassword' required>
          <button type='submit' class='button'>Login</button>
        </form>
        <form id='registerForm' style='display:none;'>
          <label>Role</label>
          <select id='registerRole' style='width:100%;padding:12px;border:1px solid #d1d5db;border-radius:12px;'>
            <option value='patient'>Patient</option>
            <option value='staff'>Staff</option>
          </select>
          <label>Name</label><input type='text' id='registerName' required>
          <label>Email</label><input type='email' id='registerEmail' required>
          <label>Password</label><input type='password' id='registerPassword' required>
          <label>Age (patient only)</label><input type='text' id='registerAge'>
          <label>Phone</label><input type='text' id='registerPhone'>
          <button type='submit' class='button'>Register</button>
        </form>
      </div>
      <p class='notice'>After login, use the dashboard to submit requests, upload documents, and inspect patient or staff workflows.</p>
    </div>
  </div>
  <script>
    const loginTab = document.getElementById('loginTab');
    const registerTab = document.getElementById('registerTab');
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    loginTab.addEventListener('click', () => { loginTab.classList.add('active'); registerTab.classList.remove('active'); loginForm.style.display = 'block'; registerForm.style.display = 'none'; });
    registerTab.addEventListener('click', () => { registerTab.classList.add('active'); loginTab.classList.remove('active'); loginForm.style.display = 'none'; registerForm.style.display = 'block'; });

    loginForm.addEventListener('submit', async (event) => {
      event.preventDefault();
      const response = await fetch('/login', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ email: document.getElementById('loginEmail').value, password: document.getElementById('loginPassword').value }) });
      const data = await response.json();
      if (!data.ok) { return alert(data.error || 'Login failed'); }
      window.location.href = '/dashboard';
    });

    registerForm.addEventListener('submit', async (event) => {
      event.preventDefault();
      const response = await fetch('/register', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ role: document.getElementById('registerRole').value, name: document.getElementById('registerName').value, email: document.getElementById('registerEmail').value, password: document.getElementById('registerPassword').value, age: document.getElementById('registerAge').value, phone: document.getElementById('registerPhone').value }) });
      const data = await response.json();
      if (!data.ok) { return alert(data.error || 'Registration failed'); }
      window.location.href = '/dashboard';
    });

    async function checkEmailStatus() {
      const email = document.getElementById('loginEmail').value.trim();
      const statusElement = document.getElementById('emailStatus');
      if (!email) { statusElement.textContent = ''; return; }
      try {
        const response = await fetch(`/api/patient-exists?email=${encodeURIComponent(email)}`);
        const data = await response.json();
        if (data.exists) {
          statusElement.textContent = 'Existing patient account found. Use Login.';
        } else {
          statusElement.textContent = 'No patient found. Please register as a new patient.';
        }
      } catch (err) {
        statusElement.textContent = '';
      }
    }

    document.getElementById('loginEmail').addEventListener('blur', checkEmailStatus);
  </script>
</body>
</html>
"""

DASHBOARD_PAGE = """
<!doctype html>
<html>
<head>
  <meta charset='utf-8'>
  <title>AgentCare Dashboard</title>
  <style>
    body { margin: 0; font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #eef2ff; color: #111827; }
    .topbar { background: #312e81; color: white; padding: 18px 28px; display: flex; align-items: center; justify-content: space-between; gap: 16px; }
    .topbar h1 { margin: 0; font-size: 1.5rem; }
    .button { border: none; border-radius: 12px; padding: 12px 18px; font-weight: 700; cursor: pointer; }
    .button-primary { background: #4f46e5; color: white; }
    .button-secondary { background: white; color: #111827; border: 1px solid #d1d5db; }
    .shell { max-width: 1280px; margin: 0 auto; padding: 24px; }
    .grid { display: grid; gap: 20px; }
    .grid-3 { grid-template-columns: repeat(3, minmax(0, 1fr)); }
    .grid-2 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .card { background: white; border-radius: 22px; box-shadow: 0 18px 42px rgba(15, 23, 42, .08); padding: 24px; }
    h2 { margin-top: 0; }
    .small-card { background: white; border-radius: 18px; padding: 18px; border: 1px solid #e5e7eb; }
    input, textarea, select { width: 100%; border: 1px solid #d1d5db; border-radius: 14px; padding: 14px; margin-top: 10px; margin-bottom: 10px; }
    table { width: 100%; border-collapse: collapse; margin-top: 14px; }
    th, td { text-align: left; padding: 12px 10px; border-bottom: 1px solid #e5e7eb; }
    th { color: #374151; font-weight: 700; }
    .status-chip { display: inline-flex; gap: 8px; align-items: center; font-size: .92rem; padding: 6px 10px; border-radius: 999px; background: #eef2ff; color: #3730a3; }
    .tabs { display: flex; gap: 12px; flex-wrap: wrap; margin-top: 18px; }
    .tab { border: 1px solid #d1d5db; border-radius: 999px; padding: 10px 16px; cursor: pointer; background: white; }
    .tab.active { background: #4f46e5; color: white; border-color: #4f46e5; }
    .hidden { display: none; }
    .notice { font-size: .95rem; color: #4b5563; margin-top: 8px; }
  </style>
</head>
<body>
  <div class='topbar'>
    <h1>AgentCare Dashboard</h1>
    <div>
      <button class='button button-secondary' onclick='goHome()'>Home</button>
      <button class='button button-primary' onclick='logout()'>Logout</button>
    </div>
  </div>
  <main class='shell'>
    <div id='root'></div>
  </main>
  <script>
    let currentUser = null;
    let dashboardData = null;

    async function fetchJson(url, options) {
      const resp = await fetch(url, options);
      if (resp.status === 401) { window.location.href = '/login'; throw new Error('Unauthorized'); }
      return resp.json();
    }

    function goHome() { window.location.href = '/'; }
    function logout() { fetch('/logout').then(() => window.location.href = '/login'); }

    function createCard(title, value, accent) {
      return `<div class='small-card'><h3>${title}</h3><p style='font-size:2rem; margin:12px 0 0; color:${accent || '#111827'}'>${value}</p></div>`;
    }

    function formatDate(value) { return value ? value.split('T')[0] : '-'; }

    function updatePatientDoctorOptions() {
      const departmentId = document.getElementById('patientDepartmentSelect').value;
      const availableDoctors = dashboardData.available_doctors || [];
      const filtered = availableDoctors.filter(doc => String(doc.department_id) === String(departmentId));
      const select = document.getElementById('patientDoctorSelect');
      select.innerHTML = filtered.length ? filtered.map(doc => `<option value='${doc.id}'>${doc.name} (${doc.specialty})</option>`).join('') : '<option value="">No doctors available</option>';
      if (filtered.length) {
        loadPatientDoctorSchedule();
      } else {
        document.getElementById('patient-doctor-calendar').innerHTML = '<p>No doctor availability for this department.</p>';
      }
    }

    async function loadPatientDoctorSchedule() {
      const doctorId = document.getElementById('patientDoctorSelect').value;
      if (!doctorId) {
        document.getElementById('patient-doctor-calendar').innerHTML = '<p>Select a doctor to view availability.</p>';
        return;
      }
      const schedule = await fetchJson(`/api/doctors/${doctorId}/schedule`);
      document.getElementById('patient-doctor-calendar').innerHTML = `<h3>${schedule.doctor.name}</h3><p><strong>Department:</strong> ${schedule.doctor.department_name}</p><p><strong>Availability:</strong> ${schedule.doctor.availability}</p><h4>Open slots</h4>${schedule.slots.length ? `<table><thead><tr><th>Date</th><th>Time</th><th>Status</th></tr></thead><tbody>${schedule.slots.map(slot => `<tr><td>${slot.slot_date}</td><td>${slot.slot_time}</td><td>${slot.status}</td></tr>`).join('')}</tbody></table>` : '<p>No schedule slots available.</p>'}`;
    }

    function renderPatientDashboard() {
      const patient = dashboardData.patient;
      const upcoming = dashboardData.appointments || [];
      const documents = dashboardData.documents || [];
      const reminders = dashboardData.reminders || [];
      const workflows = dashboardData.workflows || [];
      const availableDoctors = dashboardData.available_doctors || [];
      const availableSlots = dashboardData.available_slots || [];
      const requiredDocuments = dashboardData.required_documents || [];
      const departments = dashboardData.departments || [];
      document.getElementById('root').innerHTML = `
        <div class='grid grid-3'>
          <div class='card'>
            <h2>Patient Information</h2>
            <p><strong>Name:</strong> ${dashboardData.user.name}</p>
            <p><strong>Email:</strong> ${dashboardData.user.email}</p>
            <p><strong>Patient ID:</strong> ${patient.id}</p>
            <p><strong>Age:</strong> ${patient.age || 'N/A'}</p>
            <p><strong>Phone:</strong> ${patient.phone || 'N/A'}</p>
          </div>
          <div class='card'>
            <h2>AI Administrative Assistant</h2>
            <p>Ask in plain English. Example: “I need a cardiology appointment next week and want to upload my previous ECG.”</p>
            <textarea id='requestText' rows='6' placeholder='Type your request here'></textarea>
            <button class='button button-primary' onclick='submitRequest()'>Submit Request</button>
            <div class='notice'>You can request booking, rescheduling, cancellation, document collection, or follow-up reminders.</div>
          </div>
          <div class='card'>
            <h2>Upload Medical Documents</h2>
            <input type='file' id='documentFile'>
            <input type='text' id='documentName' placeholder='Document label, e.g. ECG report'>
            <button class='button button-primary' onclick='uploadDocument()'>Upload Document</button>
            <div class='notice'>Accepted documents are classified automatically and stored in the workflow history.</div>
          </div>
        </div>
        <div class='grid grid-2' style='margin-top: 22px;'>
          <div class='card'>
            <h2>Book by Department</h2>
            <label>Department</label>
            <select id='patientDepartmentSelect' onchange='updatePatientDoctorOptions()'>
              ${departments.map(dep => `<option value='${dep.id}'>${dep.name}</option>`).join('')}
            </select>
            <label>Doctor</label>
            <select id='patientDoctorSelect' onchange='loadPatientDoctorSchedule()'>
              ${availableDoctors.filter(doc => departments.length ? doc.department_id === departments[0].id : true).map(doc => `<option value='${doc.id}'>${doc.name} (${doc.specialty})</option>`).join('')}
            </select>
            <button class='button button-secondary' onclick='loadPatientDoctorSchedule()'>Show Doctor Availability</button>
            <div id='patient-doctor-calendar' style='margin-top:16px;'></div>
          </div>
          <div class='card'>
            <h2>Available Appointment Slots</h2>
            ${availableSlots.length ? `<table><thead><tr><th>Doctor</th><th>Department</th><th>Date</th><th>Time</th></tr></thead><tbody>${availableSlots.map(slot => `<tr><td>${slot.doctor_name}</td><td>${slot.department_name}</td><td>${slot.slot_date}</td><td>${slot.slot_time}</td></tr>`).join('')}</tbody></table>` : '<p>No available slots at this time.</p>'}
          </div>
        </div>
        <div class='card' style='margin-top:22px;'>
          <h2>Required Documents</h2>
          ${requiredDocuments.length ? `<table><thead><tr><th>Document</th><th>Status</th><th>Uploaded At</th></tr></thead><tbody>${requiredDocuments.map(doc => `<tr><td>${doc.document_type.replace(/_/g, ' ')}</td><td>${doc.status}</td><td>${formatDate(doc.uploaded_at)}</td></tr>`).join('')}</tbody></table>` : '<p>No document requirements available yet.</p>'}
        </div>
        <div class='grid grid-2' style='margin-top: 22px;'>
          <div class='card'>
            <h2>Appointment Status</h2>
            ${upcoming.length ? `<table><thead><tr><th>Department</th><th>Doctor</th><th>Date</th><th>Time</th><th>Status</th></tr></thead><tbody>${upcoming.map(row => `<tr><td>${row.department_name}</td><td>${row.doctor_name}</td><td>${row.appointment_date}</td><td>${row.appointment_time}</td><td>${row.status}</td></tr>`).join('')}</tbody></table>` : '<p>No appointments scheduled.</p>'}
          </div>
          <div class='card'>
            <h2>Reminders</h2>
            ${reminders.length ? `<ul>${reminders.map(r => `<li><strong>${r.reminder_type}</strong>: ${r.message} (due ${r.due_at})</li>`).join('')}</ul>` : '<p>No reminders yet.</p>'}
          </div>
        </div>
        <div class='card' style='margin-top:22px;'>
          <h2>Workflow Timeline</h2>
          ${workflows.length ? `<ol>${workflows.map(item => `<li><strong>${item.department}</strong> - ${item.status} (${formatDate(item.created_at)})</li>`).join('')}</ol>` : '<p>No workflows available.</p>'}
        </div>
      `;
    }

    function renderStaffDashboard() {
      const metrics = dashboardData;
      document.getElementById('root').innerHTML = `
        <div class='grid grid-3'>
          ${createCard('Today’s Patients', metrics.patient_count, '#2563eb')}
          ${createCard('Pending Requests', metrics.pending_requests, '#9333ea')}
          ${createCard('Escalations', metrics.escalations, '#dc2626')}
          ${createCard('Upcoming Appointments', metrics.upcoming_appointments, '#047857')}
          ${createCard('Missing Documents', metrics.missing_documents, '#d97706')}
        </div>
        <div class='tabs'>
          <div class='tab active' onclick='showTab("requests")'>Requests</div>
          <div class='tab' onclick='showTab("appointments")'>Appointments</div>
          <div class='tab' onclick='showTab("doctors")'>Doctor Management</div>
          <div class='tab' onclick='showTab("departments")'>Departments</div>
          <div class='tab' onclick='showTab("escalations")'>Escalation Queue</div>
          <div class='tab' onclick='showTab("ai")'>AI Assistant</div>
          <div class='tab' onclick='showTab("audit")'>Audit Logs</div>
          <div class='tab' onclick='showTab("reset")'>System Reset</div>
        </div>
        <div id='staff-content'>
          <div id='requests' class='card'> <h2>Loading requests...</h2> </div>
          <div id='appointments' class='card hidden'> <h2>Loading appointments...</h2> </div>
          <div id='doctors' class='card hidden'> <h2>Loading doctor management...</h2> </div>
          <div id='departments' class='card hidden'> <h2>Loading department schedule...</h2> </div>
          <div id='escalations' class='card hidden'> <h2>Loading escalation queue...</h2> </div>
          <div id='ai' class='card hidden'> <h2>AI Assistant</h2><div id='ai-content'></div> </div>
          <div id='audit' class='card hidden'> <h2>Loading audit logs...</h2> </div>
          <div id='reset' class='card hidden'> <h2>Reset system</h2><div id='reset-content'></div> </div>
        </div>
      `;
      loadStaffTables();
    }

    function showTab(tab) {
      document.querySelectorAll('.tab').forEach(el => el.classList.toggle('active', el.textContent.toLowerCase().startsWith(tab)));
      document.querySelectorAll('#staff-content > div').forEach(div => div.classList.toggle('hidden', div.id !== tab));
    }

    async function loadStaffTables() {
      const [requests, appointments, patients, documents, escalations, audit, doctors, departments] = await Promise.all([
        fetchJson('/api/requests'),
        fetchJson('/api/appointments'),
        fetchJson('/api/patients'),
        fetchJson('/api/documents'),
        fetchJson('/api/escalations'),
        fetchJson('/api/audit-logs'),
        fetchJson('/api/doctors'),
        fetchJson('/api/departments')
      ]);

      document.getElementById('requests').innerHTML = `<h2>Patient Requests</h2>${requests.length ? `<table><thead><tr><th>Patient</th><th>Request</th><th>Status</th><th>Department</th><th>Created</th><th>Action</th></tr></thead><tbody>${requests.map(r => `<tr><td>${r.patient_name}</td><td>${r.request}</td><td>${r.status}</td><td>${r.department}</td><td>${formatDate(r.created_at)}</td><td><button class='button button-secondary' onclick='takeWorkflowAction("${r.id}", "open")'>Open</button> <button class='button button-primary' onclick='takeWorkflowAction("${r.id}", "approved")'>Approve</button> <button class='button button-secondary' onclick='takeWorkflowAction("${r.id}", "escalated")'>Escalate</button> <button class='button button-secondary' onclick='takeWorkflowAction("${r.id}", "rejected")'>Reject</button> <button class='button button-secondary' onclick='showWorkflowAIRequest(${r.patient_id}, "${encodeURIComponent(r.request)}")'>AI Assist</button></td></tr>`).join('')}</tbody></table>` : '<p>No requests found.</p>'}`;

      document.getElementById('appointments').innerHTML = `<h2>Appointments</h2>${appointments.length ? `<table><thead><tr><th>Patient</th><th>Department</th><th>Doctor</th><th>Date</th><th>Time</th><th>Status</th></tr></thead><tbody>${appointments.map(a => `<tr><td>${a.patient_name}</td><td>${a.department}</td><td>${a.doctor_name}</td><td>${a.appointment_date}</td><td>${a.appointment_time}</td><td>${a.status}</td></tr>`).join('')}</tbody></table>` : '<p>No appointments found.</p>'}`;

      document.getElementById('doctors').innerHTML = `<h2>Doctor Management</h2><div class='notice'>Add or update a doctor, then view schedule by doctor.</div><form id='doctorForm'><label>Department</label><select id='doctorDepartment'>${departments.map(dep => `<option value='${dep.id}'>${dep.name}</option>`).join('')}</select><label>Name</label><input type='text' id='doctorName' placeholder='Doctor name'><label>Specialty</label><input type='text' id='doctorSpecialty' placeholder='Specialty'><label>Availability</label><input type='text' id='doctorAvailability' placeholder='Mon-Fri 09:00-17:00'><label>Active</label><select id='doctorActive'><option value='1'>Active</option><option value='0'>Inactive</option></select><button type='button' class='button button-primary' onclick='createDoctor()'>Add Doctor</button></form><div style="margin-top:16px;"><label>View schedule for</label><select id='doctorScheduleSelect'>${doctors.map(doc => `<option value='${doc.id}'>${doc.name} (${doc.department_name})</option>`).join('')}</select><button class='button button-secondary' onclick='loadDoctorSchedule()'>Show Doctor Calendar</button></div><div id='doctor-schedule' style='margin-top:16px;'></div><div style='margin-top:24px;'><h3>Existing Doctors</h3>${doctors.length ? `<table><thead><tr><th>Name</th><th>Department</th><th>Specialty</th><th>Availability</th><th>Active</th></tr></thead><tbody>${doctors.map(doc => `<tr><td>${doc.name}</td><td>${doc.department_name}</td><td>${doc.specialty}</td><td>${doc.availability}</td><td>${doc.active ? 'Yes' : 'No'}</td></tr>`).join('')}</tbody></table>` : '<p>No doctors found.</p>'}</div>`;

      document.getElementById('departments').innerHTML = `<h2>Department Schedules</h2><div class='notice'>View the schedule and appointments for each department.</div><label>Select department</label><select id='departmentScheduleSelect'>${departments.map(dep => `<option value='${dep.id}'>${dep.name}</option>`).join('')}</select><button class='button button-secondary' onclick='loadDepartmentSchedule()'>Show Department Calendar</button><div id='department-schedule' style='margin-top:16px;'></div>`;

      document.getElementById('escalations').innerHTML = `<h2>Escalation Queue</h2>${escalations.length ? `<table><thead><tr><th>Patient</th><th>Reason</th><th>Status</th><th>Created</th></tr></thead><tbody>${escalations.map(e => `<tr><td>${e.patient_name}</td><td>${e.reason}</td><td>${e.status}</td><td>${formatDate(e.created_at)}</td></tr>`).join('')}</tbody></table>` : '<p>No escalations open.</p>'}`;

      document.getElementById('audit').innerHTML = `<h2>Audit Logs</h2>${audit.length ? `<table><thead><tr><th>Entity</th><th>Action</th><th>Details</th><th>Created</th></tr></thead><tbody>${audit.map(a => `<tr><td>${a.entity_type}</td><td>${a.action}</td><td>${a.details}</td><td>${formatDate(a.created_at)}</td></tr>`).join('')}</tbody></table>` : '<p>No audit records found.</p>'}`;

      document.getElementById('ai-content').innerHTML = `<label>Choose patient</label><select id='aiPatientSelect'>${patients.map(p => `<option value='${p.id}'>${p.patient_name} (${p.email})</option>`).join('')}</select><label>AI request</label><textarea id='aiRequestText' rows='4' placeholder='Ask the AI assistant to collect documents, route follow-ups, or diagnose a patient.'></textarea><button class='button button-primary' onclick='submitStaffAIRequest()'>Send AI Request</button><div class='notice'>Examples:Please collect the insurance card and arrange a follow-up reminder for Mary Chen after her neurology visit.</div>`;

      document.getElementById('reset-content').innerHTML = `<label>Confirm password to reset system</label><input type='password' id='resetPassword' placeholder='Staff password'><button class='button button-primary' onclick='resetSystem()'>Reset System</button>`;
    }

    function showWorkflowAIRequest(patientId, promptRequest) {
      const decodedRequest = decodeURIComponent(promptRequest);
      showTab('ai');
      document.querySelectorAll('.tab').forEach(el => el.classList.toggle(el.textContent.trim().toLowerCase() === 'ai assistant', el.textContent.trim().toLowerCase() === 'ai assistant'));
      const patientSelect = document.getElementById('aiPatientSelect');
      if (patientSelect) {
        patientSelect.value = patientId;
      }
      const aiText = document.getElementById('aiRequestText');
      if (aiText) {
        aiText.value = `Please route this request to the right department: ${decodedRequest}`;
      }
    }

    async function submitStaffAIRequest() {
      const patient_id = document.getElementById('aiPatientSelect').value;
      const requestText = document.getElementById('aiRequestText').value.trim();
      if (!requestText) return alert('Enter an AI request.');
      const result = await fetchJson('/api/staff-ai', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ patient_id, request: requestText }) });
      if (!result.ok) return alert(result.error);
      alert('AI request submitted.');
      loadDashboard();
    }

    async function takeWorkflowAction(workflowId, action) {
      const comment = prompt('Optional comment for this action:');
      const result = await fetchJson(`/api/workflows/${workflowId}/action`, { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ action, comment }) });
      alert(result.ok ? `Workflow ${action} completed` : result.error);
      loadDashboard();
    }

    async function createDoctor() {
      const department_id = document.getElementById('doctorDepartment').value;
      const name = document.getElementById('doctorName').value.trim();
      const specialty = document.getElementById('doctorSpecialty').value.trim();
      const availability = document.getElementById('doctorAvailability').value.trim();
      const active = Number(document.getElementById('doctorActive').value);
      if (!name || !specialty || !availability) return alert('Please fill all doctor fields.');
      const result = await fetchJson('/api/doctors', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ department_id, name, specialty, availability, active }) });
      if (!result.ok) return alert(result.error);
      alert('Doctor added');
      loadDashboard();
    }

    async function loadDoctorSchedule() {
      const doctorId = document.getElementById('doctorScheduleSelect').value;
      const schedule = await fetchJson(`/api/doctors/${doctorId}/schedule`);
      document.getElementById('doctor-schedule').innerHTML = `<h3>${schedule.doctor.name} schedule</h3><p><strong>Department:</strong> ${schedule.doctor.department_name}</p><p><strong>Availability:</strong> ${schedule.doctor.availability}</p><h4>Slots</h4>${schedule.slots.length ? `<table><thead><tr><th>Date</th><th>Time</th><th>Status</th></tr></thead><tbody>${schedule.slots.map(slot => `<tr><td>${slot.slot_date}</td><td>${slot.slot_time}</td><td>${slot.status}</td></tr>`).join('')}</tbody></table>` : '<p>No slots.</p>'}<h4>Appointments</h4>${schedule.appointments.length ? `<table><thead><tr><th>Patient</th><th>Date</th><th>Time</th><th>Status</th></tr></thead><tbody>${schedule.appointments.map(a => `<tr><td>${a.patient_name}</td><td>${a.appointment_date}</td><td>${a.appointment_time}</td><td>${a.status}</td></tr>`).join('')}</tbody></table>` : '<p>No appointments.</p>'}`;
    }

    async function loadDepartmentSchedule() {
      const departmentId = document.getElementById('departmentScheduleSelect').value;
      const schedule = await fetchJson(`/api/departments/${departmentId}/schedule`);
      document.getElementById('department-schedule').innerHTML = `<h3>${schedule.department.name} schedule</h3><h4>Doctors</h4>${schedule.doctors.length ? `<table><thead><tr><th>Name</th><th>Specialty</th><th>Availability</th><th>Active</th></tr></thead><tbody>${schedule.doctors.map(d => `<tr><td>${d.name}</td><td>${d.specialty}</td><td>${d.availability}</td><td>${d.active ? 'Yes' : 'No'}</td></tr>`).join('')}</tbody></table>` : '<p>No doctors.</p>'}<h4>Appointments</h4>${schedule.appointments.length ? `<table><thead><tr><th>Patient</th><th>Doctor</th><th>Date</th><th>Time</th><th>Status</th></tr></thead><tbody>${schedule.appointments.map(a => `<tr><td>${a.patient_name}</td><td>${a.doctor_name}</td><td>${a.appointment_date}</td><td>${a.appointment_time}</td><td>${a.status}</td></tr>`).join('')}</tbody></table>` : '<p>No appointments.</p>'}`;
    }

    async function resetSystem() {
      const password = document.getElementById('resetPassword').value;
      if (!password) return alert('Password is required to reset the system.');
      const result = await fetchJson('/api/system/reset', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ password }) });
      if (!result.ok) return alert(result.error);
      alert('System reset complete. Audit log updated.');
      window.location.reload();
    }

    async function submitRequest() {
      const requestText = document.getElementById('requestText').value.trim();
      if (!requestText) return alert('Enter a request.');
      const payload = { request: requestText, patient_name: dashboardData.user.name, patient_email: dashboardData.user.email, patient_age: dashboardData.patient.age, patient_phone: dashboardData.patient.phone };
      const result = await fetchJson('/api/requests', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) });
      alert(`Request submitted: ${result.status}`);
      loadDashboard();
    }

    async function uploadDocument() {
      const fileInput = document.getElementById('documentFile');
      const nameInput = document.getElementById('documentName').value.trim();
      if (!fileInput.files.length) return alert('Select a file to upload.');
      const form = new FormData();
      form.append('file', fileInput.files[0]);
      form.append('document_name', nameInput || fileInput.files[0].name);
      const data = await fetchJson('/api/documents/upload', { method: 'POST', body: form });
      alert(`Upload status: ${data.status}`);
      loadDashboard();
    }

    async function loadDashboard() {
      const data = await fetchJson('/api/dashboard');
      dashboardData = data.dashboard;
      currentUser = data.dashboard.user;
      if (dashboardData.patient) {
        renderPatientDashboard();
      } else {
        renderStaffDashboard();
      }
    }

    loadDashboard();
  </script>
</body>
</html>
"""

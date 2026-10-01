# Campus Guardian

Campus Guardian is a campus safety platform that helps students and staff report incidents quickly and enables authorized responders to monitor, triage, and manage those reports from a central dashboard.

## Project idea

This project focuses on making campus safety faster, smarter, and more visible. Students can submit incident reports with location details and urgency, while responders receive the reports on a live dashboard with AI-assisted triage and prioritization.

## Key features

- Emergency reporting for theft, medical incidents, fire, harassment, suspicious activity, unsafe infrastructure, and other concerns.
- Location-aware reports from a campus map or text-based location field.
- Optional anonymous reporting.
- SOS button for emergency escalation.
- Responder dashboard with active incidents, severity tags, and status tracking.
- AI classification and severity analysis using simple rule-based logic in the MVP.
- Incident lifecycle tracking: Reported → Acknowledged → Responding → Resolved.

## MVP architecture

- Frontend: HTML, CSS, JavaScript
- Backend: Python Flask
- Data layer: in-memory incident list for demo purposes
- AI layer: lightweight rule-based classifier and severity estimator
- UI: report form + responder dashboard

## Project structure

- app.py — Flask application
- templates/index.html — student-facing landing page and incident form
- templates/dashboard.html — responder dashboard
- static/css/style.css — styling for the app
- static/js/main.js — front-end interactions, including SOS button
- requirements.txt — Python dependencies

## Run locally

1. Open the project folder.
2. Create a virtual environment if needed.
3. Install dependencies:

   pip install -r requirements.txt

4. Start the app:

   python app.py

5. Open the browser at:

   http://127.0.0.1:5000/

## Demo flow

- A student opens the home page and submits a suspicious activity report.
- The app automatically analyzes the category and suggests a severity level.
- The responder dashboard shows the incident, its location, and the AI summary.
- Security personnel can monitor and manage the case from one place.

## Suggested next steps

- Add real database storage with MySQL or PostgreSQL.
- Add authentication for responders and students.
- Add map integration with Leaflet and OpenStreetMap.
- Add image upload support.
- Replace rule-based AI with a real ML or NLP model.
- Add email/SMS notifications for emergency alerts.

## Hackathon pitch angle

Campus Guardian turns campus safety into a fast, digital response system: faster reporting, faster triage, and better visibility for security teams.

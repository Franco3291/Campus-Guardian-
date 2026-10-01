# Campus Guardian

Campus Guardian is a campus safety platform built to help students and staff report emergencies quickly while giving authorized responders a centralized place to receive, triage, and manage incident reports.

## Features

- Student incident reporting with category selection and location details.
- Optional anonymous reporting.
- Emergency SOS trigger for urgent situations.
- Role-based login for students and responders.
- SQLite-backed persistence instead of in-memory demo data.
- Responder dashboard with incident status updates and live severity tracking.
- AI-style classification and severity summary for each report.
- Incident lifecycle: Reported → Acknowledged → Responding → Resolved.

## Demo login accounts

- Student: student@campus.edu / password123
- Responder: responder@campus.edu / password123

## Google Maps configuration

To enable live map integration and automatic browser geolocation, add your Google Maps JavaScript API key in the environment before starting the app:

```powershell
$env:GOOGLE_MAPS_API_KEY="YOUR_GOOGLE_MAPS_API_KEY"
python app.py
```

If you do not provide a key, the app still works in demo mode, but the Google map will not load and the browser will only use geolocation for report capture.

## Project structure

- app.py — Flask app and database setup
- templates/index.html — landing page and incident form
- templates/login.html — login screen for both roles
- templates/dashboard.html — responder dashboard with status controls
- static/css/style.css — app styling
- static/js/main.js — SOS interaction logic
- campus_guardian.db — SQLite database generated on first run
- requirements.txt — Python dependencies

## Run locally

1. Open the project folder.
2. Create and activate a virtual environment if needed.
3. Install dependencies:

   python -m venv .venv
   .\.venv\Scripts\activate
   python -m pip install -r requirements.txt

4. Start the app:

   python app.py

5. Open the browser at:

   http://127.0.0.1:5000/

## Hackathon flow

- A student logs in and reports a suspicious activity incident.
- The app classifies the incident and sets a preliminary severity.
- The responder logs in and sees the dashboard with the new alert.
- The responder updates the incident status from Reported to Acknowledged or Responding.

## Next improvements

- Add campus map integration with Leaflet and OpenStreetMap.
- Add photo upload support.
- Add SMS/email notifications for emergency cases.
- Add a real ML model or NLP classifier for incident detection.
- Expand to a multi-role admin dashboard.

## Pitch angle

Campus Guardian turns campus safety into a fast, digital response system: faster reporting, faster triage, and better visibility for the entire campus security team.

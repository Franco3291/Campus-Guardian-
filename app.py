from flask import Flask, jsonify, render_template, request, redirect, url_for

app = Flask(__name__)

INCIDENTS = [
    {
        "id": 101,
        "title": "Suspicious activity near hostel gate",
        "category": "Suspicious Activity",
        "severity": "High",
        "status": "Reported",
        "location": "Student Hostel Area",
        "time": "7:42 PM",
        "reporter": "Anonymous",
        "details": "Two individuals were seen loitering near the hostel entrance after dark.",
        "analysis": {
            "classification": "Suspicious Activity",
            "severity": "High",
            "summary": "Possible loitering near a student accommodation area; immediate check recommended."
        }
    },
    {
        "id": 102,
        "title": "Minor medical incident",
        "category": "Medical Emergency",
        "severity": "Medium",
        "status": "Acknowledged",
        "location": "Library Block",
        "time": "4:15 PM",
        "reporter": "Student",
        "details": "A student reported dizziness and was assisted by a staff member.",
        "analysis": {
            "classification": "Medical Emergency",
            "severity": "Medium",
            "summary": "Student reported dizziness; first aid response is likely sufficient."
        }
    }
]

SEVERITY_BY_CATEGORY = {
    "Theft": "High",
    "Medical Emergency": "High",
    "Fire": "Critical",
    "Assault/Harassment": "Critical",
    "Suspicious Activity": "High",
    "Unsafe Infrastructure": "Medium",
    "Other": "Medium",
}


def analyze_incident(category, details):
    base = category or "Other"
    severity = SEVERITY_BY_CATEGORY.get(base, "Medium")
    summary = details.strip() if details else "No additional detail provided."

    if len(summary) > 120:
        summary = summary[:117] + "..."

    return {
        "classification": base,
        "severity": severity,
        "summary": summary
    }


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', incidents=INCIDENTS)


@app.route('/report', methods=['GET', 'POST'])
def report():
    if request.method == 'POST':
        category = request.form.get('category', 'Other')
        title = request.form.get('title') or 'New incident report'
        location = request.form.get('location') or 'Unknown location'
        details = request.form.get('details', '')
        reporter = 'Anonymous' if request.form.get('anonymous') else 'Student'

        analysis = analyze_incident(category, details)
        incident = {
            "id": max((item['id'] for item in INCIDENTS), default=100) + 1,
            "title": title,
            "category": category,
            "severity": analysis['severity'],
            "status": 'Reported',
            "location": location,
            "time": 'Just now',
            "reporter": reporter,
            "details": details,
            "analysis": analysis
        }
        INCIDENTS.insert(0, incident)
        return redirect(url_for('dashboard'))

    return render_template('index.html')


@app.route('/api/incidents')
def api_incidents():
    return jsonify(INCIDENTS)


@app.route('/sos', methods=['POST'])
def sos():
    incident = {
        "id": max((item['id'] for item in INCIDENTS), default=100) + 1,
        "title": "Emergency SOS activated",
        "category": "Medical Emergency",
        "severity": "Critical",
        "status": "Reported",
        "location": "Campus-wide location tracking",
        "time": "Just now",
        "reporter": "Student",
        "details": "Emergency SOS button pressed by a student. Immediate response required.",
        "analysis": {
            "classification": "Medical Emergency",
            "severity": "Critical",
            "summary": "Emergency alert triggered. Responders should prioritize immediate dispatch."
        }
    }
    INCIDENTS.insert(0, incident)
    return jsonify({"status": "SOS sent", "incident": incident})


if __name__ == '__main__':
    app.run(debug=True)

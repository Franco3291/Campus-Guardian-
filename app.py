import os
import sqlite3
from datetime import datetime

from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'campus-guardian-demo-key')
app.config['DATABASE'] = 'campus_guardian.db'

SEVERITY_BY_CATEGORY = {
    'Theft': 'High',
    'Medical Emergency': 'High',
    'Fire': 'Critical',
    'Assault/Harassment': 'Critical',
    'Suspicious Activity': 'High',
    'Unsafe Infrastructure': 'Medium',
    'Other': 'Medium',
}


def get_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute(
        '''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'student'
        )
        '''
    )
    conn.execute(
        '''
        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            severity TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Reported',
            location TEXT NOT NULL,
            lat REAL,
            lng REAL,
            details TEXT,
            reporter_name TEXT NOT NULL,
            reporter_role TEXT NOT NULL DEFAULT 'student',
            anonymous INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            ai_summary TEXT NOT NULL,
            ai_severity TEXT NOT NULL
        )
        '''
    )
    incident_columns = {
        column['name'] for column in conn.execute('PRAGMA table_info(incidents)').fetchall()
    }
    for column in ('lat', 'lng'):
        if column not in incident_columns:
            conn.execute(f'ALTER TABLE incidents ADD COLUMN {column} REAL')

    user_count = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    if user_count == 0:
        conn.executemany(
            'INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)',
            [
                ('Student User', 'student@campus.edu', generate_password_hash('password123'), 'student'),
                ('Safety Responder', 'responder@campus.edu', generate_password_hash('password123'), 'responder'),
            ],
        )

    incident_count = conn.execute('SELECT COUNT(*) FROM incidents').fetchone()[0]
    if incident_count == 0:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        conn.executemany(
            '''
            INSERT INTO incidents
            (title, category, severity, status, location, lat, lng, details, reporter_name, reporter_role, anonymous, created_at, ai_summary, ai_severity)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            [
                (
                    'Suspicious activity near hostel gate',
                    'Suspicious Activity',
                    'High',
                    'Reported',
                    'Student Hostel Area',
                    6.5288,
                    3.3788,
                    'Two individuals were seen loitering near the hostel entrance after dark.',
                    'Anonymous',
                    'student',
                    1,
                    now,
                    'Possible loitering near student accommodation; a quick check is recommended.',
                    'High',
                ),
                (
                    'Minor medical incident',
                    'Medical Emergency',
                    'Medium',
                    'Acknowledged',
                    'Library Block',
                    6.5164,
                    3.3665,
                    'A student reported dizziness and was assisted by campus staff.',
                    'Student User',
                    'student',
                    0,
                    now,
                    'Student reported dizziness; on-site medical support may be sufficient.',
                    'Medium',
                ),
            ],
        )

    conn.commit()
    conn.close()


def analyze_incident(category, details):
    base = category or 'Other'
    severity = SEVERITY_BY_CATEGORY.get(base, 'Medium')
    summary = (details or 'No additional detail provided.').strip() or 'No additional detail provided.'
    if len(summary) > 140:
        summary = summary[:137] + '...'
    return {
        'classification': base,
        'severity': severity,
        'summary': summary,
    }


def current_user():
    user_id = session.get('user_id')
    if not user_id:
        return None
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return user


def login_required(role=None):
    def decorator(view):
        def wrapped(*args, **kwargs):
            user = current_user()
            if not user:
                return redirect(url_for('login'))
            if role and user['role'] != role:
                return redirect(url_for('dashboard'))
            return view(*args, **kwargs)
        wrapped.__name__ = view.__name__
        return wrapped
    return decorator


@app.route('/')
def home():
    user = current_user()
    conn = get_db()
    incidents = conn.execute(
        'SELECT * FROM incidents ORDER BY created_at DESC LIMIT 5'
    ).fetchall()
    conn.close()
    return render_template('index.html', user=user, incidents=incidents, google_maps_api_key=os.environ.get('GOOGLE_MAPS_API_KEY', ''))


@app.route('/login', methods=['GET', 'POST'])
def login():
    user = current_user()
    if user:
        return redirect(url_for('dashboard'))

    error = None
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        role = request.form.get('role', 'student')
        conn = get_db()
        user_record = conn.execute(
            'SELECT * FROM users WHERE email = ? AND role = ?',
            (email, role),
        ).fetchone()
        conn.close()

        if user_record and check_password_hash(user_record['password_hash'], password):
            session['user_id'] = user_record['id']
            session['role'] = user_record['role']
            session['name'] = user_record['name']
            return redirect(url_for('dashboard'))

        error = 'Invalid email, password, or selected role.'

    return render_template('login.html', user=None, error=error)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


@app.route('/dashboard')
@login_required()
def dashboard():
    conn = get_db()
    incidents = conn.execute(
        'SELECT * FROM incidents ORDER BY created_at DESC'
    ).fetchall()
    map_incidents = [
        {
            'lat': incident['lat'],
            'lng': incident['lng'],
            'title': incident['title'],
            'category': incident['category'],
            'severity': incident['severity'],
            'status': incident['status'],
        }
        for incident in incidents
        if incident['lat'] is not None and incident['lng'] is not None
    ]
    stats = {
        'total': conn.execute('SELECT COUNT(*) FROM incidents').fetchone()[0],
        'high': conn.execute("SELECT COUNT(*) FROM incidents WHERE severity = 'High'").fetchone()[0],
        'critical': conn.execute("SELECT COUNT(*) FROM incidents WHERE severity = 'Critical'").fetchone()[0],
        'reported': conn.execute("SELECT COUNT(*) FROM incidents WHERE status = 'Reported'").fetchone()[0],
    }
    conn.close()
    return render_template('dashboard.html', user=current_user(), incidents=incidents, map_incidents=map_incidents, stats=stats, google_maps_api_key=os.environ.get('GOOGLE_MAPS_API_KEY', ''))


@app.route('/report', methods=['POST'])
@login_required()
def report():
    title = request.form.get('title') or 'New incident report'
    category = request.form.get('category', 'Other')
    location = request.form.get('location') or 'Unknown location'
    lat = request.form.get('lat')
    lng = request.form.get('lng')
    details = request.form.get('details', '')
    anonymous = 'anonymous' in request.form
    analysis = analyze_incident(category, details)

    user = current_user()
    reporter_name = 'Anonymous' if anonymous else (user['name'] if user else 'Student')
    reporter_role = user['role'] if user else 'student'

    conn = get_db()
    conn.execute(
        '''
        INSERT INTO incidents
        (title, category, severity, status, location, lat, lng, details, reporter_name, reporter_role, anonymous, created_at, ai_summary, ai_severity)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        (
            title,
            category,
            analysis['severity'],
            'Reported',
            location,
            float(lat) if lat not in (None, '') else None,
            float(lng) if lng not in (None, '') else None,
            details,
            reporter_name,
            reporter_role,
            1 if anonymous else 0,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            analysis['summary'],
            analysis['severity'],
        ),
    )
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))


@app.route('/incident/<int:incident_id>/status', methods=['POST'])
@login_required(role='responder')
def update_incident_status(incident_id):
    new_status = request.form.get('status', 'Acknowledged')
    conn = get_db()
    conn.execute('UPDATE incidents SET status = ? WHERE id = ?', (new_status, incident_id))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))


@app.route('/api/incidents')
def api_incidents():
    conn = get_db()
    rows = conn.execute('SELECT * FROM incidents ORDER BY created_at DESC').fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])


@app.route('/sos', methods=['POST'])
@login_required()
def sos():
    user = current_user()
    location = request.form.get('location') or 'Campus-wide emergency tracking'
    lat = request.form.get('lat')
    lng = request.form.get('lng')
    conn = get_db()
    analysis = analyze_incident('Medical Emergency', 'Emergency SOS activated by a campus user.')
    conn.execute(
        '''
        INSERT INTO incidents
        (title, category, severity, status, location, lat, lng, details, reporter_name, reporter_role, anonymous, created_at, ai_summary, ai_severity)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        (
            'Emergency SOS activated',
            'Medical Emergency',
            'Critical',
            'Reported',
            location,
            float(lat) if lat not in (None, '') else None,
            float(lng) if lng not in (None, '') else None,
            'Emergency SOS was triggered. Immediate response required.',
            user['name'] if user else 'Student',
            user['role'] if user else 'student',
            0,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            analysis['summary'],
            analysis['severity'],
        ),
    )
    conn.commit()
    conn.close()
    return jsonify({'status': 'SOS sent', 'message': 'Emergency alert sent to responders.'})


if __name__ == '__main__':
    init_db()
    app.run(debug=True)

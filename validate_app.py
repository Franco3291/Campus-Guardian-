from app import app

client = app.test_client()
resp = client.post(
    '/login',
    data={
        'role': 'responder',
        'email': 'responder@campus.edu',
        'password': 'password123',
    },
    follow_redirects=True,
)
print('status=', resp.status_code)
print('has_dashboard=', 'Campus safety overview' in resp.get_data(as_text=True))
print('has_login=', '/login' in resp.get_data(as_text=True))
print('has_title=', 'Campus Guardian Dashboard' in resp.get_data(as_text=True))

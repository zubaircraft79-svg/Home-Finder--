from app.models import User
from conftest import login_with_otp


def test_user_registration(client, app):
    res = client.post("/auth/register", data={
        "full_name": "New User",
        "email": "new@example.com",
        "password": "Password123!",
        "gdpr_consent": "on",
    }, follow_redirects=True)
    assert res.status_code == 200
    with app.app_context():
        assert User.query.filter_by(email="new@example.com").first() is not None


def test_login_invalid_credentials(client):
    res = client.post("/auth/login", data={"email": "user@example.com", "password": "bad"})
    assert res.status_code == 401


def test_otp_success_and_failure(client):
    client.post("/auth/login", data={"email": "user@example.com", "password": "Password123!"})
    bad = client.post("/auth/verify-otp", data={"otp": "000000"})
    assert bad.status_code == 401
    good = login_with_otp(client)
    assert b"Property listings" in good.data

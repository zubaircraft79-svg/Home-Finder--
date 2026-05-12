import pytest
from app import create_app
from app.config import TestConfig
from app.extensions import db
from app.seed import seed_database


@pytest.fixture()
def app():
    app = create_app(TestConfig)
    with app.app_context():
        seed_database()
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


def login_with_otp(client, email="user@example.com", password="Password123!"):
    from app.models import Notification, User
    client.post("/auth/login", data={"email": email, "password": password})
    with client.application.app_context():
        user = User.query.filter_by(email=email).first()
        note = Notification.query.filter_by(user_id=user.id, notification_type="otp").order_by(Notification.created_at.desc()).first()
        code = note.message.rsplit(" ", 1)[-1]
        return client.post("/auth/verify-otp", data={"otp": code}, follow_redirects=True)
    raise AssertionError("OTP not found")

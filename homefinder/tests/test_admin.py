from conftest import login_with_otp
from app.models import Property


def test_role_protection(client):
    login_with_otp(client)
    assert client.get("/admin/").status_code == 403
    assert client.get("/supervisor/").status_code == 403


def test_admin_property_creation(client, app):
    login_with_otp(client, "admin@example.com", "Admin123!")
    res = client.post("/admin/properties/new", data={
        "title": "Test Office",
        "description": "Professional office listing for tests.",
        "property_type": "commercial",
        "location": "Athens",
        "address": "Test Street 1",
        "price": "100000",
        "bedrooms": "0",
        "bathrooms": "1",
        "area_sq_m": "80",
        "amenities": "metro",
        "status": "available",
    }, follow_redirects=True)
    assert res.status_code == 200
    with app.app_context():
        assert Property.query.filter_by(title="Test Office").first() is not None


def test_supervisor_access(client):
    login_with_otp(client, "supervisor@example.com", "Supervisor123!")
    assert client.get("/supervisor/").status_code == 200
    assert client.get("/admin/").status_code == 403

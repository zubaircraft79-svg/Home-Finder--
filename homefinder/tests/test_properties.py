from app.models import Enquiry, Favourite, ViewingBooking
from conftest import login_with_otp


def test_property_listing_loads_and_filtering(client):
    res = client.get("/properties/")
    assert res.status_code == 200
    assert b"Modern Apartment in Athens" in res.data
    filtered = client.get("/properties/?location=Glyfada&property_type=residential")
    assert filtered.status_code == 200
    assert b"Family House in Glyfada" in filtered.data


def test_favourite_add_remove(client, app):
    login_with_otp(client)
    client.post("/properties/2/favourite")
    with app.app_context():
        assert Favourite.query.filter_by(property_id=2).first() is not None
    client.post("/properties/2/favourite/remove")
    with app.app_context():
        assert Favourite.query.filter_by(property_id=2).first() is None


def test_enquiry_and_booking_submission(client, app):
    login_with_otp(client)
    client.post("/properties/1/enquiry", data={"name": "Demo User", "email": "user@example.com", "phone": "2101002000", "message": "Please send viewing details."})
    client.post("/properties/1/booking", data={"preferred_date": "2026-06-01", "preferred_time": "10:00", "note": "Morning"})
    with app.app_context():
        assert Enquiry.query.filter_by(property_id=1).count() >= 1
        assert ViewingBooking.query.filter_by(property_id=1).count() == 1

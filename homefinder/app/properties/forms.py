from datetime import datetime
from app.auth.forms import clean_text, validate_email


def validate_enquiry(form):
    errors = []
    data = {
        "name": clean_text(form.get("name"), 120),
        "email": clean_text(form.get("email"), 255),
        "phone": clean_text(form.get("phone"), 40),
        "message": clean_text(form.get("message"), 1000),
    }
    if not data["name"]:
        errors.append("Name is required.")
    if not validate_email(data["email"]):
        errors.append("Valid email is required.")
    if len(data["phone"]) < 7:
        errors.append("Phone number is required.")
    if len(data["message"]) < 10:
        errors.append("Message must be at least 10 characters.")
    return data, errors


def validate_booking(form):
    errors = []
    data = {
        "preferred_date": None,
        "preferred_time": clean_text(form.get("preferred_time"), 20),
        "note": clean_text(form.get("note"), 500),
    }
    try:
        data["preferred_date"] = datetime.strptime(form.get("preferred_date", ""), "%Y-%m-%d").date()
    except ValueError:
        errors.append("Valid preferred date is required.")
    if not data["preferred_time"]:
        errors.append("Preferred time is required.")
    return data, errors

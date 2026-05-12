from app.auth.forms import clean_text


def validate_property(form):
    errors = []
    data = {
        "title": clean_text(form.get("title"), 180),
        "description": clean_text(form.get("description"), 3000),
        "property_type": clean_text(form.get("property_type"), 30),
        "location": clean_text(form.get("location"), 120),
        "address": clean_text(form.get("address"), 255),
        "price": form.get("price", type=int),
        "bedrooms": form.get("bedrooms", type=int) or 0,
        "bathrooms": form.get("bathrooms", type=int) or 0,
        "area_sq_m": form.get("area_sq_m", type=int),
        "amenities": clean_text(form.get("amenities"), 400),
        "status": clean_text(form.get("status"), 30),
        "is_premium": bool(form.get("is_premium")),
        "image_url": clean_text(form.get("image_url"), 500),
    }
    for field in ["title", "description", "property_type", "location", "address", "status"]:
        if not data[field]:
            errors.append(f"{field.replace('_', ' ').title()} is required.")
    if data["property_type"] not in {"residential", "commercial", "rental"}:
        errors.append("Property type is invalid.")
    if data["status"] not in {"available", "unavailable"}:
        errors.append("Status is invalid.")
    if not data["price"] or data["price"] <= 0:
        errors.append("Price must be positive.")
    if not data["area_sq_m"] or data["area_sq_m"] <= 0:
        errors.append("Area must be positive.")
    return data, errors

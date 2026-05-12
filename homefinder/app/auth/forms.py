import re


def validate_email(value):
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", value or ""))


def validate_password(value):
    return bool(value and len(value) >= 8 and re.search(r"[A-Z]", value) and re.search(r"\d", value))


def clean_text(value, max_len=255):
    return (value or "").strip()[:max_len]

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def database_uri():
    uri = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'homefinder.db'}")
    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql+psycopg://", 1)
    elif uri.startswith("postgresql://"):
        uri = uri.replace("postgresql://", "postgresql+psycopg://", 1)
    return uri


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-homefinder-secret")
    SQLALCHEMY_DATABASE_URI = database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    SHOW_DEV_OTP = os.getenv("SHOW_DEV_OTP", "true").lower() == "true"
    AUTO_SEED = os.getenv("AUTO_SEED", "false").lower() == "true"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"
    PREFERRED_URL_SCHEME = os.getenv("PREFERRED_URL_SCHEME", "http")
    PER_PAGE = 6


class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SHOW_DEV_OTP = True

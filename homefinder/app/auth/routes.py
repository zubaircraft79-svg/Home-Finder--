import random
import secrets
from datetime import datetime, timedelta
from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_user, logout_user
from werkzeug.security import generate_password_hash
from app.auth.forms import clean_text, validate_email, validate_password
from app.extensions import db
from app.models import ActivityLog, Notification, OTPCode, User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def log_action(action, description, user=None):
    actor = user or (current_user if current_user.is_authenticated else None)
    db.session.add(ActivityLog(
        user_id=actor.id if actor else None,
        role=actor.role if actor else "guest",
        action=action,
        description=description,
        ip_address=request.remote_addr,
    ))


def create_otp(user):
    code = f"{random.randint(100000, 999999)}"
    otp = OTPCode(user_id=user.id, code_hash=generate_password_hash(code), expires_at=datetime.utcnow() + timedelta(minutes=5))
    db.session.add(otp)
    msg = "OTP sent. Check your email."
    if current_app.config["SHOW_DEV_OTP"]:
        msg = f"Development OTP: {code}"
    db.session.add(Notification(user_id=user.id, title="Login verification code", message=msg, notification_type="otp"))
    log_action("otp_sent", "OTP generated for login verification.", user)
    db.session.commit()
    return code


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    if request.method == "POST":
        full_name = clean_text(request.form.get("full_name"), 120)
        email = clean_text(request.form.get("email"), 255).lower()
        password = request.form.get("password", "")
        role = clean_text(request.form.get("role"), 20) or "user"
        consent = bool(request.form.get("gdpr_consent"))
        errors = []
        if not full_name:
            errors.append("Full name is required.")
        if not validate_email(email):
            errors.append("Valid email is required.")
        if not validate_password(password):
            errors.append("Password must be 8+ chars with uppercase and number.")
        if not consent:
            errors.append("GDPR consent is required.")
        if role not in {"user", "seller"}:
            errors.append("Account type is invalid.")
        if User.query.filter_by(email=email).first():
            errors.append("Email already registered.")
        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template("auth/register.html"), 400
        user = User(full_name=full_name, email=email, role=role, gdpr_consent=True)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()
        log_action("register", f"User registered: {email}", user)
        db.session.commit()
        flash("Account created. Please log in.", "success")
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    if request.method == "POST":
        email = clean_text(request.form.get("email"), 255).lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()
        log_action("login_attempt", f"Login attempt for {email}", user)
        if not user or not user.check_password(password) or not user.is_active:
            db.session.commit()
            flash("Invalid credentials.", "danger")
            return render_template("auth/login.html"), 401
        session["pending_otp_user_id"] = user.id
        dev_code = create_otp(user)
        if current_app.config["SHOW_DEV_OTP"]:
            session["dev_otp_code"] = dev_code
            flash(f"Development OTP: {dev_code}", "info")
        else:
            flash("OTP generated. Check your email notification.", "info")
        return redirect(url_for("auth.verify_otp"))
    return render_template("auth/login.html")


@auth_bp.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():
    user_id = session.get("pending_otp_user_id")
    if not user_id:
        return redirect(url_for("auth.login"))
    user = db.session.get(User, user_id)
    if not user:
        return redirect(url_for("auth.login"))
    latest_otp = OTPCode.query.filter_by(user_id=user.id, used=False).order_by(OTPCode.created_at.desc()).first()
    if request.method == "POST":
        code = clean_text(request.form.get("otp"), 10)
        if not latest_otp or latest_otp.expires_at < datetime.utcnow() or not latest_otp.check_code(code):
            flash("Invalid or expired OTP.", "danger")
            return render_template("auth/verify_otp.html", dev_code=session.get("dev_otp_code")), 401
        latest_otp.used = True
        token = secrets.token_hex(32)
        user.active_session_token = token
        user.last_login_at = datetime.utcnow()
        login_user(user)
        session["session_token"] = token
        session.pop("pending_otp_user_id", None)
        session.pop("dev_otp_code", None)
        log_action("otp_verified", "OTP verified.", user)
        log_action("login_success", "User logged in.", user)
        db.session.commit()
        flash("Login successful.", "success")
        if user.role == "admin":
            return redirect(url_for("admin.dashboard"))
        if user.role == "seller":
            return redirect(url_for("seller.dashboard"))
        if user.role == "supervisor":
            return redirect(url_for("supervisor.dashboard"))
        return redirect(url_for("properties.list_properties"))
    return render_template("auth/verify_otp.html", dev_code=session.get("dev_otp_code"))


@auth_bp.route("/logout")
def logout():
    if current_user.is_authenticated:
        current_user.active_session_token = None
        log_action("logout", "User logged out.", current_user)
        db.session.commit()
    logout_user()
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for("main.index"))

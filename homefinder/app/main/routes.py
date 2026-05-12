from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from app.extensions import db
from app.models import ActivityLog, Property

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    premium = Property.query.filter_by(is_premium=True, status="available").limit(3).all()
    newest = Property.query.order_by(Property.created_at.desc()).limit(6).all()
    return render_template("index.html", premium=premium, newest=newest)


@main_bp.route("/privacy")
def privacy():
    return render_template("privacy.html")


@main_bp.route("/premium")
def premium_services():
    premium = Property.query.filter_by(is_premium=True, status="available").order_by(Property.created_at.desc()).limit(6).all()
    return render_template("premium.html", premium=premium)


@main_bp.route("/request-data-deletion", methods=["POST"])
@login_required
def request_data_deletion():
    current_user.data_deletion_requested = True
    db.session.add(ActivityLog(user_id=current_user.id, role=current_user.role, action="data_deletion_requested", description="User requested personal data deletion."))
    db.session.commit()
    flash("Data deletion request recorded for the demo.", "success")
    return redirect(url_for("main.privacy"))

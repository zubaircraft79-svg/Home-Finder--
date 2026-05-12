from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from app.extensions import db
from app.models import Notification

notifications_bp = Blueprint("notifications", __name__, url_prefix="/notifications")


@notifications_bp.route("/")
@login_required
def list_notifications():
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    return render_template("notifications.html", notifications=notifications)


@notifications_bp.route("/mark-read", methods=["POST"])
@login_required
def mark_read():
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({"is_read": True})
    db.session.commit()
    flash("Notifications marked as read.", "success")
    return redirect(url_for("notifications.list_notifications"))

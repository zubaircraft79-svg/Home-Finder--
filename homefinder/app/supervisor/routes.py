from collections import Counter
from datetime import date
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user
from sqlalchemy import extract
from app.decorators import roles_required
from app.extensions import db
from app.models import ActivityLog, Enquiry, Favourite, Property, ReportSnapshot, ViewingBooking

supervisor_bp = Blueprint("supervisor", __name__, url_prefix="/supervisor")


def month_filter(model, month, year):
    return model.query.filter(extract("month", model.created_at) == month, extract("year", model.created_at) == year)


def popular_property_field(field):
    values = [getattr(p, field) for p in Property.query.all()]
    return Counter(values).most_common(1)[0][0] if values else "N/A"


@supervisor_bp.route("/")
@roles_required("supervisor")
def dashboard():
    stats = {
        "searches": ActivityLog.query.filter_by(action="property_search").count(),
        "enquiries": Enquiry.query.count(),
        "favourites": Favourite.query.count(),
        "viewings": ViewingBooking.query.count(),
        "reports": ReportSnapshot.query.count(),
    }
    saved = db.session.query(Property.title, db.func.count(Favourite.id).label("count")).join(Favourite).group_by(Property.id).order_by(db.desc("count")).limit(5).all()
    return render_template("supervisor/dashboard.html", stats=stats, saved=saved)


@supervisor_bp.route("/reports", methods=["GET", "POST"])
@roles_required("supervisor")
def reports():
    today = date.today()
    if request.method == "POST":
        month = request.form.get("month", today.month, type=int)
        year = request.form.get("year", today.year, type=int)
        snapshot = ReportSnapshot(
            generated_by=current_user.id,
            month=month,
            year=year,
            total_searches=month_filter(ActivityLog, month, year).filter_by(action="property_search").count(),
            total_enquiries=month_filter(Enquiry, month, year).count(),
            total_favourites=month_filter(Favourite, month, year).count(),
            total_viewings=month_filter(ViewingBooking, month, year).count(),
            popular_location=popular_property_field("location"),
            popular_property_type=popular_property_field("property_type"),
        )
        db.session.add(snapshot)
        db.session.add(ActivityLog(user_id=current_user.id, role=current_user.role, action="report_generated", description=f"Generated report {month}/{year}", ip_address=request.remote_addr))
        db.session.commit()
        flash("Monthly report snapshot generated.", "success")
        return redirect(url_for("supervisor.reports"))
    snapshots = ReportSnapshot.query.order_by(ReportSnapshot.created_at.desc()).all()
    return render_template("supervisor/reports.html", snapshots=snapshots, today=today)


@supervisor_bp.route("/activity-logs")
@roles_required("supervisor")
def activity_logs():
    page = request.args.get("page", 1, type=int)
    logs = ActivityLog.query.order_by(ActivityLog.created_at.desc()).paginate(page=page, per_page=25, error_out=False)
    return render_template("supervisor/activity_logs.html", logs=logs)

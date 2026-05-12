from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user
from app.admin.forms import validate_property
from app.decorators import roles_required
from app.extensions import db
from app.models import ActivityLog, Enquiry, Property, ViewingBooking

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_log(action, description):
    db.session.add(ActivityLog(user_id=current_user.id, role=current_user.role, action=action, description=description, ip_address=request.remote_addr))


@admin_bp.route("/")
@roles_required("admin")
def dashboard():
    stats = {
        "total_properties": Property.query.count(),
        "active_listings": Property.query.filter_by(status="available").count(),
        "enquiries": Enquiry.query.count(),
        "viewings": ViewingBooking.query.count(),
        "premium": Property.query.filter_by(is_premium=True).count(),
    }
    recent_enquiries = Enquiry.query.order_by(Enquiry.created_at.desc()).limit(5).all()
    return render_template("admin/dashboard.html", stats=stats, recent_enquiries=recent_enquiries)


@admin_bp.route("/properties")
@roles_required("admin")
def properties():
    props = Property.query.order_by(Property.created_at.desc()).all()
    return render_template("admin/properties.html", properties=props)


@admin_bp.route("/properties/new", methods=["GET", "POST"])
@roles_required("admin")
def property_create():
    if request.method == "POST":
        data, errors = validate_property(request.form)
        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template("admin/property_form.html", property=None), 400
        prop = Property(**data, created_by=current_user.id)
        db.session.add(prop)
        db.session.flush()
        admin_log("admin_property_created", f"Created property {prop.title}")
        db.session.commit()
        flash("Property created.", "success")
        return redirect(url_for("admin.properties"))
    return render_template("admin/property_form.html", property=None)


@admin_bp.route("/properties/<int:property_id>/edit", methods=["GET", "POST"])
@roles_required("admin")
def property_edit(property_id):
    prop = db.session.get(Property, property_id) or abort(404)
    if request.method == "POST":
        data, errors = validate_property(request.form)
        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template("admin/property_form.html", property=prop), 400
        for key, value in data.items():
            setattr(prop, key, value)
        admin_log("admin_property_updated", f"Updated property {prop.title}")
        db.session.commit()
        flash("Property updated.", "success")
        return redirect(url_for("admin.properties"))
    return render_template("admin/property_form.html", property=prop)


@admin_bp.route("/properties/<int:property_id>/delete", methods=["POST"])
@roles_required("admin")
def property_delete(property_id):
    prop = db.session.get(Property, property_id) or abort(404)
    prop.status = "unavailable"
    admin_log("admin_property_deleted", f"Deactivated property {prop.title}")
    db.session.commit()
    flash("Property deactivated.", "info")
    return redirect(url_for("admin.properties"))


@admin_bp.route("/enquiries", methods=["GET", "POST"])
@roles_required("admin")
def enquiries():
    if request.method == "POST":
        row = db.session.get(Enquiry, request.form.get("enquiry_id", type=int)) or abort(404)
        status = request.form.get("status")
        if status in {"new", "in_progress", "resolved"}:
            row.status = status
            db.session.commit()
            flash("Enquiry status updated.", "success")
    rows = Enquiry.query.order_by(Enquiry.created_at.desc()).all()
    return render_template("admin/enquiries.html", enquiries=rows)


@admin_bp.route("/viewings", methods=["GET", "POST"])
@roles_required("admin")
def viewings():
    if request.method == "POST":
        row = db.session.get(ViewingBooking, request.form.get("booking_id", type=int)) or abort(404)
        status = request.form.get("status")
        if status in {"pending", "confirmed", "cancelled"}:
            row.status = status
            db.session.commit()
            flash("Viewing status updated.", "success")
    rows = ViewingBooking.query.order_by(ViewingBooking.created_at.desc()).all()
    return render_template("admin/viewings.html", bookings=rows)

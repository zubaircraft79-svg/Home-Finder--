from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user
from sqlalchemy import func
from app.admin.forms import validate_property
from app.decorators import roles_required
from app.extensions import db
from app.models import ActivityLog, Enquiry, Property, PropertyView, ViewingBooking

seller_bp = Blueprint("seller", __name__, url_prefix="/seller")


def seller_log(action, description):
    db.session.add(ActivityLog(user_id=current_user.id, role=current_user.role, action=action, description=description, ip_address=request.remote_addr))


def seller_property_or_404(property_id):
    prop = db.session.get(Property, property_id) or abort(404)
    if prop.created_by != current_user.id:
        abort(403)
    return prop


@seller_bp.route("/")
@roles_required("seller")
def dashboard():
    ids = [row.id for row in Property.query.filter_by(created_by=current_user.id).all()]
    stats = {
        "my_properties": len(ids),
        "active_listings": Property.query.filter_by(created_by=current_user.id, status="available").count(),
        "customer_views": PropertyView.query.filter(PropertyView.property_id.in_(ids)).count() if ids else 0,
        "enquiries": Enquiry.query.filter(Enquiry.property_id.in_(ids)).count() if ids else 0,
        "viewings": ViewingBooking.query.filter(ViewingBooking.property_id.in_(ids)).count() if ids else 0,
    }
    top_properties = (
        db.session.query(Property, func.count(PropertyView.id).label("view_count"))
        .outerjoin(PropertyView, PropertyView.property_id == Property.id)
        .filter(Property.created_by == current_user.id)
        .group_by(Property.id)
        .order_by(func.count(PropertyView.id).desc(), Property.created_at.desc())
        .limit(5)
        .all()
    )
    recent_enquiries = Enquiry.query.join(Property).filter(Property.created_by == current_user.id).order_by(Enquiry.created_at.desc()).limit(5).all()
    return render_template("seller/dashboard.html", stats=stats, top_properties=top_properties, recent_enquiries=recent_enquiries)


@seller_bp.route("/properties")
@roles_required("seller")
def properties():
    props = (
        db.session.query(Property, func.count(PropertyView.id).label("view_count"))
        .outerjoin(PropertyView, PropertyView.property_id == Property.id)
        .filter(Property.created_by == current_user.id)
        .group_by(Property.id)
        .order_by(Property.created_at.desc())
        .all()
    )
    return render_template("seller/properties.html", properties=props)


@seller_bp.route("/properties/new", methods=["GET", "POST"])
@roles_required("seller")
def property_create():
    if request.method == "POST":
        data, errors = validate_property(request.form)
        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template("seller/property_form.html", property=None), 400
        prop = Property(**data, created_by=current_user.id)
        db.session.add(prop)
        db.session.flush()
        seller_log("seller_property_created", f"Seller created property {prop.title}")
        db.session.commit()
        flash("Listing posted.", "success")
        return redirect(url_for("seller.properties"))
    return render_template("seller/property_form.html", property=None)


@seller_bp.route("/properties/<int:property_id>/edit", methods=["GET", "POST"])
@roles_required("seller")
def property_edit(property_id):
    prop = seller_property_or_404(property_id)
    if request.method == "POST":
        data, errors = validate_property(request.form)
        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template("seller/property_form.html", property=prop), 400
        for key, value in data.items():
            setattr(prop, key, value)
        seller_log("seller_property_updated", f"Seller updated property {prop.title}")
        db.session.commit()
        flash("Listing updated.", "success")
        return redirect(url_for("seller.properties"))
    return render_template("seller/property_form.html", property=prop)


@seller_bp.route("/properties/<int:property_id>/delete", methods=["POST"])
@roles_required("seller")
def property_delete(property_id):
    prop = seller_property_or_404(property_id)
    prop.status = "unavailable"
    seller_log("seller_property_deactivated", f"Seller deactivated property {prop.title}")
    db.session.commit()
    flash("Listing deactivated.", "info")
    return redirect(url_for("seller.properties"))


@seller_bp.route("/enquiries", methods=["GET", "POST"])
@roles_required("seller")
def enquiries():
    if request.method == "POST":
        row = db.session.get(Enquiry, request.form.get("enquiry_id", type=int)) or abort(404)
        if row.property.created_by != current_user.id:
            abort(403)
        status = request.form.get("status")
        if status in {"new", "in_progress", "resolved"}:
            row.status = status
            db.session.commit()
            flash("Enquiry status updated.", "success")
    rows = Enquiry.query.join(Property).filter(Property.created_by == current_user.id).order_by(Enquiry.created_at.desc()).all()
    return render_template("seller/enquiries.html", enquiries=rows)


@seller_bp.route("/viewings", methods=["GET", "POST"])
@roles_required("seller")
def viewings():
    if request.method == "POST":
        row = db.session.get(ViewingBooking, request.form.get("booking_id", type=int)) or abort(404)
        if row.property.created_by != current_user.id:
            abort(403)
        status = request.form.get("status")
        if status in {"pending", "confirmed", "cancelled"}:
            row.status = status
            db.session.commit()
            flash("Viewing status updated.", "success")
    rows = ViewingBooking.query.join(Property).filter(Property.created_by == current_user.id).order_by(ViewingBooking.created_at.desc()).all()
    return render_template("seller/viewings.html", bookings=rows)

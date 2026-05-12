from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_
from app.extensions import db
from app.main.forms import clean_search_args
from app.models import ActivityLog, Enquiry, Favourite, Notification, Property, PropertyView, ViewingBooking
from app.properties.forms import validate_booking, validate_enquiry

properties_bp = Blueprint("properties", __name__, url_prefix="/properties")


def log(action, description):
    db.session.add(ActivityLog(
        user_id=current_user.id if current_user.is_authenticated else None,
        role=current_user.role if current_user.is_authenticated else "guest",
        action=action,
        description=description,
        ip_address=request.remote_addr,
    ))


def filtered_query(args):
    query = Property.query
    if args["q"]:
        like = f"%{args['q']}%"
        query = query.filter(or_(Property.title.ilike(like), Property.description.ilike(like), Property.location.ilike(like)))
    if args["location"]:
        query = query.filter(Property.location.ilike(f"%{args['location']}%"))
    if args["property_type"]:
        query = query.filter_by(property_type=args["property_type"])
    if args["min_price"]:
        query = query.filter(Property.price >= args["min_price"])
    if args["max_price"]:
        query = query.filter(Property.price <= args["max_price"])
    if args["bedrooms"] is not None:
        query = query.filter(Property.bedrooms >= args["bedrooms"])
    if args["amenities"]:
        query = query.filter(Property.amenities.ilike(f"%{args['amenities']}%"))
    if args["status"]:
        query = query.filter_by(status=args["status"])
    if args["premium"]:
        query = query.filter_by(is_premium=True)
    if args["sort"] == "price_low":
        query = query.order_by(Property.price.asc())
    elif args["sort"] == "price_high":
        query = query.order_by(Property.price.desc())
    else:
        query = query.order_by(Property.is_premium.desc(), Property.created_at.desc())
    return query


@properties_bp.route("/")
def list_properties():
    args = clean_search_args(request.args)
    query = filtered_query(args)
    pagination = query.paginate(page=args["page"], per_page=6, error_out=False)
    query_args = request.args.to_dict(flat=True)
    query_args.pop("page", None)
    if any(v for k, v in args.items() if k not in {"sort", "page"} and v):
        log("property_search", f"Search/filter used: {dict(request.args)}")
        db.session.commit()
    return render_template("properties/list.html", properties=pagination.items, pagination=pagination, filters=args, query_args=query_args)


@properties_bp.route("/<int:property_id>")
def detail(property_id):
    prop = db.session.get(Property, property_id) or abort(404)
    is_owner_view = current_user.is_authenticated and current_user.id == prop.created_by
    if not is_owner_view:
        db.session.add(PropertyView(property_id=prop.id, user_id=current_user.id if current_user.is_authenticated else None, ip_address=request.remote_addr))
    log("property_view", f"Viewed property {prop.title}")
    db.session.commit()
    similar = Property.query.filter(Property.id != prop.id).filter(or_(Property.location == prop.location, Property.property_type == prop.property_type)).limit(3).all()
    is_favourite = False
    if current_user.is_authenticated:
        is_favourite = Favourite.query.filter_by(user_id=current_user.id, property_id=prop.id).first() is not None
    return render_template("properties/detail.html", property=prop, similar=similar, is_favourite=is_favourite)


@properties_bp.route("/favourites")
@login_required
def favourites():
    rows = Favourite.query.filter_by(user_id=current_user.id).order_by(Favourite.created_at.desc()).all()
    return render_template("properties/favourites.html", favourites=rows)


@properties_bp.route("/<int:property_id>/favourite", methods=["POST"])
@login_required
def add_favourite(property_id):
    prop = db.session.get(Property, property_id) or abort(404)
    existing = Favourite.query.filter_by(user_id=current_user.id, property_id=prop.id).first()
    if not existing:
        db.session.add(Favourite(user_id=current_user.id, property_id=prop.id))
        db.session.add(ActivityLog(user_id=current_user.id, role=current_user.role, action="favourite_added", description=f"Added favourite: {prop.title}"))
        flash("Property saved.", "success")
    db.session.commit()
    return redirect(request.referrer or url_for("properties.detail", property_id=prop.id))


@properties_bp.route("/<int:property_id>/favourite/remove", methods=["POST"])
@login_required
def remove_favourite(property_id):
    row = Favourite.query.filter_by(user_id=current_user.id, property_id=property_id).first()
    if row:
        title = row.property.title
        db.session.delete(row)
        db.session.add(ActivityLog(user_id=current_user.id, role=current_user.role, action="favourite_removed", description=f"Removed favourite: {title}"))
        db.session.commit()
        flash("Property removed from favourites.", "info")
    return redirect(request.referrer or url_for("properties.favourites"))


@properties_bp.route("/<int:property_id>/enquiry", methods=["GET", "POST"])
@login_required
def enquiry(property_id):
    prop = db.session.get(Property, property_id) or abort(404)
    if request.method == "POST":
        data, errors = validate_enquiry(request.form)
        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template("properties/enquiry.html", property=prop), 400
        db.session.add(Enquiry(user_id=current_user.id, property_id=prop.id, **data))
        db.session.add(Notification(user_id=current_user.id, title="Enquiry submitted", message=f"We received your enquiry for {prop.title}.", notification_type="enquiry"))
        if prop.created_by and prop.created_by != current_user.id:
            db.session.add(Notification(user_id=prop.created_by, title="New customer enquiry", message=f"{data['name']} enquired about {prop.title}.", notification_type="seller_enquiry"))
        db.session.add(ActivityLog(user_id=current_user.id, role=current_user.role, action="enquiry_submitted", description=f"Submitted enquiry for {prop.title}"))
        db.session.commit()
        flash("Enquiry submitted.", "success")
        return redirect(url_for("properties.detail", property_id=prop.id))
    return render_template("properties/enquiry.html", property=prop)


@properties_bp.route("/<int:property_id>/booking", methods=["GET", "POST"])
@login_required
def booking(property_id):
    prop = db.session.get(Property, property_id) or abort(404)
    if request.method == "POST":
        data, errors = validate_booking(request.form)
        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template("properties/booking.html", property=prop), 400
        db.session.add(ViewingBooking(user_id=current_user.id, property_id=prop.id, **data))
        db.session.add(Notification(user_id=current_user.id, title="Viewing requested", message=f"Viewing request recorded for {prop.title}.", notification_type="booking"))
        if prop.created_by and prop.created_by != current_user.id:
            db.session.add(Notification(user_id=prop.created_by, title="New viewing request", message=f"A customer requested a viewing for {prop.title}.", notification_type="seller_booking"))
        db.session.add(ActivityLog(user_id=current_user.id, role=current_user.role, action="viewing_scheduled", description=f"Scheduled viewing for {prop.title}"))
        db.session.commit()
        flash("Viewing request submitted.", "success")
        return redirect(url_for("properties.detail", property_id=prop.id))
    return render_template("properties/booking.html", property=prop)


@properties_bp.route("/<int:property_id>/subscribe-similar", methods=["POST"])
@login_required
def subscribe_similar(property_id):
    prop = db.session.get(Property, property_id) or abort(404)
    db.session.add(Notification(user_id=current_user.id, title="Similar listing alert", message=f"You subscribed to alerts similar to {prop.title}.", notification_type="similar_listing"))
    db.session.commit()
    flash("Similar listing alert created.", "success")
    return redirect(url_for("properties.detail", property_id=prop.id))

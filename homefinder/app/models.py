from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from .extensions import db, login_manager


class TimestampMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class User(UserMixin, TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="user", nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    gdpr_consent = db.Column(db.Boolean, default=False, nullable=False)
    last_login_at = db.Column(db.DateTime)
    active_session_token = db.Column(db.String(64))
    data_deletion_requested = db.Column(db.Boolean, default=False, nullable=False)

    favourites = db.relationship("Favourite", back_populates="user", cascade="all, delete-orphan")
    enquiries = db.relationship("Enquiry", back_populates="user")
    viewing_bookings = db.relationship("ViewingBooking", back_populates="user")
    listed_properties = db.relationship("Property", back_populates="seller", foreign_keys="Property.created_by")
    property_views = db.relationship("PropertyView", back_populates="user")
    activity_logs = db.relationship("ActivityLog", back_populates="user")
    notifications = db.relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    otp_codes = db.relationship("OTPCode", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


class Property(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(180), nullable=False)
    description = db.Column(db.Text, nullable=False)
    property_type = db.Column(db.String(30), nullable=False, index=True)
    location = db.Column(db.String(120), nullable=False, index=True)
    address = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    bedrooms = db.Column(db.Integer, default=0)
    bathrooms = db.Column(db.Integer, default=0)
    area_sq_m = db.Column(db.Integer, nullable=False)
    amenities = db.Column(db.String(400), default="")
    status = db.Column(db.String(30), default="available", nullable=False)
    is_premium = db.Column(db.Boolean, default=False, nullable=False)
    image_url = db.Column(db.String(500))
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"))

    seller = db.relationship("User", back_populates="listed_properties", foreign_keys=[created_by])
    enquiries = db.relationship("Enquiry", back_populates="property", cascade="all, delete-orphan")
    viewing_bookings = db.relationship("ViewingBooking", back_populates="property", cascade="all, delete-orphan")
    favourites = db.relationship("Favourite", back_populates="property", cascade="all, delete-orphan")
    views = db.relationship("PropertyView", back_populates="property", cascade="all, delete-orphan")

    @property
    def amenity_list(self):
        return [item.strip() for item in (self.amenities or "").split(",") if item.strip()]

    @property
    def image_gallery(self):
        fallback = {
            "residential": [
                "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?auto=format&fit=crop&w=1400&q=80",
                "https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?auto=format&fit=crop&w=1400&q=80",
                "https://images.unsplash.com/photo-1600585154526-990dced4db0d?auto=format&fit=crop&w=1400&q=80",
            ],
            "commercial": [
                "https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&w=1400&q=80",
                "https://images.unsplash.com/photo-1497366412874-3415097a27e7?auto=format&fit=crop&w=1400&q=80",
                "https://images.unsplash.com/photo-1497366754035-f200968a6e72?auto=format&fit=crop&w=1400&q=80",
            ],
            "rental": [
                "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&w=1400&q=80",
                "https://images.unsplash.com/photo-1484154218962-a197022b5858?auto=format&fit=crop&w=1400&q=80",
                "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&w=1400&q=80",
            ],
        }
        urls = [item.strip() for item in (self.image_url or "").replace("\n", ",").split(",") if item.strip()]
        urls.extend(fallback.get(self.property_type, fallback["residential"]))
        unique = []
        for url in urls:
            if url not in unique:
                unique.append(url)
        return unique[:3]


class Favourite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey("property.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    __table_args__ = (db.UniqueConstraint("user_id", "property_id", name="uq_user_property_favourite"),)

    user = db.relationship("User", back_populates="favourites")
    property = db.relationship("Property", back_populates="favourites")


class PropertyView(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey("property.id"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    ip_address = db.Column(db.String(80))
    viewed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    property = db.relationship("Property", back_populates="views")
    user = db.relationship("User", back_populates="property_views")


class Enquiry(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey("property.id"), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(40), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(30), default="new", nullable=False)

    user = db.relationship("User", back_populates="enquiries")
    property = db.relationship("Property", back_populates="enquiries")


class ViewingBooking(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey("property.id"), nullable=False)
    preferred_date = db.Column(db.Date, nullable=False)
    preferred_time = db.Column(db.String(20), nullable=False)
    note = db.Column(db.Text)
    status = db.Column(db.String(30), default="pending", nullable=False)

    user = db.relationship("User", back_populates="viewing_bookings")
    property = db.relationship("Property", back_populates="viewing_bookings")


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    title = db.Column(db.String(160), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(40), default="system", nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", back_populates="notifications")


class OTPCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    code_hash = db.Column(db.String(255), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", back_populates="otp_codes")

    def check_code(self, code):
        return check_password_hash(self.code_hash, code)


class ActivityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    role = db.Column(db.String(30))
    action = db.Column(db.String(80), nullable=False, index=True)
    description = db.Column(db.String(500), nullable=False)
    ip_address = db.Column(db.String(80))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    user = db.relationship("User", back_populates="activity_logs")


class ReportSnapshot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    generated_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    total_searches = db.Column(db.Integer, default=0)
    total_enquiries = db.Column(db.Integer, default=0)
    total_favourites = db.Column(db.Integer, default=0)
    total_viewings = db.Column(db.Integer, default=0)
    popular_location = db.Column(db.String(120))
    popular_property_type = db.Column(db.String(30))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

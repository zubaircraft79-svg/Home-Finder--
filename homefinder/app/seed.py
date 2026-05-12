from datetime import date, datetime, timedelta
from werkzeug.security import generate_password_hash
from .extensions import db
from .models import ActivityLog, Enquiry, Favourite, Notification, Property, PropertyView, ReportSnapshot, User, ViewingBooking


PROPERTIES = [
    ("Modern Apartment in Athens", "Bright two-bedroom apartment with balcony, renovated kitchen, and quick access to cafes and offices.", "residential", "Athens", "Kolonaki, Athens", 285000, 2, 1, 86, "balcony,metro,parking,renovated", "available", True, "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=1200&q=80"),
    ("Family House in Glyfada", "Detached family home with garden, generous living spaces, and schools nearby.", "residential", "Glyfada", "Ano Glyfada", 640000, 4, 3, 210, "garden,parking,fireplace,storage", "available", False, "https://images.unsplash.com/photo-1564013799919-ab600027ffc6?auto=format&fit=crop&w=1200&q=80"),
    ("Commercial Office in Syntagma", "Professional office floor suitable for legal, finance, or consultancy firms.", "commercial", "Syntagma", "Syntagma Square", 520000, 0, 2, 145, "elevator,metro,security,meeting rooms", "available", True, "https://images.unsplash.com/photo-1497366754035-f200968a6e72?auto=format&fit=crop&w=1200&q=80"),
    ("Rental Studio in Piraeus", "Efficient furnished studio near port and university transit routes.", "rental", "Piraeus", "Terpsithea, Piraeus", 620, 1, 1, 38, "furnished,metro,air conditioning", "available", False, "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&w=1200&q=80"),
    ("Luxury Villa in Voula", "Premium villa with pool, sea-view terraces, smart-home systems, and private parking.", "residential", "Voula", "Panorama Voula", 1850000, 5, 5, 420, "pool,sea view,garden,smart home,parking", "available", True, "https://images.unsplash.com/photo-1613977257363-707ba9348227?auto=format&fit=crop&w=1200&q=80"),
    ("Student Apartment near Metro", "Compact apartment ideal for students, close to metro, supermarkets, and campus routes.", "rental", "Athens", "Ambelokipi, Athens", 780, 1, 1, 48, "metro,furnished,balcony", "unavailable", False, "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&w=1200&q=80"),
    ("Retail Space in Monastiraki", "High-footfall retail unit with frontage on a busy tourist route.", "commercial", "Monastiraki", "Ermou District", 390000, 0, 1, 92, "street frontage,storage,metro", "available", False, "https://images.unsplash.com/photo-1441986300917-64674bd600d8?auto=format&fit=crop&w=1200&q=80"),
    ("Furnished Rental in Kallithea", "Move-in ready rental with two bedrooms, modern appliances, and quick access to Syggrou Avenue.", "rental", "Kallithea", "Central Kallithea", 980, 2, 1, 74, "furnished,balcony,renovated,parking", "available", True, "https://images.unsplash.com/photo-1484154218962-a197022b5858?auto=format&fit=crop&w=1200&q=80"),
    ("Seaside Apartment in Alimos", "Contemporary apartment near marina with sea breeze, balcony, and open-plan living.", "residential", "Alimos", "Alimos Marina", 450000, 3, 2, 118, "sea view,balcony,parking,elevator", "available", False, "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&w=1200&q=80"),
    ("Business Office in Marousi", "Flexible office suite in business district with reception area and conference space.", "commercial", "Marousi", "Kifisias Avenue", 610000, 0, 2, 175, "parking,security,meeting rooms,elevator", "unavailable", True, "https://images.unsplash.com/photo-1497366811353-6870744d04b2?auto=format&fit=crop&w=1200&q=80"),
]


def seed_database():
    db.drop_all()
    db.create_all()
    users = [
        User(full_name="Demo User", email="user@example.com", role="user", gdpr_consent=True),
        User(full_name="Admin Manager", email="admin@example.com", role="admin", gdpr_consent=True),
        User(full_name="Supervisor Lead", email="supervisor@example.com", role="supervisor", gdpr_consent=True),
        User(full_name="Seller Partner", email="seller@example.com", role="seller", gdpr_consent=True),
    ]
    for user, password in zip(users, ["Password123!", "Admin123!", "Supervisor123!", "Seller123!"]):
        user.password_hash = generate_password_hash(password)
        db.session.add(user)
    db.session.flush()
    for item in PROPERTIES:
        db.session.add(Property(
            title=item[0], description=item[1], property_type=item[2], location=item[3], address=item[4],
            price=item[5], bedrooms=item[6], bathrooms=item[7], area_sq_m=item[8], amenities=item[9],
            status=item[10], is_premium=item[11], image_url=item[12], created_by=users[3].id if item[2] == "residential" else users[1].id
        ))
    db.session.flush()
    db.session.add(Favourite(user_id=users[0].id, property_id=1))
    db.session.add(Enquiry(user_id=users[0].id, property_id=1, name="Demo User", email="user@example.com", phone="+30 210 100 2000", message="I would like more details."))
    db.session.add(ViewingBooking(user_id=users[0].id, property_id=2, preferred_date=date.today() + timedelta(days=3), preferred_time="11:00", note="Weekend preferred."))
    db.session.add(PropertyView(user_id=users[0].id, property_id=1, ip_address="127.0.0.1"))
    db.session.add(PropertyView(user_id=None, property_id=1, ip_address="127.0.0.1"))
    db.session.add(Notification(user_id=users[0].id, title="Welcome to HomeFinder", message="Your demo account is ready.", notification_type="system"))
    db.session.add(ActivityLog(user_id=users[0].id, role="user", action="property_search", description="Seeded search trend for Athens", created_at=datetime.utcnow()))
    db.session.add(ReportSnapshot(generated_by=users[2].id, month=date.today().month, year=date.today().year, total_searches=1, total_enquiries=1, total_favourites=1, total_viewings=1, popular_location="Athens", popular_property_type="residential"))
    db.session.commit()

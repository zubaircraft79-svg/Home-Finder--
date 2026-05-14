# HomeFinder Portal - Project Documentation

## 1. Project Name

HomeFinder Portal

## 2. Project Type

Full-stack Flask real estate web application for a university Software Engineering project.

## 3. Project Purpose

HomeFinder Portal is an online real estate platform where users can browse, search, save, enquire about, and book viewings for properties. The system supports multiple roles: normal users, sellers, admins, and supervisors.

The website is designed as a realistic property portal prototype with authentication, OTP verification, seller listing management, admin management, supervisor reporting, notifications, premium listings, activity logs, seeded demo data, and deployment support.

## 4. Main User Roles

### Normal User / Customer

Customers can register, log in, verify OTP, browse properties, search/filter listings, view property details, use the photo gallery, save favourites, send enquiries, book viewings, subscribe to similar listing alerts, view notifications, and request data deletion.

### Seller

Sellers can register as sellers, log in with OTP, access a seller dashboard, post properties, edit their own properties, deactivate their own properties, promote listings as premium, view customer view counts, manage enquiries, manage viewing bookings, and receive customer notifications.

### Admin

Admins can access the admin dashboard, view platform statistics, add properties, edit any property, deactivate any property, manage all enquiries, and manage all viewing bookings.

### Supervisor

Supervisors can access reports, generate report snapshots, and view activity logs.

## 5. Technology Stack

### Backend

- Python
- Flask
- Flask Blueprints
- SQLAlchemy ORM
- Flask-Login
- Werkzeug password hashing
- Gunicorn

### Database

- SQLite locally
- PostgreSQL online
- `DATABASE_URL` support

### Frontend

- HTML5
- CSS3
- JavaScript
- Jinja2 templates
- Custom responsive UI

### Testing

- Pytest
- Flask test client

### Deployment

- Render
- Render Blueprint
- Gunicorn
- PostgreSQL

## 6. Project Structure

```text
homefinder/
  app/
    __init__.py
    config.py
    decorators.py
    extensions.py
    models.py
    seed.py
    admin/
    auth/
    main/
    notifications/
    properties/
    seller/
    supervisor/
    static/
      css/
      js/
      images/
    templates/
      admin/
      auth/
      errors/
      properties/
      seller/
      supervisor/
  tests/
  .env.example
  .gitignore
  Procfile
  README.md
  PROJECT_DOCUMENTATION.md
  render.yaml
  requirements.txt
  run.py
  runtime.txt
```

## 7. Important Files

### `run.py`

Starts the Flask application and exposes `app` for Gunicorn.

Production command:

```text
gunicorn run:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120
```

### `app/__init__.py`

Main Flask app factory.

It creates the app, loads config, initializes database/login manager, registers blueprints, enforces one active session per user, injects notification counts, handles errors, adds `/health`, creates tables, and auto-seeds when enabled.

### `app/config.py`

Stores configuration for local and online use.

Supports:

- SQLite locally
- PostgreSQL online
- `DATABASE_URL`
- secure cookies
- `AUTO_SEED`
- `SHOW_DEV_OTP`

### `app/models.py`

Contains all database models.

### `app/seed.py`

Creates demo database data.

### `render.yaml`

Render deployment configuration.

### `requirements.txt`

Python dependencies.

## 8. Database Models

### User

Stores accounts.

Important fields:

- full name
- email
- password hash
- role
- active session token
- GDPR consent
- data deletion request flag

Roles:

- user
- seller
- admin
- supervisor

### Property

Stores property listings.

Important fields:

- title
- description
- property type
- location
- address
- price
- bedrooms
- bathrooms
- area
- amenities
- status
- premium flag
- image URL
- creator/seller ID

Property types:

- residential
- commercial
- rental

Statuses:

- available
- unavailable

### PropertyView

Tracks customer views on properties. Sellers use this to see listing interest.

### Favourite

Stores saved properties for users.

### Enquiry

Stores customer enquiry messages.

Statuses:

- new
- in_progress
- resolved

### ViewingBooking

Stores customer viewing requests.

Statuses:

- pending
- confirmed
- cancelled

### Notification

Stores notifications for users, sellers, and OTP messages.

### OTPCode

Stores hashed OTP login codes.

### ActivityLog

Stores audit logs for important actions.

### ReportSnapshot

Stores supervisor monthly report snapshots.

## 9. Authentication Flow

1. User enters email and password.
2. System checks hashed password.
3. System creates a six-digit OTP.
4. OTP is hashed and stored.
5. OTP notification is created.
6. In demo mode, OTP is shown on screen.
7. User submits OTP.
8. System verifies OTP.
9. User is logged in.
10. Active session token is generated.
11. User is redirected by role.

Redirects:

- user -> property listings
- seller -> seller dashboard
- admin -> admin dashboard
- supervisor -> supervisor dashboard

## 10. Security Features

- hashed passwords
- hashed OTP codes
- OTP expiry
- one active session per user
- role-based route protection
- HTTP-only session cookies
- SameSite cookies
- secure cookie support for HTTPS
- activity logging
- input cleaning

## 11. Main Pages

### Home Page

Includes hero section, search form, browse properties button, premium services button, premium listings, and newest listings.

### Property Listings Page

Includes keyword search, location filter, property type filter, price filters, bedroom filter, amenities filter, status filter, premium-only filter, sorting, and pagination.

### Property Detail Page

Includes 3-photo gallery, price, location, description, amenities, favourite button, enquiry button, booking button, premium note, and similar properties.

### Premium Page

Explains premium services and shows current premium listings.

### Seller Dashboard

Shows seller property stats, active listings, customer views, enquiries, viewings, most viewed listings, and recent enquiries.

### Admin Dashboard

Shows overall property and request management tools.

### Supervisor Dashboard

Shows reports and activity logs.

## 12. Premium Feature

Customers can view premium listings, see premium badges, use premium-only search, and open premium page.

Sellers can promote listings as premium and track customer views.

## 13. Property Gallery Feature

Each property has at least 3 photos.

The app uses the property main image plus fallback images by property type.

Users can:

- click next
- click previous
- click dots
- swipe on touch screens

## 14. Demo Data

Seed command creates:

- 4 demo users
- 10 properties
- favourite
- enquiry
- viewing booking
- property views
- notification
- activity log
- supervisor report snapshot

Run seed:

```powershell
python -m flask --app run.py seed
```

## 15. Demo Accounts

Normal user:

```text
user@example.com / Password123!
```

Seller:

```text
seller@example.com / Seller123!
```

Admin:

```text
admin@example.com / Admin123!
```

Supervisor:

```text
supervisor@example.com / Supervisor123!
```

## 16. Seeded Properties

1. Modern Apartment in Athens
2. Family House in Glyfada
3. Commercial Office in Syntagma
4. Rental Studio in Piraeus
5. Luxury Villa in Voula
6. Student Apartment near Metro
7. Retail Space in Monastiraki
8. Furnished Rental in Kallithea
9. Seaside Apartment in Alimos
10. Business Office in Marousi

Residential properties are assigned to the seller account. Commercial and rental properties are assigned to the admin account.

## 17. Local Setup

```powershell
cd "C:\Users\zubai\Desktop\SW_homeFInder - zubi version\homefinder"
python -m pip install -r requirements.txt
python -m flask --app run.py seed
python -m flask --app run.py run
```

Open:

```text
http://127.0.0.1:5000
```

## 18. Testing

Run:

```powershell
python -m pytest tests -p no:cacheprovider
```

Tests cover:

- registration
- invalid login
- OTP login
- property listing/filtering
- favourites
- enquiries
- bookings
- admin property creation
- role protection
- seller dashboard
- seller listing creation
- seller analytics
- seller notifications

## 19. Deployment

The app supports Render hosting.

Important files:

- `render.yaml`
- `Procfile`
- `requirements.txt`
- `runtime.txt`

Build command:

```text
python -m pip install --upgrade pip && python -m pip install -r requirements.txt
```

Start command:

```text
gunicorn run:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120
```

Required environment variables:

```text
SECRET_KEY
DATABASE_URL
SHOW_DEV_OTP=true
AUTO_SEED=true
SESSION_COOKIE_SECURE=true
PREFERRED_URL_SCHEME=https
```

Health route:

```text
/health
```

Expected response:

```json
{"status":"ok"}
```

## 20. Database Notes

Local database:

```text
homefinder.db
```

Online database:

```text
PostgreSQL through DATABASE_URL
```

Important:

- Render does not use local `homefinder.db`.
- Online demo data appears only if `AUTO_SEED=true`.
- Auto-seed runs only when the online database has zero users.

## 21. Limitations

- OTP is simulated.
- Premium payment is not real.
- Property images use URLs, not uploads.
- No database migration tool.
- No real payment system.
- No real email system.
- Render free database can expire.
- Render free service can sleep after inactivity.

## 22. Future Improvements

- Real email OTP.
- Real payment integration.
- Image uploads.
- Cloud image storage.
- Flask-Migrate.
- Admin user management.
- Seller verification.
- Map view.
- Saved searches.
- Property comparison.
- Better charts.
- Production monitoring.

## 23. Final Summary

HomeFinder Portal is a complete Flask real estate platform prototype. It includes customer property browsing, seller listing management, premium listings, admin management, supervisor reporting, OTP login, notifications, activity logs, seeded demo data, tests, and Render deployment support.


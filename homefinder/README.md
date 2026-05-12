# HomeFinder Portal

Professional full-stack Flask real estate portal for university Software Engineering Scenario 2.

## Features

- User registration, password hashing, login, OTP/2FA simulation, one active session per user
- Role-based access for user, seller, admin, and supervisor
- Property browse/search/filter/sort with backend SQLAlchemy queries and pagination
- Favourites, enquiries, viewing bookings, similar listing notification subscription
- Seller dashboard for posting listings, tracking views, and managing customer requests
- Admin dashboard for listing, enquiry, and viewing management
- Supervisor dashboard with monthly report snapshots and activity logs
- Notifications, GDPR consent, privacy page, deletion request marker
- Premium services placeholder with no real payment processing
- Activity logging for key user/admin/supervisor actions
- Pytest unit/integration examples

## Tech Stack

- Python Flask, Blueprints, Jinja2
- SQLAlchemy ORM with SQLite
- Flask-Login sessions
- Werkzeug password and OTP hashing
- HTML5, CSS3, JavaScript
- Pytest

## Setup

```powershell
cd C:\Users\zubai\Desktop\SW_homeFInder\homefinder
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:FLASK_APP="run.py"
flask seed
flask run
```

Open `http://127.0.0.1:5000`.

## Demo Accounts

- Normal user: `user@example.com` / `Password123!`
- Seller: `seller@example.com` / `Seller123!`
- Admin: `admin@example.com` / `Admin123!`
- Supervisor: `supervisor@example.com` / `Supervisor123!`

In development mode, OTP is shown in the OTP notification text and flashed after login flow.

## Tests

```powershell
cd C:\Users\zubai\Desktop\SW_homeFInder\homefinder
python -m pytest tests -p no:cacheprovider
```

## Free Hosting After GitHub Upload

Recommended free option: Render Blueprint with a free Python web service plus free Render Postgres.

### What is already configured

- `render.yaml` creates the Flask web service and a Postgres database.
- `gunicorn` starts the backend with `gunicorn run:app --bind 0.0.0.0:$PORT`.
- `DATABASE_URL` is connected automatically from Render Postgres.
- `AUTO_SEED=true` creates demo users and properties when the cloud database is empty.
- `/health` returns `{"status":"ok"}` for a quick deployment check.
- `.gitignore` keeps local SQLite DBs, logs, virtualenvs, and cache folders out of GitHub.

### Deploy steps

1. Create a new GitHub repository.
2. Upload the contents of this `homefinder` folder as the repository root.
3. Make sure these files are at the GitHub repo root:
   - `render.yaml`
   - `run.py`
   - `requirements.txt`
   - `runtime.txt`
   - `app/`
4. Go to Render.
5. Choose **New > Blueprint**.
6. Connect the GitHub repository.
7. Render reads `render.yaml`; approve the free web service and free Postgres database.
8. Click **Apply** / **Deploy**.
9. Wait for build and deploy to finish.
10. Open the generated `https://...onrender.com` URL.
11. Test `/health`. It should show:

```json
{"status":"ok"}
```

### Demo accounts online

After first deploy, `AUTO_SEED=true` creates:

- Normal user: `user@example.com` / `Password123!`
- Seller: `seller@example.com` / `Seller123!`
- Admin: `admin@example.com` / `Admin123!`
- Supervisor: `supervisor@example.com` / `Supervisor123!`

Important notes:

- Do not use SQLite on Render for live demo data. Render free web service filesystem is temporary, so local SQLite files disappear after redeploy/restart.
- This project uses `DATABASE_URL`; on Render it connects to Postgres automatically.
- `AUTO_SEED=true` seeds demo users/properties only when the cloud database is empty.
- `SHOW_DEV_OTP=true` shows OTP on the verification page for demonstration. Turn it off if real email sending is later added.
- Free Render web apps sleep after 15 minutes of inactivity, so first load can take about a minute.
- Free Render Postgres databases expire after 30 days. Good for university demo; not permanent production storage.
- Local uploaded files are not safe on Render free services. This app uses image URLs, so property photos are safe.

### Manual Render web service fallback

If Blueprint fails, create manually:

- Service type: Web Service
- Runtime: Python 3
- Build command: `python -m pip install --upgrade pip && python -m pip install -r requirements.txt`
- Start command: `gunicorn run:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120`
- Add free Postgres, then set web service env var `DATABASE_URL` to the Postgres connection string.
- Env vars:
  - `SECRET_KEY`: generate random value
  - `AUTO_SEED`: `true`
  - `SHOW_DEV_OTP`: `true`
  - `SESSION_COOKIE_SECURE`: `true`
  - `PREFERRED_URL_SCHEME`: `https`

## Project Structure

```text
homefinder/
  app/
    auth/ main/ properties/ admin/ supervisor/ notifications/
    templates/
    static/
    models.py seed.py extensions.py config.py decorators.py
  tests/
  run.py
  requirements.txt
  .env.example
```

## University Demonstration Notes

Show normal user flow first: register/login, OTP, search/filter, save, enquire, book viewing, notifications, privacy deletion request. Then log in as seller to post a property, review listing views, and manage customer requests. Then log in as admin to manage all listings and requests. Then log in as supervisor to generate monthly report snapshot and inspect activity logs. Database schema uses relationships and constraints suitable for documentation diagrams.

from flask import Flask, jsonify, render_template, session
from flask_login import current_user, logout_user
from werkzeug.middleware.proxy_fix import ProxyFix
from .config import Config
from .extensions import db, login_manager
from .models import Notification


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
    db.init_app(app)
    login_manager.init_app(app)

    from .auth.routes import auth_bp
    from .main.routes import main_bp
    from .properties.routes import properties_bp
    from .admin.routes import admin_bp
    from .seller.routes import seller_bp
    from .supervisor.routes import supervisor_bp
    from .notifications.routes import notifications_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(properties_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(seller_bp)
    app.register_blueprint(supervisor_bp)
    app.register_blueprint(notifications_bp)

    @app.before_request
    def enforce_single_session():
        if current_user.is_authenticated:
            token = session.get("session_token")
            if not token or token != current_user.active_session_token:
                logout_user()
                session.clear()

    @app.context_processor
    def inject_notifications():
        unread = 0
        if current_user.is_authenticated:
            unread = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
        return {"unread_notifications": unread}

    @app.errorhandler(403)
    def forbidden(error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(401)
    def unauthorized(error):
        return render_template("errors/401.html"), 401

    @app.get("/health")
    def health():
        return jsonify(status="ok")

    @app.cli.command("seed")
    def seed_command():
        from .seed import seed_database
        seed_database()
        print("Seeded HomeFinder demo data.")

    with app.app_context():
        db.create_all()
        if app.config.get("AUTO_SEED"):
            from .models import User
            if User.query.count() == 0:
                from .seed import seed_database
                seed_database()

    return app

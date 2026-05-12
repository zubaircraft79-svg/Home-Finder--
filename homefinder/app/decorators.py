from functools import wraps
from flask import abort, redirect, session, url_for
from flask_login import current_user


def roles_required(*roles):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for("auth.login"))
            if current_user.role not in roles:
                abort(403)
            return view(*args, **kwargs)
        return wrapped
    return decorator


def active_session_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if current_user.is_authenticated:
            token = session.get("session_token")
            if not token or token != current_user.active_session_token:
                abort(401)
        return view(*args, **kwargs)
    return wrapped

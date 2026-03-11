from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user

def role_required(*allowed_roles):
    """
    Decorator to check if the current user has one of the allowed roles.
    Must be used *after* @login_required.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('frontend.login'))
                
            if current_user.role not in allowed_roles:
                flash('You do not have permission to access that page.', 'danger')
                return redirect(url_for('frontend.dashboard'))
                
            return fn(*args, **kwargs)
        return wrapper
    return decorator

from functools import wraps
from flask import abort, redirect, url_for, flash
from flask_login import current_user


def admin_required(f):
    """Decorator to restrict access strictly to Admin users."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if not current_user.is_admin:
            flash('Access Denied: Administrative privileges required.', 'danger')
            return redirect(url_for('jobs.index'))
        return f(*args, **kwargs)
    return decorated_function

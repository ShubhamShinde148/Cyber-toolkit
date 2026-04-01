import re
from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user
import ipaddress

def login_required_v2(f):
    """
    Custom login_required decorator for the V2 platform.
    Redirects unauthenticated users to the V2 login page instead of the legacy one.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth_bp.login'))
        return f(*args, **kwargs)
    return decorated_function

def is_valid_ip(ip_str):
    """Validate IPv4 or IPv6 address."""
    try:
        ipaddress.ip_address(ip_str)
        return True
    except ValueError:
        return False

def is_valid_domain(domain_str):
    """Basic validation for domain formatting avoiding injection."""
    pattern = re.compile(
        r'^(?:[a-zA-Z0-9]'
        r'(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+'
        r'[a-zA-Z]{2,63}$'
    )
    return bool(pattern.match(domain_str))

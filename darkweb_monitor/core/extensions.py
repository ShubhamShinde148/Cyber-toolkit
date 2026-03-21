from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize extensions (unbound)
db = SQLAlchemy()
login_manager = LoginManager()

# Default settings
login_manager.login_view = 'auth_bp.login'
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "info"


# ==========================================
# Database Models (Identical to legacy system)
# ==========================================
class User(UserMixin, db.Model):
    """
    User model for authentication and database storage.
    Automatically maps to the existing SQLite 'user' table.
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)

    def set_password(self, password_text):
        """Hash and set the user's password using werkzeug."""
        self.password = generate_password_hash(password_text)

    def check_password(self, password_text):
        """Verify the password against the stored hash."""
        return check_password_hash(self.password, password_text)

    def __repr__(self):
        return f"<User {self.username}>"


@login_manager.user_loader
def load_user(user_id):
    """Flask-Login callback to reload the user object from the session."""
    return User.query.get(int(user_id))

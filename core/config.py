import os
from datetime import timedelta

class Config:
    """Base configuration class."""
    
    # Application Config
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-dev-key')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    
    # Database Config
    # Uses the same database as the legacy system
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 
        f"sqlite:///{os.path.join(INSTANCE_DIR, 'darkweb_monitor.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session Config
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    
    # API Keys (loaded via load_dotenv in app.py)
    GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    ABUSEIPDB_API_KEY = os.environ.get('ABUSEIPDB_API_KEY')
    OTX_API_KEY = os.environ.get('OTX_API_KEY')
    GREYNOISE_API_KEY = os.environ.get('GREYNOISE_API_KEY')
    SHODAN_API_KEY = os.environ.get('SHODAN_API_KEY')

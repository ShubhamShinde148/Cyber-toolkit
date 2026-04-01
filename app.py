import inspect
# Helper to resolve Awaitable/Coroutine or direct result
def resolve_awaitable(obj):
    # Handle tuple (Awaitable, ...) or direct Awaitable or direct result
    if isinstance(obj, tuple):
        first = obj[0]
        if inspect.iscoroutine(first):
            import asyncio
            return asyncio.run(first)
        return first
    if inspect.iscoroutine(obj):
        import asyncio
        return asyncio.run(obj)
    return obj
# ...existing code...
# ...existing code...

"""
Dark Web Leak Monitor - Web Application
Flask-based REST API and web interface.
"""

import os
import asyncio
import io
import re
import uuid
import base64
import requests
from urllib.parse import urlsplit
from dotenv import load_dotenv

# Load environment variables from .env file BEFORE other imports
load_dotenv()

from flask import Flask, render_template, request, jsonify, send_file, send_from_directory, redirect, url_for, flash, session
from flask_login import login_user
from flask_cors import CORS
# from flask_login import LoginManager, UserMixin, current_user, login_required, login_user, logout_user
import json
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.middleware.dispatcher import DispatcherMiddleware

# from breach_checker import BreachChecker

from services.breach_checker import BreachChecker
from services.email_checker import EmailChecker
from services.risk_analyzer import RiskAnalyzer
from services.password_generator import PasswordGenerator, PasswordConfig
from services.batch_checker import BatchChecker
from services.export_manager import ExportManager
from services.report_generator import ReportGenerator

# Cyber Tools
from tools import (
    HashTool, Base64Tool, URLTool, JWTDecoder,
    PasswordStrengthAnalyzer, IPLookupTool, DNSLookupTool,
    SubdomainFinder, TextBinaryConverter, ROT13Tool,
    AssetHealthChecker, SurfaceAuditTool
)
from tools.ip_threat_intel import IPThreatIntelScanner

# OSINT Modules
from services.username_osint import UsernameOSINT
from services.domain_scanner import DomainScanner
from services.ip_intelligence import IPIntelligence
from services.cyber_risk_engine import CyberRiskEngine
from services.security_advisor import SecurityAdvisor
from services.breach_timeline import BreachTimeline
from services.quiz_engine import CybersecurityQuiz, CertificateGenerator, QuizResult, Question
from services.metadata_extractor import MetadataExtractor
from services.website_technology_detector import WebsiteTechnologyDetector
from services.steganography import SteganographyTool
from services.whois_lookup import WhoisLookup
from services.chatbot import CybersecurityChatbot, ask_chatbot, is_chatbot_configured
from services.feedback_mailer import send_feedback_email, is_email_configured
from routes.ctf_routes import ctf_engine

import firebase_admin

from firebase_admin import credentials, firestore, auth as firebase_auth
from google.cloud.firestore_v1.base_query import FieldFilter

# Firebase bootstrap for local and Railway deployment.
cred_path = os.path.join(os.path.dirname(__file__), "darkweb-monitor-fee1c-firebase-adminsdk-fbsvc-be2b34d535.json")
firebase_ready = False

try:
    if not firebase_admin._apps:
        # Option 1: raw JSON in env var (recommended for Railway)
        if os.getenv("FIREBASE_CREDENTIALS_JSON"):
            cred_info = json.loads(os.getenv("FIREBASE_CREDENTIALS_JSON"))
            firebase_admin.initialize_app(credentials.Certificate(cred_info))
        # Option 2: base64-encoded JSON in env var
        elif os.getenv("FIREBASE_CREDENTIALS_BASE64"):
            decoded = base64.b64decode(os.getenv("FIREBASE_CREDENTIALS_BASE64")).decode("utf-8")
            cred_info = json.loads(decoded)
            firebase_admin.initialize_app(credentials.Certificate(cred_info))
        # Option 3: local key file for development
        elif os.path.exists(cred_path):
            firebase_admin.initialize_app(credentials.Certificate(cred_path))
        else:
            raise RuntimeError(
                "Firebase credentials not found. Set FIREBASE_CREDENTIALS_JSON "
                "or FIREBASE_CREDENTIALS_BASE64 in Railway variables."
            )

    db = firestore.client()
    firebase_ready = True
    print("Firebase connected successfully")
except Exception as firebase_err:
    db = None
    print(f"[WARN] Firebase not initialized: {firebase_err}")

app = Flask(__name__, 
            static_folder='static',
            template_folder='templates')
os.makedirs(app.instance_path, exist_ok=True)

# Import and mount the optional V2 modular app without blocking main app startup.
modular_ready = False
try:
    from app_modular import create_modular_app
    app_v2 = create_modular_app()
    app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
        '/v2': app_v2.wsgi_app
    })
    modular_ready = True
except Exception as modular_err:
    print(f"[WARN] Modular V2 app disabled: {modular_err}")

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'change-this-secret-key-in-production')
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['REMEMBER_COOKIE_HTTPONLY'] = True
CORS(app)

@app.route('/health')
def health():
    return jsonify({
        'status': 'ok',
        'service': 'dark-web-monitor',
        'firebase_ready': firebase_ready,
        'modular_ready': modular_ready
    }), 200

# login_manager = LoginManager()
# login_manager.init_app(app)
# login_manager.login_view = 'login'
# login_manager.login_message = 'Please login to access cybersecurity tools.'
# login_manager.login_message_category = 'warning'


# @login_manager.user_loader
# def load_user(user_id):
#     """Load a user from the database."""
#     return get_user_by_id(user_id)



class User:
    def __init__(self):
        self.id = "anonymous"
        self.username = "Anonymous"
        self.email = ""
        self.is_authenticated = False

    @staticmethod
    def from_doc(doc):
        if not doc or not hasattr(doc, 'to_dict'):
            return None
        data = doc.to_dict()
        user = User()
        user.id = data.get('id', data.get('username', 'anonymous'))
        user.username = data.get('username', 'Anonymous')
        user.email = data.get('email', '')
        user.is_authenticated = True
        return user

current_user = User()


def normalize_redirect_target(target):
    if not target:
        return None

    parsed = urlsplit(target)

    if parsed.scheme or parsed.netloc:
        if parsed.netloc and parsed.netloc != request.host:
            return None
        if parsed.query:
            target = f"{target}?{parsed.query}"

    if not target.startswith('/'):
        return None

    return target


def get_post_login_redirect():
    target = request.args.get('next') or request.form.get('next')
    return normalize_redirect_target(target) or url_for('dashboard')


def is_valid_email(email):
    return re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email or '') is not None


def get_user_by_id(user_id):
    """Look up a user by Firestore document ID."""
    doc = resolve_awaitable(db.collection('users').document(str(user_id)).get())
    return User.from_doc(doc)


def get_user_by_username(username):
    """Look up a user by username (case-insensitive)."""
    docs = resolve_awaitable(
        db.collection('users')
        .where(filter=FieldFilter('username_lower', '==', username.strip().lower()))
        .limit(1)
        .stream()
    )
    for doc in docs:
        return User.from_doc(doc)
    return None


def get_user_by_email(email):
    """Look up a user by email (case-insensitive)."""
    docs = resolve_awaitable(
        db.collection('users')
        .where(filter=FieldFilter('email', '==', email.strip().lower()))
        .limit(1)
        .stream()
    )
    for doc in docs:
        return User.from_doc(doc)
    return None


def get_user_by_identifier(identifier):
    """Look up a user by username or email."""
    user = get_user_by_email(identifier)
    if user:
        return user
    return get_user_by_username(identifier)


def create_user(username, email, password):
    """Create a new user document in Firestore and return a User object."""
    password_hash = generate_password_hash(password)
    user_id = str(uuid.uuid4())
    now = datetime.now().isoformat()

    db.collection('users').document(user_id).set({
        'username': username.strip(),
        'username_lower': username.strip().lower(),
        'email': email.strip().lower(),
        'password_hash': password_hash,
        'created_at': now,
        'last_login': now
    })

    return get_user_by_id(user_id)


def update_last_login(user_id):
    """Update the last_login timestamp for a user."""
    db.collection('users').document(str(user_id)).update({
        'last_login': datetime.now().isoformat()
    })


# ==================== SCAN HISTORY ====================

def log_scan(user_id, tool_used, input_value, result_summary, risk_score=None):
    """Save a scan record to the Firestore scan_history collection."""
    scan_id = str(uuid.uuid4())
    db.collection('scan_history').document(scan_id).set({
        'user_id': str(user_id),
        'tool_used': tool_used,
        'input_value': input_value[:200],  # truncate for safety
        'result_summary': result_summary[:500],
        'risk_score': risk_score,
        'timestamp': datetime.now().isoformat()
    })
    return scan_id


def get_user_scans(user_id, limit=20):
    """Fetch recent scan history for a user, newest first."""
    docs = (db.collection('scan_history')
            .where(filter=FieldFilter('user_id', '==', str(user_id)))
            .stream())
    scans = []
    for doc in docs:
        data = doc.to_dict() if hasattr(doc, 'to_dict') else {}
        if data is not None:
            data['id'] = getattr(doc, 'id', None)
            scans.append(data)
    scans.sort(key=lambda s: s.get('timestamp', ''), reverse=True)
    return scans[:limit]


# ==================== SECURITY REPORTS ====================

def save_security_report(user_id, report_type, generated_data, risk_level):
    """Save a security report to Firestore."""
    report_id = str(uuid.uuid4())
    db.collection('security_reports').document(report_id).set({
        'user_id': str(user_id),
        'report_type': report_type,
        'generated_data': json.dumps(generated_data) if not isinstance(generated_data, str) else generated_data,
        'risk_level': risk_level,
        'created_at': datetime.now().isoformat()
    })
    return report_id

def get_user_reports(user_id, limit=10):
    """Fetch recent security reports for a user."""
    docs = (db.collection('security_reports')
            .where(filter=FieldFilter('user_id', '==', str(user_id)))
            .stream())
    reports = []
    for doc in docs:
        data = doc.to_dict() if hasattr(doc, 'to_dict') else {}
        if data is not None:
            data['id'] = getattr(doc, 'id', None)
            reports.append(data)
    reports.sort(key=lambda r: r.get('created_at', ''), reverse=True)
    return reports[:limit]



# @login_manager.unauthorized_handler
# def handle_unauthorized():
#     message = login_manager.login_message or 'Please login to access cybersecurity tools.'
# 
#     if request.path.startswith('/api/'):
#         next_target = normalize_redirect_target(request.referrer) or url_for('dashboard')
#         return jsonify({
#             'error': 'Authentication required.',
#             'message': message,
#             'login_url': url_for('login', next=next_target)
#         }), 401
# 
#     flash(message, login_manager.login_message_category or 'warning')
#     next_target = request.full_path.rstrip('?') if request.query_string else request.path
#     return redirect(url_for('login', next=next_target))

# Initialize services
breach_checker = BreachChecker()
email_checker = EmailChecker()
risk_analyzer = RiskAnalyzer()
password_generator = PasswordGenerator()
batch_checker = BatchChecker()
export_manager = ExportManager()
report_generator = ReportGenerator()

# OSINT Service instances
username_osint = UsernameOSINT(timeout=8, max_workers=15)
domain_scanner = DomainScanner()
ip_intelligence = IPIntelligence(timeout=10)
cyber_risk_engine = CyberRiskEngine()
security_advisor = SecurityAdvisor()
breach_timeline = BreachTimeline()

# Quiz instances
cybersecurity_quiz = CybersecurityQuiz()
certificate_generator = CertificateGenerator()

# Forensics tools
metadata_extractor = MetadataExtractor()
website_technology_detector = WebsiteTechnologyDetector(timeout=10)
whois_lookup = WhoisLookup()
steganography_tool = SteganographyTool()

# ChatGPT Chatbot
cybersecurity_chatbot = CybersecurityChatbot()

# Learning Mode
LEARNING_MODE_MAINTENANCE = True
learning_engine = None

# Cyber Tools instances
hash_tool = HashTool()
base64_tool = Base64Tool()
url_tool = URLTool()
jwt_decoder = JWTDecoder()
password_strength_analyzer = PasswordStrengthAnalyzer()
ip_lookup_tool = IPLookupTool()
dns_lookup_tool = DNSLookupTool()
subdomain_finder = SubdomainFinder()
text_binary_converter = TextBinaryConverter()
rot13_tool = ROT13Tool()

# Defensive web tools (allowlist-only)
_defense_allowlist = [
    h.strip() for h in os.getenv('DEFENSE_ALLOWLIST', 'localhost,127.0.0.1').split(',')
    if h.strip()
]
asset_health_checker = AssetHealthChecker(allowlist_hosts=_defense_allowlist, timeout=6)
surface_audit_tool = SurfaceAuditTool(allowlist_hosts=_defense_allowlist, timeout=6)

# Store last results for export
last_results = {}


@app.route('/login')
def login_redirect():
    """Redirect legacy login requests to the V2 platform."""
    return redirect('/v2/auth/login')

@app.route('/register')
def register_redirect():
    """Redirect legacy registration requests to the V2 platform."""
    return redirect('/v2/auth/register')


@app.route('/google-login', methods=['POST'])
def google_login():
    """Authenticate a user via Google OAuth using Firebase ID token."""
    data = request.get_json(silent=True)
    if not data or not data.get('idToken'):
        return jsonify({'status': 'error', 'message': 'Missing ID token.'}), 400

    try:
        decoded_token = firebase_auth.verify_id_token(data['idToken'])
    except Exception:
        return jsonify({'status': 'error', 'message': 'Invalid or expired token.'}), 401

    email = decoded_token.get('email', '').strip().lower()
    name = decoded_token.get('name', email.split('@')[0])

    if not email:
        return jsonify({'status': 'error', 'message': 'No email in token.'}), 400

    user = get_user_by_email(email)

    if user is None:
        # Create a new user for first-time Google sign-in
        user_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        username = name.replace(' ', '_')[:32]
        # Ensure unique username
        base_username = username
        counter = 1
        while get_user_by_username(username):
            username = f"{base_username}_{counter}"[:32]
            counter += 1

        db.collection('users').document(user_id).set({
            'username': username,
            'username_lower': username.lower(),
            'email': email,
            'password_hash': '',
            'auth_provider': 'google',
            'created_at': now,
            'last_login': now
        })
        user = get_user_by_id(user_id)

    if user:
        update_last_login(user.id)
        login_user(user)
        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'error', 'message': 'User creation failed'}), 500


# Legacy register logic removed. Uses V2 platform registration via global redirect.


# @app.route('/logout', methods=['POST'])
# # @login_required
# def logout():
#     """Log out the current user."""
#     logout_user()
#     flash('You have been logged out.', 'info')
#     return redirect(url_for('login'))


@app.route('/dashboard')
# # @login_required
def dashboard():
    """Authenticated user landing page with scan history and reports."""
    scans = []
    reports = []
    certificates = []
    # try:
    #     scans = get_user_scans(current_user.id, limit=10)
    # except Exception:
    #     pass
    # try:
    #     reports = get_user_reports(current_user.id, limit=5)
    # except Exception:
    #     pass
    # try:
    #     certs_ref = db.collection('quiz_certificates') \
    #         .where('user_id', '==', current_user.id) \
    #         .order_by('created_at', direction=firestore.Query.DESCENDING)
    #     for doc in certs_ref.stream():
    #         if doc.id != 'cert_counter':
    #             certificates.append(doc.to_dict())
    # except Exception:
    #     pass
    return render_template('dashboard.html', scans=scans, reports=reports, certificates=certificates, current_user=current_user)


# ==================== WEB PAGES ====================

@app.route('/')
def index():
    """Serve the main page with dynamic statistics."""
    import random
    
    # Calculate some dynamic stats
    try:
        user_count_result = resolve_awaitable(db.collection('users').count().get())
        # Firestore AggregationResult is not subscriptable; access .value directly
        if hasattr(user_count_result, 'value'):
            user_count = user_count_result.value
        elif isinstance(user_count_result, list) and user_count_result and hasattr(user_count_result[0], 'value'):
            user_count = user_count_result[0].value
        else:
            user_count = 1200
    except Exception:
        user_count = 1200 # Fallback
        
    stats = {
        'breach_count': 748 + random.randint(1, 50),
        'accounts_analyzed': 12.4 + (random.randint(1, 9) / 10),
        'privacy_protection': 100,
        'response_time': 0.82
    }
    
    return render_template('index.html', current_user=current_user, stats=stats)


@app.route('/password-check')
# @login_required
def password_check_page():
    """Password check page."""
    return render_template('password_check.html', current_user=current_user)


@app.route('/email-check')
# @login_required
def email_check_page():
    """Email check page."""
    return render_template('email_check.html', current_user=current_user)


@app.route('/generator')
# @login_required
def generator_page():
    """Password generator page."""
    return render_template('generator.html', current_user=current_user)


@app.route('/batch')
# @login_required
def batch_page():
    """Batch check page."""
    return render_template('batch.html', current_user=current_user)


@app.route('/about')
def about_page():
    """About page."""
    return render_template('about.html', current_user=current_user)


@app.route('/username-osint')
# @login_required
def username_osint_page():
    """Username OSINT scanner page."""
    return render_template('username_osint.html', current_user=current_user)


@app.route('/domain-scanner')
# @login_required
def domain_scanner_page():
    """Domain security scanner page."""
    return render_template('domain_scanner.html', current_user=current_user)


@app.route('/ip-intelligence')
# @login_required
def ip_intelligence_page():
    """IP intelligence page."""
    return render_template('ip_intelligence.html', current_user=current_user)


@app.route('/website-technology-detector')
# @login_required
def website_technology_detector_page():
    """Website technology detector page."""
    return render_template('website_technology_detector.html', current_user=current_user)


@app.route('/whois-lookup')
# @login_required
def whois_lookup_page():
    """WHOIS lookup page."""
    return render_template('whois_lookup.html', current_user=current_user)


@app.route('/risk-assessment')
# @login_required
def risk_assessment_page():
    """Cyber risk assessment page."""
    return render_template('risk_assessment.html', current_user=current_user)


@app.route('/security-advisor')
# @login_required
def security_advisor_page():
    """Security advisor page."""
    return render_template('security_advisor.html')


@app.route('/breach-timeline')
# @login_required
def breach_timeline_page():
    """Breach timeline visualization page."""
    return render_template('breach_timeline.html')


@app.route('/quiz')
# @login_required
def quiz_page():
    """Cybersecurity quiz page."""
    return render_template('quiz.html')


@app.route('/cyber-tools')
# @login_required
def cyber_tools_page():
    """Cyber Tools dashboard page."""
    return render_template('cyber_tools.html')


@app.route('/tools')
# @login_required
def tools_hub_page():
    """Categorized tools hub page."""
    return render_template('tools_hub.html')


@app.route('/snake')
def snake_page():
    """Classic Snake game page."""
    return render_template('snake.html', current_user=current_user)


@app.route('/metadata-extractor')
# @login_required
def metadata_extractor_page():
    """Metadata forensics extractor page."""
    return render_template('metadata_extractor.html')


@app.route('/steganography')
# @login_required
def steganography_page():
    """Steganography tool page — hide and extract messages in images."""
    return render_template('steganography.html')


@app.route('/attack-map')
# @login_required
def attack_map_page():
    """Live Global Cyber Attack Map page."""
    return render_template('attack_map.html')


@app.route('/ip-threat-intel')
# @login_required
def ip_threat_intel_page():
    """SOC-Level IP Threat Intelligence Scanner page."""
    return render_template('ip_threat_intel.html')


@app.route('/learning-mode')
# @login_required
def learning_mode_page():
    """Cybersecurity Learning Mode page."""
    if LEARNING_MODE_MAINTENANCE:
        return (
            "<h2>Learning Mode is under maintenance</h2>"
            "<p>Please try again later.</p>",
            503,
        )
    return render_template('learning_mode.html', roadmap=learning_engine.get_roadmap())


@app.route('/api/learning/topic-content', methods=['POST'])
# @login_required
def api_learning_topic_content():
    """Generate AI learning content for a single topic. Always returns valid fallback data."""
    if LEARNING_MODE_MAINTENANCE:
        return jsonify({'error': 'Learning Mode is under maintenance'}), 503

    data = request.get_json(silent=True) or {}
    topic = data.get('topic', '').strip()
    difficulty = data.get('difficulty', 'beginner').strip()
    if not topic:
        return jsonify({'error': 'Topic is required'}), 400
    try:
        result = learning_engine.generate_topic_content(topic, difficulty)
        return jsonify(result)
    except Exception as e:
        # Fallback: static roadmap topic or generic fallback
        roadmap = learning_engine.get_roadmap()
        if isinstance(roadmap, dict):
            for level in roadmap.values():
                if isinstance(level, dict) and "topics" in level:
                    for t in level["topics"]:
                        if t["title"].lower() == topic.lower():
                            return jsonify({
                                "title": t["title"],
                                "difficulty": difficulty,
                                "explanation": f"This is a static fallback explanation for {t['title']}.",
                                "tools": [],
                                "practice": "No AI content available. Practice with online resources.",
                                "quick_notes": [],
                                "steps": []
                            })
        return jsonify({
            "title": topic,
            "difficulty": difficulty,
            "explanation": "AI content unavailable. Please try again later.",
            "tools": [],
            "practice": "No AI content available.",
            "quick_notes": [],
            "steps": []
        })


@app.route('/api/learning/ask', methods=['POST'])
# @login_required
def api_learning_ask():
    """Ask the AI a deeper question about a topic. Always returns valid fallback data."""
    if LEARNING_MODE_MAINTENANCE:
        return jsonify({'error': 'Learning Mode is under maintenance'}), 503

    data = request.get_json(silent=True) or {}
    topic = data.get('topic', '').strip()
    question = data.get('question', '').strip()
    if not topic or not question:
        return jsonify({'error': 'Topic and question are required'}), 400
    try:
        answer = learning_engine.ask_about_topic(topic, question)
        return jsonify({'answer': answer})
    except Exception as e:
        return jsonify({'answer': "AI is currently unavailable. Please try again later or review the static roadmap content."})


@app.route('/api/learning/daily-topic', methods=['POST'])
# @login_required
def api_learning_daily_topic():
    """Generate a daily cybersecurity topic. Always returns valid fallback data and uses 24h cache."""
    if LEARNING_MODE_MAINTENANCE:
        return jsonify({'error': 'Learning Mode is under maintenance'}), 503

    try:
        result = learning_engine.generate_daily_topic()
        return jsonify(result)
    except Exception as e:
        # Fallback: static topic
        return jsonify({
            "title": "Phishing Awareness",
            "summary": "Phishing is a common cyber attack where attackers trick users into revealing sensitive information. Learn how to spot and avoid phishing attempts.",
            "fun_fact": "The first phishing lawsuit was filed in 2004 against a California teenager.",
            "difficulty": "beginner"
        })


# ==================== API ENDPOINTS ====================


@app.route('/api/steganography/encode', methods=['POST'])
# @login_required
def api_steg_encode():
    """Hide a message inside an uploaded image. Returns the encoded PNG."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No image uploaded'}), 400
        file = request.files['file']
        message = request.form.get('message', '').strip()
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        image_data = file.read()
        if len(image_data) > steganography_tool.MAX_FILE_SIZE:
            return jsonify({'error': 'File too large (max 10MB)'}), 400
        encoded = steganography_tool.encode(image_data, message)
        return send_file(
            io.BytesIO(encoded),
            mimetype='image/png',
            as_attachment=True,
            download_name='stego_image.png'
        )
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': f'Encoding failed: {str(e)}'}), 500


@app.route('/api/steganography/decode', methods=['POST'])
# @login_required
def api_steg_decode():
    """Extract a hidden message from an uploaded image."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No image uploaded'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        image_data = file.read()
        if len(image_data) > steganography_tool.MAX_FILE_SIZE:
            return jsonify({'error': 'File too large (max 10MB)'}), 400
        result = steganography_tool.decode(image_data)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': f'Decode failed: {str(e)}'}), 500


@app.route('/api/steganography/capacity', methods=['POST'])
# @login_required
def api_steg_capacity():
    """Return how many characters can be hidden in the uploaded image."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No image uploaded'}), 400
        file = request.files['file']
        image_data = file.read()
        info = steganography_tool.get_capacity(image_data)
        return jsonify(info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/check-password', methods=['POST'])
def api_check_password():
    """
    Check a password for breaches.
    
    Request body: {"password": "string"}
    """
    global last_results
    
    try:
        data = request.get_json()
        password = data.get('password', '')
        
        if not password:
            return jsonify({'error': 'Password is required'}), 400
        
        if len(password) < 4:
            return jsonify({'error': 'Password too short'}), 400
        
        # Check password
        breach_result = breach_checker.check(password)
        password_strength = breach_checker.check_password_strength(password)
        risk_assessment = risk_analyzer.analyze(breach_result.breach_count, password_strength)
        
        # Mask password for response
        masked = password[:2] + '*' * min(len(password) - 4, 8) + password[-2:] if len(password) > 4 else '****'
        
        result = {
            'success': True,
            'password_masked': masked,
            'breach_count': breach_result.breach_count,
            'is_compromised': breach_result.is_compromised,
            'risk_level': risk_assessment.level.value,
            'risk_score': risk_assessment.score,
            'risk_color': risk_assessment.color,
            'api_status': breach_result.api_status,
            'password_strength': {
                'length': password_strength['length'],
                'has_upper': password_strength['has_upper'],
                'has_lower': password_strength['has_lower'],
                'has_digit': password_strength['has_digit'],
                'has_special': password_strength['has_special'],
                'is_strong': password_strength['is_strong']
            },
            'recommendations': risk_assessment.recommendations,
            'checked_at': datetime.now().isoformat()
        }
        
        # Log scan to Firestore
        # if current_user.is_authenticated:
        #     summary = f"Breaches: {breach_result.breach_count}, Risk: {risk_assessment.level.value}"
        #     log_scan(current_user.id, 'Password Breach Check', masked, summary, risk_assessment.score)
        
        last_results = result
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/check-email', methods=['POST'])
def api_check_email():
    """
    Check an email for breaches.
    
    Request body: {"email": "string"}
    """
    global last_results
    
    try:
        data = request.get_json()
        email = data.get('email', '')
        
        if not email or '@' not in email:
            return jsonify({'error': 'Valid email is required'}), 400
        
        # Check email
        breach_result = email_checker.check_breaches(email)
        
        result = {
            'success': True,
            'email': breach_result.email,
            'is_compromised': breach_result.is_compromised,
            'breach_count': breach_result.breach_count,
            'api_status': breach_result.api_status,
            'breaches': [
                {
                    'name': b.name,
                    'domain': b.domain,
                    'breach_date': b.breach_date,
                    'pwn_count': b.pwn_count,
                    'data_classes': b.data_classes,
                    'description': b.description
                }
                for b in breach_result.breaches
            ],
            'checked_at': breach_result.checked_at
        }
        
        # Log scan to Firestore
        # if current_user.is_authenticated:
        #     summary = f"Breaches: {breach_result.breach_count}, Compromised: {breach_result.is_compromised}"
        #     log_scan(current_user.id, 'Email Breach Check', email, summary)
        
        last_results = result
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate-password', methods=['POST'])
def api_generate_password():
    """
    Generate a secure password.
    
    Request body: {
        "type": "random" | "memorable" | "pin",
        "length": number,
        "include_uppercase": bool,
        "include_lowercase": bool,
        "include_digits": bool,
        "include_special": bool,
        "count": number (for multiple)
    }
    """
    try:
        data = request.get_json() or {}
        gen_type = data.get('type', 'random')
        length = data.get('length', 16)
        count = data.get('count', 1)
        
        results = []
        
        for _ in range(min(count, 10)):  # Limit to 10
            if gen_type == 'memorable':
                words = data.get('words', 4)
                result = password_generator.generate_memorable(num_words=words)
            elif gen_type == 'pin':
                result = password_generator.generate_pin(length=min(length, 12))
            else:
                config = PasswordConfig(
                    length=min(max(length, 8), 128),
                    include_uppercase=data.get('include_uppercase', True),
                    include_lowercase=data.get('include_lowercase', True),
                    include_digits=data.get('include_digits', True),
                    include_special=data.get('include_special', True)
                )
                generator = PasswordGenerator(config)
                result = generator.generate()
            
            results.append({
                'password': result.password,
                'length': result.length,
                'entropy': result.entropy,
                'strength': result.strength.value,
                'has_uppercase': result.has_uppercase,
                'has_lowercase': result.has_lowercase,
                'has_digits': result.has_digits,
                'has_special': result.has_special,
                'memorable': result.memorable
            })
        
        return jsonify({
            'success': True,
            'passwords': results if count > 1 else results[0]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/batch-check', methods=['POST'])
def api_batch_check():
    """
    Batch check passwords or emails.
    
    Request body: {
        "type": "passwords" | "emails",
        "items": ["string", ...]
    }
    """
    global last_results
    
    try:
        data = request.get_json()
        check_type = data.get('type', 'passwords')
        items = data.get('items', [])
        
        if not items:
            return jsonify({'error': 'No items to check'}), 400
        
        if len(items) > 50:
            return jsonify({'error': 'Maximum 50 items allowed'}), 400
        
        if check_type == 'emails':
            batch_result = batch_checker.check_emails(items)
        else:
            batch_result = batch_checker.check_passwords(items)
        
        result = {
            'success': True,
            'type': check_type,
            'total_items': batch_result.total_items,
            'compromised_count': batch_result.compromised_count,
            'safe_count': batch_result.safe_count,
            'error_count': batch_result.error_count,
            'compromise_rate': round(batch_result.compromise_rate, 1),
            'processing_time': batch_result.processing_time,
            'results': batch_result.results,
            'checked_at': batch_result.checked_at
        }
        
        last_results = result
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate-report', methods=['POST'])
def api_generate_report():
    """
    Generate a PDF report from the last check results.
    """
    global last_results
    
    try:
        if not last_results:
            return jsonify({'error': 'No results to export'}), 400
        
        data = request.get_json() or {}
        password = data.get('password', '********')
        
        filepath = report_generator.generate(
            password=password,
            breach_count=last_results.get('breach_count', 0),
            risk=last_results.get('risk_level', 'UNKNOWN'),
            recommendations=last_results.get('recommendations', [])
        )
        
        return jsonify({
            'success': True,
            'filepath': filepath,
            'filename': os.path.basename(filepath)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/export', methods=['POST'])
def api_export():
    """
    Export results to various formats.
    
    Request body: {"format": "json" | "csv" | "html" | "txt" | "all"}
    """
    global last_results
    
    try:
        if not last_results:
            return jsonify({'error': 'No results to export'}), 400
        
        data = request.get_json() or {}
        fmt = data.get('format', 'json')
        
        if fmt == 'all':
            exports = export_manager.export_all(last_results, 'web_report')
            return jsonify({
                'success': True,
                'exports': exports
            })
        elif fmt == 'json':
            path = export_manager.export_json(last_results, 'web_report')
        elif fmt == 'csv':
            path = export_manager.export_csv([last_results], 'web_report')
        elif fmt == 'html':
            path = export_manager.export_html(last_results, 'web_report')
        elif fmt == 'txt':
            path = export_manager.export_txt(last_results, 'web_report')
        else:
            return jsonify({'error': 'Invalid format'}), 400
        
        return jsonify({
            'success': True,
            'filepath': path,
            'filename': os.path.basename(path)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/download/<filename>')
def download_file(filename):
    """Download an exported file."""
    try:
        # Check exports folder first
        exports_path = os.path.join(os.getcwd(), 'exports')
        if os.path.exists(os.path.join(exports_path, filename)):
            return send_from_directory(exports_path, filename, as_attachment=True)
        
        # Check current directory
        if os.path.exists(filename):
            return send_file(filename, as_attachment=True)
        
        return jsonify({'error': 'File not found'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/stats')
def api_stats():
    """Get application statistics."""
    return jsonify({
        'version': '4.0',
        'features': [
            'Password Breach Check',
            'Email Breach Check',
            'Password Generator',
            'Batch Processing',
            'Multiple Export Formats',
            'Username OSINT Scanner',
            'Domain Security Scanner',
            'WHOIS Lookup',
            'IP Intelligence',
            'Cyber Risk Assessment',
            'Security Advisor',
            'Breach Timeline',
            'Cyber Tools Toolkit'
        ],
        'cyber_tools': [
            'Hash Generator (MD5, SHA1, SHA256, SHA512)',
            'Base64 Encoder/Decoder',
            'URL Encoder/Decoder',
            'JWT Token Decoder',
            'Password Strength Analyzer',
            'IP Intelligence Lookup',
            'DNS Lookup Tool',
            'Subdomain Finder',
            'Text/Binary Converter',
            'ROT13/Caesar Cipher'
        ],
        'api_source': 'Have I Been Pwned',
        'protection': 'k-anonymity'
    })


# ==================== OSINT API ENDPOINTS ====================

@app.route('/api/username-osint', methods=['POST'])
def api_username_osint():
    """
    Scan username across multiple platforms.
    
    Request body: {"username": "string", "platforms": ["optional", "list"]}
    """
    global last_results
    
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        platforms = data.get('platforms')  # Optional list of specific platforms
        
        if not username:
            return jsonify({'error': 'Username is required'}), 400
        
        # Perform scan
        result = username_osint.scan(username, platforms)
        
        if result['success']:
            last_results = result
            # Log scan to Firestore
                    # if current_user.is_authenticated:
                    #     summary = f"Found: {result.get('total_found', 0)}/{result.get('total_checked', 0)} platforms"
                    #     log_scan(current_user.id, 'Username OSINT', username, summary)        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/username-osint/platforms')
def api_username_platforms():
    """Get available platforms for username scanning."""
    return jsonify({
        'platforms': username_osint.get_available_platforms(),
        'categories': username_osint.get_categories(),
        'total': len(username_osint.PLATFORMS)
    })


@app.route('/api/domain-scan', methods=['POST'])
def api_domain_scan():
    """
    Scan domain for security issues.
    
    Request body: {"domain": "string", "full_scan": bool}
    """
    global last_results
    
    try:
        data = request.get_json()
        domain = data.get('domain', '').strip()
        full_scan = data.get('full_scan', True)
        
        if not domain:
            return jsonify({'error': 'Domain is required'}), 400
        
        # Perform scan
        if full_scan:
            result = domain_scanner.scan(domain)
        else:
            result = domain_scanner.quick_scan(domain)
        
        if result['success']:
            last_results = result
            # Log scan to Firestore
                    # if current_user.is_authenticated:
                    #     grade = result.get('security_grade', 'N/A')
                    #     score = result.get('security_score', 0)
                    #     summary = f"Grade: {grade}, Score: {score}"
                    #     log_scan(current_user.id, 'Domain Security Scan', domain, summary, score)        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ip-intelligence', methods=['POST'])
def api_ip_intelligence():
    """
    Analyze IP address for threat intelligence.
    
    Request body: {"ip": "string"}
    """
    global last_results
    
    try:
        data = request.get_json()
        ip = data.get('ip', '').strip()
        
        if not ip:
            return jsonify({'error': 'IP address is required'}), 400
        
        # Perform analysis
        result = ip_intelligence.analyze(ip)
        
        if result['success']:
            last_results = result
            # Log scan to Firestore
                    # if current_user.is_authenticated:
                    #     threat = result.get('threats', {}).get('threat_level', 'N/A')
                    #     summary = f"Threat level: {threat}"
                    #     log_scan(current_user.id, 'IP Intelligence', ip, summary)        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/whois-lookup', methods=['POST'])
def api_whois_lookup():
    """
    Fetch WHOIS information for a domain.

    Request body: {"domain": "string"}
    """
    global last_results

    try:
        data = request.get_json() or {}
        domain = data.get('domain', '').strip()

        if not domain:
            return jsonify({'error': 'Domain is required'}), 400

        result = whois_lookup.lookup(domain)

        if result['success']:
            last_results = result
            # Log scan to Firestore
            # if current_user.is_authenticated:
            #     registrar = result.get('registrar', 'N/A')
            #     summary = f"Registrar: {registrar}"
            #     log_scan(current_user.id, 'WHOIS Lookup', domain, summary)
            return jsonify(result)

        return jsonify(result), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/website-technology-detector', methods=['POST'])
def api_website_technology_detector():
    """Inspect response headers and infer exposed website technologies."""
    global last_results

    try:
        data = request.get_json(silent=True) or {}
        website_url = data.get('url', '').strip()

        if not website_url:
            return jsonify({'success': False, 'error': 'Website URL is required'}), 400

        result = website_technology_detector.analyze(website_url)
        last_results = result
        # Log scan to Firestore
        # if current_user.is_authenticated:
        #     summary = f"Technologies detected for {website_url}"
        #     log_scan(current_user.id, 'Website Technology Detector', website_url, summary)
        return jsonify(result)
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except RuntimeError as e:
        return jsonify({'success': False, 'error': str(e)}), 502
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/ip-intelligence/quick', methods=['POST'])
def api_ip_quick():
    """Quick IP lookup with essential information only."""
    try:
        data = request.get_json()
        ip = data.get('ip', '').strip()
        
        if not ip:
            return jsonify({'error': 'IP address is required'}), 400
        
        result = ip_intelligence.quick_lookup(ip)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/risk-assessment', methods=['POST'])
def api_risk_assessment():
    """
    Calculate comprehensive cyber risk score.
    
    Request body: {
        "password_breach_count": number,
        "password_strength": number,
        "email_breaches": [array],
        "username_platforms_found": number,
        "domain_score": number,
        "ip_reputation": number,
        ...
    }
    """
    try:
        data = request.get_json()
        
        # Reset engine for new assessment
        cyber_risk_engine.reset()
        
        # Add risk factors based on input
        if data.get('password_breach_count', 0) > 0:
            cyber_risk_engine.add_password_breach_risk(
                breach_count=data['password_breach_count'],
                passwords_compromised=data.get('passwords_compromised', 0)
            )
        
        if data.get('email_breaches'):
            cyber_risk_engine.add_email_breach_risk(data['email_breaches'])
        
        if data.get('username_platforms_found', 0) > 0:
            cyber_risk_engine.add_username_exposure_risk(
                platforms_found=data['username_platforms_found'],
                total_checked=data.get('username_platforms_checked', 25)
            )
        
        if data.get('domain_security_score') is not None:
            cyber_risk_engine.add_domain_security_risk(
                security_score=data['domain_security_score'],
                issues=data.get('domain_issues', [])
            )
        
        if data.get('ip_reputation_score') is not None:
            cyber_risk_engine.add_ip_reputation_risk(
                reputation_score=data['ip_reputation_score'],
                threat_factors=data.get('ip_threat_factors', []),
                is_blacklisted=data.get('ip_is_blacklisted', False)
            )
        
        if data.get('password_strength') is not None and data['password_strength'] < 80:
            cyber_risk_engine.add_weak_password_risk(
                strength_score=data['password_strength'],
                issues=data.get('password_issues', [])
            )
        
        # Perform assessment
        result = cyber_risk_engine.assess()
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/security-recommendations', methods=['POST'])
def api_security_recommendations():
    """
    Get personalized security recommendations.
    
    Request body: {
        "password_breached": bool,
        "password_breach_count": number,
        "email_breach_count": number,
        "username_platforms_found": number,
        "has_https": bool,
        "has_spf": bool,
        "has_2fa": bool,
        ...
    }
    """
    try:
        data = request.get_json() or {}
        
        # Set context
        security_advisor.set_context(data)
        
        # Get recommendations
        max_count = data.get('max_recommendations', 10)
        result = security_advisor.get_recommendations(max_count)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/security-recommendations/quick-wins')
def api_quick_wins():
    """Get quick win security recommendations."""
    return jsonify({
        'quick_wins': security_advisor.get_quick_wins()
    })


@app.route('/api/security-recommendations/action-plan', methods=['POST'])
def api_action_plan():
    """Generate security action plan."""
    try:
        data = request.get_json() or {}
        timeframe = data.get('timeframe', 'week')
        
        # Set context if provided
        if 'context' in data:
            security_advisor.set_context(data['context'])
        
        plan = security_advisor.generate_action_plan(timeframe)
        return jsonify(plan)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/breach-timeline', methods=['POST'])
def api_breach_timeline():
    """
    Generate breach timeline visualization data.
    
    Request body: {"breaches": [array of breach objects]}
    """
    try:
        data = request.get_json()
        breaches = data.get('breaches', [])
        
        if not breaches:
            return jsonify({'error': 'No breach data provided'}), 400
        
        # Clear and add breaches
        breach_timeline.clear()
        for breach in breaches:
            breach_timeline.add_breach_from_dict(breach)
        
        # Generate report
        result = breach_timeline.get_full_report()
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/breach-timeline/chart/<chart_type>')
def api_breach_chart(chart_type):
    """Get chart data for breach visualization."""
    try:
        if chart_type not in ['line', 'bar', 'doughnut']:
            return jsonify({'error': 'Invalid chart type'}), 400
        
        chart_data = breach_timeline.get_chart_js_data(chart_type)
        return jsonify(chart_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/comprehensive-scan', methods=['POST'])
def api_comprehensive_scan():
    """
    Perform comprehensive OSINT scan combining all modules.
    
    Request body: {
        "email": "string",
        "username": "string" (optional),
        "password": "string" (optional),
        "domain": "string" (optional),
        "ip": "string" (optional)
    }
    """
    global last_results
    
    try:
        data = request.get_json()
        results = {
            'success': True,
            'scans_performed': [],
            'scan_time': datetime.now().isoformat()
        }
        
        # Email scan
        email = data.get('email', '').strip()
        if email and '@' in email:
            try:
                email_result = email_checker.check_breaches(email)
                results['email'] = {
                    'email': email,
                    'is_compromised': email_result.is_compromised,
                    'breach_count': email_result.breach_count,
                    'breaches': [
                        {
                            'name': b.name,
                            'breach_date': b.breach_date,
                            'data_classes': b.data_classes
                        }
                        for b in email_result.breaches[:10]  # Limit
                    ]
                }
                results['scans_performed'].append('email')
            except Exception as e:
                results['email'] = {'error': str(e)}
        
        # Password scan
        password = data.get('password', '')
        if password and len(password) >= 4:
            try:
                breach_result = breach_checker.check(password)
                strength = breach_checker.check_password_strength(password)
                results['password'] = {
                    'is_compromised': breach_result.is_compromised,
                    'breach_count': breach_result.breach_count,
                    'strength': strength
                }
                results['scans_performed'].append('password')
            except Exception as e:
                results['password'] = {'error': str(e)}
        
        # Username scan
        username = data.get('username', '').strip()
        if username:
            try:
                username_result = username_osint.scan(username)
                if username_result['success']:
                    results['username'] = {
                        'platforms_found': username_result['total_found'],
                        'platforms_checked': username_result['total_checked'],
                        'profiles': username_result['found_profiles'][:10]  # Limit
                    }
                    results['scans_performed'].append('username')
            except Exception as e:
                results['username'] = {'error': str(e)}
        
        # Domain scan
        domain = data.get('domain', '').strip()
        if domain:
            try:
                domain_result = domain_scanner.quick_scan(domain)
                if domain_result['success']:
                    results['domain'] = {
                        'security_score': domain_result['security_score'],
                        'security_grade': domain_result['security_grade'],
                        'has_https': domain_result['ssl'].get('has_https', False),
                        'email_security_grade': domain_result['email_security']['grade'],
                        'issues': domain_result['issues']
                    }
                    results['scans_performed'].append('domain')
            except Exception as e:
                results['domain'] = {'error': str(e)}
        
        # IP scan
        ip = data.get('ip', '').strip()
        if ip:
            try:
                ip_result = ip_intelligence.analyze(ip)
                if ip_result['success']:
                    results['ip'] = {
                        'location': ip_result['summary']['location'],
                        'threat_level': ip_result['threats']['threat_level'],
                        'reputation_score': ip_result['reputation']['score'],
                        'is_blacklisted': ip_result['blacklists']['is_blacklisted']
                    }
                    results['scans_performed'].append('ip')
            except Exception as e:
                results['ip'] = {'error': str(e)}
        
        # Calculate overall risk
        cyber_risk_engine.reset()
        
        if 'password' in results and isinstance(results['password'], dict):
            breach_count = results['password'].get('breach_count', 0)
            try:
                breach_count = int(breach_count)
            except Exception:
                breach_count = 0
            if breach_count > 0:
                cyber_risk_engine.add_password_breach_risk(breach_count)

        if 'email' in results and isinstance(results['email'], dict):
            breach_count = results['email'].get('breach_count', 0)
            try:
                breach_count = int(breach_count)
            except Exception:
                breach_count = 0
            if breach_count > 0:
                breaches = []
                for b in results['email'].get('breaches', []):
                    if isinstance(b, dict) and 'name' in b:
                        breaches.append({'Name': b['name']})
                cyber_risk_engine.add_email_breach_risk(breaches)

        if 'username' in results and isinstance(results['username'], dict):
            platforms_found = results['username'].get('platforms_found', 0)
            platforms_checked = results['username'].get('platforms_checked', 0)
            try:
                platforms_found = int(platforms_found)
            except Exception:
                platforms_found = 0
            try:
                platforms_checked = int(platforms_checked)
            except Exception:
                platforms_checked = 0
            if platforms_found > 0:
                cyber_risk_engine.add_username_exposure_risk(
                    platforms_found,
                    platforms_checked
                )
        
        if cyber_risk_engine.factors:
            risk_result = cyber_risk_engine.assess()
            results['risk_assessment'] = {
                'overall_score': risk_result['overall_score'],
                'risk_level': risk_result['risk_level'],
                'recommendations': risk_result['recommendations'][:5]
            }
        
        last_results = results

        # Log comprehensive scan to Firestore
        # if current_user.is_authenticated:
        #     scans_done = ', '.join(results.get('scans_performed', []))
        #     risk_score = results.get('risk_assessment', {}).get('overall_score')
        #     summary = f"Scans: {scans_done}"
        #     log_scan(current_user.id, 'Comprehensive Scan', email or username or domain or ip, summary, risk_score)
        #     # Save security report
        #     risk_level = results.get('risk_assessment', {}).get('risk_level', 'Unknown')
        #     save_security_report(current_user.id, 'Comprehensive Scan', results, risk_level)

        return jsonify(results)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== QUIZ ENDPOINTS ====================

def _save_quiz_to_firestore(quiz_id, questions):
    """Persist quiz session to Firestore so it survives server restarts."""
    try:
        doc_data = {
            'quiz_id': quiz_id,
            'created_at': datetime.now().isoformat(),
            'questions': [
                {
                    'id': q.id,
                    'question': q.question,
                    'options': list(q.options),
                    'correct_answer': q.correct_answer,
                    'category': q.category,
                    'difficulty': q.difficulty,
                    'explanation': q.explanation
                }
                for q in questions
            ]
        }
        db.collection('quiz_sessions').document(quiz_id).set(doc_data)
        print(f'[QUIZ] Saved quiz {quiz_id} to Firestore ({len(questions)} questions)')
    except Exception as e:
        print(f'[QUIZ] ERROR saving quiz {quiz_id} to Firestore: {e}')


def _restore_quiz_from_firestore(quiz_id):
    """Restore a quiz session from Firestore into the in-memory dict."""
    try:
        doc = resolve_awaitable(db.collection('quiz_sessions').document(quiz_id).get())
        if not getattr(doc, 'exists', False):
            print(f'[QUIZ] Quiz {quiz_id} not found in Firestore')
            return False
        data = doc.to_dict() if hasattr(doc, 'to_dict') else {}
        from services.quiz_engine import Question
        questions = []
        qlist = data.get('questions') if isinstance(data, dict) else []
        if qlist:
            for q in qlist:
                if isinstance(q, dict):
                    questions.append(Question(
                        id=q.get('id'),
                        question=q.get('question'),
                        options=q.get('options'),
                        correct_answer=q.get('correct_answer'),
                        category=q.get('category'),
                        difficulty=q.get('difficulty'),
                        explanation=q.get('explanation')
                    ))
        cybersecurity_quiz.active_quizzes[quiz_id] = questions
        print(f'[QUIZ] Restored quiz {quiz_id} from Firestore ({len(questions)} questions)')
        return True
    except Exception as e:
        print(f'[QUIZ] ERROR restoring quiz {quiz_id}: {e}')
        return False


def _delete_quiz_from_firestore(quiz_id):
    """Remove a quiz session from Firestore after submission."""
    try:
        db.collection('quiz_sessions').document(quiz_id).delete()
    except Exception as e:
        print(f'[QUIZ] ERROR deleting quiz {quiz_id}: {e}')


def _send_certificate_email(to_email, participant_name, certificate_id, result, pdf_bytes):
    """Send certificate PDF as email attachment to the user.

    Returns True on success, raises on failure.
    """
    import smtplib
    from email.message import EmailMessage
    from email.utils import formatdate

    sender_email = os.getenv('FEEDBACK_EMAIL_ADDRESS')
    sender_password = os.getenv('FEEDBACK_EMAIL_PASSWORD')
    if not sender_email or not sender_password:
        print('[CERT] Email not configured (FEEDBACK_EMAIL_ADDRESS / FEEDBACK_EMAIL_PASSWORD missing)')
        return False

    pct = result.percentage
    status = 'PASSED' if result.passed else 'NOT PASSED'
    status_color = '#00ff88' if result.passed else '#ff0055'

    # Build category breakdown rows for the email
    cat_rows = ""
    for cat, scores in result.category_scores.items():
        cat_pct = (scores['correct'] / scores['total'] * 100) if scores['total'] > 0 else 0
        cat_rows += f'''
        <tr>
            <td style="padding:12px 16px; color:#e6edf3; font-size:13px; border-bottom:1px solid #2d3548;">{cat}</td>
            <td style="padding:12px 16px; text-align:right; color:{'#00ff88' if cat_pct>=70 else '#888'}; font-size:13px; border-bottom:1px solid #2d3548;">{scores['correct']}/{scores['total']}</td>
        </tr>'''

    cert_url = request.host_url.rstrip('/') + url_for('certificate_page', certificate_id=certificate_id)

    html_body = f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;background:#0a0e17;">
<table width="100%" cellspacing="0" cellpadding="0" style="background:#0a0e17;">
<tr><td align="center" style="padding:40px 20px;">
<table width="600" cellspacing="0" cellpadding="0" style="background:linear-gradient(145deg,#1a1f2e,#0d1117);border:1px solid #00ff88;border-radius:16px;overflow:hidden;">
  <tr><td style="background:linear-gradient(135deg,#00ff88,#00cc6a);padding:28px;text-align:center;">
    <h1 style="margin:0;color:#0a0e17;font-size:22px;">&#128274; Cybersecurity Awareness Certificate</h1>
    <p style="margin:8px 0 0;color:#0a0e17;opacity:0.8;font-size:14px;">Dark Web Monitor Security Lab</p>
  </td></tr>
  <tr><td style="padding:30px;text-align:center;">
    <p style="color:#888;font-size:14px;margin:0 0 5px;">Congratulations!</p>
    <h2 style="color:#FFD700;font-size:26px;margin:0 0 10px;letter-spacing:1px;">{participant_name}</h2>
    <p style="color:#e6edf3;font-size:15px;line-height:1.6;margin:0;">
      You have successfully completed the <span style="color:#00ff88;font-weight:600;">Cybersecurity Awareness Quiz</span>.
    </p>
  </td></tr>
  <tr><td style="padding:0 30px;">
    <table width="100%" cellspacing="0" cellpadding="0" style="background:#0d1117;border-radius:10px;">
      <tr>
        <td style="padding:20px;text-align:center;border-right:1px solid #2d3548;">
          <div style="font-size:36px;font-weight:700;color:{'#00ff88' if pct>=70 else '#ffaa00' if pct>=40 else '#ff0055'};">{pct}%</div>
          <div style="color:#888;font-size:12px;margin-top:4px;">SCORE</div>
        </td>
        <td style="padding:20px;text-align:center;border-right:1px solid #2d3548;">
          <div style="font-size:36px;font-weight:700;color:#e6edf3;">{result.score}/{result.total}</div>
          <div style="color:#888;font-size:12px;margin-top:4px;">CORRECT</div>
        </td>
        <td style="padding:20px;text-align:center;">
          <div style="font-size:18px;font-weight:700;color:{status_color};">{status}</div>
          <div style="color:#888;font-size:12px;margin-top:4px;">STATUS</div>
        </td>
      </tr>
    </table>
  </td></tr>
  <tr><td style="padding:20px 30px;">
    <h3 style="color:#00ff88; font-size:14px; margin:0 0 10px; text-transform:uppercase; letter-spacing:1px;">Category Breakdown</h3>
    <table width="100%" cellspacing="0" cellpadding="0" style="background:#0d1117; border-radius:8px;">{cat_rows}</table>
  </td></tr>
  <tr><td style="padding:20px 30px;">
    <table width="100%" cellspacing="0" cellpadding="0" style="background:#0d1117; border-radius:8px;">
      <tr><td style="padding:1
          <td style="padding:12px 16px; color:#e6edf3;font-family:monospace;border-bottom:1px solid #2d3548;">{certificate_id}</td></tr>
      <tr><td style="padding:12px 16px; color:#888; font-size:13px; border-bottom:1px solid #2d3548;">Date</td>
          <td style="padding:12px 16px; color:#e6edf3;border-bottom:1px solid #2d3548;">{result.completion_time}</td></tr>
      <tr><td style="padding:12px 16px; color:#888; font-size:13px;">Issued By</td>
          <td style="padding:12px 16px; color:#e6edf3;">Dark Web Monitor Security Lab</td></tr>
    </table>
  </td></tr>
  <tr><td style="padding:20px 30px 30px; text-align:center;">
    <a href="{cert_url}" style="display:inline-block; padding:12px 28px; background:#00ff88; color:#0a0e17; text
  </td></tr>
  <tr><td style="background:#0d1117; padding:16px; text-align:center; border-top:1px solid #2d3548;">
    <p style="margin:0; color:#555; font-size:11px;">&copy; 2026 Dark Web Monitor. All rights reserved.</p>
  </td></tr>
</table>
</td></tr></table>
</body></html>'''

    plain_text = (
        f"Congratulations {participant_name}!\\n\\n"
        f"You have completed the Cybersecurity Awareness Quiz.\\n"
        f"Score: {result.score}/{result.total} ({pct}%) — {status}\\n"
        f"Certificate ID: {certificate_id}\\n"
        f"Date: {result.completion_time}\\n\\n"
        f"Your certificate PDF is attached.\\n\\n"
        f"— Dark Web Monitor Security Lab"
    )

    msg = EmailMessage()
    msg['Subject'] = f'Cybersecurity Awareness Certificate \u2013 {certificate_id}'
    msg['From'] = f'Dark Web Monitor <{sender_email}>'
    msg['To'] = to_email
    msg['Date'] = formatdate(localtime=True)

    msg.set_content(plain_text)
    msg.add_alternative(html_body, subtype='html')

    # Attach the PDF
    safe_name = participant_name.replace(' ', '_').replace('/', '_')
    msg.add_attachment(
        pdf_bytes,
        maintype='application',
        subtype='pdf',
        filename=f'Certificate_{safe_name}_{certificate_id}.pdf'
    )

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)

    return True





@app.route('/api/quiz/start', methods=['POST'])
def api_quiz_start():
    """Start a new quiz session (static questions)."""
    try:
        data = request.get_json() or {}
        category = data.get('category', 'all')
        count = data.get('count', 10)
        
        # Validate parameters
        count = max(5, min(20, int(count)))

        # Default: Use static questions
        session = cybersecurity_quiz.start_quiz(category=category, count=count, shuffle=True)
        quiz_id = session['quiz_id']
        
        # Persist to Firestore so the session survives server restarts
        _save_quiz_to_firestore(quiz_id, cybersecurity_quiz.active_quizzes[quiz_id])
        return jsonify({
            'success': True,
            'quiz_id': quiz_id,
            'total_questions': session['total_questions'],
            'pass_threshold': session['pass_threshold'],
            'questions': session['questions'],
            'category': category
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/quiz/submit', methods=['POST'])
def api_quiz_submit():
    """Submit quiz answers and get results."""
    try:
        data = request.get_json()
        quiz_id = data.get('quiz_id')
        participant_name = data.get('participant_name', 'Anonymous')
        email = data.get('email', '')
        answers = data.get('answers', {})
        
        print(f'[QUIZ] Submit request for quiz_id={quiz_id}, in_memory={quiz_id in cybersecurity_quiz.active_quizzes}')
        
        # Keep answers as-is: keys can be UUID question IDs or numeric indices.
        if not isinstance(answers, dict):
            return jsonify({'success': False, 'error': 'Invalid answers payload'}), 400
        
        # Restore quiz from Firestore if lost from memory (e.g. server restart)
        if quiz_id not in cybersecurity_quiz.active_quizzes:
            print(f'[QUIZ] Quiz {quiz_id} not in memory, attempting Firestore restore...')
            if not _restore_quiz_from_firestore(quiz_id):
                return jsonify({'success': False, 'error': 'Invalid quiz ID or quiz expired'}), 400
        
        # Prevent duplicate: check if this quiz_id was already submitted
        dup_check = db.collection('quiz_certificates') \
            .where(filter=FieldFilter('quiz_id', '==', quiz_id)).limit(1).stream()
        if any(True for _ in dup_check):
            return jsonify({'success': False, 'error': 'This quiz has already been submitted'}), 400
        
        # Get detailed results before submitting
        detailed = cybersecurity_quiz.get_detailed_results(quiz_id, answers)
        
        # Submit and get result
        result = cybersecurity_quiz.submit_quiz(quiz_id, participant_name, email, answers)
        
        if result is None:
            return jsonify({'success': False, 'error': 'Invalid quiz ID or quiz expired'}), 400
        
        # Clean up Firestore session
        _delete_quiz_from_firestore(quiz_id)
        
        # ── 1. Generate Certificate ID ──
        cert_seq = db.collection('quiz_certificates').document('cert_counter')
        counter_doc = resolve_awaitable(cert_seq.get())
        seq_num = 1
        if hasattr(counter_doc, 'exists') and counter_doc.exists:
            counter_data = counter_doc.to_dict() if hasattr(counter_doc, 'to_dict') else {}
            seq_num = counter_data.get('seq', 0) + 1 if counter_data else 1
        cert_seq.set({'seq': seq_num})
        cert_year = datetime.now().strftime('%Y')
        certificate_id = f'DWM-CERT-{cert_year}-{seq_num:04d}'
        
        # Use logged-in user's email (fall back to form email)
        user_email = ''
        user_id = None
        username = None
        # if current_user.is_authenticated:
        #     user_email = current_user.email or ''
        #     user_id = current_user.id
        #     username = current_user.username
        if not user_email:
            user_email = email  # fallback to form-submitted email
        
        # ── 2. Generate PDF Certificate ──
        pdf_bytes = certificate_generator.generate(result, certificate_id=certificate_id)
        
        # ── 3. Save PDF to /certificates/ folder ──
        cert_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'certificates')
        os.makedirs(cert_dir, exist_ok=True)
        pdf_filename = f'{certificate_id}.pdf'
        pdf_path = os.path.join(cert_dir, pdf_filename)
        with open(pdf_path, 'wb') as f:
            f.write(pdf_bytes)
        print(f'[CERT] PDF saved: {pdf_path}')
        
        # ── 4. Save certificate metadata to Firestore ──
        cert_record = {
            'certificate_id': certificate_id,
            'quiz_id': quiz_id,
            'participant_name': participant_name,
            'email': user_email,
            'user_id': user_id,
            'username': username,
            'score': result.score,
            'total': result.total,
            'percentage': result.percentage,
            'passed': result.passed,
            'completion_time': result.completion_time,
            'category_scores': result.category_scores,
            'certificate_file': f'certificates/{pdf_filename}',
            'created_at': datetime.now().isoformat()
        }
        db.collection('quiz_certificates').document(certificate_id).set(cert_record)
        print(f'[CERT] Firestore record saved: {certificate_id}')

        # ── 4b. Verify certificate record was persisted in Firestore ──
        verify_doc = resolve_awaitable(db.collection('quiz_certificates').document(certificate_id).get())
        db_verified = bool(getattr(verify_doc, 'exists', False))
        if not db_verified:
            return jsonify({
                'success': False,
                'error': 'Certificate was generated but database persistence verification failed.'
            }), 500
        
        # ── 5. Auto-email certificate to user ──
        email_sent = False
        email_error = ''
        if user_email:
            try:
                email_sent = _send_certificate_email(
                    to_email=user_email,
                    participant_name=participant_name,
                    certificate_id=certificate_id,
                    result=result,
                    pdf_bytes=pdf_bytes
                )
                if email_sent:
                    print(f'[CERT] Email sent to {user_email}')
            except Exception as mail_err:
                email_error = str(mail_err)
                print(f'[CERT] Email failed: {email_error}')
        
        return jsonify({
            'success': True,
            'certificate_id': certificate_id,
            'db_verified': db_verified,
            'email_sent': email_sent,
            'email_error': email_error,
            'result': {
                'quiz_id': result.quiz_id,
                'score': result.score,
                'total': result.total,
                'percentage': result.percentage,
                'passed': result.passed,
                'completion_time': result.completion_time,
                'category_scores': result.category_scores
            },
            'detailed_results': detailed
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/certificate/send-email', methods=['POST'])
def api_send_certificate_email():
    """Manually re-send a certificate to a user's email."""
    try:
        data = request.get_json()
        certificate_id = data.get('certificate_id')
        email = data.get('email')
        
        if not certificate_id:
            return jsonify({'success': False, 'error': 'Certificate ID is required'}), 400
            
        doc = resolve_awaitable(db.collection('quiz_certificates').document(certificate_id).get())
        if not getattr(doc, 'exists', False):
            return jsonify({'success': False, 'error': 'Certificate not found'}), 404
        cert_data = doc.to_dict() or {}
        recipient_email = email or cert_data.get('email')
        if not recipient_email:
            return jsonify({'success': False, 'error': 'No recipient email provided'}), 400

        # Reconstruct QuizResult
        result = QuizResult(
            quiz_id=cert_data.get('quiz_id', 'unknown'),
            participant_name=cert_data.get('participant_name', 'Anonymous'),
            email=recipient_email,
            score=cert_data.get('score', 0),
            total=cert_data.get('total', 20),
            percentage=cert_data.get('percentage', 0.0),
            passed=cert_data.get('passed', False),
            completion_time=cert_data.get('completion_time', ''),
            answers={},
            category_scores=cert_data.get('category_scores', {})
        )
        # Regenerate PDF bytes
        pdf_bytes = certificate_generator.generate(result, certificate_id=certificate_id)
        # Send Email
        success = _send_certificate_email(
            to_email=recipient_email,
            participant_name=result.participant_name,
            certificate_id=certificate_id,
            result=result,
            pdf_bytes=pdf_bytes
        )
        if success:
            return jsonify({'success': True, 'message': f'Certificate sent to {recipient_email}'})
        else:
            return jsonify({'success': False, 'error': 'Failed to send email. Check server configuration.'}), 500
            
    except Exception as e:
        print(f'[CERT] Manual email error: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500


# ── CTF CHALLENGES ROUTES ──
@app.route('/ctf/')
def ctf_dashboard():
    """Redirect to the new modular CTF platform."""
    return redirect('/v2/ctf/')

# Note: Migrated to routes/ctf_routes.py and registered as blueprint in V2 platform.


@app.route('/api/quiz/certificate', methods=['POST'])
def api_quiz_certificate():
    """Generate and download a PDF certificate."""
    try:
        data = request.get_json()
        result_data = data.get('result', {})
        
        # Create QuizResult object
        result = QuizResult(
            quiz_id=result_data.get('quiz_id', 'unknown'),
            participant_name=data.get('participant_name', 'Anonymous'),
            email=data.get('email', ''),
            score=result_data.get('score', 0),
            total=result_data.get('total', 20),
            percentage=result_data.get('percentage', 0),
            passed=result_data.get('passed', False),
            completion_time=result_data.get('completion_time', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            answers={},
            category_scores=result_data.get('category_scores', {})
        )
        
        # Generate PDF
        pdf_bytes = certificate_generator.generate(result)
        
        # Create response with PDF
        from io import BytesIO
        buffer = BytesIO(pdf_bytes)
        buffer.seek(0)
        
        safe_name = (result.participant_name or 'Anonymous').replace(" ", "_") if result.participant_name else 'Anonymous'
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'cybersecurity_certificate_{safe_name}.pdf'
        )
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/certificates/download/<certificate_id>')
# @login_required
def download_saved_certificate(certificate_id):
    """Download a previously saved certificate PDF from the certificates folder."""
    import re
    # Validate certificate_id format to prevent path traversal
    if not re.match(r'^DWM-CERT-\d{4}-[A-Z0-9]+$', certificate_id):
        return jsonify({'success': False, 'error': 'Invalid certificate ID format'}), 400

    # Verify the certificate belongs to the current user
    doc = resolve_awaitable(db.collection('quiz_certificates').document(certificate_id).get())
    if not getattr(doc, 'exists', False):
        return jsonify({'success': False, 'error': 'Certificate not found'}), 404
    cert = doc.to_dict() if doc else None
    # if cert.get('user_id') != current_user.id:
    #     return jsonify({'success': False, 'error': 'Unauthorized'}), 403

    cert_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'certificates')
    pdf_path = os.path.join(cert_dir, f'{certificate_id}.pdf')
    if not os.path.isfile(pdf_path):
        return jsonify({'success': False, 'error': 'PDF file not found on server'}), 404

    return send_file(
        pdf_path,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'Certificate_{certificate_id}.pdf'
    )


# ==================== CERTIFICATE PAGE ROUTES ====================

@app.route('/certificate/<certificate_id>')
def certificate_page(certificate_id):
    """Display a web-based certificate page."""
    try:
        doc = resolve_awaitable(db.collection('quiz_certificates').document(certificate_id).get())
        if not getattr(doc, 'exists', False):
            return render_template('404.html'), 404
        cert = doc.to_dict() if doc else None
        if cert is None:
            return render_template('404.html'), 404

        # Backward-compatible fallback: some older records may miss certificate_id.
        if not cert.get('certificate_id'):
            cert['certificate_id'] = certificate_id
            try:
                db.collection('quiz_certificates').document(certificate_id).update({'certificate_id': certificate_id})
            except Exception:
                pass

        verify_url = request.host_url.rstrip('/') + url_for('verify_certificate', certificate_id=certificate_id)
        return render_template('certificate.html', cert=cert, verify_url=verify_url)
    except Exception:
        return render_template('404.html'), 404


@app.route('/verify/<certificate_id>')
def verify_certificate(certificate_id):
    """Public verification endpoint for certificates."""
    try:
        doc = resolve_awaitable(db.collection('quiz_certificates').document(certificate_id).get())
        if not getattr(doc, 'exists', False):
            return jsonify({'valid': False, 'error': 'Certificate not found'}), 404
        cert = doc.to_dict() if doc else {}
        resolved_certificate_id = cert.get('certificate_id') or certificate_id
        return jsonify({
            'valid': True,
            'certificate_id': resolved_certificate_id,
            'participant_name': cert.get('participant_name'),
            'score': cert.get('score'),
            'total': cert.get('total'),
            'percentage': cert.get('percentage'),
            'passed': cert.get('passed'),
            'completion_time': cert.get('completion_time'),
            'issued_by': 'Dark Web Monitor Security Lab'
        })
    except Exception:
        return jsonify({'valid': False, 'error': 'Verification failed'}), 500


@app.route('/certificate-history')
# @login_required
def certificate_history_page():
    """Show user's earned certificates and verification tool."""
    return render_template('certificate_history.html')


@app.route('/api/certificate-history')
# @login_required
def api_certificate_history():
    """Get all certificates for the current logged-in user."""
    try:
        docs = resolve_awaitable(db.collection('quiz_certificates').stream())
        certificates = []
        for doc in docs:
            if getattr(doc, 'id', '') == 'cert_counter':
                continue
            data = doc.to_dict() if hasattr(doc, 'to_dict') else {}
            if not data:
                continue

            # Ensure every record has certificate_id for UI and verification links.
            if not data.get('certificate_id'):
                data['certificate_id'] = getattr(doc, 'id', '')

            certificates.append(data)

        certificates.sort(key=lambda c: c.get('created_at', ''), reverse=True)
        return jsonify({'success': True, 'certificates': certificates[:100]})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'certificates': []}), 500


@app.route('/api/verify-certificate', methods=['POST'])
def api_verify_certificate_public():
    """Public API to verify a certificate by ID."""
    try:
        data = request.get_json()
        cert_id = data.get('certificate_id', '').strip()
        if not cert_id:
            return jsonify({'valid': False, 'error': 'Certificate ID is required'}), 400
        doc = resolve_awaitable(db.collection('quiz_certificates').document(cert_id).get())
        if not getattr(doc, 'exists', False):
            return jsonify({'valid': False, 'error': 'Certificate not found. This ID does not match any issued certificate.'})
        cert = doc.to_dict() if doc else {}
        resolved_certificate_id = cert.get('certificate_id') or cert_id
        return jsonify({
            'valid': True,
            'certificate_id': resolved_certificate_id,
            'participant_name': cert.get('participant_name'),
            'score': cert.get('score'),
            'total': cert.get('total'),
            'percentage': cert.get('percentage'),
            'passed': cert.get('passed'),
            'completion_time': cert.get('completion_time'),
            'issued_by': 'Dark Web Monitor Security Lab'
        })
    except Exception:
        return jsonify({'valid': False, 'error': 'Verification failed'}), 500


@app.route('/api/email-certificate', methods=['POST'])
# @login_required
def api_email_certificate():
    """Send a certificate to the current user's registered email."""
    try:
        data = request.get_json()
        cert_id = data.get('certificate_id', '').strip()
        if not cert_id:
            return jsonify({'success': False, 'error': 'Certificate ID is required'}), 400

        doc = resolve_awaitable(db.collection('quiz_certificates').document(cert_id).get())
        if not getattr(doc, 'exists', False):
            return jsonify({'success': False, 'error': 'Certificate not found'}), 404
        cert = doc.to_dict() if doc else None

        user_email = data.get('email')
        if not user_email:
            return jsonify({'success': False, 'error': 'Email address is required in the request payload'}), 400
        sender_email = os.getenv('FEEDBACK_EMAIL_ADDRESS')
        sender_password = os.getenv('FEEDBACK_EMAIL_PASSWORD')
        if not sender_email or not sender_password:
            return jsonify({'success': False, 'error': 'Email service is not configured on the server'}), 500

        pct = cert.get('percentage', 0) if cert else 0
        passed = cert.get('passed', False) if cert else False
        status_text = 'PASSED' if passed else 'NOT PASSED'
        status_color = '#00ff88' if passed else '#ff0055'
        name = cert.get('participant_name', 'Anonymous') if cert else 'Anonymous'
        score = cert.get('score', 0) if cert else 0
        total = cert.get('total', 20) if cert else 20
        comp_time = cert.get('completion_time', 'N/A') if cert else 'N/A'
        cert_url = request.host_url.rstrip('/') + f'/certificate/{cert_id}'
        verify_url = request.host_url.rstrip('/') + f'/verify/{cert_id}'

        # Build category rows
        cat_rows = ''
        for cat, sc in (cert.get('category_scores', {}) if cert else {}).items():
            cat_pct = round(sc.get('correct', 0) / sc.get('total', 1) * 100) if sc.get('total', 0) > 0 else 0
            bar_color = '#00ff88' if cat_pct >= 70 else '#ffaa00' if cat_pct >= 40 else '#ff0055'
            cat_rows += f'''<tr>
                <td style="padding:8px 12px; color:#e6edf3; border-bottom:1px solid #2d3548;">{cat}</td>
                <td style="padding:8px 12px; border-bottom:1px solid #2d3548;">
                    <div style="background:rgba(255,255,255,0.05); border-radius:4px; height:8px; width:100%;">
                        <div style="background:{bar_color}; height:8px; border-radius:4px; width:{cat_pct}%;"></div>
                    </div>
                </td>
                <td style="padding:8px 12px; color:#e6edf3; text-align:right; border-bottom:1px solid #2d3548;">{cat_pct}%</td>
            </tr>'''

        html_body = f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"></head>
<body style="margin:0; padding:0; font-family:'Helvetica Neue', Helvetica, Arial, sans-serif; background:#050a0f;">
<table width="100%" cellspacing="0" cellpadding="0" style="background:#050a0f; padding:50px 0;">
<tr><td align="center">
    <!-- Main Outer Container with Neon Corners -->
    <table width="680" cellspacing="0" cellpadding="0" style="background:#08111a; border:1px solid #00ffc6; border-radius:4px; position:relative; table-layout:fixed;">
        <tr><td style="padding:2px; position:relative;">
            
            <!-- Content Wrapper -->
            <table width="100%" cellspacing="0" cellpadding="0" style="background:#080f19;">
                <!-- Header -->
                <tr><td style="padding:30px 40px 10px;">
                    <table width="100%" cellspacing="0" cellpadding="0">
                        <tr>
                            <td>
                                <div style="font-size:18px; font-weight:bold; color:#00ffc6; letter-spacing:2px; display:inline-block; vertical-align:middle;">🛡️ DARK WEB MONITOR</div>
                                <div style="font-size:10px; color:#888; letter-spacing:1px; text-transform:uppercase; margin-top:2px;">Security Lab</div>
                            </td>
                            <td align="right">
                                <div style="font-size:9px; color:#ffd700; letter-spacing:2px; text-transform:uppercase; font-weight:bold;">CYBERSECURITY AWARENESS PROGRAM</div>
                            </td>
                        </tr>
                    </table>
                </td></tr>

                <!-- Main Body with Shield Style -->
                <tr><td align="center" style="padding:20px 40px 40px;">
                    
                    <!-- Top Badge -->
                    <div style="margin:0 auto 20px; width:45px; height:45px; border:2.5px solid #00ffc6; border-radius:50%; color:#00ffc6; line-height:42px; font-size:9px; font-weight:bold; text-align:center; background:rgba(0,255,198,0.05);">AWARD</div>
                    
                    <h1 style="color:#ffffff; font-size:32px; font-weight:900; margin:0 0 15px; letter-spacing:6px; text-shadow:0 0 15px rgba(255,255,255,0.2);">CERTIFICATE OF COMPLETION</h1>
                    <div style="width:200px; height:2px; background:#00ffc6; margin:0 auto 30px; border-radius:1px;"></div>
                    
                    <p style="color:#666; font-size:12px; margin:0 0 10px; text-transform:uppercase; letter-spacing:3px;">This is to certify that</p>
                    
                    <h2 style="color:#ffd700; font-size:48px; font-weight:800; margin:0 0 5px; letter-spacing:3px; text-shadow:0 0 10px rgba(255,215,0,0.3);">{name}</h2>
                    <div style="width:300px; height:2px; background:linear-gradient(90deg, transparent, #ffd700, transparent); margin:0 auto 30px;"></div>
                    
                    <p style="color:#888; font-size:16px; line-height:1.7; margin:0 0 40px; max-width:540px;">
                        has successfully completed the <strong style="color:#00ffc6;">Cybersecurity Awareness Quiz</strong> demonstrating proficiency in cybersecurity fundamentals, threat awareness, and security best practices.
                    </p>
                    
                    <!-- Bottom Circles Row (Pass/Score) -->
                    <table width="100%" cellspacing="0" cellpadding="0">
                        <tr>
                            <td align="center" width="50%">
                                <div style="width:90px; height:90px; border:4px solid #00ffc6; border-radius:50%; line-height:82px; display:inline-block; text-align:center; box-shadow:0 0 15px rgba(0,255,198,0.2);">
                                    <span style="color:#ffffff; font-size:22px; font-weight:bold;">{pct}%</span>
                                </div>
                                <div style="margin-top:10px; color:#888; font-size:11px; letter-spacing:1px;">SCORE: {score}/{total}</div>
                            </td>
                            <td align="center" width="50%">
                                <div style="width:50px; height:50px; border:2.5px solid {status_color}; border-radius:50%; line-height:45px; display:inline-block; text-align:center; color:{status_color};">
                                    <span style="font-size:24px;">{'✓' if passed else '✕'}</span>
                                </div>
                                <div style="margin-top:10px; color:{status_color}; font-size:14px; font-weight:bolder; letter-spacing:1px;">{status_text}</div>
                                <div style="color:#888; font-size:10px; letter-spacing:1px;">STATUS</div>
                            </td>
                        </tr>
                    </table>
                </td></tr>
                
                <!-- Bottom Branding/QR Section -->
                <tr><td style="padding:25px 40px; background:rgba(255,255,255,0.015); border-top:1px solid rgba(0,255,198,0.15); border-bottom:1px solid rgba(0,255,198,0.05);">
                    <table width="100%" cellspacing="0" cellpadding="0">
                        <tr>
                            <td width="33%" style="font-size:11px; color:#555; vertical-align:middle;">
                                <div style="margin-bottom:4px;">CERT ID: <span style="font-family:monospace; color:#888;">{cert_id}</span></div>
                                <div>ISSUED: <span style="color:#888;">{comp_time}</span></div>
                            </td>
                            <td width="34%" align="center" style="vertical-align:middle;">
                                <div style="background:#fff; padding:6px; display:inline-block; border-radius:2px;">
                                    <img src="https://api.qrserver.com/v1/create-qr-code/?size=60x60&data={verify_url}" width="60" height="60" alt="QR" style="display:block;">
                                </div>
                                <div style="margin-top:5px; font-size:8px; color:#444; letter-spacing:1px;">SCAN TO VERIFY</div>
                            </td>
                            <td width="33%" align="right" style="vertical-align:bottom; padding-bottom:5px;">
                                <div style="font-size:13px; font-weight:bold; color:#fff; border-bottom:2px solid #00ffc6; padding-bottom:3px; display:inline-block;">Verified by Dark Web Monitor</div>
                            </td>
                        </tr>
                    </table>
                </td></tr>

                <!-- Outer Button Footer -->
                <tr><td style="padding:30px; text-align:center; background:#050a0f;">
                     <a href="{cert_url}" style="display:inline-block; padding:12px 30px; background:transparent; color:#00ffc6; border:1px solid #00ffc6; text-decoration:none; border-radius:3px; font-weight:bold; font-size:13px; letter-spacing:2px; text-transform:uppercase; transition:all 0.3s;">VALIDATE SECURE ACCESS</a>
                     <p style="margin:25px 0 0; color:#333; font-size:10px; letter-spacing:0.5px;">&copy; 2026 Dark Web Monitor Security Lab. All rights reserved.</p>
                </td></tr>
            </table>
        </td></tr>
    </table>
</td></tr></table>
</body></html>'''

        # Generate PDF for attachment using quiz_engine logic
        from services.quiz_engine import CybersecurityQuiz, CertificateGenerator, QuizResult
        
        # We need to recreate the result object for the generator
        # Note: we might need answers and category_scores from the cert data
        mock_result = QuizResult(
            quiz_id=cert_id,
            participant_name=name,
            email=user_email,
            score=score,
            total=total,
            percentage=pct,
            passed=passed,
            completion_time=comp_time,
            answers=cert.get('answers', {}) if cert else {},
            category_scores=cert.get('category_scores', {}) if cert else {}
        )
        
        pdf_gen = CertificateGenerator()
        pdf_bytes = pdf_gen.generate(mock_result, certificate_id=cert_id)

        import smtplib
        from email.message import EmailMessage as EM
        from email.utils import formatdate
        from email.mime.application import MIMEApplication

        msg = EM()
        msg['Subject'] = f'Your Official Cybersecurity Certificate - {cert_id}'
        msg['From'] = f'Dark Web Monitor <{sender_email}>'
        msg['To'] = user_email
        msg['Date'] = formatdate(localtime=True)

        msg.set_content(f'Dear {name},\n\nCongratulations! You have successfully completed the Cybersecurity Awareness Quiz. Please find your official certificate attached as a PDF.\n\nCertificate ID: {cert_id}\nScore: {pct}%\n\nYou can also verify your certificate online at: {cert_url}')
        msg.add_alternative(html_body, subtype='html')
        
        # Attach PDF
        msg.add_attachment(
            pdf_bytes,
            maintype='application',
            subtype='pdf',
            filename=f'DarkWebMonitor_Certificate_{cert_id}.pdf'
        )

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)

        return jsonify({'success': True, 'message': f'Certificate sent to {user_email}'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tools/hash', methods=['POST'])
def api_hash_generator():
    """
    Generate hashes for input text.
    
    Request body: {"text": "string", "algorithm": "md5|sha1|sha256|sha512" (optional)}
    """
    try:
        data = request.get_json()
        text = data.get('text', '')
        algorithm = data.get('algorithm')
        
        if not text:
            return jsonify({'success': False, 'error': 'Text is required'}), 400
        
        if algorithm:
            result = hash_tool.generate(text, algorithm)
            return jsonify({
                'success': True,
                'algorithm': algorithm,
                'hash': result.single_hash,
                'all_hashes': {
                    'md5': result.md5,
                    'sha1': result.sha1,
                    'sha256': result.sha256,
                    'sha512': result.sha512
                }
            })
        else:
            result = hash_tool.generate_all(text)
            return jsonify({
                'success': True,
                'hashes': {
                    'md5': result.md5,
                    'sha1': result.sha1,
                    'sha256': result.sha256,
                    'sha512': result.sha512
                }
            })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/tools/hash/verify', methods=['POST'])
def api_hash_verify():
    """
    Verify if a hash matches text.
    
    Request body: {"text": "string", "hash": "string", "algorithm": "string" (optional)}
    """
    try:
        data = request.get_json()
        text = data.get('text', '')
        hash_value = data.get('hash', '')
        algorithm = data.get('algorithm')
        
        if not text or not hash_value:
            return jsonify({'success': False, 'error': 'Text and hash are required'}), 400
        
        result = hash_tool.verify_hash(text, hash_value, algorithm)
        return jsonify({
            'success': True,
            'match': result['match'],
            'detected_algorithm': result['algorithm'],
            'algorithms_checked': result['checked_algorithms']
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/tools/base64', methods=['POST'])
def api_base64():
    """
    Base64 encode or decode text.
    
    Request body: {"text": "string", "operation": "encode|decode", "url_safe": bool (optional)}
    """
    try:
        data = request.get_json()
        text = data.get('text', '')
        operation = data.get('operation', 'encode')
        url_safe = data.get('url_safe', False)
        
        if not text:
            return jsonify({'success': False, 'error': 'Text is required'}), 400
        
        if operation == 'decode':
            if url_safe:
                result = base64_tool.decode_url_safe(text)
            else:
                result = base64_tool.decode(text)
        else:
            if url_safe:
                result = base64_tool.encode_url_safe(text)
            else:
                result = base64_tool.encode(text)
        
        return jsonify({
            'success': result.success,
            'operation': result.operation,
            'output': result.output,
            'error': result.error
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/tools/url', methods=['POST'])
def api_url_encoder():
    """
    URL encode or decode text.
    
    Request body: {"text": "string", "operation": "encode|decode|parse", "plus_encoding": bool}
    """
    try:
        data = request.get_json()
        text = data.get('text', '')
        operation = data.get('operation', 'encode')
        plus_encoding = data.get('plus_encoding', False)
        
        if not text:
            return jsonify({'success': False, 'error': 'Text is required'}), 400
        
        if operation == 'decode':
            result = url_tool.decode(text, plus_encoding)
        elif operation == 'parse':
            result = url_tool.parse_url(text)
            return jsonify({
                'success': result.success,
                'operation': result.operation,
                'output': result.output,
                'parsed_info': result.parsed_info,
                'error': result.error
            })
        else:
            result = url_tool.encode(text, plus_encoding)
        
        return jsonify({
            'success': result.success,
            'operation': result.operation,
            'output': result.output,
            'error': result.error
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/tools/jwt', methods=['POST'])
def api_jwt_decoder():
    """
    Decode a JWT token.
    
    Request body: {"token": "string"}
    """
    try:
        data = request.get_json()
        token = data.get('token', '')
        
        if not token:
            return jsonify({'success': False, 'error': 'Token is required'}), 400
        
        result = jwt_decoder.decode(token)
        
        return jsonify({
            'success': result.is_valid_format,
            'header': result.header,
            'payload': result.payload,
            'signature': result.signature,
            'expiration': result.expiration,
            'issued_at': result.issued_at,
            'is_expired': result.is_expired,
            'formatted': jwt_decoder.format_output(result),
            'error': result.error
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/tools/password-strength', methods=['POST'])
def api_password_strength():
    """
    Analyze password strength.
    
    Request body: {"password": "string"}
    """
    try:
        data = request.get_json()
        password = data.get('password', '')
        
        if not password:
            return jsonify({'success': False, 'error': 'Password is required'}), 400
        
        result = password_strength_analyzer.analyze(password)
        
        # result may be an object or dict
        if isinstance(result, dict):
            strength_level = result.get('strength_level')
            if hasattr(strength_level, 'value'):
                strength_level_value = getattr(strength_level, 'value', None)
            else:
                strength_level_value = strength_level
            return jsonify({
                'success': True,
                'length': result.get('password_length'),
                'strength_level': strength_level_value,
                'strength_score': result.get('strength_score'),
                'entropy_bits': result.get('entropy_bits'),
                'crack_time': result.get('crack_time_display'),
                'characteristics': {
                    'has_uppercase': result.get('has_uppercase'),
                    'has_lowercase': result.get('has_lowercase'),
                    'has_digits': result.get('has_digits'),
                    'has_special': result.get('has_special'),
                    'has_repeated': result.get('has_repeated'),
                    'has_sequential': result.get('has_sequential'),
                    'has_common_pattern': result.get('has_common_pattern')
                },
                'checks_passed': result.get('checks_passed'),
                'checks_failed': result.get('checks_failed'),
                'suggestions': result.get('suggestions'),
                'unique_chars': result.get('unique_chars')
            })
        else:
            return jsonify({
                'success': True,
                'length': getattr(result, 'password_length', None),
                'strength_level': getattr(getattr(result, 'strength_level', None), 'value', None),
                'strength_score': getattr(result, 'strength_score', None),
                'entropy_bits': getattr(result, 'entropy_bits', None),
                'crack_time': getattr(result, 'crack_time_display', None),
                'characteristics': {
                    'has_uppercase': getattr(result, 'has_uppercase', None),
                    'has_lowercase': getattr(result, 'has_lowercase', None),
                    'has_digits': getattr(result, 'has_digits', None),
                    'has_special': getattr(result, 'has_special', None),
                    'has_repeated': getattr(result, 'has_repeated', None),
                    'has_sequential': getattr(result, 'has_sequential', None),
                    'has_common_pattern': getattr(result, 'has_common_pattern', None)
                },
                'checks_passed': getattr(result, 'checks_passed', None),
                'checks_failed': getattr(result, 'checks_failed', None),
                'suggestions': getattr(result, 'suggestions', None),
                'unique_chars': getattr(result, 'unique_chars', None)
            })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/tools/ip-lookup', methods=['POST'])
def api_ip_lookup():
    """
    Lookup IP address information.
    
    Request body: {"ip": "string"}
    """
    try:
        data = request.get_json()
        ip = data.get('ip', '')
        
        if not ip:
            return jsonify({'success': False, 'error': 'IP address is required'}), 400
        
        result = ip_lookup_tool.lookup(ip)
        
        return jsonify({
            'success': result.is_valid,
            'ip': result.ip,
            'hostname': result.hostname,
            'ip_type': result.ip_type,
            'geolocation': {
                'country': result.country,
                'country_code': result.country_code,
                'region': result.region,
                'city': result.city,
                'latitude': result.latitude,
                'longitude': result.longitude,
                'timezone': result.timezone
            },
            'network': {
                'asn': result.asn,
                'org': result.org,
                'isp': result.isp
            },
            'classification': {
                'is_private': result.is_private,
                'is_reserved': result.is_reserved,
                'is_loopback': result.is_loopback,
                'is_datacenter': result.is_datacenter,
                'is_proxy': result.is_proxy,
                'is_vpn': result.is_vpn,
                'is_tor': result.is_tor
            },
            'formatted': ip_lookup_tool.format_output(result),
            'error': result.error
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/tools/dns', methods=['POST'])
def api_dns_lookup():
    """
    Perform DNS lookup.
    
    Request body: {"domain": "string", "record_types": ["A", "MX", ...] (optional)}
    """
    try:
        data = request.get_json()
        domain = data.get('domain', '')
        record_types = data.get('record_types')
        
        if not domain:
            return jsonify({'success': False, 'error': 'Domain is required'}), 400
        
        result = dns_lookup_tool.lookup(domain, record_types)
        
        return jsonify({
            'success': result.success,
            'domain': result.domain,
            'records': result.records,
            'query_time_ms': result.query_time_ms,
            'nameservers': result.nameservers,
            'formatted': dns_lookup_tool.format_output(result),
            'error': result.error
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/tools/dns/reverse', methods=['POST'])
def api_dns_reverse():
    """
    Perform reverse DNS lookup.
    
    Request body: {"ip": "string"}
    """
    try:
        data = request.get_json()
        ip = data.get('ip', '')
        
        if not ip:
            return jsonify({'success': False, 'error': 'IP address is required'}), 400
        
        result = dns_lookup_tool.reverse_lookup(ip)
        
        return jsonify({
            'success': result.success,
            'ip': result.domain,
            'records': result.records,
            'error': result.error
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/tools/subdomains', methods=['POST'])
def api_subdomain_finder():
    """
    Find subdomains for a domain.
    
    Request body: {"domain": "string", "quick": bool (optional)}
    """
    try:
        data = request.get_json()
        domain = data.get('domain', '')
        quick = data.get('quick', True)
        
        if not domain:
            return jsonify({'success': False, 'error': 'Domain is required'}), 400
        
        if quick:
            result = subdomain_finder.quick_scan(domain)
        else:
            result = subdomain_finder.find(domain)
        
        return jsonify({
            'success': result.success,
            'domain': result.domain,
            'subdomains': result.subdomains,
            'total_found': result.total_found,
            'sources_used': result.sources_used,
            'formatted': subdomain_finder.format_output(result),
            'error': result.error
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/tools/asset-health', methods=['POST'])
def api_asset_health():
    """
    Defensive health checks for allowlisted assets only.

    Request body: {"target": "https://host-or-hostname"}
    """
    try:
        data = request.get_json() or {}
        target = data.get('target', '')
        if not target:
            return jsonify({'success': False, 'error': 'Target is required'}), 400
        result = asset_health_checker.check(target)
        return jsonify(result), (200 if result.get('success') else 400)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/tools/surface-audit', methods=['POST'])
def api_surface_audit():
    """
    Defensive route audit for allowlisted base URLs.

    Request body: {"base_url": "http://localhost:5000", "routes": ["/", "/quiz", ...]}
    """
    try:
        data = request.get_json() or {}
        base_url = data.get('base_url', '')
        routes = data.get('routes')
        if not base_url:
            return jsonify({'success': False, 'error': 'Base URL is required'}), 400
        result = surface_audit_tool.audit(base_url, routes)
        return jsonify(result), (200 if result.get('success') else 400)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/tools/text-binary', methods=['POST'])
def api_text_binary():
    """
    Convert between text and binary/hex/decimal/octal.
    
    Request body: {"text": "string", "operation": "to_binary|from_binary|to_hex|from_hex|to_decimal|from_decimal|to_octal|from_octal|all"}
    """
    try:
        data = request.get_json()
        text = data.get('text', '')
        operation = data.get('operation', 'all')
        
        if not text:
            return jsonify({'success': False, 'error': 'Text is required'}), 400
        
        if operation == 'all':
            result = text_binary_converter.convert_all(text)
            return jsonify({
                'success': True,
                'operation': 'all',
                'conversions': result
            })
        elif operation == 'to_binary':
            result = text_binary_converter.text_to_binary(text)
        elif operation == 'from_binary':
            result = text_binary_converter.binary_to_text(text)
        elif operation == 'to_hex':
            result = text_binary_converter.text_to_hex(text)
        elif operation == 'from_hex':
            result = text_binary_converter.hex_to_text(text)
        elif operation == 'to_decimal':
            result = text_binary_converter.text_to_decimal(text)
        elif operation == 'from_decimal':
            result = text_binary_converter.decimal_to_text(text)
        elif operation == 'to_octal':
            result = text_binary_converter.text_to_octal(text)
        elif operation == 'from_octal':
            result = text_binary_converter.octal_to_text(text)
        else:
            return jsonify({'success': False, 'error': 'Invalid operation'}), 400
        
        return jsonify({
            'success': result.success,
            'operation': result.operation,
            'output': result.output,
            'error': result.error
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/tools/rot13', methods=['POST'])
def api_rot13():
    """
    Apply ROT13/Caesar cipher.
    
    Request body: {"text": "string", "operation": "rot13|rot47|caesar|atbash|reverse|brute", "shift": number (for caesar)}
    """
    try:
        data = request.get_json()
        text = data.get('text', '')
        operation = data.get('operation', 'rot13')
        shift = data.get('shift', 13)
        
        if not text:
            return jsonify({'success': False, 'error': 'Text is required'}), 400
        
        if operation == 'rot13':
            result = rot13_tool.rot13(text)
        elif operation == 'rot47':
            result = rot13_tool.rot47(text)
        elif operation == 'caesar':
            result = rot13_tool.caesar_cipher(text, shift)
        elif operation == 'atbash':
            result = rot13_tool.atbash(text)
        elif operation == 'reverse':
            result = rot13_tool.reverse_string(text)
        elif operation == 'brute':
            brute_results = rot13_tool.brute_force(text)
            return jsonify({
                'success': True,
                'operation': 'brute_force',
                'results': brute_results,
                'formatted': rot13_tool.format_brute_force(text)
            })
        else:
            return jsonify({'success': False, 'error': 'Invalid operation'}), 400
        
        return jsonify({
            'success': result.success,
            'operation': result.operation,
            'output': result.output,
            'shift': result.shift,
            'error': result.error
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/tools/list')
def api_tools_list():
    """Get list of available cyber tools."""
    return jsonify({
        'tools': [
            {
                'id': 'hash',
                'name': 'Hash Generator',
                'description': 'Generate MD5, SHA1, SHA256, SHA512 hashes',
                'icon': 'fa-hashtag'
            },
            {
                'id': 'base64',
                'name': 'Base64 Encoder/Decoder',
                'description': 'Encode and decode Base64 strings',
                'icon': 'fa-code'
            },
            {
                'id': 'url',
                'name': 'URL Encoder/Decoder',
                'description': 'Encode, decode, and parse URLs',
                'icon': 'fa-link'
            },
            {
                'id': 'jwt',
                'name': 'JWT Token Decoder',
                'description': 'Decode and analyze JSON Web Tokens',
                'icon': 'fa-key'
            },
            {
                'id': 'password-strength',
                'name': 'Password Strength Analyzer',
                'description': 'Analyze password strength and get suggestions',
                'icon': 'fa-shield-alt'
            },
            {
                'id': 'ip-lookup',
                'name': 'IP Intelligence Lookup',
                'description': 'Get geolocation and threat intelligence for IPs',
                'icon': 'fa-network-wired'
            },
            {
                'id': 'dns',
                'name': 'DNS Lookup Tool',
                'description': 'Query DNS records (A, MX, NS, TXT, etc.)',
                'icon': 'fa-server'
            },
            {
                'id': 'subdomains',
                'name': 'Subdomain Finder',
                'description': 'Discover subdomains for a domain',
                'icon': 'fa-sitemap'
            },
            {
                'id': 'asset-health',
                'name': 'Asset Health Checker',
                'description': 'Allowlist-based DNS, TLS, and security-header checks',
                'icon': 'fa-heart-pulse'
            },
            {
                'id': 'surface-audit',
                'name': 'Surface Audit Tool',
                'description': 'Audit known routes for broken pages and server errors',
                'icon': 'fa-route'
            },
            {
                'id': 'text-binary',
                'name': 'Text ↔ Binary Converter',
                'description': 'Convert between text, binary, hex, decimal',
                'icon': 'fa-exchange-alt'
            },
            {
                'id': 'rot13',
                'name': 'ROT13/Caesar Cipher',
                'description': 'Encode/decode with ROT13, ROT47, Caesar cipher',
                'icon': 'fa-lock'
            }
        ]
    })


@app.route('/api/metadata-extract', methods=['POST'])
def api_metadata_extract():
    """
    Extract metadata from uploaded files.
    
    Accepts: JPG, PNG, PDF, DOCX files (max 50MB)
    Returns: Extracted metadata including GPS, author, camera info, etc.
    """
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Read file data into memory (no permanent storage)
        file_data = file.read()
        filename = file.filename
        
        # Extract metadata
        result = metadata_extractor.extract(file_data, filename)
        # If extract returns a dict, use it directly; else, try to_dict if available
        if isinstance(result, dict):
            response_data = result
        elif hasattr(metadata_extractor, 'to_dict'):
            response_data = metadata_extractor.to_dict(result)
        else:
            response_data = {'success': False, 'error': 'Could not extract metadata'}
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Extraction failed: {str(e)}'
        }), 500


@app.route('/api/metadata-features', methods=['GET'])
def api_metadata_features():
    """Return available metadata extraction features based on installed dependencies."""
    try:
        features = getattr(metadata_extractor, 'get_available_features', lambda: [])()
        deps = getattr(metadata_extractor, '_check_dependencies', lambda: [])()
        max_file_size = getattr(metadata_extractor, 'max_file_size', 50 * 1024 * 1024)
        allowed_ext = getattr(metadata_extractor, 'ALLOWED_EXTENSIONS', set(['jpg', 'png', 'pdf', 'docx']))
        return jsonify({
            'success': True,
            'features': features,
            'dependencies': deps,
            'max_file_size_mb': max_file_size // (1024 * 1024),
            'allowed_extensions': list(allowed_ext)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== FEEDBACK ====================

# Store feedback in memory (for demo) - in production, use a database
feedback_storage = []

@app.route('/api/feedback', methods=['POST'])
def api_submit_feedback():
    """
    Submit user feedback from exit intent modal.
    
    Request body: {
        "rating": int (1-5),
        "feedback": str (optional),
        "timestamp": str (ISO format),
        "page": str (page URL path),
        "userAgent": str
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        rating = data.get('rating')
        if not rating or not isinstance(rating, int) or rating < 1 or rating > 5:
            return jsonify({'error': 'Invalid rating. Must be 1-5.'}), 400
        
        feedback_entry = {
            'id': len(feedback_storage) + 1,
            'rating': rating,
            'feedback': data.get('feedback', '').strip()[:500],  # Limit to 500 chars
            'page': data.get('page', '/'),
            'user_agent': data.get('userAgent', ''),
            'timestamp': data.get('timestamp', datetime.now().isoformat()),
            'received_at': datetime.now().isoformat(),
            'ip': request.remote_addr
        }
        
        # Store in memory (replace with database in production)
        feedback_storage.append(feedback_entry)
        
        # Send email notification (async-friendly, won't block response)
        email_sent = False
        email_error = None
        if is_email_configured():
            try:
                email_sent, email_message = send_feedback_email(feedback_entry)
                if not email_sent:
                    email_error = email_message
                    print(f"[Feedback Email Warning] {email_message}")
            except Exception as email_err:
                email_error = str(email_err)
                print(f"[Feedback Email Error] {email_err}")
        
        # Log feedback for monitoring
        print(f"[Feedback] Rating: {rating}/5 | Page: {feedback_entry['page']} | Time: {feedback_entry['received_at']} | Email: {'Sent' if email_sent else 'Not sent'}")
        
        return jsonify({
            'success': True,
            'message': 'Feedback received. Thank you!',
            'id': feedback_entry['id']
        })
        
    except Exception as e:
        print(f"[Feedback Error] {str(e)}")
        return jsonify({'error': 'Failed to save feedback'}), 500


@app.route('/feedback')
def feedback_page():
    """Render the dedicated feedback form page."""
    return render_template('feedback_form.html')


@app.route('/submit-feedback', methods=['POST'])
def submit_feedback_form():
    """
    Handle feedback form submission from the dedicated feedback page.
    Accepts both JSON and form data.
    
    Request body/form: {
        "rating": int (1-5),
        "feedback": str (optional),
        "page": str (optional)
    }
    """
    try:
        # Handle both JSON and form data
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
        
        if not data:
            if request.is_json:
                return jsonify({'error': 'No data provided'}), 400
            return render_template('feedback_form.html', error='No data provided')
        
        # Get and validate rating
        rating = data.get('rating')
        if isinstance(rating, str):
            try:
                rating = int(rating)
            except ValueError:
                rating = None
        
        if not rating or not isinstance(rating, int) or rating < 1 or rating > 5:
            if request.is_json:
                return jsonify({'error': 'Invalid rating. Must be 1-5.'}), 400
            return render_template('feedback_form.html', error='Please select a rating (1-5 stars)')
        
        # Build feedback entry
        feedback_entry = {
            'id': len(feedback_storage) + 1,
            'rating': rating,
            'feedback': str(data.get('feedback', '')).strip()[:500],
            'page': data.get('page', request.referrer or '/feedback').strip()[:200],
            'user_agent': request.headers.get('User-Agent', ''),
            'timestamp': datetime.now().isoformat(),
            'received_at': datetime.now().isoformat(),
            'ip': request.remote_addr
        }
        
        # Store in memory
        feedback_storage.append(feedback_entry)
        
        # Send email notification
        email_sent = False
        if is_email_configured():
            try:
                email_sent, email_msg = send_feedback_email(feedback_entry)
                if not email_sent:
                    print(f"[Feedback Email Warning] {email_msg}")
            except Exception as email_err:
                print(f"[Feedback Email Error] {email_err}")
        
        # Log feedback
        print(f"[Feedback Form] Rating: {rating}/5 | Page: {feedback_entry['page']} | Email: {'Sent' if email_sent else 'Not sent'}")
        
        # Return success response
        success_message = "Thank you! Your feedback helps us improve Dark Web Leak Monitor."
        
        if request.is_json:
            return jsonify({
                'success': True,
                'message': success_message,
                'id': feedback_entry['id']
            })
        
        return render_template('feedback_form.html', success=True, message=success_message)
        
    except Exception as e:
        print(f"[Feedback Form Error] {str(e)}")
        if request.is_json:
            return jsonify({'error': 'Failed to submit feedback'}), 500
        return render_template('feedback_form.html', error='An error occurred. Please try again.')


@app.route('/api/feedback/stats', methods=['GET'])
def api_feedback_stats():
    """
    Get feedback statistics (admin endpoint).
    """
    try:
        if not feedback_storage:
            return jsonify({
                'total': 0,
                'average_rating': 0,
                'ratings_distribution': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            })
        
        total = len(feedback_storage)
        avg_rating = sum(f['rating'] for f in feedback_storage) / total
        
        distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for f in feedback_storage:
            distribution[f['rating']] += 1
        
        return jsonify({
            'total': total,
            'average_rating': round(avg_rating, 2),
            'ratings_distribution': distribution,
            'recent': feedback_storage[-10:][::-1]  # Last 10, most recent first
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== CHATBOT API ====================

@app.route('/chatbot', methods=['POST'])
def chatbot_api():
    """
    CyberGuard AI chatbot endpoint.
    
    Request body: {"message": "string", "history": [{"role": "user/assistant", "content": "string"}]}
    Response: {"success": bool, "message": "string", "error": "string"}
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        user_message = data.get('message', '')
        conversation_history = data.get('history', [])
        
        if not user_message or not user_message.strip():
            return jsonify({
                'success': False,
                'error': 'Message is required'
            }), 400
        
        # Use class method for queries with conversation history, standalone for simple queries
        if conversation_history:
            result = cybersecurity_chatbot.get_response(
                user_message=user_message,
                conversation_history=conversation_history
            )
            return jsonify(result)
        else:
            response = ask_chatbot(user_message)
            return jsonify({
                'success': True,
                'message': response
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@app.route('/api/chatbot/status', methods=['GET'])
def chatbot_status():
    """Check if chatbot is configured and ready."""
    return jsonify({
        'configured': is_chatbot_configured(),
        'model': 'llama-3.1-8b-instant'
    })


@app.route('/api/chatbot/suggestions', methods=['GET'])
def chatbot_suggestions():
    """Get quick response suggestions for the chatbot."""
    return jsonify({
        'suggestions': cybersecurity_chatbot.get_quick_responses()
    })


@app.route('/ask-ai', methods=['POST'])
def ask_ai():
    """Direct AI endpoint — simple request/response."""
    try:
        data = request.get_json()
        if not data or not data.get('message', '').strip():
            return jsonify({'reply': 'Please provide a message.'}), 400

        user_msg = data['message'].strip()
        reply = ask_chatbot(user_msg)
        return jsonify({'reply': reply})
    except Exception as e:
        return jsonify({'reply': f'Something went wrong. Please try again.'}), 500


# ==================== IP THREAT INTELLIGENCE API ====================

ip_threat_scanner = IPThreatIntelScanner()


@app.route('/api/ip-threat-intel', methods=['POST'])
def api_ip_threat_intel():
    """
    SOC-level IP threat intelligence scan.
    Queries AbuseIPDB, OTX, GreyNoise, Shodan and returns a unified report.
    """
    try:
        data = request.get_json()
        ip = data.get('ip', '').strip()

        if not ip:
            return jsonify({'success': False, 'error': 'IP address is required'}), 400

        if not IPThreatIntelScanner.validate_ip(ip):
            return jsonify({'success': False, 'error': 'Invalid or non-public IP address'}), 400

        report = ip_threat_scanner.scan(ip)
        result = ip_threat_scanner.report_to_dict(report)
        result['success'] = True

        # Log scan to Firestore
        # if current_user.is_authenticated:
        #     summary = f"Risk: {report.risk_score}/100 ({report.threat_level}), Sources: {len(report.sources_queried)}"
        #     log_scan(current_user.id, 'IP Threat Intel', ip, summary, report.risk_score)

        #     # Save to dedicated ip_scans collection
        #     scan_id = str(uuid.uuid4())
        #     db.collection('ip_scans').document(scan_id).set({
        #         'user_id': str(current_user.id),
        #         'ip': ip,
        #         'risk_score': report.risk_score,
        #         'threat_level': report.threat_level,
        #         'timestamp': datetime.now().isoformat(),
        #         'sources': report.sources_queried,
        #     })

        return jsonify(result)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/ip-threat-intel/report', methods=['POST'])
def api_ip_threat_intel_report():
    """Generate a downloadable security report for an IP threat intel scan."""
    try:
        data = request.get_json()
        report_data = data.get('report')
        if not report_data:
            return jsonify({'success': False, 'error': 'Report data is required'}), 400

        ip = report_data.get('ip', 'unknown')
        risk_score = report_data.get('risk_score', 0)
        threat_level = report_data.get('threat_level', 'Unknown')

        html = render_template('ip_threat_intel_report.html', report=report_data)

        # Save report to Firestore
        # if current_user.is_authenticated:
        #     save_security_report(
        #         current_user.id,
        #         'IP Threat Intelligence',
        #         {'ip': ip, 'risk_score': risk_score, 'threat_level': threat_level},
        #         threat_level
        #     )

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'ip_threat_report_{ip.replace(".", "_")}_{timestamp}.html'
        filepath = os.path.join('exports', filename)
        os.makedirs('exports', exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)

        return send_file(filepath, as_attachment=True, download_name=filename)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== LIVE ATTACK MAP API ====================

# In-memory cache for live attacks data
_live_attacks_cache = {
    'data': None,
    'timestamp': None,
    'ttl': 300  # Cache for 5 minutes
}

@app.route('/api/live-attacks', methods=['GET'])
def api_live_attacks():
    """
    Fetch live threat intelligence data from AlienVault OTX.
    Falls back to AbuseIPDB if OTX unavailable.
    Uses in-memory caching to respect API rate limits.
    """
    try:
        # Return cached data if still fresh
        cache = _live_attacks_cache
        if cache['data'] and cache['timestamp']:
            age = (datetime.now() - cache['timestamp']).total_seconds()
            if age < cache['ttl']:
                return jsonify(cache['data'])

        enriched_data = []

        # --- Primary: AlienVault OTX ---
        otx_key = os.getenv('OTX_API_KEY')
        if otx_key:
            try:
                headers = {'X-OTX-API-KEY': otx_key}
                resp = requests.get(
                    'https://otx.alienvault.com/api/v1/pulses/activity',
                    headers=headers,
                    params={'limit': 10, 'modified_since': (datetime.now() - __import__('datetime').timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%S')},
                    timeout=15
                )
                if resp.status_code == 200:
                    pulses = resp.json().get('results', [])
                    seen_ips = set()
                    for pulse in pulses:
                        for indicator in pulse.get('indicators', []):
                            if indicator.get('type') in ('IPv4', 'IPv4Addr') and len(enriched_data) < 60:
                                ip = indicator.get('indicator', '')
                                if ip and ip not in seen_ips:
                                    seen_ips.add(ip)
                                    # Lookup geo for the IP via OTX geo endpoint
                                    try:
                                        geo_resp = requests.get(
                                            f'https://otx.alienvault.com/api/v1/indicators/IPv4/{ip}/geo',
                                            headers=headers, timeout=5
                                        )
                                        if geo_resp.status_code == 200:
                                            geo = geo_resp.json()
                                            lat = geo.get('latitude')
                                            lng = geo.get('longitude')
                                            cc = geo.get('country_code', 'XX')
                                            if lat and lng:
                                                enriched_data.append({
                                                    'ipAddress': ip,
                                                    'countryCode': cc,
                                                    'abuseConfidenceScore': 85,
                                                    'latitude': lat,
                                                    'longitude': lng
                                                })
                                    except Exception:
                                        # Skip this IP if geo lookup fails
                                        cc = 'XX'
                                        coords = get_country_coordinates(cc)
                                        enriched_data.append({
                                            'ipAddress': ip,
                                            'countryCode': cc,
                                            'abuseConfidenceScore': 80,
                                            'latitude': coords['lat'],
                                            'longitude': coords['lng']
                                        })
            except Exception:
                pass  # Fall through to AbuseIPDB

        # --- Fallback: AbuseIPDB if OTX gave few results ---
        if len(enriched_data) < 10:
            abuse_key = os.getenv('ABUSEIPDB_API_KEY')
            if abuse_key:
                try:
                    resp = requests.get(
                        'https://api.abuseipdb.com/api/v2/blacklist',
                        headers={'Key': abuse_key, 'Accept': 'application/json'},
                        params={'confidenceMinimum': 75, 'limit': 100},
                        timeout=15
                    )
                    if resp.status_code == 200:
                        for entry in resp.json().get('data', [])[:50]:
                            ip_address = entry.get('ipAddress')
                            country_code = entry.get('countryCode', 'XX')
                            abuse_score = entry.get('abuseConfidenceScore', 0)
                            coords = get_country_coordinates(country_code)
                            enriched_data.append({
                                'ipAddress': ip_address,
                                'countryCode': country_code,
                                'abuseConfidenceScore': abuse_score,
                                'latitude': coords['lat'],
                                'longitude': coords['lng']
                            })
                except Exception:
                    pass

        if not enriched_data:
            return jsonify({
                'success': False,
                'error': 'No threat data available. APIs may be rate-limited.'
            }), 503

        result = {
            'success': True,
            'data': enriched_data,
            'meta': {
                'totalIPs': len(enriched_data),
                'generatedAt': datetime.now().isoformat()
            }
        }

        # Update cache
        cache['data'] = result
        cache['timestamp'] = datetime.now()

        return jsonify(result)

    except Exception as e:
        if _live_attacks_cache['data']:
            return jsonify(_live_attacks_cache['data'])
        return jsonify({'success': False, 'error': str(e)}), 500


def get_country_coordinates(country_code):
    """
    Get approximate center coordinates for a country code.
    Returns latitude and longitude for the country capital/center.
    """
    # Mapping of country codes to approximate center coordinates
    country_coords = {
        'US': {'lat': 37.0902, 'lng': -95.7129},
        'CN': {'lat': 35.8617, 'lng': 104.1954},
        'RU': {'lat': 61.524, 'lng': 105.3188},
        'DE': {'lat': 51.1657, 'lng': 10.4515},
        'GB': {'lat': 55.3781, 'lng': -3.436},
        'FR': {'lat': 46.2276, 'lng': 2.2137},
        'NL': {'lat': 52.1326, 'lng': 5.2913},
        'BR': {'lat': -14.235, 'lng': -51.9253},
        'IN': {'lat': 20.5937, 'lng': 78.9629},
        'JP': {'lat': 36.2048, 'lng': 138.2529},
        'KR': {'lat': 35.9078, 'lng': 127.7669},
        'AU': {'lat': -25.2744, 'lng': 133.7751},
        'CA': {'lat': 56.1304, 'lng': -106.3468},
        'IT': {'lat': 41.8719, 'lng': 12.5674},
        'ES': {'lat': 40.4637, 'lng': -3.7492},
        'VN': {'lat': 14.0583, 'lng': 108.2772},
        'UA': {'lat': 48.3794, 'lng': 31.1656},
        'PL': {'lat': 51.9194, 'lng': 19.1451},
        'IR': {'lat': 32.4279, 'lng': 53.688},
        'ID': {'lat': -0.7893, 'lng': 113.9213},
        'TH': {'lat': 15.87, 'lng': 100.9925},
        'PH': {'lat': 12.8797, 'lng': 121.774},
        'SG': {'lat': 1.3521, 'lng': 103.8198},
        'MY': {'lat': 4.2105, 'lng': 101.9758},
        'TR': {'lat': 38.9637, 'lng': 35.2433},
        'MX': {'lat': 23.6345, 'lng': -102.5528},
        'AR': {'lat': -38.4161, 'lng': -63.6167},
        'ZA': {'lat': -30.5595, 'lng': 22.9375},
        'EG': {'lat': 26.8206, 'lng': 30.8025},
        'SA': {'lat': 23.8859, 'lng': 45.0792},
        'AE': {'lat': 23.4241, 'lng': 53.8478},
        'HK': {'lat': 22.3193, 'lng': 114.1694},
        'TW': {'lat': 23.6978, 'lng': 120.9605},
        'LT': {'lat': 55.1694, 'lng': 23.8813},
        'BG': {'lat': 42.7339, 'lng': 25.4858},
        'RO': {'lat': 45.9432, 'lng': 24.9668},
        'CZ': {'lat': 49.8175, 'lng': 15.473},
        'SE': {'lat': 60.1282, 'lng': 18.6435},
        'NO': {'lat': 60.472, 'lng': 8.4689},
        'FI': {'lat': 61.9241, 'lng': 25.7482},
        'DK': {'lat': 56.2639, 'lng': 9.5018},
        'AT': {'lat': 47.5162, 'lng': 14.5501},
        'CH': {'lat': 46.8182, 'lng': 8.2275},
        'BE': {'lat': 50.5039, 'lng': 4.4699},
        'PT': {'lat': 39.3999, 'lng': -8.2245},
        'GR': {'lat': 39.0742, 'lng': 21.8243},
        'HU': {'lat': 47.1625, 'lng': 19.5033},
        'IL': {'lat': 31.0461, 'lng': 34.8516},
        'NG': {'lat': 9.082, 'lng': 8.6753},
        'KE': {'lat': -0.0236, 'lng': 37.9062},
        'PK': {'lat': 30.3753, 'lng': 69.3451},
        'BD': {'lat': 23.685, 'lng': 90.3563},
        'CO': {'lat': 4.5709, 'lng': -74.2973},
        'CL': {'lat': -35.6751, 'lng': -71.543},
        'PE': {'lat': -9.19, 'lng': -75.0152},
        'VE': {'lat': 6.4238, 'lng': -66.5897},
        'NZ': {'lat': -40.9006, 'lng': 174.886},
    }
    
    return country_coords.get(country_code, {'lat': 0, 'lng': 0})


PROTECTED_API_VIEWS = (
    'api_check_password',
    'api_check_email',
    'api_generate_password',
    'api_batch_check',
    'api_generate_report',
    'api_export',
    'download_file',
    'api_username_osint',
    'api_username_platforms',
    'api_domain_scan',
    'api_whois_lookup',
    'api_ip_intelligence',
    'api_website_technology_detector',
    'api_ip_quick',
    'api_risk_assessment',
    'api_security_recommendations',
    'api_quick_wins',
    'api_action_plan',
    'api_breach_timeline',
    'api_breach_chart',
    'api_comprehensive_scan',
    'api_generate_quiz',
    'api_quiz_start',
    'api_quiz_submit',
    'api_quiz_certificate',
    'api_hash_generator',
    'api_hash_verify',
    'api_base64',
    'api_url_encoder',
    'api_jwt_decoder',
    'api_password_strength',
    'api_ip_lookup',
    'api_dns_lookup',
    'api_dns_reverse',
    'api_subdomain_finder',
    'api_text_binary',
    'api_rot13',
    'api_tools_list',
    'api_metadata_extract',
    'api_metadata_features',
    'api_live_attacks',
    'api_ip_threat_intel',
    'api_ip_threat_intel_report',
    'api_certificate_history',
    'api_email_certificate'
)

# for view_name in PROTECTED_API_VIEWS:
#     app.view_functions[view_name] = login_required(app.view_functions[view_name])

@app.route("/firebase-test")
def firebase_test():

    db.collection("test").add({
        "name": "Shubham",
        "msg": "Firebase connected"
    })

    return "Firebase working!"

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500


# ==================== RUN ====================

if __name__ == '__main__':
    # Required directories
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs('exports', exist_ok=True)
    
    print("""
╔════════════════════════════════════════════════════════════════════╗
║         🔒 DARK WEB LEAK MONITOR - OSINT PLATFORM v4.0 🔒         ║
╠════════════════════════════════════════════════════════════════════╣
║  Features:                                                         ║
║    • Password Breach Check    • Username OSINT Scanner            ║
║    • Email Breach Check       • Domain Security Scanner           ║
║    • Password Generator       • IP Intelligence                   ║
║    • Batch Processing         • Cyber Risk Assessment             ║
║    • Multi-format Export      • Security Advisor                  ║
║    • PDF Reports              • Breach Timeline Visualization     ║
║    • Cybersecurity Quiz       • PDF Certificates                  ║
╠════════════════════════════════════════════════════════════════════╣
║  Cyber Tools (CyberChef-style):                                    ║
║    • Hash Generator           • IP/DNS Lookup                     ║
║    • Base64 Encoder           • Subdomain Finder                  ║
║    • URL Encoder              • Text/Binary Converter             ║
║    • JWT Decoder              • ROT13/Caesar Cipher               ║
║    • Password Analyzer        • And more...                       ║
╚════════════════════════════════════════════════════════════════════╝
    """)
    print("🌐 Starting web server...")
    print("📍 Open http://localhost:5000 in your browser")
    print("🛑 Press Ctrl+C to stop\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

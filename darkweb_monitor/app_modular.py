import os
from dotenv import load_dotenv
from flask import Flask

# Load environment variables
load_dotenv()

# Import the core settings and extensions
from core.config import Config
from core.extensions import db, login_manager

# Import the blueprints
from routes.auth_routes import auth_bp
from routes.tools_routes import tools_bp
from routes.osint_routes import osint_bp
from routes.learning_routes import learning_bp
from routes.quiz_routes import quiz_bp
from routes.recon_routes import recon_bp
from routes.intel_routes import intel_bp
from routes.ui_routes import ui_bp
from routes.ctf_routes import ctf_bp

def create_modular_app():
    """
    Application Factory for the new V2 Modular architecture.
    Creates a discrete Flask instance that can run independently or be mounted.
    """
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize Extensions
    db.init_app(app)
    login_manager.init_app(app)
    
    # Register V2 Blueprints
    app.register_blueprint(ui_bp, url_prefix='/')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(tools_bp, url_prefix='/tools')
    app.register_blueprint(osint_bp, url_prefix='/osint')
    app.register_blueprint(learning_bp, url_prefix='/learning')
    app.register_blueprint(quiz_bp, url_prefix='/quiz')
    app.register_blueprint(recon_bp, url_prefix='/recon')
    app.register_blueprint(intel_bp, url_prefix='/intel')
    app.register_blueprint(ctf_bp, url_prefix='/ctf')
    
    # Context Processor for global variables
    @app.context_processor
    def inject_global_vars():
        return {
            'platform_version': 'V2.0 Modular'
        }
        
    @app.errorhandler(Exception)
    def handle_exception(e):
        import traceback
        return f"<pre>{traceback.format_exc()}</pre>", 500
        
    # Global template aliases to satisfy the shared navbar.html
    # which hardcodes url_for('index'), url_for('dashboard'), etc.
    @app.route('/')
    def index():
        """Alias for the root to ensure navbar.html 'index' endpoint works in V2 context."""
        from flask import redirect, url_for
        return redirect(url_for('ui_bp.dashboard'))
        
    @app.route('/dashboard')
    def dashboard():
        """Alias for /dashboard to ensure legacy navbar links work in V2 context."""
        from flask import redirect, url_for
        return redirect(url_for('ui_bp.dashboard'))

    @app.route('/login')
    def login_alias():
        """Redirect global login calls to V2 auth."""
        from flask import redirect, url_for
        return redirect(url_for('auth_bp.login'))

    @app.route('/register')
    def register_alias():
        """Redirect global register calls to V2 auth."""
        from flask import redirect, url_for
        return redirect(url_for('auth_bp.register'))

    @app.route('/legacy-gateway/<endpoint>')
    def legacy_gateway(endpoint):
        """Redirects the user from V2 context back to the legacy V1 platform for specific features."""
        from flask import redirect
        # Mapping for the most common legacy endpoints
        endpoint_map = {
            'quiz_page': '/quiz',
            'learning_mode_page': '/learning-mode',
            'certificate_history_page': '/certificate-history',
            'about_page': '/about',
            'tools_hub_page': '/tools',
            'password_check_page': '/password-check',
            'email_check_page': '/email-check',
            'domain_scanner_page': '/domain-scanner',
            'ip_intelligence_page': '/ip-intelligence',
            'risk_assessment_page': '/risk-assessment',
            'ctf_dashboard': '/ctf/'
        }
        target = endpoint_map.get(endpoint, f"/{endpoint.replace('_', '-')}")
        return redirect(target)
        
    # Alias missing endpoints to the legacy gateway
    for missing_endpoint in [
        'tools_hub_page', 'password_check_page', 'email_check_page', 
        'breach_timeline_page', 'username_osint_page', 'ip_intelligence_page',
        'metadata_extractor_page', 'steganography_page', 'domain_scanner_page',
        'whois_lookup_page', 'website_technology_detector_page', 'risk_assessment_page',
        'security_advisor_page', 'attack_map_page', 'ip_threat_intel_page',
        'quiz_page', 'learning_mode_page', 'certificate_history_page', 'about_page',
        'cyber_tools_page', 'generator_page', 'batch_page', 'register', 'login',
        'ctf_dashboard'
    ]:
        app.add_url_rule(f'/v2-redirect/{missing_endpoint}', endpoint=missing_endpoint, view_func=lambda e=missing_endpoint: legacy_gateway(e))

    with app.app_context():
        # Ensure database tables are created when imported by app.py
        db.create_all()

    return app

if __name__ == '__main__':
    # When run directly, operate as a standalone server on port 5001
    # This ensures it doesn't conflict with legacy app.py on 5000
    modular_app = create_modular_app()
        
    print("🚀 Starting V2 Modular Platform on port 5001...")
    modular_app.run(debug=True, port=5001)

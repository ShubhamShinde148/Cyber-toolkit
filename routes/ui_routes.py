from flask import Blueprint, render_template
from utils.helpers import login_required_v2
from services.threat_intel_service import ThreatIntelService

ui_bp = Blueprint('ui_bp', __name__)

@ui_bp.route('/dashboard')
@login_required_v2
def dashboard():
    """Render the new V2 Modular Dashboard landing page with live intel."""
    stats = {
        "health_score": ThreatIntelService.calculate_health_score(),
        "vulnerabilities": ThreatIntelService.get_latest_vulnerabilities(3),
        "leaks": ThreatIntelService.get_darkweb_leaks(2),
        "news": ThreatIntelService.get_cyber_news(3),
        "breach_total": "1.4k", # Static for now
        "active_scans": 3
    }
    return render_template('soc_dashboard.html', stats=stats)

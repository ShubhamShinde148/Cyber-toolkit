from flask import Blueprint, render_template
from utils.helpers import login_required_v2
from services.threat_intel_service import ThreatIntelService

intel_bp = Blueprint('intel_bp', __name__)

@intel_bp.route('/feed')
@login_required_v2
def feed():
    """
    V2 Elite Hub: Displays a comprehensive feed of global threat intelligence.
    """
    vulnerabilities = ThreatIntelService.get_latest_vulnerabilities(limit=10)
    leaks = ThreatIntelService.get_darkweb_leaks(limit=5)
    news = ThreatIntelService.get_cyber_news(limit=5)
    
    return render_template('v2/threat_feed.html', 
                           vulnerabilities=vulnerabilities, 
                           leaks=leaks,
                           news=news)

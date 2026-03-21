from flask import Blueprint, render_template, request, flash, redirect, url_for
from datetime import datetime
from utils.helpers import login_required_v2
from services.threat_intel_service import ThreatIntelService
from services.osint_service import OSINTService
from services.breach_service import BreachService
from services.risk_service import RiskService

recon_bp = Blueprint('recon_bp', __name__)

@recon_bp.route('/master-recon', methods=['GET', 'POST'])
@login_required_v2
def master_recon():
    """
    V2 Elite Tool: Performs a consolidated OSINT scan across multiple services.
    """
    results = None
    target = request.form.get('target', '') if request.method == 'POST' else ''

    if request.method == 'POST' and target:
        osint_svc = OSINTService()
        breach_svc = BreachService()
        risk_svc = RiskService()
        
        is_email = '@' in target
        
        # 1. Breach Check
        if is_email:
            breach_data = breach_svc.check_email(target)
            osint_data = osint_svc.scan_domain(target.split('@')[-1])
        else:
            breach_data = {"is_compromised": False, "breach_count": 0}
            osint_data = osint_svc.scan_domain(target)
            
        # 2. IP / Intel Check (if domain resolved)
        ip = osint_data.get('dns', {}).get('records', {}).get('A', [None])[0]
        ip_intel = osint_svc.scan_ip(ip) if ip else {}
        
        # 3. Consolidate Risk
        risk_report = risk_svc.calculate_full_risk(
            breach_results=breach_data,
            osint_results={**osint_data, **ip_intel, "ip": ip},
            email=target if is_email else None
        )
        
        results = {
            "target": target,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M %p"),
            "risk_level": risk_report['risk_level_display']['label'],
            "risk_score": risk_report['overall_score'],
            "breach_count": breach_data.get('breach_count', 0),
            "whois_status": "Protected" if "@" not in osint_data.get('email', '') else "Exposed",
            "ip_reputation": ip_intel.get('reputation', {}).get('category', 'Unknown'),
            "alerts": [f.get('description', '') for f in risk_report.get('factors', [])],
            "recommendations": risk_report.get('recommendations', [])
        }
        flash(f"Master Recon completed for {target}", "success")

    return render_template('v2/master_recon.html', results=results, target=target)

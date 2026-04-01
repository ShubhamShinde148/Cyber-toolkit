from .cyber_risk_engine import CyberRiskEngine, RiskFactor, RiskCategory

class RiskService:
    """
    Service layer for scoring overall cyber risk.
    Uses the CyberRiskEngine to perform weighted multi-factor analysis.
    """
    
    def __init__(self):
        self.engine = CyberRiskEngine()
        
    def calculate_full_risk(self, breach_results=None, osint_results=None, email=None):
        """
        Calculates a comprehensive risk score based on provided intelligence.
        """
        self.engine.reset()
        
        # Add password breach factors if available
        if breach_results and breach_results.get('is_compromised'):
            self.engine.add_password_breach_risk(breach_results['breach_count'])
            
        # Add email breach factors if available
        if email and breach_results and breach_results.get('breaches'):
            self.engine.add_email_breach_risk(breach_results['breaches'])
            
        # Add domain security factors if available
        if osint_results and osint_results.get('domain'):
            self.engine.add_domain_security_risk(
                osint_results.get('security_score', 50),
                osint_results.get('issues', [])
            )
            
        # Add IP reputation factors if available
        if osint_results and osint_results.get('ip'):
            threats = osint_results.get('threats', {})
            self.engine.add_ip_reputation_risk(
                osint_results.get('reputation', {}).get('score', 100),
                threats.get('risk_factors', []),
                osint_results.get('blacklists', {}).get('is_blacklisted', False)
            )
            
        return self.engine.assess()

    def calculate_simple_score(self, factors):
        """Legacy placeholder logic."""
        return 100 - sum(factors.values()) if factors else 100

"""
Security Recommendation Engine
==============================
Intelligent security advisor that provides personalized recommendations
based on user's security profile and detected vulnerabilities.

Features:
- Context-aware recommendations
- Priority-based action items
- Step-by-step remediation guides
- Security best practices library
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import re


class Priority(Enum):
    """Recommendation priority levels."""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    INFORMATIONAL = 5


class Category(Enum):
    """Recommendation categories."""
    PASSWORD = "password"
    AUTHENTICATION = "authentication"
    PRIVACY = "privacy"
    NETWORK = "network"
    MONITORING = "monitoring"
    RECOVERY = "recovery"
    INFRASTRUCTURE = "infrastructure"
    AWARENESS = "awareness"


@dataclass
class Recommendation:
    """Security recommendation."""
    id: str
    title: str
    description: str
    priority: Priority
    category: Category
    steps: List[str] = field(default_factory=list)
    tools: List[str] = field(default_factory=list)
    time_estimate: str = ""
    difficulty: str = "easy"
    tags: List[str] = field(default_factory=list)


class SecurityAdvisor:
    """
    Intelligent security recommendation engine.
    
    Provides personalized, actionable security recommendations
    based on detected vulnerabilities and security profile.
    """
    
    # Recommendation templates
    RECOMMENDATIONS_DB = {
        # Password Related
        "change_breached_password": Recommendation(
            id="PWD001",
            title="Change Compromised Password Immediately",
            description="Your password has been found in data breaches. Attackers may attempt to use this password on your accounts.",
            priority=Priority.CRITICAL,
            category=Category.PASSWORD,
            steps=[
                "Log into the affected account(s) immediately",
                "Navigate to account settings/security",
                "Change your password to a new, unique password",
                "Use a password with at least 16 characters",
                "Include uppercase, lowercase, numbers, and symbols",
                "Do NOT reuse this password anywhere else"
            ],
            tools=["Bitwarden", "1Password", "LastPass", "KeePassXC"],
            time_estimate="5-10 minutes per account",
            difficulty="easy",
            tags=["breach", "urgent", "password"]
        ),
        
        "use_password_manager": Recommendation(
            id="PWD002",
            title="Start Using a Password Manager",
            description="A password manager generates and securely stores unique passwords for all your accounts, eliminating password reuse.",
            priority=Priority.HIGH,
            category=Category.PASSWORD,
            steps=[
                "Choose a reputable password manager",
                "Create a strong master password (16+ characters)",
                "Install browser extension and mobile app",
                "Import existing passwords from browser",
                "Gradually update accounts with generated passwords",
                "Enable auto-fill for convenience"
            ],
            tools=["Bitwarden (Free)", "1Password", "Dashlane", "NordPass"],
            time_estimate="30 minutes initial setup",
            difficulty="easy",
            tags=["password", "essential"]
        ),
        
        "enable_2fa": Recommendation(
            id="AUTH001",
            title="Enable Two-Factor Authentication",
            description="2FA adds an extra layer of security requiring both your password AND a second factor (like a code from your phone).",
            priority=Priority.HIGH,
            category=Category.AUTHENTICATION,
            steps=[
                "Go to account security settings",
                "Look for 'Two-Factor Authentication' or '2FA'",
                "Choose authenticator app (recommended) or SMS",
                "Scan QR code with authenticator app",
                "Save backup codes in a secure location",
                "Test login with 2FA enabled"
            ],
            tools=["Google Authenticator", "Authy", "Microsoft Authenticator", "YubiKey"],
            time_estimate="5 minutes per account",
            difficulty="easy",
            tags=["authentication", "essential"]
        ),
        
        "use_security_key": Recommendation(
            id="AUTH002",
            title="Use Hardware Security Key",
            description="Hardware security keys provide the strongest protection against phishing and account takeover.",
            priority=Priority.MEDIUM,
            category=Category.AUTHENTICATION,
            steps=[
                "Purchase a FIDO2 compatible security key",
                "Set up the key with your most important accounts",
                "Register at least 2 keys as backup",
                "Store backup key in a secure location",
                "Test login with each key"
            ],
            tools=["YubiKey", "Google Titan", "Thetis", "Feitian"],
            time_estimate="15 minutes per account",
            difficulty="medium",
            tags=["authentication", "advanced"]
        ),
        
        "review_privacy_settings": Recommendation(
            id="PRV001",
            title="Review Social Media Privacy Settings",
            description="Your username was found on multiple platforms. Review privacy settings to limit public exposure.",
            priority=Priority.MEDIUM,
            category=Category.PRIVACY,
            steps=[
                "Review each platform where your profile exists",
                "Set profile to private where appropriate",
                "Remove or limit personal information visible",
                "Disable people search/discovery features",
                "Review connected apps and revoke unnecessary access",
                "Limit who can send you friend/follow requests"
            ],
            tools=["Privacy Checkup (available on most platforms)"],
            time_estimate="10-15 minutes per platform",
            difficulty="easy",
            tags=["privacy", "social"]
        ),
        
        "use_unique_usernames": Recommendation(
            id="PRV002",
            title="Use Different Usernames for Sensitive Accounts",
            description="Using the same username everywhere makes it easier to link your accounts and target you.",
            priority=Priority.LOW,
            category=Category.PRIVACY,
            steps=[
                "Identify sensitive accounts (banking, email, work)",
                "Create unique usernames for these accounts",
                "Consider using email aliases (e.g., user+twitter@email.com)",
                "Document username mappings securely",
                "Update accounts gradually starting with most sensitive"
            ],
            tools=["SimpleLogin", "AnonAddy", "Firefox Relay"],
            time_estimate="5 minutes per account",
            difficulty="easy",
            tags=["privacy", "identity"]
        ),
        
        "implement_email_security": Recommendation(
            id="INF001",
            title="Implement Email Security Records",
            description="Your domain is missing critical email security records (SPF, DKIM, DMARC) that prevent email spoofing.",
            priority=Priority.HIGH,
            category=Category.INFRASTRUCTURE,
            steps=[
                "Access your domain's DNS settings",
                "Add SPF record: v=spf1 include:_spf.google.com ~all",
                "Configure DKIM through your email provider",
                "Add DMARC record: v=DMARC1; p=quarantine; rua=mailto:...",
                "Test configuration with online tools",
                "Monitor DMARC reports"
            ],
            tools=["MXToolbox", "dmarcian", "DMARC Analyzer"],
            time_estimate="30-60 minutes",
            difficulty="medium",
            tags=["email", "domain"]
        ),
        
        "enable_https": Recommendation(
            id="INF002",
            title="Enable HTTPS on Your Domain",
            description="Your website doesn't have HTTPS enabled, making connections vulnerable to interception.",
            priority=Priority.HIGH,
            category=Category.INFRASTRUCTURE,
            steps=[
                "Obtain an SSL certificate (Let's Encrypt is free)",
                "Install certificate on your web server",
                "Update site to use HTTPS URLs",
                "Set up HTTP to HTTPS redirect",
                "Update any hardcoded HTTP links",
                "Enable HSTS for extra security"
            ],
            tools=["Let's Encrypt", "Certbot", "Cloudflare SSL"],
            time_estimate="30 minutes - 2 hours",
            difficulty="medium",
            tags=["ssl", "domain"]
        ),
        
        "monitor_identity": Recommendation(
            id="MON001",
            title="Set Up Identity Monitoring",
            description="Monitor the dark web and breach databases for your personal information.",
            priority=Priority.MEDIUM,
            category=Category.MONITORING,
            steps=[
                "Sign up for Have I Been Pwned notifications",
                "Consider a credit monitoring service",
                "Set up Google Alerts for your name/email",
                "Review credit reports regularly",
                "Enable login notifications on accounts"
            ],
            tools=["Have I Been Pwned", "Firefox Monitor", "Credit Karma"],
            time_estimate="15 minutes",
            difficulty="easy",
            tags=["monitoring", "identity"]
        ),
        
        "backup_recovery_codes": Recommendation(
            id="REC001",
            title="Backup Recovery Codes",
            description="Save backup/recovery codes for all accounts with 2FA in case you lose access to your authenticator.",
            priority=Priority.MEDIUM,
            category=Category.RECOVERY,
            steps=[
                "Log into each account with 2FA enabled",
                "Generate/view backup recovery codes",
                "Print codes or save in encrypted storage",
                "Store in a secure physical location",
                "Consider splitting codes across locations"
            ],
            tools=["Password Manager encrypted notes", "Printed storage"],
            time_estimate="5 minutes per account",
            difficulty="easy",
            tags=["recovery", "2fa"]
        ),
        
        "secure_network": Recommendation(
            id="NET001",
            title="Secure Your Network Connection",
            description="Use secure DNS and consider a VPN for sensitive activities.",
            priority=Priority.LOW,
            category=Category.NETWORK,
            steps=[
                "Use encrypted DNS (1.1.1.1, 8.8.8.8, or DNS-over-HTTPS)",
                "Enable firewall on your router and devices",
                "Use a reputable VPN for sensitive browsing",
                "Avoid public WiFi for sensitive transactions",
                "Keep router firmware updated"
            ],
            tools=["Cloudflare 1.1.1.1", "Mullvad VPN", "ProtonVPN"],
            time_estimate="30 minutes",
            difficulty="medium",
            tags=["network", "vpn"]
        ),
        
        "security_awareness": Recommendation(
            id="AWR001",
            title="Learn to Recognize Phishing",
            description="Phishing is the #1 way accounts get compromised. Learn to spot suspicious emails and links.",
            priority=Priority.LOW,
            category=Category.AWARENESS,
            steps=[
                "Verify sender email addresses carefully",
                "Hover over links before clicking",
                "Never enter credentials from email links",
                "Be suspicious of urgency/threats",
                "When in doubt, go directly to the site",
                "Report suspected phishing attempts"
            ],
            tools=["PhishMe training", "KnowBe4"],
            time_estimate="Ongoing awareness",
            difficulty="easy",
            tags=["awareness", "phishing"]
        )
    }
    
    def __init__(self):
        """Initialize the security advisor."""
        self.context: Dict = {}
        self.triggered_recommendations: List[str] = []
    
    def set_context(self, context: Dict):
        """
        Set security context for personalized recommendations.
        
        Args:
            context: Dictionary with security profile data
        """
        self.context = context
    
    def _evaluate_triggers(self) -> List[str]:
        """
        Evaluate which recommendations should trigger based on context.
        
        Returns:
            List of recommendation IDs to include
        """
        triggered = []
        
        # Password breach triggers
        if self.context.get('password_breached'):
            triggered.append('change_breached_password')
        
        if self.context.get('password_breach_count', 0) > 0:
            triggered.append('change_breached_password')
            triggered.append('use_password_manager')
        
        # Weak password
        if self.context.get('password_strength', 100) < 60:
            triggered.append('use_password_manager')
        
        # Email breaches
        if self.context.get('email_breach_count', 0) > 0:
            triggered.append('enable_2fa')
            triggered.append('use_password_manager')
            triggered.append('monitor_identity')
        
        # Username exposure
        if self.context.get('username_platforms_found', 0) > 5:
            triggered.append('review_privacy_settings')
            triggered.append('use_unique_usernames')
        
        # Domain security
        if not self.context.get('has_spf', True):
            triggered.append('implement_email_security')
        
        if not self.context.get('has_https', True):
            triggered.append('enable_https')
        
        # IP reputation
        if self.context.get('ip_threat_level') in ['high', 'critical']:
            triggered.append('secure_network')
        
        # General recommendations always included at lower priority
        if 'enable_2fa' not in triggered and not self.context.get('has_2fa'):
            triggered.append('enable_2fa')
        
        if 'use_password_manager' not in triggered and not self.context.get('uses_password_manager'):
            triggered.append('use_password_manager')
        
        # Always include awareness
        triggered.append('security_awareness')
        triggered.append('backup_recovery_codes')
        
        return list(set(triggered))  # Remove duplicates
    
    def get_recommendations(self, max_count: int = 10) -> Dict:
        """
        Get personalized security recommendations.
        
        Args:
            max_count: Maximum number of recommendations to return
            
        Returns:
            Dictionary with recommendations
        """
        triggered_ids = self._evaluate_triggers()
        
        recommendations = []
        for rec_id in triggered_ids:
            if rec_id in self.RECOMMENDATIONS_DB:
                rec = self.RECOMMENDATIONS_DB[rec_id]
                recommendations.append({
                    'id': rec.id,
                    'title': rec.title,
                    'description': rec.description,
                    'priority': rec.priority.value,
                    'priority_label': rec.priority.name,
                    'category': rec.category.value,
                    'steps': rec.steps,
                    'tools': rec.tools,
                    'time_estimate': rec.time_estimate,
                    'difficulty': rec.difficulty,
                    'tags': rec.tags
                })
        
        # Sort by priority (lower number = higher priority)
        recommendations.sort(key=lambda x: x['priority'])
        
        # Limit count
        recommendations = recommendations[:max_count]
        
        # Group by category
        by_category = {}
        for rec in recommendations:
            cat = rec['category']
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(rec)
        
        # Get priority counts
        priority_counts = {
            'critical': len([r for r in recommendations if r['priority'] == 1]),
            'high': len([r for r in recommendations if r['priority'] == 2]),
            'medium': len([r for r in recommendations if r['priority'] == 3]),
            'low': len([r for r in recommendations if r['priority'] == 4]),
            'informational': len([r for r in recommendations if r['priority'] == 5])
        }
        
        return {
            'success': True,
            'total_recommendations': len(recommendations),
            'recommendations': recommendations,
            'by_category': by_category,
            'priority_summary': priority_counts,
            'generated_at': datetime.now().isoformat(),
            'context_used': list(self.context.keys())
        }
    
    def get_recommendation_by_id(self, rec_id: str) -> Optional[Dict]:
        """
        Get a specific recommendation by ID.
        
        Args:
            rec_id: Recommendation ID
            
        Returns:
            Recommendation dictionary or None
        """
        for key, rec in self.RECOMMENDATIONS_DB.items():
            if rec.id == rec_id:
                return {
                    'id': rec.id,
                    'title': rec.title,
                    'description': rec.description,
                    'priority': rec.priority.value,
                    'priority_label': rec.priority.name,
                    'category': rec.category.value,
                    'steps': rec.steps,
                    'tools': rec.tools,
                    'time_estimate': rec.time_estimate,
                    'difficulty': rec.difficulty,
                    'tags': rec.tags
                }
        return None
    
    def get_quick_wins(self) -> List[Dict]:
        """
        Get quick win recommendations that are easy and high-impact.
        
        Returns:
            List of quick win recommendations
        """
        quick_wins = []
        
        for key, rec in self.RECOMMENDATIONS_DB.items():
            if rec.difficulty == "easy" and rec.priority.value <= 2:
                quick_wins.append({
                    'id': rec.id,
                    'title': rec.title,
                    'time_estimate': rec.time_estimate,
                    'impact': 'high' if rec.priority.value == 1 else 'medium'
                })
        
        return quick_wins[:5]
    
    def generate_action_plan(self, timeframe: str = "week") -> Dict:
        """
        Generate a prioritized action plan.
        
        Args:
            timeframe: 'day', 'week', or 'month'
            
        Returns:
            Structured action plan
        """
        all_recs = self.get_recommendations(max_count=20)['recommendations']
        
        if timeframe == "day":
            plan_recs = [r for r in all_recs if r['priority'] <= 2][:3]
            title = "Today's Security Actions"
        elif timeframe == "week":
            plan_recs = [r for r in all_recs if r['priority'] <= 3][:7]
            title = "This Week's Security Plan"
        else:  # month
            plan_recs = all_recs[:15]
            title = "Monthly Security Improvement Plan"
        
        return {
            'title': title,
            'timeframe': timeframe,
            'total_actions': len(plan_recs),
            'actions': [
                {
                    'day': i + 1,
                    'task': rec['title'],
                    'priority': rec['priority_label'],
                    'time_needed': rec['time_estimate'],
                    'category': rec['category']
                }
                for i, rec in enumerate(plan_recs)
            ],
            'total_time_estimate': f"Approximately {len(plan_recs) * 15}-{len(plan_recs) * 30} minutes"
        }
    
    def get_all_recommendations(self) -> List[Dict]:
        """Get all available recommendations."""
        return [
            {
                'id': rec.id,
                'title': rec.title,
                'category': rec.category.value,
                'priority': rec.priority.name,
                'difficulty': rec.difficulty
            }
            for rec in self.RECOMMENDATIONS_DB.values()
        ]


# Example usage
if __name__ == "__main__":
    advisor = SecurityAdvisor()
    
    print("=" * 60)
    print("Security Recommendation Engine - Test")
    print("=" * 60)
    
    # Set context with vulnerabilities
    advisor.set_context({
        'password_breached': True,
        'password_breach_count': 500,
        'password_strength': 45,
        'email_breach_count': 3,
        'username_platforms_found': 8,
        'has_https': False,
        'has_spf': False,
        'has_2fa': False,
        'uses_password_manager': False
    })
    
    # Get recommendations
    results = advisor.get_recommendations()
    
    print(f"\nTotal Recommendations: {results['total_recommendations']}")
    print(f"Critical: {results['priority_summary']['critical']}")
    print(f"High: {results['priority_summary']['high']}")
    
    print("\nTop Recommendations:")
    for rec in results['recommendations'][:5]:
        print(f"\n[{rec['priority_label']}] {rec['title']}")
        print(f"   Category: {rec['category']}")
        print(f"   Time: {rec['time_estimate']}")
        print(f"   Steps: {len(rec['steps'])} actions")
    
    print("\n\nQuick Wins:")
    for qw in advisor.get_quick_wins():
        print(f"  • {qw['title']} ({qw['time_estimate']})")

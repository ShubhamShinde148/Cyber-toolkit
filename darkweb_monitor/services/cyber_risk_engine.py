"""
Cyber Risk Score Engine
=======================
Comprehensive risk scoring engine that aggregates data from all OSINT modules
to provide a unified cyber risk assessment.

Features:
- Multi-factor risk calculation
- Historical trending
- Category-based scoring
- Risk mitigation suggestions
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import math


class RiskCategory(Enum):
    """Risk assessment categories."""
    CREDENTIAL = "credential"
    IDENTITY = "identity"
    INFRASTRUCTURE = "infrastructure"
    REPUTATION = "reputation"
    EXPOSURE = "exposure"


class RiskLevel(Enum):
    """Risk severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MINIMAL = "minimal"


@dataclass
class RiskFactor:
    """Individual risk factor."""
    name: str
    category: RiskCategory
    score: float  # 0-100
    weight: float  # 0-1
    description: str
    evidence: List[str] = field(default_factory=list)
    mitigations: List[str] = field(default_factory=list)


@dataclass
class RiskAssessment:
    """Complete risk assessment result."""
    overall_score: float
    risk_level: RiskLevel
    factors: List[RiskFactor]
    recommendations: List[str]
    timestamp: datetime


class CyberRiskEngine:
    """
    Advanced cyber risk scoring engine.
    
    Aggregates multiple data sources to calculate comprehensive
    risk scores with actionable insights.
    
    Scoring Methodology:
    - Weighted factor aggregation
    - Category-based analysis
    - Evidence-based scoring
    - Risk decay over time
    """
    
    # Category weights for overall score calculation
    CATEGORY_WEIGHTS = {
        RiskCategory.CREDENTIAL: 0.30,      # Password breaches, weak passwords
        RiskCategory.IDENTITY: 0.25,        # Personal info exposure
        RiskCategory.INFRASTRUCTURE: 0.20,  # Domain/IP security
        RiskCategory.REPUTATION: 0.15,      # Online presence risks
        RiskCategory.EXPOSURE: 0.10         # Data exposure level
    }
    
    # Risk level thresholds
    RISK_THRESHOLDS = {
        RiskLevel.CRITICAL: 80,
        RiskLevel.HIGH: 60,
        RiskLevel.MEDIUM: 40,
        RiskLevel.LOW: 20,
        RiskLevel.MINIMAL: 0
    }
    
    def __init__(self):
        """Initialize the risk engine."""
        self.factors: List[RiskFactor] = []
        self.history: List[RiskAssessment] = []
    
    def reset(self):
        """Reset all risk factors for new assessment."""
        self.factors = []
    
    def add_factor(self, factor: RiskFactor):
        """
        Add a risk factor to the assessment.
        
        Args:
            factor: RiskFactor to add
        """
        self.factors.append(factor)
    
    def add_password_breach_risk(self, breach_count: int, passwords_compromised: int = 0):
        """
        Add risk factor for password breaches.
        
        Args:
            breach_count: Number of times password found in breaches
            passwords_compromised: Number of unique passwords compromised
        """
        if breach_count == 0:
            return
        
        # Calculate score based on breach severity
        base_score = min(100, 20 + (math.log10(breach_count + 1) * 30))
        
        if passwords_compromised > 1:
            base_score = min(100, base_score + (passwords_compromised * 5))
        
        evidence = [
            f"Password found in {breach_count:,} breach records",
        ]
        
        if passwords_compromised > 0:
            evidence.append(f"{passwords_compromised} password(s) compromised")
        
        mitigations = [
            "Change compromised password immediately",
            "Enable two-factor authentication",
            "Use a password manager for unique passwords",
            "Consider a security key for critical accounts"
        ]
        
        if breach_count > 100:
            mitigations.insert(0, "URGENT: Password widely exposed - change NOW")
        
        self.add_factor(RiskFactor(
            name="Password Breach Exposure",
            category=RiskCategory.CREDENTIAL,
            score=base_score,
            weight=0.9,
            description=f"Password found in {breach_count:,} known data breaches",
            evidence=evidence,
            mitigations=mitigations
        ))
    
    def add_email_breach_risk(self, breaches: List[Dict]):
        """
        Add risk factor for email breaches.
        
        Args:
            breaches: List of breach records
        """
        if not breaches:
            return
        
        breach_count = len(breaches)
        
        # Calculate score based on breach count and severity
        base_score = min(100, 15 + (breach_count * 8))
        
        # Check for sensitive breaches
        sensitive_breaches = [
            b for b in breaches 
            if b.get('IsSensitive') or b.get('DataClasses', [])
        ]
        
        if sensitive_breaches:
            base_score = min(100, base_score + (len(sensitive_breaches) * 5))
        
        evidence = [
            f"Email found in {breach_count} data breach(es)",
        ]
        
        # List recent breaches
        for breach in breaches[:5]:
            evidence.append(f"- {breach.get('Name', 'Unknown')} ({breach.get('BreachDate', 'Unknown date')})")
        
        if len(breaches) > 5:
            evidence.append(f"- ... and {len(breaches) - 5} more")
        
        mitigations = [
            "Change passwords for affected services",
            "Enable 2FA on all breached accounts",
            "Monitor accounts for suspicious activity",
            "Consider identity monitoring services"
        ]
        
        self.add_factor(RiskFactor(
            name="Email Breach Exposure",
            category=RiskCategory.IDENTITY,
            score=base_score,
            weight=0.85,
            description=f"Email address found in {breach_count} known breaches",
            evidence=evidence,
            mitigations=mitigations
        ))
    
    def add_username_exposure_risk(self, platforms_found: int, total_checked: int):
        """
        Add risk factor for username exposure across platforms.
        
        Args:
            platforms_found: Number of platforms where username was found
            total_checked: Total platforms checked
        """
        if platforms_found == 0:
            return
        
        exposure_ratio = platforms_found / total_checked if total_checked > 0 else 0
        
        # Higher exposure = higher risk (but not always bad)
        base_score = min(100, platforms_found * 3)
        
        # Adjust based on exposure ratio
        if exposure_ratio > 0.5:
            base_score = min(100, base_score + 15)
        
        evidence = [
            f"Username found on {platforms_found} of {total_checked} platforms",
            f"Exposure ratio: {exposure_ratio:.1%}"
        ]
        
        mitigations = [
            "Use different usernames for sensitive accounts",
            "Review privacy settings on each platform",
            "Consider using aliases for non-essential services",
            "Enable login notifications where available"
        ]
        
        self.add_factor(RiskFactor(
            name="Username Exposure",
            category=RiskCategory.EXPOSURE,
            score=base_score,
            weight=0.6,
            description=f"Username is publicly discoverable on {platforms_found} platforms",
            evidence=evidence,
            mitigations=mitigations
        ))
    
    def add_domain_security_risk(self, security_score: int, issues: List[str]):
        """
        Add risk factor for domain security issues.
        
        Args:
            security_score: Domain security score (0-100)
            issues: List of security issues found
        """
        # Invert score - lower security = higher risk
        risk_score = max(0, 100 - security_score)
        
        if not issues and security_score >= 80:
            return  # Low risk, skip
        
        evidence = [f"Domain security score: {security_score}/100"]
        evidence.extend([f"- {issue}" for issue in issues])
        
        mitigations = [
            "Implement missing email security records (SPF, DKIM, DMARC)",
            "Ensure HTTPS is properly configured",
            "Enable HTTP to HTTPS redirect",
            "Consider DNSSEC implementation"
        ]
        
        self.add_factor(RiskFactor(
            name="Domain Security",
            category=RiskCategory.INFRASTRUCTURE,
            score=risk_score,
            weight=0.7,
            description=f"Domain has {len(issues)} security issues",
            evidence=evidence,
            mitigations=mitigations
        ))
    
    def add_ip_reputation_risk(self, reputation_score: int, threat_factors: List[str], 
                                is_blacklisted: bool):
        """
        Add risk factor for IP reputation.
        
        Args:
            reputation_score: IP reputation score (0-100)
            threat_factors: List of threat indicators
            is_blacklisted: Whether IP is blacklisted
        """
        # Invert score - lower reputation = higher risk
        risk_score = max(0, 100 - reputation_score)
        
        if is_blacklisted:
            risk_score = min(100, risk_score + 30)
        
        if risk_score < 20 and not threat_factors:
            return  # Low risk, skip
        
        evidence = [f"IP reputation score: {reputation_score}/100"]
        
        if is_blacklisted:
            evidence.append("⚠️ IP is blacklisted")
        
        evidence.extend([f"- {factor}" for factor in threat_factors])
        
        mitigations = [
            "Check for malware or compromised systems",
            "Review outbound traffic patterns",
            "Contact ISP if blacklisted incorrectly",
            "Consider using a reputable VPN for sensitive activities"
        ]
        
        self.add_factor(RiskFactor(
            name="IP Reputation",
            category=RiskCategory.REPUTATION,
            score=risk_score,
            weight=0.65,
            description=f"Network has reputation concerns",
            evidence=evidence,
            mitigations=mitigations
        ))
    
    def add_weak_password_risk(self, strength_score: int, issues: List[str]):
        """
        Add risk factor for weak password.
        
        Args:
            strength_score: Password strength (0-100)
            issues: List of password weaknesses
        """
        # Invert strength - lower strength = higher risk
        risk_score = max(0, 100 - strength_score)
        
        if strength_score >= 80:
            return  # Strong password, no risk
        
        evidence = [f"Password strength: {strength_score}/100"]
        evidence.extend([f"- {issue}" for issue in issues])
        
        mitigations = [
            "Use a longer password (minimum 12 characters)",
            "Include uppercase, lowercase, numbers, and symbols",
            "Avoid common words and patterns",
            "Use a password manager to generate strong passwords"
        ]
        
        self.add_factor(RiskFactor(
            name="Weak Password",
            category=RiskCategory.CREDENTIAL,
            score=risk_score,
            weight=0.8,
            description="Current password does not meet security standards",
            evidence=evidence,
            mitigations=mitigations
        ))
    
    def calculate_category_scores(self) -> Dict[RiskCategory, float]:
        """
        Calculate risk scores per category.
        
        Returns:
            Dictionary mapping categories to scores
        """
        category_scores = {cat: [] for cat in RiskCategory}
        
        for factor in self.factors:
            weighted_score = factor.score * factor.weight
            category_scores[factor.category].append(weighted_score)
        
        # Average scores per category
        result = {}
        for category, scores in category_scores.items():
            if scores:
                result[category] = sum(scores) / len(scores)
            else:
                result[category] = 0
        
        return result
    
    def calculate_overall_score(self) -> float:
        """
        Calculate weighted overall risk score.
        
        Returns:
            Overall risk score (0-100)
        """
        if not self.factors:
            return 0
        
        category_scores = self.calculate_category_scores()
        
        overall = 0
        total_weight = 0
        
        for category, weight in self.CATEGORY_WEIGHTS.items():
            if category in category_scores and category_scores[category] > 0:
                overall += category_scores[category] * weight
                total_weight += weight
        
        if total_weight > 0:
            overall = overall / total_weight * (total_weight / sum(self.CATEGORY_WEIGHTS.values()))
        
        return min(100, max(0, overall))
    
    def determine_risk_level(self, score: float) -> RiskLevel:
        """
        Determine risk level from score.
        
        Args:
            score: Risk score (0-100)
            
        Returns:
            RiskLevel enum value
        """
        for level, threshold in sorted(self.RISK_THRESHOLDS.items(), 
                                        key=lambda x: x[1], reverse=True):
            if score >= threshold:
                return level
        
        return RiskLevel.MINIMAL
    
    def generate_recommendations(self) -> List[str]:
        """
        Generate prioritized recommendations based on risk factors.
        
        Returns:
            List of prioritized recommendations
        """
        all_mitigations = []
        
        # Collect mitigations from high-scoring factors
        sorted_factors = sorted(self.factors, key=lambda x: x.score * x.weight, reverse=True)
        
        for factor in sorted_factors[:5]:  # Top 5 risk factors
            for mitigation in factor.mitigations:
                if mitigation not in all_mitigations:
                    all_mitigations.append(mitigation)
        
        # Add urgency prefix for critical items
        recommendations = []
        for i, rec in enumerate(all_mitigations[:10]):
            if i == 0 and sorted_factors and sorted_factors[0].score >= 70:
                recommendations.append(f"🔴 CRITICAL: {rec}")
            elif i < 3:
                recommendations.append(f"🟠 HIGH: {rec}")
            else:
                recommendations.append(f"🟡 {rec}")
        
        return recommendations
    
    def assess(self) -> Dict:
        """
        Perform complete risk assessment.
        
        Returns:
            Dictionary with assessment results
        """
        overall_score = self.calculate_overall_score()
        risk_level = self.determine_risk_level(overall_score)
        category_scores = self.calculate_category_scores()
        recommendations = self.generate_recommendations()
        
        # Store in history
        assessment = RiskAssessment(
            overall_score=overall_score,
            risk_level=risk_level,
            factors=self.factors.copy(),
            recommendations=recommendations,
            timestamp=datetime.now()
        )
        self.history.append(assessment)
        
        # Build response
        return {
            'success': True,
            'overall_score': round(overall_score, 1),
            'risk_level': risk_level.value,
            'risk_level_display': self._format_risk_level(risk_level),
            'category_scores': {
                cat.value: round(score, 1) 
                for cat, score in category_scores.items()
            },
            'factors': [
                {
                    'name': f.name,
                    'category': f.category.value,
                    'score': round(f.score, 1),
                    'description': f.description,
                    'evidence': f.evidence,
                    'mitigations': f.mitigations
                }
                for f in sorted(self.factors, key=lambda x: x.score, reverse=True)
            ],
            'total_factors': len(self.factors),
            'recommendations': recommendations,
            'assessed_at': datetime.now().isoformat(),
            'summary': self._generate_summary(overall_score, risk_level)
        }
    
    def _format_risk_level(self, level: RiskLevel) -> Dict:
        """Format risk level for display."""
        formats = {
            RiskLevel.CRITICAL: {
                'label': 'CRITICAL',
                'color': '#ff0000',
                'icon': '🔴',
                'description': 'Immediate action required'
            },
            RiskLevel.HIGH: {
                'label': 'HIGH',
                'color': '#ff6600',
                'icon': '🟠',
                'description': 'Significant risks identified'
            },
            RiskLevel.MEDIUM: {
                'label': 'MEDIUM',
                'color': '#ffcc00',
                'icon': '🟡',
                'description': 'Moderate risks present'
            },
            RiskLevel.LOW: {
                'label': 'LOW',
                'color': '#00cc00',
                'icon': '🟢',
                'description': 'Minor concerns only'
            },
            RiskLevel.MINIMAL: {
                'label': 'MINIMAL',
                'color': '#00ff88',
                'icon': '✅',
                'description': 'No significant risks detected'
            }
        }
        return formats.get(level, formats[RiskLevel.MINIMAL])
    
    def _generate_summary(self, score: float, level: RiskLevel) -> str:
        """Generate human-readable summary."""
        if level == RiskLevel.CRITICAL:
            return f"Your cyber risk score is {score:.0f}/100 (CRITICAL). Multiple serious security issues require immediate attention."
        elif level == RiskLevel.HIGH:
            return f"Your cyber risk score is {score:.0f}/100 (HIGH). Significant vulnerabilities have been identified."
        elif level == RiskLevel.MEDIUM:
            return f"Your cyber risk score is {score:.0f}/100 (MEDIUM). Some security improvements are recommended."
        elif level == RiskLevel.LOW:
            return f"Your cyber risk score is {score:.0f}/100 (LOW). Your security posture is generally good."
        else:
            return f"Your cyber risk score is {score:.0f}/100 (MINIMAL). Your security profile looks excellent."
    
    def get_trend(self) -> Dict:
        """
        Get risk score trend from history.
        
        Returns:
            Dictionary with trend data
        """
        if len(self.history) < 2:
            return {
                'available': False,
                'message': 'Not enough data for trend analysis'
            }
        
        recent = self.history[-5:]
        scores = [a.overall_score for a in recent]
        
        avg = sum(scores) / len(scores)
        latest = scores[-1]
        previous = scores[-2]
        
        change = latest - previous
        trend = 'stable'
        
        if change > 5:
            trend = 'worsening'
        elif change < -5:
            trend = 'improving'
        
        return {
            'available': True,
            'current_score': latest,
            'previous_score': previous,
            'change': change,
            'trend': trend,
            'average': avg,
            'history': [
                {
                    'score': a.overall_score,
                    'level': a.risk_level.value,
                    'timestamp': a.timestamp.isoformat()
                }
                for a in recent
            ]
        }


# Example usage  
if __name__ == "__main__":
    engine = CyberRiskEngine()
    
    print("=" * 60)
    print("Cyber Risk Score Engine - Test")
    print("=" * 60)
    
    # Simulate risk factors
    engine.add_password_breach_risk(breach_count=1500, passwords_compromised=2)
    engine.add_email_breach_risk([
        {'Name': 'Adobe', 'BreachDate': '2013-10-04'},
        {'Name': 'LinkedIn', 'BreachDate': '2016-05-18'},
        {'Name': 'Dropbox', 'BreachDate': '2012-07-01'}
    ])
    engine.add_username_exposure_risk(platforms_found=12, total_checked=25)
    engine.add_weak_password_risk(strength_score=45, issues=[
        'Password too short',
        'Missing special characters'
    ])
    
    # Perform assessment
    results = engine.assess()
    
    print(f"\nOverall Risk Score: {results['overall_score']}/100")
    print(f"Risk Level: {results['risk_level_display']['icon']} {results['risk_level_display']['label']}")
    print(f"\n{results['summary']}")
    
    print("\nCategory Scores:")
    for category, score in results['category_scores'].items():
        print(f"  {category}: {score}")
    
    print("\nTop Recommendations:")
    for rec in results['recommendations'][:5]:
        print(f"  {rec}")

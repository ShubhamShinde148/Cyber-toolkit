"""
Risk Analyzer Module
Provides comprehensive risk assessment for compromised credentials.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class RiskLevel(Enum):
    """Risk level classifications."""
    SAFE = "SAFE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class RiskAssessment:
    """Comprehensive risk assessment result."""
    level: RiskLevel
    score: int  # 0-100
    breach_count: int
    recommendations: list
    color: str  # For UI/reporting


class RiskAnalyzer:
    """Analyzes breach data to determine risk level."""
    
    # Breach count thresholds
    THRESHOLDS = {
        'critical': 100000,
        'high': 10000,
        'medium': 1000,
        'low': 1
    }
    
    # Risk colors for reporting
    COLORS = {
        RiskLevel.SAFE: '#2ecc71',      # Green
        RiskLevel.LOW: '#27ae60',        # Dark Green
        RiskLevel.MEDIUM: '#f39c12',     # Orange
        RiskLevel.HIGH: '#e74c3c',       # Red
        RiskLevel.CRITICAL: '#8e44ad'    # Purple
    }
    
    def analyze(self, breach_count: int, password_strength: Optional[dict] = None) -> RiskAssessment:
        """
        Perform comprehensive risk analysis.
        
        Args:
            breach_count: Number of times password found in breaches
            password_strength: Optional dict with strength metrics
        """
        # Convert to int if string
        if isinstance(breach_count, str):
            breach_count = int(breach_count) if breach_count.isdigit() else 0
        
        # Determine risk level based on breach count
        if breach_count == 0:
            level = RiskLevel.SAFE
            score = 0
        elif breach_count < self.THRESHOLDS['low']:
            level = RiskLevel.LOW
            score = 20
        elif breach_count < self.THRESHOLDS['medium']:
            level = RiskLevel.LOW
            score = 30
        elif breach_count < self.THRESHOLDS['high']:
            level = RiskLevel.MEDIUM
            score = 50
        elif breach_count < self.THRESHOLDS['critical']:
            level = RiskLevel.HIGH
            score = 75
        else:
            level = RiskLevel.CRITICAL
            score = 100
        
        # Adjust score based on password strength if provided
        if password_strength and not password_strength.get('is_strong', True):
            score = min(100, score + 10)
            if level == RiskLevel.SAFE:
                level = RiskLevel.LOW
        
        recommendations = self._generate_recommendations(level, breach_count, password_strength)
        
        return RiskAssessment(
            level=level,
            score=score,
            breach_count=breach_count,
            recommendations=recommendations,
            color=self.COLORS[level]
        )
    
    def _generate_recommendations(
        self, 
        level: RiskLevel, 
        breach_count: int,
        password_strength: Optional[dict]
    ) -> list:
        """Generate actionable security recommendations."""
        recommendations = []
        
        if level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            recommendations.extend([
                "🚨 IMMEDIATE ACTION REQUIRED: Change this password NOW",
                "Enable two-factor authentication on all accounts",
                "Check for unauthorized access to your accounts",
                "Consider using a password manager"
            ])
        elif level == RiskLevel.MEDIUM:
            recommendations.extend([
                "⚠️ Change this password soon",
                "Enable two-factor authentication",
                "Use a unique password for each account"
            ])
        elif level == RiskLevel.LOW:
            recommendations.extend([
                "Consider changing this password as a precaution",
                "Ensure this password is unique to one account"
            ])
        else:
            recommendations.append("✅ This password was not found in known breaches")
        
        # Add strength-based recommendations
        if password_strength:
            if not password_strength.get('has_special'):
                recommendations.append("Add special characters (!@#$%^&*)")
            if not password_strength.get('has_digit'):
                recommendations.append("Add numbers to strengthen password")
            if password_strength.get('length', 0) < 12:
                recommendations.append("Use at least 12 characters")
        
        return recommendations


# Legacy function for backward compatibility
def analyze_risk(breaches) -> str:
    """Legacy wrapper - returns risk level as string."""
    # Fix the bug: breaches might be string or int, not a list
    if isinstance(breaches, str):
        breach_count = int(breaches) if breaches.isdigit() else 0
    elif isinstance(breaches, int):
        breach_count = breaches
    else:
        breach_count = 0
    
    analyzer = RiskAnalyzer()
    result = analyzer.analyze(breach_count)
    return result.level.value

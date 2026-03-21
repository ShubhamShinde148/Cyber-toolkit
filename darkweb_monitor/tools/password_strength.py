"""
Password Strength Analyzer Tool
Analyze password strength with detailed feedback.
"""

import re
import math
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class StrengthLevel(Enum):
    """Password strength levels."""
    VERY_WEAK = "Very Weak"
    WEAK = "Weak"
    FAIR = "Fair"
    STRONG = "Strong"
    VERY_STRONG = "Very Strong"


@dataclass
class PasswordAnalysis:
    """Result of password strength analysis."""
    password_length: int
    strength_level: StrengthLevel
    strength_score: int  # 0-100
    entropy_bits: float
    crack_time_display: str
    crack_time_seconds: float
    
    has_uppercase: bool
    has_lowercase: bool
    has_digits: bool
    has_special: bool
    has_repeated: bool
    has_sequential: bool
    has_common_pattern: bool
    
    checks_passed: List[str]
    checks_failed: List[str]
    suggestions: List[str]
    
    char_diversity: int
    unique_chars: int


class PasswordStrengthAnalyzer:
    """Analyze password strength with detailed feedback."""
    
    # Common weak passwords and patterns
    COMMON_PASSWORDS = {
        'password', '123456', '12345678', 'qwerty', 'abc123', 'monkey', 
        'password1', 'iloveyou', 'admin', 'welcome', 'login', 'princess',
        'letmein', 'sunshine', 'master', 'dragon', 'passw0rd', 'shadow',
        'michael', 'football', 'batman', 'trustno1', '111111', '123123'
    }
    
    KEYBOARD_PATTERNS = [
        'qwerty', 'asdfgh', 'zxcvbn', 'qazwsx', '1qaz2wsx',
        'qwertyuiop', 'asdfghjkl', 'zxcvbnm'
    ]
    
    SEQUENTIAL_PATTERNS = [
        '0123456789', 'abcdefghijklmnopqrstuvwxyz',
        '9876543210', 'zyxwvutsrqponmlkjihgfedcba'
    ]
    
    def __init__(self):
        pass
    
    def analyze(self, password: str) -> PasswordAnalysis:
        """
        Perform comprehensive password strength analysis.
        
        Args:
            password: Password to analyze
            
        Returns:
            PasswordAnalysis with detailed results
        """
        length = len(password)
        
        # Character type checks
        has_upper = bool(re.search(r'[A-Z]', password))
        has_lower = bool(re.search(r'[a-z]', password))
        has_digit = bool(re.search(r'\d', password))
        has_special = bool(re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?`~]', password))
        
        # Pattern detection
        has_repeated = self._has_repeated_chars(password)
        has_sequential = self._has_sequential_chars(password)
        has_common = self._has_common_pattern(password)
        
        # Character diversity
        unique_chars = len(set(password))
        char_diversity = self._calculate_char_pool_size(password)
        
        # Calculate entropy
        entropy = self._calculate_entropy(password, char_diversity)
        
        # Calculate crack time
        crack_seconds = self._estimate_crack_time(password, entropy)
        crack_display = self._format_crack_time(crack_seconds)
        
        # Build checks passed/failed lists
        checks_passed = []
        checks_failed = []
        
        if length >= 12:
            checks_passed.append("✓ Good length (12+ characters)")
        elif length >= 8:
            checks_passed.append("✓ Minimum length met (8+ characters)")
        else:
            checks_failed.append("✗ Too short (minimum 8 characters)")
        
        if has_upper:
            checks_passed.append("✓ Contains uppercase letters")
        else:
            checks_failed.append("✗ Missing uppercase letters")
        
        if has_lower:
            checks_passed.append("✓ Contains lowercase letters")
        else:
            checks_failed.append("✗ Missing lowercase letters")
        
        if has_digit:
            checks_passed.append("✓ Contains numbers")
        else:
            checks_failed.append("✗ Missing numbers")
        
        if has_special:
            checks_passed.append("✓ Contains special characters")
        else:
            checks_failed.append("✗ Missing special characters")
        
        if not has_repeated:
            checks_passed.append("✓ No repeated character patterns")
        else:
            checks_failed.append("✗ Contains repeated characters")
        
        if not has_sequential:
            checks_passed.append("✓ No sequential characters")
        else:
            checks_failed.append("✗ Contains sequential characters")
        
        if not has_common:
            checks_passed.append("✓ Not a common password pattern")
        else:
            checks_failed.append("✗ Contains common password pattern")
        
        # Calculate score
        score = self._calculate_score(
            length, has_upper, has_lower, has_digit, has_special,
            has_repeated, has_sequential, has_common, unique_chars, entropy
        )
        
        # Determine strength level
        strength = self._score_to_strength(score)
        
        # Generate suggestions
        suggestions = self._generate_suggestions(
            length, has_upper, has_lower, has_digit, has_special,
            has_repeated, has_sequential, has_common
        )
        
        return PasswordAnalysis(
            password_length=length,
            strength_level=strength,
            strength_score=score,
            entropy_bits=round(entropy, 2),
            crack_time_display=crack_display,
            crack_time_seconds=crack_seconds,
            has_uppercase=has_upper,
            has_lowercase=has_lower,
            has_digits=has_digit,
            has_special=has_special,
            has_repeated=has_repeated,
            has_sequential=has_sequential,
            has_common_pattern=has_common,
            checks_passed=checks_passed,
            checks_failed=checks_failed,
            suggestions=suggestions,
            char_diversity=char_diversity,
            unique_chars=unique_chars
        )
    
    def _has_repeated_chars(self, password: str) -> bool:
        """Check for repeated character sequences."""
        # Check for 3+ repeated chars
        if re.search(r'(.)\1{2,}', password):
            return True
        
        # Check for repeated patterns
        for i in range(1, len(password) // 2 + 1):
            pattern = password[:i]
            if pattern * (len(password) // len(pattern)) == password[:len(pattern) * (len(password) // len(pattern))]:
                if len(password) // len(pattern) >= 3:
                    return True
        
        return False
    
    def _has_sequential_chars(self, password: str) -> bool:
        """Check for sequential characters."""
        pwd_lower = password.lower()
        
        # Check keyboard patterns
        for pattern in self.KEYBOARD_PATTERNS:
            if pattern in pwd_lower:
                return True
        
        # Check sequential patterns (3+ in a row)
        for seq_pattern in self.SEQUENTIAL_PATTERNS:
            for i in range(len(seq_pattern) - 2):
                if seq_pattern[i:i+3] in pwd_lower:
                    return True
        
        return False
    
    def _has_common_pattern(self, password: str) -> bool:
        """Check for common password patterns."""
        pwd_lower = password.lower()
        
        # Direct match
        if pwd_lower in self.COMMON_PASSWORDS:
            return True
        
        # Check if password contains common password
        for common in self.COMMON_PASSWORDS:
            if common in pwd_lower and len(common) >= 4:
                return True
        
        # Check for year patterns at end
        if re.search(r'(19|20)\d{2}$', password):
            return True
        
        return False
    
    def _calculate_char_pool_size(self, password: str) -> int:
        """Calculate the character pool size."""
        pool = 0
        if re.search(r'[a-z]', password):
            pool += 26
        if re.search(r'[A-Z]', password):
            pool += 26
        if re.search(r'\d', password):
            pool += 10
        if re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?`~]', password):
            pool += 32
        if re.search(r'\s', password):
            pool += 1
        return pool if pool > 0 else 1
    
    def _calculate_entropy(self, password: str, pool_size: int) -> float:
        """Calculate password entropy in bits."""
        if not password:
            return 0
        return len(password) * math.log2(pool_size) if pool_size > 1 else 0
    
    def _estimate_crack_time(self, password: str, entropy: float) -> float:
        """Estimate time to crack the password."""
        # Assume 10 billion guesses per second (high-end attack)
        guesses_per_second = 10_000_000_000
        
        # Number of possible combinations = 2^entropy
        combinations = 2 ** entropy
        
        # Average case: half the combinations
        seconds = (combinations / 2) / guesses_per_second
        
        return seconds
    
    def _format_crack_time(self, seconds: float) -> str:
        """Format crack time for display."""
        if seconds < 0.001:
            return "Instant"
        if seconds < 1:
            return f"{seconds*1000:.0f} milliseconds"
        if seconds < 60:
            return f"{seconds:.0f} seconds"
        if seconds < 3600:
            return f"{seconds/60:.0f} minutes"
        if seconds < 86400:
            return f"{seconds/3600:.1f} hours"
        if seconds < 2592000:  # 30 days
            return f"{seconds/86400:.0f} days"
        if seconds < 31536000:  # 1 year
            return f"{seconds/2592000:.0f} months"
        if seconds < 31536000 * 100:
            return f"{seconds/31536000:.0f} years"
        if seconds < 31536000 * 1000000:
            return f"{seconds/31536000/1000:.0f} thousand years"
        if seconds < 31536000 * 1000000000:
            return f"{seconds/31536000/1000000:.0f} million years"
        return "Centuries+"
    
    def _calculate_score(self, length, has_upper, has_lower, has_digit, 
                         has_special, has_repeated, has_sequential, 
                         has_common, unique_chars, entropy) -> int:
        """Calculate overall strength score (0-100)."""
        score = 0
        
        # Length scoring (up to 30 points)
        score += min(length * 2, 30)
        
        # Character types (up to 40 points)
        if has_upper:
            score += 10
        if has_lower:
            score += 10
        if has_digit:
            score += 10
        if has_special:
            score += 10
        
        # Unique characters (up to 15 points)
        score += min(unique_chars, 15)
        
        # Entropy bonus (up to 15 points)
        score += min(entropy / 10, 15)
        
        # Penalties
        if has_repeated:
            score -= 15
        if has_sequential:
            score -= 15
        if has_common:
            score -= 25
        if length < 8:
            score -= 20
        
        return max(0, min(100, int(score)))
    
    def _score_to_strength(self, score: int) -> StrengthLevel:
        """Convert score to strength level."""
        if score < 20:
            return StrengthLevel.VERY_WEAK
        elif score < 40:
            return StrengthLevel.WEAK
        elif score < 60:
            return StrengthLevel.FAIR
        elif score < 80:
            return StrengthLevel.STRONG
        else:
            return StrengthLevel.VERY_STRONG
    
    def _generate_suggestions(self, length, has_upper, has_lower, 
                              has_digit, has_special, has_repeated,
                              has_sequential, has_common) -> List[str]:
        """Generate improvement suggestions."""
        suggestions = []
        
        if length < 12:
            suggestions.append("Increase length to at least 12 characters")
        if length < 16:
            suggestions.append("Consider using 16+ characters for better security")
        if not has_upper:
            suggestions.append("Add uppercase letters (A-Z)")
        if not has_lower:
            suggestions.append("Add lowercase letters (a-z)")
        if not has_digit:
            suggestions.append("Add numbers (0-9)")
        if not has_special:
            suggestions.append("Add special characters (!@#$%^&*)")
        if has_repeated:
            suggestions.append("Avoid repeated character patterns")
        if has_sequential:
            suggestions.append("Avoid sequential characters (abc, 123)")
        if has_common:
            suggestions.append("Avoid common words and patterns")
        
        if not suggestions:
            suggestions.append("Great password! Consider using a password manager")
        
        return suggestions


# Convenience function
def analyze_password(password: str) -> Dict:
    """Quick password analysis."""
    analyzer = PasswordStrengthAnalyzer()
    result = analyzer.analyze(password)
    return {
        'score': result.strength_score,
        'level': result.strength_level.value,
        'entropy': result.entropy_bits,
        'crack_time': result.crack_time_display,
        'suggestions': result.suggestions
    }

"""
Breach Checker Module
Checks passwords against Have I Been Pwned API using k-anonymity model.
"""

import requests
import hashlib
from typing import Tuple, Optional
from dataclasses import dataclass


@dataclass
class BreachResult:
    """Stores breach check results with detailed information."""
    password_hash: str
    breach_count: int
    is_compromised: bool
    api_status: str
    

class BreachChecker:
    """Handles password breach checking with the HIBP API."""
    
    API_URL = "https://api.pwnedpasswords.com/range/"
    TIMEOUT = 10
    
    @staticmethod
    def hash_password(password: str) -> Tuple[str, str, str]:
        """
        Hash password using SHA-1 and split for k-anonymity.
        Returns: (full_hash, prefix, suffix)
        """
        sha1 = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
        return sha1, sha1[:5], sha1[5:]
    
    @staticmethod
    def check_password_strength(password: str) -> dict:
        """Analyze password strength characteristics."""
        return {
            'length': len(password),
            'has_upper': any(c.isupper() for c in password),
            'has_lower': any(c.islower() for c in password),
            'has_digit': any(c.isdigit() for c in password),
            'has_special': any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password),
            'is_strong': len(password) >= 12 and 
                        any(c.isupper() for c in password) and
                        any(c.islower() for c in password) and
                        any(c.isdigit() for c in password) and
                        any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password)
        }
    
    def check(self, password: str) -> BreachResult:
        """
        Check if password has been compromised in data breaches.
        Uses k-anonymity to protect the password during lookup.
        """
        full_hash, prefix, suffix = self.hash_password(password)
        
        try:
            response = requests.get(
                f"{self.API_URL}{prefix}",
                timeout=self.TIMEOUT,
                headers={'User-Agent': 'DarkWebLeakMonitor/2.0'}
            )
            response.raise_for_status()
            
            # Parse response and find matching hash
            for line in response.text.splitlines():
                parts = line.split(':')
                if len(parts) == 2:
                    hash_suffix, count = parts
                    if hash_suffix == suffix:
                        return BreachResult(
                            password_hash=full_hash,
                            breach_count=int(count),
                            is_compromised=True,
                            api_status="success"
                        )
            
            return BreachResult(
                password_hash=full_hash,
                breach_count=0,
                is_compromised=False,
                api_status="success"
            )
            
        except requests.exceptions.Timeout:
            return BreachResult(
                password_hash=full_hash,
                breach_count=0,
                is_compromised=False,
                api_status="timeout"
            )
        except requests.exceptions.RequestException as e:
            return BreachResult(
                password_hash=full_hash,
                breach_count=0,
                is_compromised=False,
                api_status=f"error: {str(e)}"
            )


# Legacy function for backward compatibility
def check_password(password: str) -> int:
    """Legacy wrapper - returns breach count as integer."""
    checker = BreachChecker()
    result = checker.check(password)
    return result.breach_count

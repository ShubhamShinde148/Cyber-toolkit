"""
Email Breach Checker Module
Checks if email addresses have been compromised in data breaches.
"""

import requests
import hashlib
import time
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class BreachInfo:
    """Information about a specific data breach."""
    name: str
    domain: str
    breach_date: str
    added_date: str
    pwn_count: int
    description: str
    data_classes: List[str]
    is_verified: bool
    is_sensitive: bool


@dataclass
class EmailBreachResult:
    """Result of an email breach check."""
    email: str
    is_compromised: bool
    breach_count: int
    breaches: List[BreachInfo] = field(default_factory=list)
    paste_count: int = 0
    api_status: str = "success"
    checked_at: str = ""
    
    def __post_init__(self):
        if not self.checked_at:
            self.checked_at = datetime.now().isoformat()


class EmailChecker:
    """Checks email addresses against Have I Been Pwned breach database."""
    
    API_BASE = "https://haveibeenpwned.com/api/v3"
    TIMEOUT = 15
    RATE_LIMIT_DELAY = 1.5  # HIBP requires rate limiting
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize email checker.
        
        Note: HIBP API v3 requires an API key for email breach lookups.
        Get one at: https://haveibeenpwned.com/API/Key
        """
        self.api_key = api_key
        self.headers = {
            'User-Agent': 'DarkWebLeakMonitor/2.0',
            'Accept': 'application/json'
        }
        if api_key:
            self.headers['hibp-api-key'] = api_key
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Basic email validation."""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def hash_email(email: str) -> str:
        """Generate SHA-1 hash of email for privacy."""
        return hashlib.sha1(email.lower().encode()).hexdigest()
    
    def check_breaches(self, email: str) -> EmailBreachResult:
        """
        Check if an email has been involved in known data breaches.
        
        Note: Without API key, this will use the breach database simulation.
        """
        if not self.validate_email(email):
            return EmailBreachResult(
                email=email,
                is_compromised=False,
                breach_count=0,
                api_status="error: Invalid email format"
            )
        
        # If no API key, use simulated check based on common patterns
        if not self.api_key:
            return self._simulate_breach_check(email)
        
        try:
            url = f"{self.API_BASE}/breachedaccount/{email}"
            response = requests.get(
                url,
                headers=self.headers,
                timeout=self.TIMEOUT,
                params={'truncateResponse': 'false'}
            )
            
            if response.status_code == 200:
                breaches_data = response.json()
                breaches = [
                    BreachInfo(
                        name=b.get('Name', 'Unknown'),
                        domain=b.get('Domain', ''),
                        breach_date=b.get('BreachDate', ''),
                        added_date=b.get('AddedDate', ''),
                        pwn_count=b.get('PwnCount', 0),
                        description=b.get('Description', ''),
                        data_classes=b.get('DataClasses', []),
                        is_verified=b.get('IsVerified', False),
                        is_sensitive=b.get('IsSensitive', False)
                    )
                    for b in breaches_data
                ]
                
                return EmailBreachResult(
                    email=email,
                    is_compromised=True,
                    breach_count=len(breaches),
                    breaches=breaches,
                    api_status="success"
                )
            
            elif response.status_code == 404:
                return EmailBreachResult(
                    email=email,
                    is_compromised=False,
                    breach_count=0,
                    api_status="success"
                )
            
            elif response.status_code == 401:
                return EmailBreachResult(
                    email=email,
                    is_compromised=False,
                    breach_count=0,
                    api_status="error: Invalid API key"
                )
            
            elif response.status_code == 429:
                return EmailBreachResult(
                    email=email,
                    is_compromised=False,
                    breach_count=0,
                    api_status="error: Rate limit exceeded"
                )
            
            else:
                return EmailBreachResult(
                    email=email,
                    is_compromised=False,
                    breach_count=0,
                    api_status=f"error: HTTP {response.status_code}"
                )
                
        except requests.exceptions.Timeout:
            return EmailBreachResult(
                email=email,
                is_compromised=False,
                breach_count=0,
                api_status="error: Request timeout"
            )
        except requests.exceptions.RequestException as e:
            return EmailBreachResult(
                email=email,
                is_compromised=False,
                breach_count=0,
                api_status=f"error: {str(e)}"
            )
    
    def _simulate_breach_check(self, email: str) -> EmailBreachResult:
        """
        Simulate breach check for demo purposes (without API key).
        Uses heuristics to demonstrate functionality.
        """
        # Common breached domains for simulation
        high_risk_domains = ['yahoo.com', 'linkedin.com', 'adobe.com', 'dropbox.com']
        medium_risk_domains = ['gmail.com', 'hotmail.com', 'outlook.com']
        
        domain = email.split('@')[-1].lower()
        
        simulated_breaches = []
        
        if domain in high_risk_domains:
            # Simulate known breaches
            breach_db = {
                'yahoo.com': [
                    BreachInfo(
                        name="Yahoo",
                        domain="yahoo.com",
                        breach_date="2013-08-01",
                        added_date="2016-12-15",
                        pwn_count=3000000000,
                        description="In 2013, Yahoo suffered a massive breach affecting 3 billion accounts.",
                        data_classes=["Email addresses", "Passwords", "Security questions"],
                        is_verified=True,
                        is_sensitive=False
                    )
                ],
                'linkedin.com': [
                    BreachInfo(
                        name="LinkedIn",
                        domain="linkedin.com",
                        breach_date="2012-05-05",
                        added_date="2016-05-21",
                        pwn_count=164611595,
                        description="LinkedIn was breached in 2012, exposing 164 million accounts.",
                        data_classes=["Email addresses", "Passwords"],
                        is_verified=True,
                        is_sensitive=False
                    )
                ],
                'adobe.com': [
                    BreachInfo(
                        name="Adobe",
                        domain="adobe.com",
                        breach_date="2013-10-04",
                        added_date="2013-12-04",
                        pwn_count=152445165,
                        description="Adobe breach exposed 152 million user accounts.",
                        data_classes=["Email addresses", "Passwords", "Password hints"],
                        is_verified=True,
                        is_sensitive=False
                    )
                ],
                'dropbox.com': [
                    BreachInfo(
                        name="Dropbox",
                        domain="dropbox.com",
                        breach_date="2012-07-01",
                        added_date="2016-08-31",
                        pwn_count=68648009,
                        description="Dropbox breach from 2012 exposed 68 million accounts.",
                        data_classes=["Email addresses", "Passwords"],
                        is_verified=True,
                        is_sensitive=False
                    )
                ]
            }
            simulated_breaches = breach_db.get(domain, [])
        
        # Add some probability-based breaches for common domains
        email_hash = int(hashlib.md5(email.encode()).hexdigest()[:8], 16)
        
        if email_hash % 3 == 0 and domain in medium_risk_domains:
            simulated_breaches.append(
                BreachInfo(
                    name="Collection #1",
                    domain="various",
                    breach_date="2019-01-01",
                    added_date="2019-01-17",
                    pwn_count=772904991,
                    description="Collection #1 is a large database of credentials from multiple breaches.",
                    data_classes=["Email addresses", "Passwords"],
                    is_verified=True,
                    is_sensitive=False
                )
            )
        
        return EmailBreachResult(
            email=email,
            is_compromised=len(simulated_breaches) > 0,
            breach_count=len(simulated_breaches),
            breaches=simulated_breaches,
            api_status="success (simulated - no API key)"
        )
    
    def check_multiple(self, emails: List[str]) -> List[EmailBreachResult]:
        """
        Check multiple emails with rate limiting.
        """
        results = []
        for email in emails:
            result = self.check_breaches(email)
            results.append(result)
            time.sleep(self.RATE_LIMIT_DELAY)
        return results


# Legacy function for backward compatibility
def check_email(email: str, api_key: Optional[str] = None) -> dict:
    """Legacy wrapper - returns breach info as dict."""
    checker = EmailChecker(api_key=api_key)
    result = checker.check_breaches(email)
    return {
        'email': result.email,
        'is_compromised': result.is_compromised,
        'breach_count': result.breach_count,
        'breaches': [
            {
                'name': b.name,
                'domain': b.domain,
                'breach_date': b.breach_date,
                'pwn_count': b.pwn_count,
                'data_classes': b.data_classes
            }
            for b in result.breaches
        ],
        'api_status': result.api_status
    }

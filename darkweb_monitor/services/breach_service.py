from .breach_checker import BreachChecker
from .email_checker import EmailChecker

class BreachService:
    """
    Service layer for handling email and password breach detections.
    Wraps legacy logic for use in the V2 Modular Architecture.
    """
    
    def __init__(self):
        self.password_checker = BreachChecker()
        self.email_checker = EmailChecker() # Note: API key could be passed here from config
        
    def check_password(self, password):
        """
        Check if a password has been compromised.
        Returns detailed breach information.
        """
        result = self.password_checker.check(password)
        return {
            "status": result.api_status,
            "breach_count": result.breach_count,
            "is_compromised": result.is_compromised,
            "hash_prefix": result.password_hash[:5]
        }

    def check_email(self, email):
        """
        Check if an email has been compromised.
        """
        result = self.email_checker.check_breaches(email)
        return {
            "email": result.email,
            "is_compromised": result.is_compromised,
            "breach_count": result.breach_count,
            "breaches": [
                {
                    "name": b.name,
                    "date": b.breach_date,
                    "pwn_count": b.pwn_count,
                    "description": b.description
                } for b in result.breaches
            ],
            "api_status": result.api_status
        }

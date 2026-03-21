"""
Batch Checker Module
Processes multiple passwords/emails from files for bulk checking.
"""

import os
import time
from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from datetime import datetime
from pathlib import Path

from .breach_checker import BreachChecker, BreachResult
from .email_checker import EmailChecker, EmailBreachResult
from .risk_analyzer import RiskAnalyzer, RiskAssessment


@dataclass
class BatchResult:
    """Results of a batch check operation."""
    total_items: int
    compromised_count: int
    safe_count: int
    error_count: int
    results: List[dict] = field(default_factory=list)
    processing_time: float = 0.0
    checked_at: str = ""
    
    def __post_init__(self):
        if not self.checked_at:
            self.checked_at = datetime.now().isoformat()
    
    @property
    def compromise_rate(self) -> float:
        """Calculate percentage of compromised items."""
        if self.total_items == 0:
            return 0.0
        return (self.compromised_count / self.total_items) * 100


class BatchChecker:
    """Handles batch processing of passwords and emails."""
    
    def __init__(self, rate_limit_delay: float = 0.5):
        self.breach_checker = BreachChecker()
        self.email_checker = EmailChecker()
        self.risk_analyzer = RiskAnalyzer()
        self.rate_limit_delay = rate_limit_delay
    
    def _read_file(self, filepath: str) -> List[str]:
        """Read items from a file, one per line."""
        path = Path(filepath)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Clean and filter empty lines
        items = [line.strip() for line in lines if line.strip()]
        
        # Remove comments (lines starting with #)
        items = [item for item in items if not item.startswith('#')]
        
        return items
    
    def check_passwords(
        self, 
        passwords: List[str],
        callback: Optional[callable] = None
    ) -> BatchResult:
        """
        Check multiple passwords for breaches.
        
        Args:
            passwords: List of passwords to check
            callback: Optional callback(index, total, result) for progress updates
        """
        start_time = time.time()
        results = []
        compromised = 0
        safe = 0
        errors = 0
        
        for i, password in enumerate(passwords):
            try:
                # Check password
                breach_result = self.breach_checker.check(password)
                password_strength = self.breach_checker.check_password_strength(password)
                risk_assessment = self.risk_analyzer.analyze(
                    breach_result.breach_count, 
                    password_strength
                )
                
                # Mask password for storage
                masked = password[:2] + '*' * min(len(password) - 4, 8) + password[-2:] if len(password) > 4 else '****'
                
                result = {
                    'index': i + 1,
                    'password_masked': masked,
                    'password_length': len(password),
                    'breach_count': breach_result.breach_count,
                    'is_compromised': breach_result.is_compromised,
                    'risk_level': risk_assessment.level.value,
                    'risk_score': risk_assessment.score,
                    'api_status': breach_result.api_status,
                    'strength': password_strength
                }
                results.append(result)
                
                if breach_result.is_compromised:
                    compromised += 1
                else:
                    safe += 1
                
                if callback:
                    callback(i + 1, len(passwords), result)
                
            except Exception as e:
                results.append({
                    'index': i + 1,
                    'password_masked': '****',
                    'error': str(e)
                })
                errors += 1
            
            # Rate limiting
            if i < len(passwords) - 1:
                time.sleep(self.rate_limit_delay)
        
        processing_time = time.time() - start_time
        
        return BatchResult(
            total_items=len(passwords),
            compromised_count=compromised,
            safe_count=safe,
            error_count=errors,
            results=results,
            processing_time=round(processing_time, 2)
        )
    
    def check_passwords_from_file(
        self, 
        filepath: str,
        callback: Optional[callable] = None
    ) -> BatchResult:
        """Check passwords from a file (one per line)."""
        passwords = self._read_file(filepath)
        return self.check_passwords(passwords, callback)
    
    def check_emails(
        self, 
        emails: List[str],
        callback: Optional[callable] = None
    ) -> BatchResult:
        """
        Check multiple emails for breaches.
        
        Args:
            emails: List of emails to check
            callback: Optional callback(index, total, result) for progress updates
        """
        start_time = time.time()
        results = []
        compromised = 0
        safe = 0
        errors = 0
        
        for i, email in enumerate(emails):
            try:
                # Check email
                breach_result = self.email_checker.check_breaches(email)
                
                result = {
                    'index': i + 1,
                    'email': email,
                    'is_compromised': breach_result.is_compromised,
                    'breach_count': breach_result.breach_count,
                    'breaches': [
                        {
                            'name': b.name,
                            'domain': b.domain,
                            'breach_date': b.breach_date,
                            'pwn_count': b.pwn_count
                        }
                        for b in breach_result.breaches
                    ],
                    'api_status': breach_result.api_status
                }
                results.append(result)
                
                if breach_result.is_compromised:
                    compromised += 1
                else:
                    safe += 1
                
                if callback:
                    callback(i + 1, len(emails), result)
                
            except Exception as e:
                results.append({
                    'index': i + 1,
                    'email': email,
                    'error': str(e)
                })
                errors += 1
            
            # Rate limiting (HIBP requires this)
            if i < len(emails) - 1:
                time.sleep(max(self.rate_limit_delay, 1.5))
        
        processing_time = time.time() - start_time
        
        return BatchResult(
            total_items=len(emails),
            compromised_count=compromised,
            safe_count=safe,
            error_count=errors,
            results=results,
            processing_time=round(processing_time, 2)
        )
    
    def check_emails_from_file(
        self, 
        filepath: str,
        callback: Optional[callable] = None
    ) -> BatchResult:
        """Check emails from a file (one per line)."""
        emails = self._read_file(filepath)
        return self.check_emails(emails, callback)
    
    def generate_summary(self, batch_result: BatchResult) -> str:
        """Generate a text summary of batch results."""
        lines = [
            "=" * 60,
            "BATCH CHECK SUMMARY",
            "=" * 60,
            f"Total Items Checked: {batch_result.total_items}",
            f"Compromised: {batch_result.compromised_count} ({batch_result.compromise_rate:.1f}%)",
            f"Safe: {batch_result.safe_count}",
            f"Errors: {batch_result.error_count}",
            f"Processing Time: {batch_result.processing_time}s",
            f"Checked At: {batch_result.checked_at}",
            "=" * 60,
            "",
            "DETAILED RESULTS:",
            "-" * 60
        ]
        
        for result in batch_result.results:
            if 'error' in result:
                lines.append(f"#{result['index']}: ERROR - {result['error']}")
            elif 'password_masked' in result:
                status = "COMPROMISED" if result['is_compromised'] else "SAFE"
                lines.append(
                    f"#{result['index']}: {result['password_masked']} | "
                    f"{status} | Breaches: {result['breach_count']:,} | "
                    f"Risk: {result['risk_level']}"
                )
            elif 'email' in result:
                status = "COMPROMISED" if result['is_compromised'] else "SAFE"
                lines.append(
                    f"#{result['index']}: {result['email']} | "
                    f"{status} | Breaches: {result['breach_count']}"
                )
        
        return '\n'.join(lines)


def check_passwords_batch(passwords: List[str]) -> BatchResult:
    """Convenience function to check multiple passwords."""
    checker = BatchChecker()
    return checker.check_passwords(passwords)


def check_emails_batch(emails: List[str]) -> BatchResult:
    """Convenience function to check multiple emails."""
    checker = BatchChecker()
    return checker.check_emails(emails)

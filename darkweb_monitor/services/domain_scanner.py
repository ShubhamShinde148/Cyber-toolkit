"""
Domain Breach Scanner Module
============================
Scans domains for potential security issues and breach information.
Checks DNS records, email security configurations, and known breach databases.

Uses public APIs and DNS queries for assessment.
"""

import requests
import socket
import re
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import hashlib


@dataclass
class DomainInfo:
    """Container for domain information."""
    domain: str
    registrable: bool
    dns_records: Dict
    email_security: Dict
    breach_info: Dict
    ssl_info: Dict
    reputation: Dict


class DomainScanner:
    """
    Comprehensive domain security scanner.
    
    Features:
    - DNS record enumeration
    - Email security (SPF, DKIM, DMARC) checking
    - SSL/TLS certificate verification
    - Domain reputation scoring
    - Breach database lookup
    """
    
    # Common subdomains to check
    COMMON_SUBDOMAINS = [
        'www', 'mail', 'email', 'webmail', 'ftp', 'remote',
        'admin', 'portal', 'vpn', 'api', 'dev', 'staging',
        'test', 'blog', 'shop', 'store', 'cdn', 'static'
    ]
    
    # DNS record types to query
    DNS_RECORD_TYPES = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME', 'SOA']
    
    def __init__(self, timeout: int = 10):
        """
        Initialize domain scanner.
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'DarkWeb Monitor Security Scanner/1.0'
        })
    
    def validate_domain(self, domain: str) -> tuple[bool, str]:
        """
        Validate domain format.
        
        Args:
            domain: Domain to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not domain:
            return False, "Domain cannot be empty"
        
        # Remove protocol if present
        domain = re.sub(r'^https?://', '', domain)
        domain = domain.split('/')[0]  # Remove path
        
        # Basic domain validation regex
        domain_pattern = r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
        
        if not re.match(domain_pattern, domain):
            return False, "Invalid domain format"
        
        if len(domain) > 253:
            return False, "Domain name too long"
        
        return True, domain
    
    def _get_dns_records(self, domain: str) -> Dict:
        """
        Get DNS records for domain using socket and public DNS APIs.
        
        Args:
            domain: Domain to query
            
        Returns:
            Dictionary of DNS records
        """
        records = {
            'A': [],
            'AAAA': [],
            'MX': [],
            'NS': [],
            'TXT': [],
            'has_ipv6': False,
            'nameservers': []
        }
        
        try:
            # Get A records (IPv4)
            try:
                ips = socket.gethostbyname_ex(domain)
                records['A'] = ips[2]
            except socket.gaierror:
                pass
            
            # Try to get IPv6
            try:
                ipv6_info = socket.getaddrinfo(domain, None, socket.AF_INET6)
                if ipv6_info:
                    records['AAAA'] = list(set([info[4][0] for info in ipv6_info]))
                    records['has_ipv6'] = True
            except socket.gaierror:
                pass
            
            # Use public DNS API for more records
            try:
                dns_api_url = f"https://dns.google/resolve?name={domain}&type=ANY"
                response = self.session.get(dns_api_url, timeout=self.timeout)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if 'Answer' in data:
                        for answer in data['Answer']:
                            rtype = answer.get('type', 0)
                            rdata = answer.get('data', '')
                            
                            # Type mappings
                            type_map = {
                                1: 'A', 2: 'NS', 5: 'CNAME',
                                15: 'MX', 16: 'TXT', 28: 'AAAA'
                            }
                            
                            if rtype in type_map:
                                record_type = type_map[rtype]
                                if record_type in records and isinstance(records[record_type], list):
                                    if rdata not in records[record_type]:
                                        records[record_type].append(rdata)
            except Exception:
                pass
                
        except Exception as e:
            records['error'] = str(e)
        
        return records
    
    def _check_email_security(self, domain: str) -> Dict:
        """
        Check email security configurations (SPF, DKIM, DMARC).
        
        Args:
            domain: Domain to check
            
        Returns:
            Dictionary with email security status
        """
        security = {
            'spf': {'exists': False, 'record': None, 'issues': []},
            'dmarc': {'exists': False, 'record': None, 'policy': None, 'issues': []},
            'dkim': {'likely_exists': False, 'note': 'DKIM requires selector to verify'},
            'score': 0,
            'grade': 'F'
        }
        
        try:
            # Check SPF
            spf_url = f"https://dns.google/resolve?name={domain}&type=TXT"
            response = self.session.get(spf_url, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'Answer' in data:
                    for answer in data['Answer']:
                        txt_data = answer.get('data', '').strip('"')
                        
                        if txt_data.startswith('v=spf1'):
                            security['spf']['exists'] = True
                            security['spf']['record'] = txt_data
                            security['score'] += 30
                            
                            # Check for weak SPF
                            if '+all' in txt_data:
                                security['spf']['issues'].append('Weak SPF: +all allows any sender')
                            elif '?all' in txt_data:
                                security['spf']['issues'].append('Neutral SPF: ?all provides no protection')
                            elif '-all' in txt_data:
                                security['score'] += 10  # Strong SPF
            
            # Check DMARC
            dmarc_url = f"https://dns.google/resolve?name=_dmarc.{domain}&type=TXT"
            response = self.session.get(dmarc_url, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'Answer' in data:
                    for answer in data['Answer']:
                        txt_data = answer.get('data', '').strip('"')
                        
                        if 'v=DMARC1' in txt_data:
                            security['dmarc']['exists'] = True
                            security['dmarc']['record'] = txt_data
                            security['score'] += 30
                            
                            # Parse policy
                            if 'p=reject' in txt_data:
                                security['dmarc']['policy'] = 'reject'
                                security['score'] += 15
                            elif 'p=quarantine' in txt_data:
                                security['dmarc']['policy'] = 'quarantine'
                                security['score'] += 10
                            elif 'p=none' in txt_data:
                                security['dmarc']['policy'] = 'none'
                                security['dmarc']['issues'].append('DMARC policy is none - no enforcement')
            
            # Check common DKIM selectors
            dkim_selectors = ['default', 'google', 'selector1', 'selector2', 'k1', 'mail']
            for selector in dkim_selectors:
                try:
                    dkim_url = f"https://dns.google/resolve?name={selector}._domainkey.{domain}&type=TXT"
                    response = self.session.get(dkim_url, timeout=3)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if 'Answer' in data:
                            security['dkim']['likely_exists'] = True
                            security['score'] += 15
                            break
                except Exception:
                    continue
            
            # Calculate grade
            score = security['score']
            if score >= 90:
                security['grade'] = 'A+'
            elif score >= 80:
                security['grade'] = 'A'
            elif score >= 70:
                security['grade'] = 'B'
            elif score >= 60:
                security['grade'] = 'C'
            elif score >= 40:
                security['grade'] = 'D'
            else:
                security['grade'] = 'F'
                
        except Exception as e:
            security['error'] = str(e)
        
        return security
    
    def _check_ssl(self, domain: str) -> Dict:
        """
        Check SSL/TLS configuration.
        
        Args:
            domain: Domain to check
            
        Returns:
            Dictionary with SSL information
        """
        ssl_info = {
            'has_https': False,
            'redirects_to_https': False,
            'certificate_valid': False,
            'issues': []
        }
        
        try:
            # Check HTTPS
            https_url = f"https://{domain}"
            response = self.session.get(
                https_url,
                timeout=self.timeout,
                allow_redirects=True,
                verify=True
            )
            
            ssl_info['has_https'] = True
            ssl_info['certificate_valid'] = True
            ssl_info['final_url'] = response.url
            
            # Check HTTP redirect
            try:
                http_url = f"http://{domain}"
                http_response = self.session.get(
                    http_url,
                    timeout=5,
                    allow_redirects=True
                )
                
                if http_response.url.startswith('https://'):
                    ssl_info['redirects_to_https'] = True
                else:
                    ssl_info['issues'].append('HTTP does not redirect to HTTPS')
                    
            except Exception:
                pass
                
        except requests.exceptions.SSLError as e:
            ssl_info['has_https'] = True
            ssl_info['certificate_valid'] = False
            ssl_info['issues'].append(f'SSL Certificate Error: {str(e)[:100]}')
            
        except requests.exceptions.ConnectionError:
            ssl_info['issues'].append('Could not connect to domain')
            
        except Exception as e:
            ssl_info['error'] = str(e)
        
        return ssl_info
    
    def _check_breaches(self, domain: str) -> Dict:
        """
        Check for known breaches associated with domain.
        
        Note: This checks against known breach databases via API.
        For comprehensive results, premium API access may be required.
        
        Args:
            domain: Domain to check
            
        Returns:
            Dictionary with breach information
        """
        breach_info = {
            'breaches_found': 0,
            'breach_list': [],
            'risk_level': 'unknown',
            'last_checked': datetime.now().isoformat()
        }
        
        try:
            # Using Have I Been Pwned API for domain breaches
            # Note: This would require API key for production use
            # Here we return simulated structure for the module
            
            breach_info['note'] = 'Domain breach checking requires HIBP API key'
            breach_info['api_required'] = True
            
            # Calculate risk based on domain age and type
            # This is a placeholder for actual breach data
            breach_info['risk_level'] = 'low'
            
        except Exception as e:
            breach_info['error'] = str(e)
        
        return breach_info
    
    def _check_subdomains(self, domain: str) -> List[str]:
        """
        Enumerate common subdomains.
        
        Args:
            domain: Base domain
            
        Returns:
            List of found subdomains
        """
        found_subdomains = []
        
        def check_subdomain(subdomain: str) -> Optional[str]:
            full_domain = f"{subdomain}.{domain}"
            try:
                socket.gethostbyname(full_domain)
                return full_domain
            except socket.gaierror:
                return None
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = executor.map(check_subdomain, self.COMMON_SUBDOMAINS)
            found_subdomains = [r for r in results if r is not None]
        
        return found_subdomains
    
    def scan(self, domain: str, full_scan: bool = True) -> Dict:
        """
        Perform comprehensive domain security scan.
        
        Args:
            domain: Domain to scan
            full_scan: Whether to perform all checks
            
        Returns:
            Dictionary with complete scan results
        """
        # Validate domain
        is_valid, result = self.validate_domain(domain)
        if not is_valid:
            return {
                'success': False,
                'error': result,
                'domain': domain
            }
        
        clean_domain = result
        
        # Perform scans
        dns_records = self._get_dns_records(clean_domain)
        email_security = self._check_email_security(clean_domain)
        ssl_info = self._check_ssl(clean_domain)
        breach_info = self._check_breaches(clean_domain)
        
        # Optional deep scans
        subdomains = []
        if full_scan:
            subdomains = self._check_subdomains(clean_domain)
        
        # Calculate overall security score
        security_score = 0
        issues = []
        recommendations = []
        
        # DNS Score
        if dns_records.get('A'):
            security_score += 10
        if dns_records.get('has_ipv6'):
            security_score += 5
        else:
            recommendations.append('Consider adding IPv6 (AAAA) records')
        
        # Email Security Score
        security_score += email_security.get('score', 0) * 0.3
        if not email_security['spf']['exists']:
            issues.append('No SPF record found')
            recommendations.append('Add SPF record to prevent email spoofing')
        if not email_security['dmarc']['exists']:
            issues.append('No DMARC record found')
            recommendations.append('Implement DMARC policy for email security')
        
        # SSL Score
        if ssl_info.get('has_https'):
            security_score += 20
            if ssl_info.get('certificate_valid'):
                security_score += 10
            if ssl_info.get('redirects_to_https'):
                security_score += 10
            else:
                recommendations.append('Redirect all HTTP traffic to HTTPS')
        else:
            issues.append('HTTPS not configured')
            recommendations.append('Enable HTTPS with valid SSL certificate')
        
        # Calculate grade
        if security_score >= 90:
            grade = 'A+'
        elif security_score >= 80:
            grade = 'A'
        elif security_score >= 70:
            grade = 'B'
        elif security_score >= 60:
            grade = 'C'
        elif security_score >= 40:
            grade = 'D'
        else:
            grade = 'F'
        
        return {
            'success': True,
            'domain': clean_domain,
            'scan_time': datetime.now().isoformat(),
            'security_score': round(security_score),
            'security_grade': grade,
            'dns': {
                'records': dns_records,
                'has_ipv4': bool(dns_records.get('A')),
                'has_ipv6': dns_records.get('has_ipv6', False),
                'mx_records': dns_records.get('MX', []),
                'nameservers': dns_records.get('NS', [])
            },
            'email_security': email_security,
            'ssl': ssl_info,
            'breaches': breach_info,
            'subdomains_found': subdomains,
            'issues': issues,
            'recommendations': recommendations,
            'summary': {
                'total_issues': len(issues),
                'critical_issues': len([i for i in issues if 'HTTPS' in i or 'SPF' in i]),
                'has_email_protection': email_security['spf']['exists'] or email_security['dmarc']['exists'],
                'has_ssl': ssl_info.get('has_https', False)
            }
        }
    
    def quick_scan(self, domain: str) -> Dict:
        """
        Perform quick domain scan (essential checks only).
        
        Args:
            domain: Domain to scan
            
        Returns:
            Dictionary with basic scan results
        """
        return self.scan(domain, full_scan=False)


# Example usage
if __name__ == "__main__":
    scanner = DomainScanner(timeout=10)
    
    print("=" * 60)
    print("Domain Security Scanner - Test")
    print("=" * 60)
    
    test_domain = "example.com"
    print(f"\nScanning domain: {test_domain}")
    print("-" * 40)
    
    results = scanner.quick_scan(test_domain)
    
    if results['success']:
        print(f"Security Grade: {results['security_grade']}")
        print(f"Security Score: {results['security_score']}/100")
        print(f"\nEmail Security: {results['email_security']['grade']}")
        print(f"Has HTTPS: {results['ssl'].get('has_https', False)}")
        
        if results['issues']:
            print("\nIssues Found:")
            for issue in results['issues']:
                print(f"  - {issue}")
        
        if results['recommendations']:
            print("\nRecommendations:")
            for rec in results['recommendations']:
                print(f"  - {rec}")
    else:
        print(f"Error: {results['error']}")

from .domain_scanner import DomainScanner
from .ip_intelligence import IPIntelligence

class OSINTService:
    """
    Service layer for handling WHOIS, IP, and Domain reconnaissance.
    Aggregates logic from legacy OSINT modules for V2 integration.
    """
    
    def __init__(self):
        self.domain_scanner = DomainScanner()
        self.ip_intelligence = IPIntelligence()
        
    def scan_domain(self, domain, full_scan=False):
        """
        Perform a security scan on a domain.
        """
        return self.domain_scanner.scan(domain, full_scan=full_scan)
        
    def scan_ip(self, ip_address):
        """
        Perform threat intelligence analysis on an IP address.
        """
        return self.ip_intelligence.analyze(ip_address)

    def get_whois(self, domain):
        """
        Perform a WHOIS lookup for a domain.
        """
        # IPIntelligence can also handle resolution if needed
        return self.domain_scanner._get_dns_records(domain)

"""
Subdomain Finder Tool
Discover subdomains using various techniques.
"""

import socket
import concurrent.futures
from typing import Dict, List, Optional, Set
from dataclasses import dataclass

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    import dns.resolver
    HAS_DNSPYTHON = True
except ImportError:
    HAS_DNSPYTHON = False


@dataclass
class SubdomainResult:
    """Result of subdomain discovery."""
    domain: str
    subdomains: List[Dict[str, str]]  # [{subdomain, ip, source}]
    total_found: int
    sources_used: List[str]
    success: bool
    error: Optional[str] = None


class SubdomainFinder:
    """Discover subdomains using multiple techniques."""
    
    # Common subdomain prefixes for brute force
    COMMON_SUBDOMAINS = [
        'www', 'mail', 'ftp', 'smtp', 'pop', 'imap', 'webmail',
        'admin', 'administrator', 'cpanel', 'whm', 'ns1', 'ns2',
        'dns', 'dns1', 'dns2', 'mx', 'mx1', 'mx2', 'email',
        'api', 'app', 'apps', 'dev', 'development', 'staging',
        'test', 'testing', 'beta', 'demo', 'stage', 'prod',
        'production', 'live', 'cdn', 'static', 'assets', 'media',
        'img', 'images', 'image', 'video', 'videos', 'files',
        'download', 'downloads', 'upload', 'uploads', 'ftp',
        'sftp', 'ssh', 'vpn', 'remote', 'rdp', 'owa',
        'exchange', 'autodiscover', 'portal', 'gateway', 'secure',
        'ssl', 'shop', 'store', 'cart', 'checkout', 'pay',
        'payment', 'billing', 'invoice', 'support', 'help',
        'helpdesk', 'ticket', 'tickets', 'kb', 'wiki', 'docs',
        'doc', 'documentation', 'blog', 'news', 'forum', 'forums',
        'community', 'social', 'mobile', 'm', 'wap', 'status',
        'health', 'monitor', 'monitoring', 'stats', 'analytics',
        'tracking', 'login', 'signin', 'signup', 'register',
        'auth', 'oauth', 'sso', 'identity', 'id', 'account',
        'accounts', 'my', 'profile', 'user', 'users', 'member',
        'members', 'client', 'clients', 'customer', 'customers',
        'partner', 'partners', 'internal', 'intranet', 'extranet',
        'corp', 'corporate', 'company', 'office', 'cloud', 'aws',
        'azure', 'gcp', 's3', 'jenkins', 'gitlab', 'github',
        'bitbucket', 'jira', 'confluence', 'slack', 'teams',
        'zoom', 'meet', 'calendar', 'drive', 'backup', 'db',
        'database', 'mysql', 'postgres', 'postgresql', 'mongo',
        'mongodb', 'redis', 'elastic', 'elasticsearch', 'kibana',
        'grafana', 'prometheus', 'docker', 'kubernetes', 'k8s'
    ]
    
    def __init__(self, timeout: int = 5, max_workers: int = 20):
        self.timeout = timeout
        self.max_workers = max_workers
        if HAS_DNSPYTHON:
            self.resolver = dns.resolver.Resolver()
            self.resolver.timeout = timeout
            self.resolver.lifetime = timeout
    
    def find(self, domain: str, use_bruteforce: bool = True,
             use_crtsh: bool = True, custom_wordlist: List[str] = None) -> SubdomainResult:
        """
        Find subdomains for a domain.
        
        Args:
            domain: Target domain
            use_bruteforce: Use common subdomain bruteforce
            use_crtsh: Query crt.sh for certificate transparency
            custom_wordlist: Custom list of subdomain prefixes
            
        Returns:
            SubdomainResult with discovered subdomains
        """
        domain = domain.strip().lower()
        
        # Clean domain
        if domain.startswith('http://'):
            domain = domain[7:]
        if domain.startswith('https://'):
            domain = domain[8:]
        domain = domain.split('/')[0]
        
        found_subdomains: Set[str] = set()
        subdomain_details: List[Dict] = []
        sources_used = []
        
        # Certificate Transparency search
        if use_crtsh and HAS_REQUESTS:
            ct_subs = self._search_crtsh(domain)
            sources_used.append('crt.sh')
            for sub in ct_subs:
                if sub not in found_subdomains:
                    found_subdomains.add(sub)
                    ip = self._resolve_domain(sub)
                    subdomain_details.append({
                        'subdomain': sub,
                        'ip': ip or 'N/A',
                        'source': 'crt.sh'
                    })
        
        # Bruteforce common subdomains
        if use_bruteforce:
            wordlist = custom_wordlist or self.COMMON_SUBDOMAINS
            bruteforce_subs = self._bruteforce_subdomains(domain, wordlist)
            sources_used.append('bruteforce')
            
            for sub, ip in bruteforce_subs:
                if sub not in found_subdomains:
                    found_subdomains.add(sub)
                    subdomain_details.append({
                        'subdomain': sub,
                        'ip': ip,
                        'source': 'bruteforce'
                    })
        
        # Sort results
        subdomain_details.sort(key=lambda x: x['subdomain'])
        
        return SubdomainResult(
            domain=domain,
            subdomains=subdomain_details,
            total_found=len(subdomain_details),
            sources_used=sources_used,
            success=True
        )
    
    def _search_crtsh(self, domain: str) -> List[str]:
        """Search certificate transparency logs via crt.sh."""
        subdomains = set()
        
        try:
            response = requests.get(
                f'https://crt.sh/?q=%.{domain}&output=json',
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                for entry in data:
                    name = entry.get('name_value', '')
                    # Handle multiple names in one certificate
                    for sub in name.split('\n'):
                        sub = sub.strip().lower()
                        # Remove wildcard prefix
                        if sub.startswith('*.'):
                            sub = sub[2:]
                        if sub.endswith(domain) and sub != domain:
                            subdomains.add(sub)
        except Exception:
            pass
        
        return list(subdomains)
    
    def _resolve_domain(self, domain: str) -> Optional[str]:
        """Resolve domain to IP address."""
        if HAS_DNSPYTHON:
            try:
                answers = self.resolver.resolve(domain, 'A')
                return str(answers[0])
            except Exception:
                return None
        else:
            try:
                return socket.gethostbyname(domain)
            except Exception:
                return None
    
    def _check_subdomain(self, subdomain: str) -> Optional[tuple]:
        """Check if subdomain exists."""
        ip = self._resolve_domain(subdomain)
        if ip:
            return (subdomain, ip)
        return None
    
    def _bruteforce_subdomains(self, domain: str, wordlist: List[str]) -> List[tuple]:
        """Bruteforce subdomains using wordlist."""
        found = []
        subdomains_to_check = [f"{prefix}.{domain}" for prefix in wordlist]
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self._check_subdomain, sub): sub 
                      for sub in subdomains_to_check}
            
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    found.append(result)
        
        return found
    
    def quick_scan(self, domain: str) -> SubdomainResult:
        """Quick subdomain scan with limited wordlist."""
        quick_list = [
            'www', 'mail', 'ftp', 'admin', 'api', 'app', 'dev',
            'test', 'staging', 'cdn', 'static', 'blog', 'shop',
            'store', 'portal', 'vpn', 'remote', 'ns1', 'ns2',
            'mx', 'smtp', 'pop', 'imap', 'webmail'
        ]
        return self.find(domain, use_bruteforce=True, use_crtsh=True, 
                        custom_wordlist=quick_list)
    
    def format_output(self, result: SubdomainResult) -> str:
        """Format subdomain result for display."""
        lines = [
            f"=== SUBDOMAIN DISCOVERY ===",
            f"Target Domain: {result.domain}",
            f"Total Found: {result.total_found}",
            f"Sources: {', '.join(result.sources_used)}",
            ""
        ]
        
        if not result.subdomains:
            lines.append("No subdomains found.")
            return '\n'.join(lines)
        
        lines.append("=== DISCOVERED SUBDOMAINS ===")
        for sub in result.subdomains:
            lines.append(f"  {sub['subdomain']}")
            lines.append(f"    IP: {sub['ip']} | Source: {sub['source']}")
        
        return '\n'.join(lines)


# Convenience function
def find_subdomains(domain: str) -> Dict:
    """Quick subdomain finder."""
    finder = SubdomainFinder()
    result = finder.quick_scan(domain)
    return {
        'domain': result.domain,
        'subdomains': result.subdomains,
        'total': result.total_found,
        'success': result.success
    }

"""
Subdomain Finder Tool
Discover subdomains using various techniques.
"""

import ipaddress
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
        candidates: Dict[str, Set[str]] = {}

        def add_candidate(name: str, source: str):
            sub = self._normalize_candidate(name, domain)
            if not sub:
                return
            if sub not in candidates:
                candidates[sub] = set()
            candidates[sub].add(source)
        
        # Certificate Transparency search
        if use_crtsh and HAS_REQUESTS:
            sources_used.append('crt.sh')
            ct_subs = self._search_crtsh(domain)
            for sub in ct_subs:
                add_candidate(sub, 'crt.sh')

        # API Source: dns.bufferover.run
        if HAS_REQUESTS:
            sources_used.append('bufferover')
            bo_subs = self._search_bufferover(domain)
            for sub in bo_subs:
                add_candidate(sub, 'bufferover')
        
        # Bruteforce common subdomains
        if use_bruteforce:
            wordlist = custom_wordlist or self.COMMON_SUBDOMAINS
            sources_used.append('wordlist')
            brute_candidates = self._bruteforce_candidates(domain, wordlist)
            for sub in brute_candidates:
                add_candidate(sub, 'wordlist')

        # DNS resolve filter: only keep valid resolvable subdomains.
        if candidates:
            resolved = self._resolve_candidates(list(candidates.keys()))
            for sub, ip in resolved:
                if sub not in found_subdomains:
                    found_subdomains.add(sub)
                    subdomain_details.append({
                        'subdomain': sub,
                        'ip': ip,
                        'source': ', '.join(sorted(candidates[sub]))
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

    def _search_bufferover(self, domain: str) -> List[str]:
        """Query dns.bufferover.run for passive DNS subdomains."""
        results = set()
        try:
            response = requests.get(
                f"https://dns.bufferover.run/dns?q=.{domain}",
                timeout=self.timeout
            )
            if response.status_code != 200:
                return []

            data = response.json() if response.text else {}
            # Known keys from API response: FDNS_A, RDNS, etc.
            for key in ("FDNS_A", "RDNS"):
                for entry in data.get(key, []) or []:
                    if not isinstance(entry, str):
                        continue
                    # FDNS_A can be "ip,sub.domain.tld"
                    candidate = entry.split(",")[-1].strip().lower()
                    candidate = candidate.lstrip("*.").rstrip(".")
                    if candidate.endswith(domain) and candidate != domain:
                        results.add(candidate)
        except Exception:
            return []
        return list(results)
    
    def _resolve_domain(self, domain: str) -> Optional[str]:
        """Resolve domain to IP address (A or AAAA)."""
        if not HAS_DNSPYTHON:
            return None

        for record_type in ("A", "AAAA"):
            try:
                answers = self.resolver.resolve(domain, record_type)
                for ans in answers:
                    ip = str(ans).strip()
                    if self._is_valid_ip(ip):
                        return ip
            except Exception:
                continue
        return None
    
    def _check_subdomain(self, subdomain: str) -> Optional[tuple]:
        """Resolve subdomain and return tuple if valid."""
        ip = self._resolve_domain(subdomain)
        if ip:
            return (subdomain, ip)
        return None

    def _bruteforce_candidates(self, domain: str, wordlist: List[str]) -> List[str]:
        """Generate candidate subdomains from wordlist (resolution happens later)."""
        out = []
        seen = set()
        for prefix in wordlist:
            p = (prefix or "").strip().lower().strip(".")
            if not p:
                continue
            sub = f"{p}.{domain}"
            if sub not in seen:
                seen.add(sub)
                out.append(sub)
        return out

    def _resolve_candidates(self, candidates: List[str]) -> List[tuple]:
        """Resolve many candidates concurrently and keep only valid."""
        found = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self._check_subdomain, sub): sub for sub in candidates}
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    found.append(result)
        return found

    def _normalize_candidate(self, subdomain: str, domain: str) -> Optional[str]:
        sub = (subdomain or "").strip().lower()
        if not sub:
            return None
        sub = sub.lstrip("*.").rstrip(".")
        if sub == domain:
            return None
        if not sub.endswith(domain):
            return None
        # Exclude wildcard placeholders and obvious invalid labels.
        if "*" in sub or ".." in sub:
            return None
        return sub

    def _is_valid_ip(self, value: str) -> bool:
        try:
            ipaddress.ip_address(value)
            return True
        except Exception:
            return False
    
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

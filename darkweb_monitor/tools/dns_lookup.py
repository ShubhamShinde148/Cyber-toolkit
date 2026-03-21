"""
DNS Lookup Tool
Perform DNS queries and retrieve various record types.
"""

import socket
from typing import Dict, List, Optional
from dataclasses import dataclass

try:
    import dns.resolver
    import dns.reversename
    HAS_DNSPYTHON = True
except ImportError:
    HAS_DNSPYTHON = False


@dataclass
class DNSRecord:
    """A single DNS record."""
    record_type: str
    value: str
    ttl: Optional[int] = None


@dataclass
class DNSResult:
    """Result of DNS lookup."""
    domain: str
    records: Dict[str, List[str]]
    success: bool
    query_time_ms: Optional[float] = None
    nameservers: Optional[List[str]] = None
    error: Optional[str] = None


class DNSLookupTool:
    """Perform DNS lookups for various record types."""
    
    SUPPORTED_RECORD_TYPES = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME', 'SOA', 'PTR', 'CAA']
    
    def __init__(self, timeout: int = 5):
        self.timeout = timeout
        if HAS_DNSPYTHON:
            self.resolver = dns.resolver.Resolver()
            self.resolver.timeout = timeout
            self.resolver.lifetime = timeout
    
    def lookup(self, domain: str, record_types: List[str] = None) -> DNSResult:
        """
        Perform DNS lookup for specified record types.
        
        Args:
            domain: Domain name to lookup
            record_types: List of record types (default: A, AAAA, MX, NS, TXT)
            
        Returns:
            DNSResult with all found records
        """
        domain = domain.strip().lower()
        
        # Remove protocol prefix if present
        if domain.startswith('http://'):
            domain = domain[7:]
        if domain.startswith('https://'):
            domain = domain[8:]
        
        # Remove trailing slash and path
        domain = domain.split('/')[0]
        
        if not record_types:
            record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT']
        
        records = {}
        
        if HAS_DNSPYTHON:
            return self._lookup_with_dnspython(domain, record_types)
        else:
            return self._lookup_basic(domain)
    
    def _lookup_with_dnspython(self, domain: str, record_types: List[str]) -> DNSResult:
        """Lookup using dnspython library."""
        import time
        records = {}
        nameservers = None
        
        start_time = time.time()
        
        for rtype in record_types:
            rtype = rtype.upper()
            if rtype not in self.SUPPORTED_RECORD_TYPES:
                continue
            
            try:
                answers = self.resolver.resolve(domain, rtype)
                records[rtype] = []
                
                for rdata in answers:
                    if rtype == 'MX':
                        records[rtype].append(f"{rdata.preference} {rdata.exchange}")
                    elif rtype == 'SOA':
                        records[rtype].append(
                            f"Primary NS: {rdata.mname}, "
                            f"Email: {rdata.rname}, "
                            f"Serial: {rdata.serial}"
                        )
                    else:
                        records[rtype].append(str(rdata))
                
                # Get nameservers from the response
                if rtype == 'NS':
                    nameservers = records[rtype]
                    
            except dns.resolver.NXDOMAIN:
                return DNSResult(
                    domain=domain,
                    records={},
                    success=False,
                    error="Domain does not exist (NXDOMAIN)"
                )
            except dns.resolver.NoAnswer:
                # No records of this type
                continue
            except dns.resolver.NoNameservers:
                return DNSResult(
                    domain=domain,
                    records={},
                    success=False,
                    error="No nameservers available"
                )
            except dns.resolver.Timeout:
                continue
            except Exception as e:
                continue
        
        query_time = (time.time() - start_time) * 1000
        
        return DNSResult(
            domain=domain,
            records=records,
            success=len(records) > 0,
            query_time_ms=round(query_time, 2),
            nameservers=nameservers,
            error=None if records else "No records found"
        )
    
    def _lookup_basic(self, domain: str) -> DNSResult:
        """Basic lookup using socket (fallback)."""
        records = {}
        
        try:
            # Get A records
            ips = socket.gethostbyname_ex(domain)
            records['A'] = ips[2]
            
            # Get hostname aliases
            if ips[1]:
                records['CNAME'] = ips[1]
                
        except socket.gaierror as e:
            return DNSResult(
                domain=domain,
                records={},
                success=False,
                error=f"DNS lookup failed: {str(e)}"
            )
        except Exception as e:
            return DNSResult(
                domain=domain,
                records={},
                success=False,
                error=f"Lookup error: {str(e)}"
            )
        
        return DNSResult(
            domain=domain,
            records=records,
            success=True,
            error="Note: Limited record types available (install dnspython for full support)"
        )
    
    def reverse_lookup(self, ip: str) -> DNSResult:
        """
        Perform reverse DNS lookup.
        
        Args:
            ip: IP address to lookup
            
        Returns:
            DNSResult with PTR record
        """
        records = {}
        
        if HAS_DNSPYTHON:
            try:
                rev_name = dns.reversename.from_address(ip)
                answers = self.resolver.resolve(rev_name, 'PTR')
                records['PTR'] = [str(rdata) for rdata in answers]
                
                return DNSResult(
                    domain=ip,
                    records=records,
                    success=True
                )
            except Exception as e:
                return DNSResult(
                    domain=ip,
                    records={},
                    success=False,
                    error=f"Reverse lookup failed: {str(e)}"
                )
        else:
            try:
                hostname, _, _ = socket.gethostbyaddr(ip)
                records['PTR'] = [hostname]
                return DNSResult(
                    domain=ip,
                    records=records,
                    success=True
                )
            except socket.herror:
                return DNSResult(
                    domain=ip,
                    records={},
                    success=False,
                    error="No reverse DNS record found"
                )
            except Exception as e:
                return DNSResult(
                    domain=ip,
                    records={},
                    success=False,
                    error=f"Reverse lookup failed: {str(e)}"
                )
    
    def get_all_records(self, domain: str) -> DNSResult:
        """Get all available DNS records."""
        return self.lookup(domain, self.SUPPORTED_RECORD_TYPES)
    
    def format_output(self, result: DNSResult) -> str:
        """Format DNS result for display."""
        lines = [
            f"=== DNS LOOKUP RESULTS ===",
            f"Domain: {result.domain}"
        ]
        
        if result.query_time_ms:
            lines.append(f"Query Time: {result.query_time_ms}ms")
        
        if not result.success:
            lines.append(f"Status: Failed")
            lines.append(f"Error: {result.error}")
            return '\n'.join(lines)
        
        lines.append(f"Status: Success")
        lines.append("")
        
        for rtype, values in result.records.items():
            lines.append(f"=== {rtype} Records ===")
            for value in values:
                lines.append(f"  {value}")
            lines.append("")
        
        if result.error:
            lines.append(f"Note: {result.error}")
        
        return '\n'.join(lines)


# Convenience function
def dns_lookup(domain: str) -> Dict:
    """Quick DNS lookup."""
    tool = DNSLookupTool()
    result = tool.lookup(domain)
    return {
        'domain': result.domain,
        'success': result.success,
        'records': result.records,
        'error': result.error
    }

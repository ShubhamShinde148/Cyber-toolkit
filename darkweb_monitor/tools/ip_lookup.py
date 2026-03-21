"""
IP Intelligence Lookup Tool
Lookup IP address information including geolocation, ASN, and threat data.
"""

import socket
import re
from typing import Dict, Optional, List
from dataclasses import dataclass
import json

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


@dataclass
class IPInfo:
    """IP address information."""
    ip: str
    hostname: Optional[str]
    ip_type: str  # 'IPv4', 'IPv6', 'Private', 'Reserved'
    is_valid: bool
    
    # Geolocation
    country: Optional[str] = None
    country_code: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timezone: Optional[str] = None
    
    # Network info
    asn: Optional[str] = None
    org: Optional[str] = None
    isp: Optional[str] = None
    
    # Classification
    is_private: bool = False
    is_reserved: bool = False
    is_loopback: bool = False
    is_datacenter: bool = False
    is_vpn: bool = False
    is_proxy: bool = False
    is_tor: bool = False
    
    error: Optional[str] = None


class IPLookupTool:
    """IP address intelligence lookup."""
    
    # Private IP ranges
    PRIVATE_RANGES = [
        ('10.0.0.0', '10.255.255.255'),
        ('172.16.0.0', '172.31.255.255'),
        ('192.168.0.0', '192.168.255.255'),
    ]
    
    # Reserved IP ranges
    RESERVED_RANGES = [
        ('0.0.0.0', '0.255.255.255'),       # "This" network
        ('127.0.0.0', '127.255.255.255'),   # Loopback
        ('169.254.0.0', '169.254.255.255'), # Link-local
        ('224.0.0.0', '239.255.255.255'),   # Multicast
        ('240.0.0.0', '255.255.255.255'),   # Reserved
    ]
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
    
    def _is_valid_ip(self, ip: str) -> bool:
        """Check if string is a valid IP address."""
        # IPv4
        ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if re.match(ipv4_pattern, ip):
            parts = ip.split('.')
            return all(0 <= int(part) <= 255 for part in parts)
        
        # IPv6
        try:
            socket.inet_pton(socket.AF_INET6, ip)
            return True
        except socket.error:
            pass
        
        return False
    
    def _ip_to_int(self, ip: str) -> int:
        """Convert IP address to integer."""
        parts = ip.split('.')
        return sum(int(part) << (8 * (3 - i)) for i, part in enumerate(parts))
    
    def _is_private(self, ip: str) -> bool:
        """Check if IP is in private range."""
        try:
            ip_int = self._ip_to_int(ip)
            for start, end in self.PRIVATE_RANGES:
                if self._ip_to_int(start) <= ip_int <= self._ip_to_int(end):
                    return True
        except Exception:
            pass
        return False
    
    def _is_reserved(self, ip: str) -> bool:
        """Check if IP is in reserved range."""
        try:
            ip_int = self._ip_to_int(ip)
            for start, end in self.RESERVED_RANGES:
                if self._ip_to_int(start) <= ip_int <= self._ip_to_int(end):
                    return True
        except Exception:
            pass
        return False
    
    def _get_hostname(self, ip: str) -> Optional[str]:
        """Reverse DNS lookup."""
        try:
            hostname, _, _ = socket.gethostbyaddr(ip)
            return hostname
        except socket.herror:
            return None
        except Exception:
            return None
    
    def lookup(self, ip: str) -> IPInfo:
        """
        Perform IP lookup with all available information.
        
        Args:
            ip: IP address to lookup
            
        Returns:
            IPInfo with all available data
        """
        ip = ip.strip()
        
        # Validate IP
        if not self._is_valid_ip(ip):
            return IPInfo(
                ip=ip,
                hostname=None,
                ip_type='Invalid',
                is_valid=False,
                error="Invalid IP address format"
            )
        
        # Determine IP type
        is_ipv6 = ':' in ip
        is_private = not is_ipv6 and self._is_private(ip)
        is_reserved = not is_ipv6 and self._is_reserved(ip)
        is_loopback = ip.startswith('127.') or ip == '::1'
        
        if is_ipv6:
            ip_type = 'IPv6'
        elif is_private:
            ip_type = 'Private'
        elif is_reserved:
            ip_type = 'Reserved'
        else:
            ip_type = 'IPv4'
        
        # Get hostname
        hostname = self._get_hostname(ip)
        
        # For private/reserved IPs, return basic info
        if is_private or is_reserved or is_loopback:
            return IPInfo(
                ip=ip,
                hostname=hostname,
                ip_type=ip_type,
                is_valid=True,
                is_private=is_private,
                is_reserved=is_reserved,
                is_loopback=is_loopback
            )
        
        # Try to get geolocation data
        geo_data = self._lookup_geolocation(ip)
        
        return IPInfo(
            ip=ip,
            hostname=hostname,
            ip_type=ip_type,
            is_valid=True,
            is_private=is_private,
            is_reserved=is_reserved,
            is_loopback=is_loopback,
            **geo_data
        )
    
    def _lookup_geolocation(self, ip: str) -> Dict:
        """Lookup geolocation using free API."""
        if not HAS_REQUESTS:
            return {'error': 'requests library not available'}
        
        try:
            # Using ip-api.com (free, no API key needed)
            response = requests.get(
                f'http://ip-api.com/json/{ip}',
                timeout=self.timeout,
                params={
                    'fields': 'status,message,country,countryCode,region,regionName,city,lat,lon,timezone,isp,org,as,proxy,hosting'
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'success':
                    return {
                        'country': data.get('country'),
                        'country_code': data.get('countryCode'),
                        'region': data.get('regionName'),
                        'city': data.get('city'),
                        'latitude': data.get('lat'),
                        'longitude': data.get('lon'),
                        'timezone': data.get('timezone'),
                        'isp': data.get('isp'),
                        'org': data.get('org'),
                        'asn': data.get('as'),
                        'is_proxy': data.get('proxy', False),
                        'is_datacenter': data.get('hosting', False)
                    }
                else:
                    return {'error': data.get('message', 'Lookup failed')}
            
            return {'error': f'API returned status {response.status_code}'}
            
        except requests.exceptions.Timeout:
            return {'error': 'Request timed out'}
        except requests.exceptions.RequestException as e:
            return {'error': f'Request failed: {str(e)}'}
        except Exception as e:
            return {'error': f'Lookup failed: {str(e)}'}
    
    def format_output(self, info: IPInfo) -> str:
        """Format IP info for display."""
        lines = [
            f"=== IP INFORMATION ===",
            f"IP Address: {info.ip}",
            f"Type: {info.ip_type}",
            f"Valid: {'Yes' if info.is_valid else 'No'}"
        ]
        
        if info.hostname:
            lines.append(f"Hostname: {info.hostname}")
        
        if info.error:
            lines.append(f"Error: {info.error}")
            return '\n'.join(lines)
        
        if info.is_private:
            lines.append("Status: Private IP address")
            return '\n'.join(lines)
        
        if info.is_reserved or info.is_loopback:
            lines.append("Status: Reserved/Loopback address")
            return '\n'.join(lines)
        
        lines.append("")
        lines.append("=== GEOLOCATION ===")
        
        if info.country:
            lines.append(f"Country: {info.country} ({info.country_code})")
        if info.region:
            lines.append(f"Region: {info.region}")
        if info.city:
            lines.append(f"City: {info.city}")
        if info.latitude and info.longitude:
            lines.append(f"Coordinates: {info.latitude}, {info.longitude}")
        if info.timezone:
            lines.append(f"Timezone: {info.timezone}")
        
        lines.append("")
        lines.append("=== NETWORK ===")
        
        if info.isp:
            lines.append(f"ISP: {info.isp}")
        if info.org:
            lines.append(f"Organization: {info.org}")
        if info.asn:
            lines.append(f"ASN: {info.asn}")
        
        if info.is_proxy or info.is_datacenter or info.is_vpn or info.is_tor:
            lines.append("")
            lines.append("=== THREAT INDICATORS ===")
            if info.is_proxy:
                lines.append("⚠️  Proxy detected")
            if info.is_datacenter:
                lines.append("⚠️  Datacenter/Hosting IP")
            if info.is_vpn:
                lines.append("⚠️  VPN detected")
            if info.is_tor:
                lines.append("⚠️  Tor exit node")
        
        return '\n'.join(lines)


# Convenience function
def lookup_ip(ip: str) -> Dict:
    """Quick IP lookup."""
    tool = IPLookupTool()
    info = tool.lookup(ip)
    return {
        'ip': info.ip,
        'valid': info.is_valid,
        'type': info.ip_type,
        'hostname': info.hostname,
        'country': info.country,
        'city': info.city,
        'isp': info.isp,
        'error': info.error
    }

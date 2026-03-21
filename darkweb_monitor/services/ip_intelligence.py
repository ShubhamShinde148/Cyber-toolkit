"""
IP Intelligence Module
======================
Provides comprehensive IP address analysis including:
- Geolocation lookup
- ISP/ASN information
- Threat intelligence and blacklist checking
- VPN/Proxy/Tor detection
- Abuse history

Uses multiple free APIs for maximum accuracy.
"""

import requests
import socket
import re
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import ipaddress


@dataclass
class IPInfo:
    """Container for IP intelligence data."""
    ip: str
    version: int
    geolocation: Dict
    network: Dict
    threats: Dict
    reputation: Dict


class IPIntelligence:
    """
    Comprehensive IP address intelligence analyzer.
    
    Features:
    - IP geolocation (country, city, coordinates)
    - ISP and ASN information
    - VPN/Proxy/Tor detection
    - Blacklist checking
    - Threat scoring
    """
    
    # Known threat IP ranges (simplified examples)
    KNOWN_THREAT_RANGES = [
        # These are example ranges - in production, use threat feeds
    ]
    
    # Blacklist services to check
    BLACKLISTS = [
        'zen.spamhaus.org',
        'bl.spamcop.net',
        'b.barracudacentral.org',
        'dnsbl.sorbs.net',
        'spam.dnsbl.sorbs.net'
    ]
    
    def __init__(self, timeout: int = 10):
        """
        Initialize IP Intelligence module.
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'DarkWeb Monitor IP Intel/1.0',
            'Accept': 'application/json'
        })
    
    def validate_ip(self, ip: str) -> tuple[bool, str, int]:
        """
        Validate and classify IP address.
        
        Args:
            ip: IP address to validate
            
        Returns:
            Tuple of (is_valid, cleaned_ip/error, ip_version)
        """
        if not ip:
            return False, "IP address cannot be empty", 0
        
        ip = ip.strip()
        
        try:
            ip_obj = ipaddress.ip_address(ip)
            version = ip_obj.version
            
            # Check if it's a private IP
            if ip_obj.is_private:
                return True, ip, version  # Still valid, but limited info
            
            if ip_obj.is_loopback:
                return False, "Cannot analyze loopback address", 0
            
            if ip_obj.is_multicast:
                return False, "Cannot analyze multicast address", 0
            
            return True, ip, version
            
        except ValueError:
            # Check if it's a hostname
            hostname_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z]{2,})+$'
            if re.match(hostname_pattern, ip):
                try:
                    resolved_ip = socket.gethostbyname(ip)
                    return True, resolved_ip, 4
                except socket.gaierror:
                    return False, f"Could not resolve hostname: {ip}", 0
            
            return False, "Invalid IP address format", 0
    
    def _get_geolocation(self, ip: str) -> Dict:
        """
        Get geolocation data for IP address.
        
        Args:
            ip: IP address
            
        Returns:
            Dictionary with geolocation data
        """
        geo_data = {
            'country': None,
            'country_code': None,
            'region': None,
            'city': None,
            'latitude': None,
            'longitude': None,
            'timezone': None,
            'postal_code': None
        }
        
        try:
            # Using ip-api.com (free, no key required)
            response = self.session.get(
                f"http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,mobile,proxy,hosting",
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'success':
                    geo_data = {
                        'country': data.get('country'),
                        'country_code': data.get('countryCode'),
                        'region': data.get('regionName'),
                        'city': data.get('city'),
                        'latitude': data.get('lat'),
                        'longitude': data.get('lon'),
                        'timezone': data.get('timezone'),
                        'postal_code': data.get('zip'),
                        'is_mobile': data.get('mobile', False),
                        'is_proxy': data.get('proxy', False),
                        'is_hosting': data.get('hosting', False),
                        'isp': data.get('isp'),
                        'org': data.get('org'),
                        'asn': data.get('as')
                    }
                else:
                    geo_data['error'] = data.get('message', 'Unknown error')
                    
        except Exception as e:
            geo_data['error'] = str(e)
        
        return geo_data
    
    def _get_network_info(self, ip: str) -> Dict:
        """
        Get network/ISP information for IP.
        
        Args:
            ip: IP address
            
        Returns:
            Dictionary with network information
        """
        network_info = {
            'isp': None,
            'organization': None,
            'asn': None,
            'asn_name': None,
            'network_type': 'unknown'
        }
        
        try:
            # Try to get additional network info from ipinfo.io
            response = self.session.get(
                f"https://ipinfo.io/{ip}/json",
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                
                network_info['isp'] = data.get('org', '').split(' ', 1)[-1] if data.get('org') else None
                network_info['organization'] = data.get('org')
                network_info['hostname'] = data.get('hostname')
                
                # Parse ASN from org field (format: "AS12345 Company Name")
                org = data.get('org', '')
                if org.startswith('AS'):
                    parts = org.split(' ', 1)
                    network_info['asn'] = parts[0]
                    network_info['asn_name'] = parts[1] if len(parts) > 1 else None
                
                # Determine network type
                org_lower = org.lower()
                if any(x in org_lower for x in ['hosting', 'cloud', 'server', 'data center', 'datacenter']):
                    network_info['network_type'] = 'hosting'
                elif any(x in org_lower for x in ['mobile', 'cellular', 'wireless']):
                    network_info['network_type'] = 'mobile'
                elif any(x in org_lower for x in ['vpn', 'proxy', 'anonymizer']):
                    network_info['network_type'] = 'vpn_proxy'
                else:
                    network_info['network_type'] = 'residential_business'
                    
        except Exception as e:
            network_info['error'] = str(e)
        
        return network_info
    
    def _check_blacklists(self, ip: str) -> Dict:
        """
        Check IP against DNS blacklists.
        
        Args:
            ip: IP address (IPv4 only for DNSBL)
            
        Returns:
            Dictionary with blacklist results
        """
        blacklist_results = {
            'is_blacklisted': False,
            'blacklist_count': 0,
            'blacklisted_on': [],
            'clean_on': [],
            'checks_performed': 0
        }
        
        try:
            # Only works with IPv4
            ip_obj = ipaddress.ip_address(ip)
            if ip_obj.version != 4:
                blacklist_results['note'] = 'DNSBL checks only support IPv4'
                return blacklist_results
            
            # Reverse IP for DNSBL query
            reversed_ip = '.'.join(reversed(ip.split('.')))
            
            for blacklist in self.BLACKLISTS:
                try:
                    query = f"{reversed_ip}.{blacklist}"
                    socket.gethostbyname(query)
                    
                    # If we get a response, IP is listed
                    blacklist_results['is_blacklisted'] = True
                    blacklist_results['blacklist_count'] += 1
                    blacklist_results['blacklisted_on'].append(blacklist)
                    
                except socket.gaierror:
                    # No response means not listed
                    blacklist_results['clean_on'].append(blacklist)
                    
                blacklist_results['checks_performed'] += 1
                
        except Exception as e:
            blacklist_results['error'] = str(e)
        
        return blacklist_results
    
    def _analyze_threats(self, ip: str, geo_data: Dict, network_info: Dict, blacklists: Dict) -> Dict:
        """
        Analyze threat level based on collected data.
        
        Args:
            ip: IP address
            geo_data: Geolocation data
            network_info: Network information
            blacklists: Blacklist results
            
        Returns:
            Dictionary with threat analysis
        """
        threat_analysis = {
            'threat_score': 0,
            'threat_level': 'low',
            'risk_factors': [],
            'is_vpn': False,
            'is_proxy': False,
            'is_tor': False,
            'is_hosting': False,
            'is_mobile': False
        }
        
        # Check for VPN/Proxy/Hosting
        if geo_data.get('is_proxy'):
            threat_analysis['is_proxy'] = True
            threat_analysis['threat_score'] += 20
            threat_analysis['risk_factors'].append('Proxy/VPN detected')
        
        if geo_data.get('is_hosting'):
            threat_analysis['is_hosting'] = True
            threat_analysis['threat_score'] += 15
            threat_analysis['risk_factors'].append('Hosting/Data center IP')
        
        if geo_data.get('is_mobile'):
            threat_analysis['is_mobile'] = True
            # Mobile IPs are less suspicious
        
        # Network type analysis
        if network_info.get('network_type') == 'vpn_proxy':
            threat_analysis['is_vpn'] = True
            threat_analysis['threat_score'] += 25
            if 'Proxy/VPN detected' not in threat_analysis['risk_factors']:
                threat_analysis['risk_factors'].append('VPN service provider')
        
        # Blacklist score
        if blacklists.get('is_blacklisted'):
            bl_count = blacklists.get('blacklist_count', 0)
            threat_analysis['threat_score'] += min(bl_count * 15, 45)
            threat_analysis['risk_factors'].append(f'Listed on {bl_count} blacklist(s)')
        
        # Check for Tor exit nodes (simplified check via known ASNs)
        asn = network_info.get('asn', '')
        org = str(network_info.get('organization', '')).lower()
        
        if 'tor' in org or 'torservers' in org:
            threat_analysis['is_tor'] = True
            threat_analysis['threat_score'] += 35
            threat_analysis['risk_factors'].append('Tor network detected')
        
        # Calculate threat level
        score = threat_analysis['threat_score']
        if score >= 70:
            threat_analysis['threat_level'] = 'critical'
        elif score >= 50:
            threat_analysis['threat_level'] = 'high'
        elif score >= 30:
            threat_analysis['threat_level'] = 'medium'
        elif score >= 10:
            threat_analysis['threat_level'] = 'low'
        else:
            threat_analysis['threat_level'] = 'minimal'
        
        return threat_analysis
    
    def _calculate_reputation(self, threat_analysis: Dict, blacklists: Dict) -> Dict:
        """
        Calculate overall IP reputation score.
        
        Args:
            threat_analysis: Threat analysis data
            blacklists: Blacklist results
            
        Returns:
            Dictionary with reputation data
        """
        # Start with perfect score and subtract for issues
        reputation_score = 100
        
        # Subtract for threat score
        reputation_score -= threat_analysis.get('threat_score', 0)
        
        # Ensure score stays in valid range
        reputation_score = max(0, min(100, reputation_score))
        
        # Determine reputation category
        if reputation_score >= 90:
            category = 'excellent'
            description = 'This IP has an excellent reputation with no known issues.'
        elif reputation_score >= 70:
            category = 'good'
            description = 'This IP has a good reputation with minor concerns.'
        elif reputation_score >= 50:
            category = 'fair'
            description = 'This IP has some reputation issues that warrant caution.'
        elif reputation_score >= 30:
            category = 'poor'
            description = 'This IP has significant reputation issues.'
        else:
            category = 'bad'
            description = 'This IP has a very poor reputation and should be treated with extreme caution.'
        
        return {
            'score': reputation_score,
            'category': category,
            'description': description,
            'blacklist_free': not blacklists.get('is_blacklisted', False)
        }
    
    def analyze(self, ip: str) -> Dict:
        """
        Perform comprehensive IP address analysis.
        
        Args:
            ip: IP address or hostname to analyze
            
        Returns:
            Dictionary with complete analysis results
        """
        # Validate IP
        is_valid, result, version = self.validate_ip(ip)
        if not is_valid:
            return {
                'success': False,
                'error': result,
                'ip': ip
            }
        
        analyzed_ip = result
        is_private = False
        
        try:
            ip_obj = ipaddress.ip_address(analyzed_ip)
            is_private = ip_obj.is_private
        except ValueError:
            pass
        
        if is_private:
            return {
                'success': True,
                'ip': analyzed_ip,
                'ip_version': version,
                'is_private': True,
                'note': 'Private IP address - limited intelligence available',
                'geolocation': {'country': 'Private Network'},
                'network': {'network_type': 'private'},
                'threats': {'threat_level': 'minimal', 'threat_score': 0},
                'reputation': {'score': 100, 'category': 'private'}
            }
        
        # Gather intelligence
        geo_data = self._get_geolocation(analyzed_ip)
        network_info = self._get_network_info(analyzed_ip)
        blacklists = self._check_blacklists(analyzed_ip)
        threat_analysis = self._analyze_threats(analyzed_ip, geo_data, network_info, blacklists)
        reputation = self._calculate_reputation(threat_analysis, blacklists)
        
        return {
            'success': True,
            'ip': analyzed_ip,
            'ip_version': version,
            'is_private': False,
            'analyzed_at': datetime.now().isoformat(),
            'geolocation': {
                'country': geo_data.get('country'),
                'country_code': geo_data.get('country_code'),
                'region': geo_data.get('region'),
                'city': geo_data.get('city'),
                'coordinates': {
                    'latitude': geo_data.get('latitude'),
                    'longitude': geo_data.get('longitude')
                },
                'timezone': geo_data.get('timezone'),
                'postal_code': geo_data.get('postal_code')
            },
            'network': {
                'isp': geo_data.get('isp') or network_info.get('isp'),
                'organization': geo_data.get('org') or network_info.get('organization'),
                'asn': geo_data.get('asn') or network_info.get('asn'),
                'hostname': network_info.get('hostname'),
                'network_type': network_info.get('network_type')
            },
            'threats': {
                'threat_level': threat_analysis['threat_level'],
                'threat_score': threat_analysis['threat_score'],
                'is_vpn': threat_analysis['is_vpn'],
                'is_proxy': threat_analysis['is_proxy'],
                'is_tor': threat_analysis['is_tor'],
                'is_hosting': threat_analysis['is_hosting'],
                'is_mobile': threat_analysis['is_mobile'],
                'risk_factors': threat_analysis['risk_factors']
            },
            'blacklists': {
                'is_blacklisted': blacklists['is_blacklisted'],
                'blacklist_count': blacklists['blacklist_count'],
                'listed_on': blacklists['blacklisted_on'],
                'checks_performed': blacklists['checks_performed']
            },
            'reputation': reputation,
            'summary': {
                'location': f"{geo_data.get('city', 'Unknown')}, {geo_data.get('country', 'Unknown')}",
                'risk_level': threat_analysis['threat_level'],
                'reputation_score': reputation['score'],
                'is_safe': reputation['score'] >= 70 and not blacklists['is_blacklisted']
            }
        }
    
    def quick_lookup(self, ip: str) -> Dict:
        """
        Quick IP lookup with essential information only.
        
        Args:
            ip: IP address
            
        Returns:
            Dictionary with basic IP information
        """
        is_valid, result, version = self.validate_ip(ip)
        if not is_valid:
            return {'success': False, 'error': result}
        
        geo_data = self._get_geolocation(result)
        
        return {
            'success': True,
            'ip': result,
            'country': geo_data.get('country'),
            'city': geo_data.get('city'),
            'isp': geo_data.get('isp'),
            'is_proxy': geo_data.get('is_proxy', False),
            'is_hosting': geo_data.get('is_hosting', False)
        }


# Example usage
if __name__ == "__main__":
    intel = IPIntelligence(timeout=10)
    
    print("=" * 60)
    print("IP Intelligence Module - Test")
    print("=" * 60)
    
    # Test with Google's public DNS
    test_ip = "8.8.8.8"
    print(f"\nAnalyzing IP: {test_ip}")
    print("-" * 40)
    
    results = intel.analyze(test_ip)
    
    if results['success']:
        print(f"Location: {results['summary']['location']}")
        print(f"ISP: {results['network']['isp']}")
        print(f"Organization: {results['network']['organization']}")
        print(f"Threat Level: {results['threats']['threat_level']}")
        print(f"Reputation Score: {results['reputation']['score']}/100")
        print(f"Reputation: {results['reputation']['category']}")
        
        if results['threats']['risk_factors']:
            print("\nRisk Factors:")
            for factor in results['threats']['risk_factors']:
                print(f"  - {factor}")
        
        if results['blacklists']['is_blacklisted']:
            print(f"\n⚠️ BLACKLISTED on {results['blacklists']['blacklist_count']} list(s)")
    else:
        print(f"Error: {results['error']}")

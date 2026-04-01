"""
IP Threat Intelligence Module
==============================
SOC-Level multi-source threat intelligence scanner.
Queries AbuseIPDB, AlienVault OTX, GreyNoise, and Shodan
to produce a unified risk score and threat report.
"""

import os
import requests
import ipaddress
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime


@dataclass
class ThreatIntelReport:
    """Unified threat intelligence report for an IP address."""
    ip: str
    risk_score: int = 0
    threat_level: str = 'Unknown'
    # AbuseIPDB
    abuse_confidence: int = 0
    abuse_total_reports: int = 0
    abuse_country: str = ''
    abuse_isp: str = ''
    abuse_domain: str = ''
    abuse_is_tor: bool = False
    abuse_last_reported: str = ''
    # OTX
    otx_pulse_count: int = 0
    otx_reputation: int = 0
    otx_pulses: List[Dict] = field(default_factory=list)
    otx_malware_count: int = 0
    # GreyNoise
    greynoise_classification: str = ''
    greynoise_noise: bool = False
    greynoise_riot: bool = False
    greynoise_name: str = ''
    greynoise_message: str = ''
    # Shodan
    shodan_ports: List[int] = field(default_factory=list)
    shodan_hostnames: List[str] = field(default_factory=list)
    shodan_org: str = ''
    shodan_os: str = ''
    shodan_vulns: List[str] = field(default_factory=list)
    # Meta
    scan_timestamp: str = ''
    sources_queried: List[str] = field(default_factory=list)
    errors: Dict[str, str] = field(default_factory=dict)


class IPThreatIntelScanner:
    """
    SOC-level IP threat intelligence scanner.
    Aggregates data from four threat intelligence APIs.
    """

    TIMEOUT = 10  # seconds per API call

    def __init__(self):
        self.abuseipdb_key = os.getenv('ABUSEIPDB_API_KEY', '')
        self.otx_key = os.getenv('OTX_API_KEY', '')
        self.greynoise_key = os.getenv('GREYNOISE_API_KEY', '')
        self.shodan_key = os.getenv('SHODAN_API_KEY', '')

    @staticmethod
    def validate_ip(ip: str) -> bool:
        """Validate that the string is a proper public IPv4/IPv6 address."""
        try:
            addr = ipaddress.ip_address(ip)
            return addr.is_global
        except ValueError:
            return False

    # ------------------------------------------------------------------
    # Individual API queries
    # ------------------------------------------------------------------

    def _query_abuseipdb(self, ip: str, report: ThreatIntelReport):
        if not self.abuseipdb_key:
            report.errors['abuseipdb'] = 'API key not configured'
            return
        try:
            resp = requests.get(
                'https://api.abuseipdb.com/api/v2/check',
                headers={'Key': self.abuseipdb_key, 'Accept': 'application/json'},
                params={'ipAddress': ip, 'maxAgeInDays': '90', 'verbose': ''},
                timeout=self.TIMEOUT,
            )
            if resp.status_code == 200:
                data = resp.json().get('data', {})
                report.abuse_confidence = data.get('abuseConfidenceScore', 0)
                report.abuse_total_reports = data.get('totalReports', 0)
                report.abuse_country = data.get('countryCode', '')
                report.abuse_isp = data.get('isp', '')
                report.abuse_domain = data.get('domain', '')
                report.abuse_is_tor = data.get('isTor', False)
                report.abuse_last_reported = data.get('lastReportedAt', '')
                report.sources_queried.append('AbuseIPDB')
            else:
                report.errors['abuseipdb'] = f'HTTP {resp.status_code}'
        except requests.RequestException as exc:
            report.errors['abuseipdb'] = str(exc)

    def _query_otx(self, ip: str, report: ThreatIntelReport):
        if not self.otx_key:
            report.errors['otx'] = 'API key not configured'
            return
        try:
            resp = requests.get(
                f'https://otx.alienvault.com/api/v1/indicators/IPv4/{ip}/general',
                headers={'X-OTX-API-KEY': self.otx_key, 'Accept': 'application/json'},
                timeout=self.TIMEOUT,
            )
            if resp.status_code == 200:
                data = resp.json()
                report.otx_pulse_count = data.get('pulse_info', {}).get('count', 0)
                report.otx_reputation = data.get('reputation', 0)
                pulses = data.get('pulse_info', {}).get('pulses', [])
                report.otx_pulses = [
                    {'name': p.get('name', ''), 'created': p.get('created', '')}
                    for p in pulses[:10]
                ]
                # Count malware-related pulses
                report.otx_malware_count = sum(
                    1 for p in pulses
                    if any(t.get('name', '').lower() in ('malware', 'malicious host', 'c2')
                           for t in p.get('tags', []) if isinstance(t, dict))
                    or any(kw in p.get('name', '').lower()
                           for kw in ('malware', 'botnet', 'c2', 'ransomware', 'trojan'))
                )
                report.sources_queried.append('AlienVault OTX')
            else:
                report.errors['otx'] = f'HTTP {resp.status_code}'
        except requests.RequestException as exc:
            report.errors['otx'] = str(exc)

    def _query_greynoise(self, ip: str, report: ThreatIntelReport):
        if not self.greynoise_key:
            report.errors['greynoise'] = 'API key not configured'
            return
        try:
            resp = requests.get(
                f'https://api.greynoise.io/v3/community/{ip}',
                headers={'key': self.greynoise_key, 'Accept': 'application/json'},
                timeout=self.TIMEOUT,
            )
            if resp.status_code == 200:
                data = resp.json()
                report.greynoise_classification = data.get('classification', '')
                report.greynoise_noise = data.get('noise', False)
                report.greynoise_riot = data.get('riot', False)
                report.greynoise_name = data.get('name', '')
                report.greynoise_message = data.get('message', '')
                report.sources_queried.append('GreyNoise')
            elif resp.status_code == 404:
                # IP not found in GreyNoise — not noise
                report.greynoise_noise = False
                report.greynoise_classification = 'unknown'
                report.greynoise_message = 'IP not observed by GreyNoise'
                report.sources_queried.append('GreyNoise')
            else:
                report.errors['greynoise'] = f'HTTP {resp.status_code}'
        except requests.RequestException as exc:
            report.errors['greynoise'] = str(exc)

    def _query_shodan(self, ip: str, report: ThreatIntelReport):
        if not self.shodan_key:
            report.errors['shodan'] = 'API key not configured'
            return
        try:
            resp = requests.get(
                f'https://api.shodan.io/shodan/host/{ip}',
                params={'key': self.shodan_key},
                timeout=self.TIMEOUT,
            )
            if resp.status_code == 200:
                data = resp.json()
                report.shodan_ports = data.get('ports', [])
                report.shodan_hostnames = data.get('hostnames', [])
                report.shodan_org = data.get('org', '')
                report.shodan_os = data.get('os', '') or ''
                report.shodan_vulns = list(data.get('vulns', []))[:20]
                report.sources_queried.append('Shodan')
            elif resp.status_code == 404:
                report.shodan_ports = []
                report.sources_queried.append('Shodan')
            else:
                report.errors['shodan'] = f'HTTP {resp.status_code}'
        except requests.RequestException as exc:
            report.errors['shodan'] = str(exc)

    # ------------------------------------------------------------------
    # Threat Score Engine
    # ------------------------------------------------------------------

    @staticmethod
    def calculate_risk_score(report: ThreatIntelReport) -> int:
        """
        Calculate a unified risk score (0-100) from all sources.
        Weighted:
          AbuseIPDB confidence  → 40 %
          OTX pulse count       → 20 %
          GreyNoise noise/class → 20 %
          Shodan exposure       → 20 %
        """
        score = 0.0

        # --- AbuseIPDB (up to 40 pts) ---
        score += min(report.abuse_confidence * 0.4, 40)

        # --- OTX (up to 20 pts) ---
        pulse_score = min(report.otx_pulse_count * 2, 15)
        if report.otx_malware_count > 0:
            pulse_score += 5
        score += min(pulse_score, 20)

        # --- GreyNoise (up to 20 pts) ---
        if report.greynoise_noise:
            score += 10
        classification = report.greynoise_classification.lower()
        if classification == 'malicious':
            score += 10
        elif classification == 'unknown':
            score += 5

        # --- Shodan (up to 20 pts) ---
        port_count = len(report.shodan_ports)
        if port_count > 0:
            score += min(port_count * 2, 10)
        if len(report.shodan_vulns) > 0:
            score += min(len(report.shodan_vulns) * 2, 10)

        # Tor exit node bonus
        if report.abuse_is_tor:
            score += 5

        return max(0, min(int(round(score)), 100))

    @staticmethod
    def classify_threat(risk_score: int) -> str:
        if risk_score >= 70:
            return 'Critical'
        if risk_score >= 50:
            return 'High'
        if risk_score >= 20:
            return 'Medium'
        return 'Low'

    # ------------------------------------------------------------------
    # Main scan entry point
    # ------------------------------------------------------------------

    def scan(self, ip: str) -> ThreatIntelReport:
        """Run a full multi-source threat intelligence scan."""
        report = ThreatIntelReport(ip=ip, scan_timestamp=datetime.now().isoformat())

        self._query_abuseipdb(ip, report)
        self._query_otx(ip, report)
        self._query_greynoise(ip, report)
        self._query_shodan(ip, report)

        report.risk_score = self.calculate_risk_score(report)
        report.threat_level = self.classify_threat(report.risk_score)

        return report

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    @staticmethod
    def report_to_dict(report: ThreatIntelReport) -> dict:
        """Convert report to a JSON-serialisable dict."""
        return {
            'ip': report.ip,
            'risk_score': report.risk_score,
            'threat_level': report.threat_level,
            'scan_timestamp': report.scan_timestamp,
            'sources_queried': report.sources_queried,
            'errors': report.errors,
            'abuseipdb': {
                'confidence_score': report.abuse_confidence,
                'total_reports': report.abuse_total_reports,
                'country': report.abuse_country,
                'isp': report.abuse_isp,
                'domain': report.abuse_domain,
                'is_tor': report.abuse_is_tor,
                'last_reported': report.abuse_last_reported,
            },
            'otx': {
                'pulse_count': report.otx_pulse_count,
                'reputation': report.otx_reputation,
                'malware_count': report.otx_malware_count,
                'pulses': report.otx_pulses,
            },
            'greynoise': {
                'classification': report.greynoise_classification,
                'noise': report.greynoise_noise,
                'riot': report.greynoise_riot,
                'name': report.greynoise_name,
                'message': report.greynoise_message,
            },
            'shodan': {
                'ports': report.shodan_ports,
                'hostnames': report.shodan_hostnames,
                'organization': report.shodan_org,
                'os': report.shodan_os,
                'vulns': report.shodan_vulns,
            },
        }

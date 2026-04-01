"""
Defensive web assessment tools.
Safe-by-default checks with strict host allowlisting.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
import socket
import ssl
import time
from typing import Dict, List, Optional
from urllib.parse import urlparse, urlunparse

import requests


SECURITY_HEADERS = (
    "strict-transport-security",
    "content-security-policy",
    "x-content-type-options",
    "x-frame-options",
    "referrer-policy",
    "permissions-policy",
)


@dataclass
class DefensiveResult:
    success: bool
    error: Optional[str] = None


class DefensiveBase:
    def __init__(self, allowlist_hosts: List[str], timeout: int = 6):
        self.timeout = timeout
        normalized = []
        for host in allowlist_hosts or []:
            h = (host or "").strip().lower()
            if h:
                normalized.append(h)
        self.allowlist_hosts = sorted(set(normalized))

    def _normalize_target(self, target: str, default_scheme: str = "https") -> Optional[str]:
        t = (target or "").strip()
        if not t:
            return None
        if "://" not in t:
            t = f"{default_scheme}://{t}"

        parsed = urlparse(t)
        if not parsed.hostname:
            return None

        safe_path = parsed.path or "/"
        cleaned = parsed._replace(path=safe_path, params="", query="", fragment="")
        return urlunparse(cleaned)

    def _host_allowed(self, hostname: str) -> bool:
        host = (hostname or "").strip().lower()
        if not host:
            return False
        for allowed in self.allowlist_hosts:
            if host == allowed or host.endswith(f".{allowed}"):
                return True
        return False

    def _resolve_dns(self, hostname: str) -> List[str]:
        ips = set()
        try:
            for family, _, _, _, sockaddr in socket.getaddrinfo(hostname, None):
                ip = None
                if family == socket.AF_INET:
                    ip = sockaddr[0]
                elif family == socket.AF_INET6:
                    ip = sockaddr[0]
                if ip:
                    ips.add(ip)
        except Exception:
            return []
        return sorted(ips)


class AssetHealthChecker(DefensiveBase):
    def check(self, target: str) -> Dict:
        normalized = self._normalize_target(target)
        if not normalized:
            return {"success": False, "error": "Invalid target URL/host"}

        parsed = urlparse(normalized)
        hostname = parsed.hostname or ""
        if not self._host_allowed(hostname):
            return {
                "success": False,
                "error": "Target host is not allowlisted",
                "host": hostname,
                "allowlist": self.allowlist_hosts,
            }

        ips = self._resolve_dns(hostname)
        dns_ok = len(ips) > 0

        http_status = None
        final_url = normalized
        response_ms = None
        server = None
        missing_headers = list(SECURITY_HEADERS)
        present_headers = {}
        request_error = None
        tls_info = self._tls_info(hostname) if parsed.scheme == "https" else None

        try:
            started = time.perf_counter()
            response = requests.get(normalized, timeout=self.timeout, allow_redirects=True)
            response_ms = round((time.perf_counter() - started) * 1000, 1)
            http_status = response.status_code
            final_url = response.url
            server = response.headers.get("Server")

            headers_lower = {k.lower(): v for k, v in response.headers.items()}
            present_headers = {h: headers_lower.get(h) for h in SECURITY_HEADERS if h in headers_lower}
            missing_headers = [h for h in SECURITY_HEADERS if h not in headers_lower]
        except Exception as exc:
            request_error = str(exc)

        healthy = dns_ok and http_status is not None and http_status < 500
        risk = "low"
        if not healthy or request_error:
            risk = "high"
        elif missing_headers:
            risk = "medium"

        return {
            "success": True,
            "target": normalized,
            "host": hostname,
            "allowlisted": True,
            "dns_ok": dns_ok,
            "resolved_ips": ips,
            "http_status": http_status,
            "final_url": final_url,
            "response_ms": response_ms,
            "server": server,
            "security_headers_present": present_headers,
            "security_headers_missing": missing_headers,
            "tls": tls_info,
            "healthy": healthy and not request_error,
            "risk_level": risk,
            "request_error": request_error,
            "checked_at": datetime.now(timezone.utc).isoformat(),
        }

    def _tls_info(self, hostname: str) -> Dict:
        try:
            context = ssl.create_default_context()
            with socket.create_connection((hostname, 443), timeout=self.timeout) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as tls_sock:
                    cert = tls_sock.getpeercert()
                    not_after = cert.get("notAfter")
                    expiry = None
                    days_left = None
                    if not_after:
                        expiry = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
                        days_left = (expiry - datetime.now(timezone.utc)).days
                    return {
                        "enabled": True,
                        "issuer": dict(x[0] for x in cert.get("issuer", ())) if cert.get("issuer") else {},
                        "subject": dict(x[0] for x in cert.get("subject", ())) if cert.get("subject") else {},
                        "expires_at": expiry.isoformat() if expiry else None,
                        "days_until_expiry": days_left,
                    }
        except Exception as exc:
            return {"enabled": False, "error": str(exc)}


class SurfaceAuditTool(DefensiveBase):
    DEFAULT_ROUTES = [
        "/",
        "/dashboard",
        "/tools",
        "/cyber-tools",
        "/quiz",
        "/username-osint",
        "/metadata-extractor",
        "/certificate-history",
        "/about",
    ]

    def audit(self, base_url: str, routes: Optional[List[str]] = None) -> Dict:
        normalized = self._normalize_target(base_url)
        if not normalized:
            return {"success": False, "error": "Invalid base URL"}

        parsed = urlparse(normalized)
        host = parsed.hostname or ""
        if not self._host_allowed(host):
            return {
                "success": False,
                "error": "Base host is not allowlisted",
                "host": host,
                "allowlist": self.allowlist_hosts,
            }

        route_list = routes if isinstance(routes, list) and routes else list(self.DEFAULT_ROUTES)
        cleaned_routes = []
        for route in route_list:
            r = (route or "").strip()
            if not r:
                continue
            if not r.startswith("/"):
                r = "/" + r
            cleaned_routes.append(r)
        cleaned_routes = sorted(set(cleaned_routes))

        findings = []
        summary = {
            "checked": 0,
            "ok": 0,
            "redirects": 0,
            "client_errors": 0,
            "server_errors": 0,
            "request_errors": 0,
        }

        for route in cleaned_routes:
            target = f"{parsed.scheme}://{parsed.netloc}{route}"
            entry = {
                "route": route,
                "url": target,
                "status_code": None,
                "category": "unknown",
                "ok": False,
                "response_ms": None,
                "location": None,
                "error": None,
            }
            try:
                started = time.perf_counter()
                response = requests.get(target, timeout=self.timeout, allow_redirects=False)
                elapsed = round((time.perf_counter() - started) * 1000, 1)
                code = response.status_code
                entry["status_code"] = code
                entry["response_ms"] = elapsed
                entry["location"] = response.headers.get("Location")

                if 200 <= code < 300:
                    entry["category"] = "ok"
                    entry["ok"] = True
                    summary["ok"] += 1
                elif 300 <= code < 400:
                    entry["category"] = "redirect"
                    summary["redirects"] += 1
                elif 400 <= code < 500:
                    entry["category"] = "client_error"
                    summary["client_errors"] += 1
                else:
                    entry["category"] = "server_error"
                    summary["server_errors"] += 1
            except Exception as exc:
                entry["category"] = "request_error"
                entry["error"] = str(exc)
                summary["request_errors"] += 1

            summary["checked"] += 1
            findings.append(entry)

        return {
            "success": True,
            "base_url": f"{parsed.scheme}://{parsed.netloc}",
            "allowlisted": True,
            "routes": findings,
            "summary": summary,
            "checked_at": datetime.now(timezone.utc).isoformat(),
        }

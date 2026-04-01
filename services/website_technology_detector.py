"""Website technology detector based on HTTP response headers."""

import ipaddress
import socket
from urllib.parse import urlsplit, urlunsplit

import requests
from requests import RequestException


class WebsiteTechnologyDetector:
    """Inspect website headers and infer exposed technologies."""

    def __init__(self, timeout=10):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'DarkWebLeakMonitor/1.0',
            'Accept': '*/*'
        })

    def analyze(self, raw_url):
        primary_url, fallback_url = self._prepare_urls(raw_url)
        self._validate_public_target(primary_url)

        request_error = None
        for candidate_url in filter(None, [primary_url, fallback_url]):
            response = None
            try:
                response = self.session.get(
                    candidate_url,
                    timeout=self.timeout,
                    allow_redirects=True,
                    stream=True
                )

                selected_headers = {
                    'Server': response.headers.get('Server'),
                    'X-Powered-By': response.headers.get('X-Powered-By'),
                    'Content-Type': response.headers.get('Content-Type')
                }

                return {
                    'success': True,
                    'requested_url': candidate_url,
                    'final_url': response.url,
                    'status_code': response.status_code,
                    'redirected': response.url != candidate_url,
                    'headers': {
                        key: value or 'Not disclosed'
                        for key, value in selected_headers.items()
                    },
                    'detected_technologies': self._detect_technologies(selected_headers)
                }
            except RequestException as exc:
                request_error = exc
            finally:
                if response is not None:
                    response.close()

        raise RuntimeError('Could not reach the website to inspect its headers.') from request_error

    def _prepare_urls(self, raw_url):
        candidate = (raw_url or '').strip()
        if not candidate:
            raise ValueError('Website URL is required.')

        if '://' not in candidate:
            primary = self._normalize_url(f'https://{candidate}')
            fallback = self._normalize_url(f'http://{candidate}')
            return primary, fallback

        return self._normalize_url(candidate), None

    def _normalize_url(self, url):
        parsed = urlsplit(url)

        if parsed.scheme not in {'http', 'https'}:
            raise ValueError('Only http:// and https:// URLs are supported.')

        if not parsed.netloc or not parsed.hostname:
            raise ValueError('Enter a valid website URL.')

        if parsed.username or parsed.password:
            raise ValueError('URLs with embedded credentials are not allowed.')

        sanitized = parsed._replace(fragment='')
        return urlunsplit(sanitized)

    def _validate_public_target(self, url):
        hostname = urlsplit(url).hostname
        if hostname is None:
            raise ValueError('Enter a valid website URL.')

        normalized_host = hostname.rstrip('.').lower()
        if normalized_host == 'localhost' or normalized_host.endswith('.localhost'):
            raise ValueError('Localhost targets are not allowed.')

        try:
            resolved_addresses = {info[4][0] for info in socket.getaddrinfo(normalized_host, None)}
        except socket.gaierror as exc:
            raise ValueError('Could not resolve the website host.') from exc

        for address in resolved_addresses:
            ip_address = ipaddress.ip_address(address)
            if (
                ip_address.is_private
                or ip_address.is_loopback
                or ip_address.is_link_local
                or ip_address.is_multicast
                or ip_address.is_reserved
                or ip_address.is_unspecified
            ):
                raise ValueError('Private or local network targets are not allowed.')

    def _detect_technologies(self, selected_headers):
        detections = []
        seen = set()

        def add_detection(name, source, value):
            key = (name.lower(), source.lower())
            if key in seen:
                return
            seen.add(key)
            detections.append({
                'name': name,
                'source': source,
                'value': value
            })

        server_header = (selected_headers.get('Server') or '').strip()
        powered_by_header = (selected_headers.get('X-Powered-By') or '').strip()
        content_type_header = (selected_headers.get('Content-Type') or '').strip()

        if server_header:
            add_detection(server_header, 'Server header', server_header)

        if powered_by_header:
            add_detection(powered_by_header, 'X-Powered-By header', powered_by_header)

        if content_type_header:
            add_detection(content_type_header, 'Content-Type header', content_type_header)

        fingerprints = {
            'Nginx': ('nginx',),
            'Apache HTTP Server': ('apache',),
            'Cloudflare': ('cloudflare',),
            'LiteSpeed': ('litespeed',),
            'Microsoft IIS': ('iis', 'microsoft-iis'),
            'OpenResty': ('openresty',),
            'Gunicorn': ('gunicorn',),
            'Uvicorn': ('uvicorn',),
            'Caddy': ('caddy',),
            'Express': ('express',),
            'Node.js': ('node.js', 'nodejs'),
            'PHP': ('php',),
            'ASP.NET': ('asp.net',),
            'Python WSGI': ('wsgi',)
        }

        header_sources = (
            ('Server header', server_header.lower(), server_header),
            ('X-Powered-By header', powered_by_header.lower(), powered_by_header)
        )

        for source, normalized_value, raw_value in header_sources:
            for technology_name, markers in fingerprints.items():
                if any(marker in normalized_value for marker in markers):
                    add_detection(technology_name, source, raw_value)

        if not detections:
            detections.append({
                'name': 'No explicit technology fingerprint exposed',
                'source': 'Headers',
                'value': 'Server and X-Powered-By were not present.'
            })

        return detections

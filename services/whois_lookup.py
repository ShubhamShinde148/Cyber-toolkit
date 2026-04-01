"""
WHOIS Lookup Module
===================
Fetches WHOIS registration data for a domain and normalizes the fields used by
the Flask UI.
"""

from __future__ import annotations

from datetime import date, datetime
import re
from typing import Any

import whois


class WhoisLookup:
    """Lookup and normalize WHOIS information for a domain name."""

    DOMAIN_PATTERN = re.compile(
        r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
    )

    def validate_domain(self, domain: str) -> tuple[bool, str]:
        """Validate a user-supplied domain and return the normalized hostname."""
        if not domain:
            return False, 'Domain is required'

        normalized = domain.strip().lower()
        normalized = re.sub(r'^https?://', '', normalized)
        normalized = normalized.split('/')[0].split('?')[0]
        normalized = normalized.rstrip('.')

        if normalized.startswith('www.'):
            normalized = normalized[4:]

        if len(normalized) > 253:
            return False, 'Domain name is too long'

        if not self.DOMAIN_PATTERN.fullmatch(normalized):
            return False, 'Invalid domain format'

        return True, normalized

    def lookup(self, domain: str) -> dict[str, Any]:
        """Fetch WHOIS data and return the fields required by the UI."""
        is_valid, normalized_or_error = self.validate_domain(domain)
        if not is_valid:
            return {
                'success': False,
                'error': normalized_or_error
            }

        normalized_domain = normalized_or_error

        try:
            record = whois.whois(normalized_domain)
        except Exception as exc:
            return {
                'success': False,
                'error': f'WHOIS lookup failed: {exc}'
            }

        registrar = self._clean_text(record.get('registrar'))
        creation_date = self._format_date(record.get('creation_date'))
        expiration_date = self._format_date(record.get('expiration_date'))
        name_servers = self._normalize_name_servers(record.get('name_servers'))

        if not any([registrar, creation_date, expiration_date, name_servers]):
            return {
                'success': False,
                'error': 'No WHOIS data found for this domain'
            }

        return {
            'success': True,
            'domain': normalized_domain,
            'whois': {
                'registrar': registrar or 'Not available',
                'creation_date': creation_date or 'Not available',
                'expiration_date': expiration_date or 'Not available',
                'name_servers': name_servers or ['Not available']
            }
        }

    def _format_date(self, value: Any) -> str | None:
        """Normalize WHOIS date fields into YYYY-MM-DD."""
        if isinstance(value, list):
            values = [self._format_date(item) for item in value]
            values = [item for item in values if item]
            return values[0] if values else None

        if isinstance(value, datetime):
            return value.strftime('%Y-%m-%d')

        if isinstance(value, date):
            return value.isoformat()

        if value is None:
            return None

        text = str(value).strip()
        return text or None

    def _normalize_name_servers(self, value: Any) -> list[str]:
        """Return a sorted list of unique name servers."""
        if not value:
            return []

        if not isinstance(value, list):
            value = [value]

        normalized = {
            str(item).strip().rstrip('.').lower()
            for item in value
            if str(item).strip()
        }
        return sorted(normalized)

    def _clean_text(self, value: Any) -> str | None:
        """Normalize WHOIS text fields into a single readable string."""
        if isinstance(value, list):
            values = [self._clean_text(item) for item in value]
            values = [item for item in values if item]
            return values[0] if values else None

        if value is None:
            return None

        text = str(value).strip()
        return text or None

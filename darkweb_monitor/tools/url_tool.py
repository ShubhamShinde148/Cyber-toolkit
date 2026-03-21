"""
URL Encoder/Decoder Tool
Encode and decode URLs and URL components.
"""

from urllib.parse import quote, unquote, quote_plus, unquote_plus, urlparse, parse_qs
from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class URLResult:
    """Result of URL operation."""
    input_text: str
    output: str
    operation: str
    success: bool
    error: Optional[str] = None
    parsed_info: Optional[Dict] = None


class URLTool:
    """URL encoding and decoding operations."""
    
    def __init__(self):
        pass
    
    def encode(self, text: str, plus_encoding: bool = False) -> URLResult:
        """
        URL encode text.
        
        Args:
            text: Input text to encode
            plus_encoding: If True, spaces become '+' instead of '%20'
            
        Returns:
            URLResult with encoded string
        """
        try:
            if plus_encoding:
                encoded = quote_plus(text)
            else:
                encoded = quote(text, safe='')
            
            return URLResult(
                input_text=text[:200] + '...' if len(text) > 200 else text,
                output=encoded,
                operation='encode',
                success=True
            )
        except Exception as e:
            return URLResult(
                input_text=text[:200] if len(text) > 200 else text,
                output='',
                operation='encode',
                success=False,
                error=str(e)
            )
    
    def decode(self, encoded_text: str, plus_encoding: bool = False) -> URLResult:
        """
        URL decode text.
        
        Args:
            encoded_text: URL encoded string
            plus_encoding: If True, '+' becomes space
            
        Returns:
            URLResult with decoded string
        """
        try:
            if plus_encoding:
                decoded = unquote_plus(encoded_text)
            else:
                decoded = unquote(encoded_text)
            
            return URLResult(
                input_text=encoded_text[:200] + '...' if len(encoded_text) > 200 else encoded_text,
                output=decoded,
                operation='decode',
                success=True
            )
        except Exception as e:
            return URLResult(
                input_text=encoded_text[:200] if len(encoded_text) > 200 else encoded_text,
                output='',
                operation='decode',
                success=False,
                error=str(e)
            )
    
    def encode_component(self, text: str) -> URLResult:
        """
        Encode URL component (like encodeURIComponent in JavaScript).
        
        Args:
            text: Component to encode
            
        Returns:
            URLResult with encoded component
        """
        try:
            # Encode everything except unreserved characters
            encoded = quote(text, safe='-_.~')
            return URLResult(
                input_text=text[:200] + '...' if len(text) > 200 else text,
                output=encoded,
                operation='encode_component',
                success=True
            )
        except Exception as e:
            return URLResult(
                input_text=text[:200] if len(text) > 200 else text,
                output='',
                operation='encode_component',
                success=False,
                error=str(e)
            )
    
    def parse_url(self, url: str) -> URLResult:
        """
        Parse a URL into its components.
        
        Args:
            url: URL to parse
            
        Returns:
            URLResult with parsed URL information
        """
        try:
            parsed = urlparse(url)
            query_params = parse_qs(parsed.query) if parsed.query else {}
            
            parsed_info = {
                'scheme': parsed.scheme or 'N/A',
                'hostname': parsed.hostname or 'N/A',
                'port': parsed.port or ('443' if parsed.scheme == 'https' else '80' if parsed.scheme == 'http' else 'N/A'),
                'path': parsed.path or '/',
                'query': parsed.query or 'N/A',
                'query_params': query_params,
                'fragment': parsed.fragment or 'N/A',
                'username': parsed.username or 'N/A',
                'password': '***' if parsed.password else 'N/A'
            }
            
            # Format output nicely
            output_lines = [
                f"Scheme: {parsed_info['scheme']}",
                f"Host: {parsed_info['hostname']}",
                f"Port: {parsed_info['port']}",
                f"Path: {parsed_info['path']}",
                f"Query: {parsed_info['query']}",
                f"Fragment: {parsed_info['fragment']}"
            ]
            
            if query_params:
                output_lines.append("Query Parameters:")
                for key, values in query_params.items():
                    output_lines.append(f"  {key}: {', '.join(values)}")
            
            return URLResult(
                input_text=url[:200] + '...' if len(url) > 200 else url,
                output='\n'.join(output_lines),
                operation='parse',
                success=True,
                parsed_info=parsed_info
            )
        except Exception as e:
            return URLResult(
                input_text=url[:200] if len(url) > 200 else url,
                output='',
                operation='parse',
                success=False,
                error=f"URL parsing failed: {str(e)}"
            )
    
    def encode_html_entities(self, text: str) -> URLResult:
        """
        Encode HTML entities.
        
        Args:
            text: Text with HTML characters
            
        Returns:
            URLResult with encoded HTML
        """
        import html
        try:
            encoded = html.escape(text)
            return URLResult(
                input_text=text[:200] + '...' if len(text) > 200 else text,
                output=encoded,
                operation='html_encode',
                success=True
            )
        except Exception as e:
            return URLResult(
                input_text=text[:200] if len(text) > 200 else text,
                output='',
                operation='html_encode',
                success=False,
                error=str(e)
            )
    
    def decode_html_entities(self, text: str) -> URLResult:
        """
        Decode HTML entities.
        
        Args:
            text: Text with HTML entities
            
        Returns:
            URLResult with decoded text
        """
        import html
        try:
            decoded = html.unescape(text)
            return URLResult(
                input_text=text[:200] + '...' if len(text) > 200 else text,
                output=decoded,
                operation='html_decode',
                success=True
            )
        except Exception as e:
            return URLResult(
                input_text=text[:200] if len(text) > 200 else text,
                output='',
                operation='html_decode',
                success=False,
                error=str(e)
            )


# Convenience functions
def url_encode(text: str) -> str:
    """Quick URL encode."""
    return URLTool().encode(text).output


def url_decode(text: str) -> str:
    """Quick URL decode."""
    return URLTool().decode(text).output

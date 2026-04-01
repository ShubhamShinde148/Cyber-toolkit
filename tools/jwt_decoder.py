"""
JWT Token Decoder Tool
Decode and analyze JSON Web Tokens without verification.
"""

import base64
import json
from typing import Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class JWTResult:
    """Result of JWT decoding."""
    token: str
    header: Dict[str, Any]
    payload: Dict[str, Any]
    signature: str
    is_valid_format: bool
    expiration: Optional[str] = None
    issued_at: Optional[str] = None
    is_expired: Optional[bool] = None
    error: Optional[str] = None


class JWTDecoder:
    """Decode and analyze JWT tokens (without verification)."""
    
    def __init__(self):
        pass
    
    def _base64_url_decode(self, data: str) -> bytes:
        """Decode base64url encoded data."""
        # Add padding if needed
        padding = 4 - len(data) % 4
        if padding != 4:
            data += '=' * padding
        
        # Convert base64url to base64
        data = data.replace('-', '+').replace('_', '/')
        
        return base64.b64decode(data)
    
    def decode(self, token: str) -> JWTResult:
        """
        Decode a JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            JWTResult with decoded header, payload, and metadata
        """
        token = token.strip()
        
        # Check basic format
        parts = token.split('.')
        if len(parts) != 3:
            return JWTResult(
                token=token[:50] + '...' if len(token) > 50 else token,
                header={},
                payload={},
                signature='',
                is_valid_format=False,
                error=f"Invalid JWT format: expected 3 parts separated by '.', got {len(parts)}"
            )
        
        try:
            # Decode header
            header_bytes = self._base64_url_decode(parts[0])
            header = json.loads(header_bytes.decode('utf-8'))
        except Exception as e:
            return JWTResult(
                token=token[:50] + '...' if len(token) > 50 else token,
                header={},
                payload={},
                signature='',
                is_valid_format=False,
                error=f"Failed to decode header: {str(e)}"
            )
        
        try:
            # Decode payload
            payload_bytes = self._base64_url_decode(parts[1])
            payload = json.loads(payload_bytes.decode('utf-8'))
        except Exception as e:
            return JWTResult(
                token=token[:50] + '...' if len(token) > 50 else token,
                header=header,
                payload={},
                signature='',
                is_valid_format=False,
                error=f"Failed to decode payload: {str(e)}"
            )
        
        # Extract time-related claims
        expiration = None
        issued_at = None
        is_expired = None
        
        if 'exp' in payload:
            try:
                exp_timestamp = int(payload['exp'])
                expiration = datetime.fromtimestamp(exp_timestamp).isoformat()
                is_expired = datetime.now().timestamp() > exp_timestamp
            except (ValueError, TypeError):
                expiration = str(payload['exp'])
        
        if 'iat' in payload:
            try:
                iat_timestamp = int(payload['iat'])
                issued_at = datetime.fromtimestamp(iat_timestamp).isoformat()
            except (ValueError, TypeError):
                issued_at = str(payload['iat'])
        
        # Get signature (just show hex representation)
        try:
            signature_bytes = self._base64_url_decode(parts[2])
            signature = signature_bytes.hex()[:64] + ('...' if len(signature_bytes) > 32 else '')
        except Exception:
            signature = parts[2][:32] + '...'
        
        return JWTResult(
            token=token[:100] + '...' if len(token) > 100 else token,
            header=header,
            payload=payload,
            signature=signature,
            is_valid_format=True,
            expiration=expiration,
            issued_at=issued_at,
            is_expired=is_expired
        )
    
    def get_claims(self, token: str) -> Dict[str, Any]:
        """
        Get all claims from a JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            Dictionary of all claims
        """
        result = self.decode(token)
        if not result.is_valid_format:
            return {'error': result.error}
        
        claims = {**result.payload}
        
        # Add interpreted time claims
        if result.expiration:
            claims['_exp_human'] = result.expiration
            claims['_is_expired'] = result.is_expired
        
        if result.issued_at:
            claims['_iat_human'] = result.issued_at
        
        return claims
    
    def format_output(self, result: JWTResult) -> str:
        """
        Format JWT result for display.
        
        Args:
            result: JWTResult to format
            
        Returns:
            Formatted string output
        """
        if not result.is_valid_format:
            return f"Error: {result.error}"
        
        lines = [
            "=== JWT HEADER ===",
            json.dumps(result.header, indent=2),
            "",
            "=== JWT PAYLOAD ===",
            json.dumps(result.payload, indent=2),
            "",
            "=== TOKEN INFO ===",
            f"Algorithm: {result.header.get('alg', 'Unknown')}",
            f"Type: {result.header.get('typ', 'Unknown')}"
        ]
        
        if result.expiration:
            status = " (EXPIRED)" if result.is_expired else " (Valid)"
            lines.append(f"Expiration: {result.expiration}{status}")
        
        if result.issued_at:
            lines.append(f"Issued At: {result.issued_at}")
        
        # Common claims
        if 'sub' in result.payload:
            lines.append(f"Subject: {result.payload['sub']}")
        if 'iss' in result.payload:
            lines.append(f"Issuer: {result.payload['iss']}")
        if 'aud' in result.payload:
            lines.append(f"Audience: {result.payload['aud']}")
        
        lines.extend([
            "",
            "=== SIGNATURE ===",
            f"(hex): {result.signature}",
            "",
            "⚠️  Note: Signature not verified (requires secret/public key)"
        ])
        
        return '\n'.join(lines)


# Convenience function
def decode_jwt(token: str) -> Dict[str, Any]:
    """Quick JWT decode."""
    decoder = JWTDecoder()
    result = decoder.decode(token)
    return {
        'header': result.header,
        'payload': result.payload,
        'is_valid': result.is_valid_format,
        'is_expired': result.is_expired,
        'error': result.error
    }

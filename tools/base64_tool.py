"""
Base64 Encoder/Decoder Tool
Encode and decode text using Base64 encoding.
"""

import base64
from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class Base64Result:
    """Result of Base64 operation."""
    input_text: str
    output: str
    operation: str  # 'encode' or 'decode'
    success: bool
    error: Optional[str] = None


class Base64Tool:
    """Base64 encoding and decoding operations."""
    
    def __init__(self):
        pass
    
    def encode(self, text: str) -> Base64Result:
        """
        Encode text to Base64.
        
        Args:
            text: Input text to encode
            
        Returns:
            Base64Result with encoded string
        """
        try:
            encoded = base64.b64encode(text.encode('utf-8')).decode('utf-8')
            return Base64Result(
                input_text=text[:100] + '...' if len(text) > 100 else text,
                output=encoded,
                operation='encode',
                success=True
            )
        except Exception as e:
            return Base64Result(
                input_text=text[:100] if len(text) > 100 else text,
                output='',
                operation='encode',
                success=False,
                error=str(e)
            )
    
    def decode(self, encoded_text: str) -> Base64Result:
        """
        Decode Base64 text.
        
        Args:
            encoded_text: Base64 encoded string
            
        Returns:
            Base64Result with decoded string
        """
        try:
            # Clean up the input (remove whitespace)
            cleaned = encoded_text.strip().replace('\n', '').replace('\r', '')
            
            # Add padding if needed
            padding_needed = len(cleaned) % 4
            if padding_needed:
                cleaned += '=' * (4 - padding_needed)
            
            decoded = base64.b64decode(cleaned).decode('utf-8')
            return Base64Result(
                input_text=encoded_text[:100] + '...' if len(encoded_text) > 100 else encoded_text,
                output=decoded,
                operation='decode',
                success=True
            )
        except UnicodeDecodeError:
            # Try decoding as binary and return hex representation
            try:
                decoded_bytes = base64.b64decode(encoded_text.strip())
                hex_output = decoded_bytes.hex()
                return Base64Result(
                    input_text=encoded_text[:100] + '...' if len(encoded_text) > 100 else encoded_text,
                    output=f"[Binary data - Hex: {hex_output[:100]}{'...' if len(hex_output) > 100 else ''}]",
                    operation='decode',
                    success=True
                )
            except Exception as e:
                return Base64Result(
                    input_text=encoded_text[:100] if len(encoded_text) > 100 else encoded_text,
                    output='',
                    operation='decode',
                    success=False,
                    error=f"Invalid Base64 data: {str(e)}"
                )
        except Exception as e:
            return Base64Result(
                input_text=encoded_text[:100] if len(encoded_text) > 100 else encoded_text,
                output='',
                operation='decode',
                success=False,
                error=f"Decoding failed: {str(e)}"
            )
    
    def encode_url_safe(self, text: str) -> Base64Result:
        """
        Encode text to URL-safe Base64.
        
        Args:
            text: Input text to encode
            
        Returns:
            Base64Result with URL-safe encoded string
        """
        try:
            encoded = base64.urlsafe_b64encode(text.encode('utf-8')).decode('utf-8')
            return Base64Result(
                input_text=text[:100] + '...' if len(text) > 100 else text,
                output=encoded,
                operation='encode_urlsafe',
                success=True
            )
        except Exception as e:
            return Base64Result(
                input_text=text[:100] if len(text) > 100 else text,
                output='',
                operation='encode_urlsafe',
                success=False,
                error=str(e)
            )
    
    def decode_url_safe(self, encoded_text: str) -> Base64Result:
        """
        Decode URL-safe Base64 text.
        
        Args:
            encoded_text: URL-safe Base64 encoded string
            
        Returns:
            Base64Result with decoded string
        """
        try:
            cleaned = encoded_text.strip()
            padding_needed = len(cleaned) % 4
            if padding_needed:
                cleaned += '=' * (4 - padding_needed)
            
            decoded = base64.urlsafe_b64decode(cleaned).decode('utf-8')
            return Base64Result(
                input_text=encoded_text[:100] + '...' if len(encoded_text) > 100 else encoded_text,
                output=decoded,
                operation='decode_urlsafe',
                success=True
            )
        except Exception as e:
            return Base64Result(
                input_text=encoded_text[:100] if len(encoded_text) > 100 else encoded_text,
                output='',
                operation='decode_urlsafe',
                success=False,
                error=f"URL-safe decoding failed: {str(e)}"
            )
    
    def is_valid_base64(self, text: str) -> bool:
        """Check if text is valid Base64."""
        try:
            cleaned = text.strip().replace('\n', '').replace('\r', '')
            base64.b64decode(cleaned, validate=True)
            return True
        except Exception:
            return False


# Convenience functions
def base64_encode(text: str) -> str:
    """Quick Base64 encode."""
    return Base64Tool().encode(text).output


def base64_decode(text: str) -> str:
    """Quick Base64 decode."""
    return Base64Tool().decode(text).output

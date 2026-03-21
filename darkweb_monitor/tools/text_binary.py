"""
Text ↔ Binary Converter Tool
Convert between text, binary, hex, and other formats.
"""

from typing import Optional
from dataclasses import dataclass


@dataclass
class ConversionResult:
    """Result of text/binary conversion."""
    input_text: str
    output: str
    operation: str
    success: bool
    error: Optional[str] = None


class TextBinaryConverter:
    """Convert between text and various binary representations."""
    
    def __init__(self):
        pass
    
    def text_to_binary(self, text: str, separator: str = ' ') -> ConversionResult:
        """
        Convert text to binary representation.
        
        Args:
            text: Input text
            separator: Separator between binary bytes
            
        Returns:
            ConversionResult with binary string
        """
        try:
            binary = separator.join(format(ord(char), '08b') for char in text)
            return ConversionResult(
                input_text=text[:100] + '...' if len(text) > 100 else text,
                output=binary,
                operation='text_to_binary',
                success=True
            )
        except Exception as e:
            return ConversionResult(
                input_text=text[:100] if len(text) > 100 else text,
                output='',
                operation='text_to_binary',
                success=False,
                error=str(e)
            )
    
    def binary_to_text(self, binary: str) -> ConversionResult:
        """
        Convert binary to text.
        
        Args:
            binary: Binary string (spaces or no spaces)
            
        Returns:
            ConversionResult with text
        """
        try:
            # Clean up input
            binary = binary.replace(' ', '').replace('\n', '').replace('\t', '')
            
            # Validate binary
            if not all(c in '01' for c in binary):
                raise ValueError("Input contains non-binary characters")
            
            # Pad to multiple of 8
            if len(binary) % 8 != 0:
                binary = binary.zfill(len(binary) + (8 - len(binary) % 8))
            
            # Convert to text
            text = ''
            for i in range(0, len(binary), 8):
                byte = binary[i:i+8]
                text += chr(int(byte, 2))
            
            return ConversionResult(
                input_text=binary[:50] + '...' if len(binary) > 50 else binary,
                output=text,
                operation='binary_to_text',
                success=True
            )
        except Exception as e:
            return ConversionResult(
                input_text=binary[:50] if len(binary) > 50 else binary,
                output='',
                operation='binary_to_text',
                success=False,
                error=f"Invalid binary: {str(e)}"
            )
    
    def text_to_hex(self, text: str, separator: str = ' ') -> ConversionResult:
        """
        Convert text to hexadecimal.
        
        Args:
            text: Input text
            separator: Separator between hex bytes
            
        Returns:
            ConversionResult with hex string
        """
        try:
            hex_str = separator.join(format(ord(char), '02x') for char in text)
            return ConversionResult(
                input_text=text[:100] + '...' if len(text) > 100 else text,
                output=hex_str,
                operation='text_to_hex',
                success=True
            )
        except Exception as e:
            return ConversionResult(
                input_text=text[:100] if len(text) > 100 else text,
                output='',
                operation='text_to_hex',
                success=False,
                error=str(e)
            )
    
    def hex_to_text(self, hex_str: str) -> ConversionResult:
        """
        Convert hexadecimal to text.
        
        Args:
            hex_str: Hex string
            
        Returns:
            ConversionResult with text
        """
        try:
            # Clean up input
            hex_str = hex_str.replace(' ', '').replace('\n', '').replace('0x', '').replace('\\x', '')
            
            # Validate hex
            if not all(c in '0123456789abcdefABCDEF' for c in hex_str):
                raise ValueError("Input contains non-hex characters")
            
            # Convert to text
            text = bytes.fromhex(hex_str).decode('utf-8')
            
            return ConversionResult(
                input_text=hex_str[:50] + '...' if len(hex_str) > 50 else hex_str,
                output=text,
                operation='hex_to_text',
                success=True
            )
        except UnicodeDecodeError:
            # Return raw bytes representation
            try:
                raw_bytes = bytes.fromhex(hex_str)
                return ConversionResult(
                    input_text=hex_str[:50] + '...' if len(hex_str) > 50 else hex_str,
                    output=f"[Binary data: {len(raw_bytes)} bytes]",
                    operation='hex_to_text',
                    success=True
                )
            except Exception as e:
                return ConversionResult(
                    input_text=hex_str[:50] if len(hex_str) > 50 else hex_str,
                    output='',
                    operation='hex_to_text',
                    success=False,
                    error=f"Invalid hex: {str(e)}"
                )
        except Exception as e:
            return ConversionResult(
                input_text=hex_str[:50] if len(hex_str) > 50 else hex_str,
                output='',
                operation='hex_to_text',
                success=False,
                error=f"Invalid hex: {str(e)}"
            )
    
    def text_to_decimal(self, text: str, separator: str = ' ') -> ConversionResult:
        """
        Convert text to decimal ASCII values.
        
        Args:
            text: Input text
            separator: Separator between values
            
        Returns:
            ConversionResult with decimal values
        """
        try:
            decimal = separator.join(str(ord(char)) for char in text)
            return ConversionResult(
                input_text=text[:100] + '...' if len(text) > 100 else text,
                output=decimal,
                operation='text_to_decimal',
                success=True
            )
        except Exception as e:
            return ConversionResult(
                input_text=text[:100] if len(text) > 100 else text,
                output='',
                operation='text_to_decimal',
                success=False,
                error=str(e)
            )
    
    def decimal_to_text(self, decimal_str: str) -> ConversionResult:
        """
        Convert decimal ASCII values to text.
        
        Args:
            decimal_str: Space-separated decimal values
            
        Returns:
            ConversionResult with text
        """
        try:
            # Parse decimal values
            values = decimal_str.replace(',', ' ').split()
            text = ''.join(chr(int(v)) for v in values)
            
            return ConversionResult(
                input_text=decimal_str[:50] + '...' if len(decimal_str) > 50 else decimal_str,
                output=text,
                operation='decimal_to_text',
                success=True
            )
        except Exception as e:
            return ConversionResult(
                input_text=decimal_str[:50] if len(decimal_str) > 50 else decimal_str,
                output='',
                operation='decimal_to_text',
                success=False,
                error=f"Invalid decimal values: {str(e)}"
            )
    
    def text_to_octal(self, text: str, separator: str = ' ') -> ConversionResult:
        """
        Convert text to octal representation.
        
        Args:
            text: Input text
            separator: Separator between octal values
            
        Returns:
            ConversionResult with octal string
        """
        try:
            octal = separator.join(format(ord(char), 'o') for char in text)
            return ConversionResult(
                input_text=text[:100] + '...' if len(text) > 100 else text,
                output=octal,
                operation='text_to_octal',
                success=True
            )
        except Exception as e:
            return ConversionResult(
                input_text=text[:100] if len(text) > 100 else text,
                output='',
                operation='text_to_octal',
                success=False,
                error=str(e)
            )
    
    def octal_to_text(self, octal_str: str) -> ConversionResult:
        """
        Convert octal to text.
        
        Args:
            octal_str: Space-separated octal values
            
        Returns:
            ConversionResult with text
        """
        try:
            values = octal_str.replace(',', ' ').split()
            text = ''.join(chr(int(v, 8)) for v in values)
            
            return ConversionResult(
                input_text=octal_str[:50] + '...' if len(octal_str) > 50 else octal_str,
                output=text,
                operation='octal_to_text',
                success=True
            )
        except Exception as e:
            return ConversionResult(
                input_text=octal_str[:50] if len(octal_str) > 50 else octal_str,
                output='',
                operation='octal_to_text',
                success=False,
                error=f"Invalid octal values: {str(e)}"
            )
    
    def convert_all(self, text: str) -> dict:
        """
        Convert text to all formats.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with all conversions
        """
        return {
            'original': text,
            'binary': self.text_to_binary(text).output,
            'hex': self.text_to_hex(text).output,
            'decimal': self.text_to_decimal(text).output,
            'octal': self.text_to_octal(text).output
        }


# Convenience functions
def to_binary(text: str) -> str:
    """Quick text to binary."""
    return TextBinaryConverter().text_to_binary(text).output


def from_binary(binary: str) -> str:
    """Quick binary to text."""
    return TextBinaryConverter().binary_to_text(binary).output

"""
ROT13 Encoder/Decoder Tool
Apply ROT13 and other Caesar cipher variations.
"""

import string
from typing import Optional
from dataclasses import dataclass


@dataclass
class ROTResult:
    """Result of ROT operation."""
    input_text: str
    output: str
    shift: int
    operation: str
    success: bool
    error: Optional[str] = None


class ROT13Tool:
    """ROT13 and Caesar cipher operations."""
    
    def __init__(self):
        pass
    
    def rot13(self, text: str) -> ROTResult:
        """
        Apply ROT13 encoding (also works as decoder).
        
        Args:
            text: Input text
            
        Returns:
            ROTResult with encoded/decoded text
        """
        return self.caesar_cipher(text, 13)
    
    def caesar_cipher(self, text: str, shift: int) -> ROTResult:
        """
        Apply Caesar cipher with custom shift.
        
        Args:
            text: Input text
            shift: Number of positions to shift (positive = right, negative = left)
            
        Returns:
            ROTResult with shifted text
        """
        try:
            result = []
            shift = shift % 26  # Normalize shift
            
            for char in text:
                if char.isalpha():
                    # Determine the base (uppercase or lowercase)
                    base = ord('A') if char.isupper() else ord('a')
                    # Shift the character
                    shifted = (ord(char) - base + shift) % 26 + base
                    result.append(chr(shifted))
                else:
                    # Keep non-alphabetic characters unchanged
                    result.append(char)
            
            output = ''.join(result)
            
            return ROTResult(
                input_text=text[:200] + '...' if len(text) > 200 else text,
                output=output,
                shift=shift,
                operation=f'ROT{shift}' if shift == 13 else f'Caesar (shift={shift})',
                success=True
            )
        except Exception as e:
            return ROTResult(
                input_text=text[:200] if len(text) > 200 else text,
                output='',
                shift=shift,
                operation='caesar',
                success=False,
                error=str(e)
            )
    
    def rot47(self, text: str) -> ROTResult:
        """
        Apply ROT47 encoding (includes numbers and symbols).
        
        Args:
            text: Input text
            
        Returns:
            ROTResult with encoded/decoded text
        """
        try:
            result = []
            
            for char in text:
                code = ord(char)
                # ROT47 affects ASCII 33 (!) to 126 (~)
                if 33 <= code <= 126:
                    # Shift by 47 within the range
                    shifted = ((code - 33 + 47) % 94) + 33
                    result.append(chr(shifted))
                else:
                    result.append(char)
            
            output = ''.join(result)
            
            return ROTResult(
                input_text=text[:200] + '...' if len(text) > 200 else text,
                output=output,
                shift=47,
                operation='ROT47',
                success=True
            )
        except Exception as e:
            return ROTResult(
                input_text=text[:200] if len(text) > 200 else text,
                output='',
                shift=47,
                operation='ROT47',
                success=False,
                error=str(e)
            )
    
    def brute_force(self, text: str) -> dict:
        """
        Try all possible ROT shifts (1-25).
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with all possible shifts
        """
        results = {}
        for shift in range(1, 26):
            result = self.caesar_cipher(text, shift)
            results[f'ROT{shift}'] = result.output
        return results
    
    def atbash(self, text: str) -> ROTResult:
        """
        Apply Atbash cipher (reverse alphabet).
        
        Args:
            text: Input text
            
        Returns:
            ROTResult with encoded/decoded text
        """
        try:
            result = []
            
            for char in text:
                if char.isalpha():
                    if char.isupper():
                        # A -> Z, B -> Y, etc.
                        result.append(chr(ord('Z') - (ord(char) - ord('A'))))
                    else:
                        result.append(chr(ord('z') - (ord(char) - ord('a'))))
                else:
                    result.append(char)
            
            output = ''.join(result)
            
            return ROTResult(
                input_text=text[:200] + '...' if len(text) > 200 else text,
                output=output,
                shift=0,
                operation='Atbash',
                success=True
            )
        except Exception as e:
            return ROTResult(
                input_text=text[:200] if len(text) > 200 else text,
                output='',
                shift=0,
                operation='Atbash',
                success=False,
                error=str(e)
            )
    
    def reverse_string(self, text: str) -> ROTResult:
        """
        Reverse a string.
        
        Args:
            text: Input text
            
        Returns:
            ROTResult with reversed text
        """
        try:
            return ROTResult(
                input_text=text[:200] + '...' if len(text) > 200 else text,
                output=text[::-1],
                shift=0,
                operation='Reverse',
                success=True
            )
        except Exception as e:
            return ROTResult(
                input_text=text[:200] if len(text) > 200 else text,
                output='',
                shift=0,
                operation='Reverse',
                success=False,
                error=str(e)
            )
    
    def format_brute_force(self, text: str) -> str:
        """
        Format brute force results for display.
        
        Args:
            text: Input text
            
        Returns:
            Formatted string with all shifts
        """
        results = self.brute_force(text)
        lines = ["=== CAESAR CIPHER BRUTE FORCE ===", ""]
        
        for shift, output in results.items():
            lines.append(f"{shift}: {output[:80]}{'...' if len(output) > 80 else ''}")
        
        return '\n'.join(lines)


# Convenience functions
def rot13(text: str) -> str:
    """Quick ROT13."""
    return ROT13Tool().rot13(text).output


def caesar(text: str, shift: int) -> str:
    """Quick Caesar cipher."""
    return ROT13Tool().caesar_cipher(text, shift).output

"""
Password Generator Module
Generates cryptographically secure passwords with customizable options.
"""

import secrets
import string
import math
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum


class PasswordStrength(Enum):
    """Password strength levels."""
    WEAK = "WEAK"
    FAIR = "FAIR"
    GOOD = "GOOD"
    STRONG = "STRONG"
    VERY_STRONG = "VERY_STRONG"


@dataclass
class GeneratedPassword:
    """Contains generated password and its metadata."""
    password: str
    length: int
    entropy: float
    strength: PasswordStrength
    has_uppercase: bool
    has_lowercase: bool
    has_digits: bool
    has_special: bool
    memorable: bool


@dataclass
class PasswordConfig:
    """Configuration for password generation."""
    length: int = 16
    include_uppercase: bool = True
    include_lowercase: bool = True
    include_digits: bool = True
    include_special: bool = True
    exclude_ambiguous: bool = True  # Exclude 0, O, l, 1, etc.
    exclude_chars: str = ""
    min_uppercase: int = 1
    min_lowercase: int = 1
    min_digits: int = 1
    min_special: int = 1


class PasswordGenerator:
    """Generates secure passwords with various options."""
    
    # Character sets
    UPPERCASE = string.ascii_uppercase
    LOWERCASE = string.ascii_lowercase
    DIGITS = string.digits
    SPECIAL = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    # Ambiguous characters to exclude
    AMBIGUOUS = "0O1lI|"
    
    # Word lists for memorable passwords
    ADJECTIVES = [
        "happy", "brave", "quick", "calm", "bright", "clever", "swift", "bold",
        "gentle", "fierce", "noble", "wise", "proud", "eager", "lively", "keen",
        "vivid", "cosmic", "silent", "golden", "silver", "crystal", "mystic", "royal"
    ]
    
    NOUNS = [
        "tiger", "eagle", "river", "mountain", "forest", "ocean", "thunder", "dragon",
        "phoenix", "falcon", "wolf", "panther", "storm", "comet", "nebula", "sparrow",
        "castle", "garden", "harbor", "meadow", "glacier", "volcano", "canyon", "island"
    ]
    
    VERBS = [
        "runs", "jumps", "flies", "swims", "dances", "leaps", "soars", "glides",
        "sprints", "dashes", "bounds", "races", "zooms", "blazes", "charges", "ventures"
    ]
    
    def __init__(self, config: Optional[PasswordConfig] = None):
        self.config = config or PasswordConfig()
    
    def _build_charset(self) -> str:
        """Build character set based on configuration."""
        charset = ""
        
        if self.config.include_uppercase:
            charset += self.UPPERCASE
        if self.config.include_lowercase:
            charset += self.LOWERCASE
        if self.config.include_digits:
            charset += self.DIGITS
        if self.config.include_special:
            charset += self.SPECIAL
        
        # Remove ambiguous characters if requested
        if self.config.exclude_ambiguous:
            charset = ''.join(c for c in charset if c not in self.AMBIGUOUS)
        
        # Remove user-specified excluded characters
        if self.config.exclude_chars:
            charset = ''.join(c for c in charset if c not in self.config.exclude_chars)
        
        return charset
    
    def _calculate_entropy(self, password: str) -> float:
        """Calculate password entropy in bits."""
        charset_size = 0
        
        if any(c in self.UPPERCASE for c in password):
            charset_size += 26
        if any(c in self.LOWERCASE for c in password):
            charset_size += 26
        if any(c in self.DIGITS for c in password):
            charset_size += 10
        if any(c in self.SPECIAL for c in password):
            charset_size += len(self.SPECIAL)
        
        if charset_size == 0:
            return 0
        
        return len(password) * math.log2(charset_size)
    
    def _assess_strength(self, entropy: float) -> PasswordStrength:
        """Assess password strength based on entropy."""
        if entropy < 28:
            return PasswordStrength.WEAK
        elif entropy < 36:
            return PasswordStrength.FAIR
        elif entropy < 60:
            return PasswordStrength.GOOD
        elif entropy < 128:
            return PasswordStrength.STRONG
        else:
            return PasswordStrength.VERY_STRONG
    
    def generate(self) -> GeneratedPassword:
        """Generate a random password based on configuration."""
        charset = self._build_charset()
        
        if not charset:
            raise ValueError("No character set available. Enable at least one character type.")
        
        # Ensure minimum requirements
        password_chars = []
        
        if self.config.include_uppercase and self.config.min_uppercase > 0:
            chars = self.UPPERCASE
            if self.config.exclude_ambiguous:
                chars = ''.join(c for c in chars if c not in self.AMBIGUOUS)
            password_chars.extend(secrets.choice(chars) for _ in range(self.config.min_uppercase))
        
        if self.config.include_lowercase and self.config.min_lowercase > 0:
            chars = self.LOWERCASE
            if self.config.exclude_ambiguous:
                chars = ''.join(c for c in chars if c not in self.AMBIGUOUS)
            password_chars.extend(secrets.choice(chars) for _ in range(self.config.min_lowercase))
        
        if self.config.include_digits and self.config.min_digits > 0:
            chars = self.DIGITS
            if self.config.exclude_ambiguous:
                chars = ''.join(c for c in chars if c not in self.AMBIGUOUS)
            password_chars.extend(secrets.choice(chars) for _ in range(self.config.min_digits))
        
        if self.config.include_special and self.config.min_special > 0:
            password_chars.extend(secrets.choice(self.SPECIAL) for _ in range(self.config.min_special))
        
        # Fill remaining length with random characters
        remaining = self.config.length - len(password_chars)
        if remaining > 0:
            password_chars.extend(secrets.choice(charset) for _ in range(remaining))
        
        # Shuffle to avoid predictable patterns
        password_list = list(password_chars)
        secrets.SystemRandom().shuffle(password_list)
        password = ''.join(password_list)
        
        entropy = self._calculate_entropy(password)
        
        return GeneratedPassword(
            password=password,
            length=len(password),
            entropy=round(entropy, 2),
            strength=self._assess_strength(entropy),
            has_uppercase=any(c in self.UPPERCASE for c in password),
            has_lowercase=any(c in self.LOWERCASE for c in password),
            has_digits=any(c in self.DIGITS for c in password),
            has_special=any(c in self.SPECIAL for c in password),
            memorable=False
        )
    
    def generate_memorable(self, num_words: int = 4, separator: str = "-", include_number: bool = True) -> GeneratedPassword:
        """
        Generate a memorable passphrase using random words.
        Format: adjective-noun-verb-noun (+ optional number)
        """
        words = []
        
        # Build memorable phrase
        if num_words >= 1:
            words.append(secrets.choice(self.ADJECTIVES))
        if num_words >= 2:
            words.append(secrets.choice(self.NOUNS))
        if num_words >= 3:
            words.append(secrets.choice(self.VERBS))
        if num_words >= 4:
            words.append(secrets.choice(self.NOUNS))
        
        # Add extra words if needed
        for _ in range(max(0, num_words - 4)):
            words.append(secrets.choice(self.ADJECTIVES + self.NOUNS))
        
        # Capitalize first letter of each word
        words = [w.capitalize() for w in words]
        
        # Add number if requested
        if include_number:
            words.append(str(secrets.randbelow(900) + 100))
        
        password = separator.join(words)
        entropy = self._calculate_entropy(password)
        
        return GeneratedPassword(
            password=password,
            length=len(password),
            entropy=round(entropy, 2),
            strength=self._assess_strength(entropy),
            has_uppercase=any(c.isupper() for c in password),
            has_lowercase=any(c.islower() for c in password),
            has_digits=any(c.isdigit() for c in password),
            has_special=separator in self.SPECIAL,
            memorable=True
        )
    
    def generate_pin(self, length: int = 6) -> GeneratedPassword:
        """Generate a numeric PIN."""
        pin = ''.join(secrets.choice(self.DIGITS) for _ in range(length))
        entropy = self._calculate_entropy(pin)
        
        return GeneratedPassword(
            password=pin,
            length=len(pin),
            entropy=round(entropy, 2),
            strength=self._assess_strength(entropy),
            has_uppercase=False,
            has_lowercase=False,
            has_digits=True,
            has_special=False,
            memorable=True
        )
    
    def generate_multiple(self, count: int = 5) -> List[GeneratedPassword]:
        """Generate multiple passwords."""
        return [self.generate() for _ in range(count)]
    
    @staticmethod
    def check_against_common(password: str) -> bool:
        """
        Check if password matches common weak passwords.
        Returns True if password is common/weak.
        """
        common_passwords = {
            "password", "123456", "12345678", "qwerty", "abc123",
            "monkey", "1234567", "letmein", "trustno1", "dragon",
            "baseball", "iloveyou", "master", "sunshine", "ashley",
            "bailey", "shadow", "123123", "654321", "superman",
            "qazwsx", "michael", "football", "password1", "password123"
        }
        return password.lower() in common_passwords


# Convenience functions
def generate_password(length: int = 16, **kwargs) -> str:
    """Generate a single secure password."""
    config = PasswordConfig(length=length, **kwargs)
    generator = PasswordGenerator(config)
    return generator.generate().password


def generate_passphrase(num_words: int = 4, separator: str = "-") -> str:
    """Generate a memorable passphrase."""
    generator = PasswordGenerator()
    return generator.generate_memorable(num_words, separator).password


def generate_pin(length: int = 6) -> str:
    """Generate a numeric PIN."""
    generator = PasswordGenerator()
    return generator.generate_pin(length).password

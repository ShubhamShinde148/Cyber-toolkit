import math
import re


class PasswordStrengthAnalyzer:
    COMMON_PATTERNS = (
        "password", "qwerty", "admin", "welcome", "letmein",
        "123456", "12345678", "abc123", "iloveyou", "football",
    )

    def analyze(self, password):
        password = password or ""
        length = len(password)

        has_uppercase = any(c.isupper() for c in password)
        has_lowercase = any(c.islower() for c in password)
        has_digits = any(c.isdigit() for c in password)
        has_special = any(not c.isalnum() for c in password)
        has_repeated = self._has_repeated_sequence(password)
        has_sequential = self._has_sequential_chars(password)
        has_common_pattern = self._has_common_pattern(password)
        unique_chars = len(set(password))

        score = 0
        checks_passed = []
        checks_failed = []
        suggestions = []

        # Length scoring
        if length >= 16:
            score += 30
            checks_passed.append("Length is excellent (16+ characters)")
        elif length >= 12:
            score += 22
            checks_passed.append("Length is strong (12+ characters)")
        elif length >= 8:
            score += 14
            checks_passed.append("Length is acceptable (8+ characters)")
            checks_failed.append("Use 12+ characters for stronger security")
            suggestions.append("Increase password length to at least 12 characters")
        else:
            score += 4
            checks_failed.append("Password is too short")
            suggestions.append("Use at least 12 characters")

        # Character variety scoring
        if has_uppercase:
            score += 10
            checks_passed.append("Contains uppercase letters")
        else:
            checks_failed.append("No uppercase letters")
            suggestions.append("Add uppercase letters")

        if has_lowercase:
            score += 10
            checks_passed.append("Contains lowercase letters")
        else:
            checks_failed.append("No lowercase letters")
            suggestions.append("Add lowercase letters")

        if has_digits:
            score += 10
            checks_passed.append("Contains digits")
        else:
            checks_failed.append("No digits")
            suggestions.append("Add numbers")

        if has_special:
            score += 12
            checks_passed.append("Contains special characters")
        else:
            checks_failed.append("No special characters")
            suggestions.append("Add special characters (e.g. !@#$)")

        # Penalties
        if has_repeated:
            score -= 8
            checks_failed.append("Contains repeated character patterns")
            suggestions.append("Avoid repeated character patterns (e.g. aaa, 111)")

        if has_sequential:
            score -= 10
            checks_failed.append("Contains sequential patterns")
            suggestions.append("Avoid sequences like abc, 123, qwerty")

        if has_common_pattern:
            score -= 25
            checks_failed.append("Contains common password words/patterns")
            suggestions.append("Avoid common words like 'password' or 'admin'")

        # Bonus for diversity
        if unique_chars >= max(8, length // 2):
            score += 8
            checks_passed.append("Good character diversity")

        score = max(0, min(100, int(score)))
        strength_level = self._score_to_level(score)

        entropy_bits = self._estimate_entropy_bits(
            password=password,
            has_uppercase=has_uppercase,
            has_lowercase=has_lowercase,
            has_digits=has_digits,
            has_special=has_special,
        )
        crack_time_display = self._format_crack_time(entropy_bits)

        # De-duplicate suggestions while preserving order.
        deduped_suggestions = []
        for s in suggestions:
            if s not in deduped_suggestions:
                deduped_suggestions.append(s)

        return {
            "password_length": length,
            "strength_level": strength_level,
            "strength_score": score,
            "entropy_bits": round(entropy_bits, 1),
            "crack_time_display": crack_time_display,
            "has_uppercase": has_uppercase,
            "has_lowercase": has_lowercase,
            "has_digits": has_digits,
            "has_special": has_special,
            "has_repeated": has_repeated,
            "has_sequential": has_sequential,
            "has_common_pattern": has_common_pattern,
            "checks_passed": checks_passed,
            "checks_failed": checks_failed,
            "suggestions": deduped_suggestions,
            "unique_chars": unique_chars,
        }

    def _score_to_level(self, score):
        if score < 20:
            return "Very Weak"
        if score < 40:
            return "Weak"
        if score < 60:
            return "Fair"
        if score < 80:
            return "Strong"
        return "Very Strong"

    def _has_repeated_sequence(self, password):
        return re.search(r"(.)\1\1", password) is not None

    def _has_sequential_chars(self, password):
        if len(password) < 3:
            return False
        lowered = password.lower()
        seqs = "abcdefghijklmnopqrstuvwxyz0123456789"
        rev_seqs = seqs[::-1]
        for i in range(len(lowered) - 2):
            tri = lowered[i:i + 3]
            if tri in seqs or tri in rev_seqs:
                return True
        return False

    def _has_common_pattern(self, password):
        lowered = password.lower()
        return any(p in lowered for p in self.COMMON_PATTERNS)

    def _estimate_entropy_bits(self, password, has_uppercase, has_lowercase, has_digits, has_special):
        charset_size = 0
        if has_lowercase:
            charset_size += 26
        if has_uppercase:
            charset_size += 26
        if has_digits:
            charset_size += 10
        if has_special:
            charset_size += 32
        if charset_size == 0 or not password:
            return 0.0
        return len(password) * math.log2(charset_size)

    def _format_crack_time(self, entropy_bits):
        if entropy_bits <= 0:
            return "Instant"

        # Approximate offline cracking speed for modern GPU rigs.
        guesses_per_second = 1e9
        seconds = (2 ** entropy_bits) / guesses_per_second

        minute = 60
        hour = 3600
        day = 86400
        year = 31536000

        if seconds < 1:
            return "Less than a second"
        if seconds < minute:
            return f"{int(seconds)} seconds"
        if seconds < hour:
            return f"{int(seconds / minute)} minutes"
        if seconds < day:
            return f"{int(seconds / hour)} hours"
        if seconds < year:
            return f"{int(seconds / day)} days"
        years = seconds / year
        if years < 1e6:
            return f"{int(years)} years"
        return "Millions of years"

function analyzePassword(password) {
  const checks = {
    minLength: password.length >= 12,
    hasUppercase: /[A-Z]/.test(password),
    hasLowercase: /[a-z]/.test(password),
    hasNumber: /[0-9]/.test(password),
    hasSymbol: /[^A-Za-z0-9]/.test(password),
    noRepeatingTriples: !/(.)\1\1/.test(password),
  };

  const passed = Object.values(checks).filter(Boolean).length;
  const score = Math.round((passed / Object.keys(checks).length) * 100);

  let level = 'Weak';
  if (score >= 80) level = 'Very Strong';
  else if (score >= 65) level = 'Strong';
  else if (score >= 45) level = 'Medium';

  const suggestions = [];
  if (!checks.minLength) suggestions.push('Use at least 12 characters.');
  if (!checks.hasUppercase) suggestions.push('Add uppercase letters.');
  if (!checks.hasLowercase) suggestions.push('Add lowercase letters.');
  if (!checks.hasNumber) suggestions.push('Add numbers.');
  if (!checks.hasSymbol) suggestions.push('Add symbols like !@#$%.');
  if (!checks.noRepeatingTriples) suggestions.push('Avoid repeated character patterns.');

  return {
    score,
    level,
    checks,
    suggestions,
  };
}

module.exports = { analyzePassword };

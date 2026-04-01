function shiftChar(char, shift) {
  const code = char.charCodeAt(0);
  const isUpper = code >= 65 && code <= 90;
  const isLower = code >= 97 && code <= 122;

  if (!isUpper && !isLower) return char;

  const base = isUpper ? 65 : 97;
  const normalized = code - base;
  const shifted = (normalized + shift + 26) % 26;

  return String.fromCharCode(base + shifted);
}

function rot13(input) {
  return [...input].map((c) => shiftChar(c, 13)).join('');
}

function caesar(input, shift) {
  return [...input].map((c) => shiftChar(c, shift)).join('');
}

module.exports = { rot13, caesar };

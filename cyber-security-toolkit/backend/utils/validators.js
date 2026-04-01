function requireTextField(body, fieldName) {
  const value = body?.[fieldName];
  if (typeof value !== 'string' || value.trim() === '') {
    return `${fieldName} is required`;
  }
  return null;
}

function isValidHostname(hostname) {
  if (!hostname || typeof hostname !== 'string') return false;
  return /^[a-zA-Z0-9.-]+$/.test(hostname) && hostname.length <= 253;
}

module.exports = {
  requireTextField,
  isValidHostname,
};

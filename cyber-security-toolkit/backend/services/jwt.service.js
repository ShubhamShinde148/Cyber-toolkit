function base64UrlDecode(input) {
  const normalized = input.replace(/-/g, '+').replace(/_/g, '/');
  const padLength = (4 - (normalized.length % 4)) % 4;
  const padded = normalized + '='.repeat(padLength);
  return Buffer.from(padded, 'base64').toString('utf8');
}

function decodeJwt(token) {
  const parts = token.split('.');
  if (parts.length < 2) {
    throw new Error('Invalid JWT format');
  }

  let header;
  let payload;

  try {
    header = JSON.parse(base64UrlDecode(parts[0]));
    payload = JSON.parse(base64UrlDecode(parts[1]));
  } catch (error) {
    throw new Error('Unable to decode JWT payload');
  }

  return {
    header,
    payload,
    signature: parts[2] || null,
  };
}

module.exports = { decodeJwt };

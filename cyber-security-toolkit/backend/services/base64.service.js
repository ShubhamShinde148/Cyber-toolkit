function encodeBase64(input) {
  return Buffer.from(input, 'utf8').toString('base64');
}

function decodeBase64(input) {
  try {
    return Buffer.from(input, 'base64').toString('utf8');
  } catch (error) {
    throw new Error('Invalid Base64 string');
  }
}

module.exports = { encodeBase64, decodeBase64 };

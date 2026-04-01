function encodeUrl(input) {
  return encodeURIComponent(input);
}

function decodeUrl(input) {
  try {
    return decodeURIComponent(input);
  } catch (error) {
    throw new Error('Invalid URL-encoded string');
  }
}

module.exports = { encodeUrl, decodeUrl };

async function lookupIp(ip) {
  const endpoint = `https://ipapi.co/${encodeURIComponent(ip)}/json/`;
  const response = await fetch(endpoint);

  if (!response.ok) {
    throw new Error('IP lookup API request failed');
  }

  const data = await response.json();

  if (data.error) {
    throw new Error(data.reason || 'IP lookup failed');
  }

  return {
    ip: data.ip,
    city: data.city,
    region: data.region,
    country: data.country_name,
    countryCode: data.country_code,
    latitude: data.latitude,
    longitude: data.longitude,
    org: data.org,
    timezone: data.timezone,
    asn: data.asn,
  };
}

module.exports = { lookupIp };

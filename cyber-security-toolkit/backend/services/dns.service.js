async function dnsLookup(domain, type = 'A') {
  const endpoint = `https://dns.google/resolve?name=${encodeURIComponent(domain)}&type=${encodeURIComponent(type)}`;
  const response = await fetch(endpoint);

  if (!response.ok) {
    throw new Error('DNS API request failed');
  }

  const data = await response.json();
  const answers = (data.Answer || []).map((item) => ({
    name: item.name,
    type: item.type,
    ttl: item.TTL,
    data: item.data,
  }));

  return {
    status: data.Status,
    question: data.Question || [],
    answers,
  };
}

module.exports = { dnsLookup };

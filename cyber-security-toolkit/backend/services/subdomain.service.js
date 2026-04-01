const dns = require('dns').promises;
const { commonWordlist } = require('../utils/wordlist');

async function fetchCrtSh(domain) {
  try {
    const response = await fetch(`https://crt.sh/?q=%25.${encodeURIComponent(domain)}&output=json`);
    if (!response.ok) return [];
    const rows = await response.json();
    const out = new Set();

    rows.forEach((row) => {
      String(row.name_value || '')
        .split('\n')
        .map((v) => v.replace(/^\*\./, '').trim().toLowerCase())
        .filter((v) => v.endsWith(`.${domain}`) || v === domain)
        .forEach((v) => out.add(v));
    });

    return [...out];
  } catch {
    return [];
  }
}

async function fetchBufferOver(domain) {
  try {
    const response = await fetch(`https://dns.bufferover.run/dns?q=.${encodeURIComponent(domain)}`);
    if (!response.ok) return [];
    const data = await response.json();
    const rows = [...(data.FDNS_A || []), ...(data.RDNS || [])];
    const out = new Set();

    rows.forEach((row) => {
      const value = String(row).split(',').pop().trim().toLowerCase().replace(/^\*\./, '');
      if (value.endsWith(`.${domain}`) || value === domain) {
        out.add(value);
      }
    });

    return [...out];
  } catch {
    return [];
  }
}

function buildWordlistCandidates(domain, customWords = []) {
  const words = [...new Set([...commonWordlist, ...customWords.map((w) => String(w).trim().toLowerCase())])]
    .filter(Boolean);
  return words.map((w) => `${w}.${domain}`);
}

async function resolveHost(hostname) {
  try {
    const records = await dns.lookup(hostname, { all: true });
    if (!records?.length) return null;
    return records[0].address;
  } catch {
    return null;
  }
}

async function findSubdomains(domain, customWordlist = []) {
  const cleanDomain = String(domain || '').trim().toLowerCase().replace(/^https?:\/\//, '').split('/')[0];
  if (!cleanDomain) {
    throw new Error('Domain is required');
  }

  const [crtSh, bufferOver] = await Promise.all([
    fetchCrtSh(cleanDomain),
    fetchBufferOver(cleanDomain),
  ]);

  const apiCandidates = new Set([...crtSh, ...bufferOver]);
  const wordlistCandidates = buildWordlistCandidates(cleanDomain, customWordlist);
  const allCandidates = [...new Set([...apiCandidates, ...wordlistCandidates])]
    .filter((host) => host.endsWith(`.${cleanDomain}`) || host === cleanDomain);

  const resolved = await Promise.all(
    allCandidates.map(async (host) => {
      const ip = await resolveHost(host);
      if (!ip) return null;
      return {
        subdomain: host,
        ip,
        source: apiCandidates.has(host) ? 'api+wordlist' : 'wordlist',
      };
    })
  );

  const valid = resolved.filter(Boolean).sort((a, b) => a.subdomain.localeCompare(b.subdomain));

  return {
    domain: cleanDomain,
    totalCandidates: allCandidates.length,
    totalValid: valid.length,
    validSubdomains: valid,
    sources: {
      apiCandidates: apiCandidates.size,
      wordlistCandidates: wordlistCandidates.length,
    },
  };
}

module.exports = { findSubdomains };

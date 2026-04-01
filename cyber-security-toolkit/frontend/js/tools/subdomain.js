import { postJson } from '../api.js';

export const subdomainTool = {
  id: 'subdomain',
  name: 'Subdomain Finder (API + Wordlist)',
  description: 'Combine passive API sources + wordlist and keep only DNS-valid subdomains.',
  render: () => `
    <h2>${subdomainTool.name}</h2>
    <label>Target Domain</label>
    <input id="subdomain-domain" type="text" placeholder="example.com" />
    <label>Custom Wordlist (optional, comma-separated)</label>
    <input id="subdomain-words" type="text" placeholder="dev,uat,stage" />
    <button class="btn" id="subdomain-find">Find Subdomains</button>
    <div id="subdomain-result" class="result" style="display:none"></div>
  `,
  bind: () => {
    const domain = document.getElementById('subdomain-domain');
    const words = document.getElementById('subdomain-words');
    const result = document.getElementById('subdomain-result');
    const show = (msg, err = false) => { result.style.display = 'block'; result.classList.toggle('error', err); result.textContent = msg; };

    document.getElementById('subdomain-find').addEventListener('click', async () => {
      try {
        const wordlist = words.value
          .split(',')
          .map((w) => w.trim())
          .filter(Boolean);

        const data = await postJson('/api/subdomain/find', { domain: domain.value.trim(), wordlist });
        show(JSON.stringify(data.data, null, 2));
      } catch (e) {
        show(e.message, true);
      }
    });
  },
};

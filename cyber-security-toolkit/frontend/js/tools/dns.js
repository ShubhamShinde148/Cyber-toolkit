import { postJson } from '../api.js';

export const dnsTool = {
  id: 'dns',
  name: 'DNS Lookup Tool',
  description: 'Resolve DNS records via DNS-over-HTTPS API.',
  render: () => `
    <h2>${dnsTool.name}</h2>
    <div class="row">
      <div>
        <label>Domain</label>
        <input id="dns-domain" type="text" placeholder="example.com" />
      </div>
      <div>
        <label>Record Type</label>
        <select id="dns-type">
          <option value="A">A</option>
          <option value="AAAA">AAAA</option>
          <option value="MX">MX</option>
          <option value="TXT">TXT</option>
          <option value="NS">NS</option>
        </select>
      </div>
    </div>
    <button class="btn" id="dns-lookup">Lookup DNS</button>
    <div id="dns-result" class="result" style="display:none"></div>
  `,
  bind: () => {
    const domain = document.getElementById('dns-domain');
    const type = document.getElementById('dns-type');
    const result = document.getElementById('dns-result');
    const show = (msg, err = false) => { result.style.display = 'block'; result.classList.toggle('error', err); result.textContent = msg; };

    document.getElementById('dns-lookup').addEventListener('click', async () => {
      try {
        const data = await postJson('/api/dns/lookup', { domain: domain.value.trim(), type: type.value });
        show(JSON.stringify(data.data, null, 2));
      } catch (e) { show(e.message, true); }
    });
  },
};

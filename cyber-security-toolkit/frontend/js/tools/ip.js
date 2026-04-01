import { postJson } from '../api.js';

export const ipTool = {
  id: 'ip',
  name: 'IP Intelligence Lookup',
  description: 'Query IP metadata from external threat intelligence API.',
  render: () => `
    <h2>${ipTool.name}</h2>
    <label>IP Address</label>
    <input id="ip-input" type="text" placeholder="e.g. 8.8.8.8" />
    <button class="btn" id="ip-lookup">Lookup</button>
    <div id="ip-result" class="result" style="display:none"></div>
  `,
  bind: () => {
    const input = document.getElementById('ip-input');
    const result = document.getElementById('ip-result');
    const show = (msg, err = false) => { result.style.display = 'block'; result.classList.toggle('error', err); result.textContent = msg; };

    document.getElementById('ip-lookup').addEventListener('click', async () => {
      try {
        const data = await postJson('/api/ip/lookup', { ip: input.value.trim() });
        show(JSON.stringify(data.data, null, 2));
      } catch (e) { show(e.message, true); }
    });
  },
};

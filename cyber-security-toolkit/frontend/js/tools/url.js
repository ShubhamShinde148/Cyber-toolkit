import { postJson } from '../api.js';

export const urlTool = {
  id: 'url',
  name: 'URL Encoder / Decoder',
  description: 'Encode unsafe URL characters and decode encoded text.',
  render: () => `
    <h2>${urlTool.name}</h2>
    <label>Input</label>
    <textarea id="url-input" placeholder="Enter URL text..."></textarea>
    <div class="row">
      <button class="btn" id="url-encode">Encode</button>
      <button class="btn" id="url-decode">Decode</button>
    </div>
    <div id="url-result" class="result" style="display:none"></div>
  `,
  bind: () => {
    const input = document.getElementById('url-input');
    const result = document.getElementById('url-result');
    const show = (msg, err = false) => { result.style.display = 'block'; result.classList.toggle('error', err); result.textContent = msg; };

    document.getElementById('url-encode').addEventListener('click', async () => {
      try { show((await postJson('/api/url/encode', { text: input.value })).output); }
      catch (e) { show(e.message, true); }
    });

    document.getElementById('url-decode').addEventListener('click', async () => {
      try { show((await postJson('/api/url/decode', { text: input.value })).output); }
      catch (e) { show(e.message, true); }
    });
  },
};

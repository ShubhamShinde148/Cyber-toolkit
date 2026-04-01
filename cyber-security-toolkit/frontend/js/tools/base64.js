import { postJson } from '../api.js';

export const base64Tool = {
  id: 'base64',
  name: 'Base64 Encoder / Decoder',
  description: 'Convert plaintext to Base64 and decode back safely.',
  render: () => `
    <h2>${base64Tool.name}</h2>
    <label>Input Text</label>
    <textarea id="base64-input" placeholder="Type text or Base64 value..."></textarea>
    <div class="row">
      <button class="btn" id="base64-encode">Encode</button>
      <button class="btn" id="base64-decode">Decode</button>
    </div>
    <div id="base64-result" class="result" style="display:none"></div>
  `,
  bind: () => {
    const input = document.getElementById('base64-input');
    const result = document.getElementById('base64-result');

    const show = (message, isError = false) => {
      result.style.display = 'block';
      result.classList.toggle('error', isError);
      result.textContent = message;
    };

    document.getElementById('base64-encode').addEventListener('click', async () => {
      const text = input.value.trim();
      if (!text) return show('Please enter input text.', true);
      try {
        const data = await postJson('/api/base64/encode', { text });
        show(data.output);
      } catch (err) {
        show(err.message, true);
      }
    });

    document.getElementById('base64-decode').addEventListener('click', async () => {
      const text = input.value.trim();
      if (!text) return show('Please enter input text.', true);
      try {
        const data = await postJson('/api/base64/decode', { text });
        show(data.output);
      } catch (err) {
        show(err.message, true);
      }
    });
  },
};

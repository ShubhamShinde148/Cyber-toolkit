import { postJson } from '../api.js';

export const jwtTool = {
  id: 'jwt',
  name: 'JWT Token Decoder',
  description: 'Decode JWT header and payload without verifying signature.',
  render: () => `
    <h2>${jwtTool.name}</h2>
    <label>JWT Token</label>
    <textarea id="jwt-input" placeholder="Paste JWT token..."></textarea>
    <button class="btn" id="jwt-decode">Decode Token</button>
    <div id="jwt-result" class="result" style="display:none"></div>
  `,
  bind: () => {
    const input = document.getElementById('jwt-input');
    const result = document.getElementById('jwt-result');
    const show = (msg, err = false) => { result.style.display = 'block'; result.classList.toggle('error', err); result.textContent = msg; };

    document.getElementById('jwt-decode').addEventListener('click', async () => {
      try {
        const data = await postJson('/api/jwt/decode', { token: input.value.trim() });
        show(JSON.stringify({ header: data.header, payload: data.payload, signature: data.signature }, null, 2));
      } catch (e) {
        show(e.message, true);
      }
    });
  },
};

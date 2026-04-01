import { postJson } from '../api.js';

export const cipherTool = {
  id: 'cipher',
  name: 'ROT13 / Caesar Cipher',
  description: 'Apply ROT13 or Caesar shift for basic text obfuscation.',
  render: () => `
    <h2>${cipherTool.name}</h2>
    <label>Input Text</label>
    <textarea id="cipher-input" placeholder="Enter text..."></textarea>
    <label>Caesar Shift (-25 to 25)</label>
    <input id="cipher-shift" type="number" value="3" min="-25" max="25" />
    <div class="row">
      <button class="btn" id="cipher-rot13">ROT13</button>
      <button class="btn" id="cipher-caesar">Caesar</button>
    </div>
    <div id="cipher-result" class="result" style="display:none"></div>
  `,
  bind: () => {
    const input = document.getElementById('cipher-input');
    const shift = document.getElementById('cipher-shift');
    const result = document.getElementById('cipher-result');
    const show = (msg, err = false) => { result.style.display = 'block'; result.classList.toggle('error', err); result.textContent = msg; };

    document.getElementById('cipher-rot13').addEventListener('click', async () => {
      try {
        const data = await postJson('/api/cipher/rot13', { text: input.value });
        show(data.output);
      } catch (e) { show(e.message, true); }
    });

    document.getElementById('cipher-caesar').addEventListener('click', async () => {
      try {
        const data = await postJson('/api/cipher/caesar', { text: input.value, shift: Number(shift.value) });
        show(data.output);
      } catch (e) { show(e.message, true); }
    });
  },
};

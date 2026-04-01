import { postJson } from '../api.js';

export const passwordTool = {
  id: 'password',
  name: 'Password Strength Analyzer',
  description: 'Analyze complexity, checks, and suggestions for stronger passwords.',
  render: () => `
    <h2>${passwordTool.name}</h2>
    <label>Password</label>
    <input id="password-input" type="password" placeholder="Enter password..." />
    <button class="btn" id="password-check">Analyze</button>
    <div id="password-result" class="result" style="display:none"></div>
  `,
  bind: () => {
    const input = document.getElementById('password-input');
    const result = document.getElementById('password-result');
    const show = (msg, err = false) => { result.style.display = 'block'; result.classList.toggle('error', err); result.textContent = msg; };

    document.getElementById('password-check').addEventListener('click', async () => {
      try {
        const data = await postJson('/api/password/strength', { password: input.value });
        show(JSON.stringify(data.analysis, null, 2));
      } catch (e) { show(e.message, true); }
    });
  },
};

import { navbar } from './components/navbar.js';
import { toolCards } from './components/cards.js';

import { base64Tool } from './tools/base64.js';
import { cipherTool } from './tools/cipher.js';
import { urlTool } from './tools/url.js';
import { jwtTool } from './tools/jwt.js';
import { passwordTool } from './tools/password.js';
import { ipTool } from './tools/ip.js';
import { dnsTool } from './tools/dns.js';
import { subdomainTool } from './tools/subdomain.js';

const tools = [
  base64Tool,
  cipherTool,
  urlTool,
  jwtTool,
  passwordTool,
  ipTool,
  dnsTool,
  subdomainTool,
];

let activeToolId = base64Tool.id;

function renderApp() {
  const activeTool = tools.find((t) => t.id === activeToolId) || tools[0];

  const html = `
    ${navbar()}
    <main class="main">
      <section class="hero">
        <h1>Cyber Security Toolkit Dashboard</h1>
        <p>Modular defensive toolkit with encoding, token parsing, intelligence lookups, and recon utilities.</p>
      </section>

      <section class="grid" id="tool-grid">
        ${toolCards(tools, activeToolId)}
      </section>

      <section class="workspace" id="workspace">
        ${activeTool.render()}
      </section>
    </main>
  `;

  const app = document.getElementById('app');
  app.innerHTML = html;

  // Bind card actions.
  document.querySelectorAll('[data-tool-id]').forEach((card) => {
    card.addEventListener('click', () => {
      activeToolId = card.getAttribute('data-tool-id');
      renderApp();
    });
  });

  // Bind active tool handlers.
  activeTool.bind();
}

renderApp();

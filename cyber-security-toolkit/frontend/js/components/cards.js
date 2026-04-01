export function toolCards(tools, activeId) {
  return tools.map((tool) => `
    <article class="tool-card ${activeId === tool.id ? 'active' : ''}" data-tool-id="${tool.id}">
      <h3 class="tool-name">${tool.name}</h3>
      <p class="tool-desc">${tool.description}</p>
    </article>
  `).join('');
}

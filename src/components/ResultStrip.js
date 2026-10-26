export function ResultStrip(title, note) {
  return `
    <aside class="result-strip" aria-label="${title}">
      <span class="result-marker" aria-hidden="true"></span>
      <div><strong>${title}</strong><span>${note}</span></div>
      <span class="status-pill status-hold">Held for review</span>
    </aside>
  `
}

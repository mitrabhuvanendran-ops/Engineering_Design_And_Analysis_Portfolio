export function StatTile(stat) {
  return `
    <article class="stat-tile">
      <span class="stat-unit">${stat.unit}</span>
      <p class="stat-value" data-count="${stat.value}">${String(stat.value).padStart(2, '0')}</p>
      <p class="stat-label">${stat.label}</p>
    </article>
  `
}

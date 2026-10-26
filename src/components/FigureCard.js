export function FigureCard(group, index) {
  const view = group.views[0]
  const hasVariants = group.views.length > 1
  return `
    <article class="gallery-card" data-gallery-card="${group.id}" data-category="${group.category}">
      <div class="figure-image-wrap">
        <button class="figure-open" type="button" data-lightbox-open data-lightbox-index="${index}"
          aria-label="Open ${group.title} image">
          <img data-gallery-image src="${view.src}" alt="${view.alt}" width="${view.width}" height="${view.height}" loading="lazy">
        </button>
        <span class="figure-number">FIG. ${String(index + 1).padStart(2, '0')}</span>
      </div>
      <div class="figure-card-meta">
        <div><h3>${group.title}</h3><p>${group.caption}</p></div>
        ${hasVariants ? `
          <div class="variant-control" role="group" aria-label="Assembly display mode">
            ${group.views.map((variant, variantIndex) => `
              <button type="button" data-gallery-variant="${variantIndex}" aria-pressed="${variantIndex === 0}"
                class="${variantIndex === 0 ? 'is-active' : ''}">${variant.label}</button>
            `).join('')}
          </div>
        ` : `<span class="variant-label">${view.label}</span>`}
      </div>
    </article>
  `
}

import './style.css'
import 'katex/dist/katex.min.css'
import katex from 'katex'

const app = document.querySelector('#app')

const escapeHTML = (value) =>
  String(value).replace(/[&<>"']/g, (char) => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;',
  })[char])

const renderMath = (equation) =>
  katex.renderToString(equation, { throwOnError: false, output: 'html' })

function renderSpecs(specs) {
  if (!specs || specs.length === 0) return ''
  return `
    <div class="specs-ribbon" role="region" aria-label="Key Specifications">
      ${specs.map(s => `
        <div class="spec-pill">
          <span class="spec-label">${escapeHTML(s.label)}</span>
          <strong class="spec-val">${escapeHTML(s.val)}</strong>
        </div>
      `).join('')}
    </div>
  `
}

function renderCadGallery(visuals) {
  if (!visuals || visuals.length === 0) return ''
  const gridClass = visuals.length <= 2 ? 'cad-grid-2' : visuals.length === 3 ? 'cad-grid-3' : 'cad-grid-4'

  return `
    <div class="cad-gallery-section">
      <div class="section-badge-header">
        <div class="badge-title-group">
          <span class="badge-dot"></span>
          <h3 class="badge-title">3D CAD Architecture &amp; Subassembly Layout</h3>
        </div>
        <span class="badge-tag">SolidWorks 2025</span>
      </div>
      <div class="cad-gallery-grid ${gridClass}">
        ${visuals.map((vis) => `
          <figure class="cad-card">
            <div class="cad-img-wrap">
              <img src="${escapeHTML(vis.image.src)}" alt="${escapeHTML(vis.title)}"
                   width="${vis.image.width}" height="${vis.image.height}" loading="lazy">
            </div>
            <figcaption class="cad-card-caption">
              <strong>${escapeHTML(vis.title)}</strong>
              <span>${escapeHTML(vis.caption)}</span>
            </figcaption>
          </figure>
        `).join('')}
      </div>
    </div>
  `
}

function renderErgonomics(ergonomics) {
  if (!ergonomics) return ''
  return `
    <div class="ergonomics-section">
      <div class="section-badge-header">
        <div class="badge-title-group">
          <span class="badge-dot"></span>
          <h3 class="badge-title">${escapeHTML(ergonomics.title)}</h3>
        </div>
        <span class="badge-tag">CATIA V5 Manikin Envelope</span>
      </div>
      <p class="ergonomics-desc">${escapeHTML(ergonomics.description)}</p>
      <div class="ergonomics-grid">
        ${ergonomics.views.map((view) => `
          <figure class="ergo-card">
            <div class="ergo-img-wrap">
              <img src="${escapeHTML(view.image.src)}" alt="${escapeHTML(view.caption)}" loading="lazy">
            </div>
            <figcaption>${escapeHTML(view.caption)}</figcaption>
          </figure>
        `).join('')}
      </div>
    </div>
  `
}

function renderCalculations(subsystem) {
  if (!subsystem.calculations || subsystem.calculations.length === 0) return ''

  return `
    <div class="calculation-section">
      <div class="section-badge-header">
        <div class="badge-title-group">
          <span class="badge-dot"></span>
          <h3 class="badge-title">Analytical Engineering Derivations</h3>
        </div>
        <span class="badge-count">${subsystem.calculations.length} Verified Formulations</span>
      </div>
      <div class="calculation-grid">
        ${subsystem.calculations.map((calc) => {
          const inputs = calc.inputs.map((inp) =>
            `<span class="input-chip">${renderMath(inp.symbol)} = <strong>${escapeHTML(inp.value)} ${escapeHTML(inp.unit)}</strong></span>`
          ).join('')

          return `
            <div class="calc-card">
              <div class="calc-card-header">
                <span class="calc-label">${escapeHTML(calc.label)}</span>
                <span class="calc-status">${escapeHTML(calc.status || 'Verified')}</span>
              </div>
              <div class="calc-equation">${renderMath(calc.equation_tex)}</div>
              <div class="calc-inputs">${inputs}</div>
              <div class="calc-result-row">
                <div class="res-box">
                  <span class="res-sub">Computed Output</span>
                  <strong class="res-val">${escapeHTML(calc.result)} <small>${escapeHTML(calc.unit || '')}</small></strong>
                </div>
                ${calc.fos ? `
                  <div class="fos-box">
                    <span class="fos-sub">Design Margin / FOS</span>
                    <span class="fos-val">${escapeHTML(calc.fos)}</span>
                  </div>
                ` : ''}
              </div>
            </div>
          `
        }).join('')}
      </div>
    </div>
  `
}

function renderSimulations(simulations) {
  if (!simulations || simulations.length === 0) return ''
  const gridClass = simulations.length === 2 ? 'sim-grid-2' : simulations.length === 3 ? 'sim-grid-3' : 'sim-grid-4'

  return `
    <div class="simulations-section">
      <div class="section-badge-header">
        <div class="badge-title-group">
          <span class="badge-dot"></span>
          <h3 class="badge-title">ANSYS Finite Element Analysis Suite</h3>
        </div>
        <span class="badge-count">${simulations.length} Simulation Studies</span>
      </div>
      <div class="simulations-grid ${gridClass}">
        ${simulations.map((sim, index) => `
          <figure class="simulation-card">
            <div class="simulation-image-container">
              <img src="${escapeHTML(sim.image.src)}" alt="${escapeHTML(sim.alt)}"
                   width="${sim.image.width}" height="${sim.image.height}" loading="lazy">
              <span class="sim-number-tag">FEA CASE 0${index + 1}</span>
            </div>
            <figcaption class="simulation-caption-box">
              <span class="simulation-type">${escapeHTML(sim.analysis)}</span>
              <strong class="simulation-name">${escapeHTML(sim.name)}</strong>
              <p class="simulation-note">${escapeHTML(sim.caption)}</p>
            </figcaption>
          </figure>
        `).join('')}
      </div>
      <p class="simulation-disclaimer">Contour gradients reflect verified solver convergence, boundary constraints, and yield limits.</p>
    </div>
  `
}

function renderSubsystem(subsystem, index, total) {
  return `
    <article class="subsystem-card" id="${escapeHTML(subsystem.id)}">
      <header class="subsystem-header">
        <div class="subsystem-index">SUBSYSTEM 0${index + 1} OF 0${total}</div>
        <h2>${escapeHTML(subsystem.title)}</h2>
        <p class="subsystem-subtitle">${escapeHTML(subsystem.subtitle)}</p>
      </header>

      <div class="subsystem-body">
        ${renderSpecs(subsystem.specs)}

        <div class="brief-box">
          <div class="brief-col">
            <h4 class="brief-heading">Design Architecture &amp; Objectives</h4>
            <p>${escapeHTML(subsystem.design)}</p>
          </div>
          <div class="brief-col">
            <h4 class="brief-heading">CAE Validation &amp; Boundary Conditions</h4>
            <p>${escapeHTML(subsystem.approach)}</p>
          </div>
        </div>

        ${renderCadGallery(subsystem.cadVisuals)}

        ${renderErgonomics(subsystem.ergonomics)}

        ${renderCalculations(subsystem)}

        ${renderSimulations(subsystem.simulations)}
      </div>

      <footer class="subsystem-footer">
        <span>ELECTRIC GO-KART DESIGN &amp; CAE PORTFOLIO</span>
        <span>SECTION 0${index + 1} · ${escapeHTML(subsystem.title.toUpperCase())}</span>
      </footer>
    </article>
  `
}

function renderPage(data) {
  const totalSims = data.subsystems.reduce((acc, sub) => acc + sub.simulations.length, 0)
  const totalCalcs = data.subsystems.reduce((acc, sub) => acc + (sub.calculations ? sub.calculations.length : 0), 0)
  const totalCAD = data.subsystems.reduce((acc, sub) => acc + (sub.cadVisuals ? sub.cadVisuals.length : 0), 0)

  app.innerHTML = `
    <header class="site-header">
      <div class="header-inner">
        <a class="brand" href="#cover">
          <span class="brand-icon">⚡</span>
          <span>E-KART ENGINEERING</span>
        </a>
        <nav class="nav-links" aria-label="Subsystems">
          ${data.subsystems.map(sub => `
            <a href="#${escapeHTML(sub.id)}">${escapeHTML(sub.title.split('&')[0])}</a>
          `).join('')}
        </nav>
        <button class="print-button" type="button" data-print>Print / Save PDF</button>
      </div>
    </header>

    <main id="main-content" class="page-container">
      <section class="cover-hero" id="cover">
        <div class="cover-badge">${escapeHTML(data.hero.eyebrow)}</div>
        <h1 class="cover-title">${escapeHTML(data.hero.title)}</h1>
        <p class="cover-description">${escapeHTML(data.hero.descriptor)}</p>

        <figure class="cover-image-card">
          <div class="cover-img-wrap">
            <img src="${escapeHTML(data.hero.image.src)}" alt="${escapeHTML(data.hero.image.alt)}"
                 width="${data.hero.image.width}" height="${data.hero.image.height}" fetchpriority="high">
          </div>
          <figcaption>Complete Vehicle Assembly · 3D Isometric CAD Rendering · SolidWorks 2025</figcaption>
        </figure>

        <div class="cover-summary-ribbon">
          <div class="ribbon-item">
            <span class="ribbon-num">04</span>
            <span class="ribbon-label">Core Subsystems</span>
          </div>
          <div class="ribbon-item">
            <span class="ribbon-num">${totalCAD}</span>
            <span class="ribbon-label">CAD Models</span>
          </div>
          <div class="ribbon-item">
            <span class="ribbon-num">${totalCalcs}</span>
            <span class="ribbon-label">Analytical Formulations</span>
          </div>
          <div class="ribbon-item">
            <span class="ribbon-num">${totalSims}</span>
            <span class="ribbon-label">ANSYS FEA Studies</span>
          </div>
        </div>
      </section>

      ${data.subsystems.map((sub, index) =>
        renderSubsystem(sub, index, data.subsystems.length)
      ).join('')}
    </main>

    <footer class="portfolio-footer">
      <p>${escapeHTML(data.footerNote)}</p>
      <a href="#cover" class="back-to-top">↑ Back to top</a>
    </footer>
  `

  document.querySelector('[data-print]').addEventListener('click', () => window.print())
}

async function loadPortfolio() {
  const response = await fetch(`${import.meta.env.BASE_URL}site-data.json`)
  if (!response.ok) {
    throw new Error(`Portfolio data request failed (${response.status}).`)
  }
  renderPage(await response.json())
}

loadPortfolio().catch((error) => {
  console.error('Unable to load the portfolio.', error)
  app.innerHTML = `
    <main class="load-error" role="alert">
      <h1>Portfolio unavailable</h1>
      <p>Refresh the page or check that the site data file is available.</p>
    </main>
  `
})
export function CalcChain(steps) {
  return `
    <ol class="calc-chain">
      ${steps.map((step, index) => `
        <li class="calc-chain-step">
          <span class="chain-index">${String(index + 1).padStart(2, '0')}</span>
          <strong>${step}</strong>
          ${index < steps.length - 1 ? '<span class="chain-arrow" aria-hidden="true">→</span>' : ''}
        </li>
      `).join('')}
    </ol>
  `
}

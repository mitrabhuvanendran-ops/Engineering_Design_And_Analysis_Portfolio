import katex from 'katex'

const renderMath = (equation) =>
  katex.renderToString(equation, { throwOnError: false, output: 'html' })

export function CalcCard(metric) {
  const inputs = metric.inputs
    .map((input) => `${input.symbol}=${input.value} ${input.unit}`)
    .join(' · ')

  return `
    <article class="calc-card">
      <div class="calc-card-top">
        <span>${metric.label}</span>
        <span class="status-pill status-recalculated">Recalculated</span>
      </div>
      <div class="calc-equation">${renderMath(metric.equation_tex)}</div>
      <p class="calc-inputs">${inputs}</p>
      <div class="calc-result">
        <strong>${metric.result}</strong><span>${metric.unit}</span>
      </div>
    </article>
  `
}

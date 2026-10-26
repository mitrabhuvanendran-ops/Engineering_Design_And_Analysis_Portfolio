import katex from 'katex'

const renderMath = (equation) =>
  katex.renderToString(equation, { throwOnError: false, output: 'html' })

function csvCell(value) {
  return `"${String(value).replaceAll('"', '""')}"`
}

export function DataTable(rows) {
  const tableRows = rows.map((row) => `
    <tr data-row>
      <td>${row.label}</td>
      <td class="mono-cell">${renderMath(row.equation_tex)}</td>
      <td class="mono-cell">${row.inputs.map((input) => `${input.value} ${input.unit}`).join(' + ')}</td>
      <td class="numeric-cell">${row.result} <span>${row.unit}</span></td>
      <td><span class="status-pill status-recalculated">Recalculated</span></td>
    </tr>
  `).join('')

  return `
    <div class="data-table-shell">
      <div class="table-controls">
        <label class="search-field">
          <span class="sr-only">Filter calculations</span>
          <span aria-hidden="true">⌕</span>
          <input type="search" data-table-search placeholder="Filter calculations">
        </label>
        <button class="button button-small button-outline" type="button" data-csv>Download CSV</button>
      </div>
      <div class="data-table-wrap">
        <table class="data-table" data-appendix-table>
          <thead><tr>
            <th><button type="button" data-sort="label">Parameter <span>↕</span></button></th>
            <th>Equation</th><th>Inputs</th>
            <th><button type="button" data-sort="result">Recomputed <span>↕</span></button></th>
            <th><button type="button" data-sort="status">Status <span>↕</span></button></th>
          </tr></thead>
          <tbody>${tableRows}</tbody>
        </table>
      </div>
      <p class="table-summary" aria-live="polite" data-table-summary>${rows.length} calculations shown</p>
    </div>
  `
}

export function initDataTable(rows) {
  const table = document.querySelector('[data-appendix-table]')
  const body = table.querySelector('tbody')
  const search = document.querySelector('[data-table-search]')
  let sortKey = 'label'
  let ascending = true
  let filtered = [...rows]
  const rowElements = new Map(
    [...body.querySelectorAll('[data-row]')].map((row) => [row.children[0].textContent, row]),
  )

  const renderRows = () => {
    const query = search.value.trim().toLowerCase()
    filtered = rows.filter((row) =>
      `${row.label} ${row.symbol} ${row.equation_tex} ${row.inputs.map((input) => input.value).join(' ')}`
        .toLowerCase()
        .includes(query),
    )
    filtered.sort((left, right) => {
      const a = left[sortKey]
      const b = right[sortKey]
      const order = typeof a === 'number' ? a - b : String(a).localeCompare(String(b))
      return ascending ? order : -order
    })
    body.replaceChildren(...filtered.map((row) => rowElements.get(row.label)).filter(Boolean))
    document.querySelector('[data-table-summary]').textContent =
      `${filtered.length} calculation${filtered.length === 1 ? '' : 's'} shown`
  }

  search.addEventListener('input', renderRows)
  document.querySelectorAll('[data-sort]').forEach((button) => {
    button.addEventListener('click', () => {
      const nextKey = button.dataset.sort
      ascending = nextKey === sortKey ? !ascending : true
      sortKey = nextKey
      renderRows()
    })
  })

  document.querySelector('[data-csv]').addEventListener('click', () => {
    const header = ['Parameter', 'Symbol', 'Equation', 'Inputs', 'Recomputed', 'Unit', 'Status']
    const records = filtered.map((row) => [
      row.label,
      row.symbol,
      row.equation_tex,
      row.inputs.map((input) => `${input.value} ${input.unit}`).join(' + '),
      row.result,
      row.unit,
      'Recalculated',
    ])
    const content = [header, ...records].map((record) => record.map(csvCell).join(',')).join('\r\n')
    const url = URL.createObjectURL(new Blob([content], { type: 'text/csv;charset=utf-8' }))
    const link = document.createElement('a')
    link.href = url
    link.download = 'design-calculations.csv'
    link.click()
    URL.revokeObjectURL(url)
  })
}

export function ThemeToggle() {
  return `
    <button class="theme-toggle" type="button" data-theme-toggle aria-pressed="false">
      <span class="theme-icon" aria-hidden="true">◐</span><span class="theme-label">Dark mode</span>
    </button>
  `
}

export function initThemeToggle() {
  const button = document.querySelector('[data-theme-toggle]')
  const label = button.querySelector('.theme-label')
  const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches
  const initiallyDark =
    document.documentElement.dataset.theme === 'dark' ||
    (!document.documentElement.dataset.theme && systemDark)
  button.setAttribute('aria-pressed', String(initiallyDark))
  label.textContent = initiallyDark ? 'Light mode' : 'Dark mode'
  button.addEventListener('click', () => {
    const currentlyDark =
      document.documentElement.dataset.theme === 'dark' ||
      (!document.documentElement.dataset.theme && systemDark)
    const dark = !currentlyDark
    document.documentElement.dataset.theme = dark ? 'dark' : 'light'
    button.setAttribute('aria-pressed', String(dark))
    label.textContent = dark ? 'Light mode' : 'Dark mode'
  })
}

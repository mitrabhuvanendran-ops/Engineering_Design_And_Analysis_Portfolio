export function initLightbox(images) {
  const dialog = document.querySelector('.lightbox')
  const image = dialog.querySelector('[data-lightbox-image]')
  const caption = dialog.querySelector('[data-lightbox-caption]')
  const count = dialog.querySelector('[data-lightbox-count]')
  let activeIndex = 0
  let returnFocus = null

  const showImage = (index) => {
    activeIndex = (index + images.length) % images.length
    const item = images[activeIndex]
    image.src = item.src
    image.alt = item.alt
    image.width = item.width
    image.height = item.height
    caption.textContent = item.alt
    count.textContent = `${String(activeIndex + 1).padStart(2, '0')} / ${String(images.length).padStart(2, '0')}`
  }

  document.querySelectorAll('[data-lightbox-open]').forEach((button) => {
    button.addEventListener('click', () => {
      returnFocus = button
      showImage(Number(button.dataset.lightboxIndex))
      dialog.showModal()
    })
  })

  dialog.querySelector('[data-lightbox-close]').addEventListener('click', () => dialog.close())
  dialog.querySelector('[data-lightbox-prev]').addEventListener('click', () => showImage(activeIndex - 1))
  dialog.querySelector('[data-lightbox-next]').addEventListener('click', () => showImage(activeIndex + 1))
  dialog.addEventListener('click', (event) => {
    if (event.target === dialog) dialog.close()
  })
  dialog.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') dialog.close()
    if (event.key === 'ArrowLeft') showImage(activeIndex - 1)
    if (event.key === 'ArrowRight') showImage(activeIndex + 1)
  })
  dialog.addEventListener('close', () => returnFocus?.focus())
}

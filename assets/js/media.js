// Product media may use local /static/images/ paths or HTTPS URLs.
export function imageSource(value) {
  return value;
}

document.addEventListener('error', event => {
  const image = event.target;
  if (image instanceof HTMLImageElement && !image.dataset.fallback) {
    image.dataset.fallback = 'true';
    image.alt = 'Image unavailable; guitar studio photograph shown for illustration.';
    image.src = '/static/images/guitar_front.jpg';
  }
}, true);

// Local copies of the photographs already used in the design reference.
const photos = new Set([
  "photo-1493225457124-a3eb161ffa5f",
  "photo-1510915361894-db8b60106cb1",
  "photo-1516924962500-2b4b3b99ea02",
  "photo-1519892300165-cb5542fb47c7",
  "photo-1525201548942-d8732f6617a0",
  "photo-1550291652-6ea9114a47b1",
  "photo-1550985616-10810253b84d",
  "photo-1564186763535-ebb21ef5277f",
  "photo-1605020420620-20c943cc4669"
]);
export function imageSource(value) {
  try {
    const url = new URL(value);
    const photo = url.pathname.slice(1);
    if (url.hostname === 'images.unsplash.com' && photos.has(photo)) return `/static/images/${photo}.jpg`;
  } catch { /* Keep the supplied path for local assets. */ }
  return value;
}

document.addEventListener('error', event => {
  const image = event.target;
  if (image instanceof HTMLImageElement && !image.dataset.fallback) {
    image.dataset.fallback = 'true';
    image.src = '/static/images/placeholder.svg';
  }
}, true);

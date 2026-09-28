// Native HTML template helpers. Content from API responses is always assigned as text.
export const $ = (root, selector) => root.querySelector(selector);
export const $$ = (root, selector) => [...root.querySelectorAll(selector)];
export const field = (root, name) => $(root, `[data-field="${name}"]`);
export function text(root, name, value) { field(root, name).textContent = value; }
export function clone(name) {
  return document.getElementById(`${name}-template`).content.firstElementChild.cloneNode(true);
}
export function icon(name, size = 17) {
  const svg = clone(`icon-${name}`);
  svg.setAttribute('width', size); svg.setAttribute('height', size);
  svg.setAttribute('class', `lucide lucide-${name}`);
  return svg;
}
export const peso = value => new Intl.NumberFormat('en-PH', {
  style: 'currency', currency: 'PHP', maximumFractionDigits: 0,
}).format(value);

// Web Animations and IntersectionObserver replace the former motion dependency.
const revealObservers = new Map();
export function disposeAnimations(root) {
  for (const [node, observer] of revealObservers) {
    if (root.contains(node)) {observer.disconnect(); revealObservers.delete(node);}
  }
}
function frame(values = {}) {
  const result = {};
  const transform = [];
  for (const [key, value] of Object.entries(values || {})) {
    if (key === 'x' || key === 'y') transform.push(`translate${key.toUpperCase()}(${typeof value === 'number' ? `${value}px` : value})`);
    else if (key === 'scale') transform.push(`scale(${value})`);
    else result[key] = typeof value === 'number' && ['width', 'height'].includes(key) ? `${value}px` : value;
  }
  if (transform.length) result.transform = transform.join(' ');
  return result;
}
export function animate(root) {
  const nodes = [...(root.matches?.('[data-motion]') ? [root] : []), ...$$(root, '[data-motion]')];
  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  for (const node of nodes) {
    const config = JSON.parse(node.dataset.motion);
    const start = frame(config.initial);
    const end = frame(config.animate);
    Object.assign(node.style, end);
    node.removeAttribute('data-motion');
    if (reduced) continue;
    const run = () => {
      if (!node.isConnected) return;
      node.animate([start, end], {
        duration: (config.transition?.duration || .4) * 1000,
        delay: (config.transition?.delay || 0) * 1000,
        easing: 'cubic-bezier(.22, 1, .36, 1)', fill: 'backwards',
      });
    };
    if (config.viewport) {
      Object.assign(node.style, start);
      const observer = new IntersectionObserver(entries => {
        if (entries.some(entry => entry.isIntersecting)) {
          Object.assign(node.style, end); run(); observer.disconnect(); revealObservers.delete(node);
        }
      }, {threshold: .18});
      revealObservers.set(node, observer); observer.observe(node);
    } else run();
  }
}
export async function dismiss(node, type = 'fade') {
  if (!node || node.dataset.closing) return;
  node.dataset.closing = 'true';
  if (!matchMedia('(prefers-reduced-motion: reduce)').matches) {
    const panel = $(node, '.cart-panel, .finder-modal') || node;
    const end = type === 'cart' ? {transform: 'translateX(100%)'} : {opacity: 0, transform: 'translateY(16px)'};
    await panel.animate([{}, end], {duration: 250, easing: 'ease-in', fill: 'forwards'}).finished;
  }
  node.remove();
}

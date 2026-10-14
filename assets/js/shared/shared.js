// Shared browser helpers: DOM, API requests, images, cart storage and dialogs.

// DOM
// Native HTML template helpers. Content from API responses is always assigned as text.
export const $ = (root, selector) => root.querySelector(selector);
export const $$ = (root, selector) => [...root.querySelectorAll(selector)];
export const field = (root, name) => $(root, `[data-field="${name}"]`);
export function text(root, name, value) {
  field(root, name).textContent = value;
}
export function clone(name) {
  return document
    .getElementById(`${name}-template`)
    .content.firstElementChild.cloneNode(true);
}
export function icon(name, size = 17) {
  const svg = clone(`icon-${name}`);
  svg.setAttribute("width", size);
  svg.setAttribute("height", size);
  svg.setAttribute("class", `lucide lucide-${name}`);
  return svg;
}
export const peso = (value) =>
  new Intl.NumberFormat("en-PH", {
    style: "currency",
    currency: "PHP",
    maximumFractionDigits: 0,
  }).format(value);

// Web Animations and IntersectionObserver replace the former motion dependency.
const revealObservers = new Map();
export function disposeAnimations(root) {
  for (const [node, observer] of revealObservers) {
    if (root.contains(node)) {
      observer.disconnect();
      revealObservers.delete(node);
    }
  }
}
function frame(values = {}) {
  const result = {};
  const transform = [];
  for (const [key, value] of Object.entries(values || {})) {
    if (key === "x" || key === "y")
      transform.push(
        `translate${key.toUpperCase()}(${typeof value === "number" ? `${value}px` : value})`,
      );
    else if (key === "scale") transform.push(`scale(${value})`);
    else
      result[key] =
        typeof value === "number" && ["width", "height"].includes(key)
          ? `${value}px`
          : value;
  }
  if (transform.length) result.transform = transform.join(" ");
  return result;
}
export function animate(root) {
  const nodes = [
    ...(root.matches?.("[data-motion]") ? [root] : []),
    ...$$(root, "[data-motion]"),
  ];
  const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
  for (const node of nodes) {
    const config = JSON.parse(node.dataset.motion);
    const start = frame(config.initial);
    const end = frame(config.animate);
    Object.assign(node.style, end);
    node.removeAttribute("data-motion");
    if (reduced) continue;
    const run = () => {
      if (!node.isConnected) return;
      node.animate([start, end], {
        duration: (config.transition?.duration || 0.4) * 1000,
        delay: (config.transition?.delay || 0) * 1000,
        easing: "cubic-bezier(.22, 1, .36, 1)",
        fill: "backwards",
      });
    };
    if (config.viewport) {
      Object.assign(node.style, start);
      const observer = new IntersectionObserver(
        (entries) => {
          if (entries.some((entry) => entry.isIntersecting)) {
            Object.assign(node.style, end);
            run();
            observer.disconnect();
            revealObservers.delete(node);
          }
        },
        { threshold: 0.18 },
      );
      revealObservers.set(node, observer);
      observer.observe(node);
    } else run();
  }
}
export async function dismiss(node, type = "fade") {
  if (!node || node.dataset.closing) return;
  node.dataset.closing = "true";
  if (!matchMedia("(prefers-reduced-motion: reduce)").matches) {
    const panel = $(node, ".cart-panel, .finder-modal") || node;
    const end =
      type === "cart"
        ? { transform: "translateX(100%)" }
        : { opacity: 0, transform: "translateY(16px)" };
    await panel.animate([{}, end], {
      duration: 250,
      easing: "ease-in",
      fill: "forwards",
    }).finished;
  }
  node.remove();
}

// API
// Same-origin API client. Authentication failures never fall back to demo access.
let csrf = "";
export async function api(path, options = {}) {
  const headers = { ...options.headers };
  if (options.body !== undefined) headers["Content-Type"] = "application/json";
  if (options.method && !["GET", "HEAD"].includes(options.method))
    headers["X-CSRF-Token"] = csrf;
  let response;
  try {
    response = await fetch(`/api${path}`, {
      ...options,
      headers,
      credentials: "same-origin",
      body:
        options.body === undefined ? undefined : JSON.stringify(options.body),
    });
  } catch {
    throw new Error(
      "Unable to reach AUDIA. Check your connection and try again.",
    );
  }
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    if (response.status === 401 && !path.startsWith("/auth/")) {
      window.dispatchEvent(new Event("audia:unauthorized"));
    }
    const error = new Error(
      data.error || "We could not complete that request. Please try again.",
    );
    error.status = response.status;
    throw error;
  }
  if (data.csrf_token) csrf = data.csrf_token;
  return data;
}

// MEDIA
// Product media may use local /static/images/ paths or HTTPS URLs.
export function imageSource(value) {
  return value;
}

document.addEventListener(
  "error",
  (event) => {
    const image = event.target;
    if (image instanceof HTMLImageElement && !image.dataset.fallback) {
      image.dataset.fallback = "true";
      image.alt =
        "Image unavailable; guitar studio photograph shown for illustration.";
      image.src = "/static/images/guitar_front.jpg";
    }
  },
  true,
);

// CART STORAGE
const key = "audia-cart";
export function readCart() {
  try {
    const value = JSON.parse(sessionStorage.getItem(key) || "[]");
    return Array.isArray(value)
      ? value
          .filter(
            (item) =>
              Number.isInteger(item.id) &&
              Number.isInteger(item.qty) &&
              item.qty > 0 &&
              item.qty <= 99,
          )
          .slice(0, 50)
      : [];
  } catch {
    return [];
  }
}
export function writeCart(items) {
  sessionStorage.setItem(
    key,
    JSON.stringify(items.map(({ id, qty }) => ({ id, qty }))),
  );
}

// UI
export function notice(message) {
  let node = document.getElementById("notice");
  if (!node) {
    node = document.createElement("div");
    node.id = "notice";
    node.className = "notice";
    node.setAttribute("role", "status");
    document.body.append(node);
  }
  node.textContent = message;
  node.hidden = false;
  clearTimeout(notice.timer);
  notice.timer = setTimeout(() => {
    node.hidden = true;
  }, 6500);
}

export function dialog(title, template) {
  const node = clone("dialog");
  const titleId = `dialog-title-${crypto.randomUUID()}`;
  field(node, "dialog-title").id = titleId;
  node.setAttribute("aria-labelledby", titleId);
  field(node, "dialog-title").textContent = title;
  if (template) field(node, "dialog-body").append(clone(template));
  document.body.append(node);
  node.addEventListener("click", (event) => {
    if (
      event.target === node ||
      event.target.closest('[data-action="dialog-close"]')
    )
      node.close();
  });
  node.addEventListener("close", () => node.remove(), { once: true });
  const close = node.close.bind(node);
  node.close = () => {
    close();
    node.remove();
  };
  node.showModal();
  return node;
}

export function formError(form, message) {
  const error = field(form, "form-error");
  error.textContent = message;
  error.hidden = !message;
}

export function busy(form, pending, label = "Save changes") {
  const button = form.querySelector('button[type="submit"]');
  button.disabled = pending;
  button.textContent = pending ? "Please wait…" : label;
}

export function empty(node, message) {
  const text = document.createElement("p");
  text.className = "empty-state";
  text.textContent = message;
  node.replaceChildren(text);
}

export function orderDetails(order) {
  const panel = dialog(`Order ${order.id}`, "order-detail");
  for (const key of [
    "status",
    "customer",
    "address",
    "phone",
    "payment",
    "date",
  ]) {
    field(panel, key).textContent = order[key];
  }
  field(panel, "total").textContent = new Intl.NumberFormat("en-PH", {
    style: "currency",
    currency: "PHP",
  }).format(order.amount);
  for (const item of order.items) {
    const row = document.createElement("li");
    row.textContent = `${item.name} × ${item.quantity}`;
    field(panel, "items").append(row);
  }
  return panel;
}

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
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
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
// Presentation frames stay in the animation API, not inline style attributes.
const presentationFrames = new WeakMap();
function presentFrame(node, values, pending = false) {
  presentationFrames.get(node)?.cancel();
  node.dataset.motionState = pending ? "pending" : "ready";
  if (pending) {
    presentationFrames.set(node, node.animate([values, values], { duration: 1, fill: "forwards" }));
  } else {
    // All existing final poses are full opacity and neutral translation/scale.
    // Keep settled presentation in animations.css, without a persistent effect layer.
    if ("opacity" in values) node.dataset.motionOpacity = String(values.opacity);
    if ("transform" in values) node.dataset.motionTransform = "settled";
    if (values.height === "auto") node.dataset.motionHeight = "auto";
  }
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
    presentFrame(node, end);
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
      presentFrame(node, start, true);
      const observer = new IntersectionObserver(
        (entries) => {
          if (entries.some((entry) => entry.isIntersecting)) {
            presentFrame(node, end);
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
      cache: "no-store",
      body:
        options.body === undefined ? undefined : JSON.stringify(options.body),
    });
  } catch {
    throw new Error(
      "Unable to reach AUDIA. Check your connection and try again.",
    );
  }
  const data = await response.json().catch(() => ({}));
  if (response.status === 403 && data.error?.startsWith("Your session has changed.") && !options._retried) {
    await api("/auth/session");
    return api(path, { ...options, _retried: true });
  }
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
  window.dispatchEvent(new Event("audia:cart-changed"));
}

// Poll visible pages without overlapping requests; stop on navigation or disposal.
export function poll(task, interval = 15000) {
  let timer, stopped = false, running = false;
  async function tick() {
    clearTimeout(timer);
    if (stopped || running) return;
    if (!document.hidden) {
      running = true;
      try { await task(); } catch { /* The view owns its error feedback. */ }
      finally { running = false; }
    }
    if (!stopped) timer = setTimeout(tick, interval);
  }
  const refresh = () => { if (!document.hidden) void tick(); };
  document.addEventListener("visibilitychange", refresh);
  window.addEventListener("focus", refresh);
  function stop() {
    stopped = true; clearTimeout(timer);
    document.removeEventListener("visibilitychange", refresh);
    window.removeEventListener("focus", refresh);
    window.removeEventListener("pagehide", stop);
  }
  window.addEventListener("pagehide", stop);
  timer = setTimeout(tick, interval);
  return stop;
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

export function orderDetails(order, { live = true } = {}) {
  const panel = dialog(`Order ${order.id}`, "order-detail");
  function render(order) {
    field(panel, "status").dataset.status = order.status;
    for (const key of [
      "status",
      "customer",
      "address",
      "phone",
      "payment",
      "date",
      "payment_status",
    ]) {
      field(panel, key).textContent = order[key];
    }
    field(panel, "total").textContent = new Intl.NumberFormat("en-PH", {
      style: "currency",
      currency: "PHP",
    }).format(order.amount);
    field(panel, "items").replaceChildren();
    for (const item of order.items) {
      const row = document.createElement("li");
      row.textContent = `${item.name} × ${item.quantity} · ${peso(item.price)} each · ${peso(item.price * item.quantity)}`;
      field(panel, "items").append(row);
    }
    text(panel, "subtotal", peso(order.subtotal ?? order.amount));
    text(panel, "shipping", peso(order.shipping_fee ?? 0));
    renderTracking(field(panel, "tracking"), order);
    field(panel, "history").replaceChildren(...(order.history || []).map((event) => {
      const row = document.createElement("li");
      row.textContent = `${new Date(event.at).toLocaleString()} · ${event.kind === "payment" ? event.note : event.status}`;
      return row;
    }));
    text(panel, "tracking-update", !order.history?.length ? "Earlier status timestamps were not recorded for this order." : live ? "Updates automatically while this window is open." : "Status shown when opened. Reopen to review later changes.");
  }
  render(order);
  if (live) {
    const stop = poll(async () => {
      if (!panel.isConnected) return stop();
      try {
        const data = await api(`/orders/${encodeURIComponent(order.id)}`);
        if (panel.isConnected) render(data.order);
      } catch (error) { if (panel.isConnected) text(panel, "tracking-update", `Unable to refresh: ${error.message}`); }
    });
    panel.addEventListener("close", stop, { once: true });
  }
  return panel;
}

export function renderTracking(node, order) {
  const stages = ["Pending", "Confirmed", "Processing", "Shipped", "Out for Delivery", "Delivered"];
  const current = stages.indexOf(order.status);
  node.replaceChildren(...stages.map((status, index) => {
    const item = document.createElement("li");
    item.textContent = status === "Pending" ? "Pending confirmation" : status;
    item.dataset.state = current === index ? "current" : current > index ? "done" : "waiting";
    if (current === index) item.setAttribute("aria-current", "step");
    const recorded = (order.history || []).find((event) => event.kind === "status" && event.status === status);
    if (recorded) {
      const time = document.createElement("small");
      time.textContent = new Date(recorded.at).toLocaleString();
      item.append(time);
    }
    return item;
  }));
  const placed = document.createElement("li");
  placed.textContent = `Order placed · ${new Date(order.created_at).toLocaleString()}`;
  placed.dataset.state = "done";
  node.prepend(placed);
  if (current < 0) {
    const terminal = document.createElement("li");
    terminal.textContent = `Order ${order.status.toLowerCase()}`;
    terminal.dataset.state = "current";
    node.append(terminal);
  }
}

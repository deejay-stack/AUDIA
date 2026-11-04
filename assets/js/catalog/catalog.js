import { mountSearchFilter } from "../search_filter/search_filter.js";
import { guitarAudio, previewURL } from "../shared/guitar_audio.js";
import { simulatePayment } from "../shared/payments.js";
import {
  imageSource,
  api,
  dialog,
  notice,
  formError,
  busy,
  orderDetails,
  readCart,
  writeCart,
  $,
  $$,
  field,
  text,
  clone,
  icon,
  peso,
  animate,
  dismiss,
} from "../shared/shared.js";

export function mountStore(page, app) {
  // State is scoped to this visit, matching the original screen's lifetime.
  let products = [];
  let saved = new Set();
  const storedCart = readCart();
  let cart = [];
  let cartPanel;
  let mobile;
  const cards = new Map();
  let soundButton = null;
  const audioEvents = new AbortController();
  const stopAudio = () => { void guitarAudio.dispose(); };
  window.addEventListener("pagehide", stopAudio, { signal: audioEvents.signal });
  document.addEventListener("visibilitychange", () => { if (document.hidden) stopAudio(); }, { signal: audioEvents.signal });
  let alive = true;

  const searchFilter = mountSearchFilter(page, app, { renderProducts, closeMobile, addToCart });

  const account = $(page, '[data-action="account"]');
  account.setAttribute("aria-label", app.user ? "Open account" : "Sign in");

  function renderProducts() {
    const list = searchFilter.filterProducts(products);
    const grid = field(page, "products");
    const activeIds = new Set(list.map((p) => p.id));
    for (const [id, card] of cards)
      if (!activeIds.has(id)) {
        if (soundButton && card.contains(soundButton)) guitarAudio.stop();
        card.remove();
        cards.delete(id);
      }
    const nextCards = list.map((product, index) => {
      let card = cards.get(product.id);
      const fresh = !card;
      if (fresh) {
        card = clone("product-card");
        cards.set(product.id, card);
        const motion = JSON.parse(card.dataset.motion);
        motion.transition.delay = index * 0.05;
        card.dataset.motion = JSON.stringify(motion);
      }
      card.dataset.productId = product.id;
      const sound = $(card, '[data-action="sound"]');
      sound.dataset.audioCategory = product.category;
      sound.disabled = !previewURL(product.category);
      sound.title = sound.disabled ? "No licensed recording is available for this category." :
        `Representative ${product.category.toLowerCase()} recording; not a recording of ${product.name}.`;
      if (sound !== soundButton) {
        $(sound, "span").textContent = sound.disabled ? "No recording" : "Test Sound";
        sound.setAttribute("aria-label", sound.disabled ? "No recording available" : `Test Sound · representative ${product.category.toLowerCase()} recording`);
      }
      const image = field(card, "image");
      image.src = imageSource(product.image);
      image.alt = product.name;
      text(card, "badge", product.badge);
      text(card, "category", `${product.brand} · ${product.category}`);
      text(card, "rating", `${product.rating} (${product.reviews})`);
      text(card, "name", product.name);
      text(card, "description", product.description);
      text(card, "price", peso(product.price));
      text(
        card,
        "stock",
        product.stock ? `${product.stock} available` : "Out of stock",
      );
      const add = $(card, '[data-action="add"]');
      add.disabled = product.stock < 1;
      const heart = $(card, '[data-action="like"] svg');
      heart.setAttribute(
        "fill",
        saved.has(product.id) ? "currentColor" : "none",
      );
      heart.classList.toggle("is-saved", saved.has(product.id));
      $(card, '[data-action="add"]').setAttribute(
        "aria-label",
        `Add ${product.name} to cart`,
      );
      return { card, fresh };
    });
    grid.replaceChildren(...nextCards.map((item) => item.card));
    nextCards
      .filter((item) => item.fresh)
      .forEach((item) => animate(item.card));
    field(page, "no-products").hidden = list.length > 0;
    $$(page, ".filter-chip").forEach((button) =>
      button.classList.toggle(
        "filter-chip-active",
        button.dataset.category === searchFilter.category,
      ),
    );
  }

  function renderCart() {
    writeCart(cart);
    const count = cart.reduce((sum, item) => sum + item.qty, 0);
    const button = $(page, '[data-action="cart"]');
    button.setAttribute("aria-label", `Open cart, ${count} items`);
    let badge = $(button, "span");
    if (count && !badge) {
      badge = clone("cart-badge");
      badge.setAttribute("aria-live", "polite");
      button.append(badge);
    }
    if (badge) {
      badge.textContent = count;
      badge.hidden = count === 0;
    }
    if (!cartPanel) return;
    text(cartPanel, "cart-count", `${count} items`);
    const body = field(cartPanel, "cart-body");
    if (!cart.length) body.replaceChildren(clone("cart-empty"));
    else {
      const rows = clone("cart-items");
      rows.replaceChildren(
        ...cart.map((item) => {
          const row = clone("cart-item");
          row.dataset.productId = item.id;
          field(row, "image").src = imageSource(item.image);
          field(row, "image").alt = item.name;
          text(row, "brand", item.brand);
          text(row, "name", item.name);
          text(row, "price", peso(item.price));
          text(row, "quantity", item.qty);
          return row;
        }),
      );
      body.replaceChildren(rows);
    }
    field(cartPanel, "cart-footer").hidden = cart.length === 0;
    text(
      cartPanel,
      "subtotal",
      peso(cart.reduce((sum, item) => sum + item.price * item.qty, 0)),
    );
  }
  function openCart() {
    if (!cartPanel) {
      cartPanel = clone("cart");
      cartPanel.setAttribute("role", "dialog");
      cartPanel.setAttribute("aria-modal", "true");
      cartPanel.setAttribute("aria-label", "Your shopping cart");
      page.append(cartPanel);
      animate(cartPanel);
      cartPanel.addEventListener("keydown", (event) => {
        if (event.key === "Escape") { event.preventDefault(); closeCart(); return; }
        if (event.key !== "Tab") return;
        const focusable = [...cartPanel.querySelectorAll('button:not(:disabled),a[href],input:not(:disabled)')].filter((node) => node.getClientRects().length);
        const first = focusable[0], last = focusable.at(-1);
        if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
        else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
      });
    }
    renderCart();
    cartPanel.querySelector('[data-action="close-cart"]').focus();
  }
  function addToCart(product) {
    if (!product || product.stock < 1)
      return notice("This item is currently out of stock.");
    if (
      (cart.find((item) => item.id === product.id)?.qty || 0) >= Math.min(product.stock, 99)
    )
      return notice("You have reached the available stock for this item.");
    cart = cart.some((item) => item.id === product.id)
      ? cart.map((item) =>
          item.id === product.id ? { ...item, qty: item.qty + 1 } : item,
        )
      : [...cart, { ...product, qty: 1 }];
    openCart();
    notice(`${product.name} added to your cart.`);
  }
  function changeQuantity(id, delta) {
    const item = cart.find((item) => item.id === id);
    if (delta > 0 && item && item.qty >= Math.min(item.stock, 99))
      return notice("You have reached the available stock for this item.");
    cart = cart
      .map((item) =>
        item.id === id ? { ...item, qty: Math.max(0, item.qty + delta) } : item,
      )
      .filter((item) => item.qty > 0);
    renderCart();
  }
  function closeCart() {
    const closing = cartPanel;
    cartPanel = null;
    dismiss(closing, "cart");
    $(page, '[data-action="cart"]').focus();
  }

  function openCheckout() {
    if (!app.user) {
      notice("Sign in to place your order. Your cart is saved.");
      app.navigate("auth");
      return;
    }
    if (!cart.length) return;
    const panel = dialog("Your next chapter starts here.", "checkout");
    const form = panel.querySelector("form");
    let submitting = false, pendingOrder = null;
    form.elements.address.value = app.user.address || "";
    form.elements.phone.value = app.user.phone || "";
    const subtotal = cart.reduce((sum, item) => sum + item.price * item.qty, 0);
    text(form, "checkout-subtotal", peso(subtotal));
    text(form, "checkout-shipping", peso(0));
    field(form, "checkout-items").replaceChildren(...cart.map((item) => {
      const row = document.createElement("li");
      row.textContent = `${item.name} × ${item.qty} · ${peso(item.price * item.qty)}`;
      return row;
    }));
    form.addEventListener("change", () => {
      const demo = form.elements.payment_method.value !== "cod";
      text(form, "payment-preview", demo ? "Demonstration mode. Review and confirm on the next screen. No money is transferred." : "Pay with cash when your order arrives. No online payment is required.");
      form.querySelector('[type="submit"]').textContent = demo ? "Proceed to payment" : "Place order";
      form.querySelector('[type="submit"]').disabled = submitting;
    });
    field(form, "checkout-total").textContent = peso(
      cart.reduce((sum, item) => sum + item.price * item.qty, 0),
    );
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      if (form.querySelector("[type=submit]").disabled) return;
      if (submitting) return;
      if (!form.reportValidity()) return;
      submitting = true;
      busy(form, true);
      formError(form, "");
      const body = {
        address: form.elements.address.value.trim(), phone: form.elements.phone.value.trim(),
        payment_method: form.elements.payment_method.value,
        expected_total: subtotal.toFixed(2),
        items: cart.map((item) => ({ product_id: item.id, quantity: item.qty })),
      };
      // Keep the same key after a lost response or reopening the same checkout.
      const signature = JSON.stringify(body);
      let attempt;
      try { attempt = JSON.parse(sessionStorage.getItem("audia-checkout")); } catch { /* New attempt below. */ }
      if (attempt?.signature !== signature) attempt = { signature, key: crypto.randomUUID() };
      sessionStorage.setItem("audia-checkout", JSON.stringify(attempt));
      try {
        const data = pendingOrder ? { order: pendingOrder } : await api("/orders", {
          method: "POST",
          body: { ...body, request_key: attempt.key },
        });
        if (!pendingOrder) {
          pendingOrder = data.order;
          const inventory = await api("/products").catch(() => null);
          if (inventory) products = inventory.products;
          cart = [];
          sessionStorage.removeItem("audia-checkout");
          renderCart();
          renderProducts();
          closeCart();
          // The saved order is immutable; retry its payment instead of placing it twice.
          form.querySelectorAll('input,textarea').forEach((control) => { control.disabled = true; });
        }
        if (pendingOrder.is_demo) {
          pendingOrder = await simulatePayment(pendingOrder);
          if (pendingOrder.can_retry_payment) {
            text(form, "payment-preview", `Order ${pendingOrder.id} saved and unpaid. Continue payment here or from My Orders. Cancel the unpaid order there to release reserved stock.`);
            return;
          }
        }
        panel.close();
        orderDetails(pendingOrder);
        notice(pendingOrder.is_demo ? "Demo payment confirmed. Follow your order in My Orders." : "Order placed. Pay with cash on delivery.");
      } catch (error) {
        formError(form, error.message);
      } finally {
        submitting = false;
        busy(form, false, pendingOrder?.is_demo ? "Retry demo payment" : form.elements.payment_method.value === "cod" ? "Place order" : "Proceed to payment");
      }
    });
  }

  async function trackOrder() {
    if (!app.user) {
      notice("Sign in to track orders securely.");
      app.navigate("auth");
      return;
    }
    const id = field(page, "order").value.trim();
    if (!id) return notice("Enter your order number.");
    try {
      const data = await api(`/orders/${encodeURIComponent(id)}`);
      if (alive) orderDetails(data.order);
    } catch (error) {
      notice(error.message);
    }
  }

  function closeMobile() {
    if (mobile) {
      mobile.remove();
      mobile = null;
    }
    $(page, '[data-action="menu"]').replaceChildren(icon("menu", 19));
  }
  function toggleMobile() {
    if (mobile) return closeMobile();
    mobile = clone("mobile-nav");
    $(page, "header").append(mobile);
    animate(mobile);
    $(page, '[data-action="menu"]').replaceChildren(icon("x", 19));
  }
  function playSound(button) {
    if (soundButton === button && guitarAudio.current) { guitarAudio.stop(); return; }
    const url = previewURL(button.dataset.audioCategory);
    if (!url) return;
    void guitarAudio.play({ url, onState(state, message) {
      const playing = state === "playing", loading = state === "loading";
      if (loading) soundButton = button;
      const label = $(button, "span");
      const glyph = icon(playing ? "pause" : "play", 15);
      glyph.setAttribute("fill", "currentColor");
      button.replaceChildren(glyph);
      if (label) {
        label.textContent = loading ? "Loading…" : playing ? "Stop Sound" : "Test Sound";
        button.append(label);
      }
      button.dataset.audioState = state;
      button.setAttribute("aria-busy", String(loading));
      button.setAttribute("aria-pressed", String(playing || loading));
      button.setAttribute("aria-label", `${loading ? "Cancel loading" : playing ? "Stop Sound" : "Test Sound"} · representative ${button.dataset.audioCategory.toLowerCase()} recording`);
      field(page,"audio-status").textContent = state === "error" ? message : playing ?
        `Playing a representative ${button.dataset.audioCategory.toLowerCase()} recording, not this product model.` : loading ? "Loading guitar recording…" : "Sound stopped.";
      if (!playing && !loading) soundButton = null;
    }});
  }

  page.addEventListener("click", async (event) => {
    const button = event.target.closest("[data-action]");
    if (!button) return;
    if (!app.user) {
      app.navigate("auth");
      return;
    }
    if (button.tagName === "A") event.preventDefault();
    if (searchFilter.handleAction(button)) return;
    const id = Number(button.closest("[data-product-id]")?.dataset.productId);
    switch (button.dataset.action) {
      case "product-detail": {
        const product = products.find((p) => p.id === id);
        if (!product) break;
        const panel = dialog(product.name, "product-detail");
        field(panel, "detail-image").src = imageSource(product.image);
        field(panel, "detail-image").alt = product.name;
        text(panel, "detail-category", `${product.brand} · ${product.category}`);
        text(panel, "detail-price", peso(product.price));
        text(panel, "detail-description", product.description);
        text(panel, "detail-stock", product.stock ? `${product.stock} in stock · Free standard delivery` : "Out of stock");
        field(panel, "detail-specs").replaceChildren(...product.specs.map((spec) => {
          const li = document.createElement("li"); li.textContent = spec; return li;
        }));
        const add = field(panel, "detail-add");
        add.disabled = product.stock < 1;
        add.addEventListener("click", () => { panel.close(); addToCart(product); });
        break;
      }
      case "home":
        window.scrollTo({ top: 0, behavior: "smooth" });
        break;
      case "account": {
        const fromMobile = mobile?.contains(button);
        closeMobile();
        app.navigate(
          app.user?.role === "admin"
            ? "dashboard"
            : app.user
              ? "account"
              : "auth",
        );
        break;
      }
      case "admin-login":
        app.navigate("auth", "admin");
        break;
      case "menu":
        toggleMobile();
        break;
      case "mobile-link":
        closeMobile();
        break;
      case "add":
        addToCart(products.find((p) => p.id === id));
        break;
      case "cart":
        openCart();
        break;
      case "checkout":
        openCheckout();
        break;
      case "bundle": {
        const product = products.find((p) => p.category === "Bundles");
        if (product) {
          const panel = dialog(product.name, "bundle-detail");
          field(panel, "description").textContent = product.description;
          field(panel, "price").textContent = peso(product.price);
          field(panel, "image").src = imageSource(product.image);
          field(panel, "image").alt = product.name;
          field(panel, "bundle-add").addEventListener("click", () => {
            panel.close();
            addToCart(product);
          });
        } else
          notice(
            "This bundle is not currently available. Please contact the store.",
          );
        break;
      }
      case "support-info": {
        const panel = dialog(button.textContent.trim(), "support-info");
        const topic = button.dataset.topic;
        const descriptions = {
          delivery:
            "Delivery details are confirmed with your order. For a return, contact the store with your order number before sending an item back.",
          warranty:
            "Warranty coverage depends on the instrument and manufacturer. Contact the store with your order number and a description of the issue.",
          setup:
            "Every instrument benefits from a setup matched to your playing style. Ask the store about action, string gauge, and setup availability.",
        };
        field(panel, "support-copy").textContent =
          descriptions[topic] ||
          "Ask AUDI for guitar guidance or contact the store about an existing order.";
        api("/store")
          .then((data) => {
            if (panel.isConnected) {
              const link = field(panel, "support-email");
              link.textContent = data.store.support_email;
              link.href = `mailto:${data.store.support_email}`;
            }
          })
          .catch((error) => notice(error.message));
        break;
      }
      case "close-cart":
        closeCart();
        break;
      case "increase":
        changeQuantity(id, 1);
        break;
      case "decrease":
        changeQuantity(id, -1);
        break;
      case "like": {
        if (!app.user) {
          notice("Sign in to save instruments.");
          app.navigate("auth");
          break;
        }
        button.disabled = true;
        try {
          const data = await api(`/account/saved/${id}`, {
            method: saved.has(id) ? "DELETE" : "PUT",
          });
          if (data.saved) saved.add(id);
          else saved.delete(id);
          if (alive) renderProducts();
        } catch (error) {
          notice(error.message);
        } finally {
          button.disabled = false;
        }
        break;
      }
      case "sound":
        playSound(button);
        break;
      case "track":
        trackOrder();
        break;
    }
  });
  field(page, "no-products").hidden = false;
  field(page, "no-products").textContent = "Loading instruments…";
  api("/products")
    .then((data) => {
      if (!alive) return;
      products = data.products;
      $$(page, "[data-category-count]").forEach((node) => {
        node.textContent = products.filter(
          (product) => product.category === node.dataset.categoryCount,
        ).length;
      });
      cart = storedCart
        .map((item) => {
          const product = products.find((p) => p.id === item.id);
          return product && product.stock > 0 ? { ...product, qty: Math.min(item.qty, product.stock, 99) } : null;
        })
        .filter(Boolean);
      field(page, "no-products").textContent = "No guitar matches that search.";
      renderProducts();
      renderCart();
      if (new URLSearchParams(location.search).get("cart") === "1") openCart();
      if (app.openFinder) {
        app.openFinder = false;
        searchFilter.openFinder();
      }
      if (searchFilter.hasSelection) $(page, "#shop").scrollIntoView();
    })
    .catch((error) => {
      if (alive) {
        field(page, "no-products").hidden = false;
        field(page, "no-products").textContent = error.message;
      }
    });
  if (app.user)
    api("/account/saved")
      .then((data) => {
        if (alive) {
          saved = new Set(data.products.map((p) => p.id));
          if (data.profile) searchFilter.restoreProfile(data.profile);
          renderProducts();
        }
      })
      .catch((error) => notice(error.message));
  return {
    destroy() {
      alive = false;
      stopAudio();
      audioEvents.abort();
      searchFilter.destroy();
    },
  };
}

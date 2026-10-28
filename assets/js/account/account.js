import {
  imageSource,
  field,
  clone,
  peso,
  api,
  busy,
  empty,
  formError,
  notice,
  orderDetails,
  poll,
} from "../shared/shared.js";

export function mountAccount(page, app) {
  let alive = true,
    orders = [],
    saved = [];
  if (field(page, "greeting")) field(page, "greeting").textContent =
    `Welcome back, ${app.user.name.split(" ")[0]}.`;
  const profile = page.querySelector('[data-form="profile"]');
  if (profile) for (const name of ["name", "email", "phone", "address"])
    profile.elements[name].value = app.user[name] || "";
  let loadingOrders = false, loadedOrders = false, snapshot = "";
  async function loadOrders() {
    if (loadingOrders) return;
    loadingOrders = true;
    try {
      const data = await api("/orders");
      if (!alive) return;
      textUpdate("Tracking up to date. Automatically refreshes every 15 seconds.");
      const next = JSON.stringify(data.orders);
      if (snapshot === next) return;
      snapshot = next;
      loadedOrders = true;
      orders = data.orders;
      if (!orders.length)
        return empty(
          field(page, "orders"),
          "Your first order starts with your next favorite instrument.",
        );
      field(page, "orders").replaceChildren(
        ...orders.map((order) => {
          const card = clone("order-card");
          card.dataset.orderId = order.id;
          for (const key of ["id", "date", "product", "status"])
            field(card, key).textContent = order[key];
          field(card, "amount").textContent = peso(order.amount);
          field(card, "status").dataset.status = order.status;
          field(card, "payment").textContent = `${order.payment} · ${order.payment_status}`;
          field(card, "tracking").textContent = order.status === "Pending" ? "Awaiting store confirmation" : `Tracking: ${order.status}`;
          return card;
        }),
      );
    } catch (error) {
      if (alive) {
        textUpdate(`Unable to refresh tracking: ${error.message}`);
        if (!loadedOrders) empty(field(page, "orders"), error.message);
      }
    } finally {
      loadingOrders = false;
    }
  }
  function textUpdate(message) { field(page, "orders-update").textContent = message; }
  async function loadSaved() {
    try {
      const data = await api("/account/saved");
      if (!alive) return;
      saved = data.products;
      field(page, "finder-profile").textContent = data.profile
        ? `Last Guitar Finder: ${data.profile.level} · ${data.profile.category} · ${peso(data.profile.budget)}`
        : "Find instruments suited to your experience and budget.";
      if (!saved.length)
        return empty(
          field(page, "saved"),
          "Tap the heart on an instrument to save it here.",
        );
      field(page, "saved").replaceChildren(
        ...saved.map((product) => {
          const item = clone("saved-item");
          item.dataset.productId = product.id;
          field(item, "image").src = imageSource(product.image);
          field(item, "image").alt = product.name;
          field(item, "name").textContent = product.name;
          field(item, "price").textContent = peso(product.price);
          return item;
        }),
      );
    } catch (error) {
      if (alive) empty(field(page, "saved"), error.message);
    }
  }
  page.addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.target;
    if (form.querySelector("[type=submit]").disabled) return;
    const values = Object.fromEntries(new FormData(form)),
      password = form.dataset.form === "password";
    if (password && values.password !== values.confirm)
      return formError(form, "The new passwords do not match.");
    busy(form, true);
    formError(form, "");
    try {
      const data = await api(password ? "/auth/password" : "/auth/profile", {
        method: password ? "POST" : "PATCH",
        body: values,
      });
      if (!alive) return;
      app.user = data.user;
      if (password) form.reset();
      notice(password ? "Password updated." : "Profile saved.");
    } catch (error) {
      if (alive) formError(form, error.message);
    } finally {
      if (alive)
        busy(form, false, password ? "Update password" : "Save profile");
    }
  });
  page.addEventListener("click", async (event) => {
    const button = event.target.closest("[data-action]");
    if (!button) return;
    const action = button.dataset.action;
    if (action === "store") app.navigate(app.user.role === "admin" ? "dashboard" : "storefront");
    if (action === "logout") app.logout();
    if (action === "refresh-orders") loadOrders();
    if (action === "view-order")
      orderDetails(
        orders.find(
          (order) =>
            order.id === button.closest("[data-order-id]").dataset.orderId,
        ),
      );
    if (action === "saved-shop") {
      app.searchProduct = saved.find(
        (p) =>
          p.id ===
          Number(button.closest("[data-product-id]").dataset.productId),
      ).name;
      app.navigate("storefront");
    }
    if (action === "find-guitar") {
      app.openFinder = true;
      app.navigate("storefront");
    }
    if (action === "unsave") {
      button.disabled = true;
      try {
        await api(
          `/account/saved/${button.closest("[data-product-id]").dataset.productId}`,
          { method: "DELETE" },
        );
        if (alive) loadSaved();
      } catch (error) {
        notice(error.message);
        button.disabled = false;
      }
    }
  });
  const customer = app.user.role === "customer";
  if (customer) loadOrders();
  const stopPolling = customer ? poll(loadOrders) : () => {};
  if (profile && customer) loadSaved();
  return {
    destroy() {
      alive = false;
      stopPolling();
    },
  };
}

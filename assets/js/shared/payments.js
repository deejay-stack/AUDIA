// Persisted internal simulation. Every displayed amount/reference comes from the server.
import { api, dialog, field, text, peso, busy, formError } from "./shared.js";

export async function simulatePayment(order) {
  const panel = dialog(`Demo payment · ${order.payment}`, "demo-payment");
  const form = panel.querySelector("form");
  const submit = form.querySelector('[type="submit"]');
  const cancel = field(form, "cancel-payment");
  const closeButton = panel.querySelector('[data-action="dialog-close"]');
  const storageKey = `audia-payment-${order.id}`;
  let attempt, submitting = false, finished = false, resolveResult;
  const result = new Promise((resolve) => { resolveResult = resolve; });
  text(form, "payment-method", `${order.payment} · demonstration`);
  text(form, "payment-amount", peso(order.amount));
  text(form, "payment-order", order.id);
  text(form, "payment-reference", "Preparing…");
  text(form, "payment-expiry", "10 minutes from creation");

  function lock(pending) {
    submitting = pending;
    busy(form, pending, "Confirm demo payment");
    cancel.disabled = pending;
    closeButton.disabled = pending;
    form.elements.outcome.disabled = pending;
  }
  function conclude(data) {
    order = data.order;
    attempt = data.attempt;
    finished = true;
    sessionStorage.removeItem(storageKey);
    const messages = {
      Succeeded: "Demo payment confirmed. No money was transferred.",
      Failed: "Demo payment failed. Your order is unpaid; you can retry safely.",
      Cancelled: "Demo payment cancelled. Your order is unpaid; return to checkout or retry in My Orders.",
      "Timed out": "The demo transaction expired. Your order is unpaid; start a new attempt.",
    };
    text(form, "payment-result", messages[attempt.status]);
    field(form, "payment-result").dataset.status = attempt.status;
    submit.hidden = true;
    cancel.textContent = attempt.status === "Succeeded" ? "View order" : "Back to checkout / order";
    field(form, "test-controls").hidden = true;
  }
  async function confirm(outcome) {
    if (!attempt || submitting || finished) return;
    lock(true);
    formError(form, "");
    try {
      conclude(await api(`/orders/${order.id}/payment-attempts/${attempt.id}/confirm`, {
        method: "POST", body: { outcome },
      }));
    } catch (error) {
      formError(form, error.message);
    } finally { lock(false); }
  }
  function exit() {
    panel.close();
    resolveResult(order);
  }
  cancel.addEventListener("click", () => {
    if (finished || !attempt) exit();
    else void confirm("cancelled");
  });
  // Escape, backdrop and close all cancel persistently before leaving the dialog.
  panel.addEventListener("cancel", (event) => {
    event.preventDefault();
    if (!submitting) { if (finished || !attempt) exit(); else void confirm("cancelled"); }
  });
  panel.addEventListener("click", (event) => {
    if (event.target === panel || event.target.closest('[data-action="dialog-close"]')) {
      event.stopImmediatePropagation();
      if (!submitting) { if (finished || !attempt) exit(); else void confirm("cancelled"); }
    }
  }, { capture: true });
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    void confirm(form.elements.outcome.value);
  });
  lock(true);
  try {
    let key = sessionStorage.getItem(storageKey);
    if (!key) { key = crypto.randomUUID(); sessionStorage.setItem(storageKey, key); }
    const data = await api(`/orders/${order.id}/payment-attempts`, { method: "POST", body: { request_key: key } });
    attempt = data.attempt;
    text(form, "payment-reference", attempt.id);
    text(form, "payment-expiry", new Date(attempt.expires_at).toLocaleString());
    if (attempt.status !== "Pending") conclude(data);
    else {
      field(form, "test-controls").hidden = !data.test_controls;
      text(form, "payment-result", "Confirm to complete this simulated transaction.");
    }
  } catch (error) {
    formError(form, error.message);
  } finally {
    lock(false);
    submit.disabled = !attempt || finished;
  }
  return result;
}

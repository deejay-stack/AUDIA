// Persisted internal simulation. Every displayed amount/reference comes from the server.
import { api, dialog, field, text, peso, busy, formError } from "./shared.js";

export async function simulatePayment(order) {
  const panel = dialog(`Payment · ${order.payment}`, "demo-payment");
  const form = panel.querySelector("form");
  const submit = form.querySelector('[type="submit"]');
  const cancel = field(form, "cancel-payment");
  const closeButton = panel.querySelector('[data-action="dialog-close"]');
  const storageKey = `audia-payment-${order.id}`;
  let attempt, submitting = false, finished = false, authorizing = false, resolveResult;
  const result = new Promise((resolve) => { resolveResult = resolve; });
  const requiredFields=['payment-review','payment-success','gcash-authorization','success-amount','success-number'];
  if(requiredFields.some(name=>!field(form,name))){
    formError(form,'Checkout has been updated. Refresh this page before continuing payment.');
    submit.disabled=true;
    cancel.addEventListener('click',()=>{panel.close();resolveResult(order);});
    panel.addEventListener('close',()=>resolveResult(order),{once:true});
    return result;
  }
  text(form, "payment-method", order.payment);
  text(form, "payment-amount", peso(order.amount));
  text(form, "payment-order", order.id);
  text(form, "payment-reference", "Preparing…");
  text(form, "payment-expiry", "10 minutes from creation");

  function lock(pending) {
    submitting = pending;
    busy(form, pending, authorizing ? `Pay ${peso(order.amount)}` : 'Confirm payment');
    submit.disabled = pending || finished || !attempt;
    cancel.disabled = pending;
    closeButton.disabled = pending;
    form.elements.outcome.disabled = pending;
    form.elements.gcash_number.disabled = pending || finished;
  }
  function conclude(data) {
    order = data.order;
    attempt = data.attempt;
    finished = true;
    sessionStorage.removeItem(storageKey);
    const messages = {
      Succeeded: "Payment confirmed. No money was transferred.",
      Failed: "Payment failed. Your order is unpaid; you can retry safely.",
      Cancelled: "Payment cancelled. Your order is unpaid; return to checkout or retry in My Orders.",
      "Timed out": "The transaction expired. Your order is unpaid; start a new attempt.",
      "Awaiting review": "Authorization submitted. Payment is pending store verification; no collection or paid receipt exists yet.",
      Verified: "Payment confirmed after store verification.",
      Rejected: "Payment was rejected by the store. You may retry from My Orders.",
    };
    text(form, "payment-result", order.receipt_url && !['Succeeded','Verified'].includes(attempt.status) ? `This attempt is ${attempt.status.toLowerCase()}. The saved order's latest payment status is ${order.payment_status}; its store receipt is available below.` : messages[attempt.status]);
    field(form, "payment-result").dataset.status = attempt.status;
    submit.hidden = true;
    cancel.textContent = attempt.status === "Succeeded" ? "View order" : "Back to checkout / order";
    field(form, "test-controls").hidden = true;
    field(form,'gcash-authorization').hidden=true;
    form.elements.gcash_number.required=false;
    if (order.receipt_url) {
      field(form, "payment-review").hidden = true;
      field(form, "payment-success").hidden = false;
      text(form,'success-amount',peso(order.amount));text(form,'success-method',order.payment);text(form,'success-order',order.id);
      text(form,'success-number',attempt.payer_number_masked ? `GCash number: ${attempt.payer_number_masked}` : '');
      field(form, "success-receipt").href = order.receipt_url;
      field(form, "success-qr").src = order.qr_url;
      text(form, "success-reference", order.payment_reference);
      text(form, "success-date", new Date(order.payment_collected_at).toLocaleString('en-PH',{timeZone:'Asia/Manila'}));
      field(form,'payment-success').scrollIntoView({block:'start',behavior:'smooth'});
    }
  }
  async function confirm(outcome) {
    if (!attempt || submitting || finished) return;
    lock(true);
    formError(form, "");
    try {
      conclude(await api(`/orders/${order.id}/payment-attempts/${attempt.id}/confirm`, {
        method: "POST", body: { outcome, ...(authorizing && outcome==='success' ? {gcash_number:form.elements.gcash_number.value.trim()} : {}) },
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
    if(order.payment==='GCash' && form.elements.outcome.value==='success' && !authorizing && !finished){
      authorizing=true;
      field(form,'payment-review').hidden=true;
      field(form,'gcash-authorization').hidden=false;
      field(form,'test-controls').hidden=true;
      text(form,'gcash-amount',peso(order.amount));
      text(form,'payment-result','Enter your GCash number, then confirm the amount to complete payment.');
      form.elements.gcash_number.required=true;
      submit.textContent=`Pay ${peso(order.amount)}`;
      form.elements.gcash_number.focus();
      return;
    }
    if(authorizing && !form.reportValidity())return;
    void confirm(form.elements.outcome.value);
  });
  lock(true);
  try {
    let key = sessionStorage.getItem(storageKey);
    if (!key) { key = crypto.randomUUID(); sessionStorage.setItem(storageKey, key); }
    const data = await api(`/orders/${order.id}/payment-attempts`, { method: "POST", body: { request_key: key } });
    attempt = data.attempt;
    const profile = data.profile;
    text(form, "payment-store", profile.store_name + ' checkout');
    text(form, "payment-recipient", profile.recipient);
    text(form, "payment-account", profile.test_account ? `${profile.test_account} · ${profile.masked_account}` : 'Store-controlled authorization');
    text(form, "payment-mode", attempt.manual_review ? 'Manual store verification required' : 'Automatic internal simulation');
    text(form, "payment-instructions", profile.instructions + (attempt.manual_review ? ' Confirmation submits this authorization for administrator review.' : ' Confirm to authorize the exact amount above in the school simulator.'));
    const providers={GCash:'gcash.svg',Maya:'maya.svg',BPI:'bpi.svg',BDO:'bdo.svg',Metrobank:'metrobank.png'};
    const logo=field(form,'payment-logo');
    logo.dataset.provider=order.payment;
    if(providers[order.payment]) { const img=document.createElement('img');img.src='/static/images/payments/'+providers[order.payment];img.alt=order.payment;const fallback=document.createElement('span');fallback.textContent=order.payment;fallback.hidden=true;logo.append(img,fallback); }
    else logo.textContent=order.payment;
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

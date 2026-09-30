import {clone, field} from './dom.js';

export function notice(message) {
  let node = document.getElementById('notice');
  if (!node) {
    node = document.createElement('div'); node.id = 'notice'; node.className = 'notice';
    node.setAttribute('role', 'status'); document.body.append(node);
  }
  node.textContent = message; node.hidden = false;
  clearTimeout(notice.timer); notice.timer = setTimeout(() => {node.hidden = true;}, 6500);
}

export function dialog(title, template) {
  const node = clone('dialog');
  const titleId = `dialog-title-${crypto.randomUUID()}`;
  field(node, 'dialog-title').id = titleId; node.setAttribute('aria-labelledby', titleId);
  field(node, 'dialog-title').textContent = title;
  if (template) field(node, 'dialog-body').append(clone(template));
  document.body.append(node);
  node.addEventListener('click', event => {
    if (event.target === node || event.target.closest('[data-action="dialog-close"]')) node.close();
  });
  node.addEventListener('close', () => node.remove(), {once: true});
  const close = node.close.bind(node);
  node.close = () => {close(); node.remove();};
  node.showModal();
  return node;
}

export function formError(form, message) {
  const error = field(form, 'form-error');
  error.textContent = message; error.hidden = !message;
}

export function busy(form, pending, label = 'Save changes') {
  const button = form.querySelector('button[type="submit"]');
  button.disabled = pending; button.textContent = pending ? 'Please wait…' : label;
}

export function empty(node, message) {
  const text = document.createElement('p'); text.className = 'empty-state'; text.textContent = message;
  node.replaceChildren(text);
}

export function orderDetails(order) {
  const panel = dialog(`Order ${order.id}`, 'order-detail');
  for (const key of ['status', 'customer', 'address', 'phone', 'payment', 'date']) {
    field(panel, key).textContent = order[key];
  }
  field(panel, 'total').textContent = new Intl.NumberFormat('en-PH', {style:'currency', currency:'PHP'}).format(order.amount);
  for (const item of order.items) {
    const row = document.createElement('li'); row.textContent = `${item.name} × ${item.quantity}`;
    field(panel, 'items').append(row);
  }
  return panel;
}

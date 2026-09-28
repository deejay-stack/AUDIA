import {fallbackSales} from './data.js';
import {$, $$, field, text, clone, peso, animate, dismiss} from './dom.js';

const labels = {overview: 'Overview', sales: 'Sales directory', products: 'Products', customers: 'Customers'};
const statusStyles = {
  Paid: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-400/10 dark:text-emerald-300',
  Processing: 'bg-blue-100 text-blue-700 dark:bg-blue-400/10 dark:text-blue-300',
  Pending: 'bg-amber-100 text-amber-700 dark:bg-amber-400/10 dark:text-amber-300',
  Refunded: 'bg-rose-100 text-rose-700 dark:bg-rose-400/10 dark:text-rose-300',
};

export function mountAdmin(page, app) {
  let active = 'overview';
  let sales = fallbackSales;
  let query = '';
  let status = 'All';
  let backdrop;
  let alive = true;
  const main = field(page, 'admin-view');

  function saleRow(sale, recent) {
    const row = clone(recent ? 'recent-sale' : 'sale-row');
    for (const name of ['id', 'customer', 'email', 'product', ...(recent ? [] : ['date', 'payment'])]) text(row, name, sale[name]);
    text(row, 'amount', peso(sale.amount));
    const pill = field(row, 'status'); pill.textContent = sale.status;
    pill.className = `inline-flex rounded-full px-2.5 py-1 text-[11px] font-semibold ${statusStyles[sale.status] || statusStyles.Pending}`;
    return row;
  }
  function renderData() {
    if (active === 'overview') field(main, 'sales-rows').replaceChildren(...sales.slice(0, 5).map(sale => saleRow(sale, true)));
    if (active === 'sales') {
      const filtered = sales.filter(sale => (status === 'All' || sale.status === status)
        && `${sale.id} ${sale.customer} ${sale.product} ${sale.email}`.toLowerCase().includes(query.toLowerCase()));
      field(main, 'sales-rows').replaceChildren(...filtered.map(sale => saleRow(sale, false)));
      text(main, 'sales-count', `Showing ${filtered.length} of ${sales.length} sales`);
    }
    if (active === 'customers') field(main, 'customers').replaceChildren(...sales.map(sale => {
      const card = clone('customer'); text(card, 'initials', sale.customer.split(' ').map(part => part[0]).join(''));
      text(card, 'customer', sale.customer); text(card, 'email', sale.email);
      text(card, 'order', `Latest ${sale.id}`); text(card, 'amount', peso(sale.amount));
      return card;
    }));
  }
  function closeSidebar() {
    const sidebar = $(page, 'aside'); sidebar.classList.add('-translate-x-full'); sidebar.classList.remove('translate-x-0');
    if (backdrop) {dismiss(backdrop); backdrop = null;}
  }
  function navigate(next) {
    if (next !== active || !main.children.length) {
      active = next; query = ''; status = 'All';
      const view = clone(active === 'products' ? 'admin-products' : active);
      main.replaceChildren(view); renderData(); animate(view);
    }
    text(page, 'admin-title', labels[active]);
    $$(page, 'aside nav button').forEach(button => {
      const selected = button.dataset.action === active;
      button.className = `flex w-full items-center gap-3 rounded-xl px-3 py-3 text-sm font-medium transition ${selected
        ? 'bg-zinc-950 text-white dark:bg-acid dark:text-ink'
        : 'text-zinc-500 hover:bg-zinc-100 hover:text-zinc-950 dark:hover:bg-white/5 dark:hover:text-white'}`;
      const badge = $(button, 'span');
      if (badge) badge.className = `ml-auto rounded-full px-2 py-0.5 text-[9px] ${selected ? 'bg-white/15 dark:bg-black/10' : 'bg-zinc-100 dark:bg-white/5'}`;
    });
    closeSidebar();
  }
  page.addEventListener('click', event => {
    const action = event.target.closest('[data-action]')?.dataset.action;
    if (labels[action]) navigate(action);
    if (action === 'store') app.navigate('storefront');
    if (action === 'logout') app.logout();
    if (action === 'close-sidebar') closeSidebar();
    if (action === 'sidebar') {
      const sidebar = $(page, 'aside'); sidebar.classList.remove('-translate-x-full'); sidebar.classList.add('translate-x-0');
      if (!backdrop) {backdrop = clone('sidebar-backdrop'); page.prepend(backdrop); animate(backdrop);}
    }
  });
  page.addEventListener('input', event => {
    if (event.target.dataset.field === 'sales-query') {query = event.target.value; renderData();}
  });
  page.addEventListener('change', event => {
    if (event.target.dataset.field === 'sales-status') {status = event.target.value; renderData();}
  });
  navigate('overview');
  fetch('/api/admin/sales').then(response => response.json()).then(data => {
    if (alive && data.sales?.length) {sales = data.sales; renderData();}
  }).catch(() => {});
  return {destroy() {alive = false;}};
}

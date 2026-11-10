import { api, field, text, peso, empty, dialog, busy, formError, orderDetails, poll, notice } from '../shared/shared.js';

const stamp = value => new Date(value).toLocaleString('en-PH', { timeZone: 'Asia/Manila' });
const node = (tag, value, className) => {
  const item = document.createElement(tag);
  if (value !== undefined) item.textContent = value;
  if (className) item.className = className;
  return item;
};

function bars(container, entries, currency = true, drilldown) {
  const max = Math.max(...entries.map(([, value]) => Math.abs(value)), 0);
  if (!entries.length || !max) return empty(container, 'No records for this period.');
  container.replaceChildren(...entries.map(([label, value]) => {
    const row = node('div', undefined, 'finance-bar');
    if(drilldown){row.tabIndex=0;row.setAttribute('role','button');row.setAttribute('aria-label',`Inspect ${label} transactions`);row.addEventListener('click',()=>drilldown(label));row.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();drilldown(label);}});}
    row.dataset.negative = value < 0;
    const caption = node('span'), meter = document.createElement('meter');
    caption.append(node('span', label), node('strong', currency ? peso(value) : value));
    meter.min = 0; meter.max = max; meter.value = Math.abs(value);
    meter.setAttribute('aria-label', `${label}: ${currency ? peso(value) : value}`);
    row.append(caption, meter); return row;
  }));
}

export function renderFinanceSummary(main, report, app, period, group) {
  const counts = new Set(['total_orders','new_customers','low_stock_items','pending_payments','paid_orders','cancelled_orders','refunded_transactions','products_sold']);
  for (const item of main.querySelectorAll('[data-metric]')) {
    const key = item.dataset.metric;
    text(item, key, counts.has(key) ? report[key] : peso(report[key]));
    item.dataset.action = key === 'new_customers' ? 'customers' : key === 'low_stock_items' ? 'products' : key === 'total_orders' || key === 'cancelled_orders' ? 'sales' : 'transactions';
  }
  text(main, 'today', new Date().toLocaleDateString('en-PH', {timeZone:'Asia/Manila', weekday:'long',month:'long',day:'numeric'}));
  text(main, 'admin-greeting', `Welcome back, ${app.user.name.split(' ')[0]}.`);
  text(main, 'report-formula', `${report.start} through ${report.end}. ${report.formula} Today/week/month cards show the current Manila calendar period.`);
  text(main,'completion-rates',`Order completion: ${report.completion_rate}% · Cancellation rate: ${report.cancellation_rate}% for the selected period.`);
  field(main,'recent-activity').replaceChildren(...report.recent_activity.map(e=>node('li',`${stamp(e.at)} · ${e.order_id} · ${e.note||e.status}`)));
  text(main, 'report-legacy', `${report.excluded_legacy_records} historical record(s) lack a complete collection/refund date and are excluded from dated financial totals.`);
  field(main, 'report-legacy').hidden = !report.excluded_legacy_records;
  field(main, 'report-period').value = period;
  field(main, 'report-start').value = report.start;
  field(main, 'report-end').value = report.end;
  field(main, 'report-group').value = group;
  field(main, 'revenue-chart').className = 'finance-time-chart';
  bars(field(main, 'revenue-chart'), report.chart.map(day => [day.date, day.amount]));
  const drilldown=filters=>main.dispatchEvent(new CustomEvent('audia:ledger-filter',{bubbles:true,detail:{start:report.start,end:report.end,...filters}}));
  bars(field(main, 'method-chart'), Object.entries(report.payment_methods),true,method=>drilldown({method}));
  bars(field(main, 'channel-chart'), Object.entries(report.channels).map(([k,v]) => [k === 'pos' ? 'Counter POS' : 'Online store', v]),true,channel=>drilldown({channel:channel==='Counter POS'?'pos':'online'}));
  bars(field(main, 'status-chart'), Object.entries(report.order_statuses), false);
  const operational=field(main,'operations-summary');
  if(operational){operational.replaceChildren(...[['refunds',`${report.refund_requests} open refund / cancellation requests`],['transactions',`${report.verification_pending} bank authorizations to verify`],['delivery',`${Object.entries(report.order_statuses).filter(([s])=>['Processing','Packed','Shipped','Out for Delivery'].includes(s)).reduce((n,[,v])=>n+v,0)} orders in fulfillment`]].map(([action,label])=>{const b=node('button',label,'secondary-btn');b.type='button';b.dataset.action=action;return b;}));}
  bars(field(main, 'category-report'), Object.entries(report.categories));
  const best = field(main, 'best-sellers');
  if (!report.best_sellers.length) empty(best, 'Collected product sales appear here.');
  else best.replaceChildren(...report.best_sellers.map(p => node('p', `${p.name} (#${p.id}) · ${p.quantity} sold · ${peso(p.revenue)}`, 'form-hint')));
}

export async function mountPos(main) {
  const root = main.firstElementChild, form = root.querySelector('form'), cart = new Map();
  const storage = 'audia-pos-draft';
  let draft;
  try { draft = JSON.parse(sessionStorage.getItem(storage)); } catch { /* Start clean. */ }
  let key = draft?.key || crypto.randomUUID(), products = [], completed = false, sending = false, pendingPayload = draft?.pendingPayload || null;
  if (draft?.values) for (const [name, value] of Object.entries(draft.values)) if (form.elements[name]) form.elements[name].value = value;
  if (Array.isArray(draft?.items)) for (const item of draft.items) if (Number.isInteger(item.product_id) && Number.isInteger(item.quantity)) cart.set(item.product_id, item.quantity);
  function save() {
    const values=Object.fromEntries([...form.elements].filter(c=>c.name).map(c=>[c.name,c.value]));
    sessionStorage.setItem(storage, JSON.stringify({key, pendingPayload, items: [...cart].map(([product_id,quantity]) => ({product_id,quantity})), values}));
  }
  function total() {
    const subtotal = [...cart].reduce((sum,[id,qty]) => sum + Math.round((products.find(p => p.id === id)?.price || 0)*100)*qty, 0);
    text(root, 'pos-subtotal', peso(subtotal/100));
    text(root, 'pos-total', peso((subtotal - Math.round(Number(form.elements.discount.value || 0)*100))/100));
    form.elements.discount_reason.required = Number(form.elements.discount.value) > 0;
  }
  function renderCart() {
    const target = field(root, 'pos-cart');
    if (!cart.size) empty(target, 'Add a product to begin a sale.');
    else target.replaceChildren(...[...cart].map(([id,qty]) => {
      const p = products.find(p => p.id === id), row = node('div', undefined, 'pos-cart-row');
      const label = node('span', p ? `${p.name} · ${peso(p.price)}` : `Unavailable product #${id}`);
      const input = document.createElement('input'); input.type='number'; input.min=1; input.max=Math.min(p?.stock || 99,99); input.value=qty;
      input.disabled=completed || !!pendingPayload; input.setAttribute('aria-label', `Quantity for ${p?.name || id}`);
      input.addEventListener('change', () => { if (!input.checkValidity()) return input.reportValidity(); cart.set(id,Number(input.value)); save(); total(); });
      const remove = node('button','×'); remove.type='button'; remove.disabled=completed || !!pendingPayload; remove.setAttribute('aria-label',`Remove ${p?.name || id}`);
      remove.addEventListener('click', () => { cart.delete(id); save(); renderCart(); });
      row.append(label,input,remove); return row;
    }));
    total();
  }
  function renderProducts() {
    const query = field(root,'pos-search').value.trim().toLowerCase();
    const shown = products.filter(p => p.active && (!query || `${p.id} ${p.name} ${p.brand}`.toLowerCase().includes(query))).slice(0,40);
    if (!shown.length) return empty(field(root,'pos-products'),'No matching products.');
    field(root,'pos-products').replaceChildren(...shown.map(p => {
      const button = node('button',undefined,'pos-product'); button.type='button'; button.disabled=!p.stock || completed || sending || !!pendingPayload;
      const copy = node('span',p.name); copy.append(node('small',`#${p.id} · ${p.stock} available`)); button.append(copy,node('strong',peso(p.price)));
      button.addEventListener('click', () => {
        if ((cart.get(p.id)||0) >= Math.min(p.stock,99)) return notice('Available stock limit reached.');
        cart.set(p.id,(cart.get(p.id)||0)+1); save(); renderCart();
      }); return button;
    }));
  }
  field(root,'pos-search').addEventListener('input',renderProducts);
  field(root,'pos-search').addEventListener('keydown', event => {
    if (event.key === 'Enter') { event.preventDefault(); const code=event.target.value.trim().toLowerCase(); const p=products.find(p=>p.active && (String(p.id)===code || p.name.toLowerCase()===code)); if (p && p.stock && !completed && !sending && !pendingPayload && (cart.get(p.id)||0)<Math.min(p.stock,99)) { cart.set(p.id,(cart.get(p.id)||0)+1); save(); renderCart(); } }
  });
  form.addEventListener('input', () => { if (!completed) { save(); total(); } });
  field(root,'pos-new').addEventListener('click', () => { sessionStorage.removeItem(storage); void mountFresh(); });
  async function mountFresh() {
    const { clone } = await import('../shared/shared.js'); main.replaceChildren(clone('pos')); await mountPos(main);
  }
  form.addEventListener('submit',async event => {
    event.preventDefault(); if (sending || completed) return;
    if (!cart.size) return formError(form,'Add at least one product.');
    save(); sending=true; busy(form,true); formError(form,'');
    // Freeze the submitted payload until its response is known. An uncertain network
    // result keeps the same request key for a safe replay after reload.
    const values=Object.fromEntries(new FormData(form));
    const items=[...cart].map(([product_id,quantity])=>({product_id,quantity}));
    const subtotal=items.reduce((sum,i)=>sum+Math.round((products.find(p=>p.id===i.product_id)?.price||0)*100)*i.quantity,0);
    for (const control of form.elements) control.disabled=true;
    renderProducts();
    try {
      pendingPayload ||= {...values,discount:values.discount,confirmed:true,items,request_key:key,expected_total:((subtotal-Math.round(Number(values.discount)*100))/100).toFixed(2)};
      save();
      const data=await api('/admin/pos',{method:'POST',body:pendingPayload});
      if (!root.isConnected) return;
      completed=true; sessionStorage.removeItem(storage);
      const receipt=field(root,'pos-receipt'); receipt.href=data.order.receipt_url; receipt.hidden=false;
      field(root,'pos-new').hidden=false; field(root,'pos-new').disabled=false;
      notice(`Sale ${data.order.id} recorded. Receipt is ready.`); renderCart();
    } catch(error) {
      if (root.isConnected) formError(form,error.message + (!error.status || error.status >= 500 ? ' Retry will recover the original submitted sale safely.' : ''));
      if (error.status && error.status < 500) {key=crypto.randomUUID();pendingPayload=null;}
      for (const control of form.elements) control.disabled=!!pendingPayload && control.type !== 'submit';
      renderCart();
      save();
    } finally {
      sending=false; busy(form,completed,completed?'Transaction recorded':'Complete transaction');
      if (completed) form.querySelector('[type=submit]').textContent='Transaction recorded';
      renderProducts();
    }
  });
  try { const data=await api('/admin/products'); if (!root.isConnected) return; products=data.products; renderProducts(); renderCart(); }
  catch(error) { empty(field(root,'pos-products'),error.message); }
  if(pendingPayload){
    for(const control of form.elements) control.disabled=control.type !== 'submit';
    formError(form,'An earlier response was interrupted. Retry to recover the original submitted sale safely.');
  }
}

export async function mountTransactions(main, defaults = {}) {
  const root=main.firstElementChild, form=root.querySelector('form');
  let page=1, pages=1, loading=false, generation=0;
  const today=new Intl.DateTimeFormat('en-CA',{timeZone:'Asia/Manila',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date());
  form.elements.start.value=defaults.start || today.slice(0,8)+'01'; form.elements.end.value=defaults.end || today;
  for (const [k,v] of Object.entries(defaults)) if (form.elements[k]) form.elements[k].value=v;
  async function load() {
    const request=++generation; loading=true; text(root,'ledger-loading','Loading transactions…');
    const params=new URLSearchParams({...Object.fromEntries(new FormData(form)),page});
    field(root,'ledger-export').href='/api/admin/transactions/export?'+params;
    try {
      const data=await api('/admin/transactions?'+params); if (!root.isConnected || request!==generation) return;
      pages=data.pages; field(root,'ledger-error').hidden=true;
      field(root,'ledger-rows').replaceChildren(...data.transactions.map(t=>{
        const row=node('tr');
        for (const value of [t.reference,t.customer,t.method,peso(t.amount),t.status,stamp(t.date),t.channel==='pos'?'Counter POS':'Online store',t.verification]) row.append(node('td',value));
        row.firstElementChild.append(node('small',t.order_id));
        const actions=node('td'), details=node('button','Details / refund'); details.type='button'; details.addEventListener('click',()=>void detailsPanel(t.order_id)); actions.append(details);
        if(t.receipt_url) {const a=node('a','Receipt');a.href=t.receipt_url;a.target='_blank';a.rel='noopener';actions.append(a);}
        row.append(actions);return row;
      }));
      field(root,'ledger-empty').hidden=!!data.transactions.length;
      text(root,'ledger-count',`${data.count} transactions · Page ${data.page} of ${data.pages}`);
      field(root,'ledger-prev').disabled=page<=1; field(root,'ledger-next').disabled=page>=pages;
    } catch(error) {if(root.isConnected) {text(root,'ledger-error',error.message);field(root,'ledger-error').hidden=false;}}
    finally {if(request===generation){loading=false;text(root,'ledger-loading','');}}
  }
  async function detailsPanel(id) {
    try {
      const data=await api(`/admin/transactions/${id}`); if(!root.isConnected)return;
      const t=data.transaction, panel=dialog(`Transaction ${t.reference}`,'transaction-detail');
      const info=field(panel,'transaction-info');
      for(const [label,value] of [['Order',id],['Customer',t.customer],['Method',t.method],['Amount',peso(t.amount)],['Status',t.status],['Refunded',peso(t.refunded)],['Channel',t.channel]]) info.append(node('dt',label),node('dd',value));
      const events=field(panel,'transaction-events');
      if(!t.events.length) empty(events,'Historical record: no detailed payment events were recorded.');
      else events.replaceChildren(...t.events.map(e=>node('li',`${stamp(e.at)} · ${e.previous} → ${e.status} · ${e.action} · ${e.actor_id ? 'Actor #'+e.actor_id : 'System'}`)));
      const refunds=field(panel,'transaction-refunds');
      if(!t.refunds.length) empty(refunds,'No refunds recorded.');
      else refunds.replaceChildren(...t.refunds.map(r=>node('li',`${stamp(r.at)} · ${r.id} · ${peso(r.amount)} · ${r.reason}`)));
      field(panel,'transaction-order').addEventListener('click',()=>orderDetails(data.order,{live:false,customer:false}));
      if(t.status==='Pending Verification'){
        const review=document.createElement('form');review.className='stack-form';
        const heading=node('h3','Verify simulated bank authorization');
        const note=document.createElement('input');note.required=true;note.minLength=3;note.maxLength=180;note.placeholder='Verification note';note.setAttribute('aria-label','Bank verification note');
        const action=document.createElement('select');action.setAttribute('aria-label','Bank verification decision');action.append(new Option('Approve internal payment','approve'),new Option('Reject authorization','reject'));
        const error=node('p',undefined,'form-error');error.dataset.field='form-error';error.hidden=true;error.setAttribute('role','alert');
        const button=node('button','Save verification','primary-btn');button.type='submit';review.append(heading,note,action,error,button);field(panel,'dialog-body').append(review);
        const attempt=[...data.order.payment_attempts].reverse().find(a=>a.status==='Awaiting review');
        review.addEventListener('submit',async e=>{e.preventDefault();busy(review,true);try{await api(`/admin/payments/${id}/verify`,{method:'POST',body:{action:action.value,note:note.value,attempt_id:attempt?.id}});panel.close();notice('Bank authorization reviewed.');await load();}catch(e){formError(review,e.message);}finally{busy(review,false,'Save verification');}});
      }
      const refundForm=field(panel,'refund-form');
      refundForm.hidden=!['Paid','Partially Refunded'].includes(t.status);
      refundForm.elements.amount.max=(t.amount-t.refunded).toFixed(2);
      const requestKey=crypto.randomUUID(); let sending=false;
      refundForm.addEventListener('submit',async event=>{
        event.preventDefault();if(sending)return;sending=true;busy(refundForm,true);formError(refundForm,'');
        try {await api(`/admin/transactions/${id}/refunds`,{method:'POST',body:{amount:refundForm.elements.amount.value,reason:refundForm.elements.reason.value,request_key:requestKey}});panel.close();notice('Internal refund recorded.');await load();}
        catch(error){formError(refundForm,error.message);}finally{sending=false;busy(refundForm,false,'Record refund');}
      });
    }catch(error){notice(error.message);}
  }
  form.addEventListener('submit',event=>{event.preventDefault();page=1;void load();});
  field(root,'ledger-prev').addEventListener('click',()=>{if(page>1&&!loading){page--;void load();}});
  field(root,'ledger-next').addEventListener('click',()=>{if(page<pages&&!loading){page++;void load();}});
  await load();
  const stop=poll(async()=>{if(!root.isConnected)return stop();if(!loading)await load();});
  return stop;
}

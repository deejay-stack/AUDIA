import { mountPos, mountTransactions, renderFinanceSummary } from "./finance.js";
import { mountOperations, customerProfile } from './operations.js';
import {
  imageSource,
  $,
  $$,
  field,
  text,
  clone,
  peso,
  animate,
  dismiss,
  api,
  dialog,
  notice,
  empty,
  busy,
  formError,
  orderDetails,
  poll,
} from "../shared/shared.js";

const labels = {
  overview: "Overview",
  pos: "Point of sale",
  transactions: "Payments & transactions",
  sales: "Orders & payments",
  products: "Products",
  customers: "Customers",
  settings: "Settings",
  refunds: 'Returns & Refunds', inventory: 'Inventory movements', delivery: 'Fulfillment & Delivery',
};

export function mountAdmin(page, app) {
  let active = "",
    sales = [],
    products = [],
    customers = [],
    query = "",
    status = "All",
    paymentFilter = '', salesSort = 'newest',
    pageNumber = 0,
    period = "week", group = "day", reportStart = "", reportEnd = "", ledgerDefaults = {}, stopLedger;
  let alive = true,
    generation = 0,
    backdrop,
    summary;
  const main = field(page, "admin-view");
  page.addEventListener('audia:ledger-filter',event=>{ledgerDefaults=event.detail;void navigate('transactions');});
  text(page, "admin-name", app.user.name);
  function saleRow(sale, recent = false) {
    const row = clone(recent ? "recent-sale" : "sale-row");
    row.dataset.orderId = sale.id;
    for (const key of [
      "id",
      "customer",
      "email",
      "product",
      ...(recent ? [] : ["date", "payment"]),
    ])
      text(row, key, sale[key]);
    text(row, "amount", peso(sale.amount));
    if (!recent) text(row, "payment", `${sale.payment} · ${sale.payment_status}`);
    text(row, "status", sale.status);
    field(row, "status").className =
      `order-status status-${sale.status.toLowerCase().replaceAll(" ", "-")}`;
    return row;
  }
  function renderSales() {
    const filtered = sales.filter(
      (sale) =>
        (status === "All" || sale.status === status) && (!paymentFilter || sale.payment_status === paymentFilter) &&
        `${sale.id} ${sale.customer} ${sale.email} ${sale.product}`
          .toLowerCase()
          .includes(query.toLowerCase()),
    );
    const recent = active === "overview";
    filtered.sort((a,b)=>salesSort==='amount'?b.amount-a.amount:salesSort==='customer'?a.customer.localeCompare(b.customer):b.created_at.localeCompare(a.created_at));
    pageNumber = Math.max(
      0,
      Math.min(pageNumber, Math.ceil(filtered.length / 10) - 1),
    );
    const shown = recent
      ? filtered.slice(0, 5)
      : filtered.slice(pageNumber * 10, pageNumber * 10 + 10);
    field(main, "sales-rows").replaceChildren(
      ...shown.map((sale) => saleRow(sale, recent)),
    );
    field(main, "sales-empty").hidden = shown.length > 0;
    if (!recent) {
      text(
        main,
        "sales-count",
        filtered.length
          ? `Showing ${pageNumber * 10 + 1}–${pageNumber * 10 + shown.length} of ${filtered.length} orders`
          : "No matching orders",
      );
      $(main, '[data-action="sales-previous"]').disabled = pageNumber === 0;
      $(main, '[data-action="sales-next"]').disabled =
        (pageNumber + 1) * 10 >= filtered.length;
    }
  }
  function renderProducts() {
    const filtered = products.filter((product) =>
      `${product.name} ${product.brand}`
        .toLowerCase()
        .includes(query.toLowerCase()),
    );
    if (!filtered.length)
      return empty(
        field(main, "admin-products"),
        "No products match your search.",
      );
    field(main, "admin-products").replaceChildren(
      ...filtered.map((product) => {
        const card = clone("admin-product");
        card.dataset.productId = product.id;
        field(card, "image").src = imageSource(product.image);
        field(card, "image").alt = product.name;
        text(card, "name", product.name);
        text(card, "category", `${product.brand} · ${product.category}`);
        text(card, "price", peso(product.price));
        text(
          card,
          "stock",
          product.active ? `${product.stock} in stock` : "Archived",
        );
        $(card, '[data-action="edit-product"]').setAttribute(
          "aria-label",
          `Edit ${product.name}`,
        );
        return card;
      }),
    );
  }
  function renderCustomers() {
    const filtered = customers.filter((customer) =>
      `${customer.name} ${customer.email}`
        .toLowerCase()
        .includes(query.toLowerCase()),
    );
    if (!filtered.length)
      return empty(field(main, "customers"), "No customers match your search.");
    field(main, "customers").replaceChildren(
      ...filtered.map((customer) => {
        const card = clone("customer");
        card.tabIndex=0;card.setAttribute('role','button');card.setAttribute('aria-label',`View ${customer.name}`);
        card.addEventListener('click',()=>void customerProfile(customer.id));
        card.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();void customerProfile(customer.id);}});
        text(
          card,
          "initials",
          customer.name
            .split(" ")
            .map((part) => part[0])
            .slice(0, 2)
            .join(""),
        );
        text(card, "customer", customer.name);
        text(card, "email", customer.email);
        text(card, "order", `${customer.orders} orders`);
        text(card, "amount", peso(customer.amount));
        return card;
      }),
    );
  }
  function renderSummary() {
    renderFinanceSummary(main, summary, app, period, group);
  }

  function closeSidebar() {
    const sidebar = $(page, "aside");
    sidebar.classList.add("is-sidebar-closed");
    sidebar.classList.remove("is-sidebar-open");
    if (backdrop) {
      dismiss(backdrop);
      backdrop = null;
    }
  }
  async function navigate(next) {
    if (!alive) return;
    stopLedger?.(); stopLedger = null;
    active = next;
    const url=next==='overview'?'/admin':'/admin/'+next;
    if(location.pathname!==url)history.replaceState(null,'',url);
    window.scrollTo({top:0, behavior:"instant"});
    query = "";
    status = "All";
    paymentFilter='';salesSort='newest';
    pageNumber = 0;
    const request = ++generation;
    main.replaceChildren(clone(next === "products" ? "admin-products" : next));
    text(page, "admin-title", labels[next]);
    $$(page, "aside nav button").forEach((button) => {
      const selected = button.dataset.action === next;
      button.setAttribute("aria-current", selected ? "page" : "false");
      button.className = selected ? "admin-sidebar__link--selected" : "admin-sidebar__link";
    });
    closeSidebar();
    animate(main.firstElementChild);
    try {
      if (next === "overview") {
        const [report, orders] = await Promise.all([
          api(`/admin/summary?${new URLSearchParams({period, group, ...(reportStart ? {start:reportStart,end:reportEnd} : {})})}`),
          api("/admin/sales"),
        ]);
        if (!alive || request !== generation) return;
        summary = report;
        sales = orders.sales;
        renderSummary();
        renderSales();
        text(page, "order-count", sales.length);
      } else if (next === "pos") {
        await mountPos(main);
      } else if (['refunds','inventory','delivery'].includes(next)) {
        stopLedger=await mountOperations(main,next);
      } else if (next === "transactions") {
        stopLedger = await mountTransactions(main, ledgerDefaults);
        ledgerDefaults = {};
      } else if (next === "sales") {
        const data = await api("/admin/sales");
        if (!alive || request !== generation) return;
        sales = data.sales;
        renderSales();
      } else if (next === "products") {
        const data = await api("/admin/products");
        if (!alive || request !== generation) return;
        products = data.products;
        renderProducts();
      } else if (next === "customers") {
        const data = await api("/admin/customers");
        if (!alive || request !== generation) return;
        customers = data.customers;
        renderCustomers();
      } else if (next === "settings") {
        const data = await api("/admin/settings");
        if (!alive || request !== generation) return;
        const form = main.querySelector("form");
        for (const [key, value] of Object.entries(data.settings))
          if (form.elements[key]) form.elements[key].value = value;
        const audit=await api('/admin/audit');if(!alive||request!==generation)return;
        field(main,'settings-audit').replaceChildren(...audit.events.map(e=>{const li=document.createElement('li');li.textContent=`${new Date(e.at).toLocaleString()} · ${e.action} · Actor #${e.actor_id}`;return li;}));
      }
    } catch (error) {
      if (!alive || request !== generation) return;
      if (error.status === 401) {
        app.user = null;
        app.navigate("auth", "admin");
        notice("Your session expired. Please sign in again.");
        return;
      }
      const message = document.createElement("p");
      message.className = "form-error";
      message.textContent = error.message;
      message.setAttribute("role", "alert");
      main.prepend(message);
    }
  }
  function productEditor(product) {
    const panel = dialog(
        product ? "Edit instrument" : "Add an instrument",
        "product-form",
      ),
      form = panel.querySelector("form");
    if(product){
      const history=document.createElement('button');history.type='button';history.className='secondary-btn';history.textContent='View product sales history';field(form,'product-history').append(history);
      history.addEventListener('click',async()=>{try{const data=await api(`/admin/products/${product.id}/history`),p=dialog(`${product.name} · Sales history`),body=field(p,'dialog-body');if(!data.orders.length)empty(body,'No orders for this product.');for(const order of data.orders){const b=document.createElement('button');b.type='button';b.className='secondary-btn';b.textContent=`${order.id} · ${order.customer} · ${order.payment_status} · ${peso(order.amount)}`;b.addEventListener('click',()=>orderDetails(order,{customer:false}));body.append(b);}}catch(e){notice(e.message);}});
    }
    api('/admin/settings').then(({settings})=>{
      form.elements.category.replaceChildren(...settings.categories.split(',').map(c=>new Option(c,c)));
      if(product)form.elements.category.value=product.category;
    }).catch(e=>formError(form,e.message));
    const upload=form.querySelector('[name=upload_image]');
    upload.addEventListener('change',async()=>{
      if(!upload.files.length)return;
      const body=new FormData();body.set('purpose','product');body.set('image',upload.files[0]);
      busy(form,true);try{form.elements.image.value=(await api('/uploads',{method:'POST',body})).url;notice('Product image uploaded. Save the product to use it.');}catch(e){formError(form,e.message);}finally{busy(form,false,'Save product');}
    });
    if (product)
      for (const [key, value] of Object.entries(product)) {
        if (!form.elements[key]) continue;
        if (key === "active") form.elements[key].checked = value;
        else
          form.elements[key].value = key === "specs" ? value.join("\n") : value;
      }
    const archive = $(form, '[data-action="archive-product"]');
    archive.hidden = !product?.active;
    archive.addEventListener("click", async () => {
      archive.disabled = true;
      try {
        await api(`/admin/products/${product.id}`, { method: "DELETE" });
        panel.close();
        notice("Product archived.");
        if (alive) navigate(active);
      } catch (error) {
        formError(form, error.message);
        archive.disabled = false;
      }
    });
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      if (form.querySelector("[type=submit]").disabled) return;
      busy(form, true);
      formError(form, "");
      const values = Object.fromEntries(new FormData(form));
      delete values.upload_image;
      values.price = Number(values.price);
      values.stock = Number(values.stock);
      values.active = form.elements.active.checked;
      values.specs = values.specs
        .split("\n")
        .map((item) => item.trim())
        .filter(Boolean);
      try {
        await api(
          product ? `/admin/products/${product.id}` : "/admin/products",
          { method: product ? "PUT" : "POST", body: values },
        );
        panel.close();
        notice("Product saved.");
        if (alive) navigate(active);
      } catch (error) {
        formError(form, error.message);
      } finally {
        busy(form, false, "Save product");
      }
    });
  }
  async function editOrder(order) {
    try { order = (await api(`/orders/${order.id}`)).order; }
    catch (error) { notice(error.message); return; }
    if (!alive) return;
    const panel = orderDetails(order, { live: false, customer: false }),
      choices = order.next_statuses || [];
    const canCollect = order.payment === "Cash on delivery" && order.payment_status === "Pending";
    if (!choices.length && !canCollect) return;
    const form = clone("order-status");
    field(panel, "dialog-body").append(form);
    form.elements.status.replaceChildren(
      new Option(`Keep ${order.status}`, order.status),
      ...choices.map((status) => new Option(status === "Confirmed" ? "Accept order (Confirmed)" : status === "Rejected" ? "Reject order" : status, status)),
    );
    function paymentControls() {
      const collecting = canCollect && form.elements.status.value === "Delivered";
      field(form, "collection").hidden = !collecting;
      form.elements.collection_confirmed.disabled = !collecting;
      form.elements.payment_reference.disabled = !collecting;
      form.elements.payment_reference.required = collecting && form.elements.collection_confirmed.checked;
      field(form, "refund").hidden = !(order.payment_status === "Paid" && form.elements.status.value === "Refunded");
    }
    form.addEventListener("change", paymentControls);
    paymentControls();
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      if (form.querySelector("[type=submit]").disabled) return;
      busy(form, true);
      formError(form, "");
      try {
        await api(`/admin/sales/${order.id}`, {
          method: "PATCH",
          body: {
            status: form.elements.status.value, expected_status: order.status,
            reason:form.elements.reason.value,
            ...(form.elements.collection_confirmed.checked && !form.elements.collection_confirmed.disabled ? {
              payment_status: "Paid", collection_confirmed: true,
              payment_reference: form.elements.payment_reference.value,
            } : {}),
            refund_confirmed: form.elements.refund_confirmed.checked,
          },
        });
        panel.close();
        notice("Order updated.");
        if (alive) navigate(active);
      } catch (error) {
        formError(form, error.message);
      } finally {
        busy(form, false, "Update order");
      }
    });
  }
  page.addEventListener("click", async (event) => {
    const button = event.target.closest("[data-action]");
    if (!button) return;
    const action = button.dataset.action;
    if (labels[action]) {
      if (action === "transactions" && button.dataset.metric && summary) {
        const key = button.dataset.metric === "pending_payments" ? "pending_collection" : button.dataset.metric;
        ledgerDefaults = {start:summary.start,end:summary.end};
        if (["pending_collection","gross_sales","net_sales","collected_total","refunded_total","paid_orders","products_sold","refunded_transactions"].includes(key)) ledgerDefaults.metric = key;

        else ledgerDefaults.metric = "revenue";
        const today = new Intl.DateTimeFormat('en-CA',{timeZone:'Asia/Manila',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date());
        if (key === 'today_revenue') ledgerDefaults.start = ledgerDefaults.end = today;
        if (key === 'monthly_revenue') {ledgerDefaults.start=today.slice(0,8)+'01';ledgerDefaults.end=today;}
        if (key === 'weekly_revenue') {const d=new Date(today+'T00:00:00Z');d.setUTCDate(d.getUTCDate()-(d.getUTCDay()+6)%7);ledgerDefaults.start=d.toISOString().slice(0,10);ledgerDefaults.end=today;}
      }
      navigate(action);
    }
    if (action === 'report-dates') {reportStart=field(main,'report-start').value;reportEnd=field(main,'report-end').value;group=field(main,'report-group').value;navigate('overview');}
    if (action === 'print-report') window.print();
    if (action === "store") app.navigate("landing");
    if (action === "admin-account") app.navigate("account");
    if (action === "logout") app.logout();
    if (action === "close-sidebar") closeSidebar();
    if (action === "sidebar") {
      if(matchMedia('(min-width:1024px)').matches){page.classList.toggle('sidebar-collapsed');return;}
      const sidebar = $(page, "aside");
      sidebar.classList.remove("is-sidebar-closed");
      sidebar.classList.add("is-sidebar-open");
      if (!backdrop) {
        backdrop = clone("sidebar-backdrop");
        page.prepend(backdrop);
        animate(backdrop);
      }
    }
    if (action === "add-product") productEditor();
    if (action === "edit-product")
      productEditor(
        products.find(
          (product) =>
            product.id ===
            Number(button.closest("[data-product-id]").dataset.productId),
        ),
      );
    if (action === "edit-order")
      editOrder(
        sales.find(
          (order) =>
            order.id === button.closest("[data-order-id]").dataset.orderId,
        ),
      );
    if (action === "sales-previous") {
      pageNumber--;
      renderSales();
    }
    if (action === "sales-next") {
      pageNumber++;
      renderSales();
    }
    if (action === "export-sales") {
      try {
        const response = await fetch(
          `/api/admin/sales/export?${new URLSearchParams({ q: query, status, payment_status:paymentFilter })}`,
        );
        if (!response.ok)
          throw new Error(
            "Unable to export sales. Please sign in and try again.",
          );
        const url = URL.createObjectURL(await response.blob()),
          link = document.createElement("a");
        link.href = url;
        link.download = "audia-sales.csv";
        link.click();
        setTimeout(() => URL.revokeObjectURL(url), 1000);
      } catch (error) {
        notice(error.message);
      }
    }
    if (action === "notifications") {
      const panel = dialog("Store notifications", "notifications");
      try {
        const data = await api("/admin/summary");
        if (!panel.isConnected) return;
        const alerts = [
          `${data.pending_orders} orders awaiting processing.`,
          `${data.refund_requests} cancellation / refund requests awaiting review.`,
          `${data.verification_pending} simulated bank payments awaiting verification.`,
          ...data.low_stock.map(
            (product) => `${product.name}: ${product.stock} left in stock.`,
          ),
        ];
        field(panel, "alerts").replaceChildren(
          ...alerts.map((message) => {
            const item = document.createElement("li");
            item.textContent = message;
            return item;
          }),
        );
      } catch (error) {
        empty(field(panel, "alerts"), error.message);
      }
    }
  });
  page.addEventListener("input", (event) => {
    const name = event.target.dataset.field;
    if (name === "sales-query") {
      query = event.target.value;
      pageNumber = 0;
      renderSales();
    }
    if (name === "product-query") {
      query = event.target.value;
      renderProducts();
    }
    if (name === "customer-query") {
      query = event.target.value;
      renderCustomers();
    }
  });
  page.addEventListener("change", (event) => {
    if(event.target.dataset.field==='sales-payment'){paymentFilter=event.target.value;pageNumber=0;renderSales();}
    if(event.target.dataset.field==='sales-sort'){salesSort=event.target.value;pageNumber=0;renderSales();}
    if (event.target.dataset.field === "sales-status") {
      status = event.target.value;
      pageNumber = 0;
      renderSales();
    }
    if (event.target.dataset.field === "report-group") {group=event.target.value;navigate("overview");}
    if (event.target.dataset.field === "report-period") {
      period = event.target.value; reportStart = reportEnd = "";
      navigate("overview");
    }
  });
  page.addEventListener("submit", async (event) => {
    if(event.target.dataset.form==='admin-search'){
      event.preventDefault();const value=event.target.elements.q.value;await navigate('sales');query=value;field(main,'sales-query').value=value;renderSales();return;
    }
    if (event.target.dataset.form !== "settings") return;
    event.preventDefault();
    const form = event.target;
    if (form.querySelector("[type=submit]").disabled) return;
    busy(form, true);
    formError(form, "");
    try {
      const data = await api("/admin/settings", {
        method: "PUT",
        body: Object.fromEntries(new FormData(form)),
      });
      if (alive) text(page, "store-name", data.settings.store_name);
      notice("Store settings saved.");
    } catch (error) {
      formError(form, error.message);
    } finally {
      busy(form, false, "Save settings");
    }
  });
  api("/admin/settings")
    .then((data) => {
      if (alive) text(page, "store-name", data.settings.store_name);
    })
    .catch(() => {});
  navigate(document.body.dataset.adminSection || 'overview');
  const stopPolling = poll(async () => {
    if (!alive || !["overview", "sales"].includes(active)) return;
    const view = active;
    try {
      const data = await api("/admin/sales");
      if (!alive || view !== active) return;
      if (active === "overview") {
        summary = await api(`/admin/summary?${new URLSearchParams({period,group,...(reportStart?{start:reportStart,end:reportEnd}:{})})}`);
        if (!alive || view !== active) return;
        renderSummary();
      }
      if (JSON.stringify(data.sales) !== JSON.stringify(sales)) {
        sales = data.sales; renderSales(); text(page, "order-count", sales.length);
      }
    } catch { /* Keep displayed records; manual navigation exposes request errors. */ }
  });
  return {
    destroy() {
      alive = false;
      generation++;
      stopPolling(); stopLedger?.();
    },
  };
}

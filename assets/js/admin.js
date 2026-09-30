import {imageSource} from './media.js';
import {$, $$, field, text, clone, peso, animate, dismiss} from './dom.js';
import {api} from './api.js';
import {dialog, notice, empty, busy, formError, orderDetails} from './ui.js';

const labels={overview:'Overview',sales:'Sales directory',products:'Products',customers:'Customers',settings:'Settings'};
const transitions={Pending:['Processing','Cancelled'],Processing:['Shipped','Cancelled'],Shipped:['Delivered'],Delivered:['Refunded'],Cancelled:[],Refunded:[]};

export function mountAdmin(page,app) {
  let active='',sales=[],products=[],customers=[],query='',status='All',pageNumber=0,period='week';
  let alive=true,generation=0,backdrop,summary;
  const main=field(page,'admin-view');
  text(page,'admin-name',app.user.name);
  function saleRow(sale,recent=false) {
    const row=clone(recent?'recent-sale':'sale-row');row.dataset.orderId=sale.id;
    for(const key of ['id','customer','email','product',...(recent?[]:['date','payment'])])text(row,key,sale[key]);
    text(row,'amount',peso(sale.amount));text(row,'status',sale.status);field(row,'status').className=`order-status status-${sale.status.toLowerCase()}`;
    return row;
  }
  function renderSales() {
    const filtered=sales.filter(sale=>(status==='All'||sale.status===status)&&`${sale.id} ${sale.customer} ${sale.email} ${sale.product}`.toLowerCase().includes(query.toLowerCase()));
    const recent=active==='overview';
    pageNumber=Math.max(0,Math.min(pageNumber,Math.ceil(filtered.length/10)-1));
    const shown=recent?filtered.slice(0,5):filtered.slice(pageNumber*10,pageNumber*10+10);
    field(main,'sales-rows').replaceChildren(...shown.map(sale=>saleRow(sale,recent)));
    field(main,'sales-empty').hidden=shown.length>0;
    if(!recent){
      text(main,'sales-count',filtered.length?`Showing ${pageNumber*10+1}–${pageNumber*10+shown.length} of ${filtered.length} orders`:'No matching orders');
      $(main,'[data-action="sales-previous"]').disabled=pageNumber===0;
      $(main,'[data-action="sales-next"]').disabled=(pageNumber+1)*10>=filtered.length;
    }
  }
  function renderProducts() {
    const filtered=products.filter(product=>`${product.name} ${product.brand}`.toLowerCase().includes(query.toLowerCase()));
    if(!filtered.length)return empty(field(main,'admin-products'),'No products match your search.');
    field(main,'admin-products').replaceChildren(...filtered.map(product=>{
      const card=clone('admin-product');card.dataset.productId=product.id;
      field(card,'image').src = imageSource(product.image);field(card,'image').alt=product.name;
      text(card,'name',product.name);text(card,'category',`${product.brand} · ${product.category}`);
      text(card,'price',peso(product.price));text(card,'stock',product.active?`${product.stock} in stock`:'Archived');
      $(card,'[data-action="edit-product"]').setAttribute('aria-label',`Edit ${product.name}`);return card;
    }));
  }
  function renderCustomers() {
    const filtered=customers.filter(customer=>`${customer.name} ${customer.email}`.toLowerCase().includes(query.toLowerCase()));
    if(!filtered.length)return empty(field(main,'customers'),'No customers match your search.');
    field(main,'customers').replaceChildren(...filtered.map(customer=>{
      const card=clone('customer');text(card,'initials',customer.name.split(' ').map(part=>part[0]).slice(0,2).join(''));
      text(card,'customer',customer.name);text(card,'email',customer.email);text(card,'order',`${customer.orders} orders`);text(card,'amount',peso(customer.amount));return card;
    }));
  }
  function renderSummary() {
    for(const key of ['gross_revenue','total_orders','new_customers','low_stock_items'])text(main,key,key==='gross_revenue'?peso(summary[key]):summary[key]);
    text(main,'today',new Date().toLocaleDateString('en-PH',{weekday:'long',month:'long',day:'numeric'}));
    text(main,'admin-greeting',`Welcome back, ${app.user.name.split(' ')[0]}.`);
    field(main,'report-period').value=period;
    const chart=field(main,'revenue-chart'),max=Math.max(...summary.chart.map(day=>day.amount),0);
    if(!max)empty(chart,'No delivered revenue in this period.');
    else{
      const ns='http://www.w3.org/2000/svg',svg=document.createElementNS(ns,'svg');
      svg.setAttribute('viewBox','0 0 700 230');svg.setAttribute('role','img');svg.setAttribute('aria-label','Delivered revenue by day');
      const title=document.createElementNS(ns,'title');title.textContent='Daily delivered revenue';svg.append(title);
      const width=700/summary.chart.length;
      summary.chart.forEach((day,index)=>{
        const rect=document.createElementNS(ns,'rect'),height=day.amount/max*185;
        for(const [name,value] of Object.entries({x:index*width+3,y:200-height,width:Math.max(width-6,1),height,rx:4}))rect.setAttribute(name,String(value));
        const title=document.createElementNS(ns,'title');title.textContent=`${day.date}: ${peso(day.amount)}`;rect.append(title);svg.append(rect);
      });
      const caption=document.createElement('p');caption.className='form-hint';caption.textContent=`${summary.chart[0].date} — ${summary.chart.at(-1).date} · Peak ${peso(max)}`;
      chart.replaceChildren(svg,caption);
    }
    const categories=field(main,'category-report'),total=Object.values(summary.categories).reduce((sum,value)=>sum+value,0);
    if(!total)empty(categories,'Category totals appear after delivery.');
    else categories.replaceChildren(...Object.entries(summary.categories).map(([category,value])=>{
      const row=document.createElement('div'),label=document.createElement('p'),meter=document.createElement('meter');
      label.textContent=`${category} · ${Math.round(value/total*100)}%`;meter.min=0;meter.max=total;meter.value=value;meter.setAttribute('aria-label',`${category} revenue`);
      row.append(label,meter);return row;
    }));
  }
  function closeSidebar(){
    const sidebar=$(page,'aside');sidebar.classList.add('-translate-x-full');sidebar.classList.remove('translate-x-0');
    if(backdrop){dismiss(backdrop);backdrop=null;}
  }
  async function navigate(next) {
    if(!alive)return;active=next;query='';status='All';pageNumber=0;const request=++generation;
    main.replaceChildren(clone(next==='products'?'admin-products':next));text(page,'admin-title',labels[next]);
    $$ (page,'aside nav button').forEach(button=>{const selected=button.dataset.action===next;button.setAttribute('aria-current',selected?'page':'false');
      button.className=`flex w-full items-center gap-3 rounded-xl px-3 py-3 text-sm font-medium transition ${selected?'bg-zinc-950 text-white dark:bg-acid dark:text-ink':'text-zinc-500 hover:bg-zinc-100 dark:hover:bg-white/5'}`;});
    closeSidebar();animate(main.firstElementChild);
    try{
      if(next==='overview'){
        const [report,orders]=await Promise.all([api(`/admin/summary?period=${period}`),api('/admin/sales')]);
        if(!alive||request!==generation)return;summary=report;sales=orders.sales;renderSummary();renderSales();text(page,'order-count',sales.length);
      }else if(next==='sales'){
        const data=await api('/admin/sales');if(!alive||request!==generation)return;sales=data.sales;renderSales();
      }else if(next==='products'){
        const data=await api('/admin/products');if(!alive||request!==generation)return;products=data.products;renderProducts();
      }else if(next==='customers'){
        const data=await api('/admin/customers');if(!alive||request!==generation)return;customers=data.customers;renderCustomers();
      }else if(next==='settings'){
        const data=await api('/admin/settings');if(!alive||request!==generation)return;
        const form=main.querySelector('form');for(const [key,value] of Object.entries(data.settings))if(form.elements[key])form.elements[key].value=value;
      }
    }catch(error){
      if(!alive||request!==generation)return;
      if(error.status===401){app.user=null;app.navigate('auth','admin');notice('Your session expired. Please sign in again.');return;}
      const message=document.createElement('p');message.className='form-error';message.textContent=error.message;message.setAttribute('role','alert');main.prepend(message);
    }
  }
  function productEditor(product) {
    const panel=dialog(product?'Edit instrument':'Add an instrument','product-form'),form=panel.querySelector('form');
    if(product)for(const [key,value] of Object.entries(product)){
      if(!form.elements[key])continue;
      if(key==='active')form.elements[key].checked=value;else form.elements[key].value=key==='specs'?value.join('\n'):value;
    }
    const archive=$(form,'[data-action="archive-product"]');archive.hidden=!product?.active;
    archive.addEventListener('click',async()=>{
      archive.disabled=true;
      try{await api(`/admin/products/${product.id}`,{method:'DELETE'});panel.close();notice('Product archived.');if(alive)navigate(active);}
      catch(error){formError(form,error.message);archive.disabled=false;}
    });
    form.addEventListener('submit',async event=>{
      event.preventDefault();if(form.querySelector('[type=submit]').disabled)return;busy(form,true);formError(form,'');
      const values=Object.fromEntries(new FormData(form));values.price=Number(values.price);values.stock=Number(values.stock);values.active=form.elements.active.checked;
      values.specs=values.specs.split('\n').map(item=>item.trim()).filter(Boolean);
      try{await api(product?`/admin/products/${product.id}`:'/admin/products',{method:product?'PUT':'POST',body:values});panel.close();notice('Product saved.');if(alive)navigate(active);}
      catch(error){formError(form,error.message);}finally{busy(form,false,'Save product');}
    });
  }
  function editOrder(order) {
    const panel=orderDetails(order),choices=transitions[order.status]||[];
    if(!choices.length)return;
    const form=clone('order-status');field(panel,'dialog-body').append(form);
    form.elements.status.replaceChildren(...choices.map(status=>new Option(status,status)));
    form.addEventListener('submit',async event=>{
      event.preventDefault();if(form.querySelector('[type=submit]').disabled)return;busy(form,true);formError(form,'');
      try{await api(`/admin/sales/${order.id}`,{method:'PATCH',body:{status:form.elements.status.value}});panel.close();notice('Order updated.');if(alive)navigate(active);}
      catch(error){formError(form,error.message);}finally{busy(form,false,'Update order');}
    });
  }
  page.addEventListener('click',async event=>{
    const button=event.target.closest('[data-action]');if(!button)return;const action=button.dataset.action;
    if(labels[action])navigate(action);
    if(action==='store')app.navigate('storefront');
    if(action==='admin-account')app.navigate('account');
    if(action==='logout')app.logout();
    if(action==='close-sidebar')closeSidebar();
    if(action==='sidebar'){
      const sidebar=$(page,'aside');sidebar.classList.remove('-translate-x-full');sidebar.classList.add('translate-x-0');
      if(!backdrop){backdrop=clone('sidebar-backdrop');page.prepend(backdrop);animate(backdrop);}
    }
    if(action==='add-product')productEditor();
    if(action==='edit-product')productEditor(products.find(product=>product.id===Number(button.closest('[data-product-id]').dataset.productId)));
    if(action==='edit-order')editOrder(sales.find(order=>order.id===button.closest('[data-order-id]').dataset.orderId));
    if(action==='sales-previous'){pageNumber--;renderSales();}
    if(action==='sales-next'){pageNumber++;renderSales();}
    if(action==='export-sales'){
      try{
        const response=await fetch(`/api/admin/sales/export?${new URLSearchParams({q:query,status})}`);
        if(!response.ok)throw new Error('Unable to export sales. Please sign in and try again.');
        const url=URL.createObjectURL(await response.blob()),link=document.createElement('a');link.href=url;link.download='audia-sales.csv';link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
      }catch(error){notice(error.message);}
    }
    if(action==='notifications'){
      const panel=dialog('Store notifications','notifications');
      try{const data=await api('/admin/summary');if(!panel.isConnected)return;
        const alerts=[`${data.pending_orders} orders awaiting processing.`,...data.low_stock.map(product=>`${product.name}: ${product.stock} left in stock.`)];
        field(panel,'alerts').replaceChildren(...alerts.map(message=>{const item=document.createElement('li');item.textContent=message;return item;}));
      }catch(error){empty(field(panel,'alerts'),error.message);}
    }
  });
  page.addEventListener('input',event=>{
    const name=event.target.dataset.field;
    if(name==='sales-query'){query=event.target.value;pageNumber=0;renderSales();}
    if(name==='product-query'){query=event.target.value;renderProducts();}
    if(name==='customer-query'){query=event.target.value;renderCustomers();}
  });
  page.addEventListener('change',event=>{
    if(event.target.dataset.field==='sales-status'){status=event.target.value;pageNumber=0;renderSales();}
    if(event.target.dataset.field==='report-period'){period=event.target.value;navigate('overview');}
  });
  page.addEventListener('submit',async event=>{
    if(event.target.dataset.form!=='settings')return;event.preventDefault();const form=event.target;
    if(form.querySelector('[type=submit]').disabled)return;busy(form,true);formError(form,'');
    try{const data=await api('/admin/settings',{method:'PUT',body:Object.fromEntries(new FormData(form))});if(alive)text(page,'store-name',data.settings.store_name);notice('Store settings saved.');}
    catch(error){formError(form,error.message);}finally{busy(form,false,'Save settings');}
  });
  api('/admin/settings').then(data=>{if(alive)text(page,'store-name',data.settings.store_name);}).catch(()=>{});
  navigate('overview');
  return {destroy(){alive=false;generation++;}};
}

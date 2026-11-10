import { api, field, text, peso, dialog, busy, formError, empty, orderDetails, poll, notice } from '../shared/shared.js';
import { node } from '../shared/order_operations.js';

export async function mountOperations(main, section) {
  const root=main.firstElementChild,form=root.querySelector('form');let page=1,pages=1,loading=false;
  const target=field(root,'operations-rows');
  async function load(){
    if(loading)return;loading=true;field(root,'operations-error').hidden=true;
    try{
      const params=new URLSearchParams({...Object.fromEntries(new FormData(form)),page});
      let rows,count;
      if(section==='refunds'){
        const data=await api('/admin/requests?'+params);rows=data.requests;count=data.count;pages=data.pages;
      }else if(section==='inventory'){
        const data=await api('/admin/inventory/movements?'+params);rows=data.movements;count=data.count;pages=data.pages;
      }else{
        const data=await api('/admin/sales');const q=form.elements.q.value.toLowerCase();
        rows=data.sales.filter(o=>o.channel!=='pos'&&`${o.id} ${o.customer} ${o.product}`.toLowerCase().includes(q));count=rows.length;pages=Math.max(1,Math.ceil(count/20));rows=rows.slice((page-1)*20,page*20);
      }
      if(!root.isConnected)return;
      if(!rows.length)empty(target,'No matching records.');else target.replaceChildren(...rows.map(r=>{
        const card=node('article',undefined,'operations-row');
        if(section==='refunds'){
          card.append(node('strong',`${r.id} · ${r.status}`),node('p',`${r.order_id} · ${r.customer} · ${peso(r.amount)} · ${r.reason}`));
          const button=node('button','Review request','secondary-btn');button.type='button';button.addEventListener('click',()=>void review(r));card.append(button);
        }else if(section==='inventory'){
          card.append(node('strong',`Product #${r.product_id} · ${r.delta>0?'+':''}${r.delta} units · Balance ${r.balance}`),node('p',`${r.reason} · ${r.order_id||'Catalog'} · ${new Date(r.at).toLocaleString()}`));
        }else{
          card.append(node('strong',`${r.id} · ${r.customer}`),node('p',`${r.status} · ${r.payment_status} · ${r.address}`));
          const button=node('button','Manage delivery','secondary-btn');button.type='button';button.addEventListener('click',()=>void deliveryEditor(r,load));
          const detail=node('button','Order details','secondary-btn');detail.type='button';detail.addEventListener('click',()=>orderDetails(r,{customer:false}));card.append(button,detail);
        }
        return card;
      }));
      text(root,'operations-count',`${count} records · Page ${page} of ${pages}`);field(root,'operations-prev').disabled=page<=1;field(root,'operations-next').disabled=page>=pages;
    }catch(e){text(root,'operations-error',e.message);field(root,'operations-error').hidden=false;}finally{loading=false;}
  }
  async function review(r){
    const panel=dialog(`Review ${r.id}`,'review-request'),info=field(panel,'review-info'),form=panel.querySelector('form');
    for(const [label,value] of [['Order',r.order_id],['Customer',r.customer],['Type / status',`${r.kind} · ${r.status}`],['Reason',r.reason],['Explanation',r.explanation||'—'],['Requested',peso(r.amount)],['Approved',r.approved_amount==null?'Awaiting review':peso(r.approved_amount)],['Destination',r.destination]])info.append(node('dt',label),node('dd',value));
    for(const item of r.items)info.append(node('dt','Product'),node('dd',`${item.name} × ${item.quantity}`));
    const orderButton=node('button','Inspect original order','secondary-btn');orderButton.type='button';orderButton.addEventListener('click',async()=>{try{const d=await api('/orders/'+r.order_id);orderDetails(d.order,{customer:false});}catch(e){notice(e.message);}});info.after(orderButton);
    field(panel,'review-events').replaceChildren(...r.events.map(e=>node('li',`${new Date(e.at).toLocaleString()} · ${e.status}: ${e.note}`)));
    for(const url of r.evidence){const link=node('a');link.href=url;link.target='_blank';link.rel='noopener';const img=node('img');img.src=url;img.alt='Customer return evidence';link.append(img);field(panel,'review-evidence').append(link);}
    if(r.confirmation_url){field(panel,'review-confirmation').href=r.confirmation_url;field(panel,'review-confirmation').hidden=false;}
    form.hidden=!r.next_statuses.length;form.elements.status.replaceChildren(...r.next_statuses.map(s=>new Option(s,s)));form.elements.amount.value=r.approved_amount??r.amount;form.elements.amount.max=r.amount;
    function controls(){form.elements.amount.disabled=form.elements.status.value!=='Approved';form.elements.restock.disabled=!(r.status==='Item Received'&&form.elements.status.value==='Refund Processing'&&!r.restocked);}
    controls();form.addEventListener('change',controls);let sending=false;
    form.addEventListener('submit',async event=>{
      event.preventDefault();if(sending)return;sending=true;busy(form,true);formError(form,'');
      try{await api('/admin/requests/'+r.id,{method:'PATCH',body:{status:form.elements.status.value,amount:form.elements.amount.value,note:form.elements.note.value,restock:!form.elements.restock.disabled&&form.elements.restock.checked}});panel.close();notice('Request review saved.');await load();}
      catch(e){formError(form,e.message);}finally{sending=false;busy(form,false,'Save review');}
    });
  }
  form.addEventListener('submit',e=>{e.preventDefault();page=1;void load();});
  field(root,'operations-prev').addEventListener('click',()=>{if(page>1){page--;void load();}});field(root,'operations-next').addEventListener('click',()=>{if(page<pages){page++;void load();}});
  await load();const stop=poll(async()=>{if(!root.isConnected)return stop();await load();});return stop;
}

export async function deliveryEditor(order, reload=()=>{}){
  try{
    const data=await api(`/orders/${order.id}/delivery`),panel=dialog(`Delivery ${order.id}`,'delivery-editor'),form=panel.querySelector('form');
    if(data.delivery){for(const key of ['method','reference','window','note'])form.elements[key].value=data.delivery[key];form.elements.route.value=data.delivery.route.map(p=>p.join(', ')).join('\n');form.elements.progress.value=data.delivery.progress+1;}
    form.elements.status.replaceChildren(new Option(`Keep ${order.status}`,order.status),...(order.next_statuses||[]).filter(s=>!['Cancelled','Rejected','Refunded','Returned'].includes(s)).map(s=>new Option(s,s)));
    let sending=false;form.addEventListener('submit',async event=>{
      event.preventDefault();if(sending)return;sending=true;busy(form,true);formError(form,'');
      try{
        const values=Object.fromEntries(new FormData(form));const route=values.route.trim().split('\n').map(line=>line.split(',').map(v=>Number(v.trim())));
        await api(`/admin/orders/${order.id}/delivery`,{method:'PUT',body:{...values,route,progress:Number(values.progress)-1,expected_status:order.status}});panel.close();notice('Delivery update saved.');await reload();
      }catch(e){formError(form,e.message);}finally{sending=false;busy(form,false,'Save delivery update');}
    });
  }catch(e){notice(e.message);}
}

export async function customerProfile(id){
  try{
    const data=await api('/admin/customers/'+id),panel=dialog(data.customer.name),body=field(panel,'dialog-body');
    body.append(node('p',`${data.customer.email} · ${data.customer.phone||'No phone'} · ${data.customer.address||'No address'}`,'form-hint'));
    const form=node('form',undefined,'stack-form');const label=node('label','Account access'),select=node('select');select.name='suspended';select.append(new Option('Active','false'),new Option('Suspended','true'));select.value=String(data.suspended);label.append(select);
    const reason=node('input');reason.name='reason';reason.required=true;reason.minLength=3;reason.maxLength=200;reason.placeholder='Reason for account status change';reason.setAttribute('aria-label','Account status reason');reason.value=data.reason;
    const error=node('p',undefined,'form-error');error.dataset.field='form-error';error.hidden=true;error.setAttribute('role','alert');const save=node('button','Save account status','primary-btn');save.type='submit';form.append(label,reason,error,save);body.append(form);
    form.addEventListener('submit',async e=>{e.preventDefault();busy(form,true);try{await api(`/admin/customers/${id}/status`,{method:'PUT',body:{suspended:select.value==='true',reason:reason.value}});notice('Account access updated.');panel.close();}catch(e){formError(form,e.message);}finally{busy(form,false,'Save account status');}});
    body.append(node('h3','Order and transaction history'));
    if(!data.orders.length)body.append(node('p','No orders yet.','empty-state'));
    for(const order of data.orders){const b=node('button',`${order.id} · ${order.status} · ${order.payment_status} · ${peso(order.amount)}`,'secondary-btn');b.type='button';b.addEventListener('click',()=>orderDetails(order,{customer:false}));body.append(b);}
    body.append(node('h3','Cancellation and refund requests'));
    for(const r of data.requests)body.append(node('p',`${r.id} · ${r.status} · ${r.reason}`));
  }catch(e){notice(e.message);}
}

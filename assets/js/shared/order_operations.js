import { api, dialog, field, text, busy, formError, peso, empty } from './shared.js';

export const node=(tag,value,cls)=>{const n=document.createElement(tag);if(value!==undefined)n.textContent=value;if(cls)n.className=cls;return n;};

export async function customerRequest(order, cancellation=false) {
  const panel=dialog(cancellation?'Cancel order':'Return / Refund','customer-request'),form=panel.querySelector('form');
  const key=crypto.randomUUID();let sending=false,uploaded=[];
  text(form,'request-summary',`${order.id} · ${order.status} · ${order.product} · Total ${peso(order.amount)}`);
  field(form,'evidence-input').hidden=cancellation;
  const reasons=cancellation?['Ordered the wrong item','Changed my mind','Incorrect shipping address','Found a better option','Delivery is taking too long','Other reason']:['Received damaged product','Received wrong item','Missing item','Product does not match description','Defective product','Package not received','Other eligible reason'];
  form.elements.reason.replaceChildren(...reasons.map(r=>new Option(r,r)));
  if(!cancellation) for(const item of order.items) {
    const label=node('label',`${item.name} · ${peso(item.price)} per unit`),input=node('input');
    input.type='number';input.min=0;input.max=item.quantity;input.value=0;input.dataset.itemId=item.id;
    input.setAttribute('aria-label',`Quantity to refund: ${item.name}`);label.append(input);field(form,'request-products').append(label);
  }
  try{const {store}=await api('/store');text(form,'request-policy',cancellation?store.cancellation_policy:store.return_policy);}catch(error){text(form,'request-policy',error.message);}
  form.addEventListener('submit',async event=>{
    event.preventDefault();if(sending)return;
    const items=[...form.querySelectorAll('[data-item-id]')].filter(i=>Number(i.value)>0).map(i=>({item_id:Number(i.dataset.itemId),quantity:Number(i.value)}));
    if(!cancellation&&!items.length)return formError(form,'Select at least one product quantity.');
    const files=[...form.elements.evidence.files];
    if(files.length>4)return formError(form,'Attach up to four images.');
    sending=true;busy(form,true);formError(form,'');
    try{
      for(let i=uploaded.length;i<files.length;i++){const body=new FormData();body.set('purpose','evidence');body.set('image',files[i]);uploaded.push((await api('/uploads',{method:'POST',body})).id);}
      const body={request_key:key,reason:form.elements.reason.value,explanation:form.elements.explanation.value,items,evidence:uploaded};
      await api(`/orders/${order.id}/${cancellation?'cancel':'requests'}`,{method:'POST',body});
      panel.close();panel.dispatchEvent(new Event('request-submitted'));
    }catch(error){formError(form,error.message);}finally{sending=false;busy(form,false,'Submit request');}
  });
  form.elements.evidence.addEventListener('change',()=>{uploaded=[];});
  return panel;
}

export async function loadRequestHistory(panel, order) {
  const target=field(panel,'request-history');
  try{
    const data=await api(`/orders/${order.id}/requests`);if(!panel.isConnected)return;
    if(!data.requests.length)return empty(target,'No cancellation or refund requests.');
    target.replaceChildren(...data.requests.map(r=>{
      const card=node('article',undefined,'request-card');card.append(node('strong',`${r.kind==='cancellation'?'Cancellation':'Return / Refund'} · ${r.status}`),node('p',`${r.id} · ${peso(r.amount)} requested · ${r.reason}`),node('p',`Destination: ${r.destination}`));
      for(const e of r.events)card.append(node('small',`${new Date(e.at).toLocaleString()} · ${e.status}: ${e.note}`));
      if(r.confirmation_url){const link=node('a','View refund confirmation');link.href=r.confirmation_url;link.target='_blank';link.rel='noopener';card.append(link);}
      if(['Requested','Under Review'].includes(r.status) && document.body.dataset.page!=='dashboard'){
        const form=node('form',undefined,'stack-form'),input=node('textarea');input.name='note';input.required=true;input.minLength=3;input.maxLength=300;input.placeholder='Additional information for the store';input.setAttribute('aria-label','Additional request information');
        const error=node('p',undefined,'form-error');error.dataset.field='form-error';error.hidden=true;const send=node('button','Send information','secondary-btn');send.type='submit';form.append(input,error,send);
        form.addEventListener('submit',async e=>{e.preventDefault();busy(form,true);try{await api(`/orders/${order.id}/requests/${r.id}/reply`,{method:'POST',body:{note:input.value}});await loadRequestHistory(panel,order);}catch(e){formError(form,e.message);}finally{busy(form,false,'Send information');}});card.append(form);
      }
      return card;
    }));
  }catch(error){empty(target,error.message+' Reopen this order to retry.');}
}

let leafletPromise, googlePromise;
function googleMaps(key){
  googlePromise ||= new Promise((resolve,reject)=>{
    const timer=setTimeout(()=>reject(new Error('Google Maps timed out.')),12000);
    window.audiaGoogleReady=()=>{clearTimeout(timer);resolve();};
    window.gm_authFailure=()=>{clearTimeout(timer);reject(new Error('Google Maps authorization failed.'));window.dispatchEvent(new Event('audia:map-auth-error'));};
    void script('https://maps.googleapis.com/maps/api/js?key='+encodeURIComponent(key)+'&loading=async&libraries=marker&callback=audiaGoogleReady').catch(e=>{clearTimeout(timer);reject(e);});
  }).catch(e=>{googlePromise=null;throw e;});
  return googlePromise;
}
function script(url){return new Promise((resolve,reject)=>{const s=document.createElement('script');s.src=url;s.onload=resolve;s.onerror=()=>reject(new Error('Map library could not load.'));document.head.append(s);setTimeout(()=>reject(new Error('Map loading timed out.')),12000);});}
async function leaflet(){
  if(!leafletPromise){const css=node('link');css.rel='stylesheet';css.href='/static/vendor/leaflet/leaflet.css';document.head.append(css);leafletPromise=script('/static/vendor/leaflet/leaflet.js').catch(e=>{leafletPromise=null;throw e;});}
  await leafletPromise;return window.L;
}

export function mountDelivery(panel, order) {
  let map, snapshot='', opened=false, google=false, googleFailed=false;
  const container=field(panel,'delivery-map'),error=field(panel,'delivery-map-error'),button=field(panel,'show-delivery-map');
  async function refresh(){
    try{
      const data=await api(`/orders/${order.id}/delivery`);if(!panel.isConnected)return;
      const d=data.delivery;
      text(panel,'delivery-summary',d?`${d.method} · ${d.reference} · ${d.window||'Delivery window not assigned'} · ${d.note} · Simulated route progress ${d.progress+1}/${d.route.length}. This is not real courier GPS.`:'A delivery route has not been assigned. Your shipping address is recorded above; the store will update tracking here.');
      button.hidden=!d;
      if(!opened||!d)return;
      const signature=JSON.stringify(data);if(snapshot===signature)return;snapshot=signature;
      container.hidden=false;error.textContent='';
      if(map&&!google)map.remove();map=null;container.replaceChildren();google=false;
      const points=d.route;
      if(data.map_provider==='google'&&data.google_maps_key&&!googleFailed){
        try{
          await googleMaps(data.google_maps_key);
          if(!window.google?.maps?.Map)throw new Error('Google Maps unavailable.');
          const G=window.google.maps;map=new G.Map(container,{center:{lat:points[0][0],lng:points[0][1]},zoom:12,mapId:'DEMO_MAP_ID'});google=true;
          const bounds=new G.LatLngBounds();points.forEach(([lat,lng])=>bounds.extend({lat,lng}));map.fitBounds(bounds);
          new G.Polyline({path:points.map(([lat,lng])=>({lat,lng})),map,strokeColor:'#7c3aed'});
          for(const [i,title] of [[0,'Dispatch'],[points.length-1,'Destination'],[d.progress,'Simulated progress']])new G.marker.AdvancedMarkerElement({map,position:{lat:points[i][0],lng:points[i][1]},title});
          return;
        }catch{googleFailed=true;google=false;error.textContent='Google Maps is unavailable. Showing the Leaflet map.';container.replaceChildren();}
      }
      const L=await leaflet();if(!panel.isConnected)return;
      map=L.map(container,{scrollWheelZoom:false}).fitBounds(points,{padding:[28,28]});
      const tiles=L.tileLayer(data.map_tile_url,{maxZoom:19,attribution:'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>'}).addTo(map);
      tiles.on('tileerror',()=>{error.textContent='Map tiles are unavailable. The stored simulated route and markers remain visible. Use Retry map to reload.';});
      L.polyline(points,{color:'#7c3aed',weight:4}).addTo(map);
      L.circleMarker(points[0],{radius:8,color:'#6366f1'}).addTo(map).bindPopup('Store / dispatch');
      L.circleMarker(points.at(-1),{radius:8,color:'#16a34a'}).addTo(map).bindPopup('Delivery destination');
      L.circleMarker(points[d.progress],{radius:11,color:'#db2777'}).addTo(map).bindPopup('Simulated delivery progress — not live GPS').openPopup();
      requestAnimationFrame(()=>map.invalidateSize());
    }catch(e){error.textContent=e.message+' Use Retry map to try again.';snapshot='';}
  }
  button.addEventListener('click',()=>{opened=true;snapshot='';button.textContent='Retry map';void refresh();});
  const failed=()=>{if(google&&panel.isConnected){googleFailed=true;snapshot='';void refresh();}};
  window.addEventListener('audia:map-auth-error',failed);
  panel.addEventListener('close',()=>{if(map&&!google)map.remove();window.removeEventListener('audia:map-auth-error',failed);},{once:true});
  void refresh();return refresh;
}

// Deterministic dynamic-component visual/style contract. Uses only disposable data.
const {chromium}=require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const phase=process.env.FRONTEND_PHASE || 'after';
const base=process.env.AUDIA_BASE_URL || 'http://127.0.0.1:5056';
const output='test-results/frontend/dynamic';
const properties=['display','position','top','right','bottom','left','width','height','max-width','min-width','max-height','min-height','grid-template-columns','flex-direction','flex-grow','align-items','justify-content','gap','margin-top','margin-right','margin-bottom','margin-left','padding-top','padding-right','padding-bottom','padding-left','font-family','font-size','font-weight','line-height','letter-spacing','color','background-color','background-image','border-top-width','border-right-width','border-bottom-width','border-left-width','border-top-color','border-radius','box-shadow','opacity','transform','overflow-x','overflow-y','text-align','white-space','object-fit','transition-property','transition-duration'];
(async()=>{
 const browser=await chromium.launch({headless:true});
 try {
  fs.mkdirSync(path.join(output,phase),{recursive:true});
  const customer=await browser.newContext({viewport:{width:1440,height:1000},reducedMotion:'reduce'});
  let csrf=(await(await customer.request.get(base+'/api/auth/session')).json()).csrf_token;
  await customer.request.post(base+'/api/auth/register',{headers:{'X-CSRF-Token':csrf},data:{name:'Frontend Player',email:'frontend@example.com',password:'frontend-password-123'}});
  csrf=(await(await customer.request.get(base+'/api/auth/session')).json()).csrf_token;
  const login=await customer.request.post(base+'/api/auth/login',{headers:{'X-CSRF-Token':csrf},data:{email:'frontend@example.com',password:'frontend-password-123',role:'customer'}});
  assert.equal(login.status(),200);
  const admin=await browser.newContext({viewport:{width:1440,height:1000},reducedMotion:'reduce'});
  const adminCsrf=(await(await admin.request.get(base+'/api/auth/session')).json()).csrf_token;
  assert.equal((await admin.request.post(base+'/api/auth/login',{headers:{'X-CSRF-Token':adminCsrf},data:{email:'admin@example.com',password:'admin-password-123',role:'admin'}})).status(),200);
  const fixturePath=path.join(output,'api-fixtures.json');
  let fixture={};
  if(phase==='before'&&!process.env.FRONTEND_CAPTURE_REFERENCE) {
   const session=(await(await customer.request.get(base+'/api/auth/session')).json());
   const order=await customer.request.post(base+'/api/orders',{headers:{'X-CSRF-Token':session.csrf_token},data:{request_key:'frontend-visual-fixture-2026',address:'123 Frontend Street, Manila',phone:'09171234567',items:[{product_id:1,quantity:1}]}});
   assert.ok([200,201].includes(order.status()));
   for(const [context,urls] of [[customer,['/api/products','/api/orders','/api/account/saved']],[admin,['/api/admin/summary?period=week','/api/admin/sales','/api/admin/products','/api/admin/customers','/api/admin/settings']]]) {
    for(const url of urls) {const response=await context.request.get(base+url);assert.equal(response.status(),200);fixture[url]=await response.json();}
   }
   fs.writeFileSync(fixturePath,JSON.stringify(fixture,null,2));
  } else fixture=JSON.parse(fs.readFileSync(fixturePath,'utf8'));
  for(const context of [customer,admin]) await context.route('**/api/**',route=>{
   const url=new URL(route.request().url()),key=url.pathname+url.search;
   if(route.request().method()==='GET'&&fixture[key])return route.fulfill({status:200,contentType:'application/json',body:JSON.stringify(fixture[key])});
   if(url.pathname==='/api/chat')return route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({answer:'Practice slowly. Choose a guitar within your budget.'})});
   return route.continue();
  });
  const errors=[],differences=[];let count=0;
  const page=await customer.newPage(),adminPage=await admin.newPage();
  for(const p of [page,adminPage])p.on('pageerror',e=>errors.push(e.message));
  async function ready(p){await p.locator('#root:not([inert])').waitFor();await p.evaluate(()=>document.fonts.ready);}
  async function record(p,name){
   const selected=process.env.FRONTEND_CASES?.split(',');
   const complete=phase==='before'&&!process.env.FRONTEND_CAPTURE_REFERENCE&&['dark','light'].every(t=>[375,1440].every(w=>fs.existsSync(path.join(output,'before',`${name}-${t}-${w}.json`))));
   if(complete||(selected&&!selected.includes(name))){await p.evaluate(()=>{document.documentElement.classList.remove('dark');localStorage.setItem('audia-theme','light');});await p.setViewportSize({width:1440,height:1000});return;}
   for(const theme of ['dark','light']) {
    await p.evaluate(theme=>{document.documentElement.classList.toggle('dark',theme==='dark');localStorage.setItem('audia-theme',theme);},theme);
    for(const width of [375,1440]) {
     await p.setViewportSize({width,height:1000});await p.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
     await p.waitForFunction(width=>innerWidth===width&&matchMedia('(min-width: 1024px)').matches===(width>=1024),width);
     await p.waitForTimeout(150);
     await p.locator('img').evaluateAll(nodes=>Promise.all(nodes.filter(n=>n.getClientRects().length).map(n=>{n.loading='eager';return n.decode().catch(()=>{});})));
     const key=`${name}-${theme}-${width}`;
     // Paint and settle finite transitions before reading inherited styles.
     // Dynamic panels need viewport captures; full page baselines are separate.
     await p.screenshot({path:path.join(output,phase,key+'.png'),fullPage:false,animations:'disabled'});
     const data=await p.evaluate(properties=>{
      const result=[];
      function walk(node,key){
       const css=getComputedStyle(node),box=node.getBoundingClientRect();
       if(box.width&&box.height&&css.visibility!=='hidden')result.push({key,tag:node.tagName,classes:node.getAttribute('class')||'',styles:Object.fromEntries(properties.map(p=>[p,css.getPropertyValue(p)])),box:[box.x,box.y,box.width,box.height]});
       [...node.children].forEach((child,index)=>{if(child.tagName!=='TEMPLATE')walk(child,key+'.'+index);});
      }
      [...document.body.children].forEach((node,index)=>{if(node.id==='root'||node.matches('dialog[open]'))walk(node,''+index);});
      return result;
     },properties);
     fs.writeFileSync(path.join(output,phase,key+'.json'),JSON.stringify(data,null,2));
     if(phase==='after') {
      const original=JSON.parse(fs.readFileSync(path.join(output,'before',key+'.json'),'utf8'));
      const current=new Map(data.map(n=>[n.key,n]));
      // Native dialogs make the background inert. Its CSS recalculation can be
      // deferred when this recorder switches themes; compare the active dialog.
      // The same background components are independently captured in their page cases.
      const dialogKey=await p.locator('dialog[open]').count()?data.find(n=>n.tag==='DIALOG')?.key:null;
      const customPanel=data.find(n=>n.classes.split(' ').some(c=>['finder-modal','cart-panel','chat-panel'].includes(c)));
      const activeKey=dialogKey || (customPanel ? (customPanel.classes.includes('chat-panel')?customPanel.key:customPanel.key.split('.').slice(0,-1).join('.')) : null);
      for(const node of original){
       if(activeKey&&node.key!==activeKey&&!node.key.startsWith(activeKey+'.'))continue;
       const other=current.get(node.key);if(!other){differences.push({case:key,key:node.key,missing:true,originalClasses:node.classes});continue;}
       for(const prop of properties)if(node.styles[prop]!==other.styles[prop])differences.push({case:key,key:node.key,classes:other.classes,originalClasses:node.classes,property:prop,before:node.styles[prop],after:other.styles[prop]});
      }
     }
     count++;
    }
   }
  }
  await page.goto(base+'/shop');await ready(page);await page.locator('.product-card').first().waitFor();
  await record(page,'catalog');
  await page.getByRole('button',{name:'Add ELECTRIC_001 to cart',exact:true}).click();await page.locator('.cart-panel').waitFor();await record(page,'cart');
  await page.getByRole('button',{name:'Proceed to checkout',exact:true}).click();await page.locator('[data-form=checkout]').waitFor();await record(page,'checkout');
  await page.getByRole('button',{name:'Close dialog',exact:true}).click();await page.getByRole('button',{name:'Close cart',exact:true}).click();
  await page.getByRole('button',{name:'Start guitar finder',exact:true}).click();await page.locator('.finder-modal').waitFor();await record(page,'finder-budget');
  await page.getByRole('button',{name:'Continue',exact:false}).click();await record(page,'finder-options');
  await page.getByRole('button',{name:'Continue',exact:false}).click();await page.getByRole('button',{name:'Continue',exact:false}).click();await page.getByRole('button',{name:'Show my matches',exact:false}).click();await page.locator('[data-field=matches] img').first().waitFor();await record(page,'finder-results');
  await page.goto(base+'/account');await ready(page);await page.locator('.account-order').waitFor();await record(page,'account-orders');await page.getByRole('button',{name:'View order',exact:true}).first().click();await page.locator('.order-detail').waitFor();await record(page,'order-details');
  await page.goto(base+'/tuner');await ready(page);await page.getByRole('button',{name:'Open customer support',exact:true}).click();await page.getByRole('textbox',{name:'Your message'}).fill('Help me choose a guitar');await page.getByRole('button',{name:'Send message',exact:true}).click();await page.getByText('Practice slowly. Choose a guitar within your budget.',{exact:true}).waitFor();await record(page,'chat');
  await adminPage.goto(base+'/admin');await ready(adminPage);await adminPage.waitForFunction(()=>document.querySelector('[data-field=total_orders]')?.textContent==='1');await record(adminPage,'admin-overview');
  await adminPage.locator('aside nav').getByRole('button',{name:'Products',exact:true}).click();await adminPage.getByRole('button',{name:'Edit ELECTRIC_001',exact:true}).waitFor();await record(adminPage,'admin-products');await adminPage.getByRole('button',{name:'Edit ELECTRIC_001',exact:true}).click();await adminPage.locator('[data-form=product]').waitFor();await record(adminPage,'admin-product-editor');await adminPage.getByRole('button',{name:'Close dialog',exact:true}).click();
  for(const [label,name,wait] of [['Sales directory','admin-sales','tbody tr'],['Customers','admin-customers','[data-field=customers]'],['Settings','admin-settings','[data-form=settings]']]){
   await (label==='Settings'?adminPage:adminPage.locator('aside nav')).getByRole('button',{name:label,exact:false}).click();await adminPage.locator(wait).waitFor();await record(adminPage,name);
  }
  await adminPage.getByRole('button',{name:'Notifications',exact:true}).click();await adminPage.locator('.notification-list').waitFor();await record(adminPage,'admin-notifications');
  const guest=await browser.newContext({viewport:{width:1440,height:1000},reducedMotion:'reduce'});
  const authPage=await guest.newPage();authPage.on('pageerror',e=>errors.push(e.message));
  await authPage.goto(base+'/login');await ready(authPage);await record(authPage,'auth-login');
  await authPage.getByRole('button',{name:'Administrator',exact:true}).click();await record(authPage,'auth-admin');
  await authPage.getByRole('button',{name:'Customer',exact:true}).click();await authPage.getByRole('button',{name:'Forgot password?',exact:true}).click();await record(authPage,'auth-recovery');
  await authPage.goto(base+'/register');await ready(authPage);await record(authPage,'auth-register');
  await authPage.goto(base+'/reset-password');await ready(authPage);await record(authPage,'auth-reset');
  fs.writeFileSync(path.join(output,'differences.json'),JSON.stringify(differences,null,2));
  assert.deepEqual(errors,[]);
  if(phase==='after')assert.equal(differences.length,0,'Dynamic component styles differ; inspect test-results/frontend/dynamic/differences.json');
  console.log(`Captured ${count} ${phase} dynamic component cases; ${differences.length} computed-style differences. See test-results/frontend/dynamic/differences.json.`);
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});

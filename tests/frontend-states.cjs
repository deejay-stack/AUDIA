// Compare focus, hover, sidebar and normal-motion presentation against the
// untouched frontend reference. Both servers must use disposable fixture data.
const {chromium}=require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const base=process.env.AUDIA_BASE_URL || 'http://127.0.0.1:5056';
const phase=process.env.FRONTEND_PHASE || 'after';
const output='test-results/frontend/states';
const fixture=JSON.parse(fs.readFileSync('test-results/frontend/dynamic/api-fixtures.json','utf8'));
const properties=Object.keys(JSON.parse(fs.readFileSync('test-results/frontend/dynamic/before/catalog-dark-375.json','utf8'))[0].styles);
(async()=>{
 const browser=await chromium.launch({headless:true});
 try {
  fs.mkdirSync(path.join(output,phase),{recursive:true});
  const contexts={};const errors=[];let count=0;
  for(const role of ['guest','customer','admin','motion']){
   const context=await browser.newContext({reducedMotion:role==='motion'?'no-preference':'reduce'});
   const csrf=(await(await context.request.get(base+'/api/auth/session')).json()).csrf_token;
   if(['customer','motion'].includes(role))await context.request.post(base+'/api/auth/register',{headers:{'X-CSRF-Token':csrf},data:{name:'Frontend Player',email:'frontend@example.com',password:'frontend-password-123'}});
   if(role!=='guest'){
    const token=(await(await context.request.get(base+'/api/auth/session')).json()).csrf_token;
    const admin=role==='admin';
    assert.equal((await context.request.post(base+'/api/auth/login',{headers:{'X-CSRF-Token':token},data:{email:admin?'admin@example.com':'frontend@example.com',password:admin?'admin-password-123':'frontend-password-123',role:admin?'admin':'customer'}})).status(),200);
   }
   await context.route('**/api/**',route=>{
    const url=new URL(route.request().url()),key=url.pathname+url.search;
    if(route.request().method()==='GET'&&fixture[key])return route.fulfill({json:fixture[key]});
    return route.continue();
   });
   contexts[role]=context;
  }
  const cases=[
   {name:'catalog-focus-hover',role:'customer',route:'/shop',targets:['[data-field=search]','.product-card'],setup:async p=>{
    await p.locator('.product-card').first().waitFor();await p.locator('[data-field=search]').focus();await p.locator('.product-card').first().hover();
   }},
   {name:'auth-focus-hover',role:'guest',route:'/login',targets:['[data-field=email]','[data-action=forgot]'],setup:async p=>{
    await p.locator('[data-field=email]').focus();await p.locator('[data-action=forgot]').hover();
   }},
   {name:'chat-focus-hover',role:'customer',route:'/tuner',targets:['.chat-panel','[data-field=chat-input]'],setup:async p=>{
    await p.getByRole('button',{name:'Open customer support',exact:true}).click();await p.getByRole('textbox',{name:'Your message'}).focus();await p.locator('[data-action=chat-suggestion]').first().hover();
   }},
   {name:'admin-sidebar-open-hover',role:'admin',route:'/admin',targets:['aside'],setup:async(p,width)=>{
    if(width<1024)await p.locator('[data-action=sidebar]').click();await p.locator('aside nav [data-action=products]').hover();
   }},
   {name:'normal-catalog-reveals',role:'motion',route:'/shop',targets:['.hero-copy','.product-card'],setup:async p=>{
    await p.locator('.product-card').first().waitFor();await p.locator('.product-card').first().scrollIntoViewIfNeeded();await p.waitForTimeout(1200);
   }},
  ];
  for(const item of cases)for(const theme of ['dark','light'])for(const width of [375,1440]){
   const page=await contexts[item.role].newPage();page.on('pageerror',e=>errors.push(e.message));
   await page.setViewportSize({width,height:1000});
   await page.addInitScript(theme=>localStorage.setItem('audia-theme',theme),theme);
   await page.goto(base+item.route);await page.locator('#root:not([inert])').waitFor();await page.evaluate(()=>document.fonts.ready);
   await page.waitForTimeout(150);await item.setup(page,width);await page.waitForTimeout(300);
   const key=`${item.name}-${theme}-${width}`;
   await page.screenshot({path:path.join(output,phase,key+'.png'),animations:'disabled'});
   const nodes=[];
   for(const [index,selector] of item.targets.entries()){
    const target=page.locator(selector).first();assert.equal(await target.count(),1,selector);
    nodes.push(...await target.evaluate((root,{properties,index})=>{
     const result=[];
     function walk(node,key){
      const css=getComputedStyle(node);result.push({key,styles:Object.fromEntries(properties.map(p=>[p,css.getPropertyValue(p)]))});
      [...node.children].forEach((child,i)=>walk(child,key+'.'+i));
     }
     walk(root,''+index);return result;
    },{properties,index}));
   }
   fs.writeFileSync(path.join(output,phase,key+'.json'),JSON.stringify(nodes,null,2));
   if(phase==='after')assert.deepEqual(nodes,JSON.parse(fs.readFileSync(path.join(output,'before',key+'.json'),'utf8')),key);
   await page.close();count++;
  }
  assert.deepEqual(errors,[]);
  console.log(`PASS: ${count} ${phase} hover/focus/sidebar/normal-motion style cases, both themes and mobile/desktop.`);
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});

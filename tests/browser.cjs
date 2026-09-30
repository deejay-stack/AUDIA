// Run against `python tests/serve.py`, never against a real customer database.
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const base=process.env.AUDIA_BASE_URL||'http://127.0.0.1:5056';
(async()=>{
  const browser=await chromium.launch({headless:true});
  try{
    const page=await browser.newPage({viewport:{width:1440,height:1000},reducedMotion:'reduce'});
    const errors=[];page.on('pageerror',error=>errors.push(error.message));
    const button=(name,root=page)=>root.getByRole('button',{name,exact:true});
    const email=`player-${Date.now()}@example.com`,password='player-password-123';
    async function fits(label){
      for(const width of [320,390,768,1440]){
        await page.setViewportSize({width,height:1000});
        await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
        await page.waitForFunction(()=>document.documentElement.scrollWidth<=innerWidth,{},{timeout:2000});
        const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth);
        assert.equal(overflow,false,`${label} overflows at ${width}`);
        if(await page.locator('.admin-page').count() && !await page.locator('dialog[open]').count()) {
          await page.waitForFunction(expected=>{
            const shell=document.querySelector('.admin-page > div');
            return shell && parseInt(getComputedStyle(shell).paddingLeft)===expected;
          },width>=1024?270:0,{timeout:2000});
          const padding=await page.locator('.admin-page > div').evaluate(el=>parseInt(getComputedStyle(el).paddingLeft));
          assert.equal(padding,width>=1024?270:0,`${label} sidebar spacing at ${width}`);
        }
      }
    }
    async function capture(name){
      if(process.env.SCREENSHOT_DIR){fs.mkdirSync(process.env.SCREENSHOT_DIR,{recursive:true});await page.screenshot({path:`${process.env.SCREENSHOT_DIR}/${name}.png`,fullPage:true});}
    }
    const catalogRequests=[];
    page.on('request',request=>{if(new URL(request.url()).pathname==='/api/products')catalogRequests.push(request.url());});
    await page.goto(base);await page.locator('.landing-page').waitFor();
    assert.equal(await page.locator('.product-card').count(),0);
    assert.equal(await button('Open cart').count(),0);
    assert.equal(await page.locator('#shop').count(),0);
    assert.equal((await page.request.get(base+'/api/products')).status(),401);
    await page.locator('.landing-page img').evaluateAll(images=>Promise.all(images.map(image=>{image.loading='eager';return image.decode();})));
    assert.deepEqual(await page.locator('.landing-page img').evaluateAll(images=>images.filter(image=>image.dataset.fallback||!image.naturalWidth).map(image=>image.src)),[]);
    await fits('landing dark');await capture('landing-dark');
    await button('Switch to light mode').click();await fits('landing light');await capture('landing-light');
    assert.deepEqual(catalogRequests,[],'The landing page must not request the full catalog');
    await button('Explore electric guitars').click();await page.locator('.auth-page').waitFor();
    await button('Back to store').click();await page.locator('.landing-page').waitFor();
    await page.goto(base+'/#storefront');await page.locator('.auth-page').waitFor();
    assert.equal(await page.locator('.product-card').count(),0);
    await button('Back to store').click();await button('Create an account').click();
    await fits('registration');await capture('registration');
    await page.locator('[data-field=name]').fill('Browser Player');await page.locator('[data-field=email]').fill(email);
    await page.locator('[data-field=password]').fill(password);await page.locator('[data-field=confirm]').fill(password);
    await button('Create account').click();await page.locator('.storefront').waitFor();
    await page.locator('.product-card').first().waitFor();
    assert.equal(await page.locator('.product-card').count(),42);
    await fits('storefront light');await capture('storefront');
    await page.locator('.category-card img').evaluateAll(images=>Promise.all(images.map(image=>image.decode())));
    assert.deepEqual(await page.locator('.category-card img').evaluateAll(images=>images.filter(image=>image.dataset.fallback||!image.naturalWidth).map(image=>image.src)),[]);
    await page.getByPlaceholder('Search guitars or brands').fill('ACOUSTIC_001');assert.equal(await page.locator('.product-card').count(),1);
    await page.getByPlaceholder('Search guitars or brands').fill('');
    await button('Find my guitar').click();
    for(let i=0;i<3;i++)await button('Continue').click();
    await button('Show my matches').click();await page.getByText('Your closest matches.').waitFor();
    await button('Close finder').click({position:{x:10,y:10}});
    await button('Open customer support').click();await button('I am a beginner').click();await page.getByText(/For a beginner, prioritize comfort/).waitFor();await button('Open customer support').click();
    await page.reload();await button('Open account').waitFor();
    await button('Save guitar').first().click();
    await button('Add ELECTRIC_001 to cart').click();await button('Proceed to checkout').click();
    const checkout=page.locator('dialog');await checkout.locator('[name=address]').fill('123 Guitar Street, Quezon City');await checkout.locator('[name=phone]').fill('09171234567');await fits('checkout');await capture('checkout');
    await button('Place order').click();await page.locator('.order-detail').waitFor();
    const orderId=(await page.locator('dialog[open] [data-field=dialog-title]').innerText()).replace('Order ','');
    assert.match(await page.locator('.order-detail').innerText(),/12,990/);
    await button('Close dialog').click();await button('Open account').click();await page.locator('.account-page').waitFor();
    await page.locator('.account-order').waitFor();await page.locator('.saved-item').waitFor();await fits('account');await capture('account');
    const profile=page.locator('[data-form=profile]');await profile.locator('[name=address]').fill('456 Updated Street, Quezon City');await button('Save profile').click();await page.getByText('Profile saved.',{exact:true}).waitFor();
    await button('Sign out').click();await button('Sign in').click();
    await page.locator('[data-field=email]').fill(email);await page.locator('[data-field=password]').fill('incorrect');await button('Sign in').click();await page.getByText('Incorrect email or password.',{exact:true}).waitFor();
    // An API failure must not grant access.
    await page.route('**/api/auth/login',route=>route.abort());await page.locator('[data-field=password]').fill(password);await button('Sign in').click();await page.getByText(/Unable to reach AUDIA/).waitFor();assert.equal(await page.locator('.auth-page').count(),1);await page.unroute('**/api/auth/login');
    await button('Forgot password?').click();await button('Send reset link').click();await page.getByText(/If an account exists/).waitFor();await button('Back to sign in').click();
    await button('Administrator').click();await page.locator('[data-field=email]').fill('admin@example.com');await page.locator('[data-field=password]').fill('admin-password-123');await button('Open dashboard').click();
    await page.locator('.admin-page').waitFor();await page.locator('[data-field=total_orders]').filter({hasText:'1'}).waitFor();await fits('admin overview');await capture('overview');
    await button('Add product').click();const form=page.locator('[data-form=product]');
    await form.locator('[name=name]').fill('Browser Test Guitar');await form.locator('[name=brand]').fill('AUDIA');await form.locator('[name=price]').fill('9999');await form.locator('[name=stock]').fill('3');await form.locator('[name=image]').fill('/static/images/electric/Amber_Flame.png');await form.locator('[name=description]').fill('A test guitar for browser integration checks.');await fits('product editor');await button('Save product').click();await page.getByText('Product saved.',{exact:true}).waitFor();
    await page.locator('aside nav').getByRole('button',{name:'Products',exact:true}).click();await button('Edit Browser Test Guitar').waitFor();await fits('products');await capture('products');
    await button('Edit Browser Test Guitar').click();await page.locator('[name=stock]').fill('5');await button('Save product').click();await page.locator('article').filter({has:button('Edit Browser Test Guitar')}).getByText('5 in stock',{exact:true}).waitFor();
    await page.locator('aside nav').getByRole('button',{name:'Sales directory'}).click();await page.locator('tbody tr').waitFor();await fits('sales');await capture('sales');
    for(const status of ['Processing','Shipped','Delivered']){
      await button('Manage order').click();await page.locator('dialog select').selectOption(status);await button('Update order').click();await page.locator('tbody').getByText(status,{exact:true}).waitFor();
    }
    const download=page.waitForEvent('download');await button('Export CSV').click();assert.equal((await download).suggestedFilename(),'audia-sales.csv');
    await page.getByPlaceholder('Search order, customer, email, or product').fill('missing');await page.getByText('No orders match your search.').waitFor();await page.getByPlaceholder('Search order, customer, email, or product').fill('');
    await page.locator('aside nav').getByRole('button',{name:'Customers',exact:true}).click();await page.getByText(email,{exact:true}).waitFor();await fits('customers');
    await button('Settings').click();await page.waitForFunction(()=>document.querySelector('[name=store_name]')?.value==='AUDIA Flagship');await page.locator('[name=store_name]').fill('AUDIA Test Studio');await page.locator('[name=support_email]').fill('support@example.com');await button('Save settings').click();await page.getByText('AUDIA Test Studio',{exact:true}).waitFor();await fits('settings');await capture('settings');
    await button('Notifications').click();await page.locator('.notification-list li').first().waitFor();await button('Close dialog').click();
    await page.setViewportSize({width:390,height:900});await button('Open admin menu').click();await page.locator('aside nav').getByRole('button',{name:'Overview',exact:true}).click();await page.locator('[data-field=gross_revenue]').filter({hasText:'12,990'}).waitFor();await capture('admin-mobile');
    await page.setViewportSize({width:1440,height:1000});await button('Switch to dark mode').click();await fits('admin dark');
    await button('Sign out of admin').click();await button('Sign in').click();await page.locator('[data-field=email]').fill(email);await page.locator('[data-field=password]').fill(password);await button('Sign in').click();await button('Open account').waitFor();
    await page.getByPlaceholder('Enter your order number').fill(orderId);await button('Track').click();await page.locator('.order-detail').getByText('Delivered',{exact:true}).waitFor();await button('Close dialog').click();
    await button('Open account').click();const security=page.locator('[data-form=password]');await security.locator('[name=current_password]').fill(password);await security.locator('[name=password]').fill('changed-password-123');await security.locator('[name=confirm]').fill('changed-password-123');await button('Update password').click();await page.getByText('Password updated.',{exact:true}).waitFor();
    await page.reload();await page.locator('.account-page').waitFor();await button('Remove').click();await page.getByText('Tap the heart on an instrument to save it here.').waitFor();
    await button('Sign out').click();await page.locator('.landing-page').waitFor();
    assert.equal(await page.locator('.product-card').count(),0);
    assert.equal(await button('Open cart').count(),0);
    assert.equal(await page.evaluate(()=>sessionStorage.getItem('audia-cart')),'[]');
    assert.equal((await page.request.get(base+'/api/products')).status(),401);
    await button('Explore bass guitars').click();await page.locator('[data-field=email]').fill(email);await page.locator('[data-field=password]').fill('changed-password-123');await button('Sign in').click();
    await page.waitForFunction(()=>document.querySelectorAll('.product-card').length===10);
    assert.match(await page.locator('.product-card').first().innerText(),/BASS_001/);
    // Revocation in another tab must remove protected UI when the API next rejects access.
    const authState=await (await page.request.get(base+'/api/auth/session')).json();
    await page.request.post(base+'/api/auth/logout',{headers:{'X-CSRF-Token':authState.csrf_token}});
    await button('Open account').click();await page.locator('.auth-page').waitFor();
    assert.equal(await page.locator('.product-card').count(),0);
    assert.deepEqual(errors,[]);
    console.log('PASS: Public landing, uploaded photos, guest/deep-link restrictions, category sign-in, logout and session revocation');
    console.log('PASS: Registration, real login, session restoration, recovery, password changes, and logout');
    console.log('PASS: Catalog, finder, chat, saved instruments, checkout, account, and order tracking');
    console.log('PASS: Inventory create/edit, order fulfillment, revenue, export, customers, settings, and notifications');
    console.log('PASS: Responsive layouts, both themes, API failure handling, and no JavaScript errors');
  }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});

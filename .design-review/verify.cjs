const { chromium } = require('C:/Users/daniel jay bernadas/AppData/Local/npm-cache/_npx/e41f203b7505f1fb/node_modules/playwright');
const fs = require('node:fs');
const assert = require('node:assert/strict');
const base = 'http://127.0.0.1:4173';
(async () => {
  const browser = await chromium.launch({headless:true});
  const page = await browser.newPage({viewport:{width:1440,height:1000},reducedMotion:'reduce'});
  const errors = [];
  const report = [];
  page.on('pageerror', e => errors.push(e.message));
  async function fits(label) {
    await page.waitForTimeout(150);
    const size = await page.evaluate(() => ({width:innerWidth,scroll:document.documentElement.scrollWidth}));
    assert.ok(size.scroll <= size.width, `${label} overflows: ${JSON.stringify(size)}`);
    report.push(`${label}: no horizontal overflow`);
  }
  async function shot(name, fullPage=false) { await page.waitForTimeout(500); await page.screenshot({path:`.design-review/${name}.png`,fullPage}); }
  await page.goto(base,{waitUntil:'networkidle'});
  await page.locator('.hero-photo img').evaluate(img => img.decode().catch(()=>{}));
  for (const theme of ['dark','light']) {
    if (await page.locator('html').evaluate(el=>el.classList.contains('dark')) !== (theme === 'dark')) await page.getByRole('button',{name:`Switch to ${theme} mode`}).click();
    await page.waitForTimeout(300);
    await fits(`Desktop storefront ${theme}`);
    await shot(`store-${theme}`);
    await shot(`store-${theme}-full`,true);
    for (const width of [320,390,768,1024]) {
      await page.setViewportSize({width,height:900});
      await fits(`Storefront ${theme} ${width}px`);
      if(width===390) await shot(`mobile-${theme}`,true);
    }
    await page.setViewportSize({width:1440,height:1000});
  }
  const search = page.getByPlaceholder('Search guitars or brands');
  await search.fill('Yamaha');
  assert.equal(await page.locator('.product-card').count(),1);
  await search.fill('');
  await page.locator('#shop').getByRole('button',{name:'Bass',exact:true}).click();
  assert.equal(await page.locator('.product-card').count(),1);
  await page.locator('#shop').getByRole('button',{name:'All',exact:true}).click();
  await page.getByRole('button',{name:'Add Squier Sonic Stratocaster to cart'}).click();
  await page.locator('.cart-panel').waitFor();
  assert.ok((await page.locator('.cart-panel').innerText()).includes('12,990'));
  await shot('cart-light');
  await page.getByRole('button',{name:'Close cart',exact:true}).click({position:{x:10,y:10}});
  await page.getByRole('button',{name:'Find my guitar',exact:true}).click();
  await shot('finder-light');
  for(let i=0;i<3;i++) await page.getByRole('button',{name:'Continue',exact:true}).click();
  await page.getByRole('button',{name:'Show my matches'}).click();
  await page.getByText('Your closest matches.').waitFor();
  await page.getByRole('button',{name:'Close finder',exact:true}).click({position:{x:10,y:10}});
  report.push('Search, category filters, add to cart, and four-step finder passed');
  await page.getByRole('button',{name:'Open customer support'}).click();
  await page.setViewportSize({width:390,height:600});
  await page.waitForTimeout(300);
  const chat = await page.locator('.chat-panel').boundingBox();
  assert.ok(chat.y>=0 && chat.y+chat.height<=600);
  await shot('chat-mobile');
  await page.getByRole('button',{name:'Open customer support'}).click();
  await page.getByRole('button',{name:'Open menu',exact:true}).click();
  await page.getByRole('button',{name:'Sign in',exact:true}).click();
  await page.locator('.auth-page').waitFor();
  for(const theme of ['light','dark']) {
    if (await page.locator('html').evaluate(el=>el.classList.contains('dark')) !== (theme === 'dark')) await page.getByRole('button',{name:`Switch to ${theme} mode`}).click();
    for(const width of [320,390,1440]) {
      await page.setViewportSize({width,height:1000});
      await fits(`Sign-in ${theme} ${width}px`);
      if(width!==320) await shot(`auth-${theme}-${width}`);
    }
  }
  await page.getByRole('button',{name:'Administrator',exact:true}).click();
  await page.getByRole('button',{name:'Open dashboard',exact:true}).click();
  await page.locator('.admin-page').waitFor();
  await page.waitForTimeout(1000);
  for(const theme of ['dark','light']) {
    if (await page.locator('html').evaluate(el=>el.classList.contains('dark')) !== (theme === 'dark')) await page.getByRole('button',{name:`Switch to ${theme} mode`}).click();
    for(const width of [1440,768,390,320]) {
      await page.setViewportSize({width,height:1000});
      await fits(`Dashboard ${theme} ${width}px`);
      if(width===390 || width===1440) await shot(`admin-${theme}-${width}`,true);
    }
  }
  await page.setViewportSize({width:1440,height:1000});
  for(const name of ['Sales directory','Products','Customers']) {
    await page.locator('aside nav').getByRole('button',{name}).click();
    await fits(`Admin ${name} desktop`);
    await shot(`admin-${name.toLowerCase().replaceAll(' ','-')}`,true);
    for(const width of [390,320]) { await page.setViewportSize({width,height:900}); await fits(`Admin ${name} ${width}px`); }
    await page.setViewportSize({width:1440,height:1000});
  }
  assert.deepEqual(errors,[]);
  report.push('No JavaScript runtime errors');
  report.push('Reduced motion: sound animation = '+await page.evaluate(()=>matchMedia('(prefers-reduced-motion: reduce)').matches));
  fs.writeFileSync('.design-review/verification.json',JSON.stringify({report,errors},null,2));
  console.log(report.join('\n'));
  await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});

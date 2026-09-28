// Optional browser regression test. Install Playwright separately or set PLAYWRIGHT_MODULE.
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const assert = require('node:assert/strict');
const base = process.env.AUDIA_BASE_URL || 'http://127.0.0.1:5000';

(async () => {
  const browser = await chromium.launch({headless: true});
  const page = await browser.newPage({viewport: {width: 1440, height: 1000}, reducedMotion: 'reduce'});
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  const report = [];
  const buttons = (name, root = page) => root.getByRole('button', {name, exact: true});
  const count = async (selector, expected) => {
    await page.waitForFunction(({selector, expected}) => document.querySelectorAll(selector).length === expected, {selector, expected});
  };
  const close = async name => {await buttons(name).click({position: {x: 10, y: 10}});};
  async function fits(label) {
    for (const width of [320, 390, 768, 1024, 1440]) {
      await page.setViewportSize({width, height: 1000});
      await page.waitForTimeout(150);
      const size = await page.evaluate(() => ({width: innerWidth, scroll: document.documentElement.scrollWidth}));
      assert.ok(size.scroll <= size.width, `${label} overflows at ${width}`);
    }
  }
  await page.goto(base);
  await count('.product-card', 6);
  await fits('Storefront dark');
  await buttons('Switch to light mode').click();
  assert.equal(await page.evaluate(() => localStorage.getItem('audia-theme')), 'light');
  await page.reload(); await count('.product-card', 6);
  assert.equal(await page.locator('html').evaluate(el => el.classList.contains('dark')), false);
  await fits('Storefront light');
  const search = page.getByPlaceholder('Search guitars or brands');
  await search.fill('YAMAHA'); await count('.product-card', 1);
  assert.match(await page.locator('.product-card').innerText(), /Yamaha FG800/);
  await search.fill('missing guitar'); await count('.product-card', 0);
  await page.getByText('No guitar matches that search.').waitFor();
  await search.fill(''); await count('.product-card', 6);
  for (const [category, expected] of [['Electric', 3], ['Acoustic', 1], ['Classical', 1], ['Bass', 1], ['All', 6]]) {
    await buttons(category, page.locator('#shop')).click(); await count('.product-card', expected);
  }
  const sort = page.locator('#shop select');
  for (const [value, expected] of [['Price: low', 'Squier'], ['Price: high', 'PRS'], ['Rating', 'Epiphone'], ['Featured', 'Squier']]) {
    await sort.selectOption(value);
    assert.match(await page.locator('.product-card h3').first().innerText(), new RegExp(expected));
  }
  const like = buttons('Save guitar').first();
  await like.click(); assert.equal(await like.locator('svg').getAttribute('fill'), 'currentColor');
  await like.click(); assert.equal(await like.locator('svg').getAttribute('fill'), 'none');
  await buttons('Play guitar tone').first().click();
  await page.getByText('Playing', {exact: true}).waitFor();
  await page.getByText('Hear the tone', {exact: true}).waitFor();
  report.push('Catalog search, empty results, every category, all sort modes, wishlist, and sound preview');

  await buttons('Add Squier Sonic Stratocaster to cart').click();
  const cart = page.locator('.cart-panel'); await cart.waitFor();
  assert.match(await cart.innerText(), /12,990/);
  await cart.locator('button').filter({has: page.locator('svg.lucide-plus')}).click();
  assert.match(await cart.innerText(), /25,980/);
  await cart.locator('button').filter({has: page.locator('svg.lucide-minus')}).click();
  await cart.locator('button').filter({has: page.locator('svg.lucide-minus')}).click();
  await cart.getByText('Your cart is empty.').waitFor();
  await close('Close cart');
  await buttons('Add Squier Sonic Stratocaster to cart').click(); await close('Close cart');
  await buttons('Add Squier Sonic Stratocaster to cart').click();
  assert.match(await cart.innerText(), /25,980/); await close('Close cart');
  report.push('Cart additions, repeat additions, quantity controls, subtotal, and empty state');

  await buttons('Find my guitar').click();
  const finder = page.locator('.finder-modal');
  const range = finder.locator('input[type=range]'); await range.fill('15000');
  assert.match(await finder.innerText(), /15,000/);
  await buttons('Continue').click(); await buttons('Intermediate', finder).click();
  await buttons('Continue').click(); await buttons('Blues', finder).click();
  await buttons('Continue').click(); await buttons('Acoustic', finder).click();
  const requestPromise = page.waitForRequest(request => request.url().endsWith('/api/finder'));
  await buttons('Show my matches').click();
  assert.deepEqual((await requestPromise).postDataJSON(), {budget: 15000, level: 'Intermediate', genre: 'Blues', category: 'Acoustic'});
  await page.getByText('Your closest matches.').waitFor();
  assert.match(await finder.innerText(), /Yamaha FG800/);
  await buttons('Start again').click(); assert.equal(await finder.locator('input').inputValue(), '15000');
  await close('Close finder');
  await buttons('Find my guitar').click(); assert.equal(await finder.locator('input').inputValue(), '15000');
  for (let i = 0; i < 3; i++) await buttons('Continue').click();
  await buttons('Show my matches').click(); await page.getByText('Your closest matches.').waitFor();
  await finder.locator('button').filter({has: page.locator('svg.lucide-plus')}).first().click();
  await cart.waitFor(); assert.match(await cart.innerText(), /Yamaha FG800/); await close('Close cart');
  report.push('Finder answers, API payload, recommendations, restart, remembered answers, and add-to-cart');

  const order = page.getByPlaceholder('AUD-24018');
  await order.fill('aud-12345'); await buttons('Track').click();
  assert.match(await page.locator('#track .surface-card').innerText(), /AUD-12345/);
  await order.fill('aud-99999'); assert.match(await page.locator('#track .surface-card').innerText(), /AUD-99999/);
  await order.fill(''); await buttons('Track').click(); assert.match(await page.locator('#track .surface-card').innerText(), /AUD-24018/);
  await buttons('Open customer support').click();
  await buttons('I am a beginner').click();
  await page.getByText(/For a beginner, prioritize comfort/).waitFor();
  await page.getByPlaceholder('Ask about a guitar').fill('Acoustic or electric?');
  await page.getByPlaceholder('Ask about a guitar').press('Enter');
  await page.getByText(/Choose acoustic if you want simplicity/).waitFor();
  await buttons('Open customer support').click(); await buttons('Open customer support').click();
  await page.getByText(/Choose acoustic if you want simplicity/).waitFor();
  await page.setViewportSize({width: 390, height: 600});
  await page.waitForTimeout(300);
  const chatBox = await page.locator('.chat-panel').boundingBox(); assert.ok(chatBox.y >= 0 && chatBox.y + chatBox.height <= 600, `Chat bounds: ${JSON.stringify(chatBox)}`);
  await buttons('Open customer support').click();
  await buttons('Open menu').click(); await buttons('Sign in').click();
  await page.locator('.auth-page').waitFor();
  report.push('Order tracking, chat presets, typed chat, retained conversation, and mobile navigation');

  await fits('Sign-in light');
  await buttons('Switch to dark mode').click(); await fits('Sign-in dark');
  await buttons('Show password').click(); assert.equal(await page.locator('input').nth(1).getAttribute('type'), 'text');
  await buttons('Hide password').click();
  await buttons('Administrator').click();
  await page.locator('input[type=password]').fill('incorrect'); await buttons('Open dashboard').click();
  await page.getByText('Incorrect email or password.').waitFor();
  await buttons('Customer').click(); await buttons('Sign in').click();
  await page.locator('.storefront').waitFor();
  await buttons('Open account').waitFor();
  await buttons('Admin portal').click(); await buttons('Open dashboard').click();
  await page.locator('.admin-page').waitFor(); await fits('Dashboard dark');
  await buttons('Switch to light mode').click(); await fits('Dashboard light');
  await page.locator('aside nav').getByRole('button', {name: 'Sales directory'}).click();
  await count('tbody tr', 6);
  const salesQuery = page.getByPlaceholder('Search order, customer, email, or product');
  await salesQuery.fill('mika'); await count('tbody tr', 1);
  await salesQuery.fill(''); await page.locator('main select').selectOption('Paid'); await count('tbody tr', 3);
  await salesQuery.fill('missing'); await count('tbody tr', 0);
  await page.locator('aside nav').getByRole('button', {name: 'Products', exact: true}).click(); await fits('Admin products');
  await page.locator('aside nav').getByRole('button', {name: 'Customers', exact: true}).click(); await fits('Admin customers');
  await page.locator('aside nav').getByRole('button', {name: 'Sales directory'}).click(); await count('tbody tr', 6);
  await page.setViewportSize({width: 390, height: 900});
  await page.locator('header button').first().click();
  await page.locator('aside nav').getByRole('button', {name: 'Overview', exact: true}).click();
  await page.setViewportSize({width: 1440, height: 1000});
  await buttons('View storefront').click(); await buttons('Open account').click(); await page.locator('.admin-page').waitFor();
  await buttons('Sign out of admin').click(); await buttons('Sign in').waitFor();
  report.push('Customer/admin authentication, invalid credentials, password visibility, responsive admin views, sales filtering, and logout');

  // Exercise the original local fallbacks without changing the Flask API.
  await page.route('**/api/**', route => route.abort());
  await page.reload(); await count('.product-card', 6);
  await buttons('Find my guitar').click();
  for (let i = 0; i < 3; i++) await buttons('Continue').click();
  await buttons('Show my matches').click(); await page.getByText('Your closest matches.').waitFor();
  assert.match(await page.locator('.finder-modal').innerText(), /Squier Sonic/);
  await close('Close finder');
  await buttons('Open customer support').click(); await buttons('I am a beginner').click();
  await page.getByText(/For a first guitar, comfort matters most/).waitFor();
  await buttons('Open customer support').click(); await buttons('Admin portal').click();
  await buttons('Open dashboard').click(); await page.locator('.admin-page').waitFor(); await count('tbody tr', 5);
  await buttons('Sign out of admin').click(); await buttons('Sign in').click();
  await page.locator('.auth-page').waitFor(); await buttons('Sign in').click();
  await page.locator('.storefront').waitFor(); await buttons('Open account').waitFor();
  report.push('Catalog, finder, chat, customer/admin login, and sales fallbacks when API requests fail');
  assert.deepEqual(errors, []);
  console.log(report.map(item => `PASS: ${item}`).join('\n'));
  console.log('PASS: No JavaScript runtime errors');
  await browser.close();
})().catch(error => {console.error(error); process.exit(1);});

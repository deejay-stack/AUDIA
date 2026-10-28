// Verify that editing the documented component rule changes the rendered UI.
// Run against tests/serve.py; CSS changes are intercepted in memory only.
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const base = process.env.AUDIA_BASE_URL || 'http://127.0.0.1:5056';
const root = path.resolve(__dirname, '..');
const edits = [
  ['landing/landing', '.landing-page', 'background-color', 'rgb(61, 51, 81)'],
  ['catalog/catalog', '.catalog-product-card__name', 'font-size', '27px'],
  ['catalog/catalog', '.catalog-product-card__description', 'color', 'rgb(19, 123, 87)'],
  ['tuner/tuner', '.tuner-container', 'background-color', 'rgb(31, 75, 99)'],
  ['tuner/tuner_meter', '.tuner-indicator', 'background', 'rgb(111, 37, 81)'],
  ['tuner/tuner_meter', '.tuner-container[data-tuning="in-tune"] .tuner-indicator', 'background', 'rgb(29, 101, 64)'],
  ['chatbot/chatbot_panel', '.chatbot-panel', 'background-color', 'rgb(33, 66, 99)'],
  ['chatbot/chatbot_panel', '.dark .chatbot-panel', 'background-color', 'rgb(44, 77, 110)'],
];
const escape = value => value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
const sheets = new Map();
for (const [file, selector, property, value] of edits) {
  const key = '/static/css/' + file + '.css';
  const source = sheets.get(key) || fs.readFileSync(path.join(root, 'assets/css', file + '.css'), 'utf8');
  const rule = new RegExp('(^|\\n)' + escape(selector) + '\\s*\\{([^}]+)\\}', 'g');
  let count = 0;
  const changed = source.replace(rule, (match, newline, body) => {
    count++;
    const declaration = new RegExp('(^|;)\\s*' + escape(property) + '\\s*:[^;]*;', 'g');
    return newline + selector + ' {' + body.replace(declaration, '$1') + '\n  ' + property + ': ' + value + ';\n}';
  });
  assert.equal(count, 1, `Expected one editable rule: ${file} ${selector}`);
  sheets.set(key, changed);
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  try {
    const context = await browser.newContext({ reducedMotion: 'reduce' });
    const token = (await (await context.request.get(base + '/api/auth/session')).json()).csrf_token;
    const registration = await context.request.post(base + '/api/auth/register', {
      headers: { 'X-CSRF-Token': token },
      data: { name: 'CSS Student', email: 'css-student@example.com', password: 'css-student-password-123' },
    });
    assert.ok([201, 409].includes(registration.status()));
    const csrf = (await (await context.request.get(base + '/api/auth/session')).json()).csrf_token;
    assert.equal((await context.request.post(base + '/api/auth/login', {
      headers: { 'X-CSRF-Token': csrf },
      data: { email: 'css-student@example.com', password: 'css-student-password-123', role: 'customer' },
    })).status(), 200);
    await context.route('**/static/css/**', route => {
      const body = sheets.get(new URL(route.request().url()).pathname);
      return body ? route.fulfill({ contentType: 'text/css', body }) : route.continue();
    });
    const page = await context.newPage();
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    let checks = 0;
    async function expectStyle(selector, property, value) {
      assert.equal(await page.locator(selector).first().evaluate((node, property) => getComputedStyle(node).getPropertyValue(property), property), value, selector + ' ' + property);
      checks++;
    }
    for (const theme of ['light', 'dark']) for (const width of [375, 1440]) {
      await page.setViewportSize({ width, height: 1000 });
      await page.addInitScript(theme => localStorage.setItem('audia-theme', theme), theme);
      await page.goto(base + '/');
      await page.locator('#root:not([inert])').waitFor();
      await expectStyle('.landing-page', 'background-color', 'rgb(61, 51, 81)');
      await page.goto(base + '/shop');
      await page.locator('#root:not([inert])').waitFor();
      await page.locator('.product-card').first().waitFor();
      await expectStyle('.catalog-product-card__name', 'font-size', '27px');
      await expectStyle('.catalog-product-card__description', 'color', 'rgb(19, 123, 87)');
      await page.goto(base + '/tuner');
      await page.locator('#root:not([inert])').waitFor();
      await expectStyle('.tuner-container', 'background-color', 'rgb(31, 75, 99)');
      await expectStyle('.tuner-indicator', 'background-color', 'rgb(111, 37, 81)');
      await page.locator('.tuner-container').evaluate(node => node.dataset.tuning = 'in-tune');
      await expectStyle('.tuner-indicator', 'background-color', 'rgb(29, 101, 64)');
      await page.getByRole('button', { name: 'Open customer support', exact: true }).click();
      await expectStyle('.chatbot-panel', 'background-color', theme === 'dark' ? 'rgb(44, 77, 110)' : 'rgb(33, 66, 99)');
    }
    assert.deepEqual(errors, []);
    console.log(`PASS: ${checks} component CSS edits reach the browser in both themes at mobile and desktop widths.`);
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });

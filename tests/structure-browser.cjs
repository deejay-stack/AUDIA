// Compare existing screens before/after a structure-only migration.
// Run with tests/serve.py and STRUCTURE_PHASE=before, then =after.
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const zlib = require('node:zlib');
const base = process.env.AUDIA_BASE_URL || 'http://127.0.0.1:5056';
const phase = process.env.STRUCTURE_PHASE || 'after';
assert.ok(['before', 'after'].includes(phase));
const directory = process.env.STRUCTURE_SNAPSHOTS || 'test-results/architecture/screens';

function decodeScreenshot(data) {
  let offset = 8, width, height, channels;
  const chunks = [];
  while (offset < data.length) {
    const length = data.readUInt32BE(offset);
    const type = data.toString('ascii', offset + 4, offset + 8);
    const chunk = data.subarray(offset + 8, offset + 8 + length);
    if (type === 'IHDR') {
      width = chunk.readUInt32BE(0); height = chunk.readUInt32BE(4);
      assert.equal(chunk[8], 8);
      assert.ok([2, 6].includes(chunk[9]));
      channels = chunk[9] === 2 ? 3 : 4;
    }
    if (type === 'IDAT') chunks.push(chunk);
    offset += length + 12;
  }
  const raw = zlib.inflateSync(Buffer.concat(chunks));
  const stride = width * channels, pixels = Buffer.alloc(stride * height);
  for (let row = 0; row < height; row++) {
    const filter = raw[row * (stride + 1)];
    for (let column = 0; column < stride; column++) {
      const index = row * stride + column;
      const left = column >= channels ? pixels[index - channels] : 0;
      const above = row ? pixels[index - stride] : 0;
      const corner = row && column >= channels ? pixels[index - stride - channels] : 0;
      let predictor = 0;
      if (filter === 1) predictor = left;
      if (filter === 2) predictor = above;
      if (filter === 3) predictor = Math.floor((left + above) / 2);
      if (filter === 4) {
        const estimate = left + above - corner;
        const distances = [Math.abs(estimate - left), Math.abs(estimate - above), Math.abs(estimate - corner)];
        predictor = [left, above, corner][distances.indexOf(Math.min(...distances))];
      }
      pixels[index] = (raw[row * (stride + 1) + column + 1] + predictor) & 255;
    }
  }
  return { width, height, channels, pixels };
}

function sameAppearance(before, after) {
  if (before.equals(after)) return true;
  const a = decodeScreenshot(before), b = decodeScreenshot(after);
  if (a.width !== b.width || a.height !== b.height || a.channels !== b.channels) return false;
  let changed = 0;
  for (let index = 0; index < a.pixels.length; index += a.channels) {
    let different = false;
    for (let channel = 0; channel < a.channels; channel++) {
      const delta = Math.abs(a.pixels[index + channel] - b.pixels[index + channel]);
      if (delta > 4) return false;
      different ||= delta > 0;
    }
    if (different) changed++;
  }
  // Permit tiny compositor rounding: at most 4/255 in 0.1% of pixels.
  // An unchanged admin badge differed in four edge pixels by at most 4/255.
  return changed / (a.width * a.height) <= .001;
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  try {
    const contexts = {};
    for (const role of ['guest', 'customer', 'admin']) {
      const context = await browser.newContext({ viewport: { width: 1440, height: 1000 }, reducedMotion: 'reduce' });
      if (role !== 'guest') {
        const email = role === 'admin' ? 'admin@example.com' : 'structure@example.com';
        const password = role === 'admin' ? 'admin-password-123' : 'structure-password-123';
        let csrf = (await (await context.request.get(base + '/api/auth/session')).json()).csrf_token;
        if (role === 'customer') {
          const register = await context.request.post(base + '/api/auth/register', {
            headers: { 'X-CSRF-Token': csrf }, data: { name: 'Structure Player', email, password },
          });
          assert.ok([201, 409].includes(register.status()));
          csrf = (await (await context.request.get(base + '/api/auth/session')).json()).csrf_token;
        }
        const login = await context.request.post(base + '/api/auth/login', {
          headers: { 'X-CSRF-Token': csrf }, data: { email, password, role: role === 'admin' ? 'admin' : 'customer' },
        });
        assert.equal(login.status(), 200);
      }
      contexts[role] = context;
    }
    const cases = [
      ['guest', '/'], ['guest', '/login'], ['guest', '/register'], ['guest', '/reset-password'],
      ['customer', '/'], ['customer', '/shop'], ['customer', '/account'], ['admin', '/admin'],
      ['customer', '/tuner'], ['customer', '/lessons'], ['customer', '/lessons/getting-started'],
      ['customer', '/lessons/chords'], ['customer', '/lessons/chords/c-major'], ['customer', '/lessons/strumming'],
    ];
    let captured = 0;
    for (const [role, route] of cases) {
      const page = await contexts[role].newPage();
      const errors = [];
      page.on('pageerror', error => errors.push(error.message));
      page.on('response', response => {
        if (response.status() >= 400 && new URL(response.url()).pathname.startsWith('/static/')) {
          errors.push(`Missing asset: ${response.url()}`);
        }
      });
      await page.goto(base + route);
      await page.locator('#root:not([inert])').waitFor();
      if (route === '/shop') await page.waitForFunction(() => document.querySelectorAll('.product-card').length === 42);
      if (route === '/account') await page.getByText('Your first order starts with your next favorite instrument.', { exact: true }).waitFor();
      if (route === '/admin') await page.waitForFunction(() => document.querySelector('[data-field=total_orders]')?.textContent === '0');
      await page.locator('img').evaluateAll(images => Promise.all(images.map(async image => {
        image.loading = 'eager'; await image.decode();
      })));
      for (const theme of ['dark', 'light']) {
        if (await page.locator('html').evaluate(node => node.classList.contains('dark')) !== (theme === 'dark')) {
          await page.locator('#root [data-action="theme"]').first().click();
        }
        await page.evaluate(() => document.activeElement.blur());
        await page.mouse.move(0, 0);
        for (const width of [375, 1440]) {
          await page.setViewportSize({ width, height: 1000 });
          await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
          // Let Chromium finish applying resized media queries before the full-page capture.
          await page.waitForTimeout(150);
          assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), `${route} overflow`);
          const name = `${role}-${route.slice(1).replaceAll('/', '-') || 'landing'}-${theme}-${width}.png`;
          const target = path.join(directory, phase, name);
          fs.mkdirSync(path.dirname(target), { recursive: true });
          await page.screenshot({ path: target, fullPage: true, animations: 'disabled' });
          if (phase === 'after') {
            const original = path.join(directory, 'before', name);
            assert.ok(fs.existsSync(original), `Missing baseline: ${name}`);
            assert.ok(sameAppearance(fs.readFileSync(original), fs.readFileSync(target)), `Visual appearance changed: ${name}`);
          }
          captured++;
        }
      }
      assert.deepEqual(errors, [], `Browser errors: ${role} ${route}`);
      await page.close();
    }
    console.log(`PASS: ${captured} ${phase} screenshots, all assets loaded, no browser errors${phase === 'after' ? ', visually unchanged from before (strict pixel tolerance)' : ''}`);
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });

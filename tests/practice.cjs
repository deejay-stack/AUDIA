// Run against python tests/serve.py (disposable database), never production.
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const base = process.env.AUDIA_BASE_URL || 'http://127.0.0.1:5056';

(async () => {
  const browser = await chromium.launch({ headless: true, args: [
    '--use-fake-device-for-media-stream', '--use-fake-ui-for-media-stream',
  ] });
  const errors = [];
  try {
    const context = await browser.newContext({ viewport: { width: 1440, height: 1000 }, reducedMotion: 'reduce' });
    const email = `practice-${Date.now()}@example.com`;
    let session = await (await context.request.get(base + '/api/auth/session')).json();
    const register = await context.request.post(base + '/api/auth/register', {
      headers: { 'X-CSRF-Token': session.csrf_token },
      data: { name: 'Practice Player', email, password: 'practice-password-123' },
    });
    assert.equal(register.status(), 201);
    session = await (await context.request.get(base + '/api/auth/session')).json();
    assert.equal((await context.request.post(base + '/api/auth/login', {
      headers: { 'X-CSRF-Token': session.csrf_token }, data: { email, password: 'practice-password-123' },
    })).status(), 200);

    // Use real Web Audio nodes and streams for deterministic pitch/lifecycle tests.
    // The app still executes its actual getUserMedia -> analyser -> YIN path.
    await context.addInitScript(() => {
      const NativeAudioContext = window.AudioContext;
      const nativeGetUserMedia = navigator.mediaDevices.getUserMedia.bind(navigator.mediaDevices);
      window.__audio = { mode: 'sine', calls: 0, stopped: 0, contexts: [], frequency: 110, stream: null };
      window.AudioContext = class extends NativeAudioContext {
        constructor(...args) { super(...args); window.__audio.contexts.push(this); }
      };
      navigator.mediaDevices.getUserMedia = async (constraints) => {
        const state = window.__audio;
        state.calls++;
        if (state.mode === 'pending') await new Promise(resolve => { state.resolve = resolve; });
        if (['denied', 'missing', 'busy'].includes(state.mode)) {
          throw new DOMException('Test microphone error', state.mode === 'denied'
            ? 'NotAllowedError' : state.mode === 'missing' ? 'NotFoundError' : 'NotReadableError');
        }
        let stream;
        if (state.mode === 'native') stream = await nativeGetUserMedia(constraints);
        else {
          const generator = new NativeAudioContext();
          await generator.resume();
          const oscillator = generator.createOscillator();
          oscillator.frequency.value = state.frequency;
          const gain = generator.createGain(); gain.gain.value = .2;
          const destination = generator.createMediaStreamDestination();
          oscillator.connect(gain); gain.connect(destination); oscillator.start();
          stream = destination.stream;
          state.setPitch = frequency => oscillator.frequency.setValueAtTime(frequency, generator.currentTime);
          state.setVolume = volume => gain.gain.setValueAtTime(volume, generator.currentTime);
          state.disconnect = () => { stream.getTracks()[0].dispatchEvent(new Event('ended')); };
          state.cleanup = () => { oscillator.stop(); void generator.close(); };
        }
        for (const track of stream.getTracks()) {
          const stop = track.stop.bind(track);
          track.stop = () => { state.stopped++; stop(); state.cleanup?.(); };
        }
        state.stream = stream;
        return stream;
      };
    });
    const page = await context.newPage();
    page.on('pageerror', error => errors.push(error.message));
    const newRequests = [];
    page.on('request', request => {
      if (request.method() !== 'GET') newRequests.push(request.method() + ' ' + new URL(request.url()).pathname);
    });
    const ready = () => page.locator('#root:not([inert])').waitFor();
    const start = () => page.getByRole('button', { name: 'Start Tuner', exact: true }).click();
    const stop = () => page.getByRole('button', { name: 'Stop Tuner', exact: true }).click();
    await page.goto(base + '/tuner'); await ready();
    assert.equal(await page.evaluate(() => window.__audio.calls), 0, 'No permission prompt on page load');
    await start(); await page.getByText('Listening', { exact: true }).waitFor();
    const targets = [[82.406889, 'E', '2'], [110, 'A', '2'], [146.832384, 'D', '3'],
      [195.997718, 'G', '3'], [246.941651, 'B', '3'], [329.627557, 'E', '4']];
    for (const [frequency, note, octave] of targets) {
      await page.evaluate(frequency => window.__audio.setPitch(frequency), frequency);
      await page.waitForFunction(({ note, octave }) => document.querySelector('#tuner-note').textContent === note
        && document.querySelector('#tuner-octave').textContent === octave
        && document.querySelector('#tuner-status').textContent === 'In Tune', { note, octave });
      assert.equal(await page.locator(`[data-tuning-note="${note}${octave}"][data-active]`).count(), 1);
      assert.ok(Math.abs(parseFloat(await page.locator('#tuner-frequency').innerText()) - frequency) < .5);
    }
    for (const [cents, status] of [[-25, 'Too Flat'], [-10, 'Slightly Flat'], [10, 'Slightly Sharp'], [25, 'Too Sharp']]) {
      await page.evaluate(frequency => window.__audio.setPitch(frequency), 110 * 2 ** (cents / 1200));
      await page.getByText(status, { exact: true }).waitFor();
      const position = await page.locator('#tuner-indicator').evaluate(node => parseFloat(node.style.left));
      assert.ok(cents < 0 ? position < 50 : position > 50);
    }
    await page.evaluate(() => window.__audio.setVolume(0));
    await page.getByText('Play a string', { exact: true }).waitFor();
    assert.equal(await page.locator('#tuner-indicator').isHidden(), true);
    await page.evaluate(() => { window.__audio.setPitch(110); window.__audio.setVolume(.2); });
    await page.getByText('In Tune', { exact: true }).waitFor();
    await stop();
    await page.waitForFunction(() => window.__audio.contexts.every(context => context.state === 'closed'));
    assert.equal(await page.evaluate(() => window.__audio.stream.getTracks().every(track => track.readyState === 'ended')), true);

    for (const [mode, message] of [['denied', 'Permission denied'], ['missing', 'No microphone was detected'], ['busy', 'The microphone could not be started']]) {
      await page.evaluate(mode => { window.__audio.mode = mode; }, mode);
      await start(); await page.getByText(message, { exact: mode === 'denied' }).waitFor();
      assert.equal(await page.getByRole('button', { name: 'Start Tuner', exact: true }).isEnabled(), true);
      await page.waitForFunction(() => window.__audio.contexts.every(context => context.state === 'closed'));
    }
    await page.evaluate(() => { window.__audio.mode = 'pending'; });
    await start(); await page.getByText('Requesting microphone', { exact: true }).waitFor();
    await page.waitForFunction(() => Boolean(window.__audio.resolve));
    await stop(); await page.evaluate(() => { window.__audio.mode = 'sine'; window.__audio.resolve(); });
    await page.waitForFunction(() => window.__audio.stopped === 2);
    assert.equal(await page.locator('#tuner-microphone').innerText(), 'Microphone inactive');
    await start(); await page.getByText('Listening', { exact: true }).waitFor();
    await page.evaluate(() => window.__audio.disconnect());
    await page.getByText(/The microphone was disconnected/).waitFor();

    // Also exercise actual browser microphone permission and capture with a fake device.
    await page.evaluate(() => { window.__audio.mode = 'native'; window.__audio.cleanup = null; });
    await start(); await page.getByText('Listening', { exact: true }).waitFor();
    await stop();
    assert.equal(await page.evaluate(() => window.__audio.stream.getTracks()[0].readyState), 'ended');

    await page.evaluate(() => { window.__audio.mode = 'sine'; });
    await start(); await page.getByText('Listening', { exact: true }).waitFor();
    await page.evaluate(() => {
      Object.defineProperty(document, 'hidden', { configurable: true, value: true });
      document.dispatchEvent(new Event('visibilitychange'));
      delete document.hidden;
    });
    await page.waitForFunction(() => window.__audio.stream.getTracks()[0].readyState === 'ended'
      && window.__audio.contexts.every(context => context.state === 'closed'));
    await start(); await page.getByText('Listening', { exact: true }).waitFor();
    await page.evaluate(() => window.dispatchEvent(new Event('pagehide')));
    await page.waitForFunction(() => window.__audio.stream.getTracks()[0].readyState === 'ended'
      && window.__audio.contexts.every(context => context.state === 'closed'));

    await page.evaluate(() => { window.__audio.mode = 'sine'; });
    await start(); await page.getByText('Listening', { exact: true }).waitFor();
    await page.goto(base + '/lessons'); await ready();
    assert.ok(await page.getByRole('heading', { name: 'Learn Guitar', exact: true }).count());
    await page.getByRole('link', { name: 'Start learning', exact: true }).click(); await ready();
    await page.getByRole('link', { name: 'Next: basic chords →', exact: true }).click(); await ready();
    assert.equal(await page.locator('.chord-diagram').count(), 8);
    await page.locator('.chord-card').first().click(); await ready();
    assert.equal(await page.locator('.chord-diagram .chord-string').count(), 6);
    await page.getByRole('link', { name: 'Add a strumming pattern →', exact: true }).click(); await ready();
    assert.equal(await page.locator('.strumming-pattern').count(), 3);
    for (const pattern of await page.locator('.strumming-pattern').all()) {
      assert.deepEqual(await pattern.locator('.strumming-count').allTextContents(), ['1', '&', '2', '&', '3', '&', '4', '&']);
    }

    const routes = ['/tuner', '/lessons', '/lessons/getting-started', '/lessons/chords', '/lessons/strumming',
      ...['c-major', 'g-major', 'd-major', 'a-major', 'e-major', 'a-minor', 'e-minor', 'd-minor'].map(slug => '/lessons/chords/' + slug)];
    for (const route of routes) {
      await page.goto(base + route); await ready();
      for (const theme of ['dark', 'light']) {
        if (await page.locator('html').evaluate(node => node.classList.contains('dark')) !== (theme === 'dark')) {
          await page.locator('[data-action="theme"]').click();
        }
        for (const width of [320, 375, 768, 1024, 1440]) {
          await page.setViewportSize({ width, height: 1000 });
          await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
          // Wait for Chromium's SVG layout to settle after resizing; keep the size assertion below.
          await page.waitForFunction(() => [...document.querySelectorAll('.chord-diagram')]
            .every(node => node.getBoundingClientRect().width >= 180));
          assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), `${route}: ${theme} at ${width}px`);
          const clipped = await page.locator('.chord-diagram, .tuner-meter, .strumming-pattern, .practice-nav').evaluateAll(nodes =>
            nodes.some(node => { const box = node.getBoundingClientRect(); return box.left < 0 || box.right > innerWidth; }));
          assert.equal(clipped, false, `${route}: clipped component at ${width}px`);
          const tinyDiagrams = await page.locator('.chord-diagram').evaluateAll(nodes =>
            nodes.some(node => node.getBoundingClientRect().width < 180));
          assert.equal(tinyDiagrams, false, `${route}: chord diagram too small to read at ${width}px`);
          if (process.env.SCREENSHOT_DIR && width === 320 && ['/tuner', '/lessons', '/lessons/chords', '/lessons/strumming'].includes(route)) {
            fs.mkdirSync(process.env.SCREENSHOT_DIR, { recursive: true });
            await page.screenshot({ path: `${process.env.SCREENSHOT_DIR}/${route.slice(1).replaceAll('/', '-')}-${theme}-mobile.png`, fullPage: true });
          }
        }
        if (process.env.SCREENSHOT_DIR && ['/tuner', '/lessons', '/lessons/chords', '/lessons/strumming'].includes(route)) {
          fs.mkdirSync(process.env.SCREENSHOT_DIR, { recursive: true });
          await page.screenshot({ path: `${process.env.SCREENSHOT_DIR}/${route.slice(1).replaceAll('/', '-')}-${theme}.png`, fullPage: true });
        }
      }
    }
    assert.deepEqual(newRequests, [], 'Practice pages must never upload audio or mutate server state');
    assert.deepEqual(errors, [], 'No browser JavaScript errors');
    console.log('PASS: Audio capture, six strings, flat/sharp meter, silence recovery, denial/missing/busy, stop, pending cancellation, disconnect and restart');
    console.log('PASS: Lessons, eight SVG shapes, beat alignment, links, 130 layout/theme cases and no JavaScript errors or audio uploads');
    const storage = await context.storageState();
    await context.close();

    // Unsupported browser must produce an actionable message without an uncaught error.
    const unsupported = await browser.newContext({ storageState: storage });
    await unsupported.addInitScript(() => { window.AudioContext = undefined; window.webkitAudioContext = undefined; });
    const unsupportedPage = await unsupported.newPage();
    await unsupportedPage.goto(base + '/tuner'); await unsupportedPage.locator('#root:not([inert])').waitFor();
    await unsupportedPage.getByRole('button', { name: 'Start Tuner' }).click();
    await unsupportedPage.getByText(/Your browser does not support/).waitFor();
    await unsupportedPage.evaluate(() => Object.defineProperty(window, 'isSecureContext', { value: false, configurable: true }));
    await unsupportedPage.getByRole('button', { name: 'Start Tuner' }).click();
    await unsupportedPage.getByText(/Microphone access requires HTTPS or localhost/).waitFor();
    await unsupported.close();
    console.log('PASS: Unsupported audio API, insecure address and page lifecycle cleanup');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });

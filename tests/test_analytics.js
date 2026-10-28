const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const source = fs.readFileSync(path.join(__dirname, '../assets/js/analytics.js'), 'utf8');
const KEY = 'lozhka.analytics-consent.v1';
const COUNTER = 113844022;
const TAG_URL = `https://mc.yandex.ru/metrika/tag.js?id=${COUNTER}`;

function makeStorage(initial = {}) {
  const values = new Map(Object.entries(initial));
  return {
    getItem(key) { return values.has(key) ? values.get(key) : null; },
    setItem(key, value) { values.set(key, String(value)); },
    removeItem(key) { values.delete(key); },
  };
}

function element() {
  const listeners = {};
  return {
    hidden: false,
    isConnected: true,
    focused: false,
    addEventListener(name, listener) { listeners[name] = listener; },
    click() { listeners.click?.({ target: this }); },
    focus() { this.focused = true; },
  };
}

function boot(storage = makeStorage(), url = 'https://example.test/recipes/pasta.html') {
  const banner = element();
  banner.hidden = true;
  const accept = element();
  const deny = element();
  const open = element();
  const title = element();
  const windowListeners = {};
  const scripts = [];
  const document = {
    scripts,
    referrer: 'https://example.test/',
    head: { appendChild(script) { scripts.push(script); } },
    createElement(tag) { assert.equal(tag, 'script'); return {}; },
    querySelector(selector) {
      return {
        '#consent-banner': banner,
        '[data-consent-accept]': accept,
        '[data-consent-deny]': deny,
        '#consent-title': title,
      }[selector] || null;
    },
    querySelectorAll(selector) {
      return selector === '[data-consent-open]' ? [open] : [];
    },
  };
  const window = {
    localStorage: storage,
    location: { href: url },
    addEventListener(name, listener) { windowListeners[name] = listener; },
  };
  vm.runInNewContext(source, { window, document, Date });
  return { window, scripts, banner, accept, deny, open, title, storage, windowListeners };
}

function queuedCalls(window) {
  return Array.from(window.ym?.a || [], (args) => Array.from(args));
}

test('no analytics request is made before a visitor chooses', () => {
  const page = boot();
  assert.equal(page.banner.hidden, false);
  assert.equal(page.scripts.length, 0);
  assert.equal(page.window.ym, undefined);
  assert.equal(page.window[`disableYaCounter${COUNTER}`], true);
});

test('refusal is saved and persists without loading the counter', () => {
  const storage = makeStorage();
  const first = boot(storage);
  first.deny.click();
  assert.equal(storage.getItem(KEY), 'declined');
  assert.equal(first.banner.hidden, true);
  assert.equal(first.scripts.length, 0);
  const next = boot(storage);
  assert.equal(next.banner.hidden, true);
  assert.equal(next.scripts.length, 0);
  assert.equal(next.window.ym, undefined);
});

test('acceptance loads and initializes the requested counter on each page', () => {
  const storage = makeStorage();
  const first = boot(storage);
  first.accept.click();
  assert.equal(storage.getItem(KEY), 'accepted');
  assert.equal(first.banner.hidden, true);
  assert.equal(first.scripts.length, 1);
  assert.equal(first.scripts[0].src, TAG_URL);
  assert.equal(first.scripts[0].async, true);
  const [id, method, options] = queuedCalls(first.window)[0];
  assert.equal(id, COUNTER);
  assert.equal(method, 'init');
  assert.equal(options.webvisor, true);
  assert.equal(options.clickmap, true);
  assert.equal(options.ecommerce, 'dataLayer');
  assert.equal(options.url, 'https://example.test/recipes/pasta.html');
  const next = boot(storage, 'https://example.test/about.html');
  assert.equal(next.banner.hidden, true);
  assert.equal(next.scripts.length, 1);
  assert.equal(queuedCalls(next.window)[0][2].url, 'https://example.test/about.html');
});

test('visitors can revoke and re-enable consent without a duplicate loader', () => {
  const page = boot(makeStorage({ [KEY]: 'accepted' }));
  page.open.click();
  assert.equal(page.banner.hidden, false);
  assert.equal(page.title.focused, true);
  page.deny.click();
  assert.equal(page.window[`disableYaCounter${COUNTER}`], true);
  assert.equal(page.storage.getItem(KEY), 'declined');
  assert.deepEqual(queuedCalls(page.window).map((call) => call[1]), ['init', 'destruct']);
  assert.equal(page.open.focused, true);
  page.open.click();
  page.accept.click();
  assert.equal(page.window[`disableYaCounter${COUNTER}`], false);
  assert.equal(page.scripts.length, 1);
  assert.deepEqual(queuedCalls(page.window).map((call) => call[1]), ['init', 'destruct', 'init']);
});

test('a consent change in another tab starts and stops the counter', () => {
  const storage = makeStorage();
  const page = boot(storage);
  storage.setItem(KEY, 'accepted');
  page.windowListeners.storage({ key: KEY });
  assert.equal(page.scripts.length, 1);
  assert.equal(page.banner.hidden, true);
  storage.setItem(KEY, 'declined');
  page.windowListeners.storage({ key: KEY });
  assert.equal(page.window[`disableYaCounter${COUNTER}`], true);
  assert.equal(queuedCalls(page.window).at(-1)[1], 'destruct');
  storage.removeItem(KEY);
  page.windowListeners.storage({ key: KEY });
  assert.equal(page.banner.hidden, false);
});

test('unavailable or read-only storage never restores stale consent', () => {
  const storage = {
    getItem() { return 'accepted'; },
    setItem() { throw new Error('read-only'); },
    removeItem() { throw new Error('read-only'); },
  };
  const page = boot(storage);
  assert.equal(page.banner.hidden, false);
  assert.equal(page.scripts.length, 0);
  page.accept.click();
  assert.equal(page.scripts.length, 1);
  page.open.click();
  page.deny.click();
  assert.equal(page.window[`disableYaCounter${COUNTER}`], true);
  assert.equal(boot(storage).scripts.length, 0);
});

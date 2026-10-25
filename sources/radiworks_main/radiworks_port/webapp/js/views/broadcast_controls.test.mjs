import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const priorWindow = Object.getOwnPropertyDescriptor(globalThis, 'window');
globalThis.window = { matchMedia: () => ({ matches: true }) };
const { initBroadcastView } = await import('./broadcast.js');
const { initStatusBar } = await import('./statusbar.js');
if (priorWindow) Object.defineProperty(globalThis, 'window', priorWindow);
else delete globalThis.window;

class FakeElement {
  constructor(id = '', tagName = 'div') {
    this.id = id;
    this.tagName = tagName.toUpperCase();
    this._children = [];
    this._innerHTML = '';
    this._textContent = '';
    this.listeners = new Map();
    this.attributes = {};
    this.className = '';
    this.style = {};
    this.classList = {
      values: new Set(),
      toggle: (name, force) => {
        const on = force ?? !this.classList.values.has(name);
        if (on) this.classList.values.add(name);
        else this.classList.values.delete(name);
        return on;
      },
      contains: (name) => this.classList.values.has(name),
    };
  }
  get children() { return this._children; }
  get lastChild() { return this._children.at(-1) || null; }
  get textContent() { return this._textContent || this._children.map((child) => child.textContent).join(''); }
  set textContent(value) { this._textContent = String(value); this._children = []; this._innerHTML = ''; }
  get innerHTML() { return this._innerHTML; }
  set innerHTML(value) { this._innerHTML = String(value); this._textContent = ''; this._children = []; }
  addEventListener(type, listener) {
    const listeners = this.listeners.get(type) || [];
    listeners.push(listener);
    this.listeners.set(type, listeners);
  }
  setAttribute(name, value) { this.attributes[name] = String(value); }
  append(...elements) { for (const element of elements) this.appendChild(element); }
  appendChild(element) { element.parentElement = this; this._children.push(element); this._innerHTML = ''; return element; }
  prepend(element) { element.parentElement = this; this._children.unshift(element); this._innerHTML = ''; }
  replaceChildren(...elements) { this._children = []; this._innerHTML = ''; this.append(...elements); }
  remove() {
    if (this.parentElement) this.parentElement._children = this.parentElement._children.filter((child) => child !== this);
    this.parentElement = null;
  }
  querySelector() { return null; }
  getBoundingClientRect() { return { top: 100, bottom: 120, left: 0, right: 100, width: 100, height: 20 }; }
  focus() {}
  click() {
    if (this.disabled) return;
    for (const listener of this.listeners.get('click') || []) listener({ target: this, preventDefault() {} });
  }
}

class EventHub {
  constructor() { this.listeners = new Map(); }
  addEventListener(type, listener) {
    const listeners = this.listeners.get(type) || new Set();
    listeners.add(listener);
    this.listeners.set(type, listeners);
  }
  dispatchEvent(event) {
    for (const listener of this.listeners.get(event.type) || []) listener(event);
    return true;
  }
  emit(type, detail = {}) { this.dispatchEvent(new CustomEvent(type, { detail })); }
}

class FakeCustomEvent {
  constructor(type, options = {}) { this.type = type; this.detail = options.detail; }
}

function deferred() {
  let resolve, reject;
  const promise = new Promise((yes, no) => { resolve = yes; reject = no; });
  return { promise, resolve, reject };
}

async function settle() {
  await new Promise((resolve) => setImmediate(resolve));
  await new Promise((resolve) => setImmediate(resolve));
}

function makeHarness(initialQueue = { active: [], queued: [], resonanceTotals: {} }, options = {}) {
  const globalNames = ['document', 'window', 'HTMLElement', 'CustomEvent', 'setInterval', 'alert'];
  const originals = new Map(globalNames.map((name) => [name, Object.getOwnPropertyDescriptor(globalThis, name)]));
  const elements = new Map();
  const element = (id, tagName = 'div') => {
    if (!elements.has(id)) elements.set(id, new FakeElement(id, tagName));
    return elements.get(id);
  };
  const body = element('body');
  const statusbar = element('statusbar');
  const document = {
    body,
    hidden: false,
    getElementById: (id) => element(id),
    createElement: (tagName) => new FakeElement('', tagName),
    addEventListener() {},
    querySelector: (selector) => selector === '.statusbar' ? statusbar : null,
  };
  Object.defineProperty(globalThis, 'document', { configurable: true, writable: true, value: document });
  Object.defineProperty(globalThis, 'window', { configurable: true, writable: true, value: {
    matchMedia: () => ({ matches: true }),
    addEventListener() {},
    innerHeight: 1000,
    scrollBy() {},
  } });
  Object.defineProperty(globalThis, 'HTMLElement', { configurable: true, writable: true, value: FakeElement });
  Object.defineProperty(globalThis, 'CustomEvent', { configurable: true, writable: true, value: FakeCustomEvent });
  Object.defineProperty(globalThis, 'setInterval', { configurable: true, writable: true, value: () => 1 });
  Object.defineProperty(globalThis, 'alert', { configurable: true, writable: true, value: () => {} });

  const eventBus = new EventHub();
  let queueState = initialQueue;
  let queueCalls = 0;
  const pendingStatusbarQueue = options.holdStatusbarInitialQueue ? deferred() : null;
  let stopAllCalls = 0;
  const api = {
    settings: async () => ({ booleans: {} }),
    updateSettings: async () => {},
    broadcast: async () => {},
    stopCurrent: async () => {},
    stopAll: async () => { stopAllCalls += 1; },
    queue: async () => {
      queueCalls += 1;
      if (pendingStatusbarQueue && queueCalls === 2) return pendingStatusbarQueue.promise;
      return queueState;
    },
    entropyFeed: async () => ({ feedSize: 0 }),
  };
  initBroadcastView(api, eventBus);
  initStatusBar(api, eventBus);
  return {
    api, body, elements, eventBus,
    el: (id) => element(id),
    get queueState() { return queueState; },
    set queueState(value) { queueState = value; },
    get stopAllCalls() { return stopAllCalls; },
    initialStatusbarQueue: pendingStatusbarQueue,
    restore() {
      for (const [name, descriptor] of originals) {
        if (descriptor) Object.defineProperty(globalThis, name, descriptor);
        else delete globalThis[name];
      }
    },
  };
}

function resonance(signature, resonanceCount = 1) {
  return {
    broadcastId: `${signature}-broadcast`, signature, resonanceCount,
    binaural: { left_freq: 220, right_freq: 224 },
  };
}

test('Broadcast-Reiter und Analyse-Dock bieten getrennte Aktionen mit erreichbarer Erklärung', () => {
  const html = readFileSync(new URL('../../index.html', import.meta.url), 'utf8');
  assert.match(html, /id="stop-all-btn"[^>]*>Broadcasts leeren/);
  assert.match(html, /id="dock-stop-all-btn"[^>]*>Broadcasts leeren/);
  assert.match(html, /id="clear-resonance-display-btn"[^>]*>Resonanzanzeige leeren/);
  assert.match(html, /id="dock-clear-resonance-display-btn"[^>]*>Resonanzanzeige leeren/);
  assert.match(html, /id="broadcast-controls-status"[^>]*role="status"[^>]*aria-live="polite"/);
  assert.match(html, /id="broadcast-resonance-status"[^>]*role="status"[^>]*aria-live="polite"/);
  assert.match(html, /id="dock-controls-status"[^>]*role="status"[^>]*aria-live="polite"/);
  assert.match(html, /id="dock-resonance-status"[^>]*role="status"[^>]*aria-live="polite"/);
  assert.ok((html.match(/Broadcasts dieser Instanz/g) || []).length >= 2);
  assert.match(html, /GV-Sitzungshistorie bleibt erhalten/);
});

test('beide Stop-Aktionen verwenden stopAll und melden Erfolg in beiden Ansichten', async () => {
  const h = makeHarness();
  try {
    await settle();
    h.el('stop-all-btn').click();
    await settle();
    assert.equal(h.stopAllCalls, 1);
    assert.match(h.el('broadcast-controls-status').textContent, /dieser Instanz wurden gestoppt/);
    assert.match(h.el('dock-controls-status').textContent, /Auto bleibt unverändert/);

    h.el('dock-stop-all-btn').click();
    await settle();
    assert.equal(h.stopAllCalls, 2);
    assert.match(h.el('broadcast-controls-status').textContent, /dieser Instanz wurden gestoppt/);
    assert.match(h.el('dock-controls-status').textContent, /Auto bleibt unverändert/);
  } finally { h.restore(); }
});

test('fehlgeschlagener Stop meldet den Fehler, gibt beide Buttons frei und verhindert Doppelklicks', async () => {
  const h = makeHarness();
  try {
    await settle();
    const pending = deferred();
    let stopCalls = 0;
    h.api.stopAll = () => { stopCalls += 1; return pending.promise; };
    h.el('stop-all-btn').click();
    h.el('dock-stop-all-btn').click();
    assert.equal(stopCalls, 1);
    assert.equal(h.el('stop-all-btn').disabled, true);
    assert.equal(h.el('dock-stop-all-btn').disabled, true);
    pending.reject(new Error('offline'));
    await settle();
    assert.match(h.el('broadcast-controls-status').textContent, /konnten nicht geleert werden.*offline/);
    assert.match(h.el('dock-controls-status').textContent, /konnten nicht geleert werden.*offline/);
    assert.equal(h.el('broadcast-controls-status').textContent.includes('wurden gestoppt'), false);
    assert.equal(h.el('stop-all-btn').disabled, false);
    assert.equal(h.el('dock-stop-all-btn').disabled, false);
  } finally { h.restore(); }
});
test('beide Anzeige-Aktionen leeren nur die sichtbaren Listen; neue Resonanzen erscheinen wieder', async () => {
  const h = makeHarness({ active: [], queued: [], resonanceTotals: { RATE: 1 } });
  try {
    await settle();
    h.queueState = { active: [], queued: [], resonanceTotals: { RATE: 2 } };
    h.eventBus.emit('broadcast.resonance', resonance('RATE', 2));
    await settle();
    assert.equal(h.el('resonance-list').children.length, 1);
    assert.equal(h.el('resonated-mini').children.length, 1);

    h.el('clear-resonance-display-btn').click();
    await settle();
    assert.match(h.el('resonance-list').innerHTML, /Noch keine Resonanz/);
    assert.match(h.el('resonated-mini').innerHTML, /Noch keine Resonanz/);
    assert.match(h.el('broadcast-resonance-status').textContent, /browserlokal/);
    assert.equal(h.stopAllCalls, 0, 'display clear never stops broadcasts');

    h.queueState = { active: [], queued: [], resonanceTotals: { RATE: 3 } };
    h.eventBus.emit('broadcast.resonance', resonance('RATE', 3));
    await settle();
    assert.equal(h.el('resonance-list').children.length, 1);
    assert.equal(h.el('resonated-mini').children[0]?.children[0]?.textContent || '', '1');

    h.queueState = { active: [], queued: [], resonanceTotals: { RATE: 4 } };
    h.eventBus.emit('broadcast.resonance', resonance('RATE', 4));
    await settle();
    h.el('dock-clear-resonance-display-btn').click();
    await settle();
    assert.match(h.el('resonance-list').innerHTML, /Noch keine Resonanz/);
    assert.match(h.el('resonated-mini').innerHTML, /Noch keine Resonanz/);
    assert.equal(h.stopAllCalls, 0);
  } finally { h.restore(); }
});

test('nach dem Leeren bleiben Serverdeltas maßgeblich und doppelte WS-Ereignisse zählen nicht zusätzlich', async () => {
  const h = makeHarness({ active: [], queued: [], resonanceTotals: { RATE: 4 } });
  try {
    await settle();
    h.el('dock-clear-resonance-display-btn').click();
    await settle();
    h.queueState = { active: [], queued: [], resonanceTotals: { RATE: 7 } };
    h.eventBus.emit('broadcast.progress', {});
    await settle();
    assert.equal(h.el('resonated-mini').children[0]?.children[0]?.textContent || '', '3');

    h.eventBus.emit('broadcast.resonance', resonance('RATE', 3));
    await settle();
    h.eventBus.emit('broadcast.resonance', resonance('RATE', 3));
    await settle();
    assert.equal(h.el('resonated-mini').children[0]?.children[0]?.textContent || '', '3');
  } finally { h.restore(); }
});
test('vor dem ersten Queue-Stand geleert: alte Zähler bleiben verborgen, neue Events erscheinen', async () => {
  const h = makeHarness({ active: [], queued: [], resonanceTotals: { RATE: 6 } }, { holdStatusbarInitialQueue: true });
  try {
    await settle();
    h.el('dock-clear-resonance-display-btn').click();
    h.initialStatusbarQueue.resolve({ active: [], queued: [], resonanceTotals: { RATE: 6 } });
    await settle();
    h.eventBus.emit('broadcast.progress', {});
    await settle();
    assert.match(h.el('resonated-mini').innerHTML, /Noch keine Resonanz/);

    h.queueState = { active: [], queued: [], resonanceTotals: { RATE: 7 } };
    h.eventBus.emit('broadcast.resonance', resonance('RATE', 7));
    await settle();
    assert.equal(h.el('resonated-mini').children[0]?.children[0]?.textContent || '', '1');
  } finally { h.restore(); }
});

test('Clear überholt laufenden Refresh und wartenden Kontextabruf', async () => {
  const h = makeHarness({ active: [], queued: [], resonanceTotals: { RATE: 4 } });
  try {
    await settle();
    const staleRefresh = deferred();
    let next = 0;
    h.api.queue = () => {
      next += 1;
      if (next === 1) return staleRefresh.promise;
      return Promise.resolve(h.queueState);
    };

    h.eventBus.emit('broadcast.resonance', resonance('RATE', 4));
    h.eventBus.emit('analysis.context');
    h.el('dock-clear-resonance-display-btn').click();
    h.queueState = { active: [], queued: [], resonanceTotals: { RATE: 5 } };
    h.eventBus.emit('broadcast.resonance', resonance('RATE', 5));
    staleRefresh.resolve({ active: [], queued: [], resonanceTotals: { RATE: 4, OLD: 8 } });
    await settle();
    assert.equal(h.el('resonated-mini').children[0]?.children[0]?.textContent || '', '1');
    assert.equal(h.el('resonated-mini').children.length, 1);
  } finally { h.restore(); }
});
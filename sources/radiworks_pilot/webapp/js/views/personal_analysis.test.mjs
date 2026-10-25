import test from 'node:test';
import assert from 'node:assert/strict';
import { initPersonalAnalysis } from './personal_analysis.js';

class Element {
  constructor(tagName = 'div') {
    this.tagName = tagName.toUpperCase();
    this.children = [];
    this.listeners = new Map();
    this.attributes = {};
    this.textContent = '';
    this.hidden = false;
    this.disabled = false;
    this.value = '';
    this.className = '';
  }
  addEventListener(type, listener) {
    const listeners = this.listeners.get(type) || [];
    listeners.push(listener);
    this.listeners.set(type, listeners);
  }
  setAttribute(name, value) { this.attributes[name] = value; }
  append(...elements) { this.children.push(...elements); }
  appendChild(element) { this.children.push(element); return element; }
  replaceChildren(...elements) { this.children = [...elements]; }
  click() {
    if (this.disabled) return;
    for (const listener of this.listeners.get('click') || []) listener({ target: this });
  }
}

class EventHub {
  constructor() { this.listeners = new Map(); }
  addEventListener(type, listener) {
    const listeners = this.listeners.get(type) || new Set();
    listeners.add(listener);
    this.listeners.set(type, listeners);
  }
  emit(type, detail = {}) {
    for (const listener of this.listeners.get(type) || []) listener({ detail });
  }
}

function deferred() {
  let resolve, reject;
  const promise = new Promise((yes, no) => { resolve = yes; reject = no; });
  return { promise, resolve, reject };
}

function makeJob({
  id = 'a'.repeat(32), status = 'running', completedRates = 1,
  totalRates = 1382, rows = [], updatedAt = '2026-10-06T12:00:00.000Z',
  catalog = 'Catalog A', mode = 'seeded', seed = 1,
} = {}) {
  return {
    id, requestId: id, status, createdAt: '2026-10-06T11:00:00.000Z', updatedAt,
    resultDigest: status === 'completed' ? 'f'.repeat(64) : null,
    error: null, procedure: 'EXP1', mode, seed, weight: 'Normal',
    caseId: 'c'.repeat(32), contextVersion: 1, contextDigest: 'd'.repeat(64),
    catalog: { name: catalog, sha256: 'e'.repeat(64) },
    inputDigest: '1'.repeat(64), implementationHash: '2'.repeat(64),
    completedRates, totalRates, complete: status === 'completed',
    entropy: { mode, sources: [mode === 'seeded' ? 'seeded' : 'os'], drawCount: completedRates },
    rows,
  };
}

function makeHarness(apiOverrides = {}) {
  const original = new Map(['document', 'window', 'crypto', 'setTimeout', 'clearTimeout'].map((key) => [
    key, Object.getOwnPropertyDescriptor(globalThis, key),
  ]));
  const elements = new Map();
  const timers = new Map();
  let nextTimerId = 1;
  const element = (id) => {
    if (!elements.has(id)) elements.set(id, new Element());
    return elements.get(id);
  };
  const binding = { ref: 'b'.repeat(64), contextVersion: 1 };
  const installGlobal = (key, value) => Object.defineProperty(globalThis, key, { configurable: true, writable: true, value });
  installGlobal('document', {
    getElementById: element,
    createElement: (tagName) => new Element(tagName),
    querySelector: () => new Element('button'),
  });
  installGlobal('window', { __RADIWORKS_CASE_BINDING__: binding });
  installGlobal('crypto', { randomUUID: () => String(nextTimerId++) + '-request' });
  installGlobal('setTimeout', (callback) => {
    const id = nextTimerId++;
    timers.set(id, callback);
    return id;
  });
  installGlobal('clearTimeout', (id) => timers.delete(id));

  const procedureSelect = new Element('select');
  procedureSelect.value = 'personal';
  const eventBus = new EventHub();
  const api = {
    catalogLabel: (name) => name,
    personalJobs: async () => ({ jobs: [] }),
    personalJob: async () => { throw new Error('unexpected personalJob call'); },
    startPersonal: async () => { throw new Error('unexpected startPersonal call'); },
    cancelPersonal: async () => { throw new Error('unexpected cancelPersonal call'); },
    broadcast: async () => {},
    ...apiOverrides,
  };
  const view = initPersonalAnalysis(api, eventBus, procedureSelect);
  return {
    api, binding, elements, eventBus, procedureSelect, timers, view,
    el: element,
    runNextTimer: async () => {
      const entry = timers.entries().next().value;
      assert.ok(entry, 'expected a scheduled personal-job poll');
      timers.delete(entry[0]);
      entry[1]();
      await new Promise((resolve) => setImmediate(resolve));
    },
    restore: () => {
      for (const [key, descriptor] of original) {
        if (descriptor) Object.defineProperty(globalThis, key, descriptor);
        else delete globalThis[key];
      }
    },
  };
}

async function flush() { await new Promise((resolve) => setImmediate(resolve)); }

function row(label, inputIndex = 0) {
  return { inputIndex, rate: label, score: 0.75, intensity: 0.25 };
}

test('manual refresh recovers a failed poll, updates its same job, and preserves the start lock', async () => {
  const first = makeJob({ completedRates: 567 });
  const fresher = makeJob({ completedRates: 568, updatedAt: '2026-10-06T12:00:02.000Z' });
  let latest = first;
  let personalJobCalls = 0;
  let starts = 0;
  const h = makeHarness({
    personalJobs: async () => ({ jobs: [latest] }),
    personalJob: async () => {
      personalJobCalls += 1;
      if (personalJobCalls === 1) throw new Error('temporary GET failure');
      return latest;
    },
    startPersonal: async () => { starts += 1; return first; },
  });
  try {
    await h.view.start({ database: 'Catalog A', mode: 'seeded', seed: 1, weight: 'Normal' });
    await h.runNextTimer();
    assert.match(h.el('personal-analysis-status').textContent, /Status nicht bestätigt/);
    assert.equal(h.timers.size, 0, 'a failed poll does not start an automatic retry');

    latest = fresher;
    await h.view.refresh();
    assert.match(h.el('personal-analysis-status').textContent, /568\/1382/);
    assert.equal(h.timers.size, 1, 'refresh resumes polling after the failed GET');

    await h.view.start({ database: 'Catalog B', mode: 'stochastic', seed: 0, weight: 'Normal' });
    assert.equal(starts, 1, 'the existing active job still blocks a duplicate POST');
    assert.match(h.el('personal-analysis-status').textContent, /Ein Auftrag ist noch aktiv/);
  } finally { h.restore(); }
});


test('a confirmed active POST starts polling while history GET is still pending', async () => {
  const accepted = makeJob({ completedRates: 567 });
  const progress = makeJob({ completedRates: 568, updatedAt: '2026-10-06T12:00:02.000Z' });
  let detailCalls = 0;
  const h = makeHarness({
    personalJobs: () => new Promise(() => {}),
    personalJob: async () => { detailCalls += 1; return progress; },
    startPersonal: async () => accepted,
  });
  try {
    let settled = false;
    const startPromise = h.view.start({ database: 'Catalog A', mode: 'seeded', seed: 1, weight: 'Normal' })
      .then(() => { settled = true; });
    await flush();
    assert.equal(settled, true, 'a hung history GET cannot delay start completion');
    assert.equal(h.timers.size, 1, 'the confirmed active job has a poll scheduled');
    await h.runNextTimer();
    assert.equal(detailCalls, 1);
    assert.match(h.el('personal-analysis-status').textContent, /568\/1382/);
    void startPromise;
  } finally { h.restore(); }
});
test('selecting a completed history item does not release or stop another active job', async () => {
  const active = makeJob({ id: 'a'.repeat(32), completedRates: 567 });
  const older = makeJob({
    id: 'b'.repeat(32), status: 'completed', completedRates: 39, totalRates: 39,
    rows: [row('older-rate')], catalog: 'Old catalog',
  });
  let starts = 0;
  const h = makeHarness({
    personalJobs: async () => ({ jobs: [active, older] }),
    personalJob: async () => active,
    startPersonal: async () => { starts += 1; return makeJob({ id: 'c'.repeat(32) }); },
  });
  try {
    await h.view.refresh();
    assert.match(h.el('personal-analysis-status').textContent, /vollständige sortierte Ergebnisliste erscheint erst nach Abschluss/i);
    assert.match(h.el('personal-analysis-proof').textContent, /Catalog A/);
    h.el('personal-history').children[1].click();
    assert.equal(h.el('personal-result-body').children.length, 1, 'the selected history result remains visible');
    assert.equal(h.timers.size, 1, 'polling for the active job continues');

    await h.view.start({ database: 'Catalog B', mode: 'stochastic', seed: 0, weight: 'Normal' });
    assert.equal(starts, 0, 'history selection must not permit a second POST');
    assert.match(h.el('personal-analysis-status').textContent, /Ein Auftrag ist noch aktiv/);
  } finally { h.restore(); }
});

test('a late poll for the active job does not replace a newly selected history result', async () => {
  const active = makeJob({ id: 'a'.repeat(32), completedRates: 567 });
  const older = makeJob({
    id: 'b'.repeat(32), status: 'completed', completedRates: 1, totalRates: 1,
    rows: [row('older-rate')], catalog: 'Old catalog',
  });
  const delayedPoll = deferred();
  const h = makeHarness({
    personalJobs: async () => ({ jobs: [active, older] }),
    personalJob: () => delayedPoll.promise,
    startPersonal: async () => active,
  });
  try {
    await h.view.start({ database: 'Catalog A', mode: 'seeded', seed: 1, weight: 'Normal' });
    await h.runNextTimer();
    await h.view.refresh();
    h.el('personal-history').children[1].click();
    assert.equal(h.el('personal-result-body').children[0].children[1].textContent, 'older-rate');

    delayedPoll.resolve(makeJob({ ...active, completedRates: 568 }));
    await flush();
    assert.equal(h.el('personal-result-body').children.length, 1, 'late poll must preserve the selected history rows');
    assert.equal(h.el('personal-result-body').children[0].children[1].textContent, 'older-rate');
  } finally { h.restore(); }
});

test('an empty history snapshot cannot clear a submission that is still in flight', async () => {
  const post = deferred();
  let starts = 0;
  const h = makeHarness({
    personalJobs: async () => ({ jobs: [] }),
    startPersonal: () => { starts += 1; return post.promise; },
  });
  try {
    const firstStart = h.view.start({ database: 'Catalog A', mode: 'seeded', seed: 1, weight: 'Normal' });
    await h.view.refresh();
    const secondStart = h.view.start({ database: 'Catalog B', mode: 'stochastic', seed: 0, weight: 'Normal' });
    assert.equal(starts, 1, 'an empty concurrent list response must retain the in-flight start guard');

    post.resolve(makeJob({ status: 'queued', completedRates: 0, rows: [] }));
    await Promise.all([firstStart, secondStart]);
    await flush();
  } finally { h.restore(); }
});

test('a stale active history snapshot cannot regress a terminal job or restore its lock', async () => {
  const running = makeJob({ id: 'a'.repeat(32), completedRates: 567, updatedAt: '2026-10-06T12:00:01.000Z' });
  const completed = makeJob({
    id: running.id, status: 'completed', completedRates: 1382, totalRates: 1382,
    rows: [row('final-rate')], updatedAt: '2026-10-06T12:01:00.000Z',
  });
  let listJob = running;
  let starts = 0;
  const h = makeHarness({
    personalJobs: async () => ({ jobs: [listJob] }),
    startPersonal: async () => { starts += 1; return completed; },
  });
  try {
    await h.view.start({ database: 'Catalog A', mode: 'seeded', seed: 1, weight: 'Normal' });
    await flush();
    assert.match(h.el('personal-analysis-status').textContent, /abgeschlossen/);

    listJob = running;
    await h.view.refresh();
    h.el('personal-history').children[0].click();
    assert.match(h.el('personal-analysis-status').textContent, /abgeschlossen/);
    assert.equal(h.el('personal-result-body').children[0].children[1].textContent, 'final-rate');

    await h.view.start({ database: 'Catalog B', mode: 'seeded', seed: 2, weight: 'Normal' });
    assert.equal(starts, 2, 'terminal job permits a deliberate new start; stale snapshot does not lock it');
  } finally { h.restore(); }
});



test('a delayed stale poll cannot regress a completed job returned by refresh', async () => {
  const running = makeJob({ id: 'a'.repeat(32), completedRates: 567, updatedAt: '2026-10-06T12:00:01.000Z' });
  const completed = makeJob({
    id: running.id, status: 'completed', completedRates: 1382, totalRates: 1382,
    rows: [row('final-rate')], updatedAt: '2026-10-06T12:01:00.000Z',
  });
  const delayedPoll = deferred();
  let listJob = running;
  let starts = 0;
  const h = makeHarness({
    personalJobs: async () => ({ jobs: [listJob] }),
    personalJob: () => delayedPoll.promise,
    startPersonal: async () => { starts += 1; return running; },
  });
  try {
    await h.view.start({ database: 'Catalog A', mode: 'seeded', seed: 1, weight: 'Normal' });
    await h.runNextTimer();
    listJob = completed;
    await h.view.refresh();
    assert.match(h.el('personal-analysis-status').textContent, /abgeschlossen/);

    delayedPoll.resolve(running);
    await flush();
    await flush();
    assert.match(h.el('personal-analysis-status').textContent, /abgeschlossen/);
    assert.equal(h.el('personal-result-body').children[0].children[1].textContent, 'final-rate');
    await h.view.start({ database: 'Catalog B', mode: 'seeded', seed: 2, weight: 'Normal' });
    assert.equal(starts, 2, 'stale poll cannot restore the completed job lock');
  } finally { h.restore(); }
});
test('a late cancel response does not replace a different selected history result', async () => {
  const active = makeJob({ id: 'a'.repeat(32), completedRates: 567 });
  const older = makeJob({
    id: 'b'.repeat(32), status: 'completed', completedRates: 1, totalRates: 1,
    rows: [row('older-rate')], catalog: 'Old catalog',
  });
  const cancel = deferred();
  const h = makeHarness({
    personalJobs: async () => ({ jobs: [active, older] }),
    personalJob: async () => { throw new Error('temporary GET failure'); },
    cancelPersonal: () => cancel.promise,
    startPersonal: async () => active,
  });
  try {
    await h.view.start({ database: 'Catalog A', mode: 'seeded', seed: 1, weight: 'Normal' });
    await h.view.refresh();
    h.el('personal-cancel').click();
    h.el('personal-history').children[1].click();
    cancel.resolve(makeJob({ ...active, status: 'cancelled', completedRates: 567 }));
    await flush();
    assert.equal(h.el('personal-result-body').children.length, 1, 'late cancel must preserve the selected history rows');
    assert.equal(h.el('personal-result-body').children[0].children[1].textContent, 'older-rate');
  } finally { h.restore(); }
});

test('personal stochastic readiness is independent of Original recovery availability', async () => {
  const { analyzeStartReadiness } = await import('./analyze.js');
  assert.equal(typeof analyzeStartReadiness, 'function');

  const blockedOriginalRecovery = {
    activeCase: true,
    available: false,
  };
  assert.deepEqual(analyzeStartReadiness({
    procedure: 'personal', mode: 'stochastic',
    entropyStatus: { stochasticRecovery: blockedOriginalRecovery },
    analysisBusy: false, catalogsReady: true,
  }), { disabled: false, noteHidden: true, noteText: '' });
  assert.deepEqual(analyzeStartReadiness({
    procedure: 'original', mode: 'stochastic',
    entropyStatus: { stochasticRecovery: blockedOriginalRecovery },
    analysisBusy: false, catalogsReady: true,
  }), {
    disabled: true, noteHidden: false,
    noteText: 'Fallgebundene stochastic-Recovery ist nicht verfügbar. Bitte seeded verwenden oder die Betreiberkonfiguration prüfen.',
  });
  assert.equal(analyzeStartReadiness({
    procedure: 'personal', mode: 'stochastic',
    entropyStatus: null, analysisBusy: false, catalogsReady: false,
  }).disabled, true);
});
test('a late start response does not replace history selected while the POST is pending', async () => {
  const first = makeJob({ id: 'a'.repeat(32), status: 'completed', completedRates: 1, totalRates: 1, rows: [row('first-rate')] });
  const selected = makeJob({ id: 'b'.repeat(32), status: 'completed', completedRates: 1, totalRates: 1, rows: [row('selected-rate')] });
  const post = deferred();
  const h = makeHarness({
    personalJobs: async () => ({ jobs: [first, selected] }),
    startPersonal: () => post.promise,
  });
  try {
    await h.view.refresh();
    const starting = h.view.start({ database: 'Catalog C', mode: 'seeded', seed: 3, weight: 'Normal' });
    h.el('personal-history').children[1].click();
    post.resolve(makeJob({ id: 'c'.repeat(32), status: 'queued', completedRates: 0, rows: [] }));
    await starting;
    assert.equal(h.el('personal-result-body').children.length, 1, 'late start response must preserve selected history rows');
    assert.equal(h.el('personal-result-body').children[0].children[1].textContent, 'selected-rate');
  } finally { h.restore(); }
});

test('a late POST response after case.changed cannot replace the new case or keep its start locked', async () => {
  const oldPost = deferred();
  const oldRef = 'b'.repeat(64);
  const newRef = 'd'.repeat(64);
  const newCaseJob = makeJob({ id: 'b'.repeat(32), status: 'completed', rows: [row('new-case-rate')] });
  const newActive = makeJob({ id: 'c'.repeat(32), status: 'running', completedRates: 1, catalog: 'New catalog' });
  let starts = 0;
  const h = makeHarness({
    personalJobs: async (ref) => ({ jobs: ref === newRef ? [newCaseJob] : [] }),
    startPersonal: () => (++starts === 1 ? oldPost.promise : Promise.resolve(newActive)),
  });
  try {
    const oldStart = h.view.start({ database: 'Old catalog', mode: 'seeded', seed: 1, weight: 'Normal' });
    h.binding.ref = newRef;
    h.binding.contextVersion = 2;
    h.eventBus.emit('case.changed');
    await h.view.refresh();

    oldPost.resolve(makeJob({ id: 'a'.repeat(32), status: 'running', completedRates: 1, catalog: 'Old catalog' }));
    await oldStart;
    assert.equal(h.el('personal-result-body').children[0].children[1].textContent, 'new-case-rate');

    await h.view.start({ database: 'New catalog', mode: 'seeded', seed: 2, weight: 'Normal' });
    assert.equal(starts, 2, 'old accepted POST must not block a new-case start');
    assert.match(h.el('personal-analysis-proof').textContent, /New catalog/);
  } finally { h.restore(); }
});

test('a late poll response after case.changed cannot replace the new case or restore the old lock', async () => {
  const oldPoll = deferred();
  const newRef = 'd'.repeat(64);
  const oldActive = makeJob({ id: 'a'.repeat(32), completedRates: 1 });
  const newCaseJob = makeJob({ id: 'b'.repeat(32), status: 'completed', rows: [row('new-case-rate')] });
  let starts = 0;
  const h = makeHarness({
    personalJobs: async (ref) => ({ jobs: ref === newRef ? [newCaseJob] : [oldActive] }),
    personalJob: () => oldPoll.promise,
    startPersonal: async () => { starts += 1; return oldActive; },
  });
  try {
    await h.view.start({ database: 'Old catalog', mode: 'seeded', seed: 1, weight: 'Normal' });
    await h.runNextTimer();

    h.binding.ref = newRef;
    h.binding.contextVersion = 2;
    h.eventBus.emit('case.changed');
    await h.view.refresh();
    oldPoll.resolve(makeJob({ ...oldActive, completedRates: 2, catalog: 'Old catalog' }));
    await flush();
    assert.equal(h.el('personal-result-body').children[0].children[1].textContent, 'new-case-rate');

    await h.view.start({ database: 'New catalog', mode: 'seeded', seed: 2, weight: 'Normal' });
    assert.equal(starts, 2, 'old poll must not restore an active-job lock in the new case');
  } finally { h.restore(); }
});

test('a late cancel response after case.changed cannot replace the new case or restore the old lock', async () => {
  const oldCancel = deferred();
  const newRef = 'd'.repeat(64);
  const oldActive = makeJob({ id: 'a'.repeat(32), completedRates: 1 });
  const newCaseJob = makeJob({ id: 'b'.repeat(32), status: 'completed', rows: [row('new-case-rate')] });
  let starts = 0;
  const h = makeHarness({
    personalJobs: async (ref) => ({ jobs: ref === newRef ? [newCaseJob] : [oldActive] }),
    cancelPersonal: () => oldCancel.promise,
    startPersonal: async () => { starts += 1; return oldActive; },
  });
  try {
    await h.view.start({ database: 'Old catalog', mode: 'seeded', seed: 1, weight: 'Normal' });
    h.el('personal-cancel').click();

    h.binding.ref = newRef;
    h.binding.contextVersion = 2;
    h.eventBus.emit('case.changed');
    await h.view.refresh();
    oldCancel.resolve(makeJob({ ...oldActive, status: 'running', completedRates: 2 }));
    await flush();
    assert.equal(h.el('personal-result-body').children[0].children[1].textContent, 'new-case-rate');

    await h.view.start({ database: 'New catalog', mode: 'seeded', seed: 2, weight: 'Normal' });
    assert.equal(starts, 2, 'old cancel response must not restore an active-job lock in the new case');
  } finally { h.restore(); }
});
test('responses from an old case cannot replace the new case history', async () => {
  const oldRead = deferred();
  const oldJob = makeJob({ id: 'a'.repeat(32), status: 'completed', rows: [row('old-case-rate')] });
  const newJob = makeJob({ id: 'b'.repeat(32), status: 'completed', rows: [row('new-case-rate')] });
  let calls = 0;
  const h = makeHarness({
    personalJobs: () => (++calls === 1 ? oldRead.promise : Promise.resolve({ jobs: [newJob] })),
  });
  try {
    const oldRefresh = h.view.refresh();
    h.binding.ref = 'd'.repeat(64);
    h.eventBus.emit('case.changed');
    await h.view.refresh();
    oldRead.resolve({ jobs: [oldJob] });
    await oldRefresh;
    assert.equal(h.el('personal-result-body').children[0].children[1].textContent, 'new-case-rate');
    assert.doesNotMatch(h.el('personal-analysis-status').textContent, /old-case-rate/);
  } finally { h.restore(); }
});

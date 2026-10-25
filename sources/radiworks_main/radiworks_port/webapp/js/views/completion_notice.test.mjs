import test from 'node:test';
import assert from 'node:assert/strict';
import {
  completionNoticeText,
  createCompletionDeduper,
  initCompletionNotice,
  isFinishedBroadcast,
} from './completion_notice.js';

const broadcastId = 'a'.repeat(32);

class EventHub {
  listeners = new Map();
  addEventListener(type, listener) {
    const listeners = this.listeners.get(type) || new Set();
    listeners.add(listener);
    this.listeners.set(type, listeners);
  }
  removeEventListener(type, listener) {
    this.listeners.get(type)?.delete(listener);
  }
  emit(type, detail) {
    for (const listener of this.listeners.get(type) || []) listener({ detail });
  }
}

test('only successful finished progress events qualify for a notice', () => {
  assert.equal(isFinishedBroadcast({ finished: true }), true);
  assert.equal(isFinishedBroadcast({ finished: true, stopped: true }), false);
  assert.equal(isFinishedBroadcast({ finished: true, failed: true }), false);
  assert.equal(isFinishedBroadcast({ stopped: true }), false);
  assert.equal(isFinishedBroadcast({ failed: true }), false);
  assert.equal(isFinishedBroadcast({ progress: 1 }), false);
});

test('notice uses an opaque job summary and never renders signatures or personal references', () => {
  const jobId = 'b'.repeat(32);
  const secretSignature = 'Private Person / Sensitive focus';
  const text = completionNoticeText({
    broadcastId,
    finished: true,
    signature: secretSignature,
    targetReference: {
      jobId,
      caseId: 'c'.repeat(32),
      source: { personalJobId: 'd'.repeat(32) },
    },
  });
  assert.equal(text, 'Broadcast abgeschlossen · Auftrag bbbbbbbb.');
  assert.equal(text.includes(secretSignature), false);
  assert.equal(text.includes('c'.repeat(32)), false);
  assert.equal(text.includes('d'.repeat(32)), false);
});

test('notice falls back only to a shortened opaque broadcast ID', () => {
  assert.equal(
    completionNoticeText({ broadcastId, finished: true, signature: 'private' }),
    'Broadcast abgeschlossen · Broadcast aaaaaaaa.',
  );
  assert.equal(completionNoticeText({ broadcastId: 'private', finished: true }), null);
});

test('deduplication suppresses replays and keeps only a bounded recent set', () => {
  const deduper = createCompletionDeduper(2);
  const first = '1'.repeat(32);
  const second = '2'.repeat(32);
  const third = '3'.repeat(32);
  assert.equal(deduper.accept(first), true);
  assert.equal(deduper.accept(first), false);
  assert.equal(deduper.accept(second), true);
  assert.equal(deduper.accept(third), true);
  assert.equal(deduper.size, 2);
  assert.equal(deduper.accept(second), false);
  assert.equal(deduper.accept(first), true);
  assert.equal(deduper.size, 2);
});

test('view honors explicit preference changes and ignores a stale initial settings read', async () => {
  const originalDocument = Object.getOwnPropertyDescriptor(globalThis, 'document');
  const node = { hidden: false, textContent: '', attributes: {}, setAttribute(key, value) { this.attributes[key] = value; } };
  globalThis.document = { getElementById: (id) => id === 'broadcast-completion-notice' ? node : null };
  let resolveInitialSettings;
  const api = { settings: () => new Promise((resolve) => { resolveInitialSettings = resolve; }) };
  const eventBus = new EventHub();
  try {
    const dispose = initCompletionNotice(api, eventBus);
    assert.equal(node.attributes.role, 'status');
    assert.equal(node.attributes['aria-live'], 'polite');
    assert.equal(node.attributes['aria-atomic'], 'true');
    assert.equal(node.hidden, true);

    eventBus.emit('broadcast.progress', { broadcastId, finished: true });
    assert.equal(node.textContent, '');
    assert.equal(node.hidden, true);

    eventBus.emit('settings.changed', { booleans: { 'broadcast.localCompletionNotice': true } });
    resolveInitialSettings({ booleans: { 'broadcast.localCompletionNotice': false } });
    await new Promise((resolve) => setImmediate(resolve));

    eventBus.emit('broadcast.progress', {
      broadcastId,
      finished: true,
      targetReference: { jobId: 'e'.repeat(32) },
    });
    assert.equal(node.textContent, 'Broadcast abgeschlossen · Auftrag eeeeeeee.');
    assert.equal(node.hidden, false);
    eventBus.emit('broadcast.progress', { broadcastId, finished: true, failed: true });
    assert.equal(node.textContent, 'Broadcast abgeschlossen · Auftrag eeeeeeee.');
    assert.equal(node.hidden, false);

    eventBus.emit('broadcast.progress', { broadcastId: 'invalid', finished: true });
    assert.equal(node.textContent, '');
    assert.equal(node.hidden, true);
    eventBus.emit('settings.changed', { booleans: { 'broadcast.localCompletionNotice': false } });
    assert.equal(node.textContent, '');
    assert.equal(node.hidden, true);
    dispose();
    eventBus.emit('broadcast.progress', { broadcastId: 'f'.repeat(32), finished: true });
    assert.equal(node.textContent, '');
    assert.equal(node.hidden, true);
  } finally {
    if (originalDocument) Object.defineProperty(globalThis, 'document', originalDocument);
    else delete globalThis.document;
  }
});
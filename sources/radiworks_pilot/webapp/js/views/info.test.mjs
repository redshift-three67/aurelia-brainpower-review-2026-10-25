import test from 'node:test';
import assert from 'node:assert/strict';
import { initInfoView } from './info.js';

test('unavailable entropy status is explained without unhandled rejection', async () => {
  const prior = Object.getOwnPropertyDescriptor(globalThis, 'document');
  const list = { textContent: '', children: [], append(...items) { this.children.push(...items); } };
  globalThis.document = { getElementById: () => list, createElement: () => ({ textContent: '' }) };
  try {
    initInfoView({ manifest: () => new Promise(() => {}), entropyStatus: () => Promise.reject(new Error('synthetic unavailable status')) });
    await new Promise(resolve => setImmediate(resolve));
    assert.match(list.textContent, /Entropie-Status.*nicht erreichbar/);
  } finally {
    if (prior) Object.defineProperty(globalThis, 'document', prior); else delete globalThis.document;
  }
});
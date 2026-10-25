import test from 'node:test';
import assert from 'node:assert/strict';
import {
  OPTIONS_VERSION,
  OPTIONS_VERSION_KEY,
  SETTING_DESCRIPTIONS,
  buildSettingsUpdate,
  displayValues,
  visibleKeys,
} from './settings-policy.js';

test('the settings policy exposes only supported active controls', () => {
  const keys = visibleKeys();
  assert.deepEqual(keys.booleans.slice().sort(), [
    'analysis.very.high.max.hit',
    'broadcast.delta.time',
    'broadcast.legacyMixMode',
    'broadcast.localCompletionNotice',
    'broadcast.single.rates.only',
    'dynamic.adjustments',
    'play.binaural.sound',
  ].sort());
  assert.deepEqual(keys.integers.slice().sort(), [
    'broadcast.adjustment.maxFollowups',
    'broadcast.adjustment.minSeconds',
  ].sort());
  assert.deepEqual(keys.strings, ['entropy.defaultMode']);

  for (const hidden of [
    'broadcast.embedded',
    'notification.after.broadcast',
    'power.switch',
    'use.overlay',
    'watchlist.activate',
    'future.safety.option',
  ]) {
    assert.equal(
      Object.values(keys).some((group) => group.includes(hidden)),
      false,
      hidden + ' must remain hidden',
    );
  }
});

test('legacy True values appear off until the explicit policy gate is saved', () => {
  const stored = {
    booleans: {
      'broadcast.single.rates.only': true,
      'broadcast.delta.time': true,
      'dynamic.adjustments': true,
      'broadcast.localCompletionNotice': true,
    },
    integers: {},
    strings: { 'entropy.defaultMode': 'seeded' },
  };
  const shown = displayValues(stored);
  assert.equal(shown.booleans['broadcast.single.rates.only'], false);
  assert.equal(shown.booleans['broadcast.delta.time'], false);
  assert.equal(shown.booleans['dynamic.adjustments'], false);
  assert.equal(shown.booleans['broadcast.localCompletionNotice'], true);
  assert.equal(stored.booleans['broadcast.single.rates.only'], true);
  assert.equal(stored.booleans['broadcast.delta.time'], true);
  assert.equal(stored.booleans['dynamic.adjustments'], true);
});

test('an explicit options-v1 gate makes stored legacy values visible', () => {
  const shown = displayValues({
    booleans: {
      'broadcast.single.rates.only': true,
      'broadcast.delta.time': true,
      'dynamic.adjustments': true,
    },
    integers: {},
    strings: { [OPTIONS_VERSION_KEY]: OPTIONS_VERSION },
  });
  assert.equal(shown.booleans['broadcast.single.rates.only'], true);
  assert.equal(shown.booleans['broadcast.delta.time'], true);
  assert.equal(shown.booleans['dynamic.adjustments'], true);
});

test('save merges visible edits into stored state and preserves hidden and unknown keys', () => {
  const stored = {
    name: 'Settings',
    booleans: {
      'notification.after.broadcast': true,
      'broadcast.embedded': true,
      'future.hidden': true,
      'broadcast.single.rates.only': true,
    },
    integers: { 'private.future.limit': 73 },
    strings: { 'private.future.mode': 'kept', 'entropy.defaultMode': 'seeded' },
  };
  const before = JSON.stringify(stored);
  const update = buildSettingsUpdate(stored, {
    booleans: {
      'broadcast.single.rates.only': false,
      'broadcast.localCompletionNotice': true,
      'notification.after.broadcast': false,
      'unknown.injected': true,
    },
    integers: { 'broadcast.adjustment.maxFollowups': 2, 'private.future.limit': 0 },
    strings: { 'entropy.defaultMode': 'stochastic', 'private.future.mode': 'changed' },
  });

  assert.equal(update.booleans['broadcast.single.rates.only'], false);
  assert.equal(update.booleans['broadcast.localCompletionNotice'], true);
  assert.equal(update.booleans['notification.after.broadcast'], true);
  assert.equal(update.booleans['broadcast.embedded'], true);
  assert.equal(update.booleans['future.hidden'], true);
  assert.equal(Object.hasOwn(update.booleans, 'unknown.injected'), false);
  assert.equal(update.integers['private.future.limit'], 73);
  assert.equal(update.integers['broadcast.adjustment.maxFollowups'], 2);
  assert.equal(update.strings['private.future.mode'], 'kept');
  assert.equal(update.strings['entropy.defaultMode'], 'stochastic');
  assert.equal(update.strings[OPTIONS_VERSION_KEY], OPTIONS_VERSION);
  assert.equal(JSON.stringify(stored), before);
});

test('defaults and numeric bounds are explicit and descriptions avoid unsupported claims', () => {
  assert.equal(SETTING_DESCRIPTIONS['broadcast.localCompletionNotice'].default, false);
  assert.equal(SETTING_DESCRIPTIONS['broadcast.adjustment.maxFollowups'].default, 1);
  assert.equal(SETTING_DESCRIPTIONS['broadcast.adjustment.maxFollowups'].min, 0);
  assert.equal(SETTING_DESCRIPTIONS['broadcast.adjustment.maxFollowups'].max, 3);
  assert.equal(SETTING_DESCRIPTIONS['broadcast.adjustment.minSeconds'].default, 10);
  assert.equal(SETTING_DESCRIPTIONS['broadcast.adjustment.minSeconds'].min, 1);
  assert.equal(SETTING_DESCRIPTIONS['broadcast.adjustment.minSeconds'].max, 86400);
  assert.match(SETTING_DESCRIPTIONS['analysis.very.high.max.hit'].help, /100.*1000/);
  assert.match(SETTING_DESCRIPTIONS['analysis.very.high.max.hit'].help, /manuelle Auswahl/i);
});

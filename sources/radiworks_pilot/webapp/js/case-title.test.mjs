import { test } from 'node:test';
import assert from 'node:assert/strict';
import { contextTitlePreview } from './case-title.js';

test('automatic title combines personal fields and focus without changing the input', () => {
  const personal={firstName:' Ada ',lastName:'Mu\u0308ller',birthDate:'1980-02-29',place:' Augsburg ',placeKind:'birth'};
  const before=JSON.stringify(personal);
  assert.equal(contextTitlePreview(personal,' Balance '),'Ada Müller 29021980 Augsburg - Balance');
  assert.equal(JSON.stringify(personal),before);
});
test('only the explicitly active location is included', () => {
  assert.equal(contextTitlePreview({firstName:'Ada',place:'Berlin'},''),'Ada');
  assert.equal(contextTitlePreview({firstName:'Ada',place:'Berlin',placeKind:'residence'},''),'Ada Berlin');
});
test('partial context and focus do not produce empty separators', () => {
  assert.equal(contextTitlePreview({lastName:'Example'},''),'Example');
  assert.equal(contextTitlePreview({},'Ruhe'),'Ruhe');
  assert.equal(contextTitlePreview({},''),'Neuer Fall (ID beim Speichern)');
});
test('display text is preserved rather than turned into a file path', () => {
  const focus='Richtung A/B: Ruhe '+ 'x'.repeat(220);
  assert.equal(contextTitlePreview({firstName:'Ada'},focus),'Ada - '+focus);
});

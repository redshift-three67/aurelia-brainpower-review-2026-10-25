import test from 'node:test';
import assert from 'node:assert/strict';
import { caseJobGuard, analysisJobOrigin } from './job-context.js';
test('explicitly guards the displayed selection, including no-case', () => {
  assert.deepEqual(caseJobGuard(null), {expected_case_ref:null,expected_context_version:null});
  const selection={ref:'a'.repeat(64),contextVersion:3};
  assert.deepEqual(caseJobGuard(selection), {expected_case_ref:selection.ref,expected_context_version:3});
  assert.equal(selection.contextVersion,3);
});
test('does not silently downgrade invalid displayed identity to no-case', () => {
  for (const selection of [{ref:'x'}, {ref:'a'.repeat(64),contextVersion:0}, {ref:'a'.repeat(64),contextVersion:'3'}]) {
    assert.throws(() => caseJobGuard(selection), /Fallbindung/);
  }
});

test('result broadcast keeps immutable draft origin without a status response', () => {
  const draft='12345678-1234-1234-1234-123456789abc';
  assert.deepEqual(analysisJobOrigin(draft,null),{source_draft_id:draft});
  assert.deepEqual(analysisJobOrigin(draft,'a'.repeat(32)),{source_draft_id:draft});
  assert.deepEqual(analysisJobOrigin(null,'a'.repeat(32)),{source_session_id:'a'.repeat(32)});
  for (const values of [[null,null],['wrong',null],[null,'wrong']]) assert.throws(()=>analysisJobOrigin(...values),/Analyseherkunft/);
});

const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

const source = fs.readFileSync('governor_workbench/static/app.js', 'utf8');
const start = source.indexOf('  async function api(');
const end = source.indexOf('\n  function connection(', start);
assert(start >= 0 && end > start);
const delays = [];
const context = {
  AbortController: class {constructor() {this.signal = {}; } abort() {}},
  setTimeout: (_, delay) => {delays.push(delay); return 1;}, clearTimeout() {},
  fetch: async () => ({ok: true, json: async () => ({ok: true})}),
  state: {csrf_token: 'fixture'},
};
vm.createContext(context);
vm.runInContext(source.slice(start, end), context);

(async () => {
  await context.api('/api/scope?kind=group&id=aurelia-integration');
  assert.equal(delays.at(-1), 180000, 'Full local group intake needs the measured multi-project scan window');
  await context.api('/api/actions', {action: 'scope_route_b_review', scope_kind: 'group', scope_id: 'aurelia-integration'});
  assert.equal(delays.at(-1), 180000, 'Route-B admission performs the same full scope scan');
  await context.api('/api/actions', {action: 'scope_review'});
  assert.equal(delays.at(-1), 25000, 'Existing action timeout stays unchanged');
  await context.api('/api/state');
  assert.equal(delays.at(-1), 25000, 'Ordinary polling retains the short timeout');
  console.log('Route B UI: long scoped scans and normal requests have separate deadlines.');
})().catch(error => {console.error(error); process.exitCode = 1;});

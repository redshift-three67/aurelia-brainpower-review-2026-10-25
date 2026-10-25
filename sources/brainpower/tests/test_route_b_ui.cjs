const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

const source = fs.readFileSync('governor_workbench/static/app.js', 'utf8');
const start = source.indexOf('  const registryRoles = ');
const end = source.indexOf('  function intakeDraftKey(', start);
assert(start >= 0 && end > start);
const buttons = [], calls = [];
const project = {id: 'p', name: 'Pilot', model_egress: true, archived: false};
const state = {registry: {projects: [project], groups: []}};
const supervisor = {value: 'gpt-5.6-sol'};
const context = {
  state, intakeScope: null, pending: new Set(), intakeRequest: 0, document: {createTextNode: text => ({text})},
  node(tag, cls, text) {
    const value = {tag, cls, text, dataset: {}, children: [], append(...items) {this.children.push(...items);},
      addEventListener(name, handler) {this[name] = handler;}};
    if (tag === 'button') buttons.push(value);
    return value;
  },
  $: id => id === 'supervisor' ? supervisor : {},
  registryControls() {}, notify() {}, activateTab() {}, loadState: async () => {},
  api: async (path, body) => {calls.push({path, body}); return {job: {id: 'synthetic'}};},
  encodeURIComponent,
};
vm.createContext(context);
vm.runInContext(source.slice(start, end), context);

(async () => {
  const section = context.scopeActions('project', 'p');
  assert(section.children.some(child => child.tag === 'p' && child.text.includes('Sol High → Luna Max')));
  const byAction = action => buttons.find(button => button.dataset.scopeAction === action);
  assert(byAction('scope_review') && byAction('scope_route_b_review') && byAction('scope_route_b_plan'));
  assert.equal(context.scopeBlocked('scope_route_b_plan', 'project', 'p'), true);
  assert.equal(context.scopeBlocked('scope_route_b_review', 'project', 'p'), false);
  const checkbox = section.children.find(child => child.tag === 'label').children[0];
  checkbox.checked = true;
  await byAction('scope_route_b_review').click();
  assert.equal(calls.at(-1).path, '/api/actions');
  assert.equal(calls.at(-1).body.action, 'scope_route_b_review');
  assert.equal(calls.at(-1).body.critical_review, true);
  await byAction('scope_review').click();
  assert.equal(calls.at(-1).body.action, 'scope_review');
  assert.equal('critical_review' in calls.at(-1).body, false);
  project.model_egress = false;
  assert.equal(context.scopeBlocked('scope_route_b_review', 'project', 'p'), true);
  console.log('Route B UI: separate actions, plan gate, explicit Astra choice and model-egress gate verified.');
})().catch(error => {console.error(error); process.exitCode = 1;});

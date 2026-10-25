const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

const source = fs.readFileSync('governor_workbench/static/app.js', 'utf8');
const start = source.indexOf('  const scopedReviewActions = ');
const end = source.indexOf('\n  function renderGovernance(', start);
assert.ok(start >= 0 && end > start, 'Scoped review status logic is present');
const c = {labels:{scope_route_b_review:'Route B'},stamp:value=>value};
vm.createContext(c);
vm.runInContext(source.slice(start,end),c);

const result = {scope_hash:'h1',review_scope:{kind:'project',id:'radiworks'},
  review:{decision:'REVIEW_ONLY',summary:'Scope checked'},stale:false,freshness:'recently_observed'};
const job = {action:'scope_route_b_review',request:{scope_kind:'project',scope_id:'radiworks'},
  status:'completed',created_at:'2026-09-24T10:00:00Z',result};
const observation = {kind:'project',id:'radiworks',scope_hash:'h1',stale:false,observed_at:'2026-09-25T10:00:00Z'};
function check(changes={},expected='current') {
  c.state = {jobs:[{...job,...changes,result:{...result,...changes.result}}],
    registry:{observations:[{...observation,...changes.observation}]}};
  assert.equal(c.reviewScopeState('project','radiworks').kind,expected);
}
check();
check({result:{stale:true}},'historical');
check({result:{freshness:'unknown_requires_rescan'}},'historical');
check({result:{scope_hash:'h2'}},'historical');
check({observation:{stale:true}},'historical');
check({result:{review:{decision:'ALLOW',summary:'Invalid grant'}}},'historical');
check({status:'failed'},'historical');
assert.equal(c.reviewScopeState('group','aurelia').kind,'unreviewed','Project review never validates group scope');
c.state.jobs = [{...job,action:'scope_compare',result:{...result,comparison:{complete:true},success:true}}];
assert.equal(c.reviewScopeState('project','radiworks').kind,'current');
c.state.jobs[0].result.comparison.complete = false;
assert.equal(c.reviewScopeState('project','radiworks').kind,'historical');
c.state.jobs = [{...job,action:'scope_review',result:{...result}}];
assert.equal(c.reviewScopeState('project','radiworks').kind,'current');
c.state.registry.observations = [];
c.state.registry.recent_scope_observations = [{...observation,observed_at:'2026-09-25T10:00:00Z'}];
assert.equal(c.reviewScopeState('project','radiworks').kind,'current','Fresh scope cache supports a grouped project absent from ScopeMonitor rotation');
c.state.registry.recent_scope_observations[0].stale = true;
assert.equal(c.reviewScopeState('project','radiworks').kind,'historical','Stale fallback never synchronizes a review');
const later = '2026-09-25T10:01:00Z';
c.state.jobs = [{...job,result:{...result,scope_hash:'h2'}}];
c.state.registry.observations = [{...observation}];
c.state.registry.recent_scope_observations = [{...observation,scope_hash:'h2',observed_at:later}];
assert.equal(c.reviewScopeState('project','radiworks').kind,'current','Newer recent hash takes precedence over older primary hash');
c.state.registry.observations[0].observed_at = '2026-09-25T10:02:00Z';
assert.equal(c.reviewScopeState('project','radiworks').kind,'historical','Newer primary hash cannot be displaced by older matching recent hash');
c.state.registry.recent_scope_observations[0].observed_at = '2026-09-25T10:02:00Z';
assert.equal(c.reviewScopeState('project','radiworks').kind,'current','Recent cache wins an equal-timestamp tie');

const options = c.matrixScopeOptions([{id:'group',name:'Aurelia',members:[{project_id:'radiworks'}]}],
  new Map([['radiworks','RadiWorks'],['standalone','Eigenständig']]),
  [{id:'radiworks',group_id:'group',archived:false},{id:'standalone',group_id:null,archived:false}]);
assert.equal(options[0].key,'group:group','First active group is the initial matrix choice');
assert.equal(options[0].ids.join(','),'radiworks','Group selection excludes standalone projects');
assert.equal(options.find(option=>option.key==='project:standalone').ids.join(','),'standalone');
assert.match(options.find(option=>option.key==='project:radiworks').label,/^Modul einzeln:/);
assert.match(options.find(option=>option.key==='project:standalone').label,/^Einzelprojekt:/);
const archived = c.matrixScopeOptions([{id:'group',name:'Aurelia',members:[{project_id:'radiworks'},{project_id:'old'},{project_id:'unregistered'}]}],
  new Map([['radiworks','RadiWorks'],['old','Archiv'],['unregistered','Lokal beobachtet']]),
  [{id:'radiworks',group_id:'group',archived:false},{id:'old',group_id:'group',archived:true}]);
assert.equal(archived[0].ids.join(','),'radiworks,unregistered','Archived member is excluded; locally observed member without registry row remains visible');
assert.equal(archived.some(option=>option.key==='project:old'),false,'Archived member is not selectable');
assert.ok(archived.some(option=>option.key==='project:unregistered'),'Unregistered observed project remains selectable');

(async()=>{
  const calls=[]; c.pending=new Set(); c.api=async path=>{calls.push(path);return {};};
  c.loadState=async()=>true; c.notify=()=>{}; c.scopeName=()=> 'RadiWorks'; c.renderStatusPages=()=>{};
  await c.refreshReviewScope('project','radiworks',{disabled:false});
  assert.deepEqual(calls,['/api/scope?kind=project&id=radiworks&fresh=1'],'Manual refresh forces one read-only local scope scan');
  console.log('Review status, grouped cache fallback, matrix scope isolation and manual local refresh checked.');
})().catch(error=>{console.error(error);process.exitCode=1;});

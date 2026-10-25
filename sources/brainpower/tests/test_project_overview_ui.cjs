const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

const source = fs.readFileSync('governor_workbench/static/app.js', 'utf8');
const html = fs.readFileSync('governor_workbench/static/index.html', 'utf8');

function functionSource(name) {
  const match = new RegExp(`^  function ${name}\\(`, 'm').exec(source);
  assert.ok(match, `app.js defines ${name}`);
  const rest = source.slice(match.index);
  const next = /\n  (?:async )?function /.exec(rest);
  return next ? rest.slice(0, next.index) : rest;
}

class Element {
  constructor(tag = 'div', className = '', text = '') {
    this.tagName = tag.toUpperCase();
    this.className = className;
    this.textContent = text;
    this.children = [];
    this.dataset = {};
    this.attributes = {};
    this.listeners = {};
    this.hidden = false;
    this.disabled = false;
  }
  append(...children) { this.children.push(...children); }
  replaceChildren(...children) { this.children = children; }
  addEventListener(type, listener) { this.listeners[type] = listener; }
  setAttribute(name, value) { this.attributes[name] = String(value); }
  scrollIntoView() {}
  focus() { this.focused = true; }
  click() { if (!this.disabled) this.listeners.click?.({currentTarget:this}); }
  get textContentDeep() { return [this.textContent, ...this.children.map(child => child.textContentDeep || child.textContent || '')].join(' '); }
}

function fixture() {
  const elements = new Map();
  const c = {
    state: {registry:{groups:[],projects:[]},jobs:[],governor:{steps:[]}},
    focusedScope: null,
    currentTab: 'directory',
    intakeScope: null,
    plansScope: null,
    document: {createTextNode: text => new Element('#text', '', text)},
    node: (tag, className, text) => new Element(tag, className, text),
    $: id => { if (!elements.has(id)) elements.set(id, new Element()); return elements.get(id); },
    projectName: id => c.state.registry.projects.find(project => project.id === id)?.name || id,
    scopeName: (kind,id) => kind === 'group' ? c.state.registry.groups.find(group => group.id === id)?.name || id : c.projectName(id),
    registryRoles: {parent:'Hauptprojekt',module:'Modul',contracts:'Verträge / Schnittstellen',member:'Mitglied'},
    reviewScopeState: () => ({kind:'unreviewed',label:'Noch kein Review',detail:'Kein aktueller Reviewnachweis.'}),
    reviewIndicator: info => new Element('span',`status-indicator ${info.kind}`,info.label),
    set: (id,text) => { c.$(id).textContent = text; },
    activateTab: name => { c.currentTab = name; },
    scopeActions: () => new Element('div','scope-actions'),
    renderRegistryObservations: () => {},
    governanceSteps: () => c.state.governor.steps,
    registryControls: () => {},
  };
  vm.createContext(c);
  for (const name of [
    'registryGroupMembers',
    'registryDirectoryEntries',
    'aureliaDesignPlanVisible',
    'scopeMembers',
    'scopeBlocked',
    'openRegistryScope',
    'renderFocusedScopeActions',
    'renderRegistryDirectory',
    'registryMemberButton',
    'renderFocusedScope',
    'returnToProjectDirectory',
  ]) vm.runInContext(functionSource(name), c);
  return {c, el:c.$};
}

function run() {
  const {c, el} = fixture();
  const find = (element,predicate) => predicate(element) ? element : element.children.map(child => find(child,predicate)).find(Boolean);
  c.state.registry = {
    groups:[
      {id:'aurelia',name:'Aurelia',archived:false,members:[{project_id:'aurelia'},{project_id:'radiworks'},{project_id:'morphic_v1'}]},
      {id:'archived-group',name:'Alte Gruppe',archived:true,members:[{project_id:'archived-project',archived:true}]},
    ],
    projects:[
      {id:'aurelia',name:'Aurelia',group_id:'aurelia',role:'parent',archived:false},
      {id:'radiworks',name:'RadiWorks',group_id:'aurelia',role:'module',archived:false},
      {id:'morphic_v1',name:'Morphic',group_id:'aurelia',role:'module',archived:false},
      {id:'standalone',name:'Standalone',group_id:null,archived:false},
      {id:'archived-module',name:'Archiviertes Modul',group_id:'aurelia',archived:true},
      {id:'archived-project',name:'Archiviertes Projekt',group_id:'archived-group',archived:true},
      {id:'archived-standalone',name:'Archiviertes Einzelprojekt',group_id:null,archived:true},
    ],
  };

  const entries = c.registryDirectoryEntries(c.state.registry.groups,c.state.registry.projects);
  assert.equal(entries.map(entry => `${entry.kind}:${entry.id}`).join(','), 'group:aurelia,group:archived-group,project:standalone,project:archived-standalone',
    'directory lists groups and standalone projects while grouped projects stay under their group');
  assert.equal(entries[0].memberCount,4,'group member count includes archived members');

  c.activateTab('registry');
  c.renderFocusedScope();
  assert.equal(c.focusedScope,null,'direct navigation to Projekte & Gruppen does not select a scope');
  assert.ok(el('registry-focused-detail').textContentDeep.includes('Projektübersicht'));

  c.renderRegistryDirectory();
  const archivedGroupCard = el('registry-directory-cards').children.find(card => card.className.includes('archived'));
  assert.ok(archivedGroupCard?.children.some(child => child.dataset?.openScopeId === 'archived-group'),
    'archived groups remain visible and openable in the directory');
  const groupCard = el('registry-directory-cards').children[0];
  const openGroup = groupCard.children.find(child => child.textContent === 'Öffnen');
  assert.ok(openGroup,'group directory card offers an explicit open button');
  openGroup.click();
  assert.deepEqual({...c.focusedScope},{kind:'group',id:'aurelia'});
  assert.equal(c.currentTab,'registry','opening a directory card navigates to Projekte & Gruppen');
  c.returnToProjectDirectory();
  assert.equal(c.currentTab,'directory','detail back action returns to the directory without losing the current scope');
  assert.deepEqual({...c.focusedScope},{kind:'group',id:'aurelia'});
  c.openRegistryScope('group','archived-group');
  const archivedGroup = c.registryDirectoryEntries(c.state.registry.groups,c.state.registry.projects).find(entry => entry.id === 'archived-group');
  assert.equal(archivedGroup.archived,true,'archived groups remain discoverable in the directory');
  assert.equal(c.scopeBlocked('scope_review','group','archived-group'),true,'archived group actions remain blocked by existing guards');
  const archivedStandaloneOpen = find(el('registry-directory-cards'),child => child.dataset?.openScopeId === 'archived-standalone');
  assert.ok(archivedStandaloneOpen,'archived standalone projects remain openable from the directory');
  archivedStandaloneOpen.click();
  assert.deepEqual({...c.focusedScope},{kind:'project',id:'archived-standalone'});
  assert.equal(c.scopeBlocked('scope_review','project','archived-standalone'),true,'archived standalone project actions remain blocked by existing guards');
  c.openRegistryScope('group','aurelia');

  c.renderFocusedScope();
  const openModule = find(el('registry-focused-detail'),child => child.dataset?.openProjectId === 'radiworks');
  assert.ok(openModule,'group overview exposes each member as an openable project');
  openModule.click();
  assert.deepEqual({...c.focusedScope},{kind:'project',id:'radiworks'});
  c.renderFocusedScope();
  const backlink = find(el('registry-focused-detail'),child => child.id === 'registry-focused-group-backlink');
  assert.equal(backlink.dataset.openGroupId,'aurelia','grouped project overview links back to its group');
  backlink.click();
  assert.deepEqual({...c.focusedScope},{kind:'group',id:'aurelia'},'group backlink returns to the containing group');

  assert.equal(c.aureliaDesignPlanVisible({kind:'group',id:'aurelia'},c.state.registry.groups,c.state.registry.projects),true);
  assert.equal(c.aureliaDesignPlanVisible({kind:'project',id:'radiworks'},c.state.registry.groups,c.state.registry.projects),true,
    'every current group module inherits the Aurelia design planning panel');
  const futureProjects = [...c.state.registry.projects,{id:'future-module',name:'Future Module',group_id:'aurelia',role:'module',archived:false}];
  assert.equal(c.aureliaDesignPlanVisible({kind:'project',id:'future-module'},c.state.registry.groups,futureProjects),true,
    'new group members inherit the planning requirement when assigned to Aurelia');
  assert.equal(c.aureliaDesignPlanVisible({kind:'project',id:'archived-module'},c.state.registry.groups,c.state.registry.projects),true,
    'archived modules remain discoverable under the same planning scope');
  assert.equal(c.aureliaDesignPlanVisible({kind:'project',id:'standalone'},c.state.registry.groups,c.state.registry.projects),false);
  assert.equal(c.aureliaDesignPlanVisible({kind:'group',id:'other'},c.state.registry.groups,c.state.registry.projects),false);
  assert.equal(c.aureliaDesignPlanVisible({kind:'project',id:'aurelia'},[],[{id:'aurelia',name:'Aurelia',group_id:null}]),true,
    'a standalone project with the stable Aurelia id receives its own planning panel');
  assert.equal(c.aureliaDesignPlanVisible({kind:'group',id:'aurelia-copy'},
    [{id:'aurelia-copy',name:'Aurelia-inspired project',members:[{project_id:'other'}]}],
    [{id:'other',name:'Other',group_id:'aurelia-copy'}]),false,
    'a similarly named group without the Aurelia project does not inherit its planning requirement');

  assert.match(html,/id="matrix-design-template"/);
  assert.match(html,/data-tab="directory"/);
  assert.match(html,/aria-controls="panel-directory"/);
  assert.match(html,/data-nav="registry"/);
  assert.match(html,/Design-Template/);
  assert.match(html,/D0–D4/);
  assert.match(html,/modul_templates/);
  assert.match(html,/Funktionen, Datenmodelle, Freigaben und Hermes-Routing werden nicht übertragen/);
  assert.match(html,/zählt nicht als abgenommener Gate-Schritt/i);
  assert.match(source,/const selectedSteps = steps\.filter\(step => chosenIds\.has\(step\.project_id\)\)/,
    'the new design plan stays outside the existing matrix accepted-step count');
  console.log('Project overview navigation, group backlinks, and Aurelia design planning visibility checked.');
}

try { run(); }
catch (error) { console.error(error); process.exitCode = 1; }

'use strict';
(() => {
  const $ = id => document.getElementById(id);
  const labels = {refresh:'Bestand aktualisieren',hybrid_review:'Hybrid-Review',model_check:'Modellprüfung',radiworks_tests:'RadiWorks-Tests',hermes_check:'Hermes-Prüfung',queued:'In Warteschlange',running:'Läuft',completed:'Abgeschlossen',failed:'Fehlgeschlagen',cancelled:'Abgebrochen',canceled:'Abgebrochen',interrupted:'Unterbrochen',pending:'Ausstehend'};
  let state = null, selected = null, focusedScope = null, currentTab = 'events', stream = null, loading = null;
  let lastReceived = 0, pollTimer = null, noticeTimer = null, connectionMode = 'connecting';
  let memory = null, memoryRequest = 0, memoryBusy = false, dirty = false;
  let decisionEvidence = null, decisionBusy = false;
  let intakeScope = null;
  let scopePlans = [], plansScope = null;
  let intakeRequest = 0, loadedIntakeDraft = null, scopeStrategies = [], strategiesScope = null;
  let intakeProject = '';
  const intakeDrafts = new Map(), intakeSelections = new Map();
  Object.assign(labels,{compare_reviews:'Sol / Astra vergleichen',governance_report:'Governance-Bericht',accepted:'Abgenommen',stale:'Veraltet',ready:'Bereit',blocked:'Gesperrt',review_required:'Review erforderlich',authorize:'Autorisiert',revoke:'Autorisierung widerrufen',accept:'Abgenommen',reject:'Abgelehnt'});
  Object.assign(labels,{live_start:'Prüfbrowser öffnen',live_capture:'Browsernachweis erfassen',live_stop:'Prüfsitzung schließen'});
  Object.assign(labels,{scope_review:'Review im gewählten Umfang',scope_compare:'Sol / Astra im gewählten Umfang'});
  Object.assign(labels,{scope_plan:'Matrixplan hybrid entwerfen'});
  Object.assign(labels,{scope_route_b_review:'Route B · Umfang prüfen',scope_route_b_plan:'Route B · Matrixplan entwerfen'});
  Object.assign(labels,{plan_test:'Ausgewählten Testschritt prüfen',scope_patch:'Änderung im Pilot-Arbeitsbereich vorschlagen',stage_test:'Pilot testen + Supervisor prüfen'});
  Object.assign(labels,{plan_failure:'Testfehler prüfen',pilot_transition:'Quellenübergang bestätigen',pilot_complete:'Übernahmeabschluss bestätigen',pilot_verify:'Übernahme nachprüfen',pilot_assess:'Pilot-Nachweis prüfen',pilot_prepare:'Pilot-Rückübernahme vorbereiten',pilot_apply:'Pilotänderungen übernehmen',pilot_rollback:'Eigene Pilotänderungen zurücknehmen'});
  const pending = new Set();
  const questionViews = new Map();
  const transitionNotes = new Map();
  Object.assign(labels,{waiting_for_operator:'Wartet auf deine Antwort',review_required:'Neue Prüfung erforderlich'});
  const format = value => value == null ? '—' : typeof value === 'object' ? JSON.stringify(value, null, 2) : String(value);
  const stamp = value => { if (!value) return 'Nicht beobachtet'; const d = new Date(value); return Number.isNaN(d.valueOf()) ? String(value) : d.toLocaleString('de-DE'); };
  const age = value => { if (!value) return 'Alter unbekannt'; const seconds = Math.floor((Date.now() - new Date(value).valueOf()) / 1000); if (!Number.isFinite(seconds)) return 'Alter unbekannt'; if (seconds < 60) return 'vor wenigen Sekunden'; if (seconds < 3600) return `vor ${Math.floor(seconds / 60)} Min.`; if (seconds < 86400) return `vor ${Math.floor(seconds / 3600)} Std.`; return `vor ${Math.floor(seconds / 86400)} Tagen`; };
  const node = (tag, cls, text) => { const n = document.createElement(tag); if (cls) n.className = cls; if (text != null) n.textContent = text; return n; };
  const set = (id, text, cls) => { $(id).textContent = text; if (cls) $(id).className = cls; };
  const activeProject = () => state?.projects?.find(p => p.id === selected);
  const statusClass = status => ['completed'].includes(status) ? 'good' : ['failed','interrupted'].includes(status) ? 'bad' : 'warn';
  function notify(message, error = false) { clearTimeout(noticeTimer); $('notice').hidden = false; $('notice').className = `notice${error ? ' error' : ''}`; $('notice').textContent = message; if (!error) noticeTimer = setTimeout(() => { $('notice').hidden = true; }, 11000); }
  async function api(path, body) {
    const longScope = path.startsWith('/api/scope?') || (path === '/api/actions' && ['scope_route_b_review','scope_route_b_plan'].includes(body?.action));
    const controller = new AbortController(); const timer = setTimeout(() => controller.abort(), longScope ? 180000 : 25000);
    try {
      const options = {credentials:'same-origin',headers:{Accept:'application/json'},signal:controller.signal};
      if (body !== undefined) { options.method = 'POST'; options.headers['Content-Type'] = 'application/json'; options.headers['X-CSRF-Token'] = state?.csrf_token || ''; options.body = JSON.stringify(body); }
      const response = await fetch(path, options);
      let data; try { data = await response.json(); } catch { throw new Error(`Ungültige Antwort vom Dienst (HTTP ${response.status}).`); }
      if (!response.ok) { const error = new Error(data.error || `HTTP ${response.status}`); error.status = response.status; throw error; }
      return data;
    } catch (error) { if (error.name === 'AbortError') throw new Error('Zeitüberschreitung. Der Dienst hat nicht rechtzeitig geantwortet.'); throw error; }
    finally { clearTimeout(timer); }
  }
  function connection(mode) {
    connectionMode = mode;
    set('connection', mode === 'live' ? '● Live verbunden' : mode === 'polling' ? '◌ Wiederverbindung · Abruf aktiv' : mode === 'offline' ? '○ Dienst nicht erreichbar' : '◌ Verbindung wird aufgebaut', `connection${mode === 'live' ? ' live' : ''}`);
    $('connection-banner').hidden = mode === 'live' || mode === 'connecting';
    $('connection-banner').textContent = mode === 'offline' ? 'Lokaler Dienst nicht erreichbar. Angezeigte Daten können veraltet sein. Die Verbindung wird automatisch erneut geprüft.' : 'Der Live-Stream wird erneut verbunden. Die Oberfläche ruft den aktuellen Stand vorübergehend regelmäßig ab.';
  }
  async function loadState() {
    if (loading) return loading;
    loading = (async () => { try { const next = await api('/api/state'); ingest(next); if (connectionMode !== 'live') connection('polling'); return true; } catch (error) { connection('offline'); if (!state) $('projects').replaceChildren(emptyRow(`Projektstand konnte nicht geladen werden: ${error.message}`)); return false; } finally { loading = null; } })();
    return loading;
  }
  function connectStream() {
    if (!window.EventSource) { connection('polling'); return; }
    if (stream) stream.close();
    stream = new EventSource('/api/events');
    stream.addEventListener('state', event => { try { ingest(JSON.parse(event.data)); connection('live'); } catch { connection('polling'); } });
    stream.onopen = () => connection('live');
    stream.onerror = () => { connection('polling'); loadState(); };
  }
  function ingest(next) {
    if (!next || !Array.isArray(next.projects)) return;
    const focused = document.activeElement;
    // SSE may omit the session token; preserve the token from the same-origin bootstrap.
    state = {...next,csrf_token:next.csrf_token || state?.csrf_token}; lastReceived = Date.now();
    if (!selected || !state.projects.some(p => p.id === selected)) selected = state.projects[0]?.id || null;
    renderSummary(); renderProjects(); renderDetail(); renderJobs(); renderEvents(); renderPlanned(); renderMemoryOptions(); renderControls(); renderGovernance(); renderStatusPages(); renderLive(); renderRegistry(); renderQuestions();
    if (focused?.id && !focused.isConnected) $(focused.id)?.focus({preventScroll:true});
  }
  function renderSummary() {
    const monitor = state.monitor || {}, runtime = state.runtime || {}, models = runtime.models || {};
    set('monitor-status', monitor.last_error ? '! Beobachtung gestört' : monitor.enabled ? '● Beobachtung läuft' : 'Ⅱ Beobachtung pausiert', monitor.last_error ? 'bad' : monitor.enabled ? 'good' : 'warn');
    renderObserved(); $('observed').title = stamp(state.observed_at);
    set('router-status', runtime.router?.reachable ? '● Erreichbar' : '○ Nicht erreichbar', runtime.router?.reachable ? 'good' : 'warn');
    set('router-url', runtime.router?.error || runtime.router?.url || 'Keine Routerbeobachtung');
    set('hermes-status', runtime.hermes?.available ? 'CLI verfügbar' : 'CLI nicht verfügbar', runtime.hermes?.available ? 'good' : 'warn');
    set('hermes-detail', runtime.hermes?.available ? 'Ausführung separat prüfen' : 'Pfad oder Installation prüfen');
    set('model-status', `${models.transport === 'hermes' ? 'Hermes → ' : ''}${models.orchestrator || 'Terra'} → ${state.settings?.supervisor || models.supervisor || 'Sol'}`);
    set('footer-update', `Letzte Beobachtung: ${stamp(state.observed_at)}`);
    $('monitor-status').title = monitor.last_error || `Quellen: ${monitor.interval_seconds || 15}s · Git: ${monitor.git_interval_seconds || 60}s`;
  }
  function renderObserved() { set('observed',state.monitor?.last_error ? `Fehler: ${format(state.monitor.last_error)} · Letzter Stand ${age(state.observed_at)}` : `Stand ${age(state.observed_at)}`); }
  function emptyRow(message) { const tr = node('tr'); const td = node('td','empty',message); td.colSpan = 3; tr.append(td); return tr; }
  function renderProjects() {
    const configured = (state.registry?.projects || []).filter(project => project.configured);
    const awaitingObservation = !state.projects.length && (!state.observed_at || configured.length > 0);
    set('project-count',awaitingObservation ? configured.length ? `${configured.length} konfiguriert` : '—' : state.projects.length);
    if (!state.projects.length) { $('projects').replaceChildren(emptyRow(awaitingObservation ? 'Noch kein aktueller Beobachtungsstand. Jetzt aktualisieren, um die konfigurierten Projekte einzulesen.' : 'Keine Projekte konfiguriert. Prüfe die lokale Dienstkonfiguration.')); return; }
    $('projects').replaceChildren(...state.projects.map(p => {
      const tr = node('tr', `project-row${p.id === selected ? ' selected' : ''}`); const first = node('td'); const button = node('button','project-select',p.name);
      button.id = `project-select-${p.id}`;
      button.setAttribute('aria-pressed',String(p.id === selected)); button.addEventListener('click',() => selectProject(p.id)); first.append(button,node('span','subline',p.branch ? `${p.branch} · ${p.head ? String(p.head).slice(0,8) : 'HEAD fehlt'}` : p.status || 'Kein Git-Nachweis'));
      const gate = node('td'); gate.append(node('span','chip',format(p.gate || 'Nicht dokumentiert')),node('span','subline',labels[p.status] || p.status || 'Status nicht dokumentiert'),node('span','subline',`${(p.memories || []).length} Gedächtnisquellen · ${age(p.observed_at)}`));
      const step = node('td',null,format(p.next_step || 'Nächsten Schritt anhand der Quellen klären')); if (p.depends_on?.length) step.append(node('span','subline',`Abhängig von: ${p.depends_on.map(projectName).join(', ')}`)); tr.append(first,gate,step); return tr;
    }));
  }
  function projectName(id) { return state.projects.find(p => p.id === id)?.name || (state.planned_projects || []).find(p => p.id === id)?.name || id; }
  function abandonDraft() { return !dirty || window.confirm('Deine Änderungen sind noch nicht gespeichert. Entwurf verwerfen?'); }
  function selectProject(id) {
    if (id === selected) return true;
    if (memoryBusy) { notify('Bitte warte, bis der laufende Dateizugriff abgeschlossen ist.',true); return false; }
    if (!abandonDraft()) return false;
    selected = id; resetMemory(); renderProjects(); renderDetail(); renderMemoryOptions(); return true;
  }
  function meta(parent, label, value) { const item = node('div'); item.append(node('dt',null,label),node('dd',null,format(value))); parent.append(item); }
  function actionButton(text, action, projectId, primary = false) { const button = node('button', `button ${primary ? 'primary' : 'secondary'}`,text); button.id = `action-${action}-${projectId || 'all'}`; button.dataset.action = action; if (projectId) button.dataset.projectId = projectId; button.addEventListener('click',() => runAction(action,projectId,button)); return button; }
  function renderDetail() {
    const p = activeProject(); if (!p) { set('detail-title','Projekt auswählen'); return; }
    const expanded = new Set([...$('project-detail').querySelectorAll('details[open]')].map(d => d.id));
    set('detail-title',p.name); set('detail-kind',p.kind === 'planned' ? 'Geplant' : 'QUELLENFOKUS');
    const box = $('project-detail'); box.replaceChildren();
    const dl = node('dl','detail-meta'); meta(dl,'Aufgelöster Projektpfad',p.path || 'Kein Projektpfad'); meta(dl,'Git-Arbeitsstand',p.git_status || (p.head && p.git_status != null ? 'Arbeitsbaum sauber' : 'Kein Git-Nachweis')); meta(dl,'HEAD',p.head || 'Nicht ermittelt'); box.append(dl);
    meta(dl,'Git-Beobachtung',p.git_observed_at ? `${stamp(p.git_observed_at)} · ${age(p.git_observed_at)}` : 'Separater Git-Zeitpunkt nicht erfasst');
    const next = node('section','next-action'); next.append(node('span','eyebrow','NÄCHSTER SCHRITT'),node('h3',null,format(p.next_step || 'Voraussetzungen anhand der Quellen prüfen')),node('p',null,`Gate: ${format(p.gate || 'Nicht dokumentiert')}`));
    next.append(node('p',null,labels[p.status] || p.status || 'Status nicht dokumentiert'),node('p',null,p.status_basis || 'Dokumentierte Planungsbasis; keine automatisch erteilte Freigabe.'));
    if (p.documented_status) next.append(node('p','muted',`Dokumentierter Ausgangsstand: ${format(p.documented_status)}`));
    next.append(node('p',null,p.depends_on?.length ? `Voraussetzungen: ${p.depends_on.map(projectName).join(', ')}. Der dokumentierte Status ersetzt keine Ausführungsfreigabe.` : 'Produktänderungen benötigen einen konkret freigegebenen Umfang.'));
    next.append(node('p',null,`Evidenz ${age(p.observed_at)} · ${stamp(p.observed_at)}`)); box.append(next);
    if (p.warnings?.length) { const ul = node('ul','warning-list'); p.warnings.forEach(w => ul.append(node('li',null,format(w)))); box.append(ul); }
    const actions = node('div','detail-actions'); actions.append(actionButton('Hybrid-Review starten','hybrid_review',p.id,true)); if (/radiworks/i.test(p.id) || /^radiworks$/i.test(p.name)) actions.append(actionButton('RadiWorks-Tests','radiworks_tests',p.id)); box.append(actions,node('p','small muted','Review übermittelt die Quellen dieses Projekts an Terra und den gewählten Supervisor. Modellaufrufe können Kosten verursachen.'));
    const sources = node('details'); sources.id = `detail-sources-${p.id}`; sources.open = expanded.has(sources.id); sources.append(node('summary',null,`Quellen & Hashes · ${(p.memories || []).length} Gedächtnisdateien`));
    if (p.documented_statuses && Object.keys(p.documented_statuses).length) { const documented = node('dl','detail-meta'); Object.entries(p.documented_statuses).forEach(([source,status]) => meta(documented,`Dokumentiert · ${source}`,status)); sources.append(documented); }
    const list = node('ul','source-list');
    for (const m of p.memories || []) { const li = node('li'); const button = node('button','text-button',m.name); button.addEventListener('click',async () => { if (!await openMemory(m.name)) return; activateTab('memory'); $('panel-memory').scrollIntoView({block:'start',behavior:'smooth'}); }); li.append(button,node('span','subline',`${m.committed ? 'Aktuelle Bytes im HEAD' : 'Aktuelle Bytes nicht im HEAD'} · ${m.staged ? 'Im Index' : 'Nicht vorgemerkt'} · ${m.size ?? '?'} Byte`),node('span','evidence-hash',`SHA-256 ${m.sha256 || 'Nicht erfasst'}`)); list.append(li); }
    for (const [index,s] of (p.sources || []).entries()) { const li = node('li'); if (typeof s === 'string') li.append(node('span',null,s)); else { const d = node('details'); d.id = `source-details-${p.id}-${index}`; d.open = expanded.has(d.id); d.append(node('summary',null,s.name || s.path || s.type || 'Quelle'),node('span','evidence-hash',s.path || 'Pfad nicht erfasst'),node('span','evidence-hash',`SHA-256 ${s.sha256 || 'Nicht erfasst'}`),node('pre',null,format(s.content ?? s))); li.append(d); } list.append(li); }
    if (!list.children.length) list.append(node('li','muted','Keine lesbaren Quellen erfasst.'));
    sources.append(list,node('span','meta-label','EVIDENZ-FINGERABDRUCK'),node('span','evidence-hash',p.evidence_hash || 'Noch kein Hash erfasst')); box.append(sources);
  }
  function updateRoutineControls() {
    for (const input of document.querySelectorAll('[data-routine-confirmation]')) {
      input.disabled = state.settings?.reasoning_mode !== 'auto';
      if (input.disabled) input.checked = false;
    }
  }
  function renderControls() {
    updateRoutineControls();
    const current = state.settings?.supervisor || state.runtime?.models?.supervisor;
    if ($('reasoning-mode')) $('reasoning-mode').value = state.settings?.reasoning_mode || 'medium';
    const options = state.runtime?.models?.options;
    if (Array.isArray(options) && options.length) {
      const values = options.map(o => typeof o === 'string' ? {value:o,label:o} : {value:o.id || o.value || o.model || o.name,label:o.label || o.name || o.id || o.model});
      const signature = JSON.stringify(values);
      if ($('supervisor').dataset.options !== signature) { $('supervisor').replaceChildren(...values.map(o => { const n = node('option',null,o.label); n.value = o.value; return n; })); $('supervisor').dataset.options = signature; }
    }
    if (current) { if (![...$('supervisor').options].some(o => o.value === current)) { const o = node('option',null,current); o.value = current; $('supervisor').append(o); } $('supervisor').value = current; }
    $('auto-review').checked = Boolean(state.settings?.auto_review);
    set('monitor-toggle',state.monitor?.enabled ? 'Beobachtung pausieren' : 'Beobachtung fortsetzen');
    document.querySelectorAll('[data-action]').forEach(b => { const key = `${b.dataset.action}:${b.dataset.projectId || ''}`; b.disabled = pending.has(key) || (state.jobs || []).some(j => ['queued','running'].includes(j.status) && j.action === b.dataset.action && (j.project_id || '') === (b.dataset.projectId || '')); });
    $('review-all').disabled = pending.has('hybrid_review:') || (state.jobs || []).some(j => ['queued','running'].includes(j.status) && j.action === 'hybrid_review' && !j.project_id);
  }
  async function runAction(action, projectId, button, stepId, liveId) {
    if (!state) { notify('Der Dienst ist noch nicht verbunden.',true); return; }
    const key = `${action}:${liveId || projectId || ''}`; if (pending.has(key)) return;
    pending.add(key); if (button) button.disabled = true; renderControls();
    try { const body = {action}; if (projectId) body.project_id = projectId; if (stepId) body.step_id = stepId; if (liveId) body.live_id = liveId; if (['hybrid_review','model_check','governance_report'].includes(action)) body.supervisor = $('supervisor').value; const result = await api('/api/actions',body); notify(`${labels[action] || action}: Auftrag ${result.job?.id || ''} angenommen.`); activateTab('jobs'); await loadState(); }
    catch (error) { notify(`Auftrag konnte nicht gestartet werden: ${error.message}`,true); }
    finally { pending.delete(key); if (button) button.disabled = false; if (state) { renderControls(); renderGovernance(); renderLive(); } }
  }
  async function saveSettings(body, control) { control.disabled = true; try { await api('/api/settings',body); await loadState(); notify('Betriebseinstellung gespeichert.'); } catch (error) { notify(`Einstellung nicht gespeichert: ${error.message}`,true); if (state) renderControls(); } finally { control.disabled = false; } }
  const fieldLabels = {summary:'Zusammenfassung',decision:'Votum',findings:'Befunde',required_evidence:'Benötigte Nachweise',steps:'Schritte',title:'Ziel',description:'Beschreibung',reason:'Begründung',reasons:'Voraussetzungen / Sperrgründe',priority:'Priorität',severity:'Schweregrad',source:'Quelle',sources:'Quellen',sha256:'SHA-256',evidence_hash:'Quellenstand',decision_hash:'Entscheidungsstand',path:'Pfad',project_id:'Projekt',depends_on:'Abhängigkeiten',criteria:'Abnahmekriterien',action:'Aktion',kind:'Art',status:'Status',provenance:'Herkunft',content:'Inhalt',model:'Modell',model_id:'Modellidentität',observed_at:'Beobachtet',plan:'Plan',review:'Review',reviews:'Reviews',comparison:'Vergleich',errors:'Fehler',success:'Erfolgreich',result:'Ergebnis',data:'Inhalt'};
  Object.assign(fieldLabels,{requirements_recorded:'Anforderungen erfasst',memories_present:'Gedächtnisse vorhanden',evidence_complete:'Evidenz im Prüfumfang vollständig',missing_proofs:'Fehlende Nachweise / Hinweise',intake_accepted:'Aufnahme ausdrücklich bestätigt'});
  function readable(value, depth = 0) {
    if (value == null || typeof value !== 'object') return node('p','readable-text',typeof value === 'boolean' ? value ? 'Ja' : 'Nein' : format(value));
    if (depth > 7) return node('pre',null,format(value));
    if (Array.isArray(value)) { const list = node('ol','readable-list'); if (!value.length) list.append(node('li','muted','Keine Einträge')); value.slice(0,100).forEach(v => { const li = node('li'); li.append(readable(v,depth+1)); list.append(li); }); return list; }
    const dl = node('dl','readable-fields'); Object.entries(value).slice(0,60).forEach(([key,v]) => { const item = node('div'); item.append(node('dt',null,fieldLabels[key] || key.replaceAll('_',' '))); const dd = node('dd'); dd.append(readable(v,depth+1)); item.append(dd); dl.append(item); }); return dl;
  }
  function jobNarrative(result) {
    const box = node('div','job-narrative'); if (!result || typeof result !== 'object') return box;
    if (result.historical_verified === true || result.freshness === 'unknown_requires_rescan') box.append(node('p','small warn',`Historischer Nachweis${result.historical_verified === true ? ' · zum damaligen Prüfzeitpunkt verifiziert' : ''}. Der aktuelle Stand ist nicht verifiziert; erneute Aufnahme und Prüfung erforderlich.`));
    if (result.review_scope) {
      box.append(node('p','small warn','Beratender Planungskandidat · keine Übernahme in die freigegebene Schrittmatrix und keine Ausführungsfreigabe.'),node('p','small muted',`Prüfumfang: ${scopeName(result.review_scope.kind,result.review_scope.id)}`));
      if (result.freshness_requires_rescan) box.append(node('p','small warn','Historische Momentaufnahme. Die aktuelle Frische erfordert eine erneute lokale Aufnahme; ein unveränderter Bildschirm belegt keine unveränderten Quellen.'));
      box.append(node('code','evidence-hash',`Umfangshash: ${result.scope_hash || 'Nicht geliefert'}`));
      if (result.intake) { const intake = node('section'); intake.append(node('h3',null,'Aufnahme zum Reviewzeitpunkt'),readable(result.intake)); box.append(intake); }
    }
    if (typeof result.report_url === 'string') { try { const url = new URL(result.report_url,location.origin); if (url.origin === location.origin && url.pathname === '/api/reports' && url.searchParams.has('id')) { const link = node('a','button secondary','Quellenbericht öffnen'); link.href = url.href; link.target = '_blank'; link.rel = 'noopener'; box.append(link); } } catch { /* Invalid links remain text in the raw evidence. */ } }
    if (result.proposal) { const proposal = node('section'); proposal.append(node('h3',null,'Strukturierter Planungsvorschlag · keine Ausführung'),readable(result.proposal)); box.append(proposal); }
    if (result.stage) {
      const section = node('section'); section.append(node('h3',null,'Isolierter Pilot-Arbeitsbereich'),node('p','small warn','Produktdateien bleiben unverändert. Keine Rückübernahme in das Projekt. Tests werden nur nach gesondertem Klick gestartet.'),node('code','evidence-hash',`Manifest: ${result.stage.manifest_hash || 'Nicht geliefert'}`),node('p','evidence-hash',result.stage.path || ''));
      const files = result.stage.manifest?.files || result.stage.files || [];
      for (const file of files) { const item = node('article','governance-step'); item.append(node('h3',null,file.path || 'Datei'),node('code','evidence-hash',`Original: ${file.original_sha256 || 'Neue Datei'} · Vorschlag: ${file.staged_sha256 || 'Nicht geliefert'}`),node('pre',null,file.diff || 'Kein Diff geliefert')); section.append(item); }
      const manifest = node('details'); manifest.append(node('summary',null,'Vollständiges Manifest'),readable(result.stage.manifest || result.stage)); section.append(manifest); box.append(section);
    }
    if (result.memory_coverage?.status === 'staged') {
      const coverage=result.memory_coverage;
      box.append(node('p','small warn',`Gedächtnis stufenweise geprüft: ${coverage.files?.length || 0} Originaldateien, ${coverage.stages?.length || 0} quellengebundene Leseabschnitte. Der Abschlussbericht sah belegte Auszüge und Zusammenfassungen, nicht sämtliche Originalzeilen. Kritische Aussagen an den Originalen prüfen.`));
    }
    if (result.stage_blocked) box.append(node('p','small warn',result.stage_blocked));
    if (result.post_test_review) { const section = node('section'); section.append(node('h3',null,'Supervisor nach dem Pilottest'),readable(result.post_test_review)); box.append(section); }
    if (result.stage_job_id) box.append(node('p','small warn','Pilot-Testnachweis · ausschließlich Standardbibliothek-unittest im bereitgestellten tests-Ordner. Keine Produktänderung oder Rückübernahme.'));
    for (const key of ['summary','plan','review','reviews','comparison','errors']) if (result[key] != null) { const section = node('section'); section.append(node('h3',null,fieldLabels[key]),readable(result[key])); box.append(section); }
    for (const key of ['exceptions','logs','console','screenshot']) if (result[key] != null) { const section = node('section'); section.append(node('h3',null,({exceptions:'Ausnahmen',logs:'Protokoll',console:'Browserkonsole',screenshot:'Screenshot-Datei'})[key]),readable(result[key])); box.append(section); }
    if (typeof result.screenshot_url === 'string') { try { const url = new URL(result.screenshot_url,location.origin); if (url.origin === location.origin && url.pathname === '/api/live/screenshot' && url.searchParams.has('id')) { const figure = node('figure','live-screenshot'); const img = node('img'); img.src = url.href; img.alt = 'Erfasster Browserstand der eigenen lokalen Prüfsitzung'; img.loading = 'lazy'; figure.append(img,node('figcaption','small muted','Erfasster Browserstand · Zeitpunkt und Sitzung im vollständigen Nachweis')); box.append(figure); } } catch { /* Invalid URLs are retained only in the text evidence. */ } }
    return box;
  }
  Object.assign(labels,{runtime_start:'Testdienst starten',runtime_stop:'Testdienst stoppen',runtime_check:'Bereitschaft prüfen'});
  async function runtimeAction(action, body) {
    if (pending.has('runtime')) return;
    pending.add('runtime'); renderRuntimes();
    try {
      await api('/api/runtime/' + action, body);
      notify(action === 'start' ? 'Laufzeitstart eingereiht.' : action === 'check' ? 'Bereitschaftsprüfung eingereiht.' : 'Stop eingereiht.');
      await loadState();
    } catch (error) { notify(error.message, true); }
    finally { pending.delete('runtime'); renderRuntimes(); }
  }
  function renderRuntimes() {
    let container = $('runtime-profiles');
    if (!container) { container = node('section','live-item'); container.id = 'runtime-profiles'; $('panel-live').append(container); }
    const data = state.runtime_profiles || {}, profiles = data.profiles || [], instances = data.instances || [];
    const active = instances.some(row => ['starting','running'].includes(row.status));
    const busy = pending.has('runtime') || (state.jobs || []).some(job => ['queued','running'].includes(job.status));
    container.replaceChildren(node('h3',null,'Lokaler Laufzeittest'),node('p','small muted','Prüft Start, Bereitschaft und Stop. Läuft höchstens eine Stunde; nach Governor-Neustart ist ein neuer manueller Start nötig.'));
    for (const profile of profiles) {
      const entry = node('div','live-item');
      entry.append(node('p',null,`${profile.name} · Port ${profile.port}`));
      const start = node('button','button secondary','Testdienst starten');
      start.disabled = busy || active || !profile.supported;
      start.addEventListener('click',() => runtimeAction('start',{profile_id:profile.id,profile_hash:profile.hash}));
      entry.append(start); container.append(entry);
    }
    const names = {starting:'Startet',running:'Läuft',stopped:'Gestoppt',failed:'Fehlgeschlagen',interrupted:'Unterbrochen'};
    for (const row of instances) {
      const entry = node('article','live-item');
      entry.append(node('span','chip',names[row.status] || row.status),node('p','small muted',`${row.started_at || 'Zeit unbekannt'} · Port ${row.port ?? 'unbekannt'}`),node('p',null,row.reason || (row.readiness_verified ? 'Bereitschaft bestätigt.' : 'Bereitschaft noch nicht bestätigt.')));
      if (['starting','running'].includes(row.status)) {
        if (row.status === 'running') {
          const check = node('button','button secondary','Bereitschaft prüfen'); check.disabled = busy;
          check.addEventListener('click',() => runtimeAction('check',{instance_id:row.id})); entry.append(check);
        }
        const stop = node('button','button secondary','Testdienst stoppen'); stop.disabled = busy;
        stop.addEventListener('click',() => runtimeAction('stop',{instance_id:row.id})); entry.append(stop);
      }
      if (row.last_check) entry.append(node('p','small',`Letzte Prüfung: ${row.last_check.checked_at} · ${row.last_check.summary} Historischer Nachweis, keine laufende Überwachung.`));
      container.append(entry);
    }
  }
  function renderLive() {
    renderRuntimes();
    const live = state.live_views || {}, targets = Array.isArray(live.targets) ? live.targets : [], sessions = Array.isArray(live.sessions) ? live.sessions : [];
    $('live-error').hidden = !live.error; set('live-error',live.error ? format(live.error) : '');
    const byId = new Map(targets.map(target => [target.project_id,target]));
    const known = new Map();
    for (const project of state.projects || []) known.set(project.id,project.name);
    for (const project of state.registry?.projects || []) if (!project.archived) known.set(project.id,project.name);
    for (const target of targets) if (!known.has(target.project_id)) known.set(target.project_id,target.name || target.project_id);
    $('live-targets').replaceChildren(...(known.size ? [...known].map(([id,name]) => {
      const target = byId.get(id), item = node('article','live-item');
      const heading = node('div','step-heading'); heading.append(node('h3',null,name),node('span','chip',target?.url ? id === 'radiworks' ? 'API-Vorschau' : 'Lokales Ziel' : 'Noch kein Ziel')); item.append(heading);
      if (target?.url) {
        item.append(node('p','evidence-hash',target.url));
        if (id === 'radiworks') item.append(node('p','small warn','RadiWorks stellt hier bislang eine API-Vorschau bereit; dies ist kein vollständiger Browser-UI-Test.'));
        if (['radi144','morphic_v1'].includes(id)) item.append(node('p','small muted','Radi144 und Morphic verwenden lokal beide Port 8000. Die Dienste nur nacheinander starten; der jeweils andere Zielpfad darf nicht als bestandener Modultest gewertet werden.'));
        const start = node('button','button secondary','Prüfbrowser öffnen'); start.disabled = pending.has(`live_start:${id}`); start.addEventListener('click',() => runAction('live_start',id,start)); item.append(start);
      } else item.append(node('p','small muted','Kein lokales Browserziel konfiguriert. Für dieses Modul ist noch keine Live-Ansicht verfügbar.'));
      return item;
    }) : [node('p','empty','Noch keine beobachteten Projekte oder Live-Ziele vorhanden.')]));
    $('live-sessions').replaceChildren(...(sessions.length ? sessions.map(session => { const item = node('article','live-item'); item.append(node('h3',null,projectName(session.project_id) || 'Prüfsitzung'),node('span','chip',labels[session.status] || session.status || 'Status unbekannt'),node('p','evidence-hash',session.url || 'Keine URL geliefert'),node('p','small muted',`Sitzung ${session.id} · PID ${session.pid ?? 'nicht erfasst'} · CDP ${session.debug_port ?? 'nicht erfasst'}`)); const buttons = node('div','detail-actions'); for (const [action,label] of [['live_capture','Nachweis erfassen'],['live_stop','Sitzung schließen']]) { const button = node('button','button secondary',label); button.disabled = !['running','active'].includes(session.status) || pending.has(`${action}:${session.id}`); button.addEventListener('click',() => runAction(action,undefined,button,undefined,session.id)); buttons.append(button); } item.append(buttons); return item; }) : [node('p','empty','Keine eigenen Prüfsitzungen vorhanden.')]));
  }
  function governanceSteps() { return Array.isArray(state?.governor?.steps) ? state.governor.steps : []; }
  const scopedReviewActions = new Set(['scope_review','scope_compare','scope_route_b_review']);
  function reviewScopeState(kind,id) {
    const primary = (state.registry?.observations || []).find(row => row.kind === kind && row.id === id);
    const recent = (state.registry?.recent_scope_observations || []).find(row => row.kind === kind && row.id === id);
    const valid = row => row?.stale === false && typeof row.scope_hash === 'string' && Boolean(row.scope_hash) && Number.isFinite(Date.parse(row.observed_at));
    const observation = valid(recent) && (!valid(primary) || Date.parse(recent.observed_at) >= Date.parse(primary.observed_at)) ? recent : valid(primary) ? primary : null;
    const job = (state.jobs || []).find(row => scopedReviewActions.has(row.action) &&
      (row.request?.scope_kind || row.result?.review_scope?.kind) === kind &&
      (row.request?.scope_id || row.result?.review_scope?.id) === id);
    if (!job) return {kind:'unreviewed',label:'Kein Review im sichtbaren Auftragsverlauf',detail:'Für diesen Umfang ist kein Reviewnachweis in den zuletzt geladenen Aufträgen sichtbar.'};
    const result = job.result || {}, decision = result.review?.decision;
    const reportValid = job.action === 'scope_compare'
      ? result.comparison?.complete === true && result.success === true
      : ['BLOCK','REVIEW_ONLY'].includes(decision) && typeof result.review?.summary === 'string' && Boolean(result.review.summary.trim());
    const current = job.status === 'completed' && reportValid && result.stale === false &&
      result.freshness === 'recently_observed' && observation?.stale === false &&
      typeof result.scope_hash === 'string' && Boolean(result.scope_hash) && result.scope_hash === observation.scope_hash;
    const title = labels[job.action] || job.action;
    if (current) return {kind:'current',label:'Zum beobachteten Umfang synchron',detail:`${title} · ${stamp(job.ended_at || job.created_at)} · Hash ${result.scope_hash.slice(0,12)}…`,job};
    if (['queued','running'].includes(job.status)) return {kind:'pending',label:'Review läuft',detail:`${title} · Ein aktueller Nachweis liegt noch nicht vor.`,job};
    if (job.status !== 'completed') return {kind:'historical',label:'Letzter Review nicht abgeschlossen',detail:`${title} · ${labels[job.status] || job.status}. Aktueller Abgleich offen.`,job};
    const reason = !reportValid ? 'Kein gültiger vollständiger Reviewbericht.' : !observation || observation.stale ? 'Lokale Umfangsbeobachtung fehlt oder ist veraltet.' : result.freshness !== 'recently_observed' ? 'Frische erfordert erneute lokale Aufnahme.' : result.stale !== false || result.scope_hash !== observation.scope_hash ? 'Quellenstand oder Reviewbindung nicht aktuell.' : 'Aktueller Abgleich nicht nachgewiesen.';
    return {kind:'historical',label:'Historisch · Abgleich offen',detail:`${title} · ${reason}`,job};
  }
  function reviewIndicator(info) {
    const mark = node('span',`status-indicator ${info.kind}`,info.label);
    mark.setAttribute('aria-label',`Reviewstatus: ${info.label}`);
    return mark;
  }
  async function refreshReviewScope(kind,id,button) {
    const key = `review-scope:${kind}:${id}`;
    if (pending.has(key)) return;
    pending.add(key); button.disabled = true;
    try {
      await api(`/api/scope?kind=${encodeURIComponent(kind)}&id=${encodeURIComponent(id)}&fresh=1`);
      if (!await loadState()) throw new Error('Aktueller Governor-Stand konnte nicht geladen werden.');
      notify(`${scopeName(kind,id)} lokal neu geprüft. Reviewbindung im aktuellen Stand beachten.`);
    } catch (error) { notify(`Umfang konnte nicht lokal geprüft werden: ${error.message}`,true); }
    finally { pending.delete(key); if (state) renderStatusPages(); }
  }
  function scopeRefreshButton(kind,id,info) {
    if (info.kind === 'current') return null;
    const button = node('button','button secondary','Umfang lokal neu prüfen');
    button.type = 'button'; button.disabled = pending.has(`review-scope:${kind}:${id}`);
    button.title = 'Liest nur den ausgewählten Umfang lokal neu ein. Kein Modellaufruf und keine Freigabe.';
    button.addEventListener('click',() => refreshReviewScope(kind,id,button));
    return button;
  }
  function activeGroups() { return (state.registry?.groups || []).filter(group => !group.archived); }
  function matrixScopeOptions(groups,names,registryProjects) {
    const registered = new Map(registryProjects.map(project => [project.id,project]));
    const visible = id => names.has(id) && registered.get(id)?.archived !== true;
    const options = groups.map(group => {
      const ids = new Set([...(group.members || []).map(member => member.project_id),...registryProjects.filter(project => project.group_id === group.id && !project.archived).map(project => project.id)]);
      return {key:`group:${group.id}`,kind:'group',id:group.id,label:`Produktgruppe: ${group.name}`,ids:[...ids].filter(visible)};
    });
    for (const [id,name] of names) {
      if (!visible(id)) continue;
      const group = groups.find(item => item.id === registered.get(id)?.group_id);
      options.push({key:`project:${id}`,kind:'project',id,label:`${group ? 'Modul einzeln' : 'Einzelprojekt'}: ${name}${group ? ` (${group.name})` : ''}`,ids:[id]});
    }
    return options;
  }
  function aureliaDesignPlanVisible(scope,groups,projects) {
    if (!scope) return false;
    const project = scope.kind === 'project' ? projects.find(item => item.id === scope.id) : null;
    if (project?.id === 'aurelia') return true;
    const groupId = scope.kind === 'group' ? scope.id : project?.group_id;
    const group = groups.find(item => item.id === groupId);
    if (!group) return false;
    const hasAureliaMember = (group.members || []).some(member => (typeof member === 'string' ? member : member.project_id) === 'aurelia');
    const aureliaProject = projects.find(item => item.id === 'aurelia');
    return hasAureliaMember || aureliaProject?.group_id === group.id;
  }
  function renderStatusPages() {
    const registry = state.registry || {}, projectRows = state.governor?.projects || [], steps = governanceSteps();
    const names = new Map((state.projects || []).map(project => [project.id,project.name]));
    const archivedIds = new Set((registry.projects || []).filter(project => project.archived).map(project => project.id));
    for (const id of archivedIds) names.delete(id);
    for (const project of registry.projects || []) if (!project.archived) names.set(project.id,project.name);
    for (const row of projectRows) if (!names.has(row.id) && !archivedIds.has(row.id)) names.set(row.id,projectName(row.id));
    const groups = activeGroups(), reviewCards = [];
    for (const group of groups) {
      const info = reviewScopeState('group',group.id), card = node('article',`status-card review-${info.kind}`);
      const heading = node('div','status-card-head'); heading.append(node('span','eyebrow','PRODUKTGRUPPE'),node('h4',null,group.name));
      card.append(heading,reviewIndicator(info),node('p','small muted',info.detail),node('p','small muted',`${(group.members || []).length} zugeordnete Projekte · eigener Gruppenumfang`)); reviewCards.push(card);
      const refresh = scopeRefreshButton('group',group.id,info); if (refresh) card.append(refresh);
    }
    for (const [id,name] of names) {
      const info = reviewScopeState('project',id), project = (registry.projects || []).find(row => row.id === id), card = node('article',`status-card review-${info.kind}`);
      const heading = node('div','status-card-head'); heading.append(node('span','eyebrow',project?.group_id ? 'MODUL IN GRUPPE' : 'EINZELPROJEKT'),node('h4',null,name));
      card.append(heading,reviewIndicator(info),node('p','small muted',info.detail));
      if (project?.group_id) card.append(node('p','small muted',`Gruppe: ${scopeName('group',project.group_id)} · Projekt-Review und Gruppen-Review sind getrennte Nachweise.`));
      const refresh = scopeRefreshButton('project',id,info); if (refresh) card.append(refresh);
      reviewCards.push(card);
    }
    $('reviews-grid').replaceChildren(...(reviewCards.length ? reviewCards : [node('p','empty','Noch keine Projekte oder Gruppen im lokalen Stand vorhanden.')]));
    set('reviews-summary',`${reviewCards.filter(card => card.classList.contains('review-current')).length} von ${reviewCards.length} Umfängen synchron · sichtbarer Auftragsverlauf`);
    $('reviews-global').replaceChildren(readable(state.governor?.review_summary || 'Kein globaler Reviewbericht vorhanden.'));

    const options = matrixScopeOptions(groups,names,registry.projects || []), picker = $('matrix-scope'), previous = picker.value;
    const signature = JSON.stringify(options.map(option => [option.key,option.label]));
    if (picker.dataset.options !== signature) {
      picker.replaceChildren(...options.map(option => { const item = node('option',null,option.label); item.value = option.key; return item; }));
      picker.dataset.options = signature;
    }
    picker.value = options.some(option => option.key === previous) ? previous : options[0]?.key || '';
    picker.disabled = !options.length;
    const chosen = options.find(option => option.key === picker.value), chosenIds = new Set(chosen?.ids || []);
    const selectedGroup = chosen?.kind === 'group' ? groups.find(group => group.id === chosen.id) : null;
    $('matrix-design-template').hidden = !aureliaDesignPlanVisible(chosen,groups,registry.projects || []);
    if (selectedGroup) {
      const info = reviewScopeState('group',selectedGroup.id), block = node('article','matrix-group');
      block.append(node('strong',null,selectedGroup.name),reviewIndicator(info),node('span','small muted',`${chosenIds.size} Module im gewählten Umfang · Gruppenreview separat`));
      const refresh = scopeRefreshButton('group',selectedGroup.id,info); if (refresh) block.append(refresh);
      $('matrix-groups').replaceChildren(block);
    } else $('matrix-groups').replaceChildren();
    const cards = [...names].filter(([id]) => chosenIds.has(id)).map(([id,name]) => {
      const own = steps.filter(step => step.project_id === id), accepted = own.filter(step => step.accepted === true).length;
      const pending = own.filter(step => step.accepted !== true), project = (registry.projects || []).find(row => row.id === id);
      const info = reviewScopeState('project',id), card = node('article','status-card matrix-card');
      const heading = node('div','status-card-head'); heading.append(node('span','eyebrow',project?.group_id ? `MODUL · ${scopeName('group',project.group_id)}` : 'EINZELPROJEKT'),node('h4',null,name)); card.append(heading);
      const count = node('p','matrix-count',own.length ? `${accepted} / ${own.length}` : '0 / 0'); count.append(node('span','small muted',' definierte Schritte abgenommen')); card.append(count);
      if (own.length) { const progress = node('progress','matrix-progress'); progress.max = own.length; progress.value = accepted; progress.setAttribute('aria-label',`${name}: ${accepted} von ${own.length} definierten Schritten abgenommen`); card.append(progress); }
      card.append(reviewIndicator(info),node('p','small muted',`Review: ${info.detail}`));
      const refresh = scopeRefreshButton('project',id,info); if (refresh) card.append(refresh);
      if (!own.length) card.append(node('p','small warn','Noch keine Schritte für dieses Projekt definiert. Umfang und Nachweiskriterien klären.'));
      else if (!pending.length) card.append(node('p','small good','Alle aktuell definierten Schritte abgenommen. Neue Quellen oder Entscheidungen können den Stand ändern.'));
      else {
        card.append(node('h5',null,`Noch erforderlich (${pending.length})`));
        const list = node('ol','matrix-tasks');
        for (const step of pending) {
          const item = node('li'); item.append(node('strong',null,step.title || step.id),node('span','chip',labels[step.status] || step.status || 'Nicht bewertet'));
          const reasons = Array.isArray(step.reasons) ? step.reasons : [];
          if (reasons.length) { const explanation = node('ul','matrix-reasons'); for (const reason of reasons) explanation.append(node('li',null,format(reason))); item.append(explanation); }
          else item.append(node('p','small muted','Konkrete Nachweise und Voraussetzungen im Governance-Detail prüfen.'));
          list.append(item);
        }
        card.append(list);
      }
      return card;
    });
    $('matrix-rows').replaceChildren(...(cards.length ? cards : [node('p','empty',chosen ? 'Im gewählten Umfang sind noch keine beobachteten Projektmodule vorhanden.' : 'Noch keine Projekte in der berechneten Gate-Matrix vorhanden.')]));
    const selectedSteps = steps.filter(step => chosenIds.has(step.project_id));
    set('matrix-summary',chosen ? `${selectedSteps.filter(step => step.accepted === true).length} / ${selectedSteps.length} definierte Schritte im gewählten Umfang abgenommen` : 'Kein Umfang ausgewählt');
    const shared = steps.filter(step => !step.project_id);
    $('matrix-shared').replaceChildren(...(shared.length ? shared.map(step => { const item = node('article','matrix-shared-step'); item.append(node('strong',null,step.title || step.id),node('span','chip',labels[step.status] || step.status || 'Nicht bewertet')); if (step.reasons?.length) { const list = node('ul','matrix-reasons'); for (const reason of step.reasons) list.append(node('li',null,format(reason))); item.append(list); } return item; }) : [node('p','small muted','Keine projektübergreifenden Schritte definiert.')])) ;
  }
  function renderGovernance() {
    const governor = state.governor || {}, steps = governanceSteps(); set('governance-count',steps.length);
    const expandedSteps = new Set([...$('governance-steps').querySelectorAll('details[open]')].map(d => d.id));
    set('governance-summary',`${steps.filter(s => s.status === 'ready').length} bereit · ${steps.filter(s => s.status === 'blocked').length} gesperrt · ${steps.filter(s => s.status === 'review_required').length} im Review`);
    const ranks = new Map((Array.isArray(governor.next_steps) ? governor.next_steps : []).map((s,index) => [typeof s === 'string' ? s : s.id,index]));
    const ordered = [...steps].sort((a,b) => (ranks.get(a.id) ?? 1000)-(ranks.get(b.id) ?? 1000) || Number(a.priority ?? 999)-Number(b.priority ?? 999));
    $('governance-steps').replaceChildren(...(ordered.length ? ordered.map((step,index) => {
      const article = node('article','governance-step'); const heading = node('div','step-heading'); heading.append(node('span','step-rank',String(index+1).padStart(2,'0')),node('h3',null,step.title || step.id),node('span','chip',labels[step.status] || step.status || 'Nicht bewertet')); article.append(heading,node('p','small muted',`${step.project_id ? projectName(step.project_id) : 'Projektübergreifend'} · Priorität ${step.priority ?? 'offen'} · ${step.kind === 'read_only' ? 'Lesender Schritt' : format(step.kind)}`));
      if (step.reasons?.length) article.append(readable(step.reasons));
      if (step.depends_on?.length) article.append(node('p','small muted',`Abhängigkeiten: ${step.depends_on.map(id => steps.find(s => s.id === id)?.title || id).join(' · ')}`));
      const criteria = node('details'); criteria.id = `criteria-${step.id}`; criteria.open = expandedSteps.has(criteria.id); criteria.append(node('summary',null,'Umfang & Abnahmekriterien'),readable(step.criteria || 'Keine Kriterien geliefert')); article.append(criteria);
      const actions = node('div','detail-actions'); const choose = node('button','button secondary','Entscheidung vorbereiten'); choose.id = `choose-step-${step.id}`; choose.addEventListener('click',() => { $('decision-step').value = step.id; captureDecision(); $('decision-form').scrollIntoView({block:'center',behavior:'smooth'}); $('decision-kind').focus({preventScroll:true}); }); actions.append(choose);
      if (step.action === 'governance_report') { const run = node('button','button quiet','Bericht erstellen'); run.disabled = !(step.can_run ?? step.status === 'ready') || pending.has(`governance_report:${step.project_id || ''}`); run.title = 'Lokaler Quellen- und Entscheidungsbericht. Keine fachliche Gate-Abnahme und kein Modellaufruf.'; run.addEventListener('click',() => runAction('governance_report',step.project_id,run,step.id)); actions.append(run); }
      article.append(actions); return article;
    }) : [node('p','empty','Noch keine berechneten Schritte. Die Governance-Auswertung wird vom lokalen Dienst bereitgestellt.')]));
    const select = $('decision-step'), selectedStep = select.value, signature = JSON.stringify(steps.map(s => [s.id,s.title]));
    if (select.dataset.steps !== signature) { select.replaceChildren(node('option',null,'Schritt auswählen …')); select.firstChild.value = ''; steps.forEach(step => { const option = node('option',null,`${step.project_id ? projectName(step.project_id) : 'Übergreifend'} · ${step.title || step.id}`); option.value = step.id; select.append(option); }); select.value = selectedStep; select.dataset.steps = signature; }
    $('governance-knowledge').replaceChildren(readable(governor.knowledge || 'Noch keine Wissensbasis bereitgestellt.'));
    $('governance-reviews').replaceChildren(readable(governor.review_summary || 'Noch keine aktuelle Reviewauswertung bereitgestellt.'));
    const decisions = Array.isArray(state.decisions) ? state.decisions : [];
    $('decision-history').replaceChildren(...(decisions.length ? [...decisions].reverse().map(d => { const item = node('article','decision-entry'); item.append(node('h3',null,`${labels[d.kind] || d.kind} · ${steps.find(s => s.id === d.step_id)?.title || d.step_id}`),node('p','small muted',`${stamp(d.created_at)} · ${d.actor || 'Betreiber'}`),node('p','small',d.reason),node('code','evidence-hash',`Quellenstand ${d.evidence_hash || 'Nicht erfasst'}`)); return item; }) : [node('p','empty','Noch keine Betreiberentscheidungen erfasst.')]));
    updateDecisionGuard();
  }
  function captureDecision() {
    const step = governanceSteps().find(s => s.id === $('decision-step').value);
    decisionEvidence = step ? state.evidence_hash || null : null;
    $('decision-kind').value = ''; $('decision-reason').value = '';
    $('decision-scope').replaceChildren();
    if (step) {
      const steps = governanceSteps(), ranks = new Map((Array.isArray(state.governor?.next_steps) ? state.governor.next_steps : []).map((s,index) => [typeof s === 'string' ? s : s.id,index]));
      const ordered = [...steps].sort((a,b) => (ranks.get(a.id) ?? 1000)-(ranks.get(b.id) ?? 1000) || Number(a.priority ?? 999)-Number(b.priority ?? 999));
      $('decision-scope').append(node('strong',null,step.title || step.id),node('p','good',`Reihenfolge ${ordered.findIndex(s => s.id === step.id)+1} · Priorität ${step.priority ?? 'offen'}`),node('p',null,`Status: ${labels[step.status] || step.status}. ${step.action ? `Zulässige Aktion: ${labels[step.action] || step.action}.` : 'Keine ausführbare Aktion hinterlegt.'}`),node('p',null,`Abhängigkeiten: ${step.depends_on?.length ? step.depends_on.map(id => steps.find(s => s.id === id)?.title || id).join(' · ') : 'Keine hinterlegt'}`),node('strong',null,'Umfang & Abnahmekriterien'),readable(step.criteria || 'Keine Kriterien geliefert'),node('strong',null,'Voraussetzungen / Sperrgründe'),readable(step.reasons || []));
    }
    else $('decision-scope').textContent = 'Wähle einen Schritt und prüfe seine Voraussetzungen.';
    set('decision-evidence',decisionEvidence || 'Kein gebundener Quellenstand verfügbar'); updateDecisionGuard();
  }
  function updateDecisionGuard() {
    const step = governanceSteps().find(s => s.id === $('decision-step').value), drift = Boolean(decisionEvidence && decisionEvidence !== state.evidence_hash);
    $('decision-drift').hidden = !drift; $('decision-rebase').hidden = !drift;
    set('decision-drift','Die Evidenz hat sich seit deiner Auswahl geändert. Prüfe den aktuellen Umfang erneut, bevor du eine Entscheidung erfasst.');
    $('decision-submit').disabled = decisionBusy || !step || !decisionEvidence || drift || !$('decision-kind').value || !$('decision-reason').value.trim();
    $('decision-step').disabled = decisionBusy; $('decision-kind').disabled = decisionBusy; $('decision-reason').disabled = decisionBusy; $('decision-rebase').disabled = decisionBusy;
  }
  function renderQuestions() {
    const questions = (state.operator_questions || []).filter(q => q.status === 'pending');
    const active = new Set(questions.map(q => String(q.id)));
    set('question-count',questions.filter(q => !questionViews.get(String(q.id))?.accepted).length);
    for (const question of questions) {
      const id = String(question.id);
      if (questionViews.has(id)) continue;
      const article = node('article','operator-question');
      const heading = node('h3',null,question.question?.text || 'Rückfrage zum Auftrag');
      const context = node('p','small muted',`${scopeName(question.scope_kind,question.scope_id)} · Auftrag ${question.job_id} · Rückfrage ${question.revision} · Supervisor ${question.supervisor || 'wie im Auftrag'}`);
      const reason = node('p','readable-text',question.question?.reason || 'Für diesen Auftrag wird eine Klärung benötigt.');
      const jobLink = node('button','text-button','Auftrag & bisherigen Verlauf ansehen'); jobLink.type = 'button';
      jobLink.addEventListener('click',() => { activateTab('jobs'); const job = document.getElementById(`job-${question.job_id}`); (job || $('panel-jobs')).scrollIntoView({block:'start',behavior:'smooth'}); job?.querySelector('summary')?.focus({preventScroll:true}); });
      const form = node('form','question-form');
      const label = node('label',null,'Deine Antwort');
      const answer = node('textarea'); answer.id = `question-answer-${id}`; answer.rows = 4; answer.maxLength = 4000; answer.required = true; label.htmlFor = answer.id;
      const hint = node('p','small muted','Bis zu 4.000 Zeichen. Die Antwort wird zur Umfangsprüfung an die Modelle gesendet; dabei können Modellkosten entstehen.');
      hint.id = `question-hint-${id}`; answer.setAttribute('aria-describedby',hint.id);
      const actions = node('div','detail-actions');
      const send = node('button','button primary','Antwort senden'); send.type = 'submit'; send.disabled = true;
      const cancel = node('button','button danger','Auftrag abbrechen'); cancel.type = 'button';
      const feedback = node('p','small muted'); feedback.setAttribute('role','status');
      actions.append(send,cancel); form.append(label,answer,hint,actions,feedback);
      article.append(context,heading,reason,jobLink,node('code','evidence-hash',`Gebundener Umfang: ${question.scope_hash}`),form);
      const view = {article,answer,send,cancel,feedback,busy:false,accepted:false,active:true,question};
      questionViews.set(id,view); $('question-list').append(article);
      answer.addEventListener('input',() => { send.disabled = view.busy || !view.active || !answer.value.trim(); });
      form.addEventListener('submit',async event => {
        event.preventDefault(); if (view.busy || !view.active || !answer.value.trim()) return;
        view.busy = true; send.disabled = true; cancel.disabled = true; answer.readOnly = true;
        feedback.className = 'small muted'; feedback.textContent = 'Antwort wird übermittelt …';
        try {
          await api('/api/questions/answer',{question_id:question.id,answer:answer.value.trim(),scope_hash:question.scope_hash});
          view.accepted = true; answer.value = '';
          notify('Antwort angenommen. Derselbe Auftrag wartet jetzt auf die hybride Umfangsprüfung.');
          await loadState();
        } catch (error) { feedback.className = 'small bad'; feedback.textContent = `Antwort nicht angenommen: ${error.message} Dein Entwurf bleibt hier erhalten.`; }
        finally { view.busy = false; answer.readOnly = view.accepted; renderQuestions(); }
      });
      cancel.addEventListener('click',async () => {
        if (view.busy || !view.active) return;
        view.busy = true; send.disabled = true; cancel.disabled = true;
        try { await api('/api/jobs/cancel',{id:question.job_id}); view.accepted = true; answer.value = ''; notify('Abbruch angefordert. Den endgültigen Status zeigt der Auftrag.'); await loadState(); }
        catch (error) { feedback.className = 'small bad'; feedback.textContent = `Abbruch nicht angenommen: ${error.message}`; }
        finally { view.busy = false; renderQuestions(); }
      });
    }
    for (const [id,view] of questionViews) {
      view.active = active.has(id) && !view.accepted;
      // Keep an accepted ID until the next authoritative state removes it, so a
      // delayed refresh cannot recreate the old answer form.
      if (view.accepted && active.has(id)) { view.article.hidden = true; continue; }
      if (!view.active && !view.busy && !view.answer.value) { view.article.remove(); questionViews.delete(id); continue; }
      view.send.disabled = view.busy || !view.active || !view.answer.value.trim();
      view.cancel.disabled = view.busy || !view.active;
      if (!view.active && !view.busy && view.answer.value && !view.feedback.textContent) {
        view.feedback.className = 'small warn'; view.feedback.textContent = 'Diese Rückfrage ist nicht mehr offen. Dein Entwurf bleibt zum Kopieren erhalten; prüfe den aktuellen Auftrag.';
      }
    }
    $('operator-questions').hidden = ![...questionViews.values()].some(view => !view.article.hidden);
  }
  function tokenUsage(job, openIds = new Set()) {
    const usage = job.token_usage;
    const box = node('div','small muted');
    if (!usage?.recorded) {
      box.append(node('p',null,'Tokenverbrauch: nicht erfasst. Keine Aussage über Kosten oder kostenlose Ausführung.'));
      return box;
    }
    const count = value => Number.isSafeInteger(value) && value >= 0 ? value.toLocaleString('de-DE') : 'unbekannt';
    box.append(node('p',null,`Tokens · Eingang: ${count(usage.input_tokens)} · Ausgang: ${count(usage.output_tokens)} · Gesamt: ${count(usage.total_tokens)} · ${usage.call_count} Aufrufversuche`));
    box.append(node('p',null,`Davon Cache-Eingang: ${count(usage.cached_tokens)} · Reasoning-Ausgang: ${count(usage.reasoning_tokens)} (in Eingang bzw. Ausgang enthalten; unbekannt ist nicht null)`));
    if (!usage.complete) box.append(node('p','warn','Unvollständige Verbrauchsdaten: Zahlen sind nur gemeldete Teilsummen. Fehlende Werte zählen nicht als null.'));
    const details = node('details'); details.dataset.id = `usage-${job.id}`; details.open = openIds.has(details.dataset.id); details.append(node('summary',null,'Verbrauch je Modellaufruf'));
    for (const call of usage.calls || []) {
      const status = {started:'Begonnen / Abschluss nicht erfasst',completed:'Abgeschlossen',failed:'Fehlgeschlagen',cancelled:'Abgebrochen'}[call.status] || 'Unbekannt';
      details.append(node('p',null,`${call.model} · ${status} · Eingang ${count(call.input_tokens)} · Ausgang ${count(call.output_tokens)} · Gesamt ${count(call.total_tokens)}`));
      details.append(node('p',null,`Cache-Eingang: ${count(call.cached_tokens)} · Reasoning-Ausgang: ${count(call.reasoning_tokens)}`));
      const routing = call.routing;
      details.append(node('p',null,routing ? `Reasoning ${routing.requested} → ${routing.effective} · ${routing.role} · ${routing.reason} · Regel ${routing.version} (gesendete Auswahl; keine Messung interner Modellarbeit)` : 'Reasoning-Auswahl nicht erfasst; historischer Aufruf.'));
    }
    box.append(details); return box;
  }

  function renderJobs() {
    renderSequences();
    renderTestChains();
    const journal = $('pilot-transactions');
    if (journal) {
      journal.replaceChildren(); journal.hidden = !(state.pilot_transactions || []).length;
      if (!journal.hidden) journal.append(node('h3',null,'Dauerhafte Pilottransaktionen'),node('p','small muted','Aktueller Schreib- und Wiederherstellungsstand, auch wenn der ursprüngliche Auftrag nicht mehr in der kurzen Auftragsliste steht.'));
      for (const tx of state.pilot_transactions || []) {
        const article=node('article','job');
        renderPilotReceipt(article,{action:'pilot_journal',result:{pilot_transaction:tx}}); journal.append(article);
      }
    }
    const jobs = state.jobs || []; set('job-count',jobs.length);
    const openIds = new Set([...$('jobs').querySelectorAll('details[open]')].map(d => d.dataset.id));
    if (!jobs.length) { $('jobs').replaceChildren(node('p','empty','Noch keine Aufträge. Starte eine Prüfung in der Projektmatrix.')); return; }
    $('jobs').replaceChildren(...jobs.slice().sort((a,b) => String(b.created_at).localeCompare(String(a.created_at))).map(j => {
      const stale = j.result?.stale === true;
      const scope = j.result?.review_scope || (j.request?.scope_kind ? {kind:j.request.scope_kind,id:j.request.scope_id} : null);
      const article = node('article','job'); article.id = `job-${j.id}`; const head = node('div','job-head'); head.append(node('strong',null,labels[j.action] || j.action),node('span',stale ? 'warn' : statusClass(j.status),labels[j.status] || j.status),node('span','muted',scope ? scopeName(scope.kind,scope.id) : j.project_id ? projectName(j.project_id) : 'Alle / System'),node('time',null,stamp(j.created_at)));
      if (stale) head.append(node('span','chip stale-badge','Veraltet – neu prüfen'));
      else if (j.result?.historical_verified === true || j.result?.freshness === 'unknown_requires_rescan') head.append(node('span','chip','Historischer Nachweis · aktuell ungeprüft'));
      if (['queued','running','waiting_for_operator'].includes(j.status)) { const cancel = node('button','button danger','Abbrechen'); cancel.addEventListener('click',async () => { cancel.disabled = true; try { await api('/api/jobs/cancel',{id:j.id}); notify('Abbruch angefordert. Der endgültige Status erscheint im Auftrag.'); await loadState(); } catch (error) { notify(error.message,true); cancel.disabled = false; } }); head.append(cancel); }
      const details = node('details'); details.dataset.id = j.id; details.open = openIds.has(String(j.id)); details.append(node('summary',null,`Ergebnis & Nachweis · ${j.id}`),node('pre',null,format(j.result ?? j.error ?? 'Noch kein Ergebnis. Der Auftrag wurde nicht als erfolgreich bewertet.'))); if (j.error && j.result) details.append(node('pre','bad',j.error)); article.append(head); if (stale) article.append(node('p','small warn','Die Eingangsquellen haben sich geändert. Dieses Ergebnis belegt nicht den aktuellen Projektstand.')); article.append(jobNarrative(j.result),details);
      if (j.token_usage?.recorded || ['hybrid_review','compare_reviews','scope_review','scope_compare','scope_plan','scope_route_b_review','scope_route_b_plan','scope_patch','stage_test','model_check'].includes(j.action)) article.append(tokenUsage(j,openIds));
      if (j.action === 'scope_patch' && j.status === 'completed' && j.result?.stage && pilotAllowed(j.request?.scope_id)) {
        article.append(node('p','small muted','Nur den bereitgestellten tests-Ordner mit Standardbibliothek-unittest ausführen und danach den Supervisor prüfen lassen. Modellaufrufe können Kosten verursachen. Bei fehlendem aktuellen Umfang zuerst „Aufnahme prüfen“.'));
        const test = node('button','button secondary','Pilot testen + Supervisor prüfen'); test.type = 'button'; test.dataset.stageTest = j.id; test.disabled = pilotBusy() || stale || !pilotSourceCurrent(j.request?.scope_id,j.result.scope_hash);
        test.addEventListener('click',() => runPilotAction('stage_test',{stage_job_id:j.id},j.request?.scope_id,j.result.scope_hash)); article.append(test);
        if (!(state.sequences || []).some(s => s.stage_job_id === j.id)) {
          const preview=node('button','button secondary','Prüffolge vorschauen');preview.disabled=pilotBusy();
          preview.addEventListener('click',()=>previewSequence(j.id,preview));article.append(preview);
        }
      }
      renderPilotReceipt(article,j);
      return article;
    }));
  }
  function renderEvents() {
    const events = state.events || [], filter = $('event-filter'); const value = filter.value;
    const sources = [...new Set(events.map(e => e.source || 'Governor'))].sort(); filter.replaceChildren(node('option',null,'Alle Quellen')); filter.firstChild.value = ''; sources.forEach(s => { const o = node('option',null,s); o.value = s; filter.append(o); }); filter.value = sources.includes(value) ? value : '';
    set('event-count',events.length); const filtered = events.filter(e => !filter.value || (e.source || 'Governor') === filter.value).slice().reverse();
    $('events').replaceChildren(...(filtered.length ? filtered.map(e => { const li = node('li','event'); const time = node('time',null,new Date(e.time).toLocaleTimeString('de-DE')); time.title = stamp(e.time); li.append(time,node('span','event-source',e.source || 'Governor'),node('span',`event-message ${['error','critical'].includes(e.level) ? 'bad' : e.level === 'warning' ? 'warn' : ''}`,`[${e.level || 'info'}] ${format(e.message)}`)); return li; }) : [node('li','empty','Keine Ereignisse für diese Auswahl.')]));
  }
  const registryRoles = {parent:'Hauptprojekt',module:'Modul',contracts:'Verträge / Schnittstellen',member:'Mitglied'};
  function registryGroupMembers(group,projects) {
    const known = new Map(projects.map(project => [project.id,project])), members = new Map();
    for (const member of group?.members || []) {
      const id = typeof member === 'string' ? member : member.project_id;
      if (!id) continue;
      const project = known.get(id);
      members.set(id,project || {id,name:projectName(id),group_id:group.id,role:member.role || '',archived:Boolean(member.archived)});
    }
    for (const project of projects) if (project.group_id === group?.id) members.set(project.id,project);
    return [...members.values()];
  }
  function registryDirectoryEntries(groups,projects) {
    const groupEntries = groups.map(group => {
      const members = registryGroupMembers(group,projects);
      return {kind:'group',id:group.id,name:group.name,archived:Boolean(group.archived),memberCount:members.length,activeMemberCount:members.filter(member => !member.archived).length};
    });
    const projectEntries = projects.filter(project => !project.group_id).map(project => ({kind:'project',id:project.id,name:project.name,archived:Boolean(project.archived)}));
    return [...groupEntries,...projectEntries];
  }
  function openRegistryScope(kind,id) {
    focusedScope = {kind,id};
    const intakeMatches = intakeScope?.kind === kind && intakeScope?.id === id;
    const plansMatch = plansScope?.kind === kind && plansScope?.id === id;
    $('registry-intake').hidden = !intakeMatches; $('scope-plans').hidden = !plansMatch; $('scope-guide').hidden = !intakeMatches;
    activateTab('registry');
    renderFocusedScope();
    renderRegistryObservations();
    $('registry-focused-view').focus({preventScroll:true});
    $('panel-registry').scrollIntoView({behavior:'smooth',block:'start'});
  }
  function renderFocusedScopeActions(kind,id,item,group) {
    const actions = $('registry-focused-actions');
    const signature = JSON.stringify([kind,id,item?.archived,item?.group_id,group?.archived]);
    if (actions.dataset.scopeSignature === signature) return;
    actions.dataset.scopeSignature = signature;
    if (item) actions.replaceChildren(scopeActions(kind,id,Boolean(item.group_id)));
    else actions.replaceChildren();
  }
  function registryMemberButton(project) {
    const button = node('button','text-button',project.name || projectName(project.id));
    button.type = 'button'; button.dataset.openProjectId = project.id;
    button.addEventListener('click',() => openRegistryScope('project',project.id));
    return button;
  }
  function renderRegistryDirectory() {
    const registry = state.registry, groups = registry?.groups || [], projects = registry?.projects || [];
    const entries = registryDirectoryEntries(groups,projects), cards = $('registry-directory-cards');
    set('directory-summary',registry ? `${groups.length} Gruppen · ${projects.filter(project => !project.group_id).length} eigenständige Projekte` : 'Register nicht verfügbar');
    const display = entries.map(entry => [entry,reviewScopeState(entry.kind,entry.id)]);
    const signature = JSON.stringify(display);
    if (cards.dataset.directory === signature) return;
    cards.dataset.directory = signature;
    if (!entries.length) {
      cards.replaceChildren(node('p','empty',registry ? 'Noch keine Gruppen oder eigenständigen Projekte registriert.' : 'Der lokale Dienst stellt noch kein Projektregister bereit.')); return;
    }
    cards.replaceChildren(...display.map(([entry,review]) => {
      const card = node('article',`registry-directory-card${entry.archived ? ' archived' : ''}`);
      const heading = node('div','registry-directory-heading');
      heading.append(node('span','eyebrow',entry.kind === 'group' ? 'PROJEKTGRUPPE' : 'EIGENSTÄNDIGES PROJEKT'),node('h4',null,entry.name || entry.id));
      heading.append(node('span',`chip${entry.archived ? ' archived-chip' : ''}`,entry.archived ? 'Archiviert' : entry.kind === 'group' ? `${entry.activeMemberCount} aktiv · ${entry.memberCount} gesamt` : 'Aktiv'));
      card.append(heading,reviewIndicator(review),node('p','small muted',review.detail));
      if (entry.kind === 'group') card.append(node('p','small muted',`${entry.memberCount} zugeordnete Projekte · eigener Gruppenumfang`));
      const open = node('button','button secondary','Öffnen'); open.type = 'button'; open.dataset.openScopeKind = entry.kind; open.dataset.openScopeId = entry.id;
      open.addEventListener('click',() => openRegistryScope(entry.kind,entry.id)); card.append(open);
      return card;
    }));
  }
  function renderFocusedScope() {
    const view = $('registry-focused-detail');
    if (!focusedScope) {
      if (view.dataset.scopeSignature !== 'empty') { view.replaceChildren(node('p','empty','Öffne eine Gruppe oder ein Projekt aus der Projektübersicht.')); view.dataset.scopeSignature = 'empty'; }
      renderFocusedScopeActions(null,null,null,null); registryControls(); return;
    }
    const registry = state.registry || {}, projects = registry.projects || [], kind = focusedScope.kind, id = focusedScope.id;
    const group = kind === 'group' ? (registry.groups || []).find(item => item.id === id) : null;
    const project = kind === 'project' ? projects.find(item => item.id === id) : null;
    const item = group || project;
    if (!item) { const signature = JSON.stringify([kind,id,'missing']); if (view.dataset.scopeSignature !== signature) { view.replaceChildren(node('p','empty','Dieser Eintrag ist im aktuellen Register nicht mehr vorhanden. Kehre zur Projektübersicht zurück, um einen verfügbaren Umfang zu öffnen.')); view.dataset.scopeSignature = signature; } renderFocusedScopeActions(kind,id,null,null); registryControls(); return; }
    const parentGroup = project?.group_id ? (registry.groups || []).find(item => item.id === project.group_id) : null;
    const members = kind === 'group' ? registryGroupMembers(group,projects) : [];
    const review = reviewScopeState(kind,id);
    const memberIds = new Set(kind === 'group' ? members.map(member => member.id) : [id]);
    const steps = governanceSteps().filter(step => memberIds.has(step.project_id));
    const accepted = steps.filter(step => step.accepted === true).length;
    const signature = JSON.stringify([kind,id,item,parentGroup,review.kind,review.label,review.detail,steps.map(step => [step.id,step.accepted,step.status]),members.map(member => [member.id,member.name,member.role,member.archived])]);
    $('scope-guide').hidden = !(intakeScope?.kind === kind && intakeScope?.id === id);
    renderFocusedScopeActions(kind,id,item,parentGroup);
    if (view.dataset.scopeSignature === signature) { registryControls(); return; }
    view.dataset.scopeSignature = signature;
    const title = node('div','registry-scope-heading');
    const type = kind === 'group' ? 'PROJEKTGRUPPE' : project.group_id ? `PROJEKT · ${registryRoles[project.role] || 'GRUPPENMITGLIED'}` : 'EIGENSTÄNDIGES PROJEKT';
    title.append(node('span','eyebrow',type),node('h2',null,item.name || item.id));
    title.append(node('span',`chip${item.archived ? ' archived-chip' : ''}`,item.archived ? 'Archiviert' : kind === 'group' ? `${members.length} Mitglieder` : project.group_id ? registryRoles[project.role] || project.role || 'Rolle offen' : 'Aktiv'));
    const overview = node('section','registry-scope-overview'); overview.append(title);
    const reviewLine = node('div','registry-scope-summary');
    const reviewItem = node('div','registry-summary-item'); reviewItem.append(node('span','meta-label','REVIEWSTATUS'),reviewIndicator(review),node('p','small muted',review.detail));
    const summaryLabel = node('span','meta-label','GOVERNOR-MATRIX');
    const matrix = node('div','registry-summary-item'); matrix.append(summaryLabel,node('strong',null,steps.length ? `${accepted} / ${steps.length}` : 'Keine Schritte definiert'),node('span','small muted','ausdrücklich abgenommene definierte Schritte'));
    reviewLine.append(reviewItem,matrix); overview.append(reviewLine);
    if (item.archived || (kind === 'group' && members.some(member => member.archived))) overview.append(node('p','small warn','Dieser Umfang enthält archivierte Einträge. Verfügbare Aktionen bleiben durch die vorhandenen Archivierungswachen gesperrt.'));
    if (kind === 'group') {
      const memberSection = node('section','registry-focused-members-section');
      memberSection.append(node('h3',null,'Mitglieder'),node('p','small muted','Jedes Mitglied öffnet seinen eigenen Projektüberblick. Projekt- und Gruppenreviews bleiben getrennte Nachweise.'));
      const memberList = node('div','registry-member-list'); memberList.id = 'registry-focused-members';
      if (!members.length) memberList.append(node('p','empty','Noch keine Mitglieder. Dauerhafte Zuordnungen bearbeitest du im Register.'));
      for (const member of members) {
        const row = node('div','registry-member-row'); row.append(registryMemberButton(member));
        row.append(node('span','chip',registryRoles[member.role] || member.role || 'Rolle offen'));
        if (member.archived) row.append(node('span','chip archived-chip','Archiviert'));
        memberList.append(row);
      }
      memberSection.append(memberList); overview.append(memberSection);
    } else if (project.group_id) {
      const backlink = node('button','text-button registry-group-backlink',`← Gruppe: ${scopeName('group',project.group_id)}`);
      backlink.type = 'button'; backlink.id = 'registry-focused-group-backlink'; backlink.dataset.openGroupId = project.group_id;
      backlink.addEventListener('click',() => openRegistryScope('group',project.group_id)); overview.append(backlink);
    }
    if (project?.requirements) { const details = node('details','registry-project-requirements'); details.append(node('summary',null,'Ziel & Anforderungen'),node('p','readable-text',project.requirements)); overview.append(details); }
    view.replaceChildren(overview);
    registryControls();
  }
  function returnToProjectDirectory() {
    activateTab('directory');
    $('panel-directory').scrollIntoView({behavior:'smooth',block:'start'});
  }
  function scopeName(kind, id) { return (kind === 'group' ? state?.registry?.groups : state?.registry?.projects)?.find(item => item.id === id)?.name || id || 'Unbekannter Umfang'; }
  function scopeMembers(kind, id) { return (state?.registry?.projects || []).filter(p => kind === 'group' ? p.group_id === id : p.id === id); }
  function scopeBlocked(action, kind, id) {
    const members = scopeMembers(kind,id), group = state?.registry?.groups?.find(g => g.id === id);
    return !members.length || members.some(p => p.archived) || (kind === 'group' && group?.archived) || (action !== 'intake' && members.some(p => !p.model_egress)) || (['scope_plan','scope_route_b_plan'].includes(action) && (intakeScope?.kind !== kind || intakeScope?.id !== id || !intakeScope?.result.plan_ready));
  }
  function scopeActions(kind, id, grouped = false) {
    const section = node('div','scope-actions'), buttons = node('div','detail-actions');
    const observation = node('div','scope-observation'); observation.dataset.observationKind = kind; observation.dataset.observationId = id; section.append(observation);
    const criticalLabel = node('label','check-label'); const critical = node('input'); critical.type = 'checkbox'; criticalLabel.append(critical,document.createTextNode(' Für Route-B-Reviews eine unabhängige Astra-Prüfung ausdrücklich anfordern'));
    for (const [action,label] of [['intake',grouped ? 'Einzelaufnahme prüfen' : 'Aufnahme prüfen'],['scope_review',kind === 'group' ? 'Gruppe hybrid reviewen' : 'Projekt hybrid reviewen'],['scope_compare','Sol / Astra vergleichen'],['scope_plan','Matrixplan hybrid entwerfen'],['scope_route_b_review','Route B · Umfang prüfen'],['scope_route_b_plan','Route B · Matrixplan entwerfen']]) {
      const button = node('button','button quiet',label); button.type = 'button'; button.dataset.scopeAction = action; button.dataset.scopeKind = kind; button.dataset.scopeId = id;
      button.title = action === 'intake' ? 'Liest ausschließlich den ausgewählten Umfang lokal neu ein. Kein Modellaufruf.' : 'Übermittelt ausschließlich diesen Umfang an Modelle. Alle Mitglieder benötigen gespeicherte Modellfreigaben. Kosten möglich.';
      button.addEventListener('click',() => runScope(action,kind,id,critical.checked)); buttons.append(button);
    }
    section.append(buttons,criticalLabel,node('p','small muted','Route-B-Review: Sol High → Luna Max; Astra Medium bei erkanntem Risiko/Widerspruch oder obiger Auswahl. Route-B-Matrixplan: Astra Medium prüft immer zusätzlich und unabhängig. Beratend; Modellversand nur mit Freigabe jedes Mitglieds.'));
    if (grouped) section.append(node('p','small muted','Einzelaufnahme im Projektumfang · Gruppenzugehörigkeit und gemeinsame Gates bleiben verbindlich.'));
    return section;
  }
  async function runScope(action, kind, id, criticalReview = false) {
    const key = `scope:${action}:${kind}:${id}`; if (pending.has(key) || scopeBlocked(action,kind,id)) return;
    const request = action === 'intake' ? ++intakeRequest : null;
    pending.add(key); registryControls();
    try {
      if (action === 'intake') {
        const result = await api(`/api/scope?kind=${encodeURIComponent(kind)}&id=${encodeURIComponent(id)}`);
        if (request !== intakeRequest) return;
        const box = $('registry-intake-result'); $('registry-intake').hidden = false;
        box.replaceChildren(node('h3',null,scopeName(kind,id)),node('p','small muted',`Lokal erfasst: ${stamp(new Date().toISOString())}. Momentaufnahme; spätere Änderungen erfordern eine erneute Aufnahme.`),node('p',result.plan_ready ? 'small good' : 'small warn',result.plan_ready ? 'Aufnahmevoraussetzungen vorhanden. Das ist keine Planabnahme.' : 'Aufnahme unvollständig. Anforderungen, Gedächtnisse, ausdrückliche Bestätigung und fehlende Nachweise prüfen.'),node('code','evidence-hash',`Umfangshash: ${result.scope_hash || 'Nicht geliefert'}`));
        for (const entry of result.intake || []) {
          const item = node('article','registry-project'); item.append(node('h3',null,scopeName('project',entry.project_id)),node('p','small',`Anforderungen: ${entry.requirements_recorded ? 'erfasst' : 'fehlen'} · Gedächtnisse: ${entry.memories_present ? 'vorhanden' : 'fehlen'} · Evidenz: ${entry.evidence_complete ? 'im Prüfumfang vollständig' : 'unvollständig'}`),node('p',entry.intake_accepted ? 'small good' : 'small warn',entry.intake_accepted ? 'Aufnahme ausdrücklich und quellengebunden bestätigt.' : 'Aufnahme noch nicht für diesen Quellenstand bestätigt.'),node('strong','small','Fehlende Nachweise / Hinweise'),readable(entry.missing_proofs || [])); box.append(item);
        }
        prepareIntakeForms(kind,id,result); $('scope-guide').hidden = false; renderWorkflowGuide();
        $('registry-intake').scrollIntoView({block:'nearest',behavior:'smooth'});
      } else {
        const body = {action,scope_kind:kind,scope_id:id,supervisor:$('supervisor').value};
        if (['scope_route_b_review','scope_route_b_plan'].includes(action)) body.critical_review = criticalReview;
        const result = await api('/api/actions',body);
        notify(`${scopeName(kind,id)}: Beratender Reviewauftrag ${result.job?.id || ''} angenommen.`); activateTab('jobs'); await loadState();
      }
    } catch (error) { if (action !== 'intake' || request === intakeRequest) notify(`Prüfung für ${scopeName(kind,id)} nicht gestartet: ${error.message}`,true); }
    finally { pending.delete(key); registryControls(); }
  }
  function intakeDraftKey(scope, projectId = '') { return JSON.stringify([scope.kind,scope.id,projectId]); }
  function rememberIntakeDraft() {
    if (!intakeScope || !intakeProject) return;
    const fields = Object.fromEntries(['requirements','test-strategy','dependencies','open-evidence'].map(field => [field,$(`scope-intake-${field}`).value]));
    intakeDrafts.set(intakeDraftKey(intakeScope,intakeProject),{fields,draft:loadedIntakeDraft,source_hash:intakeScope.result.scope_hash});
    intakeSelections.set(intakeDraftKey(intakeScope),intakeProject);
  }
  function restoreIntakeDraft() {
    intakeProject = $('scope-intake-project').value;
    const saved = intakeScope && intakeDrafts.get(intakeDraftKey(intakeScope,intakeProject));
    loadedIntakeDraft = saved?.draft || null;
    $('scope-intake-draft').replaceChildren();
    for (const field of ['requirements','test-strategy','dependencies','open-evidence']) $(`scope-intake-${field}`).value = saved?.fields[field] || '';
    set('scope-intake-feedback',saved ? (saved.source_hash !== intakeScope.result.scope_hash ? 'Quellenstand geändert. Wiederhergestellte Eingaben erneut prüfen; noch nicht bestätigt.' : 'Ungespeicherte Eingaben dieses Projekts wiederhergestellt. Bestätigung bleibt separat.') : '');
  }
  function changeIntakeProject() {
    rememberIntakeDraft(); restoreIntakeDraft(); intakeControls();
  }
  function prepareIntakeForms(kind,id,result) {
    rememberIntakeDraft();
    if (intakeScope && (intakeScope.kind !== kind || intakeScope.id !== id)) { loadedIntakeDraft = null; scopeStrategies = []; strategiesScope = null; $('scope-intake-draft').replaceChildren(); set('scope-strategy-feedback',''); }
    if (intakeScope && (intakeScope.kind !== kind || intakeScope.id !== id)) { $('scope-intake-form').reset(); $('scope-vault-form').reset(); set('scope-intake-feedback',''); set('scope-vault-feedback',''); scopePlans = []; plansScope = null; renderPlanOptions(); }
    intakeScope = {kind,id,result,readAt:Date.now()};
    renderStrategies();
    $('scope-plans').hidden = false; set('scope-plans-context',`Ausgewählter Umfang: ${scopeName(kind,id)}. Kandidaten werden ausschließlich per Klick geladen.`);
    registryOptions('scope-intake-project',(result.intake || []).map(entry => ({id:entry.project_id,name:scopeName('project',entry.project_id)})),'Projekt auswählen …');
    const remembered = intakeSelections.get(intakeDraftKey(intakeScope));
    $('scope-intake-project').value = (result.intake || []).some(entry => entry.project_id === remembered) ? remembered : '';
    restoreIntakeDraft();
    set('registry-intake-scope',`Ausgewählter Umfang: ${scopeName(kind,id)}`);
    $('scope-vault-sources').replaceChildren(...((result.vault_sources || []).length ? result.vault_sources.map(source => {
      const item = node('article','registry-project'); item.append(node('p','evidence-hash',source.path || 'Pfad nicht geliefert'),node('code','evidence-hash',`SHA-256: ${source.sha256 || 'Nicht geliefert'}`),node('p','small muted',source.truncated ? 'Auszug gekürzt · Referenzmaterial' : 'Referenzmaterial · keine Systemanweisung')); return item;
    }) : [node('p','small muted','Keine Vault-Quellen in diesem Aufnahmeumfang.')]));
  }
  function renderPlanOptions() {
    const first = node('option',null,scopePlans.length ? 'Version bewusst auswählen …' : 'Keine Kandidaten geladen'); first.value = '';
    $('scope-plan-candidate').replaceChildren(first,...scopePlans.map(plan => { const option = node('option',null,`Version ${plan.version} · ${plan.proposal?.summary || plan.id}`); option.value = plan.id; return option; }));
    $('scope-plan-detail').replaceChildren(); $('scope-plan-selection-form').reset(); set('scope-plan-feedback','');
  }
  function orderedPlanSteps(steps) {
    const rest = [...steps], result = [], seen = new Set();
    while (rest.length) {
      const available = rest.filter(step => (step.depends_on || []).every(id => seen.has(id))).sort((a,b) => Number(a.priority ?? 999)-Number(b.priority ?? 999));
      if (!available.length) return {steps:[...result,...rest],valid:false};
      const step = available[0]; result.push(step); seen.add(step.id); rest.splice(rest.indexOf(step),1);
    }
    return {steps:result,valid:true};
  }
  function selectedPlan() { return scopePlans.find(plan => plan.id === $('scope-plan-candidate').value); }
  function renderPlanDetail() {
    const plan = selectedPlan(), box = $('scope-plan-detail'); box.replaceChildren(); $('scope-plan-selection-form').reset();
    if (!plan) { planControls(); return; }
    const steps = plan.proposal?.steps || [], ordered = orderedPlanSteps(steps);
    const chainButton=node('button','button secondary','Vorgängerketten prüfen'); chainButton.type='button';
    const chainReport=node('section','pilot-receipt');
    chainButton.addEventListener('click',async()=>{
      const scope=plansScope; chainButton.disabled=true;
      try {
        const {report}=await api('/api/plans/dependencies',{scope_kind:scope.kind,scope_id:scope.id,candidate_id:plan.id});
        if(selectedPlan()?.id!==plan.id || plansScope!==scope || !chainReport.isConnected)return;
        chainReport.replaceChildren(node('h3',null,'Vorgängerketten'),node('p','small',`Prüfzeitpunkt: ${report.checked_at}`),node('p',null,report.current ? 'Plan und Quellen zum Prüfzeitpunkt aktuell.' : report.reason),node('p','small warn',report.limitation));
        const list=node('ul','readable-list');
        for(const step of report.steps) {
          const item=node('li',null,`${step.title} (${step.project_id}) · ${step.selected ? 'Ausgewählt' : 'Nicht ausgewählt'} · Direkte Vorgänger: ${step.direct_predecessors.join(', ') || 'Keine'} · Alle Vorgänger: ${step.all_predecessors.join(', ') || 'Keine'} · Fehlende Abschlussbelege: ${step.missing_completion_ids.join(', ') || 'Keine'} · Letzter Testauftrag: ${step.latest_test ? (labels[step.latest_test.status] || step.latest_test.status) : 'Keiner'} · Abschluss: ${{accepted:step.action==='test'?'Test erfolgreich belegt':step.action==='change'?'Änderung technisch belegt':'Fachlich abgenommen',stale:'Veraltet',withdrawn:'Zurückgenommen',not_proven:'Nicht belegt'}[step.completion_status] || 'Unbekannt'}.`);
          if (step.test_attempts) {
            const attempts=step.test_attempts;
            item.append(node('p','small',`Testversuche: ${attempts.used}/${attempts.limit} · Verbleibend: ${attempts.remaining}. Jeder Start erfolgt ausdrücklich; auch abgebrochene Versuche zählen.`));
            if(attempts.reason) item.append(node('p','small warn',attempts.reason));
            if(attempts.history?.length) {
              const history=node('ul','small');
              for(const attempt of attempts.history) history.append(node('li',null,`${attempt.created_at} · ${labels[attempt.status] || attempt.status} · ${attempt.id}`));
              item.append(history);
            }
          }
          if (step.test_run_available) {
            const run=node('button','button secondary','Diesen Testschritt ausführen'); run.disabled=pilotBusy();
            run.addEventListener('click',async()=>{
              if(run.disabled)return; run.disabled=true;
              try {
                const response=await api('/api/plans/test',{candidate_id:plan.id,step_id:step.id,scope_hash:report.scope_hash,selection_id:report.selection_id});
                notify(`Testauftrag ${response.job.id} angenommen. Danach Vorgängerketten erneut prüfen.`);
                activateTab('jobs'); await loadState();
              } catch(error) { notify(error.message,true); run.disabled=false; }
            });
            item.append(node('p','small muted','Fester Python-Unittest-Adapter auf einer Kopie der ausgewählten Dateien. Kein Modellaufruf, keine Änderung am Original und keine automatische Folgeausführung.'),run);
          }
          if(step.completion_receipt) item.append(node('p','small',`Abnahmevermerk: ${step.completion_receipt.note}`));
          const canAccept=report.current && step.selected && !step.missing_completion_ids.length && ['review','clarify'].includes(step.action) && step.completion_status!=='accepted';
          const canWithdraw=step.completion_receipt?.status==='accepted';
          if(canAccept || canWithdraw) {
            const note=node('textarea'); note.maxLength=2000; note.setAttribute('aria-label',`Abnahmebegründung für ${step.title}`);
            const controls=node('div'); controls.append(note,node('p','small muted','Ausdrückliche fachliche Erklärung; keine Produktfreigabe. Bitte Prüfung bzw. Rücknahme begründen.'));
            for(const [action,label,allowed] of [['complete-step','Diesen Klärungs-/Reviewschritt fachlich abnehmen',canAccept],['withdraw-completion','Diese Abnahme zurücknehmen',canWithdraw]]) {
              if(!allowed) continue;
              const button=node('button','button secondary',label); button.type='button';
              button.addEventListener('click',async()=>{
                if(!note.value.trim()) { notify('Bitte eine fachliche Begründung eingeben.',true); return; }
                controls.querySelectorAll('button').forEach(b=>b.disabled=true);
                const payload=action==='complete-step' ? {scope_kind:scope.kind,scope_id:scope.id,candidate_id:plan.id,step_id:step.id,scope_hash:report.scope_hash,selection_id:report.selection_id,note:note.value} : {candidate_id:plan.id,step_id:step.id,expected_receipt_id:step.completion_receipt.id,note:note.value};
                try { await api('/api/plans/'+action,payload); if(chainButton.isConnected) chainButton.click(); }
                catch(error) { notify(error.message,true); controls.querySelectorAll('button').forEach(b=>b.disabled=false); }
              }); controls.append(button);
            }
            item.append(controls);
          }
          list.append(item);
        }
        chainReport.append(list,node('p','small muted','Momentaufnahme; keine Ausführung freigegeben. Nach Änderungen erneut prüfen.'));
        if(report.current && report.steps.filter(s=>s.selected && s.action==='change').length>=2){
          const changes=node('button','button secondary','Abhängige Änderungen vorschauen');changes.type='button';
          changes.addEventListener('click',()=>showChangeChainPreview(plan,report));chainReport.append(changes);
        }
        if(report.current && report.steps.filter(s=>s.selected && s.action==='test' && s.completion_status!=='accepted').length>=2){
          const chains=node('button','button secondary','Testkette vorbereiten');chains.type='button';
          chains.addEventListener('click',()=>showTestChain(plan,report));chainReport.append(chains);
        }
      } catch(error) { if(chainReport.isConnected) chainReport.replaceChildren(node('p','small warn',error.message)); }
      finally { chainButton.disabled=false; }
    });
    box.append(chainButton,chainReport);
    if(steps.filter(step=>step.action==='change').length>=2){
      const history=node('button','button secondary','Änderungskette und Historie');history.type='button';
      history.addEventListener('click',()=>showChangeChainPreview(plan));box.append(history);
    }
    box.append(node('h3',null,`Version ${plan.version} · ${plan.proposal?.summary || 'Planungskandidat'}`),node('code','evidence-hash',`Quellenstand: ${plan.scope_hash}`),node('code','evidence-hash',`Vorschlagshash: ${plan.proposal_hash}`));
    if (!ordered.valid) box.append(node('p','small warn','Unaufgelöste oder zyklische Abhängigkeiten. Auswahl ist gesperrt.'));
    for (const [index,step] of ordered.steps.entries()) {
      const article = node('article','governance-step'); const heading = node('div','step-heading'); heading.append(node('span','step-rank',String(index+1).padStart(2,'0')),node('h3',null,step.title));
      article.append(heading,node('p','small muted',`${scopeName('project',step.project_id)} · Priorität ${step.priority} · Aktion ${step.action}`),node('p','readable-text',step.rationale),node('p','small',`Abhängigkeiten: ${step.depends_on?.length ? step.depends_on.map(id => steps.find(s => s.id === id)?.title || id).join(' · ') : 'Keine'}`),node('strong','small','Dateiumfang'),readable(step.scope || []),node('strong','small','Vorgesehene Tests'),readable(step.tests || []));
      const label = node('label','check-label'); const input = node('input'); input.type = 'checkbox'; input.value = step.id; input.dataset.planStep = step.id; input.addEventListener('change',planControls); label.append(input,document.createTextNode('Diesen Schritt auswählen')); article.append(label); box.append(article);
      if (plansScope?.kind === 'project' && plansScope.id === step.project_id && step.action === 'change' && !step.depends_on?.length && pilotAllowed(step.project_id)) {
        article.append(node('p','small warn','Nur dieser ausdrücklich konfigurierte Einzelpilot: Änderungsvorschlag in einem isolierten Arbeitsbereich. Aktuelle bestätigte Planauswahl erforderlich. Keine Änderung der Produktdateien und keine Rückübernahme.'));
        const patch = node('button','button secondary','Änderung im Pilot-Arbeitsbereich vorschlagen'); patch.type = 'button'; patch.dataset.pilotPatch = step.id;
        const routine = node('input'); routine.type = 'checkbox'; routine.dataset.routineConfirmation = step.id; routine.disabled = state.settings?.reasoning_mode !== 'auto';
        if (step.scope?.length && step.scope.every(path => /\.(md|txt)$/i.test(path))) {
          const confirmation = node('label','check-label');
          confirmation.append(routine,document.createTextNode('Nur im Auto-Modus: als unkritische Dokumentationsroutine bestätigen. Vollständiger Plan, keine Sicherheits-, Diagnose-, Backup- oder Migrationsarbeit. Nur der Vorschlag darf Low nutzen; Review bleibt Medium.'));
          article.append(confirmation);
        }
        patch.addEventListener('click',() => runPilotAction('scope_patch',{scope_kind:'project',scope_id:step.project_id,candidate_id:plan.id,step_id:step.id,...(routine.checked ? {routine_note:'Unkritische Dokumentationsroutine bestätigt; vollständiger Plan, keine Sicherheits-, Diagnose-, Backup- oder Migrationsarbeit.'} : {})},step.project_id,plan.scope_hash)); article.append(patch);
      }
    }
    const review = node('details'); review.append(node('summary',null,'Unabhängiger Review'),readable(plan.review || 'Kein Review geliefert')); box.append(review);
    const index = scopePlans.indexOf(plan), previous = scopePlans[index+1];
    if (previous) {
      const diff = node('details'); diff.append(node('summary',null,`Vergleich mit vorheriger Version ${previous.version}`));
      const grid = node('div','diff-grid'); for (const [label,proposal] of [[`Vorher · Version ${previous.version}`,previous.proposal],[`Ausgewählt · Version ${plan.version}`,plan.proposal]]) { const part = node('div'); part.append(node('h3',null,label),node('pre',null,format(proposal))); grid.append(part); } diff.append(grid); box.append(diff);
    } else box.append(node('p','small muted','Keine frühere Version für diesen Vergleich geladen.'));
    planControls();
  }
  function planSelectionIssue(plan, ids, mode) {
    if (!plan) return 'Zuerst eine Planversion auswählen.';
    if (!ids.length) return 'Mindestens einen Schritt bewusst auswählen.';
    const steps = plan.proposal?.steps || [], seen = new Set();
    for (const id of ids) {
      const step = steps.find(item => item.id === id);
      if (!step) return 'Die Auswahl enthält einen unbekannten Schritt. Planversion erneut laden.';
      const missing = (step.depends_on || []).filter(dependency => !seen.has(dependency));
      if (missing.length) return `Für „${step.title || id}“ fehlen vorher ausgewählte Voraussetzungen: ${missing.map(dependency => steps.find(item => item.id === dependency)?.title || dependency).join(' · ')}. Wähle diese Schritte ebenfalls und bestätige die Schrittfolge in der angezeigten Planreihenfolge.`;
      seen.add(id);
    }
    if (!mode) return 'Einzelschritt oder Schrittfolge bewusst wählen.';
    if (mode === 'single' && ids.length !== 1) return 'Für „Einzelner Schritt“ genau einen unabhängigen Schritt auswählen oder auf „Schrittfolge“ wechseln.';
    return '';
  }
  function workflowHint(v) {
    const hint = (step,title,reason,target=null) => ({step,title,reason,target});
    if (v.busy) return hint(1,'Prüfung läuft','Antwort abwarten. Der laufende Auftrag behält seinen ursprünglichen Umfang.');
    if (!v.scope) return hint(1,'Umfang wählen','Bei einem Projekt oder einer Gruppe „Aufnahme prüfen“ wählen. Das liest ausschließlich lokale Quellen.');
    if (!v.current) return hint(1,'Aufnahme erneut prüfen','Der gelesene Quellenstand ist veraltet oder ungeprüft. Erst den gewählten Umfang frisch einlesen.','intake');
    if (!v.ready) {
      if (!v.member) return hint(2,'Projekt für die Aufnahme wählen','Bei Gruppen wird jedes Mitglied separat bestätigt.','scope-intake-project');
      if (!v.proofs) return hint(2,'Aufnahmenachweise ergänzen','Gedächtnis oder vollständige Quelle fehlt. Hinweise in der lokalen Aufnahme prüfen.');
      if (v.staleDraft) return hint(2,'Aktuellen Entwurf prüfen','Der geladene Entwurf gehört zu einem älteren Quellenstand. Erneutes Laden ersetzt die vier Textfelder.','scope-intake-draft-load');
      if (v.canConfirm) return hint(2,'Eingaben prüfen und Aufnahme bestätigen','Die Bestätigung bindet diese vier Felder an den gelesenen Quellenstand; sie erteilt keine Produktfreigabe.','intake-confirm');
      return hint(2,'Aufnahme vervollständigen','Alle vier Felder bewusst ausfüllen; danach ausdrücklich bestätigen. Bei Gruppen auch die anderen Mitglieder prüfen.','scope-intake-requirements');
    }
    if (!v.plansLoaded) return hint(3,'Kandidaten und Strategie laden','Bereits gespeicherte Planung bewusst abrufen; dabei wird kein Modellauftrag gestartet.','scope-plans-load');
    if (!v.planCount) return hint(3,'Planentwurf anfordern','Noch kein Kandidat geladen. „Matrixplan hybrid entwerfen“ benötigt die Modellfreigabe aller Mitglieder und kann Kosten verursachen.','plan');
    if (!v.plan) return hint(3,'Planversion bewusst auswählen','Eine Version zur Prüfung wählen. Auswahl allein übernimmt oder startet nichts.','scope-plan-candidate');
    if (!v.planCurrent) return hint(3,'Planstand erneut laden','Der Kandidat passt nicht zum aktuell geprüften Umfang. Keine Freigabe aus historischen Daten ableiten.','scope-plans-load');
    if (!v.validPlan) return hint(3,'Planabhängigkeiten klären','Die Schrittreihenfolge ist nicht gültig. Kandidat und Abhängigkeiten vor einer Bestätigung prüfen.');
    return hint(4,'Planinhalt und getrennte Freigaben prüfen','Strategieübernahme und Schrittauswahl sind getrennte Entscheidungen. Zulässige Pilotaktionen bleiben ausdrücklich auszulösen; keine automatische Ausführung.','scope-plan-detail');
  }
  function renderWorkflowGuide() {
    const box = $('scope-guide'); if (!box) return;
    document.querySelectorAll('.workflow-next').forEach(el => el.classList.remove('workflow-next'));
    const scope = intakeScope, plan = selectedPlan();
    const member = scope?.result.intake?.find(entry => entry.project_id === $('scope-intake-project').value);
    const busy = [...pending].some(key => key.startsWith('scope:intake:') || ['scope:write','intake:draft','plans:load','plans:approve','strategies:adopt'].includes(key));
    const matching = scope && plansScope?.kind === scope.kind && plansScope?.id === scope.id;
    const hint = workflowHint({scope:Boolean(scope),busy,current:scopeSourceCurrent(scope?.result.scope_hash),ready:scope?.result.plan_ready,
      member:Boolean(member),proofs:member?.memories_present && member?.evidence_complete,
      staleDraft:loadedIntakeDraft && !scopeSourceCurrent(loadedIntakeDraft.loaded_scope_hash),
      canConfirm:!$('scope-intake-form').querySelector('[type=submit]').disabled,
      plansLoaded:matching && strategiesScope === scope,planCount:scopePlans.length,plan:Boolean(plan),
      planCurrent:matching && plan?.current !== false && scopeSourceCurrent(plan?.scope_hash),validPlan:plan && orderedPlanSteps(plan.proposal?.steps || []).valid});
    const scopeButton = action => [...document.querySelectorAll('[data-scope-action]')].find(el => el.dataset.scopeAction === action && el.dataset.scopeKind === scope?.kind && el.dataset.scopeId === scope?.id);
    const target = hint.target === 'intake' ? scopeButton('intake') : hint.target === 'plan' ? scopeButton('scope_plan') : hint.target === 'intake-confirm' ? $('scope-intake-form').querySelector('[type=submit]') : hint.target ? $(hint.target) : null;
    set('scope-guide-context',scope ? `${scope.kind === 'group' ? 'Gruppenplanung · keine allgemeine Gruppenausführung' : 'Einzelprojekt'}: ${scopeName(scope.kind,scope.id)}` : 'Noch kein Umfang ausgewählt');
    set('scope-guide-title',`${hint.step} / 4 · ${hint.title}`);
    set('scope-guide-reason',hint.reason + (target?.disabled ? ' Dieser Bedienweg ist derzeit gesperrt; Voraussetzungen oder laufende Aufträge prüfen.' : ''));
    if (target && !target.disabled) target.classList.add('workflow-next');
  }
  function planControls() {
    const busy = pending.has('plans:load') || pending.has('plans:approve') || pending.has('strategies:adopt'), plan = selectedPlan();
    const ids = [...$('scope-plan-detail').querySelectorAll('[data-plan-step]:checked')].map(input => input.value), mode = $('scope-plan-mode').value;
    const matching = intakeScope && plansScope?.kind === intakeScope.kind && plansScope?.id === intakeScope.id;
    const fresh = matching && scopeSourceCurrent(plan?.scope_hash) && plan?.current !== false;
    const strategyReady = strategiesScope === intakeScope && strategiesScope?.result.scope_hash === plan?.scope_hash;
    if ($('scope-strategy-status')) {
      const current = strategiesScope === intakeScope && scopeStrategies[0]?.current === true && scopeSourceCurrent(scopeStrategies[0]?.scope_hash);
      set('scope-strategy-status',current ? 'Aktuell zum geprüften Quellenstand · keine Ausführungsfreigabe.' : 'Historische Strategie · Aktualität nicht bestätigt. Umfang und Strategien erneut laden.',current ? 'small good' : 'small warn');
    }
    $('scope-strategy-adopt').disabled = busy || !fresh || !strategyReady || !plan || !orderedPlanSteps(plan.proposal?.steps || []).valid || scopeStrategies[0]?.candidate_id === plan.id;
    set('scope-strategy-guard',!plan ? 'Kandidaten laden und eine Version bewusst auswählen.' : !fresh ? 'Quellenstand veraltet oder ungeprüft. Umfang und Kandidaten erneut laden.' : !strategyReady ? 'Übernommene Strategie und Kandidaten erneut gemeinsam laden.' : scopeStrategies[0]?.candidate_id === plan.id ? 'Dieser Kandidat ist bereits als Strategie übernommen.' : 'Übernahme speichert eine neue Strategieversion. Produktgates und separate Schrittauswahl bleiben bestehen.', !plan || (fresh && strategyReady) ? 'small muted' : 'small warn');
    $('scope-plans-load').disabled = busy || !intakeScope;
    $('scope-plan-candidate').disabled = busy; $('scope-plan-mode').disabled = busy;
    document.querySelectorAll('[data-plan-step]').forEach(input => { input.disabled = busy; });
    const selectionIssue = planSelectionIssue(plan,ids,mode);
    set('scope-plan-selection-guard',selectionIssue || 'Alle ausgewählten Voraussetzungen stehen vor den abhängigen Schritten. Der Dienst prüft die Auswahl erneut.',selectionIssue ? 'small warn' : 'small muted');
    $('scope-plan-selection-form').querySelector('[type=submit]').disabled = busy || !fresh || !plan || !orderedPlanSteps(plan.proposal?.steps || []).valid || Boolean(selectionIssue);
    document.querySelectorAll('[data-pilot-patch]').forEach(button => { button.disabled = busy || pilotBusy() || !plan || !pilotSourceCurrent(plansScope?.id,plan.scope_hash); });
    renderWorkflowGuide();
  }
  function pilotAllowed(projectId) { const project = state?.registry?.projects?.find(p => p.id === projectId); return Boolean(project && !project.archived && !project.group_id && project.model_egress && state?.execution_capabilities?.pilot_project_ids?.includes(projectId)); }
  function pilotReceiptProject(job) {
    const source = (state.jobs || []).find(item => item.id === (job.result?.apply_proposal?.stage_job_id || job.request?.stage_job_id));
    return job.request?.scope_id || source?.request?.scope_id;
  }
  function pilotReceiptFresh(projectId, hash) {
    if (!pilotAllowed(projectId) || !hash) return false;
    const latest = state.registry?.observations?.find(item => item.kind === 'project' && item.id === projectId);
    return !latest || (!latest.stale && !latest.error && (!latest.scope_hash || latest.scope_hash === hash));
  }
  function renderPilotReceipt(article, job) {
    const result = job.result || {}, projectId = pilotReceiptProject(job);
    if(result.repair_binding && result.candidate) {
      const candidate=result.candidate,binding=result.repair_binding,receipt=node('section','pilot-receipt');
      receipt.append(node('h3',null,'Reparaturplan zur bewussten Auswahl'),
        node('p','small',`Fehlerauftrag: ${binding.source_job_id} · Ursprünglicher Plan: ${binding.candidate_id} · Neuer Kandidat: ${candidate.id}`),
        node('p',null,'Zuerst den aktuellen Kandidaten prüfen und seine Schritte ausdrücklich auswählen. Danach Änderungsvorschlag und isolierten Test starten. Übernahme, Quellenübergang und Folgeabschlüsse bleiben separate Bestätigungen.'));
      const open=node('button','button secondary','Reparaturplan zur Auswahl öffnen');
      open.addEventListener('click',async()=>{
        open.disabled=true;
        try {
          activateTab('registry');await runScope('intake',candidate.scope_kind,candidate.scope_id);
          if(intakeScope?.kind!==candidate.scope_kind || intakeScope?.id!==candidate.scope_id)throw Error('Projektumfang konnte nicht geladen werden.');
          await loadScopePlans();
          if(!scopePlans.some(p=>p.id===candidate.id))throw Error('Historischer Kandidat nicht in der aktuellen Liste. Kandidaten im Projekt prüfen.');
          $('scope-plan-candidate').value=candidate.id;renderPlanDetail();$('scope-plan-detail').scrollIntoView({block:'nearest'});
        } catch(error) { notify(error.message,true); }
        finally { open.disabled=false; }
      });
      receipt.append(open);article.append(receipt);
    }
    if (job.action === 'plan_test' && result.test_evidence) {
      const value=result.test_evidence.test, receipt=node('section','pilot-receipt');
      receipt.append(node('h3',null,'Beleg des Testschritts'),
        node('p',null,result.success && result.completion_receipt ? 'Test bestanden und gebundener Abschlussbeleg gespeichert.' : 'Kein erfolgreicher Abschlussbeleg.'),
        node('p','small',`Tests: ${value.count} · Fehler: ${value.errors} · Fehlschläge: ${value.failures} · Ausgelassen: ${value.skipped}`),
        node('p','small muted','Historischer Testlauf. Aktuelle Anerkennung im Vorgängerkettenbericht prüfen. Keine Produktfreigabe oder automatische Fortsetzung.'));
      if(['completed','failed'].includes(job.status) && result.success===false) {
        const check=node('button','button secondary','Testfehler auf Aktualität prüfen');check.disabled=pilotBusy();
        check.addEventListener('click',()=>runTestFailure(job.id,check));receipt.append(check);
      }
      article.append(receipt);
    }
    if(result.test_failure) {
      const value=result.test_failure,receipt=node('section','pilot-receipt');
      receipt.append(node('h3',null,'Gebundene Testfehlerdiagnose'),node('p','small',`Historische Prüfung: ${value.checked_at} · Quellauftrag: ${value.source_job_id}`),
        node('p',null,value.evidence_usable?'Testfehler am geprüften Stand belegt. Ursache muss fachlich geprüft werden.':`Als Reparaturgrundlage gesperrt: ${value.reason}`));
      const next=node('ul','readable-list');for(const action of value.next_steps || [])next.append(node('li',null,action));receipt.append(next);
      if(job.status==='completed' && value.evidence_usable) {
        const note=node('textarea');note.maxLength=2000;note.setAttribute('aria-label',`Begründung der Reparaturplanung ${job.id}`);
        const plan=node('button','button secondary','Reparaturplan mit Modellen erstellen');plan.disabled=true;
        note.addEventListener('input',()=>{plan.disabled=pilotBusy() || !note.value.trim();});
        plan.addEventListener('click',()=>runRepairPlan(job.id,note.value,plan));
        receipt.append(node('p','small warn','Sendet den aktuellen freigegebenen Projektkontext, gebundene Dateiquellen, Fehlerauszug und deine Begründung über das konfigurierte Terra-Routing und den ausgewählten Supervisor. Nur Planung innerhalb der geprüften Dateien; höchstens zwei Versuche. Ein neuer geprüfter Kandidat ersetzt die bisherige Planrevision und benötigt eine eigene Auswahl. Keine Codeänderung oder automatische Ausführung.'),note,plan);
      }
      if(value.output_excerpt) receipt.append(node('pre','readable-text',value.output_excerpt));
      receipt.append(node('p','small muted',`Auszug ${value.output_truncated?'gekürzt':'ungekürzt'} aus der gespeicherten Ausgabe; diese kann bereits begrenzt sein. Ausgabe-SHA-256: ${value.output_sha256}. Keine Reparaturfreigabe oder automatische Fortsetzung.`));
      const check=node('button','button secondary','Testfehler erneut prüfen');check.disabled=pilotBusy();
      check.addEventListener('click',()=>runTestFailure(value.source_job_id,check));receipt.append(check);article.append(receipt);
    }
    if (job.action === 'stage_test' && !['queued','running'].includes(job.status)) {
      const check = node('button','button secondary','Nachweis prüfen'); check.disabled = pilotBusy();
      check.addEventListener('click',() => runPilotTransfer('assess',{verified_test_job_id:job.id},check));
      article.append(check);
    }
    if (result.post_apply_verification) {
      const value = result.post_apply_verification, receipt = node('section','pilot-receipt');
      receipt.append(node('h3',null,'Nachprüfung der Übernahme'),node('p','small',`Prüfzeitpunkt: ${value.checked_at}`),
        node('p',null,value.evidence_usable ? 'Dateiabgleich und gebundene Nachweise zum Prüfzeitpunkt bestätigt.' : 'Nachweis gesperrt oder unvollständig.'));
      const items = node('ul','readable-list');
      for (const check of value.checks || []) items.append(node('li',null,`${check.label}: ${{passed:'Bestätigt',blocked:'Gesperrt',not_checked:'Nicht geprüft'}[check.status] || 'Unbekannt'}${check.reason ? ' · '+check.reason : ''}`));
      receipt.append(items,node('p','small',value.observed_scope_hash ? (value.context_matches_plan ? 'Planungskontext zum Prüfzeitpunkt unverändert.' : 'Planungskontext verändert: gesonderte Bewertung erforderlich.') : 'Aktueller Planungskontext nicht nachgewiesen.'),
        node('p','small muted','Historischer Dateiabgleich mit früherem Staging-Test. Kein neuer Funktionstest im Ziel, keine Schritt-Abnahme und keine automatische Fortsetzung.'));
      if (value.observed_scope_hash) receipt.append(node('code','evidence-hash',`Planstand: ${value.plan_scope_hash || 'unbekannt'}\nNachher-Stand: ${value.observed_scope_hash}`));
      const closure = value.technical_completion;
      const transitioned=(state.jobs || []).some(item=>item.status==='completed' && item.result?.change_chain?.transition?.technical_receipt_id===closure?.receipt?.id);
      if (!transitioned && job.status === 'completed' && value.evidence_usable === true && closure?.status === 'current' && value.observed_scope_hash !== value.plan_scope_hash) {
        const reason=node('textarea'); reason.maxLength=2000; reason.setAttribute('aria-label','Begründung zum Quellenübergang');
        reason.value=transitionNotes.get(closure.receipt.id) || '';
        const transition=node('button','button secondary','Diesen Quellenübergang für die Kette bestätigen'); transition.disabled=pilotBusy() || !reason.value.trim();
        reason.addEventListener('input',() => { transitionNotes.set(closure.receipt.id,reason.value);transition.disabled=pilotBusy() || !reason.value.trim(); });
        transition.addEventListener('click',() => runChangeChainTransition(value,closure.receipt,reason.value,transition));
        receipt.append(node('p','small warn','Bestätigt die bestehende Planauswahl für den angezeigten neuen Quellenstand und belegt den übernommenen Änderungsschritt. Aufnahme am aktuellen Stand muss bereits bestätigt sein. Alte Folgebelege bleiben ungültig; neue Tests und Reviews sind erforderlich. Weitere Änderungen starten nicht automatisch.'),reason,transition);
      }
      if (closure?.receipt) receipt.append(node('p','small',`Abschlussbeleg ${closure.receipt.id}: ${closure.status === 'current' ? 'zum Prüfzeitpunkt passend' : 'veraltet'}.`));
      if (job.status === 'completed' && value.evidence_usable === true && closure?.status !== 'current') {
        const note = node('textarea'); note.maxLength = 2000; note.setAttribute('aria-label',`Begründung zum Übernahmeabschluss ${job.id}`);
        const confirm = node('button','button secondary','Diesen Nachher-Stand als Übernahmeabschluss bestätigen');
        const already = (state.jobs || []).some(item => item.result?.technical_completion?.verified_job_id === job.id);
        confirm.disabled = true;
        note.addEventListener('input',() => { confirm.disabled = pilotBusy() || already || !note.value.trim(); });
        confirm.addEventListener('click',() => runPilotTransfer('complete',{verified_job_id:job.id,observed_scope_hash:value.observed_scope_hash,note:note.value},confirm));
        receipt.append(node('p','small muted','Bestätigt ausschließlich diese übernommene Änderung am angezeigten Nachher-Stand. Plan, Aufnahme und Folgefreigaben werden nicht erneuert. Vor Speicherung wird erneut geprüft. Begründung erforderlich.'),note,confirm);
      }
      const check = node('button','button secondary','Übernahme erneut nachprüfen'); check.disabled = pilotBusy();
      check.addEventListener('click',() => runPilotTransfer('verify',{transaction_id:value.transaction_id},check));
      receipt.append(check); article.append(receipt);
    }
    if (result.technical_completion) {
      const value=result.technical_completion, receipt=node('section','pilot-receipt');
      receipt.append(node('h3',null,'Gebundener Übernahmeabschluss'),node('p','small',`Beleg ${value.id} · ${value.created_at}`),
        node('p','readable-text',value.note),node('code','evidence-hash',`Nachher-Stand: ${value.binding?.observed_scope_hash || 'unbekannt'}`),
        node('p','small muted','Historischer Betreiberbeleg. Aktuelle Gültigkeit erneut prüfen. Keine neue Ziel-Testausführung, Planannahme oder Folgefreigabe.'));
      const check=node('button','button secondary','Abschlussbeleg erneut prüfen'); check.disabled=pilotBusy();
      check.addEventListener('click',() => runPilotTransfer('verify',{transaction_id:value.transaction_id},check));
      receipt.append(check); article.append(receipt);
    }
    if (result.change_chain) {
      const t=result.change_chain.transition;
      const section=node('section','pilot-receipt');
      section.append(node('h3',null,'Bestätigter Quellenübergang'),node('p','readable-text',t.note),
        node('code','evidence-hash',`Vorher: ${t.from_scope_hash}\nNachher: ${t.to_scope_hash}`),
        node('p','small muted','Historischer Beleg. Vorgängerketten erneut prüfen, bevor Folgeabschlüsse bewertet werden. Keine automatische Ausführung.'));
      article.append(section);
    }
    if (result.pilot_assessment) {
      const value = result.pilot_assessment, receipt = node('section','pilot-receipt');
      receipt.append(node('h3',null,'Pilot-Nachweisprüfung'),node('p','small',`Prüfzeitpunkt: ${value.checked_at}`),
        node('p',null,value.evidence_usable ? 'Voraussetzungen zum Prüfzeitpunkt erfüllt.' : 'Nachweis derzeit gesperrt.'));
      const items = node('ul','readable-list');
      for (const check of value.checks || []) items.append(node('li',null,`${check.label}: ${{passed:'Bestätigt',blocked:'Gesperrt',not_checked:'Nicht geprüft'}[check.status] || 'Unbekannt'}${check.reason ? ' · '+check.reason : ''}`));
      receipt.append(items,node('p','small muted','Historischer Prüfbeleg, keine Freigabe und keine laufende Überwachung. Vor einer Übernahme wird erneut geprüft.'));
      article.append(receipt);
    }
    if (job.action === 'stage_test' && job.status === 'completed' && result.verified === true && result.success === true && pilotAllowed(projectId)) {
      const prepare = node('button','button secondary','Rückübernahme vorbereiten'); prepare.type = 'button'; prepare.dataset.pilotPrepare = job.id;
      prepare.disabled = pilotBusy() || result.stale === true || !pilotReceiptFresh(projectId,result.scope_hash);
      prepare.addEventListener('click',() => runPilotTransfer('prepare',{verified_test_job_id:job.id},prepare));
      article.append(node('p','small muted','Eine Vorbereitung erstellt den konkreten Dateivergleich für deine Freigabe. Sie übernimmt noch keine Änderungen.'),prepare);
    }
    const proposal = result.apply_proposal;
    if (proposal) {
      const receipt = node('section','pilot-receipt'); receipt.append(node('h3',null,'Rückübernahme zur ausdrücklichen Freigabe'));
      receipt.append(node('p','small warn','Der folgende Klick übernimmt genau diese Änderungen in das angezeigte Pilotprojekt. Danach ist eine neue Prüfung erforderlich; weitere Schritte starten nicht automatisch.'));
      receipt.append(node('strong','small','Zielordner des Pilotprojekts'),node('p','readable-text',proposal.manifest?.original_root || 'Nicht angegeben'));
      receipt.append(node('p','small',`Verifizierter Testauftrag: ${proposal.verified_test_job_id} · Vorschlagsauftrag: ${proposal.stage_job_id}`));
      const files = node('ul','readable-list');
      for (const file of proposal.manifest?.files || []) {
        const item = node('li'); item.append(node('strong',null,file.path),node('code','evidence-hash',`Vorher: ${file.original_sha256 || 'Datei neu'}\nNachher: ${file.staged_sha256 || 'Nicht angegeben'}`)); files.append(item);
      }
      receipt.append(node('h3',null,'Dateien und exakte Änderungen'),files,node('pre','pilot-diff',proposal.diff || 'Kein Dateivergleich vorhanden.'));
      receipt.append(node('code','evidence-hash',`Freigabevorschlag: ${proposal.id}\nVorschlagshash: ${proposal.proposal_hash}\nUmfangshash: ${proposal.scope_hash}\nManifesthash: ${proposal.manifest_hash}`));
      const used = (state.jobs || []).some(item => item.result?.pilot_transaction?.proposal_id === proposal.id);
      const apply = node('button','button primary','Diese Änderungen im Pilotprojekt übernehmen'); apply.type = 'button'; apply.dataset.pilotApply = proposal.id;
      apply.disabled = pilotBusy() || used || job.status !== 'completed' || result.success !== true || result.stale === true || !proposal.id || !proposal.proposal_hash || !proposal.diff || !proposal.manifest?.files?.length || !pilotReceiptFresh(projectId,proposal.scope_hash);
      apply.addEventListener('click',() => runPilotTransfer('apply',{proposal_id:proposal.id,proposal_hash:proposal.proposal_hash},apply));
      receipt.append(apply,node('p','small muted',used ? 'Zu diesem Vorschlag liegt bereits ein Übernahmebeleg im Auftragsjournal vor.' : 'Der Dienst prüft Quellen, Testnachweis und Vorschlagshash vor dem Schreiben erneut. Bei Drift wird die Übernahme abgewiesen.'));
      article.append(receipt);
    }
    const transaction = (state.pilot_transactions || []).find(tx => tx.id === result.pilot_transaction?.id) || result.pilot_transaction;
    if (transaction) {
      const receipt = node('section','pilot-receipt'); receipt.append(node('h3',null,'Beleg der Pilotänderung'));
      const allReceipts = (state.jobs || []).map(item => item.result?.pilot_transaction).filter(item => item?.id === transaction.id);
      const rolledBack = transaction.status === 'rolled_back' || allReceipts.some(item => item.status === 'rolled_back');
      receipt.append(node('p','small',`Transaktion ${transaction.id} · ${rolledBack ? 'Zurückgenommen' : transaction.status === 'completed' || transaction.status === 'applied' ? 'Übernommen' : transaction.status}`),node('p','readable-text',transaction.original_root || transaction.root || 'Zielordner im technischen Beleg'));
      const files = node('ul','readable-list');
      for (const file of transaction.files || []) { const item = node('li'); item.append(node('strong',null,file.path),node('code','evidence-hash',`Vorher: ${file.before || 'Datei nicht vorhanden'}\nNachher: ${file.after || 'Datei nicht vorhanden'}`)); files.append(item); }
      receipt.append(files,node('p','small warn','Dieser Beleg ersetzt keine neue Projektprüfung. Es gibt keine automatische Fortsetzung oder allgemeine Produktabnahme.'));
      if (transaction.status === 'completed' && !rolledBack) {
        const check = node('button','button secondary','Übernahme nachprüfen'); check.disabled = pilotBusy();
        check.addEventListener('click',() => runPilotTransfer('verify',{transaction_id:transaction.id},check));
        receipt.append(check);
      }
      if (!['completed','applied','rolled_back'].includes(transaction.status)) receipt.append(node('p','bad','Unvollständiger oder fehlgeschlagener Schreibvorgang. Der tatsächliche Dateistand benötigt Prüfung; keine automatische Wiederholung. Laufende oder hart unterbrochene Vorgänge müssen gesondert untersucht werden.'));
      if (['completed','applied','interrupted','recovery_needed','conflict'].includes(transaction.status)) {
        const rollback = node('button','button danger','Eigene Pilotänderungen zurücknehmen'); rollback.type = 'button'; rollback.dataset.pilotRollback = transaction.id;
        rollback.disabled = pilotBusy() || rolledBack;
        rollback.addEventListener('click',() => runPilotTransfer('rollback',{transaction_id:transaction.id},rollback));
        receipt.append(node('p','small muted','Die Rücknahme betrifft ausschließlich die in diesem Beleg aufgeführten eigenen Änderungen. Zwischenzeitliche Änderungen führen zum Konflikt statt zum Überschreiben.'),rollback);
      }
      article.append(receipt);
    }
  }
  async function runRepairPlan(jobId,note,button) {
    if(button.disabled || pilotBusy())return;
    pending.add('pilot:action');renderJobs();registryControls();
    try { await api('/api/plans/repair',{diagnosis_job_id:jobId,note});activateTab('jobs');await loadState(); }
    catch(error) { notify(error.message,true); }
    finally { pending.delete('pilot:action');renderJobs();registryControls(); }
  }
  async function runTestFailure(jobId,button) {
    if(button.disabled || pilotBusy())return;
    pending.add('pilot:action');renderJobs();registryControls();
    try { await api('/api/plans/test-failure',{job_id:jobId});activateTab('jobs');await loadState(); }
    catch(error) { notify(error.message,true); }
    finally { pending.delete('pilot:action');renderJobs();registryControls(); }
  }
  async function runChangeChainTransition(value,receipt,note,button) {
    if(button.disabled || pilotBusy())return;
    pending.add('pilot:action');renderJobs();registryControls();
    try {
      const current=await api('/api/change-chains/state',{candidate_id:value.candidate_id});
      const chain=current.chains[0];
      const payload={technical_receipt_id:receipt.id,observed_scope_hash:value.observed_scope_hash,selection_id:value.selection_id,note};
      if(chain)await api('/api/change-chains/confirm',{...payload,chain_id:chain.chain.id,expected_head:chain.head_id});
      else await api('/api/pilot/transition',payload);
      notify(chain?'Quellenübergang im Änderungsjournal bestätigt. Keine automatische Fortsetzung.':'Bestätigung des Quellenübergangs beauftragt.');
      activateTab('jobs');await loadState();
    } catch(error) {notify(`Quellenübergang nicht bestätigt: ${error.message}`,true);}
    finally {pending.delete('pilot:action');renderJobs();registryControls();}
  }
  async function runPilotTransfer(action, payload, button) {
    if (button.disabled || pilotBusy()) return;
    pending.add('pilot:action'); renderJobs(); registryControls();
    try {
      const response = await api(`/api/pilot/${action}`,payload);
      const description = {complete:'Bestätigung des Übernahmeabschlusses',verify:'Nachprüfung der Übernahme',assess:'Nachweisprüfung',prepare:'Vorbereitung der Rückübernahme',apply:'Ausdrücklich freigegebene Pilotübernahme',rollback:'Rücknahme eigener Pilotänderungen'}[action];
      notify(`${description}: Auftrag ${response.job?.id || ''} angenommen. Der endgültige Beleg erscheint im Auftragsjournal.`);
      activateTab('jobs'); await loadState();
    } catch (error) { notify(`Pilotaktion nicht angenommen: ${error.message} Der angezeigte Beleg bleibt erhalten.`,true); }
    finally { pending.delete('pilot:action'); renderJobs(); registryControls(); }
  }
  function pilotBusy() { return pending.has('pilot:action') || (state?.test_chains || []).some(s=>['testing','checking'].includes(s.status)) || (state?.sequences || []).some(s=>['testing','assessing'].includes(s.status)) || (state?.jobs || []).some(job => ['queued','running'].includes(job.status)); }

  function renderTestChains(){
    let box=$('test-chain-history');
    if(!box){box=node('section','jobs');box.id='test-chain-history';$('jobs').before(box);}
    box.replaceChildren();box.hidden=!(state.test_chains || []).length;
    if(!box.hidden)box.append(node('h3',null,'Genehmigte Testketten'),node('p','small','Letzte 40 Ketten. Testergebnisse sind keine Produkt- oder Deploymentfreigabe.'));
    const names={testing:'Test läuft',checking:'Abschlussbeleg wird geprüft',completed:'Testkette abgeschlossen',blocked:'Gesperrt',failed:'Fehlgeschlagen',cancelled:'Abgebrochen',interrupted:'Unterbrochen'};
    for(const s of state.test_chains || []){
      const row=node('article','job');row.append(node('strong',null,names[s.status] || s.status),node('p','small',`${stamp(s.created_at)} · ${s.id}`));
      for(const child of s.children || [])row.append(node('p','small',`${child.ordinal+1}. ${child.step_id} · Auftrag ${child.job_id}`));
      if(['testing','checking'].includes(s.status)){
        const cancel=node('button','button danger','Testkette abbrechen');cancel.disabled=s.cancel_requested;
        cancel.addEventListener('click',async()=>{cancel.disabled=true;try{await api('/api/test-chains/cancel',{chain_id:s.id});await loadState();}catch(e){notify(e.message,true);cancel.disabled=false;}});row.append(cancel);
      }
      const details=node('details');details.append(node('summary',null,'Bindung und Ereignisse'),node('pre',null,format(s)));row.append(details);box.append(row);
    }
  }

  function showChangeChainPreview(plan,dependencyReport){
    const dialog=node('dialog','sequence-dialog');dialog.setAttribute('aria-label','Abhängige Änderungen vorschauen');
    dialog.append(node('h2',null,'Zwei abhängige Änderungen prüfen'),node('p',null,'A → B: Ausgangsstand und Übergänge ausdrücklich bestätigen. Jeder Schritt benötigt eigene Tests, Review und Übernahme. Öffnen und Aktualisieren starten keine Ausführung.'));
    const choices=node('div'),output=node('div'),history=node('section','pilot-receipt'),successorOutput=node('div');
    const baselineNote=node('textarea');baselineNote.maxLength=2000;baselineNote.setAttribute('aria-label','Begründung zum Ausgangsstand H0');
    const successorNote=node('textarea');successorNote.maxLength=2000;successorNote.setAttribute('aria-label','Begründung zur H1-Bestätigung');
    const preview=node('button','button secondary','Änderungsfolge prüfen'),begin=node('button','button secondary','Ausgangsstand H0 ausdrücklich festhalten');
    const reload=node('button','button secondary','Kettenhistorie aktualisieren'),successor=node('button','button secondary','H1 für B frisch prüfen');
    const acknowledge=node('button','button secondary','Diesen H1-Stand ausdrücklich bestätigen'),propose=node('button','button','B mit Modellen im Arbeitsbereich vorschlagen');
    const close=node('button','button secondary','Schließen');
    let busy=false,loaded=false,revision=0,report=null,snapshot=null,consents=[],h1=null,consent=null,submitted=false;
    const ids=()=>[...choices.querySelectorAll('input:checked')].map(i=>i.value);
    const refresh=()=>{
      preview.disabled=busy || !loaded || Boolean(snapshot) || ids().length!==2;
      begin.disabled=busy || !loaded || Boolean(snapshot) || !report?.eligible || !baselineNote.value.trim() || pilotBusy();
      reload.disabled=busy;successor.disabled=busy || !loaded || !snapshot || snapshot.requires_new_plan || snapshot.transition_count!==1;
      acknowledge.disabled=busy || !h1?.eligible || !successorNote.value.trim() || Boolean(consent) || pilotBusy();
      propose.disabled=busy || !h1?.eligible || !consent || submitted || pilotBusy();
      choices.querySelectorAll('input').forEach(input=>input.disabled=busy || Boolean(snapshot));
    };
    const renderHistory=()=>{
      history.replaceChildren(node('h3',null,'Gespeicherte Kettenhistorie'));
      if(!snapshot){history.append(node('p','small','Noch kein Ausgangsstand für diesen Kandidaten gespeichert.'));return;}
      history.append(node('p','small',`Kette ${snapshot.chain.id} · A: ${snapshot.chain.binding.step_ids[0]} · B: ${snapshot.chain.binding.step_ids[1]}`),node('p','readable-text',snapshot.chain.note),node('code','evidence-hash',`H0: ${snapshot.chain.binding.scope_hash}`));
      let transitionIndex=0;
      for(const event of snapshot.events || []){
        if(event.kind==='transition')history.append(node('code','evidence-hash',`H${++transitionIndex}: ${event.evidence.technical_receipt.binding.observed_scope_hash}`));
        history.append(node('p','small',`${event.kind==='rollback'?'Rücknahme':'Quellenübergang'} · ${event.id} · ${event.note}`));
      }
      history.append(node('code','evidence-hash',`Gespeicherte Spitze: ${snapshot.scope_hash}\nJournalhash: ${snapshot.head_hash}`),node('p','small muted','Historische Kontinuität ist kein aktueller Datei- oder Funktionstest. H1 vor B separat prüfen.'));
      const active=snapshot.active_transition_ids || [],latest=(snapshot.events || []).find(event=>event.id===active[active.length-1]);
      history.append(node('p','small warn',latest?`Nur das jüngste aktive Glied zuerst zurücknehmen: Transaktion ${latest.evidence.transaction.id}. B vor A; Rücknahme separat beim Transaktionsbeleg. Keine Kaskade.`:'Keine bestätigte aktive Kantenübernahme. Offene Transaktionen im Auftragsjournal prüfen.'));
      if(snapshot.requires_new_plan)history.append(node('p','small warn','Rücknahme protokolliert: Neue Planrevision erforderlich. Alte Freigaben werden nicht reaktiviert.'));
      for(const item of consents)history.append(node('p','small',`Historische H1-Bestätigung ${item.id}: ${item.note}`));
    };
    const loadHistory=async()=>{
      loaded=false;report=null;h1=null;consent=null;output.replaceChildren();successorOutput.replaceChildren();
      const value=await api('/api/change-chains/state',{candidate_id:plan.id});
      if(!dialog.isConnected)return;
      snapshot=value.chains[0] || null;consents=value.consents || [];loaded=true;renderHistory();
    };
    const run=async(action,mutating=false)=>{
      if(busy || (mutating && pilotBusy()))return;busy=true;if(mutating)pending.add('pilot:action');refresh();
      try{await action();}catch(error){report=null;h1=null;consent=null;notify(error.message,true);}
      finally{busy=false;if(mutating)pending.delete('pilot:action');refresh();}
    };
    const steps=dependencyReport?.steps || (plan.proposal?.steps || []).map(step=>({...step,selected:true}));
    for(const step of steps.filter(s=>s.selected && s.action==='change')){
      const label=node('label'),input=node('input');input.type='checkbox';input.value=step.id;
      input.addEventListener('change',()=>{revision++;report=null;output.replaceChildren();refresh();});
      label.append(input,document.createTextNode(step.title));choices.append(label);
    }
    preview.addEventListener('click',()=>{
      if(preview.disabled)return;const observed=revision;
      run(async()=>{
        const value=await api('/api/change-chains/preview',{candidate_id:plan.id,step_ids:ids()});
        if(observed!==revision || !dialog.isConnected)return;
        report=value;
        output.replaceChildren(node('p',value.eligible?'small':'small warn',value.reason));
        const ordered=node('ol');for(const step of value.steps || [])ordered.append(node('li',null,`${step.title} · ${step.readiness==='conditional'?'Bedingt – benötigt Abschluss: '+step.waiting_for.join(', '):'Voraussetzungen beobachtet; keine Ausführungsfreigabe'}`));output.append(ordered);
        if(value.binding)output.append(node('code','evidence-hash',`H0: ${value.binding.scope_hash}\nVorschaubindung: ${value.binding_hash}`));
        output.append(node('p','small warn','Momentaufnahme. Ausgangsstand separat festhalten; dies startet keine Änderung.'));
      });
    });
    baselineNote.addEventListener('input',refresh);successorNote.addEventListener('input',refresh);
    begin.addEventListener('click',()=>{if(!begin.disabled)run(async()=>{
      await api('/api/change-chains/begin',{candidate_id:plan.id,step_ids:report.binding.step_ids,binding_hash:report.binding_hash,note:baselineNote.value});
      await loadHistory();notify('Ausgangsstand gespeichert. A separat vorschlagen, prüfen und übernehmen.');
    },true);});
    reload.addEventListener('click',()=>run(loadHistory));
    successor.addEventListener('click',()=>{if(!successor.disabled)run(async()=>{
      h1=null;consent=null;
      const value=await api('/api/change-chains/successor-preview',{chain_id:snapshot.chain.id});
      if(!dialog.isConnected)return;h1=value;
      successorOutput.replaceChildren(node('p',value.eligible?'small':'small warn',value.reason));
      if(value.binding)successorOutput.append(node('code','evidence-hash',`H0: ${value.binding.original_scope_hash}\nH1: ${value.binding.effective_scope_hash}\nVorgänger: ${value.binding.predecessor_event_id}\nSchritt B: ${value.binding.step_id}\nVorschaubindung: ${value.binding_hash}`));
      consent=value.eligible?consents.find(item=>item.binding_hash===value.binding_hash) || null:null;
    });});
    acknowledge.addEventListener('click',()=>{if(!acknowledge.disabled)run(async()=>{
      const value=await api('/api/change-chains/acknowledge',{chain_id:snapshot.chain.id,binding_hash:h1.binding_hash,note:successorNote.value});
      consent=value.consent;consents=[consent];renderHistory();notify('H1 ausdrücklich bestätigt. B wurde noch nicht vorgeschlagen.');
    },true);});
    propose.addEventListener('click',()=>{if(!propose.disabled)run(async()=>{
      const value=await api('/api/change-chains/propose',{consent_id:consent.id});submitted=true;
      notify(`B-Vorschlagsauftrag ${value.job.id} angenommen. Eigene Tests, Review und Übernahme bleiben erforderlich.`);
      dialog.close();activateTab('jobs');await loadState();
    },true);});
    close.addEventListener('click',()=>dialog.close());dialog.addEventListener('close',()=>dialog.remove(),{once:true});
    dialog.append(history,reload,choices,preview,output,baselineNote,begin,node('h3',null,'Separater Nachfolger B'),successor,successorOutput,successorNote,acknowledge,
      node('p','small warn','Der separate B-Vorschlag sendet den freigegebenen Projektkontext, gebundene Dateiquellen und die Begründung über das konfigurierte Terra-Routing und den ausgewählten Supervisor. Modellaufrufe können Kosten verursachen. Nur isolierter Arbeitsbereich; keine Übernahme. B benötigt eigene neue Tests und Reviews.'),propose,close);
    document.body.append(dialog);dialog.showModal();run(loadHistory);
  }

  function showTestChain(plan,dependencyReport){
    const dialog=node('dialog','sequence-dialog');dialog.setAttribute('aria-label','Genehmigte Testkette');
    dialog.append(node('h2',null,'Testkette vorbereiten'),node('p',null,'Zwei bis fünf Tests auswählen. Ausführung nacheinander auf isolierten Kopien mit dem festen Python-Testadapter. Kein Modellaufruf, keine Änderung am Original und keine Produktfreigabe.'));
    const choices=node('div'),output=node('div'),note=node('textarea');note.maxLength=2000;note.setAttribute('aria-label','Begründung der Testkette');
    const preview=node('button','button secondary','Reihenfolge und Belege prüfen'),start=node('button','button','Testkette ausdrücklich starten'),close=node('button','button secondary','Schließen');
    let report=null,busy=false,revision=0;
    const ids=()=>[...choices.querySelectorAll('input:checked')].map(i=>i.value);
    const refresh=()=>{preview.disabled=busy || ids().length<2 || ids().length>5;start.disabled=busy || !report?.eligible || !note.value.trim() || pilotBusy();};
    for(const step of dependencyReport.steps.filter(s=>s.selected && s.action==='test' && s.completion_status!=='accepted')){
      const label=node('label'),input=node('input');input.type='checkbox';input.value=step.id;
      input.addEventListener('change',()=>{revision++;report=null;output.replaceChildren();refresh();});label.append(input,document.createTextNode(step.title));choices.append(label);
    }
    preview.addEventListener('click',async()=>{
      if(preview.disabled)return;busy=true;const observed=revision;refresh();
      try{const value=await api('/api/test-chains/preview',{candidate_id:plan.id,step_ids:ids()});
        if(observed!==revision || !dialog.isConnected)return;report=value;output.replaceChildren(node('p',null,value.reason));
        const ordered=node('ol');for(const step of value.steps || [])ordered.append(node('li',null,`${step.title} · ${step.readiness==='conditional'?'Bedingt – benötigt erfolgreiche Vorgänger: '+step.waiting_for.join(', '):'Vorgänger aktuell belegt'}`));output.append(ordered);
      }catch(e){report=null;notify(e.message,true);}finally{busy=false;refresh();}
    });
    note.addEventListener('input',refresh);
    start.addEventListener('click',async()=>{
      if(start.disabled || busy || pilotBusy())return;busy=true;pending.add('pilot:action');refresh();
      try{await api('/api/test-chains/start',{candidate_id:plan.id,step_ids:report.binding.step_ids,binding_hash:report.binding_hash,note:note.value});dialog.close();activateTab('jobs');await loadState();}
      catch(e){report=null;notify(e.message,true);}finally{busy=false;pending.delete('pilot:action');refresh();}
    });
    close.addEventListener('click',()=>dialog.close());dialog.addEventListener('close',()=>dialog.remove(),{once:true});
    dialog.append(choices,preview,output,note,start,close);document.body.append(dialog);dialog.showModal();refresh();
  }

  function renderSequences() {
    let box=$('sequence-history');
    if(!box){box=node('section','jobs');box.id='sequence-history';$('jobs').before(box);}
    box.replaceChildren();box.hidden=!(state.sequences || []).length;
    const names={testing:'Test und Supervisorprüfung',assessing:'Nachweise werden geprüft',awaiting_transfer_decision:'Beendet – separate Übernahmeentscheidung erforderlich',blocked:'Gesperrt',failed:'Fehlgeschlagen',cancelled:'Abgebrochen',interrupted:'Unterbrochen'};
    if(!box.hidden)box.append(node('h3',null,'Gebundene Prüffolgen'),node('p','small muted','Letzte 40 Folgen. Historische Nachweise; keine Übernahme- oder Planabschlussfreigabe.'));
    for(const s of state.sequences || []){
      const row=node('article','job');row.append(node('strong',null,names[s.status] || s.status),node('p','small',`${stamp(s.created_at)} · ${s.id}`));
      for(const child of s.children || [])row.append(node('p','small',`${child.ordinal===0?'Test + Supervisor':'Nachweisprüfung'}: ${child.job_id}`));
      if(['testing','assessing'].includes(s.status)){
        const cancel=node('button','button danger','Prüffolge abbrechen');cancel.disabled=s.cancel_requested;
        if(s.cancel_requested)row.append(node('p','small warn','Abbruch angefordert; der laufende Schritt gibt den Platz nach seinem Ende frei.'));
        cancel.addEventListener('click',async()=>{cancel.disabled=true;try{await api('/api/sequences/cancel',{sequence_id:s.id});await loadState();}catch(e){notify(e.message,true);cancel.disabled=false;}});row.append(cancel);
      }
      const details=node('details');details.append(node('summary',null,'Bindung und Ereignisse'),node('pre',null,format(s)));row.append(details);box.append(row);
    }
  }

  async function previewSequence(id,button) {
    button.disabled=true;
    try {
      const report=await api('/api/sequences/preview',{stage_job_id:id});
      const dialog=node('dialog','sequence-dialog');dialog.setAttribute('aria-label','Gebundene Prüffolge');
      dialog.append(node('h2',null,'Prüffolge bestätigen'),node('p',null,'1. Isolierter Test mit Supervisorprüfung. 2. Lokale Nachweisprüfung. Halt vor jeder Übernahme; kein automatischer Planabschluss.'),
        node('p','warn',`Der Nachreview sendet freigegebenen Projektkontext, versiegelte Dateiinhalte und Testergebnis über das konfigurierte Routing an ${report.binding?.routing?.supervisor || 'den Supervisor'} auf ${report.binding?.routing?.reasoning || 'medium'}. Dabei können Kosten entstehen.`),node('p',null,report.reason));
      const note=node('textarea');note.maxLength=2000;note.setAttribute('aria-label','Begründung der Prüffolge');note.required=true;
      const start=node('button','button','Prüffolge ausdrücklich starten');start.disabled=true;
      const close=node('button','button secondary','Schließen');close.addEventListener('click',()=>dialog.close());
      let busy=false;
      note.addEventListener('input',()=>{start.disabled=busy || report.eligible!==true || !note.value.trim() || pilotBusy();});
      start.addEventListener('click',async()=>{
        if(busy || !note.value.trim() || report.eligible!==true || pilotBusy())return;
        busy=true;start.disabled=true;pending.add('pilot:action');
        try{await api('/api/sequences/start',{stage_job_id:id,binding_hash:report.binding_hash,note:note.value});dialog.close();notify('Gebundene Prüffolge gestartet. Halt vor jeder Übernahme.');await loadState();}
        catch(e){notify(e.message,true);dialog.close();}
        finally{pending.delete('pilot:action');}
      });
      dialog.append(note,start,close);dialog.addEventListener('close',()=>dialog.remove(),{once:true});document.body.append(dialog);dialog.showModal();
    }catch(e){notify(e.message,true);}finally{button.disabled=pilotBusy();}
  }
  function pilotSourceCurrent(projectId, hash) {
    if (!pilotAllowed(projectId) || !hash || intakeScope?.kind !== 'project' || intakeScope?.id !== projectId || intakeScope.result.scope_hash !== hash) return false;
    const latest = state?.registry?.observations?.find(item => item.kind === 'project' && item.id === projectId);
    return !latest || new Date(latest.observed_at).valueOf() < intakeScope.readAt || (!latest.stale && !latest.error && (!latest.scope_hash || latest.scope_hash === hash));
  }
  async function runPilotAction(action, payload, projectId, hash) {
    if (pilotBusy() || !pilotSourceCurrent(projectId,hash)) return;
    pending.add('pilot:action'); registryControls(); renderJobs();
    try {
      await api('/api/actions',{action,...payload,supervisor:$('supervisor').value});
      notify(action === 'scope_patch' ? 'Pilot-Änderungsvorschlag beauftragt. Produktdateien bleiben unverändert.' : 'Begrenzter Pilottest mit Supervisor beauftragt. Keine Rückübernahme.'); activateTab('jobs'); await loadState();
    } catch (error) { notify(`Pilotauftrag nicht gestartet: ${error.message}`,true); }
    finally { pending.delete('pilot:action'); registryControls(); renderJobs(); }
  }
  async function loadScopePlans() {
    if (!intakeScope || pending.has('plans:load')) return;
    const scope = intakeScope, {kind,id} = scope; pending.add('plans:load'); planControls();
    set('scope-plan-feedback','Kandidaten und übernommene Strategie werden geladen …');
    try {
      const query = `?kind=${encodeURIComponent(kind)}&id=${encodeURIComponent(id)}`;
      const results = await Promise.allSettled([api(`/api/plans${query}`),api(`/api/strategies${query}`)]);
      if (intakeScope !== scope) return;
      const [plans,strategies] = results;
      scopePlans = plans.status === 'fulfilled' ? plans.value.plans || [] : []; plansScope = plans.status === 'fulfilled' ? {kind,id} : null;
      strategiesScope = strategies.status === 'fulfilled' && strategies.value.scope_hash === scope.result.scope_hash ? scope : null;
      if (strategies.status === 'fulfilled') scopeStrategies = strategies.value.revisions || [];
      renderPlanOptions(); renderStrategies();
      const errors = results.filter(item => item.status === 'rejected').map(item => item.reason.message);
      set('scope-plan-feedback',errors.length ? `Laden unvollständig: ${errors.join(' · ')}` : `${scopePlans.length} Kandidaten und ${scopeStrategies.length} Strategieversionen geladen.`);
    }
    catch (error) { if (intakeScope === scope) { strategiesScope = null; set('scope-plan-feedback',`Kandidaten nicht geladen: ${error.message}`); } }
    finally { pending.delete('plans:load'); planControls(); }
  }
  function scopeSourceCurrent(hash) {
    if (!hash || !intakeScope || hash !== intakeScope.result.scope_hash) return false;
    const latest = state?.registry?.observations?.find(item => item.kind === intakeScope.kind && item.id === intakeScope.id);
    return !latest || new Date(latest.observed_at).valueOf() < intakeScope.readAt || (!latest.stale && !latest.error && (!latest.scope_hash || latest.scope_hash === hash));
  }
  function renderStrategies() {
    const latest = scopeStrategies[0], box = $('scope-strategy-current');
    box.replaceChildren();
    if (!latest) box.append(node('p','small muted',strategiesScope ? 'Noch keine Strategie ausdrücklich übernommen.' : 'Übernommene Strategie noch nicht geladen.'));
    else {
      const fresh = strategiesScope === intakeScope && latest.current === true && scopeSourceCurrent(latest.scope_hash);
      box.append(node('h3',null,`Version ${latest.version} · ${latest.proposal?.summary || 'Übernommene Strategie'}`),node('p',fresh ? 'small good' : 'small warn',fresh ? 'Aktuell zum geprüften Quellenstand · keine Ausführungsfreigabe.' : 'Historische Strategie · Aktualität nicht bestätigt. Umfang und Strategien erneut laden.'),node('code','evidence-hash',`Quellenstand: ${latest.scope_hash}`),node('code','evidence-hash',`Revision: ${latest.id} · Kandidat: ${latest.candidate_id}`));
      box.querySelector('p').id = 'scope-strategy-status';
      const detail = node('details'); detail.append(node('summary',null,'Übernommene Schritte und Review'),readable({...latest.proposal,steps:orderedPlanSteps(latest.proposal?.steps || []).steps}),readable(latest.review || {})); box.append(detail);
    }
    $('scope-strategy-history').replaceChildren(...(scopeStrategies.length ? scopeStrategies.map(revision => {
      const detail = node('details'); detail.append(node('summary',null,`Version ${revision.version} · ${stamp(revision.created_at)} · ${revision.proposal?.summary || revision.id}`),node('code','evidence-hash',`Revision: ${revision.id} · Quellenstand: ${revision.scope_hash}`),readable(revision.proposal || {}),readable(revision.review || {})); return detail;
    }) : [node('p','small muted','Keine Strategieversionen geladen.')]));
  }
  async function adoptStrategy() {
    planControls(); if ($('scope-strategy-adopt').disabled) return;
    const scope = intakeScope, plan = selectedPlan();
    const payload = {scope_kind:scope.kind,scope_id:scope.id,candidate_id:plan.id,scope_hash:plan.scope_hash,expected_previous_id:scopeStrategies[0]?.id || null};
    pending.add('strategies:adopt'); planControls(); set('scope-strategy-feedback','Strategie wird übernommen …');
    try {
      const result = await api('/api/strategies/adopt',payload);
      if (intakeScope !== scope) return;
      scopeStrategies = [result.revision,...scopeStrategies.filter(item => item.id !== result.revision.id)];
      renderPlanOptions(); renderStrategies();
      set('scope-strategy-feedback','Strategie ausdrücklich übernommen. Keine Ausführung gestartet. Schrittauswahl wurde zurückgesetzt.');
      await loadScopePlans();
    } catch (error) { if (intakeScope === scope) { strategiesScope = null; renderPlanOptions(); renderStrategies(); set('scope-strategy-feedback',`Übernahme nicht bestätigt: ${error.message}. Umfang und Kandidaten erneut laden.`); } }
    finally { pending.delete('strategies:adopt'); planControls(); }
  }
  async function loadIntakeDraft() {
    const scope = intakeScope, projectId = $('scope-intake-project').value;
    if (!scope || !projectId || pending.has('intake:draft') || pending.has('scope:write')) return;
    pending.add('intake:draft'); intakeControls(); set('scope-intake-feedback','Lokaler Aufnahmeentwurf wird geladen …');
    try {
      const result = await api(`/api/intake/drafts?kind=${encodeURIComponent(scope.kind)}&id=${encodeURIComponent(scope.id)}`);
      if (intakeScope !== scope || $('scope-intake-project').value !== projectId) return;
      const draft = (result.drafts || []).find(item => item.project_id === projectId), box = $('scope-intake-draft');
      box.replaceChildren();
      if (!draft) { set('scope-intake-feedback','Kein gespeicherter Aufnahmeentwurf für dieses Projekt. Eingaben bleiben erhalten.'); return; }
      box.append(node('p','small muted',`Lokaler Entwurf · ${stamp(draft.created_at)} · noch nicht bestätigt`),node('code','evidence-hash',`Quellenhash: ${draft.source_hash}`),node('code','evidence-hash',`Umfangshash: ${draft.scope_hash}`));
      const sources = node('ul','source-list'); for (const source of draft.sources || []) sources.append(node('li','evidence-hash',`${source.name} · SHA-256 ${source.sha256}`)); box.append(sources);
      if (draft.current !== true || result.scope_hash !== scope.result.scope_hash || !scopeSourceCurrent(result.scope_hash)) { box.append(node('p','small warn','Entwurf veraltet. Umfang erneut prüfen; die Eingaben wurden nicht ersetzt.')); set('scope-intake-feedback','Veralteten Entwurf nicht geladen.'); return; }
      for (const field of ['requirements','test_strategy','dependencies','open_evidence']) $(`scope-intake-${field.replaceAll('_','-')}`).value = draft.fields?.[field] || '';
      loadedIntakeDraft = {...draft,loaded_scope_hash:result.scope_hash}; set('scope-intake-feedback','Entwurf geladen. Vier Felder prüfen und gegebenenfalls bearbeiten; Aufnahme separat ausdrücklich bestätigen.');
    } catch (error) { if (intakeScope === scope && $('scope-intake-project').value === projectId) set('scope-intake-feedback',`Entwurf nicht geladen: ${error.message}`); }
    finally { pending.delete('intake:draft'); intakeControls(); }
  }
  async function approvePlanSelection() {
    planControls(); if ($('scope-plan-selection-form').querySelector('[type=submit]').disabled) return;
    const plan = selectedPlan(); if (!plan || !plansScope || pending.has('plans:approve')) return;
    const payload = {scope_kind:plansScope.kind,scope_id:plansScope.id,candidate_id:plan.id,scope_hash:plan.scope_hash,selected_step_ids:[...$('scope-plan-detail').querySelectorAll('[data-plan-step]:checked')].map(input => input.value),mode:$('scope-plan-mode').value};
    const scope = intakeScope;
    pending.add('plans:approve'); planControls();
    try { await api('/api/plans/approve',payload); if (intakeScope !== scope) return; set('scope-plan-feedback','Planauswahl unveränderlich protokolliert. Keine Produktausführung gestartet.'); document.querySelectorAll('[data-plan-step]').forEach(input => { input.checked = false; }); $('scope-plan-mode').value = ''; }
    catch (error) { if (intakeScope === scope) set('scope-plan-feedback',`Auswahl nicht bestätigt: ${error.message}`); }
    finally { pending.delete('plans:approve'); planControls(); }
  }
  function intakeControls() {
    for (const type of ['intake','vault']) {
      const form = $(`scope-${type}-form`), busy = pending.has('scope:write') || pending.has('intake:draft');
      for (const control of form.elements) control.disabled = busy || !intakeScope;
      const entry = intakeScope?.result.intake?.find(item => item.project_id === $('scope-intake-project').value);
      form.querySelector('[type=submit]').disabled = busy || !intakeScope || (type === 'intake' && (!entry?.memories_present || !entry?.evidence_complete || !scopeSourceCurrent(intakeScope.result.scope_hash) || (loadedIntakeDraft && !scopeSourceCurrent(loadedIntakeDraft.loaded_scope_hash)) || ['requirements','test-strategy','dependencies','open-evidence'].some(field => !$(`scope-intake-${field}`).value.trim())));
    }
    $('scope-intake-draft-load').disabled = !intakeScope || !$('scope-intake-project').value || pending.has('scope:write') || pending.has('intake:draft');
    if (loadedIntakeDraft && !scopeSourceCurrent(loadedIntakeDraft.loaded_scope_hash)) set('scope-intake-feedback','Der geladene Entwurf ist inzwischen veraltet. Umfang prüfen und den aktuellen Entwurf bewusst laden. Deine Eingaben bleiben erhalten.');
    renderWorkflowGuide();
  }
  async function saveScopeRecord(type, form) {
    intakeControls();
    if (!intakeScope || pending.has('scope:write') || form.querySelector('[type=submit]').disabled) return;
    const scope = intakeScope;
    const {kind,id,result} = intakeScope;
    const payload = {scope_kind:kind,scope_id:id};
    if (type === 'intake') { payload.scope_hash = result.scope_hash; payload.project_id = $('scope-intake-project').value; payload.fields = Object.fromEntries(['requirements','test_strategy','dependencies','open_evidence'].map(field => [field,$(`scope-intake-${field.replaceAll('_','-')}`).value.trim()])); }
    else { payload.path = $('scope-vault-path').value.trim(); payload.model_egress = $('scope-vault-egress').checked; }
    pending.add('scope:write'); registryControls(); set(`scope-${type}-feedback`,'Wird gespeichert …');
    try {
      await api(type === 'intake' ? '/api/intake' : '/api/vault/sources',payload);
      if (intakeScope !== scope) return;
      if (type === 'intake') { intakeDrafts.delete(intakeDraftKey(scope,payload.project_id)); intakeSelections.delete(intakeDraftKey(scope)); intakeProject = ''; loadedIntakeDraft = null; $('scope-intake-draft').replaceChildren(); }
      form.reset(); set(`scope-${type}-feedback`,type === 'intake' ? 'Aufnahme bestätigt. Keine Produktfreigabe.' : 'Vault-Quelle ausdrücklich zugeordnet.');
      await runScope('intake',kind,id);
    } catch (error) { if (intakeScope === scope) set(`scope-${type}-feedback`,`Nicht gespeichert: ${error.message}`); }
    finally { pending.delete('scope:write'); registryControls(); }
  }
  function registryOptions(id, items, placeholder) {
    const select = $(id), signature = JSON.stringify(items.map(item => [item.id,item.name]));
    if (select.dataset.options === signature) return;
    const value = select.value, first = node('option',null,placeholder); first.value = '';
    select.replaceChildren(first,...items.map(item => { const option = node('option',null,item.name); option.value = item.id; return option; }));
    select.value = items.some(item => item.id === value) ? value : ''; select.dataset.options = signature;
  }
  function registryControls() {
    for (const kind of ['project','group','membership','policy']) {
      const form = $(`registry-${kind}-form`), busy = pending.has(`registry:${kind}`);
      for (const control of form.elements) control.disabled = busy;
      form.querySelector('[type=submit]').disabled = busy || !state?.registry || (kind === 'membership' && (!$('registry-member-project').value || !$('registry-member-group').value || !$('registry-member-role').value)) || (kind === 'policy' && !$('registry-policy-project').value);
    }
    document.querySelectorAll('[data-registry-archive]').forEach(button => { button.disabled = pending.has(`registry:archive:${button.dataset.registryArchive}`); });
    document.querySelectorAll('[data-registry-memory]').forEach(button => { button.disabled = pending.has(`registry:memory:${button.dataset.registryMemory}`); });
    document.querySelectorAll('[data-stage-test]').forEach(button => { const source = state?.jobs?.find(job => job.id === button.dataset.stageTest); button.disabled = pilotBusy() || !source || source.result?.stale === true || !pilotSourceCurrent(source.request?.scope_id,source.result?.scope_hash); });
    document.querySelectorAll('[data-scope-action]').forEach(button => { const {scopeAction:action,scopeKind:kind,scopeId:id} = button.dataset; button.disabled = pending.has('scope:write') || scopeBlocked(action,kind,id) || pending.has(`scope:${action}:${kind}:${id}`) || (action !== 'intake' && (state?.jobs || []).some(job => ['queued','running'].includes(job.status))); });
    intakeControls();
    planControls();
  }
  function registryProject(project) {
    const article = node('article','registry-project'); const heading = node('div','step-heading');
    heading.append(node('h3',null,project.name),node('span','chip',project.archived ? 'Archiviert' : project.group_id ? registryRoles[project.role] || project.role || 'Rolle fehlt' : 'Einzelprojekt'));
    article.append(heading,node('p','evidence-hash',project.path || 'Kein Pfad erfasst'));
    if (project.group_id) article.append(node('p','small muted',`Dauerhafte Rolle: ${registryRoles[project.role] || project.role || 'nicht erfasst'} (${project.role || 'offen'})`));
    article.append(node('p','small muted',project.configured ? 'Bestehende Konfiguration · zusätzliche Aufnahme im gewählten Umfang möglich.' : 'Registriert · laufende lokale Beobachtung bei aktiviertem Monitor; beratender Review per Klick.'),node('p','small muted',`Modellversand: ${project.model_egress ? 'explizit erlaubt' : 'nicht erlaubt'}`));
    article.append(node('p','small warn',project.memory_provisioning === 'provisioned_incomplete' ? 'Strategiegedächtnis zugeordnet · inhaltliche Aufnahme noch unvollständig.' : project.memory_provisioning === 'pending' || !project.memory_provisioning ? 'Strategiegedächtnis noch nicht zugeordnet · bei unklarer Zuordnung prüfen und erneut versuchen.' : `Gedächtnisbereitstellung: ${format(project.memory_provisioning)}`));
    if (project.group_id && !project.archived) { const button = node('button','button quiet','Strategiegedächtnis zuordnen'); button.type = 'button'; button.dataset.registryMemory = project.id; button.addEventListener('click',() => registryMutation(`memory:${project.id}`,'/api/registry/memory',{project_id:project.id},null,'Strategiegedächtnis zugeordnet. Die inhaltliche Aufnahme bleibt gesondert zu prüfen.')); article.append(button); }
    if (project.requirements) { const details = node('details'); details.append(node('summary',null,'Ziel & Anforderungen'),node('p','readable-text',project.requirements)); article.append(details); }
    if (!project.archived) {
      const actions = node('details','registry-archive'); actions.append(node('summary',null,'Registereintrag archivieren'));
      actions.append(node('p','small muted','Archiviert nur diesen Registereintrag. Ordner und bestehende Beobachtungskonfiguration bleiben bestehen; Gruppe und Rolle bleiben gebunden.'));
      const button = node('button','button quiet','Eintrag jetzt archivieren'); button.type = 'button'; button.dataset.registryArchive = project.id;
      button.addEventListener('click',() => registryMutation(`archive:${project.id}`,'/api/registry/archive',{project_id:project.id},null,'Registereintrag archiviert.'));
      actions.append(button); article.append(actions);
    }
    return article;
  }
  function renderRegistry() {
    const registry = state.registry, projects = registry?.projects || [], groups = registry?.groups || [];
    set('registry-summary',registry ? `${groups.filter(g => !g.archived).length} Gruppen · ${projects.filter(p => !p.archived).length} aktive Projekte` : 'Register noch nicht verfügbar');
    renderRegistryDirectory();
    renderFocusedScope();
    // Keep form drafts and expanded entries intact through unchanged SSE snapshots.
    const signature = JSON.stringify([projects,groups]), list = $('registry-groups');
    if (list.dataset.registry !== signature) {
      const sections = groups.map(group => {
        const section = node('section','registry-group'); const heading = node('div','section-heading');
        const title = node('div'); title.append(node('span','eyebrow','PROJEKTGRUPPE'),node('h3',null,group.name)); heading.append(title);
        const members = projects.filter(p => p.group_id === group.id);
        heading.append(node('span','count',group.archived ? 'Archiviert' : `${members.filter(p => !p.archived).length} aktiv`));
        section.append(heading,...(members.length ? members.map(registryProject) : [node('p','empty','Noch keine Mitglieder. Ordne ein Einzelprojekt mit seiner Rolle dauerhaft zu.')])); return section;
      });
      list.replaceChildren(...(sections.length ? sections : [node('p','empty',registry ? 'Noch keine Gruppen. Projekte können eigenständig bleiben oder dauerhaft einer Gruppe zugeordnet werden.' : 'Der lokale Dienst stellt noch kein Projektregister bereit.')]));
      const singles = projects.filter(p => !p.group_id);
      $('registry-singles').replaceChildren(...(singles.length ? singles.map(registryProject) : [node('p','empty','Keine Einzelprojekte registriert.')]));
      list.dataset.registry = signature;
    }
    registryOptions('registry-member-project',projects.filter(p => !p.group_id && !p.archived),'Einzelprojekt auswählen …');
    registryOptions('registry-member-group',groups.filter(g => !g.archived),'Gruppe auswählen …');
    registryOptions('registry-policy-project',projects.filter(p => !p.archived),'Projekt auswählen …');
    renderRegistryObservations();
    registryControls();
  }
  function renderRegistryObservations() {
    set('registry-monitor-note',state.monitor?.enabled ? 'Lokale Umfangsbeobachtung aktiv · ein Umfang pro Zyklus, reihum. Modellreviews neuer Gruppen starten ausschließlich per Klick.' : 'Lokale Umfangsbeobachtung pausiert · globale Beobachtungseinstellung. „Aufnahme prüfen“ bleibt als manueller Abruf verfügbar.');
    const observations = state.registry?.observations || [];
    document.querySelectorAll('[data-observation-kind]').forEach(box => {
      const kind = box.dataset.observationKind, id = box.dataset.observationId;
      const observation = observations.find(item => item.kind === kind && item.id === id);
      const archived = scopeMembers(kind,id).some(project => project.archived) || (kind === 'group' && state.registry?.groups?.find(group => group.id === id)?.archived);
      if (!observation) { box.replaceChildren(node('p','small muted',archived ? 'Archivierter Umfang · keine aktive Umfangsbeobachtung.' : 'Noch keine lokale Umfangsbeobachtung erfasst.')); return; }
      const nodes = [node('p','small muted',`Letzte Beobachtung: ${stamp(observation.observed_at)} · ${age(observation.observed_at)}`)];
      if (observation.error) nodes.push(node('p','small warn',`Beobachtung gestört: ${format(observation.error)}`));
      if (observation.last_success_at) nodes.push(node('p','small muted',`Letzter erfolgreicher Abruf: ${stamp(observation.last_success_at)}`));
      if (observation.stale) nodes.push(node('p','small warn','Gespeicherter Umfangsstand veraltet · erneut prüfen.'));
      nodes.push(node('p',observation.plan_ready && !observation.error && !observation.stale ? 'small good' : 'small muted',observation.plan_ready && !observation.error && !observation.stale ? 'Aufnahmevoraussetzungen für einen Planentwurf erfüllt · keine Planfreigabe.' : 'Aufnahmevoraussetzungen für einen Planentwurf noch nicht aktuell belegt.'));
      box.replaceChildren(...nodes);
    });
  }
  async function registryMutation(kind, path, payload, form, message) {
    const key = `registry:${kind}`; if (pending.has(key) || !state?.registry) return;
    pending.add(key); registryControls(); const feedback = $(`registry-${kind}-feedback`);
    if (feedback) feedback.textContent = 'Wird gespeichert …';
    try {
      const result = await api(path,payload); if (form) form.reset();
      const outcome = result.memory_warning ? `${message} ${result.memory_warning} Zuordnung prüfen und anschließend erneut versuchen.` : message;
      if (feedback) feedback.textContent = outcome;
      notify(outcome,Boolean(result.memory_warning)); await loadState();
    } catch (error) {
      const message = `Registeränderung nicht gespeichert: ${error.message}`;
      if (feedback) feedback.textContent = message;
      notify(message,true);
    } finally { pending.delete(key); registryControls(); }
  }
  function activateTab(name) {
    currentTab = name; document.querySelectorAll('[data-tab]').forEach(b => { const active = b.dataset.tab === name; b.setAttribute('aria-selected',String(active)); b.tabIndex = active ? 0 : -1; $(`panel-${b.dataset.tab}`).hidden = !active; });
    document.querySelectorAll('[data-nav]').forEach(b => b.classList.toggle('active',b.dataset.nav === (name === 'events' ? 'overview' : name)));
  }
  function resetMemory() { memoryRequest++; memory = null; dirty = false; memoryBusy = false; $('memory-editor').value = ''; $('memory-editor').disabled = true; $('memory-save').disabled = true; $('memory-reload').disabled = true; $('memory-diff').hidden = true; set('memory-status','Keine Datei geöffnet'); set('memory-feedback','Speichern prüft den Quellenhash und erstellt eine Sicherungskopie.'); }
  function renderMemoryOptions() {
    const select = $('memory-file'), files = activeProject()?.memories || []; const desired = memory?.project === selected ? memory.name : '';
    const signature = JSON.stringify([selected,files.map(m => m.name)]);
    if (select.dataset.options !== signature) { select.replaceChildren(node('option',null,files.length ? 'Datei auswählen …' : 'Keine Gedächtnisdateien vorhanden')); select.firstChild.value = ''; files.forEach(m => { const o = node('option',null,m.name); o.value = m.name; select.append(o); }); select.dataset.options = signature; }
    select.value = desired; select.disabled = memoryBusy || !files.length;
  }
  async function openMemory(name, force = false) {
    if (!name || (!force && memory?.name === name && memory?.project === selected)) return Boolean(memory);
    if (!abandonDraft()) { renderMemoryOptions(); return false; }
    const request = ++memoryRequest, project = selected; memoryBusy = true; $('memory-file').disabled = true; $('memory-save').disabled = true; $('memory-reload').disabled = true; $('memory-editor').disabled = true; set('memory-status','Datei wird geladen …');
    try { const result = await api(`/api/memory?project=${encodeURIComponent(project)}&name=${encodeURIComponent(name)}`); if (request !== memoryRequest || selected !== project) return false; memory = {...result,project,name}; dirty = false; $('memory-editor').value = result.content; $('memory-editor').disabled = false; $('memory-diff').hidden = true; set('memory-status',`Gelesen · SHA-256 ${String(result.sha256).slice(0,12)}…`); set('memory-feedback','Original geladen. Speichern erzeugt eine Sicherungskopie.'); return true; }
    catch (error) { if (request === memoryRequest) { notify(`Datei konnte nicht geladen werden: ${error.message}`,true); set('memory-status',memory ? 'Bisheriger Entwurf bleibt geöffnet' : 'Lesefehler'); $('memory-editor').disabled = !memory; } return false; }
    finally { if (request === memoryRequest) { memoryBusy = false; $('memory-reload').disabled = !memory; $('memory-save').disabled = !dirty; renderMemoryOptions(); } }
  }
  async function saveMemory() {
    if (!memory || !dirty || memoryBusy) return; memoryBusy = true; const current = memory; const content = $('memory-editor').value; $('memory-save').disabled = true; $('memory-editor').disabled = true; $('memory-file').disabled = true; $('memory-reload').disabled = true;
    try { const result = await api('/api/memory',{project:current.project,name:current.name,content,expected_sha256:current.sha256}); memory = {...current,content,sha256:result.sha256}; dirty = false; $('memory-diff').hidden = true; set('memory-status',`Gespeichert · SHA-256 ${String(result.sha256).slice(0,12)}…`); set('memory-feedback',`Gespeichert und geprüft. Sicherung: ${result.backup || 'Siehe Auditprotokoll'}`); notify('Gedächtnis gespeichert. Sicherungskopie angelegt.'); await loadState(); }
    catch (error) { const text = error.status === 409 ? 'Konflikt: Die Datei wurde außerhalb dieses Editors verändert. Dein Entwurf bleibt erhalten. Sichere deinen Text und lade den aktuellen Stand neu; es wurde nichts überschrieben.' : `Speichern fehlgeschlagen: ${error.message}`; set('memory-feedback',text); notify(text,true); }
    finally { memoryBusy = false; $('memory-editor').disabled = false; $('memory-save').disabled = !dirty; $('memory-reload').disabled = false; renderMemoryOptions(); }
  }
  function renderPlanned() {
    const container = $('module-dependencies'); const selectedDeps = new Set([...container.querySelectorAll('input:checked')].map(i => i.value));
    const planned = state.planned_projects || []; const all = [...state.projects,...planned.filter(p => !state.projects.some(x => x.id === p.id))];
    const signature = JSON.stringify(all.map(p => [p.id,p.name]));
    if (container.dataset.options !== signature) { container.replaceChildren(...all.map(p => { const label = node('label'); const input = node('input'); input.type = 'checkbox'; input.value = p.id; input.checked = selectedDeps.has(p.id); label.append(input,document.createTextNode(p.name)); return label; })); container.dataset.options = signature; }
    $('planned-list').replaceChildren(...(planned.length ? planned.map(p => { const item = node('article','planned-item'); item.append(node('h3',null,p.name),node('p','muted',p.description || 'Keine Beschreibung'),node('span','chip','Geplant · Implementierung gesperrt'),node('p','small muted',p.depends_on?.length ? `Abhängigkeiten: ${p.depends_on.map(projectName).join(', ')}` : 'Keine Abhängigkeiten angegeben')); return item; }) : [node('p','empty','Noch keine Module vorgemerkt. Neue Vorhaben erscheinen hier mit ihren Abhängigkeiten.')]));
  }
  $('registry-project-form').addEventListener('submit',event => { event.preventDefault(); registryMutation('project','/api/registry/projects',{name:$('registry-project-name').value.trim(),path:$('registry-project-path').value.trim(),requirements:$('registry-project-requirements').value.trim(),model_egress:$('registry-project-egress').checked},event.currentTarget,'Projekt registriert. Die lokale Aufnahme kann jetzt per Klick geprüft werden.'); });
  for (const type of ['intake','vault']) $('scope-'+type+'-form').addEventListener('submit',event => { event.preventDefault(); saveScopeRecord(type,event.currentTarget); });
  $('scope-plans-load').addEventListener('click',loadScopePlans);
  $('scope-strategy-adopt').addEventListener('click',adoptStrategy);
  $('scope-intake-draft-load').addEventListener('click',loadIntakeDraft);
  $('scope-plan-candidate').addEventListener('change',renderPlanDetail);
  $('scope-plan-mode').addEventListener('change',planControls);
  $('scope-plan-selection-form').addEventListener('submit',event => { event.preventDefault(); approvePlanSelection(); });
  $('scope-intake-project').addEventListener('change',changeIntakeProject);
  $('scope-intake-form').addEventListener('input',intakeControls);
  $('registry-policy-project').addEventListener('change',() => { const project = state?.registry?.projects?.find(p => p.id === $('registry-policy-project').value); $('registry-policy-requirements').value = project?.requirements || ''; $('registry-policy-egress').checked = Boolean(project?.model_egress); set('registry-policy-feedback',''); registryControls(); });
  $('registry-policy-form').addEventListener('submit',event => { event.preventDefault(); registryMutation('policy','/api/registry/policy',{project_id:$('registry-policy-project').value,requirements:$('registry-policy-requirements').value.trim(),model_egress:$('registry-policy-egress').checked},event.currentTarget,'Anforderungen und Modellfreigabe gespeichert.'); });
  $('registry-group-form').addEventListener('submit',event => { event.preventDefault(); registryMutation('group','/api/registry/groups',{name:$('registry-group-name').value.trim()},event.currentTarget,'Gruppe angelegt.'); });
  $('registry-membership-form').addEventListener('submit',event => { event.preventDefault(); registryMutation('membership','/api/registry/memberships',{project_id:$('registry-member-project').value,group_id:$('registry-member-group').value,role:$('registry-member-role').value},event.currentTarget,'Projekt und Rolle dauerhaft der Gruppe zugeordnet.'); });
  for (const id of ['registry-member-project','registry-member-group','registry-member-role']) $(id).addEventListener('change',registryControls);
  document.querySelectorAll('[data-action]').forEach(button => button.addEventListener('click',() => runAction(button.dataset.action,undefined,button)));
  $('review-all').addEventListener('click',() => runAction('hybrid_review',undefined,$('review-all')));
  $('review-all').title = 'Übermittelt den Quellenkontext aller Projekte an die konfigurierten Modelle. Modellaufrufe können Kosten verursachen.';
  $('supervisor').addEventListener('change',() => saveSettings({supervisor:$('supervisor').value},$('supervisor')));
  $('reasoning-mode').addEventListener('change',() => saveSettings({reasoning_mode:$('reasoning-mode').value},$('reasoning-mode')));
  $('auto-review').addEventListener('change',() => saveSettings({auto_review:$('auto-review').checked},$('auto-review')));
  $('monitor-toggle').addEventListener('click',() => saveSettings({monitor_enabled:!state?.monitor?.enabled},$('monitor-toggle')));
  $('event-filter').addEventListener('change',renderEvents);
  $('decision-step').addEventListener('change',captureDecision);
  $('decision-kind').addEventListener('change',updateDecisionGuard);
  $('decision-reason').addEventListener('input',updateDecisionGuard);
  $('decision-rebase').addEventListener('click',captureDecision);
  $('decision-form').addEventListener('submit',async event => {
    event.preventDefault(); updateDecisionGuard(); if ($('decision-submit').disabled) return;
    const payload = {step_id:$('decision-step').value,kind:$('decision-kind').value,reason:$('decision-reason').value.trim(),evidence_hash:decisionEvidence};
    decisionBusy = true; updateDecisionGuard();
    try { await api('/api/decisions',payload); set('decision-feedback','Entscheidung mit Begründung und Quellenbindung erfasst. Der Governor bewertet die Voraussetzungen erneut.'); $('decision-kind').value = ''; $('decision-reason').value = ''; decisionEvidence = null; set('decision-evidence','Für eine weitere Entscheidung Schritt erneut auswählen'); notify('Betreiberentscheidung protokolliert.'); await loadState(); }
    catch (error) { set('decision-feedback',`Entscheidung nicht gespeichert: ${error.message}`); notify(`Entscheidung nicht gespeichert: ${error.message}`,true); if (error.status === 409) await loadState(); }
    finally { decisionBusy = false; updateDecisionGuard(); }
  });
  document.querySelectorAll('[data-tab]').forEach(button => { button.addEventListener('click',() => activateTab(button.dataset.tab)); button.addEventListener('keydown',e => { const tabs = [...document.querySelectorAll('[data-tab]')]; let idx = tabs.indexOf(button); if (e.key === 'ArrowRight') idx = (idx+1)%tabs.length; else if (e.key === 'ArrowLeft') idx = (idx+tabs.length-1)%tabs.length; else if (e.key === 'Home') idx = 0; else if (e.key === 'End') idx = tabs.length-1; else return; e.preventDefault(); tabs[idx].focus(); activateTab(tabs[idx].dataset.tab); }); });
  $('registry-back-to-directory').addEventListener('click',returnToProjectDirectory);
  $('matrix-scope').addEventListener('change',renderStatusPages);
  document.querySelectorAll('[data-nav]').forEach(button => button.addEventListener('click',() => { const name = button.dataset.nav; if (name === 'overview') { activateTab('events'); $('main').scrollIntoView({behavior:'smooth'}); } else { activateTab(name); $(`panel-${name}`).scrollIntoView({behavior:'smooth',block:'start'}); } }));
  $('memory-file').addEventListener('change',() => { if (!$('memory-file').value) { if (abandonDraft()) resetMemory(); renderMemoryOptions(); } else openMemory($('memory-file').value); });
  $('memory-reload').addEventListener('click',() => memory && openMemory(memory.name,true));
  $('memory-save').addEventListener('click',saveMemory);
  $('memory-editor').addEventListener('input',() => { dirty = Boolean(memory && $('memory-editor').value !== memory.content); $('memory-save').disabled = !dirty || memoryBusy; $('memory-diff').hidden = !dirty; set('memory-status',dirty ? 'Ungespeicherte Änderungen' : 'Unverändert'); if (dirty) { set('memory-original',memory.content); set('memory-draft',$('memory-editor').value); } });
  window.addEventListener('beforeunload',event => { if (dirty || memoryBusy) { event.preventDefault(); event.returnValue = ''; } });
  $('planned-form').addEventListener('submit',async event => { event.preventDefault(); const button = event.currentTarget.querySelector('[type=submit]'); button.disabled = true; try { await api('/api/projects',{name:$('module-name').value.trim(),description:$('module-description').value.trim(),depends_on:[...$('module-dependencies').querySelectorAll('input:checked')].map(i => i.value)}); $('planned-form').reset(); notify('Modul vorgemerkt. Die Implementierung bleibt gesperrt.'); await loadState(); } catch (error) { notify(`Modul nicht angelegt: ${error.message}`,true); } finally { button.disabled = false; } });
  (async () => { const ok = await loadState(); if (ok) connectStream(); pollTimer = setInterval(async () => { if (connectionMode !== 'live' || Date.now()-lastReceived > 30000) { const ready = await loadState(); if (ready && !stream) connectStream(); } if (state) renderObserved(); },5000); })();
})();

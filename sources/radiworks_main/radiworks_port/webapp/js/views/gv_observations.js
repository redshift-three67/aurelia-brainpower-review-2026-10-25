/* Additive GV-2 view: explicit activation, immutable broadcast IDs, own history. */
export function pairGvControls(snapshot) {
  const controls = new Map((snapshot.controls || []).map(c => [c.broadcastId, c]));
  const entries = (snapshot.eligible || []).map(e => ({
    ...controls.get(e.broadcastId), ...e, eligible: true, binding: e.observationBinding,
    enabled: Boolean(controls.get(e.broadcastId)?.enabled),
  }));
  const seen = new Set(entries.map(e => e.broadcastId));
  for (const c of controls.values()) if (!seen.has(c.broadcastId)) entries.push({...c, eligible: false});
  return entries;
}
export function trendPresentation(value) {
  const delta = value?.delta;
  if (!Number.isInteger(delta)) return {label: 'Basis', tone: 'neutral', delta: null};
  const strong = Math.abs(delta) >= 200;
  return {label: delta === 0 ? 'Unverändert' : delta > 0 ? (strong ? 'Stark steigend' : 'Steigend') : (strong ? 'Stark sinkend' : 'Sinkend'),
    tone: delta === 0 ? 'neutral' : delta > 0 ? 'up' : 'down', delta};
}
const text = (el, value) => { if (el.textContent !== String(value)) el.textContent = String(value); };
const short = id => String(id || '').slice(0, 8);
function node(tag, content, className) {
  const el = document.createElement(tag); if (content !== undefined) text(el, content);
  if (className) el.className = className; return el;
}
function trendCell(value) {
  const t = trendPresentation(value);
  const arrow = t.delta === null ? '—' : t.delta === 0 ? '=' : t.delta > 0 ? '↑' : '↓';
  const strong = Number.isInteger(t.delta) && Math.abs(t.delta) >= 200;
  const delta = t.delta === null ? '' : ` (${t.delta > 0 ? '+' : ''}${t.delta})`;
  return node('td', `${strong ? arrow + arrow : arrow} ${t.label}${delta}`, `gv-trend trend-${t.tone}`);
}
export function initGvObservationsView(api) {
  const panel = document.getElementById('gv-observations-panel');
  if (!panel) return;
  const section = document.getElementById('view-broadcast');
  const status = document.getElementById('gv-observation-status');
  const error = document.getElementById('gv-observation-poll-error');
  const excluded = document.getElementById('gv-observation-excluded');
  const controls = document.getElementById('gv-observation-controls');
  const selector = document.getElementById('gv-observation-session');
  const statusError = document.getElementById('gv-observation-status-error');
  const historyError = document.getElementById('gv-observation-history-error');
  const summary = document.getElementById('gv-observation-history-summary');
  const body = document.getElementById('gv-observation-history-body');
  const cards = new Map(); const sessions = new Map();
  let timer = null, busy = false, action = false, generation = 0, paused = false;
  const visible = () => !paused && !document.hidden && !section.hidden;
  function renderControls(snapshot) {
    const entries = pairGvControls(snapshot); const wanted = new Set();
    for (const e of entries) {
      wanted.add(e.broadcastId);
      let card = cards.get(e.broadcastId);
      if (!card) {
        const el = node('div', undefined, 'gv-observation-card');
        const title = node('h4'), info = node('p', undefined, 'hint'), state = node('p');
        const button = node('button', undefined, 'btn'); button.type = 'button';
        button.dataset.gvBroadcastId = e.broadcastId;
        el.append(title, info, state, button); controls.append(el);
        card = {el, title, info, state, button, entry: e}; cards.set(e.broadcastId, card);
        button.addEventListener('click', async () => {
          if (action || !card.entry.eligible) return;
          action = true; generation++;
          for (const c of cards.values()) c.button.disabled = true;
          try {
            const next = await api.setGvObservation(e.broadcastId, !card.entry.enabled);
            text(error, ''); renderControls(next);
          } catch (failure) {
            text(error, `Aktivierung/Änderung nicht bestätigt: ${failure.message}. Der letzte Serverstatus bleibt maßgeblich.`);
          } finally {
            action = false;
            for (const c of cards.values()) c.button.disabled = !c.entry.eligible;
            refresh();
          }
        });
      }
      card.entry = e;
      text(card.title, e.signature || `Broadcast ${short(e.broadcastId)}`);
      text(card.info, `Sitzung ${short(e.binding?.sessionId)} · Fall ${short(e.binding?.caseRef)} · Rate ${(e.binding?.rateIndex ?? 0) + 1} · Broadcast ${short(e.broadcastId)}`);
      const remaining = Math.max(0, Number(e.nextInSeconds || 0));
      const countdown = `${Math.floor(remaining / 60)}:${String(remaining % 60).padStart(2, '0')}`;
      text(card.state, e.error || (e.enabled ? `Aktiv · nächste Beobachtung in ${countdown}` : e.eligible ? 'Aus · noch keine automatische Beobachtung' : 'Broadcast beendet/ungeeignet · Historie bleibt erhalten'));
      text(card.button, e.enabled ? 'Beobachtung ausschalten' : 'Beobachtung aktivieren (21 Min.)');
      card.button.setAttribute('aria-label', `${card.button.textContent} · Broadcast ${short(e.broadcastId)} · Rate ${(e.binding?.rateIndex ?? 0) + 1}`);
      card.button.disabled = action || !e.eligible;
    }
    for (const [id, c] of cards) if (!wanted.has(id)) {
      if (c.el.contains(document.activeElement)) panel.querySelector('h2').focus();
      c.el.remove(); cards.delete(id);
    }
    text(status, `${entries.filter(e => e.enabled).length} Beobachtung(en) aktiv · ${snapshot.eligible.length} geeignete aktive Broadcasts. Nach Neustart aus.`);
    text(excluded, `${snapshot.excludedCount} ungebundene aktive Broadcasts (Direkt/Auto) sind für GV-2 nicht geeignet. Ihre bestehende Ausführung bleibt erhalten.`);
    if (!entries.length && !controls.querySelector('.gv-empty')) controls.append(node('p', 'Noch kein geeigneter aktiver Broadcast. Prüfdraft prüfen und freigeben, um einen unveränderlich zugeordneten Auftrag zu erhalten.', 'hint gv-empty'));
    if (entries.length) controls.querySelector('.gv-empty')?.remove();
  }
  function renderHistory(all, history) {
    for (const row of all.sessionIndex || []) sessions.set(row.sessionId, row.caseRef);
    const old = selector.value;
    for (const [id, ref] of sessions) if (![...selector.options].some(o => o.value === id)) {
      const option = node('option', `Sitzung ${short(id)} · Fall ${short(ref)}`); option.value = id; selector.append(option);
    }
    selector.value = old;
    text(summary, `${history.records.length} von ${history.total} Beobachtungen angezeigt${history.truncated ? ' · gekürzt: die jüngsten 200; Sitzung gezielt wählen' : ''}. Erste Zeile je Broadcast: Basis. Maximal 1000 Einträge je Broadcast.`);
    const fragment = document.createDocumentFragment();
    for (const r of history.records) {
      const tr = node('tr');
      const date = new Date(r.observedAt);
      tr.append(node('td', date.toLocaleString('de-DE')), node('td', short(r.binding.sessionId)), node('td', String(r.binding.rateIndex + 1), 'num'), node('td', short(r.broadcastId)),
        node('td', r.caseGv, 'num'), trendCell(r.caseTrend), node('td', r.rateGv, 'num'), trendCell(r.rateTrend));
      fragment.append(tr);
    }
    if (!history.records.length) {
      const tr = node('tr'), td = node('td', 'Noch keine Beobachtung. Nach bewusster Aktivierung entsteht die erste Basis nach 21 Minuten.');
      td.colSpan = 8; tr.append(td); fragment.append(tr);
    }
    body.replaceChildren(fragment);
  }
  async function refresh() {
    if (!visible() || busy || action) return;
    busy = true; const ticket = generation; const selected = selector.value;
    try {
      const current = () => ticket === generation && visible();
      // History failure must never hide active controls or their off switch.
      const statusRequest = api.gvObservations().then(snapshot => {
        if (current()) { renderControls(snapshot); text(statusError, ''); }
      }).catch(failure => {
        if (current()) text(statusError, `Broadcaststatus nicht erreichbar: ${failure.message}. Anzeige kann veraltet sein.`);
      });
      const historyRequest = api.gvObservationHistory(selected || undefined).then(history => {
        if (current()) { renderHistory(history, history); text(historyError, ''); }
      }).catch(failure => {
        if (current()) text(historyError, `Historienabgleich fehlgeschlagen: ${failure.message}. Vorhandene Historie kann veraltet sein; Ausschalten bleibt möglich.`);
      });
      await Promise.all([statusRequest, historyRequest]);
    } finally { busy = false; }
  }
  function updateVisibility() {
    generation++;
    if (timer) { clearInterval(timer); timer = null; }
    if (visible()) { refresh(); timer = setInterval(refresh, 5000); }
  }
  selector.addEventListener('change', () => { generation++; refresh(); });
  new MutationObserver(updateVisibility).observe(section, {attributes: true, attributeFilter: ['hidden']});
  document.addEventListener('visibilitychange', updateVisibility);
  window.addEventListener('pagehide', () => { paused = true; updateVisibility(); });
  window.addEventListener('pageshow', () => { paused = false; updateVisibility(); });
  updateVisibility();
}

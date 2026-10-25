import { caseJobGuard } from "./job-context.js";
/* API-Client + WebSocket-Fachkanal (Umschlag v:1, Reconnect an letzter Event-ID).
   Contract: Modul_Templates/standards/API_CONTRACT.md — apiBase NIE hardcodet. */

function resolveApiBase(apiBase) {
  const target = new URL(apiBase || "/", location.href);
  if (!["http:", "https:"].includes(target.protocol) || target.origin !== location.origin || target.username || target.password) {
    throw new Error("API-Ziel nicht freigegeben. Bitte diese lokale Instanz ohne fremde Verbindungsparameter öffnen.");
  }
  target.search = "";
  target.hash = "";
  target.pathname = target.pathname.replace(/\/$/, "");
  return target;
}

function resolveSocketTarget(value) {
  const page = new URL(window.location.href);
  const target = new URL(value, page);
  if (target.protocol === "http:") target.protocol = "ws:";
  else if (target.protocol === "https:") target.protocol = "wss:";
  const expected = page.protocol === "https:" ? "wss:" : "ws:";
  if (!["http:", "https:"].includes(page.protocol) || target.protocol !== expected
      || target.host !== page.host || target.username || target.password) {
    throw new Error("WebSocket-Ziel nicht freigegeben. Bitte diese lokale Instanz ohne fremde Verbindungsparameter öffnen.");
  }
  target.hash = "";
  return target.toString();
}

export function resolveConfig() {
  const injected = window.__MODULE_CONFIG__ || {};
  const params = new URLSearchParams(location.search);
  const config = {
    apiBase: injected.apiBase || params.get("api") || "",
    wsUrl: injected.wsUrl || params.get("ws") || null,
    theme: injected.theme || params.get("theme") || "radiworks",
    accent: injected.accent || params.get("accent") || "wellenreiter",
    mode: injected.mode || params.get("mode") || null,
  };
  resolveApiBase(config.apiBase);
  if (!config.wsUrl) {
    const apiUrl = resolveApiBase(config.apiBase);
    apiUrl.protocol = apiUrl.protocol === "https:" ? "wss:" : "ws:";
    apiUrl.pathname = `${apiUrl.pathname.replace(/\/$/, "")}/ws`;
    apiUrl.search = "";
    apiUrl.hash = "";
    config.wsUrl = apiUrl.toString();
  }
  config.wsUrl = resolveSocketTarget(config.wsUrl);
  return config;
}

async function jsonOrThrow(response) {
  if (!response.ok) {
    let detail = `${response.status}`;
    try {
      const body = await response.json();
      detail = body.error?.message || body.detail?.message || (typeof body.detail === "string" ? body.detail : JSON.stringify(body));
    } catch (_) { /* Textfehler */ }
    const error = new Error(detail); error.status = response.status; throw error;
  }
  return response.json();
}

async function boundCaseOrThrow(response) {
  const data = await jsonOrThrow(response);
  const ref = response.headers.get("X-RadiWorks-Case-Ref");
  if (data?.name && !ref) throw new Error("Fallbindung fehlt. Bitte Fall erneut laden.");
  return { data, ref };
}

export function createClient(apiBase) {
  const base = resolveApiBase(apiBase).toString().replace(/\/$/, "");
  const url = (path) => base + path;
  const catalogLabels = new Map();
  return {
    catalogLabel: selector => catalogLabels.get(selector) || (String(selector || "").startsWith("catalog-") ? "Katalogreferenz " + String(selector).slice(8,20) : String(selector || "")),
    personalCapability: () => fetch(url('/personal-analyses/capability')).then(jsonOrThrow),
    personalJobs: (ref) => fetch(url('/personal-analyses?case_ref='+encodeURIComponent(ref))).then(jsonOrThrow),
    personalJob: (id, ref) => fetch(url('/personal-analyses/'+encodeURIComponent(id)+'?case_ref='+encodeURIComponent(ref))).then(jsonOrThrow),
    startPersonal: (body) => fetch(url('/personal-analyses'),{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}).then(jsonOrThrow),
    cancelPersonal: (id, ref) => fetch(url('/personal-analyses/'+encodeURIComponent(id)+'/cancel'),{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({expected_case_ref:ref})}).then(jsonOrThrow),
    comparisonCapability: (signal) => fetch(url('/comparisons/capability'), {signal}).then(jsonOrThrow),
    comparisonSources: (ref, signal) => fetch(url('/comparisons/sources?case_ref='+encodeURIComponent(ref)), {signal}).then(jsonOrThrow),
    comparisons: (ref, signal) => fetch(url('/comparisons?case_ref='+encodeURIComponent(ref)), {signal}).then(jsonOrThrow),
    comparison: (id, ref, signal) => fetch(url('/comparisons/'+encodeURIComponent(id)+'?case_ref='+encodeURIComponent(ref)), {signal}).then(jsonOrThrow),
    startComparison: (body, signal) => fetch(url('/comparisons'), {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body),signal}).then(jsonOrThrow),
    cancelComparison: (id, body, signal) => fetch(url('/comparisons/'+encodeURIComponent(id)+'/cancel'), {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body),signal}).then(jsonOrThrow),
    retryComparison: (id, body, signal) => fetch(url('/comparisons/'+encodeURIComponent(id)+'/retry'), {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body),signal}).then(jsonOrThrow),
    gvObservations: () => fetch(url("/gv-observations"), {signal: AbortSignal.timeout(10000)}).then(jsonOrThrow),
    setGvObservation: (id, enabled) => fetch(url(`/gv-observations/${encodeURIComponent(id)}`), {
      method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({enabled}), signal: AbortSignal.timeout(10000),
    }).then(jsonOrThrow),
    gvObservationHistory: (session) => fetch(url("/gv-observations/history" + (session ? "?session_id=" + encodeURIComponent(session) : "")), {signal: AbortSignal.timeout(10000)}).then(jsonOrThrow),
    ping: (signal) => fetch(url("/ping"), { signal }).then(jsonOrThrow),
    manifest: () => fetch(url("/manifest")).then(jsonOrThrow),
    entropyStatus: () => fetch(url("/entropy/status")).then(jsonOrThrow),
    entropyFeed: () => fetch(url("/entropy/feed")).then(jsonOrThrow),
    databaseSuggestions: (body, signal) => fetch(url("/database-suggestions"), {
      method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(body), signal,
    }).then(jsonOrThrow),
    confirmDatabaseSuggestion: (body, signal) => fetch(url("/database-suggestions/confirm"), {
      method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(body), signal,
    }).then(jsonOrThrow),
    databases: () => fetch(url("/catalogs")).then(jsonOrThrow).then(data => {
      if (!Array.isArray(data.catalogs)) throw new Error("Katalogindex fehlt. Bitte den aktuellen Prüfstand verwenden.");
      const ids = new Set();
      for (const entry of data.catalogs) {
        if (!/^catalog-[0-9a-f]{64}$/.test(entry.id) || !/^catalog-[0-9a-f]{64}$/.test(entry.exactId)
            || typeof entry.name !== "string" || typeof entry.label !== "string"
            || ids.has(entry.id) || ids.has(entry.exactId) || entry.id === entry.exactId) {
          throw new Error("Katalogindex ungültig. Bitte Prüfstand neu laden.");
        }
        ids.add(entry.id); ids.add(entry.exactId);
        catalogLabels.set(entry.id,entry.label);
        catalogLabels.set(entry.exactId,entry.label + " (Einzeldatenbank)");
      }
      return {...data, databases: data.catalogs.map(entry => entry.name)};
    }),
    analysis: (body) =>
      fetch(url("/analysis"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      }).then(jsonOrThrow),
    gv: (body) =>
      fetch(url("/gv"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      }).then(jsonOrThrow),
    anomaly: (body) =>
      fetch(url("/search-anomaly"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      }).then(jsonOrThrow),
    gvRoundState: () => fetch(url("/analysis/gv-round")).then(jsonOrThrow),
    gvPageStart: (body) =>
      fetch(url("/analysis/gv-page/start"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      }).then(jsonOrThrow),
    gvRound: (body = {}) =>
      fetch(url("/analysis/gv-round"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      }).then(jsonOrThrow),
    essentialQuestions: (body = {}) =>
      fetch(url("/essential-questions"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      }).then(jsonOrThrow),
    settings: () => fetch(url("/settings")).then(jsonOrThrow),
    updateSettings: (body) =>
      fetch(url("/settings"), {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      }).then(jsonOrThrow),
    stickStatus: () => fetch(url("/stickpad")).then(jsonOrThrow),
    stickPosition: (x, y, mode = "reproducible") =>
      fetch(url("/stickpad/position"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ x, y, mode }),
      }).then(jsonOrThrow),
    stickAnalyze: (database) =>
      fetch(url("/stickpad/analyze"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ database }),
      }).then(jsonOrThrow),
    stickGv: () => fetch(url("/stickpad/gv"), { method: "POST" }).then(jsonOrThrow),
    stickClear: () => fetch(url("/stickpad"), { method: "DELETE" }).then(jsonOrThrow),
    draftTransition: (id, status) =>
      fetch(url(`/drafts/${id}/transition`), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status }),
      }).then(jsonOrThrow),
    stickPadFollowup: (body) =>
      fetch(url("/analysis/stickpad-followup"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      }).then(jsonOrThrow),
    drafts: () => fetch(url("/drafts")).then(jsonOrThrow),
    draft: (id) => fetch(url(`/drafts/${id}`)).then(jsonOrThrow),
    draftPromote: (id, body = {}) =>
      fetch(url(`/drafts/${id}/promote`), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      }).then(jsonOrThrow),
    broadcast: async (body) => {
      const command = {...body, ...caseJobGuard(window.__RADIWORKS_CASE_BINDING__)};
      const post = (path, value) => fetch(url(path), {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(value)}).then(jsonOrThrow);
      const preview = await post("/broadcast/preview", command);
      const policy = preview.executionPolicy;
      if (policy.deltaApplied || policy.dynamicEnabled) {
        const message = `Broadcast-Vorschau: ${policy.requestedSeconds} Sekunden eingegeben; ${policy.seconds} Sekunden Laufzeit. Fall-GV-Bezug: ${policy.referenceGv}. ${policy.dynamicEnabled ? `Begrenzte Anpassungen: höchstens ${policy.maxFollowups} Folgeaufträge, Mindestdauer ${policy.minSeconds} Sekunden.` : 'Keine dynamischen Folgeaufträge.'} Starten?`;
        if (!window.confirm(message)) throw new Error('Broadcast vor dem Start abgebrochen.');
      }
      return post("/broadcast", {...command, expected_preview_digest: preview.previewDigest});
    },
    broadcastAdjustments: () => fetch(url('/broadcast/adjustments')).then(jsonOrThrow),
    watchlistPreview: (body) => fetch(url('/watchlist/preview'), {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}).then(jsonOrThrow),
    watchlistStart: (body) => fetch(url('/watchlist'), {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}).then(jsonOrThrow),
    watchlists: () => fetch(url('/watchlist')).then(jsonOrThrow),
    watchlist: (id) => fetch(url('/watchlist/'+encodeURIComponent(id))).then(jsonOrThrow),
    watchlistCancel: (id, body) => fetch(url('/watchlist/'+encodeURIComponent(id)+'/cancel'), {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}).then(jsonOrThrow),
    queue: () => fetch(url("/broadcast/queue")).then(jsonOrThrow),
    stopCurrent: () => fetch(url("/broadcast/current"), { method: "DELETE" }).then(jsonOrThrow),
    stopAll: () => fetch(url("/broadcast/all"), { method: "DELETE" }).then(jsonOrThrow),
    presentationProfile: (ref, version) => fetch(url('/presentation-profile?case_ref='+encodeURIComponent(ref)+'&context_version='+encodeURIComponent(version)), {signal:AbortSignal.timeout(10000)}).then(jsonOrThrow),
    savePresentationProfile: (body) => fetch(url('/presentation-profile'), {method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify(body),signal:AbortSignal.timeout(15000)}).then(jsonOrThrow),
    presentationImageUrl: (sha) => url('/presentation-images/'+encodeURIComponent(sha)),
    uploadPresentationImage: (body) => fetch(url('/presentation-images'), {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body),signal:AbortSignal.timeout(15000)}).then(jsonOrThrow),
    contextImageUrl: (sha) => url("/context-images/" + encodeURIComponent(sha)),
    uploadContextImage: (body) => fetch(url("/context-images"), {
      method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(body),
    }).then(jsonOrThrow),
    cases: () => fetch(url("/cases")).then(jsonOrThrow),
    loadCase: (name) => fetch(url(`/cases/${encodeURIComponent(name)}`)).then(jsonOrThrow),
    activateCase: (name) => fetch(url(`/cases/${encodeURIComponent(name)}/activate`), { method: "POST" }).then(boundCaseOrThrow),
    activateCaseRef: (ref) => fetch(url(`/cases/ref/${encodeURIComponent(ref)}/activate`), { method: "POST" }).then(boundCaseOrThrow),
    currentCase: () => fetch(url("/cases/current")).then(jsonOrThrow),
    currentCaseWithRef: (signal) => fetch(url("/cases/current"), {signal}).then(boundCaseOrThrow),
    currentCaseRef: () => fetch(url("/cases/current/ref")).then(jsonOrThrow),
    saveCase: (body) =>
      fetch(url("/cases"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      }).then(boundCaseOrThrow),
    saveCurrentCaseMetadata: (body) =>
      fetch(url("/cases/current/metadata"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      }).then(boundCaseOrThrow),
    recentCases: () => fetch(url("/cases/recent")).then(jsonOrThrow),
    sessions: () => fetch(url("/analysis/sessions")).then(jsonOrThrow),
    viewSession: (index) =>
      fetch(url(`/analysis/sessions/${index}/view`), { method: "POST" }).then(jsonOrThrow),
    caseStatistics: (name) =>
      fetch(url(`/cases/${encodeURIComponent(name)}/statistics`)).then(jsonOrThrow),
    caseStatisticsRef: (ref) =>
      fetch(url(`/cases/ref/${encodeURIComponent(ref)}/statistics`)).then(jsonOrThrow),
    imagesAnalyze: (body) =>
      fetch(url("/images/analyze"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      }).then(jsonOrThrow),
    imagesBroadcast: (body) =>
      fetch(url("/images/broadcast"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({...body, ...caseJobGuard(window.__RADIWORKS_CASE_BINDING__)}),
      }).then(jsonOrThrow),
    scripts: () => fetch(url("/scripts")).then(jsonOrThrow),
    script: (name) => fetch(url(`/scripts/${encodeURIComponent(name)}`)).then(jsonOrThrow),
    scriptExecute: (body) =>
      fetch(url("/script/execute"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      }).then(jsonOrThrow),
    entropyAcquire: (integerList) =>
      fetch(url("/entropy/acquire"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ integerList }),
      }).then(jsonOrThrow),
    trainingStart: (database) =>
      fetch(url("/training/start"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ database }),
      }).then(jsonOrThrow),
    trainingUncover: () => fetch(url("/training/uncover"), { method: "POST" }).then(jsonOrThrow),
    autoMode: (signal) => fetch(url("/auto-mode"), { signal }).then(jsonOrThrow),
    autoModeOn: (database, multiplier, signal) =>
      fetch(url("/auto-mode/on"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ database, multiplier, ...caseJobGuard(window.__RADIWORKS_CASE_BINDING__)}),
        signal,
      }).then(jsonOrThrow),
    autoModeOff: (signal) => fetch(url("/auto-mode/off"), { method: "POST", signal }).then(jsonOrThrow),
    clarkeCompare: (rate) =>
      fetch(url("/materia/clarke-compare"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ rate }),
      }).then(jsonOrThrow),
  };
}

/* WebSocket mit Reconnect an letzter Event-ID und Boot-Kennung.
   server.hello wird als Kontrollereignis mit ID 0 nicht an Fach-Views
   weitergereicht. Ein Boot-Wechsel setzt den Cursor zurück und meldet
   "server.restarted", bevor der Server seine neue History replayt. */
export function connectSocket(wsUrl, { onEvent, onState, paused = false }) {
  wsUrl = resolveSocketTarget(wsUrl);
  let socket = null;
  let reconnectTimer = null;
  let lastEventId = null;
  let knownBoot = null;
  let closedByUser = false;
  let suspended = paused;

  const reconnectUrl = () => {
    const target = new URL(wsUrl, window.location.href);
    if (lastEventId !== null) target.searchParams.set("last_event_id", String(lastEventId));
    else if (knownBoot !== null) target.searchParams.set("last_event_id", "0");
    if (knownBoot !== null) target.searchParams.set("last_boot", knownBoot);
    return target.toString();
  };

  const open = () => {
    if (closedByUser || suspended) return;
    reconnectTimer = null;
    onState?.("connecting");
    const current = new WebSocket(reconnectUrl());
    socket = current;
    current.onopen = () => { if (socket === current) onState?.("online"); };
    current.onmessage = (message) => {
      if (socket !== current || suspended) return;
      try {
        const envelope = JSON.parse(message.data);
        if (!envelope || envelope.v !== 1) return;

        const boot = typeof envelope.boot === "string" && envelope.boot
          ? envelope.boot
          : null;
        if (knownBoot !== null && boot !== null && boot !== knownBoot) {
          lastEventId = null;
          onEvent?.({
            v: 1,
            id: 0,
            boot,
            type: "server.restarted",
            payload: {},
            ts: envelope.ts,
          });
        }
        if (boot !== null) knownBoot = boot;
        if (envelope.type === "server.hello") {
          const cursor = envelope.payload?.cursor;
          if (Number.isInteger(cursor) && cursor >= 0) lastEventId = cursor;
          return;
        }
        if (envelope.type === "server.replay_gap") {
          const oldest = envelope.payload?.oldestAvailableEventId;
          const latest = envelope.payload?.latestEventId;
          lastEventId = Number.isInteger(oldest)
            ? Math.max(0, oldest - 1)
            : (Number.isInteger(latest) ? latest : null);
          onEvent?.(envelope);
          return;
        }

        if (Number.isInteger(envelope.id) && envelope.id > 0) {
          lastEventId = lastEventId === null
            ? envelope.id
            : Math.max(lastEventId, envelope.id);
        }
        onEvent?.(envelope);
      } catch (_) { /* kein v:1-Umschlag — ignorieren */ }
    };
    current.onclose = () => {
      if (socket !== current) return;
      socket = null;
      if (closedByUser || suspended) return;
      onState?.("offline");
      if (reconnectTimer === null) reconnectTimer = setTimeout(open, 2000);
    };
    current.onerror = () => { if (socket === current && !suspended) onState?.("offline"); };
  };

  if (suspended) onState?.("paused");
  else open();
  return {
    suspend() {
      if (closedByUser || suspended) return;
      suspended = true;
      if (reconnectTimer !== null) clearTimeout(reconnectTimer);
      reconnectTimer = null;
      const current = socket;
      socket = null;
      current?.close();
      onState?.("paused");
    },
    resume() {
      if (closedByUser || !suspended) return;
      suspended = false;
      open();
    },
    close() {
      closedByUser = true;
      if (reconnectTimer !== null) clearTimeout(reconnectTimer);
      reconnectTimer = null;
      const current = socket;
      socket = null;
      current?.close();
    },
  };
}

/* API-Client + WebSocket-Fachkanal (Umschlag v:1, Reconnect an letzter Event-ID).
   Contract: Modul_Templates/standards/API_CONTRACT.md — apiBase NIE hardcodet. */

function resolveApiBase(apiBase) {
  const target = new URL(apiBase || "/", location.href);
  target.search = "";
  target.hash = "";
  target.pathname = target.pathname.replace(/\/$/, "");
  return target;
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
  if (!config.wsUrl) {
    const apiUrl = resolveApiBase(config.apiBase);
    apiUrl.protocol = apiUrl.protocol === "https:" ? "wss:" : "ws:";
    apiUrl.pathname = `${apiUrl.pathname.replace(/\/$/, "")}/ws`;
    apiUrl.search = "";
    apiUrl.hash = "";
    config.wsUrl = apiUrl.toString();
  }
  return config;
}

async function jsonOrThrow(response) {
  if (!response.ok) {
    let detail = `${response.status}`;
    try {
      const body = await response.json();
      detail = body.error?.message || body.detail || JSON.stringify(body);
    } catch (_) { /* Textfehler */ }
    throw new Error(detail);
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
  return {
    ping: (signal) => fetch(url("/ping"), { signal }).then(jsonOrThrow),
    manifest: () => fetch(url("/manifest")).then(jsonOrThrow),
    entropyStatus: () => fetch(url("/entropy/status")).then(jsonOrThrow),
    entropyFeed: () => fetch(url("/entropy/feed")).then(jsonOrThrow),
    databases: () => fetch(url("/databases")).then(jsonOrThrow),
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
    broadcast: (body) =>
      fetch(url("/broadcast"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      }).then(jsonOrThrow),
    queue: () => fetch(url("/broadcast/queue")).then(jsonOrThrow),
    stopCurrent: () => fetch(url("/broadcast/current"), { method: "DELETE" }).then(jsonOrThrow),
    stopAll: () => fetch(url("/broadcast/all"), { method: "DELETE" }).then(jsonOrThrow),
    cases: () => fetch(url("/cases")).then(jsonOrThrow),
    loadCase: (name) => fetch(url(`/cases/${encodeURIComponent(name)}`)).then(jsonOrThrow),
    activateCase: (name) => fetch(url(`/cases/${encodeURIComponent(name)}/activate`), { method: "POST" }).then(boundCaseOrThrow),
    activateCaseRef: (ref) => fetch(url(`/cases/ref/${encodeURIComponent(ref)}/activate`), { method: "POST" }).then(boundCaseOrThrow),
    currentCase: () => fetch(url("/cases/current")).then(jsonOrThrow),
    currentCaseWithRef: () => fetch(url("/cases/current")).then(boundCaseOrThrow),
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
        body: JSON.stringify(body),
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
        body: JSON.stringify({ database, multiplier }),
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

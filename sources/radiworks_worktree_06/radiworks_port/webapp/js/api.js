/* API-Client + WebSocket-Fachkanal (Umschlag v:1, Reconnect an letzter Event-ID).
   Contract: Modul_Templates/standards/API_CONTRACT.md — apiBase NIE hardcodet. */

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
    config.wsUrl =
      (location.protocol === "https:" ? "wss://" : "ws://") +
      location.host +
      (config.apiBase || "").replace(/\/$/, "") +
      "/ws";
  }
  return config;
}

async function jsonOrThrow(response) {
  if (!response.ok) {
    let detail = `${response.status}`;
    try {
      const body = await response.json();
      detail = body.detail || JSON.stringify(body);
    } catch (_) { /* Textfehler */ }
    throw new Error(detail);
  }
  return response.json();
}

export function createClient(apiBase) {
  const base = (apiBase || "").replace(/\/$/, "");
  const url = (path) => base + path;
  return {
    ping: () => fetch(url("/ping")).then(jsonOrThrow),
    manifest: () => fetch(url("/manifest")).then(jsonOrThrow),
    entropyStatus: () => fetch(url("/entropy/status")).then(jsonOrThrow),
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
    stickPosition: (x, y) =>
      fetch(url("/stickpad/position"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ x, y }),
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
    stopAll: () => fetch(url("/broadcast/all"), { method: "DELETE" }).then(jsonOrThrow),
    cases: () => fetch(url("/cases")).then(jsonOrThrow),
    loadCase: (name) => fetch(url(`/cases/${encodeURIComponent(name)}`)).then(jsonOrThrow),
    currentCase: () => fetch(url("/cases/current")).then(jsonOrThrow),
    saveCase: (body) =>
      fetch(url("/cases"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      }).then(jsonOrThrow),
    recentCases: () => fetch(url("/cases/recent")).then(jsonOrThrow),
    sessions: () => fetch(url("/analysis/sessions")).then(jsonOrThrow),
    viewSession: (index) =>
      fetch(url(`/analysis/sessions/${index}/view`), { method: "POST" }).then(jsonOrThrow),
    caseStatistics: (name) =>
      fetch(url(`/cases/${encodeURIComponent(name)}/statistics`)).then(jsonOrThrow),
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
    autoModeOn: (database, multiplier) =>
      fetch(url("/auto-mode/on"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ database, multiplier }),
      }).then(jsonOrThrow),
    autoModeOff: () => fetch(url("/auto-mode/off"), { method: "POST" }).then(jsonOrThrow),
    clarkeCompare: (rate) =>
      fetch(url("/materia/clarke-compare"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ rate }),
      }).then(jsonOrThrow),
  };
}

/* WebSocket mit Reconnect an letzter Event-ID (docs/15-live.md).
   Boot-Erkennung: startet die Engine neu, werden Events mit neuer Boot-ID
   akzeptiert (ID-Filter zurückgesetzt) und "server.restarted" gemeldet —
   die Webapp räumt dann Geister-Panels weg. */
export function connectSocket(wsUrl, { onEvent, onState }) {
  let socket = null;
  let lastEventId = null;
  let knownBoot = null;
  let closedByUser = false;

  const open = () => {
    const target = lastEventId == null ? wsUrl : `${wsUrl}?last_event_id=${lastEventId}`;
    onState?.("connecting");
    socket = new WebSocket(target);
    socket.onopen = () => onState?.("online");
    socket.onmessage = (message) => {
      try {
        const envelope = JSON.parse(message.data);
        if (envelope && envelope.v === 1) {
          if (knownBoot !== null && envelope.boot !== knownBoot) {
            lastEventId = null;
            onEvent?.({ v: 1, id: 0, boot: envelope.boot, type: "server.restarted", payload: {}, ts: envelope.ts });
          }
          knownBoot = envelope.boot;
          lastEventId = envelope.id;
          onEvent?.(envelope);
        }
      } catch (_) { /* kein v:1-Umschlag — ignorieren */ }
    };
    socket.onclose = () => {
      if (closedByUser) return;
      onState?.("offline");
      setTimeout(open, 2000);
    };
    socket.onerror = () => onState?.("offline");
  };

  open();
  return {
    close() {
      closedByUser = true;
      socket?.close();
    },
  };
}

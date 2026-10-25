/* Permanente Statusleiste (Original-Dashboard-Fuß, Aether_1/4):
   Status-LEDs · Broadcast-Queue mit Balken · Resonated Rates (Zähler,
   sortiert) · GV-Miniaturgraph. Läuft auf ALLEN Tabs, wie im Original. */

import { drawSeries } from "./gvgraph.js";

/* Laufzeit-Anzeige wie im Original („1 min 40 s 300 ms"). */
function formatDuration(seconds) {
  const totalMs = Math.max(0, Math.round(seconds * 1000));
  const m = Math.floor(totalMs / 60000);
  const s = Math.floor((totalMs % 60000) / 1000);
  const ms = totalMs % 1000;
  if (m > 0) return `${m} min ${s} s ${ms} ms`;
  return `${s} s ${ms} ms`;
}

export function initStatusBar(api, eventBus) {
  const leds = {
    broadcasting: document.getElementById("sled-broadcasting"),
    clearing: document.getElementById("sled-clearing"),
    grounding: document.getElementById("sled-grounding"),
  };
  const meters = {
    packages: document.getElementById("meter-packages"),
    cache: document.getElementById("meter-cache"),
    progress: document.getElementById("meter-progress"),
    queue: document.getElementById("meter-queue"),
  };
  const queueBars = document.getElementById("queue-bars");
  const resonatedMini = document.getElementById("resonated-mini");
  const gvMini = document.getElementById("gv-mini");
  const gvMiniText = document.getElementById("gv-mini-text");
  const dockToggle = document.getElementById("dock-toggle");
  const dockSummary = document.getElementById("dock-summary");
  const dockStopAllBtn = document.getElementById("dock-stop-all-btn");
  const dockClearResonanceBtn = document.getElementById("dock-clear-resonance-display-btn");
  const dockControlsStatus = document.getElementById("dock-controls-status");
  const dockResonanceStatus = document.getElementById("dock-resonance-status");
  const gvSeries = [];
  let resonanceBaseline = {};
  let latestQueue = null;
  let queueRequest = 0;
  let queueFetchInFlight = false;
  let queueRefreshPending = false;
  let contextRefreshPending = false;
  let clearPendingBaseline = false;

  function setDockOpen(open) {
    document.body.classList.toggle("dock-open", open);
    dockToggle.setAttribute("aria-expanded", String(open));
    dockToggle.textContent = open ? "Broadcast schließen" : "Broadcast öffnen";
  }
  dockToggle.addEventListener("click", () => setDockOpen(!document.body.classList.contains("dock-open")));
  dockStopAllBtn.addEventListener("click", () => {
    eventBus.dispatchEvent(new CustomEvent("broadcast.stop-all.request", { detail: { source: "dock" } }));
  });
  dockClearResonanceBtn.addEventListener("click", () => {
    eventBus.dispatchEvent(new CustomEvent("broadcast.resonance-display.clear", { detail: { source: "dock" } }));
  });
  eventBus.addEventListener("broadcast.controls.status", (event) => {
    const detail = event.detail || {};
    const status = detail.kind === "resonance-display" ? dockResonanceStatus : dockControlsStatus;
    status.textContent = detail.text || "";
    status.hidden = !detail.text;
  });
  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape" || !document.body.classList.contains("analysis-active")
        || !document.body.classList.contains("dock-open") || document.querySelector("dialog[open]")) return;
    event.preventDefault();
    setDockOpen(false);
    dockToggle.focus();
  });

  // Fixed dock must never cover a control reached with the keyboard.
  document.addEventListener("focusin", (event) => {
    const target = event.target;
    if (!document.body.classList.contains("analysis-active") || !(target instanceof HTMLElement)
        || target.closest(".statusbar")) return;
    const rect = target.getBoundingClientRect();
    const dock = document.querySelector(".statusbar").getBoundingClientRect();
    const bottom = Math.min(window.innerHeight, dock.top) - 12;
    const shift = rect.bottom > bottom ? rect.bottom - bottom : rect.top < 12 ? rect.top - 12 : 0;
    if (shift) window.scrollBy({top:shift, behavior:"instant"});
  });

  const ledOn = (el, on) => el.classList.toggle("on", Boolean(on));

  function publishResonanceStatus(text) {
    eventBus.dispatchEvent(new CustomEvent("broadcast.controls.status", {
      detail: { text, error: false, kind: "resonance-display" },
    }));
  }

  function renderResonanceTotals(resonanceTotals = {}) {
    const totals = clearPendingBaseline
      ? []
      : Object.entries(resonanceTotals)
        .map(([signature, count]) => [signature, Math.max(0, count - (resonanceBaseline[signature] || 0))]);
    const visible = totals
      .filter(([, count]) => count > 0)
      .sort((a, b) => b[1] - a[1]);
    resonatedMini.innerHTML = "";
    if (!visible.length) {
      resonatedMini.innerHTML = '<li class="hint">Noch keine Resonanz.</li>';
    } else {
      for (const [signature, count] of visible.slice(0, 8)) {
        const li = document.createElement("li");
        li.className = "resonated-row";
        const c = document.createElement("strong");
        c.textContent = String(count);
        const n = document.createElement("span");
        n.textContent = signature;
        n.title = signature;
        li.append(c, n);
        resonatedMini.appendChild(li);
      }
    }
  }
  function renderQueue(queue) {
    const active = queue.active || [];
    const queued = queue.queued || [];
    const summary = `${active.length} aktiv · ${queued.length} wartend`;
    if (dockSummary.textContent !== summary) dockSummary.textContent = summary;
    meters.queue.textContent = `QUEUE ${queued.length + active.length}`;
    meters.progress.textContent = `PROGRESS ${
      active.length ? Math.round((active[0].progress || 0) * 100) : 0
    } %`;
    ledOn(leds.broadcasting, active.length > 0);

    queueBars.innerHTML = "";
    if (!active.length && !queued.length) {
      queueBars.innerHTML = '<p class="hint">Leer.</p>';
    }
    for (const entry of [...active, ...queued]) {
      const row = document.createElement("div");
      row.className = "queue-bar-row";
      const name = document.createElement("span");
      name.className = "queue-bar-name";
      name.textContent = `${entry.signature} · ${formatDuration(entry.seconds ?? 0)}`;
      name.title = entry.signature;
      const track = document.createElement("span");
      track.className = "queue-bar-track";
      const fill = document.createElement("span");
      fill.className = "queue-bar-fill";
      fill.style.width = `${Math.round((entry.progress || 0) * 100)}%`;
      track.appendChild(fill);
      const count = document.createElement("span");
      count.className = "hint";
      count.textContent = `#${entry.resonanceCount ?? 0}`;
      // Transparenz: statistische Wartezeit bis zur nächsten Resonanz
      // (Wahrscheinlichkeit 1/(6765+multiplier) je Draw, ~60 Draws/s je Panel)
      const expectedSeconds = Math.round((6765 + (entry.multiplier ?? 1)) / 60);
      count.title = `Resonanz statistisch alle ~${expectedSeconds} s je Panel (1/(6765+Multiplikator) je Draw)`;
      row.append(name, track, count);
      queueBars.appendChild(row);
    }
    latestQueue = queue;
    if (clearPendingBaseline) {
      resonanceBaseline = { ...(queue.resonanceTotals || {}) };
      clearPendingBaseline = false;
      publishResonanceStatus("Resonanzanzeige geleert; die Zählerbasis wurde beim ersten gültigen Queue-Stand festgelegt. Neue Resonanzen ab diesem Stand werden angezeigt.");
    }
    renderResonanceTotals(queue.resonanceTotals || {});
  }

  async function refreshQueue({ resetBaseline = false } = {}) {
    if (queueFetchInFlight) {
      if (resetBaseline) {
        queueRequest += 1;
        contextRefreshPending = true;
        queueRefreshPending = false;
      } else if (!contextRefreshPending) {
        queueRefreshPending = true;
      }
      return;
    }
    queueFetchInFlight = true;
    const request = ++queueRequest;
    try {
      const queue = await api.queue();
      if (request !== queueRequest) return;
      if (resetBaseline) {
        resonanceBaseline = { ...(queue.resonanceTotals || {}) };

      }
      renderQueue(queue);
    } catch (_) { /* offline */ }
    finally {
      queueFetchInFlight = false;
      if (contextRefreshPending) {
        contextRefreshPending = false;
        queueRefreshPending = false;
        void refreshQueue({ resetBaseline: true });
      } else if (queueRefreshPending) {
        queueRefreshPending = false;
        void refreshQueue();
      }
    }
  }

  async function refresh() {
    if (document.hidden) return;
    void refreshQueue();
    try {
      const feed = await api.entropyFeed();
      meters.cache.textContent = `CACHE ${feed.feedSize}`;
      meters.packages.textContent = `PACKAGES ${Math.ceil(feed.feedSize / 10000)}`;
    } catch (_) { /* offline */ }
  }

  eventBus.addEventListener("broadcast.progress", () => refresh());
  eventBus.addEventListener("broadcast.resonance", () => refresh());
  eventBus.addEventListener("broadcast.resonance-display.clear", () => {
    queueRequest += 1;
    queueRefreshPending = false;
    contextRefreshPending = false;
    if (latestQueue) {
      resonanceBaseline = { ...(latestQueue.resonanceTotals || {}) };
      clearPendingBaseline = false;
      publishResonanceStatus("Resonanzanzeige browserlokal zurückgesetzt. Neue Server-Resonanzen ab dem aktuellen Zählerstand werden angezeigt; die GV-Sitzungshistorie bleibt erhalten.");
    } else {
      clearPendingBaseline = true;
      publishResonanceStatus("Resonanzanzeige browserlokal zurückgesetzt. Die Zählerbasis wird beim ersten gültigen Queue-Stand festgelegt; neue Resonanzen ab diesem Stand werden angezeigt.");
    }
    renderResonanceTotals(latestQueue?.resonanceTotals || {});
  });  eventBus.addEventListener("analysis.context", () => {
    void refreshQueue({ resetBaseline: true });
  });
  eventBus.addEventListener("clear.flash", () => {
    ledOn(leds.clearing, true);
    setTimeout(() => ledOn(leds.clearing, false), 2500);
  });
  eventBus.addEventListener("grounding.start", () => {
    ledOn(leds.grounding, true);
    setTimeout(() => ledOn(leds.grounding, false), 12000);
  });
  eventBus.addEventListener("gv.value", (event) => {
    const { gv, runs, source } = event.detail;
    if (gv != null) {
      gvSeries.push(gv);
      if (gvSeries.length > 60) gvSeries.shift();
      drawSeries(gvMini, gvSeries);
    }
    const counter = source === "auto" ? "Auto-Züge" : "GV-Züge dieser Runde";
    gvMiniText.textContent = `GV ${gv ?? "—"} (${counter}: ${runs ?? 0})`;
  });

  refresh();
  setInterval(refresh, 2000);
  document.addEventListener("visibilitychange", () => { if (!document.hidden) refresh(); });
}

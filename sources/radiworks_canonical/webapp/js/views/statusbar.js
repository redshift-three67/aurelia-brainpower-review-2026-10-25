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
  const gvSeries = [];
  let resonanceBaseline = {};

  function setDockOpen(open) {
    document.body.classList.toggle("dock-open", open);
    dockToggle.setAttribute("aria-expanded", String(open));
    dockToggle.textContent = open ? "Broadcast schließen" : "Broadcast öffnen";
  }
  dockToggle.addEventListener("click", () => setDockOpen(!document.body.classList.contains("dock-open")));
  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape" || !document.body.classList.contains("analysis-active")
        || !document.body.classList.contains("dock-open") || document.querySelector("dialog[open]")) return;
    event.preventDefault();
    setDockOpen(false);
    dockToggle.focus();
  });

  const ledOn = (el, on) => el.classList.toggle("on", Boolean(on));

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
    // Resonated Rates (Original: Zähler absteigend, oben)
    const totals = Object.entries(queue.resonanceTotals || {})
      .map(([signature, count]) => [signature, Math.max(0, count - (resonanceBaseline[signature] || 0))])
      .filter(([, count]) => count > 0)
      .sort((a, b) => b[1] - a[1]);
    resonatedMini.innerHTML = "";
    if (!totals.length) {
      resonatedMini.innerHTML = '<li class="hint">Noch keine Resonanz.</li>';
    } else {
      for (const [signature, count] of totals.slice(0, 8)) {
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

  async function refresh() {
    if (document.hidden) return;
    try {
      renderQueue(await api.queue());
    } catch (_) { /* offline */ }
    try {
      const feed = await api.entropyFeed();
      meters.cache.textContent = `CACHE ${feed.feedSize}`;
      meters.packages.textContent = `PACKAGES ${Math.ceil(feed.feedSize / 10000)}`;
    } catch (_) { /* offline */ }
  }

  eventBus.addEventListener("broadcast.progress", () => refresh());
  eventBus.addEventListener("broadcast.resonance", () => refresh());
  eventBus.addEventListener("analysis.context", async () => {
    try {
      const queue = await api.queue();
      resonanceBaseline = { ...(queue.resonanceTotals || {}) };
      renderQueue(queue);
    } catch (_) {
      // Ohne aktuellen Zählerstand bleiben bestehende Werte sichtbar.
    }
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

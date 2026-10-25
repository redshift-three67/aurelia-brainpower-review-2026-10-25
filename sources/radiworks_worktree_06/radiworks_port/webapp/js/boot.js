/* Boot: Konfiguration → Theme → Views → Fachkanal.
   Theme-Vertrag (UI_DESIGN_STANDARD §1/§2): data-module-theme + data-accent
   am Wurzelelement — steuerbar von Aurelia ODER aus dem Modul selbst. */

import { connectSocket, createClient, resolveConfig } from "./api.js";
import { initAnalyzeView } from "./views/analyze.js";
import { initBroadcastView, renderEmitterSequence } from "./views/broadcast.js";
import { initInfoView } from "./views/info.js";
import { initSettingsView } from "./views/settings.js";
import { initStickPadView } from "./views/stickpad.js";
import { initCasesView } from "./views/cases.js";
import { initImagesView } from "./views/images.js";
import { initPeggottyView } from "./views/peggotty.js";
import { initEntropyView } from "./views/entropy.js";
import { initStatusBar } from "./views/statusbar.js";

const config = resolveConfig();
const root = document.documentElement;

/* ---- Theme (Layer 2/3) ---- */
root.setAttribute("data-module-theme", config.theme);
root.setAttribute("data-accent", config.accent);
if (config.mode) root.setAttribute("data-mode", config.mode);

const accentSelect = document.getElementById("accent-select");
accentSelect.value = config.accent;
accentSelect.addEventListener("change", () => {
  root.setAttribute("data-accent", accentSelect.value);
  window.parent?.postMessage(
    { type: "module:theme", theme: config.theme, accent: accentSelect.value },
    "*"
  );
});

/* ---- Modus: Hell → Dunkel → Auto (Circadian, Radiquant5-Design) ---- */
const modeToggle = document.getElementById("mode-toggle");
let circadianTimer = null;

function applyCircadian() {
  const hour = new Date().getHours();
  // Circadian: dunkel abends/nachts (18–8 Uhr), hell tagsüber
  root.setAttribute("data-mode", hour >= 18 || hour < 8 ? "dark" : "light");
}

function setMode(mode) {
  if (circadianTimer) { clearInterval(circadianTimer); circadianTimer = null; }
  if (mode === "dark") {
    root.setAttribute("data-mode", "dark");
    modeToggle.textContent = "Dunkel";
    modeToggle.setAttribute("aria-pressed", "true");
  } else if (mode === "auto") {
    applyCircadian();
    circadianTimer = setInterval(applyCircadian, 5 * 60 * 1000);
    document.addEventListener("visibilitychange", () => { if (!document.hidden) applyCircadian(); });
    modeToggle.textContent = "Auto (Circadian)";
    modeToggle.setAttribute("aria-pressed", "false");
  } else {
    root.setAttribute("data-mode", "light");
    modeToggle.textContent = "Hell";
    modeToggle.setAttribute("aria-pressed", "false");
  }
}

const MODE_CYCLE = ["light", "dark", "auto"];
let modeIndex = 0;
modeToggle.addEventListener("click", () => {
  modeIndex = (modeIndex + 1) % MODE_CYCLE.length;
  setMode(MODE_CYCLE[modeIndex]);
});
if (config.mode === "circadian") config.mode = "auto";
if (config.mode) {
  modeIndex = Math.max(0, MODE_CYCLE.indexOf(config.mode));
  setMode(config.mode);
}

/* ---- Tabs ---- */
const tabs = [...document.querySelectorAll(".tab")];
tabs.forEach((tab) =>
  tab.addEventListener("click", () => {
    tabs.forEach((t) => t.setAttribute("aria-selected", String(t === tab)));
    document.querySelectorAll(".view").forEach((view) => {
      view.hidden = view.id !== `view-${tab.dataset.tab}`;
    });
  })
);

/* ---- API + Fachkanal ---- */
const api = createClient(config.apiBase);
const eventBus = new EventTarget();

const statusEl = document.getElementById("ws-status");
connectSocket(config.wsUrl, {
  onState: (state) => {
    statusEl.classList.toggle("online", state === "online");
    statusEl.classList.toggle("offline", state === "offline");
    statusEl.querySelector(".led-text").textContent =
      state === "online" ? "Live" : state === "connecting" ? "verbinde …" : "offline";
  },
  onEvent: (envelope) => {
    eventBus.dispatchEvent(new CustomEvent(envelope.type, { detail: envelope.payload }));
  },
});

/* ---- Build-Zeile (E-E-A-T: Herkunft sichtbar) ---- */
api.manifest().then((m) => {
  document.getElementById("footer-build").textContent =
    `${m.id} ${m.version} · ${m.hash.slice(0, 19)}… · repro: ${m.repro} · isHardwareActivatable: ${m.isHardwareActivatable}`;
});

/* ---- Views ---- */
initAnalyzeView(api, eventBus);
initBroadcastView(api, eventBus);
initInfoView(api, eventBus);
initSettingsView(api);
initStickPadView(api);
initCasesView(api, eventBus);
initImagesView(api);
initPeggottyView(api);
initEntropyView(api);
initStatusBar(api, eventBus);
eventBus.addEventListener("emitter.sequence", (event) => renderEmitterSequence(event.detail));

/* ---- Aktiver Fall im Header (Original: Fenstertitel mit Fallnamen) ---- */
const caseBadge = document.getElementById("case-badge");
function setCaseBadge(name) {
  caseBadge.textContent = name ? `Fall: ${name}` : "kein Fall geladen";
  caseBadge.classList.toggle("case-active", Boolean(name));
  // Vektor-Bindung (g): aktiver Fall ist der aktuelle „Fokus" — Broadcasts
  // stellen ihn der Signatur voran (wie im Original: sessionName + Eingabe).
  window.__RADIWORKS_CASE__ = name || null;
}
api.currentCase().then((current) => setCaseBadge(current?.name || null)).catch(() => {});
eventBus.addEventListener("case.changed", (event) => setCaseBadge(event.detail?.name || null));

api.ping().catch(() => {
  statusEl.querySelector(".led-text").textContent = "Engine nicht erreichbar";
});

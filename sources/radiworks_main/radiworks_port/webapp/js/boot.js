/* Boot: Konfiguration → Theme → Views → Fachkanal.
   Theme-Vertrag (UI_DESIGN_STANDARD §1/§2): data-module-theme + data-accent
   am Wurzelelement — steuerbar von Aurelia ODER aus dem Modul selbst. */

import { connectSocket, createClient, resolveConfig } from "./api.js";
import { initAnalyzeView } from "./views/analyze.js";
import { initBroadcastView, renderEmitterSequence } from "./views/broadcast.js";
import { initInfoView } from "./views/info.js";
import { initCompletionNotice } from "./views/completion_notice.js";
import { initAdjustmentHistory } from "./views/adjustment_history.js";
import { initSettingsView } from "./views/settings.js";
import { initStickPadView } from "./views/stickpad.js";
import { initCasesView } from "./views/cases.js";
import { initImagesView } from "./views/images.js";
import { initPeggottyView } from "./views/peggotty.js";
import { initEntropyView } from "./views/entropy.js";
import { initGvObservationsView } from "./views/gv_observations.js";
import { initStatusBar } from "./views/statusbar.js";

let config;
try {
  config = resolveConfig();
} catch (error) {
  const notice = document.createElement("p");
  notice.className = "panel";
  notice.setAttribute("role", "alert");
  notice.textContent = "Verbindung gesperrt: Diese lokale RadiWorks-Instanz darf nur mit ihrem eigenen Server verbunden sein. Bitte die Adresse ohne api-/ws-Parameter öffnen.";
  document.querySelector("main").prepend(notice);
  document.querySelectorAll("button,input,select,textarea").forEach(element => { element.disabled = true; });
  throw error;
}
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
if (!["light", "dark", "auto"].includes(config.mode)) config.mode = "dark";
if (config.mode) {
  modeIndex = Math.max(0, MODE_CYCLE.indexOf(config.mode));
  setMode(config.mode);
}

/* ---- Tabs ---- */
const tabs = [...document.querySelectorAll(".tab")];
function activateTab(tab, focus = false) {
  tabs.forEach((item) => {
    item.setAttribute("aria-selected", String(item === tab));
    item.tabIndex = item === tab ? 0 : -1;
  });
  document.querySelectorAll(".view").forEach((view) => {
    view.hidden = view.id !== tab.getAttribute("aria-controls");
  });
  document.body.classList.toggle("analysis-active", tab.id === "tab-analyse");
  if (focus) tab.focus();
  tab.scrollIntoView({block:"nearest", inline:"nearest", behavior:"instant"});
}
tabs.forEach((tab) => tab.addEventListener("click", () => activateTab(tab)));
document.querySelectorAll("[data-open-tab]").forEach(button => button.addEventListener("click", () => {
  const tab = document.getElementById(button.dataset.openTab);
  if (tabs.includes(tab)) activateTab(tab, true);
}));
document.querySelector(".tabs").addEventListener("keydown", (event) => {
  const index = tabs.indexOf(event.target);
  if (index < 0) return;
  let next;
  if (event.key === "ArrowRight") next = (index + 1) % tabs.length;
  else if (event.key === "ArrowLeft") next = (index - 1 + tabs.length) % tabs.length;
  else if (event.key === "Home") next = 0;
  else if (event.key === "End") next = tabs.length - 1;
  else return;
  event.preventDefault();
  activateTab(tabs[next], true);
});

/* ---- API + Fachkanal ---- */
const api = createClient(config.apiBase);
const eventBus = new EventTarget();

const statusEl = document.getElementById("ws-status");
const liveConnection = connectSocket(config.wsUrl, {
  paused: document.hidden,
  onState: (state) => {
    eventBus.dispatchEvent(new CustomEvent("connection.state", {detail:{state}}));
    statusEl.classList.toggle("online", state === "online");
    statusEl.classList.toggle("offline", state === "offline");
    statusEl.querySelector(".led-text").textContent =
      state === "online" ? "Live" : state === "connecting" ? "verbinde …" : state === "paused" ? "pausiert" : "offline";
  },
  onEvent: (envelope) => {
    eventBus.dispatchEvent(new CustomEvent(envelope.type, { detail: envelope.payload }));
  },
});
document.addEventListener("visibilitychange", () => {
  if (document.hidden) liveConnection.suspend();
  else liveConnection.resume();
});
window.addEventListener("pagehide", () => liveConnection.suspend());
window.addEventListener("pageshow", () => { if (!document.hidden) liveConnection.resume(); });

/* ---- Build-Zeile (E-E-A-T: Herkunft sichtbar) ---- */
api.manifest().then((m) => {
  document.getElementById("footer-build").textContent =
    `${m.id} ${m.version} · ${m.hash.slice(0, 19)}… · repro: ${m.repro} · isHardwareActivatable: ${m.isHardwareActivatable}`;
});

/* ---- Views ---- */
initAnalyzeView(api, eventBus);
initBroadcastView(api, eventBus);
initInfoView(api, eventBus);
initSettingsView(api, eventBus);
initCompletionNotice(api, eventBus);
initAdjustmentHistory(api, eventBus);
initStickPadView(api, eventBus);
initCasesView(api, eventBus);
initImagesView(api);
initPeggottyView(api);
initEntropyView(api);
initStatusBar(api, eventBus);
initGvObservationsView(api);
eventBus.addEventListener("emitter.sequence", (event) => renderEmitterSequence(event.detail));

/* ---- Aktiver Fall im Header (Original: Fenstertitel mit Fallnamen) ---- */
const caseBadge = document.getElementById("case-badge");
function setCaseBadge(name) {
  caseBadge.textContent = name ? `Fall: ${name}` : "kein Fall geladen";
  caseBadge.classList.toggle("case-active", Boolean(name));
  // Vektor-Bindung (g): aktiver Fall ist der aktuelle „Fokus" — Broadcasts
  // stellen ihn der Signatur voran (wie im Original: sessionName + Eingabe).
  window.__RADIWORKS_CASE__ = name === "[CopyGuard: Text zurückgehalten]" ? null : (name || null);
}
api.currentCaseWithRef().then(({data, ref}) => {
  setCaseBadge(data?.name || null);
  window.__RADIWORKS_CASE_BINDING__ = ref ? {ref, contextVersion:data.contextVersion || null} : null;
}).catch(() => {});
eventBus.addEventListener("case.changed", (event) => {
  setCaseBadge(event.detail?.name || event.detail?.savedCase?.name || null);
  const ref = event.detail?.ref;
  window.__RADIWORKS_CASE_BINDING__ = ref ? {ref, contextVersion:event.detail?.contextVersion || event.detail?.savedCase?.contextVersion || null} : null;
});

api.ping().catch(() => {
  statusEl.querySelector(".led-text").textContent = "Engine nicht erreichbar";
});

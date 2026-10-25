/* Analyse-View im Original-Layout (Aether_4):
   Spalten Nr/EW/Rate/Potenz/Lvl/HIT/GV/GV-RE/REC, Pagination à 21,
   HIT = höchste GV der Seite (Marker), Wortwiederholungs-Hervorhebung,
   Zeilen-Broadcast + Materia-Medica-Link, GV-Runde mit runs-Zähler +
   Graph, Auto-Modus, Essenzielle Fragen, Grounding/Clear/Training. */

import { initRandomModeSelection, isRandomMode } from "../random-mode-selection.js";
import { initWatchlist } from "./watchlist.js";
import { initPersonalAnalysis } from "./personal_analysis.js";
import { analysisJobOrigin } from "../job-context.js";
import { drawSeries } from "./gvgraph.js";
import { compareRateGv, analysisTrialLabel } from "./gv_presentation.js";
import { filterDatabaseNames } from "./database_search.js";
import { initCatalogSuggestions } from "./catalog_suggestions.js";

export function analyzeStartReadiness({ procedure, mode, entropyStatus, analysisBusy, catalogsReady }) {
  const baseDisabled = analysisBusy || !catalogsReady;
  if (!isRandomMode(mode || entropyStatus?.defaultMode)) {
    return { disabled: true, noteHidden: false, noteText: 'Bitte einen Zufallsmodus ausw\u00e4hlen.' };
  }
  if (procedure === 'personal') {
    return { disabled: baseDisabled, noteHidden: true, noteText: '' };
  }
  if (!entropyStatus) {
    return { disabled: true, noteHidden: false, noteText: 'Entropie-Status wird geladen …' };
  }

  const recovery = entropyStatus.stochasticRecovery;
  const effectiveMode = mode || entropyStatus.defaultMode;
  if (effectiveMode !== 'stochastic') {
    return { disabled: baseDisabled, noteHidden: true, noteText: '' };
  }
  if (recovery?.activeCase && !recovery?.available) {
    return {
      disabled: true,
      noteHidden: false,
      noteText: 'Fallgebundene stochastic-Recovery ist nicht verfügbar. Bitte seeded verwenden oder die Betreiberkonfiguration prüfen.',
    };
  }
  return {
    disabled: baseDisabled,
    noteHidden: false,
    noteText: recovery?.activeCase
      ? 'Fallgebundene stochastic-Recovery ist verschlüsselt verfügbar.'
      : 'Stochastic ohne aktiven Fall ist möglich, aber nicht für Session-Recovery verfügbar.',
  };
}
const PAGE_SIZE = 21; // wie im Original (AnalyseScreen, startIndex = (page-1)*21)
const AUTO_RECONCILE_WAIT_MS = 1500;
const AUTO_COMMAND_TIMEOUT_MS = 4000;
const AUTO_SYNC_TIMEOUT_MS = 2000;
const AUTO_STATE_POLL_MS = 2000;
const COPYGUARD_REDACTION = "[CopyGuard: Text zurückgehalten]";

export function initAnalyzeView(api, eventBus) {
  const dbSelect = document.getElementById("db-select");
  const dbSearch = document.getElementById("db-search");
  const dbSearchClear = document.getElementById("db-search-clear");
  const dbFocusSearch = document.getElementById("db-focus-search");
  const dbSearchStatus = document.getElementById("db-search-status");
  const caseFocusHint = document.getElementById("case-focus-hint");
  // Phase 2 Persistenz: Die Auswahl kann erst nach dem Katalog-Rendern gelten.
  const savedDb = localStorage.getItem("radiworks_selected_db");
  const seedInput = document.getElementById("seed-input");
  const modeSelect = document.getElementById("mode-select");
  const randomChoice = initRandomModeSelection(modeSelect, document.getElementById("random-mode-status"));
  const maxHitsSelect = document.getElementById("maxhits-select");
  let cutoffChosen = false;
  maxHitsSelect.addEventListener("change", () => { cutoffChosen = true; });
  api.settings().then(saved => {
    if (!cutoffChosen) maxHitsSelect.value = saved.booleans?.["analysis.very.high.max.hit"] === true ? "1000" : "100";
  }).catch(error => { console.warn("EW-Vorbelegung nicht verfügbar", error.name); });
  const form = document.getElementById("analyze-form");
  const procedureSelect=document.getElementById("analysis-procedure");
  const personalAnalysis=initPersonalAnalysis(api,eventBus,procedureSelect);
  function showProcedure() {
    const personal=procedureSelect.value==="personal";
    const visible=(element,show)=>{element.hidden=!show;element.style.display=show?"":"none";};
    visible(document.getElementById("personal-analysis-panel"),personal);
    visible(document.getElementById("personal-weight-control"),personal);
    visible(document.getElementById("watchlist-panel"),!personal);
    // Original GV stays observable; only Original commands are gated. Child busy/CopyGuard flags remain intact.
    document.getElementById("original-gv-controls").disabled=personal;
    document.getElementById("original-draft-controls").disabled=personal;
    document.getElementById("original-tools-hint").hidden=!personal;
    document.getElementById("gv-title").textContent=personal ? "General Vitality · Original" : "General Vitality";
    document.getElementById("draft-title").textContent=personal ? "Originalanalyse prüfen und freigeben" : "Analyse prüfen und freigeben";
    updateStickPadVisibility();
    visible(document.getElementById("result-count").closest(".panel"),!personal);
    maxHitsSelect.disabled=personal;
    applyStochasticRecoveryReadiness();
  }
  procedureSelect.addEventListener("change",showProcedure);
  document.getElementById("original-tools-btn").addEventListener("click",()=>{
    procedureSelect.value="original";
    procedureSelect.dispatchEvent(new Event("change"));
    document.getElementById("gv-btn").focus();
  });
  function originalSelected() { return procedureSelect.value==="original"; }
  const analyzeButton = form.querySelector(".btn-primary");
  const analysisRequestStatus = document.getElementById("analysis-request-status");
  const stochasticRecoveryNote = document.getElementById("stochastic-recovery-note");

  const gvValue = document.getElementById("gv-value");
  const gvMeta = document.getElementById("gv-meta");
  const gvAnalysisTrials = document.getElementById("gv-analysis-trials");
  const gvManualSteps = document.getElementById("gv-manual-steps");
  const gvAutoSummary = document.getElementById("gv-auto-summary");
  const gvBtn = document.getElementById("gv-btn");
  const gvPageBtn = document.getElementById("gv-page-btn");
  const gvLaterPageBtn = document.getElementById("gv-later-page-btn");
  const gvPageStatus = document.getElementById("gv-page-status");
  const autoOnBtn = document.getElementById("auto-on-btn");
  const autoOffBtn = document.getElementById("auto-off-btn");
  const multiplierInput = document.getElementById("mul-input");
  const graph = document.getElementById("gv-graph");

  const eqBtn = document.getElementById("eq-btn");
  const eqReport = document.getElementById("eq-report");

  const draftEmpty = document.getElementById("draft-empty");
  const draftBody = document.getElementById("draft-body");
  const draftStatus = document.getElementById("draft-status");
  const draftCopyguard = document.getElementById("draft-copyguard");
  const draftKernel = document.getElementById("draft-kernel");
  const readyBtn = document.getElementById("draft-ready-btn");
  const promoteBtn = document.getElementById("draft-promote-btn");
  const draftHint = document.getElementById("draft-hint");

  const resultEmpty = document.getElementById("result-empty");
  const resultWrap = document.getElementById("result-wrap");
  const resultBody = document.getElementById("result-body");
  const resultCount = document.getElementById("result-count");
  const resultDatabase = document.getElementById("result-database");
  const stickPadFollowup = document.getElementById("stickpad-followup");
  const stickPadFollowupBtn = document.getElementById("stickpad-followup-btn");
  const resultRecurrenceHint = document.getElementById("result-recurrence-hint");
  const resultGvHint = document.getElementById("result-gv-hint");
  const pager = document.getElementById("pager");

  let rates = [];
  let lastResultDatabase = null;
  let lastResultDraftId = null;
  let currentSessionId = null;
  let gvPageBusy = false;
  let page = 1;
  let autoStateRevision = 0;
  let autoSyncRequest = 0;
  let autoCommandRequest = 0;
  let autoSafetyError = null;
  const autoCommandsInFlight = new Map();
  const gvSeries = [];
  let entropyStatus = null;
  let catalogsReady = false;
  let analysisBusy = false;
  let stickPadSourceSessionId = null;
  let stickPadFollowupSupported = false;
  let latestCaseGv = null;
  let autoEnabled = false;
  initWatchlist(api,eventBus,()=>({original:procedureSelect.value==="original",sessionId:currentSessionId,rates,mode:modeSelect.value||entropyStatus?.defaultMode||"seeded",seed:seedInput.value===""?0:Number(seedInput.value)}));
  showProcedure();
  analyzeButton.disabled = true;
  api.ping().then((status) => {
    stickPadFollowupSupported = status.supportsStickPadFollowup === true;
    updateStickPadVisibility();
  }).catch(() => { stickPadFollowup.hidden = true; });

  function stochasticRecoveryBlocked() {
    const recovery = entropyStatus?.stochasticRecovery;
    const effectiveMode = modeSelect.value || entropyStatus?.defaultMode;
    return effectiveMode === "stochastic" && recovery?.activeCase && !recovery?.available;
  }

  function applyStochasticRecoveryReadiness() {
    const readiness = analyzeStartReadiness({
      procedure: procedureSelect.value,
      mode: modeSelect.value || entropyStatus?.defaultMode,
      entropyStatus,
      analysisBusy,
      catalogsReady,
    });
    stochasticRecoveryNote.hidden = readiness.noteHidden;
    stochasticRecoveryNote.textContent = readiness.noteText;
    analyzeButton.disabled = readiness.disabled;
  }

  async function refreshStochasticRecoveryReadiness() {
    try {
      entropyStatus = await api.entropyStatus();
    } catch (_) {
      entropyStatus = null;
    }
    randomChoice.adopt(entropyStatus?.defaultMode);
    applyStochasticRecoveryReadiness();
  }

  /* ---- Datenbanken ---- */
  const databaseGroups = [
    ["HOMEOPATHY", "Homeopathie"],
    ["BIOLOGICAL", "Biologisch"],
    ["SYMBOLISM", "Symbolik"],
    ["ESSENCES", "Essenzen"],
    ["CHEMICAL", "Chemie"],
    ["ENERGY", "Energie"],
    ["AGRICULTURE", "Agriculture"],
    ["ANALYSIS", "Analyse-Raten"],
  ];
  const categoryButtons = [...document.querySelectorAll(".cat-btn")];
  categoryButtons.forEach((button) => { button.disabled = true; });
  let allDatabaseNames = [];
  let catalogEntries = [];
  function entryForSelector(value) {
    const direct = catalogEntries.find(entry => entry.id === value || entry.exactId === value);
    if (direct) return direct;
    const name = String(value || "").replace(/\.txt$/, "");
    const matches = catalogEntries.filter(entry => entry.name === name);
    return matches.length === 1 ? matches[0] : null;
  }
  function selectorFor(value) {
    const entry = entryForSelector(value);
    if (!entry) return value;
    return value === entry.exactId || String(value).endsWith(".txt") ? entry.exactId : entry.id;
  }
  let caseFocus = "";

  function appendDatabaseOption(parent, value, label, group = false) {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = label;
    if (group) option.dataset.group = "true";
    parent.appendChild(option);
    return option;
  }

  function renderDatabases(names, selectedValue = "") {
    dbSelect.innerHTML = "";
    const selectedEntry = entryForSelector(selectedValue);
    const selectedId = selectorFor(selectedValue);
    const exact = selectedEntry && (selectedId === selectedEntry.exactId);
    const entries = catalogEntries.filter(entry => names.includes(entry.name));
    if (exact) appendDatabaseOption(dbSelect, selectedId, "Einzeldatenbank: " + selectedEntry.label);
    const selectedGroup = databaseGroups.find(([prefix]) => prefix === selectedValue);
    const groupVisible = selectedGroup && entries.some(entry => entry.name.startsWith(selectedValue));
    if (!exact && selectedEntry && !entries.some(entry => entry.id === selectedEntry.id)) {
      appendDatabaseOption(dbSelect, selectedId, "Aktuell gewählt: " + selectedEntry.label);
    } else if (selectedGroup && !groupVisible) {
      appendDatabaseOption(dbSelect, selectedValue, "Aktuell gewählt: " + selectedGroup[1], true);
    }
    const remaining = new Set(entries);
    for (const [prefix, label] of databaseGroups) {
      const children = entries.filter(entry => entry.name.startsWith(prefix));
      if (!children.length) continue;
      const group = document.createElement("optgroup"); group.label = label;
      appendDatabaseOption(group, prefix, "Alle " + label + "-Datenbanken", true);
      for (const entry of children) appendDatabaseOption(group, entry.id, entry.label);
      dbSelect.appendChild(group);
      children.forEach(entry => remaining.delete(entry));
    }
    if (remaining.size) {
      const group = document.createElement("optgroup"); group.label = "Weitere Datenbanken";
      for (const entry of [...remaining].sort((a,b)=>a.name < b.name ? -1 : a.name > b.name ? 1 : 0)) {
        appendDatabaseOption(group, entry.id, entry.label);
      }
      dbSelect.appendChild(group);
    }
    if (!names.length && !dbSelect.options.length) {
      const empty = appendDatabaseOption(dbSelect, "", "Keine Namenstreffer"); empty.disabled = true;
    }
    if (selectedId && [...dbSelect.options].some(option => option.value === selectedId)) dbSelect.value = selectedId;
  }

  function updateCategoryButtons() {
    categoryButtons.forEach((button) => {
      const prefix = button.dataset.cat;
      const available = allDatabaseNames.some((name) => name.startsWith(prefix));
      button.disabled = !available;
      button.title = available ? "" : `Keine ${prefix}-Datenbanken im Katalog`;
    });
  }

  function applyDatabaseSearch() {
    const selectedValue = dbSelect.value;
    const found = filterDatabaseNames(allDatabaseNames, databaseGroups, dbSearch.value);
    renderDatabases(found, selectedValue);
    dbSearchStatus.textContent = found.length
      ? `${found.length} von ${allDatabaseNames.length} Datenbanken nach Namen oder Gruppe sichtbar. Die Auswahl bleibt bis zum ausdrücklichen Wechsel erhalten.`
      : "Keine Namenstreffer. Die bisherige Auswahl bleibt erhalten; Suche löschen zeigt alle Datenbanken.";
    updateDbHint();
  }

  initCatalogSuggestions(api, eventBus, (choice) => {
    const entry = catalogEntries.find(item => item.exactId === choice.selector && item.id === choice.catalogId);
    if (!entry || entry.name !== choice.name) throw new Error("Datenbankliste geändert. Bitte Ansicht neu laden.");
    renderDatabases(filterDatabaseNames(allDatabaseNames, databaseGroups, dbSearch.value), choice.selector);
    dbSelect.value = choice.selector;
    dbSelect.dispatchEvent(new Event("change"));
  });

  let focusRevision = 0;
  async function refreshCaseFocus() {
    const revision = ++focusRevision;
    try {
      const current = await api.currentCase();
      if (revision !== focusRevision) return;
      caseFocus = typeof current.focus === "string" && current.focus !== COPYGUARD_REDACTION
        ? current.focus : "";
      dbFocusSearch.disabled = !caseFocus;
      caseFocusHint.textContent = caseFocus
        ? `Fallfokus: ${caseFocus}. Nur nach Katalognamen suchen; keine Änderung der Analysewerte.`
        : "Kein nutzbarer Fallfokus geladen. Die Suche ist eine Namenshilfe und ändert keine Analysewerte.";
    } catch (_) {
      if (revision !== focusRevision) return;
      caseFocus = "";
      dbFocusSearch.disabled = true;
      caseFocusHint.textContent = "Fallfokus derzeit nicht verfügbar. Die manuelle Datenbanksuche bleibt nutzbar.";
    }
  }

  dbSearch.addEventListener("input", applyDatabaseSearch);
  dbSearchClear.addEventListener("click", () => {
    dbSearch.value = "";
    applyDatabaseSearch();
    dbSearch.focus();
  });
  dbFocusSearch.addEventListener("click", () => {
    if (!caseFocus) return;
    dbSearch.value = caseFocus;
    applyDatabaseSearch();
    dbSearch.focus();
  });
  eventBus.addEventListener("case.changed", refreshCaseFocus);
  refreshCaseFocus();

  api.databases().then((data) => {
    catalogEntries = data.catalogs;
    allDatabaseNames = data.databases;
    const candidate = location.port === "8112" || Number(location.port) >= 8110;
    const syntheticOnly = catalogEntries.length > 0 && catalogEntries.every(entry => entry.name.startsWith("SYNTHETIC"));
    document.getElementById("catalog-environment").textContent =
      (candidate ? "Prüfkandidat" : "Lokale Instanz") + " · Port " + location.port + " · " + catalogEntries.length
      + " Datenbanken · " + (syntheticOnly ? "nur synthetischer Prüfkatalog" : data.releaseId ? "verifizierter Katalog " + data.releaseId.slice(0,12) : "lokaler Katalog");
    const restoredDb = selectorFor(savedDb || "");
    renderDatabases(data.databases, savedDb || "");
    const savedOption = savedDb && [...dbSelect.options].some(
      (option) => option.value === restoredDb
    );
    // Original-Standard bevorzugen (wie AetherOnePi: Clarke mit MM-Urls)
    const preferred = [...dbSelect.options].find((option) =>
      entryForSelector(option.value)?.name.startsWith("HOMEOPATHY_Clarke_With_MateriaMedicaUrls")
    );
    if (savedOption) {
      dbSelect.value = restoredDb;
    } else if (preferred) {
      dbSelect.value = preferred.value;
    }
    updateCategoryButtons();
    applyDatabaseSearch();
    updateDbHint();
    if (rates.length) renderResult(); // Kataloglabels auch bei schneller Historienantwort nachziehen.
    catalogsReady = true;
    return Promise.all([syncAutoModeState(), refreshStochasticRecoveryReadiness()]);
  }).catch((error) => {
    gvAutoSummary.textContent = `Auto-Modus-Status nicht verfügbar: ${error.message}`;
  });

  /* ---- Kategorie-Schnellwahl (Aether_4-Buttons = Präfix-Selektoren) ---- */
  categoryButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const prefix = button.dataset.cat;
      dbSearch.value = "";
      applyDatabaseSearch();
      const groupOption = dbSelect.querySelector(
        `option[data-group="true"][value="${prefix}"]`
      );
      if (!groupOption) return;
      dbSelect.value = groupOption.value;
      localStorage.setItem("radiworks_selected_db", dbSelect.value);
      updateDbHint();
      eventBus.dispatchEvent(new Event("analysis.context"));
      form.requestSubmit(); // Kategorie analysiert alle zugehörigen Kinddatenbanken
    });
  });

  modeSelect.addEventListener("change", applyStochasticRecoveryReadiness);
  eventBus.addEventListener("case.changed", refreshStochasticRecoveryReadiness);

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!randomChoice.ready()) { applyStochasticRecoveryReadiness(); return; }
    if(procedureSelect.value==="personal") {
      await personalAnalysis.start({database:dbSelect.value,mode:modeSelect.value||entropyStatus?.defaultMode,seed:seedInput.value.trim()===""?0:Number(seedInput.value),weight:document.getElementById("personal-weight").value});
      return;
    }
    if (gvPageBusy) return;
    if (stochasticRecoveryBlocked()) {
      applyStochasticRecoveryReadiness();
      return;
    }
    setBusy(true);
    analysisRequestStatus.textContent = "Analyse angefordert …";
    let requestPending = true;
    const waitTimer = setTimeout(async () => {
      if (!requestPending) return;
      analysisRequestStatus.textContent = "Die Analyseantwort steht noch aus. Bitte nicht erneut starten; Servererreichbarkeit wird geprüft.";
      const probe = new AbortController();
      const probeTimer = setTimeout(() => probe.abort(), 3000);
      try {
        await api.ping(probe.signal);
        if (requestPending) analysisRequestStatus.textContent = "Server erreichbar; die Analyseantwort steht weiter aus. Bitte nicht erneut starten.";
      } catch {
        if (requestPending) analysisRequestStatus.textContent = "Auch die Serverprobe antwortet nicht. Bitte nicht erneut starten; der Analyseauftrag kann noch laufen.";
      } finally {
        clearTimeout(probeTimer);
      }
    }, 8000);
    const body = { database: dbSelect.value, max_hits: Number(maxHitsSelect.value) };
    if (seedInput.value.trim() !== "") body.seed = Number(seedInput.value);
    if (modeSelect.value !== "") body.mode = modeSelect.value;
    try {
      const run = await api.analysis(body);
      rates = run.result.rateObjects || [];
      lastResultDatabase = body.database;
      lastResultDraftId = run.draft?.id || null;
      const bound = await api.gvRoundState().catch(() => null);
      currentSessionId = bound?.draftId === lastResultDraftId ? bound.sessionId : null;
      gvPageStatus.textContent = "21er-Runde: bereit für die erste Ergebnisseite.";
      page = 1;
      renderResult();
      eventBus.dispatchEvent(new Event("analysis.context"));
      renderDraft(run.draft, run.passport);
      applyGvState({
        generalVitality: run.result.generalVitality,
        totalRuns: 0,
        gv: null,
        result: run.result,
      });
      analysisRequestStatus.textContent = currentSessionId || !window.__RADIWORKS_CASE__
        ? `Analyse abgeschlossen: ${rates.length} Raten im Ergebnis.`
        : `Analyse abgeschlossen: ${rates.length} Raten. Sitzungsstatus nicht bestätigt; vor einer Seitenprüfung den Fall neu laden.`;
      setStickPadSource(null);
    } catch (error) {
      analysisRequestStatus.textContent = `Analyse fehlgeschlagen: ${error.message}`;
    } finally {
      requestPending = false;
      clearTimeout(waitTimer);
      setBusy(false);
    }
  });

  function setBusy(busy) {
    analysisBusy = busy;
    analyzeButton.disabled = busy;
    stickPadFollowupBtn.disabled = busy;
    analyzeButton.textContent = busy ? "Analysiere …" : "Analyse starten";
    if (!busy) applyStochasticRecoveryReadiness();
  }

  /* ---- Ergebnistabelle ---- */
  function recurrenceWords(list) {
    const words = new Map();
    for (const rate of list) {
      const name = (rate.nameOrRate || "").trim();
      const parts = name.includes(" ")
        ? name.split(" ").map((p) => p.replace(/-/g, "").replace(/>/g, "").trim())
        : [name];
      for (const part of parts) {
        if (part.length < 3) continue;
        words.set(part, (words.get(part) || 0) + 1);
      }
    }
    return words;
  }

  function updateStickPadVisibility() {
    stickPadFollowup.hidden = !originalSelected() || !stickPadFollowupSupported || !stickPadSourceSessionId;
  }

  function setStickPadSource(sessionId) {
    stickPadSourceSessionId = sessionId || null;
    updateStickPadVisibility();
  }

  stickPadFollowupBtn.addEventListener("click", async () => {
    if (!originalSelected() || !stickPadSourceSessionId || analysisBusy || gvPageBusy) return;
    if (stochasticRecoveryBlocked()) {
      applyStochasticRecoveryReadiness();
      return;
    }
    setBusy(true);
    analysisRequestStatus.textContent = "Stick-Pad-Treffer werden als neue Sitzung analysiert …";
    const body = {
      source_session_id: stickPadSourceSessionId,
      max_hits: Number(maxHitsSelect.value),
    };
    if (seedInput.value.trim() !== "") body.seed = Number(seedInput.value);
    if (modeSelect.value !== "") body.mode = modeSelect.value;
    try {
      const run = await api.stickPadFollowup(body);
      rates = run.result.rateObjects || [];
      lastResultDatabase = "Stick-Pad-Treffer (Folgeanalyse)";
      lastResultDraftId = run.draft?.id || null;
      const bound = await api.gvRoundState().catch(() => null);
      currentSessionId = bound?.draftId === lastResultDraftId ? bound.sessionId : null;
      page = 1;
      renderResult();
      renderDraft(run.draft, run.passport);
      showSessionNav(true);
      sessionIndicator.dataset.pointer = String(run.sessionIndex);
      sessionIndicator.textContent = `Folgeanalyse (Nr. ${run.sessionIndex})`;
      gvPageStatus.textContent = "21er-Runde: bereit für die erste Ergebnisseite.";
      applyGvState({ generalVitality: run.result.generalVitality, totalRuns: 0, gv: null, result: run.result });
      setStickPadSource(null);
      eventBus.dispatchEvent(new Event("analysis.context"));
      analysisRequestStatus.textContent = `Stick-Pad-Folgeanalyse abgeschlossen: ${rates.length} Raten in neuer Sitzung.`;
    } catch (error) {
      analysisRequestStatus.textContent = `Stick-Pad-Folgeanalyse fehlgeschlagen: ${error.message}`;
    } finally {
      setBusy(false);
    }
  });

  function showCaseGv(value, source) {
    latestCaseGv = Number.isInteger(value) && value > 0 ? value : null;
    gvValue.textContent = latestCaseGv == null ? "—" : String(latestCaseGv);
    gvMeta.textContent = `Letzter Fall-GV: ${latestCaseGv ?? "—"} · Quelle: ${source}`;
    updateRateGvComparison();
  }

  function updateRateGvComparison() {
    const descriptions = {
      higher: ["↑", "über dem zuletzt angezeigten Fall-GV"],
      equal: ["=", "gleich dem zuletzt angezeigten Fall-GV"],
      lower: ["↓", "unter dem zuletzt angezeigten Fall-GV"],
    };
    for (const row of resultBody.querySelectorAll("tr[data-rate-gv]")) {
      const rateGv = Number(row.dataset.rateGv);
      const status = compareRateGv(rateGv, latestCaseGv);
      row.classList.remove("rate-gv-higher", "rate-gv-equal", "rate-gv-lower");
      if (status !== "unset") row.classList.add(`rate-gv-${status}`);
      const cell = row.querySelector("[data-gv-cell]");
      if (!cell) continue;
      const detail = descriptions[status];
      cell.textContent = detail ? `${rateGv} ${detail[0]}` : (rateGv > 0 ? String(rateGv) : "—");
      cell.setAttribute("aria-label", detail
        ? `Raten-GV ${rateGv}, ${detail[1]}`
        : (rateGv > 0 ? `Raten-GV ${rateGv}; kein Fall-GV zum Vergleich` : "Raten-GV noch nicht geprüft"));
      cell.title = detail ? `${rateGv} ${detail[1]}` : "Kein GV-Vergleich verfügbar";
    }
  }

  function renderResult() {
    const pages = Math.max(1, Math.ceil(rates.length / PAGE_SIZE));
    page = Math.min(page, pages);
    gvLaterPageBtn.hidden = page === 1 || rates.length === 0;
    if (!gvPageBusy) gvLaterPageBtn.textContent = `Seite ${page}: Raten-GV prüfen`;
    const start = (page - 1) * PAGE_SIZE;
    const pageRows = rates.slice(start, start + PAGE_SIZE);

    resultEmpty.hidden = rates.length > 0;
    resultWrap.hidden = rates.length === 0;
    resultRecurrenceHint.hidden = rates.length === 0;
    resultGvHint.hidden = rates.length === 0;
    resultCount.textContent = rates.length ? `${rates.length} Raten` : "";
    resultDatabase.textContent = rates.length
      ? `Datenbank des Ergebnisses: ${api.catalogLabel(lastResultDatabase) || "bei dieser gespeicherten Sitzung nicht belegt"}`
      : "Datenbank des Ergebnisses: noch keine Analyse.";
    pager.innerHTML = "";
    if (rates.length > PAGE_SIZE) {
      for (let i = 1; i <= pages; i++) {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "pager-btn" + (i === page ? " active" : "");
        btn.textContent = String(i);
        btn.setAttribute("aria-label", `Seite ${i}`);
        btn.addEventListener("click", () => { page = i; renderResult(); });
        pager.appendChild(btn);
      }
    }

    resultBody.innerHTML = "";
    const words = recurrenceWords(rates);
    const pageTopGv = pageRows.reduce((max, r) => Math.max(max, r.gv || 0), 0);
    let hitMarked = false; // Original: nur EIN Marker (erste Zeile mit höchster GV)

    pageRows.forEach((rate, index) => {
      const tr = document.createElement("tr");
      tr.dataset.rateGv = String(rate.gv || 0);

      // Wortwiederholung hervorheben (Original: roter Schleier)
      const name = (rate.nameOrRate || "").trim();
      const parts = name.includes(" ")
        ? name.split(" ").map((p) => p.replace(/-/g, "").replace(/>/g, "").trim())
        : [name];
      const repeated = parts.some((p) => p.length >= 3 && (words.get(p) || 0) > 1);
      if (repeated) {
        tr.classList.add("row-recurrence");
      }

      const isHit = !hitMarked && (rate.gv || 0) > 0 && (rate.gv || 0) === pageTopGv;
      if (isHit) hitMarked = true;

      const cells = [
        String(start + index),
        String(rate.energeticValue ?? "—"),
        rate.nameOrRate || "—",
        rate.potency || "—",
        rate.level ? `L${rate.level}` : "—",
        isHit ? "▲" : "", // HIT-Marker
        rate.gv ? String(rate.gv) : "—",
        rate.recurringGeneralVitality > 1 ? String(rate.recurringGeneralVitality) : "—",
        rate.recurring > 0 ? String(rate.recurring) : "—",
      ];
      cells.forEach((value, cellIndex) => {
        const td = document.createElement("td");
        if (cellIndex === 6) td.dataset.gvCell = "true";
        if ([1, 4, 5, 6, 7, 8].includes(cellIndex)) td.classList.add("num");
        if (cellIndex === 5 && value) {
          td.classList.add("hit-cell");
          td.title = "Höchste GV dieser Seite (HIT, wie im Original)";
        }
        td.textContent = value;
        if (cellIndex === 2 && repeated) {
          const marker = document.createElement("abbr");
          marker.className = "recurrence-marker";
          marker.textContent = "W";
          marker.title = "Wiederholung in Ratenbezeichnung";
          marker.setAttribute("aria-label", "Wiederholung in Ratenbezeichnung");
          td.appendChild(marker);
        }
        tr.appendChild(td);
      });

      const actionTd = document.createElement("td");
      // CLARKE-Button (Original: nur bei Clarke-Datenbanken)
      if (rate.nameOrRate !== COPYGUARD_REDACTION && api.catalogLabel(lastResultDatabase).toLowerCase().includes("clarke")) {
        const clarke = document.createElement("button");
        clarke.type = "button";
        clarke.className = "mm-link";
        clarke.textContent = "Clarke";
        clarke.title = "Klinischer Symptom-Vergleich (Materia Medica)";
        clarke.addEventListener("click", () => showClarkeCompare(rate.nameOrRate));
        actionTd.appendChild(clarke);
      }
      if (rate.nameOrRate !== COPYGUARD_REDACTION && rate.url && rate.url !== COPYGUARD_REDACTION) {
        const mm = document.createElement("a");
        mm.className = "mm-link";
        mm.href = rate.url;
        mm.target = "_blank";
        mm.rel = "noopener";
        mm.textContent = "MM";
        mm.title = `Materia Medica: ${rate.url}`;
        actionTd.appendChild(mm);
      }
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "btn btn-broadcast";
      btn.textContent = "Broadcast";
      if (rate.nameOrRate === COPYGUARD_REDACTION) {
        btn.disabled = true;
        btn.title = "CopyGuard hält diesen Text zurück";
      }
      btn.addEventListener("click", () => broadcastRate(rate));
      actionTd.appendChild(btn);
      tr.appendChild(actionTd);
      resultBody.appendChild(tr);
    });
    updateRateGvComparison();
  }

  /* ---- CLARKE-Vergleich (Aether_4-Button) ---- */
  async function showClarkeCompare(rateName) {
    try {
      const data = await api.clarkeCompare(rateName);
      const dialog = document.getElementById("clarke-dialog");
      const content = document.getElementById("clarke-content");
      content.replaceChildren();

      const heading = document.createElement("h3");
      heading.textContent = `== ${data.rate} ==`;
      content.appendChild(heading);

      const clinical = document.createElement("p");
      const clinicalLabel = document.createElement("strong");
      clinicalLabel.textContent = `Klinische Symptome (${data.clinical.length}): `;
      clinical.appendChild(clinicalLabel);
      for (const symptom of data.clinical.slice(0, 40)) {
        const badge = document.createElement("span");
        badge.className = "badge";
        badge.textContent = symptom;
        clinical.append(badge, " ");
      }
      content.appendChild(clinical);

      const sharedLabel = document.createElement("p");
      sharedLabel.textContent = "Gemeinsame Symptome mit anderen Analyse-Raten:";
      content.appendChild(sharedLabel);
      const sharedList = document.createElement("ul");
      for (const entry of data.sharedCounts) {
        const item = document.createElement("li");
        item.textContent = `${entry.count} — ${entry.symptom}`;
        sharedList.appendChild(item);
      }
      content.appendChild(sharedList);

      for (const [remedy, info] of Object.entries(data.others)) {
        const comparison = document.createElement("p");
        const label = document.createElement("strong");
        label.textContent = remedy;
        comparison.append(label, ` — teilt: ${info.shared.slice(0, 8).join(", ")}`);
        content.appendChild(comparison);
      }
      dialog.showModal();
    } catch (error) {
      alert(`Clarke-Vergleich: ${error.message}`);
    }
  }

  async function broadcastRate(rate) {
    const signature = `${rate.nameOrRate} ${rate.energeticValue ?? ""} ${rate.potency ?? ""}`.trim();
    // Original performClickEvent: SEKUNDEN = GV der Rate (sonst 60)
    const seconds = rate.gv && rate.gv > 0 ? rate.gv : 60;
    try {
      await api.broadcast({ signature, seconds, multiplier: 1, ...analysisJobOrigin(lastResultDraftId, currentSessionId) });
      document.querySelector('.tab[data-tab="broadcast"]').click();
    } catch (error) {
      alert(`Broadcast abgelehnt: ${error.message}`);
    }
  }

  /* ---- Draft (D18-Zweiklick) ---- */
  function renderDraft(draft, passport) {
    draftEmpty.hidden = true;
    draftBody.hidden = false;
    const promotionState = draft.promotion?.state;
    draftStatus.textContent = promotionState === "interrupted"
      ? `${draft.status} · Freigabe unterbrochen`
      : draft.status;
    draftCopyguard.textContent = `${draft.copyguard_verdict} · ${draft.copyguard_digest.slice(0, 10)}…`;
    draftKernel.textContent = `${passport.kernel} ${passport.kernel_version}`;
    readyBtn.disabled = draft.status !== "draft";
    promoteBtn.disabled = draft.status !== "ready" ||
      Boolean(promotionState && promotionState !== "failed");
    if (promotionState === "interrupted") {
      draftHint.textContent = `Freigabeauftrag ${draft.promotion.id} wurde unterbrochen. Keine automatische Wiederholung; bitte vor einem neuen Auftrag prüfen.`;
    } else if (promotionState === "failed") {
      draftHint.textContent = "Einreihung fehlgeschlagen; der Prüfentwurf bleibt bereit. Erneutes Freigeben ist eine neue bewusste Aktion.";
    } else if (draft.status === "draft") {
      draftHint.textContent = "Schritt 1 von 2: Ergebnis prüfen und bestätigen. CopyGuard sperrt die Freigabe bei unzulässigen Formulierungen oder fehlender Prüfung.";
    } else if (draft.status === "ready") {
      draftHint.textContent = "Schritt 2 von 2: Bewusst für den virtuellen Broadcast freigeben — erst danach werden Aufträge eingereiht.";
    } else {
      draftHint.textContent = `Status: ${draft.status}`;
    }
  }

  readyBtn.addEventListener("click", async () => {
    if (!originalSelected()) return;
    try {
      const draft = await api.draftTransition(currentDraftId(), "ready");
      renderDraft(draft, { kernel: draft.source_kernel, kernel_version: draft.source_kernel_version });
    } catch (error) {
      alert(`Übergang abgelehnt: ${error.message}`);
    }
  });

  promoteBtn.addEventListener("click", async () => {
    if (!originalSelected()) return;
    try {
      // Original „BROADCAST MIX“ übernimmt den MULTIPLIER der UI — hier ebenso.
      const multiplier = Number(document.getElementById("mul-input").value) || 1;
      const result = await api.draftPromote(currentDraftId(), {
        max_rates: 5,
        seconds_per_rate: 60,
        multiplier,
      });
      const updated = await api.draft(currentDraftId());
      renderDraft(updated, { kernel: updated.source_kernel, kernel_version: updated.source_kernel_version });
      draftHint.textContent =
        `Freigegeben — ${result.broadcastEntries.length} Raten (Multiplikator ${multiplier}) in der Broadcast-Queue.`;
      document.querySelector('.tab[data-tab="broadcast"]').click();
    } catch (error) {
      try {
        const updated = await api.draft(currentDraftId());
        renderDraft(updated, { kernel: updated.source_kernel, kernel_version: updated.source_kernel_version });
      } catch (refreshError) {
        draftHint.textContent = `Freigabestatus nicht abrufbar: ${refreshError.message}`;
      }
      alert(`Freigabe blockiert: ${error.message}`);
    }
  });

  let activeDraftId = null;
  const _origRenderDraft = renderDraft;
  renderDraft = function (draft, passport) {
    activeDraftId = draft.id;
    draftBody.dataset.draftId = draft.id;
    _origRenderDraft(draft, passport);
  };
  function currentDraftId() { return activeDraftId; }

  async function syncDraftForSession(draftId) {
    if (!draftId) {
      activeDraftId = null;
      delete draftBody.dataset.draftId;
      draftBody.hidden = true;
      draftEmpty.hidden = false;
      draftEmpty.textContent = "Für diese Sitzung liegt kein Prüfentwurf vor.";
      return;
    }
    if (activeDraftId === draftId) return;
    try {
      const draft = await api.draft(draftId);
      if (lastResultDraftId === draftId) {
        renderDraft(draft, { kernel: draft.source_kernel, kernel_version: draft.source_kernel_version });
      }
    } catch (error) {
      if (lastResultDraftId === draftId) {
        activeDraftId = null;
        delete draftBody.dataset.draftId;
        draftBody.hidden = true;
        draftEmpty.hidden = false;
        draftEmpty.textContent = `Prüfentwurf dieser Sitzung nicht abrufbar: ${error.message}`;
      }
      throw error;
    }
  }

  api.drafts().then(({ drafts }) => {
    if (activeDraftId || lastResultDraftId) return;
    const interrupted = drafts
      .filter((draft) => draft.promotion?.state === "interrupted")
      .sort((a, b) => b.updated.localeCompare(a.updated))[0];
    if (interrupted) {
      renderDraft(interrupted, {
        kernel: interrupted.source_kernel,
        kernel_version: interrupted.source_kernel_version,
      });
    }
  }).catch((error) => {
    draftEmpty.textContent = `Freigabestatus nicht abrufbar: ${error.message}`;
  });

  /* ---- GV-Runde + runs + Graph + Auto-Modus ---- */
  function applyGvState(state) {
    if (Object.hasOwn(state, "draftId")) {
      lastResultDraftId = state.draftId;
      if (activeDraftId !== lastResultDraftId) {
        void syncDraftForSession(lastResultDraftId).catch(() => {});
      }
    }
    if (state.sessionId) currentSessionId = state.sessionId;
    if (state.result) {
      rates = state.result.rateObjects || rates;
      gvAnalysisTrials.textContent = analysisTrialLabel(state.result);
    }
    if (state.totalRuns != null) gvManualSteps.textContent = `Manuelle GV-Züge dieser Runde: ${state.totalRuns}`;
    if (state.gv != null && state.rateIndex == null) {
      showCaseGv(state.generalVitality, "manuelle GV-Runde");
    } else if (!autoEnabled && state.gv == null) {
      showCaseGv(state.generalVitality, "gespeicherte Analyse");
    }
    if (state.gv != null) {
      gvSeries.push(state.gv);
      if (gvSeries.length > 140) gvSeries.shift();
      drawGraph();
      eventBus.dispatchEvent(new CustomEvent("gv.value", { detail: { gv: state.gv, runs: state.totalRuns, source: "manual" } }));
    }
    if (state.result) {
      renderResult();
    }
  }

  function drawGraph() {
    drawSeries(graph, gvSeries);
  }

  gvBtn.addEventListener("click", async () => {
    if (!originalSelected() || gvPageBusy) return;
    try {
      // Kein Seed: die GV-Runde setzt den Entropiestrom der Analyse fort
      // (Original: weitere Züge aus demselben Hotbits-Cache).
      applyGvState(await api.gvRound({}));
    } catch (error) {
      alert(`GV-Runde: ${error.message}`);
    }
  });

  /* ---- Auto-Modus = serverseitiger Harmonisierungsregler (Original
     handleAutoMode): bei leerer Pending-Queue und GV <= 300 analysiert und
     sendet die Engine selbstständig (10-1000 s, UI-Multiplikator).
     Der Browser startet nur — die Uhr läuft im Server (Hard Rule 4). ---- */
  function applyAutoModeState(state) {
    const enabled = state?.enabled === true;
    autoEnabled = enabled;
    autoOnBtn.classList.toggle("btn-primary", enabled);
    autoOffBtn.classList.toggle("btn-primary", !enabled);

    if (originalSelected() && enabled && state?.database && [...dbSelect.options].some((o) => o.value === selectorFor(state.database))) {
      dbSelect.value = selectorFor(state.database);
      updateDbHint();
    }
    if (enabled && Number.isInteger(state?.multiplier)) {
      multiplierInput.value = String(state.multiplier);
    }
    if (enabled && state?.caseGv > 0) showCaseGv(state.caseGv, "Auto-Modus, letzter Zug");

    const runs = state?.runs ?? 0;
    const average = state?.average;
    if (enabled) autoSafetyError = null;
    if (!enabled && autoSafetyError) {
      gvAutoSummary.textContent = autoSafetyError;
    } else if (enabled) {
      gvAutoSummary.textContent = `Auto-Modus: AN · letzter Zug ${state.caseGv || "—"} · Ø letzte ${Math.min(runs, 10)} Züge: ${average ?? "—"} · Auto-Züge: ${runs}`;
    } else if (runs > 0) {
      gvAutoSummary.textContent = `Auto-Modus: AUS · letzter Zug ${state.caseGv || "—"} · Ø: ${average ?? "—"} · Auto-Züge: ${runs}`;
    } else {
      gvAutoSummary.textContent = "Auto-Modus: AUS · noch keine Auto-GV-Züge.";
    }
  }

  function applyAutoModeUpdate(state) {
    autoStateRevision += 1;
    applyAutoModeState(state);
  }

  async function autoRequest(request, timeoutMs, timeoutMessage) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);
    try {
      return await request(controller.signal);
    } catch (error) {
      if (controller.signal.aborted) throw new Error(timeoutMessage);
      throw error;
    } finally {
      clearTimeout(timer);
    }
  }

  async function runAutoModeCommand(request) {
    const command = ++autoCommandRequest;
    autoSyncRequest += 1; // laufende GET-Snapshots sind ab jetzt veraltet
    const revision = autoStateRevision;
    const pending = autoRequest(
      request,
      AUTO_COMMAND_TIMEOUT_MS,
      "Auto-Modus-Kommando hat das Zeitlimit überschritten",
    );
    autoCommandsInFlight.set(pending, command);
    try {
      const state = await pending;
      if (command === autoCommandRequest && revision === autoStateRevision) {
        applyAutoModeUpdate(state);
      }
      return state;
    } finally {
      autoCommandsInFlight.delete(pending);
    }
  }

  async function syncAutoModeState() {
    const request = ++autoSyncRequest;
    const revision = autoStateRevision;
    const state = await autoRequest(
      (signal) => api.autoMode(signal),
      AUTO_SYNC_TIMEOUT_MS,
      "Auto-Modus-Statusabgleich hat das Zeitlimit überschritten",
    );
    if (request === autoSyncRequest && revision === autoStateRevision) {
      applyAutoModeUpdate(state);
    }
    return state;
  }

  async function reconcileAutoModeState() {
    const reconciliationCommand = autoCommandRequest;
    const deadline = Date.now() + AUTO_RECONCILE_WAIT_MS;
    while (autoCommandsInFlight.size > 0 && Date.now() < deadline) {
      const remaining = deadline - Date.now();
      let waitTimer;
      await Promise.race([
        Promise.allSettled([...autoCommandsInFlight.keys()]),
        new Promise((resolve) => { waitTimer = setTimeout(resolve, remaining); }),
      ]);
      clearTimeout(waitTimer);
      await Promise.resolve();
    }
    if (reconciliationCommand !== autoCommandRequest) return null;
    return syncAutoModeState();
  }

  function latestAutoCommandIsRunning() {
    return [...autoCommandsInFlight.values()].some(
      (command) => command === autoCommandRequest
    );
  }

  setInterval(() => {
    if (document.hidden || latestAutoCommandIsRunning()) return;
    syncAutoModeState().catch(() => {});
  }, AUTO_STATE_POLL_MS);
  document.addEventListener("visibilitychange", () => {
    if (!document.hidden && !latestAutoCommandIsRunning()) syncAutoModeState().catch(() => {});
  });

  autoOnBtn.addEventListener("click", async () => {
    if (!originalSelected()) return;
    try {
      const multiplier = Number(multiplierInput.value) || 1;
      await runAutoModeCommand(
        (signal) => api.autoModeOn(dbSelect.value, multiplier, signal)
      );
    } catch (error) {
      await reconcileAutoModeState().catch(() => {});
      alert(`Auto-Modus: ${error.message}`);
    }
  });
  autoOffBtn.addEventListener("click", async () => {
    try {
      await runAutoModeCommand((signal) => api.autoModeOff(signal));
    } catch (error) {
      await reconcileAutoModeState().catch(() => {});
      alert(`Auto-Modus konnte nicht ausgeschaltet werden: ${error.message}`);
    }
  });

  eventBus.addEventListener("auto.mode", (event) => {
    applyAutoModeUpdate(event.detail);
  });
  eventBus.addEventListener("auto.error", (event) => {
    const phase = event.detail?.phase ? ` (${event.detail.phase})` : "";
    const message = event.detail?.message || "Unbekannter Fehler";
    const text = `AUTO MODE — Fehler${phase}: ${message}`;
    if (event.detail?.phase === "copyguard") autoSafetyError = text;
    gvAutoSummary.textContent = text;
  });
  eventBus.addEventListener("server.replay_gap", () => {
    autoStateRevision += 1;
    syncAutoModeState().catch(() => {
      gvAutoSummary.textContent = "AUTO MODE — Status nach Replay-Lücke nicht verfügbar";
    });
  });
  eventBus.addEventListener("server.restarted", () => {
    autoSafetyError = null;
    autoStateRevision += 1;
    syncAutoModeState().catch(() => {
      gvAutoSummary.textContent = "AUTO MODE — Status nach Engine-Neustart nicht verfügbar";
    });
  });

  // Serverseitige GV-Züge des Auto-Modus in Graph und Statusleiste übernehmen
  eventBus.addEventListener("gv.update", (event) => {
    const { gv, runs, average } = event.detail;
    if (gv != null) {
      autoStateRevision += 1;
      gvSeries.push(gv);
      if (gvSeries.length > 140) gvSeries.shift();
      drawGraph();
      showCaseGv(gv, "Auto-Modus, letzter Zug");
      gvAutoSummary.textContent = `Auto-Modus: AN · letzter Zug ${gv} · Ø letzte ${Math.min(runs, 10)} Züge: ${average ?? "—"} · Auto-Züge: ${runs}`;
      eventBus.dispatchEvent(new CustomEvent("gv.value", { detail: { gv, runs, source: "auto" } }));
    }
  });

  /* ---- Datenbank-Anzeige (Aether_4: „SELECTED DATABASE: …") ---- */
  const dbHint = document.getElementById("selected-db-hint");
  function updateDbHint() {
    const selected = dbSelect.selectedOptions[0];
    if (!selected) {
      dbHint.textContent = "Keine Datenbank gewählt.";
    } else if (selected.dataset.group === "true") {
      dbHint.textContent = `Gewählte Gruppe: ${selected.textContent}`;
    } else {
      dbHint.textContent = "Gewählte Datenbank: " + selected.textContent;
    }
  }
  dbSelect.addEventListener("change", () => {
    localStorage.setItem("radiworks_selected_db", dbSelect.value);
    updateDbHint();
    eventBus.dispatchEvent(new Event("analysis.context"));
  });

  gvPageBtn.addEventListener("click", async () => {
    if (!originalSelected() || gvPageBusy) return;
    if (!lastResultDraftId || rates.length === 0) {
      gvPageStatus.textContent = "Bitte zuerst eine neue Analyse ausführen.";
      return;
    }
    gvPageBusy = true;
    gvPageBtn.disabled = true;
    gvBtn.disabled = true;
    analyzeButton.disabled = true;
    try {
      const state = await api.gvRoundState();
      if (!state.active || state.draftId !== lastResultDraftId) {
        throw new Error("Die Analyse hat sich geändert. Bitte neu analysieren.");
      }
      if (state.pageStart !== 0) {
        throw new Error("Diese Sitzung prüft eine spätere Seite. Für die erste Seite die frühere Sitzung laden.");
      }
      const target = Math.min(PAGE_SIZE, rates.length) + 1; // Fall-GV plus erste 21 Raten.
      if (state.counter > target) {
        throw new Error("Der GV-Zähler liegt außerhalb der erwarteten Ergebnisseite.");
      }
      page = 1;
      renderResult();
      let startCounter = state.counter;
      if (startCounter === target) {
        if (state.supportsBoundSuccessor !== true) {
          throw new Error("Der laufende Server unterstützt die sichere Wiederholung noch nicht. Bitte den kontrollierten Neustart abwarten.");
        }
        gvPageStatus.textContent = "21er-Runde: neue Fallsitzung wird ohne Entropiezug angelegt …";
        const boundary = await api.gvRound({
          expected_draft_id: lastResultDraftId,
          expected_counter: startCounter,
        });
        if (!boundary.roundBoundary || boundary.counter !== 0 || !boundary.draftId ||
            (boundary.sessionId && boundary.draftId === lastResultDraftId)) {
          throw new Error("Die neue GV-Runde wurde nicht eindeutig gebunden; aktuellen Stand prüfen.");
        }
        applyGvState(boundary);
        startCounter = 0;
      }
      for (let counter = startCounter; counter < target; counter++) {
        gvPageStatus.textContent = counter === 0
          ? "21er-Runde: Fall-GV wird geprüft …"
          : `21er-Runde: Rate ${counter} von ${target - 1} …`;
        const step = await api.gvRound({
          expected_draft_id: lastResultDraftId,
          expected_counter: counter,
        });
        if (step.roundBoundary || step.counter !== counter + 1) {
          throw new Error("Die GV-Runde wurde unterbrochen; aktuellen Stand prüfen.");
        }
        applyGvState(step);
      }
      gvPageStatus.textContent = `21er-Runde abgeschlossen: ${target - 1} Raten-GV der ersten Seite. Die GV-Runde hat keinen Broadcast gestartet; sie kann erneut ausgeführt werden.`;
    } catch (error) {
      gvPageStatus.textContent = `21er-Runde gestoppt: ${error.message} Bereits gespeicherte Werte bleiben erhalten.`;
    } finally {
      gvPageBusy = false;
      gvPageBtn.disabled = false;
      gvBtn.disabled = false;
      applyStochasticRecoveryReadiness();
    }
  });

  gvLaterPageBtn.addEventListener("click", async () => {
    if (!originalSelected() || gvPageBusy || page < 2 || !rates.length) return;
    const selectedPage = page;
    const pageStart = (selectedPage - 1) * PAGE_SIZE;
    const pageLength = Math.min(PAGE_SIZE, rates.length - pageStart);
    if (!lastResultDraftId || !currentSessionId || pageLength < 1) {
      gvPageStatus.textContent = "Bitte zuerst eine gespeicherte Analyse-Sitzung laden.";
      return;
    }
    gvPageBusy = true;
    gvLaterPageBtn.disabled = true;
    gvPageBtn.disabled = true;
    gvBtn.disabled = true;
    analyzeButton.disabled = true;
    try {
      const state = await api.gvRoundState();
      if (!state.active || state.draftId !== lastResultDraftId || state.sessionId !== currentSessionId) {
        throw new Error("Analyse oder Sitzung hat sich geändert. Bitte die aktuelle Sitzung neu laden.");
      }
      const target = pageLength + 1; // Fall-GV und nur die Raten der gewählten Seite.
      let counter = state.counter;
      if (state.pageStart !== pageStart || counter >= target) {
        gvPageStatus.textContent = `Seite ${selectedPage}: neue vollständige Sitzung wird angelegt …`;
        const child = await api.gvPageStart({
          page: selectedPage,
          expected_draft_id: lastResultDraftId,
          expected_session_id: currentSessionId,
        });
        if (!child.sessionId || !child.draftId || child.sessionId === currentSessionId ||
            child.pageStart !== pageStart || child.counter !== 0) {
          throw new Error("Neue Seitensitzung nicht eindeutig bestätigt; Stand prüfen.");
        }
        applyGvState(child);
        showSessionNav(true);
        sessionIndicator.dataset.pointer = String(child.sessionIndex);
        sessionIndicator.textContent = `Seite ${selectedPage} · neue Sitzung (Nr. ${child.sessionIndex})`;
        const draft = await api.draft(child.draftId);
        renderDraft(draft, { kernel: draft.source_kernel, kernel_version: draft.source_kernel_version });
        counter = 0;
      } else if (activeDraftId !== lastResultDraftId) {
        const draft = await api.draft(lastResultDraftId);
        renderDraft(draft, { kernel: draft.source_kernel, kernel_version: draft.source_kernel_version });
      }
      for (; counter < target; counter++) {
        gvPageStatus.textContent = counter === 0
          ? `Seite ${selectedPage}: Fall-GV wird geprüft …`
          : `Seite ${selectedPage}: Rate ${counter} von ${pageLength} …`;
        const step = await api.gvRound({
          expected_draft_id: lastResultDraftId,
          expected_counter: counter,
        });
        if (step.roundBoundary || step.counter !== counter + 1 || step.pageStart !== pageStart) {
          throw new Error("Die Seitenprüfung wurde unterbrochen; aktuellen Stand prüfen.");
        }
        applyGvState(step);
      }
      gvPageStatus.textContent = `Seite ${selectedPage} abgeschlossen: ${pageLength} Raten-GV in einer neuen vollständigen Sitzung. Die vorige Sitzung bleibt erhalten.`;
    } catch (error) {
      gvPageStatus.textContent = `Seitenprüfung gestoppt: ${error.message} Bereits gespeicherte Werte bleiben erhalten.`;
    } finally {
      gvPageBusy = false;
      gvLaterPageBtn.disabled = false;
      gvPageBtn.disabled = false;
      gvBtn.disabled = false;
      applyStochasticRecoveryReadiness();
      renderResult();
    }
  });

  /* ---- Grounding / Clear / Training (Aether_4-Aktionsleiste) ---- */
  document.getElementById("grounding-btn").addEventListener("click", async () => {
    try {
      await api.broadcast({ signature: "GROUNDING TO THE EARTH CORE", seconds: 10, multiplier: 1 });
      eventBus.dispatchEvent(new CustomEvent("grounding.start", { detail: {} }));
    } catch (error) {
      alert(`Grounding abgelehnt: ${error.message}`);
    }
  });

  document.getElementById("clear-btn").addEventListener("click", () => {
    const flash = document.getElementById("uv-flash");
    flash.hidden = false;
    flash.classList.add("uv-active");
    eventBus.dispatchEvent(new CustomEvent("clear.flash", { detail: {} }));
    setTimeout(() => {
      flash.hidden = true;
      flash.classList.remove("uv-active");
    }, 1300); // Original: 70 Frames (~1,2 s bei 60 fps)
  });

  const trainingBar = document.getElementById("training-bar");
  const trainingSignature = document.getElementById("training-signature");
  document.getElementById("training-start-btn").addEventListener("click", async () => {
    try {
      await api.trainingStart(dbSelect.value);
      trainingBar.hidden = false;
      trainingSignature.textContent = "████████ (verdeckt)";
    } catch (error) {
      alert(`Training-Start: ${error.message}`);
    }
  });
  document.getElementById("training-uncover-btn").addEventListener("click", async () => {
    try {
      const data = await api.trainingUncover();
      trainingBar.hidden = false;
      trainingSignature.textContent = `Signatur: ${data.signature}`;
    } catch (error) {
      alert(`Training-Uncover: ${error.message}`);
    }
  });

  /* ---- Zwischenablage (Original: CLIPBOARD, solo-Modus) ---- */
  document.getElementById("clipboard-btn").addEventListener("click", async () => {
    if (!originalSelected()) return;
    const copy = {
      generalVitality: null,
      rateObjects: rates.slice(0, 21).map((r) => ({ ...r.to_dict ? r.to_dict() : r, url: "" })),
    };
    copy.generalVitality = Number(gvValue.textContent) || null;
    const prompt =
      `Bitte interpretiere dieses Radionik-Ergebnis (JSON, AetherOnePi-Ratenkatalog '${api.catalogLabel(lastResultDatabase) || "unbekannt"}').\n` +
      "Vermeide typische Detox-Floskeln der Radionik-Szene.\n" +
      "Gib Einblick in die einzelnen Raten: erkennst du gemeinsame Muster, " +
      "eine Familie oder Gruppe von Raten, ein Miasm, eine Mineralien- oder Pflanzengruppe?\n\n" +
      JSON.stringify(copy, null, 2);
    try {
      await navigator.clipboard.writeText(prompt);
      eqReport.hidden = false;
      eqReport.textContent = "Analyse (Top 21) + Interpretationsprompt in die Zwischenablage kopiert.\n" +
        "Hinweis: In Aurelia läuft die Deutung später über das lokale LLM (CopyGuard, im RAM) — kein Cloud-Aufruf.";
    } catch (error) {
      alert(`Zwischenablage nicht verfügbar: ${error.message}`);
    }
  });

  /* ---- Session-Navigation (Original: ←/→ über analysisPointer) ---- */
  const sessionNav = document.getElementById("session-nav");
  const sessionPrev = document.getElementById("session-prev");
  const sessionNext = document.getElementById("session-next");
  const sessionIndicator = document.getElementById("session-indicator");

  sessionPrev.addEventListener("click", () => stepSession(-1));
  sessionNext.addEventListener("click", () => stepSession(1));

  function showSessionNav(visible) {
    sessionNav.hidden = !visible;
  }

  async function stepSession(direction) {
    if (!originalSelected()) return;
    try {
      const data = await api.sessions();
      const usable = data.sessions.filter((s) => s.hasResult);
      if (!usable.length) {
        sessionIndicator.textContent = "Session —/—";
        return;
      }
      showSessionNav(true);
      const raw = sessionIndicator.dataset.pointer;
      let pointer;
      if (raw === undefined || raw === null || raw === "") {
        pointer = direction > 0 ? usable[usable.length - 1].index : usable[0].index;
      } else {
        const currentIndex = usable.findIndex((s) => s.index === Number(raw));
        const nextPos = Math.max(0, Math.min(usable.length - 1, (currentIndex === -1 ? 0 : currentIndex) + direction));
        pointer = usable[nextPos].index;
      }
      const viewed = await api.viewSession(pointer);
      setStickPadSource(viewed.sourceKind === "stickpad" ? viewed.sessionId : null);
      lastResultDatabase = null;
      currentSessionId = viewed.sessionId || null;
      lastResultDraftId = viewed.draftId || null;
      gvPageStatus.textContent = "Gespeicherte Sitzung geladen. Für Seite 2 und folgende die gewünschte Ergebnisseite auswählen und dort die Raten-GV ausdrücklich starten.";
      sessionIndicator.dataset.pointer = String(pointer);
      const position = usable.findIndex((s) => s.index === pointer) + 1;
      sessionIndicator.textContent = `Session ${position}/${usable.length} (Nr. ${pointer})`;
      applyGvState({
        draftId: viewed.draftId,
        generalVitality: viewed.result.generalVitality,
        totalRuns: viewed.state.totalRuns,
        gv: null,
        result: viewed.result,
      });
    } catch (error) {
      alert(`Session-Navigation: ${error.message}`);
    }
  }

  /* Fall geladen → letzte Analyse anzeigen (Fälle-Tab → Analyse-Tab) */
  eventBus.addEventListener("analysis.external", (event) => {
    const { result, state } = event.detail;
    setStickPadSource(state.sourceKind === "stickpad" ? state.sessionId : null);
    lastResultDatabase = null;
    currentSessionId = state.sessionId || null;
    lastResultDraftId = state.draftId || null;
    gvPageStatus.textContent = "Gespeicherte Sitzung geladen. Weitere Ergebnisseiten können ausdrücklich geprüft werden.";
    showSessionNav(true);
    sessionIndicator.dataset.pointer = String(state.pointer ?? "");
    sessionIndicator.textContent = state.label || `Session (Nr. ${state.pointer})`;
    applyGvState({
      draftId: state.draftId,
      generalVitality: result.generalVitality,
      totalRuns: state.totalRuns,
      gv: null,
      result,
    });
  });
  eventBus.addEventListener("stickpad.analysis", (event) => {
    const data = event.detail;
    setStickPadSource(data.sessionLinked ? data.sessionId : null);
    lastResultDatabase = data.database || null;
    lastResultDraftId = data.draft?.id || null;
    currentSessionId = data.sessionId || null;
    gvPageStatus.textContent = "21er-Runde: Stick-Pad-Ergebnis geladen; nur nach neuer Standardanalyse verfügbar.";
    renderDraft(data.draft, data.passport);
    showSessionNav(data.sessionLinked);
    sessionIndicator.dataset.pointer = data.sessionLinked ? String(data.sessionIndex) : "";
    sessionIndicator.textContent = data.sessionLinked
      ? `Stick-Pad-Session (Nr. ${data.sessionIndex})`
      : "Keine Fallsitzung";
    applyGvState({
      generalVitality: data.result.generalVitality,
      totalRuns: 0,
      gv: null,
      result: data.result,
    });
  });
  eventBus.addEventListener("gv.external", (event) => applyGvState(event.detail));

  /* ---- Fall bearbeiten (Aether_2 „EDIT CASE") ---- */
  const editDialog = document.getElementById("edit-dialog");
  let editCaseRef = null;
  let editContextVersion = null;
  let editCaseName = null;
  let editHasSession = false;
  document.getElementById("edit-case-btn").addEventListener("click", async () => {
    try {
      const bound = await api.currentCaseWithRef();
      const current = bound.data;
      if (!current?.name || !bound.ref) throw new Error("Kein Fall geladen.");
      editCaseRef = bound.ref;
      editContextVersion = current.contextVersion ?? null;
      editCaseName = current.name;
      document.getElementById("edit-name").value = current.name;
      document.getElementById("edit-desc").value = current.description || "";
      document.getElementById("edit-focus").value = current.focus || "";
      const sessions = current.sessionList || [];
      editHasSession = sessions.length > 0;
      document.getElementById("edit-intention").value =
        editHasSession ? sessions[sessions.length - 1].intention || "" : "";
      editDialog.showModal();
    } catch (error) {
      alert(`Fall konnte nicht geöffnet werden: ${error.message}`);
    }
  });
  document.getElementById("edit-cancel-btn").addEventListener("click", () => editDialog.close());
  document.getElementById("edit-save-btn").addEventListener("click", async () => {
    try {
      if (!editCaseRef) throw new Error("Bitte Fall erneut öffnen.");
      const metadata = {
        name: document.getElementById("edit-name").value.trim() || editCaseName,
        description: document.getElementById("edit-desc").value.trim() || null,
        focus: document.getElementById("edit-focus").value.trim() || null,
        expected_case_ref: editCaseRef,
        expected_context_version: editContextVersion,
      };
      if (editHasSession) {
        metadata.intention = document.getElementById("edit-intention").value.trim() || null;
      }
      const saved = await api.saveCurrentCaseMetadata(metadata);
      editCaseRef = null;
      editContextVersion = null;
      eventBus.dispatchEvent(new CustomEvent("case.changed", {
        detail: { name: saved.data.name, savedCase: saved.data, ref: saved.ref },
      }));
      editDialog.close();
    } catch (error) {
      alert(`Fall konnte nicht gespeichert werden: ${error.message}`);
    }
  });

  /* ---- Tastatur wie im Original (AetherOneEventHandler.keyPressed):
     ENTER = GV-Zug · STRG = Analyse der gewählten Liste sofort starten ·
     ←/→ = Session-Historie. Nur im ANALYZE-Tab und außerhalb von Feldern. */
  document.addEventListener("keydown", (event) => {
    if (document.getElementById("view-analyse").hidden) return;
    if (event.defaultPrevented || document.querySelector("dialog[open]")) return;
    const target = event.target;
    if (target instanceof Element && target.closest(
      "button, a, input, textarea, select, summary, [role='button'], [role='tab'], [contenteditable]"
    )) return;

    if (event.key === "Enter") {
      event.preventDefault();
      gvBtn.click(); // checkGeneralVitality (keyCode '\n')
    } else if (event.ctrlKey && event.key === "Control") {
      // keyCode 17 (Control losgelassen) im Original → analyzeCurrentDatabase:
      // die SOFORT neu gewählte Dateiliste wird geladen.
      const onUp = (upEvent) => {
        if (upEvent.key === "Control") {
          upEvent.preventDefault();
          form.requestSubmit();
          window.removeEventListener("keyup", onUp);
        }
      };
      window.addEventListener("keyup", onUp);
    } else if (event.key === "ArrowLeft" || event.key === "ArrowRight") {
      event.preventDefault();
      stepSession(event.key === "ArrowLeft" ? -1 : 1);
    }
  });

  /* STRG im BROADCAST-Tab: Signatur aus der Zwischenablage (Original). */
  document.addEventListener("keyup", (event) => {
    if (event.key !== "Control") return;
    if (document.getElementById("view-broadcast").hidden) return;
    const target = event.target;
    if (target && ["INPUT", "TEXTAREA", "SELECT"].includes(target.tagName)) return;
    navigator.clipboard.readText().then((text) => {
      if (!text) return;
      document.getElementById("sig-input").value = text.trim();
      document.getElementById("sec-input").value = "60";
    }).catch(() => { /* Clipboard-Recht verweigert */ });
  });

  /* ---- Essenzielle Fragen ---- */
  eqBtn.addEventListener("click", async () => {
    if (!originalSelected()) return;
    eqBtn.disabled = true;
    try {
      const body = {};
      if (seedInput.value.trim() !== "") body.seed = Number(seedInput.value);
      if (modeSelect.value !== "") body.mode = modeSelect.value;
      const data = await api.essentialQuestions(body);
      eqReport.hidden = false;
      eqReport.textContent = data.report;
    } catch (error) {
      eqReport.hidden = false;
      eqReport.textContent = `Fehler: ${error.message}`;
    } finally {
      eqBtn.disabled = false;
    }
  });
}

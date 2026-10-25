/* Analyse-View im Original-Layout (Aether_4):
   Spalten Nr/EW/Rate/Potenz/Lvl/HIT/GV/GV-RE/REC, Pagination à 21,
   HIT = höchste GV der Seite (Marker), Wortwiederholungs-Hervorhebung,
   Zeilen-Broadcast + Materia-Medica-Link, GV-Runde mit runs-Zähler +
   Graph, Auto-Modus, Essenzielle Fragen, Grounding/Clear/Training. */

import { drawSeries } from "./gvgraph.js";

const PAGE_SIZE = 21; // wie im Original (AnalyseScreen, startIndex = (page-1)*21)

export function initAnalyzeView(api, eventBus) {
  const dbSelect = document.getElementById("db-select");
  const seedInput = document.getElementById("seed-input");
  const modeSelect = document.getElementById("mode-select");
  const maxHitsSelect = document.getElementById("maxhits-select");
  const form = document.getElementById("analyze-form");

  const gvValue = document.getElementById("gv-value");
  const gvMeta = document.getElementById("gv-meta");
  const gvBtn = document.getElementById("gv-btn");
  const autoOnBtn = document.getElementById("auto-on-btn");
  const autoOffBtn = document.getElementById("auto-off-btn");
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
  const pager = document.getElementById("pager");

  let rates = [];
  let page = 1;
  let autoTimer = null;
  const gvSeries = [];

  /* ---- Datenbanken ---- */
  api.databases().then((data) => {
    dbSelect.innerHTML = "";
    for (const name of data.databases) {
      const option = document.createElement("option");
      option.value = name;
      option.textContent = name;
      dbSelect.appendChild(option);
    }
    // Original-Standard bevorzugen (wie AetherOnePi: Clarke mit MM-Urls)
    const preferred = [...dbSelect.options].find((o) =>
      o.value.startsWith("HOMEOPATHY_Clarke_With_MateriaMedicaUrls")
    );
    if (preferred) {
      dbSelect.value = preferred.value;
    }
    updateDbHint();
  });

  /* ---- Kategorie-Schnellwahl (Aether_4-Buttons = Präfix-Selektoren) ---- */
  document.querySelectorAll(".cat-btn").forEach((button) => {
    button.addEventListener("click", async () => {
      const prefix = button.dataset.cat;
      const match = [...dbSelect.options].find((o) => o.value.startsWith(prefix));
      if (!match) {
        alert(`Keine Datenbank mit Präfix ${prefix} vorhanden.`);
        return;
      }
      dbSelect.value = match.value;
      updateDbHint();
      form.requestSubmit(); // wie im Original: Kategorie-Knopf analysiert direkt
    });
  });

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    setBusy(true);
    const body = { database: dbSelect.value, max_hits: Number(maxHitsSelect.value) };
    if (seedInput.value.trim() !== "") body.seed = Number(seedInput.value);
    if (modeSelect.value !== "") body.mode = modeSelect.value;
    try {
      const run = await api.analysis(body);
      rates = run.result.rateObjects || [];
      page = 1;
      renderResult();
      renderDraft(run.draft, run.passport);
      applyGvState({
        generalVitality: run.result.generalVitality,
        totalRuns: 0,
        gv: null,
      });
    } catch (error) {
      alert(`Analyse fehlgeschlagen: ${error.message}`);
    } finally {
      setBusy(false);
    }
  });

  function setBusy(busy) {
    form.querySelector(".btn-primary").disabled = busy;
    form.querySelector(".btn-primary").textContent = busy ? "Analysiere …" : "Analyse starten";
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

  function renderResult() {
    const pages = Math.max(1, Math.ceil(rates.length / PAGE_SIZE));
    page = Math.min(page, pages);
    const start = (page - 1) * PAGE_SIZE;
    const pageRows = rates.slice(start, start + PAGE_SIZE);

    resultEmpty.hidden = rates.length > 0;
    resultWrap.hidden = rates.length === 0;
    resultCount.textContent = rates.length ? `${rates.length} Raten` : "";
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

      // Wortwiederholung hervorheben (Original: roter Schleier)
      const name = (rate.nameOrRate || "").trim();
      const parts = name.includes(" ")
        ? name.split(" ").map((p) => p.replace(/-/g, "").replace(/>/g, "").trim())
        : [name];
      if (parts.some((p) => p.length >= 3 && (words.get(p) || 0) > 1)) {
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
        if ([1, 4, 5, 6, 7, 8].includes(cellIndex)) td.classList.add("num");
        if (cellIndex === 5 && value) {
          td.classList.add("hit-cell");
          td.title = "Höchste GV dieser Seite (HIT, wie im Original)";
        }
        td.textContent = value;
        tr.appendChild(td);
      });

      const actionTd = document.createElement("td");
      // CLARKE-Button (Original: nur bei Clarke-Datenbanken)
      if (dbSelect.value.toLowerCase().includes("clarke")) {
        const clarke = document.createElement("button");
        clarke.type = "button";
        clarke.className = "mm-link";
        clarke.textContent = "Clarke";
        clarke.title = "Klinischer Symptom-Vergleich (Materia Medica)";
        clarke.addEventListener("click", () => showClarkeCompare(rate.nameOrRate));
        actionTd.appendChild(clarke);
      }
      if (rate.url) {
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
      btn.addEventListener("click", () => broadcastRate(rate));
      actionTd.appendChild(btn);
      tr.appendChild(actionTd);
      resultBody.appendChild(tr);
    });
  }

  /* ---- CLARKE-Vergleich (Aether_4-Button) ---- */
  async function showClarkeCompare(rateName) {
    try {
      const data = await api.clarkeCompare(rateName);
      let html = `<h3>== ${data.rate} ==</h3>`;
      html += `<p><strong>Klinische Symptome (${data.clinical.length}):</strong> ` +
        data.clinical.slice(0, 40).map((s) => `<span class="badge">${s}</span>`).join(" ") + "</p>";
      html += "<p><strong>Gemeinsame Symptome mit anderen Analyse-Raten:</strong></p><ul>";
      for (const entry of data.sharedCounts) {
        html += `<li>${entry.count} — ${entry.symptom}</li>`;
      }
      html += "</ul>";
      if (Object.keys(data.others).length) {
        html += "<p><strong>Vergleich:</strong></p>";
        for (const [remedy, info] of Object.entries(data.others)) {
          html += `<p><strong>${remedy}</strong> — teilt: ${info.shared.slice(0, 8).join(", ")}</p>`;
        }
      }
      const dialog = document.getElementById("clarke-dialog");
      document.getElementById("clarke-content").innerHTML = html;
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
      await api.broadcast({ signature, seconds, multiplier: 1 });
      document.querySelector('.tab[data-tab="broadcast"]').click();
    } catch (error) {
      alert(`Broadcast abgelehnt: ${error.message}`);
    }
  }

  /* ---- Draft (D18-Zweiklick) ---- */
  function renderDraft(draft, passport) {
    draftEmpty.hidden = true;
    draftBody.hidden = false;
    draftStatus.textContent = draft.status;
    draftCopyguard.textContent = `${draft.copyguard_verdict} · ${draft.copyguard_digest.slice(0, 10)}…`;
    draftKernel.textContent = `${passport.kernel} ${passport.kernel_version}`;
    readyBtn.disabled = draft.status !== "draft";
    promoteBtn.disabled = draft.status !== "ready";
    draftHint.textContent =
      draft.status === "draft"
        ? "Schritt 1/2: Draft prüfen (CopyGuard läuft serverseitig, fail-closed)."
        : draft.status === "ready"
          ? "Schritt 2/2: Freigeben — erst dann geht etwas in den Broadcast."
          : `Status: ${draft.status}`;
  }

  readyBtn.addEventListener("click", async () => {
    try {
      const draft = await api.draftTransition(currentDraftId(), "ready");
      renderDraft(draft, { kernel: draft.source_kernel, kernel_version: draft.source_kernel_version });
    } catch (error) {
      alert(`Übergang abgelehnt: ${error.message}`);
    }
  });

  promoteBtn.addEventListener("click", async () => {
    try {
      // Original „BROADCAST MIX“ übernimmt den MULTIPLIER der UI — hier ebenso.
      const multiplier = Number(document.getElementById("mul-input").value) || 1;
      const result = await api.draftPromote(currentDraftId(), {
        max_rates: 5,
        seconds_per_rate: 60,
        multiplier,
      });
      draftHint.textContent =
        `Freigegeben — ${result.broadcastEntries.length} Raten (Multiplikator ${multiplier}) in der Broadcast-Queue.`;
      document.querySelector('.tab[data-tab="broadcast"]').click();
    } catch (error) {
      alert(`Promote blockiert: ${error.message}`);
    }
  });

  let activeDraftId = null;
  const _origRenderDraft = renderDraft;
  renderDraft = function (draft, passport) { activeDraftId = draft.id; _origRenderDraft(draft, passport); };
  function currentDraftId() { return activeDraftId; }

  /* ---- GV-Runde + runs + Graph + Auto-Modus ---- */
  function applyGvState(state) {
    if (state.generalVitality != null) gvValue.textContent = String(state.generalVitality);
    gvMeta.textContent = `GENERAL VITALITY: ${state.generalVitality ?? "—"} (runs = ${state.totalRuns ?? 0})`;
    if (state.gv != null) {
      gvSeries.push(state.gv);
      if (gvSeries.length > 140) gvSeries.shift();
      drawGraph();
      eventBus.dispatchEvent(new CustomEvent("gv.value", { detail: { gv: state.gv, runs: state.totalRuns } }));
    }
    if (state.result) {
      rates = state.result.rateObjects || rates;
      renderResult();
    }
  }

  function drawGraph() {
    drawSeries(graph, gvSeries);
  }

  gvBtn.addEventListener("click", async () => {
    try {
      // Kein Seed: die GV-Runde setzt den Entropiestrom der Analyse fort
      // (Original: weitere Züge aus demselben Hotbits-Cache).
      applyGvState(await api.gvRound({}));
    } catch (error) {
      alert(`GV-Runde: ${error.message}`);
    }
  });

  /* ---- Auto-Modus = serverseitiger Harmonisierungsregler (Original
     handleAutoMode): bei leerer Queue und GV <= 300 analysiert und
     sendet die Engine selbstständig (10-1000 s, UI-Multiplikator).
     Der Browser startet nur — die Uhr läuft im Server (Hard Rule 4). ---- */
  autoOnBtn.addEventListener("click", async () => {
    try {
      const multiplier = Number(document.getElementById("mul-input").value) || 1;
      const state = await api.autoModeOn(dbSelect.value, multiplier);
      autoOnBtn.classList.add("btn-primary");
      autoOffBtn.classList.remove("btn-primary");
      gvMeta.textContent = `AUTO MODE ON — GV = ${state.caseGv} (runs = ${state.runs})`;
    } catch (error) {
      alert(`Auto-Modus: ${error.message}`);
    }
  });
  autoOffBtn.addEventListener("click", async () => {
    try {
      await api.autoModeOff();
    } catch (_) { /* bereits aus */ }
    if (autoTimer) { clearInterval(autoTimer); autoTimer = null; }
    autoOffBtn.classList.add("btn-primary");
    autoOnBtn.classList.remove("btn-primary");
    gvMeta.textContent = gvMeta.textContent.replace("AUTO MODE ON", "AUTO MODE OFF");
  });

  // Serverseitige GV-Züge des Auto-Modus in den Graphen übernehmen
  eventBus.addEventListener("gv.update", (event) => {
    const { gv, runs, average } = event.detail;
    if (gv != null) {
      gvSeries.push(gv);
      if (gvSeries.length > 140) gvSeries.shift();
      drawGraph();
      const avgText = average != null ? ` · Ø ${average}` : "";
      gvMeta.textContent = `AUTO MODE ON — GV = ${gv} (runs = ${runs})${avgText}`;
      gvValue.textContent = String(gv);
    }
  });

  /* ---- Datenbank-Anzeige (Aether_4: „SELECTED DATABASE: …") ---- */
  const dbHint = document.getElementById("selected-db-hint");
  function updateDbHint() {
    dbHint.textContent = dbSelect.value ? `SELECTED DATABASE: ${dbSelect.value}.txt` : "Keine Datenbank gewählt.";
  }
  dbSelect.addEventListener("change", updateDbHint);
  api.databases().then(() => updateDbHint());

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

  /* ---- KI-Zwischenablage (Original: CLIPBOARD, solo-Modus) ---- */
  document.getElementById("clipboard-btn").addEventListener("click", async () => {
    const copy = {
      generalVitality: null,
      rateObjects: rates.slice(0, 21).map((r) => ({ ...r.to_dict ? r.to_dict() : r, url: "" })),
    };
    copy.generalVitality = Number(gvValue.textContent) || null;
    const prompt =
      `Bitte interpretiere dieses Radionik-Ergebnis (JSON, AetherOnePi-Ratenkatalog '${dbSelect.value}').\n` +
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
      sessionIndicator.dataset.pointer = String(pointer);
      const position = usable.findIndex((s) => s.index === pointer) + 1;
      sessionIndicator.textContent = `Session ${position}/${usable.length} (Nr. ${pointer})`;
      applyGvState({
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
    showSessionNav(true);
    sessionIndicator.dataset.pointer = String(state.pointer ?? "");
    sessionIndicator.textContent = state.label || `Session (Nr. ${state.pointer})`;
    applyGvState({
      generalVitality: result.generalVitality,
      totalRuns: state.totalRuns,
      gv: null,
      result,
    });
  });

  /* ---- Fall bearbeiten (Aether_2 „EDIT CASE") ---- */
  const editDialog = document.getElementById("edit-dialog");
  document.getElementById("edit-case-btn").addEventListener("click", async () => {
    const current = await api.currentCase();
    if (!current || !current.name) {
      alert("Kein Fall geladen.");
      return;
    }
    document.getElementById("edit-name").value = current.name || "";
    document.getElementById("edit-desc").value = current.description || "";
    const sessions = current.sessionList || [];
    document.getElementById("edit-intention").value =
      sessions.length ? sessions[sessions.length - 1].intention || "" : "";
    editDialog.showModal();
  });
  document.getElementById("edit-cancel-btn").addEventListener("click", () => editDialog.close());
  document.getElementById("edit-save-btn").addEventListener("click", async () => {
    const current = await api.currentCase();
    current.name = document.getElementById("edit-name").value.trim() || current.name;
    current.description = document.getElementById("edit-desc").value.trim() || null;
    const sessions = current.sessionList || [];
    if (sessions.length) {
      sessions[sessions.length - 1].intention =
        document.getElementById("edit-intention").value.trim() || null;
    }
    await api.saveCase(current);
    eventBus.dispatchEvent(new CustomEvent("case.changed", { detail: { name: current.name } }));
    editDialog.close();
  });

  /* ---- Tastatur wie im Original (AetherOneEventHandler.keyPressed):
     ENTER = GV-Zug · STRG = Analyse der gewählten Liste sofort starten ·
     ←/→ = Session-Historie. Nur im ANALYZE-Tab und außerhalb von Feldern. */
  document.addEventListener("keydown", (event) => {
    if (document.getElementById("view-analyse").hidden) return;
    const target = event.target;
    if (target && ["INPUT", "TEXTAREA", "SELECT"].includes(target.tagName)) return;

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

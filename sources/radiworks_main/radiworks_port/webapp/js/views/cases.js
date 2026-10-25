import { initPresentationCases } from "../case-presentation.js";
import { contextTitlePreview } from "../case-title.js";
import { initPersonalContext } from "../case-personal.js";
/* Fälle-View (Aether_2): anlegen/sichern, laden, Statistik (StatisticsGenerator). */

export function initCasesView(api, eventBus) {
  const nameInput = document.getElementById("case-name");
  const titleMode = document.getElementById("case-title-mode");
  const titleHint = document.getElementById("case-title-help");
  const descInput = document.getElementById("case-desc");
  const focusInput = document.getElementById("case-focus");
  const saveBtn = document.getElementById("case-save-btn");
  const saveStatus = document.getElementById("case-save-status");
  const listEl = document.getElementById("case-list");
  const listEmpty = document.getElementById("case-list-empty");
  const retryBtn = document.getElementById("case-refresh-btn");
  const loadStatus = document.getElementById("case-load-status");
  const statEmpty = document.getElementById("stat-empty");
  const statWrap = document.getElementById("stat-wrap");
  const statBody = document.getElementById("stat-body");
  let activeCaseRef = null;
  let activeContextVersion = null;
  let saving = false;
  let editorEpoch = 0;
  let editorDirty = false;
  const newBtn = document.getElementById("case-new-btn");
  const editorStatus = document.getElementById("case-editor-status");
  function describeEditor() {
    saveBtn.textContent = activeCaseRef ? "Änderungen speichern" : "Neuen Fall speichern";
    editorStatus.textContent = activeCaseRef
      ? "Bearbeitung des geladenen Falls. Seine Fall-ID und bisherigen Sitzungen bleiben erhalten."
      : "Neuer Fall: Beim Speichern entsteht eine eigene Fall-ID. Ein bereits aktiver Fall und seine Sitzungen werden nicht überschrieben; erst danach wird der neue Fall aktiv.";
  }
  const personal = initPersonalContext(api, saveBtn);
  const media = initPresentationCases(api,eventBus,()=>activeCaseRef&&!editorDirty&&!saving&&!personal.preparing?{ref:activeCaseRef,contextVersion:activeContextVersion}:null);
  function refreshTitle() {
    const automatic = titleMode.value === "context";
    nameInput.readOnly = automatic;
    if (automatic) {
      nameInput.value = contextTitlePreview({
        firstName: document.getElementById("case-first-name").value,
        lastName: document.getElementById("case-last-name").value,
        birthDate: document.getElementById("case-birth-date").value,
        place: document.getElementById("case-place").value,
        placeKind: document.getElementById("case-place-kind").value,
      }, focusInput.value);
    }
    titleHint.textContent = automatic
      ? "Vorschau aus Vorname, Nachname, Geburtsdatum, aktivem Ort und Fokus. Der Server bildet den Titel beim Speichern; bestehende Sitzungen bleiben unverändert."
      : "Manuelle Fallbezeichnung. Ältere Fälle behalten ihren Titel, bis Sie ausdrücklich auf den automatischen Titel umstellen.";
  }
  function hydrateTitle(data) {
    titleMode.value = data.titleMode === "context" ? "context" : "manual";
    refreshTitle();
    // The server may use a stable neutral ID when every context field is empty.
    if (data.titleMode === "context") nameInput.value = data.name || nameInput.value;
  }
  titleMode.addEventListener("change", refreshTitle);
  for (const id of ["case-first-name", "case-last-name", "case-birth-date", "case-place", "case-place-kind", "case-focus"]) {
    const input = document.getElementById(id);
    input.addEventListener("input", refreshTitle);
    input.addEventListener("change", refreshTitle);
  }
  refreshTitle();
  describeEditor();
  for (const id of ["case-name", "case-desc", "case-focus", "case-title-mode", "case-first-name", "case-last-name", "case-birth-date", "case-place", "case-place-kind", "case-image-file"]) {
    for (const type of ["input", "change"]) document.getElementById(id).addEventListener(type, () => { editorEpoch += 1; editorDirty = true; media?.checkBinding(); });
  }
  document.getElementById("case-image-remove").addEventListener("click", () => { editorEpoch += 1; editorDirty = true; media?.checkBinding(); });
  newBtn.addEventListener("click", () => {
    if (saving || personal.preparing) return;
    editorEpoch += 1;
    activeCaseRef = null; activeContextVersion = null; editorDirty = false;
    personal.hydrate({});
    media?.invalidate();
    titleMode.value = "context";
    nameInput.value = ""; descInput.value = ""; focusInput.value = "";
    refreshTitle(); describeEditor();
    saveStatus.textContent = "Neuen Fall vorbereitet. Der bisher aktive Fall bleibt bis zum Speichern unverändert.";
    document.getElementById("case-first-name").focus();
  });

  async function refresh() {
    const data = await api.cases();
    const entries = data.entries || (data.cases || []).map((name) => ({ name }));
    listEmpty.hidden = entries.length > 0;
    listEl.hidden = entries.length === 0;
    listEl.innerHTML = "";
    for (const [index, entry] of entries.entries()) {
      const li = document.createElement("li");
      li.className = "case-row";
      const label = document.createElement("span");
      label.textContent = entry.name;
      const actions = document.createElement("span");
      actions.className = "case-actions";
      const loadBtn = document.createElement("button");
      loadBtn.type = "button";
      loadBtn.className = "btn";
      loadBtn.textContent = "Laden";
      loadBtn.setAttribute("aria-label", `Fall ${index + 1} laden: ${entry.name}`);
      loadBtn.addEventListener("click", () => selectCase(entry, `Fall ${index + 1}`));
      const statBtn = document.createElement("button");
      statBtn.type = "button";
      statBtn.className = "btn";
      statBtn.textContent = "Statistik";
      statBtn.setAttribute("aria-label", `Statistik für Fall ${index + 1}: ${entry.name}`);
      statBtn.addEventListener("click", () => showStatisticsWithFeedback(entry, `Fall ${index + 1}`, true));
      actions.append(loadBtn, statBtn);
      li.append(label, actions);
      listEl.appendChild(li);
    }
    renderRecentChips();
  }

  async function refreshCases() {
    listEmpty.textContent = "Fallliste wird geladen …";
    listEmpty.hidden = false;
    listEl.hidden = true;
    retryBtn.hidden = true;
    try {
      await refresh();
      listEmpty.textContent = "Noch keine Fälle.";
      return true;
    } catch (_) {
      listEmpty.textContent = "Fallliste derzeit nicht erreichbar.";
      listEmpty.hidden = false;
      retryBtn.hidden = false;
      return false;
    }
  }
  retryBtn.addEventListener("click", refreshCases);

  async function selectCase(entry, caseLabel) {
    if (saving) { loadStatus.textContent = "Bitte den laufenden Speicherauftrag abwarten."; return; }
    loadStatus.textContent = "Fall wird geladen …";
    try {
      const applied = await loadCase(entry);
      loadStatus.textContent = applied === false ? "Neue Eingaben bleiben erhalten; Fall wurde nicht ins Formular übernommen." : `${caseLabel} geladen.`;
    } catch (_) {
      loadStatus.textContent = "Fall konnte nicht geladen werden. Bitte Verbindung prüfen und erneut versuchen.";
    }
  }

  async function showStatisticsWithFeedback(entry, caseLabel, report = false) {
    try {
      const count = await showStatistics(entry);
      if (report) loadStatus.textContent = count
        ? `Statistik für ${caseLabel} angezeigt.`
        : `Für ${caseLabel} sind noch keine Analyseergebnisse vorhanden.`;
    } catch (_) {
      statEmpty.textContent = "Statistik derzeit nicht verfügbar.";
      statEmpty.hidden = false;
      statWrap.hidden = true;
      if (report) loadStatus.textContent = `Statistik für ${caseLabel} derzeit nicht verfügbar.`;
    }
  }

  /* „LAST CASES“ (Original: dashboardInformations, max. 11) auf der Start-Ansicht */
  async function renderRecentChips() {
    const container = document.getElementById("recent-cases");
    if (!container) return;
    try {
      const data = await api.recentCases();
      const recent = data.entries || (data.recent || []).map((name) => ({ name }));
      container.hidden = recent.length === 0;
      container.innerHTML = "";
      const title = document.createElement("p");
      title.className = "hint";
      title.textContent = "Zuletzt geladen:";
      container.appendChild(title);
      for (const [index, entry] of recent.entries()) {
        const chip = document.createElement("button");
        chip.type = "button";
        chip.className = "chip";
        chip.textContent = entry.name;
        chip.setAttribute("aria-label", `Zuletzt geladener Fall ${index + 1}: ${entry.name}`);
        chip.addEventListener("click", () => selectCase(entry, `Zuletzt geladener Fall ${index + 1}`));
        container.appendChild(chip);
      }
    } catch (_) { /* offline */ }
  }

  async function loadCase(entry, expectedEpoch = null, existingBinding = null) {
    if (expectedEpoch !== null && expectedEpoch !== editorEpoch) return false;
    const loadEpoch = expectedEpoch ?? ++editorEpoch;
    async function activateSelection() {
      const loaded = entry.ref ? await api.activateCaseRef(entry.ref) : await api.activateCase(entry.name);
      return loaded;
    }
    const loaded = existingBinding || await activateSelection();
    if (loadEpoch !== editorEpoch) return false;
    if (saving) { personal.invalidate(); throw new Error("Fallkontext wurde geändert. Bitte Fall neu laden."); }
    const caseData = loaded.data;
    if (entry.ref && loaded.ref !== entry.ref) throw new Error("Fallbindung hat sich geändert.");
    localStorage.setItem("radiworks_active_case", `ref:${loaded.ref}`);
    nameInput.value = caseData.name || entry.name;
    descInput.value = caseData.description || "";
    focusInput.value = caseData.focus || "";
    activeCaseRef = loaded.ref;
    activeContextVersion = caseData.contextVersion || null;
    personal.hydrate(caseData);
    hydrateTitle(caseData);
    editorDirty = false; describeEditor();
    eventBus?.dispatchEvent(new CustomEvent("case.changed", { detail: { name: caseData.name || entry.name, ref: loaded.ref, contextVersion: caseData.contextVersion || null } }));
    // Letzte Session mit Ergebnis in die Analyse-Ansicht holen
    try {
      const sessions = (await api.sessions()).sessions.filter((s) => s.hasResult);
      if (sessions.length) {
        const last = sessions[sessions.length - 1];
        const viewed = await api.viewSession(last.index);
        eventBus?.dispatchEvent(new CustomEvent("analysis.external", {
          detail: {
            result: viewed.result,
            state: {
              pointer: last.index,
              sessionId: viewed.sessionId,
              sourceKind: viewed.sourceKind,
              totalRuns: viewed.state.totalRuns,
              label: `Session ${sessions.length}/${sessions.length} (Nr. ${last.index}) — geladen`,
            },
          },
        }));
      }
    } catch (_) { /* keine Sessions */ }
    await renderRecentChips(); // „LAST CASES" auf der Start-Ansicht aktualisieren
    await showStatisticsWithFeedback(entry);
    return true;
  }

  async function showStatistics(entry) {
    const stats = entry.ref ? await api.caseStatisticsRef(entry.ref) : await api.caseStatistics(entry.name);
    const rows = stats.topList || [];
    statEmpty.textContent = "Für diesen Fall liegen noch keine Analyseergebnisse vor.";
    statEmpty.hidden = rows.length > 0;
    statWrap.hidden = rows.length === 0;
    statBody.innerHTML = "";
    rows.forEach((entry) => {
      const tr = document.createElement("tr");
      const cells = [String(entry.occurrence), String(entry.overallGV), String(entry.overallEnergeticValue), entry.name];
      cells.forEach((value, index) => {
        const td = document.createElement("td");
        if (index < 3) td.className = "num";
        td.textContent = value;
        tr.appendChild(td);
      });
      statBody.appendChild(tr);
    });
    return rows.length;
  }

  saveBtn.addEventListener("click", async () => {
    if (saving || personal.preparing || !personal.validate()) return;
    const name = nameInput.value.trim();
    if (titleMode.value === "manual" && !name) {
      saveStatus.textContent = "Bitte einen Fall-Namen eingeben.";
      return;
    }
    const isNew = activeCaseRef === null;
    saving = true;
    newBtn.disabled = true;
    const bindingTicket = personal.bindingToken();
    personal.setSaving(true);
    for (const input of [nameInput, descInput, focusInput, titleMode]) input.disabled = true;
    saveStatus.textContent = "Fall wird gespeichert …";
    let requestPending = true;
    const waitTimer = setTimeout(async () => {
      if (!requestPending) return;
      saveStatus.textContent = "Die Speicherantwort steht noch aus. Bitte nicht erneut klicken; Servererreichbarkeit wird geprüft.";
      const probe = new AbortController();
      const probeTimer = setTimeout(() => probe.abort(), 3000);
      try {
        await api.ping(probe.signal);
        if (requestPending) saveStatus.textContent = "Server erreichbar; die Speicherantwort steht weiter aus. Bitte nicht erneut klicken.";
      } catch {
        if (requestPending) saveStatus.textContent = "Auch die Serverprobe antwortet nicht. Bitte nicht erneut klicken; der Speicherauftrag kann noch laufen.";
      } finally {
        clearTimeout(probeTimer);
      }
    }, 8000);
    try {
      // Das projizierte Falldokument darf nicht als Rohdaten zurückgeschrieben werden.
      const boundCurrent = isNew ? {data:{}, ref:null} : await api.currentCaseWithRef();
      personal.assertBinding(bindingTicket);
      const current = boundCurrent.data;
      const metadata = {
        titleMode: titleMode.value,
        ...(titleMode.value === "manual" ? { name } : {}),
        description: descInput.value.trim() || null,
        focus: focusInput.value.trim() || null,
      };
      if (!isNew) {
        if (!activeCaseRef || boundCurrent.ref !== activeCaseRef) {
          throw new Error("Aktiver Fall hat sich geändert. Bitte Fall erneut laden.");
        }
        metadata.expected_case_ref = activeCaseRef;
        if (activeContextVersion !== null) metadata.expected_context_version = activeContextVersion;
      }
      const changes = await personal.payload(isNew);
      personal.assertBinding(bindingTicket);
      if (Object.keys(changes).length) {
        metadata[isNew ? "personalContext" : "personalContextChanges"] = changes;
      }
      const saved = !isNew
        ? await api.saveCurrentCaseMetadata(metadata)
        : await api.saveCase(metadata);
      personal.assertBinding(bindingTicket);
      const savedCase = saved.data;
      const activeName = savedCase.name || name;
      activeCaseRef = saved.ref;
      activeContextVersion = savedCase.contextVersion || null;
      personal.hydrate(savedCase, true);
      localStorage.setItem("radiworks_active_case", `ref:${saved.ref}`);
      nameInput.value = activeName;
      hydrateTitle(savedCase);
      editorDirty = false; describeEditor();
      eventBus?.dispatchEvent(new CustomEvent("case.changed", { detail: { name: activeName, ref: saved.ref, contextVersion: savedCase.contextVersion || null } }));
      const savedTicket = personal.bindingToken();
      await refreshCases();
      personal.assertBinding(savedTicket);
      saveStatus.textContent = "Fall gespeichert und in der Fallliste geprüft.";
    } catch (error) {
      saveStatus.textContent = `Speicherstatus nicht bestätigt: ${error.message}`;
    } finally {
      requestPending = false;
      clearTimeout(waitTimer);
      saving = false;
      newBtn.disabled = false;
      personal.setSaving(false);
      for (const input of [nameInput, descInput, focusInput, titleMode]) input.disabled = false;
      media?.checkBinding();
    }
  });

  eventBus?.addEventListener("case.changed", (event) => {
    const { savedCase, ref } = event.detail || {};
    if (!savedCase || !ref) return;
    if (saving) { personal.invalidate(); return; }
    if (editorDirty) { loadStatus.textContent = "Der Fall wurde andernorts geändert. Ihre Eingaben bleiben erhalten; bitte Auswahl vor dem Speichern prüfen."; return; }
    editorEpoch += 1;
    activeCaseRef = ref;
    activeContextVersion = savedCase.contextVersion || null;
    personal.hydrate(savedCase);
    nameInput.value = savedCase.name || "";
    descInput.value = savedCase.description || "";
    focusInput.value = savedCase.focus || "";
    hydrateTitle(savedCase);
    describeEditor();
    localStorage.setItem("radiworks_active_case", `ref:${ref}`);
  });

  const restoreEpoch = editorEpoch;
  refreshCases().then((loaded) => {
    if (!loaded) return;
    if (editorEpoch !== restoreEpoch) return;
    const savedCase = localStorage.getItem("radiworks_active_case");
    if (!savedCase) return;
    const entry = savedCase.startsWith("ref:")
      ? { ref: savedCase.slice(4) } : { name: savedCase };
    (async () => {
      const bound = await api.currentCaseWithRef();
      if (editorEpoch !== restoreEpoch) return;
      if (!bound.ref || (entry.ref ? bound.ref !== entry.ref : bound.data.name !== entry.name)) {
        throw new Error("Gespeicherte Auswahl ist nicht der aktive Fall.");
      }
      await loadCase(entry, restoreEpoch, bound);
    })().catch(() => {
      if (editorEpoch !== restoreEpoch) return;
      // Ein gelöschter oder nicht mehr zugänglicher Fall darf keinen
      // fehlerhaften Startzustand dauerhaft erzwingen.
      localStorage.removeItem("radiworks_active_case");
      loadStatus.textContent = "Gespeicherte Fallauswahl nicht verfügbar. Bitte Fall erneut wählen.";
    });
  });
}

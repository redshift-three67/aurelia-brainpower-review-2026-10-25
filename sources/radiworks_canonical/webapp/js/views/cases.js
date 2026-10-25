/* Fälle-View (Aether_2): anlegen/sichern, laden, Statistik (StatisticsGenerator). */

export function initCasesView(api, eventBus) {
  const nameInput = document.getElementById("case-name");
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
    loadStatus.textContent = "Fall wird geladen …";
    try {
      await loadCase(entry);
      loadStatus.textContent = `${caseLabel} geladen.`;
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

  async function loadCase(entry) {
    const loaded = entry.ref ? await api.activateCaseRef(entry.ref) : await api.activateCase(entry.name);
    const caseData = loaded.data;
    if (entry.ref && loaded.ref !== entry.ref) throw new Error("Fallbindung hat sich geändert.");
    localStorage.setItem("radiworks_active_case", `ref:${loaded.ref}`);
    nameInput.value = caseData.name || entry.name;
    descInput.value = caseData.description || "";
    focusInput.value = caseData.focus || "";
    activeCaseRef = loaded.ref;
    eventBus?.dispatchEvent(new CustomEvent("case.changed", { detail: { name: caseData.name || entry.name } }));
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
    const name = nameInput.value.trim();
    if (!name) {
      saveStatus.textContent = "Bitte einen Fall-Namen eingeben.";
      return;
    }
    saveBtn.disabled = true;
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
      const boundCurrent = await api.currentCaseWithRef();
      const current = boundCurrent.data;
      const metadata = {
        name,
        description: descInput.value.trim() || null,
        focus: focusInput.value.trim() || null,
      };
      if (current.name) {
        if (!activeCaseRef || boundCurrent.ref !== activeCaseRef) {
          throw new Error("Aktiver Fall hat sich geändert. Bitte Fall erneut laden.");
        }
        metadata.expected_case_ref = activeCaseRef;
      }
      const saved = current.name
        ? await api.saveCurrentCaseMetadata(metadata)
        : await api.saveCase(metadata);
      const savedCase = saved.data;
      const activeName = savedCase.name || name;
      activeCaseRef = saved.ref;
      localStorage.setItem("radiworks_active_case", `ref:${saved.ref}`);
      nameInput.value = activeName;
      eventBus?.dispatchEvent(new CustomEvent("case.changed", { detail: { name: activeName } }));
      await refreshCases();
      saveStatus.textContent = "Fall gespeichert und in der Fallliste geprüft.";
    } catch (error) {
      saveStatus.textContent = `Fall konnte nicht gespeichert werden: ${error.message}`;
    } finally {
      requestPending = false;
      clearTimeout(waitTimer);
      saveBtn.disabled = false;
    }
  });

  eventBus?.addEventListener("case.changed", (event) => {
    const { savedCase, ref } = event.detail || {};
    if (!savedCase || !ref) return;
    activeCaseRef = ref;
    nameInput.value = savedCase.name || "";
    descInput.value = savedCase.description || "";
    focusInput.value = savedCase.focus || "";
    localStorage.setItem("radiworks_active_case", `ref:${ref}`);
  });

  refreshCases().then((loaded) => {
    if (!loaded) return;
    const savedCase = localStorage.getItem("radiworks_active_case");
    if (!savedCase) return;
    const entry = savedCase.startsWith("ref:")
      ? { ref: savedCase.slice(4) } : { name: savedCase };
    loadCase(entry).catch(() => {
      // Ein gelöschter oder nicht mehr zugänglicher Fall darf keinen
      // fehlerhaften Startzustand dauerhaft erzwingen.
      localStorage.removeItem("radiworks_active_case");
      loadStatus.textContent = "Gespeicherte Fallauswahl nicht verfügbar. Bitte Fall erneut wählen.";
    });
  });
}

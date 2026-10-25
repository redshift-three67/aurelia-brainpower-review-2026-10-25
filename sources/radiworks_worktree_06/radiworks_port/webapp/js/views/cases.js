/* Fälle-View (Aether_2): anlegen/sichern, laden, Statistik (StatisticsGenerator). */

export function initCasesView(api, eventBus) {
  const nameInput = document.getElementById("case-name");
  const descInput = document.getElementById("case-desc");
  const saveBtn = document.getElementById("case-save-btn");
  const listEl = document.getElementById("case-list");
  const listEmpty = document.getElementById("case-list-empty");
  const statEmpty = document.getElementById("stat-empty");
  const statWrap = document.getElementById("stat-wrap");
  const statBody = document.getElementById("stat-body");

  async function refresh() {
    const data = await api.cases();
    const names = data.cases || [];
    listEmpty.hidden = names.length > 0;
    listEl.hidden = names.length === 0;
    listEl.innerHTML = "";
    for (const name of names) {
      const li = document.createElement("li");
      li.className = "case-row";
      const label = document.createElement("span");
      label.textContent = name;
      const actions = document.createElement("span");
      actions.className = "case-actions";
      const loadBtn = document.createElement("button");
      loadBtn.type = "button";
      loadBtn.className = "btn";
      loadBtn.textContent = "Laden";
      loadBtn.addEventListener("click", () => loadCase(name));
      const statBtn = document.createElement("button");
      statBtn.type = "button";
      statBtn.className = "btn";
      statBtn.textContent = "Statistik";
      statBtn.addEventListener("click", () => showStatistics(name));
      actions.append(loadBtn, statBtn);
      li.append(label, actions);
      listEl.appendChild(li);
    }
    renderRecentChips();
  }

  /* „LAST CASES“ (Original: dashboardInformations, max. 11) auf der Start-Ansicht */
  async function renderRecentChips() {
    const container = document.getElementById("recent-cases");
    if (!container) return;
    try {
      const data = await api.recentCases();
      const recent = data.recent || [];
      container.hidden = recent.length === 0;
      container.innerHTML = "";
      const title = document.createElement("p");
      title.className = "hint";
      title.textContent = "Zuletzt geladen:";
      container.appendChild(title);
      for (const name of recent) {
        const chip = document.createElement("button");
        chip.type = "button";
        chip.className = "chip";
        chip.textContent = name;
        chip.addEventListener("click", () => loadCase(name));
        container.appendChild(chip);
      }
    } catch (_) { /* offline */ }
  }

  async function loadCase(name) {
    const caseData = await api.loadCase(name);
    nameInput.value = caseData.name || name;
    descInput.value = caseData.description || "";
    eventBus?.dispatchEvent(new CustomEvent("case.changed", { detail: { name: caseData.name || name } }));
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
              totalRuns: viewed.state.totalRuns,
              label: `Session ${sessions.length}/${sessions.length} (Nr. ${last.index}) — geladen`,
            },
          },
        }));
      }
    } catch (_) { /* keine Sessions */ }
    await renderRecentChips(); // „LAST CASES" auf der Start-Ansicht aktualisieren
    await showStatistics(name);
  }

  async function showStatistics(name) {
    const stats = await api.caseStatistics(name);
    const rows = stats.topList || [];
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
  }

  saveBtn.addEventListener("click", async () => {
    const name = nameInput.value.trim();
    if (!name) {
      alert("Bitte einen Fall-Namen eingeben.");
      return;
    }
    // Aktuellen In-Memory-Fall (mit den Analysen) unter dem Namen sichern
    const current = await api.currentCase();
    const payload = { ...current, name, description: descInput.value.trim() || null };
    await api.saveCase(payload);
    eventBus?.dispatchEvent(new CustomEvent("case.changed", { detail: { name } }));
    await refresh();
  });

  refresh();
}

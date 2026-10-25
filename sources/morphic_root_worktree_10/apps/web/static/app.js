const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => Array.from(document.querySelectorAll(selector));

const WORKFLOW_STEPS = [
  {label: "Willkommen & Systemstatus"},
  {label: "Hinweise & Einwilligung"},
  {label: "Klienten-Daten"},
  {label: "Fokus & Intention"},
  {label: "Analyse-Konfiguration"},
  {label: "EMF-/Umfeld-Analyseprofil"},
  {label: "Zusammenfassung & Start"},
  {label: "Ergebnis-Matrix"},
  {label: "Ergebnis-Details & Berichte"},
  {label: "Harmonisierung, Export & Abschluss"}
];

const CLIENT_DRAFT_KEY = "morphic_v1_client_draft";

const HARMONIZATION_MODE_LABELS = {
  healing: "Healing",
  clearing: "Clearing",
  protection: "Protection",
  transformation: "Transformation",
  harmonization: "Harmonization",
  activation: "Activation"
};

let currentStep = 0;
let activeJobId = null;
let jobPollTimer = null;
let activeReportId = null;
let activeHarmonizationJobId = null;
let harmonizationPollTimer = null;

function setClientStorageState(message, state = "neutral") {
  const node = $("#client-storage-state");
  if (!node) return;
  node.textContent = message;
  node.dataset.state = state;
}

function storageUnavailable() {
  setClientStorageState("lokale Speicherung nicht verfuegbar", "bad");
}

function safeLocalStorageGet(key) {
  try {
    return window.localStorage.getItem(key);
  } catch (error) {
    storageUnavailable();
    return null;
  }
}

function safeLocalStorageSet(key, value) {
  try {
    window.localStorage.setItem(key, value);
    return true;
  } catch (error) {
    storageUnavailable();
    return false;
  }
}

function safeLocalStorageRemove(key) {
  try {
    window.localStorage.removeItem(key);
    return true;
  } catch (error) {
    storageUnavailable();
    return false;
  }
}

function setPill(id, text, state) {
  const node = $(id);
  if (!node) return;
  node.textContent = text;
  node.className = `pill ${state}`;
}

function listItem(text) {
  const li = document.createElement("li");
  li.textContent = text;
  return li;
}

function sourceBadge(label, count, state) {
  const span = document.createElement("span");
  span.className = `pill ${state}`;
  span.textContent = `${label}: ${count}`;
  return span;
}

function showInlineState(message, state = "neutral") {
  const node = $("#preview-state");
  if (!node) return;
  node.textContent = message;
  node.dataset.state = state;
}

function showHarmonizationState(message, state = "neutral") {
  const node = $("#harmonization-preview-state");
  if (!node) return;
  node.textContent = message;
  node.dataset.state = state;
}

function harmonizationModeLabel(mode) {
  return HARMONIZATION_MODE_LABELS[mode] || mode || "-";
}

function harmonizationProgressPercent(payload) {
  if (typeof payload.progress_percent === "number" && Number.isFinite(payload.progress_percent)) {
    return Math.max(0, Math.min(100, payload.progress_percent));
  }
  if (payload.status === "completed") return 100;
  return null;
}

function syncHarmonizationControls() {
  const hasReport = Boolean(activeReportId);
  const status = $("#harmonization-status-label")?.dataset.state || "neutral";
  const startButton = $("#harmonization-start-button");
  const refreshButton = $("#harmonization-refresh-button");
  const stopButton = $("#harmonization-stop-button");
  if (startButton) {
    startButton.disabled = !hasReport || status === "warn";
  }
  if (refreshButton) {
    refreshButton.disabled = !activeHarmonizationJobId;
  }
  if (stopButton) {
    stopButton.disabled = !activeHarmonizationJobId || status !== "warn";
  }
  if (!hasReport && !activeHarmonizationJobId) {
    showHarmonizationState("Waehle nach dem Scan einen Bericht fuer den Abschluss.");
  }
}

function syncResultMatrixControls() {
  const refreshButton = $("#refresh-result-matrix-button");
  if (refreshButton) {
    refreshButton.disabled = !activeJobId;
  }
}

function renderLauncherPreview(payload) {
  const preview = $("#command-preview");
  if (!preview) return;

  const lines = [];
  const launcher = payload.launcher || {};
  const profileLines = renderProfileSelection(payload);
  if (launcher.script_path) {
    lines.push(`PS1: ${launcher.script_path}`);
  }
  if (launcher.cli_entrypoint) {
    lines.push(`CLI: ${launcher.cli_entrypoint}`);
  }
  if (profileLines.length) {
    lines.push("", "Profilwahl:", ...profileLines);
  }
  if (Array.isArray(payload.command) && payload.command.length) {
    lines.push("", "Befehl:", payload.command.join(" "));
  }
  if (Array.isArray(launcher.unsupported_request_fields) && launcher.unsupported_request_fields.length) {
    lines.push("", "Noch nicht im CLI-Pfad:", launcher.unsupported_request_fields.join(", "));
  }
  if (payload.notes?.length) {
    lines.push("", "Hinweise:", `- ${payload.notes.join("\n- ")}`);
  }
  preview.textContent = lines.join("\n");
}

function renderProfileSelection(payload) {
  const unsupported = new Set(payload.launcher?.unsupported_request_fields || []);
  const imageStatus = payload.image_enabled
    ? `aktiv (${payload.image_path})`
    : "nicht gesetzt";
  const suffix = (field) => unsupported.has(field) ? " (noch nicht im CLI-Pfad aktiv)" : "";
  return [
    `- Template: ${payload.profile_template || "phase1-default"}${suffix("profile_template")}`,
    `- Entropie: ${payload.entropy_mode || "legacy"}${suffix("entropy_mode")}`,
    `- Bild: ${imageStatus}${suffix("image_path")}`,
    `- Adaptive Limits: ${payload.adaptive_limits_requested ? "aktiv" : "aus"}; effektives Vorschau-/Report-Limit ${payload.effective_result_limit}${suffix("adaptive_limits")}`
  ];
}

function jobStateLabel(status) {
  if (status === "completed") return "abgeschlossen";
  if (status === "failed") return "fehlgeschlagen";
  if (status === "error") return "fehler";
  if (status === "stopped") return "gestoppt";
  if (status === "running") return "laeuft";
  return "wartet";
}

function jobStateTone(status) {
  if (status === "completed") return "ok";
  if (status === "failed") return "bad";
  if (status === "error") return "bad";
  if (status === "stopped") return "neutral";
  if (status === "running") return "warn";
  return "neutral";
}

function jobProgressPercent(payload) {
  if (typeof payload.progress_percent === "number" && Number.isFinite(payload.progress_percent)) {
    return Math.max(0, Math.min(100, payload.progress_percent));
  }
  if (payload.status === "completed") return 100;
  return null;
}

function renderJobProgressLabel(payload) {
  const node = $("#job-progress-label");
  if (!node) return;
  const percent = jobProgressPercent(payload);
  node.textContent = percent === null
    ? "wird aus Ausgabe abgeleitet"
    : `${percent.toFixed(1)}%`;
}

function renderJobChecklist(payload) {
  const list = $("#job-substep-list");
  if (!list) return;

  const completed = Array.isArray(payload.completed_substeps) ? payload.completed_substeps : [];
  const current = payload.current_substep || "";
  const items = [];

  completed.forEach((label) => items.push({label, state: "completed"}));
  if (current && !completed.includes(current)) {
    items.push({label: current, state: payload.status === "completed" ? "completed" : "current"});
  }

  if (!items.length) {
    const empty = document.createElement("li");
    empty.className = "empty";
    empty.textContent = "Noch keine erkannten Substeps.";
    list.replaceChildren(empty);
    return;
  }

  const nodes = items.map(({label, state}) => {
    const item = document.createElement("li");
    item.className = state;
    item.textContent = label;
    return item;
  });
  list.replaceChildren(...nodes);
}

function updateJobStatus(payload) {
  const panel = $("#job-status-panel");
  const label = $("#job-status-label");
  const fill = $("#job-progress-fill");
  const startButton = $("#start-analysis-button");
  if (panel) panel.hidden = false;
  if (label) {
    label.textContent = jobStateLabel(payload.status);
    label.dataset.state = jobStateTone(payload.status);
  }
  $("#job-id-label").textContent = payload.job_id || "-";
  $("#job-returncode").textContent = payload.returncode ?? "-";
  $("#job-phase-label").textContent = payload.current_phase || "-";
  $("#job-substep-label").textContent = payload.current_substep || "Warte auf Ausgabe...";
  renderJobProgressLabel(payload);
  renderJobChecklist(payload);

  const logParts = [];
  if (payload.stdout_tail) logParts.push(payload.stdout_tail.trim());
  if (payload.stderr_tail) logParts.push(`STDERR\n${payload.stderr_tail.trim()}`);
  $("#job-log-tail").textContent = logParts.filter(Boolean).join("\n\n") || "Warte auf Ausgabe...";

  if (fill) {
    const percent = jobProgressPercent(payload);
    fill.style.width = `${percent ?? 0}%`;
  }
  if (startButton) {
    startButton.disabled = payload.status === "running";
  }
}

function validateCurrentStep() {
  if (currentStep === 1) {
    const local = $("#consent-local");
    const safety = $("#consent-safety");
    const ok = Boolean(local?.checked && safety?.checked);
    if (!ok) showInlineState("Einwilligung bestaetigen", "warn");
    return ok;
  }

  if ([2, 3, 4, 5, 6].includes(currentStep)) {
    const form = $("#scan-form");
    if (!form) return true;
    if (typeof form.reportValidity === "function") return form.reportValidity();
    return form.checkValidity();
  }

  if (currentStep === 8) {
    const ok = Boolean(activeReportId);
    if (!ok) {
      setReportState("Bitte zuerst einen Bericht in der Vorschau oeffnen.", "warn");
      showHarmonizationState("Bitte zuerst einen Bericht in der Vorschau oeffnen.", "warn");
    }
    return ok;
  }

  return true;
}

function updateProgress() {
  const pct = ((currentStep + 1) / WORKFLOW_STEPS.length) * 100;
  const fill = $("#wizard-progress-fill");
  const label = $("#wizard-progress-label");
  if (fill) fill.style.width = `${pct.toFixed(1)}%`;
  if (label) label.textContent = `${currentStep + 1} / ${WORKFLOW_STEPS.length}`;

  $$(".wizard-step").forEach((step) => {
    const index = Number(step.dataset.step || 0);
    step.classList.toggle("active", index === currentStep);
    step.classList.toggle("completed", index < currentStep);
    step.disabled = index > currentStep;
    if (index === currentStep) {
      step.setAttribute("aria-current", "step");
    } else {
      step.removeAttribute("aria-current");
    }
    const marker = step.querySelector("span");
    if (marker) marker.textContent = index < currentStep ? "✓" : String(index + 1);
  });

  $$(".wizard-panel").forEach((panel) => {
    const isActive = Number(panel.dataset.step || 0) === currentStep;
    panel.classList.toggle("active", isActive);
    panel.setAttribute("aria-hidden", isActive ? "false" : "true");
  });

  const prev = $("#btn-prev");
  const next = $("#btn-next");
  if (prev) prev.disabled = currentStep === 0;
  if (next) {
    const final = currentStep === WORKFLOW_STEPS.length - 1;
    next.textContent = final ? "Workflow bereit" : "Weiter";
    next.disabled = final;
  }
}

function goToStep(index) {
  if (index < 0 || index >= WORKFLOW_STEPS.length) return;
  if (index > currentStep && !validateCurrentStep()) return;
  currentStep = index;
  updateProgress();
  window.scrollTo({top: 0, behavior: "smooth"});
}

function navigate(direction) {
  goToStep(currentStep + direction);
}

async function loadHealth() {
  try {
    const response = await fetch("/api/health");
    const health = await response.json();
    const databases = health.databases?.databases || {};
    const warnings = health.warnings || [];
    const errors = health.errors || [];
    $("#python-version").textContent = health.python?.version || "-";
    $("#profile-count").textContent = health.profiles?.total_profiles ?? "-";
    $("#database-count").textContent = Object.keys(databases).length;
    $("#health-status").textContent = health.ok ? "OK" : "FEHLER";
    setPill("#health-pill", health.ok ? "Health OK" : "Health FEHLER", health.ok ? "ok" : "bad");

    const list = $("#health-list");
    list.replaceChildren();
    warnings.slice(0, 4).forEach((warning) => list.appendChild(listItem(`Warnung: ${warning}`)));
    errors.slice(0, 4).forEach((error) => list.appendChild(listItem(`Fehler: ${error}`)));
  } catch (error) {
    setPill("#health-pill", "Health nicht erreichbar", "bad");
    $("#health-status").textContent = "FEHLER";
  }
}

async function loadSources() {
  try {
    const response = await fetch("/api/sources");
    const payload = await response.json();
    const counts = payload.status_counts || {};
    const summary = $("#source-summary");
    summary.replaceChildren(
      sourceBadge("aktiv", counts.active || 0, "ok"),
      sourceBadge("deaktiviert", counts.disabled || 0, "neutral"),
      sourceBadge("quarantined", counts.quarantined || 0, "warn")
    );
    setPill("#source-pill", `${payload.count} Quellen`, "ok");

    const list = $("#source-list");
    list.replaceChildren();
    payload.sources.slice(0, 10).forEach((source) => {
      const item = document.createElement("article");
      item.className = "source-item";
      const title = document.createElement("strong");
      const meta = document.createElement("span");
      const scopes = document.createElement("span");
      title.textContent = source.label || source.id;
      meta.textContent = `${source.id} · ${source.status} · ${source.trust_level || "trust offen"}`;
      scopes.textContent = (source.scopes || []).join(", ");
      item.append(title, meta, scopes);
      list.appendChild(item);
    });
  } catch (error) {
    setPill("#source-pill", "Quellenfehler", "bad");
  }
}

function setReportState(message, state = "neutral") {
  const node = $("#reports-state");
  if (!node) return;
  node.textContent = message;
  node.dataset.state = state;
}

function setReportPanelState(selector, state) {
  const panel = $(selector);
  if (!panel) return;
  if (state) {
    panel.dataset.state = state;
  } else {
    delete panel.dataset.state;
  }
}

function setReportPreviewPlaceholder(message, meta = "") {
  const title = $("#report-preview-title");
  const metaNode = $("#report-preview-meta");
  const frame = $("#report-preview-frame");
  const text = $("#report-preview-text");
  const openLink = $("#report-open-link");
  if (title) title.textContent = message;
  if (metaNode) {
    metaNode.textContent = meta || "HTML, JSON und TXT erscheinen direkt hier. PDF bleibt als Datei-Link verfuegbar.";
  }
  if (frame) {
    frame.hidden = true;
    frame.srcdoc = "";
  }
  if (text) {
    text.hidden = false;
    text.textContent = "Waehle links einen Bericht fuer die Vorschau.";
  }
  if (openLink) {
    openLink.hidden = true;
    openLink.removeAttribute("href");
  }
  setReportPanelState("#report-preview-panel", "idle");
  if (!activeHarmonizationJobId) {
    activeReportId = null;
    syncHarmonizationControls();
  }
}

function reportMetaLine(entry) {
  return `${entry.kind} Bericht`;
}

function reportSessionLine(entry) {
  const label = entry.session_label || entry.session_id;
  return label ? `Sitzung ${label}` : "Berichtsvorschau";
}

function renderReportPreview(entry, payload) {
  const title = $("#report-preview-title");
  const metaNode = $("#report-preview-meta");
  const frame = $("#report-preview-frame");
  const text = $("#report-preview-text");
  const openLink = $("#report-open-link");

  if (title) title.textContent = entry.file_name || entry.label;
  if (metaNode) {
    metaNode.textContent = `${reportSessionLine(entry)} · ${reportMetaLine(entry)} · ${payload.content_type}`;
  }
  if (openLink) {
    openLink.hidden = false;
    openLink.href = payload.file_url;
  }
  setReportPanelState("#report-preview-panel", payload.mode === "html" ? "html" : payload.mode);

  if (payload.mode === "html") {
    if (frame) {
      frame.hidden = false;
      frame.srcdoc = payload.content || "";
    }
    if (text) {
      text.hidden = true;
      text.textContent = "";
    }
    return;
  }

  if (frame) {
    frame.hidden = true;
    frame.srcdoc = "";
  }
  if (!text) return;
  text.hidden = false;
  text.textContent = payload.mode === "file"
    ? "PDF-Vorschau bleibt als Datei-Link verfuegbar. Nutze 'Datei oeffnen'."
    : (payload.content || "Keine Vorschau verfuegbar.");
}

async function previewReport(entry) {
  activeReportId = entry.id;
  setReportState("lade Vorschau");
  setReportPanelState("#report-preview-panel", "loading");
  try {
    const response = await fetch(`/api/reports/${encodeURIComponent(entry.id)}/preview`);
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(JSON.stringify(payload));
    }
    renderReportPreview(entry, payload);
    setReportState("Vorschau bereit", "ok");
    showHarmonizationState("Bericht bereit. Harmonisierung ist jetzt der finale Workflow-Schritt.", "ok");
    syncHarmonizationControls();
    if (currentStep < 8) {
      goToStep(8);
    }
  } catch (error) {
    setReportPreviewPlaceholder("Vorschaufehler", reportMetaLine(entry));
    $("#report-preview-text").textContent = String(error.message || error);
    setReportState("Vorschaufehler", "bad");
    showHarmonizationState("Bericht konnte nicht geladen werden.", "bad");
    setReportPanelState("#report-preview-panel", "error");
  }
}

function buildReportItem(entry) {
  const item = document.createElement("article");
  item.className = "report-item";

  const content = document.createElement("div");
  content.className = "report-item-copy";
  const title = document.createElement("strong");
  const meta = document.createElement("span");
  const helper = document.createElement("span");
  helper.className = "report-item-helper";
  title.textContent = entry.label || entry.file_name;
  meta.textContent = reportMetaLine(entry);
  helper.textContent = "Direkt im Browser pruefen oder Datei separat oeffnen.";
  content.append(title, meta, helper);

  const actions = document.createElement("div");
  actions.className = "report-actions";

  const previewButton = document.createElement("button");
  previewButton.type = "button";
  previewButton.className = "secondary-button";
  previewButton.textContent = "Vorschau";
  previewButton.addEventListener("click", () => previewReport(entry));

  const openLink = document.createElement("a");
  openLink.className = "secondary-button report-open-link";
  openLink.href = `/api/reports/${encodeURIComponent(entry.id)}/file`;
  openLink.target = "_blank";
  openLink.rel = "noopener noreferrer";
  openLink.textContent = "Datei oeffnen";

  actions.append(previewButton, openLink);
  item.append(content, actions);
  return item;
}

function renderReportList(payload) {
  const list = $("#report-list");
  if (!list) return;

  const clients = Array.isArray(payload.clients) ? payload.clients : [];
  setReportPanelState("#report-catalog-panel", clients.length ? "ready" : "empty");
  if (!clients.length) {
    const empty = document.createElement("p");
    empty.className = "empty-state";
    empty.textContent = "Noch keine Phase-1 Berichte in den konfigurierten Report-Roots gefunden.";
    list.replaceChildren(empty);
    setReportPreviewPlaceholder("Noch kein Bericht gewaehlt");
    return;
  }

  const nodes = clients.map((client) => {
    const section = document.createElement("section");
    section.className = "report-client-group";

    const title = document.createElement("h3");
    title.className = "report-client-title";
    title.textContent = client.label;

    const summary = document.createElement("p");
    summary.className = "report-client-summary";
    summary.textContent = `${client.file_count} Berichte in ${client.sessions?.length || 0} Sitzungen`;
    section.append(title, summary);

    (client.sessions || []).forEach((session) => {
      const sessionBlock = document.createElement("section");
      sessionBlock.className = "report-session-group";

      const sessionTitle = document.createElement("h4");
      sessionTitle.className = "report-session-title";
      sessionTitle.textContent = `Session ${session.label}`;
      const sessionMeta = document.createElement("p");
      sessionMeta.className = "report-session-meta";
      sessionMeta.textContent = `${(session.files || []).length} Dateien verfuegbar`;
      sessionBlock.append(sessionTitle, sessionMeta);

      (session.files || []).forEach((entry) => {
        sessionBlock.appendChild(buildReportItem(entry));
      });
      section.appendChild(sessionBlock);
    });
    return section;
  });

  list.replaceChildren(...nodes);
}

function findReportEntry(payload, reportId) {
  const clients = Array.isArray(payload.clients) ? payload.clients : [];
  for (const client of clients) {
    for (const session of client.sessions || []) {
      for (const entry of session.files || []) {
        if (entry.id === reportId) {
          return entry;
        }
      }
    }
  }
  return null;
}

function firstReportEntry(payload) {
  const clients = Array.isArray(payload.clients) ? payload.clients : [];
  for (const client of clients) {
    for (const session of client.sessions || []) {
      for (const entry of session.files || []) {
        return entry;
      }
    }
  }
  return null;
}

async function loadReports(preferredReportId = activeReportId, autoPreviewFirst = false) {
  setReportState("lade Berichte");
  try {
    const response = await fetch("/api/reports");
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(JSON.stringify(payload));
    }
    renderReportList(payload);
    setReportState(`${payload.count || 0} Berichte geladen`, "ok");
    const preferredEntry = preferredReportId ? findReportEntry(payload, preferredReportId) : null;
    if (preferredEntry) {
      await previewReport(preferredEntry);
      return;
    }
    if (autoPreviewFirst) {
      const firstEntry = firstReportEntry(payload);
      if (firstEntry) {
        await previewReport(firstEntry);
        return;
      }
    }
    syncHarmonizationControls();
  } catch (error) {
    const list = $("#report-list");
    if (list) {
      const empty = document.createElement("p");
      empty.className = "empty-state";
      empty.textContent = String(error.message || error);
      list.replaceChildren(empty);
    }
    setReportPanelState("#report-catalog-panel", "error");
    setReportPreviewPlaceholder("Noch kein Bericht gewaehlt");
    setReportState("Berichtsfehler", "bad");
    showHarmonizationState("Berichte konnten nicht geladen werden.", "bad");
  }
}

function renderResultMatrix(payload) {
  const list = $("#result-matrix-list");
  if (!list) return;
  const profiles = Array.isArray(payload.top_profiles) ? payload.top_profiles : [];
  const paths = payload.export_paths || {};
  if (!profiles.length) {
    const empty = document.createElement("p");
    empty.className = "empty-state";
    empty.textContent = "Noch keine Matrixdaten fuer diesen Scan verfuegbar.";
    list.replaceChildren(empty);
    return;
  }
  const nodes = profiles.map((profile) => {
    const item = document.createElement("article");
    item.className = "result-matrix-item";
    const title = document.createElement("strong");
    title.textContent = profile.profile || "Profil";
    const score = document.createElement("span");
    score.textContent = `Score ${Number(profile.score || 0).toFixed(2)}`;
    const resonances = document.createElement("p");
    resonances.textContent = (profile.top_resonances || [])
      .map((entry) => `${entry.label} (${Number(entry.score || 0).toFixed(2)})`)
      .join(", ") || "Keine Resonanzen gelistet.";
    item.append(title, score, resonances);
    return item;
  });
  if (Object.keys(paths).length) {
    const exportItem = document.createElement("article");
    exportItem.className = "result-matrix-item";
    const title = document.createElement("strong");
    title.textContent = "Exportpfade";
    const details = document.createElement("p");
    details.textContent = Object.entries(paths).map(([key, value]) => `${key}: ${value}`).join(" - ");
    exportItem.append(title, details);
    nodes.push(exportItem);
  }
  list.replaceChildren(...nodes);
}

function setResultMatrixEmpty(message) {
  const list = $("#result-matrix-list");
  if (!list) return;
  const empty = document.createElement("p");
  empty.className = "empty-state";
  empty.textContent = message;
  list.replaceChildren(empty);
}

function resetResultMatrixForNewScan() {
  activeJobId = null;
  syncResultMatrixControls();
  setResultMatrixEmpty("Analyse startet. Matrix wird nach Abschluss geladen.");
  const state = $("#result-matrix-state");
  if (state) {
    state.textContent = "Matrix wartet auf Abschluss";
    state.dataset.state = "neutral";
  }
}

async function loadResultMatrix(jobId = activeJobId) {
  const state = $("#result-matrix-state");
  if (!jobId) {
    if (state) {
      state.textContent = "Noch kein Scan-Ergebnis geladen";
      state.dataset.state = "neutral";
    }
    setResultMatrixEmpty("Noch kein Scan-Ergebnis geladen.");
    return;
  }
  if (state) {
    state.textContent = "Matrix wird geladen";
    state.dataset.state = "warn";
  }
  try {
    const response = await fetch("/api/scan/jobs/" + encodeURIComponent(jobId) + "/results");
    const payload = await response.json();
    if (!response.ok) throw new Error(JSON.stringify(payload));
    renderResultMatrix(payload);
    if (state) {
      state.textContent = "Matrix bereit";
      state.dataset.state = "ok";
    }
  } catch (error) {
    if (state) {
      state.textContent = "Matrixfehler";
      state.dataset.state = "bad";
    }
    setResultMatrixEmpty("Matrix konnte nicht geladen werden.");
  }
}

function formHarmonizationPayload() {
  const form = $("#harmonization-form");
  const data = new FormData(form);
  return {
    intention: String(data.get("intention") || "").trim() || "harmonization",
    target_frequency: Number(data.get("target_frequency") || 432),
    duration_minutes: Number(data.get("duration_minutes") || 5),
    use_cpu: data.get("use_cpu") === "on",
    use_gpu: data.get("use_gpu") === "on",
    use_ram: data.get("use_ram") === "on",
    use_websocket: data.get("use_websocket") === "on",
    use_driver_layer: data.get("use_driver_layer") === "on"
  };
}

function updateHarmonizationStatus(payload) {
  const panel = $("#harmonization-status-panel");
  const label = $("#harmonization-status-label");
  const fill = $("#harmonization-progress-fill");
  if (panel) panel.hidden = false;
  if (label) {
    label.textContent = jobStateLabel(payload.status);
    label.dataset.state = jobStateTone(payload.status);
  }
  $("#harmonization-job-id-label").textContent = payload.job_id || "-";
  $("#harmonization-mode-label").textContent = harmonizationModeLabel(payload.intention || payload.mode);
  $("#harmonization-phase-label").textContent = payload.phase || "-";
  const percent = harmonizationProgressPercent(payload);
  $("#harmonization-progress-label").textContent = percent === null ? "-" : `${percent.toFixed(1)}%`;
  $("#harmonization-cycles-label").textContent = payload.total_cycles
    ? `${payload.cycles_completed || 0} / ${payload.total_cycles}`
    : String(payload.cycles_completed || 0);
  $("#harmonization-error-label").textContent = payload.error_message || "kein Fehler";
  if (fill) {
    fill.style.width = `${percent ?? 0}%`;
  }
  syncHarmonizationControls();
}

async function pollHarmonizationJob(jobId = activeHarmonizationJobId) {
  if (!jobId) return;
  try {
    const response = await fetch(`/api/harmonization/jobs/${encodeURIComponent(jobId)}`);
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(JSON.stringify(payload));
    }
    activeHarmonizationJobId = payload.job_id || jobId;
    updateHarmonizationStatus(payload);
    const done = payload.status === "completed" || payload.status === "failed" || payload.status === "error" || payload.status === "stopped";
    if (!done) {
      harmonizationPollTimer = window.setTimeout(() => pollHarmonizationJob(jobId), 1500);
      return;
    }
    showHarmonizationState(
      payload.status === "completed"
        ? "Harmonisierung abgeschlossen."
        : payload.status === "stopped"
          ? "Harmonisierung gestoppt."
          : "Harmonisierung beendet.",
      jobStateTone(payload.status)
    );
  } catch (error) {
    updateHarmonizationStatus({
      job_id: jobId,
      status: "failed",
      intention: null,
      phase: "error",
      cycles_completed: 0,
      error_message: String(error.message || error)
    });
    showHarmonizationState("Statusfehler bei der Harmonisierung.", "bad");
  }
}

async function startHarmonizationJob() {
  if (!activeReportId) {
    showHarmonizationState("Bitte zuerst einen Bericht in der Vorschau oeffnen.", "warn");
    return;
  }
  if (!$("#harmonization-form")?.reportValidity()) {
    showHarmonizationState("Harmonisierungsparameter pruefen.", "warn");
    return;
  }
  if (harmonizationPollTimer) {
    window.clearTimeout(harmonizationPollTimer);
    harmonizationPollTimer = null;
  }
  showHarmonizationState("Harmonisierung startet.", "warn");
  updateHarmonizationStatus({
    job_id: "wird erzeugt",
    status: "running",
    intention: formHarmonizationPayload().intention,
    phase: "preparing",
    cycles_completed: 0,
    total_cycles: 0,
    error_message: null,
    progress_percent: 0
  });
  try {
    const response = await fetch("/api/harmonization/jobs", {
      method: "POST",
      headers: {"content-type": "application/json"},
      body: JSON.stringify(formHarmonizationPayload())
    });
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(JSON.stringify(payload));
    }
    activeHarmonizationJobId = payload.job_id;
    updateHarmonizationStatus(payload);
  showHarmonizationState(`Harmonisierung ${harmonizationModeLabel(payload.intention || payload.mode)} laeuft.`, "warn");
    await pollHarmonizationJob(activeHarmonizationJobId);
  } catch (error) {
    updateHarmonizationStatus({
      job_id: activeHarmonizationJobId || "-",
      status: "failed",
      intention: formHarmonizationPayload().intention,
      phase: "error",
      cycles_completed: 0,
      error_message: String(error.message || error)
    });
    showHarmonizationState("Harmonisierung konnte nicht gestartet werden.", "bad");
  }
}

async function refreshHarmonizationJob() {
  await pollHarmonizationJob();
}

async function stopHarmonizationJob() {
  if (!activeHarmonizationJobId) return;
  if (harmonizationPollTimer) {
    window.clearTimeout(harmonizationPollTimer);
    harmonizationPollTimer = null;
  }
  try {
    const response = await fetch(`/api/harmonization/jobs/${encodeURIComponent(activeHarmonizationJobId)}/stop`, {
      method: "POST"
    });
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(JSON.stringify(payload));
    }
    updateHarmonizationStatus(payload);
    showHarmonizationState("Harmonisierung gestoppt.", "ok");
  } catch (error) {
    showHarmonizationState("Harmonisierung konnte nicht gestoppt werden.", "bad");
  }
}

async function uploadImageReference() {
  const input = $("#image-upload");
  const state = $("#image-upload-state");
  const meta = $("#image-upload-meta");
  const pathInput = document.querySelector('input[name="image_path"]');
  const file = input?.files?.[0];
  if (!file) return;
  if (pathInput) pathInput.value = "";
  saveClientDraftIfEnabled();
  if (state) {
    state.textContent = "Upload laeuft";
    state.dataset.state = "warn";
  }
  const data = new FormData();
  data.append("file", file);
  try {
    const response = await fetch("/api/uploads/image-reference", {
      method: "POST",
      body: data
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(JSON.stringify(payload));
    if (pathInput) pathInput.value = payload.image_path || "";
    if (state) {
      state.textContent = "Bildreferenz bereit";
      state.dataset.state = "ok";
    }
    if (meta) {
      meta.textContent = `${payload.file_name} - ${payload.size} Bytes - ${payload.content_type}`;
    }
    saveClientDraftIfEnabled();
  } catch (error) {
    if (pathInput) pathInput.value = "";
    if (state) {
      state.textContent = "Uploadfehler";
      state.dataset.state = "bad";
    }
    if (meta) meta.textContent = String(error.message || error);
    saveClientDraftIfEnabled();
  }
}

function formPayload() {
  const form = $("#scan-form");
  const data = new FormData(form);
  return {
    last_name: String(data.get("last_name") || "").trim(),
    first_name: String(data.get("first_name") || "").trim(),
    birth_date: String(data.get("birth_date") || "").trim(),
    birth_place: String(data.get("birth_place") || "").trim(),
    image_path: String(data.get("image_path") || "").trim() || null,
    focus: String(data.get("focus") || "").trim(),
    profile_level: Number(data.get("profile_level") || 3),
    top_n: Number(data.get("top_n") || 5),
    profile_template: String(data.get("profile_template") || "").trim() || "phase1-default",
    entropy_mode: String(data.get("entropy_mode") || "").trim() || "legacy",
    adaptive_limits: data.get("adaptive_limits") === "on",
    consent_local: Boolean($("#consent-local")?.checked),
    consent_safety: Boolean($("#consent-safety")?.checked)
  };
}

async function previewScan() {
  if (!$("#consent-local")?.checked || !$("#consent-safety")?.checked) {
    showInlineState("Compliance bestaetigen", "warn");
    goToStep(1);
    return;
  }
  if (!$("#scan-form").reportValidity()) {
    showInlineState("Eingaben pruefen", "warn");
    return;
  }

  showInlineState("erstelle Vorschau");
  try {
    const response = await fetch("/api/scan/preview", {
      method: "POST",
      headers: {"content-type": "application/json"},
      body: JSON.stringify(formPayload())
    });
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(JSON.stringify(payload));
    }
    renderLauncherPreview(payload);
    showInlineState("Vorschau bereit", "ok");
  } catch (error) {
    $("#command-preview").textContent = String(error.message || error);
    showInlineState("Vorschaufehler", "bad");
  }
}

async function pollScanJob(jobId = activeJobId) {
  if (!jobId) return;
  try {
    const response = await fetch("/api/scan/jobs/" + encodeURIComponent(jobId));
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(JSON.stringify(payload));
    }
    updateJobStatus(payload);
    const done = payload.status === "completed" || payload.status === "failed";
    if (!done) {
      jobPollTimer = window.setTimeout(() => pollScanJob(jobId), 1500);
    } else {
      showInlineState(payload.status === "completed" ? "Analyse abgeschlossen" : "Analyse fehlgeschlagen", jobStateTone(payload.status));
      if (payload.status === "completed") {
        await loadResultMatrix(jobId);
        await loadReports(null, true);
        goToStep(7);
      }
    }
  } catch (error) {
    updateJobStatus({
      job_id: jobId,
      status: "failed",
      returncode: "-",
      stderr_tail: String(error.message || error)
    });
    showInlineState("Statusfehler", "bad");
  }
}

async function startScanJob() {
  if (!$("#consent-local")?.checked || !$("#consent-safety")?.checked) {
    showInlineState("Compliance bestaetigen", "warn");
    goToStep(1);
    return;
  }
  if (!$("#scan-form").reportValidity()) {
    showInlineState("Eingaben pruefen", "warn");
    return;
  }

  if (jobPollTimer) {
    window.clearTimeout(jobPollTimer);
    jobPollTimer = null;
  }

  resetResultMatrixForNewScan();
  showInlineState("Analyse startet");
  updateJobStatus({
    status: "running",
    job_id: "wird erzeugt",
    returncode: "-",
    stdout_tail: "",
    stderr_tail: "",
    progress_percent: null,
    current_phase: null,
    current_substep: null,
    completed_substeps: []
  });
  try {
    const response = await fetch("/api/scan/jobs", {
      method: "POST",
      headers: {"content-type": "application/json"},
      body: JSON.stringify(formPayload())
    });
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(JSON.stringify(payload));
    }
    activeJobId = payload.job_id;
    syncResultMatrixControls();
    renderLauncherPreview(payload);
    updateJobStatus(payload);
    showInlineState("Analyse laeuft", "warn");
    await pollScanJob(activeJobId);
  } catch (error) {
    updateJobStatus({
      job_id: activeJobId || "-",
      status: "failed",
      returncode: "-",
      stderr_tail: String(error.message || error)
    });
    showInlineState("Startfehler", "bad");
  }
}

function clientDraftPayload() {
  const form = $("#scan-form");
  if (!form) return {};
  const data = new FormData(form);
  return {
    last_name: String(data.get("last_name") || ""),
    first_name: String(data.get("first_name") || ""),
    birth_date: String(data.get("birth_date") || ""),
    birth_place: String(data.get("birth_place") || ""),
    focus: String(data.get("focus") || ""),
    main_symptom: String(data.get("main_symptom") || ""),
    notes: String(data.get("notes") || ""),
    profile_level: String(data.get("profile_level") || "3"),
    top_n: String(data.get("top_n") || "5"),
    profile_template: String(data.get("profile_template") || "phase1-default"),
    entropy_mode: String(data.get("entropy_mode") || "legacy"),
    image_path: String(data.get("image_path") || ""),
    adaptive_limits: data.get("adaptive_limits") === "on"
  };
}

function applyClientDraft(draft) {
  Object.entries(draft || {}).forEach(([name, value]) => {
    const field = document.querySelector(`[name="${name}"]`);
    if (!field) return;
    if (field.type === "checkbox") {
      field.checked = Boolean(value);
    } else {
      field.value = String(value == null ? "" : value);
    }
  });
}

function saveClientDraftIfEnabled() {
  const enabled = Boolean($("#client-storage-opt-in")?.checked);
  if (!enabled) {
    setClientStorageState("keine Speicherung aktiv", "neutral");
    return;
  }
  if (!safeLocalStorageSet(CLIENT_DRAFT_KEY, JSON.stringify(clientDraftPayload()))) return;
  setClientStorageState("lokaler Entwurf gespeichert", "ok");
}

function restoreClientDraft() {
  const raw = safeLocalStorageGet(CLIENT_DRAFT_KEY);
  if (!raw) return;
  try {
    applyClientDraft(JSON.parse(raw));
    const optIn = $("#client-storage-opt-in");
    if (optIn) optIn.checked = true;
    setClientStorageState("lokaler Entwurf geladen", "ok");
  } catch (error) {
    safeLocalStorageRemove(CLIENT_DRAFT_KEY);
  }
}

function clearClientDraft() {
  if (!safeLocalStorageRemove(CLIENT_DRAFT_KEY)) return;
  const optIn = $("#client-storage-opt-in");
  if (optIn) optIn.checked = false;
  setClientStorageState("lokaler Entwurf geloescht", "neutral");
}

function bindWorkflow() {
  $$(".wizard-step").forEach((step) => {
    step.addEventListener("click", () => {
      goToStep(Number(step.dataset.step || 0));
    });
  });
  $("#btn-prev")?.addEventListener("click", () => navigate(-1));
  $("#btn-next")?.addEventListener("click", () => navigate(1));
  $("#preview-button")?.addEventListener("click", previewScan);
  $("#start-analysis-button")?.addEventListener("click", startScanJob);
  $("#refresh-reports-button")?.addEventListener("click", () => loadReports());
  $("#image-upload")?.addEventListener("change", uploadImageReference);
  $("#client-storage-opt-in")?.addEventListener("change", saveClientDraftIfEnabled);
  $("#client-storage-clear")?.addEventListener("click", clearClientDraft);
  $("#refresh-result-matrix-button")?.addEventListener("click", () => loadResultMatrix());
  $("#scan-form")?.addEventListener("input", saveClientDraftIfEnabled);
  $("#harmonization-start-button")?.addEventListener("click", startHarmonizationJob);
  $("#harmonization-refresh-button")?.addEventListener("click", refreshHarmonizationJob);
  $("#harmonization-stop-button")?.addEventListener("click", stopHarmonizationJob);
  document.addEventListener("keydown", (event) => {
    const target = event.target;
    const tag = target?.tagName || "";
    const isTypingTarget = tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT" || target?.isContentEditable;
    if (isTypingTarget) {
      return;
    }
    if (event.key === "ArrowRight") {
      event.preventDefault();
      navigate(1);
    } else if (event.key === "ArrowLeft") {
      event.preventDefault();
      navigate(-1);
    }
  });
  restoreClientDraft();
  updateProgress();
  syncHarmonizationControls();
  syncResultMatrixControls();
}

bindWorkflow();
loadHealth();
loadSources();
loadReports();

/* app.js — Bootstrap fuer die Morphic Operator Workbench.
 *
 * Verdrahtet workbench-state.js, workbench-api.js und workbench-render.js.
 * Enthaelt die Event-Handler und die Scan-/Harmonisierungs-/Reports-Logik
 * aus dem bisherigen 8-Step-Wizard, jetzt im 10-Phasen-Kontext.
 */

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => Array.from(document.querySelectorAll(selector));

const HARMONIZATION_MODE_LABELS = {
  healing: "Healing", clearing: "Clearing", protection: "Protection",
  transformation: "Transformation", harmonization: "Harmonization", activation: "Activation"
};

const FALLBACK_STEPS = [
  {id:"runtime",label:"Vorpruefung"},{id:"client",label:"Klient / Kontext"},
  {id:"focus",label:"Fokus & Zielsetzung"},{id:"profile",label:"Analyseprofil"},
  {id:"hardware",label:"Hardware & Realtime"},{id:"review",label:"Review & Freigabe"},
  {id:"run",label:"Analyse-Lauf"},{id:"results",label:"Ergebnis-Uebersicht"},
  {id:"details",label:"Technische Details"},{id:"harmonize",label:"Harmonisierung & Abschluss"},
  {id:"finalize",label:"Berichtskatalog & Export"},
];

const SCAN_PROFILE_CATALOG_LOADING_TEXT = "Registry-Prüfung läuft; Scanprofil-Pool wird geladen. Keine Wirkung auf diesen Scan, Profilpool oder Score. Externe Scanprofile erst nach validierter Catalog-Freigabe in Gate 14.";
const SCAN_PROFILE_CATALOG_INVARIANT_TEXT = "Keine Wirkung auf diesen Scan, Profilpool oder Score. Externe Scanprofile erst nach validierter Catalog-Freigabe in Gate 14.";
const SCAN_PROFILE_ACTION_LOADING_TEXT = "Scanprofil-Pool wird geladen; Vorschau und Start bleiben gesperrt.";
const SCAN_PROFILE_ACTION_READY_TEXT = "Scanprofil-Pool ist für das gewählte Level bestätigt.";
const SCAN_PROFILE_ACTION_ERROR_TEXT = "Scanprofil-Pool konnte nicht bestätigt werden; Vorschau und Start bleiben gesperrt.";

window.MorphicWorkbenchFocusHistoryStore = {
  get(key) {
    try {
      return window.localStorage.getItem(key);
    } catch (_) {
      return null;
    }
  },
  set(key, value) {
    try {
      window.localStorage.setItem(key, value);
    } catch (_) {}
  },
  remove(key) {
    try {
      window.localStorage.removeItem(key);
    } catch (_) {}
  },
};

let jobPollTimer = null;
let harmonizationPollTimer = null;
let caseGeneration = 0;
let inlineStateRevision = 0;
let scanPollDegradation = null;
let harmonizationPollDegradation = null;
let scanPollInFlight = null;
let scanStopInFlight = null;
let terminalScanAuthority = null;
let scanProfileCatalogRequestToken = 0;
let scanPreviewRequestToken = 0;
let scanResultsRequestToken = 0;
let hardwareTruthRequestToken = 0;
let emfTelemetryStatusRequestToken = 0;
let harmonizationPollInFlight = null;
const MAX_POLL_FAILURES = 5;
const EMF_TIMEOUT_RECONCILIATION_DELAYS_MS = Object.freeze([0, 100, 250, 500]);
const TERMINAL_SCAN_STATUSES = new Set(["completed", "failed", "stopped"]);
const AUTOMATIC_SCAN_STATUSES = new Set(["starting", "pending", "running"]);

function pollRetryDelay(failureCount) {
  return Math.min(2000 * (2 ** Math.max(0, failureCount - 1)), 30000);
}
let reportAuthority = createReportAuthorityState(caseGeneration);
let workbenchWired = false;

/* ── Utility ──────────────────────────────────────────────────────── */

function setPill(id, text, state) {
  const node = $(id);
  if (!node) return;
  node.textContent = text;
  node.className = `pill ${state}`;
}

function startOperationId(kind) {
  const state = window.MorphicWorkbenchState;
  const field = kind === "scan"
    ? "scanStartOperationId"
    : "harmonizationStartOperationId";
  const existing = readExistingStartOperationId(kind);
  if (existing) return existing;
  const storageKey = `morphic_${kind}_start_operation_id`;
  const randomPart = typeof crypto !== "undefined" && typeof crypto.randomUUID === "function"
    ? crypto.randomUUID()
    : `${Date.now()}-${Math.random().toString(16).slice(2)}`;
  const operationId = `${kind}-${randomPart}`;
  state[field] = operationId;
  try {
    window.localStorage.setItem(storageKey, operationId);
  } catch (_) {
    /* in-memory authority remains valid */
  }
  return operationId;
}

function readExistingStartOperationId(kind) {
  const state = window.MorphicWorkbenchState;
  const field = kind === "scan"
    ? "scanStartOperationId"
    : "harmonizationStartOperationId";
  const inMemory = String(state[field] || "").trim();
  if (inMemory) return inMemory;
  try {
    const stored = String(
      window.localStorage.getItem(`morphic_${kind}_start_operation_id`) || ""
    ).trim();
    if (stored) {
      state[field] = stored;
      return stored;
    }
  } catch (_) {
    /* localStorage unavailable: no persisted authority can be read */
  }
  return null;
}

function clearStartOperationId(kind) {
  const state = window.MorphicWorkbenchState;
  const field = kind === "scan"
    ? "scanStartOperationId"
    : "harmonizationStartOperationId";
  state[field] = null;
  try {
    window.localStorage.removeItem(`morphic_${kind}_start_operation_id`);
  } catch (_) {
    /* no persistent operation key was available */
  }
}

function shouldRetainStartOperation(error) {
  if (!error?.status) return true;
  return error.startOperationDisposition !== "safe-to-replace";
}

function hasUnresolvedStartOperation(kind) {
  return readExistingStartOperationId(kind) !== null;
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
  inlineStateRevision += 1;
  if (!node) return inlineStateRevision;
  node.textContent = message;
  node.className = `inline-state ${state}`;
  return inlineStateRevision;
}

function showWizardNavigationState(message, state = "neutral") {
  const node = $("#wizard-navigation-state");
  if (!node) return;
  node.textContent = message;
  node.className = `inline-state ${state}`;
}

function showReportPreviewState(message, state = "neutral") {
  const node = $("#report-preview-state");
  if (!node) return;
  node.textContent = message;
  node.className = `inline-state ${state}`;
}

function clearOwnedPollDegradation(owner, jobId, generation) {
  const degradation = owner === "scan" ? scanPollDegradation : harmonizationPollDegradation;
  if (!degradation || degradation.jobId !== jobId || degradation.generation !== generation) return;
  if (degradation.revision === inlineStateRevision) showInlineState("", "neutral");
  if (owner === "scan") scanPollDegradation = null;
  else harmonizationPollDegradation = null;
}

function apiErrorMessage(error, fallback) {
  const detail = typeof error?.message === "string" ? error.message.trim() : "";
  return detail ? `${fallback}: ${detail}` : fallback;
}

function scanProfileCatalogErrorMessage(error) {
  const status = Number(error?.status);
  const errorClass = Number.isInteger(status) && status >= 400 && status <= 599
    ? `HTTP ${status}`
    : "unbekannter Ladefehler";
  return `Scanprofil-Pool konnte nicht geladen werden (${errorClass}). Bitte erneut versuchen.`;
}

function isOptionalRunTraceError(error) {
  return ![401, 403].includes(Number(error?.status));
}

function healthProfileCount(profiles) {
  if (typeof profiles === "number") return profiles;
  return profiles?.total_profiles ?? profiles?.count ?? "-";
}

function healthDatabaseEntries(databases) {
  if (Array.isArray(databases)) return databases;
  const entries = databases?.databases;
  if (Array.isArray(entries)) return entries;
  if (entries && typeof entries === "object") return Object.values(entries);
  return [];
}

function scanFormControl(fieldName) {
  return document.querySelector(`[form="scan-form"][name="${fieldName}"]`)
    || document.querySelector(`#scan-form [name="${fieldName}"]`);
}

function scanProfilePoolReadyForCurrentLevel() {
  const state = window.MorphicWorkbenchState;
  const level = Number(scanFormControl("profile_level")?.value || 3);
  const fingerprint = String(
    state.scanProfileCatalog?.pool_authority?.fingerprint || ""
  );
  return !state.resetInProgress
    && state.scanProfileCatalogStatus === "ready"
    && Number(state.scanProfileCatalogLevel) === level
    && Number(state.scanProfileCatalog?.profile_level) === level
    && /^[0-9a-f]{64}$/.test(fingerprint);
}

function scanProfilePoolSupportsCurrentTopN() {
  const state = window.MorphicWorkbenchState;
  const selectedTopN = Number(scanFormControl("top_n")?.value);
  const poolCount = state.scanProfileCatalog?.internal?.count;
  return Number.isFinite(selectedTopN)
    && Number.isInteger(selectedTopN)
    && selectedTopN >= 1
    && Number.isFinite(poolCount)
    && Number.isInteger(poolCount)
    && poolCount >= 1
    && selectedTopN <= poolCount;
}

function wireScanProfileTopNControl() {
  const control = scanFormControl("top_n");
  if (!control || control.morphicTopNWired === true) return;
  control.morphicTopNWired = true;
  control.addEventListener("change", () => {
    updateScanActionAvailability();
    const state = window.MorphicWorkbenchState;
    if (state.currentStepIndex === 5) {
      window.MorphicWorkbenchRender.renderReviewCards(
        formScanPayload(),
        state.hardwareTruth,
        state.scanProfileCatalog
      );
    }
  });
}

function updateScanProfileTopNOptions() {
  const state = window.MorphicWorkbenchState;
  const select = scanFormControl("top_n");
  if (!select) return;
  wireScanProfileTopNControl();
  const poolCount = state.scanProfileCatalog?.internal?.count;
  const hasConfirmedCount = state.scanProfileCatalogStatus === "ready"
    && Number.isFinite(poolCount)
    && Number.isInteger(poolCount)
    && poolCount >= 1;
  Array.from(select.options || []).forEach((option) => {
    option.disabled = hasConfirmedCount && Number(option.value) > poolCount;
  });
}

function updateScanActionAvailability() {
  const state = window.MorphicWorkbenchState;
  const poolReady = scanProfilePoolReadyForCurrentLevel()
    && scanProfilePoolSupportsCurrentTopN();
  const preview = $("#preview-button");
  const start = $("#start-analysis-button");
  if (preview) {
    preview.disabled = !poolReady || state.scanStartPending || state.scanRunActive;
  }
  if (start) {
    start.disabled = !poolReady || state.scanStartPending || state.scanRunActive;
  }
}

function scanProfileCatalogMayOwnInlineState() {
  const state = window.MorphicWorkbenchState;
  return !state.resetInProgress && !state.scanStartPending && !state.scanRunActive;
}

function scanPreviewRequestIsCurrent(requestToken, generation, payloadSnapshot) {
  const state = window.MorphicWorkbenchState;
  return requestToken === scanPreviewRequestToken
    && generation === caseGeneration
    && !state.scanStartPending
    && !state.scanRunActive
    && scanProfilePoolReadyForCurrentLevel()
    && JSON.stringify(formScanPayload()) === payloadSnapshot;
}

function formHarmonizationPayload() {
  const form = $("#harmonization-form");
  if (!form) return {};
  const data = new FormData(form);
  const pulseSeconds = parseFloat(data.get("pulse_seconds") || "3");
  const pauseSeconds = parseFloat(data.get("pause_seconds") || "2");
  const durationFactor = parseInt(data.get("duration_factor") || "1", 10);
  return {
    intention: String(data.get("intention") || "").trim() || "harmonization",
    target_frequency: parseFloat(data.get("target_frequency") || "432"),

    use_cpu: data.get("use_cpu") === "on",
    use_gpu: data.get("use_gpu") === "on",
    use_ram: data.get("use_ram") === "on",
    use_websocket: data.get("use_websocket") === "on",
    use_driver_layer: data.get("use_driver_layer") === "on",
    pulse_seconds: pulseSeconds,
    pause_seconds: pauseSeconds,
    duration_factor: durationFactor,

    report_id: window.MorphicWorkbenchState?.activeReportId || "",
    workbench_mode: window.MorphicWorkbenchState?.workbenchMode || "standard",
  };
}

function formScanPayload(options = {}) {
  const form = $("#scan-form");
  if (!form) return {};
  const data = new FormData(form);
  const profileLevel = parseInt(data.get("profile_level") || "3", 10);
  const selectedTopN = Number(scanFormControl("top_n")?.value);
  const state = window.MorphicWorkbenchState;
  const payload = {
    last_name: String(data.get("last_name") || "").trim(),
    first_name: String(data.get("first_name") || "").trim(),
    birth_date: String(data.get("birth_date") || "").trim(),
    birth_place: String(data.get("birth_place") || "").trim(),
    focus: String(data.get("focus") || "").trim(),
    main_symptom: String(data.get("main_symptom") || "").trim(),
    profile_level: profileLevel,
    top_n: selectedTopN,
    profile_template: String(data.get("profile_template") || "").trim() || "phase1-default",
    entropy_mode: String(data.get("entropy_mode") || "").trim() || "legacy",
    image_path: String(data.get("image_path") || "").trim() || null,
    adaptive_limits: data.get("adaptive_limits") === "on",
    local_ai_enabled: data.get("local_ai_enabled") === "on",
    planetary_vector_enabled: data.get("planetary_vector_enabled") === "on",
    planet_type: String(data.get("planet_type") || "").trim(),
    consent_local: $("#consent-local")?.checked || false,
    consent_safety: $("#consent-safety")?.checked || false,
    workbench_mode: state.workbenchMode || "standard",
    scan_profile_pool_fingerprint: scanProfilePoolReadyForCurrentLevel()
      ? String(state.scanProfileCatalog.pool_authority.fingerprint)
      : "",
  };
  if (options.includeGroupActivation === true) {
    const activationEnabled = $("#group-scan-activation-enabled")?.checked === true;
    const draftId = String($("#group-scan-draft-id")?.value || "").trim();
    if (activationEnabled && draftId) payload.group_draft_id = draftId;
  }
  return payload;
}

function clientContextDraftPayload() {
  const form = $("#scan-form");
  if (!form) return {};
  const data = new FormData(form);
  return {
    last_name: String(data.get("last_name") || "").trim(),
    first_name: String(data.get("first_name") || "").trim(),
    birth_date: String(data.get("birth_date") || "").trim(),
    birth_place: String(data.get("birth_place") || "").trim(),
    birth_time: String(data.get("birth_time") || "").trim(),
    email: String(data.get("email") || "").trim(),
    notes: String(data.get("notes") || "").trim(),
  };
}

function showClientContextState(message, state = "neutral") {
  const node = $("#client-context-state");
  if (!node) return;
  node.textContent = message;
  node.className = `inline-state ${state}`;
}

async function loadClientContextDraft(generation = caseGeneration) {
  try {
    const stored = await window.MorphicWorkbenchApi.loadDraft();
    if (generation !== caseGeneration) return;
    const draft = stored && stored.draft ? stored.draft : {};
    for (const fieldName of ["birth_time", "email", "notes"]) {
      const input = scanFormControl(fieldName);
      if (input && typeof draft[fieldName] === "string") input.value = draft[fieldName];
    }
    if (Object.values(draft).some((value) => String(value || "").trim())) {
      showClientContextState("Lokaler Kontextentwurf geladen", "neutral");
    }
  } catch (e) {
    if (generation !== caseGeneration) return;
    showClientContextState("Lokaler Kontextentwurf nicht verfuegbar", "neutral");
  }
}

function validateScanPayload(payload, options = {}) {
  const requiredFields = [
    ["last_name", "Nachname"],
    ["first_name", "Vorname"],
    ["birth_date", "Geburtsdatum"],
    ["birth_place", "Geburtsort"],
    ["focus", "Fokus"],
  ];
  const missing = requiredFields
    .filter(([field]) => !String(payload[field] || "").trim())
    .map(([, label]) => label);
  if (missing.length) return `Pflichtfeld(er) ausfüllen: ${missing.join(", ")}.`;
  if (!/^\d{8}$/.test(payload.birth_date)) return "Geburtsdatum im Format DDMMYYYY eingeben.";
  const currentFingerprint = String(
    window.MorphicWorkbenchState.scanProfileCatalog?.pool_authority?.fingerprint || ""
  );
  const currentLevel = Number(scanFormControl("profile_level")?.value || 3);
  if (
    !scanProfilePoolReadyForCurrentLevel()
    || Number(payload.profile_level) !== currentLevel
    || payload.scan_profile_pool_fingerprint !== currentFingerprint
  ) {
    return "Scanprofil-Pool ist für das gewählte Level nicht bereit. Bitte neu laden und erneut prüfen.";
  }
  if (
    !scanProfilePoolSupportsCurrentTopN()
    || Number(payload.top_n) !== Number(scanFormControl("top_n")?.value)
  ) {
    return "Top-N überschreitet den bestätigten Scanprofil-Pool. Bitte Auswahl anpassen.";
  }
  if (!payload.consent_local) return "Lokale Verarbeitung und Berichtserzeugung bestaetigen";
  if (!payload.consent_safety) return "Wellbeing-Hinweis akzeptieren";
  if (
    options.includeGroupActivation === true
    && $("#group-scan-activation-enabled")?.checked === true
    && !payload.group_draft_id
  ) return "Für die bewusst angeforderte Gruppenwirkung einen Gruppenentwurf auswählen.";
  return null;
}

function phaseReadiness(index) {
  const state = window.MorphicWorkbenchState;
  if (state.scanStartPending) {
    return "Analyse-Start wird bestätigt. Navigation bleibt bis zur Serverantwort gesperrt.";
  }
  if (index <= 1) return null;
  const payload = formScanPayload({includeGroupActivation: true});
  const identityMissing = ["last_name", "first_name", "birth_date", "birth_place"]
    .some((field) => !String(payload[field] || "").trim());
  if (identityMissing) return "Bitte zuerst die Pflichtfelder der Klientenaufnahme ausfuellen.";
  if (!/^\d{8}$/.test(payload.birth_date)) return "Bitte zuerst ein gueltiges Geburtsdatum im Format DDMMYYYY eingeben.";
  if (!payload.consent_local || !payload.consent_safety) return "Bitte zuerst beide Einwilligungen in Phase 2 bestaetigen.";
  if (index >= 3 && !payload.focus) return "Bitte zuerst einen Fokus in Phase 3 festlegen.";
  if (index >= 6 && !state.activeJobId) return "Bitte die Analyse in Phase 6 pruefen und starten.";
  if (index >= 7 && !state.scanResults) return "Bitte den Analyse-Lauf zuerst erfolgreich abschliessen.";
  if (index >= 10 && !state.activeReportId) return "Bitte zuerst einen Bericht in Phase 10 auswaehlen.";
  return null;
}

window.MorphicWorkbenchCanEnterStep = phaseReadiness;
window.MorphicWorkbenchOnNavigationBlocked = (message) => showWizardNavigationState(message, "bad");

function statusLabel(status) {
  if (status === "starting") return "startet";
  if (status === "pending") return "wartet";
  if (status === "running") return "laeuft";
  if (status === "completed") return "abgeschlossen";
  if (status === "stopped") return "gestoppt";
  if (status === "error") return "fehler";
  if (status === "failed") return "fehlgeschlagen";
  if (status === "authority_ambiguous") return "Autoritaet ungeklaert";
  if (status === "rollback_failed") return "Stopp nicht bestaetigt";
  return typeof status === "string" && status.trim() ? status : "unbekannt";
}

function isTerminalScanStatus(status) {
  return typeof status === "string" && TERMINAL_SCAN_STATUSES.has(status);
}

function isAutomaticScanStatus(status) {
  return typeof status === "string" && AUTOMATIC_SCAN_STATUSES.has(status);
}

function terminalScanAuthorityStatus(jobId, generation) {
  const key = `${generation}:${jobId}`;
  return terminalScanAuthority?.key === key ? terminalScanAuthority.status : null;
}

function confirmTerminalScanAuthority(jobId, status, generation) {
  const key = `${generation}:${jobId}`;
  if (terminalScanAuthority?.key !== key) terminalScanAuthority = {key, status};
  return terminalScanAuthority.status;
}

function setScanReservationControls(reserved) {
  const state = window.MorphicWorkbenchState;
  state.scanRunActive = reserved;
  const refresh = $("#scan-refresh-button");
  const stop = $("#scan-stop-button");
  updateScanActionAvailability();
  if (refresh) refresh.disabled = !reserved;
  if (stop) stop.disabled = !reserved;
}

function adoptScanJob(result, generation = caseGeneration, message = "Analyse gestartet") {
  const state = window.MorphicWorkbenchState;
  if (generation !== caseGeneration) return false;
  const jobId = String(result?.job_id || "").trim();
  if (!jobId) return false;
  state.activeJobId = jobId;
  setScanReservationControls(true);
  const panel = $("#job-status-panel");
  if (panel) panel.hidden = false;
  const jobLabel = $("#job-id-label");
  if (jobLabel) jobLabel.textContent = jobId;
  const statusLabelNode = $("#job-status-label");
  if (statusLabelNode && result?.status) {
    statusLabelNode.textContent = statusLabel(result.status);
  }
  showInlineState(message, "ok");
  window.MorphicWorkbenchRender.resetSubstepTimeline();
  enterStep(6, false);
  void pollScanJob(jobId, generation);
  return true;
}

async function reconcileExistingScanStartOperation(
  operationId = readExistingStartOperationId("scan"),
  generation = caseGeneration
) {
  const state = window.MorphicWorkbenchState;
  const authority = String(operationId || "").trim();
  if (!authority) return {disposition: "none"};
  const ownsPendingState = !state.scanStartPending;
  if (ownsPendingState) {
    state.scanStartPending = true;
    updateScanActionAvailability();
  }
  try {
    const result = await window.MorphicWorkbenchApi.reconcileScanStartOperation(authority);
    if (generation !== caseGeneration) return {disposition: "stale"};
    const disposition = String(result?.disposition || "");
    if (disposition === "job") {
      if (!adoptScanJob(result, generation, "Bestehende Analyse wieder aufgenommen")) {
        showInlineState(
          "Startabgleich blieb unklar. Der bestehende Schlüssel bleibt reserviert.",
          "bad"
        );
        return {disposition: "unresolved"};
      }
      return result;
    }
    if (disposition === "safe-to-replace") {
      clearStartOperationId("scan");
      showInlineState("Startabgleich bestätigt: Ein neuer Start ist sicher möglich.", "neutral");
      return result;
    }
    if (disposition === "retry-same-key") {
      showInlineState(
        "Startabgleich noch offen. Derselbe Schlüssel bleibt für einen erneuten Start reserviert.",
        "bad"
      );
      return result;
    }
    showInlineState(
      "Startabgleich blieb unklar. Der bestehende Schlüssel bleibt reserviert.",
      "bad"
    );
    return {disposition: "unresolved"};
  } catch (error) {
    if (generation !== caseGeneration) return {disposition: "stale"};
    showInlineState(
      apiErrorMessage(
        error,
        "Startabgleich nicht erreichbar; der bestehende Schlüssel bleibt reserviert"
      ),
      "bad"
    );
    return {disposition: "unresolved", error};
  } finally {
    if (ownsPendingState && generation === caseGeneration) {
      state.scanStartPending = false;
      updateScanActionAvailability();
    }
  }
}

function retainUnresolvedScanReservation(status) {
  setScanReservationControls(true);
  const message = isAutomaticScanStatus(status)
    ? "Analyse laeuft. Status erneut laden oder den Scan bei Bedarf manuell stoppen."
    : "Scanstatus ist nicht abschliessend bestaetigt. Status erneut laden oder den Scan manuell stoppen.";
  showInlineState(message, isAutomaticScanStatus(status) ? "neutral" : "bad");
}

function releaseScanReservation(jobId, status) {
  setScanReservationControls(false);
  if (status === "stopped" && window.MorphicWorkbenchState.activeJobId === jobId) {
    window.MorphicWorkbenchState.activeJobId = null;
  }
  if (jobPollTimer) clearTimeout(jobPollTimer);
  jobPollTimer = null;
}

async function finalizeTerminalScan(jobId, status, generation, requestOwner) {
  const state = window.MorphicWorkbenchState;
  if (generation !== caseGeneration || state.activeJobId !== jobId) return "stale";
  const terminalStatus = confirmTerminalScanAuthority(jobId, status, generation);
  const authority = terminalScanAuthority;
  const label = $("#job-status-label");
  if (label) label.textContent = statusLabel(terminalStatus);
  if (authority.finalization) return authority.finalization;
  const finalization = finalizeTerminalScanOnce(
    jobId,
    terminalStatus,
    generation,
    requestOwner
  );
  authority.finalization = finalization;
  const clearFinalization = () => {
    if (authority.finalization === finalization) authority.finalization = null;
  };
  finalization.then(clearFinalization, clearFinalization);
  return finalization;
}

async function finalizeTerminalScanOnce(jobId, terminalStatus, generation, requestOwner) {
  const state = window.MorphicWorkbenchState;
  const initialInlineRevision = inlineStateRevision;
  releaseScanReservation(jobId, terminalStatus);
  clearStartOperationId("scan");
  const requestKey = `${generation}:${jobId}`;
  const isCurrent = () => {
    const inFlight = requestOwner === "stop" ? scanStopInFlight : scanPollInFlight;
    return (
      generation === caseGeneration
      && inFlight?.key === requestKey
      && (
        state.activeJobId === jobId
        || (terminalStatus === "stopped" && state.activeJobId === null)
      )
    );
  };
  const enableTerminalRefresh = () => {
    if (terminalStatus === "stopped" || state.activeJobId !== jobId) return;
    const refresh = $("#scan-refresh-button");
    if (refresh) refresh.disabled = false;
  };
  const showAuthenticationRequired = () => {
    enableTerminalRefresh();
    const label = $("#job-status-label");
    if (label) label.textContent = "Anmeldung erforderlich - Abschluss nicht synchronisiert";
    if (inlineStateRevision === initialInlineRevision) {
      showInlineState(
        "Scanabschluss kann erst nach erneuter Anmeldung vollständig synchronisiert werden.",
        "bad"
      );
    }
  };
  const showFollowupError = (error) => {
    enableTerminalRefresh();
    if (inlineStateRevision === initialInlineRevision) {
      showInlineState(
        apiErrorMessage(
          error,
          "Abschlussdaten konnten nicht vollständig verarbeitet werden. Status erneut laden"
        ),
        "bad"
      );
    }
  };

  try {
    await window.MorphicWorkbenchApi.syncScanRunTrace(jobId);
  } catch (error) {
    if (!isOptionalRunTraceError(error)) {
      if (!isCurrent()) return "stale";
      showAuthenticationRequired();
      return "auth";
    }
  }
  if (!isCurrent()) return "stale";
  if (terminalStatus === "completed") {
    try {
      const resultsAccepted = await loadScanResults(jobId, generation, true);
      if (!resultsAccepted || !isCurrent()) return "stale";
      await loadReports(generation, true);
    } catch (error) {
      if (!isCurrent()) return "stale";
      if ([401, 403].includes(Number(error?.status))) {
        showAuthenticationRequired();
        return "auth";
      }
      showFollowupError(error);
      return "followup-error";
    }
    if (!isCurrent()) return "stale";
  }
  if (inlineStateRevision !== initialInlineRevision) return "finalized-newer-inline";
  const terminalInline = {
    completed: ["Analyse erfolgreich abgeschlossen.", "ok"],
    failed: ["Analyse fehlgeschlagen.", "bad"],
    stopped: ["Scan bestaetigt gestoppt.", "ok"],
  }[terminalStatus];
  showInlineState(...terminalInline);
  return "finalized";
}

/* ── Health & Sources ─────────────────────────────────────────────── */

async function loadHealth(generation = caseGeneration) {
  try {
    const health = await window.MorphicWorkbenchApi.loadHealth();
    if (generation !== caseGeneration) return;
    const databases = healthDatabaseEntries(health.databases);
    const pv = $("#python-version");
    const pc = $("#profile-count");
    const dc = $("#database-count");
    const hs = $("#health-status");
    if (pv) pv.textContent = health.python?.version || "-";
    if (pc) pc.textContent = healthProfileCount(health.profiles);
    if (dc) dc.textContent = databases.length;
    if (hs) hs.textContent = health.ok ? "OK" : "WARN";
    setPill("#health-pill", health.ok ? "Health: OK" : "Health: WARN", health.ok ? "ok" : "bad");
    const hl = $("#health-list");
    if (hl) {
      hl.replaceChildren();
      databases.forEach((db) => {
        const name = db.name || db.path || "Datenbank";
        const size = db.size_bytes ?? db.size ?? 0;
        hl.appendChild(listItem(`${name}: ${size} bytes`));
      });
    }
  } catch (e) {
    if (generation !== caseGeneration) return;
    setPill("#health-pill", "Health: Fehler", "bad");
  }
}

async function loadSources(generation = caseGeneration) {
  try {
    const sources = await window.MorphicWorkbenchApi.loadSources();
    if (generation !== caseGeneration) return;
    setPill("#source-pill", `Quellen: ${sources.count}`, "ok");
    const sl = $("#source-list");
    const ss = $("#source-summary");
    if (sl) {
      sl.replaceChildren();
      sources.sources.forEach((s) => sl.appendChild(listItem(`${s.id}: ${s.label || s.id} [${s.status}]`)));
    }
    if (ss) {
      ss.replaceChildren();
      const counts = sources.status_counts || {};
      Object.entries(counts).forEach(([k, v]) => ss.appendChild(sourceBadge(k, v, k === "active" ? "ok" : k === "quarantined" ? "warn" : "neutral")));
    }
  } catch (e) {
    if (generation !== caseGeneration) return;
    setPill("#source-pill", "Quellen: Fehler", "bad");
  }
}

async function loadHealthAndSources(generation = caseGeneration) {
  if (generation !== caseGeneration) return [];
  return Promise.allSettled([
    loadHealth(generation),
    loadSources(generation),
  ]);
}

async function loadScanProfileCatalog(profileLevel, generation = caseGeneration) {
  scanPreviewRequestToken += 1;
  const requestToken = ++scanProfileCatalogRequestToken;
  const state = window.MorphicWorkbenchState;
  state.scanProfileCatalog = null;
  state.scanProfileCatalogStatus = "loading";
  state.scanProfileCatalogError = "";
  state.scanProfileCatalogLevel = Number(profileLevel);
  updateScanProfileTopNOptions();
  updateScanActionAvailability();
  const catalogInlineStateRevision = scanProfileCatalogMayOwnInlineState()
    ? showInlineState(SCAN_PROFILE_ACTION_LOADING_TEXT, "neutral")
    : null;
  const integration = $("#source-analysis-integration");
  if (integration) integration.textContent = SCAN_PROFILE_CATALOG_LOADING_TEXT;
  if (state.currentStepIndex === 5) {
    window.MorphicWorkbenchRender.renderReviewCards(
      formScanPayload(),
      state.hardwareTruth,
      null
    );
  }
  try {
    const catalog = await window.MorphicWorkbenchApi.loadScanProfileCatalog(profileLevel);
    if (
      generation !== caseGeneration ||
      requestToken !== scanProfileCatalogRequestToken
    ) return;
    const fingerprint = String(catalog?.pool_authority?.fingerprint || "");
    if (
      Number(catalog?.profile_level) !== Number(profileLevel)
      || !/^[0-9a-f]{64}$/.test(fingerprint)
    ) {
      throw new Error("Scanprofil-Katalog ist für das gewählte Level ungültig");
    }
    state.scanProfileCatalog = catalog;
    state.scanProfileCatalogStatus = "ready";
    state.scanProfileCatalogError = "";
    updateScanProfileTopNOptions();
    updateScanActionAvailability();
    if (
      catalogInlineStateRevision !== null
      && scanProfileCatalogMayOwnInlineState()
      && inlineStateRevision === catalogInlineStateRevision
    ) {
      showInlineState(SCAN_PROFILE_ACTION_READY_TEXT, "ok");
    }
    if (integration) {
      const external = catalog.external || {};
      integration.textContent = `${external.active_source_count} Registry-Quellen sind betriebsbereit; ${external.count} als Scanprofile freigegeben. Keine Wirkung auf diesen Scan, Profilpool oder Score. Externe Scanprofile erst nach validierter Catalog-Freigabe in Gate 14.`;
    }
    if (state.currentStepIndex === 5) {
      window.MorphicWorkbenchRender.renderReviewCards(
        formScanPayload(),
        state.hardwareTruth,
        catalog
      );
    }
  } catch (e) {
    if (
      generation !== caseGeneration ||
      requestToken !== scanProfileCatalogRequestToken
    ) return;
    state.scanProfileCatalog = null;
    state.scanProfileCatalogStatus = "error";
    state.scanProfileCatalogError = scanProfileCatalogErrorMessage(e);
    updateScanProfileTopNOptions();
    updateScanActionAvailability();
    if (
      catalogInlineStateRevision !== null
      && scanProfileCatalogMayOwnInlineState()
      && inlineStateRevision === catalogInlineStateRevision
    ) {
      showInlineState(SCAN_PROFILE_ACTION_ERROR_TEXT, "bad");
    }
    if (integration) {
      integration.textContent = `${state.scanProfileCatalogError} ${SCAN_PROFILE_CATALOG_INVARIANT_TEXT}`;
    }
    if (state.currentStepIndex === 5) {
      window.MorphicWorkbenchRender.renderReviewCards(
        formScanPayload(),
        state.hardwareTruth,
        null
      );
    }
  }
}

window.MorphicWorkbenchActions = window.MorphicWorkbenchActions || {};
window.MorphicWorkbenchActions.retryScanProfileCatalog = () => {
  const profileLevelControl = scanFormControl("profile_level");
  return loadScanProfileCatalog(
    parseInt(profileLevelControl?.value || "3", 10),
    caseGeneration
  );
};

function reloadScanProfileCatalogAfterDrift(generation = caseGeneration) {
  const level = parseInt(scanFormControl("profile_level")?.value || "3", 10);
  void loadScanProfileCatalog(level, generation).catch(() => {});
}

/* ── Hardware Truth ───────────────────────────────────────────────── */

async function loadHardwareTruth(generation = caseGeneration) {
  const requestToken = ++hardwareTruthRequestToken;
  const mode = window.MorphicWorkbenchState.workbenchMode || "standard";
  try {
    const payload = await window.MorphicWorkbenchApi.loadHardware(mode);
    if (
      generation !== caseGeneration
      || requestToken !== hardwareTruthRequestToken
      || mode !== (window.MorphicWorkbenchState.workbenchMode || "standard")
    ) return;
    window.MorphicWorkbenchState.hardwareTruth = payload;
    window.MorphicWorkbenchRender.renderHardwareTruth(payload);
  } catch (e) {
    if (
      generation !== caseGeneration
      || requestToken !== hardwareTruthRequestToken
      || mode !== (window.MorphicWorkbenchState.workbenchMode || "standard")
    ) return;
    window.MorphicWorkbenchState.hardwareTruth = null;
    const calibration = $("#realtime-calibration");
    const warnings = $("#hardware-gate-warnings");
    if (calibration) calibration.replaceChildren();
    if (warnings) warnings.replaceChildren();
    const grid = $("#hardware-truth-grid");
    if (grid) {
      grid.replaceChildren();
      const note = document.createElement("p");
      note.className = "hardware-note";
      note.textContent = "Hardware-Truth-Endpunkt aktuell nicht erreichbar (Server-Neustart oder Ressourcenengpass moeglich). Kein Einfluss auf den Scan selbst - nur die Anzeige ist betroffen. ";
      const retryBtn = document.createElement("button");
      retryBtn.className = "secondary-button";
      retryBtn.type = "button";
      retryBtn.textContent = "Erneut versuchen";
      retryBtn.addEventListener("click", () => loadHardwareTruth());
      note.appendChild(retryBtn);
      grid.appendChild(note);
    }
  }
}

function updateEmfTelemetryControls(active, message, stateClass = "neutral") {
  const state = window.MorphicWorkbenchState;
  state.emfTelemetryActive = active;
  state.emfTelemetryStatus = stateClass;
  const status = $("#emf-telemetry-state");
  const enable = $("#emf-enable-button");
  const disable = $("#emf-disable-button");
  if (status) {
    status.textContent = message;
    status.className = `inline-state ${stateClass}`;
  }
  if (enable) enable.disabled = Boolean(active);
  if (disable) disable.disabled = !active;
}

function showEmfTelemetryPending(message) {
  const status = $("#emf-telemetry-state");
  const enable = $("#emf-enable-button");
  const disable = $("#emf-disable-button");
  if (status) {
    status.textContent = message;
    status.className = "inline-state neutral";
  }
  if (enable) enable.disabled = true;
  if (disable) disable.disabled = true;
}

function showEmfTelemetryUnknown(message) {
  const state = window.MorphicWorkbenchState;
  state.emfTelemetryActive = null;
  state.emfTelemetryStatus = "unknown";
  const status = $("#emf-telemetry-state");
  const enable = $("#emf-enable-button");
  const disable = $("#emf-disable-button");
  if (status) {
    status.textContent = message;
    status.className = "inline-state bad";
  }
  if (enable) enable.disabled = true;
  if (disable) disable.disabled = true;
}

function syncEmfNewCaseFence(reset = $("#new-case-button")) {
  if (!reset) return;
  const state = window.MorphicWorkbenchState;
  reset.disabled = state.pendingMutations > 0
    || state.resetInProgress
    || state.emfTelemetryMutationPending
    || state.emfTelemetryMutationUnresolved;
}

function waitForEmfTimeoutReconciliation(delayMs) {
  if (delayMs <= 0) return Promise.resolve();
  return new Promise((resolve) => setTimeout(resolve, delayMs));
}

async function readEmfTelemetryStatus(generation = caseGeneration) {
  const requestToken = ++emfTelemetryStatusRequestToken;
  try {
    const payload = await window.MorphicWorkbenchApi.loadEmfStatus();
    if (
      generation !== caseGeneration
      || requestToken !== emfTelemetryStatusRequestToken
    ) return {current: false};
    if (typeof payload?.active !== "boolean") {
      return {
        current: true,
        valid: false,
        message: "EMF-Telemetrie-Status ist ungueltig.",
      };
    }
    return {current: true, valid: true, active: payload.active};
  } catch (e) {
    if (
      generation !== caseGeneration
      || requestToken !== emfTelemetryStatusRequestToken
    ) return {current: false};
    return {
      current: true,
      valid: false,
      message: apiErrorMessage(e, "EMF-Telemetrie-Status nicht verfuegbar"),
    };
  }
}

function settleEmfTelemetryStatus(active) {
  updateEmfTelemetryControls(
    active,
    active ? "EMF-Telemetrie aktiv bis manuell deaktiviert." : "EMF-Telemetrie deaktiviert.",
    active ? "ok" : "neutral"
  );
}

async function loadEmfTelemetryStatus(generation = caseGeneration) {
  const state = window.MorphicWorkbenchState;
  const observation = await readEmfTelemetryStatus(generation);
  if (!observation.current) return false;
  if (!observation.valid) {
    showEmfTelemetryUnknown(observation.message);
    return false;
  }
  state.emfTelemetryMutationUnresolved = false;
  settleEmfTelemetryStatus(observation.active);
  syncEmfNewCaseFence();
  return true;
}

async function reconcileTimedOutEmfMutation(enabled, generation) {
  const state = window.MorphicWorkbenchState;
  state.emfTelemetryMutationUnresolved = true;
  for (const delayMs of EMF_TIMEOUT_RECONCILIATION_DELAYS_MS) {
    await waitForEmfTimeoutReconciliation(delayMs);
    if (generation !== caseGeneration || state.resetInProgress) return false;
    const observation = await readEmfTelemetryStatus(generation);
    if (!observation.current) return false;
    if (observation.valid && observation.active === enabled) {
      state.emfTelemetryMutationUnresolved = false;
      settleEmfTelemetryStatus(enabled);
      return true;
    }
  }
  if (generation !== caseGeneration || state.resetInProgress) return false;
  showEmfTelemetryUnknown(
    "EMF-Umschaltung nach Zeitueberschreitung nicht eindeutig geklaert; Status unbekannt. Seite neu laden."
  );
  return false;
}

async function setEmfTelemetryEnabled(enabled, generation = caseGeneration) {
  const state = window.MorphicWorkbenchState;
  if (
    state.resetInProgress
    || state.emfTelemetryMutationPending
    || state.emfTelemetryMutationUnresolved
  ) return false;
  state.emfTelemetryMutationPending = true;
  const reset = $("#new-case-button");
  if (reset) reset.disabled = true;
  let confirmedActive = null;
  try {
    emfTelemetryStatusRequestToken += 1;
    showEmfTelemetryPending(
      enabled ? "EMF-Telemetrie wird aktiviert..." : "EMF-Telemetrie wird deaktiviert...",
    );
    let mutationSucceeded = true;
    let mutationError = null;
    try {
      if (enabled) await window.MorphicWorkbenchApi.enableEmfTelemetry();
      else await window.MorphicWorkbenchApi.disableEmfTelemetry();
    } catch (error) {
      mutationSucceeded = false;
      mutationError = error;
    }
    if (generation !== caseGeneration) return false;
    const confirmed = mutationError?.code === "request_timeout"
      ? await reconcileTimedOutEmfMutation(enabled, generation)
      : await loadEmfTelemetryStatus(generation);
    if (!confirmed || generation !== caseGeneration) return false;
    confirmedActive = state.emfTelemetryActive;
    const enable = $("#emf-enable-button");
    const disable = $("#emf-disable-button");
    if (enable) enable.disabled = true;
    if (disable) disable.disabled = true;
    await loadHardwareTruth(generation);
    if (generation !== caseGeneration) return false;
    return mutationSucceeded;
  } finally {
    if (generation === caseGeneration) {
      if (typeof confirmedActive === "boolean") {
        updateEmfTelemetryControls(
          confirmedActive,
          confirmedActive
            ? "EMF-Telemetrie aktiv bis manuell deaktiviert."
            : "EMF-Telemetrie deaktiviert.",
          confirmedActive ? "ok" : "neutral"
        );
      }
      state.emfTelemetryMutationPending = false;
      syncEmfNewCaseFence(reset);
    }
  }
}

function wireEmfTelemetryControls() {
  const enable = $("#emf-enable-button");
  const disable = $("#emf-disable-button");
  if (enable && enable.dataset.emfTelemetryWired !== "true") {
    enable.dataset.emfTelemetryWired = "true";
    enable.addEventListener("click", () => setEmfTelemetryEnabled(true));
  }
  if (disable && disable.dataset.emfTelemetryWired !== "true") {
    disable.dataset.emfTelemetryWired = "true";
    disable.addEventListener("click", () => setEmfTelemetryEnabled(false));
  }
}

/* ── Scan Preview & Start ─────────────────────────────────────────── */

async function generatePreview(generation = caseGeneration) {
  const state = window.MorphicWorkbenchState;
  if (state.scanStartPending || state.scanRunActive) {
    showWizardNavigationState("Eine Analyse wird bereits gestartet oder ausgefuehrt.", "bad");
    return false;
  }
  const requestToken = ++scanPreviewRequestToken;
  showInlineState("Vorschau wird erzeugt...", "neutral");
  try {
    const body = formScanPayload();
    const validationMessage = validateScanPayload(body);
    if (validationMessage) {
      showInlineState(validationMessage, "bad");
      return;
    }
    const payloadSnapshot = JSON.stringify(body);
    const result = await window.MorphicWorkbenchApi.loadScanPreview(body);
    if (!scanPreviewRequestIsCurrent(requestToken, generation, payloadSnapshot)) return;
    const pre = $("#command-preview");
    if (pre) pre.textContent = (result.command || []).join(" ");
    window.MorphicWorkbenchRender.renderReviewCards(
      body,
      window.MorphicWorkbenchState.hardwareTruth,
      window.MorphicWorkbenchState.scanProfileCatalog
    );
    window.MorphicWorkbenchState.saveFocusToHistory(body.focus);
    showInlineState("Vorschau bereit", "ok");
  } catch (e) {
    if (
      generation !== caseGeneration
      || requestToken !== scanPreviewRequestToken
    ) return;
    if (
      Number(e?.status) === 409
      && e?.scanProfilePoolDisposition === "stale"
    ) {
      reloadScanProfileCatalogAfterDrift(generation);
    }
    showInlineState(apiErrorMessage(e, "Vorschau fehlgeschlagen"), "bad");
  }
}

async function startScanJob(generation = caseGeneration) {
  const state = window.MorphicWorkbenchState;
  if (state.scanStartPending || state.scanRunActive) {
    showInlineState("Eine Analyse wird bereits gestartet oder ausgefuehrt.", "bad");
    return false;
  }
  scanPreviewRequestToken += 1;
  state.scanStartPending = true;
  updateScanActionAvailability();
  showInlineState("Analyse wird gestartet...", "neutral");
  try {
    const body = formScanPayload({includeGroupActivation: true});
    const validationMessage = validateScanPayload(body, {includeGroupActivation: true});
    if (validationMessage) {
      showInlineState(validationMessage, "bad");
      return false;
    }
    const operationId = startOperationId("scan");
    const result = await window.MorphicWorkbenchApi.startScanJob(body, operationId);
    if (generation !== caseGeneration) return;
    if (!adoptScanJob(result, generation)) {
      throw new Error("Serverantwort enthält keine Job-ID.");
    }
    window.MorphicWorkbenchState.saveFocusToHistory(body.focus);
    return true;
  } catch (e) {
    if (generation !== caseGeneration) return;
    const taggedPoolStale = Number(e?.status) === 409
      && e?.scanProfilePoolDisposition === "stale";
    let reconciliation = null;
    if (
      shouldRetainStartOperation(e)
      && (!e?.status || Number(e.status) === 409)
    ) {
      reconciliation = await reconcileExistingScanStartOperation(
        readExistingStartOperationId("scan"),
        generation
      );
      if (generation !== caseGeneration) return;
    }
    if (taggedPoolStale) {
      reloadScanProfileCatalogAfterDrift(generation);
    }
    if (reconciliation?.disposition === "job") return true;
    if (!shouldRetainStartOperation(e)) clearStartOperationId("scan");
    const message = ["retry-same-key", "unresolved"].includes(
      reconciliation?.disposition
    )
      ? "Start nicht bestätigt. Der bestehende Schlüssel bleibt für den Abgleich reserviert."
      : e?.status
        ? apiErrorMessage(e, "Start fehlgeschlagen")
        : "Startantwort nicht bestätigt. Erneuter Start gleicht denselben Vorgang ab.";
    showInlineState(message, "bad");
    return false;
  } finally {
    state.scanStartPending = false;
    updateScanActionAvailability();
  }
}

async function pollScanJob(jobId, generation = caseGeneration, failureCount = 0) {
  const key = `${generation}:${jobId}`;
  if (scanPollInFlight?.key === key) return scanPollInFlight.promise;
  const promise = _pollScanJobOnce(jobId, generation, failureCount);
  const authority = {key, promise};
  scanPollInFlight = authority;
  return promise.finally(() => {
    if (scanPollInFlight === authority) scanPollInFlight = null;
  });
}

async function _pollScanJobOnce(jobId, generation = caseGeneration, failureCount = 0) {
  const state = window.MorphicWorkbenchState;
  if (generation !== caseGeneration || state.activeJobId !== jobId) return;
  if (jobPollTimer) clearTimeout(jobPollTimer);
  try {
    const response = await window.MorphicWorkbenchApi.pollScanJob(jobId);
    if (generation !== caseGeneration || state.activeJobId !== jobId) return;
    const data = response && typeof response === "object" ? response : {};
    if (!isTerminalScanStatus(data.status) && terminalScanAuthorityStatus(jobId, generation)) return;
    clearOwnedPollDegradation("scan", jobId, generation);
    const sl = $("#job-status-label");
    if (sl) sl.textContent = statusLabel(data.status);
    const rc = $("#job-returncode");
    if (rc) rc.textContent = data.returncode ?? "-";
    const pf = $("#job-progress-fill");
    if (pf) {
      const percent = data.progress_percent || 0;
      pf.style.width = `${percent}%`;
      pf.setAttribute("aria-valuenow", String(Math.round(percent)));
    }
    const pl = $("#job-progress-label");
    if (pl) pl.textContent = data.progress_percent != null ? `${data.progress_percent.toFixed(0)}%` : "-";
    const ph = $("#job-phase-label");
    if (ph) ph.textContent = data.current_phase || "-";
    const ps = $("#job-substep-label");
    if (ps) ps.textContent = data.current_substep || "-";
    const lt = $("#job-log-tail");
    if (lt) {
      const diagnostics = Array.isArray(data.diagnostics) ? data.diagnostics : [];
      lt.textContent = diagnostics.map(line => String(line || "")).filter(Boolean).join("\n");
    }
    const cl = $("#job-substep-list");
    if (cl) {
      cl.replaceChildren();
      (data.completed_substeps || []).forEach((s) => cl.appendChild(listItem(s)));
    }
    window.MorphicWorkbenchRender.renderSubstepTimeline(
      data.completed_stage_ids,
      data.current_stage_id,
      data.status
    );
    if (isAutomaticScanStatus(data.status)) {
      retainUnresolvedScanReservation(data.status);
      jobPollTimer = setTimeout(() => pollScanJob(jobId, generation, 0), 2000);
    } else if (!isTerminalScanStatus(data.status)) {
      retainUnresolvedScanReservation(data.status);
    } else {
      await finalizeTerminalScan(jobId, data.status, generation, "poll");
    }
  } catch (e) {
    if (generation !== caseGeneration || state.activeJobId !== jobId) return;
    if (terminalScanAuthorityStatus(jobId, generation)) return;
    setScanReservationControls(true);
    const status = $("#job-status-label");
    if ([401, 403].includes(e?.status)) {
      if (status) status.textContent = "Anmeldung erforderlich - Polling pausiert";
      const refresh = $("#scan-refresh-button");
      if (refresh) refresh.disabled = false;
      scanPollDegradation = {
        jobId,
        generation,
        revision: showInlineState("Scanstatus kann erst nach erneuter Anmeldung aktualisiert werden.", "bad"),
      };
      return;
    }
    const nextFailure = failureCount + 1;
    if (nextFailure > MAX_POLL_FAILURES) {
      if (status) status.textContent = "Verbindung unterbrochen - Polling pausiert";
      scanPollDegradation = {
        jobId,
        generation,
        revision: showInlineState("Scanstatus ist offline; Polling wurde nach mehreren Fehlern pausiert.", "bad"),
      };
      return;
    }
    if (status) status.textContent = "Verbindung unterbrochen - erneuter Versuch";
    scanPollDegradation = {
      jobId,
      generation,
      revision: showInlineState("Scanstatus voruebergehend nicht erreichbar.", "bad"),
    };
    jobPollTimer = setTimeout(
      () => pollScanJob(jobId, generation, nextFailure),
      pollRetryDelay(nextFailure)
    );
  }
}

async function loadScanResults(jobId, generation = caseGeneration, propagateError = false) {
  const requestToken = ++scanResultsRequestToken;
  const state = window.MorphicWorkbenchState;
  let results;
  try {
    results = await window.MorphicWorkbenchApi.loadScanResults(jobId);
  } catch (e) {
    if (
      requestToken !== scanResultsRequestToken
      || generation !== caseGeneration
      || state.activeJobId !== jobId
    ) return false;
    if ([401, 403].includes(e?.status) || propagateError) throw e;
    return false;
  }
  if (
    requestToken !== scanResultsRequestToken
    || generation !== caseGeneration
    || state.activeJobId !== jobId
  ) return false;
  const reportSessionId = results?.report_session_id;
  ensureReportAuthorityGeneration(generation);
  transitionReportAuthority({
    type: REPORT_AUTHORITY_EVENT.ACTIVE_SESSION_ACCEPTED,
    generation,
    sessionId: typeof reportSessionId === "string" && reportSessionId.length > 0
      ? reportSessionId
      : null,
  });
  state.scanResults = results;
  window.MorphicWorkbenchRender.renderResults(results);
  let trace;
  try {
    trace = await window.MorphicWorkbenchApi.loadRunTrace(jobId);
  } catch (e) {
    if (
      requestToken !== scanResultsRequestToken
      || generation !== caseGeneration
      || state.activeJobId !== jobId
    ) return false;
    if (!isOptionalRunTraceError(e)) throw e;
    return true;
  }
  if (
    requestToken !== scanResultsRequestToken
    || generation !== caseGeneration
    || state.activeJobId !== jobId
  ) return false;
  state.runTrace = trace;
  window.MorphicWorkbenchRender.renderRunTrace(trace);
  return true;
}

async function stopActiveScanJob(generation = caseGeneration) {
  const jobId = window.MorphicWorkbenchState.activeJobId;
  if (!jobId) return false;
  const key = `${generation}:${jobId}`;
  if (scanStopInFlight?.key === key) return scanStopInFlight.promise;
  const promise = _stopActiveScanJob(jobId, generation);
  const authority = {key, promise};
  scanStopInFlight = authority;
  return promise.finally(() => {
    if (scanStopInFlight === authority) scanStopInFlight = null;
  });
}

async function _stopActiveScanJob(jobId, generation) {
  const state = window.MorphicWorkbenchState;
  if (generation !== caseGeneration || state.activeJobId !== jobId) return false;
  setScanReservationControls(true);
  const stop = $("#scan-stop-button");
  if (stop) stop.disabled = true;
  showInlineState("Scan-Stopp wird angefordert...", "neutral");
  try {
    const response = await window.MorphicWorkbenchApi.stopScanJob(jobId);
    if (generation !== caseGeneration || state.activeJobId !== jobId) return false;
    const data = response && typeof response === "object" ? response : {};
    if (!isTerminalScanStatus(data.status) && terminalScanAuthorityStatus(jobId, generation)) return false;
    const label = $("#job-status-label");
    if (label) label.textContent = statusLabel(data.status);
    if (!isTerminalScanStatus(data.status)) {
      retainUnresolvedScanReservation(data.status);
      return false;
    }
    const finalization = await finalizeTerminalScan(jobId, data.status, generation, "stop");
    if (finalization === "stale") return false;
    if (["auth", "followup-error"].includes(finalization)) return true;
    if (finalization === "finalized-newer-inline") return true;
    const terminalStatus = terminalScanAuthorityStatus(jobId, generation);
    if (data.status === terminalStatus) {
      showInlineState(
        terminalStatus === "stopped"
          ? "Scan wurde bestaetigt gestoppt."
          : `Scan ist bereits terminal: ${statusLabel(terminalStatus)}.`,
        terminalStatus === "failed" ? "bad" : "ok"
      );
    }
    return true;
  } catch (e) {
    if (generation !== caseGeneration || state.activeJobId !== jobId) return false;
    if (terminalScanAuthorityStatus(jobId, generation)) return false;
    setScanReservationControls(true);
    const label = $("#job-status-label");
    if ([401, 403].includes(e?.status)) {
      if (label) label.textContent = "Anmeldung erforderlich - Stopp nicht bestaetigt";
      showInlineState("Scan-Stopp erfordert eine erneute Anmeldung; die Reservation bleibt aktiv.", "bad");
    } else {
      if (label) label.textContent = "Stopp nicht bestaetigt";
      showInlineState(apiErrorMessage(e, "Scan-Stopp nicht bestaetigt; die Reservation bleibt aktiv"), "bad");
    }
    return false;
  } finally {
    if (generation === caseGeneration && state.activeJobId === jobId && state.scanRunActive) {
      const currentStop = $("#scan-stop-button");
      if (currentStop) currentStop.disabled = false;
    }
  }
}

/* ── Reports ──────────────────────────────────────────────────────── */

const REPORT_KIND_ICONS = { HTML: "🌐", JSON: "🗂️", TXT: "📄", PDF: "📕" };
const REPORT_PREVIEW_OUTCOME = Object.freeze({
  SUCCESS: "success",
  FAILURE: "failure",
  STALE: "stale",
});
const reportListMobileQuery = typeof window.matchMedia === "function"
  ? window.matchMedia("(max-width: 768px)")
  : null;
const REPORT_AUTHORITY_EVENT = Object.freeze({
  ACTIVE_SESSION_ACCEPTED: "ACTIVE_SESSION_ACCEPTED",
  CATALOG_REQUESTED: "CATALOG_REQUESTED",
  CATALOG_ACCEPTED: "CATALOG_ACCEPTED",
  CATALOG_FAILED: "CATALOG_FAILED",
  PREVIEW_REQUESTED: "PREVIEW_REQUESTED",
  PREVIEW_SUCCEEDED: "PREVIEW_SUCCEEDED",
  PREVIEW_FAILED: "PREVIEW_FAILED",
  PREVIEW_STALE: "PREVIEW_STALE",
  RESET_STARTED: "RESET_STARTED",
  RESET_ABORTED: "RESET_ABORTED",
  RESET_COMPLETED: "RESET_COMPLETED",
  HARMONIZATION_STATE_CHANGED: "HARMONIZATION_STATE_CHANGED",
  FOCUS_MOVED: "FOCUS_MOVED",
});

function createReportAuthorityState(generation = 0) {
  return Object.freeze({
    generation,
    nextCatalogRequestId: 1,
    acceptedCatalogRequestId: 0,
    nextPreviewRequestId: 1,
    activeSessionId: null,
    entriesById: new Map(),
    stable: null,
    pending: null,
    deferredRefresh: null,
    autoAttemptKey: null,
    focusId: null,
    resetCheckpoint: null,
    harmonizationStartPending: false,
    harmonizationRunActive: false,
    canHarmonize: false,
  });
}

function formatReportTimestamp(isoString) {
  if (!isoString) return "";
  const date = new Date(isoString);
  if (Number.isNaN(date.getTime())) return "";
  return date.toLocaleString("de-DE", { dateStyle: "medium", timeStyle: "short" });
}

function loadSandboxedReportHtml(frame, content) {
  return new Promise((resolve) => {
    let settled = false;
    const finish = () => {
      if (settled) return;
      settled = true;
      resolve();
    };
    frame.addEventListener("load", finish, {once: true});
    frame.srcdoc = content || "";
    setTimeout(finish, 2000);
  });
}

function flattenReportEntries(clients) {
  const entries = [];
  const seenReportIds = new Set();
  (Array.isArray(clients) ? clients : []).forEach((client) => {
    if (!client || typeof client !== "object" || Array.isArray(client)) return;
    const clientId = (
      typeof client.client_id === "string" && client.client_id.trim()
    ) ? client.client_id : "";
    const clientLabel = (
      typeof client.label === "string" && client.label.trim()
    ) ? client.label : clientId || "Unbekannt";
    (Array.isArray(client.sessions) ? client.sessions : []).forEach((session) => {
      if (!session || typeof session !== "object" || Array.isArray(session)) return;
      const sessionId = (
        typeof session.session_id === "string" && session.session_id.trim()
      ) ? session.session_id : "";
      const sessionLabel = (
        typeof session.label === "string" && session.label.trim()
      ) ? session.label : sessionId || "Unbekannt";
      (Array.isArray(session.files) ? session.files : []).forEach((file) => {
        if (
          !file
          || typeof file !== "object"
          || Array.isArray(file)
          || typeof file.id !== "string"
          || !file.id.trim()
          || seenReportIds.has(file.id)
        ) return;
        seenReportIds.add(file.id);
        entries.push({
          ...file,
          client_id: clientId,
          client_label: clientLabel,
          session_id: sessionId,
          session_label: sessionLabel,
        });
      });
    });
  });
  return entries;
}

function reportModifiedTime(entry) {
  if (!entry || typeof entry !== "object" || Array.isArray(entry)) return 0;
  const parsed = Date.parse(entry.modified_at || "");
  return Number.isFinite(parsed) ? parsed : 0;
}

function reportEntryFingerprint(entry) {
  if (!entry || typeof entry !== "object" || Array.isArray(entry)) return "";
  return JSON.stringify([
    String(entry.id || ""),
    String(entry.client_id || ""),
    String(entry.session_id || ""),
    String(entry.kind || entry.type || "").toUpperCase(),
    String(entry.file_name || entry.name || ""),
    String(entry.relative_path || entry.path || entry.file_path || ""),
    String(entry.modified_at || ""),
    entry.size === null || entry.size === undefined ? null : String(entry.size),
  ]);
}

function automaticReportCandidate(entries, sessionId) {
  if (typeof sessionId !== "string" || !sessionId) return null;
  const matches = (Array.isArray(entries) ? entries : []).filter(
    (entry) => entry
      && typeof entry === "object"
      && !Array.isArray(entry)
      && entry.session_id === sessionId
  );
  const tiers = [
    (entry) => String(entry.kind || entry.type || "").toUpperCase() === "HTML",
    (entry) => ["TXT", "JSON"].includes(
      String(entry.kind || entry.type || "").toUpperCase()
    ),
    (entry) => String(entry.kind || entry.type || "").toUpperCase() === "PDF",
  ];
  for (const accepts of tiers) {
    const ranked = matches.filter(accepts).sort(
      (left, right) => reportModifiedTime(right) - reportModifiedTime(left)
    );
    if (ranked.length) return ranked[0];
  }
  return null;
}

const REPORT_AUTHORITY_NO_EFFECTS = Object.freeze([]);

function reportAuthorityCanHarmonize(authority) {
  const stableEntry = authority.stable
    ? authority.entriesById.get(authority.stable.reportId)
    : null;
  return Boolean(
    authority.stable
    && stableEntry
    && authority.stable.entryFingerprint === reportEntryFingerprint(stableEntry)
    && authority.pending === null
    && authority.resetCheckpoint === null
    && !authority.harmonizationStartPending
    && !authority.harmonizationRunActive
  );
}

function reportAuthorityEffect(type, values = {}) {
  return Object.freeze({type, ...values});
}

function reportAuthorityState(current, changes) {
  const candidate = {...current, ...changes, canHarmonize: false};
  return Object.freeze({
    ...candidate,
    canHarmonize: reportAuthorityCanHarmonize(candidate),
  });
}

function reportAuthorityResult(state, effects = REPORT_AUTHORITY_NO_EFFECTS) {
  return Object.freeze({
    state,
    effects: effects === REPORT_AUTHORITY_NO_EFFECTS
      ? effects
      : Object.freeze(effects),
  });
}

function reportAuthorityNoop(current) {
  return reportAuthorityResult(current);
}

function reportAuthorityRequestMatches(pending, request) {
  return Boolean(
    pending
    && request
    && pending.generation === request.generation
    && pending.requestId === request.requestId
    && pending.reportId === request.reportId
    && pending.intent === request.intent
    && pending.expectedFingerprint === request.expectedFingerprint
    && pending.expectedSessionId === request.expectedSessionId
    && pending.catalogRequestId === request.catalogRequestId
  );
}

function reportAuthorityRequestIsCurrent(authority, request) {
  if (
    !reportAuthorityRequestMatches(authority.pending, request)
    || request.generation !== authority.generation
  ) return false;
  if (request.allowUnknown && request.intent === "manual") return true;
  const entry = authority.entriesById.get(request.reportId);
  if (
    !entry
    || request.expectedFingerprint === ""
    || reportEntryFingerprint(entry) !== request.expectedFingerprint
  ) return false;
  if (request.intent !== "auto") return true;
  return Boolean(
    request.catalogRequestId === authority.acceptedCatalogRequestId
    && request.expectedSessionId === authority.activeSessionId
    && entry.session_id === request.expectedSessionId
  );
}

function reportAuthorityAutoAttemptKey(generation, sessionId) {
  return typeof sessionId === "string" && sessionId
    ? `${generation}:${sessionId}`
    : null;
}

function reportAuthorityAllocatePreview(authority, reportId, intent, effects = []) {
  if (
    authority.resetCheckpoint !== null
    || !["manual", "auto", "refresh"].includes(intent)
  ) return null;
  const entry = authority.entriesById.get(reportId);
  const expectedFingerprint = reportEntryFingerprint(entry);
  const isManual = intent === "manual";
  const isUnknown = !entry || expectedFingerprint === "";
  if (isUnknown) {
    if (!isManual) return null;
  } else if (intent !== "manual" && authority.pending !== null) {
    return null;
  }
  if (intent === "auto") {
    const attemptKey = reportAuthorityAutoAttemptKey(
      authority.generation,
      authority.activeSessionId
    );
    if (
      authority.stable?.selectionSource === "manual"
      || !attemptKey
      || authority.autoAttemptKey === attemptKey
      || entry.session_id !== authority.activeSessionId
    ) return null;
  }
  if (
    intent === "refresh"
    && (
      authority.stable?.reportId !== reportId
      || authority.stable.entryFingerprint === expectedFingerprint
    )
  ) return null;

  const request = Object.freeze({
    generation: authority.generation,
    requestId: authority.nextPreviewRequestId,
    reportId,
    intent,
    expectedFingerprint: isUnknown ? "" : expectedFingerprint,
    allowUnknown: isUnknown && isManual,
    expectedSessionId: intent === "auto" ? authority.activeSessionId : null,
    catalogRequestId: authority.acceptedCatalogRequestId,
  });
  const state = reportAuthorityState(authority, {
    nextPreviewRequestId: authority.nextPreviewRequestId + 1,
    pending: request,
    deferredRefresh: intent === "refresh" ? null : authority.deferredRefresh,
  });
  return reportAuthorityResult(state, [
    ...effects,
    reportAuthorityEffect("RENDER_LOADING", {request}),
    reportAuthorityEffect("LOAD_PREVIEW", {request}),
  ]);
}

function reportAuthorityDeferredRefresh(authority, entry) {
  return Object.freeze({
    reportId: authority.stable.reportId,
    generation: authority.generation,
    expectedFingerprint: reportEntryFingerprint(entry),
    selectionSource: authority.stable.selectionSource,
    catalogRequestId: authority.acceptedCatalogRequestId,
  });
}

function reportAuthorityResumeDeferred(authority, effects) {
  const deferred = authority.deferredRefresh;
  if (!deferred || authority.pending !== null || authority.resetCheckpoint !== null) {
    return reportAuthorityResult(authority, effects);
  }
  const entry = authority.entriesById.get(deferred.reportId);
  if (
    !authority.stable
    || authority.stable.reportId !== deferred.reportId
    || !entry
    || reportEntryFingerprint(entry) !== deferred.expectedFingerprint
    || authority.stable.entryFingerprint === deferred.expectedFingerprint
  ) {
    return reportAuthorityResult(
      reportAuthorityState(authority, {deferredRefresh: null}),
      effects
    );
  }
  return reportAuthorityAllocatePreview(
    authority,
    deferred.reportId,
    "refresh",
    effects
  );
}

function reduceReportAuthority(current, event) {
  if (!current || !event || typeof event !== "object") {
    return reportAuthorityNoop(current);
  }
  if (
    event.type !== REPORT_AUTHORITY_EVENT.RESET_COMPLETED
    && Object.prototype.hasOwnProperty.call(event, "generation")
    && event.generation !== current.generation
  ) return reportAuthorityNoop(current);

  if (event.type === REPORT_AUTHORITY_EVENT.ACTIVE_SESSION_ACCEPTED) {
    if (event.generation !== current.generation) return reportAuthorityNoop(current);
    const sessionId = typeof event.sessionId === "string" && event.sessionId.trim()
      ? event.sessionId.trim()
      : null;
    return reportAuthorityResult(reportAuthorityState(current, {activeSessionId: sessionId}));
  }

  if (event.type === REPORT_AUTHORITY_EVENT.CATALOG_REQUESTED) {
    if (event.generation !== current.generation) return reportAuthorityNoop(current);
    const request = Object.freeze({
      generation: current.generation,
      requestId: current.nextCatalogRequestId,
    });
    const state = reportAuthorityState(current, {
      nextCatalogRequestId: current.nextCatalogRequestId + 1,
    });
    return reportAuthorityResult(state, [
      reportAuthorityEffect("LOAD_CATALOG", {request}),
    ]);
  }

  if (event.type === REPORT_AUTHORITY_EVENT.CATALOG_ACCEPTED) {
    const request = event.request;
    if (
      event.generation !== current.generation
      || !request
      || request.generation !== current.generation
      || request.requestId !== current.nextCatalogRequestId - 1
      || request.requestId <= current.acceptedCatalogRequestId
    ) return reportAuthorityNoop(current);

    const entriesById = new Map();
    (Array.isArray(event.entries) ? event.entries : []).forEach((entry) => {
      if (
        !entry
        || typeof entry !== "object"
        || Array.isArray(entry)
        || typeof entry.id !== "string"
        || !entry.id.trim()
        || entriesById.has(entry.id)
      ) return;
      entriesById.set(entry.id, Object.freeze({...entry}));
    });

    let stable = current.stable;
    const stableRemoved = Boolean(stable && !entriesById.has(stable.reportId));
    if (stableRemoved) stable = null;
    const hadPending = current.pending !== null;
    let pending = current.pending;
    if (pending) {
      const pendingEntry = entriesById.get(pending.reportId);
      const pendingStillCurrent = Boolean(
        pending.generation === current.generation
        && pendingEntry
        && reportEntryFingerprint(pendingEntry) === pending.expectedFingerprint
        && (
          pending.intent !== "auto"
          || (
            pending.expectedSessionId === current.activeSessionId
            && pendingEntry.session_id === pending.expectedSessionId
            && pending.catalogRequestId === request.requestId
          )
        )
      );
      if (!pendingStillCurrent) pending = null;
    }
    let focusId = entriesById.has(current.focusId)
      ? current.focusId
      : stable?.reportId || null;
    if (!entriesById.has(focusId)) focusId = null;
    let deferredRefresh = current.deferredRefresh;
    if (
      !stable
      || deferredRefresh?.reportId !== stable.reportId
      || !entriesById.has(deferredRefresh.reportId)
      || stable.entryFingerprint === reportEntryFingerprint(
        entriesById.get(stable.reportId)
      )
    ) deferredRefresh = null;

    const pendingRemoved = hadPending && pending === null;
    let state = reportAuthorityState(current, {
      acceptedCatalogRequestId: request.requestId,
      entriesById,
      stable,
      pending,
      deferredRefresh,
      focusId,
    });
    const entries = Object.freeze(Array.from(entriesById.values()));
    const effects = [reportAuthorityEffect("RENDER_CATALOG", {entries})];
    if (stableRemoved) {
      if (pending === null) effects.push(reportAuthorityEffect("RENDER_EMPTY"));
      effects.push(reportAuthorityEffect("SYNC_HARMONIZATION", {
        canHarmonize: state.canHarmonize,
      }));
    } else if (pendingRemoved && stable) {
      effects.push(
        reportAuthorityEffect("RENDER_STABLE", {view: stable.view}),
        reportAuthorityEffect("RENDER_CATALOG_SELECTION", {
          reportId: stable.reportId,
          focusId: state.focusId,
        }),
        reportAuthorityEffect("SYNC_HARMONIZATION", {
          canHarmonize: state.canHarmonize,
        })
      );
    } else if (pendingRemoved) {
      effects.push(
        reportAuthorityEffect("RENDER_EMPTY"),
        reportAuthorityEffect("SYNC_HARMONIZATION", {
          canHarmonize: state.canHarmonize,
        })
      );
    }
    const stableEntry = stable ? entriesById.get(stable.reportId) : null;
    const stableDrifted = Boolean(
      stableEntry
      && stable.entryFingerprint !== reportEntryFingerprint(stableEntry)
    );
    const refreshBeforeAuto = Boolean(
      stableDrifted
      && (
        stable.selectionSource === "manual"
        || stable.sessionId === state.activeSessionId
      )
    );
    if (refreshBeforeAuto) {
      if (pending?.intent === "manual") {
        state = reportAuthorityState(state, {
          deferredRefresh: reportAuthorityDeferredRefresh(state, stableEntry),
        });
        return reportAuthorityResult(state, effects);
      }
      if (pending !== null) return reportAuthorityResult(state, effects);
      return reportAuthorityAllocatePreview(state, stable.reportId, "refresh", effects)
        || reportAuthorityResult(state, effects);
    }
    if (pending !== null || stable?.selectionSource === "manual") {
      return reportAuthorityResult(state, effects);
    }

    const attemptKey = reportAuthorityAutoAttemptKey(
      state.generation,
      state.activeSessionId
    );
    const candidate = automaticReportCandidate(entries, state.activeSessionId);
    if (!candidate || state.autoAttemptKey === attemptKey) {
      return reportAuthorityResult(state, effects);
    }
    return reportAuthorityAllocatePreview(state, candidate.id, "auto", effects)
      || reportAuthorityResult(state, effects);
  }

  if (event.type === REPORT_AUTHORITY_EVENT.CATALOG_FAILED) {
    const request = event.request;
    if (
      event.generation !== current.generation
      || !request
      || request.generation !== current.generation
      || request.requestId !== current.nextCatalogRequestId - 1
      || request.requestId <= current.acceptedCatalogRequestId
    ) return reportAuthorityNoop(current);
    const message = typeof event.message === "string" ? event.message : "";
    return reportAuthorityResult(current, [
      reportAuthorityEffect("RENDER_CATALOG_ERROR", {message}),
    ]);
  }

  if (event.type === REPORT_AUTHORITY_EVENT.PREVIEW_REQUESTED) {
    if (event.generation !== current.generation) return reportAuthorityNoop(current);
    return reportAuthorityAllocatePreview(
      current,
      event.reportId,
      event.intent
    ) || reportAuthorityNoop(current);
  }

  if (event.type === REPORT_AUTHORITY_EVENT.PREVIEW_SUCCEEDED) {
    const request = event.request;
    if (!reportAuthorityRequestIsCurrent(current, request)) {
      return reportAuthorityNoop(current);
    }
    const entry = current.entriesById.get(request.reportId);
    const viewSource = event.view && typeof event.view === "object" && !Array.isArray(event.view)
      ? event.view
      : {};
    const view = Object.freeze({...viewSource});
    const selectionSource = request.intent === "auto"
      ? "auto"
      : request.intent === "refresh"
        ? current.stable?.selectionSource === "auto" ? "auto" : "manual"
        : "manual";
    const stable = Object.freeze({
      reportId: request.reportId,
      generation: current.generation,
      sessionId: typeof entry?.session_id === "string" ? entry.session_id : "",
      entryFingerprint: request.expectedFingerprint,
      selectionSource,
      view,
    });
    const autoAttemptKey = request.intent === "auto"
      ? reportAuthorityAutoAttemptKey(current.generation, request.expectedSessionId)
      : current.autoAttemptKey;
    const state = reportAuthorityState(current, {
      stable,
      pending: null,
      deferredRefresh: null,
      autoAttemptKey,
      focusId: request.reportId,
    });
    return reportAuthorityResult(state, [
      reportAuthorityEffect("RENDER_STABLE", {view}),
      reportAuthorityEffect("RENDER_CATALOG_SELECTION", {
        reportId: stable.reportId,
        focusId: state.focusId,
      }),
      reportAuthorityEffect("SYNC_HARMONIZATION", {
        canHarmonize: state.canHarmonize,
      }),
    ]);
  }

  if (event.type === REPORT_AUTHORITY_EVENT.PREVIEW_FAILED) {
    const request = event.request;
    if (!reportAuthorityRequestIsCurrent(current, request)) {
      return reportAuthorityNoop(current);
    }
    const autoAttemptKey = request.intent === "auto"
      ? reportAuthorityAutoAttemptKey(current.generation, request.expectedSessionId)
      : current.autoAttemptKey;
    let state = reportAuthorityState(current, {
      pending: null,
      autoAttemptKey,
    });
    const effects = state.stable
      ? [
          reportAuthorityEffect("RENDER_STABLE", {view: state.stable.view}),
          reportAuthorityEffect("RENDER_CATALOG_SELECTION", {
            reportId: state.stable.reportId,
            focusId: state.focusId,
          }),
        ]
      : [reportAuthorityEffect("RENDER_ERROR", {
          message: typeof event.message === "string" ? event.message : "",
        })];
    const resumed = reportAuthorityResumeDeferred(state, effects);
    state = resumed.state;
    return reportAuthorityResult(state, [
      ...resumed.effects,
      reportAuthorityEffect("SYNC_HARMONIZATION", {
        canHarmonize: state.canHarmonize,
      }),
    ]);
  }

  if (event.type === REPORT_AUTHORITY_EVENT.PREVIEW_STALE) {
    const request = event.request;
    if (
      !reportAuthorityRequestMatches(current.pending, request)
      || request.generation !== current.generation
    ) return reportAuthorityNoop(current);
    let state = reportAuthorityState(current, {pending: null});
    const effects = state.stable
      ? [
          reportAuthorityEffect("RENDER_STABLE", {view: state.stable.view}),
          reportAuthorityEffect("RENDER_CATALOG_SELECTION", {
            reportId: state.stable.reportId,
            focusId: state.focusId,
          }),
        ]
      : [reportAuthorityEffect("RENDER_EMPTY")];
    const resumed = reportAuthorityResumeDeferred(state, effects);
    state = resumed.state;
    return reportAuthorityResult(state, [
      ...resumed.effects,
      reportAuthorityEffect("SYNC_HARMONIZATION", {
        canHarmonize: state.canHarmonize,
      }),
    ]);
  }

  if (event.type === REPORT_AUTHORITY_EVENT.RESET_STARTED) {
    if (
      event.generation !== current.generation
      || current.resetCheckpoint !== null
    ) return reportAuthorityNoop(current);
    const pendingRefresh = current.pending?.intent === "refresh"
      ? Object.freeze({
          reportId: current.pending.reportId,
          generation: current.pending.generation,
          expectedFingerprint: current.pending.expectedFingerprint,
          selectionSource: current.stable?.selectionSource || "manual",
          catalogRequestId: current.pending.catalogRequestId,
        })
      : null;
    const resetCheckpoint = Object.freeze({
      stable: current.stable,
      deferredRefresh: pendingRefresh || current.deferredRefresh,
    });
    const state = reportAuthorityState(current, {
      nextCatalogRequestId: current.nextCatalogRequestId + 1,
      nextPreviewRequestId: current.nextPreviewRequestId + 1,
      pending: null,
      resetCheckpoint,
    });
    return reportAuthorityResult(state, [
      reportAuthorityEffect("DISABLE_HARMONIZATION"),
    ]);
  }

  if (event.type === REPORT_AUTHORITY_EVENT.RESET_ABORTED) {
    if (
      event.generation !== current.generation
      || current.resetCheckpoint === null
    ) return reportAuthorityNoop(current);
    const checkpoint = current.resetCheckpoint;
    const state = reportAuthorityState(current, {
      stable: checkpoint.stable,
      pending: null,
      deferredRefresh: checkpoint.deferredRefresh,
      resetCheckpoint: null,
    });
    const effects = state.stable
      ? [
          reportAuthorityEffect("RENDER_STABLE", {view: state.stable.view}),
          reportAuthorityEffect("RENDER_CATALOG_SELECTION", {
            reportId: state.stable.reportId,
            focusId: state.focusId,
          }),
        ]
      : [reportAuthorityEffect("RENDER_EMPTY")];
    return reportAuthorityResult(state, [
      ...effects,
      reportAuthorityEffect("SYNC_HARMONIZATION", {
        canHarmonize: state.canHarmonize,
      }),
    ]);
  }

  if (event.type === REPORT_AUTHORITY_EVENT.RESET_COMPLETED) {
    if (
      current.resetCheckpoint === null
      || event.generation !== current.generation + 1
    ) return reportAuthorityNoop(current);
    const state = createReportAuthorityState(event.generation);
    return reportAuthorityResult(state, [
      reportAuthorityEffect("RENDER_CATALOG", {entries: Object.freeze([])}),
      reportAuthorityEffect("RENDER_EMPTY"),
      reportAuthorityEffect("DISABLE_HARMONIZATION"),
    ]);
  }

  if (event.type === REPORT_AUTHORITY_EVENT.HARMONIZATION_STATE_CHANGED) {
    const state = reportAuthorityState(current, {
      harmonizationStartPending: event.harmonizationStartPending === true,
      harmonizationRunActive: event.harmonizationRunActive === true,
    });
    return reportAuthorityResult(state, [
      reportAuthorityEffect("SYNC_HARMONIZATION", {
        canHarmonize: state.canHarmonize,
      }),
    ]);
  }

  if (event.type === REPORT_AUTHORITY_EVENT.FOCUS_MOVED) {
    if (!current.entriesById.has(event.focusId)) return reportAuthorityNoop(current);
    const state = reportAuthorityState(current, {focusId: event.focusId});
    return reportAuthorityResult(state, [
      reportAuthorityEffect("RENDER_CATALOG_SELECTION", {
        reportId: state.stable?.reportId || null,
        focusId: state.focusId,
      }),
    ]);
  }

  return reportAuthorityNoop(current);
}

function reportPreviewView(reportId, preview) {
  const mode = preview?.mode === "html"
    ? "html"
    : preview?.mode === "file"
      ? "file"
      : "text";
  return Object.freeze({
    reportId,
    mode,
    kind: String(preview?.kind || preview?.mode || ""),
    title: String(preview?.title || preview?.file_name || reportId),
    content: typeof preview?.content === "string" ? preview.content : "",
    size: preview?.size ?? "",
    fileHref: `/api/reports/${encodeURIComponent(reportId)}/file`,
  });
}

function projectReportAuthority(authority = reportAuthority) {
  const state = window.MorphicWorkbenchState;
  state.activeReportSessionId = authority.activeSessionId;
  state.activeReportId = authority.stable?.reportId || null;
  state.reportSelectionSource = authority.stable?.selectionSource || null;
  state.reportFocusId = authority.focusId;
  state.reportAutoSelectionKey = authority.autoAttemptKey;
}

function transitionReportAuthority(event) {
  const previousCanHarmonize = reportAuthority.canHarmonize;
  const transition = reduceReportAuthority(reportAuthority, event);
  reportAuthority = transition.state;
  projectReportAuthority(reportAuthority);
  const effects = Array.from(transition.effects);
  const hasHarmonizationEffect = effects.some((effect) => (
    effect.type === "SYNC_HARMONIZATION"
    || effect.type === "DISABLE_HARMONIZATION"
  ));
  if (!hasHarmonizationEffect && previousCanHarmonize !== reportAuthority.canHarmonize) {
    effects.push(reportAuthorityEffect("SYNC_HARMONIZATION", {
      canHarmonize: reportAuthority.canHarmonize,
    }));
  }
  return Object.freeze(effects);
}

function ensureReportAuthorityGeneration(generation = caseGeneration) {
  if (generation !== caseGeneration || reportAuthority.generation === generation) return;
  reportAuthority = createReportAuthorityState(generation);
  projectReportAuthority(reportAuthority);
}

function syncReportHarmonizationEffect(canHarmonize) {
  const button = $("#harmonization-start-button");
  if (button) button.disabled = !canHarmonize;
}

function syncReportHarmonizationAvailability() {
  return applyReportAuthorityEffects(transitionReportAuthority({
    type: REPORT_AUTHORITY_EVENT.HARMONIZATION_STATE_CHANGED,
    harmonizationStartPending:
      window.MorphicWorkbenchState.harmonizationStartPending === true,
    harmonizationRunActive:
      window.MorphicWorkbenchState.harmonizationRunActive === true,
  }));
}

function reportListItems(reportList = $("#report-list")) {
  const scopedItems = reportList?.querySelectorAll
    ? Array.from(reportList.querySelectorAll(".report-item"))
    : [];
  if (scopedItems.length > 0) return scopedItems;
  return Array.from(document.querySelectorAll(".report-item"));
}

function reportListAnchorId(items, reportId, focusId) {
  const hasId = (id) => items.some((item) => item.dataset.reportId === id);
  if (hasId(focusId)) return focusId;
  if (hasId(reportId)) return reportId;
  return items[0]?.dataset.reportId || null;
}

function nextReportFocusIndex(index, length, key, mobile) {
  if (length <= 0) return -1;
  if (key === "Home") return 0;
  if (key === "End") return length - 1;
  const backward = mobile ? key === "ArrowUp" : key === "ArrowLeft";
  const forward = mobile ? key === "ArrowDown" : key === "ArrowRight";
  if (backward) return Math.max(0, index - 1);
  if (forward) return Math.min(length - 1, index + 1);
  return index;
}

function renderReportCatalogSelection(reportId, focusId) {
  const reportList = $("#report-list");
  const reportItems = reportListItems(reportList);
  const fallbackFocusId = reportListAnchorId(reportItems, reportId, focusId);
  reportItems.forEach((item) => {
    const selected = item.dataset.reportId === reportId;
    item.classList.toggle("selected", selected);
    item.setAttribute("aria-pressed", selected ? "true" : "false");
    item.tabIndex = item.dataset.reportId === fallbackFocusId ? 0 : -1;
  });
}

function renderReportCatalog(entries) {
  const rl = $("#report-list");
  if (!rl) return;
  rl.replaceChildren();
  const state = window.MorphicWorkbenchState;
  const safeEntries = Array.isArray(entries) ? entries : [];
  safeEntries.forEach((entry) => {
    const item = document.createElement("button");
    item.className = "report-item";
    item.type = "button";
    item.dataset.reportId = entry.id;
    item.dataset.sessionId = entry.session_id;
    const selected = entry.id === state.activeReportId;
    item.setAttribute("aria-pressed", selected ? "true" : "false");
    item.classList.toggle("selected", selected);
    const kind = String(entry.kind || entry.type || "").toUpperCase();
    const icon = REPORT_KIND_ICONS[kind] || "📄";
    const copy = document.createElement("span");
    copy.className = "report-item-copy";
    const fileName = document.createElement("strong");
    fileName.textContent = `${icon} ${entry.file_name || entry.name || entry.id || "Unbekannt"}`;
    const fileMeta = document.createElement("span");
    fileMeta.textContent = `${kind} · ${formatReportTimestamp(entry.modified_at)}`;
    const clientMeta = document.createElement("span");
    clientMeta.className = "report-item-client";
    clientMeta.textContent = entry.client_label;
    clientMeta.setAttribute("aria-label", `Klient: ${entry.client_label}`);
    const sessionMeta = document.createElement("span");
    sessionMeta.className = "report-item-session";
    sessionMeta.textContent = entry.session_label;
    sessionMeta.setAttribute("aria-label", `Session: ${entry.session_label}`);
    copy.appendChild(fileName);
    copy.appendChild(fileMeta);
    item.appendChild(copy);
    item.appendChild(clientMeta);
    item.appendChild(sessionMeta);
    item.addEventListener("click", () => (
      renderReportPreview(entry.id, caseGeneration, "manual")
    ));
    rl.appendChild(item);
  });
  renderReportCatalogSelection(state.activeReportId, state.reportFocusId);
}

function syncReportListOrientation() {
  const list = $("#report-list");
  if (!list) return;
  const isVertical = reportListIsMobile();
  list.setAttribute("aria-orientation", isVertical ? "vertical" : "horizontal");
}

function reportListIsMobile() {
  return reportListMobileQuery
    ? reportListMobileQuery.matches
    : window.innerWidth <= 768;
}

function subscribeReportListOrientation() {
  if (typeof reportListMobileQuery?.addEventListener === "function") {
    reportListMobileQuery.addEventListener("change", syncReportListOrientation);
  } else if (typeof reportListMobileQuery?.addListener === "function") {
    reportListMobileQuery.addListener(syncReportListOrientation);
  } else {
    window.addEventListener("resize", syncReportListOrientation);
  }
}

function focusReportItem(item) {
  if (!item) return;
  const list = $("#report-list");
  if (!list) return;
  const items = reportListItems(list);
  items.forEach((i) => { i.tabIndex = -1; });
  item.tabIndex = 0;
  transitionReportAuthority({
    type: REPORT_AUTHORITY_EVENT.FOCUS_MOVED,
    focusId: item.dataset.reportId,
  });
  item.focus();
  item.scrollIntoView({block: "nearest", inline: "nearest"});
}

function handleReportListKeydown(event) {
  const list = $("#report-list");
  if (!list || !list.contains(event.target)) return;
  const item = event.target.closest ? event.target.closest(".report-item") : null;
  if (!item) return;
  const items = Array.from(list.querySelectorAll(".report-item"));
  const index = items.indexOf(item);
  if (index === -1) return;
  const mobile = reportListIsMobile();
  const acceptedKeys = mobile
    ? ["ArrowUp", "ArrowDown", "Home", "End"]
    : ["ArrowLeft", "ArrowRight", "Home", "End"];
  if (!acceptedKeys.includes(event.key)) return;
  const targetIndex = nextReportFocusIndex(index, items.length, event.key, mobile);
  event.preventDefault();
  focusReportItem(items[targetIndex]);
}

function renderReportPreviewLoading() {
  const panel = $("#report-preview-panel");
  const frame = $("#report-preview-frame");
  const text = $("#report-preview-text");
  if (panel) panel.dataset.state = "loading";
  showReportPreviewState("wird geladen", "neutral");
  if (frame) {
    frame.srcdoc = "";
    frame.removeAttribute("src");
    frame.hidden = true;
  }
  if (text) {
    text.textContent = "Berichtsvorschau wird geladen …";
    text.hidden = false;
  }
  syncReportHarmonizationEffect(false);
}

function renderStableReportView(view) {
  const panel = $("#report-preview-panel");
  const frame = $("#report-preview-frame");
  const text = $("#report-preview-text");
  const title = $("#report-preview-title");
  const meta = $("#report-preview-meta");
  const link = $("#report-open-link");
  const kind = String(view?.kind || view?.mode || "").toUpperCase();
  const previewIcon = REPORT_KIND_ICONS[kind] || "📄";
  if (frame) {
    frame.srcdoc = "";
    frame.removeAttribute("src");
    frame.hidden = true;
  }
  if (text) {
    text.textContent = "";
    text.hidden = true;
  }
  if (view?.mode === "html" && frame) {
    frame.srcdoc = view.content || "";
    frame.hidden = false;
  } else if (view?.mode === "file" && text) {
    text.textContent = "PDF-Datei: Eine sichere Inline-Textvorschau ist nicht verfügbar. Bitte die Datei über ‚Datei öffnen‘ lokal anzeigen.";
    text.hidden = false;
  } else if (text) {
    text.textContent = view?.content || "";
    text.hidden = false;
  }
  if (panel) {
    panel.hidden = false;
    panel.dataset.state = "ready";
  }
  if (title) title.textContent = `${previewIcon} ${view?.title || view?.reportId || "Bericht"}`;
  if (meta) meta.textContent = `${view?.kind || view?.mode || ""} — ${view?.size ?? ""}`;
  if (link) {
    link.href = view?.fileHref || "#";
    link.hidden = !view?.fileHref;
  }
  showReportPreviewState("Vorschau geladen", "ok");
}

function renderEmptyReportPreview(message = "Waehle oben einen Bericht fuer die Vorschau.") {
  const panel = $("#report-preview-panel");
  const frame = $("#report-preview-frame");
  const text = $("#report-preview-text");
  const title = $("#report-preview-title");
  const meta = $("#report-preview-meta");
  const link = $("#report-open-link");
  if (panel) panel.dataset.state = "empty";
  if (frame) {
    frame.srcdoc = "";
    frame.removeAttribute("src");
    frame.hidden = true;
  }
  if (text) {
    text.textContent = message || "Waehle oben einen Bericht fuer die Vorschau.";
    text.hidden = false;
  }
  if (title) title.textContent = "Noch kein Bericht gewaehlt";
  if (meta) meta.textContent = "Keine stabile Vorschau geladen.";
  if (link) {
    link.href = "#";
    link.hidden = true;
  }
  syncReportHarmonizationEffect(false);
  showReportPreviewState("bereit", "neutral");
}

function renderReportPreviewError(message = "Berichtsvorschau konnte nicht geladen werden") {
  const panel = $("#report-preview-panel");
  const text = $("#report-preview-text");
  if (panel) panel.dataset.state = "error";
  if (text) {
    text.textContent = message;
    text.hidden = false;
  }
  syncReportHarmonizationEffect(false);
  showReportPreviewState(message, "bad");
}

function reportPreviewRequestStillCurrent(request) {
  const state = window.MorphicWorkbenchState;
  if (!request || request.generation !== caseGeneration || state.resetInProgress) {
    return false;
  }
  if (!reportAuthorityRequestIsCurrent(reportAuthority, request)) return false;
  if (request.intent !== "auto") return true;
  return Boolean(
    request.catalogRequestId === reportAuthority.nextCatalogRequestId - 1
  );
}

async function executeReportPreviewRequest(request) {
  if (!reportPreviewRequestStillCurrent(request)) {
    const effects = transitionReportAuthority({
      type: REPORT_AUTHORITY_EVENT.PREVIEW_STALE,
      request,
    });
    await applyReportAuthorityEffects(effects);
    return REPORT_PREVIEW_OUTCOME.STALE;
  }
  try {
    const preview = await window.MorphicWorkbenchApi.loadReportPreview(request.reportId);
    if (!reportPreviewRequestStillCurrent(request)) {
      const effects = transitionReportAuthority({
        type: REPORT_AUTHORITY_EVENT.PREVIEW_STALE,
        request,
      });
      await applyReportAuthorityEffects(effects);
      return REPORT_PREVIEW_OUTCOME.STALE;
    }
    const view = reportPreviewView(request.reportId, preview);
    if (view.mode === "html") {
      const frame = $("#report-preview-frame");
      if (frame) await loadSandboxedReportHtml(frame, view.content || "");
    }
    if (!reportPreviewRequestStillCurrent(request)) {
      const effects = transitionReportAuthority({
        type: REPORT_AUTHORITY_EVENT.PREVIEW_STALE,
        request,
      });
      await applyReportAuthorityEffects(effects);
      return REPORT_PREVIEW_OUTCOME.STALE;
    }
    const effects = transitionReportAuthority({
      type: REPORT_AUTHORITY_EVENT.PREVIEW_SUCCEEDED,
      request,
      view,
    });
    const accepted = effects.some((effect) => effect.type === "RENDER_STABLE");
    await applyReportAuthorityEffects(effects);
    if (!accepted) {
      if (reportAuthority.stable) {
        renderStableReportView(reportAuthority.stable.view);
        renderReportCatalogSelection(reportAuthority.stable.reportId, reportAuthority.focusId);
        syncReportHarmonizationEffect(reportAuthority.canHarmonize);
      }
      return REPORT_PREVIEW_OUTCOME.STALE;
    }
    return REPORT_PREVIEW_OUTCOME.SUCCESS;
  } catch (e) {
    if (!reportPreviewRequestStillCurrent(request)) {
      const effects = transitionReportAuthority({
        type: REPORT_AUTHORITY_EVENT.PREVIEW_STALE,
        request,
      });
      await applyReportAuthorityEffects(effects);
      return REPORT_PREVIEW_OUTCOME.STALE;
    }
    const effects = transitionReportAuthority({
      type: REPORT_AUTHORITY_EVENT.PREVIEW_FAILED,
      request,
      message: apiErrorMessage(e, "Berichtsvorschau konnte nicht geladen werden"),
    });
    const accepted = effects.some((effect) => (
      effect.type === "RENDER_ERROR" || effect.type === "RENDER_STABLE"
    ));
    await applyReportAuthorityEffects(effects);
    if (!accepted) return REPORT_PREVIEW_OUTCOME.STALE;
    return REPORT_PREVIEW_OUTCOME.FAILURE;
  }
}

async function applyReportAuthorityEffects(effects) {
  let outcome = REPORT_PREVIEW_OUTCOME.STALE;
  for (const effect of Array.isArray(effects) ? effects : []) {
    if (effect.type === "RENDER_CATALOG") renderReportCatalog(effect.entries);
    else if (effect.type === "RENDER_CATALOG_SELECTION") {
      renderReportCatalogSelection(effect.reportId, effect.focusId);
    } else if (effect.type === "RENDER_LOADING") renderReportPreviewLoading(effect.request);
    else if (effect.type === "RENDER_STABLE") renderStableReportView(effect.view);
    else if (effect.type === "RENDER_EMPTY") renderEmptyReportPreview(effect.message);
    else if (effect.type === "RENDER_ERROR") renderReportPreviewError(effect.message);
    else if (effect.type === "RENDER_CATALOG_ERROR") {
      const state = $("#reports-state");
      if (state) state.textContent = effect.message || "Fehler beim Laden";
    } else if (effect.type === "SYNC_HARMONIZATION") {
      if (reportAuthority.canHarmonize === (effect.canHarmonize === true)) {
        syncReportHarmonizationEffect(effect.canHarmonize === true);
      }
    } else if (effect.type === "DISABLE_HARMONIZATION") {
      syncReportHarmonizationEffect(false);
    } else if (effect.type === "LOAD_PREVIEW") {
      outcome = await executeReportPreviewRequest(effect.request);
    }
  }
  return outcome;
}

async function loadReports(generation = caseGeneration, propagateError = false) {
  const state = window.MorphicWorkbenchState;
  if (state.resetInProgress) return;
  ensureReportAuthorityGeneration(generation);
  const requestEffects = transitionReportAuthority({
    type: REPORT_AUTHORITY_EVENT.CATALOG_REQUESTED,
    generation,
  });
  const request = requestEffects.find((effect) => effect.type === "LOAD_CATALOG")?.request;
  if (!request) return;
  try {
    const data = await window.MorphicWorkbenchApi.loadReports();
    if (
      generation !== caseGeneration
      || state.resetInProgress
    ) return;
    const clients = Array.isArray(data?.clients) ? data.clients : [];
    const entries = flattenReportEntries(clients);
    const status = $("#reports-state");
    if (status) status.textContent = `${clients.length} Klient(en)`;
    const effects = transitionReportAuthority({
      type: REPORT_AUTHORITY_EVENT.CATALOG_ACCEPTED,
      generation,
      request,
      entries,
    });
    await applyReportAuthorityEffects(effects);
  } catch (e) {
    if (
      generation !== caseGeneration
      || state.resetInProgress
    ) return;
    const effects = transitionReportAuthority({
      type: REPORT_AUTHORITY_EVENT.CATALOG_FAILED,
      generation,
      request,
      message: apiErrorMessage(e, "Fehler beim Laden"),
    });
    await applyReportAuthorityEffects(effects);
    if (propagateError) throw e;
  }
}

async function renderReportPreview(
  reportId,
  generation = caseGeneration,
  selectionSource = "manual",
  options = {}
) {
  ensureReportAuthorityGeneration(generation);
  const intent = options.versionRefresh === true ? "refresh" : selectionSource;
  const effects = transitionReportAuthority({
    type: REPORT_AUTHORITY_EVENT.PREVIEW_REQUESTED,
    generation,
    reportId,
    intent,
  });
  if (!effects.some((effect) => effect.type === "LOAD_PREVIEW")) {
    return REPORT_PREVIEW_OUTCOME.STALE;
  }
  return applyReportAuthorityEffects(effects);
}

/* ── Harmonization ────────────────────────────────────────────────── */

function clearHarmonizationConfirmationState() {
  const confirmationState = $("#harmonization-confirmation-state");
  if (!confirmationState) return;
  confirmationState.textContent = "";
  confirmationState.className = "inline-state";
}

async function startHarmonizationJob(generation = caseGeneration) {
  const state = window.MorphicWorkbenchState;
  if (
    state.harmonizationStartPending ||
    state.harmonizationRunActive ||
    state.activeHarmonizationJobId ||
    !reportAuthority.canHarmonize
  ) return;
  state.harmonizationStartPending = true;
  await syncReportHarmonizationAvailability();
  const startButton = $("#harmonization-start-button");
  if (startButton) startButton.disabled = true;
  try {
    const body = formHarmonizationPayload();
    const confirmationState = $("#harmonization-confirmation-state");
    const maximumDurationConfirmed =
      $("#harmonization-max-duration-confirmation")?.checked === true;
    if (body.duration_factor === 21 && !maximumDurationConfirmed) {
      if (confirmationState) {
        confirmationState.textContent =
          "Bitte die Maximaldauer von 441 Minuten ausdrücklich bestätigen.";
        confirmationState.className = "inline-state bad";
      }
      return;
    }
    clearHarmonizationConfirmationState();
    const operationId = startOperationId("harmonization");
    const result = await window.MorphicWorkbenchApi.startHarmonization(
      body,
      operationId
    );
    if (generation !== caseGeneration) return;
    const jobId = String(result.job_id || "").trim();
    if (!jobId) throw new Error("Serverantwort enthält keine Harmonisierungs-Job-ID.");
    state.activeHarmonizationJobId = jobId;
    state.harmonizationRunActive = true;
    await syncReportHarmonizationAvailability();
    clearStartOperationId("harmonization");
    const panel = $("#harmonization-status-panel");
    if (panel) panel.hidden = false;
    const jl = $("#harmonization-job-id-label");
    if (jl) jl.textContent = jobId;
    const ml = $("#harmonization-mode-label");
    if (ml) ml.textContent = HARMONIZATION_MODE_LABELS[body.intention] || body.intention;
    const refresh = $("#harmonization-refresh-button");
    if (refresh) refresh.disabled = false;
    const stop = $("#harmonization-stop-button");
    if (stop) stop.disabled = false;
    pollHarmonizationJob(jobId, generation);
  } catch (e) {
    if (generation === caseGeneration) {
      if (!shouldRetainStartOperation(e)) {
        clearStartOperationId("harmonization");
      }
      state.harmonizationRunActive = false;
      await syncReportHarmonizationAvailability();
      const message = e?.status
        ? apiErrorMessage(e, "Harmonisierung konnte nicht gestartet werden")
        : "Harmonisierungsantwort nicht bestätigt. Erneuter Start gleicht denselben Vorgang ab.";
      showInlineState(message, "bad");
    }
  } finally {
    state.harmonizationStartPending = false;
    await syncReportHarmonizationAvailability();
    if (
      generation === caseGeneration &&
      startButton &&
      !state.harmonizationRunActive
    ) syncReportHarmonizationEffect(reportAuthority.canHarmonize);
  }
}

async function pollHarmonizationJob(jobId, generation = caseGeneration, failureCount = 0) {
  const key = `${generation}:${jobId}`;
  if (harmonizationPollInFlight?.key === key) return harmonizationPollInFlight.promise;
  const promise = _pollHarmonizationJobOnce(jobId, generation, failureCount);
  const authority = {key, promise};
  harmonizationPollInFlight = authority;
  return promise.finally(() => {
    if (harmonizationPollInFlight === authority) harmonizationPollInFlight = null;
  });
}

async function _pollHarmonizationJobOnce(jobId, generation = caseGeneration, failureCount = 0) {
  if (
    generation !== caseGeneration ||
    window.MorphicWorkbenchState.activeHarmonizationJobId !== jobId
  ) return;
  if (harmonizationPollTimer) clearTimeout(harmonizationPollTimer);
  try {
    const data = await window.MorphicWorkbenchApi.pollHarmonization(jobId);
    if (
      generation !== caseGeneration ||
      window.MorphicWorkbenchState.activeHarmonizationJobId !== jobId
    ) return;
    clearOwnedPollDegradation("harmonization", jobId, generation);
    const sl = $("#harmonization-status-label");
    if (sl) sl.textContent = statusLabel(data.status);
    const pf = $("#harmonization-progress-fill");
    if (pf) pf.style.width = `${data.progress_percent || 0}%`;
    const progressbar = $("#harmonization-progress");
    if (progressbar) {
      progressbar.setAttribute("aria-valuenow", String(Math.round(data.progress_percent || 0)));
    }
    const pl = $("#harmonization-progress-label");
    if (pl) pl.textContent = data.progress_percent != null ? `${data.progress_percent.toFixed(0)}%` : "-";
    const ph = $("#harmonization-phase-label");
    if (ph) ph.textContent = data.phase || "-";
    const cl = $("#harmonization-cycles-label");
    if (cl) cl.textContent = `${data.cycles_completed || 0} / ${data.total_cycles || 0}`;
    const el = $("#harmonization-error-label");
    if (el) el.textContent = data.error_message || (data.manual_action_required ? "Manuelle Folgeaktion erforderlich" : "kein Fehler");
    const lease = $("#harmonization-lease-label");
    if (lease) lease.textContent = data.lease?.heartbeat_at || "kein Heartbeat";
    if (["pending", "running"].includes(data.status)) {
      harmonizationPollTimer = setTimeout(() => pollHarmonizationJob(jobId, generation, 0), 2000);
    } else {
      window.MorphicWorkbenchState.harmonizationRunActive = false;
      window.MorphicWorkbenchState.activeHarmonizationJobId = null;
      await syncReportHarmonizationAvailability();
    }
  } catch (e) {
    if (
      generation !== caseGeneration ||
      window.MorphicWorkbenchState.activeHarmonizationJobId !== jobId
    ) return;
    const error = $("#harmonization-error-label");
    if ([401, 403].includes(e?.status)) {
      if (error) error.textContent = "Anmeldung erforderlich - Polling pausiert";
      harmonizationPollDegradation = {
        jobId,
        generation,
        revision: showInlineState("Harmonisierungsstatus erfordert eine erneute Anmeldung.", "bad"),
      };
      return;
    }
    const nextFailure = failureCount + 1;
    if (nextFailure > MAX_POLL_FAILURES) {
      if (error) error.textContent = "Verbindung unterbrochen - Polling pausiert";
      harmonizationPollDegradation = {
        jobId,
        generation,
        revision: showInlineState("Harmonisierungsstatus ist offline; Polling wurde pausiert.", "bad"),
      };
      return;
    }
    if (error) error.textContent = "Verbindung unterbrochen - erneuter Versuch";
    harmonizationPollDegradation = {
      jobId,
      generation,
      revision: showInlineState("Harmonisierungsstatus voruebergehend nicht erreichbar.", "bad"),
    };
    harmonizationPollTimer = setTimeout(
      () => pollHarmonizationJob(jobId, generation, nextFailure),
      pollRetryDelay(nextFailure)
    );
  }
}

async function stopHarmonizationJob(generation = caseGeneration) {
  const jobId = window.MorphicWorkbenchState.activeHarmonizationJobId;
  if (!jobId) return;
  try {
    const stopped = await window.MorphicWorkbenchApi.stopHarmonization(jobId);
    if (generation !== caseGeneration) return;
    if (stopped.status !== "stopped") {
      throw new Error(`Harmonisierung nicht gestoppt (Status: ${stopped.status || "unbekannt"})`);
    }
    if (harmonizationPollTimer) clearTimeout(harmonizationPollTimer);
    window.MorphicWorkbenchState.harmonizationRunActive = false;
    window.MorphicWorkbenchState.activeHarmonizationJobId = null;
    await syncReportHarmonizationAvailability();
    const sl = $("#harmonization-status-label");
    if (sl) sl.textContent = "gestoppt";
    const stop = $("#harmonization-stop-button");
    if (stop) stop.disabled = true;
  } catch (e) {
    if (generation !== caseGeneration) return;
    showInlineState(apiErrorMessage(e, "Harmonisierung konnte nicht sicher gestoppt werden"), "bad");
  }
}

/* ── Step-Enter-Hook ──────────────────────────────────────────────── */

function updateFocusMiniSnapshot() {
  const form = $("#scan-form");
  if (!form) return;
  const data = new FormData(form);
  const focusOut = $("#mini-snapshot-focus");
  const levelOut = $("#mini-snapshot-level");
  const topnOut = $("#mini-snapshot-topn");
  if (focusOut) focusOut.textContent = String(data.get("focus") || "").trim() || "-";
  if (levelOut) levelOut.textContent = `Level ${data.get("profile_level") || "-"}`;
  if (topnOut) topnOut.textContent = `Top-${data.get("top_n") || "-"}`;
}

/* Wird von workbench-render.js:showStep() bei jedem Phasenwechsel aufgerufen.
 * Haelt Rendering (workbench-render.js) und Business-Logik (hier) getrennt. */
function onStepEnter(index) {
  if (index === 2) {
    // Phase 3: Fokus & Zielsetzung - Fokushistorie einblenden
    const consent = $("#focus-history-consent");
    if (consent) consent.checked = window.MorphicWorkbenchState.hasFocusHistoryConsent();
    const history = window.MorphicWorkbenchState.loadFocusHistory();
    window.MorphicWorkbenchRender.renderFocusHistoryChips(history, (value) => {
      const input = document.querySelector('#scan-form [name="focus"]');
      if (input) input.value = value;
      updateFocusMiniSnapshot();
    });
    updateFocusMiniSnapshot();
  }
  if (index === 5) {
    // Phase 6: Review & Freigabe - Zusammenfassungskarten aktuell halten
    window.MorphicWorkbenchRender.renderReviewCards(
      formScanPayload(),
      window.MorphicWorkbenchState.hardwareTruth,
      window.MorphicWorkbenchState.scanProfileCatalog
    );
  }
}
window.MorphicWorkbenchOnStepEnter = onStepEnter;

/* ── Navigation ───────────────────────────────────────────────────── */

function navigate(direction) {
  const state = window.MorphicWorkbenchState;
  const total = state.registry ? state.registry.steps.length : FALLBACK_STEPS.length;
  const next = state.currentStepIndex + direction;
  if (next < 0 || next >= total) return;
  enterStep(next, direction > 0);
}

function enterStep(index, enforceGate = true) {
  const state = window.MorphicWorkbenchState;
  const pendingStartGate = state.scanStartPending && index !== 6;
  const blocked = enforceGate || pendingStartGate ? phaseReadiness(index) : null;
  if (blocked) {
    showWizardNavigationState(blocked, "bad");
    return false;
  }
  const total = state.registry ? state.registry.steps.length : FALLBACK_STEPS.length;
  if (index < 0 || index >= total) return false;
  state.currentStepIndex = index;
  state.currentStepId = state.registry ? state.registry.steps[index].id : FALLBACK_STEPS[index].id;
  showWizardNavigationState("", "neutral");
  window.MorphicWorkbenchRender.showStep(index);
  return true;
}

async function resetWorkbenchForNewCase() {
  const state = window.MorphicWorkbenchState;
  if (
    state.pendingMutations > 0
    || state.emfTelemetryMutationPending
    || state.emfTelemetryMutationUnresolved
    || state.scanStartPending
    || state.resetInProgress
  ) {
    updateScanActionAvailability();
    showInlineState("Fallwechsel wartet auf den Abschluss der laufenden Serveraktion.", "bad");
    return false;
  }
  ensureReportAuthorityGeneration(caseGeneration);
  state.resetInProgress = true;
  await applyReportAuthorityEffects(transitionReportAuthority({
    type: REPORT_AUTHORITY_EVENT.RESET_STARTED,
    generation: caseGeneration,
  }));
  const reportHarmonizationButton = $("#harmonization-start-button");
  if (reportHarmonizationButton) reportHarmonizationButton.disabled = true;
  const unresolvedScanOperation = readExistingStartOperationId("scan");
  if (unresolvedScanOperation && !state.activeJobId) {
    const reconciliation = await reconcileExistingScanStartOperation(
      unresolvedScanOperation,
      caseGeneration
    );
    if (
      reconciliation.disposition !== "safe-to-replace"
      && !(reconciliation.disposition === "job" && state.activeJobId)
    ) {
      state.resetInProgress = false;
      await applyReportAuthorityEffects(transitionReportAuthority({
        type: REPORT_AUTHORITY_EVENT.RESET_ABORTED,
        generation: caseGeneration,
      }));
      updateScanActionAvailability();
      showInlineState(
        "Fallwechsel gesperrt: Abgleich des Starts ist noch offen; derselbe Schlüssel bleibt reserviert.",
        "bad"
      );
      return false;
    }
  }
  if (hasUnresolvedStartOperation("harmonization")) {
    state.resetInProgress = false;
    await applyReportAuthorityEffects(transitionReportAuthority({
      type: REPORT_AUTHORITY_EVENT.RESET_ABORTED,
      generation: caseGeneration,
    }));
    updateScanActionAvailability();
    showInlineState(
      "Fallwechsel gesperrt: unbestätigten Start zuerst mit derselben Aktion abgleichen.",
      "bad"
    );
    return false;
  }
  scanResultsRequestToken += 1;
  scanPreviewRequestToken += 1;
  updateScanActionAvailability();
  const resetButton = $("#new-case-button");
  if (resetButton) resetButton.disabled = true;
  let scanStopped = false;
  try {
    if (state.activeJobId) {
      const stoppedScan = await window.MorphicWorkbenchApi.stopScanJob(state.activeJobId, true);
      if (!isTerminalScanStatus(stoppedScan.status)) {
        throw new Error("Scan konnte nicht sicher beendet werden");
      }
      state.activeJobId = null;
      state.scanRunActive = false;
      clearStartOperationId("scan");
      scanStopped = true;
      if (jobPollTimer) clearTimeout(jobPollTimer);
      jobPollTimer = null;
    }
    if (state.activeHarmonizationJobId) {
      const stoppedHarmonization = await window.MorphicWorkbenchApi.stopHarmonization(
        state.activeHarmonizationJobId,
        true
      );
      if (!["stopped", "completed", "error", "interrupted"].includes(stoppedHarmonization.status)) {
        throw new Error("Harmonisierung konnte nicht sicher beendet werden");
      }
      state.activeHarmonizationJobId = null;
      state.harmonizationRunActive = false;
      if (harmonizationPollTimer) clearTimeout(harmonizationPollTimer);
      harmonizationPollTimer = null;
    }
  } catch (e) {
    state.resetInProgress = false;
    await applyReportAuthorityEffects(transitionReportAuthority({
      type: REPORT_AUTHORITY_EVENT.RESET_ABORTED,
      generation: caseGeneration,
    }));
    updateScanActionAvailability();
    if (resetButton) {
      resetButton.disabled = state.pendingMutations > 0
        || state.emfTelemetryMutationPending
        || state.emfTelemetryMutationUnresolved;
    }
    const prefix = scanStopped && state.activeHarmonizationJobId
      ? "Teilweiser Fallwechsel: Scan beendet; Harmonisierung bleibt unter Kontrolle"
      : "Fallwechsel abgebrochen: Serverarbeit nicht sicher beendet";
    showInlineState(apiErrorMessage(e, prefix), "bad");
    return false;
  }
  caseGeneration += 1;
  await applyReportAuthorityEffects(transitionReportAuthority({
    type: REPORT_AUTHORITY_EVENT.RESET_COMPLETED,
    generation: caseGeneration,
  }));
  if (jobPollTimer) clearTimeout(jobPollTimer);
  if (harmonizationPollTimer) clearTimeout(harmonizationPollTimer);
  jobPollTimer = null;
  harmonizationPollTimer = null;
  scanPollDegradation = null;
  harmonizationPollDegradation = null;
  scanPollInFlight = null;
  scanStopInFlight = null;
  terminalScanAuthority = null;
  const form = $("#scan-form");
  if (form) {
    form.reset();
    form.querySelectorAll('input:not([type="checkbox"]):not([type="radio"]), textarea').forEach((control) => {
      control.value = "";
    });
    form.querySelectorAll('input[type="checkbox"], input[type="radio"]').forEach((control) => {
      control.checked = false;
    });
  }
  document.querySelectorAll('[form="scan-form"]').forEach((control) => {
    if (control.type === "checkbox" || control.type === "radio") control.checked = false;
    else if (control.tagName === "SELECT") {
      const defaultIndex = Array.from(control.options).findIndex((option) => option.defaultSelected);
      control.selectedIndex = defaultIndex >= 0 ? defaultIndex : 0;
    }
    else control.value = "";
  });
  const imageFile = $("#image-file-input");
  if (imageFile) imageFile.value = "";
  const harmonizationForm = $("#harmonization-form");
  if (harmonizationForm) harmonizationForm.reset();
  clearHarmonizationConfirmationState();
  state.currentStepIndex = 0;
  state.currentStepId = "runtime";
  state.activeJobId = null;
  state.scanStartPending = false;
  setScanReservationControls(false);
  state.activeHarmonizationJobId = null;
  state.harmonizationStartPending = false;
  state.harmonizationRunActive = false;
  state.scanProfileCatalog = null;
  state.scanProfileCatalogStatus = "loading";
  state.scanProfileCatalogError = "";
  state.scanProfileCatalogLevel = null;
  updateScanActionAvailability();
  state.scanResults = null;
  state.runTrace = null;
  state.draft = {};
  ["#command-preview", "#run-trace-display", "#job-log-tail"].forEach((selector) => {
    const node = $(selector);
    if (node) node.textContent = "";
  });
  ["#job-status-panel", "#harmonization-status-panel"].forEach((selector) => {
    const node = $(selector);
    if (node) node.hidden = true;
  });
  const lifecycleDefaults = {
    "#job-id-label": "-",
    "#job-status-label": "nicht gestartet",
    "#job-returncode": "-",
    "#job-phase-label": "-",
    "#job-substep-label": "Warte auf Ausgabe...",
    "#job-progress-label": "wird aus Ausgabe abgeleitet",
    "#job-log-tail": "Noch keine Logausgabe.",
    "#harmonization-job-id-label": "-",
    "#harmonization-status-label": "nicht gestartet",
    "#harmonization-mode-label": "-",
    "#harmonization-phase-label": "-",
    "#harmonization-progress-label": "-",
    "#harmonization-lease-label": "-",
    "#harmonization-cycles-label": "-",
    "#harmonization-error-label": "kein Fehler",
    "#group-draft-state": "nicht gespeichert",
    "#group-consent-state": "keine Identität ausgewählt",
    "#group-analysis-feature-state": "serverseitig deaktiviert",
    "#group-analysis-policy-state": "keine Stärke festgelegt",
    "#group-scan-activation-state": "Keine produktive Wirkung: nicht bewusst aktiviert",
    "#client-context-state": "nicht gespeichert",
    "#harmonization-preview-state": "Waehle nach dem Scan einen Bericht fuer den Abschluss.",
  };
  Object.entries(lifecycleDefaults).forEach(([selector, value]) => {
    const node = $(selector);
    if (node) node.textContent = value;
  });
  const scanProgress = $("#job-progress-fill");
  if (scanProgress) {
    scanProgress.style.width = "0%";
    scanProgress.setAttribute("aria-valuenow", "0");
  }
  ["#results-profile-list", "#results-metric-grid", "#report-list"].forEach((selector) => {
    const node = $(selector);
    if (node) node.replaceChildren();
  });
  ["#review-client", "#review-focus", "#review-profile", "#review-hardware", "#review-scan-scope"].forEach((selector) => {
    const node = $(selector);
    if (node) node.replaceChildren();
  });
  const previewFrame = $("#report-preview-frame");
  if (previewFrame) {
    previewFrame.srcdoc = "";
    previewFrame.removeAttribute("src");
    previewFrame.hidden = true;
  }
  const previewText = $("#report-preview-text");
  if (previewText) {
    previewText.textContent = "Waehle oben einen Bericht fuer die Vorschau.";
    previewText.hidden = false;
  }
  const previewTitle = $("#report-preview-title");
  if (previewTitle) previewTitle.textContent = "Noch kein Bericht gewaehlt";
  const previewMeta = $("#report-preview-meta");
  if (previewMeta) previewMeta.textContent = "Keine Vorschau fuer den neuen Fall geladen.";
  const previewState = $("#report-preview-state");
  if (previewState) {
    previewState.textContent = "bereit";
    previewState.className = "inline-state neutral";
  }
  const previewLink = $("#report-open-link");
  if (previewLink) {
    previewLink.href = "#";
    previewLink.hidden = true;
  }
  const harmonizationProgress = $("#harmonization-progress");
  if (harmonizationProgress) harmonizationProgress.setAttribute("aria-valuenow", "0");
  const harmonizationFill = $("#harmonization-progress-fill");
  if (harmonizationFill) harmonizationFill.style.width = "0%";
  const groupActivation = $("#group-scan-activation-enabled");
  const groupDraft = $("#group-scan-draft-id");
  if (groupActivation) groupActivation.checked = false;
  if (groupDraft) groupDraft.selectedIndex = 0;
  resetGroupDraftForm();
  [
    "#group-identity-first-name", "#group-identity-last-name",
    "#group-identity-birth-date", "#group-identity-birth-place",
    "#group-consent-client-id", "#group-consent-confirmation",
  ].forEach((selector) => {
    const node = $(selector);
    if (node) node.value = "";
  });
  ["#consent-local", "#consent-safety", "#group-identity-persistence-consent", "#context-persistence-consent", "#template-sensitive-consent"].forEach((selector) => {
    const node = $(selector);
    if (node) node.checked = false;
  });
  activeGroupDraftId = null;
  activeGroupConsentClientId = null;
  currentGroupAnalysisPolicy = null;
  const groupStrength = $("#group-analysis-strength");
  if (groupStrength) groupStrength.value = "";
  ["#group-consent-valid-until", "#group-identity-retention-days"].forEach((selector) => {
    const node = $(selector);
    if (node) node.value = "";
  });
  [
    "#register-group-identity-button", "#enable-group-consent-button",
    "#revoke-group-consent-button", "#save-client-context-button",
    "#save-group-analysis-policy-button", "#harmonization-start-button",
    "#harmonization-refresh-button", "#harmonization-stop-button",
  ].forEach((selector) => {
    const button = $(selector);
    if (button) button.disabled = true;
  });
  resetChoiceCardControls();
  const resetProfileLevel = parseInt(scanFormControl("profile_level")?.value || "3", 10);
  await loadScanProfileCatalog(resetProfileLevel, caseGeneration);
  updateFocusMiniSnapshot();
  updateGroupConsentControls();
  updateGroupScanActivationState();
  window.MorphicWorkbenchRender.resetSubstepTimeline();
  window.MorphicWorkbenchRender.showStep(0);
  state.resetInProgress = false;
  updateScanActionAvailability();
  showInlineState("Neuer Fall: lokale Eingaben und aktive Laufreferenzen wurden zurueckgesetzt.", "ok");
  if (resetButton) {
    resetButton.disabled = state.pendingMutations > 0
      || state.emfTelemetryMutationPending
      || state.emfTelemetryMutationUnresolved;
  }
  return true;
}

function resetChoiceCardControls() {
  const profile = $("#profile-template-select");
  const entropy = $("#entropy-mode-select");
  if (profile) profile.selectedIndex = 0;
  if (entropy) entropy.selectedIndex = 0;
  window.MorphicWorkbenchState.selectedSolfeggioBase = "432";
  const target = document.querySelector('#harmonization-form [name="target_frequency"]');
  if (target) target.value = "432";
  if (profile) profile.dispatchEvent(new Event("change", {bubbles: true}));
  if (entropy) entropy.dispatchEvent(new Event("change", {bubbles: true}));
  wireSolfeggioChoiceCards("#solfeggio-base-choices");
}

/* ── Choice-Cards (Radi144-Prinzip 5: Radio-Karten statt <select>) ──── */

function wireChoiceCards(containerSelector, selectSelector) {
  const select = $(selectSelector);
  if (!select) return;
  const options = Array.from(select.options).map((opt) => ({
    value: opt.value,
    label: opt.textContent.trim(),
    hint: opt.dataset.hint || "",
  }));
  const render = () => {
    window.MorphicWorkbenchRender.renderChoiceCards(containerSelector, options, select.value, (value) => {
      select.value = value;
      select.dispatchEvent(new Event("change", { bubbles: true }));
    });
  };
  render();
  select.addEventListener("change", render);
}

const SOLFEGGIO_BASE_OPTIONS = [
  { value: "432", label: "432 Hz", hint: "Setzt das gemeinsame Frequenzfeld auf 432 Hz." },
  { value: "528", label: "528 Hz", hint: "Setzt das gemeinsame Frequenzfeld auf 528 Hz." },
  { value: "429.62", label: "429.62 Hz", hint: "Setzt das gemeinsame Frequenzfeld auf 429,62 Hz." },
  { value: "498.90", label: "498.90 Hz", hint: "Setzt das gemeinsame Frequenzfeld auf 498,90 Hz." },
];

function wireSolfeggioChoiceCards(containerSelector) {
  const state = window.MorphicWorkbenchState;
  const targetFrequency = document.querySelector('#harmonization-form [name="target_frequency"]');
  const render = () => {
    window.MorphicWorkbenchRender.renderChoiceCards(
      containerSelector,
      SOLFEGGIO_BASE_OPTIONS,
      state.selectedSolfeggioBase == null ? "" : String(state.selectedSolfeggioBase),
      (value) => {
        state.selectedSolfeggioBase = value;
        if (targetFrequency) targetFrequency.value = value;
        render();
      }
    );
  };
  const syncFromFrequencyField = () => {
    const numericValue = Number(targetFrequency?.value);
    const matchingOption = Number.isFinite(numericValue)
      ? SOLFEGGIO_BASE_OPTIONS.find((option) => Number(option.value) === numericValue)
      : null;
    state.selectedSolfeggioBase = matchingOption ? matchingOption.value : null;
    render();
  };
  if (targetFrequency && targetFrequency.dataset.solfeggioChoiceWired !== "true") {
    targetFrequency.dataset.solfeggioChoiceWired = "true";
    targetFrequency.addEventListener("input", syncFromFrequencyField);
  }
  syncFromFrequencyField();
}

/* ── Bootstrap ────────────────────────────────────────────────────── */

async function bootstrapWorkbench() {
  const generation = caseGeneration;
  window.MorphicWorkbenchRender.renderStepper(FALLBACK_STEPS);
  window.MorphicWorkbenchRender.showStep(0);
  const scanStop = $("#scan-stop-button");
  if (scanStop) scanStop.addEventListener("click", () => stopActiveScanJob());
  const scanForm = $("#scan-form");
  if (scanForm) {
    scanForm.addEventListener("input", updateFocusMiniSnapshot);
  }
  const profileLevelControl = scanFormControl("profile_level");
  if (profileLevelControl) {
    profileLevelControl.addEventListener("change", () => {
      loadScanProfileCatalog(parseInt(profileLevelControl.value || "3", 10));
    });
  }
  wireScanProfileTopNControl();
  const initialProfileLevel = parseInt(scanFormControl("profile_level")?.value || "3", 10);
  const registryReady = (async () => {
      try {
        const registry = await window.MorphicWorkbenchApi.loadRegistry();
        if (generation !== caseGeneration) return;
        window.MorphicWorkbenchState.registry = registry;
        window.MorphicWorkbenchRender.renderStepper(registry.steps);
      } catch (e) {
        if (generation !== caseGeneration) return;
        window.MorphicWorkbenchRender.renderStepper(FALLBACK_STEPS);
      }
    })();
  void Promise.allSettled([
    registryReady,
    loadHealthAndSources(generation),
    loadScanProfileCatalog(initialProfileLevel, generation),
    loadEmfTelemetryStatus(generation),
    loadHardwareTruth(generation),
    loadReports(generation),
  ]);

  wireChoiceCards("#profile-template-choices", "#profile-template-select");
  wireChoiceCards("#entropy-mode-choices", "#entropy-mode-select");
  wireSolfeggioChoiceCards("#solfeggio-base-choices");
  wireEmfTelemetryControls();

  const focusHistoryConsent = $("#focus-history-consent");
  if (focusHistoryConsent) {
    focusHistoryConsent.checked = window.MorphicWorkbenchState.hasFocusHistoryConsent();
    focusHistoryConsent.addEventListener("change", () => {
      window.MorphicWorkbenchState.setFocusHistoryConsent(focusHistoryConsent.checked);
      const history = window.MorphicWorkbenchState.loadFocusHistory();
      window.MorphicWorkbenchRender.renderFocusHistoryChips(history, (value) => {
        const input = document.querySelector('#scan-form [name="focus"]');
        if (input) input.value = value;
        updateFocusMiniSnapshot();
      });
    });
  }
  const clearFocusHistory = $("#clear-focus-history");
  if (clearFocusHistory) {
    clearFocusHistory.addEventListener("click", () => {
      window.MorphicWorkbenchState.clearFocusHistory();
      window.MorphicWorkbenchRender.renderFocusHistoryChips([], () => {});
    });
  }

  const imageFileInput = $("#image-file-input");
  if (imageFileInput) imageFileInput.addEventListener("change", (e) => {
    const file = e.target.files && e.target.files[0];
    if (!file) return;
    const pathInput = $("#image-path-input");
    if (pathInput) pathInput.value = file.name;
  });

  const contextConsent = $("#context-persistence-consent");
  const saveClientContext = $("#save-client-context-button");
  if (contextConsent && saveClientContext) {
    contextConsent.addEventListener("change", () => {
      saveClientContext.disabled = !contextConsent.checked;
    });
    saveClientContext.addEventListener("click", async () => {
      const generation = caseGeneration;
      if (!contextConsent.checked) {
        showClientContextState("Explizite Speicherfreigabe erforderlich", "bad");
        return;
      }
      try {
        await window.MorphicWorkbenchApi.saveDraft({
          draft: clientContextDraftPayload(),
          persist_sensitive_data: true,
        });
        if (generation !== caseGeneration) return;
        showClientContextState("Lokaler Kontextentwurf gespeichert", "ok");
      } catch (e) {
        if (generation !== caseGeneration) return;
        showClientContextState(
          apiErrorMessage(e, "Lokaler Kontextentwurf konnte nicht gespeichert werden."),
          "bad"
        );
      }
    });
    loadClientContextDraft(generation);
  }

  // Wire event handlers
  const btnPrev = $("#btn-prev");
  const btnNext = $("#btn-next");
  if (btnPrev) btnPrev.addEventListener("click", () => navigate(-1));
  if (btnNext) btnNext.addEventListener("click", () => navigate(1));

  const previewBtn = $("#preview-button");
  if (previewBtn) previewBtn.addEventListener("click", () => generatePreview());
  const startBtn = $("#start-analysis-button");
  if (startBtn) startBtn.addEventListener("click", () => startScanJob());
  const scanRefresh = $("#scan-refresh-button");
  if (scanRefresh) scanRefresh.addEventListener("click", () => {
    const jid = window.MorphicWorkbenchState.activeJobId;
    if (jid) pollScanJob(jid, caseGeneration, 0);
  });

  const refreshBtn = $("#refresh-reports-button");
  if (refreshBtn) refreshBtn.addEventListener("click", () => loadReports());

  const reportList = $("#report-list");
  if (reportList) {
    reportList.addEventListener("keydown", handleReportListKeydown);
    syncReportListOrientation();
    subscribeReportListOrientation();
  }

  const harmStart = $("#harmonization-start-button");
  if (harmStart) harmStart.addEventListener("click", () => startHarmonizationJob());
  const durationFactor = document.querySelector('#harmonization-form [name="duration_factor"]');
  const maximumDurationConfirmation = $("#harmonization-max-duration-confirmation");
  if (durationFactor) durationFactor.addEventListener("input", clearHarmonizationConfirmationState);
  if (maximumDurationConfirmation) {
    maximumDurationConfirmation.addEventListener("change", clearHarmonizationConfirmationState);
  }
  const harmRefresh = $("#harmonization-refresh-button");
  if (harmRefresh) harmRefresh.addEventListener("click", () => {
    const jid = window.MorphicWorkbenchState.activeHarmonizationJobId;
    if (jid) pollHarmonizationJob(jid);
  });
  const harmStop = $("#harmonization-stop-button");
  if (harmStop) harmStop.addEventListener("click", () => stopHarmonizationJob());

  const modeSelect = $("#workbench-mode");
  if (modeSelect) modeSelect.addEventListener("change", (e) => {
    window.MorphicWorkbenchState.workbenchMode = e.target.value;
    window.MorphicWorkbenchRender.setModePill(e.target.value);
    loadHardwareTruth();
  });

  const openDetails = $("#open-details-button");
  if (openDetails) openDetails.addEventListener("click", () => enterStep(8));
  const openFinalize = $("#open-finalize-button");
  if (openFinalize) openFinalize.addEventListener("click", () => enterStep(9));
  const openHarmonize = $("#open-harmonize-button");
  if (openHarmonize) openHarmonize.addEventListener("click", () => enterStep(10));

  const saveTemplate = $("#save-template-button");
  if (saveTemplate) saveTemplate.addEventListener("click", async () => {
    const generation = caseGeneration;
    const payload = formScanPayload();
    delete payload.local_ai_enabled;
    const consent = $("#template-sensitive-consent");
    try {
      await window.MorphicWorkbenchApi.saveTemplate(
        "Session", payload, Boolean(consent && consent.checked)
      );
      if (generation !== caseGeneration) return;
      showInlineState("Template lokal gespeichert.", "ok");
    } catch (e) {
      if (generation !== caseGeneration) return;
      showInlineState(apiErrorMessage(e, "Template konnte nicht gespeichert werden."), "bad");
    }
  });
  const newCase = $("#new-case-button");
  if (newCase) newCase.addEventListener("click", resetWorkbenchForNewCase);

  // Keyboard navigation is intentionally scoped to the stepper so arrow keys
  // remain available for other controls and scrollable regions.
  const stepper = $("#wizard-stepper");
  if (stepper) stepper.addEventListener("keydown", (e) => {
    if (e.key === "ArrowRight") {
      e.preventDefault();
      navigate(1);
    }
    if (e.key === "ArrowLeft") {
      e.preventDefault();
      navigate(-1);
    }
    if (e.key === "Home") {
      e.preventDefault();
      enterStep(0, false);
    }
    if (e.key === "End") {
      e.preventDefault();
      const total = window.MorphicWorkbenchState.registry?.steps.length || FALLBACK_STEPS.length;
      enterStep(total - 1);
    }
  });
  const existingScanOperation = readExistingStartOperationId("scan");
  if (existingScanOperation) {
    await registryReady;
    if (generation !== caseGeneration) return;
    await reconcileExistingScanStartOperation(existingScanOperation, generation);
  }
  if (generation !== caseGeneration) return;
  document.body.dataset.workbenchReady = "true";
}

let activeGroupDraftId = null;
let currentGroupAnalysisPolicy = null;

function showGroupDraftState(message, state = "neutral") {
  const node = $("#group-draft-state");
  if (!node) return;
  node.textContent = message;
  node.className = `inline-state ${state}`;
}

function groupDraftPayload() {
  const consentRecorded = $("#group-members-consent")?.checked === true;
  const members = String($("#group-draft-members")?.value || "")
    .split(/[\s,]+/)
    .map((value) => value.trim())
    .filter(Boolean)
    .map((clientId) => ({client_id: clientId, consent_recorded: consentRecorded}));
  return {
    draft_id: activeGroupDraftId || `group-draft-${crypto.randomUUID().replaceAll("-", "")}`,
    draft: {
      group_label: String($("#group-draft-label")?.value || "").trim(),
      members,
      persistence_consent: $("#group-persistence-consent")?.checked === true,
      analysis_consent: $("#group-analysis-consent")?.checked === true,
      retention_days: 30,
    },
  };
}

function resetGroupDraftForm() {
  activeGroupDraftId = null;
  const values = ["#group-draft-label", "#group-draft-members", "#group-delete-confirmation"];
  values.forEach((selector) => { const node = $(selector); if (node) node.value = ""; });
  ["#group-members-consent", "#group-persistence-consent", "#group-analysis-consent"].forEach((selector) => {
    const node = $(selector); if (node) node.checked = false;
  });
  const save = $("#save-group-draft-button");
  const remove = $("#delete-group-draft-button");
  if (save) save.disabled = true;
  if (remove) remove.disabled = true;
}

function populateGroupDraft(payload) {
  const draft = payload?.draft || {};
  activeGroupDraftId = payload?.draft_id || null;
  const label = $("#group-draft-label");
  const members = $("#group-draft-members");
  const memberConsent = $("#group-members-consent");
  const persistence = $("#group-persistence-consent");
  const analysis = $("#group-analysis-consent");
  if (label) label.value = String(draft.group_label || "");
  if (members) members.value = (draft.members || []).map((member) => member.client_id).join("\n");
  if (memberConsent) memberConsent.checked = (draft.members || []).length > 0 && (draft.members || []).every((member) => member.consent_recorded === true);
  if (persistence) persistence.checked = draft.persistence_consent === true;
  if (analysis) analysis.checked = draft.analysis_consent === true;
  const save = $("#save-group-draft-button");
  const remove = $("#delete-group-draft-button");
  if (save) save.disabled = persistence?.checked !== true;
  if (remove) remove.disabled = !activeGroupDraftId;
}

async function loadInitialGroupDraft(generation = caseGeneration) {
  try {
    const safe = await window.MorphicWorkbenchApi.loadGroupDrafts();
    if (generation !== caseGeneration) return;
    renderGroupActivationDraftOptions(safe);
    const activationSelect = $("#group-scan-draft-id");
    if (activationSelect) activationSelect.selectedIndex = 0;
    const draftId = safe?.drafts?.[0]?.draft_id;
    if (!draftId) return;
    const payload = await window.MorphicWorkbenchApi.loadGroupDraft(draftId);
    if (generation !== caseGeneration) return;
    populateGroupDraft(payload);
    showGroupDraftState(`Lokaler Gruppenentwurf geladen: ${draftId}`, "neutral");
  } catch (e) {
    if (generation !== caseGeneration) return;
    showGroupDraftState(apiErrorMessage(e, "Lokaler Gruppenentwurf nicht verfügbar"), "bad");
  }
}

function renderGroupActivationDraftOptions(payload) {
  const select = $("#group-scan-draft-id");
  if (!select) return;
  const empty = document.createElement("option");
  empty.value = "";
  empty.textContent = "Keine Gruppe aktivieren";
  select.replaceChildren(empty);
  (payload?.drafts || []).forEach((draft) => {
    const group = (draft.vectors || []).find((vector) => vector.vector === "group");
    if (!group) return;
    const option = document.createElement("option");
    option.value = String(draft.draft_id || "");
    option.textContent = `${option.value} (${group.member_count || 0} Mitglieder)`;
    select.appendChild(option);
  });
  select.selectedIndex = 0;
  updateGroupScanActivationState();
}

async function refreshGroupActivationDraftOptions(generation = caseGeneration) {
  const safe = await window.MorphicWorkbenchApi.loadGroupDrafts();
  if (generation !== caseGeneration) return;
  renderGroupActivationDraftOptions(safe);
}

function wireGroupDraft() {
  const persistence = $("#group-persistence-consent");
  const save = $("#save-group-draft-button");
  const remove = $("#delete-group-draft-button");
  const dryRun = $("#group-erasure-dry-run-button");
  if (persistence && save) persistence.addEventListener("change", () => { save.disabled = !persistence.checked; });
  if (save) save.addEventListener("click", async () => {
    const generation = caseGeneration;
    if (!persistence?.checked) { showGroupDraftState("Explizite Speicherfreigabe erforderlich", "bad"); return; }
    try {
      const saved = await window.MorphicWorkbenchApi.saveGroupDraft(groupDraftPayload());
      if (generation !== caseGeneration) return;
      activeGroupDraftId = saved.draft_id;
      if (remove) remove.disabled = false;
      await refreshGroupActivationDraftOptions(generation);
      if (generation !== caseGeneration) return;
      showGroupDraftState(`DPAPI-geschützt gespeichert: ${saved.draft_id}`, "ok");
    } catch (e) {
      if (generation !== caseGeneration) return;
      showGroupDraftState(apiErrorMessage(e, "Gruppenentwurf konnte nicht gespeichert werden"), "bad");
    }
  });
  if (remove) remove.addEventListener("click", async () => {
    const generation = caseGeneration;
    const confirmation = String($("#group-delete-confirmation")?.value || "").trim();
    if (!activeGroupDraftId || confirmation !== activeGroupDraftId) { showGroupDraftState("Exakte Entwurfs-ID als Löschbestätigung eingeben", "bad"); return; }
    try {
      await window.MorphicWorkbenchApi.deleteGroupDraft(activeGroupDraftId, confirmation);
      if (generation !== caseGeneration) return;
      resetGroupDraftForm();
      await refreshGroupActivationDraftOptions(generation);
      if (generation !== caseGeneration) return;
      showGroupDraftState("Lokaler Gruppenentwurf gelöscht", "ok");
    } catch (e) {
      if (generation !== caseGeneration) return;
      showGroupDraftState(apiErrorMessage(e, "Gruppenentwurf konnte nicht gelöscht werden"), "bad");
    }
  });
  if (dryRun) dryRun.addEventListener("click", async () => {
    const generation = caseGeneration;
    try {
      const result = await window.MorphicWorkbenchApi.dryRunGroupDraftErasure();
      if (generation !== caseGeneration) return;
      showGroupDraftState(`${(result.drafts || []).length} Entwurf/Entwürfe zur Löschung vorgemerkt`, "neutral");
    } catch (e) {
      if (generation !== caseGeneration) return;
      showGroupDraftState(apiErrorMessage(e, "Löschplan nicht verfügbar"), "bad");
    }
  });
  loadInitialGroupDraft();
}

let activeGroupConsentClientId = null;

function showGroupConsentState(message, state = "neutral") {
  const node = $("#group-consent-state");
  if (!node) return;
  node.textContent = message;
  node.className = `inline-state ${state}`;
}

function groupIdentityRegistrationPayload() {
  return {
    first_name: String($("#group-identity-first-name")?.value || "").trim(),
    last_name: String($("#group-identity-last-name")?.value || "").trim(),
    birth_date: String($("#group-identity-birth-date")?.value || "").trim(),
    birth_place: String($("#group-identity-birth-place")?.value || "").trim(),
    persistence_consent: $("#group-identity-persistence-consent")?.checked === true,
    retention_days: Number($("#group-identity-retention-days")?.value || 365),
  };
}

function updateGroupConsentControls() {
  const confirmation = $("#group-consent-confirmation");
  const enable = $("#enable-group-consent-button");
  const revoke = $("#revoke-group-consent-button");
  const confirmed = Boolean(
    activeGroupConsentClientId
    && confirmation
    && confirmation.value.trim() === activeGroupConsentClientId
  );
  if (enable) enable.disabled = !confirmed;
  if (revoke) revoke.disabled = !confirmed;
}

function populateGroupConsentIdentity(identity) {
  activeGroupConsentClientId = String(identity?.client_id || "") || null;
  const clientId = $("#group-consent-client-id");
  if (clientId) clientId.value = activeGroupConsentClientId || "";
  updateGroupConsentControls();
}

async function loadInitialGroupConsent(generation = caseGeneration) {
  try {
    const result = await window.MorphicWorkbenchApi.loadGroupConsents();
    if (generation !== caseGeneration) return;
    const identity = result?.identities?.[0];
    if (!identity) return;
    populateGroupConsentIdentity(identity);
    const state = identity.consent_enabled ? "aktiv" : "nicht aktiv";
    showGroupConsentState(`Geschützte Identität geladen; Einwilligung ${state}`, "neutral");
  } catch (e) {
    if (generation !== caseGeneration) return;
    showGroupConsentState(apiErrorMessage(e, "Einwilligungsstatus nicht verfügbar"), "bad");
  }
}

function wireGroupConsent() {
  const identityPersistence = $("#group-identity-persistence-consent");
  const register = $("#register-group-identity-button");
  const confirmation = $("#group-consent-confirmation");
  const enable = $("#enable-group-consent-button");
  const revoke = $("#revoke-group-consent-button");
  if (identityPersistence && register) {
    identityPersistence.addEventListener("change", () => {
      register.disabled = !identityPersistence.checked;
    });
  }
  if (confirmation) confirmation.addEventListener("input", updateGroupConsentControls);
  if (register) register.addEventListener("click", async () => {
    const generation = caseGeneration;
    const payload = groupIdentityRegistrationPayload();
    if (!payload.persistence_consent) {
      showGroupConsentState("Explizite DPAPI-Speicherfreigabe erforderlich", "bad");
      return;
    }
    if (!payload.first_name || !payload.last_name || !payload.birth_date || !payload.birth_place) {
      showGroupConsentState("Identitätsfelder vollständig ausfüllen", "bad");
      return;
    }
    try {
      const identity = await window.MorphicWorkbenchApi.registerGroupIdentity(payload);
      if (generation !== caseGeneration) return;
      populateGroupConsentIdentity(identity);
      showGroupConsentState(`Sicher registriert: ${identity.client_id}`, "ok");
    } catch (e) {
      if (generation !== caseGeneration) return;
      showGroupConsentState(apiErrorMessage(e, "Identität konnte nicht registriert werden"), "bad");
    }
  });
  if (enable) enable.addEventListener("click", async () => {
    const generation = caseGeneration;
    if (!activeGroupConsentClientId || !confirmation || confirmation.value.trim() !== activeGroupConsentClientId) {
      showGroupConsentState("Exakte Client-ID als Bestätigung eingeben", "bad");
      return;
    }
    const validUntil = String($("#group-consent-valid-until")?.value || "").trim();
    if (!validUntil) {
      showGroupConsentState("Gültigkeitsende der Einwilligung angeben", "bad");
      return;
    }
    try {
      const enabled = true;
      const result = await window.MorphicWorkbenchApi.setGroupConsent(activeGroupConsentClientId, {
        confirmation_id: confirmation.value.trim(),
        enabled,
        valid_until: enabled ? new Date(validUntil).toISOString() : null,
      });
      if (generation !== caseGeneration) return;
      showGroupConsentState(`Einwilligung aktiviert bis ${result.valid_until}`, "ok");
    } catch (e) {
      if (generation !== caseGeneration) return;
      showGroupConsentState(apiErrorMessage(e, "Einwilligung konnte nicht aktiviert werden"), "bad");
    }
  });
  if (revoke) revoke.addEventListener("click", async () => {
    const generation = caseGeneration;
    if (!activeGroupConsentClientId || !confirmation || confirmation.value.trim() !== activeGroupConsentClientId) {
      showGroupConsentState("Exakte Client-ID als Bestätigung eingeben", "bad");
      return;
    }
    try {
      await window.MorphicWorkbenchApi.setGroupConsent(activeGroupConsentClientId, {
        confirmation_id: confirmation.value.trim(),
        enabled: false,
        valid_until: null,
      });
      if (generation !== caseGeneration) return;
      showGroupConsentState("Einwilligung sofort widerrufen", "ok");
    } catch (e) {
      if (generation !== caseGeneration) return;
      showGroupConsentState(apiErrorMessage(e, "Einwilligung konnte nicht widerrufen werden"), "bad");
    }
  });
  loadInitialGroupConsent();
}

function showGroupAnalysisPolicyState(message, state = "neutral") {
  const node = $("#group-analysis-policy-state");
  if (!node) return;
  node.textContent = message;
  node.className = `inline-state ${state}`;
}

function updateGroupScanActivationState() {
  const node = $("#group-scan-activation-state");
  if (!node) return;
  const requested = $("#group-scan-activation-enabled")?.checked === true;
  const draftId = String($("#group-scan-draft-id")?.value || "").trim();
  const featureEnabled = currentGroupAnalysisPolicy?.feature_enabled === true;
  const strengthReady = currentGroupAnalysisPolicy?.strength_explicit === true
    && Number(currentGroupAnalysisPolicy.strength) > 0;
  let message = "Keine produktive Wirkung: nicht bewusst aktiviert";
  let state = "neutral";
  if (!featureEnabled) {
    message = "Keine produktive Wirkung: serverseitiger Kill-Switch ist deaktiviert";
  } else if (!strengthReady) {
    message = "Keine produktive Wirkung: explizite Stärke fehlt oder ist 0";
  } else if (requested && !draftId) {
    message = "Keine produktive Wirkung: Gruppenentwurf bewusst auswählen";
    state = "bad";
  } else if (requested && draftId) {
    message = "Bereit: Gruppenwirkung wird nur für den nächsten realen Scan angefordert";
    state = "ok";
  }
  node.textContent = message;
  node.className = `inline-state ${state}`;
}

function renderGroupAnalysisPolicy(policy) {
  currentGroupAnalysisPolicy = policy || null;
  const feature = $("#group-analysis-feature-state");
  const strengthInput = $("#group-analysis-strength");
  if (feature) {
    feature.textContent = policy?.feature_enabled
      ? "Kill-Switch serverseitig freigegeben"
      : "Kill-Switch serverseitig deaktiviert";
  }
  if (strengthInput && policy?.strength_explicit === true) {
    strengthInput.value = String(policy.strength);
  }
  const strengthText = policy?.strength_explicit === true
    ? `Explizite Stärke ${policy.strength} vorgemerkt`
    : "Keine explizite Stärke festgelegt; keine produktive Wirkung";
  showGroupAnalysisPolicyState(strengthText, "neutral");
  updateGroupScanActivationState();
}

async function loadInitialGroupAnalysisPolicy(generation = caseGeneration) {
  try {
    const policy = await window.MorphicWorkbenchApi.loadGroupAnalysisPolicy();
    if (generation !== caseGeneration) return;
    renderGroupAnalysisPolicy(policy);
  } catch (e) {
    if (generation !== caseGeneration) return;
    showGroupAnalysisPolicyState(apiErrorMessage(e, "Aktivierungspolicy nicht verfügbar"), "bad");
  }
}

function wireGroupAnalysisPolicy() {
  const strengthInput = $("#group-analysis-strength");
  const save = $("#save-group-analysis-policy-button");
  const activationEnabled = $("#group-scan-activation-enabled");
  const activationDraft = $("#group-scan-draft-id");
  const updateSaveState = () => {
    if (!strengthInput || !save) return;
    const raw = strengthInput.value.trim();
    const value = Number(raw);
    save.disabled = !raw || !Number.isFinite(value) || value < 0 || value > 1;
  };
  if (strengthInput) strengthInput.addEventListener("input", updateSaveState);
  if (activationEnabled) activationEnabled.addEventListener("change", updateGroupScanActivationState);
  if (activationDraft) activationDraft.addEventListener("change", updateGroupScanActivationState);
  if (save) save.addEventListener("click", async () => {
    const generation = caseGeneration;
    const strength = Number(strengthInput?.value);
    if (!Number.isFinite(strength) || strength < 0 || strength > 1) {
      showGroupAnalysisPolicyState("Stärke muss explizit zwischen 0 und 1 liegen", "bad");
      return;
    }
    try {
      const policy = await window.MorphicWorkbenchApi.saveGroupAnalysisPolicy({strength});
      if (generation !== caseGeneration) return;
      renderGroupAnalysisPolicy(policy);
      showGroupAnalysisPolicyState(
        `Explizite Stärke ${policy.strength} vorgemerkt`,
        "ok"
      );
    } catch (e) {
      if (generation !== caseGeneration) return;
      showGroupAnalysisPolicyState(apiErrorMessage(e, "Stärke konnte nicht vorgemerkt werden"), "bad");
    }
  });
  loadInitialGroupAnalysisPolicy();
}

function setWorkbenchAuthLocked(locked) {
  const panel = $("#auth-session-panel");
  const navigation = $("#wizard-stepper");
  const workspace = $("#main-content");
  if (panel) panel.hidden = !locked;
  [navigation, workspace].forEach((node) => {
    if (!node) return;
    node.inert = locked;
    node.setAttribute("aria-hidden", locked ? "true" : "false");
  });
}

function startAuthenticatedWorkbench() {
  if (workbenchWired) return;
  workbenchWired = true;
  setWorkbenchAuthLocked(false);
  bootstrapWorkbench();
  wireGroupDraft();
  wireGroupConsent();
  wireGroupAnalysisPolicy();
}

async function initializeBrowserSession() {
  const form = $("#auth-session-form");
  const state = $("#auth-session-state");
  try {
    const status = await window.MorphicWorkbenchApi.loadAuthStatus();
    if (!status?.required || status?.authenticated) {
      startAuthenticatedWorkbench();
      return;
    }
  } catch (_) {
    // Fail closed: the protected workbench is not bootstrapped without auth status.
  }
  setWorkbenchAuthLocked(true);
  if (!form) return;
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const input = form.elements.api_key;
    const apiKey = String(input?.value || "");
    if (state) state.textContent = "Anmeldung wird geprüft";
    try {
      await window.MorphicWorkbenchApi.login(apiKey);
      if (input) input.value = "";
      if (state) state.textContent = "Sitzung aktiv";
      startAuthenticatedWorkbench();
    } catch (error) {
      if (input) input.value = "";
      if (state) state.textContent = apiErrorMessage(error, "Anmeldung fehlgeschlagen");
    }
  });
}

window.addEventListener("DOMContentLoaded", initializeBrowserSession);

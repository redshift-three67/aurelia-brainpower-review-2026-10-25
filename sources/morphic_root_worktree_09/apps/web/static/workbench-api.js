/* workbench-api.js — Browser API helpers fuer die Operator Workbench.
 *
 * Alle fetch-Aufrufe sind hier zentralisiert. Keine DOM-Manipulation,
 * keine Geschaeftslogik — nur I/O.
 */

async function requestJson(url, options = {}) {
  const mutating = String(options.method || "GET").toUpperCase() !== "GET";
  const state = window.MorphicWorkbenchState;
  const allowDuringReset = options.allowDuringReset === true;
  if (mutating && state?.resetInProgress && !allowDuringReset) {
    throw new Error("Fallwechsel läuft: neue Serveraktionen sind vorübergehend gesperrt");
  }
  const fetchOptions = {...options};
  delete fetchOptions.allowDuringReset;
  const requestedAmbiguousTimeout = Number(fetchOptions.ambiguousTimeoutMs);
  const hasAmbiguousMutationTimeout = mutating
    && Number.isFinite(requestedAmbiguousTimeout)
    && requestedAmbiguousTimeout > 0;
  delete fetchOptions.ambiguousTimeoutMs;
  const upstreamSignal = fetchOptions.signal;
  const configuredTimeout = Number(window.MORPHIC_REQUEST_TIMEOUT_MS);
  const timeoutMs = hasAmbiguousMutationTimeout
    ? requestedAmbiguousTimeout
    : Number.isFinite(configuredTimeout) && configuredTimeout > 0
      ? configuredTimeout
      : 10000;
  const boundedRequest = !mutating || hasAmbiguousMutationTimeout;
  let timedOut = false;
  const controller = boundedRequest ? new AbortController() : null;
  const abortFromUpstream = () => controller?.abort();
  const timeoutSignal = boundedRequest
    && typeof AbortSignal !== "undefined"
    && typeof AbortSignal.timeout === "function"
      ? AbortSignal.timeout(timeoutMs)
      : null;
  const abortForTimeout = () => {
    timedOut = true;
    controller?.abort();
  };
  let timeoutHandle = null;
  if (boundedRequest) {
    if (upstreamSignal) {
      if (upstreamSignal.aborted) controller.abort();
      else upstreamSignal.addEventListener("abort", abortFromUpstream, {once: true});
    }
    fetchOptions.signal = controller.signal;
    if (timeoutSignal) {
      timeoutSignal.addEventListener("abort", abortForTimeout, {once: true});
    } else {
      timeoutHandle = setTimeout(abortForTimeout, timeoutMs);
    }
  }
  if (mutating && state) {
    state.pendingMutations = Number(state.pendingMutations || 0) + 1;
    const reset = typeof document === "undefined" ? null : document.querySelector("#new-case-button");
    if (reset) reset.disabled = true;
  }
  try {
    let response;
    try {
      response = await fetch(url, fetchOptions);
    } catch (error) {
      if (timedOut && error?.name === "AbortError") {
        const timeoutError = new Error("Serveranfrage hat das Zeitlimit überschritten");
        timeoutError.code = "request_timeout";
        throw timeoutError;
      }
      throw error;
    }
    let payload = null;
    try {
      payload = await response.json();
    } catch (error) {
      if (boundedRequest && error?.name === "AbortError") {
        if (timedOut) {
          const timeoutError = new Error("Serveranfrage hat das Zeitlimit überschritten");
          timeoutError.code = "request_timeout";
          throw timeoutError;
        }
        throw error;
      }
      payload = null;
    }
    if (!response.ok) {
      const detailPayload = payload?.detail;
      let detail = typeof detailPayload === "string" ? detailPayload : "";
      if (Array.isArray(detailPayload)) {
        detail = detailPayload.map((entry) => {
          if (!entry || typeof entry !== "object") return String(entry || "");
          const location = Array.isArray(entry.loc)
            ? entry.loc.filter((part) => part !== "body").join(".")
            : "";
          return `${location ? `${location}: ` : ""}${entry.msg || "Ungueltige Eingabe"}`;
        }).filter(Boolean).join("; ");
      }
      const error = new Error(detail || `HTTP ${response.status}`);
      error.status = response.status;
      error.payload = payload;
      error.startOperationDisposition = response.headers?.get?.(
        "x-morphic-start-operation"
      ) || null;
      error.scanProfilePoolDisposition = response.headers?.get?.(
        "x-morphic-scan-profile-pool"
      ) || null;
      throw error;
    }
    return payload;
  } finally {
    if (timeoutHandle !== null) clearTimeout(timeoutHandle);
    if (timeoutSignal) {
      timeoutSignal.removeEventListener("abort", abortForTimeout);
    }
    if (boundedRequest && upstreamSignal) {
      upstreamSignal.removeEventListener("abort", abortFromUpstream);
    }
    if (mutating && state) {
      state.pendingMutations = Math.max(0, Number(state.pendingMutations || 0) - 1);
      const reset = typeof document === "undefined" ? null : document.querySelector("#new-case-button");
      if (reset) {
        reset.disabled = state.pendingMutations > 0
          || state.resetInProgress
          || state.emfTelemetryMutationPending
          || state.emfTelemetryMutationUnresolved;
      }
    }
  }
}

function requireStartOperationAuthority(operationId) {
  const normalized = String(operationId || "").trim();
  if (normalized.length < 8) {
    throw new Error("start operation authority is required");
  }
  return normalized;
}

function scanStartAmbiguousTimeoutMs() {
  const configured = Number(window.MORPHIC_SCAN_START_TIMEOUT_MS);
  return Number.isFinite(configured) && configured > 0 ? configured : 15000;
}

function emfMutationAmbiguousTimeoutMs() {
  const configured = Number(window.MORPHIC_EMF_MUTATION_TIMEOUT_MS);
  return Number.isFinite(configured) && configured > 0 ? configured : 10000;
}

window.MorphicWorkbenchApi = {
  /* ── Browser session ───────────────────────────────────────────── */

  async loadAuthStatus() {
    return requestJson("/api/auth/status");
  },

  async login(apiKey) {
    return requestJson("/api/auth/session", {
      method: "POST",
      headers: {"content-type": "application/json"},
      body: JSON.stringify({api_key: apiKey}),
    });
  },

  async logout() {
    return requestJson("/api/auth/session", {method: "DELETE"});
  },

  /* ── Workbench Registry & Hardware ─────────────────────────────── */

  async loadRegistry() {
    return requestJson("/api/workbench/registry");
  },

  async loadHardware(mode) {
    return requestJson(`/api/workbench/hardware?mode=${encodeURIComponent(mode)}`);
  },

  async loadEmfStatus() {
    return requestJson("/api/emf/status");
  },

  async enableEmfTelemetry() {
    return requestJson("/api/emf/enable", {
      method: "POST",
      ambiguousTimeoutMs: emfMutationAmbiguousTimeoutMs(),
    });
  },

  async disableEmfTelemetry() {
    return requestJson("/api/emf/disable", {
      method: "POST",
      ambiguousTimeoutMs: emfMutationAmbiguousTimeoutMs(),
    });
  },

  async loadScanProfileCatalog(profileLevel) {
    return requestJson(
      `/api/workbench/scan-profile-catalog?profile_level=${encodeURIComponent(profileLevel)}`
    );
  },

  async loadDraft() {
    return requestJson("/api/workbench/draft");
  },

  async saveDraft(payload) {
    return requestJson("/api/workbench/draft", {
      method: "PUT",
      headers: {"content-type": "application/json"},
      body: JSON.stringify(payload),
    });
  },

  async saveTemplate(name, payload, persistSensitiveData = false) {
    return requestJson("/api/workbench/templates", {
      method: "POST",
      headers: {"content-type": "application/json"},
      body: JSON.stringify({
        name,
        draft: payload,
        persist_sensitive_data: Boolean(persistSensitiveData),
      }),
    });
  },

  async loadGroupDrafts() {
    return requestJson("/api/workbench/group-draft");
  },

  async saveGroupDraft(payload) {
    return requestJson("/api/workbench/group-draft", {
      method: "PUT",
      headers: {"content-type": "application/json"},
      body: JSON.stringify(payload),
    });
  },

  async loadGroupDraft(draftId) {
    return requestJson(`/api/workbench/group-draft/${encodeURIComponent(draftId)}`);
  },

  async deleteGroupDraft(draftId, confirmationId) {
    return requestJson(`/api/workbench/group-draft/${encodeURIComponent(draftId)}`, {
      method: "DELETE",
      headers: {"content-type": "application/json"},
      body: JSON.stringify({confirmation_id: confirmationId}),
    });
  },

  async dryRunGroupDraftErasure() {
    return requestJson("/api/workbench/group-draft/erasure-dry-run");
  },

  async loadGroupConsents() {
    return requestJson("/api/workbench/group-consent");
  },

  async registerGroupIdentity(payload) {
    return requestJson("/api/workbench/group-consent/identity", {
      method: "POST",
      headers: {"content-type": "application/json"},
      body: JSON.stringify(payload),
    });
  },

  async setGroupConsent(clientId, payload) {
    return requestJson(`/api/workbench/group-consent/${encodeURIComponent(clientId)}`, {
      method: "PUT",
      headers: {"content-type": "application/json"},
      body: JSON.stringify(payload),
    });
  },

  async loadGroupAnalysisPolicy() {
    return requestJson("/api/workbench/group-analysis-policy");
  },

  async saveGroupAnalysisPolicy(payload) {
    return requestJson("/api/workbench/group-analysis-policy", {
      method: "PUT",
      headers: {"content-type": "application/json"},
      body: JSON.stringify(payload),
    });
  },

  async loadRunTrace(runId) {
    return requestJson(`/api/workbench/run-trace/${encodeURIComponent(runId)}`);
  },

  /* ── Scan / Health / Sources ───────────────────────────────────── */

  async loadHealth() {
    return requestJson("/api/health");
  },

  async loadSources() {
    return requestJson("/api/sources");
  },

  async loadScanPreview(body) {
    return requestJson("/api/scan/preview", {
      method: "POST",
      headers: {"content-type": "application/json"},
      body: JSON.stringify(body),
    });
  },

  async startScanJob(body, operationId) {
    const operationAuthority = requireStartOperationAuthority(operationId);
    return requestJson("/api/scan/jobs", {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "idempotency-key": operationAuthority,
      },
      body: JSON.stringify(body),
      ambiguousTimeoutMs: scanStartAmbiguousTimeoutMs(),
    });
  },

  async reconcileScanStartOperation(operationId) {
    const operationAuthority = requireStartOperationAuthority(operationId);
    return requestJson("/api/scan/start-operation/reconcile", {
      method: "POST",
      headers: {"idempotency-key": operationAuthority},
      ambiguousTimeoutMs: scanStartAmbiguousTimeoutMs(),
    });
  },

  async pollScanJob(jobId) {
   return requestJson(`/api/scan/jobs/${encodeURIComponent(jobId)}`);
 },

  async stopScanJob(jobId, allowDuringReset = false) {
    return requestJson(`/api/scan/jobs/${encodeURIComponent(jobId)}/stop`, {
      method: "POST",
      allowDuringReset,
    });
  },

 syncScanRunTrace(jobId) {
   return requestJson(`/api/scan/jobs/${encodeURIComponent(jobId)}/sync-trace`, {method: "POST"});
 },

  async loadScanResults(jobId) {
    return requestJson(`/api/scan/jobs/${encodeURIComponent(jobId)}/results`);
  },

  /* ── Reports ───────────────────────────────────────────────────── */

  async loadReports() {
    return requestJson("/api/reports");
  },

  async loadReportPreview(reportId) {
    return requestJson(`/api/reports/${encodeURIComponent(reportId)}/preview`);
  },

  /* ── Harmonization ─────────────────────────────────────────────── */

  async startHarmonization(body, operationId) {
    const operationAuthority = requireStartOperationAuthority(operationId);
    return requestJson("/api/harmonization/jobs", {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "idempotency-key": operationAuthority,
      },
      body: JSON.stringify(body),
    });
  },

  async pollHarmonization(jobId) {
    return requestJson(`/api/harmonization/jobs/${encodeURIComponent(jobId)}`);
  },

  async stopHarmonization(jobId, allowDuringReset = false) {
    return requestJson(`/api/harmonization/jobs/${encodeURIComponent(jobId)}/stop`, {
      method: "POST",
      allowDuringReset,
    });
  },
};

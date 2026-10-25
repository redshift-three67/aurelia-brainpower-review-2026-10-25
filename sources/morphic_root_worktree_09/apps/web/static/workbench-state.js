/* workbench-state.js — Zentraler Zustand der Operator Workbench.
 *
 * Wird von app.js (bootstrap) und workbench-render.js konsumiert.
 * Enthaelt KEINE DOM-Manipulation und KEINE fetch-Aufrufe.
 */

window.MorphicWorkbenchState = {
  registry: null,           // Phasen-Definition aus /api/workbench/registry
  currentStepId: "runtime",  // aktive Phase
  currentStepIndex: 0,
  workbenchMode: "standard", // "standard" | "expert"
  selectedSolfeggioBase: 432.0, // Solfeggio-Basisfrequenz (Task 7, Phase 11)
  activeJobId: null,
  scanStartOperationId: null,
  scanStartPending: false,
  scanRunActive: false,
  activeReportId: null,
  activeReportSessionId: null,
  reportFocusId: null,
  reportAutoSelectionKey: null,
  reportSelectionSource: null,
  activeHarmonizationJobId: null,
  harmonizationStartOperationId: null,
  harmonizationStartPending: false,
  harmonizationRunActive: false,
  emfTelemetryActive: null,
  emfTelemetryStatus: "unknown",
  emfTelemetryMutationPending: false,
  emfTelemetryMutationUnresolved: false,
  draft: {},                 // runtime-backed draft state
  hardwareTruth: null,       // Hardware-Truth-Snapshot
  scanProfileCatalog: null,  // tatsaechlich gescannter interner/externer Profil-Pool
  scanProfileCatalogStatus: "loading", // "loading" | "ready" | "error"
  scanProfileCatalogError: "",
  scanProfileCatalogLevel: null,
  scanResults: null,         // Ergebnis-Payload der letzten Scan-Ausfuehrung
  runTrace: null,            // Run-Trace-Daten fuer Details-Phase
  pendingMutations: 0,
  resetInProgress: false,       // blockiert Fallwechsel waehrend serverseitiger Mutationen

  /* ── Fokushistorie (lokal, nur nach explizitem Opt-in) ─────────── */
  FOCUS_HISTORY_KEY: "morphic_focus_history",
  FOCUS_HISTORY_CONSENT_KEY: "morphic_focus_history_consent",
  FOCUS_HISTORY_MAX: 8,

  hasFocusHistoryConsent() {
    return window.MorphicWorkbenchFocusHistoryStore.get(
      this.FOCUS_HISTORY_CONSENT_KEY
    ) === "true";
  },

  setFocusHistoryConsent(allowed) {
    if (allowed) {
      window.MorphicWorkbenchFocusHistoryStore.set(
        this.FOCUS_HISTORY_CONSENT_KEY,
        "true"
      );
    } else {
      window.MorphicWorkbenchFocusHistoryStore.remove(this.FOCUS_HISTORY_CONSENT_KEY);
      window.MorphicWorkbenchFocusHistoryStore.remove(this.FOCUS_HISTORY_KEY);
    }
  },

  loadFocusHistory() {
    if (!this.hasFocusHistoryConsent()) return [];
    try {
      const raw = window.MorphicWorkbenchFocusHistoryStore.get(this.FOCUS_HISTORY_KEY);
      const parsed = raw ? JSON.parse(raw) : [];
      return Array.isArray(parsed) ? parsed : [];
    } catch (e) {
      return [];
    }
  },

  saveFocusToHistory(value) {
    if (!this.hasFocusHistoryConsent()) return;
    const cleaned = String(value || "").trim();
    if (!cleaned) return;
    try {
      const history = this.loadFocusHistory().filter((v) => v !== cleaned);
      history.unshift(cleaned);
      const truncated = history.slice(0, this.FOCUS_HISTORY_MAX);
      window.MorphicWorkbenchFocusHistoryStore.set(
        this.FOCUS_HISTORY_KEY,
        JSON.stringify(truncated)
      );
    } catch (e) {}
  },

  clearFocusHistory() {
    window.MorphicWorkbenchFocusHistoryStore.remove(this.FOCUS_HISTORY_KEY);
  },
};

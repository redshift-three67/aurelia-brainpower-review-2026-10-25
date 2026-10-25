(function () {
  "use strict";

  const DEFAULT_TOKEN_HEADER = "X-Morphic-Admin-Token";
  const BOOTSTRAP_ENDPOINT = "/api/admin/bootstrap/exchange";
  const STATUS_ENDPOINT = "/api/admin/catalog/status";
  const ENTRIES_ENDPOINT = "/api/admin/catalog/entries";
  const RUNTIME_ENDPOINT = "/api/admin/catalog/runtime";
  let adminToken = "";
  let adminTokenHeader = DEFAULT_TOKEN_HEADER;

  function readBootstrapNonce() {
    const rawHash = window.location.hash || "";
    const params = new URLSearchParams(rawHash.startsWith("#") ? rawHash.slice(1) : rawHash);
    return params.get("admin_nonce") || "";
  }

  const bootstrapNonce = readBootstrapNonce();
  if (window.location.hash) {
    window.history.replaceState(null, document.title, window.location.pathname);
  }

  const elements = {};

  function byId(id) {
    return document.getElementById(id);
  }

  function bindElements() {
    [
      "admin-catalog-app",
      "admin-auth-state",
      "admin-session-expiry",
      "admin-refresh",
      "admin-status",
      "admin-context",
      "admin-current-revision",
      "admin-activation-version",
      "admin-revision-count",
      "admin-scope-summary",
      "admin-runtime-source",
      "admin-runtime-revision",
      "admin-runtime-redacted",
      "admin-entries-body",
      "admin-draft-id",
      "admin-revision-id",
      "admin-expected-version",
      "admin-expected-activation-version",
      "admin-expected-previous-revision",
      "admin-reason",
      "admin-entry-json",
      "admin-save-draft",
      "admin-validate-draft",
      "admin-load-diff",
      "admin-publish-draft",
      "admin-activate-revision",
      "admin-rollback-revision",
      "admin-load-runtime",
      "admin-diff",
      "admin-operation-result",
      "admin-runtime",
    ].forEach((id) => {
      elements[id] = byId(id);
    });
  }

  function setText(id, value) {
    if (elements[id]) {
      elements[id].textContent = value == null || value === "" ? "-" : String(value);
    }
  }

  function setStatus(message, tone) {
    setText("admin-status", message);
    setText("admin-auth-state", tone === "ok" ? "Admin aktiv" : message);
    if (elements["admin-auth-state"]) {
      elements["admin-auth-state"].className = `pill ${tone || "neutral"}`;
    }
    if (elements["admin-catalog-app"]) {
      elements["admin-catalog-app"].dataset.state = tone || "neutral";
    }
  }

  function setControlsEnabled(enabled) {
    [
      "admin-refresh",
      "admin-save-draft",
      "admin-validate-draft",
      "admin-load-diff",
      "admin-publish-draft",
      "admin-activate-revision",
      "admin-rollback-revision",
      "admin-load-runtime",
    ].forEach((id) => {
      if (elements[id]) {
        elements[id].disabled = !enabled;
      }
    });
  }

  function safeJson(value) {
    return JSON.stringify(value, null, 2);
  }

  function parseEntries() {
    const raw = elements["admin-entry-json"].value.trim();
    if (!raw) {
      return [];
    }
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) {
      throw new Error("Entries JSON muss ein Array sein.");
    }
    return parsed;
  }

  function textInput(id) {
    return elements[id].value.trim();
  }

  function intInput(id) {
    const raw = textInput(id);
    const value = Number.parseInt(raw || "0", 10);
    if (!Number.isInteger(value) || value < 0) {
      throw new Error(`${id} muss eine nichtnegative Ganzzahl sein.`);
    }
    return value;
  }

  function requireText(id, label) {
    const value = textInput(id);
    if (!value) {
      throw new Error(`${label} fehlt.`);
    }
    return value;
  }

  async function readJsonResponse(response) {
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      const detail = payload.detail || response.statusText || `HTTP ${response.status}`;
      throw new Error(String(detail));
    }
    return payload;
  }

  async function adminFetch(path, options) {
    const requestOptions = options || {};
    const headers = new Headers(requestOptions.headers || {});
    headers.set(adminTokenHeader, adminToken);
    if (requestOptions.body && !headers.has("Content-Type")) {
      headers.set("Content-Type", "application/json");
    }
    const response = await fetch(path, {
      ...requestOptions,
      credentials: "same-origin",
      headers,
    });
    return readJsonResponse(response);
  }

  async function bootstrap() {
    if (!bootstrapNonce) {
      setStatus("Adminstart ohne Bootstrap-Nonce.", "bad");
      setControlsEnabled(false);
      return;
    }

    const response = await fetch(BOOTSTRAP_ENDPOINT, {
      method: "POST",
      credentials: "same-origin",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ nonce: bootstrapNonce }),
    });
    const payload = await readJsonResponse(response);
    adminToken = String(payload.token || "");
    adminTokenHeader = String(payload.token_type || DEFAULT_TOKEN_HEADER);
    if (!adminToken) {
      throw new Error("Admin-Token fehlt.");
    }
    setText("admin-session-expiry", payload.expires_at || "Session aktiv");
    setStatus("Admin aktiv.", "ok");
    setControlsEnabled(true);
    await refreshCatalog();
  }

  function clearChildren(node) {
    while (node.firstChild) {
      node.removeChild(node.firstChild);
    }
  }

  function appendDefinition(list, term, value) {
    const dt = document.createElement("dt");
    dt.textContent = term;
    const dd = document.createElement("dd");
    dd.textContent = value == null || value === "" ? "-" : String(value);
    list.append(dt, dd);
  }

  function renderStatus(payload) {
    const context = payload.context || {};
    const scope = [context.tenant_id, context.workspace_id, context.scope]
      .filter(Boolean)
      .join(" / ");
    setText("admin-scope-summary", scope || "-");
    setText("admin-current-revision", payload.current_revision_id || "keine");
    setText("admin-activation-version", payload.activation_version);
    setText("admin-revision-count", payload.revision_count);

    if (elements["admin-context"]) {
      clearChildren(elements["admin-context"]);
      appendDefinition(elements["admin-context"], "Operator", context.operator_id);
      appendDefinition(elements["admin-context"], "Workspace", context.workspace_id);
      appendDefinition(elements["admin-context"], "Tenant", context.tenant_id);
      appendDefinition(elements["admin-context"], "Scope", context.scope);
    }
  }

  function createCell(value) {
    const td = document.createElement("td");
    td.textContent = value == null || value === "" ? "-" : String(value);
    return td;
  }

  function renderEntries(payload) {
    const body = elements["admin-entries-body"];
    if (!body) {
      return;
    }
    clearChildren(body);
    const entries = Array.isArray(payload.entries) ? payload.entries : [];
    if (!entries.length) {
      const row = document.createElement("tr");
      const cell = createCell("Keine aktiven Entries.");
      cell.colSpan = 5;
      row.append(cell);
      body.append(row);
      return;
    }
    entries.forEach((entry) => {
      const row = document.createElement("tr");
      const data = entry.data && typeof entry.data === "object" ? entry.data : {};
      row.append(
        createCell(entry.entry_type),
        createCell(entry.entry_id),
        createCell(entry.source_id),
        createCell(data.label || data.name || "-"),
        createCell(entry.provenance)
      );
      body.append(row);
    });
  }

  function renderRuntime(payload) {
    setText("admin-runtime-source", payload.selected_source || "-");
    setText("admin-runtime-revision", payload.active_revision_id || "keine");
    setText("admin-runtime-redacted", payload.redacted === true ? "redigiert" : "pruefen");
    setText("admin-runtime", safeJson(payload));
  }

  async function refreshCatalog() {
    const status = await adminFetch(STATUS_ENDPOINT);
    const entries = await adminFetch(ENTRIES_ENDPOINT);
    renderStatus(status);
    renderEntries(entries);
    setStatus(`Catalog geladen: ${entries.count || 0} Entries.`, "ok");
  }

  function draftPayload() {
    return {
      expected_version: intInput("admin-expected-version"),
      reason: requireText("admin-reason", "Grund"),
      entries: parseEntries(),
    };
  }

  async function saveDraft() {
    const draftId = requireText("admin-draft-id", "Draft ID");
    const payload = draftPayload();
    let result;
    if (payload.expected_version === 0) {
      result = await adminFetch("/api/admin/catalog/drafts", {
        method: "POST",
        body: JSON.stringify({ draft_id: draftId, ...payload }),
      });
    } else {
      result = await adminFetch(`/api/admin/catalog/drafts/${encodeURIComponent(draftId)}`, {
        method: "PATCH",
        body: JSON.stringify(payload),
      });
    }
    setText("admin-operation-result", safeJson(result));
    await refreshCatalog();
  }

  async function validateDraft() {
    const draftId = requireText("admin-draft-id", "Draft ID");
    const result = await adminFetch(
      `/api/admin/catalog/drafts/${encodeURIComponent(draftId)}/validate`,
      {
        method: "POST",
        body: JSON.stringify({
          expected_version: intInput("admin-expected-version"),
          reason: requireText("admin-reason", "Grund"),
        }),
      }
    );
    setText("admin-operation-result", safeJson(result));
  }

  async function loadDiff() {
    const draftId = requireText("admin-draft-id", "Draft ID");
    const result = await adminFetch(
      `/api/admin/catalog/drafts/${encodeURIComponent(draftId)}/diff`
    );
    setText("admin-diff", safeJson(result));
  }

  async function loadRuntime() {
    const result = await adminFetch(RUNTIME_ENDPOINT);
    renderRuntime(result);
  }

  async function publishDraft() {
    const draftId = requireText("admin-draft-id", "Draft ID");
    const result = await adminFetch(
      `/api/admin/catalog/drafts/${encodeURIComponent(draftId)}/publish`,
      {
        method: "POST",
        body: JSON.stringify({
          revision_id: requireText("admin-revision-id", "Revision ID"),
          expected_draft_version: intInput("admin-expected-version"),
          reason: requireText("admin-reason", "Grund"),
        }),
      }
    );
    setText("admin-operation-result", safeJson(result));
    await refreshCatalog();
  }

  async function activateRevision() {
    const revisionId = requireText("admin-revision-id", "Revision ID");
    const previous = textInput("admin-expected-previous-revision");
    const result = await adminFetch(
      `/api/admin/catalog/revisions/${encodeURIComponent(revisionId)}/activate`,
      {
        method: "POST",
        body: JSON.stringify({
          expected_previous_revision_id: previous || null,
          expected_activation_version: intInput("admin-expected-activation-version"),
          reason: requireText("admin-reason", "Grund"),
        }),
      }
    );
    setText("admin-operation-result", safeJson(result));
    await refreshCatalog();
  }

  async function rollbackRevision() {
    const revisionId = requireText("admin-revision-id", "Revision ID");
    const result = await adminFetch(
      `/api/admin/catalog/revisions/${encodeURIComponent(revisionId)}/rollback`,
      {
        method: "POST",
        body: JSON.stringify({
          expected_previous_revision_id: requireText(
            "admin-expected-previous-revision",
            "Expected Previous Revision"
          ),
          expected_activation_version: intInput("admin-expected-activation-version"),
          reason: requireText("admin-reason", "Grund"),
        }),
      }
    );
    setText("admin-operation-result", safeJson(result));
    await refreshCatalog();
  }

  async function runAction(action) {
    try {
      setStatus("Aktion laeuft.", "neutral");
      await action();
      setStatus("Aktion abgeschlossen.", "ok");
    } catch (error) {
      setStatus(error.message || "Aktion fehlgeschlagen.", "bad");
      setText("admin-operation-result", error.message || String(error));
    }
  }

  function bindEvents() {
    elements["admin-refresh"].addEventListener("click", () => runAction(refreshCatalog));
    elements["admin-save-draft"].addEventListener("click", () => runAction(saveDraft));
    elements["admin-validate-draft"].addEventListener("click", () => runAction(validateDraft));
    elements["admin-load-diff"].addEventListener("click", () => runAction(loadDiff));
    elements["admin-publish-draft"].addEventListener("click", () => runAction(publishDraft));
    elements["admin-activate-revision"].addEventListener("click", () => runAction(activateRevision));
    elements["admin-rollback-revision"].addEventListener("click", () => runAction(rollbackRevision));
    elements["admin-load-runtime"].addEventListener("click", () => runAction(loadRuntime));
  }

  document.addEventListener("DOMContentLoaded", () => {
    bindElements();
    bindEvents();
    setControlsEnabled(false);
    bootstrap().catch((error) => {
      setStatus(error.message || "Admin-Bootstrap fehlgeschlagen.", "bad");
      setControlsEnabled(false);
    });
  });
})();

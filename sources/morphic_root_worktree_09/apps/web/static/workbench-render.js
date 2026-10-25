/* workbench-render.js — Rendering-Logik fuer die Operator Workbench.
 *
 * Bekommt Daten vom State, erzeugt DOM-Knoten. Keine fetch-Aufrufe,
 * keine State-Mutationen (ausser via expliziter Callbacks).
 */

const DISPLAY_SCORE_FORMATTER = new Intl.NumberFormat("de-DE", {
  maximumFractionDigits: 3,
  useGrouping: false,
});
const EMF_PROXY_LABEL = "System-/Entropie-basierter EMF-Proxy-Index";
const EMF_PROXY_DERIVED_COPY = "Abgeleiteter System-/Entropie-Proxy; keine physische Feldmessung.";
const EMF_PROXY_METRICS = [
  ["Entropie", "entropy_score", "rng"],
  ["Jitter (ms)", "timing_jitter_ms", "cpu_timing"],
  ["Systemlast", "system_load", "system_load"],
  ["Sensorentropie", "sensor_entropy", "sensor_entropy"],
];
const EMF_SOURCE_STATUSES = new Set(["ok", "partial", "fallback"]);
const HARDWARE_STATUSES = new Set([
  "real_active",
  "real_available_not_used",
  "software_fallback",
  "not_implemented",
]);

function formatDisplayScore(value) {
  if (value === null || value === undefined || value === "") return "-";
  const numeric = Number(value);
  return Number.isFinite(numeric) ? DISPLAY_SCORE_FORMATTER.format(numeric) : "-";
}

function finiteEmfProxyValue(value) {
  if (value === null || value === undefined) return null;
  if (typeof value === "string" && value.trim() === "") return null;
  if (typeof value !== "number" && typeof value !== "string") return null;
  const numeric = Number(value);
  return Number.isFinite(numeric) ? numeric : null;
}

function formatEmfProxyValue(value) {
  const numeric = finiteEmfProxyValue(value);
  return numeric === null ? "--" : DISPLAY_SCORE_FORMATTER.format(numeric);
}

function normalizeEmfSourceStatus(value) {
  return EMF_SOURCE_STATUSES.has(value) ? value : "unknown";
}

function normalizeHardwareStatus(value) {
  return HARDWARE_STATUSES.has(value) ? value : "unknown";
}

function roundScoresForDisplay(value, key = "") {
  if (Array.isArray(value)) return value.map((item) => roundScoresForDisplay(item, key));
  if (value && typeof value === "object") {
    return Object.fromEntries(
      Object.entries(value).map(([childKey, childValue]) => [
        childKey,
        roundScoresForDisplay(childValue, childKey),
      ])
    );
  }
  if (typeof value === "number" && /score/i.test(key)) {
    return Math.round((value + Number.EPSILON) * 1000) / 1000;
  }
  return value;
}

window.MorphicWorkbenchFormatDisplayScore = formatDisplayScore;
window.MorphicWorkbenchRoundScoresForDisplay = roundScoresForDisplay;

window.MorphicWorkbenchRender = {
  /* ── Stepper ───────────────────────────────────────────────────── */

  renderStepper(steps) {
    const stepper = document.querySelector("#wizard-stepper");
    if (!stepper) return;
    stepper.replaceChildren();
    const requestedIndex = Number(window.MorphicWorkbenchState?.currentStepIndex || 0);
    const activeIndex = Math.max(0, Math.min(requestedIndex, Math.max(0, steps.length - 1)));
    steps.forEach((step, i) => {
      const btn = document.createElement("button");
      btn.className = "wizard-step" + (i === activeIndex ? " active" : "");
      btn.type = "button";
      btn.id = `wizard-step-${i}`;
      btn.dataset.step = String(i);
      btn.setAttribute("aria-controls", `${step.id}-phase`);
      btn.setAttribute("tabindex", i === activeIndex ? "0" : "-1");
      if (i === activeIndex) btn.setAttribute("aria-current", "step");
      const number = document.createElement("span");
      number.textContent = i + 1;
      btn.appendChild(number);
      btn.appendChild(document.createTextNode(step.label));
      btn.addEventListener("click", () => {
        const blocked = typeof window.MorphicWorkbenchCanEnterStep === "function"
          ? window.MorphicWorkbenchCanEnterStep(i)
          : null;
        if (blocked) {
          if (typeof window.MorphicWorkbenchOnNavigationBlocked === "function") {
            window.MorphicWorkbenchOnNavigationBlocked(blocked);
          }
          return;
        }
        window.MorphicWorkbenchState.currentStepIndex = i;
        window.MorphicWorkbenchState.currentStepId = step.id;
        this.showStep(i);
      });
      stepper.appendChild(btn);
      const panel = document.querySelector(`.wizard-panel[data-step="${i}"]`);
      if (panel) panel.setAttribute("aria-labelledby", btn.id);
    });
  },

  showStep(index) {
    const panels = document.querySelectorAll(".wizard-panel");
    const steps = document.querySelectorAll(".wizard-step");
    const total = steps.length || panels.length;
    panels.forEach((p, i) => {
      p.classList.toggle("active", i === index);
      p.setAttribute("aria-hidden", i === index ? "false" : "true");
    });
    steps.forEach((s, i) => {
      s.classList.toggle("active", i === index);
      if (i === index) s.setAttribute("aria-current", "step");
      else s.removeAttribute("aria-current");
      s.setAttribute("tabindex", i === index ? "0" : "-1");
    });
    this.updateProgress(index, total);
    const activeStep = steps[index];
    if (activeStep) {
      activeStep.focus();
      activeStep.scrollIntoView({block: "nearest", inline: "center"});
    }
    const prevBtn = document.querySelector("#btn-prev");
    const nextBtn = document.querySelector("#btn-next");
    if (prevBtn) prevBtn.disabled = index === 0;
    if (nextBtn) nextBtn.disabled = index === total - 1;
    /* Business-Logik-Hook: app.js registriert window.MorphicWorkbenchOnStepEnter,
     * damit dieses reine Rendering-Modul keine formScanPayload()/State-Kenntnis
     * braucht (Trennung Rendering vs. Logik bleibt erhalten). */
    if (typeof window.MorphicWorkbenchOnStepEnter === "function") {
      window.MorphicWorkbenchOnStepEnter(index);
    }
  },

  updateProgress(index, total) {
    const fill = document.querySelector("#wizard-progress-fill");
    const label = document.querySelector("#wizard-progress-label");
    const pct = ((index + 1) / total) * 100;
    if (fill) {
      fill.style.width = `${pct}%`;
      fill.setAttribute("aria-valuenow", String(Math.round(pct)));
    }
    if (label) label.textContent = `${index + 1} / ${total}`;
    const steps = document.querySelectorAll(".wizard-step");
    steps.forEach((s, i) => s.classList.toggle("completed", i < index));
  },

  /* ── Hardware Truth ────────────────────────────────────────────── */

  renderHardwareTruth(payload) {
    const grid = document.querySelector("#hardware-truth-grid");
    const calib = document.querySelector("#realtime-calibration");
    const warnings = document.querySelector("#hardware-gate-warnings");
    if (!grid) return;
    grid.replaceChildren();
    /* Backend liefert `components` als Dict (keyed by Komponenten-Id, siehe
     * apps/web/hardware_truth.py:build_hardware_truth_snapshot), nicht als
     * Array. Object.values() ist die korrekte Iterationsform. */
    const componentsRaw = payload.components || {};
    const components = Array.isArray(componentsRaw) ? componentsRaw : Object.values(componentsRaw);
    if (!components.length) {
      const note = document.createElement("p");
      note.className = "hardware-note";
      note.textContent = "Keine Hardware-Komponenten gemeldet.";
      grid.appendChild(note);
    }
    components.forEach((comp) => {
      const card = document.createElement("div");
      card.className = "hardware-card";
      const statusValue = normalizeHardwareStatus(comp.status);
      card.dataset.status = statusValue;
      const header = document.createElement("div");
      header.className = "hardware-card-header";
      const label = document.createElement("strong");
      label.textContent = comp.label || comp.id || "Unbekannt";
      const badge = document.createElement("span");
      badge.className = `hardware-status-badge status-${statusValue}`;
      badge.textContent = statusValue;
      const note = document.createElement("p");
      note.className = "hardware-note";
      note.textContent = comp.note || "";
      header.appendChild(label);
      header.appendChild(badge);
      card.appendChild(header);
      card.appendChild(note);
      grid.appendChild(card);
    });
    if (calib && payload.realtime_calibration) {
      const rc = payload.realtime_calibration;
      calib.replaceChildren();
      const emfIndex = finiteEmfProxyValue(rc.emf_index);
      const telemetryDisabled = rc.status === "disabled";
      if (telemetryDisabled || emfIndex === null) {
        const disabled = document.createElement("div");
        disabled.className = "emf-index-card is-disabled";
        const value = document.createElement("strong");
        value.className = "emf-index-value";
        value.textContent = "--";
        const copy = document.createElement("div");
        const title = document.createElement("span");
        title.className = "emf-index-label";
        title.textContent = EMF_PROXY_LABEL;
        const note = document.createElement("p");
        note.className = "hardware-note";
        note.textContent = telemetryDisabled
          ? "EMF-Telemetrie deaktiviert – keine Messung und kein geschätzter Nullwert."
          : "EMF-Telemetrie aktiv, aber aktuell liegt kein autoritativer Messwert vor.";
        const derived = document.createElement("p");
        derived.className = "hardware-note emf-index-derived";
        derived.textContent = EMF_PROXY_DERIVED_COPY;
        copy.appendChild(title);
        copy.appendChild(note);
        copy.appendChild(derived);
        disabled.appendChild(value);
        disabled.appendChild(copy);
        calib.appendChild(disabled);
      } else {
        const normalizedIndex = Math.max(0, Math.min(1, emfIndex));
        const emfCard = document.createElement("div");
        emfCard.className = "emf-index-card";
        const emfCopy = document.createElement("div");
        const emfLabel = document.createElement("span");
        emfLabel.className = "emf-index-label";
        emfLabel.textContent = EMF_PROXY_LABEL;
        const emfValue = document.createElement("strong");
        emfValue.className = "emf-index-value";
        emfValue.textContent = formatEmfProxyValue(rc.emf_index);
        const derived = document.createElement("p");
        derived.className = "hardware-note emf-index-derived";
        derived.textContent = EMF_PROXY_DERIVED_COPY;
        const gauge = document.createElement("div");
        gauge.className = "emf-index-gauge";
        gauge.setAttribute("role", "progressbar");
        gauge.setAttribute("aria-label", EMF_PROXY_LABEL);
        gauge.setAttribute("aria-valuemin", "0");
        gauge.setAttribute("aria-valuemax", "1");
        gauge.setAttribute("aria-valuenow", String(normalizedIndex));
        const gaugeFill = document.createElement("span");
        gaugeFill.style.width = `${normalizedIndex * 100}%`;
        gauge.appendChild(gaugeFill);
        emfCopy.appendChild(emfLabel);
        emfCopy.appendChild(emfValue);
        emfCopy.appendChild(derived);
        emfCopy.appendChild(gauge);
        emfCard.appendChild(emfCopy);
        calib.appendChild(emfCard);
      }
      if (!telemetryDisabled) {
        const metrics = document.createElement("div");
        metrics.className = "emf-source-list";
        const sourceHealth = rc.source_health && typeof rc.source_health === "object"
          ? rc.source_health
          : {};
        EMF_PROXY_METRICS.forEach(([label, valueKey, sourceKey]) => {
          const row = document.createElement("div");
          row.className = "emf-source-row";
          const metricLabel = document.createElement("span");
          metricLabel.className = "emf-source-label";
          metricLabel.textContent = label;
          const valueNode = document.createElement("strong");
          valueNode.className = "emf-source-value";
          valueNode.textContent = formatEmfProxyValue(rc[valueKey]);
          const source = document.createElement("code");
          source.className = "emf-source-key";
          source.textContent = sourceKey;
          const statusValue = normalizeEmfSourceStatus(sourceHealth[sourceKey]);
          const status = document.createElement("span");
          status.className = `emf-source-status status-${statusValue}`;
          status.textContent = statusValue;
          row.appendChild(metricLabel);
          row.appendChild(valueNode);
          row.appendChild(source);
          row.appendChild(status);
          metrics.appendChild(row);
        });
        calib.appendChild(metrics);
      }
    }
    if (warnings) {
      const gateWarnings = payload.gate_warnings || [];
      warnings.replaceChildren();
      if (gateWarnings.length) {
        const notice = document.createElement("div");
        notice.className = "notice warn";
        gateWarnings.forEach((warning, index) => {
          if (index) notice.appendChild(document.createElement("br"));
          const text = document.createElement("span");
          text.textContent = warning;
          notice.appendChild(text);
        });
        warnings.appendChild(notice);
      }
    }
  },

  /* ── Review Cards ──────────────────────────────────────────────── */

  renderReviewCards(formData, hardwarePayload, scanProfileCatalog = null) {
    const clientCard = document.querySelector("#review-client");
    const focusCard = document.querySelector("#review-focus");
    const profileCard = document.querySelector("#review-profile");
    const hwCard = document.querySelector("#review-hardware");
    const scanScopeCard = document.querySelector("#review-scan-scope");

    const valueOr = (value, fallback = "-") => value || fallback;
    const renderDefinitionCard = (card, title, fields) => {
      if (!card) return;
      card.replaceChildren();
      const heading = document.createElement("h3");
      heading.textContent = title;
      const list = document.createElement("dl");
      fields.forEach(([label, value]) => {
        const row = document.createElement("div");
        const term = document.createElement("dt");
        const definition = document.createElement("dd");
        term.textContent = label;
        definition.textContent = valueOr(value);
        row.appendChild(term);
        row.appendChild(definition);
        list.appendChild(row);
      });
      card.appendChild(heading);
      card.appendChild(list);
    };

    renderDefinitionCard(clientCard, "Klient", [
      ["Name", `${valueOr(formData.last_name)}, ${valueOr(formData.first_name)}`],
      ["Geburtsdatum", formData.birth_date],
      ["Geburtsort", formData.birth_place],
      ["Lokale Verarbeitung", formData.consent_local ? "bestaetigt" : "nicht bestaetigt"],
      ["Wellbeing-Hinweis", formData.consent_safety ? "akzeptiert" : "nicht akzeptiert"],
    ]);
    renderDefinitionCard(focusCard, "Fokus", [
      ["Fokus", formData.focus],
      ["Hauptsymptom", formData.main_symptom],
      ["Level", formData.profile_level],
      ["Top-N", formData.top_n],
    ]);
    renderDefinitionCard(profileCard, "Profil", [
      ["Template", formData.profile_template],
      ["Entropie", formData.entropy_mode],
      ["Bild", valueOr(formData.image_path, "keins")],
      ["Adaptive Limits", formData.adaptive_limits
        ? "aktiv (Phase-2-Detail-Cap; höchstens 5 ownergebundene Top-Profile)"
        : "aus (voller angeforderter Detailumfang; ownergebundene Top-Profile bis Top-N)"],
      ["Lokale KI", formData.local_ai_enabled ? "aktiviert" : "aus"],
      ["Workbench-Modus", window.MorphicWorkbenchState?.workbenchMode || "standard"],
      ["Planetenvektor", formData.planetary_vector_enabled ? (formData.planet_type || "aktiv") : "aus"],
      ["Gruppenentwurf", formData.group_draft_id || "keiner"],
    ]);
    if (hwCard) {
      const componentsRaw = (hardwarePayload && hardwarePayload.components) || {};
      const comps = Array.isArray(componentsRaw) ? componentsRaw : Object.values(componentsRaw);
      hwCard.replaceChildren();
      const heading = document.createElement("h3");
      heading.textContent = "Hardware";
      const list = document.createElement("ul");
      list.className = "compact-list";
      comps.forEach((component) => {
        const item = document.createElement("li");
        const status = document.createElement("strong");
        item.appendChild(document.createTextNode(`${valueOr(component.label)}: `));
        status.textContent = normalizeHardwareStatus(component.status);
        item.appendChild(status);
        list.appendChild(item);
      });
      hwCard.appendChild(heading);
      hwCard.appendChild(list);
    }
    if (scanScopeCard) {
      scanScopeCard.replaceChildren();
      const heading = document.createElement("h3");
      heading.textContent = "Scan-Profil bestätigen";
      scanScopeCard.appendChild(heading);
      const catalogStatus = window.MorphicWorkbenchState?.scanProfileCatalogStatus
        || (scanProfileCatalog ? "ready" : "loading");
      if (catalogStatus === "error") {
        const errorState = document.createElement("p");
        errorState.className = "inline-state bad scan-pool-error";
        errorState.setAttribute?.("role", "status");
        errorState.setAttribute?.("aria-live", "assertive");
        errorState.setAttribute?.("aria-atomic", "true");
        errorState.textContent = window.MorphicWorkbenchState?.scanProfileCatalogError
          || "Scanprofil-Pool konnte nicht geladen werden.";
        scanScopeCard.appendChild(errorState);
        const noEffect = document.createElement("p");
        noEffect.className = "source-integration-notice";
        noEffect.textContent = "Keine Wirkung auf diesen Scan, Profilpool oder Score.";
        const gateNotice = document.createElement("p");
        gateNotice.className = "source-integration-notice";
        gateNotice.textContent = "Externe Scanprofile erst nach validierter Catalog-Freigabe in Gate 14.";
        scanScopeCard.appendChild(noEffect);
        scanScopeCard.appendChild(gateNotice);
        const retryButton = document.createElement("button");
        retryButton.type = "button";
        retryButton.className = "secondary-button scan-pool-retry";
        retryButton.textContent = "Scanprofil-Pool erneut laden";
        retryButton.addEventListener("click", () => {
          const retryAction = window.MorphicWorkbenchActions?.retryScanProfileCatalog;
          if (typeof retryAction !== "function") return;
          let retryPromise;
          try {
            retryPromise = retryAction();
          } catch (_) {
            retryButton.focus?.();
            return;
          }
          scanScopeCard.querySelector?.(".scan-pool-loading")?.focus?.();
          void Promise.resolve(retryPromise).then(
            () => {
              const selector = window.MorphicWorkbenchState?.scanProfileCatalogStatus === "ready"
                ? ".scan-pool-internal-summary"
                : ".scan-pool-retry";
              scanScopeCard.querySelector?.(selector)?.focus?.();
            },
            () => scanScopeCard.querySelector?.(".scan-pool-retry")?.focus?.()
          );
        });
        scanScopeCard.appendChild(retryButton);
      } else if (!scanProfileCatalog || catalogStatus === "loading") {
        const loading = document.createElement("div");
        loading.className = "inline-state neutral scan-pool-loading";
        loading.setAttribute("role", "status");
        loading.setAttribute("aria-live", "polite");
        loading.setAttribute("aria-atomic", "true");
        loading.setAttribute("tabindex", "-1");
        const loadingText = document.createElement("p");
        loadingText.textContent = "Scanprofil-Pool wird geladen.";
        const skeleton = document.createElement("div");
        skeleton.className = "scan-pool-skeleton";
        skeleton.setAttribute("aria-hidden", "true");
        for (let index = 0; index < 3; index += 1) {
          skeleton.appendChild(document.createElement("span"));
        }
        loading.appendChild(loadingText);
        loading.appendChild(skeleton);
        scanScopeCard.appendChild(loading);
      } else {
        const internal = scanProfileCatalog.internal || {profiles: []};
        const external = scanProfileCatalog.external || {active_sources: []};
        const authority = scanProfileCatalog.pool_authority || {};
        const compareLabelAndId = (left, right) => {
          const labelComparison = String(left?.label || "").localeCompare(
            String(right?.label || ""),
            "de",
            {sensitivity: "base"}
          );
          return labelComparison || String(left?.id || "").localeCompare(
            String(right?.id || ""),
            "de",
            {sensitivity: "base"}
          );
        };
        const summary = document.createElement("p");
        summary.className = "scan-scope-summary";
        const selectedTopN = Number(formData.top_n);
        const poolCount = internal.count;
        const topNSupported = Number.isFinite(selectedTopN)
          && Number.isInteger(selectedTopN)
          && selectedTopN >= 1
          && Number.isFinite(poolCount)
          && Number.isInteger(poolCount)
          && poolCount >= 1
          && selectedTopN <= poolCount;
        summary.textContent = topNSupported
          ? `Level ${scanProfileCatalog.profile_level} prüft ${internal.count} interne Screening-Profile; anschließend werden Top-${formData.top_n} vollständig analysiert.`
          : `Level ${scanProfileCatalog.profile_level} prüft ${internal.count} interne Screening-Profile.`;
        scanScopeCard.appendChild(summary);
        if (!topNSupported) {
          const topNWarning = document.createElement("p");
          topNWarning.className = "inline-state bad scan-pool-topn-warning";
          topNWarning.setAttribute("role", "status");
          topNWarning.setAttribute("aria-live", "assertive");
          topNWarning.setAttribute("aria-atomic", "true");
          topNWarning.textContent = "Top-N überschreitet den bestätigten Scanprofil-Pool. Bitte Auswahl anpassen.";
          scanScopeCard.appendChild(topNWarning);
        }

        const badges = document.createElement("div");
        badges.className = "scan-pool-badges";
        const badgeValues = [
          `Poolquelle: ${authority.label}`,
          authority.revision_short ? `Revision: ${authority.revision_short}` : null,
          `Fingerprint: ${authority.fingerprint_short}`,
        ];
        badgeValues.filter(Boolean).forEach((value) => {
          const badge = document.createElement("span");
          badge.className = "scan-pool-badge";
          badge.textContent = value;
          badges.appendChild(badge);
        });
        scanScopeCard.appendChild(badges);

        const internalProfiles = Array.from(internal.profiles || []).sort(compareLabelAndId);
        const internalDetails = document.createElement("details");
        internalDetails.className = "scan-pool-details scan-pool-internal";
        const internalSummary = document.createElement("summary");
        internalSummary.className = "scan-pool-internal-summary";
        internalSummary.textContent = `Interner Profil-Pool: ${internal.count} Profile`;
        internalDetails.appendChild(internalSummary);

        const searchArea = document.createElement("div");
        searchArea.className = "scan-profile-search-area";
        const searchLabel = document.createElement("label");
        searchLabel.className = "scan-profile-search-label";
        searchLabel.setAttribute("for", "scan-profile-search");
        searchLabel.textContent = "Interne Profile durchsuchen";
        const search = document.createElement("input");
        search.id = "scan-profile-search";
        search.type = "search";
        search.className = "scan-profile-search";
        search.setAttribute("aria-label", "Interne Profile durchsuchen");
        search.setAttribute("aria-controls", "scan-profile-list");
        search.setAttribute("autocomplete", "off");
        const counter = document.createElement("p");
        counter.className = "scan-profile-counter";
        counter.setAttribute("role", "status");
        counter.setAttribute("aria-live", "polite");
        counter.setAttribute("aria-atomic", "true");
        counter.textContent = `${internalProfiles.length} von ${internalProfiles.length} Profilen`;
        searchArea.appendChild(searchLabel);
        searchArea.appendChild(search);
        searchArea.appendChild(counter);
        internalDetails.appendChild(searchArea);

        const internalList = document.createElement("ul");
        internalList.id = "scan-profile-list";
        internalList.className = "scan-profile-list compact-list";
        const searchableItems = [];
        internalProfiles.forEach((profile) => {
          const item = document.createElement("li");
          item.className = "scan-profile-item";
          const label = document.createElement("strong");
          label.className = "scan-profile-label";
          label.textContent = String(profile?.label || "Unbenanntes Profil");
          const idRow = document.createElement("span");
          idRow.className = "scan-profile-id-row";
          const idPrefix = document.createElement("span");
          idPrefix.textContent = "ID: ";
          const id = document.createElement("code");
          id.className = "scan-profile-id";
          id.textContent = String(profile?.id || "-");
          idRow.appendChild(idPrefix);
          idRow.appendChild(id);
          item.appendChild(label);
          item.appendChild(idRow);
          internalList.appendChild(item);
          searchableItems.push({
            item,
            searchValue: `${String(profile?.id || "")} ${String(profile?.label || "")}`.toLocaleLowerCase("de"),
          });
        });
        internalDetails.appendChild(internalList);

        const empty = document.createElement("p");
        empty.className = "inline-state neutral scan-profile-empty";
        empty.textContent = "Keine Profile entsprechen der Suche.";
        empty.hidden = true;
        internalDetails.appendChild(empty);
        search.addEventListener("input", () => {
          const query = String(search.value || "").trim().toLocaleLowerCase("de");
          let visibleCount = 0;
          searchableItems.forEach(({item, searchValue}) => {
            item.hidden = Boolean(query) && !searchValue.includes(query);
            if (!item.hidden) visibleCount += 1;
          });
          counter.textContent = `${visibleCount} von ${internalProfiles.length} Profilen`;
          empty.hidden = visibleCount !== 0;
        });
        scanScopeCard.appendChild(internalDetails);

        const externalDetails = document.createElement("details");
        externalDetails.className = "scan-pool-details scan-pool-external";
        const externalHeading = document.createElement("summary");
        externalHeading.textContent = "Externe Registry-Quellen";
        externalDetails.appendChild(externalHeading);
        const externalSummary = document.createElement("p");
        externalSummary.className = "registry-source-summary";
        externalSummary.textContent = `${external.active_source_count} Registry-Quellen sind betriebsbereit; ${external.count} als Scanprofile freigegeben.`;
        const noEffect = document.createElement("p");
        noEffect.className = "source-integration-notice";
        noEffect.textContent = "Keine Wirkung auf diesen Scan, Profilpool oder Score.";
        const gateNotice = document.createElement("p");
        gateNotice.className = "source-integration-notice";
        gateNotice.textContent = "Externe Scanprofile erst nach validierter Catalog-Freigabe in Gate 14.";
        externalDetails.appendChild(externalSummary);
        externalDetails.appendChild(noEffect);
        externalDetails.appendChild(gateNotice);

        const externalList = document.createElement("ul");
        externalList.className = "registry-source-list compact-list";
        Array.from(external.active_sources || []).sort(compareLabelAndId).forEach((source) => {
          const item = document.createElement("li");
          item.className = "registry-source-item";
          const label = document.createElement("strong");
          label.className = "registry-source-label";
          label.textContent = String(source?.label || "Unbenannte Registry-Quelle");
          const idRow = document.createElement("span");
          idRow.className = "registry-source-id-row";
          const idPrefix = document.createElement("span");
          idPrefix.textContent = "ID: ";
          const id = document.createElement("code");
          id.className = "registry-source-id";
          id.textContent = String(source?.id || "-");
          const status = document.createElement("span");
          status.className = "registry-source-status";
          status.textContent = "Registry-Status: betriebsbereit · keine Scanwirkung";
          idRow.appendChild(idPrefix);
          idRow.appendChild(id);
          item.appendChild(label);
          item.appendChild(idRow);
          item.appendChild(status);
          externalList.appendChild(item);
        });
        externalDetails.appendChild(externalList);
        scanScopeCard.appendChild(externalDetails);
      }
    }
  },

  /* ── Results Workspace ─────────────────────────────────────────── */

  renderResults(resultPayload) {
    const grid = document.querySelector("#results-metric-grid");
    if (!grid) return;
    const top = resultPayload.top_profiles || [];
    grid.replaceChildren();
    [
      ["Top-Profile", top.length],
      ["Status", resultPayload.status || "-"],
      ["Job", resultPayload.job_id || "-"],
    ].forEach(([label, value]) => {
      const metric = document.createElement("div");
      metric.className = "metric";
      const metricLabel = document.createElement("span");
      metricLabel.textContent = label;
      const metricValue = document.createElement("strong");
      metricValue.textContent = value;
      metric.appendChild(metricLabel);
      metric.appendChild(metricValue);
      grid.appendChild(metric);
    });
    const profileList = document.querySelector("#results-profile-list");
    if (!profileList) return;
    profileList.replaceChildren();
    if (!top.length) {
      const empty = document.createElement("p");
      empty.className = "inline-state neutral";
      empty.textContent = "Keine Top-Profile im Ergebnis verfuegbar.";
      profileList.appendChild(empty);
      return;
    }
    top.forEach((profile, index) => {
      const card = document.createElement("article");
      card.className = "result-profile-card";
      const heading = document.createElement("h3");
      heading.textContent = `${index + 1}. ${profile.profile || "Profil"}`;
      const score = document.createElement("p");
      score.className = "result-profile-score";
      score.textContent = `Score: ${formatDisplayScore(profile.score)}`;
      const resonances = document.createElement("ul");
      resonances.className = "compact-list";
      (profile.top_resonances || []).forEach((resonance) => {
        const item = document.createElement("li");
        const group = resonance.group ? ` · ${resonance.group}` : "";
        item.textContent = `${resonance.label || "Resonanz"}: ${formatDisplayScore(resonance.score)}${group}`;
        resonances.appendChild(item);
      });
      card.appendChild(heading);
      card.appendChild(score);
      card.appendChild(resonances);
      profileList.appendChild(card);
    });
  },

  /* ── Run Trace ─────────────────────────────────────────────────── */

  renderRunTrace(tracePayload) {
    const pre = document.querySelector("#run-trace-display");
    if (!pre) return;
    pre.textContent = JSON.stringify(roundScoresForDisplay(tracePayload), null, 2);
  },

  /* ── Mode Pill ─────────────────────────────────────────────────── */

  setModePill(mode) {
    const pill = document.querySelector("#mode-pill");
    if (!pill) return;
    pill.textContent = `Modus: ${mode === "expert" ? "Expert" : "Standard"}`;
    pill.className = `pill ${mode === "expert" ? "warn" : "ok"}`;
  },

  /* ── Fokushistorie (Chips, Radi144-Prinzip "Letzte Fokusse") ─────── */

  renderFocusHistoryChips(history, onSelect) {
    const row = document.querySelector("#focus-history-chips");
    if (!row) return;
    row.replaceChildren();
    if (!history || !history.length) {
      const empty = document.createElement("span");
      empty.className = "chip-row-empty";
      empty.textContent = "Noch keine Fokushistorie in diesem Browser.";
      row.appendChild(empty);
      return;
    }
    history.forEach((value) => {
      const chip = document.createElement("button");
      chip.type = "button";
      chip.className = "chip";
      chip.textContent = value;
      chip.addEventListener("click", () => onSelect(value));
      row.appendChild(chip);
    });
  },

  /* ── Choice-Cards (Radio-Karten statt <select>, Radi144-Prinzip 5) ─ */

  renderChoiceCards(containerId, options, currentValue, onSelect) {
    const container = document.querySelector(containerId);
    if (!container) return;
    container.replaceChildren();
    container.setAttribute("role", "radiogroup");
    const containerToken = container.id || String(containerId).replace(/[^A-Za-z0-9_-]+/g, "-");
    const sharedDescriptionIds = String(container.getAttribute("aria-describedby") || "")
      .split(/\s+/)
      .filter(Boolean);
    const hasSelection = options.some((opt) => opt.value === currentValue);
    options.forEach((opt, index) => {
      const isSelected = opt.value === currentValue;
      const card = document.createElement("button");
      card.type = "button";
      card.className = "choice-card" + (isSelected ? " selected" : "");
      card.dataset.value = opt.value;
      card.setAttribute("role", "radio");
      card.setAttribute("aria-checked", isSelected ? "true" : "false");
      card.setAttribute("tabindex", isSelected || (!hasSelection && index === 0) ? "0" : "-1");
      const valueToken = String(opt.value).replace(/[^A-Za-z0-9_-]+/g, "-");
      const titleId = `${containerToken}-${valueToken}-title`;
      const hintId = `${containerToken}-${valueToken}-hint`;
      const title = document.createElement("span");
      title.id = titleId;
      title.className = "choice-card-title";
      title.textContent = opt.label;
      const hint = document.createElement("span");
      hint.id = hintId;
      hint.className = "choice-card-hint";
      hint.textContent = opt.hint || "";
      card.setAttribute("aria-labelledby", titleId);
      card.setAttribute("aria-describedby", [hintId, ...sharedDescriptionIds].join(" "));
      card.appendChild(title);
      card.appendChild(hint);
      card.addEventListener("click", () => {
        const restoreFocus = document.activeElement === card;
        container.querySelectorAll(".choice-card").forEach((c) => {
          c.classList.remove("selected");
          c.setAttribute("aria-checked", "false");
          c.setAttribute("tabindex", "-1");
        });
        card.classList.add("selected");
        card.setAttribute("aria-checked", "true");
        card.setAttribute("tabindex", "0");
        onSelect(opt.value);
        if (restoreFocus) {
          const liveCard = Array.from(container.querySelectorAll(".choice-card"))
            .find((candidate) => candidate.dataset.value === opt.value);
          if (liveCard) liveCard.focus();
        }
      });
      card.addEventListener("keydown", (event) => {
        const cards = Array.from(container.querySelectorAll(".choice-card"));
        let targetIndex;
        switch (event.key) {
          case "ArrowRight":
          case "ArrowDown":
            targetIndex = (cards.indexOf(card) + 1) % cards.length;
            break;
          case "ArrowLeft":
          case "ArrowUp":
            targetIndex = (cards.indexOf(card) - 1 + cards.length) % cards.length;
            break;
          case "Home": targetIndex = 0; break;
          case "End": targetIndex = cards.length - 1; break;
          default: return;
        }
        event.preventDefault();
        const next = cards[targetIndex];
        const nextValue = next.dataset.value;
        next.click();
        const liveNext = Array.from(container.querySelectorAll(".choice-card"))
          .find((candidate) => candidate.dataset.value === nextValue);
        if (liveNext) liveNext.focus();
      });
      container.appendChild(card);
    });
  },

  /* ── Reale Top-N-Scan-Stages (Phase 7: Analyse-Lauf) ───────────── */

  renderSubstepTimeline(completedStageIds, currentStageId, jobStatus) {
    const timeline = document.querySelector("#substep-timeline");
    if (!timeline) return;
    const items = timeline.querySelectorAll(".substep-timeline-item");
    if (!items.length) return;
    const completed = new Set(completedStageIds || []);
    items.forEach((item) => {
      const stageId = item.dataset.stageId;
      item.classList.remove("pending", "active", "completed");
      if (completed.has(stageId)) {
        item.classList.add("completed");
      } else if (jobStatus === "running" && stageId === currentStageId) {
        item.classList.add("active");
      } else {
        item.classList.add("pending");
      }
    });
    const state = document.querySelector("#substep-timeline-state");
    if (state) {
      if (jobStatus === "completed") {
        state.textContent = `${completed.size} / ${items.length} beobachtete Stages abgeschlossen`;
        state.className = "inline-state ok";
      } else if (jobStatus === "running") {
        state.textContent = `${completed.size} / ${items.length} beobachtet`;
        state.className = "inline-state neutral";
      } else {
        state.textContent = "bereit";
        state.className = "inline-state neutral";
      }
    }
  },

  resetSubstepTimeline() {
    const timeline = document.querySelector("#substep-timeline");
    if (!timeline) return;
    timeline.querySelectorAll(".substep-timeline-item").forEach((item) => {
      item.classList.remove("active", "completed");
      item.classList.add("pending");
    });
    const state = document.querySelector("#substep-timeline-state");
    if (state) {
      state.textContent = "bereit";
      state.className = "inline-state neutral";
    }
  },
};

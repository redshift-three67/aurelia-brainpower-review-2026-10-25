// ========== MORPHIC ENGINE V1 - USER WORKFLOW ==========
const API_BASE = "/api";
const TOTAL_STEPS = 10;
let currentStep = 0;
let scanJobId = null;
let scanWs = null;
let scanPollTimer = null;
let harmJobId = null;
let scanInFlight = false;

const STEPS = [
  { num: 1, label: "Start" },
  { num: 2, label: "Klient" },
  { num: 3, label: "Fokus" },
  { num: 4, label: "Config" },
  { num: 5, label: "EMF" },
  { num: 6, label: "Scan" },
  { num: 7, label: "Ergebnisse" },
  { num: 8, label: "Synergy" },
  { num: 9, label: "Harmonie" },
  { num: 10, label: "Export" },
];

const FOCUS_PRESETS = [
  "Bronchien", "Verdauung", "Erschöpfung", "Immunsystem",
  "Stressabbau", "Schlafqualität", "Schmerzlinderung",
  "Entgiftung", "Herz-Kreislauf", "Nervensystem",
  "Hormonhaushalt", "Gelenke & Muskeln",
];

// ========== INIT ==========
document.addEventListener("DOMContentLoaded", () => {
  console.log("[Morphic] DOM ready, initializing...");
  try {
    buildNav();
    renderFocusPresets();
    checkApiStatus();
    updateProgress();
    bindButtons();
    console.log("[Morphic] Init complete");
  } catch(e) {
    console.error("[Morphic] Init error:", e);
  }
});

function bindButtons() {
  const emfToggle = document.getElementById("emfToggle");
  if (emfToggle) emfToggle.addEventListener("change", loadEMFStatus);
  const scanBtn = document.getElementById("scanStartBtn");
  if (scanBtn) scanBtn.addEventListener("click", startScan);
  const harmBtn = document.getElementById("harmBtn");
  if (harmBtn) harmBtn.addEventListener("click", startHarmonization);
}

function buildNav() {
  const nav = document.getElementById("navInner");
  if (!nav) { console.error("[Morphic] navInner not found"); return; }
  nav.innerHTML = STEPS.map((s, i) =>
    '<div class="ns' + (i === 0 ? " active" : "") + '" onclick="jumpTo(' + i + ')">' +
    '<div class="nn">' + s.num + '</div><span>' + s.label + '</span></div>' +
    (i < STEPS.length - 1 ? '<div class="nc"></div>' : '')
  ).join("");
}

function renderFocusPresets() {
  const grid = document.getElementById("focusPresets");
  if (!grid) return;
  grid.innerHTML = FOCUS_PRESETS.map(f =>
    '<button class="preset-btn" onclick="document.getElementById(\'focusInput\').value=\'' + f + '\'">' + f + '</button>'
  ).join("");
}

// ========== API STATUS ==========
async function checkApiStatus() {
  const status = document.getElementById("apiStatus");
  const sysInfo = document.getElementById("sysInfo");
  try {
    console.log("[Morphic] Checking API status...");
    const r = await fetch(API_BASE + "/status");
    if (!r.ok) throw new Error("HTTP " + r.status);
    const data = await r.json();
    status.classList.add("ok");
    status.innerHTML = '<span class="pulse"></span> Verbunden · Morphic Engine V' + (data.version || "1.0");
    console.log("[Morphic] API connected:", data);
    let healthHtml = "";
    try {
      const hr = await fetch(API_BASE + "/health");
      const health = await hr.json();
      healthHtml = '<div class="mr"><span class="ml">Status</span><span class="mv" style="color:var(--green)">' + (health.status || "ok") + '</span></div>';
    } catch(e) { healthHtml = '<div class="mr"><span class="ml">Health</span><span class="mv">n.v.</span></div>'; }
    if (sysInfo) sysInfo.innerHTML = healthHtml;
  } catch(e) {
    console.error("[Morphic] API error:", e);
    status.classList.add("err");
    status.innerHTML = '<span class="pulse"></span> Nicht verbunden - Server starten: python web_server.py';
  }
}

// ========== NAVIGATION ==========
function navigate(dir) {
  const next = currentStep + dir;
  if (next < 0 || next >= TOTAL_STEPS) return;
  if (dir > 0 && !validateStep(currentStep)) return;
  showStep(next);
}

function jumpTo(step) {
  if (step <= currentStep || canJumpTo(step)) showStep(step);
}

function canJumpTo(step) {
  return scanJobId !== null || step <= 4;
}

function showStep(step) {
  document.querySelectorAll(".sp").forEach((s, i) => {
    s.classList.toggle("active", i === step);
  });
  document.querySelectorAll(".ns").forEach((n, i) => {
    n.classList.toggle("active", i === step);
    n.classList.toggle("done", i < step);
  });
  document.querySelectorAll(".nc").forEach((n, i) => n.classList.toggle("done", i < step));
  currentStep = step;
  updateProgress();
  console.log("[Morphic] Step " + (step+1) + "/" + TOTAL_STEPS);
  if (step === 4) { console.log("[Morphic] Auto-triggering EMF..."); loadHardwareStatus(); loadEMFStatus(); }
  if (step === 6 && scanJobId) loadResults();
  if (step === 7) loadSynergy();
  if (step === 9) loadReports();
}

function updateProgress() {
  const pct = ((currentStep + 1) / TOTAL_STEPS) * 100;
  const fill = document.getElementById("opFill");
  const pctText = document.getElementById("opPct");
  if (fill) fill.style.width = pct + "%";
  if (pctText) pctText.textContent = (currentStep + 1) + "/" + TOTAL_STEPS;
  const prev = document.getElementById("btnPrev");
  const next = document.getElementById("btnNext");
  if (prev) prev.disabled = currentStep === 0;
  if (next) next.disabled = currentStep === TOTAL_STEPS - 1;
}

function validateStep(step) {
  if (step === 1) {
    const fn = document.getElementById("firstName").value.trim();
    const ln = document.getElementById("lastName").value.trim();
    const bd = document.getElementById("birthDate").value.trim();
    const bp = document.getElementById("birthPlace").value.trim();
    if (!fn || !ln || !bd || !bp) {
      const err = document.getElementById("step2Error");
      if (err) err.textContent = "Alle Pflichtfelder sind erforderlich.";
      return false;
    }
    const err = document.getElementById("step2Error");
    if (err) err.textContent = "";
  }
  return true;
}

// ========== HARDWARE-STATUS (Transparenz ueber aktive Komponenten) ==========
async function loadHardwareStatus() {
  const el = document.getElementById("hwStatusContent");
  if (!el) return;
  try {
    const r = await fetch(API_BASE + "/hardware/status");
    if (!r.ok) throw new Error("HTTP " + r.status);
    const d = await r.json();
    if (d.error) throw new Error(d.error);

    const gpuActive = d.gpu && d.gpu.has_gpu;
    const sensorCount = (d.sensors && d.sensors.count) || 0;
    const badge = (active, label) =>
      '<span class="profile-tag" style="font-size:.75rem;padding:4px 10px;margin:2px;background:' +
      (active ? 'rgba(34,197,94,.15);color:var(--green)' : 'rgba(148,163,184,.15);color:var(--tm)') +
      '">' + (active ? '&#9679; ' : '&#9675; ') + label + '</span>';

    el.innerHTML =
      '<div style="margin-bottom:10px">' +
        badge(true, "CPU-Timing-Jitter") +
        badge(true, "OS-Zufallszahlen (os.urandom)") +
        badge(gpuActive, "GPU-Beschleunigung (CuPy)") +
        badge(sensorCount > 0, "Externe Sensor-Hardware (" + sensorCount + ")") +
      '</div>' +
      '<p class="dim small">' + (d.emf_measurement_source || "") + '</p>';
  } catch (e) {
    console.error("[Morphic] Hardware-Status Fehler:", e);
    el.innerHTML = '<p class="dim">Hardware-Status nicht verf&uuml;gbar.</p>';
  }
}

// ========== EMF (nach Radi144-Pattern) ==========
async function loadEMFStatus() {
  const content = document.getElementById("emfContent");
  const counterCard = document.getElementById("emfCounterCard");
  const counterContent = document.getElementById("emfCounterContent");
  if (!content) { console.error("[Morphic] emfContent not found"); return; }

  const emfToggle = document.getElementById("emfToggle");
  const emfEnabled = emfToggle ? emfToggle.checked : true;
  if (!emfEnabled) {
    content.innerHTML = '<p style="color:var(--td);text-align:center;padding:20px 0"><span style="font-size:2rem;display:block;margin-bottom:10px">\uD83D\uDD07</span>EMF-Kompensation ist deaktiviert.<br><small class="dim">Aktivieren Sie den Schalter oben.</small></p>';
    if (counterCard) counterCard.style.display = "none";
    return;
  }

  content.innerHTML = '<p class="dim">Messe elektromagnetisches Umfeld...</p>';

  try {
    console.log("[Morphic] EMF: enable + profile");
    // EMF aktivieren (wie Radi144)
    await fetch(API_BASE + "/emf/enable", { method: "POST" }).catch(() => {});
    // Kurz warten damit Sensoren messen
    await new Promise(r => setTimeout(r, 1500));
    // Profil abrufen
    const res = await fetch(API_BASE + "/emf/profile");
    if (!res.ok) throw new Error("HTTP " + res.status);
    const data = await res.json();
    console.log("[Morphic] EMF data:", data);

    const emfIdx = data.emf_index ?? 0;
    const entropy = data.entropy_score ?? 0;
    const jitter = data.timing_jitter_ms ?? 0;
    const sysLoad = data.system_load ?? 0;
    const rec = data.recommendation || "--";

    let quality = "Niedrig";
    let qualColor = "var(--green)";
    if (emfIdx > 0.6) { quality = "Hoch"; qualColor = "var(--red)"; }
    else if (emfIdx > 0.3) { quality = "Mittel"; qualColor = "var(--amber)"; }

    content.innerHTML =
      '<div class="result-score-row">' +
        '<div class="rs-item"><div class="rs-val" style="color:' + qualColor + '">' + emfIdx.toFixed(4) + '</div><div class="rs-label">EMF-Index</div></div>' +
        '<div class="rs-item"><div class="rs-val">' + entropy.toFixed(4) + '</div><div class="rs-label">Entropy</div></div>' +
        '<div class="rs-item"><div class="rs-val">' + jitter.toFixed(2) + ' ms</div><div class="rs-label">Jitter</div></div>' +
        '<div class="rs-item"><div class="rs-val">' + sysLoad.toFixed(3) + '</div><div class="rs-label">System Load</div></div>' +
      '</div>' +
      '<div class="mr"><span class="ml">Umfeld-Qualitaet</span><span class="mv" style="color:' + qualColor + '">' + quality + ' (' + (emfIdx * 100).toFixed(1) + '%)</span></div>' +
      '<div class="mr"><span class="ml">Empfehlung</span><span class="mv">' + rec + '</span></div>';

    // Counter-Frequenzen
    const counters = data.counter_frequencies || [];
    if (counters.length > 0 && counterCard && counterContent) {
      counterCard.style.display = "";
      const freqLabels = {174:"Schmerzlinderung",285:"Regeneration",396:"Angstbefreiung",417:"Wandel",528:"DNA-Reparatur",639:"Harmonie",741:"Reinigung",852:"Intuition",963:"Einheit"};
      counterContent.innerHTML = '<div class="preset-grid">' + counters.map(f =>
        '<div class="preset-btn" style="text-align:center;cursor:default">' + f.toFixed(1) + ' Hz<small style="display:block;color:var(--tm);font-size:.68rem">' + (freqLabels[Math.round(f)] || "") + '</small></div>'
      ).join("") + '</div>';
    } else if (counterCard) {
      counterCard.style.display = "none";
    }
  } catch(e) {
    console.error("[Morphic] EMF error:", e);
    content.innerHTML = '<p style="color:var(--red)">EMF-Messung fehlgeschlagen: ' + e.message + '</p><p class="dim small">Stellen Sie sicher, dass der Server laeuft.</p>';
  }
}

// Compatibility alias
const measureEMF = loadEMFStatus;

// ========== SCAN ==========
async function startScan() {
  if (scanInFlight) {
    console.warn("[Morphic] startScan() ignored - already in flight");
    return;
  }
  scanInFlight = true;
  console.log("[Morphic] startScan() called");
  const btn = document.getElementById("scanStartBtn");
  if (btn) { btn.disabled = true; btn.textContent = "Scan läuft..."; }
  const card = document.getElementById("scanProgressCard");
  const spinner = document.getElementById("scanSpinner");
  if (card) card.style.display = "block";
  if (spinner) spinner.style.display = "block";

  const topNEl = document.querySelector("input[name='topN']:checked");
  const levelEl = document.querySelector("input[name='profileLevel']:checked");
  const topN = topNEl ? topNEl.value : "3";
  const profileLevel = levelEl ? levelEl.value : "3";
  const focusEl = document.getElementById("focusInput");
  const focusVal = focusEl ? focusEl.value.trim() : "";
  const focus = focusVal || "Harmonisierung";  // Default falls leer
  const lastName = document.getElementById("lastName").value.trim();
  const firstName = document.getElementById("firstName").value.trim();
  let birthDate = document.getElementById("birthDate").value.trim();
  const birthPlace = document.getElementById("birthPlace").value.trim();

  // Geburtsdatum normalisieren
  if (birthDate.length === 10 && birthDate.includes("-")) {
    const parts = birthDate.split("-");
    birthDate = parts[2] + parts[1] + parts[0];
  }

  const scanPayload = {
    last_name: lastName, first_name: firstName,
    birth_date: birthDate, birth_place: birthPlace,
    focus: focus, top_n: parseInt(topN), profile_level: parseInt(profileLevel),
    entropy_mode: "enhanced", profile_template: "phase1-default",
    adaptive_limits: document.getElementById("optAdaptive").checked,
    main_symptom: (document.getElementById("mainSymptom") || {}).value || "",
    notes: (document.getElementById("notes") || {}).value || "",
    consent_local: true, consent_safety: true,
  };

  const setStatus = (msg) => { const el = document.getElementById("scanStatus"); if (el) el.textContent = msg; };

  // Preview
  try {
    console.log("[Morphic] Scan preview:", scanPayload);
    const previewR = await fetch(API_BASE + "/scan/preview", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(scanPayload),
    });
    if (!previewR.ok) {
      const err = await previewR.json().catch(() => ({}));
      const msg = Array.isArray(err.detail) ? err.detail.map(d => d.msg).join("; ") : (err.detail || "HTTP " + previewR.status);
      throw new Error(msg);
    }
    console.log("[Morphic] Preview OK");
  } catch(e) {
    console.error("[Morphic] Preview error:", e);
    setStatus("Fehler: " + e.message);
    if (spinner) spinner.style.display = "none";
    if (btn) { btn.disabled = false; btn.textContent = "Scan starten"; }
    scanInFlight = false;
    return;
  }

  // Job starten
  try {
    console.log("[Morphic] Scan job start:", scanPayload);
    const r = await fetch(API_BASE + "/scan/jobs", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(scanPayload),
    });
    if (!r.ok) {
      const err = await r.json().catch(() => ({}));
      const msg = Array.isArray(err.detail) ? err.detail.map(d => d.msg).join("; ") : (err.detail || "HTTP " + r.status);
      throw new Error(msg);
    }
    const data = await r.json();
    scanJobId = data.job_id;
    setStatus("Scan gestartet (Job: " + scanJobId + ")");
    console.log("[Morphic] Job started:", scanJobId);

    // Versuche WebSocket, falle auf Polling zurueck
    try {
      connectScanWebSocket(scanJobId);
    } catch(wsErr) {
      console.warn("[Morphic] WebSocket failed, using polling:", wsErr);
      startScanPolling(scanJobId);
    }

  } catch(e) {
    console.error("[Morphic] Job error:", e);
    setStatus("Fehler: " + e.message);
    if (spinner) spinner.style.display = "none";
    if (btn) { btn.disabled = false; btn.textContent = "Scan starten"; }
    scanInFlight = false;
  }
}

function connectScanWebSocket(jobId) {
  // Vorherige Verbindung sauber schliessen, falls noch aktiv
  if (scanWs) {
    try { scanWs.onclose = null; scanWs.onerror = null; scanWs.close(); } catch(e) { /* noop */ }
    scanWs = null;
  }
  const wsUrl = (location.protocol === "https:" ? "wss://" : "ws://") + location.host + API_BASE + "/scan/jobs/" + jobId + "/ws";
  console.log("[Morphic] WebSocket:", wsUrl);
  const logsDiv = document.getElementById("scanLogs");

  try {
    scanWs = new WebSocket(wsUrl);
  } catch(e) {
    console.warn("[Morphic] WS create failed, polling:", e);
    startScanPolling(jobId);
    return;
  }

  const setStatus = (msg) => { const el = document.getElementById("scanStatus"); if (el) el.textContent = msg; };
  const setProgress = (pct) => { const el = document.getElementById("scanProgressFill"); if (el) el.style.width = pct + "%"; };

  scanWs.onopen = () => { console.log("[Morphic] WS connected"); };

  scanWs.onmessage = (e) => {
    try {
      const d = JSON.parse(e.data);
      const pct = d.progress_percent || 0;
      setProgress(pct);
      setStatus((d.current_phase || "Läuft...") + " (" + pct.toFixed(0) + "%)");
      const phaseEl = document.getElementById("scanPhase");
      if (phaseEl) phaseEl.textContent = d.current_substep || "";

      if (d.new_logs && d.new_logs.length > 0 && logsDiv) {
        d.new_logs.forEach(line => {
          const p = document.createElement("div");
          p.textContent = line;
          logsDiv.appendChild(p);
        });
        // Logs auf max 200 Zeilen begrenzen (Browser-Schutz)
        while (logsDiv.children.length > 200) {
          logsDiv.removeChild(logsDiv.firstChild);
        }
        logsDiv.scrollTop = logsDiv.scrollHeight;
      }

      if (d.status === "completed") {
        const spinner = document.getElementById("scanSpinner");
        if (spinner) spinner.style.display = "none";
        setStatus("Scan abgeschlossen!");
        const btn = document.getElementById("scanStartBtn");
        if (btn) { btn.disabled = false; btn.textContent = "Scan abgeschlossen"; }
        scanInFlight = false;
        // Auto-Harmonisierung, falls in Step 4 aktiviert
        const harmToggle = document.getElementById("optHarmonize");
        if (harmToggle && harmToggle.checked) {
          console.log("[Morphic] Auto-Harmonisierung nach Scan aktiviert");
          setTimeout(() => startHarmonization(), 800);
        }
        scanWs.close();
      } else if (d.status === "failed") {
        const spinner = document.getElementById("scanSpinner");
        if (spinner) spinner.style.display = "none";
        setStatus("Scan fehlgeschlagen" + (d.error ? ": " + d.error : ""));
        const btn = document.getElementById("scanStartBtn");
        if (btn) { btn.disabled = false; btn.textContent = "Erneut versuchen"; }
        scanInFlight = false;
        scanWs.close();
      }
    } catch(err) {
      console.error("[Morphic] WS parse error:", err);
    }
  };

  scanWs.onerror = (e) => {
    console.error("[Morphic] WS error, falling back to polling:", e);
    scanWs = null;
    startScanPolling(jobId);
  };

  scanWs.onclose = () => { scanWs = null; };
}

// Polling-Fallback (falls WebSocket nicht funktioniert)
function startScanPolling(jobId) {
  console.log("[Morphic] Polling started for", jobId);
  if (scanPollTimer) clearInterval(scanPollTimer);
  scanPollTimer = setInterval(async () => {
    try {
      const r = await fetch(API_BASE + "/scan/jobs/" + jobId);
      if (!r.ok) return;
      const d = await r.json();
      const pct = d.progress_percent || 0;
      const fill = document.getElementById("scanProgressFill");
      const status = document.getElementById("scanStatus");
      const phase = document.getElementById("scanPhase");
      if (fill) fill.style.width = pct + "%";
      if (status) status.textContent = (d.current_phase || "Läuft...") + " (" + pct.toFixed(0) + "%)";
      if (phase) phase.textContent = d.current_substep || "";

      if (d.status === "completed") {
        clearInterval(scanPollTimer);
        const spinner = document.getElementById("scanSpinner");
        if (spinner) spinner.style.display = "none";
        if (status) status.textContent = "Scan abgeschlossen!";
        const btn = document.getElementById("scanStartBtn");
        if (btn) { btn.disabled = false; btn.textContent = "Scan abgeschlossen"; }
        scanInFlight = false;
        // Auto-Harmonisierung, falls in Step 4 aktiviert
        const harmToggle = document.getElementById("optHarmonize");
        if (harmToggle && harmToggle.checked) {
          console.log("[Morphic] Auto-Harmonisierung nach Scan (polling) aktiviert");
          setTimeout(() => startHarmonization(), 800);
        }
      } else if (d.status === "failed") {
        clearInterval(scanPollTimer);
        const spinner = document.getElementById("scanSpinner");
        if (spinner) spinner.style.display = "none";
        if (status) status.textContent = "Scan fehlgeschlagen" + (d.error ? ": " + d.error : "");
        const btn = document.getElementById("scanStartBtn");
        if (btn) { btn.disabled = false; btn.textContent = "Erneut versuchen"; }
        scanInFlight = false;
      }
    } catch(e) {
      console.error("[Morphic] Polling error:", e);
    }
  }, 3000);
}

// ========== ERGEBNISSE ==========
async function loadResults() {
  if (!scanJobId) return;
  try {
    const r = await fetch(API_BASE + "/scan/jobs/" + scanJobId + "/results");
    if (!r.ok) throw new Error("HTTP " + r.status);
    const data = await r.json();
    const set = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
    set("resCount", data.top_profiles ? data.top_profiles.length : "--");
    set("resFocus", document.getElementById("focusInput") ? document.getElementById("focusInput").value : "--");
    if (data.top_profiles && data.top_profiles.length > 0) {
      set("resTopScore", data.top_profiles[0].score.toFixed(2));
    }

    // Top-Profile anzeigen
    const profileDiv = document.getElementById("profileResults");
    if (profileDiv && data.top_profiles && data.top_profiles.length > 0) {
      profileDiv.innerHTML = data.top_profiles.map((p, i) =>
        '<div class="card" style="margin-bottom:10px">' +
          '<div class="mr"><span class="ml"><strong>#' + (i+1) + ' ' + (p.profile || '--') + '</strong></span>' +
          '<span class="mv" style="color:var(--primary);font-weight:600">Score: ' + (p.score || 0).toFixed(2) + '</span></div>' +
          (p.top_resonances && p.top_resonances.length > 0 ?
            '<div class="dim small" style="margin-top:8px">' + p.top_resonances.slice(0,3).map(r =>
              '<span class="profile-tag" style="font-size:.8rem;padding:4px 10px;margin:2px">' + (r.label || '--') + ' (' + (r.score || 0).toFixed(1) + ')</span>'
            ).join('') + '</div>' : '') +
        '</div>'
      ).join('');
    } else if (profileDiv) {
      profileDiv.innerHTML = '<p class="dim">Keine Top-Profile verfuegbar.</p>';
    }

    // Top-Resonanzen anzeigen
    const resDiv = document.getElementById("resTopResonances");
    if (resDiv && data.top_resonances && data.top_resonances.length > 0) {
      resDiv.innerHTML = '<div class="result-score-row">' + data.top_resonances.slice(0, 8).map(r =>
        '<div class="rs-item"><div class="rs-val" style="color:' + (r.score >= 7 ? 'var(--red)' : r.score >= 5 ? 'var(--amber)' : 'var(--green)') + '">' + (r.score || 0).toFixed(2) + '</div><div class="rs-label">' + (r.label || '--') + '</div></div>'
      ).join('') + '</div>';
    } else if (resDiv) {
      resDiv.innerHTML = '<p class="dim">Keine Resonanzen verfuegbar.</p>';
    }

    // Export-Pfade fuer Step 10 zwischenspeichern und sofort befuellen
    if (data.export_paths) {
      const pathMap = {
        archive: "exportArchive",
        synergy: "exportSynergy",
        remedies: "exportRemedies",
        trends: "exportTrends",
      };
      Object.keys(pathMap).forEach(key => {
        const el = document.getElementById(pathMap[key]);
        if (el) el.textContent = data.export_paths[key] || "--";
      });
    }
  } catch(e) {
    console.error("loadResults:", e);
    const profileDiv = document.getElementById("resProfiles");
    if (profileDiv) profileDiv.innerHTML = '<p class="dim">Ergebnisse nicht verfuegbar.</p>';
  }
}

// ========== SYNERGY ==========
async function loadSynergy() {
  try {
    const sr = await fetch(API_BASE + "/synergy/status");
    const sdata = await sr.json();
    const qm = document.getElementById("quantumMode");
    if (qm) qm.textContent = sdata.mode || "unavailable";

    const focus = (document.getElementById("focusInput") || {}).value || "Harmonisierung";
    const focusVal = focus.trim() || "Harmonisierung";
    const quantumToggle = document.getElementById("optQuantum");
    const useQuantum = quantumToggle ? quantumToggle.checked : true;
    const or = await fetch(API_BASE + "/synergy/optimize", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ focus: focusVal, top_n: 5, combination_size: 3, threshold: 6.0, use_quantum: useQuantum }),
    });
    const odata = await or.json();
    const sc = document.getElementById("synergyCount");
    if (sc) sc.textContent = odata.combination_count || 0;

    const div = document.getElementById("synergyResults");
    if (!div) return;
    if (odata.combinations && odata.combinations.length > 0) {
      div.innerHTML = odata.combinations.map((c, i) =>
        '<div class="card" style="margin-bottom:8px"><div class="mr"><span class="ml">#' + (i+1) + ' Score: ' + c.score.toFixed(2) + '</span><span class="mv">' + c.items.map(it => it.label).join(" + ") + '</span></div><div class="dim small" style="margin-top:4px">' + c.items.map(it => it.group).join(", ") + '</div></div>'
      ).join("");
    } else {
      div.innerHTML = '<p class="dim small">Keine synergetischen Kombinationen gefunden.</p>';
    }
  } catch(e) {
    const div = document.getElementById("synergyResults");
    if (div) div.innerHTML = '<p class="dim">Synergy nicht verfügbar.</p>';
  }
}

// ========== HARMONISIERUNG ==========
async function startHarmonization() {
  const btn = document.getElementById("harmBtn");
  if (btn) { btn.disabled = true; btn.textContent = "Harmonisierung läuft..."; }
  const card = document.getElementById("harmProgressCard");
  if (card) card.style.display = "block";

  const freq = parseFloat((document.getElementById("harmFreq") || {}).value) || 432;
  const duration = parseInt((document.getElementById("harmDuration") || {}).value) || 5;
  const intentionEl = document.querySelector("input[name='intention']:checked");
  const intention = intentionEl ? intentionEl.value : "harmonization";

  try {
    const r = await fetch(API_BASE + "/harmonization/jobs", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ harmonization_mode: intention, target_frequency: freq, duration_minutes: duration, use_cpu: true, use_ram: true, use_gpu: false, use_websocket: false }),
    });
    const data = await r.json();
    harmJobId = data.job_id;
    const hs = document.getElementById("harmStatus");
    if (hs) hs.textContent = data.status || "gestartet";
    pollHarmonization();
  } catch(e) {
    const hs = document.getElementById("harmStatus");
    if (hs) hs.textContent = "Fehler: " + e.message;
    if (btn) { btn.disabled = false; btn.textContent = "Harmonisierung starten"; }
  }
}

async function pollHarmonization() {
  if (!harmJobId) return;
  try {
    const r = await fetch(API_BASE + "/harmonization/jobs/" + harmJobId);
    const data = await r.json();
    const set = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
    set("harmStatus", data.status || "--");
    set("harmProgress", (data.progress_percent || 0).toFixed(0) + "%");
    if (data.status === "completed" || data.status === "failed") {
      const btn = document.getElementById("harmBtn");
      if (btn) { btn.disabled = false; btn.textContent = "Erneut starten"; }
      return;
    }
    setTimeout(pollHarmonization, 3000);
  } catch(e) {
    const hs = document.getElementById("harmStatus");
    if (hs) hs.textContent = "Fehler";
  }
}

// ========== REPORTS ==========
async function loadReports() {
  try {
    const r = await fetch(API_BASE + "/reports");
    const data = await r.json();
    const div = document.getElementById("reportList");
    if (!div) return;
    if (data.items && data.items.length > 0) {
      div.innerHTML = data.items.slice(0, 20).map(rep =>
        '<div class="mr"><span class="ml">' + (rep.title || rep.report_id) + '</span><span class="mv"><a href="' + API_BASE + '/reports/' + rep.report_id + '/file" target="_blank" style="color:var(--primary)">' + (rep.artifact_type || 'download') + '</a></span></div>'
      ).join("");
    } else {
      div.innerHTML = '<p class="dim small">Keine Berichte verfügbar.</p>';
    }
  } catch(e) {
    const div = document.getElementById("reportList");
    if (div) div.innerHTML = '<p class="dim">Berichte nicht verfügbar.</p>';
  }
  // Export-Pfade aus Scan-Ergebnissen befuellen, falls noch nicht geschehen
  const archiveEl = document.getElementById("exportArchive");
  if (scanJobId && archiveEl && (!archiveEl.textContent || archiveEl.textContent === "--")) {
    try {
      const pr = await fetch(API_BASE + "/scan/jobs/" + scanJobId + "/results");
      if (pr.ok) {
        const pdata = await pr.json();
        if (pdata.export_paths) {
          const pathMap = {
            archive: "exportArchive",
            synergy: "exportSynergy",
            remedies: "exportRemedies",
            trends: "exportTrends",
          };
          Object.keys(pathMap).forEach(key => {
            const el = document.getElementById(pathMap[key]);
            if (el) el.textContent = pdata.export_paths[key] || "--";
          });
        }
      }
    } catch(e) {
      console.error("[Morphic] Export-Pfade laden fehlgeschlagen:", e);
    }
  }
}

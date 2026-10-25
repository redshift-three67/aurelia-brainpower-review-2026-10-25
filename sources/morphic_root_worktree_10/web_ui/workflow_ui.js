/* Morphic Engine V1 - Web-UI JavaScript
   10-Step Workflow nach Radi144-Blueprint
*/

const API_BASE = "/api/v1";
const TOTAL_STEPS = 12;
let currentStep = 0;
let emfWs = null;
let emfActive = false;
let audioCtx = null;
let audioOscs = [];
let analysisResult = null;
let currentJobId = null;

const STEP_LABELS = ["System", "Klient", "Signatur", "Fokus", "Optionen", "Analyse", "Profilberichte", "Synergy/Remedy", "Deutung/Trend", "Harmonisierung", "Export", "Vorschau"];
const FOCUS_PRESETS = [
  "Lunge", "Atmungsorgane", "Herz", "Verdauung", "Nerven", "Immunsystem",
  "Gelenke", "Wirbelsaeule", "Haut", "Schlaf", "Stress", "Energiemangel"
];

// --- Init ---
document.addEventListener("DOMContentLoaded", () => {
  buildNav();
  buildFocusPresets();
  checkApiStatus();
  document.getElementById("footerDate").textContent = new Date().toLocaleString("de-DE");
  loadProfiles();
});

// --- Navigation ---
function buildNav() {
  const nav = document.getElementById("stepperNav");
  nav.innerHTML = STEP_LABELS.map((label, i) =>
    `<div class="step-item ${i === currentStep ? "active" : ""}" onclick="navigateTo(${i})">
      <span class="step-num">${i + 1}</span> ${label}
    </div>`
  ).join("");
}

function navigateTo(step) {
  if (step < 0 || step >= TOTAL_STEPS) return;
  document.querySelectorAll(".section").forEach(s => s.classList.remove("active"));
  document.querySelector(`[data-step="${step}"]`).classList.add("active");
  currentStep = step;
  buildNav();
  updateProgress();
  if (step === 8) updateSummary();
  if (step === 11) loadReports();
}

function navigate(dir) {
  const next = currentStep + dir;
  if (next >= 0 && next < TOTAL_STEPS) navigateTo(next);
}

function updateProgress() {
  const pct = ((currentStep + 1) / TOTAL_STEPS) * 100;
  document.getElementById("progFill").style.width = pct + "%";
  document.getElementById("stepLabel").textContent = (currentStep + 1) + "/" + TOTAL_STEPS;
}

// --- API Status ---
async function checkApiStatus() {
  try {
    const r = await fetch(API_BASE + "/status");
    const d = await r.json();
    document.getElementById("apiStatus").className = "status-dot ok";
    document.getElementById("sysStatus").innerHTML =
      `<span style="color:var(--accent);font-weight:600;">Server verbunden</span> (v${d.version})`;
    const grid = document.getElementById("initGrid");
    if (grid) grid.innerHTML = `
      <div class="result-card"><div class="val">OK</div><div class="label">Server-Status</div></div>
      <div class="result-card"><div class="val">8000</div><div class="label">Port</div></div>
      <div class="result-card"><div class="val" id="profileCountInit">lade...</div><div class="label">Profile</div></div>
    `;
    loadProfiles();
  } catch (e) {
    document.getElementById("apiStatus").className = "status-dot err";
    document.getElementById("sysStatus").innerHTML = `<span style="color:#f85149;">Server nicht erreichbar</span>`;
  }
}

async function loadProfiles() {
  try {
    const r = await fetch(API_BASE + "/profiles?level=3");
    const d = await r.json();
    const el = document.getElementById("profileCount");
    if (el) el.textContent = d.count + " (Level 3)";
    const elInit = document.getElementById("profileCountInit");
    if (elInit) elInit.textContent = d.count;
  } catch (e) {}
}

async function loadAmplifiers() {
  try {
    const r = await fetch(API_BASE + "/amplifier/list");
    const d = await r.json();
    const el = document.getElementById("amplifierList");
    if (el && d.amplifiers) {
      el.innerHTML = d.amplifiers.map(a =>
        `<div style="padding:8px;border:1px solid var(--bd);border-radius:6px;margin-bottom:6px;">
         <strong>${a.name}</strong> - ${a.freq} Hz, ${a.element}, Chakra ${a.chakra}</div>`
      ).join("");
    }
  } catch (e) {
    document.getElementById("amplifierList").innerHTML = "<span style='color:#f85149;'>Fehler beim Laden</span>";
  }
}

// --- Fokus Presets ---
function buildFocusPresets() {
  const el = document.getElementById("focusPresets");
  el.innerHTML = FOCUS_PRESETS.map(p =>
    `<div class="preset-btn" onclick="addFocus('${p}')">${p}</div>`
  ).join("");
}

function addFocus(preset) {
  const el = document.getElementById("focus");
  const current = el.value.trim();
  el.value = current ? current + "; " + preset : preset;
}

// --- EMF Monitor ---
function toggleEmf() {
  if (emfActive) {
    if (emfWs) emfWs.close();
    emfActive = false;
    document.getElementById("emfBtn").textContent = "EMF-Monitor starten";
  } else {
    connectEmf();
    emfActive = true;
    document.getElementById("emfBtn").textContent = "EMF-Monitor stoppen";
  }
}

function connectEmf() {
  const wsUrl = (location.protocol === "https:" ? "wss://" : "ws://") + location.host + "/api/v1/emf/ws";
  emfWs = new WebSocket(wsUrl);
  emfWs.onmessage = (e) => {
    const d = JSON.parse(e.data);
    if (d.emf_index !== undefined) {
      document.getElementById("emfIdx").textContent = d.emf_index.toFixed(3);
      document.getElementById("emfBar").style.width = (d.emf_index * 100) + "%";
      document.getElementById("emfEnt").textContent = d.entropy_score.toFixed(3);
      document.getElementById("emfJit").textContent = d.timing_jitter_ms.toFixed(2);
      document.getElementById("emfLoad").textContent = d.system_load.toFixed(3);
      document.getElementById("emfRec").textContent = d.recommendation;
      document.getElementById("emfFreq").innerHTML = (d.counter_frequencies || []).map(f => f.toFixed(1) + " Hz").join(", ");
    }
  };
  emfWs.onclose = () => { if (emfActive) setTimeout(connectEmf, 3000); };
  emfWs.onerror = () => { if (emfWs) emfWs.close(); };
}

// --- Zusammenfassung ---
function updateSummary() {
  const name = document.getElementById("firstName").value + " " + document.getElementById("lastName").value;
  const bd = document.getElementById("birthDate").value;
  const bp = document.getElementById("birthPlace").value;
  const focus = document.getElementById("focus").value || "-";
  const level = document.getElementById("profileLevel").value;
  const topN = document.getElementById("topN").value;
  const intention = document.getElementById("intention").value;

  document.getElementById("summaryContent").innerHTML = `
    <strong>Klient:</strong> ${name}<br>
    <strong>Geburt:</strong> ${bd}, ${bp}<br>
    <strong>Fokus:</strong> ${focus}<br>
    <strong>Level:</strong> ${level} | <strong>Top-N:</strong> ${topN}<br>
    <strong>Intention:</strong> ${intention}<br>
    <strong>Harmonisierung:</strong> ${document.getElementById("harmonize").checked ? "ja" : "nein"}
  `;
}

// --- Analyse starten ---
async function startAnalysis() {
  const name = document.getElementById("lastName").value.trim();
  const first_name = document.getElementById("firstName").value.trim();

  if (!name || !first_name) {
    alert("Bitte Name und Vorname eingeben.");
    navigateTo(1);
    return;
  }

  const btn = document.getElementById("btnStart");
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span> Analysiere...';
  document.getElementById("analysisStatus").innerHTML = "Produktiver Multiplex-Workflow wird gestartet...";
  document.getElementById("analysisProgFill").style.width = "0%";
  document.getElementById("analysisLog").textContent = "";
  document.getElementById("phaseHistory").innerHTML = "";

  const payload = {
    name,
    first_name,
    birth_date: document.getElementById("birthDate").value.trim(),
    birth_place: document.getElementById("birthPlace").value.trim(),
    focus: document.getElementById("focus").value.trim(),
    intention: document.getElementById("intention").value,
    profile_level: parseInt(document.getElementById("profileLevel").value),
    top_n: parseInt(document.getElementById("topN").value),
    image_path: document.getElementById("imagePath").value.trim(),
    planet_type: document.getElementById("planetType").value.trim(),
    p_emotion: parseFloat(document.getElementById("pEmotion").value),
    p_physisch: parseFloat(document.getElementById("pPhysisch").value),
    p_mental: parseFloat(document.getElementById("pMental").value),
    p_astral: parseFloat(document.getElementById("pAstral").value),
    harmonize: document.getElementById("harmonize").checked,
    harm_duration: 1,
  };

  try {
    const r = await fetch(API_BASE + "/jobs/start", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const d = await r.json();

    if (d.error) {
      document.getElementById("analysisStatus").innerHTML = `<span style="color:#f85149;">Fehler: ${d.error}</span>`;
      btn.disabled = false;
      btn.textContent = "Erneut versuchen";
      return;
    }

    currentJobId = d.job_id;
    await pollAnalysisJob(d.job_id, btn);
  } catch (e) {
    document.getElementById("analysisStatus").innerHTML = `<span style="color:#f85149;">Fehler: ${e.message}</span>`;
    btn.disabled = false;
    btn.textContent = "Erneut versuchen";
  }
}

async function pollAnalysisJob(jobId, btn) {
  for (let i = 0; i < 600; i++) {
    try {
      const r = await fetch(API_BASE + "/jobs/" + jobId);
      const d = await r.json();
      if (d.error) {
        document.getElementById("analysisStatus").innerHTML = `<span style="color:#f85149;">Fehler: ${d.error}</span>`;
        break;
      }

      document.getElementById("analysisProgFill").style.width = (d.progress || 0) + "%";
      document.getElementById("analysisStatus").innerHTML =
        `<span style="color:var(--accent);font-weight:600;">${d.step_label || 'Laufend'}</span> - ${d.progress || 0}%`;
      const logs = (d.logs || []).slice(-20).join("\n");
      document.getElementById("analysisLog").textContent = logs;
      const phases = d.phase_history || [];
      document.getElementById("phaseHistory").innerHTML = phases.length
        ? phases.map(p => `<div><strong>Step ${p.step}</strong> - ${p.label}</div>`).join("")
        : "<div>Noch keine Phasen erkannt.</div>";

      if (d.status === "completed") {
        analysisResult = d.result || {};
        document.getElementById("analysisStatus").innerHTML =
          `<span style="color:var(--accent);font-weight:600;">Abgeschlossen!</span> CLI-Workflow erfolgreich beendet.`;
        renderResults({
          status: "completed",
          steps_completed: Array.from({length:12}, (_,k) => k + 1),
          export_paths: {},
          latest_session: d.result?.latest_session || "",
          focus: d.result?.focus || "",
          top_n: d.result?.top_n || 0,
          profile_level: d.result?.profile_level || 0,
        });
        navigateTo(9);
        loadReports();
        btn.disabled = false;
        btn.textContent = "12-Step Workflow starten";
        return;
      }

      if (d.status === "failed") {
        document.getElementById("analysisStatus").innerHTML = `<span style="color:#f85149;">Fehlgeschlagen: ${d.error || 'Unbekannter Fehler'}</span>`;
        btn.disabled = false;
        btn.textContent = "Erneut versuchen";
        return;
      }
    } catch (e) {
      document.getElementById("analysisStatus").innerHTML = `<span style="color:#f85149;">Polling-Fehler: ${e.message}</span>`;
      btn.disabled = false;
      btn.textContent = "Erneut versuchen";
      return;
    }
    await new Promise(r => setTimeout(r, 1500));
  }
  btn.disabled = false;
  btn.textContent = "12-Step Workflow starten";
}

// --- Ergebnisse rendern ---
function renderResults(d) {
  const grid = document.getElementById("resultGrid");
  grid.innerHTML = `
    <div class="result-card"><div class="val">${d.profile_level || "-"}</div><div class="label">Profil-Level</div></div>
    <div class="result-card"><div class="val">${d.top_n || "-"}</div><div class="label">Top-N</div></div>
    <div class="result-card"><div class="val">${d.steps_completed?.length || 0}/12</div><div class="label">Workflow-Steps</div></div>
    <div class="result-card"><div class="val">${d.latest_session ? 'OK' : '-'}</div><div class="label">Archiv-Session</div></div>
    <div class="result-card"><div class="val">${d.focus || '-'}</div><div class="label">Fokus</div></div>
    <div class="result-card"><div class="val">${d.status || '-'}</div><div class="label">Status</div></div>
  `;

  const table = document.getElementById("resultsTable");
  if (table) {
    table.innerHTML = d.latest_session
      ? `<tr><td>1</td><td>Profilberichte wurden erzeugt</td><td>${d.status || 'completed'}</td><td>${d.latest_session.split('\\').pop()}</td><td>${d.focus || '-'}</td></tr>`
      : `<tr><td colspan="5">Noch keine Ergebnisdaten verfuegbar.</td></tr>`;
  }

  const summary = document.getElementById("archiveSummary");
  if (summary) {
    summary.innerHTML = d.latest_session
      ? `<strong>Archivordner:</strong><br>${d.latest_session}<br><br><strong>Fokus:</strong> ${d.focus || '-'}<br><strong>Level:</strong> ${d.profile_level || '-'}<br><strong>Top-N:</strong> ${d.top_n || '-'}`
      : "Noch keine Session vorhanden.";
  }

  // Berichte-Links
  if (d.export_paths && Object.keys(d.export_paths).length) {
    const paths = d.export_paths;
    for (const [key, path] of Object.entries(paths)) {
      const el = document.getElementById("reportArchive");
      if (el) el.innerHTML += `<div>${key.toUpperCase()}: <a href="file:///${path}" target="_blank">${path.split("\\").pop()}</a></div>`;
    }
  }
}

function openReportPreview(fullPath) {
  const frame = document.getElementById("reportPreviewFrame");
  if (!frame) return;
  frame.src = API_BASE + "/report-preview?path=" + encodeURIComponent(fullPath);
}

// --- Audio (Web Audio API) ---
function toggleAudio() {
  if (audioOscs.length > 0) {
    stopAudio();
  } else {
    startAudio();
  }
}

function startAudio() {
  const freq = parseFloat(document.getElementById("harmFreq").value) || 432;
  try {
    audioCtx = audioCtx || new (window.AudioContext || window.webkitAudioContext)();
    const masterGain = audioCtx.createGain();
    masterGain.gain.value = 0.12;
    masterGain.connect(audioCtx.destination);
    masterGain.gain.linearRampToValueAtTime(0.12, audioCtx.currentTime + 0.5);

    const layers = [
      { freq: freq, gain: 1.0, type: "sine" },
      { freq: freq * 1.5, gain: 0.1, type: "sine" },
      { freq: 528.0, gain: 0.05, type: "sine" },
      { freq: freq / 2, gain: 0.15, type: "sine" },
    ];

    audioOscs = layers.map(l => {
      const osc = audioCtx.createOscillator();
      const g = audioCtx.createGain();
      osc.type = l.type;
      osc.frequency.value = Math.max(30, Math.min(l.freq, 4000));
      g.gain.value = l.gain;
      osc.connect(g);
      g.connect(masterGain);
      osc.start();
      return { osc, gain: g };
    });

    document.getElementById("audioBtn").textContent = "Audio stoppen";
    document.getElementById("audioInfo").textContent = freq.toFixed(1) + " Hz (5-Layer)";
  } catch (e) {
    alert("Audio nicht verfuegbar: " + e.message);
  }
}

function stopAudio() {
  audioOscs.forEach(({ osc, gain }) => {
    gain.gain.linearRampToValueAtTime(0, audioCtx.currentTime + 0.3);
    setTimeout(() => osc.stop(), 400);
  });
  audioOscs = [];
  document.getElementById("audioBtn").textContent = "Audio starten";
  document.getElementById("audioInfo").textContent = "432 Hz";
}

// --- Harmonisierung ---
async function startHarmonization() {
  const freq = parseFloat(document.getElementById("harmFreq").value) || 432;
  const duration = parseInt(document.getElementById("harmDuration").value) || 5;

  document.getElementById("harmStatus").innerHTML = "Starte Harmonisierung (Puls 21s / Pause 14s)...";

  try {
    const r = await fetch(API_BASE + "/harmonize/start", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ frequency: freq, duration, intention: "harmonization" }),
    });
    const d = await r.json();
    if (d.error) {
      document.getElementById("harmStatus").innerHTML = `<span style="color:#f85149;">${d.error}</span>`;
    } else {
      document.getElementById("harmStatus").innerHTML = `Job gestartet (ID: ${d.job_id}). Puls/Pause-Zyklus aktiv.`;
      pollHarmonization(d.job_id);
    }
  } catch (e) {
    document.getElementById("harmStatus").innerHTML = `<span style="color:#f85149;">${e.message}</span>`;
  }
}

async function pollHarmonization(jobId) {
  for (let i = 0; i < 60; i++) {
    try {
      const r = await fetch(API_BASE + "/harmonize/jobs");
      const d = await r.json();
      const job = d.jobs?.find(j => j.job_id === jobId);
      if (job) {
        document.getElementById("harmStatus").innerHTML =
          `Status: ${job.status} | Progress: ${job.progress}%`;
        if (job.status === "completed" || job.status === "stopped") break;
      }
    } catch (e) {}
    await new Promise(r => setTimeout(r, 5000));
  }
}

// --- Berichte laden ---
async function loadReports() {
  const name = (document.getElementById("lastName").value || "Mustermann").trim();
  try {
    const r = await fetch(API_BASE + "/reports/" + name);
    const d = await r.json();
    const targets = { archive: "reportArchive", synergy: "reportSynergy", remedies: "reportRemedies", deutung: "reportDeutung", trends: "reportTrends" };
    for (const [key, elId] of Object.entries(targets)) {
      const el = document.getElementById(elId);
      if (el) {
        el.innerHTML = "";
        const items = (d[key] || []).slice().sort((a, b) => {
          const prio = (name) => name.endsWith('.html') ? 0 : name.endsWith('.json') ? 1 : name.endsWith('.txt') ? 2 : 3;
          return prio(a.name) - prio(b.name);
        });
        el.innerHTML = items.length
          ? items.slice(0, 10).map(i => `<div><a href="#" onclick="openReportPreview(${JSON.stringify("" + (i.full_path || i.path))}); return false;">${i.name}</a> <span style="color:var(--fg2)">(${Math.round(i.size / 1024)} KB)</span></div>`).join("")
          : "<div style='color:var(--fg2);'>Keine Berichte gefunden.</div>";
        if (key === 'archive' && items.length) {
          openReportPreview(items[0].full_path || items[0].path);
        }
      }
    }
  } catch (e) {
    console.error("Reports load error:", e);
  }
}

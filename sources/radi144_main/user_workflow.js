// ========== CONFIG ==========
const API_BASE = "/api/v1";
const TOTAL_STEPS = 10;
let currentStep = 0;
let analysisResult = null;
let analysisResults = [];
let activeResultIndex = 0;
let sequenceAutoAdvance = false;
let sequenceAutoAdvanceTimer = null;
let sequenceAutoAdvanceMs = 9000;
const SEQUENCE_AUTO_ADVANCE_OPTIONS = [3000, 9000, 13000, 21000];

// Harmonizer state
let harmRunning = false;
let harmInterval = null;
let harmTimeout = null;
let harmStartTime = 0;
let harmTotalDuration = 0;
let harmIsBlank = false;
let harmCurrentIdx = 0;
let harmItems = [];
let harmPauseImageLayers = [];
let harmMatrixFrameSize = null;
let audioCtx = null;
let activeOscillators = [];
let uploadedImageBase64 = "";

const STEPS = [
  { num: 1, label: "Start" },
  { num: 2, label: "Klient" },
  { num: 3, label: "Fokus" },
  { num: 4, label: "Config" },
  { num: 5, label: "EMF" },
  { num: 6, label: "Analyse" },
  { num: 7, label: "Matrix" },
  { num: 8, label: "Details" },
  { num: 9, label: "Harmonie" },
  { num: 10, label: "Export" },
];

const AMP_FREQS = {
  rosenquarz: 350, amethyst: 480, bergkristall: 528,
  schwarzer_turmalin: 174, schungit: 196,
  orgonit_pyramide_schungit: 7.83, orgonit_pyramide_bergkristall: 7.83,
  lapislazuli: 448, selenit: 560
};
const HARM_SOLFEGGIO_FREQUENCIES = [528, 429.62, 432, 498.9];

const DEFAULT_DIGIT_COLORS = {
  0: "#FFFFFF",
  1: "#FF0000",
  2: "#FF7F00",
  3: "#FFFF00",
  4: "#00FF00",
  5: "#00FFFF",
  6: "#0000FF",
  7: "#8B00FF",
  8: "#FF00FF",
  9: "#FFD700",
};

const FOCUS_PRESETS = [
  "Harmonische Regulation Lunge",
  "Chakra-Ausgleich",
  "Stressabbau & Entspannung",
  "Immunsystem stärken",
  "Energetische Reinigung",
  "Schlafqualität verbessern",
  "Schmerzlinderung",
  "Emotionale Balance",
  "Meridian-Harmonisierung",
  "Herz-Kohärenz",
  "Konzentration & Klarheit",
  "Entgiftung & Detox",
];

const VECTOR_MODE_LABELS = {
  client: "Klient",
  group: "Gruppe",
  geo: "Geo",
  image: "Bild",
};

const IMAGE_BASE64_MAX_BYTES = 4 * 1024 * 1024;
let dbOperationController = null;
let dbProgressTimer = null;

// ========== NAV ==========
function buildNav() {
  const nav = document.getElementById("navInner");
  nav.innerHTML = "";
  STEPS.forEach((s, i) => {
    if (i > 0) {
      const c = document.createElement("div");
      c.className = "nc" + (i <= currentStep ? " done" : "");
      nav.appendChild(c);
    }
    const el = document.createElement("div");
    el.className = "ns" + (i === currentStep ? " active" : "") + (i < currentStep ? " done" : "");
    el.innerHTML = `<div class="nn">${i < currentStep ? "✓" : s.num}</div><span>${s.label}</span>`;
    el.onclick = () => {
      if (i <= currentStep || i < currentStep) goToStep(i);
    };
    nav.appendChild(el);
  });
}

function updateProgress() {
  const pct = ((currentStep + 1) / TOTAL_STEPS * 100).toFixed(1);
  document.getElementById("opFill").style.width = pct + "%";
  document.getElementById("opPct").textContent = `${currentStep + 1}/${TOTAL_STEPS}`;
  document.getElementById("btnPrev").disabled = currentStep === 0;
  const btnNext = document.getElementById("btnNext");
  if (currentStep === 5) {
    // Analysis start step - hide next, use the "Analyse starten" button instead
    btnNext.style.display = "none";
  } else if (currentStep >= 9) {
    // Export step - no next
    btnNext.style.display = "none";
  } else {
    btnNext.style.display = "";
    btnNext.disabled = false;
  }
}

function setDbStatus(message, isError = false) {
  const el = document.getElementById("dbStatus");
  if (!el) return;
  el.textContent = message;
  el.style.color = isError ? "var(--red)" : "";
}

function setDbControlsBusy(isBusy) {
  ["btnDbList", "btnDbRank", "btnDbScan"].forEach((id) => {
    const btn = document.getElementById(id);
    if (btn) btn.disabled = !!isBusy;
  });
  const cancelBtn = document.getElementById("btnDbCancel");
  if (cancelBtn) cancelBtn.style.display = isBusy ? "" : "none";
}

function startDbProgress(baseText) {
  let dots = 0;
  if (dbProgressTimer) clearInterval(dbProgressTimer);
  dbProgressTimer = setInterval(() => {
    dots = (dots + 1) % 4;
    setDbStatus(`${baseText}${".".repeat(dots)}`);
  }, 350);
}

function stopDbProgress() {
  if (dbProgressTimer) {
    clearInterval(dbProgressTimer);
    dbProgressTimer = null;
  }
}

function cancelDbOperation() {
  if (dbOperationController) {
    dbOperationController.abort();
    dbOperationController = null;
  }
  stopDbProgress();
  setDbControlsBusy(false);
  setDbStatus("DB-Vorgang abgebrochen.", true);
}

function beginDbOperation(baseText) {
  if (dbOperationController) {
    setDbStatus("Bitte warten: Ein DB-Vorgang läuft bereits.", true);
    return null;
  }
  dbOperationController = new AbortController();
  setDbControlsBusy(true);
  startDbProgress(baseText);
  return dbOperationController.signal;
}

function endDbOperation() {
  stopDbProgress();
  dbOperationController = null;
  setDbControlsBusy(false);
}

async function importGroupJsonFile() {
  const input = document.getElementById("groupJsonFile");
  const file = input?.files?.[0];
  const err = document.getElementById("clientValErr");
  if (!file) {
    if (err) err.textContent = "⚠ Bitte zuerst eine JSON-Datei auswählen.";
    return;
  }

  try {
    const raw = await file.text();
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) throw new Error("JSON muss ein Array sein.");

    const lines = parsed
      .map((member) => {
        const first = (member.first_name || member.firstName || "").toString().trim();
        const last = Array.isArray(member.last_names)
          ? (member.last_names[0] || "").toString().trim()
          : (member.last_name || member.surname || "").toString().trim();
        const birthDate = normalizeBirthDateInput(member.birth_date || member.dob || "");
        const place = (member.birth_place || member.place || "Unbekannt").toString().trim();
        if (!first || !last) return null;
        return `${last};${first};${birthDate};${place || "Unbekannt"}`;
      })
      .filter(Boolean);

    if (!lines.length) throw new Error("Keine verwertbaren Gruppenmitglieder gefunden.");
    document.getElementById("groupMembers").value = lines.join("\n");
    if (err) err.textContent = "";
    alert(`✓ ${lines.length} Gruppenmitglieder importiert.`);
  } catch (e) {
    if (err) err.textContent = `⚠ JSON-Import fehlgeschlagen: ${e.message}`;
  }
}

async function loadDbList(preselectPath = "") {
  const select = document.getElementById("dbPathSelect");
  if (!select) return;
  const signal = beginDbOperation("Lade DB-Liste");
  if (!signal) return;

  try {
    const res = await fetch(API_BASE + "/db/list", { signal });
    if (!res.ok) throw new Error("Status " + res.status);
    const data = await res.json();
    const items = Array.isArray(data.items) ? data.items : [];

    select.innerHTML = '<option value="">Keine Datenbank verwenden</option>';
    items.forEach((item) => {
      const opt = document.createElement("option");
      opt.value = item.relative_path || item.absolute_path || "";
      opt.textContent = `${item.relative_path || item.name} (${item.size_bytes || 0} B)`;
      select.appendChild(opt);
    });

    if (preselectPath) {
      const hit = Array.from(select.options).find((o) => o.value === preselectPath);
      if (hit) select.value = preselectPath;
    }

    setDbStatus(`DB-Liste geladen: ${items.length} Datei(en).`);
  } catch (e) {
    if (e.name === "AbortError") {
      setDbStatus("DB-Liste abgebrochen.", true);
    } else {
      setDbStatus(`DB-Liste fehlgeschlagen: ${e.message}`, true);
    }
  } finally {
    endDbOperation();
  }
}

async function rankDbCandidates() {
  const dbSelect = document.getElementById("dbPathSelect");
  if (!dbSelect) return;

  const signal = beginDbOperation("Berechne Top-DB Ranking");
  if (!signal) return;
  try {
    const req = {
      ...buildAnalysisConfigPayload(),
      ...buildVectorPayload("db ranking", false),
      focus: document.getElementById("focusText").value.trim() || "DB Ranking",
    };

    const res = await fetch(API_BASE + "/db/rank?limit=5", {
      method: "POST",
      signal,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(req),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `HTTP ${res.status}`);
    }

    const data = await res.json();
    const items = Array.isArray(data.items) ? data.items : [];
    if (!items.length) {
      setDbStatus("Kein DB-Ranking verfügbar.");
      return;
    }

    const best = items[0];
    if (best?.relative_path) dbSelect.value = best.relative_path;
    const lines = items.map((it, idx) => `${idx + 1}. ${it.name} (${(it.avg_score || 0).toFixed(4)})`);
    setDbStatus(`Top-DB: ${best.name} | ${lines.join(" | ")}`);
  } catch (e) {
    if (e.name === "AbortError") {
      setDbStatus("DB-Ranking abgebrochen.", true);
    } else {
      setDbStatus(`DB-Ranking fehlgeschlagen: ${e.message}`, true);
    }
  } finally {
    endDbOperation();
  }
}

async function scanDbToFocus() {
  const dbPath = document.getElementById("dbPathSelect")?.value || "";
  if (!dbPath) {
    setDbStatus("Bitte zuerst eine DB auswählen.", true);
    return;
  }

  const topN = Number(document.getElementById("dbTopN")?.value || 21);
  const signal = beginDbOperation(`Scanne DB (Top-${topN})`);
  if (!signal) return;

  try {
    const req = {
      ...buildAnalysisConfigPayload(),
      ...buildVectorPayload("db scan", false),
      focus: document.getElementById("focusText").value.trim() || "DB Scan",
      db_path: dbPath,
    };

    const res = await fetch(API_BASE + `/db/scan?top_n=${topN}`, {
      method: "POST",
      signal,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(req),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `HTTP ${res.status}`);
    }

    const data = await res.json();
    let focusString = data.focus_string || "";
    const prefix = document.getElementById("dbPrefix")?.value.trim() || "";

    if (prefix && focusString) {
      focusString = focusString
        .split(";")
        .map((item) => item.trim())
        .filter(Boolean)
        .map((item) => `${prefix} ${item}`)
        .join("; ");
    }

    if (!focusString) {
      setDbStatus("DB-Scan lieferte keine Einträge.", true);
      return;
    }

    document.getElementById("focusText").value = focusString;
    updateFocusCount();
    setDbStatus(`DB-Scan erfolgreich: ${data.count || 0} Fokus-Einträge übernommen.`);
    goToStep(2);
  } catch (e) {
    if (e.name === "AbortError") {
      setDbStatus("DB-Scan abgebrochen.", true);
    } else {
      setDbStatus(`DB-Scan fehlgeschlagen: ${e.message}`, true);
    }
  } finally {
    endDbOperation();
  }
}

function isBrowserDisplayableImageFile(file) {
  if (!file) return false;
  const type = String(file.type || "").toLowerCase();
  const name = String(file.name || "").toLowerCase();
  return type.startsWith("image/") || /\.(jpe?g|png|gif|bmp|webp|svg|tiff?)$/.test(name);
}

async function onImageFileChange(evt) {
  const file = evt.target.files?.[0];
  const info = document.getElementById("imageFileInfo");

  if (!file) {
    uploadedImageBase64 = "";
    if (info) info.textContent = "Kein Bild ausgewählt.";
    return;
  }

  if (!isBrowserDisplayableImageFile(file)) {
    uploadedImageBase64 = "";
    if (info) info.textContent = "Ungültiger Dateityp. Bitte Bild wählen.";
    return;
  }

  if (file.size > IMAGE_BASE64_MAX_BYTES) {
    uploadedImageBase64 = "";
    if (info) info.textContent = "Bild zu groß für API-Upload (max. 4 MB). Es kann weiterhin lokal als Pausenbild angezeigt werden; für die Analyse bitte Server-Pfad verwenden oder verkleinern.";
    return;
  }

  try {
    const dataUrl = await new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(String(reader.result || ""));
      reader.onerror = () => reject(new Error("Datei konnte nicht gelesen werden."));
      reader.readAsDataURL(file);
    });
    uploadedImageBase64 = dataUrl;
    if (info) info.textContent = `Bild bereit: ${file.name} (${Math.round(file.size / 1024)} KB)`;
  } catch (e) {
    uploadedImageBase64 = "";
    if (info) info.textContent = `Fehler beim Einlesen: ${e.message}`;
  }
}

function goToStep(idx) {
  if (idx < 0 || idx >= TOTAL_STEPS) return;
  document.querySelectorAll(".sp").forEach(p => p.classList.remove("active"));
  currentStep = idx;
  const target = document.querySelector(`.sp[data-step="${idx}"]`);
  if (target) target.classList.add("active");
  buildNav();
  updateProgress();
  // Trigger step-specific actions
  if (idx === 4) loadEMFStatus();
  buildSummary();
  window.scrollTo({ top: 0, behavior: "smooth" });
  const navStep = document.querySelectorAll(".ns")[idx];
  if (navStep) navStep.scrollIntoView({ behavior: "smooth", block: "nearest", inline: "center" });
  syncSequenceAutoAdvance();
}

function navigate(dir) {
  if (dir > 0 && !validateCurrentStep()) return;
  goToStep(currentStep + dir);
}

function getVectorMode() {
  return document.querySelector('input[name="vectorMode"]:checked')?.value || "client";
}

function updateVectorModeUI() {
  const mode = getVectorMode();
  const showClient = mode === "client";
  const showGroup = mode === "group";
  const showGeo = mode === "geo";
  const showImage = mode === "image";

  const clientEl = document.getElementById("clientVectorFields");
  const groupEl = document.getElementById("groupVectorCard");
  const geoEl = document.getElementById("geoVectorCard");
  const imageEl = document.getElementById("imageVectorCard");

  if (clientEl) clientEl.style.display = showClient ? "" : "none";
  if (groupEl) groupEl.style.display = showGroup ? "" : "none";
  if (geoEl) geoEl.style.display = showGeo ? "" : "none";
  if (imageEl) imageEl.style.display = showImage ? "" : "none";

  const err = document.getElementById("clientValErr");
  if (err) err.textContent = "";
}

function normalizeBirthDateInput(value) {
  const token = (value || "").trim();
  if (!token) return "1990-01-01";
  if (/^\d{4}-\d{2}-\d{2}$/.test(token)) return token;
  if (/^\d{8}$/.test(token)) {
    const d = token.slice(0, 2);
    const m = token.slice(2, 4);
    const y = token.slice(4, 8);
    return `${y}-${m}-${d}`;
  }
  return "1990-01-01";
}

function parseGroupMembers(raw) {
  return (raw || "")
    .split(/\r?\n+/)
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => {
      const parts = line.split(";").map((p) => p.trim());
      if (parts.length < 2) return null;
      const lastName = parts[0] || "Mitglied";
      const firstName = parts[1] || "Person";
      const birthDate = normalizeBirthDateInput(parts[2] || "");
      const birthPlace = parts[3] || "Unbekannt";
      return {
        last_names: [lastName],
        first_name: firstName,
        birth_date: birthDate,
        birth_place: birthPlace,
      };
    })
    .filter(Boolean);
}

function buildAnalysisConfigPayload() {
  return {
    matrix_size: parseInt(document.querySelector('input[name="matrixSize"]:checked').value, 10),
    calculation_mode: document.querySelector('input[name="calcMode"]:checked').value,
    focus_weight: document.getElementById("focusWeight").value,
    symmetry: document.querySelector('input[name="symmetry"]:checked').value,
    palette: document.getElementById("palette").value || null,
    use_planetary: document.getElementById("planetaryToggle").checked,
    amplifier: document.getElementById("amplifier").value || null,
    emf_compensate: document.getElementById("emfToggle").checked,
    hrv_sim: document.getElementById("hrvToggle").checked,
    use_quantum: true,
    use_cuda: true,
  };
}

function buildBaseClientData(
  firstNameFallback = "Analyse",
  lastNameFallback = "Client",
  placeFallback = "Unknown",
  preferTypedIdentity = true
) {
  const firstNameInput = document.getElementById("firstName").value.trim();
  const lastNameInput = document.getElementById("lastName").value.trim();
  const birthDateInput = document.getElementById("birthDate").value;
  const birthPlaceInput = document.getElementById("birthPlace").value.trim();

  const firstName = preferTypedIdentity ? (firstNameInput || firstNameFallback) : firstNameFallback;
  const lastName = preferTypedIdentity ? (lastNameInput || lastNameFallback) : lastNameFallback;
  const birthDate = preferTypedIdentity ? (birthDateInput || "1990-01-01") : "1990-01-01";
  const birthPlace = preferTypedIdentity ? (birthPlaceInput || placeFallback) : placeFallback;
  const birthTime = document.getElementById("birthTime").value;

  return {
    first_name: firstName,
    last_names: [lastName],
    birth_date: birthDate,
    birth_place: birthPlace,
    birth_time: birthTime || null,
    planet: preferTypedIdentity ? (document.getElementById("birthPlanet").value.trim() || null) : null,
    email: document.getElementById("email").value.trim() || null,
    main_symptom: document.getElementById("mainSymptom").value.trim() || null,
    notes: document.getElementById("notes").value.trim() || null,
  };
}

function fileStem(filename) {
  const name = (filename || "").split(/[\\/]/).pop() || "";
  return name.replace(/\.[^.]+$/, "") || "Bild";
}

function getActiveVectorLabel(mode = getVectorMode()) {
  if (mode === "client") {
    const fullName = [
      document.getElementById("firstName").value.trim(),
      document.getElementById("lastName").value.trim(),
    ].filter(Boolean).join(" ");
    return fullName || "Klient";
  }

  if (mode === "group") {
    const members = parseGroupMembers(document.getElementById("groupMembers").value);
    return `Gruppe (${members.length} Mitglieder)`;
  }

  if (mode === "geo") {
    const label = document.getElementById("geoLabel").value.trim();
    if (label) return label;
    const lat = document.getElementById("geoLat").value.trim();
    const lon = document.getElementById("geoLon").value.trim();
    return (lat || lon) ? `${lat || "?"}, ${lon || "?"}` : "Geo-Vektor";
  }

  if (mode === "image") {
    const imgFile = document.getElementById("imageFile")?.files?.[0]?.name || "";
    const imgPath = document.getElementById("imagePath").value.trim();
    return imgFile ? fileStem(imgFile) : (imgPath ? fileStem(imgPath) : "Bild-Vektor");
  }

  return "Vektor";
}

function buildVectorPayload(focusValue, includeDb = true) {
  const mode = getVectorMode();
  const payload = { focus: focusValue };

  if (mode === "client") {
    payload.client_data = buildBaseClientData("Analyse", "Client", "Unknown");
  } else if (mode === "group") {
    const members = parseGroupMembers(document.getElementById("groupMembers").value);
    if (!members.length) {
      throw new Error("Keine Gruppenmitglieder erkannt.");
    }
    payload.group_members = members;
  } else if (mode === "geo") {
    const lat = Number(document.getElementById("geoLat").value);
    const lon = Number(document.getElementById("geoLon").value);
    const radiusRaw = document.getElementById("geoRadius").value;
    if (!Number.isFinite(lat) || !Number.isFinite(lon)) {
      throw new Error("Geo-Koordinaten sind ungültig.");
    }
    const radius = radiusRaw ? Number(radiusRaw) : 0;
    if (Number.isNaN(radius) || radius < 0) {
      throw new Error("Geo-Radius ist ungültig.");
    }
    const label = document.getElementById("geoLabel").value.trim() || `Geo ${lat.toFixed(4)},${lon.toFixed(4)}`;
    payload.geo_coords = `${lat},${lon},${radius}`;
    payload.client_data = buildBaseClientData(label, "Resonanz", "Geo", false);
  } else if (mode === "image") {
    const imagePath = document.getElementById("imagePath").value.trim();
    if (!uploadedImageBase64 && !imagePath) {
      throw new Error("Bitte ein Bild hochladen oder einen Server-Pfad angeben.");
    }
    const usePath = !!imagePath;
    const imageLabel = usePath
      ? fileStem(imagePath)
      : fileStem(document.getElementById("imageFile")?.files?.[0]?.name || "Bild");
    payload.client_data = buildBaseClientData(imageLabel, "Bild", "Image", false);
    if (usePath) payload.image_path = imagePath;
    else payload.image_base64 = uploadedImageBase64;
  }

  if (includeDb) {
    const dbPath = document.getElementById("dbPathSelect")?.value || "";
    if (dbPath) payload.db_path = dbPath;
  }

  return payload;
}

// ========== VALIDATION ==========
function validateCurrentStep() {
  if (currentStep === 1) {
    const mode = getVectorMode();
    const err = document.getElementById("clientValErr");

    if (mode === "client") {
      const fn = document.getElementById("firstName").value.trim();
      const ln = document.getElementById("lastName").value.trim();
      const bd = document.getElementById("birthDate").value;
      const bp = document.getElementById("birthPlace").value.trim();
      if (!fn || !ln || !bd || !bp) {
        err.textContent = "⚠ Bitte alle Pflichtfelder ausfüllen (Vorname, Nachname, Geburtsdatum, Geburtsort).";
        return false;
      }
    } else if (mode === "group") {
      const members = parseGroupMembers(document.getElementById("groupMembers").value);
      if (!members.length) {
        err.textContent = "⚠ Bitte mindestens ein Gruppenmitglied im Format Nachname;Vorname;DDMMYYYY;Ort eingeben.";
        return false;
      }
    } else if (mode === "geo") {
      const lat = Number(document.getElementById("geoLat").value);
      const lon = Number(document.getElementById("geoLon").value);
      const radius = document.getElementById("geoRadius").value;
      if (!Number.isFinite(lat) || !Number.isFinite(lon)) {
        err.textContent = "⚠ Bitte gültige Latitude und Longitude eingeben.";
        return false;
      }
      if (radius && Number(radius) < 0) {
        err.textContent = "⚠ Radius darf nicht negativ sein.";
        return false;
      }
    } else if (mode === "image") {
      const imagePath = document.getElementById("imagePath").value.trim();
      if (!uploadedImageBase64 && !imagePath) {
        err.textContent = "⚠ Bitte ein Bild hochladen oder einen Server-Pfad angeben.";
        return false;
      }
    }

    err.textContent = "";
    return true;
  }
  if (currentStep === 2) {
    const focus = document.getElementById("focusText").value.trim();
    const err = document.getElementById("focusValErr");
    if (!focus) {
      err.textContent = "⚠ Bitte einen Fokus-Text eingeben oder aus den Vorschlägen wählen.";
      return false;
    }
    err.textContent = "";
    return true;
  }
  return true;
}

// ========== FOCUS PRESETS ==========
function buildPresets() {
  const grid = document.getElementById("focusPresets");
  FOCUS_PRESETS.forEach(p => {
    const btn = document.createElement("button");
    btn.className = "preset-btn";
    btn.textContent = p;
    btn.onclick = () => {
      document.getElementById("focusText").value = p;
      document.getElementById("focusValErr").textContent = "";
    };
    grid.appendChild(btn);
  });
}

// ========== API CHECK ==========
async function checkAPI() {
  const el = document.getElementById("apiStatus");
  const info = document.getElementById("sysInfo");
  try {
    const res = await fetch(API_BASE + "/emf/status", { signal: AbortSignal.timeout(5000) });
    if (res.ok) {
      const data = await res.json();
      el.className = "api-status ok";
      el.innerHTML = '<span class="pulse"></span> Server verbunden (gleicher Host)';
      const cp = data.current_profile || {};
      info.innerHTML = `<div class="mr"><span class="ml">API</span><span class="mv" style="color:var(--green)">✓ Erreichbar</span></div>
        <div class="mr"><span class="ml">EMF Modul</span><span class="mv">${data.active ? "Aktiv" : "Bereit"}</span></div>
        <div class="mr"><span class="ml">EMF Index</span><span class="mv">${cp.composite_emf_index?.toFixed(4) || "Nicht gemessen"}</span></div>`;
    } else {
      throw new Error("Status " + res.status);
    }
  } catch (e) {
    el.className = "api-status err";
    el.innerHTML = '<span class="pulse"></span> Server nicht erreichbar';
    info.innerHTML = `<div class="mr"><span class="ml">Status</span><span class="mv" style="color:var(--red)">Offline</span></div>
      <p class="dim small" style="margin-top:8px">Starten Sie den Server: <code>python main.py</code></p>`;
  }
}

// ========== EMF STATUS ==========
async function loadEMFStatus() {
  const content = document.getElementById("emfContent");
  const counterCard = document.getElementById("emfCounterCard");
  const counterContent = document.getElementById("emfCounterContent");
  
  const emfEnabled = document.getElementById("emfToggle").checked;
  if (!emfEnabled) {
    content.innerHTML = `<p style="color:var(--td);text-align:center;padding:20px 0">
      <span style="font-size:2rem;display:block;margin-bottom:10px">🔇</span>
      EMF-Kompensation ist deaktiviert.<br>
      <small class="dim">Sie können diese in Schritt 4 aktivieren.</small></p>`;
    counterCard.style.display = "none";
    return;
  }

  content.innerHTML = '<p class="dim">Messe elektromagnetisches Umfeld…</p>';
  
  try {
    // Enable EMF first
    await fetch(API_BASE + "/emf/enable", { method: "POST" });
    // Get profile (needs a moment for sensors to measure)
    await new Promise(r => setTimeout(r, 1500));
    const res = await fetch(API_BASE + "/emf/profile");
    if (!res.ok) throw new Error("Status " + res.status);
    const data = await res.json();
    
    // API returns { profile: {...}, recommendation: {...}, counter_frequencies: [...] }
    const prof = data.profile || data;
    const emfIdx = prof.composite_emf_index ?? 0;
    const entropy = prof.entropy_score ?? 0;
    const jitter = prof.timing_jitter_ms ?? 0;
    const lowNoise = prof.low_noise_window ?? false;
    const rec = data.recommendation || {};
    
    let quality = "Gut";
    let qualColor = "var(--green)";
    if (emfIdx > 0.6) { quality = "Hoch"; qualColor = "var(--red)"; }
    else if (emfIdx > 0.3) { quality = "Mittel"; qualColor = "var(--amber)"; }

    content.innerHTML = `
      <div class="emf-grid">
        <div class="emf-item"><div class="emf-val" style="color:${qualColor}">${emfIdx.toFixed(4)}</div><div class="emf-label">EMF-Index</div></div>
        <div class="emf-item"><div class="emf-val">${entropy.toFixed(4)}</div><div class="emf-label">Entropy Score</div></div>
        <div class="emf-item"><div class="emf-val">${jitter.toFixed(2)} ms</div><div class="emf-label">Timing Jitter</div></div>
        <div class="emf-item"><div class="emf-val" style="color:${lowNoise ? 'var(--green)' : 'var(--amber)'}">${lowNoise ? '✓ Ja' : '✗ Nein'}</div><div class="emf-label">Low-Noise Fenster</div></div>
      </div>
      <div class="mr"><span class="ml">Umfeld-Qualität</span><span class="mv" style="color:${qualColor}">${quality} (${(emfIdx * 100).toFixed(1)}%)</span></div>
      <div class="mr"><span class="ml">Empfehlung</span><span class="mv">${rec.recommendation || "—"}</span></div>
      <div class="mr"><span class="ml">Konfidenz</span><span class="mv">${rec.confidence ? (rec.confidence * 100).toFixed(0) + "%" : "—"}</span></div>
      ${rec.message ? `<p class="dim small" style="margin-top:10px;font-style:italic">"${rec.message}"</p>` : ""}`;

    // Counter frequencies
    const counters = data.counter_frequencies || [];
    if (counters.length > 0) {
      counterCard.style.display = "";
      counterContent.innerHTML = '<div class="sf-row">' + counters.map(c =>
        `<div class="sf-item">${c.frequency_hz} Hz<small>${c.description || c.purpose || ""}</small></div>`
      ).join("") + '</div>';
    }
  } catch (e) {
    content.innerHTML = `<p style="color:var(--red)">⚠ EMF-Messung fehlgeschlagen: ${e.message}</p>
      <p class="dim small">Stellen Sie sicher, dass der Server läuft.</p>`;
  }
}

// ========== SUMMARY ==========
function buildSummary() {
  const summaryEl = document.getElementById("summaryContent");
  const snapshotEl = document.getElementById("vectorSnapshotContent");
  const snapshotCard = document.getElementById("vectorSnapshotCard");
  const showSnapshot = currentStep >= 5;

  if (snapshotCard) {
    snapshotCard.style.display = showSnapshot ? "" : "none";
  }

  if (!summaryEl && !snapshotEl) return;

  const mode = getVectorMode();
  const modeLabel = VECTOR_MODE_LABELS[mode] || "Klient";
  const fn = document.getElementById("firstName").value.trim();
  const ln = document.getElementById("lastName").value.trim();
  const bd = document.getElementById("birthDate").value;
  const bp = document.getElementById("birthPlace").value.trim();
  const bt = document.getElementById("birthTime").value;
  const focus = document.getElementById("focusText").value.trim();
  const ms = document.querySelector('input[name="matrixSize"]:checked').value;
  const cm = document.querySelector('input[name="calcMode"]:checked').value;
  const fw = document.getElementById("focusWeight").value;
  const sym = document.querySelector('input[name="symmetry"]:checked').value;
  const pal = document.getElementById("palette").value || "Standard";
  const planetary = document.getElementById("planetaryToggle").checked;
  const emf = document.getElementById("emfToggle").checked;
  const hrv = document.getElementById("hrvToggle").checked;
  const amp = document.getElementById("amplifier").value;
  const ampLabel = amp ? document.getElementById("amplifier").selectedOptions[0].textContent : "Keiner";
  const planet = document.getElementById("birthPlanet").value.trim();
  const dbPath = document.getElementById("dbPathSelect")?.value || "";

  let vectorDetails = "";
  if (mode === "client") {
    vectorDetails = `
      <div class="mr"><span class="ml">Name</span><span class="mv">${fn} ${ln}</span></div>
      <div class="mr"><span class="ml">Geburtsdatum</span><span class="mv">${formatDate(bd)}</span></div>
      <div class="mr"><span class="ml">Geburtsort</span><span class="mv">${bp || "—"}</span></div>
      ${bt ? `<div class="mr"><span class="ml">Geburtszeit</span><span class="mv">${bt}</span></div>` : ""}
      ${planet ? `<div class="mr"><span class="ml">Geburtsplanet</span><span class="mv">${planet}</span></div>` : ""}`;
  } else if (mode === "group") {
    const members = parseGroupMembers(document.getElementById("groupMembers").value);
    vectorDetails = `<div class="mr"><span class="ml">Gruppen-Mitglieder</span><span class="mv">${members.length}</span></div>`;
  } else if (mode === "geo") {
    const lat = document.getElementById("geoLat").value;
    const lon = document.getElementById("geoLon").value;
    const radius = document.getElementById("geoRadius").value || "0";
    const label = document.getElementById("geoLabel").value.trim();
    vectorDetails = `
      ${label ? `<div class="mr"><span class="ml">Geo-Label</span><span class="mv">${label}</span></div>` : ""}
      <div class="mr"><span class="ml">Koordinaten</span><span class="mv">${lat || "—"}, ${lon || "—"}</span></div>
      <div class="mr"><span class="ml">Radius</span><span class="mv">${radius} m</span></div>`;
  } else if (mode === "image") {
    const imgFile = document.getElementById("imageFile")?.files?.[0]?.name || "";
    const imgPath = document.getElementById("imagePath").value.trim();
    vectorDetails = `<div class="mr"><span class="ml">Bildquelle</span><span class="mv">${imgFile || imgPath || "—"}</span></div>`;
  }

  const summaryHtml = `
    <div class="mr"><span class="ml">Vektor-Modus</span><span class="mv">${modeLabel}</span></div>
    ${vectorDetails}
    <div class="mr"><span class="ml">Fokus</span><span class="mv" style="color:var(--accent)">${focus}</span></div>
    <div class="mr"><span class="ml">Matrix</span><span class="mv">${ms}×${ms}</span></div>
    <div class="mr"><span class="ml">Modus</span><span class="mv">${cm}</span></div>
    <div class="mr"><span class="ml">Gewichtung</span><span class="mv">${fw}</span></div>
    <div class="mr"><span class="ml">Symmetrie</span><span class="mv">${sym}</span></div>
    <div class="mr"><span class="ml">Palette</span><span class="mv">${pal}</span></div>
    <div class="mr"><span class="ml">DB</span><span class="mv">${dbPath || "Keine"}</span></div>
    <div class="mr"><span class="ml">Amplifier</span><span class="mv" style="color:var(--pink)">${ampLabel}</span></div>
    <div class="mr"><span class="ml">Planetarisch</span><span class="mv" style="color:${planetary ? 'var(--green)' : 'var(--td)'}">${planetary ? '✓ Aktiv' : '✗ Aus'}</span></div>
    <div class="mr"><span class="ml">EMF</span><span class="mv" style="color:${emf ? 'var(--green)' : 'var(--td)'}">${emf ? '✓ Aktiv' : '✗ Aus'}</span></div>
    <div class="mr"><span class="ml">HRV-Sim</span><span class="mv" style="color:${hrv ? 'var(--green)' : 'var(--td)'}">${hrv ? '✓ Aktiv' : '✗ Aus'}</span></div>`;

  if (summaryEl) {
    summaryEl.innerHTML = summaryHtml;
  }

  if (snapshotEl && showSnapshot) {
    const vectorLabel = getActiveVectorLabel(mode);
    snapshotEl.innerHTML = `
      <div class="mr"><span class="ml">Vektor</span><span class="mv">${vectorLabel}</span></div>`;
  } else if (snapshotEl) {
    snapshotEl.innerHTML = "";
  }
}

function formatDate(d) {
  if (!d) return "—";
  const parts = d.split("-");
  return `${parts[2]}.${parts[1]}.${parts[0]}`;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function focusShortLabel(value, maxLen = 28) {
  const text = (value || "").trim();
  if (!text) return "Ohne Fokus";
  return text.length > maxLen ? `${text.slice(0, maxLen - 1)}…` : text;
}

function splitFocusEntries(raw) {
  return (raw || "")
    .split(/[;\r\n]+/)
    .map((s) => s.trim())
    .filter(Boolean);
}

function getActiveResult() {
  if (analysisResults.length > 0) {
    if (activeResultIndex < 0 || activeResultIndex >= analysisResults.length) {
      activeResultIndex = 0;
    }
    return analysisResults[activeResultIndex];
  }
  return analysisResult;
}

function ensureColorGrid(matrix, colors) {
  if (
    Array.isArray(colors) &&
    colors.length === matrix.length &&
    colors.every((row, idx) => Array.isArray(row) && row.length === matrix[idx].length)
  ) {
    return colors;
  }
  return matrix.map((row) => row.map((value) => DEFAULT_DIGIT_COLORS[value] || "#FFFFFF"));
}

function setActiveResult(index) {
  if (!analysisResults.length) return;
  if (index < 0 || index >= analysisResults.length) return;
  activeResultIndex = index;
  analysisResult = analysisResults[index];
  renderMatrix();
  renderDetails();
  syncSequenceAutoAdvance();
}

function stepSequence(delta) {
  if (analysisResults.length <= 1) return;
  const len = analysisResults.length;
  const nextIdx = (activeResultIndex + delta + len) % len;
  setActiveResult(nextIdx);
}

function clearSequenceAutoAdvanceTimer() {
  if (sequenceAutoAdvanceTimer) {
    clearInterval(sequenceAutoAdvanceTimer);
    sequenceAutoAdvanceTimer = null;
  }
}

function toggleSequenceAutoAdvance(enabled) {
  sequenceAutoAdvance = !!enabled;
  syncSequenceAutoAdvance();
  if (currentStep === 6) renderMatrix();
}

function toggleSequenceAutoAdvancePlayback() {
  toggleSequenceAutoAdvance(!sequenceAutoAdvance);
}

function setSequenceAutoAdvanceMs(ms) {
  const parsed = Number(ms);
  if (!SEQUENCE_AUTO_ADVANCE_OPTIONS.includes(parsed)) return;
  sequenceAutoAdvanceMs = parsed;
  syncSequenceAutoAdvance();
  if (currentStep === 6) renderMatrix();
}

function syncSequenceAutoAdvance() {
  clearSequenceAutoAdvanceTimer();
  if (!sequenceAutoAdvance) return;
  if (analysisResults.length <= 1) return;
  if (currentStep !== 6) return;
  if (harmRunning) return;

  sequenceAutoAdvanceTimer = setInterval(() => {
    if (!sequenceAutoAdvance || currentStep !== 6 || analysisResults.length <= 1 || harmRunning) {
      clearSequenceAutoAdvanceTimer();
      return;
    }
    stepSequence(1);
  }, sequenceAutoAdvanceMs);
}

// ========== START ANALYSIS ==========
async function startAnalysis() {
  const btn = document.getElementById("btnStart");
  const card = document.getElementById("analysisCard");
  const errEl = document.getElementById("analysisError");
  const statusEl = document.getElementById("analysisStatus");
  const fillEl = document.getElementById("apFill");

  btn.disabled = true;
  btn.innerHTML = "⏳ Läuft…";
  card.style.display = "";
  errEl.style.display = "none";
  fillEl.style.width = "10%";

  const rawFocusInput = document.getElementById("focusText").value.trim();
  const focusEntries = splitFocusEntries(rawFocusInput);
  if (!focusEntries.length) {
    btn.disabled = false;
    btn.innerHTML = "⚡ Analyse starten";
    card.style.display = "none";
    errEl.style.display = "";
    errEl.textContent = "⚠ Bitte mindestens einen Fokus angeben.";
    return;
  }

  const requestConfig = buildAnalysisConfigPayload();
  const vectorMode = getVectorMode();
  const vectorLabel = VECTOR_MODE_LABELS[vectorMode] || "Vector";

  // Progress simulation
  let progress = 10;
  let progressInterval = null;
  if (focusEntries.length === 1) {
    progressInterval = setInterval(() => {
      if (progress < 85) {
        progress += Math.random() * 8;
        fillEl.style.width = progress + "%";
      }
      if (progress < 30) statusEl.textContent = "Generiere Klienten-Signatur…";
      else if (progress < 50) statusEl.textContent = "Fokus-Vektorisierung & Bio-Matching…";
      else if (progress < 70) statusEl.textContent = "Matrix-Suche läuft (CUDA/CPU)…";
      else statusEl.textContent = "Post-Processing & Farbmapping…";
    }, 400);
  }

  try {
    analysisResults = [];
    activeResultIndex = 0;

    for (let i = 0; i < focusEntries.length; i++) {
      const currentFocus = focusEntries[i];
      const request = {
        ...requestConfig,
        ...buildVectorPayload(currentFocus, true),
      };

      statusEl.textContent =
        focusEntries.length > 1
          ? `${vectorLabel}: Fokus ${i + 1}/${focusEntries.length} → ${currentFocus}`
          : statusEl.textContent;

      const res = await fetch(API_BASE + "/analyze-matrix", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(request),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || `HTTP ${res.status} bei Fokus ${i + 1}`);
      }

      const singleResult = await res.json();
      analysisResults.push(singleResult);

      if (focusEntries.length > 1) {
        progress = 10 + ((i + 1) / focusEntries.length) * 85;
        fillEl.style.width = `${Math.min(progress, 95)}%`;
      }
    }

    if (progressInterval) clearInterval(progressInterval);
    fillEl.style.width = "100%";
    statusEl.textContent =
      analysisResults.length > 1
        ? `✓ Sequenz abgeschlossen (${analysisResults.length} Fokusse)!`
        : "✓ Analyse abgeschlossen!";

    analysisResult = analysisResults[0] || null;

    // Save focus to history
    saveFocusToHistory(rawFocusInput);
    renderFocusHistory();

    // Short delay for UX
    setTimeout(() => {
      renderMatrix();
      renderDetails();
      goToStep(6);
    }, 800);

  } catch (e) {
    if (progressInterval) clearInterval(progressInterval);
    fillEl.style.width = "0%";
    card.style.display = "none";
    errEl.style.display = "";
    errEl.textContent = `⚠ Analyse fehlgeschlagen: ${e.message}`;
    btn.disabled = false;
    btn.innerHTML = "⚡ Analyse starten";
  }
}

// ========== RENDER MATRIX ==========
function renderMatrix() {
  const active = getActiveResult();
  if (!active) return;
  const container = document.getElementById("matrixContainer");
  const legendEl = document.getElementById("matrixLegend");
  const scoreEl = document.getElementById("scoreRow");

  const data = active.matrix_data || active.matrix_12x12;
  const colors = ensureColorGrid(data, active.matrix_colors);
  const size = active.matrix_size || 12;
  const score = active.resonance_score;
  const timeMs = active.processing_time_ms;
  const hw = active.hardware_acceleration;
  const activeFocusLabel = escapeHtml(active.focus || `Fokus ${activeResultIndex + 1}`);
  const sequenceChips = analysisResults.map((item, idx) => {
    const full = item.focus || `Fokus ${idx + 1}`;
    const short = escapeHtml(focusShortLabel(full));
    const title = escapeHtml(full);
    const isActive = idx === activeResultIndex ? " active" : "";
    return `<button class="seq-chip${isActive}" onclick="setActiveResult(${idx})" title="${title}">${idx + 1}. ${short}</button>`;
  }).join("");
  const speedControls = SEQUENCE_AUTO_ADVANCE_OPTIONS.map((ms) => {
    const isActive = ms === sequenceAutoAdvanceMs ? " active" : "";
    return `<button class="seq-speed-btn${isActive}" onclick="setSequenceAutoAdvanceMs(${ms})">${ms / 1000}s</button>`;
  }).join("");
  const sequenceControls = analysisResults.length > 1
    ? `<div class="seq-panel">
        <div class="seq-top">
          <button class="btn seq-nav-btn" onclick="stepSequence(-1)">← Vorheriger</button>
          <div class="seq-active">
            <div class="seq-active-kicker">Aktiver Fokus (${activeResultIndex + 1}/${analysisResults.length})</div>
            <div class="seq-active-label">${activeFocusLabel}</div>
          </div>
          <button class="btn seq-nav-btn" onclick="stepSequence(1)">Nächster →</button>
        </div>
        <div class="seq-tools">
          <button class="btn seq-play-btn${sequenceAutoAdvance ? " running" : ""}" onclick="toggleSequenceAutoAdvancePlayback()">
            ${sequenceAutoAdvance ? "⏸ Auto pausieren" : "▶ Auto starten"}
          </button>
          <div class="seq-speed-group">
            <span class="seq-speed-label">Tempo</span>
            ${speedControls}
          </div>
        </div>
        <div class="seq-chip-row">
          ${sequenceChips}
        </div>
      </div>`
    : "";

  // Score row
  scoreEl.innerHTML = `
    ${sequenceControls}
    <div class="rs-item"><div class="rs-val">${(score * 100).toFixed(1)}%</div><div class="rs-label">Resonanz-Score</div></div>
    <div class="rs-item"><div class="rs-val">${timeMs.toFixed(0)}</div><div class="rs-label">ms Rechenzeit</div></div>
    <div class="rs-item"><div class="rs-val">${size}×${size}</div><div class="rs-label">Matrix-Größe</div></div>
    <div class="rs-item" style="min-width:200px"><div class="rs-val" style="font-size:1rem">${hw}</div><div class="rs-label">Hardware</div></div>`;

  // Matrix grid
  const cellSize = size <= 12 ? 42 : size <= 24 ? 28 : 20;
  const grid = document.createElement("div");
  grid.className = "res-matrix";
  grid.style.gridTemplateColumns = `repeat(${size}, ${cellSize}px)`;

  for (let r = 0; r < data.length; r++) {
    for (let c = 0; c < data[r].length; c++) {
      const cell = document.createElement("div");
      cell.className = "res-cell";
      cell.style.width = cellSize + "px";
      cell.style.height = cellSize + "px";
      cell.style.background = colors[r]?.[c] || "#333";
      cell.style.fontSize = size <= 12 ? ".75rem" : size <= 24 ? ".6rem" : ".5rem";
      // Contrast
      const hex = (colors[r]?.[c] || "#333333").replace("#", "");
      const rr = parseInt(hex.substring(0, 2), 16) || 0;
      const gg = parseInt(hex.substring(2, 4), 16) || 0;
      const bb = parseInt(hex.substring(4, 6), 16) || 0;
      const lum = 0.2126 * rr + 0.7152 * gg + 0.0722 * bb;
      cell.style.color = lum > 128 ? "#000" : "#fff";
      cell.textContent = data[r][c];
      cell.title = `[${r},${c}] = ${data[r][c]} → ${colors[r]?.[c] || "?"}`;
      grid.appendChild(cell);
    }
  }
  container.innerHTML = "";
  container.appendChild(grid);

  // Legend: unique colors
  const colorMap = {};
  for (let r = 0; r < data.length; r++) {
    for (let c = 0; c < data[r].length; c++) {
      const v = data[r][c];
      if (!colorMap[v]) colorMap[v] = colors[r]?.[c] || "#333";
    }
  }
  legendEl.innerHTML = Object.keys(colorMap).sort((a, b) => a - b).map(v =>
    `<div class="ml-item"><div class="ml-swatch" style="background:${colorMap[v]}"></div>${v} → ${colorMap[v]}</div>`
  ).join("");
}

// ========== RENDER DETAILS ==========
function renderDetails() {
  const r = getActiveResult();
  if (!r) return;
  const core = document.getElementById("detailCore");
  const tech = document.getElementById("detailTech");
  const emfCard = document.getElementById("emfResultCard");
  const emfEl = document.getElementById("detailEmf");
  const jsonEl = document.getElementById("rawJson");
  const sequenceRow = analysisResults.length > 1
    ? `<div class="mr"><span class="ml">Sequenz</span><span class="mv">Fokus ${activeResultIndex + 1} / ${analysisResults.length}</span></div>`
    : "";

  core.innerHTML = `
    <div class="mr"><span class="ml">Analyse-ID</span><span class="mv" style="font-size:.72rem">${r.analysis_id}</span></div>
    <div class="mr"><span class="ml">Zeitstempel</span><span class="mv">${new Date(r.timestamp).toLocaleString("de-DE")}</span></div>
    ${sequenceRow}
    <div class="mr"><span class="ml">Klient</span><span class="mv">${r.client_name}</span></div>
    <div class="mr"><span class="ml">Fokus</span><span class="mv" style="color:var(--amber)">${r.focus}</span></div>
    <div class="mr"><span class="ml">Resonanz-Score</span><span class="mv" style="color:var(--green)">${(r.resonance_score * 100).toFixed(2)}%</span></div>
    <div class="mr"><span class="ml">Symmetrie</span><span class="mv">${r.symmetry || "none"}</span></div>`;

  tech.innerHTML = `
    <div class="mr"><span class="ml">Matrix-Größe</span><span class="mv">${r.matrix_size}×${r.matrix_size}</span></div>
    <div class="mr"><span class="ml">Rechenzeit</span><span class="mv">${r.processing_time_ms.toFixed(1)} ms</span></div>
    <div class="mr"><span class="ml">Hardware</span><span class="mv">${r.hardware_acceleration}</span></div>
    <div class="mr"><span class="ml">Zellen gesamt</span><span class="mv">${r.matrix_size * r.matrix_size}</span></div>`;

  // EMF
  if (r.emf_compensation && r.emf_compensation.active) {
    emfCard.style.display = "";
    const ec = r.emf_compensation;
    let html = `
      <div class="mr"><span class="ml">Status</span><span class="mv" style="color:var(--green)">✓ Aktiv</span></div>
      <div class="mr"><span class="ml">EMF-Index</span><span class="mv">${ec.emf_index?.toFixed(4) || "—"}</span></div>
      <div class="mr"><span class="ml">Entropy</span><span class="mv">${ec.entropy_score?.toFixed(4) || "—"}</span></div>`;
    if (ec.timing_recommendation) {
      html += `<div class="mr"><span class="ml">Empfehlung</span><span class="mv">${ec.timing_recommendation.recommendation}</span></div>`;
    }
    if (ec.counter_frequencies?.length) {
      html += '<div class="sf-row" style="margin-top:10px">' + ec.counter_frequencies.map(c =>
        `<div class="sf-item">${c.frequency_hz} Hz<small>${c.description || ""}</small></div>`
      ).join("") + '</div>';
    }
    emfEl.innerHTML = html;
  } else {
    emfCard.style.display = "none";
    emfEl.innerHTML = "";
  }

  // Raw JSON
  jsonEl.textContent = JSON.stringify(
    analysisResults.length > 1
      ? { sequence_count: analysisResults.length, active_index: activeResultIndex, active_result: r }
      : r,
    null,
    2
  );
}

// ========== EXPORTS ==========
function exportJSON() {
  const active = getActiveResult();
  if (!active) return;
  const payload = analysisResults.length > 1
    ? {
        mode: "sequential",
        total_focuses: analysisResults.length,
        active_index: activeResultIndex,
        results: analysisResults,
      }
    : active;
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
  downloadBlob(blob, `resonanz_${active.client_name}_${new Date().toISOString().slice(0,10)}.json`);
}

function exportCSV() {
  const active = getActiveResult();
  if (!active) return;
  const data = active.matrix_data || active.matrix_12x12;
  const csv = data.map(row => row.join(",")).join("\n");
  const blob = new Blob([csv], { type: "text/csv" });
  downloadBlob(blob, `matrix_${active.client_name}_${new Date().toISOString().slice(0,10)}.csv`);
}

function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

function copyToClipboard() {
  const active = getActiveResult();
  if (!active) return;
  navigator.clipboard.writeText(JSON.stringify(active, null, 2)).then(() => {
    alert("✓ Ergebnis in Zwischenablage kopiert!");
  }).catch(() => {
    // Fallback
    const ta = document.createElement("textarea");
    ta.value = JSON.stringify(active, null, 2);
    document.body.appendChild(ta);
    ta.select();
    document.execCommand("copy");
    document.body.removeChild(ta);
    alert("✓ Ergebnis in Zwischenablage kopiert!");
  });
}

function resetWorkflow() {
  analysisResult = null;
  analysisResults = [];
  activeResultIndex = 0;
  sequenceAutoAdvance = false;
  sequenceAutoAdvanceMs = 9000;
  uploadedImageBase64 = "";
  clearSequenceAutoAdvanceTimer();
  const vmClient = document.querySelector('input[name="vectorMode"][value="client"]');
  if (vmClient) vmClient.checked = true;
  document.getElementById("firstName").value = "";
  document.getElementById("lastName").value = "";
  document.getElementById("birthDate").value = "";
  document.getElementById("birthPlace").value = "";
  document.getElementById("birthTime").value = "";
  document.getElementById("birthPlanet").value = "";
  document.getElementById("planetaryToggle").checked = false;
  document.getElementById("email").value = "";
  document.getElementById("mainSymptom").value = "";
  document.getElementById("notes").value = "";
  document.getElementById("groupMembers").value = "";
  document.getElementById("groupJsonFile").value = "";
  document.getElementById("geoLabel").value = "";
  document.getElementById("geoLat").value = "";
  document.getElementById("geoLon").value = "";
  document.getElementById("geoRadius").value = "";
  document.getElementById("imageFile").value = "";
  document.getElementById("imagePath").value = "";
  document.getElementById("imageFileInfo").textContent = "Kein Bild ausgewählt.";
  document.getElementById("dbPathSelect").value = "";
  document.getElementById("dbTopN").value = "21";
  document.getElementById("dbPrefix").value = "";
  if (dbOperationController) cancelDbOperation();
  else {
    stopDbProgress();
    setDbControlsBusy(false);
  }
  setDbStatus("Noch keine DB-Abfrage ausgeführt.");
  document.getElementById("focusText").value = "";
  document.getElementById("emfToggle").checked = false;
  document.getElementById("hrvToggle").checked = false;
  document.getElementById("btnStart").disabled = false;
  document.getElementById("btnStart").innerHTML = "⚡ Analyse starten";
  document.getElementById("analysisCard").style.display = "none";
  document.getElementById("analysisError").style.display = "none";
  document.getElementById("btnNext").style.display = "";
  const summaryTplInput = document.getElementById("summaryTplName");
  if (summaryTplInput) summaryTplInput.value = "";
  const harmTplInput = document.getElementById("harmTplName");
  if (harmTplInput) harmTplInput.value = "";
  const exportTplInput = document.getElementById("exportTplName");
  if (exportTplInput) exportTplInput.value = "";
  const startTplSelect = document.getElementById("startTemplateSelect");
  if (startTplSelect) startTplSelect.value = "";
  const startTplBtn = document.getElementById("btnLoadStartTemplate");
  if (startTplBtn) startTplBtn.disabled = true;
  updateVectorModeUI();
  localStorage.removeItem("resonance_session");
  goToStep(0);
}

// ========== SESSION PERSISTENCE ==========

function saveSession() {
  const session = {
    vectorMode: getVectorMode(),
    firstName: document.getElementById("firstName").value,
    lastName: document.getElementById("lastName").value,
    birthDate: document.getElementById("birthDate").value,
    birthPlace: document.getElementById("birthPlace").value,
    birthTime: document.getElementById("birthTime").value,
    birthPlanet: document.getElementById("birthPlanet").value,
    planetaryToggle: document.getElementById("planetaryToggle").checked,
    email: document.getElementById("email").value,
    mainSymptom: document.getElementById("mainSymptom").value,
    notes: document.getElementById("notes").value,
    groupMembers: document.getElementById("groupMembers").value,
    geoLabel: document.getElementById("geoLabel").value,
    geoLat: document.getElementById("geoLat").value,
    geoLon: document.getElementById("geoLon").value,
    geoRadius: document.getElementById("geoRadius").value,
    imagePath: document.getElementById("imagePath").value,
    dbPath: document.getElementById("dbPathSelect").value,
    dbTopN: document.getElementById("dbTopN").value,
    dbPrefix: document.getElementById("dbPrefix").value,
    focusText: document.getElementById("focusText").value,
    matrixSize: document.querySelector('input[name="matrixSize"]:checked')?.value || "12",
    calcMode: document.querySelector('input[name="calcMode"]:checked')?.value || "quantum",
    focusWeight: document.getElementById("focusWeight").value,
    symmetry: document.querySelector('input[name="symmetry"]:checked')?.value || "none",
    palette: document.getElementById("palette").value,
    amplifier: document.getElementById("amplifier").value,
    emfToggle: document.getElementById("emfToggle").checked,
    hrvToggle: document.getElementById("hrvToggle").checked,
    savedAt: new Date().toISOString(),
  };
  localStorage.setItem("resonance_session", JSON.stringify(session));
}

function restoreSession() {
  const raw = localStorage.getItem("resonance_session");
  if (!raw) {
    updateVectorModeUI();
    loadDbList();
    return false;
  }
  try {
    const s = JSON.parse(raw);
    const dbPathPref = s.dbPath || "";
    if (s.vectorMode) {
      const r = document.querySelector(`input[name="vectorMode"][value="${s.vectorMode}"]`);
      if (r) r.checked = true;
    }
    if (s.firstName) document.getElementById("firstName").value = s.firstName;
    if (s.lastName) document.getElementById("lastName").value = s.lastName;
    if (s.birthDate) document.getElementById("birthDate").value = s.birthDate;
    if (s.birthPlace) document.getElementById("birthPlace").value = s.birthPlace;
    if (s.birthTime) document.getElementById("birthTime").value = s.birthTime;
    if (s.birthPlanet) document.getElementById("birthPlanet").value = s.birthPlanet;
    if (Object.prototype.hasOwnProperty.call(s, "planetaryToggle")) {
      document.getElementById("planetaryToggle").checked = !!s.planetaryToggle;
    }
    if (s.email) document.getElementById("email").value = s.email;
    if (s.mainSymptom) document.getElementById("mainSymptom").value = s.mainSymptom;
    if (s.notes) document.getElementById("notes").value = s.notes;
    if (s.groupMembers) document.getElementById("groupMembers").value = s.groupMembers;
    if (s.geoLabel) document.getElementById("geoLabel").value = s.geoLabel;
    if (s.geoLat) document.getElementById("geoLat").value = s.geoLat;
    if (s.geoLon) document.getElementById("geoLon").value = s.geoLon;
    if (s.geoRadius) document.getElementById("geoRadius").value = s.geoRadius;
    if (s.imagePath) document.getElementById("imagePath").value = s.imagePath;
    if (s.dbTopN) document.getElementById("dbTopN").value = s.dbTopN;
    if (s.dbPrefix) document.getElementById("dbPrefix").value = s.dbPrefix;
    if (s.focusText) document.getElementById("focusText").value = s.focusText;
    if (s.matrixSize) {
      const r = document.querySelector(`input[name="matrixSize"][value="${s.matrixSize}"]`);
      if (r) r.checked = true;
    }
    if (s.calcMode) {
      const r = document.querySelector(`input[name="calcMode"][value="${s.calcMode}"]`);
      if (r) r.checked = true;
    }
    if (s.focusWeight) document.getElementById("focusWeight").value = s.focusWeight;
    if (s.symmetry) {
      const r = document.querySelector(`input[name="symmetry"][value="${s.symmetry}"]`);
      if (r) r.checked = true;
    }
    if (s.palette) document.getElementById("palette").value = s.palette;
    if (s.amplifier) document.getElementById("amplifier").value = s.amplifier;
    if (Object.prototype.hasOwnProperty.call(s, "emfToggle")) {
      document.getElementById("emfToggle").checked = !!s.emfToggle;
    }
    if (Object.prototype.hasOwnProperty.call(s, "hrvToggle")) {
      document.getElementById("hrvToggle").checked = !!s.hrvToggle;
    }
    updateVectorModeUI();
    loadDbList(dbPathPref);
    return true;
  } catch (e) {
    console.warn("Session restore failed:", e);
    updateVectorModeUI();
    loadDbList();
    return false;
  }
}

// Auto-save on input changes (debounced)
let saveTimer = null;
document.addEventListener("input", () => {
  clearTimeout(saveTimer);
  saveTimer = setTimeout(() => {
    saveSession();
    buildSummary();
  }, 500);
});
document.addEventListener("change", () => {
  clearTimeout(saveTimer);
  saveTimer = setTimeout(() => {
    saveSession();
    buildSummary();
  }, 300);
});

// ========== PDF EXPORT ==========

function buildPdfExportContext(active) {
  const mode = getVectorMode();
  const modeLabel = VECTOR_MODE_LABELS[mode] || "Klient";
  const paletteEl = document.getElementById("palette");
  const ampEl = document.getElementById("amplifier");
  const imageFile = document.getElementById("imageFile")?.files?.[0]?.name || "";
  const imagePath = document.getElementById("imagePath").value.trim();

  const context = {
    client_name: active?.client_name || [document.getElementById("firstName").value.trim(), document.getElementById("lastName").value.trim()].filter(Boolean).join(" "),
    focus: active?.focus || document.getElementById("focusText").value.trim(),
    vector_mode: mode,
    vector_mode_label: modeLabel,
    calculation_mode: document.querySelector('input[name="calcMode"]:checked')?.value || "quantum",
    focus_weight: document.getElementById("focusWeight").value,
    symmetry: document.querySelector('input[name="symmetry"]:checked')?.value || "none",
    palette: paletteEl?.selectedOptions?.[0]?.textContent || "Standard",
    planetary_enabled: document.getElementById("planetaryToggle").checked,
    emf_enabled: document.getElementById("emfToggle").checked,
    hrv_enabled: document.getElementById("hrvToggle").checked,
    amplifier: ampEl?.selectedOptions?.[0]?.textContent || "Keiner",
    db_path: document.getElementById("dbPathSelect")?.value || "",
  };

  if (mode === "group") {
    context.group_count = parseGroupMembers(document.getElementById("groupMembers").value).length;
  } else if (mode === "geo") {
    context.geo_lat = document.getElementById("geoLat").value || "";
    context.geo_lon = document.getElementById("geoLon").value || "";
    context.geo_radius = document.getElementById("geoRadius").value || "0";
  } else if (mode === "image") {
    context.image_source = imageFile || imagePath || "-";
  }

  return context;
}

async function exportPDF() {
  const active = getActiveResult();
  if (!active) { alert("Keine Ergebnisse vorhanden."); return; }

  const fn = document.getElementById("firstName").value.trim();
  const ln = document.getElementById("lastName").value.trim();
  const fallbackName = `${(fn || "Analyse")}_${(ln || "Client")}_Resonanzmatrix_${new Date().toISOString().slice(0,10)}.pdf`;
  const payload = {
    filename: fallbackName,
    result: active,
    context: buildPdfExportContext(active),
  };

  try {
    const res = await fetch(API_BASE + "/export/pdf", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `HTTP ${res.status}`);
    }

    const blob = await res.blob();
    if (!blob || blob.size === 0) {
      throw new Error("Leere PDF-Antwort vom Server.");
    }

    const contentDisposition = res.headers.get("content-disposition") || "";
    const filenameMatch = contentDisposition.match(/filename="?([^";]+)"?/i);
    const resolvedFilename = filenameMatch?.[1] || fallbackName;
    downloadBlob(blob, resolvedFilename);
    alert("✓ PDF-Bericht gespeichert!");
  } catch (e) {
    alert(`⚠ PDF-Export fehlgeschlagen: ${e.message}`);
  }
}

function exportExcel() {
  const active = getActiveResult();
  if (!active) { alert("Keine Ergebnisse vorhanden."); return; }
  // CSV-based Excel export
  const fn = document.getElementById("firstName").value.trim();
  const ln = document.getElementById("lastName").value.trim();
  const data = active.matrix_data || active.matrix_12x12;
  if (!data) { alert("Keine Matrix-Daten."); return; }

  let csv = `\uFEFF`; // BOM for Excel UTF-8
  csv += `Resonanzmatrix-Bericht\n`;
  csv += `Name;${fn} ${ln}\n`;
  csv += `Fokus;${active.focus || ''}\n`;
  csv += `Score;${(active.resonance_score * 100).toFixed(1)}%\n`;
  csv += `Matrix;${(active.matrix_size || 12)}x${(active.matrix_size || 12)}\n`;
  csv += `Erstellt;${new Date().toLocaleString('de-DE')}\n`;
  csv += `\n`;
  csv += `Matrix-Daten\n`;
  data.forEach(row => {
    csv += row.join(';') + '\n';
  });

  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${fn}_${ln}_Matrix_${new Date().toISOString().slice(0,10)}.csv`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  alert("✓ Matrix als CSV/Excel gespeichert!");
}

// ========== HARMONIZER ==========

function releasePauseImageLayers(layers = harmPauseImageLayers) {
  layers.forEach(layer => {
    if (layer?.url && layer.revoke !== false) {
      try { URL.revokeObjectURL(layer.url); } catch (e) {}
    }
  });
}

function buildPauseImageLayerFromFile(file, idx, sourceLabel = "Pausenbild") {
  if (!isBrowserDisplayableImageFile(file)) return null;
  return {
    url: URL.createObjectURL(file),
    name: file.name || `${sourceLabel} ${idx + 1}`,
    index: idx + 1,
    source: sourceLabel,
    revoke: true
  };
}

function collectPauseImageLayers() {
  releasePauseImageLayers();
  const explicitLayers = ["pauseImageLayer1", "pauseImageLayer2", "pauseImageLayer3"]
    .map((id, idx) => buildPauseImageLayerFromFile(document.getElementById(id)?.files?.[0], idx, "Pausenbild"))
    .filter(Boolean)
    .slice(0, 3);

  if (explicitLayers.length) return explicitLayers;

  // Fallback: Wenn im Bild-Resonanz-Schritt bereits ein JPG/PNG hochgeladen wurde,
  // soll dieses Bild in der Integrationspause sichtbar sein, auch wenn kein separates
  // Pausenbild gewählt wurde. Server-Pfade bleiben bewusst außen vor, weil sie im
  // Browser lokal nicht zuverlässig/sicher darstellbar sind.
  const analysisImageFile = document.getElementById("imageFile")?.files?.[0];
  const analysisImageLayer = buildPauseImageLayerFromFile(analysisImageFile, 0, "Analysebild");
  if (analysisImageLayer) return [analysisImageLayer];

  if (uploadedImageBase64?.startsWith("data:image/")) {
    return [{
      url: uploadedImageBase64,
      name: "Analysebild",
      index: 1,
      source: "Analysebild",
      revoke: false
    }];
  }

  return [];
}

function renderPauseLayerStack(pauseImageLayers = harmPauseImageLayers) {
  const safeLayers = pauseImageLayers.slice(0, 3);
  const frameStyle = harmMatrixFrameSize
    ? ` style="--harm-pause-frame-width:${harmMatrixFrameSize.width}px;--harm-pause-frame-height:${harmMatrixFrameSize.height}px;"`
    : "";
  const layerMarkup = safeLayers.map((layer, idx) => {
    const opacity = idx === 0 ? 0.72 : idx === 1 ? 0.48 : 0.32;
    const scale = 1 + idx * 0.018;
    return `<img class="harm-pause-layer harm-pause-layer-${idx + 1}" src="${layer.url}" alt="${escapeHtml(layer.name)}" style="opacity:${opacity};transform:translate(-50%, -50%) scale(${scale});">`;
  }).join("");

  return `<div class="harm-pause-layer-stack"${frameStyle}>
    ${layerMarkup}
    <div class="harm-pause-layer-overlay">
      <div class="harm-pause-layer-title">PAUSE — Stille & Integration</div>
      <div class="harm-pause-layer-meta">${safeLayers.length ? `${safeLayers.length} Pausenbild-Layer aktiv` : "Integration ohne Pausenbild"}</div>
    </div>
  </div>`;
}

function startHarmonizer() {
  const resultSequence = analysisResults.length ? analysisResults : (analysisResult ? [analysisResult] : []);
  if (!resultSequence.length) { alert("Bitte zuerst eine Analyse durchführen."); return; }

  const preHarmTemplateName = document.getElementById("harmTplName")?.value.trim() || "";
  if (preHarmTemplateName) {
    saveTemplateByName(preHarmTemplateName, { showAlert: false });
    const exportTplInput = document.getElementById("exportTplName");
    if (exportTplInput && !exportTplInput.value.trim()) exportTplInput.value = preHarmTemplateName;
  }

  const pulseSec = parseFloat(document.getElementById("harmPulse").value) || 14;
  const pauseSec = parseFloat(document.getElementById("harmPause").value) || 14;
  const durationFactor = parseFloat(document.getElementById("harmDuration").value) || 1;
  const selectedSolfFreq = parseFloat(document.querySelector('input[name="harmSolf"]:checked').value) || 432;
  const solfFreq = HARM_SOLFEGGIO_FREQUENCIES.includes(selectedSolfFreq) ? selectedSolfFreq : 432;
  const useAudio = document.getElementById("harmAudio").checked;
  const ampName = document.getElementById("amplifier").value;
  const ampFreq = AMP_FREQS[ampName] || 0;

  harmTotalDuration = durationFactor * 21 * 60; // seconds
  harmStartTime = Date.now() / 1000;
  harmCurrentIdx = 0;
  harmIsBlank = false;
  harmPauseImageLayers = collectPauseImageLayers();
  harmRunning = true;
  syncSequenceAutoAdvance();

  // Build transmission items from full sequence (mehrere Fokusse + bis zu 3 Varianten je Fokus)
  harmItems = [];
  resultSequence.forEach((res, seqIdx) => {
    const baseLabel = res.focus || `Fokus ${seqIdx + 1}`;
    const clientFreq = Number(res.client_frequency_hz) || 432;
    const variants = Array.isArray(res.top_10) && res.top_10.length > 0
      ? res.top_10.slice(0, 3)
      : [{ matrix_data: res.matrix_data || res.matrix_12x12 }];

    variants.forEach((variant, variantIdx) => {
      const matrix = variant.matrix_data || variant.matrix_12x12;
      if (!Array.isArray(matrix) || !matrix.length) return;
      const colors = variantIdx === 0
        ? ensureColorGrid(matrix, res.matrix_colors)
        : ensureColorGrid(matrix, null);
      harmItems.push({
        matrix,
        colors,
        label: variants.length > 1 ? `${baseLabel} (Var ${variantIdx + 1})` : baseLabel,
        clientFreq,
        solfFreq,
        ampFreq
      });
    });
  });

  if (!harmItems.length) {
    harmRunning = false;
    releasePauseImageLayers();
    harmPauseImageLayers = [];
    syncSequenceAutoAdvance();
    alert("Keine Harmonisierungsdaten verfügbar.");
    return;
  }

  // Show run card, hide config card
  document.getElementById("harmConfigCard").style.display = "none";
  document.getElementById("harmRunCard").style.display = "";

  // Start audio context
  if (useAudio) {
    try {
      audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      startAudioRecording();
    } catch (e) {
      console.warn("Web Audio API not available:", e);
      audioCtx = null;
    }
  }

  // Draw first matrix
  harmDrawMatrix();
  harmUpdateInfo();
  if (useAudio && audioCtx) harmPlayAudio();

  // Start the IMPULS/PAUSE cycle
  harmScheduleNext(pulseSec);

  // Update timer every second
  harmInterval = setInterval(() => {
    const elapsed = Date.now() / 1000 - harmStartTime;
    const remaining = Math.max(0, harmTotalDuration - elapsed);

    if (remaining <= 0) {
      stopHarmonizer();
      return;
    }

    const mins = Math.floor(remaining / 60);
    const secs = Math.floor(remaining % 60);
    document.getElementById("harmTimer").textContent =
      `${String(mins).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;
    document.getElementById("harmRemaining").textContent =
      `Restzeit: ${mins} Min ${secs} Sek`;

    const totalCycles = Math.ceil(harmTotalDuration / (pulseSec + pauseSec));
    const currentCycle = Math.floor(elapsed / (pulseSec + pauseSec)) + 1;
    document.getElementById("harmCycle").textContent =
      `Zyklus ${Math.min(currentCycle, totalCycles)} / ${totalCycles}`;
  }, 500);
}

function harmScheduleNext(delaySec) {
  if (!harmRunning) return;
  harmTimeout = setTimeout(() => {
    harmTimeout = null;
    if (!harmRunning) return;

    try {
      const pulseSec = parseFloat(document.getElementById("harmPulse").value) || 14;
      const pauseSec = parseFloat(document.getElementById("harmPause").value) || 14;

      if (harmIsBlank) {
        // End of PAUSE -> start IMPULS
        harmIsBlank = false;
        harmCurrentIdx = (harmCurrentIdx + 1) % harmItems.length;
        harmDrawMatrix();
        harmUpdateInfo();
        if (audioCtx) harmPlayAudio();
        harmScheduleNext(pulseSec);
      } else {
        // End of IMPULS -> start PAUSE
        harmIsBlank = true;
        harmClearMatrix();
        harmStopAudio();
        harmUpdateInfo();
        harmScheduleNext(pauseSec);
      }
    } catch (e) {
      console.error("Harmonizer cycle failed:", e);
      harmRunning = false;
      harmStopAudio();
      const infoEl = document.getElementById("harmInfo");
      if (infoEl) infoEl.textContent = `Harmonisierung angehalten: ${e.message}`;
    }
  }, delaySec * 1000);
}

function harmDrawMatrix() {
  const container = document.getElementById("harmMatrixContainer");
  if (!harmItems.length) return;

  const item = harmItems[harmCurrentIdx];
  const data = item.matrix;
  const colors = ensureColorGrid(data, item.colors);
  const size = data.length;
  const cellSize = size <= 12 ? 38 : size <= 24 ? 24 : 16;

  const grid = document.createElement("div");
  grid.className = "res-matrix";
  grid.style.gridTemplateColumns = `repeat(${size}, ${cellSize}px)`;

  for (let r = 0; r < data.length; r++) {
    for (let c = 0; c < data[r].length; c++) {
      const cell = document.createElement("div");
      cell.className = "res-cell";
      cell.style.width = cellSize + "px";
      cell.style.height = cellSize + "px";
      cell.style.background = colors[r]?.[c] || "#333";
      cell.style.fontSize = size <= 12 ? ".7rem" : size <= 24 ? ".55rem" : ".45rem";
      const hex = (colors[r]?.[c] || "#333333").replace("#", "");
      const rr = parseInt(hex.substring(0, 2), 16) || 0;
      const gg = parseInt(hex.substring(2, 4), 16) || 0;
      const bb = parseInt(hex.substring(4, 6), 16) || 0;
      const lum = 0.2126 * rr + 0.7152 * gg + 0.0722 * bb;
      cell.style.color = lum > 128 ? "#000" : "#fff";
      cell.textContent = data[r][c];
      grid.appendChild(cell);
    }
  }
  container.innerHTML = "";
  container.appendChild(grid);
  const rect = grid.getBoundingClientRect();
  if (rect.width > 0 && rect.height > 0) {
    harmMatrixFrameSize = {
      width: Math.ceil(rect.width),
      height: Math.ceil(rect.height)
    };
  }
}

function harmClearMatrix() {
  const container = document.getElementById("harmMatrixContainer");
  container.innerHTML = renderPauseLayerStack(harmPauseImageLayers);
}

function harmUpdateInfo() {
  const phaseLabel = document.getElementById("harmPhaseLabel");
  const infoEl = document.getElementById("harmInfo");
  const item = harmItems[harmCurrentIdx] || {};

  if (harmIsBlank) {
    phaseLabel.className = "harm-phase-pause";
    phaseLabel.textContent = "⏸ PAUSE";
    infoEl.textContent = "Stille — Integration der Resonanz";
  } else {
    phaseLabel.className = "harm-phase-pulse";
    phaseLabel.textContent = "▶ IMPULS";
    const ampName = document.getElementById("amplifier").value;
    const solfFreq = document.querySelector('input[name="harmSolf"]:checked').value;
    infoEl.textContent = `${item.label || "Matrix"} (${harmCurrentIdx + 1}/${harmItems.length}) | Solfeggio: ${solfFreq} Hz` +
      (ampName ? ` | Amplifier: ${ampName}` : "");
  }
}

function harmPlayAudio() {
  if (!audioCtx) return;
  harmStopAudio();

  const item = harmItems[harmCurrentIdx];
  if (!item) return;

  const baseFreq = Math.max(30, Math.min(item.clientFreq, 4000));
  const solfFreq = item.solfFreq || 432;
  const ampFreq = item.ampFreq || 0;
  const masterGain = audioCtx.createGain();
  masterGain.gain.value = 0.12;
  masterGain.connect(audioCtx.destination);

  // Fade in
  masterGain.gain.setValueAtTime(0, audioCtx.currentTime);
  masterGain.gain.linearRampToValueAtTime(0.12, audioCtx.currentTime + 0.5);

  // Also connect to recording destination if active
  if (recordingDest) masterGain.connect(recordingDest);

  function makeOsc(freq, gain) {
    if (freq < 20 || freq > 20000) return;
    const osc = audioCtx.createOscillator();
    const g = audioCtx.createGain();
    osc.type = "sine";
    osc.frequency.value = freq;
    g.gain.value = gain;
    osc.connect(g);
    g.connect(masterGain);
    osc.start();
    activeOscillators.push({ osc, gain: g, master: masterGain });
  }

  // Layer 1: Base frequency (Client)
  makeOsc(baseFreq, 1.0);
  // Layer 2: Fifth harmonic
  makeOsc(baseFreq * 1.5, 0.1);
  // Layer 3: Solfeggio
  makeOsc(solfFreq, 0.05);
  // Layer 4: Octave below
  makeOsc(baseFreq / 2, 0.15);
  // Layer 5: Amplifier frequency (if set)
  if (ampFreq > 20) makeOsc(ampFreq, 0.08);
}

function harmStopAudio() {
  activeOscillators.forEach(({ osc, gain, master }) => {
    try {
      if (audioCtx && master) {
        master.gain.linearRampToValueAtTime(0, audioCtx.currentTime + 0.3);
      }
      setTimeout(() => { try { osc.stop(); } catch(e) {} }, 400);
    } catch (e) {}
  });
  activeOscillators = [];
}

function stopHarmonizer() {
  harmRunning = false;
  if (harmInterval) { clearInterval(harmInterval); harmInterval = null; }
  if (harmTimeout) { clearTimeout(harmTimeout); harmTimeout = null; }
  harmStopAudio();
  releasePauseImageLayers();
  harmPauseImageLayers = [];
  harmItems = [];
  syncSequenceAutoAdvance();

  // Export session audio if recording was active
  if (mediaRecorder && mediaRecorder.state !== "inactive") {
    stopAudioRecording().then(() => {
      if (audioRecordingChunks.length > 0) {
        const shouldExport = confirm("Harmonisierung beendet.\nSession-Audio als Datei speichern?");
        if (shouldExport) exportSessionAudio();
      }
    });
  }

  if (audioCtx) { try { audioCtx.close(); } catch(e) {} audioCtx = null; }
  recordingDest = null;
  mediaRecorder = null;

  document.getElementById("harmTimer").textContent = "00:00";
  document.getElementById("harmPhaseLabel").textContent = "✓ ABGESCHLOSSEN";
  document.getElementById("harmPhaseLabel").className = "";
  document.getElementById("harmPhaseLabel").style.color = "var(--green)";
  document.getElementById("harmRemaining").textContent = "Harmonisierung beendet";
  document.getElementById("harmInfo").textContent = "Sie können die Ergebnisse exportieren oder eine neue Analyse starten.";

  // Show config card again after short delay
  setTimeout(() => {
    document.getElementById("harmConfigCard").style.display = "";
    document.getElementById("harmRunCard").style.display = "none";
    // Reset button
    document.getElementById("btnHarmStart").innerHTML = "🎵 Erneut starten";
  }, 2000);
}

// ========== FOKUS-HISTORY ==========
const FOCUS_HISTORY_KEY = "resonance_focus_history";
const MAX_FOCUS_HISTORY = 42;

function loadFocusHistory() {
  try {
    return JSON.parse(localStorage.getItem(FOCUS_HISTORY_KEY) || "[]");
  } catch { return []; }
}

function saveFocusToHistory(focusStr) {
  if (!focusStr) return;
  const parts = focusStr.split(";").map(s => s.trim()).filter(Boolean);
  let history = loadFocusHistory();
  parts.forEach(f => {
    history = history.filter(h => h !== f);
    history.push(f);
  });
  if (history.length > MAX_FOCUS_HISTORY) {
    history = history.slice(history.length - MAX_FOCUS_HISTORY);
  }
  localStorage.setItem(FOCUS_HISTORY_KEY, JSON.stringify(history));
}

function renderFocusHistory() {
  const section = document.getElementById("focusHistorySection");
  const grid = document.getElementById("focusHistory");
  const history = loadFocusHistory();
  const defaultPresets = new Set(FOCUS_PRESETS);
  const unique = history.filter(h => !defaultPresets.has(h)).reverse().slice(0, 15);

  if (unique.length === 0) {
    section.style.display = "none";
    return;
  }
  section.style.display = "";
  grid.innerHTML = "";
  unique.forEach(f => {
    const btn = document.createElement("button");
    btn.className = "focus-hist-btn";
    btn.textContent = f.length > 35 ? f.substring(0, 35) + "…" : f;
    btn.title = f;
    btn.onclick = () => {
      const ta = document.getElementById("focusText");
      const current = ta.value.trim();
      if (current && !current.endsWith(";")) {
        ta.value = current + "; " + f;
      } else {
        ta.value = current ? current + " " + f : f;
      }
      updateFocusCount();
      document.getElementById("focusValErr").textContent = "";
    };
    grid.appendChild(btn);
  });
}

// ========== MULTI-FOKUS COUNTER ==========
function updateFocusCount() {
  const ta = document.getElementById("focusText");
  const el = document.getElementById("focusCount");
  const parts = ta.value.split(";").map(s => s.trim()).filter(Boolean);
  if (parts.length <= 1) {
    el.textContent = "";
  } else if (parts.length > 42) {
    el.textContent = `${parts.length} Fokusse (Maximum: 42 — FIFO aktiv)`;
    el.style.color = "var(--red)";
    // FIFO: trim to last 42
    const trimmed = parts.slice(parts.length - 42);
    ta.value = trimmed.join("; ");
    el.textContent = `42 Fokusse (FIFO: ${parts.length - 42} entfernt)`;
  } else {
    el.textContent = `${parts.length} Fokusse`;
    el.style.color = "";
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const focusTA = document.getElementById("focusText");
  if (focusTA) {
    focusTA.addEventListener("input", updateFocusCount);
  }
});

// ========== TEMPLATE HISTORIE ==========
const TPL_STORAGE_KEY = "resonance_templates";
const MAX_TEMPLATES = 21;

function loadTemplates() {
  try {
    return JSON.parse(localStorage.getItem(TPL_STORAGE_KEY) || "[]");
  } catch { return []; }
}

function saveTemplates(templates) {
  localStorage.setItem(TPL_STORAGE_KEY, JSON.stringify(templates));
}

function openTplModal() {
  document.getElementById("tplModal").style.display = "";
  renderTplList();
}

function closeTplModal() {
  document.getElementById("tplModal").style.display = "none";
}

function buildTemplateObject(name) {
  const tpl = {
    name: name,
    savedAt: new Date().toISOString(),
    vectorMode: getVectorMode(),
    firstName: document.getElementById("firstName").value,
    lastName: document.getElementById("lastName").value,
    birthDate: document.getElementById("birthDate").value,
    birthPlace: document.getElementById("birthPlace").value,
    birthTime: document.getElementById("birthTime").value,
    birthPlanet: document.getElementById("birthPlanet").value,
    planetaryToggle: document.getElementById("planetaryToggle").checked,
    groupMembers: document.getElementById("groupMembers").value,
    geoLabel: document.getElementById("geoLabel").value,
    geoLat: document.getElementById("geoLat").value,
    geoLon: document.getElementById("geoLon").value,
    geoRadius: document.getElementById("geoRadius").value,
    imagePath: document.getElementById("imagePath").value,
    dbPath: document.getElementById("dbPathSelect").value,
    dbTopN: document.getElementById("dbTopN").value,
    dbPrefix: document.getElementById("dbPrefix").value,
    focusText: document.getElementById("focusText").value,
    matrixSize: document.querySelector('input[name="matrixSize"]:checked')?.value || "12",
    calcMode: document.querySelector('input[name="calcMode"]:checked')?.value || "quantum",
    focusWeight: document.getElementById("focusWeight").value,
    symmetry: document.querySelector('input[name="symmetry"]:checked')?.value || "none",
    palette: document.getElementById("palette").value,
    amplifier: document.getElementById("amplifier").value,
    emfToggle: document.getElementById("emfToggle").checked,
    hrvToggle: document.getElementById("hrvToggle").checked,
  };

  return tpl;
}

function saveTemplateByName(name, opts = {}) {
  const { showAlert = true } = opts;
  const cleanName = (name || "").trim();
  if (!cleanName) {
    alert("Bitte einen Namen eingeben.");
    return false;
  }

  const tpl = buildTemplateObject(cleanName);

  let templates = loadTemplates();
  // Replace if same name exists
  templates = templates.filter(t => t.name !== cleanName);
  templates.unshift(tpl);
  if (templates.length > MAX_TEMPLATES) templates = templates.slice(0, MAX_TEMPLATES);
  saveTemplates(templates);

  renderTplList();
  updateTplCount();
  syncStartTemplateSelect("0");

  if (showAlert) {
    alert(`✓ Template "${cleanName}" gespeichert!`);
  }
  return true;
}

function saveTemplate() {
  const input = document.getElementById("tplName");
  const name = input?.value.trim() || "";
  if (!saveTemplateByName(name)) return;
  if (input) input.value = "";
}

function saveTemplateFromSummary() {
  const input = document.getElementById("summaryTplName");
  const name = input?.value.trim() || "";
  if (!saveTemplateByName(name)) return;
  const harmInput = document.getElementById("harmTplName");
  if (harmInput && !harmInput.value.trim()) harmInput.value = name;
  const exportInput = document.getElementById("exportTplName");
  if (exportInput && !exportInput.value.trim()) exportInput.value = name;
}

function saveTemplateFromHarmonize() {
  const input = document.getElementById("harmTplName");
  const name = input?.value.trim() || "";
  if (!saveTemplateByName(name)) return;
  const summaryInput = document.getElementById("summaryTplName");
  if (summaryInput && !summaryInput.value.trim()) summaryInput.value = name;
  const exportInput = document.getElementById("exportTplName");
  if (exportInput && !exportInput.value.trim()) exportInput.value = name;
}

function saveTemplateFromExport() {
  const input = document.getElementById("exportTplName");
  const name = input?.value.trim() || "";
  if (!saveTemplateByName(name)) return;
}

function syncStartTemplateSelect(preferredValue = "") {
  const select = document.getElementById("startTemplateSelect");
  const btn = document.getElementById("btnLoadStartTemplate");
  if (!select) return;

  const templates = loadTemplates();
  const previous = preferredValue || select.value;
  select.innerHTML = '<option value="">Template optional auswählen...</option>';
  templates.forEach((t, idx) => {
    const opt = document.createElement("option");
    opt.value = String(idx);
    opt.textContent = t.name;
    select.appendChild(opt);
  });

  if (previous) {
    const hit = Array.from(select.options).find((o) => o.value === String(previous));
    if (hit) select.value = String(previous);
  }

  if (btn) btn.disabled = !select.value;
}

function loadSelectedStartTemplate() {
  const select = document.getElementById("startTemplateSelect");
  if (!select || !select.value) return;
  const idx = Number(select.value);
  if (Number.isNaN(idx)) return;
  loadTemplate(idx);
}

function loadTemplate(idx) {
  const templates = loadTemplates();
  const t = templates[idx];
  if (!t) return;

  uploadedImageBase64 = "";
  document.getElementById("groupMembers").value = "";
  document.getElementById("groupJsonFile").value = "";
  document.getElementById("planetaryToggle").checked = false;
  document.getElementById("geoLabel").value = "";
  document.getElementById("geoLat").value = "";
  document.getElementById("geoLon").value = "";
  document.getElementById("geoRadius").value = "";
  document.getElementById("imageFile").value = "";
  document.getElementById("imagePath").value = "";
  document.getElementById("imageFileInfo").textContent = "Kein Bild ausgewählt.";
  document.getElementById("dbTopN").value = "21";
  document.getElementById("dbPrefix").value = "";
  if (dbOperationController) cancelDbOperation();
  else {
    stopDbProgress();
    setDbControlsBusy(false);
  }

  if (t.vectorMode) {
    const r = document.querySelector(`input[name="vectorMode"][value="${t.vectorMode}"]`);
    if (r) r.checked = true;
  }

  if (t.firstName) document.getElementById("firstName").value = t.firstName;
  if (t.lastName) document.getElementById("lastName").value = t.lastName;
  if (t.birthDate) document.getElementById("birthDate").value = t.birthDate;
  if (t.birthPlace) document.getElementById("birthPlace").value = t.birthPlace;
  if (t.birthTime) document.getElementById("birthTime").value = t.birthTime;
  if (t.birthPlanet) document.getElementById("birthPlanet").value = t.birthPlanet;
  if (Object.prototype.hasOwnProperty.call(t, "planetaryToggle")) {
    document.getElementById("planetaryToggle").checked = !!t.planetaryToggle;
  }
  if (t.groupMembers) document.getElementById("groupMembers").value = t.groupMembers;
  if (t.geoLabel) document.getElementById("geoLabel").value = t.geoLabel;
  if (t.geoLat) document.getElementById("geoLat").value = t.geoLat;
  if (t.geoLon) document.getElementById("geoLon").value = t.geoLon;
  if (t.geoRadius) document.getElementById("geoRadius").value = t.geoRadius;
  if (t.imagePath) document.getElementById("imagePath").value = t.imagePath;
  if (t.dbTopN) document.getElementById("dbTopN").value = t.dbTopN;
  if (t.dbPrefix) document.getElementById("dbPrefix").value = t.dbPrefix;
  if (t.focusText) document.getElementById("focusText").value = t.focusText;
  if (t.matrixSize) {
    const r = document.querySelector(`input[name="matrixSize"][value="${t.matrixSize}"]`);
    if (r) r.checked = true;
  }
  if (t.calcMode) {
    const r = document.querySelector(`input[name="calcMode"][value="${t.calcMode}"]`);
    if (r) r.checked = true;
  }
  if (t.focusWeight) document.getElementById("focusWeight").value = t.focusWeight;
  if (t.symmetry) {
    const r = document.querySelector(`input[name="symmetry"][value="${t.symmetry}"]`);
    if (r) r.checked = true;
  }
  if (t.palette) document.getElementById("palette").value = t.palette;
  if (t.amplifier) document.getElementById("amplifier").value = t.amplifier;
  if (Object.prototype.hasOwnProperty.call(t, "emfToggle")) {
    document.getElementById("emfToggle").checked = !!t.emfToggle;
  }
  if (Object.prototype.hasOwnProperty.call(t, "hrvToggle")) {
    document.getElementById("hrvToggle").checked = !!t.hrvToggle;
  }
  updateVectorModeUI();
  loadDbList(t.dbPath || "");
  syncStartTemplateSelect(String(idx));

  const summaryTplInput = document.getElementById("summaryTplName");
  if (summaryTplInput) summaryTplInput.value = t.name || "";
  const harmTplInput = document.getElementById("harmTplName");
  if (harmTplInput) harmTplInput.value = t.name || "";
  const exportTplInput = document.getElementById("exportTplName");
  if (exportTplInput) exportTplInput.value = t.name || "";

  closeTplModal();
  saveSession();
  updateFocusCount();
  buildSummary();
  alert(`✓ Template "${t.name}" geladen!`);
}

function deleteTemplate(idx) {
  const templates = loadTemplates();
  const name = templates[idx]?.name || "";
  if (!confirm(`Template "${name}" löschen?`)) return;
  templates.splice(idx, 1);
  saveTemplates(templates);
  renderTplList();
  updateTplCount();
}

function renderTplList() {
  const container = document.getElementById("tplList");
  const templates = loadTemplates();

  if (templates.length === 0) {
    container.innerHTML = '<div class="tpl-empty">Keine gespeicherten Konfigurationen.</div>';
    return;
  }

  container.innerHTML = "";
  templates.forEach((t, i) => {
    const date = t.savedAt ? new Date(t.savedAt).toLocaleString("de-DE", { day: "2-digit", month: "2-digit", year: "numeric", hour: "2-digit", minute: "2-digit" }) : "–";
    const client = [t.firstName, t.lastName].filter(Boolean).join(" ") || "–";
    const focus = (t.focusText || "–").substring(0, 40);

    const div = document.createElement("div");
    div.className = "tpl-item";
    div.innerHTML = `
      <div class="tpl-item-info">
        <div class="tpl-item-name">${t.name}</div>
        <div class="tpl-item-meta">${date} · ${client} · ${focus}${t.focusText?.length > 40 ? '…' : ''}</div>
      </div>
      <div class="tpl-item-actions">
        <button class="tpl-btn-sm" onclick="loadTemplate(${i})">Laden</button>
        <button class="tpl-btn-sm del" onclick="deleteTemplate(${i})">✕</button>
      </div>`;
    container.appendChild(div);
  });
}

function updateTplCount() {
  const el = document.getElementById("tplCount");
  const count = loadTemplates().length;
  if (el) el.textContent = count > 0 ? `${count} Template${count > 1 ? 's' : ''} gespeichert` : "";
  syncStartTemplateSelect();
}

// ========== SESSION AUDIO WAV EXPORT ==========
let audioRecordingChunks = [];
let mediaRecorder = null;
let recordingDest = null;

function startAudioRecording() {
  if (!audioCtx) return;
  try {
    recordingDest = audioCtx.createMediaStreamDestination();
    // Connect master gain to recording destination as well
    // We do this by creating a splitter after the first audio play
    audioRecordingChunks = [];
    mediaRecorder = new MediaRecorder(recordingDest.stream, { mimeType: "audio/webm" });
    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) audioRecordingChunks.push(e.data);
    };
    mediaRecorder.start(1000); // chunk every second
  } catch (e) {
    console.warn("Audio recording not supported:", e);
    mediaRecorder = null;
  }
}

function stopAudioRecording() {
  if (!mediaRecorder || mediaRecorder.state === "inactive") return;
  return new Promise(resolve => {
    mediaRecorder.onstop = resolve;
    mediaRecorder.stop();
  });
}

async function exportSessionAudio() {
  if (!audioRecordingChunks.length) return;
  const blob = new Blob(audioRecordingChunks, { type: "audio/webm" });
  if (blob.size < 1000) return; // too small, skip
  const fn = document.getElementById("firstName").value.trim() || "Session";
  const ln = document.getElementById("lastName").value.trim() || "Audio";
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `${fn}_${ln}_Harmonisierung_${new Date().toISOString().slice(0,10)}.webm`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  audioRecordingChunks = [];
}

// ========== KEYBOARD NAV ==========
document.addEventListener("keydown", (e) => {
  if (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA" || e.target.tagName === "SELECT") return;
  if (e.key === "ArrowRight") { e.preventDefault(); navigate(1); }
  else if (e.key === "ArrowLeft") { e.preventDefault(); navigate(-1); }
  if (e.key === "Escape" && harmRunning) stopHarmonizer();
  if (e.key === "Escape" && document.getElementById("tplModal").style.display !== "none") closeTplModal();
});

// ========== INIT ==========
buildNav();
buildPresets();
updateProgress();
checkAPI();
restoreSession();
document.querySelectorAll('input[name="vectorMode"]').forEach((el) => {
  el.addEventListener("change", () => {
    updateVectorModeUI();
    saveSession();
    buildSummary();
  });
});
const imageFileInput = document.getElementById("imageFile");
if (imageFileInput) imageFileInput.addEventListener("change", onImageFileChange);
const startTemplateSelect = document.getElementById("startTemplateSelect");
if (startTemplateSelect) {
  startTemplateSelect.addEventListener("change", () => {
    const startTplBtn = document.getElementById("btnLoadStartTemplate");
    if (startTplBtn) startTplBtn.disabled = !startTemplateSelect.value;
  });
}
renderFocusHistory();
updateTplCount();
buildSummary();

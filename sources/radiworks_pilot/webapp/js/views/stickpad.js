/* Stick-Pad-View: Positionsfolge und Modus werden serverseitig erfasst. */

export function initStickPadView(api, eventBus) {
  const pad = document.getElementById("pad-area");
  const padHint = document.getElementById("pad-hint");
  const countOut = document.getElementById("pad-count");
  const modeSelect = document.getElementById("pad-mode");
  const captureOut = document.getElementById("pad-capture-out");
  const dbSelect = document.getElementById("pad-db");
  const analyzeBtn = document.getElementById("pad-analyze-btn");
  const gvBtn = document.getElementById("pad-gv-btn");
  const clearBtn = document.getElementById("pad-clear-btn");
  const gvOut = document.getElementById("pad-gv-out");
  const resultEmpty = document.getElementById("pad-result-empty");
  const resultWrap = document.getElementById("pad-result-wrap");
  const resultBody = document.getElementById("pad-result-body");

  api.databases().then((data) => {
    for (const entry of data.catalogs) {
      const option = document.createElement("option");
      option.value = entry.id;
      option.textContent = entry.label;
      dbSelect.appendChild(option);
    }
  });

  let collecting = false;
  let lastSent = 0;
  let sendQueue = Promise.resolve();
  let queued = 0;
  let ready = false;

  function showReceipt(receipt, catalogCheck = null) {
    if (!receipt) return;
    const timed = receipt.mode === "original";
    const first = receipt.positions[0]?.capturedAtMs;
    const last = receipt.positions.at(-1)?.capturedAtMs;
    const count = receipt.positions.length;
    let catalogText = "";
    if (receipt.kind === "analysis") {
      if (receipt.catalog) {
        const binding = receipt.catalog;
        catalogText = ` Ratenfolge ${binding.selector}: ${binding.rateCount} Raten, SHA-256 ${binding.digest.slice(0, 12)}…`;
      } else {
        catalogText = " Älterer Analysebeleg ohne Katalogbindung.";
      }
      if (catalogCheck?.state === "current") catalogText += " Aktueller Stand stimmt überein.";
      if (catalogCheck?.state === "changed") catalogText += " Achtung: Ratenfolge seit diesem Lauf geändert.";
      if (catalogCheck?.state === "unavailable") catalogText += " Achtung: Ratenfolge derzeit nicht verfügbar.";
    }
    captureOut.textContent = `Erfassung ${receipt.id}: ${count} ${count === 1 ? "Position" : "Positionen"}, `
      + `${timed ? `Original-Zeitmodus (${first}–${last} ms)` : "reproduzierbarer Modus"}. `
      + `${timed ? "Zeitwerte und Seeds" : "Seeds"} sind im lokalen Laufzeitzustand protokolliert.`
      + catalogText;
  }

  api.stickStatus().then((status) => {
    if (status.mode) modeSelect.value = status.mode;
    modeSelect.disabled = status.positions.length > 0;
    countOut.textContent = `${status.positions.length} ${status.positions.length === 1 ? "Position" : "Positionen"} gesammelt.`;
    showReceipt(status.lastReceipt, status.catalogCheck);
    ready = true;
  }).catch((error) => {
    padHint.textContent = `Stick-Pad-Status nicht verfügbar: ${error.message}`;
  });

  function sendPosition(x, y) {
    if (!ready || queued >= 16) return;
    queued += 1;
    modeSelect.disabled = true;
    const mode = modeSelect.value;
    sendQueue = sendQueue.then(() => api.stickPosition(x, y, mode)).then((data) => {
      countOut.textContent = `${data.positions} ${data.positions === 1 ? "Position" : "Positionen"} gesammelt.`;
      if (data.positions === 1) padHint.textContent = "Sammle …";
    }).catch((error) => {
      padHint.textContent = `Position nicht erfasst: ${error.message}`;
    }).finally(() => { queued -= 1; });
  }

  pad.addEventListener("pointerdown", (event) => {
    collecting = true;
    pad.setPointerCapture(event.pointerId);
    sendPosition(Math.round(event.offsetX), Math.round(event.offsetY));
  });
  pad.addEventListener("pointermove", (event) => {
    if (!collecting) return;
    const now = performance.now();
    if (now - lastSent < 120) return; // Rate-Limit: ~8 Positionen/s
    lastSent = now;
    sendPosition(Math.round(event.offsetX), Math.round(event.offsetY));
  });
  pad.addEventListener("pointerup", () => { collecting = false; });
  pad.addEventListener("pointerleave", () => { collecting = false; });
  // Tastatur-Pfad: Leertaste halten erzeugt Positionen aus der Zeit
  pad.addEventListener("keydown", (event) => {
    if (event.code !== "Space" || event.repeat) return;
    collecting = true;
  });
  pad.addEventListener("keyup", (event) => {
    if (event.code !== "Space") return;
    collecting = false;
    const rect = pad.getBoundingClientRect();
    sendPosition(
      Math.round((event.timeStamp % rect.width) | 0),
      Math.round((event.timeStamp % rect.height) | 0)
    );
  });

  analyzeBtn.addEventListener("click", async () => {
    try {
      await sendQueue;
      const result = await api.stickAnalyze(dbSelect.value);
      render(result);
      showReceipt(result.stickPadCapture);
      padHint.textContent = result.sessionLinked
        ? "Stick-Pad-Analyse mit dem aktiven Fall als eigene Sitzung gespeichert. Weitere GV-Werte gehören zu dieser Sitzung."
        : "Stick-Pad-Analyse als Draft gespeichert. Ohne aktiven Fall besteht keine Sitzungsverknüpfung.";
      eventBus.dispatchEvent(new CustomEvent("stickpad.analysis", { detail: result }));
      countOut.textContent = "0 Positionen gesammelt.";
      modeSelect.disabled = false;
      try {
        const status = await api.stickStatus();
        showReceipt(status.lastReceipt, status.catalogCheck);
      } catch {
        captureOut.textContent += " Aktualitätsprüfung derzeit nicht verfügbar.";
      }
    } catch (error) {
      alert(`Stick-Pad-Analyse: ${error.message}`);
    }
  });

  gvBtn.addEventListener("click", async () => {
    try {
      await sendQueue;
      const data = await api.stickGv();
      gvOut.textContent = data.roundBoundary
        ? "Neue GV-Runde vorbereitet. Gesammelte Positionen bleiben erhalten; GV erneut starten."
        : data.gv == null
          ? "Keine Positionen für eine GV."
          : data.coupled
            ? `Stick-Pad-GV: ${data.gv} · ${data.rateIndex == null ? "Fallwert" : `Rate ${data.rateIndex + 1}`} · Schritt ${data.counter}.`
            : `Stick-Pad-GV: ${data.gv} (ohne Fall-/Ratenzuordnung).`;
      if (data.gv != null) {
        showReceipt(data.stickPadCapture);
        countOut.textContent = "0 Positionen gesammelt.";
        modeSelect.disabled = false;
        if (data.coupled) eventBus.dispatchEvent(new CustomEvent("gv.external", { detail: data }));
      }
    } catch (error) {
      gvOut.textContent = `Fehler: ${error.message}`;
    }
  });

  clearBtn.addEventListener("click", async () => {
    try {
      collecting = false;
      await sendQueue;
      const cleared = await api.stickClear();
      countOut.textContent = "0 Positionen gesammelt.";
      padHint.textContent = "Hier Zeiger führen oder gedrückt halten — jede Position zählt.";
      gvOut.textContent = "";
      modeSelect.disabled = false;
      return cleared;
    } catch (error) {
      padHint.textContent = `Leeren fehlgeschlagen: ${error.message}`;
    }
  });

  function render(result) {
    const rows = result.rateObjects || [];
    resultEmpty.hidden = rows.length > 0;
    resultWrap.hidden = rows.length === 0;
    resultBody.innerHTML = "";
    rows.forEach((rate) => {
      const tr = document.createElement("tr");
      const name = document.createElement("td");
      name.textContent = rate.nameOrRate;
      const value = document.createElement("td");
      value.className = "num";
      value.textContent = String(rate.energeticValue);
      tr.append(name, value);
      resultBody.appendChild(tr);
    });
  }
}

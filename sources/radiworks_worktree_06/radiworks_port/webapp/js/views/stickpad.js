/* Stick-Pad-View (Aether_6): Zeiger-/Halte-Interaktion → Positionen → Analyse.
   Das Halten/Fließen entspricht dem Original („PRESS AND HOLD SPACE …");
   die Abbildung passiert serverseitig (bitexakte Java-Random-Emulation). */

export function initStickPadView(api) {
  const pad = document.getElementById("pad-area");
  const padHint = document.getElementById("pad-hint");
  const countOut = document.getElementById("pad-count");
  const dbSelect = document.getElementById("pad-db");
  const analyzeBtn = document.getElementById("pad-analyze-btn");
  const gvBtn = document.getElementById("pad-gv-btn");
  const clearBtn = document.getElementById("pad-clear-btn");
  const gvOut = document.getElementById("pad-gv-out");
  const resultEmpty = document.getElementById("pad-result-empty");
  const resultWrap = document.getElementById("pad-result-wrap");
  const resultBody = document.getElementById("pad-result-body");

  api.databases().then((data) => {
    for (const name of data.databases) {
      const option = document.createElement("option");
      option.value = name;
      option.textContent = name;
      dbSelect.appendChild(option);
    }
  });

  let collecting = false;
  let lastSent = 0;

  function sendPosition(x, y) {
    api.stickPosition(x, y).then((data) => {
      countOut.textContent = `${data.positions} Positionen gesammelt.`;
      if (data.positions === 1) padHint.textContent = "Sammle …";
    }).catch(() => { /* offline */ });
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
      const result = await api.stickAnalyze(dbSelect.value);
      render(result);
    } catch (error) {
      alert(`Stick-Pad-Analyse: ${error.message}`);
    }
  });

  gvBtn.addEventListener("click", async () => {
    try {
      const data = await api.stickGv();
      gvOut.textContent = data.gv == null
        ? "Keine Positionen für eine GV."
        : `Stick-Pad-GV: ${data.gv} (übrige Positionen: ${data.positions})`;
    } catch (error) {
      gvOut.textContent = `Fehler: ${error.message}`;
    }
  });

  clearBtn.addEventListener("click", async () => {
    const cleared = await api.stickClear();
    countOut.textContent = "0 Positionen gesammelt.";
    padHint.textContent = "Hier Zeiger führen oder gedrückt halten — jede Position zählt.";
    gvOut.textContent = "";
    return cleared;
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

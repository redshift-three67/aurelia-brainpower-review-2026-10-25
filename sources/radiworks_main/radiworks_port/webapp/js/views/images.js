/* Bild & Area (Aether_5 + Aether_7).
   Bilder verlassen den Browser nicht: gesendet wird nur die Anzahl der
   Schichten (Analyse) bzw. der Zeugen-Hash (Broadcast, SHA-256 statt
   MD5 — Aurelia-Hash-Familie, MD5 ist kryptografisch gebrochen). */

async function sha256Hex(buffer) {
  const digest = await crypto.subtle.digest("SHA-256", buffer);
  return [...new Uint8Array(digest)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

export function initImagesView(api) {
  const fileInput = document.getElementById("img-files");
  const countInput = document.getElementById("img-count");
  const analyzeBtn = document.getElementById("img-analyze-btn");
  const table = document.getElementById("img-table");
  const body = document.getElementById("img-body");
  const selection = document.getElementById("img-selection");
  let selectedFiles = [];

  const areaFile = document.getElementById("area-file");
  const areaW = document.getElementById("area-w");
  const areaH = document.getElementById("area-h");
  const scanBtn = document.getElementById("area-scan-btn");
  const canvas = document.getElementById("area-canvas");
  const areaOut = document.getElementById("area-out");
  const overlayCanvas = document.getElementById("area-overlay-canvas");
  const overlayStepBtn = document.getElementById("area-overlay-step");
  const overlayClearBtn = document.getElementById("area-overlay-clear");
  const overlayOut = document.getElementById("area-overlay-out");
  let areaImage = null;
  let overlayColors = null;
  let overlaySteps = 0;

  fileInput.addEventListener("change", () => {
    selectedFiles = [...(fileInput.files || [])];
    fileInput.value = "";
    selection.textContent = selectedFiles.length === 1
      ? "1 Bild ausgewählt"
      : `${selectedFiles.length} Bilder ausgewählt`;
  });

  analyzeBtn.addEventListener("click", async () => {
    const files = [...selectedFiles];
    const count = Math.max(1, Math.min(50, Number(countInput.value) || files.length || 1));
    analyzeBtn.disabled = true;
    try {
      const analysis = await api.imagesAnalyze({ count, seed: undefined });
      const hashes = await Promise.all(files.map((f) => f.arrayBuffer().then(sha256Hex)));
      body.innerHTML = "";
      table.hidden = false;
      analysis.layers.forEach((layer, index) => {
        const tr = document.createElement("tr");
        const idx = document.createElement("td");
        idx.textContent = String(layer.index + 1);
        const name = document.createElement("td");
        name.textContent = files[index] ? `Bild ${index + 1}` : `Schicht ${layer.index + 1}`;
        const hash = document.createElement("td");
        hash.className = "mono";
        hash.textContent = hashes[index] ? hashes[index].slice(0, 16) + "…" : "—";
        const gv = document.createElement("td");
        gv.className = "num";
        gv.textContent = String(layer.gv);
        const action = document.createElement("td");
        if (hashes[index]) {
          const btn = document.createElement("button");
          btn.type = "button";
          btn.className = "btn btn-broadcast";
          btn.textContent = "Broadcast";
          btn.addEventListener("click", async () => {
            try {
              await api.imagesBroadcast({ md5: hashes[index], seconds: 60 });
              document.querySelector('.tab[data-tab="broadcast"]').click();
            } catch (error) {
              alert(`Broadcast abgelehnt: ${error.message}`);
            }
          });
          action.appendChild(btn);
        } else {
          action.textContent = "—";
        }
        tr.append(idx, name, hash, gv, action);
        body.appendChild(tr);
      });
    } catch (error) {
      alert(`Bildanalyse: ${error.message}`);
    } finally {
      analyzeBtn.disabled = false;
    }
  });

  areaFile.addEventListener("change", () => {
    const file = areaFile.files?.[0];
    if (!file) return;
    areaFile.value = "";
    loadAreaFile(file);
  });

  /* Aether_5 „PASTE IMAGE / PASTE AREA": Strg+V fügt ein Bild aus der
     Zwischenablage als Fläche ein (nur wenn der Tab aktiv ist). */
  document.addEventListener("paste", (event) => {
    if (document.getElementById("view-images").hidden) return;
    const item = [...(event.clipboardData?.items || [])].find((i) => i.type.startsWith("image/"));
    if (!item) return;
    const file = item.getAsFile();
    if (file) {
      loadAreaFile(file);
      areaOut.textContent = "Bild aus der Zwischenablage eingefügt.";
    }
  });

  function loadAreaFile(file) {
    const reader = new FileReader();
    reader.onload = () => {
      const image = new Image();
      image.onload = () => {
        areaImage = image;
        overlayColors = null;
        overlaySteps = 0;
        drawArea();
        drawOverlay();
        areaOut.textContent = "Geladen: Bild — jetzt „Fläche scannen“.";
        overlayOut.textContent = "Bild geladen. Das Farb-Overlay kann getrennt vom Zahlen-Scan erzeugt werden.";
      };
      image.src = reader.result;
    };
    reader.readAsDataURL(file);
  }

  scanBtn.addEventListener("click", async () => {
    const width = Math.max(2, Math.min(64, Number(areaW.value) || 16));
    const height = Math.max(2, Math.min(64, Number(areaH.value) || 10));
    scanBtn.disabled = true;
    areaOut.textContent = "Scanne …";
    try {
      const data = await api.anomaly({ width, height, seed: undefined });
      drawHeatmap(data.values, width, height);
      const min = Math.min(...data.values);
      const max = Math.max(...data.values);
      areaOut.textContent = `Scan fertig — ${width}×${height} Zellen, GV-Spanne ${min}–${max} (grün = hohe GV).` +
        (areaImage ? "" : " (ohne Flächenbild — Grund bleibt dunkel)");
    } catch (error) {
      areaOut.textContent = `Fehler: ${error.message}`;
    } finally {
      scanBtn.disabled = false;
    }
  });

  overlayStepBtn.addEventListener("click", () => {
    if (!areaImage) {
      overlayOut.textContent = "Bitte zuerst ein Bild für Area auswählen.";
      return;
    }
    const count = 31 * 12;
    if (!overlayColors) {
      const random = crypto.getRandomValues(new Uint8Array(count * 4));
      overlayColors = Array.from({ length: count }, (_, index) => ({
        r: random[index * 4], g: random[index * 4 + 1],
        b: random[index * 4 + 2], a: random[index * 4 + 3] % 50,
      }));
    } else {
      const increments = crypto.getRandomValues(new Uint8Array(count));
      overlayColors.forEach((color, index) => {
        color.a = Math.min(255, color.a + increments[index] % 50);
      });
    }
    overlaySteps += 1;
    drawOverlay();
    overlayStepBtn.textContent = "Overlay verstärken";
    overlayOut.textContent = `Farb-Overlay: 31 × 12 Felder, Schritt ${overlaySteps}. Lokale Browser-Zufallsquelle; kein Hotbits- oder GV-Ergebnis.`;
  });

  overlayClearBtn.addEventListener("click", () => {
    overlayColors = null;
    overlaySteps = 0;
    overlayStepBtn.textContent = "Farb-Overlay erzeugen";
    drawOverlay();
    overlayOut.textContent = areaImage
      ? "Overlay zurückgesetzt; das Bild bleibt geladen."
      : "Bitte zuerst ein Bild für Area auswählen. Das Bild bleibt im Browser.";
  });

  function drawArea() {
    const ctx = canvas.getContext("2d");
    ctx.fillStyle = "#14181522";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    if (areaImage) {
      const scale = Math.min(canvas.width / areaImage.width, canvas.height / areaImage.height);
      const w = areaImage.width * scale;
      const h = areaImage.height * scale;
      ctx.drawImage(areaImage, (canvas.width - w) / 2, (canvas.height - h) / 2, w, h);
    }
  }

  function drawHeatmap(values, width, height) {
    drawArea();
    const ctx = canvas.getContext("2d");
    const cellW = canvas.width / width;
    const cellH = canvas.height / height;
    const min = Math.min(...values);
    const max = Math.max(...values);
    const span = Math.max(1, max - min);
    ctx.globalAlpha = 0.55;
    values.forEach((gv, index) => {
      const t = (gv - min) / span; // 0..1
      const col = Math.round((index % width) * cellW);
      const row = Math.floor(index / width) * cellH;
      ctx.fillStyle = `rgba(${Math.round(40 + (1 - t) * 180)}, ${Math.round(80 + t * 140)}, 62, 0.8)`;
      ctx.fillRect(col, row, cellW - 1, cellH - 1);
      ctx.globalAlpha = 0.9;
      ctx.fillStyle = "#F3EFE6";
      ctx.font = "9px sans-serif";
      ctx.fillText(String(gv), col + 2, row + cellH - 3);
      ctx.globalAlpha = 0.55;
    });
    ctx.globalAlpha = 1;
  }

  function drawOverlay() {
    const ctx = overlayCanvas.getContext("2d");
    const cellW = overlayCanvas.width / 31;
    const cellH = overlayCanvas.height / 12;
    ctx.fillStyle = "#10140f";
    ctx.fillRect(0, 0, overlayCanvas.width, overlayCanvas.height);
    if (areaImage) ctx.drawImage(areaImage, 0, 0, overlayCanvas.width, overlayCanvas.height);
    overlayColors?.forEach((color, index) => {
      ctx.fillStyle = `rgba(${color.r}, ${color.g}, ${color.b}, ${color.a / 255})`;
      ctx.fillRect((index % 31) * cellW, Math.floor(index / 31) * cellH, cellW, cellH);
    });
    ctx.strokeStyle = "rgba(0, 0, 0, 0.65)";
    ctx.lineWidth = 1;
    for (let x = 0; x <= 31; x += 1) {
      ctx.beginPath(); ctx.moveTo(x * cellW, 0); ctx.lineTo(x * cellW, overlayCanvas.height); ctx.stroke();
    }
    for (let y = 0; y <= 12; y += 1) {
      ctx.beginPath(); ctx.moveTo(0, y * cellH); ctx.lineTo(overlayCanvas.width, y * cellH); ctx.stroke();
    }
  }

  drawOverlay();
}

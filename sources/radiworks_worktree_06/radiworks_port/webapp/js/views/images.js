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

  const areaFile = document.getElementById("area-file");
  const areaW = document.getElementById("area-w");
  const areaH = document.getElementById("area-h");
  const scanBtn = document.getElementById("area-scan-btn");
  const canvas = document.getElementById("area-canvas");
  const areaOut = document.getElementById("area-out");
  let areaImage = null;

  analyzeBtn.addEventListener("click", async () => {
    const files = [...(fileInput.files || [])];
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
        name.textContent = files[index]?.name || `Schicht ${layer.index + 1}`;
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
      areaOut.textContent = `Eingefügt: ${file.name || "Zwischenablage-Bild"}.`;
    }
  });

  function loadAreaFile(file) {
    const reader = new FileReader();
    reader.onload = () => {
      const image = new Image();
      image.onload = () => {
        areaImage = image;
        drawArea();
        areaOut.textContent = `Geladen: ${file.name || "Zwischenablage-Bild"} — jetzt „Fläche scannen".`;
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
}

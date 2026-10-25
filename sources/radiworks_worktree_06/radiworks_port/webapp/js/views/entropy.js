/* Entropie-View (Aether_8 „GET HOTBITS"): Webcam-Frame-Differenz → Ganzzahlen
   → /entropy/acquire. KEINE Bildspeicherung, keine Übertragung von Frames —
   nur die abgeleiteten Ganzzahlen (Original-Algorithmus, verkleinertes
   Raster für Live-Feedback). */

const CAPTURE_W = 64;
const CAPTURE_H = 48;
const BATCH_SIZE = 200;

export function initEntropyView(api) {
  const startBtn = document.getElementById("cam-start-btn");
  const stopBtn = document.getElementById("cam-stop-btn");
  const statusEl = document.getElementById("cam-status");
  const video = document.getElementById("cam-preview");
  const feedStatus = document.getElementById("feed-status");

  let stream = null;
  let timer = null;
  let previous = null;
  let bits = "";
  const seen = new Set();
  const batch = [];
  let fedTotal = 0;

  startBtn.addEventListener("click", async () => {
    try {
      stream = await navigator.mediaDevices.getUserMedia({ video: true });
      video.srcObject = stream;
      video.hidden = false;
      statusEl.textContent = "Kamera aktiv — sammle …";
      await populateCameras();
      timer = setInterval(capture, 250);
    } catch (error) {
      statusEl.textContent = `Kamera verweigert/nicht verfügbar: ${error.message}`;
    }
  });

  async function populateCameras() {
    // Aether_8 „SHOW WEBCAMS / SET WEBCAM[n]": Geräteauswahl nach Einwilligung
    const devices = await navigator.mediaDevices.enumerateDevices();
    const cameras = devices.filter((d) => d.kind === "videoinput");
    const select = document.getElementById("cam-select");
    select.innerHTML = "";
    cameras.forEach((device, index) => {
      const option = document.createElement("option");
      option.value = device.deviceId;
      option.textContent = device.label || `Webcam ${index}`;
      select.appendChild(option);
    });
    select.onchange = async () => {
      if (!select.value) return;
      stream?.getTracks().forEach((track) => track.stop());
      stream = await navigator.mediaDevices.getUserMedia({
        video: { deviceId: { exact: select.value } },
      });
      video.srcObject = stream;
    };
  }

  stopBtn.addEventListener("click", stop);

  function stop() {
    if (timer) { clearInterval(timer); timer = null; }
    stream?.getTracks().forEach((track) => track.stop());
    stream = null;
    video.hidden = true;
    previous = null;
    bits = "";
    statusEl.textContent = "Aus.";
  }

  function capture() {
    if (!video.videoWidth) return;
    const scratch = document.createElement("canvas");
    scratch.width = CAPTURE_W;
    scratch.height = CAPTURE_H;
    const ctx = scratch.getContext("2d", { willReadFrequently: true });
    ctx.drawImage(video, 0, 0, CAPTURE_W, CAPTURE_H);
    const current = ctx.getImageData(0, 0, CAPTURE_W, CAPTURE_H).data;

    if (previous) {
      for (let i = 0; i < current.length && bits.length < 24; i += 1) {
        if (current[i] > previous[i]) bits += "1";
        else if (current[i] < previous[i]) bits += "0";
        if (bits.length === 24) {
          const parsed = parseInt(bits, 2);
          // Original-Veredelung: Wert + PRNG-Wurf (deterministisch zum Wert)
          const refined = (parsed + mulberry32(parsed)()) % 2147483647;
          if (!seen.has(refined)) {
            seen.add(refined);
            batch.push(refined);
          }
          bits = "";
        }
      }
    }
    previous = current;

    if (batch.length >= BATCH_SIZE) {
      const payload = batch.splice(0, batch.length);
      api.entropyAcquire(payload).then((data) => {
        fedTotal += data.acquired;
        feedStatus.textContent = `Feed: ${data.feedSize} Werte (insgesamt ${fedTotal} geliefert).`;
      }).catch(() => { /* offline */ });
    }
  }

  window.addEventListener("beforeunload", stop);
}

function mulberry32(seed) {
  let a = seed >>> 0;
  return function () {
    a |= 0; a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0);
  };
}

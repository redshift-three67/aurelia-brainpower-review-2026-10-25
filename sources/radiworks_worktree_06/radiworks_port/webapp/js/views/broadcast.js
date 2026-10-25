/* Broadcast-View: Senden, Fibonacci-Panels (Original-Ästhetik), LED-Streifen,
   Resonanzliste. Bewegung entfällt bei prefers-reduced-motion (statischer
   Rahmen + Textstatus), gemäß UI_DESIGN_STANDARD §4 / docs/15-live.md. */

const GROUP_CLASS = {
  whites: "on-white",
  infrared: "on-infrared",
  reds: "on-red",
  greens: "on-green",
  blues: "on-blue",
  ultraviolet: "on-ultraviolet",
};
const GROUP_LABEL = {
  whites: "weiß", infrared: "infrarot", reds: "rot",
  greens: "grün", blues: "blau", ultraviolet: "UV",
};

/* Fibonacci-Schwellen des Original-BroadcastElement (FUNKTIONSANALYSE §5.1) */
const PAINT = [
  { modulus: 13, threshold: 12, action: "signature" },
  { modulus: 21, threshold: 20, action: "overlay" },
  { modulus: 33, threshold: 32, action: "layer" },
  { modulus: 54, threshold: 53, action: "overlay-soft" },
  { modulus: 89, threshold: 89, action: "overlay-strong" },
];
const SHAPES = [144, 233, 377, 610, 987];

const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

export function initBroadcastView(api, eventBus) {
  const form = document.getElementById("broadcast-form");
  const sigInput = document.getElementById("sig-input");
  const secInput = document.getElementById("sec-input");
  const mulInput = document.getElementById("mul-input");
  const clearInput = document.getElementById("clear-input");
  const stopAllBtn = document.getElementById("stop-all-btn");
  const stage = document.getElementById("broadcast-stage");
  const queueCount = document.getElementById("queue-count");
  const resonanceList = document.getElementById("resonance-list");
  const binauralToggle = document.getElementById("binaural-toggle");

  /* Binaural-Sound (BroadcastElement.playBinauralSound): WebAudio, 3 s,
     L/R-Frequenzen aus dem Resonanz-Event; Zustand in Settings. */
  let audioCtx = null;
  api.settings().then((settings) => {
    binauralToggle.checked = settings.booleans?.["play.binaural.sound"] === true;
  });
  binauralToggle.addEventListener("change", () => {
    api.updateSettings({ booleans: { "play.binaural.sound": binauralToggle.checked } })
      .catch(() => {});
  });

  function playBinaural(params) {
    try {
      audioCtx = audioCtx || new (window.AudioContext || window.webkitAudioContext)();
      const ctx = audioCtx;
      const merger = ctx.createChannelMerger(2);
      const gain = ctx.createGain();
      gain.gain.value = params.volume ?? 0.5;
      const oscLeft = ctx.createOscillator();
      oscLeft.frequency.value = params.left_freq;
      oscLeft.connect(merger, 0, 0);
      const oscRight = ctx.createOscillator();
      oscRight.frequency.value = params.right_freq;
      oscRight.connect(merger, 0, 1);
      merger.connect(gain).connect(ctx.destination);
      const now = ctx.currentTime;
      oscLeft.start(now);
      oscRight.start(now);
      oscLeft.stop(now + 3);
      oscRight.stop(now + 3);
    } catch (_) { /* AudioContext verweigert */ }
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
      // Original broadcastNow: Signatur = Fallname + Eingabe (Vektor-Bindung)
      const focus = window.__RADIWORKS_CASE__ || null;
      const signature = focus ? `${focus} ${sigInput.value}` : sigInput.value;
      await api.broadcast({
        signature,
        seconds: Number(secInput.value),
        multiplier: Number(mulInput.value),
        clear: clearInput.checked,
      });
    } catch (error) {
      alert(`Broadcast abgelehnt: ${error.message}`);
    }
  });

  stopAllBtn.addEventListener("click", () => api.stopAll());

  /* ---- Elemente je Broadcast (320×180 wie im Original) ---- */
  const cards = new Map(); // signature → {card, canvas, ctx, progress, start, seconds}

  function ensureCard(payload) {
    const key = payload.signature;
    if (cards.has(key)) return cards.get(key);
    const card = document.createElement("div");
    card.className = "broadcast-card";
    const canvas = document.createElement("canvas");
    canvas.width = 320;
    canvas.height = 180;
    canvas.setAttribute("role", "img");
    canvas.setAttribute("aria-label", `Broadcast-Panel ${key}`);
    const caption = document.createElement("div");
    caption.className = "card-caption";
    const progress = document.createElement("div");
    progress.className = "progress-track";
    const fill = document.createElement("div");
    fill.className = "progress-fill";
    progress.appendChild(fill);
    card.append(canvas, caption, progress);
    stage.appendChild(card);
    const entry = {
      card, canvas, fill,
      ctx: canvas.getContext("2d"),
      rng: mulberry32(hash(key)),
      seconds: payload.seconds ?? 60,
      started: performance.now(),
      wave: 0,
      captionText: caption,
    };
    cards.set(key, entry);
    paintCaption(entry, key, 0);
    if (!reducedMotion) tick(entry, key);
    else paintStatic(entry, key);
    return entry;
  }

  function paintCaption(entry, key, progress) {
    entry.captionText.innerHTML = "";
    const name = document.createElement("span");
    name.textContent = key;
    const status = document.createElement("span");
    status.textContent = reducedMotion
      ? `statisch · ${(progress * 100) | 0} % (Bewegung reduziert)`
      : `Resonanz: ${entry.wave}`;
    entry.captionText.append(name, status);
  }

  /* Original draw()-Schwellen — visuelle Ebene, fachlich folgen Resonanzen
     ausschließlich den Server-Events (Server ist die Uhr). */
  function tick(entry, key) {
    const r = entry.rng;
    const ctx = entry.ctx;
    if (r.nextInt(13) >= 12) paintSignature(ctx, r, key);
    else if (r.nextInt(21) >= 20) paintOverlay(ctx, r, 5);
    else if (r.nextInt(33) >= 32) { paintOverlay(ctx, r, 8); paintSignature(ctx, r, key); }
    else if (r.nextInt(54) >= 53) paintOverlay(ctx, r, 20);

    if (r.nextInt(144) >= 143) paintShape(ctx, r, "rect");
    if (r.nextInt(233) >= 232) paintShape(ctx, r, "ellipse");
    if (r.nextInt(377) >= 376) paintShape(ctx, r, "line");
    if (r.nextInt(610) >= 609) paintShape(ctx, r, "triangle");

    const progressValue = Math.min(1, (performance.now() - entry.started) / (entry.seconds * 1000));
    entry.fill.style.width = `${progressValue * 100}%`;
    if (entry.wave > 0) {
      entry.wave = (entry.wave + 4) % 2584;
      paintWave(ctx, entry.wave);
    }
    paintCaption(entry, key, progressValue);
    if (progressValue < 1) requestAnimationFrame(() => tick(entry, key));
    else setTimeout(() => { entry.card.remove(); cards.delete(key); }, 4000);
  }

  function paintStatic(entry, key) {
    const ctx = entry.ctx;
    paintOverlay(ctx, entry.rng, 30);
    paintSignature(ctx, entry.rng, key);
  }

  eventBus.addEventListener("broadcast.progress", (event) => {
    const payload = event.detail;
    if (payload.finished || payload.stopped) {
      cards.get(payload.signature)?.card.remove();
      cards.delete(payload.signature);
      return;
    }
    if (payload.started) ensureCard(payload);
    refreshQueueCount();
  });

  /* Engine-Neustart: Geister-Panels aufräumen (In-Memory-Queue endet mit
     dem Prozess); Boot-Erkennung liefert das server.restarted-Event. */
  eventBus.addEventListener("server.restarted", () => {
    for (const entry of cards.values()) entry.card.remove();
    cards.clear();
    stage.querySelector(".restart-hint")?.remove();
    const hint = document.createElement("p");
    hint.className = "hint restart-hint";
    hint.textContent =
      "Die Engine wurde neu gestartet — laufende Broadcasts wurden dabei beendet. Bitte neu starten.";
    stage.prepend(hint);
    refreshQueueCount();
  });

  eventBus.addEventListener("broadcast.resonance", (event) => {
    const payload = event.detail;
    const entry = cards.get(payload.signature);
    if (entry) {
      entry.wave = 1;
      if (reducedMotion) paintCaption(entry, payload.signature, 0);
    }
    if (binauralToggle.checked && payload.binaural) {
      playBinaural(payload.binaural);
    }
    const item = document.createElement("li");
    const name = document.createElement("span");
    name.textContent = payload.signature;
    const meta = document.createElement("span");
    meta.textContent = `#${payload.resonanceCount} · binaural ${payload.binaural.left_freq}/${payload.binaural.right_freq} Hz`;
    item.append(name, meta);
    resonanceList.prepend(item);
    while (resonanceList.children.length > 25) resonanceList.lastChild.remove();
  });

  async function refreshQueueCount() {
    try {
      const state = await api.queue();
      queueCount.textContent = state.queued.length + state.active.length;
    } catch (_) { /* offline */ }
  }
  refreshQueueCount();
  setInterval(refreshQueueCount, 5000);
}

/* ---- LED-Choreografie (emitter.sequence) ---- */
export function renderEmitterSequence(payload) {
  const strip = document.getElementById("led-strip");
  strip.innerHTML = "";
  const title = document.createElement("p");
  title.className = "hint";
  title.textContent = `Signatur „${payload.signature}“ · ${payload.steps.length} Schritte · delay ${payload.delayMs} ms · repeat ${payload.repeat}` +
    (payload.clear ? " · CLEAR-MODUS (UV via 1/6)" : "");
  strip.appendChild(title);
  for (const step of payload.steps.slice(0, 40)) {
    const chip = document.createElement("span");
    chip.className = "led-step";
    const char = document.createElement("strong");
    char.textContent = step.char === " " ? "␣" : step.char;
    chip.appendChild(char);
    step.digitSequence.forEach((digit, index) => {
      const groups = step.litGroups[index] || [];
      if (groups.length === 0) {
        const dot = document.createElement("span");
        dot.className = "led-dot";
        dot.title = `Ziffer ${digit}: aus`;
        chip.appendChild(dot);
        return;
      }
      for (const group of groups) {
        const dot = document.createElement("span");
        dot.className = `led-dot ${GROUP_CLASS[group] || ""}`;
        dot.title = `Ziffer ${digit} → ${GROUP_LABEL[group] || group}`;
        chip.appendChild(dot);
      }
    });
    strip.appendChild(chip);
  }
}

/* ---- Zeichen-Primitives (Original-Panels, visuelle Ebene) ---- */
function paintSignature(ctx, rng, text) {
  ctx.fillStyle = `hsla(${rng.nextInt(360)}, 40%, 78%, 0.6)`;
  ctx.font = "16px serif";
  ctx.fillText(text.slice(0, 18), rng.nextInt(300) + 10, rng.nextInt(160) + 16);
}
function paintOverlay(ctx, rng, alpha) {
  ctx.fillStyle = `hsla(${rng.nextInt(360)}, 35%, 60%, ${alpha / 100})`;
  ctx.fillRect(0, 0, 320, 180);
}
function paintShape(ctx, rng, kind) {
  const x = rng.nextInt(320), y = rng.nextInt(180);
  const size = rng.nextInt(60) + 12;
  ctx.strokeStyle = `hsla(${rng.nextInt(360)}, 45%, 70%, 0.7)`;
  ctx.beginPath();
  if (kind === "rect") ctx.rect(x, y, size, size * 0.7);
  else if (kind === "ellipse") ctx.ellipse(x, y, size, size * 0.6, 0, 0, Math.PI * 2);
  else if (kind === "line") { ctx.moveTo(x, y); ctx.lineTo(x + size, y + size / 2); }
  else { ctx.moveTo(x, y); ctx.lineTo(x + size, y); ctx.lineTo(x + size / 2, y + size); ctx.closePath(); }
  ctx.stroke();
}
function paintWave(ctx, amount) {
  ctx.strokeStyle = "rgba(255,255,255,0.5)";
  ctx.beginPath();
  ctx.ellipse(160, 90, 88 - (amount % 88), 88 - (amount % 88), 0, 0, Math.PI * 2);
  ctx.stroke();
  ctx.beginPath();
  ctx.ellipse(160, 90, 88 + (amount % 88), 88 + (amount % 88), 0, 0, Math.PI * 2);
  ctx.stroke();
}

/* deterministischer Zufall je Signatur (visuelle Reproduzierbarkeit) */
function hash(text) {
  let h = 2166136261;
  for (const c of text) { h ^= c.codePointAt(0); h = Math.imul(h, 16777619); }
  return h >>> 0;
}
function mulberry32(seed) {
  let a = seed;
  return {
    nextInt(bound) {
      a |= 0; a = (a + 0x6D2B79F5) | 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) % bound;
    },
  };
}

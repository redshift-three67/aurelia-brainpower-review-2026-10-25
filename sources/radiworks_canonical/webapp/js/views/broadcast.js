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
  const stopCurrentBtn = document.getElementById("stop-current-btn");
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

  stopCurrentBtn.addEventListener("click", async () => {
    try {
      await api.stopCurrent();
      await refreshQueueState();
    } catch (error) {
      alert(`Aktueller Broadcast konnte nicht gestoppt werden: ${error.message}`);
    }
  });

  stopAllBtn.addEventListener("click", async () => {
    try {
      await api.stopAll();
      await refreshQueueState();
    } catch (error) {
      alert(`Broadcasts konnten nicht gestoppt werden: ${error.message}`);
    }
  });

  /* ---- Elemente je Broadcast (320×180 wie im Original) ---- */
  const cards = new Map(); // broadcastId → Card-Entry inkl. RAF/Removal-Timer
  let queueRevision = 0;
  let queueRequest = 0;

  function broadcastKey(payload) {
    return payload.broadcastId || payload.signature;
  }

  function disposeCard(key, entry = cards.get(key)) {
    if (!entry) return;
    if (entry.rafId !== null) cancelAnimationFrame(entry.rafId);
    if (entry.removalTimer !== null) clearTimeout(entry.removalTimer);
    entry.rafId = null;
    entry.removalTimer = null;
    entry.card.remove();
    if (cards.get(key) === entry) cards.delete(key);
  }

  function syncCardProgress(entry, payload) {
    if (Number.isFinite(payload.seconds) && payload.seconds > 0) {
      entry.seconds = payload.seconds;
    }
    if (Number.isFinite(payload.progress)) {
      const progress = Math.max(0, Math.min(1, payload.progress));
      entry.started = performance.now() - progress * entry.seconds * 1000;
      entry.fill.style.width = `${progress * 100}%`;
      paintCaption(entry, progress);
    }
  }

  function ensureCard(payload) {
    const key = broadcastKey(payload);
    if (!key) return null;
    const existing = cards.get(key);
    if (existing) {
      syncCardProgress(existing, payload);
      return existing;
    }
    stage.querySelector(".restart-hint")?.remove();
    const signature = payload.signature || "Broadcast";
    const card = document.createElement("div");
    card.className = "broadcast-card";
    const canvas = document.createElement("canvas");
    canvas.width = 320;
    canvas.height = 180;
    canvas.setAttribute("role", "img");
    canvas.setAttribute("aria-label", `Broadcast-Panel ${signature}`);
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
      key, signature, card, canvas, fill,
      ctx: canvas.getContext("2d"),
      rng: mulberry32(hash(`${signature}:${key}`)),
      seconds: payload.seconds ?? 60,
      started: performance.now(),
      wave: 0,
      captionText: caption,
      rafId: null,
      removalTimer: null,
    };
    cards.set(key, entry);
    syncCardProgress(entry, payload);
    paintCaption(entry, payload.progress ?? 0);
    if (!reducedMotion) tick(entry);
    else paintStatic(entry);
    return entry;
  }

  function paintCaption(entry, progress) {
    entry.captionText.innerHTML = "";
    const name = document.createElement("span");
    name.textContent = entry.signature;
    const status = document.createElement("span");
    status.textContent = reducedMotion
      ? `statisch · ${(progress * 100) | 0} % (Bewegung reduziert)`
      : `Resonanz: ${entry.wave}`;
    entry.captionText.append(name, status);
  }

  /* Original draw()-Schwellen — visuelle Ebene, fachlich folgen Resonanzen
     ausschließlich den Server-Events (Server ist die Uhr). */
  function tick(entry) {
    if (cards.get(entry.key) !== entry) return;
    const r = entry.rng;
    const ctx = entry.ctx;
    if (r.nextInt(13) >= 12) paintSignature(ctx, r, entry.signature);
    else if (r.nextInt(21) >= 20) paintOverlay(ctx, r, 5);
    else if (r.nextInt(33) >= 32) { paintOverlay(ctx, r, 8); paintSignature(ctx, r, entry.signature); }
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
    paintCaption(entry, progressValue);
    if (progressValue < 1) {
      entry.rafId = requestAnimationFrame(() => {
        entry.rafId = null;
        tick(entry);
      });
    } else {
      entry.removalTimer = setTimeout(() => disposeCard(entry.key, entry), 4000);
    }
  }

  function paintStatic(entry) {
    const ctx = entry.ctx;
    paintOverlay(ctx, entry.rng, 30);
    paintSignature(ctx, entry.rng, entry.signature);
  }

  eventBus.addEventListener("broadcast.progress", (event) => {
    const payload = event.detail;
    const key = broadcastKey(payload);
    if (payload.finished || payload.stopped) {
      queueRevision += 1;
      disposeCard(key);
      refreshQueueState();
      return;
    }
    if (payload.started) {
      queueRevision += 1;
      ensureCard(payload);
      refreshQueueState();
    } else if (cards.has(key)) {
      ensureCard(payload);
    }
  });

  /* Engine-Neustart: Geister-Panels samt Animationen aufräumen (In-Memory-
     Queue endet mit dem Prozess); Boot-Erkennung liefert server.restarted. */
  eventBus.addEventListener("server.restarted", () => {
    queueRevision += 1;
    for (const [key, entry] of cards) disposeCard(key, entry);
    stage.querySelector(".restart-hint")?.remove();
    const hint = document.createElement("p");
    hint.className = "hint restart-hint";
    hint.textContent =
      "Die Engine wurde neu gestartet — laufende Broadcasts wurden dabei beendet. Bitte neu starten.";
    stage.prepend(hint);
    refreshQueueState();
  });

  eventBus.addEventListener("server.replay_gap", () => {
    queueRevision += 1;
    refreshQueueState();
  });

  eventBus.addEventListener("broadcast.resonance", (event) => {
    const payload = event.detail;
    const entry = cards.get(broadcastKey(payload));
    if (entry) {
      entry.wave = 1;
      if (reducedMotion) paintCaption(entry, payload.progress ?? 0);
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

  async function refreshQueueState() {
    const request = ++queueRequest;
    const revision = queueRevision;
    try {
      const state = await api.queue();
      if (request !== queueRequest || revision !== queueRevision) return;
      queueCount.textContent = state.queued.length + state.active.length;
      const activeKeys = new Set();
      for (const active of state.active) {
        const key = broadcastKey(active);
        if (!key) continue;
        activeKeys.add(key);
        ensureCard(active);
      }
      for (const [key, entry] of cards) {
        if (!activeKeys.has(key)) disposeCard(key, entry);
      }
    } catch (_) { /* offline */ }
  }
  refreshQueueState();
  setInterval(() => { if (!document.hidden) refreshQueueState(); }, 5000);
  document.addEventListener("visibilitychange", () => { if (!document.hidden) refreshQueueState(); });
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

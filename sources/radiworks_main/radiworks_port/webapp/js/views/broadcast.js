import {describeAudioAssignment, audioProfileLabel} from '../broadcast-audio-assignment.js';
import { BroadcastAudioPlayer } from "../broadcast-audio-player.js";
import { isPulseProfile } from "../pink-pulse-profile.js";
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
  const dockStopAllBtn = document.getElementById("dock-stop-all-btn");
  const clearResonanceDisplayBtn = document.getElementById("clear-resonance-display-btn");
  const controlsStatus = document.getElementById("broadcast-controls-status");
  const resonanceStatus = document.getElementById("broadcast-resonance-status");
  const stage = document.getElementById("broadcast-stage");
  const queueCount = document.getElementById("queue-count");
  const resonanceList = document.getElementById("resonance-list");
  const binauralToggle = document.getElementById("binaural-toggle");

  /* Binaural-Sound (BroadcastElement.playBinauralSound): WebAudio, 3 s,
     L/R-Frequenzen aus dem Resonanz-Event; Zustand in Settings. */
  const audioStatus=document.getElementById('broadcast-audio-status');
  const audioEnable=document.getElementById('broadcast-audio-enable');
  const audioStop=document.getElementById('broadcast-audio-stop');
  const audioLevel=document.getElementById('broadcast-audio-level');
  const audioTest=document.getElementById('broadcast-audio-test');
  const audioAssignment=document.getElementById('broadcast-audio-assignment');
  const audio=new BroadcastAudioPlayer({onStatus:text=>{audioStatus.textContent=text;}});
  const stopAudio=()=>audio.stopAll().catch(error=>{audioStatus.textContent=`Audio-Stopp nicht bestätigt: ${error.message}`;});
  api.settings().then(settings=>{binauralToggle.checked=settings.booleans?.['play.binaural.sound']===true;updateAudioAssignment();})
    .catch(()=>{binauralToggle.checked=false;audioStatus.textContent='Original-Toneinstellung nicht geladen. Audio bleibt aus.';});
  window.addEventListener('radiworks:settings-saved',event=>{const enabled=event.detail?.booleans?.['play.binaural.sound'];if(typeof enabled==='boolean'){binauralToggle.checked=enabled;updateAudioAssignment();}});
  binauralToggle.addEventListener('change',()=>{updateAudioAssignment();api.updateSettings({booleans:{'play.binaural.sound':binauralToggle.checked}}).catch(error=>{audioStatus.textContent=`Toneinstellung nicht gespeichert: ${error.message}`;});});
  audioEnable.addEventListener('click',async()=>{audioEnable.disabled=true;try{await audio.activate();for(const entry of cards.values())startCardAudio(entry);updateAudioAssignment();}catch(error){audioStatus.textContent=`Audio nicht aktiviert: ${error.message}`;}finally{audioEnable.disabled=false;}});
  audioStop.addEventListener('click',()=>{void stopAudio();});
  audioTest.addEventListener('click',async()=>{audioTest.disabled=true;try{await audio.activate();audio.playTestTone();}catch(error){audioStatus.textContent=`Testton nicht gestartet: ${error.message}`;}finally{audioTest.disabled=false;}});
  audioLevel.addEventListener('input',()=>{try{audio.setLevel(Number(audioLevel.value)/100);}catch(error){audioStatus.textContent=error.message;}});
  eventBus.addEventListener('connection.state',event=>{if(event.detail.state!=='online')void stopAudio();});
  window.addEventListener('pagehide',()=>{void stopAudio();});
  window.addEventListener('offline',()=>{void stopAudio();});
  document.addEventListener('visibilitychange',()=>{if(document.hidden)void stopAudio();});
  function startCardAudio(entry){
    const p=entry.presentation?.profile;
    if(!audio.enabled||!p||['original','off'].includes(p.audioProfile))return;
    if(p.audioProfile==='pink'||isPulseProfile(p.audioProfile)){try{audio.startPink(entry.key,p,entry.seconds,Math.max(0,(performance.now()-entry.started)/1000),`rw-pink-v1:${entry.key}:${entry.presentation.digest}`);}catch(error){audioStatus.textContent=error.message;}return;}
    try{audio.startProfile(entry.key,{id:p.audioProfile,stageSeconds:p.stageSeconds,repeat:p.repeat},entry.seconds,Math.max(0,(performance.now()-entry.started)/1000));}
    catch(error){audioStatus.textContent=`Audioprofil nicht gestartet: ${error.message}`;}
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

  const stopAllButtons = [stopAllBtn, dockStopAllBtn].filter(Boolean);
  let stopAllBusy = false;

  function publishControlsStatus(text, error = false, kind = "stop-all") {
    eventBus.dispatchEvent(new CustomEvent("broadcast.controls.status", { detail: { text, error, kind } }));
  }

  function showControlsStatus(detail = {}) {
    const status = detail.kind === "resonance-display" ? resonanceStatus : controlsStatus;
    status.textContent = detail.text || "";
    status.hidden = !detail.text;
  }
  eventBus.addEventListener("broadcast.controls.status", (event) => showControlsStatus(event.detail));

  stopAllBtn.addEventListener("click", () => {
    eventBus.dispatchEvent(new CustomEvent("broadcast.stop-all.request", { detail: { source: "broadcast" } }));
  });
  clearResonanceDisplayBtn.addEventListener("click", () => {
    eventBus.dispatchEvent(new CustomEvent("broadcast.resonance-display.clear", { detail: { source: "broadcast" } }));
  });
  eventBus.addEventListener("broadcast.stop-all.request", async () => {
    if (stopAllBusy) return;
    stopAllBusy = true;
    stopAllButtons.forEach((button) => { button.disabled = true; });
    publishControlsStatus("Stoppe alle aktiven und wartenden Broadcasts dieser Instanz …");
    try {
      await api.stopAll();
      await refreshQueueState();
      publishControlsStatus("Alle aktiven und wartenden Broadcasts dieser Instanz wurden gestoppt. Auftragsbelege bleiben erhalten. Auto bleibt unverändert; bei aktivem Auto können neue Broadcasts entstehen.");
    } catch (error) {
      const reason = error?.message ? ` ${error.message}` : "";
      publishControlsStatus(`Broadcasts dieser Instanz konnten nicht geleert werden.${reason}`, true);
    } finally {
      stopAllBusy = false;
      stopAllButtons.forEach((button) => { button.disabled = false; });
    }
  });
  eventBus.addEventListener("broadcast.resonance-display.clear", () => {
    resonanceList.innerHTML = '<li class="hint">Noch keine Resonanz.</li>';
    publishControlsStatus("Resonanzanzeige browserlokal zurückgesetzt. Neue Resonanzen können wieder erscheinen; die GV-Sitzungshistorie bleibt erhalten.", false, "resonance-display");
  });
  /* ---- Elemente je Broadcast (320×180 wie im Original) ---- */
  const cards = new Map(); // broadcastId → Card-Entry inkl. RAF/Removal-Timer
  function updateAudioAssignment(){
    const rows=[...cards.values()].map(entry=>({seconds:entry.seconds,elapsed:Math.max(0,(performance.now()-entry.started)/1000),profile:entry.presentation?.profile}));
    const text=describeAudioAssignment(rows,binauralToggle.checked,audio.sampleRate??48000);
    if(audioAssignment.textContent!==text)audioAssignment.textContent=text;
  }
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
    audio.stopJob(key);
    entry.images?.forEach(image=>{image.onload=null;image.onerror=null;image.removeAttribute("src");});
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
      presentation: payload.presentation || null,
      images: [],
      lastImagePaint: -Infinity,
    };
    cards.set(key, entry);
    loadCardImages(entry);
    syncCardProgress(entry, payload);
    paintCaption(entry, payload.progress ?? 0);
    startCardAudio(entry);
    if (!reducedMotion) tick(entry);
    else paintStatic(entry);
    return entry;
  }

  function loadCardImages(entry){
    const hashes=entry.presentation?.profile?.images||[];
    if(!Array.isArray(hashes)||hashes.length>5||hashes.some(h=>!(/^[0-9a-f]{64}$/).test(h))){audioStatus.textContent='Bildprofil ungültig; Originaldarstellung bleibt erhalten.';return;}
    for(const sha of hashes){const image=new Image();entry.images.push(image);
      image.onload=()=>{if(cards.get(entry.key)!==entry)return;if(image.naturalWidth>1024||image.naturalHeight>1024){image.removeAttribute('src');return;}if(reducedMotion)paintStatic(entry);};
      image.onerror=()=>{if(cards.get(entry.key)===entry)entry.captionText.textContent='Animationsbild nicht verfügbar; Originaldarstellung bleibt erhalten.';};
      image.src=api.presentationImageUrl(sha);
    }
  }
  function paintCardImages(entry){
    const images=entry.images.filter(i=>i.complete&&i.naturalWidth>0&&i.naturalHeight>0);if(!images.length)return;
    const ctx=entry.ctx;ctx.save();ctx.globalAlpha=1/images.length;
    for(const img of images){const scale=Math.min(320/img.naturalWidth,180/img.naturalHeight),w=img.naturalWidth*scale,h=img.naturalHeight*scale;ctx.drawImage(img,(320-w)/2,(180-h)/2,w,h);}ctx.restore();
  }
  function paintCaption(entry, progress) {
    entry.captionText.innerHTML = "";
    const name = document.createElement("span");
    name.textContent = entry.signature;
    const status = document.createElement("span");
    status.textContent = reducedMotion
      ? `statisch · ${(progress * 100) | 0} % (Bewegung reduziert)`
      : `Resonanz: ${entry.wave}`;
    status.textContent+=` · Audio: ${audioProfileLabel(entry.presentation?.profile?.audioProfile??'original')}`;
    entry.captionText.append(name, status);
  }

  /* Original draw()-Schwellen — visuelle Ebene, fachlich folgen Resonanzen
     ausschließlich den Server-Events (Server ist die Uhr). */
  function tick(entry) {
    if (cards.get(entry.key) !== entry) return;
    const r = entry.rng;
    const ctx = entry.ctx;
    if(performance.now()-entry.lastImagePaint>500){paintCardImages(entry);entry.lastImagePaint=performance.now();}
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
    paintCardImages(entry);
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
    void stopAudio();
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
    void stopAudio();
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
    if (entry && (!entry.presentation || entry.presentation.profile.audioProfile==='original') && binauralToggle.checked && payload.binaural) {
      try{audio.playOriginal(entry.key,payload.binaural);}catch(error){audioStatus.textContent=`Ereigniston nicht abgespielt: ${error.message}`;}
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
      updateAudioAssignment();
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

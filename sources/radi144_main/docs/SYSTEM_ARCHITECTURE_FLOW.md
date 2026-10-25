# System-Architektur & Flow-Diagramme – v1.5.0

**Stand:** 04. Juni 2026  
**Notation:** Mermaid-kompatible ASCII-Diagramme

Verifizierter Nachtrag 2026-06-04:

- Die Verwaltungsdomäne unter `data/runtime/` ist jetzt real angeschlossen (`clients.json`, `sessions.json`, `artifacts.json`).
- API und CLI spiegeln Analysen in dieselben Metadatenservices.
- `POST /api/v1/analyze-matrix` gibt die Verwaltungs-IDs jetzt auch über `X-Client-ID` und `X-Session-ID` zurück; `POST /api/v1/export/pdf` liefert bei registriertem Artefakt `X-Artifact-ID`.
- Der CPU-Pfad der Engine besitzt jetzt einen defensiven RAM-Guard vor der Kandidatensuche.

Verifizierter Nachtrag 2026-06-08:

- `generate_matrix.ps1` konsumiert die Verwaltungsdomäne jetzt adapterartig fuer die Template-Historie.
- Aus `data/runtime/sessions.json` und `data/runtime/clients.json` wird `data/runtime/powershell_templates.json` als legacy-kompatible PowerShell-Leseansicht erzeugt.
- `data/session_templates.json` bleibt als Fallback erhalten.
- Details: `docs/PHASE4_POWERSHELL_METADATA_STATUS_2026-06-08.md`.

---

## 1. Gesamt-System-Architektur

```
╔══════════════════════════════════════════════════════════════════════════╗
║                    12x12 RESONANCE MATRIX ENGINE v1.5.0                ║
║                EMF Compensation & Environmental Intelligence           ║
╠══════════════════════════════════════════════════════════════════════════╣
║                                                                        ║
║  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐  ║
║  │   EINGABE    │  │   ENGINE     │  │  KOMPENSATION│  │  AUSGABE   │  ║
║  │              │  │              │  │              │  │            │  ║
║  │ • Klient     │─→│ • Signatur   │←→│ • EMF Comp.  │─→│ • Matrix   │  ║
║  │ • Fokus      │  │ • Matrix     │  │ • Amplifier  │  │ • PDF/XLSX │  ║
║  │ • Preset     │  │ • Resonanz   │  │ • HRV Sim    │  │ • Audio    │  ║
║  │ • Amplifier  │  │ • CUDA/CPU   │  │ • Geo/Group  │  │ • Harmoni. │  ║
║  └──────────────┘  └──────────────┘  └──────────────┘  └────────────┘  ║
║                                                                        ║
║  ┌──────────────────────────────────────────────────────────────────┐   ║
║  │                        API LAYER (FastAPI)                       │   ║
║  │  REST: /analyze-matrix  /emf/*  /amplifier/*                    │   ║
║  │  WS:   /emf/ws  /emf/client-sensor                             │   ║
║  └──────────────────────────────────────────────────────────────────┘   ║
║                                                                        ║
║  ┌──────────────────────────────────────────────────────────────────┐   ║
║  │                  VERWALTUNGSDOMÄNE / RUNTIME                     │   ║
║  │  Client Registry  •  Session Archive  •  Report Manifest         │   ║
║  │  clients.json  sessions.json  artifacts.json                     │   ║
║  │  powershell_templates.json = generierte PS1-Leseansicht          │   ║
║  └──────────────────────────────────────────────────────────────────┘   ║
║                                                                        ║
║  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────────┐  ║
║  │  CLI (Python) │  │  PS1 (UI)   │  │  Web Monitor (HTML/JS)      │  ║
║  │  dev_cli.py   │  │  generate_  │  │  /emf/monitor               │  ║
║  │               │  │  matrix.ps1 │  │  Auto-Reconnect WebSocket   │  ║
║  └──────────────┘  └──────────────┘  └──────────────────────────────┘  ║
╚══════════════════════════════════════════════════════════════════════════╝
```

---

## 2. Analyse-Flow (Hauptprozess)

```
START
  │
  ▼
┌─────────────────────────┐
│ 1. EINGABE VALIDIEREN   │
│    Name, DOB, Ort,      │
│    Fokus, Gewichtung    │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐     ┌──────────────────────┐
│ 2. ENGINE INIT          │     │ EMF aktiv?           │
│    Hardware-Erkennung   │────→│                      │
│    CUDA/CPU/MPS         │     │ JA → Kalibrierung    │
│    Kandidaten-Pool      │     │      Profiling       │
│    setzen               │     │      Kompensation    │
└────────┬────────────────┘     └──────────┬───────────┘
         │                                 │
         ▼                                 ▼
┌─────────────────────────┐     ┌──────────────────────┐
│ 3. CLIENT SIGNATUR      │     │ EMF-Korrektur als    │
│    6 Komponenten        │←────│ 6. Komponente        │
│    → Frequenz (Hz)      │     │ (Schumann-basiert)   │
└────────┬────────────────┘     └──────────────────────┘
         │
         ▼
┌─────────────────────────┐     ┌──────────────────────┐
│ 4. AMPLIFIER SETZEN     │     │ Amplifier aktiv?     │
│    (optional)           │────→│                      │
│    --amplifier "name"   │     │ JA → Palette modul.  │
│                         │     │      Audio-Freqs     │
└────────┬────────────────┘     └──────────┬───────────┘
         │                                 │
         ▼                                 │
┌─────────────────────────┐                │
│ 5. FOKUS-VEKTOR         │                │
│    Semantische          │                │
│    Einbettung           │                │
│    + Bio-Vektor (opt.)  │                │
└────────┬────────────────┘                │
         │                                 │
         ▼                                 │
┌─────────────────────────┐                │
│ 6. EMF-KOMPENSATION     │                │
│    auf Vektoren          │                │
│    client_vec ×= comp.  │                │
│    focus_vec ×= comp.   │                │
└────────┬────────────────┘                │
         │                                 │
         ▼                                 │
┌─────────────────────────┐                │
│ 7. MATRIX-SUCHE         │                │
│    N Kandidaten         │                │
│    GPU: VRAM-Guard      │                │
│    CPU: RAM-Guard       │                │
│    Cosinus-Ähnlichkeit  │                │
│    Gewichtung           │                │
│    → Top-10 sortiert    │                │
└────────┬────────────────┘                │
         │                                 │
         ▼                                 │
┌─────────────────────────┐                │
│ 8. AMPLIFIER-MATCHING   │←───────────────┘
│    Client ↔ 12 Amplifier│
│    Top-3 Empfehlung     │
│    + Begründungen       │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ 9. AUSGABE              │
│    • 12x12 Matrix       │
│    • Score + Intensity  │
│    • Palette (moduliert)│
│    • Amplifier-Info     │
│    • EMF-Daten          │
│    • PDF / Excel        │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ 10. HARMONISIERUNG?     │
│     --harmonize         │
│                         │
│     JA → Tkinter Window │
│          Matrix-Anzeige │
│          Audio-Engine   │
│          + EMF-Counter  │
│          + Amplifier-Hz │
└─────────────────────────┘
  │
  ▼
ENDE
```

---

## 3. EMF Compensator Flow

```
┌───────────────────────────────────────────────────────────┐
│                   EMF COMPENSATOR                        │
├───────────────────────────────────────────────────────────┤
│                                                          │
│  LAYER 1: SENSING                                        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │CPU Timing│ │RNG       │ │GPU Noise │ │System    │   │
│  │Jitter    │ │Entropy   │ │(Basic/   │ │Load      │   │
│  │          │ │Quality   │ │Server)   │ │(psutil)  │   │
│  │50 Zyklen │ │Shannon   │ │          │ │CPU + RAM │   │
│  │perf_cnt  │ │Chi²      │ │Dev:256²  │ │          │   │
│  │→ std(ms) │ │Autocorr  │ │Srv:1024² │ │          │   │
│  │          │ │→ Score   │ │+FFT+Drift│ │          │   │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘   │
│       │            │            │             │          │
│       ▼            ▼            ▼             ▼          │
│  LAYER 2: PROFILING                                      │
│  ┌──────────────────────────────────────────────────┐    │
│  │ Composite EMF Index =                             │    │
│  │   0.35 × entropy_deviation                        │    │
│  │ + 0.30 × jitter_deviation                         │    │
│  │ + 0.20 × gpu_noise                                │    │
│  │ + 0.15 × system_load                              │    │
│  │                                                    │    │
│  │ Low-Noise Window: Index < 0.3                      │    │
│  └───────────────────────┬──────────────────────────┘    │
│                          │                               │
│                          ▼                               │
│  LAYER 3: COMPENSATION                                   │
│  ┌──────────────────────────────────────────────────┐    │
│  │ Kompensationsvektor (12D):                        │    │
│  │   Schumann-Harmonische × EMF-Index               │    │
│  │                                                    │    │
│  │ Counter-Frequencies:                               │    │
│  │   Top-3 Solfeggio (gewichtet nach Profil)         │    │
│  │                                                    │    │
│  │ Timing-Empfehlung:                                │    │
│  │   < 0.3 → "proceed" (grün)                       │    │
│  │   0.3-0.7 → "proceed_with_compensation" (gelb)   │    │
│  │   > 0.7 → "delay_recommended" (rot)              │    │
│  └──────────────────────────────────────────────────┘    │
│                                                          │
│  LAYER 4: MONITORING (optional)                          │
│  ┌──────────────────────────────────────────────────┐    │
│  │ Background Thread (alle 30 Sek)                   │    │
│  │ → Profiling → History (deque, maxlen=100)         │    │
│  │ → WebSocket Push (/emf/ws, alle 5 Sek)           │    │
│  └──────────────────────────────────────────────────┘    │
└───────────────────────────────────────────────────────────┘
```

---

## 4. Amplifier-Matching Flow

```
┌────────────────────┐        ┌────────────────────┐
│  CLIENT SIGNATUR   │        │  AMPLIFIER REGISTRY │
│                    │        │  (12 Einträge)      │
│  frequency: 440 Hz │        │                    │
│  components: {...} │        │  rosenquarz: 350 Hz│
│  focus: "Heilung"  │        │  amethyst: 480 Hz  │
│  bio_info: {...}   │        │  bergkristall: 528 │
│                    │        │  ...                │
└────────┬───────────┘        └────────┬───────────┘
         │                             │
         ▼                             ▼
┌─────────────────────┐     ┌─────────────────────┐
│ Projektion in 12D   │     │ Vektor-Berechnung   │
│ Amplifier-Space     │     │ pro Amplifier (12D)  │
│                     │     │                     │
│ [0-3] Freq+Harm.    │     │ [0-3] Freq+Harm.    │
│ [4]   Element       │     │ [4]   Element        │
│ [5]   Chakra/Bio    │     │ [5]   Chakra         │
│ [6]   Stärke        │     │ [6]   Amp.Faktor     │
│ [7]   Solfeggio     │     │ [7]   Solfeggio      │
│ [8-9] Fokus-Farbe   │     │ [8-9] Mineral-Farbe  │
│ [10]  Tageszeit     │     │ [10]  Kristallsystem  │
│ [11]  EMF-Korr.     │     │ [11]  Bild-Hash      │
└────────┬────────────┘     └────────┬────────────┘
         │                           │
         └──────────┬────────────────┘
                    │
                    ▼
         ┌──────────────────────┐
         │  SCORING (pro Amp.)  │
         │                      │
         │  55% Cosinus-Ähnl.   │
         │  20% Element-Synergie│
         │  25% Property-Match  │
         │                      │
         │  Element-Zyklus:     │
         │  Holz→Feuer→Erde    │
         │  →Metall→Wasser     │
         │  →Holz              │
         └──────────┬───────────┘
                    │
                    ▼
         ┌──────────────────────┐
         │  TOP-3 EMPFEHLUNG   │
         │                      │
         │  1. Bergkristall 87% │
         │     → Hohe Resonanz  │
         │     → Universell     │
         │                      │
         │  2. Rosenquarz  74%  │
         │     → Element-Syn.   │
         │     → Herz-Chakra    │
         │                      │
         │  3. Amethyst    68%  │
         │     → Fokus-Match    │
         │     → Intuition      │
         └──────────────────────┘
```

---

## 5. Harmonisierungs-Flow

```
┌──────────────────────────────────────────────────────────┐
│               HARMONISIERUNG (Tkinter Window)            │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Eingabe: Top-3 Matrizen + Palette + Amplifier          │
│                                                          │
│  ┌─────────────────────────────────────────────────┐     │
│  │              AUDIO ENGINE                        │     │
│  │                                                  │     │
│  │  Layer 1: Client-Frequenz (f₁)     × 1.00       │     │
│  │  Layer 2: Quinte (f₁ × 1.5)       × 0.10       │     │
│  │  Layer 3: Solfeggio (528 Hz)       × 0.05       │     │
│  │  Layer 4: Sub-Oktave (f₁ / 2)     × 0.15       │     │
│  │  Layer 5: EMF Counter-Freq [×3]   × 0.03       │     │
│  │  Layer 6: Amplifier-Freq [×4]     × 0.08       │     │
│  │                                                  │     │
│  │  Fade-In: 500ms │ Fade-Out: 500ms               │     │
│  │  Format: 44.1 kHz, 16-bit PCM, Mono             │     │
│  └─────────────────────────────────────────────────┘     │
│                                                          │
│  ┌─────────────────────────────────────────────────┐     │
│  │              VISUAL ENGINE                       │     │
│  │                                                  │     │
│  │  12×12 Grid auf Canvas (375×375 px)              │     │
│  │  Farben: Palette (Amplifier-moduliert)            │     │
│  │  Zahlen: Kontrast-optimiert (Luminanz-basiert)    │     │
│  │  Hintergrund: Kohärenter Durchschnitt (12%)       │     │
│  └─────────────────────────────────────────────────┘     │
│                                                          │
│  ZYKLUS:                                                 │
│  ┌────────┐    ┌────────┐    ┌────────┐                  │
│  │Matrix 1│───→│ PAUSE  │───→│Matrix 2│───→ ...          │
│  │21 Sek  │    │14 Sek  │    │21 Sek  │                  │
│  │+ Audio │    │Blank   │    │+ Audio │                  │
│  └────────┘    └────────┘    └────────┘                  │
│                                                          │
│  Dauer: duration_factor × 21 Minuten                     │
│  Export: session_audio_lossless.wav (bei Audio)          │
│  Beenden: ESC-Taste                                      │
└──────────────────────────────────────────────────────────┘
```

---

## 6. Deployment-Flow (Linux Server)

```
┌──────────────────────────────────────────────┐
│         setup_server.sh                       │
├──────────────────────────────────────────────┤
│                                              │
│  [1/7] System Dependencies                   │
│    apt install python3.11, nvidia-driver-535 │
│    nvidia-cuda-toolkit                       │
│                                              │
│  [2/7] User & Directories                    │
│    useradd resonance                         │
│    /opt/resonance-engine/                    │
│    /var/log/resonance-engine/                │
│                                              │
│  [3/7] Deploy Application                    │
│    rsync (excl. RestorePoints, __pycache__) │
│                                              │
│  [4/7] Python venv + Dependencies            │
│    PyTorch + cu121                           │
│    requirements.txt                          │
│                                              │
│  [5/7] CUDA Verification                     │
│    torch.cuda.is_available()                 │
│    GPU Name + VRAM                           │
│                                              │
│  [6/7] systemd Service                       │
│    resonance-engine.service                  │
│    enable + daemon-reload                    │
│                                              │
│  [7/7] EMF Validation                        │
│    profile_environment()                     │
│    get_timing_recommendation()               │
│                                              │
│  → systemctl start resonance-engine          │
│  → http://SERVER:8000/docs                   │
│  → http://SERVER:8000/api/v1/emf/monitor     │
└──────────────────────────────────────────────┘
```

---

## 7. Datenfluss-Übersicht (End-to-End)

```
KLIENT                    SERVER/ENGINE                      AUSGABE
──────                    ─────────────                      ───────

Name ──────┐
DOB ───────┤
Ort ───────┤
           ├──→ ClientSignatureGenerator ──→ Frequency (Hz)
Planet ────┤         │                           │
Bild ──────┘         │ EMF-Korrektur             │
                     │ (Schumann)                │
                     ▼                           │
              ┌──────────────┐                   │
Fokus ───────→│ ResonanceMatrix│                  │
Gewicht. ────→│ Engine         │                  │
Modus ───────→│                │                  │
              │ CUDA/CPU       │                  │
              │ N Kandidaten   │                  │
              │ Cosinus-Match  │──→ 12×12 Matrix ──→ PDF
              │                │──→ Score ──────────→ Excel
              └──────┬─────────┘──→ Top-10 ────────→ CLI Output
                     │
EMF On? ────→ EMFCompensator                     
              │ Profiling                         
              │ Kompensation ──→ Counter-Freq ───→ Audio Layer
              │                                   
Amplifier ──→ AmplifierVector                    
              │ Matching ──────→ Top-3 Empf. ────→ CLI Output
              │ Palette Mod. ──→ Farb-Shift ─────→ Visual
              │ Audio Freq. ───→ Amp. Layer ─────→ Audio Layer
              │                                   
Harmonize? ──→ HarmonizerWindow                  
              │ Visual: Matrix + Palette          
              │ Audio: Client + Solf + EMF + Amp  
              │ Zyklus: Impuls/Pause              
              └──→ session_audio_lossless.wav     
```

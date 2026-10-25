# ARCHIVHINWEIS: Archivierte Legacy-Systembeschreibung

Dieses Dokument ist ein historisches Referenz-/Konzeptdokument. Es ist bewusst nicht der aktuelle alleinige SSOT fuer Radi144.

Aktueller operativer Stand und Baseline-Entscheidungen muessen gegen Code, Tests und die kuratierten Audit-Dokumente unter `docs/` verifiziert werden, insbesondere:

- `docs/RADI144_PROJECT_INTENT_2026-06-06.md`
- `docs/RADI144_TIEFENANALYSE_2026-06-03.md`
- `docs/GIT_BASELINE_AUDIT_2026-06-06.md`
- `docs/INITIAL_BASELINE_PREPARATION_2026-06-07.md`

Historische Leistungs-, Versions-, Quantum-, Hardware- oder Akkuranzclaims in diesem Dokument sind nicht automatisch als aktueller Produktivstand zu behandeln.

---

# 12x12 Resonance Matrix Engine – Vollständige Systembeschreibung (Developer Edition)

**Version:** 1.5.0 (EMF Compensation & Environmental Intelligence Edition)  
**Stand:** 09. Februar 2026  
**Status:** Finalized & Validated  
**Zielgruppe:** Entwickler:innen, DevOps, technische Reviewer  

> Verifizierter Nachtrag 2026-06-04: Diese Systembeschreibung enthaelt weiterhin gueltige Architekturteile, ist jedoch nicht die alleinige Wahrheitsquelle fuer den aktuellen Laufzeitstand. Zusaetzlich verifiziert sind inzwischen die Runtime-Verwaltungsdomäne (`data/runtime/` mit Client Registry, Session Archive, Report Manifest), API-Header `X-Client-ID` / `X-Session-ID` / `X-Artifact-ID`, ein projektlokales `tests/__init__.py` gegen Test-Import-Shadowing und ein defensiverer CPU-RAM-Guard fuer den Precision-CPU-Pfad (`20%` verfuegbarer RAM, CPU-Cap `128 MiB`). Aktueller Teststand: `29 passed, 9 warnings`.

---

## 0. Kurzüberblick (Executive Snapshot)
Die **12x12 Resonance Matrix Engine** ist ein hybrides, hardware-adaptives System zur Berechnung radionischer Resonanzfelder. In der Version 1.5.0 wurde das System um eine Echtzeit-EMF-Kompensation (Electromagnetic Field Compensation) erweitert, die Umgebungsstoerungen durch WLAN, Bluetooth, 5G und andere elektromagnetische Quellen erkennt und aktiv kompensiert.

- **EMF-Kompensation (NEU):** Echtzeit-Messung und Kompensation elektromagnetischer Umgebungsstoerungen via CPU-Timing-Jitter, RNG-Entropie, GPU-Thermal-Noise und Systemlast-Analyse.
- **Solfeggio Counter-Frequencies:** Automatische Generierung von Gegen-Frequenzen (174Hz, 285Hz, 396Hz, 417Hz, 528Hz, 639Hz, 741Hz, 852Hz, 963Hz) zur Harmonisierung.
- **WebSocket Live-Dashboard:** Echtzeit-Monitoring des EMF-Umfelds via `/api/v1/emf/ws`.
- **Plug-in Architektur:** Vorbereitung fuer spaetere RTL-SDR Hardware-Integration.
- **Adaptive Hardware-Skalierung:** Automatische Anpassung an High-End GPUs (RTX 4000 Ada), Standard-Laptops (Ryzen 9) und Office-PCs.
- **Erweiterte Gruppen-Analyse:** Einbindung des Geburtsorts fuer jedes Gruppenmitglied.

---

## 1. Architektur – Gesamtübersicht

### 1.1 Schichtenmodell (v1.5.0)
```
┌─────────────────────────────────────────────────────────────┐
│                     USER / ADMIN UI                         │
│  PowerShell CLI (ASCII) + Adaptive Group Entry + EMF Toggle │
└─────────────────────────────────────────────────────────────┘
                         │ (Einzel / Gruppe / Geo / EMF)
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    APPLICATION BRIDGE                       │
│   dev_cli.py (--emf-compensate) + REST API + WebSocket      │
└─────────────────────────────────────────────────────────────┘
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
┌─────────────────────┐ ┌───────────────────────────────────┐
│  EMF COMPENSATION   │ │      CORE COMPUTATION LAYER       │
│  LAYER (v1.5.0)     │ │  ResonanceMatrixEngine (80k - 1M) │
│                     │ │                                   │
│ - CPU Timing Jitter │◄┤  emf_compensation_vector applied  │
│ - RNG Entropy       │ │  to client + focus vectors        │
│ - GPU Thermal Noise │ │                                   │
│ - System Load       │ └───────────────────────────────────┘
│ - [RTL-SDR Plugin]  │              │
└─────────────────────┘              ▼
              │          ┌───────────────────────────────────┐
              └─────────►│  EXPORT + AUDIO + REPORTING LAYER │
   Counter-Frequencies   │  PDF / XLSX / Logs / Harmonizer   │
   + Timing Advice       └───────────────────────────────────┘
```

### 1.2 Hardware-Adaption (Dynamisch)
Die Engine nutzt `psutil` und `torch.cuda`, um die Umgebung zu analysieren:
- **Extreme Mode (1M Kandidaten):** Aktiviert bei VRAM >= 20GB (z.B. RTX 4000 SFF Ada).
- **High Mode (500k Kandidaten):** Aktiviert bei VRAM >= 8GB.
- **Standard Mode (200k Kandidaten):** Standard für CUDA-Systeme.
- **CPU Optimized:** Skalierung basierend auf verfügbarem System-RAM (80k - 250k) und Thread-Optimierung für AMD Ryzen.

---

## 2. Funktionale Hauptmodule (v1.5.0 Updates)

### 2.1 EMF-Kompensation (NEU in v1.5.0)
Das Modul `app/algorithms/emf_compensator.py` implementiert eine Echtzeit-Umfeld-Analyse und -Kompensation:

**Sensing Layer (4 Sensoren):**
- **CPU Timing Jitter:** Misst Mikrosekunden-Varianz in CPU-Zyklen als Proxy fuer elektromagnetische Stoerungen.
- **RNG Entropy Quality:** Bewertet die Qualitaet des System-Zufallsgenerators (Chi-Quadrat-Test auf `os.urandom`).
- **GPU Thermal Noise:** Nutzt GPU-Tensor-Operationen zur Messung thermischer Rauschfaktoren.
- **System Load:** Erfasst CPU-Auslastung und Arbeitsspeicher als indirekten EMF-Indikator.

**Profiling Layer:**
- Berechnet einen `composite_emf_index` (0.0 = stoerungsfrei, 1.0 = stark gestoert).
- Erkennt `low_noise_windows` fuer optimale Berechnungszeitpunkte.
- Gibt `timing_recommendation` mit Konfidenzwert zurueck.

**Compensation Layer:**
- Erzeugt einen inversen Kompensationsvektor, der auf Client- und Fokus-Vektoren angewendet wird.
- Generiert Solfeggio Counter-Frequencies (174-963 Hz) als Harmonisierungs-Empfehlungen.
- Verbessert die Seed-Qualitaet fuer Zufallsgeneratoren bei hohem EMF-Index.

**Plug-in Architektur (RTL-SDR Vorbereitung):**
- `RTLSDRPlugin`-Interface definiert: `initialize()`, `read_spectrum()`, `get_peak_frequencies()`.
- Hardware-Integration ueber `register_sdr_plugin()` Methode.
- Automatischer Fallback auf Software-Sensoren wenn keine SDR-Hardware verfuegbar.

### 2.2 REST API Endpoints (EMF)
| Endpoint | Methode | Beschreibung |
|---|---|---|
| `/api/v1/emf/enable` | POST | Aktiviert EMF-Kompensation (optional `continuous=true`) |
| `/api/v1/emf/disable` | POST | Deaktiviert EMF-Kompensation |
| `/api/v1/emf/status` | GET | Aktueller EMF-Status und Metriken |
| `/api/v1/emf/profile` | GET | Fuehrt Echtzeit-Umfeldmessung durch |
| `/api/v1/emf/ws` | WebSocket | Live-Stream (alle 5s) mit EMF-Index, Entropy, Counter-Frequencies |

### 2.3 Erweiterte Gruppen-Synergie
Der Gruppen-Flow erfasst nun Nachname, Vorname, Geburtsdatum **und Geburtsort**. JSON-Importe unterstuetzen das `utf-8-sig` Format.

### 2.4 Klienten-Dokumentation
Mit dem `USER_GUIDE_DE.md` steht eine kompakte Anleitung zur Verfuegung.

---

## 3. CLI & UI Integration (v1.5.0)

### 3.1 dev_cli.py
- Neues Flag: `--emf-compensate` aktiviert die EMF-Umfeld-Kompensation.
- EMF-Ergebnisse werden in der Konsolenausgabe angezeigt (EMF Index, Entropy, Counter-Frequencies).
- Kompensationsvektor wird automatisch auf Client- und Fokus-Vektoren angewendet.

### 3.2 generate_matrix.ps1
- Neuer UI-Prompt: "EMF-Umfeld-Kompensation aktiv? (j/N)".
- Flag wird automatisch an `dev_cli.py` weitergereicht.

### 3.3 ResonanceMatrixEngine Integration
- `enable_emf_compensation(continuous)` / `disable_emf_compensation()` Methoden.
- `calculate_resonance()` akzeptiert `emf_compensate=True` Parameter.
- Kompensationsvektor wird vor der Matrix-Suche auf beide Vektoren (Client + Fokus) angewendet.
- EMF-Daten werden im Ergebnis-Dict unter `emf_compensation` zurueckgegeben.

---

## 4. Pydantic Schemas (v1.5.0)
- `ResonanceAnalysisRequest`: Erweitert um `emf_compensate`, `focus_weight`, `calculation_mode`, `hrv_sim`, `group_members`, `geo_coords`.
- `EMFCompensationResult`: EMF-Index, Entropy-Score, Timing-Recommendation, Counter-Frequencies.
- `EMFStatusResponse`: Vollstaendiger EMF-Status fuer den `/emf/status` Endpoint.
- `EMFCounterFrequency` / `EMFTimingRecommendation`: Strukturierte Sub-Modelle.

---

## 5. Roadmap
- [x] v1.4.5: DB-Scan Edition (Auto-Resonanz Ranking)
- [x] v1.4.8: ASCII & Robust Encoding (Windows Stability Fixes)
- [x] v1.4.9: Adaptive Hardware & Client Synergy (Multi-PC Support)
- [x] v1.5.0: EMF Compensation & Environmental Intelligence (Software-Sensoren)
- [ ] v1.5.1: RTL-SDR Hardware Integration (physikalische Spektrumanalyse)
- [ ] v1.6.0: Physische HRV-Hardware Integration & D-Wave Live API

**Ende der Systembeschreibung v1.5.0.**

# 12x12 Resonance Matrix Engine – Developer Master Guide

**Version:** 1.2.0 (Quantum Ready)  
**Datum:** 12. Januar 2026  
**Status:** Production Ready (Windows Dev & Linux Root Server)

> Verifizierter Nachtrag 2026-06-04: Diese Datei beschreibt einen aelteren Architekturstand. Fuer den aktuellen Projektzustand sind zusaetzlich verifiziert: Runtime-Verwaltungsdomäne unter `data/runtime/`, API-`client_id` als echte Runtime-Registry-ID, Response-Header `X-Client-ID` / `X-Session-ID` / `X-Artifact-ID`, projektlokales `tests/__init__.py` gegen Test-Import-Shadowing und ein defensiverer CPU-RAM-Guard im Precision-CPU-Pfad (`20%` verfuegbarer RAM, CPU-Cap `128 MiB`). Aktueller Teststand: `29 passed, 9 warnings`.

---

## 1. Executive Summary
Das **12x12 Resonance Matrix System** ist eine hybride Hochleistungs-Anwendung zur Berechnung und Visualisierung radionischer Energiefelder. Es kombiniert klassische numerische Verfahren mit quanten-heuristischen Ansätzen, um aus einem Zustandsraum von $10^{144}$ Möglichkeiten diejenige 12x12-Matrix zu identifizieren, die die höchste energetische Resonanz zu einem Klienten und dessen Fokus aufweist.

Das System ist **hardware-adaptiv** konzipiert und skaliert automatisch von lokalen Laptops (CPU/APU) bis hin zu dedizierten Linux-GPU-Servern (CUDA) und bietet Schnittstellen für echtes Quantum Computing (D-Wave).

---

## 2. System-Architektur

### 2.1. Hybrid-Stack
Das System besteht aus zwei lose gekoppelten Schichten, die über Standard-I/O und Argumente kommunizieren. Dies gewährleistet maximale Stabilität und Trennung von UI und Rechenkern.

| Schicht | Technologie | Aufgabe |
| :--- | :--- | :--- |
| **Frontend / Controller** | **PowerShell Core** (`.ps1`) | Benutzerinteraktion, Session-Management, Input-Validierung (UTF-8), Prozess-Orchestrierung. |
| **Calculation Backend** | **Python 3.10+** | Mathematischer Kern. |
| **Core Libraries** | **PyTorch (CUDA/CPU)** | Vektorisierung, Tensor-Operationen, Parallelisierung. |
| **Interfaces** | **CLI & D-Wave API** | Brücke zwischen Shell, Engine und Quanten-Cloud. |

### 2.2. Hardware-Adaptivität
Die Engine prüft beim Start die Umgebung (`ResonanceMatrixEngine.__init__`) und konfiguriert sich selbst:

1.  **Windows Development (Consumer Hardware)**
    *   *Erkennung:* OS = Windows, GPU = optional (z.B. AMD Radeon 780M).
    *   *Modus:* CPU-Optimiert (Multiprocessing) oder GPU (DirectML/CUDA falls vorhanden).
    *   *Workload:* 100.000 Kandidaten-Matrizen (Balance aus Speed/Präzision).
    *   *Audio:* Nutzung von `winsound` für Echtzeit-Feedback.

2.  **Linux Root Server (High-Performance)**
    *   *Erkennung:* OS = Linux, GPU = NVIDIA RTX 4000 Ada (via `torch.cuda`).
    *   *Modus:* Native CUDA Tensor Cores (`tf32` enabled).
    *   *Workload:* **500.000 Kandidaten-Matrizen** (Maximale Tiefe, 5x Präzision).
    *   *Quantum:* Aktiviert D-Wave Interface, falls `DWAVE_API_TOKEN` gesetzt.

---

## 3. Algorithmischer Kern (Deep Dive)

### 3.1. Vektorisierung (The Embedding)
Bevor Resonanz berechnet werden kann, müssen Realitäten in Mathematik übersetzt werden.
*   **Input:** Klientendaten (Name, Geburtsdatum, Ort) + Fokus (z.B. "Heilung").
*   **Prozess:**
    *   `Client Signature`: Deterministisches Hashing der bio-grafischen Daten in einen 256-dimensionalen Vektor.
    *   `Focus Vector`: Semantisches Embedding der Intention.
    *   `Bio-Knowledge`: Optionaler Mix-In von Frequenzen (Chakren, Meridiane) aus `bio_knowledge.json`.

### 3.2. Die Such-Strategie (Search Space $10^{144}$)
Da eine vollständige Suche unmöglich ist, nutzt das System einen **Monte-Carlo-Ansatz im Vektorraum**.

#### Modus A: "Quantum" (Stochastisch / Standard)
*   **Philosophie:** Das Feld ist lebendig. Jeder Moment ist einzigartig.
*   **Technik:** Der Zufallsgenerator (RNG) wird mit Entropie (Systemzeit/Rauschen) initialisiert.
*   **Ergebnis:** Gleicher Input erzeugt bei jedem Durchlauf eine *neue*, aber *ähnlich resonante* Matrix.

#### Modus B: "Precision" (Deterministisch)
*   **Philosophie:** Wissenschaftliche Reproduzierbarkeit.
*   **Technik:** Ein **Master-Seed** wird aus dem Hash von `(Klient + Fokus)` berechnet.
*   **Ergebnis:** Gleicher Input erzeugt **bit-genau** dieselbe Matrix, selbst Jahre später.

### 3.3. Der D-Wave Quanten-Sprung (Refinement)
Wenn aktiviert, findet ein zweistufiger Prozess statt:
1.  **Coarse Search (GPU):** Findet das "Tal" im Gebirge (die besten 0.001% der Lösungen).
2.  **Quantum Annealing (QPU):** Die beste Matrix wird als Startkonfiguration an den D-Wave Quantencomputer gesendet. Durch **Quanten-Tunneln** kann das System lokale Minima verlassen und den absolut niedrigsten Energiezustand (höchste Resonanz) finden.

---

## 4. Workflow & Datenfluss

1.  **User Input (PS1):**
    *   Eingabe: "Max Mustermann", "01.01.1990", Fokus: "Klarheit".
    *   Auswahl: Modus (Quantum/Precision), Palette.
2.  **Bridge (CLI):**
    *   Aufruf: `python dev_cli.py --name "Max..." --focus "Klarheit" --mode precision ...`
3.  **Engine (Python):**
    *   Initialisierung & Hardware-Check.
    *   Generierung der Vektoren.
    *   **Matrix-Loop (CUDA):** Erzeugung & Bewertung von 500k Kandidaten.
    *   Mapping der Gewinner-Matrix auf Farben (Symmetrie/Palette).
4.  **Output:**
    *   JSON Resultat.
    *   PDF Report (ReportLab) & Excel (OpenPyXL).
    *   Audio-Synthese (Solfeggio Frequenzen) im `Harmonizer`.

---

## 5. Implementation Roadmap (Status Quo)

Die Entwicklung erfolgte in iterativen Phasen, die nun abgeschlossen sind:

### Phase 1: Foundation (Abgeschlossen)
- [x] Projekt-Struktur & Python Environment.
- [x] Grundlegende Vektor-Mathematik (NumPy).
- [x] Erste CLI Implementierung.

### Phase 2: High-Performance Core (Abgeschlossen)
- [x] Portierung auf PyTorch & CUDA.
- [x] Implementierung der Parallel-Suche (100k Kandidaten).
- [x] PDF & Excel Reporting Engine.

### Phase 3: UX & Stability (Abgeschlossen)
- [x] PowerShell Frontend mit Menüführung.
- [x] **UTF-8 Fix:** Korrekte Behandlung von Umlauten durch den gesamten Stack.
- [x] Fehlerbehandlung (Try/Catch) und Logging.

### Phase 4: Enterprise & Quantum (Abgeschlossen - Aktueller Stand)
- [x] **Adaptive Scaling:** Automatische 500k-Suche auf Linux-Servern.
- [x] **Precision Mode:** Umschaltbare Deterministik.
- [x] **D-Wave Integration:** Interface und Logik für Quantum Annealing implementiert.

---

## 6. Deployment Guide

### A. Windows Development PC
1.  Repository klonen.
2.  Python 3.10+ installieren.
3.  `pip install -r requirements.txt`.
4.  Starten mit `.\generate_matrix.ps1`.

### B. Linux Root Server (Debian/Ubuntu + NVIDIA)
1.  System-Setup:
    ```bash
    apt update && apt install python3-pip python3-venv cuda-drivers
    ```
2.  Environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```
3.  Optional: D-Wave Token setzen:
    ```bash
    export DWAVE_API_TOKEN="DEV-xxxxxxxxxxxxxxxx"
    ```
4.  Testen:
    Führen Sie `dev_cli.py` einmal manuell aus, um zu prüfen, ob "High-Performance Mode: 500k" im Log erscheint.

---

**Ende des Dokuments.**
*Entwickelt von Cascade AI für High-End Radionik-Anwendungen.*

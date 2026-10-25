# 12x12 Resonance Matrix Engine - Vollstaendige Technische Dokumentation

**Version:** 1.4.9 (Adaptive Hardware & Client Synergy Edition)  
**Stand:** 01. Februar 2026

> Verifizierter Nachtrag 2026-06-04: Diese Datei ist als technische Basis nuetzlich, bildet den aktuellen Live-Stand aber nicht vollstaendig ab. Verifiziert aktuell: API-`client_id` als echte Runtime-Registry-ID, Session-/Artefakt-Spiegelung unter `data/runtime/`, Response-Header `X-Client-ID` / `X-Session-ID` / `X-Artifact-ID`, projektlokales `tests/__init__.py` gegen Test-Package-Shadowing sowie ein defensiverer CPU-RAM-Guard im Precision-Pfad (`20%` verfuegbarer RAM, hartes CPU-Cap `128 MiB`). Aktueller Teststand: `29 passed, 9 warnings`.

## 1. Projektuebersicht

Die **12x12 Resonance Matrix Engine** ist ein hochleistungsfaehiges, hardware-adaptives System zur Berechnung radionischer Resonanzmuster. Sie operiert in einem hyper-komplexen Zustandsraum von $10^{144}$ Moeglichkeiten, definiert durch eine 12x12 Matrix, in der jede Zelle einen Wert von 0 bis 9 annehmen kann.

Das System nutzt modernste **Rechenleistung (CUDA & Multi-Core CPU)**, um nicht-lineare quanten-heuristische Suchen durchzufuehren. Es passt sich dabei dynamisch an die verfuegbare Hardware des Endgeraets an (vom Office-Laptop bis zum High-End GPU-Server).

---

## 2. Systemarchitektur

Das System ist als **Standalone Microservice** konzipiert, basierend auf Python und FastAPI.

### Technologie-Stack
*   **Framework**: FastAPI (Asynchron, High-Performance)
*   **Core Engine**: PyTorch (Tensor-Berechnungen)
*   **Beschleunigung**: CUDA (NVIDIA Tensor Cores)
*   **Mathematik**: NumPy (Vektor-Operationen)
*   **Schnittstellen**: REST API (JSON)

### Verzeichnisstruktur
```
12x12/
├── app/
│   ├── algorithms/       # Kern-Logik
│   │   ├── resonance_engine.py  # Matrix-Berechnung & GPU-Code
│   │   └── client_signature.py  # Klienten-Vektorisierung
│   ├── api/
│   │   └── resonance.py         # API-Endpunkte
│   └── schemas/
│       ├── klienten.py          # Pydantic Datenmodelle
│       └── resonance.py         # Request/Response Modelle
├── main.py               # Server-Einstiegspunkt
├── requirements.txt      # Abhängigkeiten
└── run.bat               # Start-Skript
```

---

## 3. Algorithmische Details

### 3.1. Klienten-Signatur (Vektorisierung)
Bevor eine Resonanz berechnet werden kann, muss der Klient in einen mathematischen Vektor transformiert werden. Dies geschieht in `ClientSignatureGenerator`.

**Einflussfaktoren & Gewichtung:**
1.  **Name-Frequenz (15%)**: Analysiert Phonetik und Numerologie nach Garjajev.
2.  **Geburtsdaten (20%)**: 
    *   Astronomische Basis: *Julian Day Number*.
    *   Lokale Spezifitaet: Einbindung des **Geburtsorts** via Hashing.
    *   Zeitliche Spezifitaet: Beruecksichtigung der **Geburtszeit** fuer die Phasenlage.
3.  **Bild-Signatur (25%)**: (Optional) Integriert holografische Informationen.
4.  **Organuhr (10%)**: Beruecksichtigt die aktuelle Tageszeit (TCM Meridiane).
5.  **Planetarische Einfluesse (15%)**: Moduliert die Frequenz basierend auf Zyklen.
6.  **Geo-Resonanz (Adaptiv)**: Einbindung von Google Maps Koordinaten und Umkreis-Radius.
7.  **Kollektive Synergie**: Vektor-Centroid-Berechnung fuer Gruppenanalysen.

### 3.2. Die Resonanz-Engine
Die `ResonanceMatrixEngine` ist das Herzstueck. Sie passt sich dynamisch an die Umgebung an.

**Hardware-Adaptive Skalierung:**
Das System erkennt beim Start die Hardware-Ressourcen und skaliert die Suchtiefe (Kandidaten-Matrizen):
- **Extreme Mode (1.000.000):** NVIDIA GPU >= 20GB VRAM (Ada Generation).
- **High Mode (500.000):** NVIDIA GPU >= 8GB VRAM.
- **Standard Mode (200.000):** CUDA Systeme mit kleinerem VRAM.
- **CPU Optimized (80k - 250k):** Skalierung basierend auf System-RAM und Thread-Anzahl.

**Der Prozess:**
1.  **Embedding**: Projektion von Signatur und Fokus in den 256-D latenten Raum.
2.  **Parallel-Suche**: Generierung der skalierten Kandidaten-Anzahl auf GPU/CPU.
3.  **Resonanz-Ranking**: Berechnung der Kosinus-Aehnlichkeit.
4.  **Selektion**: Kollaps des am staerksten resonanten Musters.

### 3.3. Berechnungs-Modi
Das System bietet zwei fundamentale Betriebsarten, wählbar im CLI oder Frontend:

| Modus | Beschreibung | Anwendungsfall |
| :--- | :--- | :--- |
| **Quantum (Standard)** | Stochastisch / "Lebendig". Jeder Durchlauf erzeugt bei gleichem Input leicht variierende Matrizen (ähnliche Resonanz, andere Struktur). Simuliert das Verhalten eines lebenden Energiefeldes. | Therapeutische Sitzungen, "Orakel"-Funktion, Dynamische Prozesse. |
| **Precision** | Deterministisch. Ein fester Seed, abgeleitet aus dem Hash von Klient+Fokus, steuert den Zufallsgenerator. Gleicher Input erzeugt **immer exakt** dieselbe Matrix. | Wissenschaftliche Validierung, Reproduzierbarkeitstests, Long-Term-Monitoring. |

### 3.4. Quantum Readiness (D-Wave Integration)
Das System ist architektonisch auf **Quantum Annealing** vorbereitet.
*   **Schnittstelle**: `solve_with_dwave` Interface ist implementiert.
*   **Funktion**: Bei Verfügbarkeit eines D-Wave API Tokens kann das Optimierungsproblem als QUBO (Quadratic Unconstrained Binary Optimization) formuliert und an einen echten Quantenprozessor (QPU) gesendet werden.
*   **Vorteil**: Echte energetische Minimierung durch Quanten-Tunneln statt klassischer Suche.

### 3.5. Kohärente Farbmuster-Generierung
Nachdem die Zahlenmatrix (0-9) gefunden wurde, wird sie in ein energetisches Farbspektrum übersetzt.

**Das Radionische Farbspektrum:**

| Zahl | Farbe | Hex-Code | Energetische Bedeutung |
| :--- | :--- | :--- | :--- |
| **0** | Weiß | `#FFFFFF` | Nullpunkt, Reines Potenzial, Äther |
| **1** | Rot | `#FF0000` | Wurzel-Chakra, Vitalität, Physische Erdung |
| **2** | Orange | `#FF7F00` | Sakral-Chakra, Kreativität, Emotionen |
| **3** | Gelb | `#FFFF00` | Solarplexus, Mentaler Fokus, Wille |
| **4** | Grün | `#00FF00` | Herz-Chakra, Balance, Heilung |
| **5** | Türkis | `#00FFFF` | Hals-Chakra, Ausdruck, Kommunikation |
| **6** | Blau | `#0000FF` | Stirn-Chakra, Intuition, Vision |
| **7** | Violett | `#8B00FF` | Kronen-Chakra, Transformation, Spirituell |
| **8** | Magenta | `#FF00FF` | 8. Chakra, Seelenstern, Integration |
| **9** | Gold | `#FFD700` | Solare Frequenz, Meisterschaft, Vollendung |

---

## 4. API Referenz

Das System stellt eine REST-Schnittstelle zur Verfügung.

### Endpoint: Matrix Analyse
`POST /api/v1/analyze-matrix`

#### Request Body (JSON)
```json
{
  "client_data": {
    "first_name": "Max",
    "last_names": ["Mustermann"],
    "birth_date": "1980-05-12",
    "birth_place": "München"
  },
  "focus": "Harmonische Regulation Lunge",
  "matrix_size": 12,
  "use_cuda": true
}
```

#### Response Body (JSON)
```json
{
  "analysis_id": "uuid...",
  "timestamp": "2024-01-09T20:00:00",
  "resonance_score": 0.987,  // Wert zwischen 0.0 und 1.0
  "matrix_12x12": [
    [1, 9, 0, ...], // 12 Zeilen mit je 12 Zahlen
    ...
  ],
  "matrix_colors": [
    ["#FF0000", "#FFD700", "#FFFFFF", ...], // 12 Zeilen mit je 12 Farben
    ...
  ],
  "hardware_acceleration": "CUDA (RTX 4000)",
  "processing_time_ms": 45.2
}
```

---

## 5. Installation & Betrieb

### Voraussetzungen
1.  **OS**: Windows 10/11 (empfohlen für CUDA Support).
2.  **Python**: Version 3.10 oder höher.
3.  **Hardware**: NVIDIA GPU (RTX Serie empfohlen) mit aktuellen Treibern.

### Installation
1.  Öffnen Sie eine Eingabeaufforderung im Ordner `12x12`.
2.  Installieren Sie die Abhängigkeiten:
    ```bash
    pip install -r requirements.txt
    ```
    *Hinweis: Für GPU-Support muss PyTorch mit CUDA-Unterstützung installiert sein (siehe pytorch.org).*

### Starten
Führen Sie die Datei `run.bat` aus oder nutzen Sie den Befehl:
```bash
python main.py
```
Der Server startet unter `http://localhost:8000`.

### Testen
Besuchen Sie im Browser `http://localhost:8000/docs`. Dort finden Sie eine interaktive Swagger-UI, um Anfragen direkt zu senden und die Ergebnisse zu sehen.

---

## 6. Mathematischer Hintergrund

Die Zahl der Möglichkeiten in einer 12x12 Matrix mit Werten 0-9 beträgt:
$$ 10^{144} $$

Zum Vergleich: Die Anzahl der Atome im sichtbaren Universum wird auf ca. $10^{80}$ geschätzt. Es ist unmöglich, alle Kombinationen klassisch zu berechnen.

Dieses System nutzt daher einen **resonanz-basierten Kollaps**:
Anstatt nach einer Nadel im Heuhaufen zu suchen, erzeugt das System ein "magnetisches Feld" (den Fokus-Vektor). Die Zahlenmuster "kristallisieren" entlang der Feldlinien dieses Vektors. Die GPU dient dabei als hochenergetischer Beschleuniger, der diesen Kristallisationsprozess millionenfach pro Sekunde simuliert, bis das stabilste (resonanteste) Muster gefunden ist.

# Hardware Requirements – 12x12 Resonance Matrix Engine v1.5.0

**Stand:** 09. Februar 2026  
**Status:** Produktionsbereit (Dual-Plattform)

---

## 1. Windows Development PC (Aktuell)

### 1.1 Hardware-Spezifikation

| Komponente | Spezifikation | Funktion im System |
|------------|---------------|-------------------|
| **CPU** | AMD Ryzen 9 8945HS (4.00 GHz, 8C/16T) | Matrix-Berechnung (CPU-Modus), EMF Timing-Jitter, RNG-Entropie |
| **RAM** | 16 GB DDR5 (15.3 GB nutzbar) | Kandidaten-Pool (150.000), Tensor-Operationen |
| **GPU** | AMD Radeon 780M (370 MB VRAM, shared) | Begrenzt: GPU-Noise Basis-Messung |
| **Storage** | NVMe SSD | Schneller I/O fuer Registry, Bild-Signaturen |
| **OS** | Windows 10/11 | Tkinter-Harmonizer, winsound Audio |
| **Audio** | Onboard / USB | WAV-basierte Harmonisierung (44.1 kHz, 16-bit) |

### 1.2 System-Konfiguration

```
Kandidaten-Pool:     150.000 (CPU-optimiert, 80% Thread-Nutzung)
GPU-Noise Mode:      Basic (256x256 Tensor, 10 Zyklen)
EMF-Sensoren:        CPU-Timing-Jitter, RNG-Entropie, System-Load
Amplifier:           Vollständig (Matching, Audio, Palette)
Harmonisierung:      Tkinter + winsound (Windows-nativ)
Matrix-Berechnung:   ~2-5 Sekunden pro Fokus
```

### 1.3 Einschränkungen

- **Kein CUDA** → CPU-Modus mit Thread-Optimierung
- **Begrenztes VRAM** → GPU-Noise nur Basic-Mode
- **16 GB RAM** → Max. 150.000 Kandidaten
- **Keine RTL-SDR** → Software-only EMF-Kompensation

---

## 2. Linux Debian Root Server (Ziel-Deployment)

### 2.1 Hardware-Spezifikation

| Komponente | Spezifikation | Funktion im System |
|------------|---------------|-------------------|
| **CPU** | AMD Ryzen 5 9600X (6C/12T, 3.9–5.4 GHz) | API-Server, Signatur-Generierung, EMF-Messung |
| **RAM** | 128 GB DDR5 ECC | Massiver Kandidaten-Pool (1.000.000), Multi-Client |
| **GPU** | NVIDIA RTX 4000 SFF Ada (20 GB VRAM) | CUDA Matrix-Berechnung, Server GPU-Noise (FFT, Drift) |
| **Storage** | 2× 1 TB NVMe (RAID 1) | Redundante Datenhaltung, Bild-Analyse |
| **Netzwerk** | 2× 1 GBit/s | WebSocket-Streams, Client-Sensor-Empfang |
| **OS** | Debian 12 (Bookworm) | systemd Service, NVIDIA Driver 535+ |

### 2.2 System-Konfiguration

```
Kandidaten-Pool:     1.000.000 (CUDA Extreme Mode)
GPU-Noise Mode:      Server (1024x1024, FFT-Spektrum, Drift, Memory-Noise, 20 Zyklen)
EMF-Sensoren:        Alle 4 Software-Sensoren + Remote Client Sensor
Amplifier:           Vollständig + Bild-basierte Umfeld-Analyse
API-Server:          FastAPI mit 4 Uvicorn Workers
WebSocket:           EMF Monitor + Client-Sensor + Live-Daten
Matrix-Berechnung:   ~0.2-0.5 Sekunden pro Fokus (CUDA)
CUDA Compute:        SM 8.9 (Ada Lovelace), TF32 aktiviert
```

### 2.3 CUDA-spezifische Optimierungen

| Feature | Dev PC | Linux Server |
|---------|--------|-------------|
| Tensor-Größe GPU-Noise | 256×256 | 1024×1024 |
| Messzyklen | 10 | 20 |
| FFT-Spektrumanalyse | ✗ | ✓ |
| Numerische Drift-Erkennung | ✗ | ✓ |
| GPU-Memory Noise Pattern | ✗ | ✓ |
| Kandidaten-Pool | 150K (CPU) | 1M (CUDA) |
| Multi-Client API | Begrenzt | Vollständig |

### 2.4 NVIDIA CUDA Setup

```bash
# Erforderlich:
nvidia-driver-535          # oder neuer
nvidia-cuda-toolkit        # CUDA 12.x
PyTorch 2.x + cu121       # CUDA 12.1 Wheels

# Verifikation:
python -c "import torch; print(torch.cuda.get_device_name(0))"
# → NVIDIA RTX 4000 SFF Ada Generation

python -c "import torch; print(torch.cuda.get_device_properties(0).total_mem / (1024**3))"
# → 20.0 GB
```

---

## 3. Optionale Hardware-Erweiterungen

### 3.1 RTL-SDR Empfänger (EMF-Echtzeit-Messung)

| Komponente | Empfehlung | Zweck |
|------------|-----------|-------|
| RTL-SDR V3/V4 | ~30 EUR | Breitband-EMF-Scan (24-1766 MHz) |
| Antenne | Teleskop/Dipol | WiFi, 5G, LTE Erkennung |
| Python-Lib | `pyrtlsdr>=0.3.0` | Integration in EMF Compensator |

**Status:** Plugin-Interface vorbereitet in `emf_compensator.py` (`_sdr_available`)

### 3.2 USB-Kamera (Amplifier Umfeld-Sensor)

| Komponente | Empfehlung | Zweck |
|------------|-----------|-------|
| USB Webcam | 720p+ | Amplifier-Referenzbild, Umfeld-Analyse |
| Python-Lib | `opencv-python` | Bild-Vergleich, Farbtemperatur |

**Status:** Bild-Vergleichs-Algorithmus implementiert (`compare_environment_image`)

### 3.3 HRV-Wearable (Bio-Feedback)

| Komponente | Empfehlung | Zweck |
|------------|-----------|-------|
| Polar H10 | BLE Brustgurt | RR-Intervalle, HRV-Daten |
| BLE Gateway | Raspberry Pi / ESP32 | BLE → WebSocket Bridge |
| Python-Lib | `bleak>=0.21.0` | BLE-Kommunikation |

**Status:** WebSocket-Empfang vorbereitet (`/emf/client-sensor`, Typ `hrv`)

---

## 4. Netzwerk-Architektur (Server-Deployment)

```
┌─────────────────────────────────────────────────────┐
│              LINUX DEBIAN ROOT SERVER               │
│  ┌─────────┐  ┌──────────┐  ┌───────────────────┐  │
│  │ FastAPI  │  │ Uvicorn  │  │ RTX 4000 Ada      │  │
│  │ 4 Worker │  │ Port 8000│  │ CUDA 12.x         │  │
│  │          │  │          │  │ 20 GB VRAM         │  │
│  └────┬─────┘  └────┬─────┘  └────────┬──────────┘  │
│       │              │                 │             │
│  ┌────┴──────────────┴─────────────────┴──────────┐  │
│  │           ResonanceMatrixEngine                 │  │
│  │  + EMFCompensator (Server GPU-Noise Mode)      │  │
│  │  + AmplifierVectorGenerator                    │  │
│  │  + ClientSignatureGenerator                    │  │
│  └────────────────────────────────────────────────┘  │
│                      │ WebSocket                     │
└──────────────────────┼───────────────────────────────┘
                       │
          ┌────────────┼────────────────┐
          │            │                │
     ┌────┴────┐  ┌────┴────┐    ┌─────┴──────┐
     │ Browser │  │  PS1    │    │ Mobile App │
     │ Monitor │  │  CLI    │    │ (Zukunft)  │
     │ /emf/   │  │ Remote  │    │ Sensor-    │
     │ monitor │  │         │    │ daten      │
     └─────────┘  └─────────┘    └────────────┘
```

---

## 5. Ressourcen-Verbrauch (Benchmarks)

### 5.1 Dev PC (Windows, CPU-Modus)

| Metrik | Wert |
|--------|------|
| RAM Idle | ~200 MB |
| RAM Analyse | ~800 MB (150K Kandidaten) |
| CPU Analyse | ~70% (12 Threads) |
| Analyse-Dauer | 2-5 Sek/Fokus |
| EMF-Kalibrierung | ~3 Sek |
| Amplifier-Matching | <50 ms |

### 5.2 Linux Server (CUDA, Extreme Mode)

| Metrik | Wert (geschätzt) |
|--------|-----------------|
| RAM Idle | ~400 MB |
| RAM Analyse | ~2 GB (1M Kandidaten) |
| VRAM Analyse | ~3 GB |
| GPU-Auslastung | ~40% (Analyse) |
| Analyse-Dauer | 0.2-0.5 Sek/Fokus |
| EMF Server-Noise | ~200 ms (FFT inkl.) |
| Amplifier-Matching | <10 ms |
| Concurrent Clients | ~20 (WebSocket) |

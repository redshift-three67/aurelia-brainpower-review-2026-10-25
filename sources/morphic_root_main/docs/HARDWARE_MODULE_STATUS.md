# Hardware-Modul Status

## Übersicht

Morphic Engine V1 nutzt ein **hybrides Hardware-Konzept**: Echte Hardware
wird verwendet wenn verfügbar, ansonsten wird auf Mocks/Simulationen
zurückgegriffen.

---

## Status-Tabelle

| Modul | Hardware | Status | Bemerkung |
|-------|----------|--------|-----------|
| `core/hardware/entropy.py` | CPU Jitter, OS RNG | ✅ ECHT | `time.perf_counter_ns()`, `os.urandom()` (RDRAND auf AMD) |
| `core/hardware/entropy.py` | TrueRNG (USB) | ❌ MOCK | Platzhalter, `available=False` |
| `core/hardware/sensors.py` | HID Sensors | ✅ ECHT | Via `hid` library (VID:0x0E50, PID:0x0002) |
| `core/hardware/system_info.py` | CPU/RAM/GPU | ✅ ECHT | `psutil`, CuPy GPU-Erkennung |
| `core/hardware/accel_numpy.py` | GPU (CuPy) | ✅ ECHT | Backend-Selektor NumPy/CuPy mit Smoke-Test |
| `providers/hardware/entropy_sources.py` | CPU Timer | ✅ ECHT | Delegiert an `hardware_entropy` |
| `providers/hardware/entropy_sources.py` | GPU | ✅ ECHT | CuPy Timing-Jitter wenn verfügbar |
| `providers/hardware/entropy_sources.py` | HID, TrueRNG, QRNG, Network | ❌ MOCK | Return 0.0, `healthy=False` |
| `providers/hardware/hardware_entropy.py` | CPU Timer, CPU/MEM | ✅ ECHT | `time.perf_counter_ns()`, `psutil` |
| `providers/hardware/hardware_entropy.py` | HID | ❌ MOCK | "hid module not available" |
| `apps/cli/workflow/step05_emf.py` | CPU Jitter, RNG, Load | ✅ ECHT | `perf_counter_ns`, `os.urandom`, `psutil` |
| `services/hardware_modulation.py` | GPU Compute | ⚠️ SIMULATED | CPU-Matrix-Multiplikation statt GPU |
| `services/hardware_modulation.py` | RAM Access | ⚠️ SIMULATED | Rhythmische RAM-Zugriffe |
| `services/hardware_modulation.py` | WebSocket | ✅ ECHT | `websockets` library |
| `core/hybrid_entropy.py` | Multi-Source | ✅ HYBRID | Gewichtung + XOR-Mix, Fallback `random.random()` |
| `core/quantum_synergy/grover_search.py` | Qiskit Quantum | ✅ HYBRID | Echter Grover wenn Qiskit installiert |
| `entropy_sources.py` (Root) | Wrapper | 📦 WRAPPER | Re-export von `providers/hardware` |
| `hardware_entropy.py` (Root) | Wrapper | 📦 WRAPPER | Re-export von `providers/hardware` |

---

## Legende

- ✅ **ECHT** - Nutzt echte Hardware-Messungen
- ❌ **MOCK** - Platzhalter, returniert feste Werte
- ⚠️ **SIMULATED** - Simuliert Hardware-Verhalten via CPU
- ✅ **HYBRID** - Echte Hardware wenn verfügbar, Fallback sonst
- 📦 **WRAPPER** - Re-export eines anderen Moduls

---

## Nicht implementiert

- **RTL-SDR** - Keine Referenzen im Code (nur in Doku erwähnt)
- **Kozyrev-Sensoren** - Nur Kommentar: "Hier könnten später Kozyrev-Sensoren registriert werden"

---

## Empfehlungen für P2

1. **TrueRNG:** USB-Hardware-RNG Support aktivieren (Stream `TrueRNGSource.available=True` wenn Device erkannt)
2. **QRNG:** Quantum RNG via Qiskit `RandomNumberGenerator` implementieren
3. **Network Entropy:** Echte Network-Timing-Messung via `socket` + `time.perf_counter_ns()`
4. **GPU Modulation:** CuPy-basierte GPU-Last statt CPU-Simulation in `hardware_modulation.py`
5. **HID:** `hid` library in `hardware_entropy.py` integrieren (nur in `sensors.py` vorhanden)

---

**Zuletzt aktualisiert:** 2026-07-02

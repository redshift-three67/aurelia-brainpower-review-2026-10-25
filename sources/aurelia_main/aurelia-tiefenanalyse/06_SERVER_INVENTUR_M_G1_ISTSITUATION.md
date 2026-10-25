# AURELIA — Server-Inventur & Ist-Zustand (GPU Server M G1)

Stand: 2026-08-25  
Geprüfter Zielserver: `185.242.115.210` (`root3091.ipp-srv.net`)  
Prüfzugriff: `klaus999` (Read-Only via OpenSSH)  

---

## 1. Executive Summary des Server-Audits

Der Live-Zugriff auf `185.242.115.210` belegt, dass es sich **exakt um den in der AURELIA-Verfassung spezifizierten "GPU Server M G1"** handelt.

```text
┌────────────────────────────────────────────────────────────────────────┐
│                      BESTÄTIGTE HARDWARE-DATEN                         │
├────────────────────┬───────────────────────────────────────────────────┤
│ CPU                │ AMD Ryzen 5 9600X (6 Kerne / 12 Threads, Zen 5)   │
│                    │ Voller AVX-512 & AVX-512 VNNI / BF16 Support      │
├────────────────────┼───────────────────────────────────────────────────┤
│ GPU                │ NVIDIA RTX 4000 SFF Ada Generation (20 GB VRAM)   │
│                    │ PCI-ID: 01:00.0 AD104GL (rev a1)                  │
├────────────────────┼───────────────────────────────────────────────────┤
│ RAM                │ 128 GB DDR5 (123 GiB erkannt, 103 GiB frei/Cache) │
├────────────────────┼───────────────────────────────────────────────────┤
│ Storage            │ 2× NVMe im Software-RAID 1 (mdadm)               │
│                    │ md3 ext4 (666 GB frei / 58% belegt)               │
├────────────────────┼───────────────────────────────────────────────────┤
│ OS / Kernel        │ Debian GNU/Linux 12 (Bookworm) / Kernel 6.1.0-51  │
├────────────────────┼───────────────────────────────────────────────────┤
│ TPM                │ /dev/tpm0 & /dev/tpmrm0 vorhanden (TPM 2.0)       │
└────────────────────┴───────────────────────────────────────────────────┘
```

---

## 2. Detaillierte Befunde & Abgleich mit AURELIA

### 2.1 Kritischer Befund: NVIDIA Treiber/Library Mismatch
- **Status:** Beim Aufruf von `nvidia-smi` meldet das System:
  ```text
  Failed to initialize NVML: Driver/library version mismatch
  NVML library version: 535.309
  NVRM kernel module:   535.261.03
  ```
- **Ursache:** Ein automatisches Update (`unattended-upgrades` oder `apt upgrade`) hat die Userspace-NVIDIA-Bibliotheken auf Version `535.309.01` aktualisiert, während im laufenden Kernel noch das Modul `535.261.03` geladen ist.
- **Auswirkung:** CUDA-Anwendungen und `nvidia-smi` können die GPU erst nach einem Neustart des Servers oder einem sauberen Reload der Kernel-Module wieder ansprechen.
- **Entwickler-Aktion:** Nach Absprache Server neu starten (`sudo reboot`), damit Kernel-Modul und Bibliotheken wieder synchron auf `535.309` laufen.

---

### 2.2 Bestehende Legacy-Container (`radiquant4` Altbestand)
Auf dem Server laufen aktuell noch mehrere Docker-Container des Vorgängerprodukts `radiquant4` (siehe `12-heritage.md`):
- `radiquant4-api` (Port 8000)
- `radiquant4-radi144`, `radiquant4-radiworks`, `radiquant4-radimorphic`, `radiquant4-radiblohm`, `radiquant4-radithoms`, `radiquant4-radicopen`
- `radiquant4-postgres` (Postgres 16 Alpine)
- `radiquant4-redis-jobs`, `radiquant4-redis-cache`, `radiquant4-redis-locks`
- `radiquant4-ollama` (Port 11435)
- `radiquant4-celery-worker` & `celery-beat`

**Wichtige Governance-Regel (aus `AGENTS.project.md` & `12-heritage.md`):**
- In `/opt/radiquant4` darf **nicht** geschrieben werden!
- Der Altbestand dient ausschließlich als Referenz; AURELIA wird als sauberer, modularer Kern aufgebaut.

---

### 2.3 Prototypen-Verzeichnis (`/opt/Prototypen`)
Das Verzeichnis `/opt/Prototypen/` ist vorhanden und enthält:
- `/opt/Prototypen/Radi144/`
- `/opt/Prototypen/Radimorphic/` (Stand @ `217dcf9`)
- `/opt/Prototypen/Referenzen/`

Dies bestätigt exakt die Vorgabe aus `docs/06-kernel-abi.md`: Die Prototypen können für Phase 3 read-only als Labor-Module gewrappt werden.

---

### 2.4 Hardware-Schnittstellen (Serial / USB)
- `/dev/ttyUSB*` / `/dev/ttyACM*`: Aktuell ist **kein** Spooky2 / Generator X Pro Hardware-Emitter physisch angesteckt.
- Dies entspricht exakt der Vorgabe für Phase 1: `isHardwareActivatable: false`.

---

## 3. Konkrete Server-Empfehlungen für den Übergang zu AURELIA

1. **Reboot zur Bereinigung des NVIDIA-Treibers:** Ein Reboot synchronisiert das Kernel-Modul mit NVML `535.309`, sodass CUDA wieder voll funktionsfähig ist.
2. **Systemd-Setup für AURELIA:** AURELIA wird parallel zum Altbestand in einem eigenen isolierten Pfad (z.B. `/opt/aurelia/`) mit eigenen Ports und Systemd-Units aufgebaut.
3. **PostgreSQL / Timescale Vorbereitung:** Für AURELIA sollte eine frische, RLS-fähige PostgreSQL 16 Instanz mit TimescaleDB und `pgvector` konfiguriert werden.

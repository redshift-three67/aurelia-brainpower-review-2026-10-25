# 03 — Ist-Analyse Server M G1 (2026-08-25, live verifiziert)

**Geprüft:** `185.242.115.210` (`root3091.ipp-srv.net`), User `klaus999`, ausschließlich lesende Kommandos.

---

## 1. Soll/Ist-Abgleich Hardware & OS

| Soll (docs/14-hardware.md) | Ist (verifiziert 2026-08-25) | Status |
|---|---|---|
| AMD Ryzen 5 9600X, 6C/12T, AVX-512 | `AMD Ryzen 5 9600X`, 12 CPUs, Flags enthalten `avx512f/bw/vl/vnni/vbmi2/bf16`, max 8424 MHz | ✅ exakt |
| RTX 4000 SFF Ada 20 GB, kein MIG | `01:00.0 NVIDIA AD104GL [RTX 4000 SFF Ada Generation]` | ✅ exakt |
| 128 GB DDR5 | 123 GiB total, 103 GiB verfügbar | ✅ |
| 2× 1 TB NVMe | nvme0n1 + nvme1n1 als RAID1 (md0 EFI, md1 /boot, md2 swap, md3 ext4 `/`, 666 G frei, 58 % belegt) | ✅ (RAID1 = Spiegel, **keine** zweite Fehlerdomäne — korrekt so geplant) |
| Debian Bookworm | Debian 12, Kernel 6.1.0-51-amd64 | ✅ |
| chrony/NTP als Uhr | `System clock synchronized: yes`, NTP active (chrony auf 127.0.0.1:323) | ✅ |
| TPM-fähiger Keystore | `/dev/tpm0`, `/dev/tpmrm0` vorhanden (root-only) | ✅ verfügbar, noch ungenutzt |
| CP210x-Emitter verfügbar | **kein** `/dev/ttyUSB*`/`ttyACM`, kein `cp210x`-Modul geladen | ✅ konsistent mit „Hardware-Gate zu" — kein Emitter angesteckt |

---

## 2. Verifizierte Betriebsbefunde (Abweichungen vom Soll)

### SRV-01: NVIDIA-Treiber/Library-Mismatch (KRITISCH für Phase 4+)
```
Failed to initialize NVML: Driver/library version mismatch
NVML library version: 535.309   (Debian-Pakete: libcuda1 535.309.01)
NVRM kernel module:  535.261.03 (geladen seit 14.06.2025)
```
- **Ursache:** Unattended-Upgrades haben Userspace-Pakete aktualisiert, Kernel-Modul ist alt geladen.
- **Wirkung:** `nvidia-smi` und jede CUDA-Nutzung scheitern derzeit.
- **Behebung:** Geplanter Reboot (Kernel-Modul 535.309 lädt) → danach Smoke-Test `nvidia-smi -q`. Vorherige Ankündigung an Nutzer der laufenden Alt-Container nötig.

### SRV-02: Kein CUDA-Toolkit
- `nvcc` fehlt; nur Runtime-Bibliotheken (`libcuda1`, `libnvcuvid1`) installiert.
- **Behebung:** Für Phase 3/4: `nvidia-cuda-toolkit` (Debian) oder NVIDIA-Repo mit passender Version; CUDA-Toolkit-Version an Treiber 535 koppeln (CUDA 12.2-kompatibel).

### SRV-03: Alt-System `radiquant4` produktiv belegt Ressourcen
Verifizierte laufende Container (Up, teils seit 3 Wochen):
`radiquant4-api` (Port 8000), `-radi144`, `-radiworks`, `-radimorphic`, `-radiblohm`, `-radithoms`, `-radicopen`, `-postgres` (16-alpine), `-redis-{jobs,cache,locks}`, `-ollama` (11435), `-celery-worker/beat`.
- Zusätzlich host-lokal: PostgreSQL **15** (nicht 16!) auf 127.0.0.1:5432, drei Host-Redis (6379/6380/6381, davon zwei als `dnsmasq`-User — fragwürdige Konfiguration), mehrere Uvicorn-Prozesse auf 8008–8013 (root!), xrdp (3389), Cockpit-artiges 9090, Ollama direkt auf 11434.
- **Konflikt mit Verfassung:** „Nie `/opt/radiquant4` schreiben" wird eingehalten; aber Ports (8000, 8080!, 5432) und Namensräume kollidieren mit AURELIA-Plänen. **Port 8080 ist bereits belegt** — AURELIA-Preview-Port-Konflikt beachten.
- **Risiko:** Uvicorn-Prozesse laufen als **root** (verifiziert in `ps aux`) — Hartungspunkt für Betriebphase.

### SRV-04: Sicherheitsrelevante Offene Ports
`0.0.0.0:25` (Mail), `:80/:443/:8443` (Web), `:8000` (Alt-API, öffentlich!), `:8080`, `:9090`, `:3001`, `:3389` (xrdp, öffentlich), `:6556`. Kein `ufw`/nft-Nachweis in dieser Session geprüft (nachholen).
- **Empfehlung:** Für AURELIA-Pilot: Alt-Port 8000 schließen oder auf 127.0.0.1 binden; xrdp per Firewall auf Admin-IPs beschränken; 8080-Kollision auflösen.

### SRV-05: `/opt`-Struktur bestätigt Heritage-Plan
Vorhanden: `Prototypen/{Radi144, Radimorphic, Referenzen}` (read-only-Wrapping möglich), `radiquant4` (54 Einträge, läuft), `radiquant3`, `radiquant-v5`, `radithoms(-shadowcopies)`, `morphic_v1`, `Zenflow`, `backups`, `Wiederherstellungspunkte`, ein 32-GB-Swapfile in `/opt` (ungewöhnlich, da md2 schon Swap ist).
- `/opt/Prototypen/Radimorphic` entspricht dem ABI-Migrationspfad aus `06-kernel-abi.md` ✅.

---

## 3. Bewertung

Der Server ist **der richtige Server, im richtigen Zustand für Phase 1–2** (Gehäuse/Praxis brauchen keine GPU). Für Phase 3+ sind drei Aufräumarbeiten zwingend: NVML-Sync (SRV-01), CUDA-Toolkit (SRV-02), Port-/Rechte-Hygiene (SRV-03/04). Keiner dieser Punkte ist ein Projektblocker; alle sind mit einem Wartungsfenster lösbar.

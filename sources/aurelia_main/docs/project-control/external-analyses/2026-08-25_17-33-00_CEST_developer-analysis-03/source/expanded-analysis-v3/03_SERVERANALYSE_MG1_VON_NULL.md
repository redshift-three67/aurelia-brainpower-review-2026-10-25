# 03 — Serveranalyse M G1 von Null (185.242.115.210, 2026-08-25 17:33 CEST)

**Zugriff:** SSH `klaus999@185.242.115.210` (Key `vs_code_key`), ausschließlich lesende Kommandos; `sudo -n` nur für Leseabfragen (iptables, fail2ban).  
**Hostname:** `root3091.ipp-srv.net` · **Uptime:** 24 Tage (Boot 2026-08-01 10:51) · **Load:** 0.34/0.28/0.32

---

## 1. Hardware & OS (Soll/Ist)

| Soll (docs/14-hardware.md) | Ist (verifiziert 17:33 CEST) | Status |
|---|---|---|
| Ryzen 5 9600X, 6C/12T, AVX-512 | bestätigt; Flags inkl. `avx512f/bw/vl/vnni/vbmi2/bf16`, max 8424 MHz | ✅ |
| RTX 4000 SFF Ada 20 GB, kein MIG | `01:00.0 AD104GL [RTX 4000 SFF Ada]` | ✅ |
| 128 GB DDR5 | 123 GiB, ~103 GiB verfügbar | ✅ |
| 2× 1 TB NVMe | RAID1: md0(EFI)/md1(/boot)/md2(swap)/md3(ext4 `/`, 1,8 T, 62 % belegt, 667 G frei) — **alle `[UU]` gesund** | ✅ (Belegung wächst: 58 %→62 % seit 14:50) |
| Debian Bookworm | Debian 12.15, Kernel 6.1.0-51-amd64 | ✅ |
| chrony als Uhr | NTP synchronized/active | ✅ |
| TPM-Keystore möglich | `/dev/tpm0`, `/dev/tpmrm0` (root-only) — **ungenutzt** | ⚪ verfügbar |
| CP210x-Emitter | kein `/dev/ttyUSB*`, kein cp210x-Modul | ✅ konsistent mit Hardware-Gate zu |

---

## 2. GPU-Stack

| Prüfung | Ergebnis | Bewertung |
|---|---|---|
| `nvidia-smi` | `Failed to initialize NVML: Driver/library version mismatch` (NVML 535.309 vs. Kernel-Modul 535.261.03, geladen seit 2025-06-14) | ❌ **CUDA derzeit unbenutzbar** |
| Userspace-Pakete | 45 NVIDIA-Pakete, u. a. `libcuda1 535.309.01` | Auto-Update ohne Modul-Reload |
| `nvcc`/Toolkit | nicht installiert | ❌ für Phase 3/4 nötig |
| `nvidia_uvm/drm/modeset` | geladen, 257 Nutzer | Treiber grundsätzlich aktiv |

**Behebung:** Wartungsfenster → Reboot → `nvidia-smi`-Smoke → `nvidia-cuda-toolkit` (an 535/CUDA-12.2 gekoppelt) → `deviceQuery`.

---

## 3. Systemd- & Orchestrierungszustand (**neu in V3**)

- **9 fehlgeschlagene Units**, u. a.: `radiquant4-api.service`, `radiquant4-backup.service`, **sechs** `radiquant4-engine-*.service` (Ports 8008–8013), `radiquant4-runtime-guardian.service`, **`iptables-restore.service`** („XRDP protection").
- **Gleichzeitig laufen** die Docker-Pendants derselben Dienste „Up 3 weeks (healthy)" → **Doppelorchestrierung** (systemd vs. Docker-Restart-Policy) mit verwaisten, fehlerhaften Units.
- 45 laufende Services gesamt.
- Die host-lokalen Uvicorn-Prozesse auf 8008–8013 laufen als **root** (V2-Befund, bestätigt) — hartes Hartungsziel.

**Behebung:** Failed Units disable/mask oder repair; eine Orchestrierungsebene wählen (empfohlen: Docker-Compose oder systemd, nicht beides).

---

## 4. Docker & Speicher (**neu in V3 vertieft**)

| Metrik | Wert | Bewertung |
|---|---|---|
| Images | **235** (17 aktiv) — **200,2 GB**, davon **185,1 GB (92 %) reclaimable** | ❌ massiver Müll; erklärt Disk-Wachstum |
| Volumes | 57 (11 aktiv), 15,0 GB, 5,5 GB reclaimable | ⚪ |
| Build-Cache | 615 Einträge, 3,3 GB reclaimable | ⚪ |
| Container | 15 healthy (`radiquant4-*`), 1 Crashloop (`radiquant4-strapi` — Restart alle ~40 s), mehrereExited | ❌ Strapi seit Monaten im Loop |

**Aktion:** `docker system prune`-Strategie mit Beweissicherung (vorher Images-Liste archivieren — Heritage!), Strapi-Loop beenden (stoppen, bis entschieden).

---

## 5. Sicherheit (**neu in V3; teilweise kritisch**)

| ID | Befund | Schwere |
|---|---|---|
| SRV-06 | **`PermitRootLogin yes`** in sshd_config | KRITISCH |
| SRV-07 | **`klaus999` besitzt `(ALL) NOPASSWD: ALL`** (zusätzlich zur Whitelist) — der Analysezugang ist faktisch Root | KRITISCH |
| SRV-08 | **Klartext-DB-Passwort im Crontab** (`PGPASSWORD=radiquant4_dev … backup.sh`, täglich 03:00) | HOCH |
| SRV-09 | Fail2ban sshd: **23.292 Fehlversuche, 4.622 Bans, 7 aktuell gebannt** — Server steht unter Dauerbeschuss (Internet-exponiert) | HOCH (Kontext) |
| SRV-10 | `iptables-restore.service` failed — aber INPUT policy aktuell `DROP` mit `f2b-sshd`-Chain aktiv; Regel-Persistenz nach Reboot **unklar/fragil** | HOCH |
| SRV-11 | Öffentliche Ports: 25, 80/443/8443, **8000 (Alt-API öffentlich!)**, 8080, 9090, 3001, **3389 (xRDP öffentlich)**, 6556 | HOCH |
| SRV-12 | Host-Postgres nur **15** (Soll: 16/Timescale) auf 127.0.0.1:5432; PG16 nur im Docker-Netz | MITTEL |
| SRV-13 | Drei Host-Redis-Instanzen (6379/6380/6381), zwei davon unter `dnsmasq`-User — Konfigurationsfehler-Geruch | MITTEL |
| SRV-14 | Snap-Pakete (claudeai-desktop, intellij) + Chrome-Debug-Ports 9224/9225 auf localhost — Desktop-Restanten auf einem Produktionsserver | MITTEL (Hygiene) |
| SRV-15 | **Kein AURELIA-Footprint** (`/opt/aurelia`, `~/aurelia` existieren nicht) | ✅ erwartungskonform |

**Backups (verifiziert):** `/etc/cron.d/`: `radionics-backup`, `radionics-revision-backup`, `radiquant3-backup`, `certbot`, `mdadm`, `sysstat`; User-Cron: 2×radiquant4-Backup + Redis alle 6 h nach `/opt/radiquant4/backups`. **Alle Backups liegen auf demselben Server** (md3) — es existiert **keine Offsite-Sicherung**: WV01 ist damit nicht nur offen, sondern aktuell **unerfüllt** (RPO 15 min etc. rein deklarativ).

---

## 6. `/opt`-Struktur (Heritage-Abgleich)

Bestätigt: `Prototypen/{Radi144, Radimorphic, Referenzen}` (ABI-Migrationspfad ✅), `radiquant4` (läuft, unantastbar), ferner `radiquant3`, `radiquant-v5`, `radithoms(-shadowcopies)`, `morphic_v1`, `Zenflow`, `backups/radiquant4`, `Wiederherstellungspunkte/{radiquant-hybrid, -recovery-template}`, 32-GB-Swapfile in `/opt` (doppelt zu md2-Swap — aufräumen).

---

## 7. Server-Gesamtwertung

Die **Hardware ist exakt die spezifizierte und gesund**. Der **Betriebszustand entspricht nicht dem P1-Soll** der Vorbereitungsspezifikation (Härtung, Backup-Offsite, Dienstrechte). Vor dem ersten Art.-9-Datensatz ist eine **konsolidierte Serverhärtung** (Dokument 07, Plan SH-1…SH-8) zwingend; sie ist mit ~2–3 Tagen Arbeit + einem Wartungsfenster erreichbar.

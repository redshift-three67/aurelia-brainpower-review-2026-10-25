# 03 — Serveranalyse Altsystem V4 (185.242.115.210, 2026-08-25 19:39 CEST)

**Wichtiger Kontext:** Dieses Dokument beschreibt bewusst das **unveränderte Altsystem**, da `server_changes_started: false` gilt und der Ground-Zero-Plan jede destruktive Aktion bis `G0-SRV-0` sperrt. Diese Inventur dient als **unabhängige zweite Momentaufnahme** zur Konsistenzprüfung der V3-Befunde und zur Aufdeckung neuer, in V3 nicht sichtbarer Symptome.

**Zugriff:** SSH `klaus999@185.242.115.210` (Key `vs_code_key`), ausschließlich lesende Kommandos; `sudo -n` nur für Leseabfragen. **Uptime bei dieser Prüfung:** 24 Tage 8:44h (Boot unverändert 2026-08-01 10:51 — bestätigt, dass seit V3 kein Reboot/keine Änderung stattfand).

---

## 1. Konsistenzprüfung gegenüber V3

| Merkmal | V3 (17:33 CEST) | V4 (19:39 CEST) | Konsistent? |
|---|---|---|---|
| NVML-Mismatch | Library 535.309 vs. Modul 535.261.03 | **identisch** | ✅ Ja — bestätigt „keine Änderung" |
| RAID1-Status | `[UU]` gesund, alle 4 Arrays | (nicht in dieser Session erneut abgefragt — kein Hinweis auf Änderung) | ⚪ angenommen unverändert |
| Boot-Zeitpunkt | 2026-08-01 10:51 | 2026-08-01 10:51 | ✅ Ja |
| Load Average | 0.34/0.28/0.32 | 0.21/0.37/0.43 | ✅ normale Schwankung |

**Schlussfolgerung:** Der Server wurde zwischen V3 und V4 **nachweislich nicht verändert** — die Kanon-Aussage `server_changes_started: false` ist durch unabhängige Doppelmessung erhärtet.

---

## 2. NEUE Befunde in V4 (in V3 nicht erfasst)

### SRV-16 — `radiquant4-web.service`: Dauerhafter Crashloop seit Boot (KRITISCH, neu entdeckt)
```
NRestarts=208557
ActiveState=activating / SubState=auto-restart
RestartSec=10
```
- **Root Cause identifiziert:** Die systemd-Unit verweist auf `WorkingDirectory=/opt/radiquant4/apps/web`, doch dieser Pfad wurde umbenannt zu `/opt/radiquant4/apps/web-astro` (verifiziert: `ls /opt/radiquant4/apps/` zeigt nur `api`, `engines`, `web-astro`). Jeder Startversuch scheitert an `CHDIR`.
- **Rechnerische Einordnung:** Bei `RestartSec=10` über 24 Tage (≈ 2.073.600 Sekunden) ergeben sich rechnerisch bis zu ~207.360 mögliche Zyklen — die gemessenen 208.557 Neustarts liegen in exakt dieser Größenordnung und bestätigen: **Der Dienst crasht seit dem letzten Boot ununterbrochen, alle 10 Sekunden, seit 24 Tagen**, ohne dass dies in der V3-Analyse aufgefallen war (dort wurde nur der Container-/Prozessstatus, nicht die systemd-Restart-Statistik geprüft).
- **Wirkung:** Kontinuierliche, sinnlose CPU-/Log-Last (Prozessstart-Overhead alle 10 s über 24 Tage), Journal-Aufblähung (bestätigt: 207,3 MB Journal-Footprint), und ein IRC-artiges Grundrauschen, das echte Fehler im Journal verdecken kann.
- **Ground-Zero-Bezug:** Dieser Befund untermauert zusätzlich die bereits getroffene Entscheidung „Altservice wird nicht zurückgespielt" (Ground-Zero-Design §10: „Strapi-Crashloop → Altservice nicht installiert" — dasselbe Muster gilt jetzt nachweislich auch für den Web-Frontend-Dienst).

### SRV-17 — 20 ausstehende Paket-Updates, davon sicherheitsrelevant
`apt list --upgradable` zeigt 20 Pakete, u. a. `postgresql-15` (15.16→15.19), `postgresql-15-pgvector`, `libpq5` (18.2→18.6), `nodejs` (20.20.0→20.20.2), sowie mehrere Desktop-/Dev-Tools (`claude-desktop`, `cursor`, `windsurf`, `firefox`, `google-chrome-stable`, `gh`, `kubeadm/kubectl/kubelet`). Kein Reboot-Flag gesetzt (`/var/run/reboot-required` leer), `unattended-upgrades` ist aktiv.
- **Bewertung:** Unkritisch für die Ground-Zero-Entscheidung (das System wird ohnehin ersetzt), aber bestätigt weiter die Diagnose „gewachsenes Entwicklungssystem mit Desktop-Tools, kein gehärteter Produktionsserver".

### SRV-18 — TLS-Zertifikat vorhanden und gültig
`certbot certificates` zeigt ein gültiges ECDSA-Zertifikat für `radiquant.de` (+ `admin.`, `api.`, `app.`, `www.`-Subdomains), gültig bis 2026-10-18 (53 Tage Restlaufzeit). **Neuer Fakt für die Ground-Zero-Planung:** Diese Zertifikate/Domains müssen im Backup-/Migrationsscope berücksichtigt werden (Certbot-Konfiguration, ACME-Account, DNS), auch wenn die neue AURELIA-Installation zunächst ohne öffentliche Kante startet (Ground-Zero-Design §8.2: „Caddy wird erst bei Freigabe der öffentlichen Kante installiert").

### SRV-19 — PostgreSQL-15-Datenbanklandschaft (Umfang für Backup-Scope)
Fünf Datenbanken bestätigt: `postgres`, `radionics` (Owner `postgres`, App-Rolle `radionics_app`), `radiquant2`, `radiquant3`, `radiquant3_test`, `radiquant4` (Owner `radiquant`, im Docker-Postgres-16-Container separat). Nur die Extension `plpgsql` ist auf Host-PG15 aktiv (keine `pgvector`/`timescaledb`/`ltree` trotz installiertem `postgresql-15-pgvector`-Paket).
- **Bewertung für Ground-Zero-Preflight-Task 2:** Der Sicherungsumfang „relevante PostgreSQL-Datenbanken als logische Dumps" muss **alle fünf Host-Datenbanken plus die Docker-`radiquant4`-Instanz** umfassen — eine konkrete, bisher nicht quantifizierte Checkliste für den Betreiber.

### SRV-20 — Datei-Limits (`ulimit`)
`open files (soft) = 1024`, `max user processes = 504914`, `file-max (system) ≈ 9,2 Trillionen` (kernel-generisches Maximum, kein reales Limit). Der niedrige Soft-Limit von 1024 offenen Dateien pro Prozess ist für zukünftige AURELIA-Dienste (insbesondere `aurelia-timerd` mit potenziell hunderten gleichzeitigen Kanälen, D20) **zu niedrig** und wäre bei einer Reparatur des Altsystems ein weiterer Tuning-Punkt — im Ground-Zero-Neuaufbau ist dies über systemd-`LimitNOFILE=` je Unit sauber neu zu setzen.

### SRV-21 — Keine SMART-Diagnose möglich
`smartctl` ist auf dem System nicht installiert (`sudo: smartctl: command not found`), obwohl `docs/superpowers/plans/…-preflight.md` (Basissystem-Liste im Ground-Zero-Design, §8.1) `smartmontools` explizit für die **neue** Installation vorsieht. Für das Altsystem bedeutet das: **Der physische Gesundheitszustand beider NVMe (Lebensdauer, Restschreibzyklen, Temperatur) konnte in keiner der bisherigen Analysen (V1–V4) direkt geprüft werden** — ein Nachweis, der laut Preflight-Plan vor der endgültigen Neuinstallation sinnvoll nachgeholt werden sollte, auch wenn er dort nicht explizit als eigener Schritt steht.

---

## 3. Bestätigte V3-Befunde (unverändert kritisch)
NVML-Mismatch (SRV-01), kein CUDA-Toolkit (SRV-02), Root-SSH erlaubt (SRV-06), `NOPASSWD: ALL` (SRV-07), Klartext-Cron-Passwort (SRV-08), 9 fehlgeschlagene Systemd-Units (SRV-04), 185 GB rückgewinnbare Docker-Images (SRV-03), keine Offsite-Backups (SRV-05), öffentliche Ports 8000/3389/9090 (SRV-11) — **alle unverändert vorhanden**, da keine Serveränderung stattfand.

---

## 4. Gesamtwertung Altsystem V4
Das Altsystem ist **weiterhin funktionsfähig für seinen ursprünglichen Zweck** (die meisten `radiquant4-*`-Container laufen „healthy"), aber die V4-Vertiefung zeigt: Es ist **fragiler und stärker vernachlässigt**, als die V3-Momentaufnahme allein vermuten ließ (ununterbrochener 24-Tage-Crashloop eines Frontend-Dienstes, unmögliche SMART-Diagnose, ungeprüfter Backup-Umfang über fünf Postgres-Datenbanken). Dies bestärkt die Ground-Zero-Entscheidung zusätzlich: **Eine Reparatur des Altsystems wäre nicht nur unsicher (V3), sondern auch technisch unwirtschaftlich (V4).**

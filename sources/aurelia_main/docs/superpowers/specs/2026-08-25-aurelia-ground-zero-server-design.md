# AURELIA – Ground-Zero-Serverdesign

Stand: 2026-08-25, Europe/Berlin

Status: vom Betreiber grundsätzlich freigegeben

Freigabekontext: Der Betreiber bestätigte am 25. August 2026 IPMI/BMC mit
Remote-KVM und Virtual Media, ausreichende Anbieter-USV-Kapazität, ein vom
Server getrenntes Backupsystem sowie DDoS-Schutz durch den Anbieter. Die
physische Neuinstallation bleibt bis zum bestandenen Gate `G0-SRV-0`
gesperrt.

Zielbranch: `codex/aurelia-vorbereitung`

## 1. Zweck und normativer Vorrang

Diese Spezifikation definiert den Neuaufbau des einzigen AURELIA-Originservers
M G1. Sie ergänzt die freigegebene Vorbereitungsspezifikation vom 24. August
2026 und ersetzt ausschließlich deren Annahmen über Debian/Bookworm und die
damals dokumentierte Laufwerksgröße.

Für die neue Serverbasis gelten ab dieser Freigabe:

- Ubuntu Server 24.04.4 LTS statt Debian Bookworm;
- zwei physische 2-TB-NVMe statt zwei 1-TB-NVMe;
- ein eigenes Infrastruktur-Gate vor AUDIT-02 und vor weiterer Produktarbeit;
- kein Wiederherstellen der alten Installation als Systemabbild;
- weiterhin ausschließlich synthetische Daten, kein CUDA-Toolkit, kein USB
  und keine realen Klientendaten bis zu ihren späteren Einzelgates.

Historische Spezifikationen und externe Analysen bleiben für Provenienz
unverändert. Wo sie Debian, 2×1 TB oder direkte Sofortreparaturen der alten
Installation nennen, sind diese Aussagen nicht mehr ausführbar.

## 2. Verifizierte und vom Betreiber bestätigte Ausgangslage

### 2.1 Read-only verifizierte Hardware

| Komponente | Stand |
|---|---|
| System | Supermicro Super Server, Bare Metal |
| Mainboard | Supermicro H13SAE-MF |
| CPU | AMD Ryzen 5 9600X, 6C/12T, AVX-512, ECC-fähig bei passender Bestückung |
| GPU | NVIDIA RTX 4000 SFF Ada, 20 GB, kein MIG |
| RAM | 128 GB DDR5; aktiver ECC-Schutz noch nicht bewiesen |
| Storage | 2× WD_BLACK SN850X 2 TB, jeweils ca. 1,8 TiB sichtbar |
| Netzwerk | 2× Intel I210 1 Gbit/s plus dedizierter BMC-Port |
| Management | ASPEED AST2600/IPMI, TPM2, UEFI |
| Aktueller Bootstatus | UEFI; Secure Boot war deaktiviert, Plattform im Setup Mode |

Das Board und der Ryzen unterstützen ECC-UDIMM. Die bisherige DMI-Ausgabe
meldete jedoch `Memory Error Correction Type: None`. Der aktuelle RAM darf
daher erst nach Teilenummer-, BIOS- und EDAC/RAS-Nachweis als ECC gelten.

Die SN850X ist laut Hersteller eine Client-/Gaming-SSD. Das offizielle
Datenblatt nennt keine Enterprise-Power-Loss-Protection. Sie wird deshalb
nicht als PLP-geschützter Datenbankdatenträger eingestuft. Die bestätigte USV
reduziert das Risiko eines Netzausfalls, ersetzt aber keine PLP bei Netzteil-,
Backplane-, Firmware- oder Hostfehlern.

### 2.2 Betreiberbestätigte Infrastruktur

| Voraussetzung | Status | Nachweis im Gate |
|---|---|---|
| IPMI/BMC-Webzugang | bestätigt | Login und Netztrennung prüfen |
| Remote-KVM | bestätigt | Bootmenü und Konsoleneingabe prüfen |
| Virtual Media | bestätigt | ISO einbinden und lesend booten |
| Anbieter-USV | bestätigt | Kapazität, Monitoring und Shutdownpfad dokumentieren |
| Eigenes Backupsystem außerhalb M G1 | bestätigt | Restore-Nachweis erforderlich |
| Anbieter-DDoS-Schutz | bestätigt | Leistungsumfang dokumentieren; Hostfirewall bleibt Pflicht |

Diese Angaben sind Voraussetzungen, aber noch keine Abnahmen. Insbesondere
wird das Backupsystem erst akzeptiert, nachdem mindestens eine relevante
Sicherung tatsächlich wiederhergestellt und geprüft wurde.

## 3. Betriebssystementscheidung

### 3.1 Verbindliches Installationsabbild

```text
Distribution: Ubuntu Server 24.04.4 LTS (Noble Numbat)
Architektur:  AMD64 / x86_64
ISO-Datei:    ubuntu-24.04.4-live-server-amd64.iso
Bootmodus:    UEFI
Quelle:       https://releases.ubuntu.com/releases/24.04.4/
```

Zulässig ist nur das offizielle Releaseabbild. Daily Builds,
anbieterangepasste Images und fremde Mirror-Abbilder sind ausgeschlossen. Vor
Virtual-Media-Boot werden SHA-256 und die signierte Prüfsummenquelle gegen die
offizielle Ubuntu-Veröffentlichung geprüft.

### 3.2 Begründung

Ubuntu 24.04.4 bildet gegenwärtig die stabilste gemeinsame Basis für:

- die offiziell unterstützte ChatGPT-Linux-App mit lokalen Dateien und Codex;
- die offiziell unterstützte Codex-CLI unter Linux;
- NVIDIA/CUDA-Unterstützung für Ubuntu 24.04.4;
- den kanonischen AURELIA-Datenbankstand PostgreSQL 16 aus dem Ubuntu-Archiv;
- die von Timescale dokumentierte Ubuntu-24.04-Plattform;
- einen gegenüber Ubuntu 26.04 länger erprobten Kernel-/Treiber-/Desktopstack.

Ubuntu 26.04 LTS ist nicht grundsätzlich ungeeignet. Es führt für AURELIA
jedoch aktuell Kernel 7.0, PostgreSQL 18 und eine jüngere Integrationsbasis ein.
Debian 13 ist ebenfalls technisch möglich, bietet für den festgelegten
Desktop-, OpenAI-, NVIDIA- und PostgreSQL-16-Pfad aber keinen hinreichenden
Vorteil gegenüber Ubuntu 24.04.4.

Ubuntu 24.04 erhält Standard-Sicherheitswartung bis Mai 2029 und kann mit
Ubuntu Pro/ESM bis Mai 2034 abgesichert werden. Eine spätere Migration auf
Ubuntu 26.04 wird als eigenes, getestetes LTS-Upgrade geplant und nicht mit dem
Ground-Zero-Aufbau vermischt.

## 4. Firmware- und Bootgrundlage

Vor der Betriebssysteminstallation gilt:

1. BMC- und BIOS-Versionen werden inventarisiert.
2. Firmwareupdates erfolgen nur bei dokumentierter Notwendigkeit, über
   Herstellerquelle und mit funktionsfähigem IPMI-Rückweg.
3. UEFI-only, TPM2 und IOMMU werden aktiviert.
4. Secure Boot wird mit Hersteller-/Microsoft-UEFI-Schlüsseln aus dem Setup
   Mode in den Deployed Mode überführt, sofern der kontrollierte Probelauf mit
   Ubuntu- und NVIDIA-signierten Modulen erfolgreich ist.
5. Overclocking, Precision Boost Overdrive, Curve Optimizer und aggressive
   EXPO-Profile bleiben aus. Speicher läuft zunächst mit validierter
   JEDEC-/Herstellerkonfiguration.
6. `Restore on AC Power Loss` wird auf den zum Betriebskonzept passenden
   automatischen Wiederanlauf gesetzt.
7. BMC und beide Host-NICs erhalten getrennte Rollen; BMC wird niemals aus dem
   öffentlichen Internet erreichbar.
8. Beide Netzteile werden geprüft. Wenn möglich, liegen sie auf getrennten
   PDU-/Versorgungspfaden innerhalb der Anbieter-USV.

Secure Boot ist ein Zielkriterium, darf aber nicht durch unsignierte
NVIDIA-Runfile-Installationen unterlaufen werden. Schlägt der signierte
Treiberpfad fehl, stoppt das Gate; Secure Boot wird nicht still deaktiviert.

## 5. Storage-, RAID- und Verschlüsselungsdesign

### 5.1 Schichten

```text
NVMe A                         NVMe B
├─ EFI A                       ├─ EFI B
├─ RAID1-Mitglied /boot        ├─ RAID1-Mitglied /boot
└─ RAID1-Mitglied System       └─ RAID1-Mitglied System
              │
              ▼
           mdraid1
              │
              ▼
             LUKS2
              │
              ▼
          LVM vg_aurelia
```

Die EFI-Systempartitionen bleiben getrennt und erhalten jeweils einen
bootfähigen, geprüften GRUB-Eintrag. `/boot` liegt gespiegelt auf mdraid1. Der
restliche Systembereich liegt auf einem zweiten mdraid1, darauf LUKS2, darin
LVM. Damit sind Root, Home, Logs, Swap, Datenbank und AURELIA-Daten im
Ruhezustand verschlüsselt.

Die geführte experimentelle TPM-FDE-Option des Ubuntu-24.04-Desktopinstallers
wird nicht verwendet. Canonical dokumentiert für diesen Modus unter anderem
fehlende Unterstützung externer Kernelmodule wie NVIDIA. Stattdessen wird
klassisches LUKS2 mit dokumentiertem Recovery-Verfahren aufgebaut.

### 5.2 Zielgrößen

| Logical Volume | Startgröße | Dateisystem/Zweck |
|---|---:|---|
| `lv_root` | 120 GiB | ext4, `/` |
| `lv_home` | 80 GiB | ext4, `/home` |
| `lv_log` | 64 GiB | ext4, `/var/log` |
| `lv_postgres` | 384 GiB | ext4, `/var/lib/postgresql` |
| `lv_aurelia` | 768 GiB | ext4, `/srv/aurelia` |
| `lv_build` | 192 GiB | ext4, reproduzierbare Build-/Containerdaten |
| `lv_swap` | 32 GiB | Swap innerhalb LUKS2 |
| nicht zugeordnet | mindestens 15 % | kontrollierte spätere Erweiterung |

Die Größen werden vor dem destruktiven Partitionsschritt gegen die tatsächlich
gemeldeten Sektorgrößen und nutzbaren Kapazitäten berechnet. Es gibt kein
ungeprüftes Kopieren von Gerätenamen aus dieser Spezifikation. Destruktive
Befehle verwenden ausschließlich zuvor protokollierte `/dev/disk/by-id/`-
Bezeichner.

### 5.3 Entsperrung und Wiederherstellung

- LUKS2 erhält eine starke Recovery-Passphrase und einen separat verwahrten
  Recovery-Key.
- Nach bestandenem Secure-Boot-Pfad kann TPM2-Auto-Unlock kontrolliert
  ergänzt werden.
- Firmware- und Bootänderungen werden nur durchgeführt, wenn der Recovery-Key
  verfügbar und über IPMI eingebbar ist.
- Ein fehlgeschlagenes Entsperren darf keine AURELIA-Dienste mit unvollständigen
  Datenpfaden starten.
- Der Recovery-Test umfasst Normalboot, Recovery-Key und Bootfähigkeit über
  beide EFI-/NVMe-Pfade.

## 6. Benutzer-, Desktop- und Codex-Trennung

Ubuntu Server wird zuerst ohne GUI installiert. Erst nach grüner Serverbasis
folgen minimales GNOME, GDM und XWayland.

| Identität | Zweck | Verbot |
|---|---|---|
| `aurelia-admin` | menschliche Administration, sudo mit Passwort | kein Dauerbetrieb als root |
| `aurelia-dev` | GNOME, ChatGPT/Codex, Repository, synthetische Daten | kein sudo, keine Produktivdaten, keine Dienstsecrets |
| `aurelia-app` | Web-/Control-Plane | kein Login, kein freier Datenbank-Superuser |
| `aurelia-compute` | spätere Compute-Dienste | kein Desktop, kein freier Internetzugang |
| `aurelia-backup` | definierte Sicherungsoperationen | keine interaktive Administration |
| `postgres` | PostgreSQL | kein Remote-Login |

Direkte Root-SSH-Anmeldung, SSH-Passwörter, `NOPASSWD: ALL`, gemeinsame
Administratorkonten und Mitgliedschaft von Menschen in einer klassischen
Docker-Gruppe sind ausgeschlossen.

ChatGPT/Codex ist ein cloudverbundenes Entwicklungswerkzeug. Sein Benutzer
darf nur Repositorydaten und synthetische Testdaten lesen. Unix-Rechte,
getrennte Gruppen und getrennte Datenpfade verhindern Zugriff auf:

- Art.-9-/Klientendaten;
- PostgreSQL-Datendateien und produktive Datenbank-Credentials;
- `/srv/aurelia`-Produktivobjekte und Tenant-Keys;
- systemd Credentials und Backupschlüssel;
- Hardwaregeräte für GPU- oder Emitterbetrieb.

Die RTX 4000 wird nicht als Desktop-GPU verwendet. GNOME und Remote Desktop
laufen über AMD-iGPU, ASPEED oder Software-Rendering. Dadurch bleibt das
kanonische 2/16/2-GB-VRAM-Budget unverändert.

## 7. Netzwerk- und Zugriffskonzept

### 7.1 Zonen

1. **BMC-Management:** dedizierter IPMI-Port, Management-VLAN, kein Internet.
2. **Host-Management:** WireGuard/VPN, administrative SSH-Schlüssel,
   optionaler Desktop nur durch diesen Tunnel.
3. **Produktion:** später ausschließlich Reverse Proxy auf TCP 80/443.
4. **Intern:** PostgreSQL, Redis/Valkey, Monitoring, Metrics, interne APIs und
   Daemons nur Loopback oder dediziertes internes Interface.

Während des Bootstraps darf SSH zeitlich begrenzt auf eine bekannte
Managementquelle eingeschränkt werden. Nach WireGuard-Abnahme ist SSH nicht
öffentlich. RDP/xRDP/GNOME Remote Desktop wird niemals direkt aus dem Internet
erreichbar.

DDoS-Schutz des Anbieters schützt den Upstream, ersetzt aber weder
Hostfirewall noch Rate Limits, Authentifizierung oder anwendungsbezogene
Abwehr. Auf dem Host gilt ein einziges versioniertes nftables-Regelwerk.

## 8. Dienste und Lieferkette

### 8.1 Basissystem

Vorgesehen sind nur notwendige Systemkomponenten, darunter:

- mdadm, LVM2 und cryptsetup;
- AppArmor;
- chrony;
- auditd und persistentes, größenbegrenztes Journaling;
- WireGuard und nftables;
- smartmontools und nvme-cli;
- Monitoring für RAID, NVMe, Temperatur, USV und fehlgeschlagene Units;
- kontrollierte Sicherheitsupdates ohne automatischen Neustart.

### 8.2 AURELIA-Laufzeit

- PostgreSQL 16 wird nativ und als eigene Dienstidentität betrieben.
- Erweiterungen wie pgvector, ltree und TimescaleDB werden erst nach
  Versions- und Migrationsprüfung aktiviert.
- Caddy wird erst bei Freigabe der öffentlichen Kante installiert.
- Redis/Valkey, NATS, MinIO und rootless Podman werden nur installiert, wenn
  ein freigegebener Architekturbaustein sie benötigt.
- Kubernetes und eine vollständige Microservice-Landschaft bleiben
  ausgeschlossen.
- Systemd ist die primäre Orchestrierungs- und Timerquelle.
- Secrets stehen nicht in Cron, Unit-Dateien, Environment-Dateien im
  Repository oder Prozessargumenten. Vorgesehen sind rootgeschützte systemd
  Credentials beziehungsweise ein später freigegebener Secret Store.

### 8.3 NVIDIA und CUDA

Ground Zero installiert zunächst ausschließlich einen zur Ubuntu-/Secure-
Boot-Basis passenden, paketverwalteten NVIDIA-Treiber. Runfile-Installer sind
ausgeschlossen.

Abnahme der Treiberbasis:

- Kernelmodul und Userspace-Bibliotheken besitzen dieselbe Version;
- `nvidia-smi` funktioniert vor und nach einem Reboot;
- die RTX 4000 ist nicht vom Desktop belegt;
- keine NVML-Mismatch-Meldung;
- keine fehlgeschlagene NVIDIA-Systemd-Unit;
- noch kein `nvcc` und kein CUDA-Toolkit.

Die konkrete CUDA-Toolkitversion wird erst am späteren `GATE-CUDA` gegen alle
freigegebenen Prototypen, Bibliotheken, Compiler und Reproduzierbarkeitstests
festgelegt.

## 9. Backup-, Restore- und Geheimnisstrategie

`G0-SRV-0` verlangt vor jeder Löschung:

1. mindestens zwei verifizierte Kopien außerhalb M G1;
2. mindestens eine verschlüsselte Offline- oder EU-Offsite-Kopie;
3. SHA-256-Manifest der gesicherten Projektartefakte;
4. Git-Bundle beziehungsweise vollständige Branch-/Tag-Sicherung;
5. PostgreSQL-Dumps einschließlich Rollen/Globals, sofern noch relevante
   Datenbanken existieren;
6. Prototypen, Quellcode und `docs/project-control`;
7. einen echten Restore mindestens eines Repositorys, eines Datenbankdumps
   und einer repräsentativen Datei auf ein vom Ursprung getrenntes Ziel;
8. protokolliertes Ergebnis mit Zeitpunkt und verantwortlicher Person.

Die alte Systemkonfiguration wird nur als Quarantäne-/Evidenzbestand gesichert.
Nicht automatisch zurückgespielt werden `/etc`, sudoers, sshd-Konfiguration,
Crontabs, Systemd-Units, Docker-Images, ChatGPT/Codex-Tokens oder alte
Credentials.

Das in V3 sichtbar gewordene Datenbankpasswort gilt als kompromittiert. Es
wird nicht wiederverwendet und nach Ground Zero durch neue, zufällige,
rollengetrennte Secrets ersetzt. Private SSH-Schlüssel vom alten Server werden
nicht übernommen; Adminzugänge erhalten neue Schlüssel oder geprüfte
Hardware-Keys.

## 10. Übernahme der V3-Befunde als Abnahmetests

| V3-Befund | Ground-Zero-Abnahme |
|---|---|
| Root-SSH und Passwortauthentifizierung | Root-SSH aus, Passwortauthentifizierung aus |
| `NOPASSWD: ALL` | keine Regel vorhanden |
| Klartext-DB-Secret in Cron | alte Secrets rotiert; keine Secrets in Cron |
| Doppelorchestrierung | genau eine autoritative Unit je Dienst |
| Docker-Gruppe mit Rootwirkung | kein klassischer Docker-Daemon/-Gruppenzugang |
| 23.292 SSH-Fehlversuche | SSH nicht öffentlich; VPN/Allowlist; Fail2ban nur ergänzend |
| kein Offsite-Nachweis | isolierter Restore bestanden |
| 200 GB Docker-Bestand | Altimages nicht zurückgespielt |
| NVML-Mismatch | paketverwalteter, rebootgetesteter Treiberstack |
| Strapi-Crashloop | Altservice nicht installiert |
| öffentliches xRDP/Port 8000 | keine öffentlichen Verwaltungs-/Alternativports |
| fehlgeschlagene Units | `systemctl --failed` leer |

Die acht Root-Passwortanmeldungen vom 19. und 21. August wurden vom Betreiber
als eigene autorisierte Einrichtungszugriffe bestätigt. Sie gelten daher nicht
als nachgewiesener Sicherheitsvorfall. Die unsichere Root-/Passwortfähigkeit
der Altinstallation bleibt trotzdem ein zu beseitigender Befund.

## 11. Gatefolge

| Gate | Ziel | Stop-Bedingung |
|---|---|---|
| `G0-SRV-0` | Backup und Restore | kein nachgewiesener Restore |
| `G0-SRV-1` | IPMI/KVM/Virtual Media | kein unabhängiger Recoveryzugang |
| `G0-SRV-2` | Hardware/Firmware/UEFI | unklare Geräte, defekter RAID-/NVMe-/RAM-Status |
| `G0-SRV-3` | RAID1/LUKS2/LVM-Installation | Geräte-ID oder Layout nicht zweifach bestätigt |
| `G0-SRV-4` | Boot/Encryption/Recovery | ein NVMe-/Recoverypfad nicht bootfähig |
| `G0-SRV-5` | Identitäten/SSH/VPN/Firewall | Root/Passwort/NOPASSWD/öffentliche Adminports |
| `G0-SRV-6` | minimales GNOME/Codex | Codex kann Produktivdaten oder sudo erreichen |
| `G0-SRV-7` | NVIDIA-Baseline | NVML-/Modulfehler oder Desktop belegt RTX |
| `G0-SRV-8` | Security/Logging/Updates | AppArmor/Audit/Zeit/Updates nicht nachgewiesen |
| `G0-SRV-9` | PostgreSQL-16-Basis | unsicheres Netzwerk, falsche Rechte oder fehlende Checksums |
| `G0-SRV-10` | Offsite-Backup/Restore | RPO/RTO nicht praktisch geprüft |
| `G0-SRV-11` | selektiver Projekt-Restore | Altservices oder Altsecrets werden aktiviert |
| `G0-SRV-12` | Gesamtbaseline | offene High/Critical-Befunde oder fehlende Reboot-/Soaktests |

Kein Gate wird durch Zeitdruck oder einen pauschalen Betreiberzugang
übersprungen. Ein Fehlschlag stoppt die Folge, ohne das nächste Teilsystem zu
aktivieren.

## 12. Abnahmekriterien der Gesamtbaseline

`G0-SRV-GROUND-ZERO` ist erst grün, wenn mindestens nachgewiesen sind:

- verifizierte offizielle ISO und vollständige Installationsprovenienz;
- UEFI, TPM2, angestrebter Secure-Boot-Pfad und Recovery-Key;
- beide EFI-/NVMe-Bootpfade und gesundes RAID1;
- LUKS2 für Root, Home, Logs, Swap, Datenbank und AURELIA-Daten;
- dokumentierter ECC-Status; bei Non-ECC ein explizites Vor-Art.-9-
  Beschaffungs-/Risikogate;
- USV-Monitoring und getesteter geordneter Shutdownpfad;
- keine Root-SSH-, Passwort-SSH- oder NOPASSWD-ALL-Fähigkeit;
- nur freigegebene Netzwerkports;
- IPMI getrennt und nicht öffentlich;
- AppArmor aktiv, Audit/Logs/Zeit synchron, keine fehlgeschlagenen Units;
- NVIDIA-Treiber vor/nach Reboot fehlerfrei, noch kein CUDA-Toolkit;
- PostgreSQL 16 nur intern und mit Datenchecksums;
- mindestens ein vollständiger externer Restore;
- neue Secrets, keine Altcredentials;
- Quellcode nur selektiv und hashgeprüft wiederhergestellt;
- dokumentierter Reboot-, Last-/Soak- und Recovery-Test;
- weiterhin `data_class=synthetic`, CUDA/USB/Art. 9 gesperrt.

Erst danach wird AUDIT-02 wieder aufgenommen. Ground Zero löst die in V3
festgestellten Codeprobleme nicht: Typecheck, Tests und Kanonbereinigung bleiben
eigene, nachgelagerte Arbeitspakete.

## 13. Externe Primärquellen

- Ubuntu 24.04.4 Release:
  <https://releases.ubuntu.com/releases/24.04.4/>
- Ubuntu Lifecycle:
  <https://ubuntu.com/about/release-cycle>
- OpenAI ChatGPT Desktop für Linux:
  <https://learn.chatgpt.com/docs/linux/linux-app>
- OpenAI Codex CLI:
  <https://learn.chatgpt.com/docs/codex/cli>
- NVIDIA CUDA Linux Support:
  <https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html>
- Ubuntu 24.04 Release Notes, TPM-FDE-Einschränkungen:
  <https://documentation.ubuntu.com/release-notes/24.04/>
- Ubuntu PostgreSQL 16:
  <https://packages.ubuntu.com/noble/database/postgresql>
- TimescaleDB Linux Support:
  <https://docs.timescale.com/self-hosted/latest/install/installation-linux/>
- Supermicro H13SAE-MF:
  <https://www.supermicro.com/en/products/motherboard/h13sae-mf>
- AMD Ryzen 5 9600X:
  <https://www.amd.com/en/products/processors/desktops/ryzen/9000-series/amd-ryzen-5-9600x.html>
- WD_BLACK SN850X Datenblatt:
  <https://documents.westerndigital.com/content/dam/doc-library/en_us/assets/public/western-digital/product/internal-drives/wd-black-ssd/data-sheet-wd-black-sn850x-nvme-ssd.pdf>
- PostgreSQL WAL Reliability:
  <https://www.postgresql.org/docs/16/wal-reliability.html>

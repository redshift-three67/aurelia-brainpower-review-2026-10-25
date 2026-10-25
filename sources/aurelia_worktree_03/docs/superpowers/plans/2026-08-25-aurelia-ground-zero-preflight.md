# AURELIA Ground-Zero Preflight Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Die bestehende M-G1-Installation ohne Schreibzugriff so vollständig absichern und verifizieren, dass anschließend ein separater destruktiver Installationsplan ohne Datenverlust- oder Recovery-Blindstelle freigegeben werden kann.

**Architecture:** Der Preflight endet vor jeder NVMe-Veränderung. Er kombiniert einen extern nachgewiesenen Restore, eine letzte read-only Hostinventur, eine kryptografisch geprüfte Ubuntu-ISO und einen IPMI-/Virtual-Media-Probelauf. Erst die gemeinsame Abnahme von `G0-SRV-0`, `G0-SRV-1` und `G0-SRV-2` erzeugt die unveränderliche Geräte- und Recoverymatrix für den nächsten Plan.

**Tech Stack:** bestehendes Debian-Altsystem nur read-only, IPMI/BMC Remote-KVM, betreibereigenes Backupsystem, PowerShell `Get-FileHash`, Ubuntu Server 24.04.4 LTS amd64, Git, PostgreSQL-Werkzeuge soweit Altbestände relevant sind.

---

## Dateistruktur dieses Arbeitspakets

- `docs/superpowers/specs/2026-08-25-aurelia-ground-zero-server-design.md` — freigegebenes Zielbild und Gesamtgates.
- `docs/superpowers/plans/2026-08-25-aurelia-ground-zero-preflight.md` — ausschließlich nicht-destruktiver Ausführungsplan.
- `docs/project-control/ground-zero/GATE-STATUS.md` — sanitierter, für Entwickler lesbarer Gatezustand.
- `docs/STATUS.md` — kanonischer Projektstand.
- `docs/project-control/README.md` — Leseeinstieg und Schutzgrenzen.
- Externe Backup-Protokolle, Seriennummern, Recovery-Keys und vollständige
  Hostinventare bleiben außerhalb des Git-Repositorys im betreibereigenen
  Backupsystem.

### Task 1: Kanonische Ground-Zero-Entscheidung fixieren

**Files:**
- Create: `docs/superpowers/specs/2026-08-25-aurelia-ground-zero-server-design.md`
- Create: `docs/project-control/README.md`
- Create: `docs/project-control/ground-zero/GATE-STATUS.md`
- Modify: `AGENTS.project.md`
- Modify: `docs/STATUS.md`
- Modify: `docs/09-roadmap.md`
- Modify: `docs/14-hardware.md`
- Modify: `docs/26-wiedervorlage.md`
- Modify: `docs/11-llm-handoff.md`
- Modify: `docs/02-architecture.md`
- Modify: `docs/03-security-dsgvo.md`
- Modify: `docs/07-identity.md`
- Modify: `docs/13-lovable.md`
- Modify: `docs/15-live.md`
- Modify: `docs/24-standalone.md`
- Modify: `SECURITY.md`
- Modify: `.gitignore`

- [x] **Step 1: Ubuntu-24.04.4-Entscheidung und Hardwarekorrektur dokumentieren**

  Erwarteter Stand: `AGENTS.project.md` nennt Ubuntu Server 24.04.4 LTS,
  2×2-TB-SN850X und `G0-SRV-GROUND-ZERO`.

- [x] **Step 2: Lokale Analysequellen gegen versehentliches Git-Tracking sperren**

  Regeln:

  ```gitignore
  /aurelia-tiefenanalyse*/
  /docs/project-control/external-analyses/**/source/
  ```

- [ ] **Step 3: Kanonische Ground-Zero-Dokumente validieren**

  Run:

  ```powershell
  rg -n "Ubuntu Server 24\.04\.4|G0-SRV-GROUND-ZERO|2× 2 TB|2x2TB" AGENTS.project.md SECURITY.md docs/STATUS.md docs/09-roadmap.md docs/14-hardware.md docs/26-wiedervorlage.md docs/project-control/README.md docs/superpowers/specs/2026-08-25-aurelia-ground-zero-server-design.md
  ```

  Expected: Treffer in allen kanonischen Ground-Zero-Quellen; kein Fehlercode.

- [ ] **Step 4: Schutz der lokalen Quellen prüfen**

  Run:

  ```powershell
  git check-ignore -v aurelia-tiefenanalyse/ docs/project-control/external-analyses/2026-08-25_17-33-00_CEST_developer-analysis-03/source/expanded-analysis-v3/01_EXECUTIVE_SUMMARY.md
  ```

  Expected: Beide Pfade werden durch die neuen `.gitignore`-Regeln erklärt.

- [ ] **Step 5: Dokumentationsänderungen separat committen**

  Run:

  ```powershell
  git add .gitignore AGENTS.project.md SECURITY.md docs/STATUS.md docs/02-architecture.md docs/03-security-dsgvo.md docs/07-identity.md docs/09-roadmap.md docs/11-llm-handoff.md docs/13-lovable.md docs/14-hardware.md docs/15-live.md docs/24-standalone.md docs/26-wiedervorlage.md docs/project-control/README.md docs/project-control/ground-zero/GATE-STATUS.md docs/project-control/external-analyses docs/superpowers/specs/2026-08-25-aurelia-ground-zero-server-design.md docs/superpowers/plans/2026-08-25-aurelia-ground-zero-preflight.md
  git commit -m "Plan AURELIA server ground zero"
  ```

  Expected: Ein Commit mit Ground-Zero-Steuerungsdokumenten und den bereits
  separat sanitisierten Analyse-/Verifikationsberichten; keine Datei aus einem
  Analyse-`source/`-Ordner.

### Task 2: Externes Backup und echte Wiederherstellung nachweisen

**Files:**
- Modify after operator evidence: `docs/project-control/ground-zero/GATE-STATUS.md`
- Modify after operator evidence: `docs/STATUS.md`
- Evidence outside Git: betreibereigenes Backupsystem

- [ ] **Step 1: Schreibaktivität der Altinstallation organisatorisch einfrieren**

  Der Betreiber beendet alle nicht notwendigen Entwicklungsjobs und bestätigt,
  dass zwischen finalem Backup und Neuinstallation keine Quellcode-, Datenbank-
  oder Prototypänderungen mehr vorgenommen werden. Produktive Altservices
  werden in diesem Preflight nicht neu konfiguriert.

  Expected: Ein benannter Freeze-Zeitpunkt mit Zeitzone Europe/Berlin im
  externen Backup-Protokoll.

- [ ] **Step 2: Sicherungsumfang im externen System vollständig abdecken**

  Der Sicherungssatz muss enthalten:

  - alle AURELIA-Git-Branches und Tags;
  - ungetrackte AURELIA-Dokumente einschließlich `docs/project-control`;
  - alle noch benötigten Prototypen und Laborartefakte;
  - relevante PostgreSQL-Datenbanken als logische Dumps plus Rollen/Globals;
  - relevante Objekt-/Dateidaten;
  - Konfiguration, Units, Cron, Firewall, Paket- und Containerinventar nur als
    Quarantäne-/Evidenzbestand;
  - Hashmanifest und Backupjob-Protokoll.

  Expected: Zwei Kopien außerhalb M G1, davon mindestens eine verschlüsselte
  Offline- oder EU-Offsite-Kopie.

- [ ] **Step 3: Git-Wiederherstellung auf getrenntem Ziel prüfen**

  Auf einem vom M-G1-Dateisystem getrennten Restoreziel wird das Repository
  wiederhergestellt. Dort ausführen:

  ```bash
  git fsck --full
  git branch --all
  git tag --list
  git log -1 --format='%H %cI %s'
  ```

  Expected: `git fsck --full` meldet keine beschädigten oder fehlenden Objekte;
  die erwarteten Branches einschließlich `codex/aurelia-vorbereitung` sind
  sichtbar; der letzte Commit ist nachvollziehbar.

- [ ] **Step 4: PostgreSQL-Dump auf getrenntem Ziel prüfen**

  Der für die Probe ausgewählte Dump wird im isolierten Restoreverzeichnis
  bewusst unter dem neutralen Namen `restore-probe.dump` bereitgestellt. Dort
  ausführen:

  ```bash
  pg_restore --list ./restore-probe.dump >/dev/null
  createdb aurelia_restore_probe
  pg_restore --exit-on-error --no-owner --dbname=aurelia_restore_probe ./restore-probe.dump
  psql --dbname=aurelia_restore_probe --no-align --tuples-only --command="SELECT count(*) FROM pg_catalog.pg_tables WHERE schemaname NOT IN ('pg_catalog', 'information_schema');"
  dropdb aurelia_restore_probe
  ```

  Expected: Alle Befehle liefern Rückgabecode 0; die Tabellenprüfung liefert
  eine Zahl größer als 0. Gibt es nach belegter Inventur keine relevante
  Datenbank, dokumentiert der Betreiber stattdessen diese begründete
  Nichtübernahme im vertraulichen Backup-Protokoll.

- [ ] **Step 5: Repräsentative Datei bytegenau prüfen**

  Eine repräsentative Quelldatei und ihre wiederhergestellte Kopie werden in
  einem isolierten Prüfverzeichnis unter den neutralen Namen
  `source-probe.bin` und `restored-probe.bin` bereitgestellt.

  Linux:

  ```bash
  sha256sum ./source-probe.bin ./restored-probe.bin
  ```

  PowerShell:

  ```powershell
  Get-FileHash -Algorithm SHA256 .\source-probe.bin
  Get-FileHash -Algorithm SHA256 .\restored-probe.bin
  ```

  Expected: Beide SHA-256-Werte sind identisch. Die realen vertraulichen Pfade
  werden nicht in Git oder Chat übernommen.

- [ ] **Step 6: Sanitierte Gateaussage an die Projektsteuerung übergeben**

  Die Betreiberbestätigung muss ohne Secrets mindestens enthalten: Zeitpunkt
  des letzten erfolgreichen Backups, zwei externe Kopien, Verschlüsselung,
  erfolgreicher Git-Restore, erfolgreicher Datenbank-Restore beziehungsweise
  begründete Feststellung, dass keine Datenbank übernommen werden muss, und
  erfolgreichen Datei-Hashvergleich.

  Expected: Erst nach objektiver Prüfung wird in
  `docs/project-control/ground-zero/GATE-STATUS.md` der Status
  `G0-SRV-0: bestanden` gesetzt.

### Task 3: Letzte read-only Hostinventur sichern

**Files:**
- Evidence outside Git: vertrauliches Ground-Zero-Inventar im Backupsystem
- Modify after sanitized consolidation: `docs/project-control/ground-zero/GATE-STATUS.md`

- [ ] **Step 1: System-, Boot- und Storagezustand erfassen**

  Run on M G1:

  ```bash
  date --iso-8601=seconds
  hostnamectl
  test -d /sys/firmware/efi && echo UEFI=yes || echo UEFI=no
  mokutil --sb-state
  lsblk -e7 -o NAME,PATH,SIZE,MODEL,TYPE,FSTYPE,MOUNTPOINTS
  cat /proc/mdstat
  sudo mdadm --detail --scan
  sudo pvs
  sudo vgs
  sudo lvs
  ```

  Expected: UEFI wird bestätigt; beide 2-TB-NVMe und alle mdraid-Arrays sind
  nachvollziehbar. Keine Ausgabe wird zur Änderung des Systems verwendet.

- [ ] **Step 2: Hardware- und ECC-Evidenz erfassen**

  Run on M G1:

  ```bash
  lscpu
  free -h
  sudo dmidecode --type 16
  sudo dmidecode --type 17
  lspci -nn
  ls -la /dev/tpm* /dev/ipmi* 2>/dev/null
  ```

  Expected: Ryzen 5 9600X, 128 GB, H13SAE-MF-Pfad, RTX 4000 SFF Ada, TPM und
  IPMI sind nachvollziehbar. DIMM-Teilenummern bleiben im vertraulichen
  Betreiberprotokoll; öffentlich wird nur `ECC bewiesen` oder `ECC nicht
  bewiesen` festgehalten.

- [ ] **Step 3: Dienste, Zugänge und Netzwerk als Quarantäneevidenz erfassen**

  Run on M G1:

  ```bash
  systemctl --failed --no-pager
  systemctl list-unit-files --state=enabled --no-pager
  ss -lntup
  sudo nft list ruleset
  sudo iptables-save
  sudo crontab -l
  ```

  Expected: Die Altbefunde sind für den Vergleich gesichert. Ausgaben mit
  Secrets werden ausschließlich verschlüsselt im Backupsystem gespeichert und
  weder in Git noch im Chat wiedergegeben.

- [ ] **Step 4: Unveränderliche physische Gerätezuordnung lokal sichern**

  Run on M G1:

  ```bash
  ls -l /dev/disk/by-id/
  sudo nvme list
  ```

  Expected: Beide physischen NVMe sind eindeutig einem `/dev/disk/by-id/`-
  Pfad zugeordnet. Seriennummern und Pfade bleiben vertraulich. Der spätere
  destruktive Plan wird aus dieser lokal geprüften Zuordnung erzeugt und nicht
  aus `nvme0n1`/`nvme1n1` geraten.

### Task 4: Ubuntu-ISO kryptografisch prüfen

**Files:**
- Evidence outside Git: ISO-Hashprotokoll
- Modify after verification: `docs/project-control/ground-zero/GATE-STATUS.md`

- [ ] **Step 1: Ausschließlich das offizielle Serverabbild laden**

  Download:

  ```text
  https://releases.ubuntu.com/releases/24.04.4/ubuntu-24.04.4-live-server-amd64.iso
  ```

  Expected filename:

  ```text
  ubuntu-24.04.4-live-server-amd64.iso
  ```

- [ ] **Step 2: SHA-256 unter Windows prüfen**

  Run in the ISO directory:

  ```powershell
  Get-FileHash -Algorithm SHA256 .\ubuntu-24.04.4-live-server-amd64.iso
  ```

  Expected SHA-256:

  ```text
  E907D92EEEC9DF64163A7E454CBC8D7755E8DDC7ED42F99DBC80C40F1A138433
  ```

  Quelle des Sollwerts:
  `https://releases.ubuntu.com/24.04.4/SHA256SUMS`.

- [ ] **Step 3: Bei jeder Abweichung stoppen**

  Expected: Nur ein exakt übereinstimmender Hash erlaubt Virtual Media. Bei
  Abweichung wird die Datei gelöscht, aus offizieller Quelle neu geladen und
  erneut geprüft; sie wird niemals gebootet.

### Task 5: IPMI/KVM und Virtual Media ohne Installation beweisen

**Files:**
- Evidence outside Git: IPMI-Testprotokoll ohne Zugangsdaten
- Modify after verification: `docs/project-control/ground-zero/GATE-STATUS.md`

- [ ] **Step 1: BMC ausschließlich über den Managementpfad öffnen**

  Expected: Die BMC-Adresse ist nicht öffentlich erreichbar; Login erfolgt mit
  einem individuellen Administratorkonto, nicht mit Hersteller-Defaultdaten.

- [ ] **Step 2: Remote-KVM bei laufendem Altsystem testen**

  Expected: Bildschirm, Tastatur und Bootmenü sind über KVM bedienbar. Ein
  Neustart wird erst im abgestimmten Wartungsfenster ausgelöst.

- [ ] **Step 3: Verifizierte ISO als Virtual Media nur lesend einbinden**

  Expected: BMC zeigt exakt `ubuntu-24.04.4-live-server-amd64.iso`; die
  ISO-Datei bleibt read-only eingebunden.

- [ ] **Step 4: Einmal bis zum Ubuntu-Installer-Start booten und abbrechen**

  Expected: Der Ubuntu-Server-Installer startet im UEFI-Modus, KVM-Eingaben
  funktionieren und beide NVMe werden angezeigt. Der Test wird vor jeder
  Storagebestätigung beendet; keine Partition wird verändert.

- [ ] **Step 5: `G0-SRV-1` nur nach erfolgreichem Rückboot setzen**

  Expected: Nach Auswerfen der Virtual Media startet die unveränderte
  Altinstallation. Erst dann erhält `G0-SRV-1` den Status `bestanden`.

### Task 6: Preflight abnehmen und nächsten Plan erzeugen

**Files:**
- Modify: `docs/project-control/ground-zero/GATE-STATUS.md`
- Modify: `docs/STATUS.md`
- Create only after all prerequisites pass: `docs/superpowers/plans/2026-08-25-aurelia-ground-zero-installation.md`

- [ ] **Step 1: Gateergebnisse konsolidieren**

  Expected:

  ```text
  G0-SRV-0 = bestanden
  G0-SRV-1 = bestanden
  G0-SRV-2 = bestanden
  destructive_actions_allowed = false
  ```

  `destructive_actions_allowed` bleibt selbst nach dem Preflight `false`, bis
  der Betreiber den danach erzeugten Installationsplan separat freigibt.

- [ ] **Step 2: Ground-Zero-Installationsplan aus realen Geräte-IDs erzeugen**

  Der Folgeplan enthält die lokal bestätigten `/dev/disk/by-id/`-Ziele, die
  exakten Partitionen, mdraid-, LUKS2-, LVM-, EFI-/GRUB- und Recovery-Schritte,
  jeweils mit Verifikation und Rückfallpunkt. Vertrauliche Seriennummern und
  Recovery-Keys werden nicht in Git geschrieben.

  Expected: Kein generischer `wipefs`-, `sgdisk`-, `mdadm --create`- oder
  `cryptsetup luksFormat`-Befehl ohne zweifach bestätigte absolute Zielgeräte.

- [ ] **Step 3: Betreiberfreigabe für die physische Installation einholen**

  Expected: Eine neue, eindeutige Freigabe bezieht sich auf den finalen
  Installationsplan und bestätigt unmittelbar davor den weiterhin gültigen
  Backup-/Restore-Stand. Erst diese Freigabe darf
  `destructive_actions_allowed: true` setzen.

---

## Self-Review-Ergebnis

- Spec coverage: Backup/Restore, letzte Inventur, ISO-Provenienz, IPMI/KVM,
  Virtual Media, Gerätebindung und Destruktionssperre sind abgedeckt.
- Scope boundary: Der Plan enthält bewusst keine NVMe-Löschung oder
  Installation; diese bildet nach bestandenem Preflight ein eigenständig
  freizugebendes Arbeitspaket.
- Secret boundary: Seriennummern, Recovery-Keys, Backuppfade, Dumps und
  Analysequellen bleiben außerhalb von Git und externen Reviewprompts.
- Destructive safety: Alle destruktiven Kommandoklassen bleiben bis zum
  separaten Folgeplan gesperrt.

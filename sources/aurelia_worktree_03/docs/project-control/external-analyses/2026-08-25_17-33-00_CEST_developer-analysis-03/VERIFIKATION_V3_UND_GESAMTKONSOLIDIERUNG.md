# Verifikation V3 und Gesamtkonsolidierung V1–V3

**Reasoning:** Sol 5.6 xHigh
**Prüfmodus:** vollständig lesend; lokale, Git- und Serverevidenz
**Prüfdatum:** 2026-08-25
**Serveränderungen:** keine
**GitHub-Änderungen:** keine
**AUDIT-02:** bewusst nicht fortgeführt

## 1. Ergebnis in einem Satz

V3 ist die bislang wertvollste Server-Risikoanalyse und enthält mehrere
kritische, unabhängig bestätigte Neubefunde; als Gesamtprojektstand und
Masterplan bleibt sie dennoch ungeeignet, weil sie erneut den veralteten
Vorbereitungsbranch bewertet, G0 ignoriert, mehrere Serverbeobachtungen
überdehnt und Aufwand, Rechtsstatus sowie Architektur mit unbelegter
Genauigkeit festlegt.

## 2. Gesamturteil

| Dimension | Urteil |
|---|---|
| Serverinventur | deutlich verbessert; zentrale Zahlen unabhängig bestätigt |
| Sicherheitspriorisierung | im Kern richtig, aber Incident, Hardening und produktive Phasen müssen getrennt werden |
| Projektstand | branchgebunden veraltet und deshalb teilweise falsch |
| Architektur | als Backloginput brauchbar, nicht als freigegebener Zielvertrag |
| Recht/Claims | weiterhin zu definitiv; 95 % sind nicht belegbar |
| Termin/Aufwand | keine belastbare WBS- oder Kapazitätsgrundlage |
| Phasenplan | gute Abnahmekriterien, aber falsche Autoritäts- und Gate-Reihenfolge |
| Sofortmaßnahmen | nur nach sicherem Change-Plan; kein Direktvollzug aus V3 |

V3 verbessert V2 vor allem bei SSH, Sudo, Cron, Firewall, Fail2ban,
Systemd, Docker-Disk und Backup-Topologie. Sie behebt jedoch den bereits in
V1 und V2 benannten Grundfehler nicht: Branch, Commit und Governance-Autorität
werden zwar genannt, aber nicht korrekt auf den maßgeblichen Stand
aufgelöst.

## 3. Projekt- und Git-Realität

### 3.1 Verwendeter V3-Stand

V3 prüfte korrekt den lokal ausgecheckten Branch
`codex/aurelia-vorbereitung` bei
`a726346c74b02af811fc833151f7031ead431dac`.

Auf genau diesem unvollständig eingerichteten Arbeitsstand waren reproduzierbar:

- `npm test`: 14 von 15 Quelltests bestanden; ein Test scheiterte an der
  fehlenden Auflösung von `@tanstack/react-start`;
- der Skript-Glob führte unter Windows null Skripttests aus;
- `npm run typecheck`: TS5102 und zusätzlich TS2688;
- `npm run lint`: lokales ESLint-Binary wegen fehlendem Abhängigkeitsstand
  nicht verfügbar;
- `scripts/canon-contract.mjs`: auf diesem Branch nicht vorhanden.

Diese Beobachtungen sind als Zustand des Vorbereitungsbranches richtig, aber
nicht als Gesamtzustand des Projekts.

### 3.2 Übersehene maßgebliche Folgestände

- Kanon-Implementierung:
  `b20ee873347c5fd767e2089c993f1cf93a625def`
- final freigegebenes G0-Design:
  `a6a8e7dca456d14a6748b204b787b235fdedf9be`

Zwischen `a726346` und `b20ee873` liegen 31 geänderte Dateien, darunter der
Kanonvertrag und 223 zugehörige Testzeilen. Zwischen Kanon und G0 liegt die
3.968-zeilige G0-Governance-Spezifikation. V3 berücksichtigt beides nicht.

Die bereits erhobene Kanon-Evidenz bleibt:

- Typecheck, Lint und `check:canon` bestanden im eingerichteten
  Kanon-Arbeitsstand;
- `npm test` war formal grün, übersprang unter Windows aber die Skripttests;
- direkter Skripttestlauf: 161 Tests, 146 bestanden, 15 fehlgeschlagen;
- `check:auth` ist ohne laufenden Server nicht aussagekräftig.

Folgerung: Der portable Testfinder und `zero tests = red` bleiben reale
Qualitätsaufgaben. „Kanonplan unausgeführt“ und „canon-contract existiert
nicht“ sind als projektweite Aussagen falsch.

### 3.3 Kanonfehler in V3

V3 bezeichnet D01–D24 und K1–K8 als geschlossen. Der Kanon sagt dagegen:

- D09 und D11 sind Wiedervorlage/offen;
- K6–K8 sind gesperrt und dürfen weder Kernel-ID noch Feature-Flag erhalten;
- Video/WebRTC ist ausgeschlossen;
- Phase 1 bleibt synthetisch, ohne reale Klienten, CUDA oder USB.

Auch „Phase 0 abgenommen“ darf nicht mit „G0 implementiert/green“ verwechselt
werden. Freigegeben ist das G0-Design; die Gate-Ausführung bleibt eine eigene
Arbeit.

## 4. Serverbefunde — Entscheidungsmatrix

| V3-Aussage | Ergebnis | Präzisierung |
|---|---|---|
| `PermitRootLogin yes` | bestätigt | effektiv auch im Root-Kontext; Passwortauth aktiv; Root-Passwort gesetzt |
| `klaus999 NOPASSWD: ALL` | bestätigt | zusätzlich Docker-Gruppe; der Account ist doppelt root-äquivalent |
| Klartext-DB-Passwort im Cron | Vorhandensein bestätigt | Wert nicht ausgelesen; V3 selbst reproduziert ihn und erweitert damit die Offenlegung |
| 9 fehlgeschlagene Units | widerlegt | tatsächlich zehn: neun Radiquant-Units plus Firewall-Restore |
| Doppelorchestrierung | stark gestützt | Docker-Pendants laufen; abschließende Unit-/Compose-Eigentümermatrix fehlt |
| Fail2ban 23.292/4.622 | bestätigt und fortgeschrieben | 23.305/4.623 beim Codex-Audit; Angriffsdruck, kein Kompromittierungsbeweis |
| kein Offsite-Backup | betrieblich nicht nachgewiesen | sichtbare Backups liegen lokal; Provider-Snapshots/externer Pull nicht vom Host aus ausschließbar; WV01 bis Beleg rot |
| Docker 235/200 GB/185 GB | bestätigt | keine Löschfreigabe; „rückgewinnbar“ ist kein Sicher-ist-löschbar-Nachweis |
| Disk 62 % | bestätigt | 667 GiB frei; kein akuter Kapazitätsnotstand |
| NVML-Mismatch | bestätigt | geladen 535.261, installiert/DKMS 535.309; Toolkit fehlt |
| Strapi-Crashloop | bestätigt | eigener Legacy-Bereinigungs-/Migrationsentscheid erforderlich |
| Alt-API 8000 öffentlich | bestätigt | TCP von extern erreichbar |
| xRDP 3389 öffentlich | bestätigt | TCP von extern erreichbar und UFW-allow sichtbar |
| alle genannten Listener öffentlich | widerlegt | 25/8443/8080/9090/3001/6556 von einem externen Prüfpunkt nicht erreichbar |
| Hardware exakt gesund | nicht belegt | GPU aktuell unbenutzbar; md2 pending; CPU-MHz-Wert unplausibel; SMART/RAM/Restore fehlen |
| alles in 2–3 Tagen behebbar | nicht belastbar | Hardening, Incident-Abgleich, Offsite-Restore und GPU-Recovery brauchen getrennte Change-/Testfenster |

### 4.1 Betreiberbestätigte Root-Anmeldungen

Seit dem 1. August wurden acht erfolgreiche Root-SSH-Anmeldungen per Passwort
protokolliert: sechs am 19. August und zwei am 21. August. Der Betreiber
bestätigte am 25. August 2026, dass alle acht Anmeldungen von ihm selbst bei
der Einrichtung des Servers durchgeführt wurden. Sie gelten damit als
autorisierte Wartungs-/Einrichtungszugriffe und nicht als Incident-Indikator.

Die Bestätigung ändert nicht den Härtungsbefund: Root-Passwortzugang ist
effektiv aktiv und unnötig exponiert. Künftige Root-Anmeldungen müssen nach
der kontrollierten Härtung unmöglich beziehungsweise über einen gesonderten,
protokollierten Break-Glass-Prozess geregelt sein.

### 4.2 Unsichere V3-Härtungsvorschläge

- Eine `sudoers`-Whitelist mit unrestricted `systemctl`, Paketverwaltung,
  Shell-fähigen Programmen oder Docker ist weiterhin root-äquivalent.
- `.pgpass` ist eine geschützte Klartext-Passwortdatei, kein Secret-Vault. Sie
  ist mit Modus 0600 zulässig, muss aber mit separatem, minimal berechtigtem
  Backup-DB-Konto, Rotation und Dateieigentümer gekoppelt werden.
- Ein pauschales `docker system prune -a` kann Images, Netzwerke und gestoppte
  Wiederherstellungsartefakte entfernen. Erst Inventar, Referenzgraph,
  Sicherung und gezielte Kandidatenfreigabe.
- Reboot, Firewallreload, SSHD-Reload, Maskieren von Units und Entfernen des
  Swapfiles sind eigenständige Änderungen mit Rollback und Out-of-Band-Zugang.
- Ein fehlgeschlagener Persistenzdienst bei aktuell funktionierender
  Laufzeitfirewall macht einen ungeplanten Reboot besonders riskant.

## 5. Bewertung der V3-Architektur und Innovationen

### 5.1 Übernehmen — als Anforderungen oder spätere Arbeitspakete

- formales Server-Baseline-/Hardening-Gate vor realen Art.-9-Daten;
- separater, least-privileged Audit-Zugang ohne `sudo` und Docker-Gruppe;
- SSH-, Port-, Unit-, Container- und Backup-Inventar mit signierter Evidenz;
- verschlüsseltes EU-Offsite-Backup plus isolierter Restore-Test;
- Kernel-Manifest/Registry, Golden Files und ABI-basierte
  Prototypenaufnahme;
- Emitter-Simulator und Lease-/Arming-/ACK-Automat;
- RLS-Rollen-, Grant-/Revoke- und Negativtestdesign;
- Krypto-, Recovery-, Rotation- und Crypto-Erasure-Spezifikation;
- CPU-/GPU-Benchmarks erst auf reproduzierbaren M-G1-Workloads;
- Claims-, Intended-Purpose-, MDR-/HWG- und Datenschutzfreigabe;
- messbare Abnahmekriterien mit Owner, Quelle, Exitcode und Artefakthash.

### 5.2 Übernehmen — aber umformulieren

| V3-Begriff | Konsolidierte Fassung |
|---|---|
| Phase 1.5 Serverhärtung | querschnittliches `GATE-MG1-BASELINE`, getrennt von Produktphasen |
| Postgres-WAL als Uhr | fachlicher Timerzustand in Tabellen/Ereignissen; WAL nur Durability/Recovery |
| GPU-Stream-Isolation | Scheduler-/Nebenläufigkeitsmechanismus, keine Sicherheitsgrenze |
| Merkle-/Rechenbeweis | signierter Integritäts-/Reproduzierbarkeitsnachweis, kein Korrektheits- oder ZK-Beweis |
| GBNF/CopyGuard | syntaktische Begrenzung plus deterministische Policies und menschliche Claims-Freigabe |
| bitidentischer CPU/CUDA-Replay | nur für exakt definierte Integer/Fixed-Point-Referenzen; sonst dokumentierte Toleranzen |
| kein Offsite | kein nachgewiesenes Offsite; WV01 bis Restore-Evidenz nicht erfüllt |

### 5.3 Nicht kanonisieren

- 95-/85-/25-Prozentwerte;
- 9–15 oder 12–20 Monate als belastbare Prognose;
- „kein Medizinprodukt“ als allein durch Disclaimer abgeschlossenes Faktum;
- direkte Phase-2-Fortsetzung nach dem V3-Plan;
- konkrete AES-/HKDF-/Suchverschlüsselungsfestlegung vor Threat Model und
  Datenfluss;
- deterministische Tenant-Schlüssel;
- PGlite-/LWW-basierte produktive Offline-Akte;
- CUDA-Streams oder Arenas als Tenant-Sicherheitsgrenze;
- `SCHED_FIFO`, feste CPU-Kerne oder harte Latenzversprechen ohne Messung;
- echter Zero-Knowledge-/Korrektheitsanspruch aus einem Merkle-Baum;
- unmittelbarer Reboot, Toolkitinstallation, Firewalländerung, Unit-Masking
  oder Docker-Prune aus dem Analysebericht heraus.

## 6. Rechts- und Produktabgrenzung

Die V3-Bewertung „Rechts-/Produktabgrenzung 95 %“ ist nicht haltbar. Für die
Qualifikation von Software sind Zweckbestimmung, tatsächliche Funktionen,
Reports, UI, Werbung und Vertriebsbehauptungen maßgeblich. Ein interner Satz
„kein Medizinprodukt“ und CopyGuard reduzieren Risiken, entscheiden die
Einordnung aber nicht abschließend.

Vor Pilotbetrieb sind mindestens erforderlich:

1. Intended-Purpose-/Qualification-Memo;
2. Claims-Register einschließlich Negativclaims;
3. Trennung von Wellbeing, Analyse, Dokumentation und physiologischer
   Auswertung;
4. juristisch-fachliche Freigabe von UI, Reports und Marketing;
5. Datenschutz-Folgenabschätzungsprüfung, Rechtsgrundlagen und
   Auftragsverarbeitung;
6. dokumentierte Entscheidung, ob einzelne Funktionen die Grenze zur
   Medical Device Software berühren.

## 7. Konsolidierte Priorität nach V1–V3

| Rang | Paket | Modus | Freigabezustand |
|---:|---|---|---|
| 0 | Root-Anmeldungen mit Betreiberregister abgleichen | read-only/organisatorisch | erledigt; alle acht autorisiert bestätigt |
| 1 | Incident-/Hardening-Change-Plan mit OOB, Rollback und Testmatrix | Planung | noch keine Serverfreigabe |
| 2 | DB-Geheimnisrotation und least-privileged Backup-Konto | Änderung | separates Wartungsfenster nötig |
| 3 | SSH/Sudo/Docker-Zugriffsmodell härten | Änderung | separates Wartungsfenster nötig |
| 4 | Firewall-Persistenz und öffentliche Alt-API/xRDP kontrolliert schließen | Änderung | Lockout-sicherer Change-Plan nötig |
| 5 | Offsite-Ziel, Schlüssel-Recovery und Restore-Test realisieren | Design/Änderung/Test | WV01 bis Evidenz rot |
| 6 | Systemd/Docker-Eigentümermatrix; Legacydienste gezielt stilllegen | Analyse/Änderung | kein pauschales Maskieren |
| 7 | GPU-Recovery im Wartungsfenster, danach NVML/CUDA-Baseline | Änderung/Test | kein Sofortreboot |
| 8 | portable Testsuche und vollständige CI-Gates auf Kanonbranch | lokale Implementierung | nach expliziter Freigabe |
| 9 | AUDIT-02 auf Grundlage von G0, V1–V3 und Serverevidenz abschließen | Analyse | nächster Produktplanungsschritt |
| 10 | Threat Model, Datenfluss, RLS/Krypto/IPC/Backup-Zieldesign | xHigh-Design | nach Gate-Reihenfolge |

Die Sicherheitsränge 0–7 ersetzen G0 nicht. Sie behandeln den bereits
existierenden, exponierten Legacy-/Entwicklungsserver als eigene
Betriebsrisikodomäne. Produktive AURELIA-Daten, CUDA und USB bleiben weiterhin
gesperrt.

## 8. Empfohlenes Reasoning und Reviewerstrategie

| Aufgabe | Empfohlen |
|---|---|
| Betreiberabgleich der Root-Ereignisse | high genügt; Faktencheck |
| Incident-/SSH-/Firewall-/Backup-Change-Plan | Sol 5.6 xHigh |
| externe Gegenprüfung des sanitisierten Change-Plans | unabhängiges Modell, z. B. Gemini Flash; keine Serverdaten/Secrets |
| technische Umsetzung klar abgegrenzter Änderungen | high, mit Tests und Checkpoints |
| AUDIT-02/G0-Konsolidierung | Sol 5.6 xHigh |
| Routineverifikation nach Umsetzung | kostengünstigeres Modell/high, solange Kriterien deterministisch sind |

Reasoning-Wechsel erfolgen gemäß Direktive nicht automatisch, sondern erst
nach ausdrücklicher Bestätigung.

## 9. Quellenbasis

### Projektinterne Autorität

- `AGENTS.project.md`
- Kanon: `b20ee873347c5fd767e2089c993f1cf93a625def`
- freigegebenes G0-Design:
  `a6a8e7dca456d14a6748b204b787b235fdedf9be`
- V1- und V2-Verifikationen im benachbarten Projektkontrollbereich

### Externe Primärquellen

- OpenSSH `sshd_config`: <https://man.openbsd.org/sshd_config.5>
- Docker-Gruppe und Root-Privilegien:
  <https://docs.docker.com/engine/install/linux-postinstall>
- Docker-Diskreport: <https://docs.docker.com/reference/cli/docker/system/df/>
- Docker-Prune: <https://docs.docker.com/reference/cli/docker/system/prune/>
- PostgreSQL Password File:
  <https://www.postgresql.org/docs/17/libpq-pgpass.html>
- NVIDIA NVML:
  <https://docs.nvidia.com/deploy/pdf/NVML_API_Reference_Guide.pdf>
- Debian Bookworm CUDA Toolkit:
  <https://packages.debian.org/bookworm/nvidia-cuda-toolkit>
- AMD Ryzen 5 9600X:
  <https://www.amd.com/en/products/processors/desktops/ryzen/9000-series/amd-ryzen-5-9600x.html>
- MDCG 2019-11 Rev. 1:
  <https://health.ec.europa.eu/document/download/b45335c5-1679-4c71-a91c-fc7a4d37f12b_en?filename=mdcg_2019_11_en.pdf>

## 10. Schlussurteil

V3 soll als priorisierte Sicherheits- und Betriebsquelle erhalten bleiben.
Sie ersetzt weder V1/V2 noch den Kanon oder G0. Ihre validen Serverbefunde
heben den Handlungsdruck deutlich an, aber sie legitimieren keinen
ungeplanten Vollzug.

Der sachgerechte nächste Schritt ist nicht Phase 2 und nicht Docker-/Server-
Bereinigung, sondern:

1. kontrollierter Hardening-Change-Plan;
2. sanitierte externe Gegenprüfung dieses Plans;
3. explizite Freigabe je Änderungsfenster;
4. danach Rückkehr zu AUDIT-02 und der G0-Wellensequenz.

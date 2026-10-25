# Verifikation Entwickleranalyse v2 und Vergleich mit v1

**Prüfmodus:** xHigh, vollständig lesend
**Prüfdatum:** 2026-08-25
**AUDIT-02:** nicht fortgeführt
**Server-/GitHub-Änderungen:** keine

## 1. Gesamturteil

v2 ist **strukturell und methodisch deutlich besser als v1**, aber noch nicht
als aktueller Projektstand, freigegebener Masterplan oder belastbare
Machbarkeits-/Terminprognose geeignet.

Der entscheidende Fortschritt liegt in IDs, Quellenhinweisen,
Abnahmekriterien, Serverrisiken und klarerer Trennung von Pflicht und Option.
Der entscheidende verbleibende Fehler ist die fehlende Bindung an Branch,
Commit und die inzwischen freigegebene G0-Governance. Dadurch werden reale
Befunde eines älteren Branchs zu Aussagen über das Gesamtprojekt verallgemeinert.

Die Behauptung, alle Aussagen seien direkt verifiziert, ist deshalb nicht
haltbar. Korrekt wäre: **Ein Teil der Code- und Serverbeobachtungen wurde durch
den Entwickler in seiner Session erhoben; ihre Übertragung auf den aktuellen
Kanon und mehrere Schlussfolgerungen sind nicht verifiziert.**

## 2. Vergleich v2 zu v1

| Dimension | Verbesserung in v2 | Verbleibender oder neuer Mangel |
|---|---|---|
| Methodik | Quellen- und Befundklassen werden benannt. | Kein Branch, Commit, Rohprotokoll oder reproduzierbares Evidenzpaket. |
| Codeprüfung | DEF-01 bis DEF-04 sind nachvollziehbarer beschrieben. | Die Defekte stammen überwiegend aus `aurelia-vorbereitung`, nicht aus dem maßgeblichen Kanon. |
| Server | Hardware, Treiber, Dienste, Ports und Altbestand werden erstmals konkret inventarisiert. | Von Codex nicht reproduzierbar; Aussagen über Öffentlichkeit, Ursache und Behebung gehen über die dokumentierte Evidenz hinaus. |
| Risiken | GAP- und R-IDs erhöhen Nachvollziehbarkeit. | G0, Datenfluss, RLS-Owner-Bypass, GPU-Kontextgrenzen und Supply Chain sind unzureichend berücksichtigt. |
| Innovation | „Zero-Knowledge-Merkle“ wurde korrekt auf eine Merkle-Auditspur zurückgenommen. Offline wird später und optional eingeordnet. | Merkle beweist weiterhin keine Berechnung; GBNF keine rechtliche Semantik; Offline-Sync bleibt technisch und datenschutzrechtlich ungelöst. |
| Architektur | IPC- und Kryptovertrag werden als eigene Designaufgaben erkannt. | Konkrete Algorithmen, Protokolle und Schedulingwerte werden vor Threat Model und Messung festgelegt. |
| Roadmap | Messbare `[A]`-Kriterien und Aufwandsspannen sind besser als v1. | Die gesamte Roadmap überspringt G0 und unterschätzt externe Reviews, Recht, Security, Restore und Integration. |
| Aussagenstil | Weniger absolute `100 %`-Formulierungen als v1. | 95-/85-/25-Prozentwerte, „kein Medizinprodukt“ und „nichts technisch unmöglich“ bleiben unbelegt. |

## 3. Reproduzierte, belastbare Befunde

### 3.1 Bestätigt

- Der Vorbereitungsbranch zeigt genau den von v2 beschriebenen
  `@tanstack/react-start`-Modulfehler.
- Im Vorbereitungsbranch ist die Dependencyfläche nicht vollständig
  installiert; `npm ls` ist leer. Das ist ein wichtiger Teil der Ursache, den
  v2 nicht sauber trennt.
- Der Windows-Glob in `npm test` findet null Skripttests. Dieser Fehler besteht
  auch im Kanon und ist ein echter P0-Qualitätsbefund.
- Die 14 Gate-Identity-Einzeltests sind grün. v2 nennt 15; das ist ein kleiner
  Zählfehler.
- Produktive RLS, `gpud`, `timerd`, `emitterd`, CopyGuard-Runtime,
  Kernel-Registry und produktive Klientenakte fehlen.
- Die Migration `0002_tenants.sql` bildet nur die synthetische Phase-1-Hülle.
- Das PGlite-Fallback ist serverseitig und flüchtig, nicht die in IN-07
  beschriebene Browserakte.
- Test-, IPC-, Kryptografie-, RLS-, Restore-, Hardware- und Betriebsdesigns
  sind echte spätere Arbeitsfelder.

### 3.2 Gegenüber v2 korrigiert

- Im maßgeblichen Kanon besteht `npm run typecheck` mit TypeScript 5.9.3.
- Im maßgeblichen Kanon existiert `scripts/canon-contract.mjs`; `check:canon`
  ist grün.
- Die WebRTC-Kanonbereinigung ist dort bereits umgesetzt. Ein Verbotshinweis in
  `11-llm-handoff.md` ist keine unerlaubte aktive WebRTC-Empfehlung.
- `npm test` im Kanon meldet 24/24 Quelltests grün; der vorgelagerte
  Skripttestblock bleibt wegen des Globs fälschlich bei null.
- Direkt ausgeführt melden 161 Skripttests 146 Erfolge und 15 Fehler. v2
  erfasst diese zweite Testebene nicht.
- `check:auth` soll gerade die aufgelöste Konfiguration eines laufenden Servers
  mit der Buildseite vergleichen. Eine rein statische Prüfung darf diese
  Live-Invariante nicht ersetzen; sinnvoll sind zwei getrennte Checks.
- `D01–D24` sind nicht pauschal alle „gesetzt“: D09 und D11 bleiben
  Wiedervorlagen. K6–K8 sind gesperrte Nicht-Produktpfade, keine aktiv
  gesetzten Kerne.
- Die Aussage „alle 27 Dokumente inklusive Plans/Specs“ ist als Zähl- und
  Scopeaussage unklar. Im relevanten Kanon existieren 30 Dateien unter
  `docs/`; die G0-Pläne liegen zudem in einem anderen Worktree und wurden von
  v2 erkennbar nicht einbezogen.

## 4. Kritische Findings

### V2-P0-01 – G0 wird vollständig übersprungen

v2 erklärt Phase 0 für abgenommen und setzt Phase 1/2 fort. Das widerspricht
dem final freigegebenen G0-Design. `GATE-G0` ist noch rot. Selbst ein späteres
grünes G0 erlaubt zunächst nur die gemeinsame Ausarbeitung von Debian-
Pilotprofil, Threat Model und Datenschutzdatenfluss – keine realen Daten,
Servermutation oder Produktivfreigabe.

Folge: Der v2-Phasenplan darf nur als post-G0-Backlogquelle verwendet werden.

### V2-P0-02 – Falsche maßgebliche Codebasis

v2 analysiert einen echten, aber älteren und dependency-unvollständigen
Vorbereitungsbranch. Die Diagnose wird ohne Commitangabe zum Gesamtstatus
erhoben. Dadurch werden bereits behobene Punkte als Sofortmaßnahmen geführt.

Übernehmbar bleibt ausschließlich der plattformübergreifende Testfinder sowie
die Klassifikation der 15 direkten Skripttestfehler. G0-Plan 01 sieht den
Cross-Platform-Runner und „zero tests = red“ bereits vor; es ist kein neuer,
paralleler Plan nötig.

### V2-P0-03 – Produkt-/Rechtsabgrenzung ist nicht zu 95 % bewiesen

„Kein Medizinprodukt“ folgt nicht allein aus Verfassung, Disclaimer oder
CopyGuard. Die Einordnung hängt von Zweckbestimmung, Funktionen, Reports,
Marketing- und Vertriebsaussagen ab. HRV, physiologische Kennzahlen und
Harmonisierungskommunikation erhöhen die Abgrenzungsrelevanz.

Erforderlich bleiben Qualification-/Intended-Purpose-Memo, Claims-Register,
fachliche und juristische Freigabe. CopyGuard kann diese Freigabe unterstützen,
nicht ersetzen.

### V2-P0-04 – Art.-9-Gate in Phase 2 ist unvollständig

DSB-Review, Restore und RLS reichen nicht. Vor realen Daten verlangt das
freigegebene Gate zusätzlich mindestens Datenfluss, Threat Model,
Produktionsprofil, Identität/Sitzungen, Rollen/Grants, Schlüssel-Recovery,
Retention, Löschung, Incident-Prozess und belastbare Negativtests.

`assertSynthetic()` ist eine sinnvolle zusätzliche Sperre, aber kein Ersatz
für Profil- und Gate-Evidenz.

### V2-P0-05 – Serverbefunde besitzen keine übergebene Beweiskette

Die Serverinventur kann plausibel und wertvoll sein. Es fehlen jedoch:

- vollständige Befehlsliste und unveränderte Ausgaben;
- UTC-Zeit und Lauf-ID je Befehl;
- Host-Key-/Zielbindung;
- Exitcodes und Privilegienkontext;
- Hash und Signatur des Evidenzbundles;
- klare Trennung zwischen Beobachtung, Ursache und Empfehlung.

Codex konnte mangels akzeptierter SSH-Authentisierung keine Aussage
reproduzieren. Deshalb bleiben CPU/GPU/RAM/RAID/TPM, Treiber, Container, Ports
und Prozesse `reported/unverified`.

### V2-P0-06 – Reboot und Installation sind keine Sofortmaßnahmen

Ein NVML-Library-/Kernelmodul-Mismatch ist plausibel; ein Reboot ist eine
bekannte mögliche Behebung. Er garantiert aber nur Erfolg, wenn passendes
Kernelmodul, DKMS-Build, initramfs und Paketzustand tatsächlich konsistent
sind. Vorher sind read-only Preflight, Nutzer-/Dienstabhängigkeiten, Backup,
Rollback und Wartungsfenster erforderlich.

Debian Bookworm liefert `nvidia-cuda-toolkit` 11.8, nicht CUDA 12.2. Treiber
535 kann grundsätzlich CUDA-12.x-Minor-Kompatibilität bieten; daraus folgt
nicht, dass das Debian- und das NVIDIA-Repository beliebig gemischt werden
dürfen. Außerdem muss ein Produktionserver keinen Compiler enthalten, wenn
Kernel reproduzierbar in einer getrennten Buildumgebung gebaut werden.

Keine dieser Änderungen ist für G0 autorisiert.

## 5. Hohe technische Korrekturen

### V2-P1-01 – Offene Ports sind nicht automatisch öffentlich erreichbar

`0.0.0.0` zeigt eine Bindung an alle lokalen Interfaces. Ohne Firewall-,
Provider-ACL-, Routing- und externen Erreichbarkeitstest ist „öffentlich“ nicht
bewiesen. Die Bindungen sind dennoch ein dringender Prüfpunkt. Root-Uvicorn und
Remote-Desktop wären – falls bestätigt – Härtungsrisiken.

Port 8080 aus dem App-Builder-Previewvertrag ist kein zwingender Debian-
Produktionsport. Ein interner AURELIA-Port wird erst im Pilotprofil festgelegt.

### V2-P1-02 – „Server ist für Phase 1–2 richtig“ ist zu weit

Für synthetische Phase 1 kann der berichtete Zustand genügen. Für Phase 2 mit
Art.-9-Daten genügen Hardware und laufende Dienste nicht. Ungeprüfte Firewall,
Legacy-Prozesse, Root-Dienste, Treibermismatch, Schlüssel- und Restorestatus
halten `GATE-PROFILE` und `GATE-ART9` rot.

### V2-P1-03 – CUDA-Streams/Arenen sind keine Sicherheitsgrenze

Getrennte Streams und Arenen sind notwendige Softwaredisziplin, aber keine
starke Tenantgrenze. Erforderlich sind ein vertrauenswürdiger `gpud`, keine
beliebigen Tenant-Kernel, Prozess-/CUDA-Kontextmodell, Speicherbereinigung,
OOM-/Reset-/Fault-Containment und adversarielle Negativtests. Die RTX 4000 SFF
Ada besitzt nach offizieller Liste keine MIG-Isolation.

### V2-P1-04 – Exakter CPU-/RT-Plan ist verfrüht

Die vorgeschlagene Aufteilung ignoriert SMT-Sibling-Topologie, IRQs, NUMA-
Beobachtung, thermisches Verhalten und reale Lastprofile. `SCHED_FIFO` kann
normale Prozesse unbegrenzt verdrängen und einen Server destabilisieren.

Zuerst: cgroup-/systemd-Grenzen, Thread-Caps und Störlastmessungen. CPUAffinity
oder Echtzeitklassen erst nach Benchmark, Runtime-Limit, Watchdog, Killpfad und
Rollback.

### V2-P1-05 – Kryptografiedesign ist zu früh festgelegt

AES-GCM und HKDF sind etablierte Bausteine, aber noch kein AURELIA-Schlüsseldesign.
Offen sind zufällige/versionierte DEKs, KEK-Wrapping, Key/IV-Eindeutigkeit,
Associated Data, Rotation, Backups, Recovery, Crypto-Erasure, Suchlecks,
TPM-Sealing und Break-Glass.

„Deterministische Verschlüsselung für Suchindizes“ erzeugt Gleichheits- und
Häufigkeitslecks und darf nicht als beiläufige Standardlösung aufgenommen
werden. Algorithmus- und KDF-Festlegung folgt erst Threat Model und Datenfluss.

### V2-P1-06 – PGlite/Neon sind nicht semantisch bewiesen identisch

Eine gemeinsame `Sql`-Oberfläche ist positiv. Sie beweist keine vollständige
Parität von PostgreSQL und PGlite bei RLS, Extensions, Sperren, Parallelität,
Transaktionen, Typen oder Fehlerfällen. Produktive Isolation muss gegen die
reale PostgreSQL-Rollenstruktur getestet werden.

### V2-P1-07 – RLS-Testmodell ist unvollständig

„Falscher Tenant liefert leer“ reicht nicht. Tabellenowner und Rollen mit
`BYPASSRLS` umgehen RLS; `FORCE ROW LEVEL SECURITY`, separate Owner/Migration/
Runtime-Rollen, Grants/Revokes und Schreib-, Nebenkanal- sowie Background-Job-
Tests sind nötig.

### V2-P1-08 – Bitidentische CPU-/CUDA-Replays sind nicht automatisch realistisch

Floating-Point-Reihenfolge, FMA, Bibliotheken und Compiler können Bits
verändern. `repro: strict` braucht einen exakt definierten Algorithmus,
Toolchain, Rundungsmodus und gegebenenfalls Integer-/Fixed-Point-Referenz.
Andere Kernel benötigen dokumentierte Toleranzen und kanonische
Vergleichsmetriken.

AVX-512-VNNI/BF16 ist nicht automatisch für Haar-/p-adische Floatberechnung
geeignet; niedrigere Präzision kann dem Reproduzierbarkeitsziel widersprechen.

### V2-P1-09 – Timer-/WAL-Sprache bleibt unpräzise

Anwendungsupdates erzeugen WAL; ein PostgreSQL-Checkpoint ist etwas anderes.
Persistiert werden fachliche Zustände und Zeitbelege. Innerhalb eines Boots
kann eine monotone Uhr verwendet werden; über Reboots hinweg sind UTC-
Zeitbezug, Boot-ID und dokumentierte Lückensemantik erforderlich.

### V2-P1-10 – Merkle, GBNF und Offline

- Merkle plus Ed25519 beweist Integrität eines Manifests, nicht die fachliche
  Richtigkeit der Berechnung. Ein Dritter benötigt Daten oder geeignete
  Commitments/Proofs.
- GBNF kann JSON-Syntax begrenzen, nicht die rechtliche Bedeutung von
  `cleaned_text`. Lexikon, Policies, Tests und menschliche Freigabe bleiben
  maßgeblich.
- Last-Writer-wins ist nicht „konfliktfrei“, sondern eine verlustbehaftete
  Konfliktpolitik. PGlite Sync ist Alpha und löst keine bidirektionale
  Offline-Akten-Synchronisation. IN-07 bleibt Forschung und widerspricht dem
  aktuellen No-sensitive-IndexedDB-/Service-Worker-Grundsatz.

## 6. Aufwand und Machbarkeit

„Kein technisch Unmögliches identifiziert“ ist nur als
`kein bisher bewiesener Widerspruch` zulässig. Die Anforderungen der
Radionikmodule, reale Kernelkosten, Emitterprotokolle, HRV-Hardware,
Sicherheitsprüfungen und Rechtsabgrenzung sind noch nicht vollständig bekannt.

Die Dauerangaben sind nicht belastbar:

- Executive Summary: 9–15 Monate Vollzeit;
- Phasenplan: 9–12 Monate Vollzeit;
- agentengestützt/Betreiberreviews: 12–20 Monate;
- keine ausgewiesenen Abhängigkeiten für G0, Recht, externe Reviews,
  Beschaffung, Penetrationstest, Pilotkorrekturen und Ausfallzeiten;
- keine Schätzbasis oder Konfidenzklasse.

Die Bänder können als erste Schätzfragen archiviert werden, nicht als Planung.
Erst nach G0, Threat Model, M-G1-Profil, Prototypeninventar und WBS entsteht
eine belastbare Terminprognose.

## 7. Kontrollierte Konsolidierung

### 7.1 In G0/AUDIT-02 übernehmen

- v2 als externe, commitlose Analysequelle registrieren;
- Branch-/Commit-/Zeit-/Exitcode-/Hashpflicht für künftige Analysen;
- Cross-Platform-Testfinder und `zero tests = red` – bereits in G0-Plan 01;
- die direkten Skripttestfehler als zu triagierende Evidenz, nicht pauschal als
  Produktdefekte;
- SRV-01 bis SRV-05 als unbestätigte Inputs für den späteren M-G1-Collector;
- `GATE-CUDA` um Prozess-/Kontext- und Fault-Containment erweitern;
- Risiken für Legacy-Dienste, Portbindung, Root-Prozesse, Treiberdrift,
  Repository-Mix und Produktions-Buildtoolchain;
- keine Serverbeobachtung darf automatisch eine Änderungsfreigabe erzeugen.

### 7.2 Nach `GATE-G0 green`

1. signierte/read-only M-G1-Inventur mit Rohbelegen;
2. Threat Model und DATA-/FLOW-Inventar;
3. Produktionsprofil und Alt-/Neu-Isolationsplan;
4. Krypto- und Schlüsselmanagementdesign;
5. Rollen-/RLS-/Grant-/Lifecycle-Design;
6. IPC-/Daemon-Vertrag innerhalb des modularen Monolithen;
7. Backup-/Restore- und Fehlerdomänenentscheidung;
8. erst danach Wartungs- und CUDA-Änderungsplan;
9. Kernel-/Prototypeninventar und messbare WBS;
10. Claims-/MDR-/HWG-/HRV-Freigabe.

### 7.3 Als Backloginput erhalten

- Kernel-Manifest und Registry;
- signierte Golden Files;
- synthetischer Daemon-Roundtrip;
- Emitter-Simulator und Lease-Automat;
- fachlicher WebSocket-Kanal ohne Zeugenklartext;
- Restore-Ritual und Monitoringziele;
- Computation-Manifest mit Integritätsnachweis;
- Done-when-/Gate-Kriterien je Arbeitspaket.

### 7.4 Nicht übernehmen

- 95-/85-/25-Prozentwerte;
- „kein Medizinprodukt“ als abgeschlossenes Faktum;
- 9–15 Monate als Zusage;
- Phase 0 abgeschlossen / direkte Phase-2-Fortsetzung;
- sofortiger Reboot oder Toolkitinstallation;
- öffentlicher Portstatus ohne Netzwerkevidenz;
- feste CPU-Zuordnung und `SCHED_FIFO`;
- CUDA-Stream als Tenant-Sicherheitsgrenze;
- deterministische Tenant-Schlüssel oder Suchverschlüsselung als Vorentscheidung;
- statischer `check:auth` als Ersatz der Live-Invariante;
- PGlite-LWW als produktive Offline-Lösung;
- pauschale bitidentische CPU-/CUDA-Ausgabe;
- Merkle oder GBNF als Korrektheits-/Rechtsbeweis.

## 8. Primärquellen

### Projektinterne Autorität

- `AGENTS.project.md` und Kanoncommit
  `b20ee873347c5fd767e2089c993f1cf93a625def`
- G0-Designcommit `a6a8e7dca456d14a6748b204b787b235fdedf9be`
- G0-Masterplan und Plan 01/10 im G0-Worktree

### Externe Quellen

- EU-MDR: <https://eur-lex.europa.eu/legal-content/En/TXT/PDF/?uri=CELEX%3A32017R0745>
- MDCG Software Guidance: <https://health.ec.europa.eu/document/download/b45335c5-1679-4c71-a91c-fc7a4d37f12b_en?filename=mdcg_2019_11_en.pdf>
- DSGVO: <https://eur-lex.europa.eu/legal-content/DE/TXT/?qid=1519649745211&uri=CELEX%3A32016R0679>
- AMD Ryzen 5 9600X: <https://www.amd.com/en/products/processors/desktops/ryzen/9000-series/amd-ryzen-5-9600x.html>
- NVIDIA RTX 4000 SFF Ada: <https://www.nvidia.com/es-la/products/workstations/rtx-4000-sff/>
- NVIDIA MIG-Support: <https://docs.nvidia.com/datacenter/tesla/mig-user-guide/supported-gpus.html>
- NVIDIA CUDA 12.2 Release Notes: <https://docs.nvidia.com/cuda/archive/12.2.2/cuda-toolkit-release-notes/index.html>
- NVIDIA CUDA Compatibility: <https://docs.nvidia.com/deploy/cuda-compatibility/minor-version-compatibility.html>
- NVIDIA NVML: <https://docs.nvidia.com/deploy/pdf/NVML_API_Reference_Guide.pdf>
- Debian Bookworm CUDA Toolkit: <https://packages.debian.org/bookworm/nvidia-cuda-toolkit>
- Linux Scheduling: <https://www.man7.org/linux/man-pages/man7/sched.7.html>
- Linux RT Group Scheduling: <https://docs.kernel.org/scheduler/sched-rt-group.html>
- PostgreSQL RLS: <https://www.postgresql.org/docs/current/ddl-rowsecurity.html>
- PostgreSQL WAL: <https://www.postgresql.org/docs/16/wal-intro.html>
- NIST AES-GCM: <https://csrc.nist.gov/pubs/sp/800/38/d/final>
- NIST KDF: <https://csrc.nist.gov/pubs/sp/800/56/c/r2/final>
- PGlite: <https://pglite.dev/docs/about>
- PGlite Sync: <https://pglite.dev/docs/sync>
- RFC 6962: <https://www.rfc-editor.org/info/rfc6962/>
- llama.cpp Grammars: <https://github.com/ggml-org/llama.cpp/blob/master/grammars/README.md>

## 9. Schlussfolgerung

v2 soll v1 als **besser strukturierte externe Arbeitsanalyse** ergänzen, aber
nicht als Wahrheit ersetzen. Ihre validen Teile werden nach G0 in
evidenzgebundene Arbeitspakete überführt. Die fünf genannten „Sofortmaßnahmen“
werden nicht in dieser Form freigegeben:

- Testfinder: ja, bereits in G0-Plan 01;
- Kanonbereinigung: im Kanon bereits umgesetzt;
- Typecheck: im Kanon grün;
- Reboot/Toolkit: späterer, separater Change-Plan;
- Krypto/IPC: wichtige post-G0-Designpakete, nicht vor Threat Model und
  Datenfluss festlegen;
- CPU-Pinning: erst nach Messung und Risikodesign.

Die nächste sachgerechte Arbeit bleibt AUDIT-02 und die eindeutige
G0-Wellensequenz, nicht der Start von Phase 2 oder eine Serveränderung.

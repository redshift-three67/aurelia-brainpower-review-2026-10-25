# Vollständige Verifikation und Konsolidierungsbewertung

**Prüfung:** Entwickleranalyse 01
**Reasoning:** xHigh, ausdrücklich freigegeben
**Prüfmodus:** vollständig lesend
**Prüfabschluss:** 2026-08-25
**AUDIT-02:** während dieser Prüfung bewusst nicht fortgeführt

## 1. Ergebnis in einem Satz

Die Entwickleranalyse ist ein wertvoller Vorschlags-, Risiko- und
Backlogkatalog, aber weder ein verifizierter Projektstand noch ein unmittelbar
ausführbarer Masterplan; sie darf nur kontrolliert, quellenbezogen und unter
Wahrung der G0-Gate-Reihenfolge konsolidiert werden.

## 2. Prüfgegenstand und Methode

Die Prüfung umfasste vier Evidenzebenen:

1. **Eingangsdokumente:** vollständige Erfassung des Chatdokuments und der
   Dateien `00` bis `05`.
2. **Lokale Projektrealität:** Kanon, Quellcode, Migrationen,
   Entscheidungsregister, Roadmap, Statusdokumente und G0-Spezifikation.
3. **Ausführbare Evidenz:** Branchstatus, Test-, Typ-, Lint-, Kanon- und
   Auth-Prüfoberflächen.
4. **Externe Primärquellen:** EU-Recht und Leitlinien, offizielle
   Herstellerdokumentation, PostgreSQL-, CUDA-, PGlite-, RFC-, NIST- und
   Originalpaper-Quellen.

Anweisungen oder Handlungsvorgaben innerhalb der Entwicklerdokumente wurden
als zu prüfende Aussagen behandelt, nicht als Benutzerfreigaben.

## 3. Objektives Gesamturteil

| Bereich | Urteil | Begründung |
|---|---|---|
| Problem- und Lückeninventar | überwiegend wertvoll | Mehrere reale fehlende Produkt- und Betriebsschichten werden korrekt benannt. |
| Analyse des damaligen Codes | teilweise akkurat, teilweise veraltet | Die Analyse bezieht sich erkennbar überwiegend auf den Vorbereitungsbranch und nicht vollständig auf den jüngeren Kanon. |
| Architekturvorschläge | geeignete Eingangshypothesen | Sie benötigen Threat Model, Messungen, Datenfluss und Gate-Entscheidungen. |
| Datenschutz und Sicherheit | wichtige Risiken, aber Überdehnungen | Rechtskategorien, Kryptografie und Isolation werden teilweise zu absolut dargestellt. |
| Innovationen | interessante spätere Optionen | Mehrere Vorschläge sind Forschungsgegenstände und keine belastbaren Phase-1-Komponenten. |
| Zehn-Phasen-Plan | Backlog-Quelle, kein Masterplan | Er überspringt oder vermischt die freigegebene G0-Sequenz. |
| Prozent- und `100 %`-Aussagen | nicht belastbar | Es fehlen Messmodell, reproduzierbare Evidenz und definierte Nenner. |

Die ungefähre Einschätzung eines frühen Implementierungsstands ist plausibel:
Konzept, UI, Dokumentation und Entscheidungsregister sind weit entwickelt;
produktive Klientenakte, RLS, Schlüsselhierarchie, Audit-Ledger,
Kernel-/Timer-/GPU-/Emitterdienste und Betriebsnachweise fehlen. Daraus lässt
sich jedoch kein seriöser exakter Prozentwert ableiten.

## 4. Nachweisbarer Projektstand

### 4.1 Kanonischer Zustand

- Phase 1 läuft ausschließlich mit `data_class=synthetic`.
- Keine realen Klientenakten, keine produktive CUDA-Aktivierung, kein USB- oder
  Hardwarebetrieb und kein Video.
- D01–D08, D10, D12–D24, C01–C12, X01–X20, U01–U12, K1–K5 und H1–H3 sind im
  Kanon vorhanden.
- G0 dient dazu, Quellenhierarchie, Governance, Rollen, Nachweise, Gates,
  kryptografische Bootstrap-Vertrauensanker und Recovery-Schreibpfade
  revisionssicher zu machen.
- G0 schließt eine Serveränderung, produktive Authentifizierung, RLS,
  Schlüsselverwaltung, Datenmigration, reale Daten, CUDA-/USB-Aktivierung und
  rechtliche Freigaben ausdrücklich aus.

### 4.2 Implementierter Stand

- Die UI- und Konzeptoberfläche, Auth-Hülle, synthetische
  Mandantenmitgliedschaften und zwei Migrationsebenen sind vorhanden.
- `migrations/0002_tenants.sql` legt Mandanten und Mitgliedschaften an, enthält
  aber keine produktiven RLS-Policies.
- `src/lib/db.ts` verwendet bei gesetzter `DATABASE_URL` einen realen
  PostgreSQL-/Neon-Pfad und ansonsten einen gemeinsamen, **serverseitigen und
  flüchtigen** PGlite-Preview-Fallback.
- Die produktiven Dienste `gpud`, `timerd`, Emitter, CopyGuard und der
  Radionik-Kernel sind nicht implementiert.
- Vorhandene FastAPI-/NATS-/Redis-/Timescale-/MinIO-Beschreibungen sind
  Architekturkonzepte und keine belegte laufende Zielplattform.

### 4.3 Testevidenz

Auf `codex/aurelia-vorbereitung`:

- `npm test` scheiterte an einer fehlenden Auflösung von
  `@tanstack/react-start`.
- Typecheck und weitere Checks spiegelten den älteren beziehungsweise nicht
  vollständig vorbereiteten Branchzustand wider.

Auf `codex/aurelia-kanon-implementation`:

- `npm test` meldete Erfolg und führte 24 Quelltests aus.
- Der vorgeschaltete Befehl mit `scripts/**/*.test.mjs` führte unter Windows
  wegen des literal behandelten Globs jedoch **null** Skripttests aus.
- Der direkte Start `node --test scripts/*.test.mjs` führte 161 Tests aus:
  146 bestanden, 15 schlugen fehl.
- Ein Teil der 15 Fehler ist umgebungs- oder Template-spezifisch; der
  plattformübergreifend falsche Teststart ist dennoch ein realer
  Qualitätsblocker.
- Typecheck, Lint und `check:canon` bestanden auf dem Kanon-Branch.
- `check:auth` benötigt nach seinem gegenwärtigen Vertrag einen laufenden
  Devserver; ohne diesen ist ein Fehlschlag kein Beweis für einen Auth-Defekt.

Folgerung: Der Entwicklerhinweis, die Testoberfläche zu reparieren, ist richtig;
seine konkrete Fehlerbeschreibung ist teilweise veraltet und unvollständig.

## 5. Bestätigte und übernehmbare Aussagen

Folgende Inhalte sind richtungsrichtig und sollen als Planungsinput erhalten
bleiben:

- produktive RLS-, Rollen-, Grant- und Negativtests fehlen;
- Schlüsselverwaltung, Rotation, Recovery und Crypto-Erasure benötigen ein
  vollständiges Design;
- Audit-, Einwilligungs-, Retention-, Lösch- und Incident-Prozesse fehlen;
- Kernel- und Prototypenaufnahme sollen ausschließlich über eine versionierte,
  getestete ABI erfolgen;
- GPU-, Timer- und Hardwarepfade benötigen explizite Quoten, Fehlerbehandlung,
  Reset- und Recovery-Semantik;
- der einzelne M-G1 bleibt eine gemeinsame Fehlerdomäne;
- Restore, Backup, Wiederanlauf und Schlüsselwiederherstellung müssen praktisch
  getestet werden;
- Leistungen und Kapazitäten müssen auf dem realen M-G1 mit definierten
  Workloads reproduzierbar gemessen werden;
- Claims, Reports, Gesundheitsnähe und Werbeaussagen benötigen eine eigene
  rechtliche und fachliche Freigabekette.

## 6. Kritische Differenzen und Korrekturen

### P0 – Gate- und Ablaufkonflikt

Der Entwicklerplan schlägt vor, Phase 1 zu reparieren und anschließend
unmittelbar weitere Produktphasen zu implementieren. Das widerspricht dem
freigegebenen G0-Modell. Erst G0, dann Threat Model, Datenfluss, M-G1-Profil,
RLS/Schlüssel und Betriebsarchitektur. Der Zehn-Phasen-Plan darf G0 nicht
ersetzen.

### P0 – Branch- und Aktualitätsproblem

Mehrere Aussagen stammen aus dem Vorbereitungsbranch. `check:canon` existiert
und besteht im Kanon bereits; der ursprüngliche Modultestfehler ist dort nicht
mehr derselbe. Jede künftige Analyse muss Branch, Commit, Datum und
Arbeitsbaumstatus nennen.

### P0 – Test-Gate

Ein grünes `npm test`, das unter einer Plattform stillschweigend null
Skripttests ausführt, ist kein belastbarer Gate-Nachweis. Der Runner muss Globs
plattformunabhängig expandieren oder eine explizite Dateiliste erzeugen. Null
gefundene Tests müssen fehlschlagen.

### P0 – CUDA-Isolation

Ein eigener CUDA-Stream und ein logisch getrennter Speicherbereich sind keine
Sicherheitsgrenze. Streams regeln Reihenfolge und Nebenläufigkeit. Für
AURELIA sind mindestens erforderlich:

- definiertes Angreifer- und Vertrauensmodell;
- keine beliebigen, nicht geprüften Tenant-Kernel;
- vertrauenswürdiger `gpud`-TCB;
- Prozess-/CUDA-Kontextstrategie;
- Speicherbereinigung und Canary-Negativtests;
- OOM-, Timeout-, Reset- und Fehlerfortpflanzung;
- Bewertung von MPS-Grenzen;
- Attestation und reproduzierbare Jobzuordnung.

Die RTX 4000 SFF Ada wird in der offiziellen MIG-Unterstützung nicht als
MIG-GPU geführt. MIG darf daher nicht implizit als verfügbare Hardwaregrenze
eingeplant werden.

### P0 – Medizinprodukt- und Werberecht

Ein Disclaimer allein legt die regulatorische Einordnung nicht fest.
Entscheidend sind Zweckbestimmung, Funktionen, Benutzerführung, Reports,
Werbung und Vertriebsbehauptungen. HRV, physiologische Auswertung und
Wirkversprechen erhöhen das Abgrenzungsrisiko. Erforderlich sind ein formales
Intended-Purpose-/Qualification-Memo, Claims-Register und fachlich-juristische
Freigabe.

### P1 – Modularer Monolith statt pauschaler Microservices

Die freigegebene Strategie bleibt:

- eine modulare Control Plane;
- getrennte privilegierte Prozesse nur bei begründetem Gerätebesitz, Timing,
  Privilegien oder Fehlerisolation;
- ein klarer lokaler IPC-Vertrag mit Schema, Authentisierung, Backpressure,
  Idempotenz und Fehlercodes;
- keine gleichzeitige Einführung von FastAPI, Redis und NATS ohne nachgewiesene
  Notwendigkeit.

### P1 – PGlite und Offlinebetrieb

Der aktuelle PGlite-Pfad ist keine Browser-Offline-Akte. PGlite Sync ist Alpha
und stellt keine vollständige bidirektionale, konfliktfreie Synchronisation
realer Klientendaten bereit. Offline- oder IndexedDB-Betrieb widerspricht
gegenwärtig D15 und bleibt bis zu Datenfluss, Verschlüsselung,
Geräteverlustmodell, Remote-Wipe, Konfliktmodell und `GATE-ART9` gesperrt.

### P1 – RLS

`tenant_id` und eine Absichtserklärung genügen nicht. Das spätere Design muss
enthalten:

- explizite Policies für alle Operationen;
- separate Owner-, Migrations- und Laufzeitrollen;
- Grants und Revokes;
- Bewertung von `FORCE ROW LEVEL SECURITY`;
- Schutz gegen Owner-/`BYPASSRLS`-Umgehung;
- Negativtests über Mandanten, Rollen und Hintergrundjobs;
- Retention, Löschung, Audit und Einwilligungsnachweise.

Der in der Entwickleranalyse skizzierte SQL-Ausschnitt ist dafür nicht
vollständig.

### P1 – Schlüsselhierarchie

KEK, TPM/Keyring und ein per HKDF abgeleiteter Tenant-Schlüssel sind nur eine
Hypothese. Vor einer Festlegung sind zu definieren:

- zufällige, versionierte Daten- beziehungsweise Objektschlüssel;
- Wrapping durch rotierbare KEKs;
- Nonce- und AEAD-Regeln;
- Rollen- und Prozesszugriff;
- Backup und Wiederherstellung ohne Verlust der Schlüssel;
- Rotation und Re-Encryption;
- Crypto-Erasure und Tenant-Offboarding;
- TPM-Sealing, Recovery-Root und Break-Glass;
- Swap-, Core-Dump- und Speichergrenzen.

### P1 – Merkle ist nicht Zero-Knowledge

Ein RFC-6962-artiger Merkle-Baum kann Einschluss und Append-only-Konsistenz
belegen. Er beweist weder die fachliche Korrektheit einer Berechnung noch
Zero-Knowledge. Zulässiger Arbeitsbegriff ist zunächst
`signierter Integritäts- und Reproduzierbarkeitsnachweis`. Ein echter
Zero-Knowledge- oder Verifiable-Computing-Ansatz wäre ein getrenntes
Forschungsprojekt mit eigener Kryptografieprüfung.

Der G0-Governance-Transparenzbaum und ein späterer Produktnachweis müssen
separate Domänen, Schlüssel und Logs besitzen.

### P1 – Grammatik ist keine Rechtsprüfung

GBNF kann Syntax oder JSON-Struktur begrenzen. Es kann keine medizinische,
werberechtliche oder semantische Konformität garantieren. Zulässige Lösung:
deterministische Policies, kuratierte Textbausteine, Claims-Register,
Negativtests und menschlich-juristische Freigabe. Ein LLM bleibt assistiv.

### P1 – Postgres-WAL ist nicht die Uhr

WAL ist der Durability- und Recovery-Mechanismus von PostgreSQL. Die dauerhafte
fachliche Wahrheit liegt in Tabellenzuständen, Ereignissen und der definierten
Zeit-/Recovery-Semantik. Der bestehende Kanon soll terminologisch präzisiert
werden, ohne seine Grundentscheidung – Postgres statt VRAM als persistente
Wahrheit – zu verändern.

### P2 – Kozyrev und Haar

Für `p=2` ist die Kozyrev-Basis unter der beschriebenen p-adischen Abbildung
zur Haar-Wavelet-Basis äquivalent; die uneingeschränkte Aussage „identisch“ ist
zu stark.

### P2 – Leistungs- und Betriebsziele

Werte wie `<0,2 ms`, `<100 ms`, Jitter `<10 %`, fünf Pilotpraxen, 24-Stunden-
Lasttest, RPO 15 Minuten oder RTO 8 Stunden sind Vorschläge. Vor einer
Kanonisierung benötigen sie Workload, Messmethode, Messumgebung, Owner,
Akzeptanzgrenzen und geschäftliche Freigabe.

CPU-Pinning und `SCHED_FIFO` sind vor der Live-Inventur und Messung nicht
freizugeben. Zunächst sind systemd-/cgroup-Grenzen, Prioritäten und
Störlasttests zu verwenden.

## 7. Datenschutzpräzisierung

Nicht jeder Session-, Witness- oder Protokolldatensatz ist automatisch eine
besondere Kategorie nach Art. 9 DSGVO. Gesundheitsinformationen können Art. 9
sein; biometrische Daten fallen dort insbesondere dann hinein, wenn spezielle
Verarbeitung der eindeutigen Identifizierung dient. AURELIA darf intern eine
strengere Schutzklasse verwenden, muss diese aber von der gesetzlichen
Klassifizierung trennen.

Die Aussage, Art.-9-Daten dürften rechtlich unter keinen Umständen eine
US-Cloud berühren, ist als **AURELIA-Schutzpolitik** zulässig, aber nicht als
vollständige Wiedergabe der DSGVO. Rechtlich sind zusätzlich die
Drittlandtransferregeln des Kapitels V maßgeblich. Die strengere interne
No-Egress-Policy bleibt empfohlen.

## 8. Konsolidierung in den bestehenden Plan

### 8.1 Sofort in G0/AUDIT-02 aufnehmen

1. Diese Entwicklerlieferung als externe, nicht normative Quelle registrieren.
2. Branch-, Commit-, Zeit- und Evidenzpflicht für Analysen festlegen.
3. Plattformunabhängigen Teststart in G0-Plan 01 aufnehmen.
4. Null ausgeführte Tests als Fehler behandeln.
5. `check:auth` in statische Konfigurationsprüfung und explizite Live-Probe
   trennen; fehlenden Server nicht als stillen Erfolg behandeln.
6. `GATE-CUDA` um Prozess-/Kontextgrenzen, Kernelvertrauen, OOM, Reset,
   Speicherreste und Fehlerfortpflanzung ergänzen.
7. Postgres-/WAL-Terminologie präzisieren.
8. Unbelegte Prozent-, `100 %`- und Performanceaussagen aus normativen
   Unterlagen ausschließen.
9. Übernommene Aussagen mit Quelle, Evidenzstatus, Gate, Owner und
   Akzeptanzkriterium verknüpfen.

### 8.2 Erst nach `GATE-G0 green`

1. Read-only-Inventur des realen M-G1.
2. Threat Model und vollständiger Datenfluss.
3. Rollen-, Grants-, RLS- und Schlüsselarchitektur.
4. Modularer Monolith, begründete privilegierte Daemons und IPC-Vertrag.
5. Backup-, Restore-, RPO-/RTO- und zweite-EU-Fehlerdomänenentscheidung.
6. CPU-/GPU-Benchmarks auf M-G1.
7. Kernel-/Modul-ABI und kontrollierte Prototypenaufnahme.
8. Claims-, HWG-, MDR- und Datenschutzprüfung.
9. Erst danach HRV/Web-Bluetooth, Offlinebetrieb oder weitere Hardwarepfade.

### 8.3 Als Forschungsoption aufbewahren

- Browserbasierte Offline-Klientenakte;
- Web-Bluetooth-HRV im Regelbetrieb;
- echte Zero-Knowledge-Proofs oder Verifiable Computing;
- NATS/Redis als zusätzliche Infrastruktur;
- konkrete Vendor-Festlegungen;
- feste CPU-Pinnings oder Echtzeit-Scheduling;
- harte Leistungsversprechen ohne M-G1-Benchmark.

### 8.4 In vorliegender Form nicht übernehmen

- pauschale `100 %`-Qualitäts-, Sicherheits- oder Rechtskonformitätsaussagen;
- CUDA-Stream gleich Sicherheitsisolation;
- Merkle gleich Zero-Knowledge oder Berechnungskorrektheit;
- GBNF gleich HWG-/MDR-Konformität;
- PGlite gleich bidirektionale produktive Offline-Synchronisation;
- Disclaimer gleich abschließende Medizinprodukteklassifizierung;
- direkte Fortsetzung in Produktphase 2 vor G0;
- gleichzeitige Einführung eines vollständigen Microservice-Stacks;
- ungemessene Leistungs-, Kapazitäts- oder Wiederanlaufversprechen.

## 9. Empfohlene weitere Reihenfolge

| Reihenfolge | Schritt | Empfohlenes Reasoning |
|---:|---|---|
| 1 | AUDIT-02 unter Einbezug dieser Befunde abschließen | xHigh |
| 2 | Kontrollierten Konsolidierungsentwurf erstellen | xHigh |
| 3 | Sanitisierten Prompt für eine unabhängige externe Gegenprüfung bereitstellen | externes Modell |
| 4 | Reviewergebnis quellenbezogen prüfen | xHigh |
| 5 | Dokumentation/Handoff aktualisieren und lokal verifizieren | high |
| 6 | Nach Freigabe Commit, Push und SHA-Verifikation | high |
| 7 | Nach `GATE-G0 green` M-G1-Inventur und Threat Model beginnen | xHigh |

Eine Reasoning-Änderung erfolgt nach der bestehenden Direktive nicht
automatisch, sondern erst nach ausdrücklicher Benutzerbestätigung.

## 10. Externe Primärquellen

### Recht und Datenschutz

- EU-MDR: <https://eur-lex.europa.eu/legal-content/En/TXT/PDF/?uri=CELEX%3A32017R0745>
- MDCG 2019-11 Rev. 1: <https://health.ec.europa.eu/document/download/b45335c5-1679-4c71-a91c-fc7a4d37f12b_en?filename=mdcg_2019_11_en.pdf>
- DSGVO: <https://eur-lex.europa.eu/legal-content/DE/TXT/?qid=1519649745211&uri=CELEX%3A32016R0679>
- Heilmittelwerbegesetz: <https://www.gesetze-im-internet.de/heilmwerbg/>

### Hardware, CUDA und Isolation

- AMD Ryzen 5 9600X: <https://www.amd.com/en/products/processors/desktops/ryzen/9000-series/amd-ryzen-5-9600x.html>
- NVIDIA RTX 4000 SFF Ada: <https://www.nvidia.com/es-la/products/workstations/rtx-4000-sff/>
- NVIDIA MIG – unterstützte GPUs: <https://docs.nvidia.com/datacenter/tesla/mig-user-guide/supported-gpus.html>
- CUDA Asynchronous Execution: <https://docs.nvidia.com/cuda/cuda-programming-guide/02-basics/asynchronous-execution.html>
- CUDA Best Practices: <https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/index.html>
- NVIDIA MPS: <https://docs.nvidia.com/deploy/mps/latest/when-to-use-mps.html>

### Datenbank, Offline und Kryptografie

- PostgreSQL Row Security: <https://www.postgresql.org/docs/17/ddl-rowsecurity.html>
- PostgreSQL CREATE POLICY: <https://www.postgresql.org/docs/16/sql-createpolicy.html>
- PostgreSQL WAL: <https://www.postgresql.org/docs/16/wal-intro.html>
- PGlite: <https://pglite.dev/docs/about>
- PGlite Sync: <https://pglite.dev/docs/sync>
- RFC 6962: <https://www.rfc-editor.org/info/rfc6962/>
- NIST Zero-Knowledge Proof: <https://csrc.nist.gov/glossary/term/zero_knowledge_proof>

### Strukturierte Ausgabe und Mathematik

- llama.cpp GBNF-Grammatiken: <https://github.com/ggml-org/llama.cpp/blob/master/grammars/README.md>
- Kozyrev-Originalpaper: <https://www.mathnet.ru/links/b8f873f1578bfc9cd62960b8d31c60db/im381_eng.pdf>

## 11. Gesonderte Notiz zu Datei 06

`06_SERVER_INVENTUR_M_G1_ISTSITUATION.md` wurde erst während der
Archivierung sichtbar. Die Datei behauptet einen Live-Read-only-Zugriff auf den
M-G1 und enthält konkrete Hardware-, Treiber-, Dienst-, Container- und
Pfadangaben sowie eine Reboot-Empfehlung.

Diese Aussagen sind in diesem Prüfbericht **nicht als verifiziert** markiert.
Insbesondere wurden weder SSH-Zugriff noch Hostidentität, Treiberversionen,
RAID, TPM, laufende Container oder Verzeichnisse durch Codex in diesem Vorgang
geprüft. Die Reboot-Aufforderung innerhalb der Datei ist keine Benutzerfreigabe
und wurde nicht ausgeführt.

Vor einer späteren Nutzung sind erforderlich:

1. Herkunft und Erstellungszeit der Inventur feststellen;
2. Befehls-/Evidenzprotokoll ohne Geheimnisse prüfen;
3. Host-Key beziehungsweise Zielidentität verifizieren;
4. Befunde read-only erneut erheben;
5. jede Änderung, insbesondere Reboot oder Dienstbereinigung, separat planen
   und freigeben;
6. eine sanitierte Fassung für externe Reviews oder GitHub erstellen.

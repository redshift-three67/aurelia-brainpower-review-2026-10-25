# Aurelia – Modulbestand und Vorbereitung der Datenstruktur

Erweiterung vom 09.10.2026: [Datenbereiche, Archive und Echtzeit](AURELIA_DATENDOMAENEN_ECHTZEIT_2026-10-09.md) erfasst Berichte, Trends, Zwischenablagen, Vorlagen, Harmonisierung und Trigger getrennt nach Modul. PostgreSQL bleibt eine Vergleichsbasis, Timescale optional; keine Strukturentscheidung vor vollständigerer Modulaufnahme.

Stand: 09.10.2026. **Lesender Bestandsabgleich und Architekturvorschlag; kein beschlossener Datenbankentwurf.** Der ursprüngliche lokale Erstabgleich erfolgte vor Eingang der zusätzlichen Quellen. Copen/Bohm sind inzwischen an einen gemeinsamen Explorer-Commit gebunden, Thom an einen eigenen Commit; siehe den aktuellen Nachtrag unten. Die frühere Aussage zu ausstehenden Links ist damit überholt.

Aktuelle Fortsetzung, Betreiberklärung 10.10.2026: [Workflow-Abdeckung vom 10.10.2026](AURELIA_WORKFLOW_ABDECKUNG_2026-10-10.md). Vollständige Funktionalität/Struktur/Workflows für Modulvorbereitung erfassen; keine bestehenden Testklienten oder laufenden Aufträge übernehmen. Neue P2-Cloud-Teilstagings sind zurückgestellt und blockieren diese Source-Erfassung nicht. P1 wurde im ausgewählten lokalen SQL-Umfang ausgeführt; die 22 Fallgruppen sind nicht vollständig abgenommen. Reale Rechte-/Diensteprüfungen bleiben spätere Integrationsgates; zentrale Strukturentscheidung mit dem Betreiber nach dem gemeinsamen Modulabgleich.

Keine Produktdateien, Modulalgorithmen, laufenden Instanzen, Governors-Registrierungen, Anwendungsrouten oder Datenbankschemata verändert. Neue Dateien enthalten ausschließlich Prüfwerkzeug, Metadaten und diesen Bericht. Kein neuer Governors-Modellauftrag, kein Access-Formular-/Makrostart, keine Datensätze gelesen oder exportiert. Die vollständige F:-Sicherung vom 09.10.2026 bleibt ein früherer Wiederherstellungspunkt; dieser neue Bericht ist darin noch nicht enthalten.

Maßgebliche Reihenfolge nach Betreiberergänzung 10.10.2026: [lokale Referenzen und zentrale Datenstruktur](superpowers/plans/2026-10-10-aurelia-module-lokale-referenz-und-datenstruktur.md). Erst gesicherte Originalbaselines/Machbarkeit, dann strukturtreue lokale Explorer-/Thom-Umgebungen und Funktionstests, sechs Modul-Reasonings schließen, sieben Module einschließlich RadiWorks gemeinsam konsolidieren, zentrale Struktur mit Betreiber entscheiden/vorbereiten, danach einzelne Module und Aurelia gemäß abgestimmten Modul_Templates integrieren. Lokale Ist-Referenzschemata sind keine Entscheidung über die spätere zentrale Datenbank. Noch keine Portierung/Installation begonnen.

## 1. Belegte Stände und Grenzen

| Bereich | Aktuell belegt | Für die Datenstruktur noch offen |
|---|---|---|
| RadiWorks R6.2 | Abschluss vom 08./09.10.: 200 manifestierte Produktdateien synchronisiert, Fälle/Aufträge/Kontextstände, Kataloge, GV-/Watchlist-Historie, Medienprofile und bis fünf Bildlayer. Start5 0.4.0-rc1 lokal geprüft; Betreiber bestätigt Portable5 auf weiterem PC funktionsfähig. | Autoritative Aurelia-Rechte, gemeinsame Katalogverwaltung, Quotas, Ubuntu-Abnahme und S4.8. Betreiberprüfung und lokale Paketprüfung sind getrennte Belege; keine neue Laufzeitprüfung in dieser Inventur. |
| Aurelia | Authentifizierung und Mandantenzuordnung im lokalen Code; Migrationen für Auth sowie `tenants`/`memberships`. `src/lib/db.ts` verwendet `pg` bei gesetzter DATABASE_URL, sonst flüchtiges PGlite. | Moduljobs, Aborechte, Katalogversionen, RLS und Medienverwaltung als Produktionsvertrag; tatsächlicher Serverbetrieb und aktive Schemafassung nicht frisch geprüft. |
| Radi144 | Python/FastAPI plus CLI/PowerShell; JSON-Verwaltung für Klienten, Sitzungen, Artefakte und Audit; vollständige Berichte als Dateien. Bestehende Matrixberechnung bleibt Modulzuständigkeit. | Mandantenbezug, zentrale Rechte, Klienten-ID-Zuordnung und Aurelia-Adapter. Lokaler Templateadapter ist ein PowerShell-Leseadapter. |
| RadiMorphic | Root und registrierter Worktree sind verschiedene Quellstände; SQLite-Kataloge und Dateiergebnisse. Worktree ergänzt dauerhafte JSON-Jobzustände und Owner-Methoden. | Autoritativer Quellbaum, vollständige Durchsetzung der Owner-/Tenant-Bindung in allen Routen, Abovergabe, Katalog-/Ergebnisrevisionen und Adapter. |
| RadiFarben | Aktuelle Access-Metadaten frisch und lesend erfasst: 49 lokale Tabellen, fünf verknüpfte Tabellen, 499 lokale Felder und 47 benannte QueryDefs. | Aktuelle VBA-/Abfragesemantik, verknüpfte Datenquellen, aktive Berechnungspfade und synthetische Referenzausgaben. Noch kein neuer Linux-/Web-Prototyp implementiert. |
| Modul_Templates | Gemeinsames Zielmodell und additive R6-Nachträge; normative Hostverträge unverändert. | Aktuelle Quellzuordnung weiterer Module, Datenhoheit, neutraler Kernvertrag mit modulspezifischen Fähigkeiten; kein universeller Zwang zu RadiWorks-Funktionen. |
| Governors | Fünf Projekte in `aurelia-integration` registriert; RadiFarben noch nicht registriert. Aufnahmebelege vom 15.09.2026, automatische Reviews aus. | Frische Aufnahme-/Scope-Belege vor neuem Gruppenreview; Quellenentscheidung für Morphic; spätere ausdrückliche Aufnahme von RadiFarben. |

## 2. RadiFarben: frische Quellenbindung

Quelle: `C:/Users/Hubert111/Documents/Radifarben/RadiFarben.accdb`, 86.454.272 Bytes.

Aktueller SHA-256: `2b48ce8dec5e0126072e0bc24f07b754b8b64af0651b080d257dcb1b0c8f13bc`.

Historische G1–G3-Belege verwenden eine Downloads-Kopie mit SHA-256 `32567c30d18e553a495f582ed5c90ac8e56837165931df6555a54b4200ee71b9`. Ihre VBA-Aussagen sind deshalb historische Hinweise und keine Nachweise der heutigen Berechnung.

Die aktuelle Metadatenerfassung verwendete **32-Bit DAO.DBEngine.120, OpenDatabase mit ReadOnly=true**. Der 64-Bit-Versuch scheiterte an einer nicht registrierten COM-Klasse; die vorhandene 32-Bit-Installation funktionierte. Quelle vor/nach lesendem Zugriff hashgleich, kein verbleibender Access-Lock. Keine Recordsets, Query-Ausführung oder Access-Anwendungsautomation. Die fünf verknüpften Tabellen wurden nicht dereferenziert.

Ergebnis des Vergleichs:

- Alle 49 lokalen Tabellennamen des historischen Katalogs sind vorhanden.
- Historische lokale Felder: 498; aktuelle lokale Felder: 499. `tblKlienten.BildRate` kommt hinzu; die übrigen lokalen Feldnamensfolgen stimmen überein.
- Fünf verknüpfte Tabellen: `Anreden_`, `Mandanten_`, `Modul_Version_`, `Spruch`, `Spruch_Autor`. Diese fehlen in der alten ODBC-Tabellenliste; das beweist keine spätere Neuerstellung, da die Provider unterschiedliche Objektsichten liefern.
- 45 Formular-, 54 Modul-, drei Bericht- und drei Makrocontainer-Dokumentnamen erfasst. Namen sind keine Inhalts-/Funktionsabnahme.
- Fünf Beziehungen erfasst, davon zwei Access-Systembeziehungen. Die drei fachlichen Beziehungen besitzen Attributwert 2 (`dbRelationDontEnforce`): keine dadurch erzwungene referentielle Integrität. Keine Prüfung vorhandener Datenintegrität durchgeführt.
- Die früheren 15 ODBC-Views/1.201 Gesamtspalten und heutigen 47 benannten QueryDefs/499 lokalen Felder haben unterschiedliche Zählgrenzen und sind kein unmittelbarer Versionsvergleich.
- Datentypgleichheit, VBA-Gleichheit, Abfragetexte/Parameter, Lookup-/Validierungsregeln und verknüpfte Quellen bleiben unbestätigt.

Datenbereiche im aktuellen Schema: Farben/Paletten, Raten/WuWei/Varianten, Klienten/Bilder/Themen, lokale Rechte sowie Radon-Datei-/Bild-/Timerstrukturen. Diese Bezeichnungen allein belegen weder aktive Funktionen noch fachliche Gleichheit mit RadiWorks. Ein zunächst lesender Farben-/Paletten-MVP ist eine mögliche Abgrenzung; Umfang und Port der Berechnungen werden erst nach aktueller Charakterisierung festgelegt.

Belege: `runtime/aurelia-data-inventory-20261009/radifarben-current-schema.json`, `radifarben-schema-comparison.json`, `capture-access-schema.ps1`. Historische Gegenbelege: `Documents/Radifarben/project_memories/G1_readonly_catalog_capture.md`, G2/G3 und `access_catalog_readonly.json`.

DAO-Lesezugriff: [Microsoft OpenDatabase](https://learn.microsoft.com/en-us/office/client-developer/access/desktop-database-reference/workspace-opendatabase-method-dao). Beziehungsattribute: [Microsoft RelationAttributeEnum](https://learn.microsoft.com/en-us/office/client-developer/access/desktop-database-reference/relationattributeenum-enumeration-dao).

## 3. Weitere Modulquellen

Radi144: `C:/Users/Hubert111/Documents/Radi144`. Relevante Belege: `app/api/resonance.py:52`, `app/api/clients.py:27`, `app/models/client_registry.py:33`, `app/models/session_archive.py:13`, `app/services/json_store.py:15`, `app/services/session_archive_service.py:93`. Die bisherige aus persönlichen Angaben gebildete Klienten-ID ist kein mandantenfähiger Plattform-Identifier. Session-Schemaversion und Algorithmusrevision sind getrennte Angaben; Vollberichte bleiben eigene Artefakte.

RadiMorphic-Root: `C:/morphic_v1`. Governors registriert stattdessen `C:/morphic_v1/.worktrees/operator-workbench-phase1`. **Keine automatische Auswahl oder Umbindung.**

| Vergleich | Root | Registrierter Worktree |
|---|---|---|
| Web-Jobs | Zustand im Prozessspeicher, Logs als Dateien | JSON-Jobzustände und Wiederherstellung zusätzlich vorhanden |
| Owner-Kontext | Operator/Workspace | Tenant-/Owner-Scope und zusätzliche strikte Prüfung |
| Schutzgrenze | Owner beim Job optional | Weiterhin optionale Owner-Angabe sowie allgemeine Methoden ohne Owner-Prüfung; vollständige Routerbindung ungeprüft |
| Scan-Vertrag | Kein `group_draft_id` | Optionales `group_draft_id`, weitere Draft-/Template-Verträge |
| Abo-Stub | Defaultfreigabe | Bytegleich; keine neue produktive Aboverwaltung belegt |
| DB-Health/Initializer | Unterschiedliche erwartete Description-Tabellen im Code | Gleicher Text, lediglich CRLF statt LF; tatsächliche DB-Schemata nicht gelesen |

`group_draft_id` ist eine modulinterne Draft-Referenz, kein Nachweis einer persistenten Plattform-/Governors-Projektmatrix. Weder Worktree-Präsenz noch registrierter Pfad beweisen eine laufende oder aktuelle Integrationsfreigabe.

## 4. Zielbild zur Besprechung

Empfehlung: **ein zentral verwalteter PostgreSQL innerhalb der genehmigten Servergrenze, mit klar getrennten Plattform-, Katalog- und Modulbereichen**. Lokale Module bleiben während der Vorbereitung funktionsfähig. Dieser Vorschlag konkretisiert das vorhandene Aurelia-Ziel; er ersetzt es nicht durch eine neue bereits implementierte Struktur.

| Datenbereich | Verantwortlicher im Ziel | Modulaufgabe / Abgrenzung |
|---|---|---|
| Nutzer, Mandanten, Mitgliedschaften, Modulabos, Quotas | Aurelia | Adapter erhält geprüften Nutzer-/Mandantenkontext; ein Clientfeld ersetzt keine Berechtigung. |
| Klienten, Fallidentität und Sichtbarkeit | Aurelia nach ausdrücklich festgelegtem Import-/Übergang | Zuordnung aus Tenant + Quellinstanz + Objekttyp + Original-ID; keine automatische Personenvereinigung nach Name/Geburtsdatum. Modulübergreifende Sichtbarkeit separat autorisieren. |
| Fallkontext und Auftrag | Aurelia-Rahmen plus unveränderlicher Modul-Snapshot | Modulparameter unverändert übernehmen; laufende Aufträge durch Fallbearbeitung oder Auswahlwechsel nicht ändern. |
| Berechnung und typisierte Ergebnisse | Jeweiliges Modul | Eigene Algorithmen, Feldbedeutungen und Revisionen erhalten. Gemeinsame Oberfläche macht Scores verschiedener Module nicht gleichwertig. |
| Öffentliche/freigegebene Kataloge | Zentral verwaltete, versionierte Katalogdomäne | Herkunft, technische Lesbarkeit, Nutzungsrechte und fachliche Freigabe getrennt verwalten. |
| Nutzer-/Mandantenimporte | Tenant-bezogene Katalogdomäne | Vorschau, Parservertrag, ausdrücklicher Import; keine globale Sichtbarkeit durch TXT-Upload. Rohzeilen, Gruppen, Reihenfolge und Dubletten erhalten, bis Modulregeln belegt sind. |
| Bilder, Audio, Berichte | Objektablage mit tenantbezogener Metadaten-/Zugriffsverwaltung | Unveränderliche Referenzen je Auftrag; keine beliebigen Dateipfade oder Browser-URLs als Zugriffserlaubnis. |
| Historie, Wiederherstellung und Audit | Zuständiger Laufzeitdienst mit Plattformvertrag | Ergebnisveröffentlichung, Teilfehler und Wiederanlauf nachvollziehbar; Aufbewahrung/Löschung und Backups ausdrücklich regeln. Unveränderliche Historie bedeutet keine unbegrenzte Speicherung personenbezogener Daten. |

Eigene Modultabellen und eine zentrale Datenbank widersprechen sich nicht: Die zentrale Betriebsinstanz kann getrennte Fachbereiche enthalten. Gemeinsam sind IDs, Rechte und Auftragsrahmen; fachliche Daten bleiben modulbezogen. Moduladapter übersetzen geprüfte Verträge und übernehmen keine neue Zahlenformel.

Für jeden Objekttyp ist genau ein führender Schreibpfad zu bestimmen: lokales Original, importierter Snapshot oder zentral geführter Datensatz. Eine automatische bidirektionale Synchronisation ist damit nicht freigegeben.

Die lokale Aurelia-Fassung benennt den externen DB-Pfad als `neon`, verwendet aber einen normalen `pg`-Treiber. Daraus folgt keine notwendige Neon-Bindung und kein Nachweis eines eigenen Linux-Servers. Ihr PGlite-Fallback ist im Speicher und überlebt keinen Prozessneustart. Vor produktiven Falldaten benötigt die Anwendung einen ausdrücklich festgelegten Produktionsmodus ohne stillen flüchtigen Fallback. Dokumentierte PostgreSQL-/MinIO-/Timescale-/ltree-/pgvector-Ziele sind keine nachgewiesenen laufenden Dienste. Neue Embeddings/semantische KI-Suche bleiben gemäß Betreiberdirektive gesperrt.

Mandantentrennung benötigt neben Schemas einen gemeinsamen API-/Worker-/Transaktionsvertrag, passende DB-Rollen, tenantgebundene Fremdschlüssel und Objektberechtigungen. Keine fehlende Policy als Freigabe; Besitzer/Superuser/BYPASSRLS-Rollen nicht als normaler Laufzeitnutzer verwenden. [PostgreSQL RLS](https://www.postgresql.org/docs/current/ddl-rowsecurity.html).

Auftragsvertrag noch zu definieren: Job gegenüber Ausführungsversuch, eigene parallele Zustände, Idempotenz/Wiederholung, Abbruch, Teilfehler, atomare Veröffentlichung und Wiederherstellung. Quellenhashes brauchen aufbewahrte versionierte Eingaben; ein Hash allein ermöglicht keine Reproduktion. Entropie-/Kernelangaben werden nur verlangt, soweit das jeweilige Modul solche Verfahren besitzt.

### Alternativen

| Modell | Nutzen | Grenze |
|---|---|---|
| Gemeinsamer PostgreSQL mit getrennten Fachbereichen | Empfohlenes Ziel bei gemeinsamer Betriebsverantwortung; gemeinsame IDs/Rechte und geringerer Betriebsaufwand | Gemeinsame Ausfall-/Migrationsgrenze; Isolation muss nachgewiesen werden. |
| Zentraler Core plus getrennte Modul-Datenbanken | Option bei stark unterschiedlichen Lebenszyklen oder zusätzlicher Isolation | Aufwendigere Konsistenz, Wiederherstellung und Querverweise. |
| Lokale Originale plus ausdrücklich importierte Snapshots | Empfohlener Übergang bis Adapter/Quellen feststehen | Eingeschränkte Aktualität; keine verdeckte Live-Synchronisation. |

## 5. Governors und Projektmatrix

Frisch lesend aus `runtime/journal.db`: Aurelia als `parent`, RadiWorks/Radi144/Morphic als `module`, Modul_Templates als `contracts`, alle in `aurelia-integration`. Nur diese fünf Projekte sind registriert; RadiFarben nicht. Aufnahmebelege stammen vom 15.09.2026. Ihre Hashes wurden dokumentiert, **heutige vollständige Scope-Freshness wurde nicht erneut über Governors ermittelt**. `memory_provisioning=provisioned_incomplete` ist ein gespeicherter Provisionierungsstatus und keine eigenständige aktuelle Gedächtnisabnahme.

Governors ist sinnvoll für aktuelle, quellgebundene Einzelaufnahmen, offene Abhängigkeiten, Drift, Gegenreviews und einen anschließenden Gruppenplan. Es ist weder Aurelias produktive Datenbank noch die Autorität für Abos, Mandantenzugriffe oder Moduljobs.

Die zusätzliche RadiFarben-Aufnahme sollte erst nach Quellen-/Umfangsklärung vorgeschlagen werden. Aufnahme, Gruppenzuordnung, Modellversand und Planannahme bleiben unterschiedliche Vorgänge. Keine der historischen Modellfreigaben wird hier automatisch auf neue Quellen übertragen. Automatische Reviews bleiben aus.

Routen auseinanderhalten:

- Chatvorgabe: GPT-6.1 Sol/high mit bounded GPT-6 Luna/max und GPT-6 Astra/medium. Dieses Dokument prüft keine tatsächliche Desktop-Modellauswahl.
- Governors optionale Route B im aktuellen Code: `gpt-6-sol` → `gpt-6-luna` → `gpt-6-astra`. Sie wurde nicht auf 6.1 umgestellt.
- Klassischer Governors-Pfad aus Konfiguration: Hermes/Terra mit getrennt gewähltem Supervisor; aktuell gespeicherter Supervisor `gpt-5.6-sol`. Nicht mit Chatroute oder optionaler Route B gleichsetzen.

Ein neuer Modulkatalog erfordert nicht automatisch eine Modellroutenänderung. Ein späterer 6.1-Wechsel der Anwendungsroute wäre ein separates, synthetisch zu prüfendes Routingpaket. Die Projektmatrix benötigt zuerst aktuelle Quellpfade, Umfang, Abhängigkeiten und Aufnahmebelege.

## 6. Fortsetzung in Phasen

| Phase | Inhalt | Stand / nächster Nachweis |
|---|---|---|
| DB-0 | Lokale Speicherformen, Quellen und Abweichungen erfassen | Gezielter statischer Erstabgleich erfolgt; kein vollständiges Modul-Reasoning behauptet. |
| SRC-1 | Copen/Bohm im Explorer, Thom im zweiten Repository; jeweils gebundener Commit, Export-/Quell- und begrenzte Rechen-/UI-Belege | Quellen und aktive Cloud-Struktur erfasst; Nutzungsrechte, tatsächliche Runtime-/Worker-Builds, vollständige Assets und effektive Rechte noch offen. |
| SRC-2 | Morphic-Quelle und aktuelle RadiFarben-Berechnung binden | Baumabweichung und Access-Schemadelta belegt; Quellenentscheidung, aktueller VBA-/Query-Abgleich und Referenzausgaben offen. |
| DB-1 | Gemeinsame Datenhoheit, IDs, Katalogrechte, Job-/Adaptervertrag | Dieser Bericht ist Gesprächsgrundlage; keine Schemafreigabe. |
| GOV-1 | Frische Einzelaufnahmen, RadiFarben-Aufnahmevorschlag, Gruppenreview | Erst nach geklärten Quellen/Umfang; kein automatischer Modellauftrag gestartet. |
| DB-2 | Synthetische Isolation, Parser-/Resultaterhalt, Parallelität und Restore testen | Nach ausdrücklicher Implementierungsfreigabe. |
| MOD-1 | Module einzeln an gemeinsame UX-/Hostverträge vorbereiten | Bestehende Funktionalität erhalten; Modul_Templates auf beschlossene Verträge abstimmen. |
| INT-1 | Stufenweise Aurelia-Integration | Eigene Host-/Ubuntu-/Produktgates einschließlich S4.8; weiterhin offen. |

Orientierung: Repo-Intakes brauchen nach Eingang der Links je nach Umfang zunächst ein weiteres abgegrenztes Lesepaket. Für Access-Charakterisierung und Gesamtintegration wird vor Klärung der Quellen/Umgebung keine belastbare Dauer angegeben. Qualitätsprüfung bleibt maßgeblich.

## 7. Unabhängige Prüfung und Nachvollzug

Tatsächliche Helfer: **GPT-6 Luna/max** für Radi144-/Morphic-Inventur und den Vergleich beider Morphic-Bäume; **GPT-6 Astra/medium** für unabhängige Beurteilung von Datenhoheit, Isolationsvertrag und Alternativen. Keine rekursive Delegation. Astra bestätigte die Plausibilität des Zielbilds, verlangte aber eindeutige Schreibhoheit, Identitätszuordnung, Transaktionsbindung und Job-/Versuchsregeln. Diese Korrekturen sind oben enthalten; keine Implementierungsfreigabe daraus abgeleitet.

Primärquellen zusätzlich: Aurelia `src/lib/db.ts`, `src/lib/auth/server.ts`, `src/lib/praxis/memberships.ts`, `migrations/0002_tenants.sql`, `docs/05-data.md`, `AGENTS.project.md`; Modul_Templates `MODULE_REGISTRY.md`, `standards/MODUL_STANDARD.md`, `standards/API_CONTRACT.md`; Brainpower `governor_workbench/registry.py`, `intake.py`, `route_b.py`, `config.local.json`, `docs/LLM_OPERATING_CONTRACT.json`. Konfigurations-/Keyinhalte wurden nicht exportiert; der Metadatenbeleg enthält ausschließlich ausgewählte Projekt-, Aufnahme- und Routeneinstellungen.

## 8. Konsolidierung nach aktivem Cloud-Abgleich

Dies ergänzt die lokale Matrix, nicht die unveränderte Governors-Registry oder normative Modul_Templates. [Gebundene Quellen/Exporte](AURELIA_COPEN_BOHM_THOM_BESTAND_2026-10-09.md) und [ausgeführte Referenzproben/Cloud-Metadaten](AURELIA_REFERENZPRUEFUNG_COPEN_BOHM_THOM_2026-10-09.md) bleiben die Detailbelege. Copen, Bohm und RadiMorphic sind verschiedene Module.

| Modul / Grenze | Für die zentrale Struktur jetzt belegter Bedarf | Noch kein Abnahmenachweis |
|---|---|---|
| Copen | Klient, separate v1/v2-Analyse-/Harmonisierung-/Vorlagenfamilien, Ratesignatur, Parameter-/Auftragsstand, Pause/Queue und Workerzustand | Aktive Eigentümer-/Patientbindung und atomare Claims; UI-Laden hält Pausen nicht durchgängig fest. Vier Tabellenfamilien bestehen aktiv parallel, keine stillschweigende Migration |
| Bohm | Klientenrechnung und Worttest als verbundene, getrennt versionierte Ergebnisse; Kontext-/Zeit-/Quellenstand, Archiv und Harmonisierung | Synthetischer UI-Pfad kann alte Ergebnisse mit neuer Klienten-ID archivieren; echte DB-Annahme/Abweisung dieses Payloads offen. Keine Gleichsetzung mit RadiMorphic |
| Thom | Klient/Vektor, Scan-/Sitzungsstand, Anatomie-/Organ-/Punkt-/Modellrevisionen, Harmonisierung, Medien und Echtzeit | 18 aktive Anwendungstabellen; Auftragschema ohne `session_id`. Grafische und Service-Befunde sind begrenzt, keine vollständige 3D-/Persistenz-/Worker-Abnahme |
| Klientenrechte beider Cloudprojekte | Ownership, Mitgliedschaften, Delegation und Objektverknüpfungen getrennt erfassen | RLS aktiv bei allen 18/13 Anwendungstabellen. Keine explizite `tenant_id`-Spalte gefunden; daraus folgt weder fehlende Trennung noch ein fertiger Aurelia-Mandantenvertrag |
| Vertrauliche Medien | Eigene Assetrevisionen, Rechte, Original/Ableitung, Objektbestand und DB-Referenzen gemeinsam führen | Thom `client-photos` aktiv öffentlich; Explorer `client-signatures` privat. Keine Objekte gelesen; kein Leak nachgewiesen. Datenschutzgerechte Zielkorrektur und effektive Storage-Rechte separat abnehmen |
| Privilegierte Dienste | Autorisierten Auftrag mit Nutzer-/Klienten-/Sitzungs-/Modulkontext übernehmen; aktuelle Rechte bei Start/Download prüfen | Quellcommit und Metadaten ersetzen keine Gateway-/Edge-/Worker-Version oder Nutzerprüfung. Simulation ersetzt keine reale Hardware-/Echtzeitabnahme |

Thom-Jobs-Policies dürfen nicht isoliert bewertet werden: Ihr NULL-Ownerzweig wirkt mit dem strengeren `clients`-RLS zusammen. Kein wirksamer Fremdzugriff aus dem NULL-Ausdruck allein ableiten. Ebenso belegen SECURITY-DEFINER/ PUBLIC EXECUTE allein keine ausnutzbare Lücke. Das [Prüfpaket](superpowers/plans/2026-10-09-aurelia-isolierte-rechtepruefung.md) trennt DB-Rollenprobe, echte Staging-Anmeldung und späteren Aurelia-Vertrag.

Aktualisierte Reihenfolge nach Betreiberklärung 10.10.2026: Workflow-/Algorithmusabdeckung schließen → Identitäten, Ergebnis-/Katalog-/Assetrevisionen und Datendomänen modulübergreifend konsolidieren → Quellen-/Lizenzfragen für den Strukturentscheid benennen → gemeinsame Datenstruktur mit Betreiber entscheiden → beschlossene Adapter-/Modul_Templates-Verträge umsetzen → echte Rechte-/Dienste-/Restore- und Produktintegration separat abnehmen. Bestehende Testklienten und laufende Jobs werden nicht übernommen; die frühere P2-Einrichtung ist zurückgestellt. Kein automatischer Modellauftrag, Produktfix, Cloud-DML/DDL, Quellenwechsel, Routenwechsel oder S4.8-Fortschritt aus dieser Konsolidierung.

## 9. Ergänzung aus der lokalen SQL-Charakterisierung

[363 P1-Aktionen](verification/AURELIA_P1_RECHTE_2026-10-09.md): 317 erfüllen den Sollvertrag, 46 Zielabweichungen. Normale eigene/fremde CRUD-Gegenfälle und Thom-NULL-Kombinationen sind im ausgewählten nachgebildeten Stand geprüft; reale Cloud-Anmeldung/API/Storage/Worker bleiben offen.

Für die gemeinsame Struktur zusätzlich erforderlich: konsistente Klientenbindungen auch bei abhängigen Vektor-/Protokoll-/Patientreferenzen; eigene user_id allein reicht dafür nicht. Thom nimmt widersprüchliche Jobreferenzen an, Explorer eigene Nutzerobjekte mit anderem patient_id in beiden Familien. Daraus ist kein fremder Inhaltslesezugriff nachgewiesen. Tabellenweite TRUNCATE-Grants umgehen RLS im simulierten direkten DB-Kontext; privilegierte und gewöhnliche Rechte strikt begrenzen. Kein API-Exploit oder Produktionsschaden behauptet.

Die Originalschemas/Algorithmen bleiben unverändert. Zentrale Constraints/Adapter, Delegation/Abo, Migration, normative Modul_Templates und Produktfreigaben werden erst nach eigener Entscheidung umgesetzt.

# MODULE_REGISTRY — Bestandsaufnahme aller Aurelia-Module

> **Aktueller RadiWorks-Stand 08.10.2026:** R6-Release, 200 manifestierte Produktdateien; kanonische Quelle synchronisiert. Frühere Nachträge unten sind historische Belege. [Aktueller Abgleich und Grenzen](../Brainpower/docs/verification/RADIWORKS_R6_SOURCE_TEMPLATE_SYNC_2026-10-08.md). Keine Aurelia-Integrationsfreigabe.

> Quelle: `Aurelia/src/routes/module.tsx:40-48` (Kernel-Kette „Sextett"), `Aurelia/src/routes/module.tsx:56-88` (Fachmodule),
> `Aurelia/src/lib/concept/kozyrev-labor.ts:21-60` (Kernel-IDs). Quellenstand der Karte: 2026-08-28; RadiWorks-Nachtrag: 2026-09-30.

## A. Kernel-Kette „Sextett" (die 6 RadiX-Module)

Aurelia-Regel (`module.tsx:19-22`): *„Migration: Morphic zuerst. Schreibziel der Cores ist die ABI, nicht /opt/radiquant4."*

| # | Modul | Rolle lt. Aurelia | Quellprojekt (lokal) | Reifegrad | Integrationsstatus |
|---|---|---|---|---|---|
| 1 | **RadiWorks** | Werkbank (Analyse/Broadcast/Session — AetherOnePi-Funktionalität) | `Documents\Radiworks` | Getrennter Kandidat `a242d247`: Python/FastAPI + HTML, Manifest `radiworks.engine` / `0.2.0`, lokaler Chrome-Smoke 19/19 und gezielte hörende Fallaktionsprobe; S0–S3 lokal nachgewiesen, S4 nicht zertifiziert | [Lokales Vertragsprofil v1.1, Entwurf](standards/RADIOWORKS_LOCAL_PROFILE_V1_1_DRAFT.md); Host-/Bridge-Abgleich und Registry offen |
| 2 | **Radi144** | bio_knowledge + Reportpfade (CopyGuard-Risiko) | `Documents\144er` / `12x12` (zu prüfen) | zu erfassen | offen |
| 3 | **RadiMorphic** | nächster read-only Intake (`/opt/Prototypen/Radimorphic @ 217dcf9`) | extern (`/opt/…`), lokal zu spiegeln | zu erfassen | **von Aurelia priorisiert** |
| 4 | **RadiBlohm** | Full-Kette | zu erfassen | zu erfassen | offen |
| 5 | **RadiThoms** | Full-Kette | zu erfassen | zu erfassen | offen |
| 6 | **RadiCopen** | Full-Kette | zu erfassen | zu erfassen | offen |
| — | ~~radiquant4~~ | Altbaum FastAPI+Astro (`/opt/radiquant4 @ cd9e9b4f`) | **TABU** (`AGENTS.project.md:40,62`: „Never") | — | darf nicht beschrieben werden |

Die zitierte Morphic-Priorität ist ein älterer Aurelia-Quellenbefund zur **Migration**. Die aktuelle Betreiberreihenfolge für die **lokale Prototypvorbereitung** lautet RadiWorks → Radi144 → `morphic_v1` → neues Modul mit eigenem Pfad. Erst nach diesen Einzelprüfungen wird der Produkt-Matrixplan beschlossen; danach beginnt die Aurelia-Integration unter ihren eigenen Gates. Aus dem RadiWorks-Kandidaten folgt keine automatische S4-/S5-Freigabe für irgendein Modul.

## B. Fachmodule-Karte (Produktmodule, Aurelia Phase 3+ — reine Planung, kein Code)

Witness Vault · Rate Library · Scan Engine · Field Scheduler · Session Graph · Practice Ops
(`Aurelia/src/routes/module.tsx:56-88`)

## C. Kozyrev-Kernel (einzige benannten Kernel-IDs in Aurelia)

| ID | Flag | Default |
|---|---|---|
| `kozyrev.padic.haar.v1` | `kernel.kozyrev.padic.haar.v1` | **an** (K1) |
| `kozyrev.reg.v1` | `kernel.kozyrev.reg.v1` | aus (K2) |
| `kozyrev.lab.*` | ABI-Slot | `executable: false` hart (K3) |

## D. Pflichtregeln aus der Aurelia-Verfassung (für ALLE Module)

1. **Kernel-ABI v1 als Integrationsvertrag** (`docs/06-kernel-abi.md:5-17`): `id, version, hash, input_schema, output_schema, class (cpu|cuda|quantum), repro (strict|seeded|stochastic), budget (vram_mb, cpu_ms_est, max_batch), entry (Python-Modul|WASM)` + CopyGuard auf jeden sichtbaren Text.
2. **Kein Medizinprodukt:** keine Diagnose-/Therapie-/Heilungsbehauptungen (`AGENTS.project.md:50`).
3. **Mandanten-Scoping:** jede Abfrage/buffer nach `(tenant_id, client_id, job_id)`, fail-closed (`AGENTS.project.md:59`).
4. **Live-Kanal = WebSocket** („Live: WebSocket is the analysis+harmonisation channel", `AGENTS.project.md:65`).
5. **UI:** Deutsch, WCAG 2.2 AA, Design-Tokens Pergament `#F3EFE6` / Tinte `#1C241E` / Sage `#2C4A3E`, kein Lila/Neon/Emoji (`docs/08-ui-a11y.md`).
6. **CPU-Flags:** platform AND tenant AND session, fail-closed, audited (`AGENTS.project.md:74-77`).

## RadiWorks-Nachtrag 01.10.2026

Die Zeile oben beschreibt den damaligen Commitstand. Der aktuelle getrennte Kandidat und `Documents\Radiworks\radiworks_port` wurden danach für 101 Kandidatendateien bytegleich abgeglichen; 19 neuere Dateien sind mit Ausgangs-Hashes unter `Brainpower/runtime/radiworks-source-sync-20261001/manifest.json` gesichert. Das ist ein Arbeitsstand ohne neuen Commit oder Hostfreigabe. Der lokale Stick-Pad-Folgeanalyseweg erzeugt aus gespeicherten Treffern eine getrennte Sitzung; mehrere unabhängige Aufträge im selben Fall sind weiterhin nicht implementiert. Aktuelle Grenzen stehen im RadiWorks-Profil v1.1 und in `Brainpower/docs/verification/RADIWORKS_PARALLEL_FALLAUFTRAEGE_2026-10-01.md`.

## RadiWorks-Nachtrag 02.10.2026: Datenbanksuche und Fallfokus

Nach regulärem Auslaufen der virtuellen Queue und Auto AUS wurden 14 hashgebundene Dateien aus `Brainpower/runtime/rw-focus-search-20261002/promotion-manifest.json` in `Documents/Radiworks/radiworks_port` und den lokalen 8103-Kandidaten übernommen. Ausgangsdateien und Vorschau-Daten liegen unter `Brainpower/checkpoints/radiworks-focus-search-20261002-before`. Die vollständige Engine-Suite, der synthetische Chrome-Smoke mit 21 Abschnitten und eine gezielte Fallwechselprobe bestanden; eine ausschließlich lesende Browserprobe auf 8103 bestätigte Datenbanksuche und Fokusfeld ohne Seitenfehler. Nach dem Neustart waren 3 gespeicherte Fälle, 51 Drafts, 123 Datenbanken, Auto AUS und eine leere Queue sichtbar. Der zuletzt aktive Fall wird nach einem Prozessneustart nicht automatisch ausgewählt; die Fallakte bleibt gespeichert.

Die Suche filtert Katalognamen lokal, der optionale Fallfokus ist eine ausdrückliche Suchhilfe und ein Draft-Snapshot, kein Einfluss auf Analysewerte. Lokale Fallantworten binden ihren opaken, pro Prozess wechselnden Verweis an dieselbe Antwort; dieser Verweis ist keine dauerhafte Host-Fall-ID und ersetzt keine Mandantenautorisierung. Das [RadiWorks-Profil](standards/RADIOWORKS_LOCAL_PROFILE_V1_1_DRAFT.md) und `Brainpower/docs/verification/RADIWORKS_FOKUS_DATENBANKSUCHE_2026-10-02.md` enthalten Details. Weder der gemeinsame API-Vertrag noch die S4-/Aurelia-Freigabe ändern sich dadurch.

## RadiWorks-Nachtrag 02.10.2026: UI-Wirkungshinweise und Area

Im lokalen RadiWorks-Quellstand sind Einstellungen mit erklärter tatsächlicher Wirkung gekennzeichnet; gespeicherte, noch wirkungslose Original-Schalter werden nicht als aktive Funktionen ausgegeben. Eine neue Farbansicht ergänzt den numerischen Area-Scan getrennt und verwendet ausschließlich Browser-Zufall, keine Hotbits. Quellbindung: `Brainpower/runtime/rw-settings-help-20261002/promotion-manifest.json`; Vorher-Bytes sind gesichert. Die Peggotty-Randfallkorrektur ist nur in einer isolierten Testkopie und noch nicht im laufenden 8103-Prozess. Die Modul-/Hostverträge, Mehrmandantenfähigkeit und S4-/Aurelia-Freigabe bleiben offen.

## RadiWorks-Nachtrag 02.10.2026: 8103 nach Wartung

Die historischen RadiWorks-Zeile und Nachträge bleiben zeitgebundene Belege. Der aktuelle lokale Quell-/8103-Stand enthält die geprüfte Peggotty-Duplikatgrenze (künstlicher HTTP-422-Nachweis), die korrigierte Desktop-Ergebnistabelle und das größere Broadcast-Dock. Ein externer Recovery-Schlüssel auf E: sowie eine isolierte künstliche Stochastic-Fallsitzung mit Journal-Wiederherstellung sind belegt; ein echter 8103-Falllauf im Stochastic-Modus ist noch offen. Bei einer lokalen Kamera-Probe blieben beide virtuellen Quellen statisch und der Server-Feed bei null. Die anschließend getestete Quellenwechsel-Korrektur verwirft ungesendete Kandidaten. Hotbits aus einer geeigneten bewegten Kamera mit serverbestätigtem Feed sind weiterhin nicht belegt.

Zwei künstliche Instanzen auf getrennten Ports/Homes belegen lokale Prozessisolation, nicht gleichzeitige autorisierte Jobs in einem Prozess und keinen Aurelia-Mandantenhost. Der gemeinsame API-Vertrag, Host-Rechte, WebSocket-Isolation, Matrix- und S4.8-Gates bleiben unverändert offen. Beleg: `Brainpower/docs/verification/RADIWORKS_8103_TRENDS_RECOVERY_PARALLEL_2026-10-02.md`.

## RadiWorks-Nachtrag 05.10.2026: C23-Kandidat und Portable5

Der lokale C23-Produktkandidat ist unter ../Brainpower/runtime/rw-c23-fixed-release-20261005 mit 131 manifestgebundenen Produktdateien dokumentiert. Produktmanifest-SHA-256: 9ba23c5dbfe856fc6887abf87fe13aba302ec362c1cdd432654d8fa30fe50694. Die Engine bleibt 0.2.0. Portable5 0.3.0-rc1 ist nur das Label des privaten Windows-Testpakets, keine neue Engine-Version und keine gemeinsame REST-ABI.

Original bleibt der Standard. Der ausdrücklich gewählte lokale Experimentalvergleich nutzt einen getrennten CPU-Prozess mit dem Profil 80.000 Kandidaten und höchstens 21 Raten je Ergebnisseite. Er erzeugt einen eigenen Auftrag und eine eigene Sitzung; er übernimmt keine GV-Werte und startet keinen Broadcast.

Vor dem getrennten Quellabgleich ergab der Hashvergleich zwischen diesem Pin und Documents/Radiworks/radiworks_port 77 bytegleiche, 15 abweichende und 39 fehlende Manifestdateien. Das ist ein datierter Vorherstand, kein Nachweis einer abgeschlossenen Synchronisierung oder eines Git-Commits. Der Kandidat und der kanonische Quellbaum bleiben getrennte Referenzen; alte Dateien und nicht zum Manifest gehörende Dateien sind bei einer Synchronisierung gesondert zu sichern und zu erhalten.

Das lokale Profil ändert API_CONTRACT.md oder REIFEGRADE.md nicht. Autoritative Plattformmandanten-/Auftragsrechte, CPU-Quotas und Persistenz-/Recovery-Vertrag bleiben offene Hostaufgaben; S4.8 und eine Aurelia-Integrationsfreigabe bleiben geschlossen. Die zweite-Windows-PC-Abnahme ist separat und noch nicht durch lokale Tests ersetzt.

Nachweise: C23-Template-Delta unter ../Brainpower/docs/verification/RADIWORKS_EXP1_C23_TEMPLATE_DELTA_2026-10-05.md; Portable5-Abschluss unter ../Brainpower/docs/verification/RADIWORKS_C23_PORTABLE5_ABSCHLUSS_2026-10-05.md; gepinntes Manifest unter ../Brainpower/runtime/rw-c23-fixed-release-20261005/PRODUCT_MANIFEST.json. Die Pfade sind relativ zum vorgesehenen Modul_Templates-Zielordner.


### Abschließender Quellabgleich 05.10.2026

131/131 kanonische Produktdateien SHA-gleich mit dem C23-Pin; 15 ersetzt/39 ergänzt/77 unverändert. Drei Nachträge nach Vorherkopie übernommen. Details und Grenzen: [Synchronisationsbericht](../Brainpower/docs/verification/RADIWORKS_SOURCE_TEMPLATE_SYNC_2026-10-05.md). Keine normative API-/S4.8-Freigabe.


## R6-Nachtrag 08.10.2026 – bestätigter lokaler Modulprototyp

Quellpin `Brainpower/runtime/rw-r6-release-20261008`, Produktmanifest SHA256 `445ece8f8c826e1391fead34c9a4c9b271e3b13b6d59a7654f66f11ab77b6275`, 200 Dateien; Kernel `radiworks.engine 0.2.0`, lokale REST-ABI weiterhin v1. Der kanonische Quellordner `Documents/Radiworks/radiworks_port` ist dateiweise SHA-gleich. Der Produktmanifesthash und die sieben verschiedenen lokalen Prozess-Scopes sind keine autoritative Aurelia-Identität.

- Zwei getrennte Achsen: Original AetherOne / Persönliche Heuristik sowie reproduzierbar / stochastisch. Original-EW/GV und persönliche Matrixscores bleiben getrennt; keine zusätzlichen Originalformeln. Persönliche vollständige Einzeldatenbankaufträge sind auf höchstens 4096 Raten begrenzt; Altvergleichsbelege bleiben lesbar, überholte Vergleichs-UI ist entfernt. Verfahren, Quelle, Katalog und Fallkontext werden pro Auftrag festgehalten; Umschalten ändert keine laufenden Aufträge.
- Getrennte persönliche Kontextfelder, aktiver Ortstyp, neutraler Fall-Identifier, Fokusvorschläge nach bestehender Wortheuristik und optionales Fokusbild. Keine semantische KI-Suche. Speicherung und Kontextübernahme ersetzen keine klinische Messung.
- Original-GV/21er-Runden, separate Beobachtungshistorie und ausdrücklich gestartete Watchlist; Auto AUS beendet nicht automatisch alle virtuellen Broadcasts. Broadcast-Queue und sichtbare Resonanzliste sind bewusst getrennt leerbar, erhaltene Historien bleiben erhalten.
- Fallbezogenes Medienprofil: bis zu fünf geordnete Animationsbilder; feste Einzeltöne, Solfeggiofolge, Rosa Rauschen, gleichmäßige/Phi-/Fibonacci-Pulsprofile. Phi/Fibonacci koppeln Pulsrate und Abschnittsdauer. Bestehende Broadcasts behalten ihren eingefrorenen Profilstand. Audio nur nach bewusster Browseraktivierung, keine serverseitige Schallausgabe oder unbelegte Gesundheitswirkung. Normative Host-/Mandantenrechte werden dadurch nicht erweitert.
- Sieben lokale Dauerinstanzen 8103–8109 mit getrennten Homes/Scopes und unveränderten Windows-Taskdefinitionen geprüft; externe Stochastic-Recovery weiter nur auf 8103 vorhanden. Start5 0.4.0-rc1 wird separat als Fünferpaket geprüft, keine fertige Paket- oder Zweit-PC-Abnahme aus diesem Nachtrag ableiten.

Offen bleiben autoritative Host-/Tenant-/Client-/Job-Zuordnung, Rechte/Widerruf/Quotas, Plattform-RLS, gemeinsame Datenbank-/Kataloggovernance und Importvertrag, Ubuntu-Abnahme und S4.8. Der gemeinsame API_CONTRACT und MODUL_STANDARD sind unverändert. Kamera- und weitere externe Prüfungen bleiben gesonderte Belege. Details: [R6-Quell-/Referenzabgleich](../Brainpower/docs/verification/RADIWORKS_R6_SOURCE_TEMPLATE_SYNC_2026-10-08.md).

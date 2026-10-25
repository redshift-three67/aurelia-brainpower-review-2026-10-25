# RadiFarben-Charakterisierung und Modulbindungen

Stand: 09.10.2026. Freigegebene Schritte 1 und 2: lesende Untersuchung der aktuellen RadiFarben-Quelle und der Klienten-/Sitzungs-/Auftragsbindungen in Radi144 und RadiMorphic. Ergänzung zu [Modulbestand](AURELIA_MODULDATEN_BESTAND_2026-10-09.md) und [Datendomänen](AURELIA_DATENDOMAENEN_ECHTZEIT_2026-10-09.md).

**Statische Untersuchung, keine Funktions-, Migrations- oder Integrationsfreigabe.** Produktquellen, Algorithmen, Nutzerdatensätze, Berechtigungen und Liveinstanzen wurden nicht verändert. Access, Formulare, Makros, QueryDefs und VBA wurden nicht ausgeführt. Nur Systemkatalog und Code-Speicher wurden zusätzlich zur Datei gelesen; keine Geschäftstabellen-Datensätze. Keine Governors-Aufnahme, Routingänderung oder Modellaufträge über Governors. Die drei weiteren GitHub-Quellen stehen noch aus.

## 1. Quellen und Nachweisgrenzen

| Quelle | Gebundener Stand | Aussagegrenze |
|---|---|---|
| RadiFarben, `C:/Users/Hubert111/Documents/Radifarben/RadiFarben.accdb` | 86.454.272 Bytes; SHA-256 `2b48ce8dec5e0126072e0bc24f07b754b8b64af0651b080d257dcb1b0c8f13bc`; vor/nach Auslese identisch, kein verbleibender `.laccdb` | Aktuelle Code-/Metadatenquelle; kein Laufzeitnachweis |
| Historische G1–G3-Berichte im RadiFarben-`project_memories` | Frühere ACCDB SHA `32567c30d18e553a495f582ed5c90ac8e56837165931df6555a54b4200ee71b9` | Historische Algorithmenbefunde nicht ungeprüft auf die heutige Datei übertragen |
| Radi144, `C:/Users/Hubert111/Documents/Radi144` | Ausgewählte aktuelle Quellpfade und Hashes im privaten Nachweis | Keine aktive Serverkonfiguration oder End-to-End-Abnahme |
| Morphic Root, `C:/morphic_v1` | Eigenständiger Quellenstand | Nicht mit dem Worktree zusammenführen |
| Registrierter Morphic-Worktree, `C:/morphic_v1/.worktrees/operator-workbench-phase1` | Eigenständiger Quellenstand, laut vorherigem Bestand Governors-registriert | Registrierung beweist weder laufenden Produktionspfad noch fachliche Quellautorität |

Private, vom Git ausgeschlossene Belege: `runtime/radifarben-characterization-20261009`, Zugriff auf Besitzer und SYSTEM beschränkt. Rohcode und Query-SQL bleiben dort; personenbezogene Quelltextliterale werden im Bericht nicht wiederholt.

Der statische Leser verwendet das unverändert entpackte **binary-refinery 0.11.2**; Archiv-SHA `39fe3d1abc4789903f8dd736040871863beb9a8a9d2000070931bf8339d888c4`. Kein globales Paket installiert, kein Setup ausgeführt, keine Produktabhängigkeit geändert. [Offizielle Paketquelle](https://pypi.org/project/binary-refinery/0.11.2/), [Access-Parser](https://binref.github.io/lib/access.html).

Der unveränderte Parser fällt beim aktuellen Dateikopf `03 01 00 00` auf Jet3 zurück und gewinnt keinen VBA-Speicher. Ein **lokaler, exakt auf diesen Dateikopf begrenzter Auslese-Harness** setzt das ACE2010-Seitenlayout mit 4.096 Bytes. Die anschließende unabhängige DAO-Leseprobe bestätigt für **693/693 Code-Speicherzeilen** ID, Name, Parent, Typ, Blobgröße und Blob-SHA. Das VBA-Verzeichnis deklariert 100 Module; 100 wurden direkt geparst, ohne verschluckten Projektfehler oder Unicode-Ersatzzeichen. Jede kanonische UTF-8-Datei hat einen eigenen Hash. Diese Prüfungen sichern die Rekonstruktion ab, beweisen aber keine Gleichheit von kompiliertem P-Code und Quelltext oder korrekte Laufzeitwirkung.

| Erfassung | Ergebnis | Offen |
|---|---|---|
| DAO-Schema | 49 lokale und fünf verknüpfte Tabellen, 499 lokale Felder | Links nicht geöffnet; Datensatzintegrität nicht geprüft |
| VBA | 100 Quellen, 67.966 Zeilen, 2.228 deklarierte Prozeduren | Statischer Index ist kein vollständiger Aufruf-/Erreichbarkeitsgraph |
| Objektabgleich | Alle 54 benannten Module, 44/45 Formulare, 2/3 Reports mit VBA-Quelle zugeordnet | Für `frmAufstellKeysAutoForm` und `rptAufstellKeys` keine Quelle im rekonstruierten VBA-Projekt; nicht als sicher codefrei einstufen |
| QueryDefs | SQL für 47/47 benannte Abfragen gelesen; 40 SELECT, zwei UNION, fünf UPDATE | Kein Query ausgeführt; Parameter für 30 ermittelbar, bei 17 `MSysQueries`-Leseberechtigung verweigert. Fehlende Parameter sind unbekannt, nicht leer |
| Gespeicherte Objektbindungen | Drei Script-/Makroobjekte als Metadaten vorhanden | Gespeicherte Event-, ControlSource-, RecordSource- und Makrobindungen nicht vollständig rekonstruiert |

## 2. RadiFarben: heutige Berechnungspfade

Die folgenden Zeilenangaben beziehen sich auf die privaten UTF-8-Quellen in `current-vba-acevariant`. Die aktuellen Klassen heißen **`clsRate` und `clsMatrix`**. Die historischen Namen `clsBruceCopenRate`/`clsBCJSRate` reichen nicht als aktuelle Implementierungsreferenz; eine semantische Gleichheit oder Regression wurde nicht behauptet.

| Pfad | Aktuell im Quelltext belegt | Für Erhalt und spätere Portierung erforderlich |
|---|---|---|
| Raten-/Matrixberechnung | `Form_frmRaten.vba:1102` erstellt `clsMatrix`, übergibt Ratenname/Text, Potenz, Zeilen/Spalten, Symmetrie, Bereich, Mitte, Phi-Modus, Spiegelung und Klientenverknüpfung; `clsMatrix.cls:3148` verzweigt in ohne/Kreuz/Diagonal/Punkt-Symmetrie | Alle Eingaben und Modi separat versionieren; Varianten nicht zu einem Standard zusammenziehen |
| Text→Rate | `clsMatrix.cls:2097` nutzt `clsRate.BerechneRate`; `clsRate.cls:178` berechnet Primärsumme, hängt `000` an, führt Phi-/Fibonacci-Berechnung und Potenzanpassung aus, addiert Dezimalstrings und kürzt abhängig von Ratenlänge | Zeichenbehandlung, Überläufe, Stringarithmetik, Kürzung und Fehlerzustand gehören zum Vergleich; keine stillen Rundungsverbesserungen |
| Phi-/Fibonacci-Varianten | `clsRate.cls:474` enthält Standard-, 34/21- und Potenzierungszweige mit unterschiedlichen Mantissen/Längen; `mdlMathe.bas:20-47` enthält Double- und längere Ziffernkonstanten, Präzisionskonstante 10 | Nicht durch eine universelle neue Phi-Formel ersetzen; Referenzwerte pro Modus gewinnen |
| Legacy-Bruce-Copen | `mdlRad_BruceCopen.bas:40` bleibt als eigener Long/Double-Pfad vorhanden | Gleichnamiges Ergebnis bedeutet keine identische Berechnung. Legacy LM/Q-Divisor 1 (`:318-322`) gegenüber Klasse Divisor 2 (`clsRate.cls:692-693`) getrennt behandeln |
| WuWei | `mdlRad_WuWei.bas:78-143` extrahiert Ziffern und formatiert optional mit Trennzeichen/12er-Gruppen. Import `:151` besitzt Prüf-/Bestätigungspfad und spätere DAO-Updates (`:666-691`) | Import ist eine Datenmutation, nicht Teil dieser Untersuchung; Originaltext, Format und Katalogrevision getrennt aufbewahren |
| Matrixdarstellung | `Form_frmMatrix.vba:26,116,145,443` besitzt 1.000-ms-Formulartimer, animierte Ein-/Ausblendung und optionales Mischen der Palettenzuordnung | UI-Animation nicht mit dauerhaften Beobachtungen oder Neuberechnung einer Klientenreaktion gleichsetzen |

`On Error Resume Next`, `AdminStop` und `Stop` kommen in Berechnungs- und Formularpfaden vor. Referenzprüfungen müssen deshalb Ergebnis **und** Fehler-/Abbruchzustand erfassen. Die Präzisionskonstante 10 ist ein Quellenbefund, kein mathematischer Korrektheitsnachweis.

### Klienten- und Datenbindungen

| Bereich | Belegter Bezug | Fehlende Garantie |
|---|---|---|
| Klientenverwaltung | `Form_frmKlienten.vba:23-29,62-70,89-92` setzt `tblKlienten` als Quelle, wählt nach lokalem ID-Feld und speichert über Access. Schema enthält Namen, Geburtstag/-zeit/-ort, Bild, BildRate, Thema und Änderungsfelder | Lokale ID ist keine Aurelia-Identität oder Tenantberechtigung |
| Matrix/Klient | `Form_frmRaten.vba:1180-1185` übergibt bei Verknüpfung Namen, Geburtsdatum und Geburtsort. `clsMatrix.cls:3315-3328` bildet die Anzeige; `:2219-2318` enthält Text-vor/nach-Klient, Addition und Multiplikation. `:3412-3523` nutzt namens-/ortsbezogene Primärsummen und Jahr+Monat+Tag | Nicht jeder Modus nutzt Klientenfelder. `BildRate` ist in dieser betrachteten Klassenroutine nur kommentiert (`:3348`); kein aktiver Bildberechnungsbezug belegt |
| Besendung | `Form_frmBesendung.vba:48-84` initialisiert Lauftext und startet Timer; der Quelltext enthält ein fest eingetragenes persönliches Ziel. `:126-145,173-272` aktualisiert Anzeige/Zufallswerte/Farben | Keine universelle Bindung an den ausgewählten Klienten. Erreichbarkeit des Formulars offen; Literal nicht in neue Vorlagen übernehmen. `tblBesendungen` ist als Schemaobjekt vorhanden, dessen vollständiger Schreibpfad nicht belegt |
| Paletten/Katalog | QueryDefs verweisen auf `tblRaten`, `tblRatenWuWei`, `tblFarbPaletten`, `tblFarbPaletten_colorhex`, `tblFarbWerte`; fünf UPDATE-Abfragen berechnen Palettenmerkmale. `mdlFarbPaletten_colorhex.bas:728-831` schreibt importierte Paletten | Abgeleitete Merkmale, importierte Originaldaten und persönliche Ausgaben getrennt versionieren. Colorhex-Netzimport nicht ausgeführt |
| Berichte | `Form_frmReporting.vba:35-69` öffnet ausgewählten Report oder Query, mit Sortier-/OpenArgs-Pfad | Kein hier nachgewiesenes versioniertes Ergebnis-/Berichtsarchiv, kein unveränderlicher Sitzungssnapshot |
| Vorlagen/Trigger | `tblAufstellVorlagen`, `Radon_Timer`, `Radon_Timer2`, `Radon_Timer3` als Metadaten vorhanden | Kein kompletter aktiver Schreib-/Start-/Archivpfad aus dieser Untersuchung; Access-Formulartimer sind davon verschieden |

Die drei vorhandenen Benutzerrelationen tragen `dbRelationDontEnforce`; ihre Existenz belegt keine erzwungene referenzielle Integrität. Alte Access-Rechte/CurrentUser-Mechanismen ersetzen keine künftige Aurelia-Mandanten-/Aboprüfung.

## 3. Radi144 und RadiMorphic: tatsächliche Objektketten

Die Untersuchung erfolgte durch Luna 6/max mit begrenztem Kontext, ohne Produktänderungen, Datensatzlesung, Tests oder Prozesszugriffe. Aktive Speicherwurzeln bleiben unbestätigt.

| Quelle | Klient → Sitzung → Bericht | Harmonisierung und Grenzen |
|---|---|---|
| Radi144 | `/analyze-matrix` löst/erzeugt Klienten und erstellt je Aufruf eine Sitzung. JSON-Sitzung verweist auf Klient und spätere Artefakte. PDF registriert ein Artefakt nur bei mitgesendetem `session_id` und `output_path`. API liefert Client-/Session-Header; der geprüfte `user_workflow.js`-Pfad konsumiert sie nicht und ruft den PDF-Endpunkt dort nicht auf | Sitzung speichert `harmonization_status=not_requested`. Kein durchgehender Sitzung→Harmonisierungsauftrag-Pfad belegt. Kein eigenes Fallobjekt im geprüften Modell. Nicht konsumierte Header allein beweisen keinen vollständigen Kontextverlust |
| Morphic Root | Scanroute erzeugt RAM-Job ohne Ownerübergabe und verwendet unscoped `get`. Reportkatalog leitet Klient/Sitzung aus Ordnerpfaden und Report-ID aus Pfad ab | Separater JSON-Harmonisierungsjob ohne Client-/Session-/Report-/Tenantbindung im betrachteten Modell |
| Morphic Worktree | Webroute bildet Owner aus Tenant/Operator und nutzt `get_owned`/`stop_owned`; JSON-Scanjob speichert Kommando, Owner, Artefaktpfade und gegebenenfalls Report-Session-IDs. Workbench-Trace nutzt Job-ID und personenbezogen abgeleitete Client-ID | Harmonisierung prüft Reportkatalog und speichert Schema 2 mit Report/Tenant/Operator, Lease und Idempotenz. Abgelaufene/unsichere Leases führen nicht zum automatischen Wiederstart. Separate RuntimeManifest-Registrierung ohne Context und generische unscoped Methoden bleiben bestehen |

Primärbelege:

- Radi144: `app/api/resonance.py:52-125,413-458,864-879`; `app/services/client_registry_service.py:21-55`; `session_archive_service.py:24-75`; `report_manifest_service.py:21-33`; `user_workflow.js:1042-1055,1370-1404,2070-2142`.
- Morphic Root: `apps/web/main.py:154-172,311-424`; `scan_jobs.py:197-270`; `reports.py:185-187,343-370,430-475`; `services/harmonization_worker.py:25-105,489-539`.
- Morphic Worktree: `apps/web/main.py:841-1037,1051-1250,1333-1408,1516-1535`; `scan_jobs.py:616-639,734-829,2241-2275,2474-2504,2707-2892`; `harmonization.py:148-345`; `reports.py:195-216,407-433,497-541`; `services/harmonization_worker.py:184-255,1796-1910,1942-2043`; `core/compliance/runtime_manifest.py:45-57,115-153,236-310`.

Weitere Integrationsgrenzen:

1. Radi144s 64-Bit-Präfix aus personenbezogenem stabilen Schlüssel und Morphics 80-Bit-Client-Präfix besitzen keinen Tenant-/Quellnamespace. Radi144s Session-/Artefakt-UUIDs sind auf 48 Bit gekürzt. **Kollisionsrisiko, kein nachgewiesener Zusammenstoß.** Personenähnlichkeit oder Hash darf keine automatische modulübergreifende Vereinigung bewirken.
2. Morphics Worktree-Report-ID bindet Wurzel/Pfad, nicht Inhalt oder Revision. Idempotenz bindet Request/Owner, friert die referenzierten Reportbytes jedoch nicht ein.
3. Scanjob, Modul-Session, Report-Session, Workbench-Trace und Fall sind verschiedene Objekte. Gleich verwendete IDs begründen keine universelle Gleichsetzung.
4. Radi144s Templates ersetzen gleichnamige Einträge im Browser ohne Revisionskette. Worktree-Entwurf überschreibt einen Eintrag; Template-IDs/Zeitstempel sind keine vollständige Änderungshistorie.
5. Morphic `OperatorContext` ist ausdrücklich lokaler Kontext, kein fertiges Auth-/Multitenantsystem. Der separate DPAPI-Identitätsspeicher prüft Owner/Workspace/Tenant, ist aber nicht automatisch der normale Scanpfad. Allgemeine Servicemethoden müssen vor einer universellen Schutzbehauptung auf tatsächliche Erreichbarkeit geprüft werden.

## 4. Folgerungen für die spätere zentrale Datenstruktur

**Empfohlene Entwurfsrichtung, noch kein Schemaentscheid:** typisierte Referenzen aus Tenant + Quellinstanz + Objekttyp + Original-ID. Klient/Fall/Sitzung/Job/Report/Artefakt/Vorlage getrennt halten; keine automatische Personenvereinigung. Für neue Aufträge Kontext, Katalog, Algorithmus, Vorlage und Reportinhalt mit eindeutiger Revision binden. Pro Objekt muss ein führender Schreibpfad festgelegt werden; ein einziger technischer Schreiber je ganzer Domäne ist lediglich eine mögliche Konsistenzstrategie.

Für RadiFarben zusätzlich vollständige Ratenstrings ohne ungewollten Float-/Integerverlust, Matrixgeometrie/Symmetrie, Palettenzuordnung, ausgewählten Klientenverknüpfungsmodus und Eingabestand erhalten. Frame-/Animationszustand nicht pauschal als Trend, Harmonisierung oder Archiv behandeln. Fremdmodulwerte nicht mit RadiWorks EW/GV gleichsetzen.

Bericht/Archiv, Trend/Archiv, klientenbezogene Zwischenablage, Vorlagen, Harmonisierung/Archiv und Trigger/Echtzeit bleiben getrennte Datenbereiche des bestehenden Bestandsberichts. Erst nach den zusätzlichen Modulquellen werden Lebenszyklen, Schreibhoheit, Rechte, Aufbewahrung/Löschung und Lastprofil gemeinsam entschieden. Neue Embeddings/semantische KI-Suche bleiben ausgeschlossen; Modul_Templates-Verträge wurden nicht verändert.

## 5. Phasenstand und nächste Gates

| Schritt | Stand | Nächster belastbarer Nachweis |
|---|---|---|
| 1a aktuelle RadiFarben-Quelle binden | Erledigt: ACCDB-, Code-, Query- und Auslesewerkzeug-Belege | Bei jeder späteren Quelle neue Hashbindung |
| 1b statische Charakterisierung | Kernpfade und Datenobjekte erfasst; vollständiges Modul-Reasoning noch offen | Gespeicherte Formular-/Makro-/Controlbindungen, 17 Parameterlisten und Referenzausgaben klären |
| 2 Radi144/Morphic-Bindungen | Statische Objektketten und konkrete Lücken erfasst | Morphic-Quellautorität und aktive Runtimewurzeln bestätigen; anschließend gezielte End-to-End-Bindungsprobe |
| Zusätzliche GitHub-Module | Quellen/Rechte angekündigt | Repository, Branch/Commit, Lizenz-/Nutzungsrahmen und Modulaufnahme binden |
| Zentrale Struktur | Vorbereitete Vergleichsbasis; kein finales Schema beschlossen | Alle Modulobjekte/Lebenszyklen abgleichen und mit Betreiber besprechen |

Die spätere synthetische RadiFarben-Referenzprobe sollte mindestens Zeichen-/Umlautbehandlung, leere/lange Texte, Potenzarten einschließlich LM/Q, Phi-Varianten, Dezimalüberlauf/Kürzung, alle Symmetrien und Klientenverknüpfungen, WuWei-Formate sowie Paletten-/Animationsreihenfolgen abdecken. Originalausgaben, Fehler und Abbrüche gemeinsam erfassen; keine Referenzwerte erfinden. Kontrollierte Access-Probe und Migration benötigen einen konkret festgelegten Umfang.

Tatsächlich eingesetzte Helfer: **Luna 6/max** für Schritt 2, **Astra 6/medium** für unabhängige Bewertung der wesentlichen Identitäts-/Quell-/Auslesegrenzen. Leitungsroute laut Betreiberwahl Sol 6.1/high; diese Untersuchung verifiziert keine Desktop-Modellauswahl und misst keine Tokenersparnis. R6/Start5/Dauerinstanzen und frühere F:-Archive unberührt; diese neuen Belege sind noch kein neuer F:-Sicherungspunkt.

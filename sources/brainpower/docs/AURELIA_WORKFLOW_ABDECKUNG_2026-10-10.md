# Aurelia – ergänzender Struktur- und Workflowabgleich

Stand: 10.10.2026. Quellengebundene Bestandsaufnahme für Copen, Bohm und Thom; keine Implementierung oder vollständige Laufzeitabnahme. Die früheren [Referenzproben](AURELIA_REFERENZPRUEFUNG_COPEN_BOHM_THOM_2026-10-09.md) und [P1-Rechtebefunde](verification/AURELIA_P1_RECHTE_2026-10-09.md) bleiben eigenständige Nachweise.

## 1. Betreiberklärung und Quellen

Der Betreiber benötigt die aktuelle Funktionalität, Algorithmen, Struktur und Workflows für die Aurelia-Modulvorbereitung. Bestehende Testklienten, laufende Analysen und Harmonisierungen werden dafür nicht inventarisiert, übernommen oder als Wiederherstellungsvoraussetzung behandelt. Strukturelle Klienten-/Sitzungs-/Auftragsbindungen bleiben erforderlich, auch ohne Migration bestehender Daten.

Das bereitgestellte Bild zeigt den Workspace-Default „Standard-Region für Datenhosting: Nicht festgelegt“. Es belegt weder Europa noch die effektive Region der bestehenden Projekte. Neue Cloud-Teilstagings aus P2 sind zurückgestellt; ihre Einrichtung ist keine Voraussetzung für diesen Source-Abgleich. Tatsächliche Rechte, Auth, Storage, Worker, Realtime, Deployment und erforderliche Regionsnachweise bleiben spätere Integrationsprüfungen.

| Quelle | Frisch bestätigter GitHub-Standardbranch | Lokaler Umfang |
|---|---|---|
| Explorer: Copen und Bohm | `radiquant/resonance-research-explorer`, `c69d5aa224018b0484efd90ae456a10aecc78a77` | 292 manifestierte Dateien |
| Thom | `radiquant/morpho-field-nexus`, `18e6c12c238985da698f9a46743d893b30d61ba7` | 270 manifestierte Dateien |

Lovable-Projektmetadaten und GitHub-Refs stimmen mit diesen Bindungen überein. Das ist keine Bestätigung aller ausgelieferten Edge-/Worker-/Frontendversionen. Ein erster Git-Abgleich scheiterte am geerbten Loopbackproxy; der erfolgreiche Wiederholungsaufruf deaktivierte den Git-Proxy ausschließlich für diesen lesenden Befehl. Globale Routing-/Proxykonfigurationen blieben unverändert.

## 2. Explorer: aktive Bedienpfade und Datenbereiche

Dateiangaben beziehen sich auf `runtime/aurelia-three-modules-20261009/explorer-source`. V1, Generator und V2 sind getrennte aktive Workflows, nicht automatisch drei neue Module.

| Einstieg / Verarbeitung | Speicherung oder Ausgabe | Zentraler Strukturbedarf / Aussagegrenze |
|---|---|---|
| Startseite wählt Copen v1; eigener `/copen-generator`; `/copen-visualisierung-v2` (App.tsx:26; Index.tsx:145) | V1 nutzt ältere Sitzungen; V2 nutzt neuere Sitzungen mit Worker-/Realtimepfaden | Workflowtyp, Algorithmus-/Parameterrevision, Analyseergebnis, Auftrag und Ausführungsversuch unterscheiden. Keine automatische Familienmigration |
| Generator berechnet Rate und CSV lokal (CopenGeneratorPage.tsx:75); ausgewählter Klient kommt aus PatientManagerCloud, also `patients` (:371; PatientManagerCloud.tsx:104) | Jobeintrag in `harmonization_sessions_v2` mit derselben patient_id und source_module=copen_v2 (:146–205) | Die Erzeugungsmigration 20251022084553 definiert patient_id ohne FK; generierte types.ts:256 enthält Relationships=[]; gezielte Migrationssuche fand keinen späteren entsprechenden FK. Source-Befund, kein frischer Cloud-Constraintnachweis. Quelltabellen-/ID-Zuordnung und Ownervertrag ausdrücklich festlegen, kein Fremdzugriff behauptet |
| Bohm `/morphic-field`: ClientFieldCalculator + eingebetteter WordEnergyTester (MorphicFieldPage.tsx:223; ClientFieldCalculator.tsx:1183) | Klienten in `patients_v2`, Signaturbilder in `client-signatures`; Berechnung zunächst React-State; separate Testerarchive und Harmonisierungssitzungen | Berechnung, Worttest, Archiv und Ausführung getrennte Objekte. Kein aktiver Clientinsert in `morphic_field_calculations` gefunden; eine andere Ergebnisquelle ist damit nicht ausgeschlossen |
| WordEnergyTester; Frequenz-/Anatomieübersichten; DatabaseManager in beiden Visualisierungen | `word_databases` speichert fachlich verschiedene Listen; FrequencyDatabaseOverview.tsx:106 / AnatomyDatabaseOverview.tsx:117 nutzen textliche Namenspräfixe | Katalogtyp, Einträge, Reihenfolge, Quelle, Revision, Lizenz und Nutzer-/globale Sichtbarkeit explizit führen. Gebündelte Clarke-Referenzdatei im Tester ist keine nachgewiesene Remedy-CRUD-Verwaltung |
| `/import`: FileReader, CSV/TXT-Batch und Copenrechnung (ImportPage.tsx:19; forms/BatchImportForm.tsx:29) | Lokaler Ergebniszustand und CSV-Download; OCR-Ausgabe füllt Textfeld | Kein zentraler Datenbankimport belegt. Prüfbarer Importauftrag mit Originalartefakt, Parserrevision, Zeilenfehlern und bewusster Übernahme für Aurelia vorsehen |
| PDF-/Bildauswahl mit OCR (forms/FileImportForm.tsx:86–225) | Bild-OCR-Fehler erzeugt Beispieltext; PDF-OCR verwendet weißes Canvas statt gerenderter PDF-Seiten | Genau dieser PDF-OCR-Zweig ist Platzhalter. Keine präzise OCR-/PDF-Extraktion behaupten; andere PDF-Textpfade dadurch nicht pauschal ausgeschlossen |
| DatabaseManager analysiert/archiviert; AnalysisArchiveCloud liest/löscht Archive | `analysis_archives` (DatabaseManager.tsx:278); browserseitiges PDF/CSV/TXT (:571); Archiv-CSV (AnalysisArchiveCloud.tsx:66) | Archivdatensatz und heruntergeladenes Reportartefakt getrennt. Herkunft, Datenrevision, Darstellungsversion, Exportrechte und Lösch-/Aufbewahrungsregeln fehlen als gemeinsamer Vertrag |
| HarmonizationManager wählt Tabellen je sourceModule; Recovery liest und steuert beide Sessionfamilien (HarmonizationManager.tsx:288; SessionRecoveryDashboard.tsx:61) | `morphic_field_sessions`, `harmonization_sessions_v2`, v2-Vorlagen; DatabaseManager erzeugt ebenfalls Jobs (:810) | Jobquelle umfasst mehr als Copen/Bohm. IDs, Kontextrevision, Statusereignisse, Workerclaim/Lease, Pause/Abbruch und Wiederanlauf erhalten. Nicht auf einen UI-Zähler reduzieren |
| Klientenmanager, Hardwareauswahl, Anmeldung | Zwei Klientenfamilien; Hardware teils `patients_v2`, teils localStorage; Signup initialisiert user-Rolle (AuthPage.tsx:80) | Browserpräferenz von Auftragskonfiguration trennen. Admin-/Tenant-/Aboverwaltung im aktiven UI nicht nachgewiesen; daraus folgt keine Aussage über alle Backendgrenzen |

`SessionStatusList` und `HarmonizationArchive` ohne Cloud-Suffix wurden im aktiven Import-/Rendergraph nicht als eingebundener Bedienweg gefunden; Helper/Altpfade nicht als verfügbare Oberfläche zählen. Browser-Audio im aktiven Explorer-src ist nicht nachgewiesen; kein Ausschluss anderer Deployments. Eine Suchabfrage traf zusätzlich `src/_backups`; diese Treffer wurden verworfen und tragen keine Schlussfolgerung.

## 3. Thom: Analyse, Grafik und Dienste

Dateiangaben beziehen sich auf `runtime/aurelia-three-modules-20261009/thom-source`.

| Einstieg / Verarbeitung | Speicherung oder Ausgabe | Zentraler Strukturbedarf / Aussagegrenze |
|---|---|---|
| `/analyse`: ClientVectorInterface berechnet, lädt und speichert Vektor (Analyse.tsx:81; ClientVectorInterface.tsx:314) | `clients`, `client_vectors`; Sitzungen und Chreode-Trajektorien über eigene Hooks | Anzeigen, Neuberechnen und Speichern können verschiedene Stände bilden. Kontext-, Formel-, Zufalls-/Quellenrevision und autoritativen Ergebnisstand binden; vorhandene Formeln erhalten |
| Gruppenverwaltung tatsächlich in Interface eingebunden (:642; GroupManagementPanel.tsx:140) | `client_groups`, Mitglieder; useClientGroups.ts:225 mittelt jeweils neueste verfügbare Mitgliedervektoren | Gruppe und Mitgliedschaft eigenständige Domänen; verwendete Vektorrevisionen, Skalen und tatsächlich berücksichtigte Mitgliederzahl festhalten. Kein neuer Batchanalysealgorithmus |
| Wort-Energie-Sammlungen eingebunden (:634; WordEnergyDBManager.tsx:67) | CRUD `word_energy_collections`; Katalogabfrage `word_energies`; Vorheuristik oder Hashfallback; Top5 werden als Text in Fokus eingefügt (:176–245; ClientVectorInterface.tsx:290) | Sammlung, Vorheuristikresultat und Fokusauswahl trennen. Ein Fokus-Textcallback allein belegt keinen zusätzlichen numerischen Eingang in jede Analyseformel |
| Anatomie-/Organ-/Meridianansicht, Scan und Remedy-Panel | Referenzkataloge/Modellregister; aktive Scans in UI; useResonanceResults bietet Tabellen-CRUD, gezielte Caller-Suche fand nur Definition | Punkt-/Organ-/Modellrevision, Koordinatensystem, Einheiten, Scanparameter und Rohresultat separat. Vollständige aktive Scanpersistenz weiterhin nicht belegt |
| ModelUpload in AnatomyResonanceViewer eingebunden (:2079) | Resumable Upload in `3d-models`, danach `anatomy_models`-Insert (anatomy/ModelUpload.tsx:140) | GLB/GLTF-Auswahl mit Größe/Endung geprüft, bis100MB. DRACO-Checkbox ist Metadatenflag, kein Kompressorbeleg. Abhängige glTF-Dateien, Originalhash/Revision, tatsächliche Lizenz, Referenzpunkte/Transformationen und Storage-Erfolg plus DB-Fehler brauchen Vertrag. Kein compensating delete im gelesenen Fehlerpfad |
| `/workflow` und `/import` | Anleitungen und herunterladbare Pilot-/Referenzdateien; `/export` bietet statische JSON/CSV-Dateien | Nicht mit ModelUpload oder einem Klienten-/DB-Import gleichsetzen. Administratives 2D/3D-Werkzeug bleibt Plattformvorbereitung, kein neues Modul |
| Meridianablauf mit Frequenzen, Impuls/Pause, Zyklen und Nachtests (hooks/useTreatmentSequence.ts:214) | Browser-Audio/Timer und lokale Zyklusstände; separate Archiv-/Jobpfade | Unter20Hz implementiert dieser Audioweg AM mit432Hz-Träger (:281). Das ist eine technische Ausgabe, kein Wirksamkeitsnachweis. Dauerhafte Serverausführung nicht aus Browserfunktion ableiten |
| Analyse wählt Frequenz; FrequencyOutputModule und Spooky2Panel | Analyse übergibt selectedFrequency an Spooky2; FrequencyOutputModule ist ohne Frequenzprop eingebunden (Analyse.tsx:230); eigener Zustand/Worklet/fallback (FrequencyOutputModule.tsx:165) | Kein automatisches Durchreichen aller Analysefrequenzen an dieses lokale Audiopanel belegt. Universal-Frequenzdienst, Profile und Hardwareausgabe später separat anbinden, keine stille Algorithmusänderung |
| Klientendashboard, TCM-Trends, Sitzungsberichte | `treatment_sessions`, Diagnose-/Vektorsnapshots; Reportgenerator liest bis20 abgeschlossene Sitzungen und erzeugt HTML/Browserdruck (SessionReportGenerator.tsx:119,242,251) | Persistentes Archiv, Trendberechnung und Exportdatei unterscheiden. HTML/Browserdruck ist kein geprüfter präziser PDF/OCR-Exporter |
| TreatmentArchive und HarmonizationJobService | Abgeschlossene Jobs enthalten Ergebnisdaten; gelesener improvementScore wird aus progress/100 gebildet (useTreatmentArchive.ts:99) | Fertigstellungsgrad nicht als Verbesserung/physische Klientenmessung übernehmen. Analyse-/Gruppen-/Trendwerte benötigen getrennte Typen/Einheiten und Quellen |
| Realtime-Widget, Edge-/Worker-/Hardwarepfade | Mount öffnet feste bisherige WS-Zielbindung; privilegierte Dienste und Simulationen separat | Tenant-/Objektberechtigung, Transportziel, Eventsequenz, Replay, Workeridentität und Egress bestimmen; Source und Jobrow beweisen keine vollständige Live-Hardware-/Workerfunktion |

## 4. Konsolidierung und nächste Reihenfolge

Dieser Abgleich erweitert die erfassten Hauptworkflows. Eine geschlossene vollständige Funktionsabnahme wird nicht behauptet. Für die nächste fachliche Bestandsrunde ist jeder aktive Einstieg bis zu Verarbeitung, Datenquelle, Speicherung/Export und Fehler-/Abbruch-/Wiederanlaufpfad zuzuordnen; ungenutzte Helper und mögliche externe Schreiber bleiben gesondert markiert.

| Schritt | Ergebnis dieser Runde | Weiterer Nachweis / Entscheidung |
|---|---|---|
| W1 Quellen/Scope | Beide GitHub-Stände frisch gebunden; keine bestehende Klienten-/Jobübernahme | Bei Quellenänderung Bindung erneuern; effektive Deployments separat |
| W2 Funktionsabdeckung | Zusätzliche Copen-Generator-, Katalog-, Import-, Gruppen-, Audio-, Report- und Modelluploadpfade erfasst | Geschlossene Caller-/Writer-/Fehlerpfadmatrix; Detailalgorithmen mit vorhandenen Referenzproben verbinden |
| W3 Gemeinsame Datenbereiche | Klient/Gruppe, Kontext, Katalogtyp/-revision, Resultat, Job/Versuch, Bericht/Artefakt, Asset und Dienst voneinander abgegrenzt | Mit RadiWorks/Radi144/RadiMorphic/RadiFarben und Aurelia-Admin/Abo/Trends/Triggern zusammenführen; offene Quell- und Lizenzfragen benennen |
| W4 Strukturentscheidung | Noch offen | Betreiberentscheidung über führende Speicherung, Objekt-/Revisionsverträge und Adapter; keine eigenmächtige zentrale Schemafestlegung |
| P2/P3 Integration | Neue Cloud-Teilstagings zurückgestellt; frühere P1-Befunde erhalten | Reale Auth/API-/Storage-/Worker-/Realtime-/Restoreprüfungen vor entsprechender Abnahme. Produktregion und Hostingvorgaben klären, ohne Europa zu unterstellen |

Tatsächlich eingesetzt: Luna6/max für Explorer-Abdeckung; Leitung für Thom und Konsolidierung; Astra6/medium für unabhängige Beurteilung von Scope und Aussagegrenzen. Astra verlangt eine geschlossene Abdeckungsmatrix und eindeutige Identitäts-, Ergebnis- und Dateilebenszyklen; das ist hier als nächste Arbeit ausgewiesen. Kein Rohdefinitions-/Export-/Schlüsselversand an Helfer, keine rekursive Delegation. Kein gemessener Tokenvorteil oder aus Defaults abgeleiteter Nachweis des Desktopmodells.

Vorher-/Abschlussbelege: `runtime/aurelia-three-modules-20261009/reference-plan/workflow-scope-20261010-065438Z`. Keine Cloud-Datensätze gelesen, Cloud-Ressourcen angelegt oder bestehenden Aufträge geändert. RadiWorks-Dauerinstanzen, Produktquellen/Algorithmen, normative Modul_Templates, Governors-Konfigurationen und Server blieben unverändert; keine S4.8-Freigabe.

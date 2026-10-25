# Aurelia: Bruce Copen, David Bohm und Thom – gebundener Bestand

Stand: 09.10.2026. Statische Charakterisierung der bereitgestellten Quellen und Datenexporte. Ergänzt den [bisherigen Modulbestand](AURELIA_MODULDATEN_BESTAND_2026-10-09.md), die [Datendomänen](AURELIA_DATENDOMAENEN_ECHTZEIT_2026-10-09.md) und die [RadiFarben-Untersuchung](RADIFARBEN_CHARAKTERISIERUNG_MODULBINDUNGEN_2026-10-09.md). Keine vollständige Laufzeitabnahme, Migration oder Integrationsfreigabe.

Fortsetzung desselben Tages: [Referenzprüfungen, Besitzerbezüge und Thom-3D-Abnahmeplan](AURELIA_REFERENZPRUEFUNG_COPEN_BOHM_THOM_2026-10-09.md). Dieser Nachtrag präzisiert die frühere Prüfung nach Feldnamen durch deklarierte Beziehungen, ergänzt ausgeführte lokale Rechenproben und die inzwischen vom Betreiber bestätigte Explorer-Anmeldung. Aussagen unten zur ursprünglichen Untersuchung bleiben auf diesen früheren Schritt begrenzt.

## 1. Quellen und abgegrenzte Module

| Modul | Gebundene Quelle | Tatsächlicher Einstieg | Abgrenzung |
|---|---|---|---|
| Bruce Copen | `radiquant/resonance-research-explorer`, Commit `c69d5aa224018b0484efd90ae456a10aecc78a77` | `/copen-visualisierung-v2` → `CopenVisualizationV2Page` → `CopenAlgorithmVisualizationV2` | Mehrere Berechnungspfade und Tabellenfamilien; nicht ohne Vergleich zusammenlegen. |
| David Bohm | Derselbe Explorer-Commit | `/morphic-field` → `MorphicFieldPage` → **ClientFieldCalculator** | Eigenes Modul; nicht mit dem vorhandenen lokalen RadiMorphic gleichsetzen. `MorphicFieldCalculator` ist nicht der aktive Einstieg dieses Routers. |
| Thom Field Engine | `radiquant/morpho-field-nexus`, Commit `18e6c12c238985da698f9a46743d893b30d61ba7` | `/analyse` → Vektor, 3D-Anatomie, Scan, Frequenzausgabe und Sitzungen | Spezialisierte grafische Bedienung und Algorithmen erhalten; RadiWorks liefert nur passende gemeinsame Gestaltung und Plattformkonventionen. |

Explorer: 292 verfolgte Dateien, 4.736.237 Bytes; GitHub-Commit vom 09.10.2026, 10:41:05 UTC, „Neuen Admin-Zugang erstellt“. Damit ist die vom Betreiber übermittelte Kennung `c69d5aa` bestätigt. Thom: 270 verfolgte Dateien, 4.435.930 Bytes; Commit 11:26:19 UTC, „Neuen Login hinzugefügt“.

Lovable-Projekte: Explorer `8432eebb-5390-4c07-83e7-bcddaaa60775`; Thom `7d414a8e-f393-427d-962d-848204bdd57c`. Die Thom-Git-Einstellungen zeigten `radiquant/morpho-field-nexus`, Branch `main`, „In sync with GitHub“. Zugleich zeigte der Editor unveröffentlichte Änderungen. Diese UI-Angaben beweisen weder Bytegleichheit des Editors noch Gleichheit mit der veröffentlichten Anwendung. `ThomEngineCore` wurde nicht als Quelle übernommen.

Die Quellen wurden ohne Installation oder Ausführung ihrer Anwendungen auf die genannten Commits festgelegt. Quelle, Datenexport und veröffentlichte Laufzeit bleiben drei getrennte Belege. Kein App-Login, kein Datenimport und keine externe Änderung in dieser Untersuchung.

## 2. Datenexporte

| Export | Integrität und Umfang | Wesentliche beobachtete Bestände | Grenzen |
|---|---|---|---|
| `Resonance_Explorer_Backup_2026-10-09.zip` | 22.381.074 Bytes; 13 JSON-Dateien; 194.720.783 entpackte Bytes; 14.594 Haupteinträge | 91 alte und 3.144 V2-Harmonisierungssitzungen; 11.007 Morphic-Sitzungen; 298 Wortenergiearchive; 3 alte und 15 V2-Klienten; 33 Wortdatenbanken; 1 V2-Vorlage | Export der ganzen Explorer-App. Analysearchive beider Familien und `morphic_field_calculations` leer. Keine separaten Copen-Dateinamen; `source_module` im V2-Sitzungsbestand. |
| `Feldengine_DB_2026-10-09_1135.zip` | 47.339 Bytes; 17 CSV-Tabellen; 142.901 entpackte Bytes; 619 Zeilen | 5 Klienten, 27 Vektoren, 8 Sitzungen, 5 Trajektorien, 1 Harmonisierung, 13 Modelle, 8 Organschemata, 268 Landmarken, 162 Scanpunkte, 100 Remedies | `client_group_members`, `harmonization_protocols`, `resonance_results` leer. Nur CSV; keine Fotos, GLB/GLTF oder Storage-Dateien. |

SHA-256 Explorer: `4a3e11d34096438b321e47bfd80547a6e1b34e6f1ae26f4f62563f22ee358abf`.

SHA-256 Thom: `cefd08bd9f207fef85ea342a31024193ebe788cb8eb39981c675f87c6c664b64`.

Alle ZIP-Mitglieder wurden bis EOF gelesen, CRC-geprüft und gehasht; Quellhashes vor/nachher gleich. Kein Entpacken, Ausführen oder Import von Exportinhalten. Keine Datensatzwerte, Personen-IDs oder privaten Pfad-/URL-Werte in diesem Bericht.

Keine doppelten Kandidaten-IDs gefunden. Die verfeinerte Namensprüfung fand 28 ID-artige Felder, 13 benannte Zielkandidaten und 296 eindeutige Referenzen ohne Treffer in diesen Kandidatenmengen: Explorer V2-`patient_id` 1/16; Thom `client_vectors.session_id` 27/27; `organ_landmarks.point_id` 268/268. **Das sind keine bewiesenen Fremdschlüsselverletzungen**: Text-Sessionkennungen und fachliche Punktkennungen können bewusst andere Namensräume besitzen. `user_id` wurde nicht fälschlich mit `user_roles.id` gleichgesetzt. Exportvollständigkeit, aktive Constraints, Indizes, RLS und Grants sind aus JSON/CSV nicht belegbar.

## 3. Lebenszyklen und Befunde aus dem Explorer

Belege beziehen sich auf die gepinnte Explorer-Quelle unter `runtime/aurelia-three-modules-20261009/explorer-source`. Befunde sind statisch; Fehlerszenarien wurden nicht live ausgelöst.

| Bereich | Beobachtung / Quellbeleg | Konsequenz für die Aurelia-Vorbereitung |
|---|---|---|
| Klient → Ergebnis | `ClientFieldCalculator.tsx:213` ändert Klientenfelder, ohne ein vorhandenes Resultat zurückzusetzen. `WordEnergyTester` erhält Resultat und aktuelle Klienten-ID; Archiv-/Sitzungswrites bei `WordEnergyTester.tsx:808` und `:934` verwenden diese aktuelle ID. | Risiko einer Zuordnung alter Resultate zu einem neu gewählten Klienten. Unveränderlicher Auftragskontext und kontrollierter Wechsel erforderlich. |
| Copen-Berechnung | Inline-Pfad `CopenAlgorithmVisualizationV2.tsx:260` sowie `DatabaseManager.tsx:396`/`:421` über andere Funktionen. | Jede Variante getrennt charakterisieren und mit Referenzfällen sichern; keine stille Algorithmusvereinheitlichung. |
| Worker / Wiederanlauf | `harmonization-worker/index.ts:53`/`:104` behandelt Morphic-Ablaufende; Start-/Tick-/Queue-Pfade `:110`, `:162`, `:282` betreffen V2-Harmonisierung. | Ein serverseitig fortsetzbarer Jobpfad für beide Module ist nicht belegt. Browsersteuerung von serverunabhängiger Ausführung unterscheiden. |
| Queue / Parallelität | Nächster Auftrag wird bei `worker:282` nach User und Klient gesucht, ohne Batch-/Modulfilter; Statusupdates sind keine atomare Claim-/Lease-Übernahme. | Auftrag, Modul, Batch, Revision und Worker-Besitz getrennt binden; Rennen bei parallelen Läufen gezielt testen. |
| Pause / Puls | `HarmonizationManager.tsx:637`/`:655` ändert Status; Zeitberechnung `worker:232`–`:257` kann Pausenzeit mitzählen, Pulsphase `:240`–`:250` ist nicht dauerhaft verankert. | Verbleibende aktive Dauer, Pausen und Pulsphase als eigene fachliche Zustände prüfen. |
| Archiv / Vorlagen | Copen-V2-Ansicht verwendet auch `HarmonizationTemplates`; dessen Queries greifen auf alte Tabellenfamilie zu (`:57`, `:82`, `:93`). V2-Manager nutzt V2-Vorlagen (`:326`). | Keine Tabellenfamilie löschen oder blind vereinigen. Migration erst nach Zuordnung aller tatsächlichen Schreib-/Lesepfade. |
| Nutzer / Tenant / Abo | Router-Loginprüfung `ProtectedRoute.tsx:16`; deklarierte Policies sind User-/Admin-bezogen. Die untersuchten Sitzungsschemata enthalten keine FK-Ownerprüfung über `patient_id`. | User-Schutz ist noch kein Aurelia-Tenant-/Modulabo-Vertrag. Aktive DB-Policies und serverseitige Autorisierung separat abnehmen. |
| Privilegierter Worker | Worker nutzt Service-Client (`:31`); Handler selbst zeigt keinen vollständigen Tenant-/Abo-Gate. Gateway-Konfiguration unbekannt. | Keine öffentliche Ausnutzbarkeit behauptet; tatsächliche Aufrufrechte und Gateway vor Übernahme prüfen. |
| Reproduzierbarkeit | `resonanceAnalysis.ts:65`/`:82`/`:133`/`:171` verwendet `Math.random`; persönliche Pfade enthalten Zeit-/Hardwarewerte. | Ergebnis laden, identisch neu berechnen und Job fortsetzen sind unterschiedliche Anforderungen; Quelle, Zeit, Zufallsfolge und Algorithmusrevision festhalten. |
| Weitere Datenbereiche | Browser-CSV/PDF, lokale Wortenergiehistorien und mehrere Katalogquellen vorhanden. `morphic_field_calculations` besitzt Schema, aber keinen belegten aktiven Vollspeicherpfad. | Berichtsdatei, Berichtarchiv, Zwischenablage, Katalogrevision und Rechenauftrag getrennt aufnehmen. |

Migrationen erklären im Explorer private Klientenbilder und Signed-URL-Nutzung. Das bestätigt nicht die aktive Storage-Konfiguration. Für den Bohm-Einstieg wurden `clientFieldAlgorithms`, `morphicFieldEngine`, Hardware- und Wortenergiepfade erfasst, nicht als wissenschaftlich bestätigte Messverfahren bewertet.

## 4. Thom: grafische Funktionalität ist Teil des Modulvertrags

Belege: gepinnte Thom-Quelle unter `runtime/aurelia-three-modules-20261009/thom-source`.

| Grafischer Bereich | Vorhandene Quellen / Daten | Zusätzlich zu prüfen bzw. zu erhalten |
|---|---|---|
| 3D-Modelle / Kamera | `AnatomyResonanceViewer.tsx:7`/`:8`, Canvas, OrbitControls und Modellpfad `:1070`; ein gebündeltes `public/models/human-body.glb` | Tatsächliches Rendern, WebGL-Fallback, Modellgrößen und Ladefehler; Rotation/Zoom/Layer erhalten. |
| Modellkatalog | `useAnatomyModels.ts:87`–`:155`: lokale Pfade und Cloud-Bucket `3d-models`, Auswahl, sichtbare Layer | 13/13 Exportmodelle mit Pfad, Speichertyp, Lizenztext und Version; 0/13 Lizenz-URLs. Existenz und Rechte der referenzierten Dateien bleiben offen. Ein Lizenzfeld ist kein Rechtebeleg. |
| Organe / Landmarken | 8 Organschemata, 268 Landmarken, 162 Scanpunkte; Koordinaten und Oberflächennormalen | Modellrevision, Koordinatensystem, Skalierung, Zuordnung Organ↔Punkt↔Mesh, Quelle und Lizenz zusammen versionieren. |
| Scan / Hervorhebung | `useNLSAutoScan.ts:63`–`:149`: punktweiser Browserlauf, Geschwindigkeiten, Highlight, Pause/Stop | Punktreihenfolge, Fokus, Scores und Scan-Konfiguration an denselben Auftrag binden; Hintergrundtab, Wechsel, Pause und Abbruch prüfen. |
| Farben / Werte | `AnatomyResonanceViewer.tsx:1396`–`:1478`: Scores aus Vektordimensionen, Frequenz-/Indexvariation, Organfokus und Stabilität, Begrenzung 0–6 | Bestehende Formeln erhalten. Werte sind berechnete Softwarewerte; die Ansicht allein belegt keine externe NLS-Messung. Farbe zusätzlich mit Text/Skala erklären. |
| Spezielle Oberfläche | `Analyse.tsx:225`–`:250`: Vektorinterface, 3D-Trajektorie, Anatomie, Meridianablauf, Frequenzen, Trends und Berichte | Gemeinsame Aurelia-Schriften, Kontraste und Navigation ergänzen, fachliche 3D-Führung erhalten. Tastatur-/Listenalternative, reduzierte Bewegung und verständliche Zustände als Abnahmepunkte. |
| Medien / Wiederherstellung | Modell-/Fotoreferenzen über Storage; GLB-Dateien fehlen im DB-Export | Metadatensicherung genügt nicht. Assetinventar mit Hash, Revision, Lizenz und Wiederherstellungsprobe ergänzen. |

Die erforderliche Kette lautet: **Modellrevision → ausgewählte Region/Punkt → Scan-Konfiguration → unveränderlicher Vektor-/Klientenkontext → Sitzung/Auftrag → Resultate → Trend/Bericht/Harmonisierung**. Modellwahl und grafische Aktion dürfen nicht von ihrer Datenherkunft getrennt gespeichert werden. Die NLS-Ähnlichkeit ist eine Anforderung des Betreibers an die Prüfung, keine bestätigte Geräte- oder Diagnoseeigenschaft.

## 5. Thom: Bindungen und offene Belege

| Bereich | Statischer Befund | Erforderliche Abnahme |
|---|---|---|
| Persönliche Berechnung | `ThomVectorEngine.ts:113`/`:253` nutzt Name, Datum und Geburtsort; `:304` kombiniert Signatur mit Zustandsdimensionen und Entropiemodulation. Fotoanalyse `:475` ist Platzhalter und wird hier nicht als wirksame Bildberechnung belegt. | Vollständige Eingaben, aktive Quelle und Algorithmusrevision festhalten; gleiche vs. unterschiedliche Kontexte mit Referenzfällen vergleichen. |
| Anzeigen / Speichern | Interface berechnet bei `ClientVectorInterface.tsx:326`; Speichern über `useClientDatabase.ts:173` berechnet erneut und bildet eine neue Text-Sessionkennung. Laufende Dimensionsupdates sind möglich (`ClientVectorInterface.tsx:181`). | Angezeigter und gespeicherter Kontext können auseinanderlaufen. Einen autoritativen unveränderlichen Berechnungsstand verwenden; bestehende Formel nicht ersetzen. |
| Klientenwechsel / Sitzung | `Analyse.tsx:81` lädt bei Auswahl Sitzungen; setzt aktive Sitzung/Resultat nicht zurück. `:97` schreibt bei vorhandener aktiver Sitzung mit neu ausgewählter Klienten-ID. `loadSessions` setzt nur die Liste (`useSessionManagement.ts:44`). | Statisches Risiko einer gekreuzten Klient-/Sitzungsbindung. Kontrollierter Wechseltest und atomare Bindung vor parallelem Betrieb. |
| Sitzungsnummer | `useSessionManagement.ts:74` zählt bestehende Sitzungen und verwendet `count + 1`. | Parallelität und eindeutige Nummern prüfen; eine Displaynummer ist keine stabile Job-ID. |
| Scanarchiv | `useResonanceResults` bietet Speicherung; gezielte Suche fand nur seine Definition, keinen Aufrufer. `resonance_results.csv` ist leer. | Vollständige Scanresultatpersistenz im aktiven Ablauf nicht belegt. Leere Tabelle allein beweist keine defekte Funktion. |
| Harmonisierung | `HarmonizationJobService.ts:30` nimmt optionale Session-ID entgegen; Insert `:64` enthält sie nicht. Start-/Pollingpfad vorhanden; `simulateHarmonization:228` ist ausdrücklich Demo. | Jobrow und Statuspolling beweisen keinen dauerhaften Worker. Reale Ausführung, Sessionbindung, Pause/Abbruch/Wiederanlauf separat testen. |
| Trendsemantik | `useTreatmentArchive.ts:44` speichert Ergebnisdaten ohne `improvementScore`; Lesen `:99` setzt diesen Wert auf `progress / 100`. | Fertigstellungsgrad nicht als Veränderungs-/Verbesserungswert übernehmen; fachliche Bedeutung vor zentraler Trendübernahme klären. |
| Rechte / Storage | Migration 20260304172431 bindet Klienten und Child-Tabellen an User. Migration **20260626065408** ersetzt frühere allgemeine Modell-/Referenzschreibrechte durch Admin-Policies. Foto-Bucket wird in 20251230231005 öffentlich deklariert, Frontend nutzt Public-URL. | Spätere Admin-Einschränkung berücksichtigt; keine pauschale Aussage über alte Policies. Tatsächliche Deployment-/Foto-/Tenant-/Abo-Rechte und Objektbesitz kontrollieren. |
| Route / Server | `/analyse` geschützt, `/workflow` und `/import` in `App.tsx` ohne denselben Wrapper. | Fehlender UI-Wrapper beweist keine unautorisierte DB-Änderung. Interne Schutzmechanismen und aktive RLS/Gateway separat prüfen. |

## 6. Konsequenzen für die zentrale Aurelia-Struktur – noch kein Schemaentscheid

| Gemeinsamer zentraler Bereich | Modulspezifische, versionierte Ergänzung |
|---|---|
| Tenant, Nutzer, Modulabo, Rechte und Audit | Server-Gates je Moduloperation; keine Übernahme von User-ID als vollständige Mandantengrenze |
| Klient/Fall und Kontextrevision | Bestehende Modul-IDs mit expliziter Zuordnung; keine automatische Zusammenführung von Personen |
| Auftrag/Sitzung und Workerzustand | Copen-/Bohm-Rate und Quelle; Thom-Vektor/Scan/Modellrevision; Originalalgorithmen unverändert |
| Katalog und Katalogrevision | Wortlisten, Remedies, Anatomie-/Organschemata; gemeinsame Referenzdaten von Nutzerlisten trennen |
| Medien-/Assetregister | Fotos privat; 3D-Dateien und deren Rechte/Koordinaten getrennt; Hash- und Restorebelege |
| Rohresultat, Ereignis und Trend | Originalwerte, persönliche Scores und Scan-Scores getrennt; fachliche Ereignisse nicht mit UI-Ticks gleichsetzen |
| Berichte und Archive | Exportartefakt plus Kontext-/Quelldatenrevision; Aufbewahrung und Löschung konsistent |
| Vorlagen und klientenbezogene Zwischenablagen | Vorlage mit eigener Revision; Browser-Clipboard ist noch kein zentraler Speicher |
| Harmonisierung, Trigger und Echtzeit | Unveränderliches Ziel, Idempotenz, Reihenfolge, Lease, Pausezeit, Replay/Lücken und Abschlussbeleg |

Zentrale Datenhoheit bedeutet einen führenden Schreibpfad und eine klare Autorisierung je Objekt. Module behalten ihre fachlichen Verträge und Algorithmen. Eine konkrete Datenbank-/Zeitreihen-/Objektspeicher-Auswahl folgt erst nach dem modulübergreifenden Lebenszyklusvergleich und Betreiberbesprechung. Governors kann diese Belege und offene Entscheidungen verwalten; eine Modellroute ersetzt keine Quell-, Rechte- oder Laufzeitprüfung. Keine Governors-Projektaufnahme, Routeänderung oder Modellübermittlung von Exportdaten erfolgt hier.

## 7. Phasen und nächste Schritte

| Phase | Stand | Nächster konkreter Schritt |
|---|---|---|
| Q1 Quellenbindung | Drei Module in zwei Quellen, Commits festgelegt; Exporte technisch geprüft | Aktive Deploymentstände und Storage-Bestand getrennt bestätigen |
| Q2 Charakterisierung | Zentrale Ein-/Ausgabe-, Rechte-, Archiv- und 3D-Pfade statisch erfasst; wesentliche Widersprüche dokumentiert | Ausstehende Randpfade gezielt prüfen, keine vollständige Runtimeabnahme behaupten |
| Q3 Referenzprüfung | Offen | Synthetische Klienten-/Sitzungswechsel, Berechnung, Archiv, Queue, Pause, Abbruch, Wiederanlauf und 3D-Bedienung kontrolliert vergleichen |
| Q4 Modulmatrix / Datenhoheit | Gemeinsame Anforderungen ergänzt; Entscheidung offen | RadiWorks/Radi144/RadiMorphic/RadiFarben/Copen/Bohm/Thom Lebenszyklen zusammenführen und Struktur mit Betreiber besprechen |
| Q5 Adapter / Integration | Nicht begonnen | Erst nach freigegebenem Struktur- und Modulvertrag; Algorithmuserhalt und Modul_Templates-Abgleich |

## 8. Belege und Schutz

Private, Git-ignorierte Untersuchung: `runtime/aurelia-three-modules-20261009`, Owner/SYSTEM-ACL. Quellmanifeste enthalten Pfad, Bytes und SHA je verfolgter Datei. Archivskript und bereinigte Metadaten: `archive_inventory/analyze_archives.py`, `archive_metadata.json`, `findings.md`, `verification_receipt.json`. `source-verification.json` dokumentiert erneute Quellhash-/Git-/Artefaktprüfungen sowie die strukturelle GLB-Prüfung; kein Rendernachweis.

Tatsächliche Helfer: **GPT-6 Luna/max** für begrenzte Archive-/Schema-Metadaten, **GPT-6 Astra/medium** für unabhängige consequential Explorer-Bindungsprüfung. Thom-Charakterisierung und Konsolidierung durch die Leitung. Keine gemessene Tokenersparnis; gespeicherte Routingvorgaben sind kein Nachweis des aktiven Desktop-Modells.

RadiWorks R6/Start5, Dauerinstanzen, Algorithmen, Module_Templates, Governors-Konfiguration und Serverdaten wurden nicht verändert. Die neuen Belege sind nicht automatisch Bestandteil des früheren F:-Sicherungspunkts.


## 9. Maßgebliche Fortsetzung nach Betreiberklärung, 10.10.2026

[Workflow-Abdeckung vom 10.10.2026](AURELIA_WORKFLOW_ABDECKUNG_2026-10-10.md) ergänzt aktive Bedien-/Speicherpfade einschließlich separatem Copen-Generator, typisierten Katalogbedarfen, OCR-Grenzen, Thom-Gruppen, Wortkollektionen, Audio, HTML-Berichten und Modellupload. Die ursprüngliche Q3-Zeile oben beschreibt den Erststand; ausgeführte begrenzte Referenzproben stehen im Referenzprüfbericht. Vollständige Runtimeabnahme bleibt offen.

Bestehende Testklienten/Analysen/Harmonisierungen werden nicht übernommen. Neue P2-Cloudprojekte sind für die Source-Erfassung zurückgestellt; effektive Hostingregion ist aus „Nicht festgelegt“ nicht bestimmbar. Strukturbedarf und spätere Rechte-/Worker-/Storagegates bleiben erhalten. Nächstes ist die geschlossene Workflow-/Writer-/Fehlerpfadmatrix und der modulübergreifende Datendomänenabgleich, danach Betreiberentscheidung über die zentrale Struktur.

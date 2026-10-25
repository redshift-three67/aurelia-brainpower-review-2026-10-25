# P3 – Import-Schutz und RMF-Abfragezuordnung, 11.10.2026

Dieser gruppierte Referenzblock ergänzt die bisherigen P3-Belege. Er ist keine vollständige Modulabnahme oder Freigabe der zentralen Datenbankstruktur.

| Teil | Tatsächlich geprüft | Ergebnis | Noch offen |
|---|---|---|---|
| RadiMorphic Import-Schutz | Echter `CatalogStore` mit ausschließlich synthetischem, hashgültigem Importbeleg; normaler `AdminCatalogService.publish_draft()`-Aufruf | Spezifische Ablehnung; keine Revision veröffentlicht | Tatsächliche Registry-Revalidierung und autorisierter Import-/Publikationsweg |
| RadiMorphic Pfade | Expliziter unabhängiger Root; sechs reservierte Archivnamen jeweils mit Groß-/Kleinschreibung und Suffix (24 Unterfälle); gesperrter Root gleich/übergeordnet/untergeordnet; relativer und Traversal-Pfad | Vier Testgruppen bestanden, unabhängiger Root ohne Anlage akzeptiert, Negativfälle zurückgewiesen | Standardroot mit realer Umgebung, Reparse/Links, Race, Restore, HTTP/API/Auth/Schlüssel |
| RadiFarben RMF-Zuordnung | Fünf zuvor erfasste Query-Lv-Änderungen gegen historische Abfragemetadaten und genau 100 aktuelle manifestgebundene VBA-Texte | Drei historische Definitionstreffer; sechs Literalkandidaten bei einem Objekt; zwei weitere Namen mit `~sq_`-Präfix | Bedeutung der binären Lv-Felder, aktuelle DAO-/SQL-/Parameter-/Event-/Control-/Makro-/Laufzeitparität |

## Morphic: Quellen und Ausführung

Quellstand `C:/morphic_v1/.worktrees/operator-workbench-phase1`, HEAD `151e2bb0a69d49677a0b1e40e0bffd0f172d34c4`. **Sieben** ausgeführte Dateien gegen frühere Quellenbindungen sowie vor/nach Lauf gebunden: contracts, validation_attestation, validation, store, service, paths und backup. Ihre Bytes werden direkt kompiliert; keine Produkt-Packageinitialisierer ausgeführt. Getrackter Status vor/nach leer; sieben Dateihashes und HEAD gleich. Ungetrackte Dateien nicht inventarisiert.

Worker-Final4 und neue Leitung-Wiederholung: jeweils **5 Tests, 0 Fehler, 0 Fehlschläge, 0 Skips**. Testnamen und Reihenfolge gleich. Leitung hat Testanzahl, Namen, Skipzahl und Quellenbindung ausdrücklich geprüft: der Runner allein erzwingt im `overall_status` weder genau fünf Tests noch null Skips. Dieses P2-Werkzeuglimit bleibt dokumentiert.

Synthetische Receipt-Zeile direkt in Scratch-DB eingefügt; damit ist der Service-Schutz geprüft, **nicht** der eigentliche Importweg. `service.py:1063–1084` verlangt den speziellen Revalidierungsweg. Dieser führt in `store.py:2009–2055` zu `core.source_data_promotion` und `core.source_registry`, außerhalb der sieben ausführbaren Module. Keine Registry-Autorität durch Test-Dummies ersetzt, keine reale Registry geöffnet.

Python-Guards begrenzen Produktimporte, Netzwerk-/Subprozess-Einstiege, Datei-/SQLite-Ziele und benutzen eine geschlossene synthetische `os.getenv`-Belegung. Git-Quellenbindung läuft vor/nach außerhalb dieser Guards mit geerbter Hostumgebung. Dies ist **keine OS-Sandbox oder vollständige Lesekontrolle**; SQLite-ATTACH-SQL ist nicht allgemein gesperrt. Keine Produkt-App/CLI/Worker/API/Auth-/Key-Komposition gestartet; ausschließlich synthetische Scratch-Daten im tatsächlichen Testablauf. Keine umfassende Egress-/Sicherheitsabnahme ableiten.

Fehlerbelege erhalten: zunächst falscher früherer Binding-Beleg, dann realer Store-Typcheck beim Test-Dummy; später Windows-Cleanupfehler durch nicht explizit geschlossene direkte SQLite-Verbindung. Testaufbau korrigiert, Produktquellen unverändert. `SOURCE_BINDING-final2.json` ohne passendes Resultat zählt nicht als ausgeführter bestandener Test. Zwei synthetische Scratch-Reste erhalten, kein echter Klienteninhalt. Final4 und Leitungslauf räumten ihre eigenen Scratch-Daten regulär auf.

Belege: `checkpoints/Aurelia-P3-Morphic-Import-Tests-20261011/`, insbesondere `result-final4.json`, `SOURCE_BINDING-final4.json`, `result-root-repeat-20261011.json` und `SOURCE_BINDING-root-repeat-20261011.json`.

## RadiFarben: begrenzte statische Zuordnung

Aktueller ACCDB-Hash `2993247b0b06e84d5897870790a54b0800d8db701e3d1f004c3c26e54675a1c9`; vorherige Referenz `2b48ce8dec5e0126072e0bc24f07b754b8b64af0651b080d257dcb1b0c8f13bc`. Die neue Verarbeitung nutzt den zuvor gebundenen 204-Datei-Capture mit Manifesthash `9ec1e7095625c4e6c0ce18d1a5287f39c42dccf09b076fd23341e69733379536` und die historische Query-Metadatei `c7d89827d471e407ccc78dd45cbe0645f724787a545c238ae8accbb27b2e5a4d`. Historische SQL-Definitionen bleiben an den **alten** ACCDB-Hash gebunden; kein neuer DAO-Export.

Beide konsumierten JSON-Dateien und genau 100 eindeutige kanonische VBA-Dateien ausdrücklich manifestgebunden, alle Capture-Dateien vor/nach Verarbeitung hash-/größengeprüft. Zwei neue Läufe haben bytegleiche öffentliche Aggregate und gleiche private Zuordnung außer UTC. Keine unabhängige zweite Decoderimplementierung.

| Befund | Anzahl | Aussagegrenze |
|---|---:|---|
| Geänderte Query-Objekte | 5 | Weiterhin nur erfasster Lv-Übergang NULL→binär |
| Historische Definitionstreffer | 3 | Namenszuordnung zu alten Definitionen, kein aktueller SQL-Paritätsnachweis |
| Historischer Parameterstatus | 2 captured, 1 denied | Keine neue Parameter-/Ausführungsprüfung |
| Namen mit `~sq_`-Präfix | 2 | Namensklassifikation, kein gespeicherter Besitzer-/Control-/RecordSource-Beweis |
| Literalkandidaten je Änderungsobjekt | 6 / 0 / 0 / 0 / 0 | Kein vollständiger Callgraph; null Treffer bedeutet nicht unbenutzt |
| Gebundene VBA-Dateien | 100 | Quelltextbezüge, keine VBA-Ausführung oder P-Codeparität |

Helpertests: Leitung und Astra jeweils **15 synthetische Tests bestanden, 0 Fehler/Skips**. Vor Korrekturen fehlschlagende Regressionen zu `Rem` nach Doppelpunkt und fehlendem Manifest-/Inventarvalidator erhalten. Literalsuche berücksichtigt Kommentare, Strings und einfache Prozedurgrenzen; dynamische Namen, Menü-/Geschäftszeilen und vollständige VBA-Syntax werden nicht aufgelöst. Festes Manifest wesentlich; keine allgemeine Windows-Dateinamen-Sicherheitsprüfung oder Racegarantie.

Erster Sandboxlauf endete mit WinError5 vor Ausgabe am geschützten Manifest. Danach zwei erlaubte Owner-Läufe Exit0. Neue technische Privatbelege unter `runtime/radifarben-source-versions/RF-20261011-080657Z/query-bindings-20261011-run1` und `...-run2`, beide manifestiert/rückgeprüft. Roh-SQL/VBA nicht in neue Zuordnungsdateien kopiert und nicht an Helfer gegeben. Öffentliche Ergebnisse enthalten keine Objekt-/Prozedurnamen, SQL oder Klientendatensätze.

Frische Quellenendpunkte um **15:39 UTC**: Original und aktuelle Masterkopie hashgleich zur aktuellen Referenz, alte Masterkopie zur alten Referenz; Metadaten während jeweiliger Byte-Lesung stabil, keine `.laccdb`-Datei an den drei Endpunkten. Das ist keine WORM-/Exklusiv-/kontinuierliche Beobachtung. Kein Access/COM/DAO/SQL/VBA ausgeführt oder Geschäftsdaten dekodiert.

Öffentliche Belege: `checkpoints/RadiFarben-RMF-Query-Bindings-20261011/`; Quellenendkontrolle `checkpoints/Aurelia-P3-Import-RMF-20261011-153618Z/SOURCE_FINAL.json`.

## Review, Sicherung und Reihenfolge

Tatsächlich beteiligt: **GPT-6 Luna/max** für das begrenzte Morphic-Prüfwerkzeug; **GPT-6 Astra/medium** für unabhängige Werkzeug-/Scope- und öffentliche Ergebnisprüfung; Leitung verarbeitet private RadiFarben-Quellen selbst. Astra wiederholte die 15 synthetischen RadiFarben-Tests, nicht die privaten Läufe oder den Morphic-Harness. Vor Leitung-Wiederholung kein nachgewiesener P0/P1 im begrenzten Umfang, mittlere Konfidenz; offene Grenzen oben bleiben maßgeblich. Modellroute konfiguriert dadurch nicht geändert.

Vorher-/Nachher-Sicherung und exakte Belege unter `checkpoints/Aurelia-P3-Import-RMF-20261011-153618Z`; Manifest separat frisch prüfen. Vollständige bisherige Wiederaufnahme als unveränderte Bytesuffix erhalten. Begrenzter lokaler Prüfpunkt, **keine neue F:-Gesamtsicherung** und keine Vollsicherung der Plattform. Keine Produktalgorithmen, Liveinstanzen, Cloud/WSL, Officeinstallation, Governors/Routing oder normative Modul_Templates durch diesen Block geändert.

Nächster unabhängiger P3-Block: vorhandene Writer-/Report-/Archiv-/Restore-Verträge quellengebunden weiter charakterisieren; Registry-Revalidierung und RF-E1/Access-Originalreferenzen gesondert mit passenden Ausführungsgrenzen vorbereiten. P0/P1/P2 und restliche P3-Abnahmen bleiben offen. Danach erst **P4 vollständige siebenmodulige Matrix einschließlich Aurelia/Modul_Templates**, **P5 zentrale Datenstrukturentscheidung**, anschließend P6–P8 und getrennte S4.8-Freigabe. RadiWorks-Wartungsnachträge bleiben nach dem P-Prüfpunkt priorisiert, nicht in diesem Block umgesetzt.

Abschlussreview Astra: keine neuen P0/P1 oder materiellen Überclaims im geprüften öffentlichen Umfang, mittlere Konfidenz. Präzisierung im aktuellen Plan/Wiederaufnahme umgesetzt: die drei ACCDB-Endpunkte bleiben zu **ihren jeweiligen** Referenzhashes unverändert; die alte Masterkopie hat ausdrücklich einen anderen Hash. Private Quellen/Outputs sowie Checkpointmanifest und Wiederaufnahme-Bytesuffix nicht von Astra unabhängig geprüft; diese Kontrollen sind Leitungsevidenz.

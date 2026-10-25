# P3 – RadiFarben: aktueller RMF-Quellvergleich, 11.10.2026

Der neue, vom Betreiber als höchste aktuelle RMF-Version bestätigte ACCDB-Stand ist jetzt **frisch statisch erfasst**. Die Dateien unterscheiden sich, die 100 erfassten kanonischen VBA-Quelltexte stimmen jedoch überein. Fünf Query-Objekte haben abweichende binäre `Lv`-Metadaten. Das ist keine vollständige Formular-, Algorithmus- oder Laufzeitabnahme.

## Quellenbindung

| Referenz | SHA-256 |
|---|---|
| Frühere private Masterkopie | `2b48ce8dec5e0126072e0bc24f07b754b8b64af0651b080d257dcb1b0c8f13bc` |
| Aktuelle private Masterkopie / Original bei der Vorprüfung | `2993247b0b06e84d5897870790a54b0800d8db701e3d1f004c3c26e54675a1c9` |

Aktuelle Herkunft: `runtime/radifarben-source-versions/RF-20261011-080657Z/SOURCE_VERSION.json`. Alte Extraktions- und Laufzeitbelege behalten ihre frühere Bindung; sie werden nicht auf die neue Datei umetikettiert. Keine interne semantische Versionsnummer erfunden. Weitere Betreiberstände bis zur Aurelia-Integration über neue Kopie, Herkunft, Hash, Delta und betroffene Referenzprüfungen aufnehmen.

Private Captures unter demselben Versionsordner: `static-delta-20261011-140000Z` und `static-delta-20261011-121402Z`. Tatsächliche Erfassungszeiten stehen in den Metadaten: erster Lauf 12:11:21/12:11:23 UTC; Ordnerbezeichnungen sind Nachweis-IDs, keine verbindlichen Erfassungszeiten. Roh-VBA und Objektnamen/-deltas bleiben im geschützten Ordner; Review-Agenten erhielten nur Werkzeuge und bereinigte Aggregate.

## Ergebnis und seine Bedeutung

| Gegenstand | Belegter Befund | Grenze / nächster Nachweis |
|---|---|---|
| Objektinventar | Je 45 Forms, 54 Modules, 3 Reports, 3 Scripts; zusätzlich 85 Query-Typ-Objekte aus `MSysObjects`. Kein hinzugefügter oder entfernter erfasster Schlüssel. | 190 Systemobjekte insgesamt; die 85 Query-Typ-Objekte sind nicht mit den früher über DAO erfassten 47 Querydefinitionen gleichzusetzen. Keine neue DAO-Gegenprobe. |
| Objektmetadaten | 185 von 190 vollständig im erfassten Feldsatz gleich; bei fünf Query-Objekten ist `Lv` zuvor NULL, im aktuellen Stand binär. Sonstige erfasste Felder gleich. | Bedeutung der fünf binären Änderungen offen. Keine Behauptung „nur Darstellung“ oder „keine Auswirkung“. Vollständige gespeicherte Objekte/Ereignisse/Steuerelemente weiterhin nicht dekodiert. |
| Kanonischer VBA-Quelltext | 100 Module je Stand, keine Ergänzung, Entfernung oder Quelltextänderung; gespeicherte Dateihashes und Größen rückgeprüft. Frische alte Extraktion stimmt mit dem früheren 100-Modul-Manifest überein. | Das ist Quelltextgleichheit im erfassten Umfang, keine rohe Stream-/P-Code- oder ausgeführte Formelparität. |
| Query-Speichermetadaten | Je 751 erfasste Zeilen aus `MSysQueries`; sortierte Zeilenfingerprints stimmen überein. | Kein frischer SQL-Text-/Parameter-/Ausführungsnachweis. Die 17 zuvor nicht erfassten Parameterlisten bleiben offen. |
| Wiederholung | Beide Stände erneut frisch ausgelesen; vollständige Erfassungsmetadaten außer UTC gleich. | Gleicher Parser in beiden Läufen: reproduzierbar, keine unabhängige Decoder-Gegenprobe. |
| Quellen und Werkzeuge | Beide festen Masterhashes, Dateidentität/-größe/-zeiten und fehlende Locks an gemeinsamen Prüfpunkten bestätigt; 694 Bibliotheksdateien vor/nach gegen gepinntes Archiv gleich. | Keine Exklusivsperre, WORM-Garantie, lückenlose Hostbeobachtung oder racefreie Betriebssystem-Sandbox. |

Verwendet wurde ausschließlich der bereits archivgebundene statische Parser `binary_refinery` 0.11.2 mit begrenztem ACE03-01-Headerpfad. Kein Paketdownload, kein Access-/COM-/DAO-Aufruf, kein SQL/VBA ausgeführt; keine Geschäftsdatensätze dekodiert. Vollständige ACCDB-Bytes werden für Hash und statisches System-/Codespeicherlesen eingelesen. Die Prozess-/Netzwerk-Tripwires ersetzen keine Betriebssystem-Sandbox.

## Werkzeugprüfung

- Capture-Guards: Leitung 14 synthetische Tests bestanden. Zwei zunächst gefundene P1-Befunde zu Windows-Dateinamen und gemeinsamer Quellenabschlussprüfung behoben; neue Tests zuerst wegen fehlender Implementierung rot, danach grün. Astra überprüfte die Korrekturen, elf schreibfreie Tests selbst ausgeführt; drei temporäre Integritätstests statisch geprüft und durch Leitung ausgeführt.
- Comparator: Worker und Leitung je zwölf Tests, davon elf bestanden, ein echter Symlinktest wegen Windows-Recht `1314` übersprungen. Astra acht Coretests selbst bestanden. Keine vollständige Junction-/Austauschrennen-Prüfung; die private Auswertung nutzt den reinen Comparator über explizite Zweifeldprojektion nach eigener Pfadprüfung.
- Aggregation: beide Capture-Receipts an den korrigierten Capture-Toolhash gebunden, Comparator an seinen geprüften Hash; gespeicherte VBA-Dateien und historisches Manifest kontrolliert. Private Objektdeltas und öffentliche Aggregate getrennt, neue Ausgaben exklusiv geschrieben und rückgelesen. Keine Rohdefinitionen an Helfer.

Tatsächliche Helfer: **GPT-6 Luna/max** für den synthetisch getesteten Comparator, **GPT-6 Astra/medium** für unabhängigen SPEC-/QUALITY- und Ergebnisreview; private Erfassung und abschließende Auswertung durch die Leitung. Keine Änderung von Chat-/Governors-Routing aus diesem Paket.

## Planfortsetzung

| Phase / Schritt | Stand nach diesem Paket |
|---|---|
| P3 / RF-V1 | Aktueller statischer Versions-/Objektvergleich abgeschlossen; Unterschiede und Beweisgrenzen dokumentiert. |
| P3 / RF-E1 | Synthetische Access-Import-/Exportprobe weiter offen nach COM-Startfehler `80080005`; keine neue Hostaktivierung. Vorlagenabdeckung und äußerer Vollharnesscontroller vor einem späteren Lauf klären. |
| P3 / RF-RMF | Zentralen Menü-/Formular-/Event-/Record-/Control-/Makro-/Query-Workflow und die fünf Metadatenabweichungen anhand geschützter Definitionen bzw. kontrollierter Referenzen vervollständigen; keine ungeprüfte Originalöffnung. |
| Weitere P3-Pakete | Unabhängige Morphic-Vertrags-/Writer-/Reportprüfungen fortsetzen. Radi144-/RadiFarben-Laufzeit-, Fehler-, Abbruch-, Restore- und verknüpfte Quellenbelege bleiben ausgewiesen. |
| P0, P1, P2 | Linux-/Lokalstackvoraussetzungen und vollständige lokale Explorer-/Thom-Referenzen/Parität bleiben offen. Keine neue WSL- oder Cloudaktion in diesem Paket. |
| P4 → P5 | Siebenmodulige Bedarfs-/Workflowmatrix einschließlich Aurelia und Templates vervollständigen, **danach** zentrale Datenbankentscheidung. Versionsbindung von Quellen, Objektdefinitionen und Prüfnachweisen ergänzen; keine Datenbanktechnik hier festgelegt. |
| P6–P8 / S4.8 | Kernverträge und normative Modul_Templates erst an beschlossene Struktur anpassen; Module schrittweise abnehmen, danach Integrations-/Tenant-/Abo-/Parallel-/Restorefreigaben. |
| RadiWorks | Bereits konsolidierte Wartungspunkte bleiben nachrangig; kein Live-, Algorithmus-, CopyGuard-Bypass- oder Paketumbau. |

Lokaler Vorher-/Nachher-Nachweispunkt: `checkpoints/RadiFarben-RMF-Delta-20261011-121653Z`, mit vollständiger früherer Wiederaufnahme, Werkzeugen, Review-/Test-/Ergebnisbelegen und Abschlussmanifest. Private aktuelle Rohquellen verbleiben getrennt geschützt. Dies ist keine neue F:-Gesamtsicherung und keine Broadcastzustandssicherung.

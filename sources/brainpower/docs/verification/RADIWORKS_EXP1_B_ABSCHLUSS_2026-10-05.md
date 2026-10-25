# RadiWorks EXP1-B — Ortsauswahl und skalare Vorbereitung

Stand: 2026-10-05T08:42:25.739719+02:00. Begrenztes Entwicklungspaket abgeschlossen, **keine Liveübernahme oder Aurelia-Integrationsfreigabe**.

## Ergebnis und Bedienung
Ein einziges Ortsfeld erhält eine ausdrücklich wählbare Bedeutung: Wohn-/Aufenthaltsort oder Geburtsort. Beim Wechsel wird der Eingabewert geleert und muss neu eingegeben und gespeichert werden; es gibt keinen gespeicherten inaktiven Zweitort. Ein fehlgeschlagener Speicherauftrag lässt die Eingabe erhalten. Bestehende untypisierte Ortsangaben bleiben „Typ nicht festgelegt“; sie werden nicht rückwirkend zu Geburtsorten erklärt. Neuer leerer Fall verwendet Wohn-/Aufenthaltsort als Vorbelegung. Gespeicherte Typen überstehen Browser-Neuladen.

Der Server verlangt bei Typwechsel den expliziten Ort bzw. eine explizite Leerung im selben Auftrag (409 beim Patch,422 beim vollständigen Ersatz). Kontextversion und unveränderliche Sitzungs-Snapshots halten alte Aufträge unverändert. Originalanalysen mit festem Seed liefern vor und nach Ortswechsel identische Zahlen. Ein optionales Bild bleibt eingefrorener Kontext ohne numerische Gewichtung.

Der neue reine Helper `prepare_experimental_context` validiert den eingefrorenen Snapshot und bereitet ausschließlich die vorhandenen Radi144-Namens-/Geburtsformeln vor. Version `radi144-scalar-input-v1`; Referenz-SHA3146960a23041cca959befd85882888fc3f896fe3b9a4eb83916b85aec859894. Gewichte Name0,15/Geburt0,20, normalisiert über verfügbare Komponenten. Geburtsort fließt nur bei ausdrücklich gewähltem Typ und vorhandenen Geburtsdatum ein. Wohnort/untypisierter Ort, Bild und Fokus ergeben hier keine zusätzliche Zahl. Fokus bleibt `requires-catalog-match` für die nächste Stufe. Organuhr, planetare/EMF/HRV-/Bildsignaturen sind aus; kein Modellaufruf oder Entropieverbrauch.

**Noch nicht implementiert:** vollständige Matrixberechnung, Ratenranking, neue Experimental-Sitzungen, Auswahl des Experimentalmodus und Original/Experimental-Vergleich. Das folgt als EXP1-C. Der Helper ist kein Nachweis physischer/medizinischer Wirkung oder garantierter Unterscheidbarkeit aller Personen.

## Review und Reproduzierbarkeit
Astra fand eine indirekte Systemdatumsabhängigkeit beim Lesen gespeicherter Snapshots. Behoben: Normalisierung beim Snapshot-Lesen erhält eine eingefrorene Grenze UTC-Aufnahmedatum+ein Kalendertag; der Tag ist eine konservative Zeitzonentoleranz, keine exakte Rekonstruktion der ursprünglichen lokalen Zeit. Intake behält seine strenge aktuelle Zukunftsprüfung. Kalenderformat, Prüfsumme und Kontextgleichheit werden weiter geprüft, extreme UTC-Konvertierung wird kontrolliert abgelehnt. Der Snapshot-Zeitstempel ist dadurch nicht authentifiziert; SHA-Digest ist keine digitale Signatur. Legacy-Struktur/Digests werden nicht umgeschrieben.

Root korrigierte zusätzlich die Kennzeichnung `birth-scalar` ohne Geburtsdatum. Beide Fehler sind durch zuvor fehlgeschlagene Regressionstests belegt. Astra-Nachprüfung: keine weiteren Befunde, statisch; Root hat die abschließenden Tests durchgeführt.

## Nachweise
- **585 Engine-PASS**,0Fehler,3 bekannte Windows-Symlink-Skips; `engine-reviewed.xml/log`. Bestehende Starlette/httpx-DeprecationWarning unverändert.
- **34 neue gezielte Tests**:21 Orts-/API-/Originalkompatibilitätsfälle und13 skalare/Snapshotfälle; `inputs-final.xml/log`.
- **41/41 sichtbare isolierte Chrome-Abschnitte** (36 bestehende+5 neue), eigenes synthetisches Home/ephemerer Port, tatsächlicher Kandidatenimport geprüft; `browser-reviewed.log`. Ortswechsel, Fehler+Retry, alte Sitzung, Reload,320px-Reflow und sichtbarer Tastaturfokus geprüft. Screenshots Desktop/Mobil visuell kontrolliert; keine vollständige WCAG-Abnahme.
- **19 JavaScript-Syntaxprüfungen**, **8 direkte Quellenproben** gegen AST-extrahierte Originalmethoden in RadiWorks-Python3.13; keine Torch/NumPy-/Bildabhängigkeit für die skalare Vorbereitung geladen.
- **117 Produktdateien** im Kandidat;114 VF3-Elternhashes und6 Design-/Formelreferenzen unverändert. Änderungen:4 bestehende Dateien+3 neue Dateien. `PRODUCT_MANIFEST.json`, `CHANGES.diff`, `SOURCE_STATE.json`.
- **8103–8110**:8 unveränderte Prozess-IDs,8HTTP200/pong. Erste nicht einzeln diagnostizierte Probe hatte Timeout; abschließende ausdrücklich proxyfreie Loopbackprobe0,08–0,32s. Kein Neustart, kein Task-/Key-/Live-Home-Eingriff.

Belegordner: `runtime/rw-exp1b-20261005`. Frühere fehlgeschlagene Läufe bleiben sichtbar: erster Browserzusatz aktivierte den angelegten Fall nicht ausdrücklich; Testaufbau korrigiert, reale Ladehandlung ergänzt. Früherer Engine-Vollauf lag vor Snapshotkorrektur und ist durch `engine-reviewed` ersetzt. RED-Ortstest hatte anfänglich ein fehlendes Temp-Elternverzeichnis; maßgeblich ist `place-red-fixed` mit10 echten Fehlern/11PASS, nicht der fehlerhafte erste Aufbau.

## Stand und Folge
| Paket | Stand |
|---|---|
| VF2-B/VF3 Kontext/Katalogsuche |100% begrenzte Kandidatenpakete; Regression bestätigt|
| EXP1-A Quellenprüfung |100% Vorprüfung|
| EXP1-B Ortsauswahl/skalarer Eingang |100% dieses geprüften Pakets|
| EXP1-C Matrix/Ranking/vergleichbare Sitzungen |0% Umsetzung; nächster Block|
| Quellen-/Modul_Templates-Übernahme |Ausstehend; Delta vorbereitet|
| Aurelia S4.8 |0% Freigabe|

Danach bleiben die vereinbarten Trend-/Kamera-/Stochastic-/Wiederherstellungs-/Area-/Peggotty-/Bedienabnahmen, kanonischer Quellen-/Template-Abgleich, versioniertes Win10-Testpaket bis5Instanzen und vollständige verifizierte F:-Gesamtsicherung vor Radi144. Keine Frist; Qualität zuerst. Tatsächliche Helfer: Luna6/max für den begrenzten Helper, Astra6/medium für unabhängigen Review; Root integriert/testet. Gewählte Chatleitung Sol6.1/high; kein Nachweis des Runtime-Modells aus gespeicherter Konfiguration und keine gemessene Tokenersparnis.

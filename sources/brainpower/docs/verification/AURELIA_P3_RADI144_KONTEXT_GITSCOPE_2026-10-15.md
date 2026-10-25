# P3 – Radi144-Kontextreferenz nach begrenzter Git-Korrektur bestanden

Stand 15.10.2026. Betreiberentscheidung „Ja, gehe gerne weiter,,,": den ausschließlich lokalen Prüfcontroller korrigieren, gezielt prüfen und zwei neue Referenzläufe ausführen. Originalalgorithmen bleiben unverändert. Neuer Punkt: `checkpoints/Aurelia-P3-Radi144-Context-GitScope-20261015-072137Z`. Der frühere fehlgeschlagene Punkt bleibt unverändert erhalten; dessen Kennung 1 wurde nicht erneut verwendet.

## Ergebnis und Reichweite

| Prüfung | Belegtes Ergebnis |
|---|---|
| Controllerkorrektur | Fester Radi144-Pfad und Reparse-Komponenten vor Hashlesen/Gitstart geprüft. Nur Prozessargumente: leere `safe.directory`-Liste, danach genau dieser Pfad; `core.fsmonitor=false`. Alle drei Git-Leseabfragen verwenden bereinigte Umgebung. Kein globaler Konfigurationseintrag, keine Wildcard oder Produktänderung. |
| Regressionen | Drei neue Controllertests zuerst mit drei erwarteten Fehlern gegen die bisherige Fassung; anschließend gesamte aktuelle Suite: **23 Tests erfolgreich, keine Skips**. Vier tatsächlich geprüfte Werkzeugfassungen und Ausgaben gesichert. |
| Vorreview | Astra/medium prüft tatsächliche eingefrorene Bytes, Rot-/Grünausgaben und SPEC→QUALITY unabhängig: keine materiellen Abweichungen oder Blocker. Keine Ausführungserlaubnis durch Review. |
| Neue Originalteilreferenz | Zwei frische Kindläufe mit je **12 Fallgruppen und 42 Erwartungen** bestanden. Nur acht gebundene AST-Funktionskörper mit synthetischen Ein-/Ausgabegrenzen; keine Produktmodule oder Klassenkonstruktoren importiert. |
| Vollvergleich | Vollständige Ergebnisobjekte ausschließlich ohne `label` identisch. Kanonischer SHA-256: `8929b240cad50ea6d445bf74f57f8024457d3301f10d5fdc771aea1cfb1bb536`. |
| Quellen und Git | Zehn Quellhashes, acht aktuelle AST-Verträge und vier Werkzeughashes gebunden. Vor/nach beiden Läufen gleicher HEAD `b8ac33a1360f1cb56f06e602fcd37cbda2a9c641` und benannter Raw-XY-Status ` A AGENTS.md` (Indexspalte leer, Arbeitsbaum A). Das ist keine Aussage über unbenannte Dateien. |
| Fehler-/Abschlusskontrolle | Beide Exitcodes 0, stderr leer, keine Timeouts oder Nachprüffehler. Gate auf seine ursprünglichen geschlossenen CRLF-Bytes zurückgesetzt. Laufkennungen verbraucht. |
| Ergebnisreview | Astra/medium rechnet Gruppen/Erwartungen, vollständigen Vergleich, Ergebnis-/Quellen-/AST-/Werkzeugbindungen und Controllerbelege unabhängig nach: keine materiellen Widersprüche oder Blocker. |

## Bestätigte Originalbefunde – keine Reparatur

| Gegenstand | Beobachtung in dieser begrenzten Probe | Konsequenz für P4 |
|---|---|---|
| Geburtszeit | Synthetisches Datum 2000-01-01: `HH:MM` ergibt `379.08333333333337`; natives Zeitobjekt sowie `HH:MM:SS` hier nur Datumsbeitrag `327.0`. Ungültiges Datum führt zu `0.0` und erfasster Warnung. | Ursprünglichen Typ, Serialisierung, tatsächlich angenommenen Formatweg und Fallback getrennt dokumentieren. Kein stilles Angleichen der Originalformel. |
| Registry-Projektion | Genau fünf Felder; Geburtszeit, Geolocation und freie Metadaten werden hier nicht projiziert. Nachnamenliste wird unabhängig kopiert. | ID-Auflösung und direkte Eingabe dürfen nicht pauschal als gleicher Rechenkontext gelten. Aus ausgelassener Geolocation allein folgt kein bewiesener Zahlenunterschied. |
| Inline A plus ID B | Kontextaufbau bevorzugt Inline A; Sitzungsreferenz verwendet ID B, der vorgegebene Ergebnisname bleibt von A. | Berechnungseingang, stabile Identität, Ergebnisname und Sitzungsreferenz getrennt führen; vor einer späteren Vereinheitlichung eigene Produktentscheidung. Kein nachgewiesener realer Klientenfehler. |
| Fehlende ID | 404-Grenze ohne Sitzungsversuch; beim gemischten Fall entsteht zuvor der Inline-Kontext. | Fehler-/Teilabschlussreihenfolge beibehalten und auditierbar machen. Die HTTP-Ausnahme ist ein Double, keine echte HTTP-Antwort. |
| Reine ID / reine Inline-Eingabe | Getrennte erwartete Registrywege und unabhängige synthetische Sitzungskopien bestätigt. Standalone-Fallback hat genau vier Felder. | Eingabeherkunft und Fallback nicht mit vollständigem persönlichen Kontext verwechseln. |

## Nachweise und Grenzen

Primärbelege im neuen Punkt: `ROOT-FROZEN-TOOLS.json`, `root-git-scope-red-20261015-072813Z-34ff6828/RED-MANIFEST.json`, `root-green-20261015-073213Z-96b9487d/ROOT-TEST-RECEIPT.json`, `ROOT-PREEXECUTION-REVIEW.json`, `ROOT-EXECUTION-LAUNCHES.json`, beide `runs/context-run-*/controller.json` und `result.json`, `ROOT-COMPARISON.json`, `ROOT-RESULT-REVIEW.json`. Das alte Manifest wurde vor Beginn nachgerechnet (117 Dateien, 116 ZIP-Einträge); erneute Abschlussprüfung im finalen Rücklesebeleg.

Die erste Root-Vorprüfung dieser Fortsetzung stoppte vor Teststart an einer LF-only-Annahme für die tatsächlich CRLF-geschlossene Gate-Datei. Readback bestätigte unveränderte geschlossene JSON-Bytes und alle Rotbelege. Danach ausschließlich diese Wrapperannahme korrigiert; kein Referenzversuch wiederholt oder Beleg überschrieben. Ein vorangehender Leseversuch auf `stderr.txt` wurde auf die tatsächlich gespeicherte `stderr.bin` berichtigt. Die früher dokumentierten Zwischenmanifestgrenzen des alten Punkts bleiben erhalten; sie gelten nicht als Grünbeleg dieser neuen Fassung.

`model_dump()` hält native Typen als explizites Double. Registry und Sitzungen sind synthetisch und im Speicher; keine Identitätshash-, Rechte- oder Persistenzprüfung. Kein echtes Pydantic, HTTP, UI, voller Signaturgenerator, Rechenengine, NumPy/Pillow/Torch, Stochastik oder Linuxweg in diesem Teilnachweis. Der In-Process-Auditguard ist keine Betriebssystemsandbox. Numerische Variationen beweisen keine Klientenreaktion oder Wirksamkeit.

Luna/max besitzt die drei neuen Controllertests und ihren Rotbeleg; Leitung implementiert Controllergrenze, führt Grün-/Referenzläufe aus und konsolidiert Belege; Astra/medium prüft Entwurf, eingefrorene Werkzeuge und Ergebnisse unabhängig. Daraus wird keine tatsächliche Desktop-Modellauswahl abgeleitet.

## Nächste Schritte und fortgeltende Gates

Dieser begrenzte Kontext-/Zeittypnachweis ist abgeschlossen. Nächster unabhängiger P3-Block: übrige reine Radi144-Signaturanteile und Aggregation quellengebunden vorbereiten, einschließlich expliziter Prüfuhr für Organuhr/Zeitstempel. NumPy und Bild-/Pillowpfade getrennt mit tatsächlichen Bibliotheken prüfen; keine Ersatzformel als Originalparität ausgeben. Volle API-/Store-/UI-/CLI-/Abbruch-/Parallelitätswege bleiben getrennt.

Gesamt-P3, führende Morphic-Quelle, RF-E1 und Linux-/Backendreferenzen bleiben offen. Vollständige siebenmodulige P4-Vergleichsmatrix einschließlich Aurelia und Modul_Templates vor der P5-Datenbankentscheidung; P6–P8/S4.8 separat. Keine Liveinstanzen-, Governors-, Routing-, Server-, WSL-, Access-, Cloud-, Algorithmus- oder normative Templateänderung. Lokaler begrenzter Vorher-/Nachherpunkt; Abschluss/Umfang erst durch `FINAL-READBACK.json` bestätigt. Kein F:-, Server-, Schlüssel- oder Gesamtprojektbackup.

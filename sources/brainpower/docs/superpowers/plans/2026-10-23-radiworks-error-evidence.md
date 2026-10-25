# RadiWorks: begrenzte Fehlerbelege und adaptive Chatroute

**Goal:** Fehlende Ist-/Sollgrenzen und getrennte Zustandsbeobachtungen nach einem fehlgeschlagenen Start lokal als additiven Kandidaten vorbereiten; keine Serverausführung.

**Architecture:** Drei Kopien der eingefrorenen V5-Helfer in `runtime/rw-v5-error-evidence-20261023`. Der vorhandene einmalige kombinierte Stoppbefehl bleibt unverändert. Diagnosezusätze erhalten nur erlaubte, begrenzte Felder; ursprünglicher Fehler und seine Weitergabe bleiben maßgeblich.

**Tech Stack:** Python-Standardbibliothek, unittest; Testprozesse dürfen keine untergeordneten Prozesse oder Netzwerkverbindungen starten.

## Bindung und Ausschlüsse

Der Betreiber autorisierte am23.10. die Fortsetzung und die aufgabenabhängige Chatroute. Vorherige Belege, Produktalgorithmen, normative Modul_Templates und Hermes bleiben unverändert. Ein neuer Materialstart benötigt einen neuen vollständigen Kandidaten und eine gesonderte konkrete Freigabe. Dieses Paket enthält keinen Transport und keine ausführbare Remote-Hülle.

`PLAN.json` bindet50 Kandidaten-,17 ältere Diagnose- und18 V2-Belegdateien sowie die kopierten Ursprungsdateien. Ausgangsdokumente werden vor ihrer späteren gezielten Aktualisierung gesichert.

## 1. Tests vor Änderung

- [x] `test_failure_evidence.py`: echte `remote_common.limits`, `Runtime.start`, `start_diagnostics.metadata` und vorhandenes `safe_worker` mit künstlichen Dateien und kontrollierten IO-Grenzen ausführen.
- [x] Nachweisen: Unterschied einer der fünf Grenzen wird im Beleg sichtbar; unveränderte Werte bleiben exakt akzeptiert; beliebige Ausnahmeinhalte, Pfade und Ausgaben gelangen nicht hinein.
- [x] Nachweisen: ein kombinierter Stoppversuch, danach höchstens eine feste Leseabfrage je Dienst/Slice; Einzelfehler überschreiben den Ursprungsfehler nicht. Kein inaktiver Zustand wird als vollständiger Prozess-/Cgroup-Bereinigungsbeweis ausgegeben.
- [x] RED-Beleg gegen die unveränderten kopierten Helfer sichern. Fehlende Funktionalität muss Assertionfehler auslösen, keine Import-/Umgebungsfehler.

## 2. Minimaler Kandidat

- [x] `start_diagnostics.py`: feste Fünf-Dateien-Grenzmetadaten, strikte Typ-/Längen-/Wertprüfung und getrennte zulässige Unit-Beobachtungen ergänzen.
- [x] `remote_common.py`: vorhandenen exakten Vergleich unverändert lassen; beim Mismatch bereits gelesene Werte explizit an Diagnose übergeben.
- [x] `linux_admission.py`: nach bestehendem Stoppresultat getrennte Unit-Eigenschaften lesend beobachten. Beobachterfehler über vorhandenes `safe_worker` einkapseln; ursprüngliche Exception erneut auslösen.
- [x] Legacy-Testfixture nur um synthetische Unit-Leseantworten ergänzen; neue Tests prüfen die tatsächliche Beobachterfunktion ohne Erfolgsmock.

Beobachtungen sind sequenziell und können die historischen Werte des alten Laufs nicht rekonstruieren. Zwei neue Unit-Leseabfragen verwenden die vorhandene begrenzte `props`-Funktion; dies muss vor einer späteren Paketbildung in deren Gesamtlaufzeitbudget eingehen. Erfolg des Stoppbefehls und aktueller Unit-Zustand bleiben verschiedene Fakten.

## 3. Prüfung und Review

- [x] Neue Tests, Legacy-Diagnosetests und Compileprüfungen ausführen; Eingangs-/Ausgangshashes, tatsächliche unittest-Zahlen und Prozessverbotsbeleg sichern.
- [x] Astra/medium prüft echte Helfer, Ursprungserhaltung, Datenbegrenzung, Fehlpfade und Route unabhängig. Bei materiellem Befund keine weitere Phase.
- [x] Unverändertheit aller ursprünglichen Belegdateien erneut nachweisen, Ergebnis und Wiederaufnahmepunkt sichern.

## 4. Sichere Route-Übernahme

- [x] Einen eng begrenzten Luna/medium-Quellenabgleich mit bereits geprüftem Stand vergleichen. Initialfehler und Korrekturen ausdrücklich erfassen; ein einzelner Fall begründet keine generelle Qualitäts-/Kostenzusage.
- [x] Nach Review aktuelle Chat-Arbeitsanweisung und Routendokumentation widerspruchsfrei aktualisieren: Sol6.1/medium für geklärte normale Abgleiche; Sol/high für Recovery, Nebenläufigkeit, Sicherheit und zentrale Verträge; Luna/low oder medium zunächst mit unabhängigem Quellencheck, max bei anspruchsvoller begrenzter Prüfung; Astra/medium unabhängig, high nur bei ausdrücklich gewähltem wesentlichem ungelöstem Widerspruch.
- [x] Keine globale Profildatei, kein Hermes-Routing und keine bestehende Chat-Laufzeiteinstellung ändern. Hauptchat-Umschaltungen nur als tatsächlich vom Betreiber ausgeführte Auswahl behandeln.

## Ende dieses Arbeitspakets

Akzeptierter lokaler Diagnosekandidat ist keine Behebung des historischen Kernel-Mismatch und kein freigegebenes Startpaket. Danach frisches vollständiges Paket einschließlich Laufzeitbudget/Bootstrapbindung vorbereiten; kein Retry oder Markerreset eines alten Versuchs.

Abschluss23.10.:54 lokale Tests/7Compileprüfungen und finaler unabhängiger Review ohne materiellen Blocker; Route als Arbeitsanweisung übernommen, keine Hauptchat-/Profilumschaltung. Ergebnis und Grenzen: `runtime/rw-v5-error-evidence-20261023/RESULT.json`. Keine native Ausführung und kein neues Startpaket.

# RadiWorks R1 – isolierte Linux-Speichercharakterisierung

Stand:17.10.2026. Betreiberfreigabe: „Ja ich gebe R1 frei. Danke.“ Ausgeführt wurde ausschließlich der [R1-Prüfplan](../superpowers/plans/2026-10-17-radiworks-storage-r1.md). **15 Kontrolltests und 27 unterschiedliche Produktproben erfüllen ihre begrenzten Konsistenzkriterien. Kein Speicherwächter aktiviert, kein Security-Befund geschlossen.**

## Ergebnis und unveränderte Basis

Produktbasis `d1eb34260179a499e2b0362bf609ce96957b78aa`; unabhängige additive Arbeitskopie `runtime/rw-storage-r1-20261017`, Branch `codex/rw-storage-r1-20261017`. Keine versionierte Produktdatei geändert. Kein lokaler Produktimport oder lokaler Produkttest, kein Image-Build/-Pull, kein neuer Cloud-Scan, keine Übernahme in Windows, Modul_Templates oder Aurelia.

| Prüfung | Umfang | Ergebnis / Bedeutung |
|---|---:|---|
| Steuerung |15 Tests | Grenzen, Timeout, kombinierte Ausgabe, fehlgeschlagene Prozesse, OOM-/Statusauswertung, Quellhashes, Artefaktbudget und Containerentfernung geprüft. Initialer absichtlich funktionsloser Runner lieferte zuvor12 Tests/29 erwartete fehlende Funktionsassertionen. |
| A: JSON / Recovery |17 Fälle | Zwei Payloadgrößen, partielle Writes, Flush, Close, Datei-fsync, Verzeichnis-fsync, Replace, vollständige/unterbrochene Mehrdateioperation und echte ENOSPC-Probe. Festgelegte Alt-/Neuzustände bzw. Recovery-Marker bestätigt. |
| B: Bilder / Journale |5 Fälle | Zwei PNG-Größen bytegleich zurückgelesen, doppelte Aufnahme erzeugt nur eine Bilddatei. Journal-Basislauf sowie injizierte Append-/Commitfehler geprüft; fehlerhafte Instanz verweigert weitere Nutzung. |
| C: SQLite |3 Fälle | Beide Stores im neuen Prozess gegen dieselben Daten geöffnet: PID7→8, Status running→interrupted. Zwei injizierte Transaktionsfehler führen zu Fehlerantworten ohne neue Jobzeile. |
| D: Parallelität / Konflikt |2 Fälle | Zwei gleichzeitig schreibende Threads hinterlassen einen vollständigen Kandidaten ohne temporäre Reste. Recovery-Digestkonflikt wird abgewiesen, abweichende Änderung bleibt erhalten, fehlgeschlagener Marker wird sichtbar. |

Jedes Paket verwendete das vorhandene Offline-Image `sha256:121b7b271d5709c44c1e8ac2a62d6ef21acaed6dcd009514cdcbb6caee664215`, Netzwerk aus, Root/Quellen/Harness read-only, UID/GID65532,1CPU,512MiB RAM ohne Swap,64PIDs, tmpfs32MiB und separates ENOSPC-tmpfs4MiB. Tatsächliche cgroup-/Mountgrenzen wurden im Container geprüft. PID1-Wächter175s und äußere Erfassung180s; Timeout/OOM/Ausgabegrenze wäre ein fehlgeschlagener Lauf. Kein solcher Abbruch in den erfolgreichen Produktpaketen.

Kindausgaben sind zusätzlich auf64KiB pro Prozess/128KiB zusammen begrenzt. Bericht plus Kindausgaben und8KiB Reserve bleiben unter1MiB. Eigene serverseitige Werkzeuge/Belege bleiben insgesamt unter8MiB; Hostjournale und kleine Docker-Steuermetadaten sind keine erfasste Anwendungsdatenquote.

## Messpunkte für die nächste Schutzplanung

| Beobachtung | Gemessene Bytes | Konsequenz |
|---|---:|---|
| JSON, Payload96/2048 |135 /2087 | Tatsächliche Serializerbytes zählen. |
| Recovery-Marker für zwei Ziele |1042 /4946 | Marker enthält vollständige Zustände und beansprucht zusätzlich Platz; ein kleiner fixer Statuspuffer reicht als Nachweis nicht. |
| Echte ENOSPC-Probe |4190208 Füllbytes, errno28 | Atomic-JSON-Fehler ließ den alten46-Byte-Datensatz erhalten; keine temporären Reste. Nach eigener Bereinigung4194304 Bytes frei. Keine Hostpartition gefüllt. |
| PNG2×2 /32×32 |83 /3649 | Jeweils eine gespeicherte Datei trotz doppelter Aufnahme; Nutzlast und temporären Bedarf getrennt rechnen. |
| Persönlicher SQLite-Store |24576 DB; beobachtetes Gesamtsample37400 | DELETE-Journal bis12824 Bytes im Sample; FULL/synchronous2, Busy-Timeout10000ms, foreign_keys0 beobachtet. |
| Vergleichs-SQLite-Store |36864 DB; beobachtetes Gesamtsample94384 | WAL bis24752 und SHM32768 Bytes im Sample; WAL/FULL, Busy-Timeout8000ms, foreign_keys1 beobachtet. Nicht einzelne Maxima aus unterschiedlichen Zeitpunkten addieren. |
| Zwei JSON-Schreiber |je131110 | Vollständiger Endkandidat beobachtet; kein Beleg gegen fachlich verlorene Updates. |

Diese Werte sind **kleine konkrete Beobachtungen und Stichprobenmaxima**, keine garantierten Spitzenbedarfe, Nutzerquoten oder25-Nutzer-Kapazität. Gemessene Laufzeiten betreffen diese synthetischen Proben; sie sind kein Durchsatz-/Lastbenchmark.

## Offene Aussagegrenzen

- Verzeichnis-fsync-OSError wird im bestehenden Produkt best effort geschluckt. Neuer Inhalt ist lesbar, dauerhafte Synchronisation ist damit nicht bewiesen. Kein Schutztest gegen Stromausfall bestanden.
- Nach injiziertem Journal-Append-/Flushfehler kann eine neu geöffnete Journalinstanz **im selben Prozess** den zusätzlichen Datensatz lesen, während die ursprüngliche Instanz gesperrt ist. Lesen bedeutet keine bestätigte Annahme/Commit-Dauerhaftigkeit. Kein neuer Zufallszug wurde als Reparatur veranlasst.
- Die SQLite-Fehler werden im Python-Connection-Proxy vor Commit ausgelöst; **der Proxy führt den Rollback selbst aus**. Kein Nachweis für natives SQLITE_FULL/ENOSPC, produktseitige Rollbackzuverlässigkeit bei echten I/O-Fehlern oder Prozessabbruch mitten in einer offenen Transaktion.
- C prüft die Wiederaufnahme bereits gespeicherter running-Aufträge in einem neuen Prozess. A prüft eine Exception und einen neuen RecoveryCoordinator im selben Prozess. Kein vollständiger HTTP-App-/Container-/Hostneustart oder Stromausfall wurde getestet.
- D beobachtet den vollständigen Endzustand zweier Threads, keine lückenlose Folge paralleler Leserzustände und keine allgemeine Mehrprozess-Serialisierbarkeit.
- Produktquellen59+Pilotentry vor/nach jedem Paket gleich; gesamte lokale versionierte Basis ohne Diff. Bestehende Vorschau identisch/aktiv. Finale rein lesende Prüfung bestätigt keine verbliebenen R1-Container. Keine Datenbank-/Serverbudget-/Websiteänderung.

## Prüfwerkzeugfehler und Review

Fehlversuche bleiben als Belege erhalten. Der erste RED-Versuch scheiterte vor Assertions an Harness-Rechten (UID65532 gegenüber0700/0600); nur eigenes Staging auf0755/0444 korrigiert, Parentverzeichnisse bleiben0700. Die erfolgreiche Entfernung war zunächst wegen unterschiedlich geschriebener Docker-Fehlermeldung negativ bewertet; frische Prüfung und strikte CID-/Statusregression bestätigten die Bereinigung.

Der erste C-Lauf stoppte wegen falscher Fixture-Zugriffe `jobId`/oberster `caseId`; der Quellvertrag lautet `id`/`input.caseId`. Vier Testtreiberzugriffe korrigiert, C danach erfolgreich, ohne Produkt-/Kriterienänderung. Nachweistext in A/B präzisiert, damit neue Instanz und neuer Prozess nicht verwechselt werden. Der endgültige B-Beleg enthält die korrigierte Aussage; ältere Belege sind historische Stände.

Luna/max implementierte ausschließlich den begrenzten Probe-Treiber. Astra/medium prüfte Steuerung/Probe und die Folgedeltas unabhängig. Gefundene unbeschränkte Kindausgabe vor Produktstart korrigiert und mit drei zusätzlichen Linux-Regressionen geprüft. Ergebnisreview bestätigt die15/27-Fallzählung und obige Aussagegrenzen; keine Aktivierungsfreigabe daraus ableiten.

## Belege und exakte Fortsetzung

[Hashgebundener Ergebnisindex](AURELIA_RW_STORAGE_R1_2026-10-17_INDEX.json) bindet jeden verwendeten Lauf samt Toolversion. A/B/C/D wurden teilweise mit unterschiedlich präzisierten Testtreiberversionen ausgeführt; keine Behauptung eines einzigen identischen Harness-Hashes für alle historischen Läufe. [Finalprüfung](AURELIA_RW_STORAGE_R1_2026-10-17_FINAL_CHECK_2.json), [vorherige Lokal-/Quellprüfung](AURELIA_RW_STORAGE_R1_2026-10-17_FINAL_CHECK.json). Rohbelege enthalten Befehle, Laufzeit, echte Grenzwerte, Dateihashes, Rückgabecodes und Bereinigungsstatus. Frühere RED-/C-Fehlerdateien bleiben erhalten.

**Nächster Schritt:** Aus dem bestehenden R2-Entwurf einen konkreten separaten Implementierungs-/Abnahmeplan ableiten: begrenzte Eingänge, Spitzenbedarfsrechnung einschließlich SQLite-Begleitdateien, atomare Zulassung vor Entropie/Arbeit, Abschluss-/Recoverybedarf und Migration größerer Bestände ohne Löschung. Native SQLite-Fehler-/Crashprüfungen und dauerhafter Datenträgerbetrieb bleiben vor entsprechenden Schutzbehauptungen offen. Grenzwerte nicht aus diesen zwei Größen hochrechnen. R2-Implementierung/Aktivierung benötigen ihre eigene Betreiberentscheidung; R1 erteilt sie nicht.

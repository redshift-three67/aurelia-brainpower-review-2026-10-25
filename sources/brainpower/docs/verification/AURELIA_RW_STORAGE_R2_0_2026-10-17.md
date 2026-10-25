# RadiWorks R2-0: ergänzende SQLite-Prüfungen, 17.10.2026

31 Linux-Kontrolltests und zehn synthetische Store-Proben (sechs Kapazität, vier Prozessabbruch/Wiederöffnung) erfolgreich. Der unabhängige Astra/medium-Review fand keine wesentliche Validitätslücke für diesen begrenzten Nachweis. Produktcode, Algorithmen und laufende Vorschau blieben unverändert. Keine Speicherwächter-Aktivierung, Nutzerquote, Ressourcenänderung oder neuer Cloud-Security-Scan.

## Ergebnisse

| Store | Probe | Beobachtung | Wiederöffnung |
|---|---|---|---|
| Personal, DELETE | Native Seitenbegrenzung | SQLITE_FULL, Code 13 | Vollständiger bestätigter Basisauftrag erhalten; integrity_check=ok. |
| Personal, DELETE | FULL in echter Store-Transaktionshülle | Native Ausnahme nach echtem INSERT, vor Commit; PersonalJobError/store_unavailable | Neuer Request abwesend; vollständige Baseline erhalten; integrity_check=ok. |
| Personal, DELETE | Physischer Platzmangel im 4-MiB-tmpfs | Dateisystem errno 28; SQLITE_FULL beim INSERT; PersonalJobError/store_unavailable | Nach Entfernen eigener Fülldateien Baseline erhalten, neuer Request abwesend; integrity_check=ok. |
| Vergleich, WAL | Native Seitenbegrenzung | SQLITE_FULL, Code 13 | Vollständiger bestätigter Basisauftrag erhalten; integrity_check=ok. |
| Vergleich, WAL | FULL in echter Store-Transaktionshülle | Native Ausnahme nach echtem INSERT, vor Commit; ComparisonStoreError/store_error | Neuer Request abwesend; vollständige Baseline erhalten; integrity_check=ok. |
| Vergleich, WAL | Physischer Platzmangel im 4-MiB-tmpfs | Dateisystem errno 28; SQLITE_IOERR_SHMSIZE, erweiterter Code 4874, beim PRAGMA vor Transaktionsbeginn; ComparisonStoreError/store_error | Baseline erhalten, neuer Request abwesend; integrity_check=ok. Kein Nachweis eines fehlgeschlagenen WAL-Commits. |
| Personal / Vergleich | Je eine offene Produkttransaktion | Echtes INSERT, READY mit aktiver Transaktion; Haltebarriere bis gezieltem SIGKILL, Exit -9 | Anderer Childprozess, dieselben DB-Pfade und dasselbe gehaltene tmpfs; neue Requests abwesend, volle Baseline erhalten, integrity_check=ok. |
| Personal / Vergleich | Je eine Unterbrechung nach Commit | Bestätigter running-Auftrag bleibt gespeichert | Anderer Prozess setzt über interrupt_pending auf interrupted; keine automatische Neuanalyse. |

Die beiden tatsächlichen Negativkontrollen mit vorzeitigem Commit nach READY wurden abgewiesen. Sie sind zusätzliche Protokollkontrollen innerhalb des Crashpakets, keine weiteren fachlichen Fälle. SQLite-Version 3.40.1; DELETE/WAL blieben in allen Fällen erhalten. Vollständige Messpunkte und Prozessbelege stehen in den unveränderten Laufdateien des [Index](AURELIA_RW_STORAGE_R2_0_2026-10-17_INDEX.json).

## Aussagegrenzen und Testmechanik

Die native FULL-Kontrolle begrenzt main.max_page_count und aktualisiert ausschließlich eine synthetische input_json-Zeile in einer nie bestätigten Kontrolltransaktion. Die Store-Probe löst dasselbe native UPDATE nach dem echten INSERT auf derselben aktiven Connection aus. Das exakte ComparisonStore-Schema bleibt erhalten. Der Produktadapter führt selbst weder Commit noch Rollback aus; unerwarteter UPDATE-Erfolg wäre ein Harnessfehler. Dies ist eine gezielte native Fehlerauslösung, keine unveränderte fachliche Lastprobe.

Bei den FULL-Proben war connection.in_transaction nach dem Fehler bereits false: SQLite hatte selbst zurückgerollt. Die beobachtete Produktfehlerweitergabe und konsistente Wiederöffnung sind belegt; ein hiervon unabhängiger Produkt-Rollback nicht. Die physische Vergleichsprobe belegt einen SHM-Kapazitätsfehler beim Store-Aufruf vor Transaktionsbeginn.

Die Crashaufsicht hält Container und tmpfs am Leben. Der zweite Prozess muss dieselben Daten öffnen; eine neue leere Datenbank zählt nicht als Recovery. Belegt sind Prozessabbruch und Wiederöffnung, keine Container-/Hostneustarts, Strom-/Datenträgerausfälle, vollständiger HTTP-App-Lifecycle, Parallel-/Langzeitlast oder garantierte Reserven gegen fremde Schreiber. Keine Nutzerzahl oder feste Plattformquote aus diesen Stichproben ableiten. Kein Security-Befund wird dadurch geschlossen.

## Isolation, Quellen und Kontrollen

Eigener rootloser Linux-Container je Paket: festes Offline-Image sha256:121b7b271d5709c44c1e8ac2a62d6ef21acaed6dcd009514cdcbb6caee664215, read-only Root/Quelle/Harness, UID/GID 65532, Netzwerk aus, keine Capabilities, no-new-privileges und kein Host-Schreibmount. 1 CPU, 512 MiB RAM einschließlich tmpfs, kein zusätzlicher Swap, 64 PIDs; /test-work 32 MiB, /enospc 4 MiB. Äußere Aufsicht 180 s, innerer Alarm 175 s, Childcapture 64 KiB einzeln/128 KiB zusammen, Paketausgabe 1 MiB; gespeicherte Operatorbelege lokal/remote jeweils auf 4 MiB begrenzt. Keine Builds/Pulls oder lokalen Produktläufe.

Finale Kontrollen: 21 Runner- und zehn Protokolltests, null Fehler/Fehlschläge. Frühere erwartete RED-Assertionfehler sind mit Originalstatus erhalten und werden nicht als Produktfehler oder grüne Produktproben umetikettiert. Die letzten beiden Regressionen sichern getrennte Fallbelege und negative Kennzeichnung fehlgeschlagener Fallvalidierung; validation_complete wird erst nach erfolgreicher Validierung gesetzt.

Produktbasis im eigenen Gitroot runtime/rw-storage-r2-20261017: HEAD d1eb34260179a499e2b0362bf609ce96957b78aa, Branch codex/rw-storage-r2-20261017. Jeder akzeptierte Lauf bindet 59 Pythonquellen plus Pilotentry vor/nach Ausführung, Inventar, fünf gestagte Harnessdateien, Operator-/Transporthash, Image und Laufprofil. Aktuelles Harnessbundle: 82c34a500a687111be3c797d8e7c1e9f66403807af078b0e4ae42a8a21abcbcd. Alle drei Pakete: Exit 0, kein OOM, eigener Container nachweislich entfernt. Vorschau-ID, Startzeit, RestartCount und laufender Zustand blieben identisch.

## Sicherung und Fortsetzung

[Unabhängige Bewertung](AURELIA_RW_STORAGE_R2_0_2026-10-17_REVIEW.json), [Laufindex](AURELIA_RW_STORAGE_R2_0_2026-10-17_INDEX.json) und [abschließende lokale Verifikation](AURELIA_RW_STORAGE_R2_0_2026-10-17_FINAL_CHECK.json) ergänzen die Rohbelege. Der neue Checkpoint checkpoints/RadiWorks-R2-0-20261017 sichert ausschließlich die benannten Werkzeuge und Dokumente mit erneut geprüften SHA-256-Werten. Kein Runtime-/Klientenbackup, externes Restore-Abbild, Gitcommit oder Push; das additive Harness ist weiterhin untracked in seiner unabhängigen Arbeitskopie.

Nächster Block R2-1: Eingangs-, Mengen-, Größen- und Spitzenbedarfsvertrag je Schreibpfad einschließlich Abschluss bereits angenommener Arbeit und größerer Altbestände. Numerisches Pilotprofil zur Betreiberentscheidung vorlegen; R2-Produktimplementierung und Aktivierung bleiben separate Freigaben. Host-/Stromausfallnachweise, fsync-/Journalfragen und vollständige Betriebsabnahme bleiben offen.

Lokale Tool-Timeouts hatten zuvor die Beobachtung und den Review unterbrochen. Nach Wiederaufnahme wurden die offenen Harnesspunkte korrigiert, 31 Kontrollen grün ausgeführt und die gespeicherten Kapazitäts-/Crashbelege unabhängig geprüft. Kein daraus abgeleiteter Fehler des Pilotservers. Der ältere HANDOFF bleibt als historischer Pausenstand erhalten.

Die [Auslastungsmessung beider Projekte](AURELIA_PILOT_AUSLASTUNG_2026-10-17.json) ist eine fünfsekündige Momentaufnahme, keine Lastabnahme. Weitere kostenpflichtige Cloud-Security-Scans erst nach vorheriger Zweck-/Kosten-/Guthabeninformation und Betreiberfreigabe; kein neuer Scan für R2-0, Guthaben nicht neu geprüft.

# Aurelia P3 – RadiMorphic: begrenzte Owner-/Start-/Lease-Charakterisierung

Stand 10.10.2026. Neun synthetische Fälle durch Luna6/max ausgeführt und durch die Leitung auf frischem Scratchpfad wiederholt; beide Ergebnisdetails identisch. Keine Produktquellen geändert, realen Scan-/Harmonisierungsprozesse gestartet oder Altklienten übernommen. Dieser Teilblock ergänzt den [Quellvertrag](AURELIA_P3_MORPHIC_QUELLVERTRAG_2026-10-10.md); er ersetzt keine Modulabnahme.

## Quelle und Nachweise

Geprüfte Quelle ausschließlich `C:/morphic_v1/.worktrees/operator-workbench-phase1`, HEAD `151e2bb0a69d49677a0b1e40e0bffd0f172d34c4`. Agent und Leitung erhoben HEAD/getrackten Zustand außerhalb des Harness rein lesend. Getrackte Änderungen: keine; untracked Dateien nicht inventarisiert. Elf gebundene Dateien vor/nach hashgleich, darunter geprüfte Methoden, HTTP-Quellkontext und gelesene Fixturequellen; dies ist keine vollständige Bindung aller Importabhängigkeiten. Hauptordner und Arbeitsstand bleiben unterschiedliche Quellen; kein führender Produktstand gewählt.

Werkzeug `checkpoints/Aurelia-P3-Morphic-20261010/p3_morphic_isolation_probe.py`. Drei Funktionsdefinitionen werden exakt aus AST geladen: Ownerbildung, Leaseablauf und Recovery-Dispatch. Scanmethoden und StartOperationStore stammen aus importierten Originalmodulen. Scan-Refresh, Persistenz-/Prozessautoritätswege sowie Harmonisierung-Reconciler/Eventwriter sind ausdrücklich ersetzt. Keine pytest-Suite und keine vorhandenen Testmodule importiert.

Privater Nachweispunkt: `runtime/aurelia-three-modules-20261009/reference-plan/p3-morphic-farben-20261010-142545Z`. Unter `morphic-worker-run/` liegen der erhaltene erste Fehler und zwei frische erfolgreiche Läufe: `morphic-worker-run-agentrepeat-20261010/probe-results.json` und `morphic-worker-run-rootrepeat-20261010/probe-results.json`. `MORPHIC_ROOT_BEFORE.json`/`MORPHIC_ROOT_VERIFY.json` binden eigenständig Git, elf Quellhashes, Harness und Ergebnisse. Agentenseitiger separater Receipt unter `checkpoints/Aurelia-P3-Morphic-20261010/P3_MORPHIC_SOURCE_BINDINGS_2026-10-10.json`.

Der erste Versuch scheiterte im Prüfwerkzeug: `os.fdopen` leitete einen freigegebenen Scratchdescriptor an `io.open` weiter, das ihn als pfadlosen Schreibzugriff abwies. Exceptionchain/Traceback bleiben erhalten; Korrektur ausschließlich im Harness, danach erfolgreiche frische Läufe. Kein Originalfehler daraus abgeleitet.

## Neun bestandene Charakterisierungen

| Schritt | Beobachtung in beiden Läufen | Aussagegrenze |
|---|---|---|
| M-C1 Ownerbildung | Gleiches synthetisches Tenant-/Operator-Tupel ergibt gleichen Ownerhash; anderer Tenant einen anderen. | Hash ist Zuordnung, keine Anmeldung oder Rechteprüfung. Andere Operator-/Leereingabevarianten hier nicht ausgeführt. |
| M-C2 Scan lesen | `get_owned` akzeptiert gleichen Owner und verweigert fremden Owner mit `ScanJobOwnershipError`. | Bereits beendeter RAM-Job; Refresh und I/O ersetzt. |
| M-C3 Scan stoppen | `stop_owned` akzeptiert gleichen Owner und verweigert fremden Owner. | Nur bereits beendeter RAM-Job: kein echter laufender Prozess gestoppt. |
| M-C4 Startclaim | Neuer Key/Owner erzeugt gespeicherten Pending-Claim, explizites Complete setzt ihn auf completed. | Nur sequenzieller Scratchstore; keine echte Scanausführung. |
| M-C5 Wiederholung | Gleicher Key/Owner/Request gibt completed-Record mit derselben Job-ID zurück. | Kein parallel konkurrierender Start oder Restart geprüft. |
| M-C6 Konflikt | Geänderte Requesthash bei gleichem Key/Owner führt zu `StartOperationConflictError`. | Andere Konflikt-/Abbruch-/Teilschreibfälle offen. |
| M-C7 Tenanttrennung | Derselbe Key unter dem zweiten Owner erzeugt eigenen Claim und andere Job-ID; erste Zuordnung bleibt erhalten. | Store-Scope geprüft; keine HTTP-/Abo-/Klientenrechte daraus ableiten. |
| M-C8 Heartbeat | Drei Sekunden alter Heartbeat ist bei 30s Lease frisch; 90s alter und fehlender Heartbeat gelten als abgelaufen. | Zeitzonen-, Format-, Grenzzeit- und Clockdriftfälle offen. |
| M-C9 Recovery-Dispatch | Frische/terminale Jobs übersprungen; zwei abgelaufene Jobs an Fake-Reconciler delegiert. Gründe `confirmed_process_tree_exit` und `lease_authority_unreadable` an Fake-Eventwriter gegeben. | Kein echter Prozessautoritätsnachweis, kein persistiertes Ereignis, kein Workerrestart. |

Im Original erfolgt Scan-Refresh vor der Ownerprüfung; der Harness ersetzt diesen Schritt. Die Proben belegen somit keine seiteneffektfreien Fremdzugriffe vor der Ablehnung. Ebenso ist der Recovery-Dispatcher keine Prüfung des eigentlichen Reconciler-/Prozessbaumverhaltens.

## Isolation, Review und Grenzen

Pro Lauf neun bestandene Fälle, null Treffer der überwachten Prozess-/Netz-/Thread-Starts und null abgewiesene Schreibversuche außerhalb Scratch. Vierzig protokollierte Scratch-Schreibaufrufe sind keine vierzig Dateien. Diese Nullzählungen belegen ausschließlich die beobachteten gepatchten APIs; keine allgemeine Sicherheits-/Prozesssandbox.

Bestehende Pfadkomponenten wurden vor Einrichtung auf Reparsepunkte geprüft, danach Schreibpfade lexikalisch begrenzt. Keine echten Junction-/Race-Negativtests; `_thread`/`ctypes` und sämtliche Drittanbieterpfade sind nicht allgemein gesperrt. Der ursprüngliche Windows-Dateipublish wurde zusätzlich an den zwei Scratchpfaden gebunden. Keine vollständige Importabhängigkeitsprüfung, kein Realnetz-/CLI-/OS-Konkurrenz-/DB-/Auth-/API-/UI-/Restoretest. Fehlende Belege bleiben offen.

Astra6/medium prüfte Quellmethoden, Harness, zwei Ergebnisse und Hashbindungen unabhängig lesend: kein materieller Fehler im beschriebenen neunfachen Teilumfang. Die Grenzen zu Refresh vor Ownerprüfung, terminalem Stop, Fake-Reconciliation und nicht umfassender Isolation sind übernommen. Abschließender Berichtskonsistenzreview ebenfalls ohne materielle Restbefunde.

## Weitere P3-/P4-Arbeit

Offen: administrativer Katalog mit Rechten/Kontext/Publish/Rollback; nachgelagerter CLI-Writer und Artefakt-/Reportkette; wirkliche Prozessautorität/Stop/Lease/Restart/Restore; Auth-/Tenant-/Operator-/Klientenrechte samt Shared-Root-Negativen. Für P4 Writerhoheit, Ownerkontext, dauerhafte Startidentität, Zustandsrevision, Lease/Autorität, Artefakteigentum und persistierte Ereignisse getrennt erfassen. Keine Datenbanktechnik oder Produktreparatur beschlossen.

P0-Linuxzugang/Kaltstart/Stackbudget bleibt offen. P1/P2 nicht gestartet; P3 insgesamt offen. Vollständige siebenmodulige Matrix vor P5 Betreiberentscheidung, danach normative Modul_Templates/Aurelia-Kern und P6–P8/S4.8. RadiWorks-Wartung bleibt gemäß Plan vorgemerkt; laufende Instanzen und Governors unberührt. Dieser Sicherungspunkt ist keine neue F:-Gesamtsicherung.

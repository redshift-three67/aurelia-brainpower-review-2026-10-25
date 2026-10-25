# RadiWorks R1: isolierter Linux-Speicherprüfstand

> **For agentic workers:** Use superpowers:executing-plans task-by-task; bounded independent implementation/review follows the operator's route B. Steps use checkboxes for evidence tracking.

**Goal:** Die am 17.10.2026 ausdrücklich freigegebene Stufe R1 mit synthetischen Daten ausführen und beobachtete Fehlergrenzen dokumentieren; keine Schutzaktivierung.

**Architecture:** Hashgebundene Produktquellen bleiben unverändert und read-only. Additive Prüftreiber arbeiten ausschließlich in einem netzlosen, begrenzten Container des Aurelia-Projektnutzers; dessen Supervisor hält die tmpfs-Daten bei App-Prozessneustarts. Jeder Testblock besitzt eigene Ergebnisse; unerwartete Inkonsistenz stoppt den betroffenen Block und verhindert eine pauschale R1-Abnahme.

**Tech Stack:** Python-Standardbibliothek für Treiber/Fehlerinjektion, vorhandenes Offline-Python-Image mit RadiWorks-Abhängigkeiten, rootloses Docker auf vm2565/IPv4-SSH. Kein lokaler Produktimport/-test, kein Build/Pull, kein neuer Cloud-Scan.

**Freigabe:** Betreiber: „Ja ich gebe R1 frei. Danke.“ Maßgeblich ist [der Entwurf](../specs/2026-10-17-radiworks-speicherschutz-entwurf.md), nicht die spätere Stufe R2. Quellen-HEAD `d1eb34260179a499e2b0362bf609ce96957b78aa`, Image `sha256:121b7b271d5709c44c1e8ac2a62d6ef21acaed6dcd009514cdcbb6caee664215`.

## 1. Bindung und isolierte Arbeitskopie

- [x] Schriftliche R1-Freigabe erhalten; noch keine R1-Ausführung daraus behaupten.
- [x] Exakten unabhängigen Gitroot, HEAD und saubere versionierte Produktdateien bestätigen; additive Arbeitskopie `runtime/rw-storage-r1-20261017` auf `codex/rw-storage-r1-20261017` anlegen. Keine Branchumschaltung im bestehenden Kandidaten, keine Änderungen im umgebenden Benutzerprofil-Repository.
- [x] Linux rein lesend prüfen: Benutzer/Host/IPv4, vorhandenes Image, laufende Vorschau und ihre Quellmounts. Die 59 Inventarhashes und den Pilotentry vor/nach den Paketen gegen den Kandidaten vergleichen. Drift stoppt die Ausführung.

```python
assert observed_head == 'd1eb34260179a499e2b0362bf609ce96957b78aa'
assert observed_hashes == inventory_hashes
assert image_id == 'sha256:121b7b271d5709c44c1e8ac2a62d6ef21acaed6dcd009514cdcbb6caee664215'
```

## 2. Additive Treiber und Begrenzungsnachweis

Dateien ausschließlich in der neuen Arbeitskopie: `pilot/storage_r1/probe.py` (Produktbeobachtungen), `pilot/storage_r1/runner.py` (Begrenzungsprüfungen), `pilot/storage_r1/operator_local.py` (IPv4-Transport, Containeraufsicht und Belege), `pilot/storage_r1/test_runner.py` (negative/positive Begrenzungsprüfungen). Root verantwortet Runner/Transport, begrenzter Luna-Worker darf ausschließlich Probe und deren synthetische Prüffälle bearbeiten; keine alleinige Aktivierungsentscheidung.

- [x] Runner-Sicherheitsassertionen vor Implementierung schreiben und auf Linux mit absichtlich fehlendem Runner/fehlenden Schutzfunktionen rot sehen. Negative Fälle: beschreibbarer Quellen-/Rootmount, Netzwerk, falsches Image, fremder Mount, fehlende Limits, Ausgabeüberschreitung, Timeout, OOM, fehlerhafter Ergebnisstatus, Hashdrift.
- [x] Runner minimal implementieren: exakt ein eigener Container mit Labels/ID; `--read-only --network none --cpus 1 --memory 512m --memory-swap 512m --pids-limit 64 --cap-drop ALL --security-opt no-new-privileges --log-driver none`; `/test-work` tmpfs32MiB und `/enospc` tmpfs4MiB. Quellen und Testtools read-only. Pythonbytecode aus, HOME/TMPDIR/SQLITE_TMPDIR/XDG_CACHE_HOME unter `/test-work`.
- [x] Vor Teststart Docker-Inspect des erstellten Containers gegen diese Vorgaben prüfen. Paketlaufzeit180s, stdout+stderr zusammen1MiB, externe Ergebnisdateien zusammen8MiB; Grenzverletzung als fehlgeschlagen/unvollständig erfassen und nur eigenen Container beenden. Kein unbeschränktes `communicate()` oder unbegrenztes Logfile.
- [x] Linux-Runnerprüfungen grün, anschließend unabhängiger Review vor tatsächlicher Fehlerprobe. Ausführungsbefehl im neuen Prüfverzeichnis: `python -m unittest discover -s pilot/storage_r1 -p test_runner.py -v`. Erwartung: alle benannten Grenztests erfolgreich; keine Produktabnahme daraus ableiten.

## 3. Produktproben in getrennten Paketen

- [x] **Paket A:** atomisches JSON und Mehrdatei-Recovery: zwei kleine Dokumentgrößen, vollständiger/partieller Write, Flush, Close, Datei-fsync, Verzeichnis-fsync, Replace. Alt-/Neuzustand und Marker exakt prüfen; geschluckte Verzeichnis-fsync-OSError ausdrücklich als Dauerhaftigkeitsgrenze ausweisen.
- [x] Echte ENOSPC-Probe nur durch Füllen des4MiB-Test-tmpfs; Fehler muss `errno.ENOSPC` sein. Hostfreiraum, OOM oder generischer Testabbruch ersetzen diesen Nachweis nicht. Eigene synthetische Füllfiles danach entfernen und Freiraum prüfen.
- [x] **Paket B:** Bildneuaufnahme/Deduplikation und Entropiejournal: tatsächliche Größen/Dateifolge, Append-/Commitfehler, keine stillen neuen Draws oder Erfolgsbelege bei ungültiger Persistenz. Zwei begrenzte Bild-/Journaldimensionen; keine obere Nutzergrenze daraus ableiten.
- [x] **Paket C:** persönliche und Vergleichs-SQLite-Stores: Daten-/Journal-/WAL-/SHM-Dateien beobachten, Transaktionsfehler und App-Prozessabbruch gegen denselben gespeicherten Zustand; Elternsupervisor bleibt aktiv. Keine neue leere tmpfs als Recovery-Nachweis.
- [x] **Paket D:** höchstens zwei konkurrierende synthetische Schreiber; atomare Zustände und Recoverykonflikte beobachten. Jede unerwartete Inkonsistenz stoppt dieses Paket. Keine automatische Reparatur oder Fortführung mit geänderten Erfolgskriterien.

Fehlerinjektion bleibt im Testprozess, nicht in Produktdateien. Pro Probe Ergebnisstruktur mindestens:

```python
result = {'case': case_name, 'fault': fault_name,
          'observed_errno': observed_errno, 'old_valid': old_valid,
          'new_valid': new_valid, 'recovery_required': recovery_required,
          'consistency_ok': consistency_ok, 'durability_proven': False}
assert result['consistency_ok'], result['case']
```

Messungen sind Beobachtungen. Peakrechnung, begrenzte Eingänge und SQLite-Konfiguration bleiben R2-Voraussetzung; weder Prozessneustart noch tmpfs beweisen Host-/Containerneustart- oder Stromausfallfestigkeit.

## 4. Abschluss und Wiederaufnahme

- [x] Quellenhashes, Vorschaucontainer-Identität/-Status und eigene Containerbereinigung bestätigen; keine produktiven Laufzeitdateien lesen oder schreiben.
- [x] Profil, Skripthashes, tatsächliche Befehle, Inspect, Rückgabecodes, Laufzeiten, Fehlerart, Messwerte und Abbruch-/Aufräumstatus unter `docs/verification/AURELIA_RW_STORAGE_R1_2026-10-17*` begrenzt sichern und zurücklesen.
- [x] Nur bestandene Teilprüfungen als solche ausweisen, offene Pakete/Fehler konkret benennen. `docs/SERVER_AKTUELL.md` in-place aktualisieren. Kein Security-Befundabschluss, R2-Rollout, Windows-/Templates-/Aureliaübernahme oder GitHub-Push aus R1 ableiten.

## Steuerungsstörung vor R1

Bei Beginn reagierten lokale Befehlsstarts stark verzögert; ein Runner-Start scheiterte mit `timed out after 15000ms connecting runner pipe-in`, ein zusätzlicher Node-Leseversuch mit Kernel-Timeout. Noch kein Linux-Test gestartet. Vor Durchführung muss ein verlässlicher begrenzter SSH-/Steuerungsweg bestätigt werden. Diese Infrastrukturstörung ist kein RadiWorks-Befund und kein Nachweis eines Serverfehlers.

## Verifizierter Zwischenstand 17.10.2026

IPv4-Steuerungsweg, feste Image-/Quellbindung und Containergrenzen inzwischen bestätigt. Der erste RED-Versuch erreichte wegen nicht lesbarer Harness-Rechte keine Assertions; Ursache waren UID65532 im Image gegenüber hostseitig0700/0600. Nur eigenes Staging auf0755/0444 korrigiert; Parentverzeichnisse bleiben0700, Mount bleibt read-only. Die nach erfolgreichem `rm -f` fälschlich negativ bewertete Abwesenheitsmeldung wurde durch exakte CID-/Statusprüfung mit schreibweisenunabhängiger Meldung korrigiert; frische Diagnose bestätigte keine übrigen R1-Container.

Gültiger [RED-Nachweis](../../verification/AURELIA_RW_STORAGE_R1_2026-10-17_red_edb720a2a52f.json):12 Tests mit29 erwarteten fehlenden Funktionsassertionen, keine Import-/Testfehler. [GREEN](../../verification/AURELIA_RW_STORAGE_R1_2026-10-17_controls_c590b6c7eb0e.json):12 Tests bestanden. Beide Male tatsächliche cgroup-/tmpfs-Limits bestätigt, Quellen59+Pilotentry gleich, eigene Container entfernt, bestehende Vorschau identisch/aktiv. Noch kein Produktpaket daraus ableiten. Astra-Review verlangte vor C eine eigene begrenzte Kindausgabe und die korrekte Benennung von A als Wiederaufnahme nach Ausnahme im selben Prozess; diese Korrekturen bleiben Voraussetzung für den Produktstart.

## Abschluss

Alle oben benannten R1-Pakete mit ihren begrenzten Kriterien ausgeführt; keine R2-Freigabe. Erweiterte Steuerung15/15, Produktproben27/27. Nach Fehler im C-Fixture vier Zugriffe auf den tatsächlichen Storevertrag korrigiert; kein Produktpatch und kein geändertes Erfolgskriterium. B nur nach Nachweistext-Präzisierung erneut ausgeführt. [Abschlussbericht](../../verification/AURELIA_RW_STORAGE_R1_2026-10-17.md) und [Laufindex](../../verification/AURELIA_RW_STORAGE_R1_2026-10-17_INDEX.json) sind maßgeblich für Messwerte, Toolversionen und Grenzen. SQLite-Proxyfehler, Prozesswechsel bereits gespeicherter running-Aufträge und Endzustände zweier Threads sind keine weitergehenden Dauerhaftigkeits-/I/O-/Parallelitätsgarantien.

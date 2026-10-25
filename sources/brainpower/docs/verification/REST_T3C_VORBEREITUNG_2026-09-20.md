# T3c: gebündelte Vorbereitung, getrennte Wirkungsnachweise

## Speicherlimit: Ubuntu-Nachweis abgeschlossen

Genehmigten Lauf `852c7cd9d47e412888bf3732a5236be4` einmalig ausgeführt, Berichtzeit 2026-09-20T14:32:35.554227+00:00. Vollständigen Export per SSH gelesen, lokal gesichert und maschinell validiert.

- `memory_verified`; systemd-Endebeleg `oom-kill`, ExitCode=2, ExitStatus=9 (SIGKILL), passende Boot-/Invocation-/Laufidentität, Prozessende und entfernte cgroup.
- Unit-Werte MemoryMax=134217728 Byte (128 MiB), MemorySwapMax=0 bestätigt. `limits=null` bedeutet: keine noch vorhandenen cgroup-Limitdateien am Endzeitpunkt; kein persistenter memory.events-Zähler behauptet.
- Journal `failed`, active=0: erwarteter Fehlschlag des Testworkers, während der Schutztest erfolgreich war.
- `package_removed`, `staging_absent`, `unit_retired`, `services_unchanged` jeweils true.
- Unabhängige SSH-Nachprüfung: Test-Unit not-found/inactive, MainPID=0; SSH, wg-admin und GDM active.
- Export `artifacts/t3memory20-report.json`, SHA256 `c6d966f327f2e5d16c7cf0e9cf981087bd4ed83a1cf520c102667ea0a7ecd256`, identisch mit Server. Rootquellbericht-SHA256 laut Export `95f1009bbdcb39f9a20fe9390def4df4ffcb473f70d9316f74edefa0ad77bd4c`.

Keine Wiederholung. Dieser Nachweis gilt für den synthetischen Unit-Test; keine vollständige T3- oder Produktfreigabe. Controllerverlust und vollständiger korrigierter Abbruchlauf bleiben offen. Nachstehende Artefakt-/Vorbereitungsangaben dokumentieren die Vorbereitung dieses inzwischen ausgeführten Laufs.

## Stand und Reihenfolge

| Teil | Stand | Nächster Schritt |
| --- | --- | --- |
| Normalfall | Auf Ubuntu abgeschlossen | Historischen Nachweis erhalten |
| Prozessgruppenabbruch | Beide Prozesse beendet; ursprünglicher Controllerabschluss blockiert, Recovery/Rücknahme abgeschlossen | Neuer vollständiger Lauf des korrigierten Runners gesondert abnehmen |
| Linux-TLS (T3d) | 47 Tests auf Ubuntu bestanden | Erledigt, kein erneuter Lauf |
| Speicherlimit | Auf Ubuntu geprüft, OOM-Ende und Rücknahme bestätigt | Erledigt, Beleg erhalten |
| Controllerverlust | Abgrenzung unten festgelegt, Linux-Ausführung noch nicht implementiert | Nach Speichernachweis separate Vorbereitung und Freigabe |

Gemeinsame Infrastruktur wird weiterverwendet. Fehlernachweise bleiben getrennt, damit ein erwarteter Workerfehler nicht als erfolgreicher Produktlauf oder als vollständige T3-Abnahme erscheint.

## Konkreter Speicherlimit-Test

Neue Kennung `852c7cd9d47e412888bf3732a5236be4`; genau ein Start im vorhandenen Modus memory. Unveränderter Worker fordert höchstens 160 MiB Nutzblöcke an und prüft vorab seine cgroup-Grenzen. MemoryMax=128 MiB, Swap=0, Tasks=16, CPU=25 %, RuntimeMaxSec=20 s, Stopfrist=2 s; DynamicUser und vorhandene Unit-Härtung. Helfer verweigert Start bei weniger als 2 GiB MemAvailable. Keine Lastprobe gegen den Gesamtserver, kein Neustart, keine Produktdaten.

Erfolgsnachweis erfordert passende Boot-/Invocation-/Laufidentität, Ende aller eigenen Prozesse, systemd Result=oom-kill, SIGKILL, gespeicherte MemoryMax-/Swap-Werte und unveränderte Fremddienste. Einfacher MemoryError, Exit 2, Timeout oder fehlender Beleg genügen nicht. Beobachteter OOM plus konfigurierte Grenze ist ein Unit-bezogener Nachweis; ein persistenter memory.events-Zähler wird bei bereits entfernter cgroup nicht behauptet.

Endebeleg wird vor Journalabschluss und Rücknahme dauerhaft aufgezeichnet. Journal des Workers wird failed, Prüfbericht nur bei vollständigem Abschluss memory_verified. Anschließend genau eigene fehlgeschlagene Unit zurücksetzen, Endzustand neu prüfen und nur die zwei geprüften Stagingdateien entfernen. Fehler verhindert automatische Wiederholung.

Schneller Workerabschluss: leerer ControlGroup-Wert darf nur mit unabhängigem terminalem Endebeleg und nachgewiesen entfernter erwarteter cgroup gebunden werden; kein freies Raten anhand einer PID. Andere Identitätsprüfungen bleiben erhalten.

## Lokale Verifikation und ausführbare Artefakte

- Zehn zusätzliche Tests für OOM-Abgrenzung, falsche Endbelege, Dienstabweichungen, Belegschreibfehler, Rücknahmefehler, Konfigurationsbindung und schnellen Abschluss.
- Gesamte lokale Suite: **195 Tests bestanden**, 0 Fehler/Skips, 39,641 Sekunden.
- Archiv aus neun Modulen gebaut, Syntax und Quellbytes geprüft; Helfer syntaktisch geprüft.
- `artifacts/rest-t3-memory-20260920.pyz`: SHA256 `8703c0470b7d13c502f9d4875d25ebae94df4f33678a259934fb5df042d7f05d`.
- `artifacts/server-t3-memory-20260920.py`: SHA256 `ec072e428be978b86db03dde53c2d32c470327df614fd90570ae8dbbe6ae7e52`.
- Betreiberfreigabe erteilt; nach vorheriger Abwesenheitsprüfung nach `/home/klaus999/t3memory20.pyz` und `/home/klaus999/bpt3memory20` übertragen. Beide Server-SHA256 identisch mit oben. Root-KVM-Aktion `python3 /home/klaus999/bpt3memory20` inzwischen erledigt. Ausgabeexport `/home/klaus999/t3memory20-report.json` geprüft und gesichert; nicht wiederholen.

## Abgrenzung Controllerverlust

Nur einen eigens gestarteten synthetischen Controllerprozess nach dauerhaft gespeichertem Workerbeleg gezielt beenden; nie Governor, SSH, Desktop oder den Server. Der eigene Worker bleibt durch systemd begrenzt. Ein neuer Controller darf erst nach frischer Endbeobachtung den offenen Lauf als released_unknown freigeben; kein Worker-Replay. Beobachtung vor Ende muss blockieren, RuntimeMaxSec ist nur zusätzlicher Wächter. Eigene Dateien, Unit und Dienste anschließend prüfen. Konkreter Helfer und Linux-Freigabe stehen noch aus; lokale Recoverytests ersetzen diesen Nachweis nicht.

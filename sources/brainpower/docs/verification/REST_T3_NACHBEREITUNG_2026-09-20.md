# T3: Nachbereitung des vorhandenen Abbruchtests

Status: auf Ubuntu ausgeführt und anhand des vollständigen Berichts sowie frischer SSH-Abfrage bestätigt. Berichtzeit: 2026-09-20T12:30:55.534051+00:00.

## Tatsächlicher Abschluss

- `cleanup_verified`, `journal_released=true`, kein aktiver Journaleintrag. Fachlicher Ausgang bleibt `released_unknown`, ursprünglicher Fehlerbericht unverändert.
- `package_removed=true`, `staging_absent=true`, `unit_retired=true`.
- Unabhängige SSH-Nachprüfung: Test-Unit `LoadState=not-found`, `ActiveState=inactive`, `MainPID=0`; SSH, wg-admin und GDM weiterhin active.
- Neuer Endebeleg bindet ursprüngliche Boot-/Invocation-ID, entfernte cgroup und timeout/SIGKILL. Kein erneuter Worker gestartet.
- Vollständiger Export lokal: `artifacts/t3cleanup20-report.json`, SHA256 `b0647d924275077c0eba7f50a835d9bb1911c87a45160418fa708459010433c8`. Identität, Status, Rücknahmeflags und Dienstvergleich maschinell geprüft.

Damit ist die Nachbereitung dieses Laufs abgeschlossen. T3 insgesamt bleibt offen: insbesondere Speicherlimit-Wirkung, Controllerverlust und Linux-TLS. Die fehlerfreie Ausführung eines vollständigen Abbruchlaufs mit korrigiertem Runner ist hierdurch nicht nachgewiesen.

## Vorbereitung (historisch)

Ziel ausschließlich Lauf `fcc704a500994914980489fbb99afda6`. Frische SSH-Prüfung bestätigt dieselbe InvocationID, MainPID=0, failed/timeout. Root-SSH per `sudo -n` ist nicht verfügbar (Passwort erforderlich).

## Fest gebundener Ablauf

1. Geschützte Pfade, ursprünglichen Rootbericht und Paket-SHA256 prüfen. Neue exklusive Rootinstallation verhindert versehentliche Wiederholung.
2. Bestehende Controller-Dateisperre halten. Aktiven Journaleintrag vor Wiederöffnung lesend auf Lauf, Manifest und vollständige Identität prüfen.
3. Gestagtes Paket und frischen Endebeleg prüfen. Wiederöffnung markiert den offenen alten Lauf als unknown.
4. Eigenen neuen Bericht dauerhaft schreiben; anschließend nur bei verifiziertem timeout/SIGKILL-Ende und entfernter cgroup `released_unknown` buchen. Der ursprüngliche Test bleibt historisch blocked.
5. Zweiten dauerhaften Bericht vor Rücknahme schreiben. Genau die gebundene Test-Unit zurücksetzen, strikten Endzustand prüfen und nur die zwei manifestgebundenen Testdateien sowie deren leeres Verzeichnis entfernen. Keine rekursive Löschung.
6. SSH, wg-admin und GDM vergleichen; neuen Abschlussbericht und lesbaren synthetischen Export erzeugen. Alte Berichte, Journal, Sperrdatei und installierte Belegpakete bleiben erhalten.

Keine Worker-Neuausführung, kein Stop laufender Dienste, keine Änderung an Governor, Firewall oder Produktfreigaben. Kein Reboot. Bei unklarer Identität, Bootwechsel oder fehlendem Beleg Halt. Bei Fehler nach Journalfreigabe bleibt der unbekannte fachliche Ausgang bestehen; keine Erfolgsumdeutung, keine automatische Wiederholung.

## Verifikation und Artefakte

- Fünf neue Tests: kein Replay, falsche Bindung, fehlender Endebeleg, fehlgeschlagenes Belegschreiben und fehlgeschlagene Rücknahme.
- `python -B -m unittest discover -s tests -p 'test_contract*.py' -q`: **182 Tests bestanden**, 0 Fehler/Skips, 40,773 Sekunden.
- Helfer per AST syntaktisch geprüft. Bibliotheksarchiv beim Bau byteweise mit neun lokalen Modulen verglichen.
- `artifacts/rest-t3-cleanup-20260920.pyz`: SHA256 `3f0add3baa237e3bc0e430a963c5190c6143bc4fe32ce827209efbf1bdcff4e5`.
- `artifacts/server-t3-cleanup-20260920.py`: SHA256 `7ff288af7e0e01a11d85ad4bab55b77d828dd1a901993c1e31b61d44af791fd9`.
- Beide Dateien per SSH übertragen; beide SHA256 auf Ubuntu identisch.

Die damalige Root-KVM-Aktion `python3 /home/klaus999/bpt3clean20` ist erledigt. Nicht wiederholen. Export ausgewertet und lokal gesichert; Ergebnisse oben.

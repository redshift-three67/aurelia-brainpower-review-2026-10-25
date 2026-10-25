# T3 – drei Lebenszyklus-Restpunkte lokal abgeschlossen

20.09.2026: **166 Tests bestanden, 0 Fehler, 0 Skips, 39,584 Sekunden**. Sieben neue Tests plus angepasste Fixtures; keine echte Ubuntu-Ausführung. Neue OS-Beobachtungen sind synthetisch. Windows-Datei-/Journaltests bleiben echte lokale Prüfungen.

```powershell
& 'C:/Users/Hubert111/AppData/Local/Programs/Python/Python312/python.exe' -B -m unittest discover -s tests -p 'test_contract*.py' -q
```

| Restpunkt | Umsetzung | Nachweisgrenze |
|---|---|---|
| Entfernte cgroup | Nur bei FileNotFound der Limitdateien alternativen Endepfad prüfen. Passende Invocation/Boot/Unit-ID, stabile terminale Unit, MainPID 0, gültiger Exitcode und positiver monotoner Exitzeitpunkt erforderlich. Verzeichnis zweimal unabhängig als abwesend bestätigen; reale Prüfung verlangt eingehängtes cgroup v2 und vorhandenen Elternpfad. | Fehlende Einzeldatei, wiederkehrende cgroup, fehlender Exitbeleg oder widersprüchliche Identität sperren. Limits bleiben null; keine nachträgliche Behauptung beobachteter Ressourcenlimits. |
| Nachbeobachtung | Gemeinsames monotones 5-s-Budget; 100-ms-Abstand, keine neue Ausführung. Restbudget begrenzt die systemctl-Abfragen. Identitätswechsel, unbekannter Zustand und nach Frist eintreffender Erfolg werden abgewiesen. | Keine harte Betriebssystem-Echtzeitgarantie; lokale Dateisystemlesung ist kein gewaltsam abbrechbarer Prozess. Testuhr belegt Logik, Linux-Timing bleibt offen. |
| Unit-Rücknahme | Nach erneutem passenden ended-Befund genau eigene Einheit stoppen. Danach Id/LoadState/Invocation/ActiveState/MainPID, gleiche Bootkennung und fehlende cgroup prüfen. Erst dann bekannte Paketdateien entfernen. | Unverifizierter Nachzustand bewahrt Paketdateien. Nicht geladene Einheit oder identisch gebundene inaktive Einheit zulässig; abweichende Identität bleibt blockiert. |
| Fremddienste | Zusätzlicher Zustandsvergleich nach Unit-/Paket-Rücknahme. Spätere Abweichung ergibt blocked, auch wenn Paket bereits entfernt ist. | Vergleich von SSH/wg-admin/GDM ActiveState; kein vollständiger Hostaudit. |

RED/GREEN: neue Varianten zunächst ohne Unterstützung fehlgeschlagen. Zusätzlicher Drift-Test zeigte fehlenden Fremddienstvergleich nach Rücknahme; ergänzt. Gesamtlauf nach letzter Änderung erfolgreich.

## Neues ausführbares Artefakt

`artifacts/rest-t3-runner-20260920-v2.pyz` – ZIP-Integrität und Bytegleichheit aller acht Module gegen aktuellen Quellstand geprüft. Windows-Einstiegsgate im gebauten Artefakt geprüft: Exit 2 / entry_unverified, keine privilegierte Aktion. Altes Artefakt bleibt historisch; nicht für den nächsten Test verwenden.

- Runner-SHA256: `6a4d59d48fb8aeb63ab499fafaadaddb72de2010836500a45320490c98d41669`
- Workerpaket unverändert: `artifacts/rest-t3b-20260920/`
- Worker-Manifest-SHA256: `5379aa7b6d45a25a93ba5a6b1a507e8281c3c99b0f4b555c562b7fffcd7b42f1`

## Konkreter erster Ubuntu-Test zur Betreiberfreigabe

Umfang: genau ein synthetischer **normal**-Lauf. Kein memory-/ignore_term-Modus, kein Serverneustart, keine Firewall-/SSH-/Produktänderung. Daten ausschließlich eigene Testmetadaten. Die Ausführung erzeugt eine temporäre systemd-Einheit mit 128 MiB RAM, 0 Swap, 16 Tasks, 25 % CPU, 20 s maximaler Laufzeit und 2 s Stopfrist. Controllerbeobachtung zusätzlich begrenzt. Bestehende SSH/wg-admin/GDM-Zustände vorher/nachher vergleichen.

Vorbereitung nach Freigabe: zunächst nur überprüfte Dateien übertragen; Root-Bereitstellung nach `/opt/aurelia-t3/runner.pyz` und `/opt/aurelia-t3/package` mit Rootbesitz, nicht fremdschreibbaren Elternpfaden und externem Hashabgleich. Vorhandene unbekannte Zielinhalte nicht überschreiben. Kein privates Zertifikat oder Zugangsschlüssel im Paket.

Vorgesehene einmalige Laufkennung: `0dccd173321a46d58b737b93b27fed7a`.

```text
/usr/bin/python3 -I /opt/aurelia-t3/runner.pyz normal 0dccd173321a46d58b737b93b27fed7a 5379aa7b6d45a25a93ba5a6b1a507e8281c3c99b0f4b555c562b7fffcd7b42f1
```

Test-Staging `/var/tmp/aurelia-t3/<run-id>`; dauerhaftes Testjournal, Sperrdatei und Bericht unter `/var/tmp/aurelia-t3-control`. Root-Installationspaket unter /opt bleibt als geprüfte Testquelle erhalten. Nur die eigene nachgewiesen beendete Unit und bekannte Stagingdateien werden zurückgenommen. Bei Fehler/Unsicherheit Bericht und Restzustand bewahren, keinen automatischen Start wiederholen. Report auswerten, bevor irgendein weiterer Test folgt. Kein ungeprüfter Re-Run mit neuer Laufkennung zum Umgehen eines offenen Journaleintrags.

Das Paket ist für diese begrenzte **erste Laufzeitprüfung vorbereitet**, nicht bereits auf Ubuntu abgenommen. Abweichende systemd-Feldausgabe oder Lebenszykluszustände können weiterhin zu blocked führen und werden dann anhand konkreter Belege untersucht. CPU-/OOM-/Prozessbaum-/Crashprüfungen sowie T3d bleiben gesondert offen.

Keine Serveränderung oder neue Sicherung in diesem Arbeitsschritt. Nächste Aktion benötigt die im T3-Plan vorgesehene konkrete Betreiberfreigabe für diesen Lauf.

| Quelle | SHA256 |
|---|---|
| contract_lab/linux_observer.py | 13d824a9c103053ddce6f8f0aa2bfbdc6f8f71b64657adb3361c880f9d2f889c |
| contract_lab/linux_backend.py | a750123b18e1293f174ac1a3c606e6bc9073a5f00038ee13a87557cb631ef640 |
| contract_lab/linux_runner.py | 8a3bfa783b54b36e05c72bcf38d5dc53733c183e248b6db02a98c569fc6a1efa |

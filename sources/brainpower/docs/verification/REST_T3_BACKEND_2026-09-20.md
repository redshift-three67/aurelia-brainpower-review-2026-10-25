# T3 – Linux-Backend und gezielte Paketentfernung lokal geprüft

20.09.2026: **149 Tests bestanden, 0 Fehler, 0 Skips, 39,241 Sekunden**. 13 neue Backendtests. Prüfung unter Windows mit ausdrücklich injizierten Linux-/Root-/systemd-Testantworten; lokale Paketdateien werden tatsächlich angelegt und gezielt entfernt. Kein Linux-Rechte- oder systemd-Laufzeitnachweis.

```powershell
& 'C:/Users/Hubert111/AppData/Local/Programs/Python/Python312/python.exe' -B -m unittest discover -s tests -p 'test_contract*.py' -q
```

| Baustein | Implementiertes / geprüftes Verhalten |
|---|---|
| Umgebung | Standardpfad verweigert Nicht-Linux und Nicht-root. Python exakt 3.12.3 und systemd-Hauptversion 255 erforderlich; leere/abweichende Version sperrt. |
| Einheit | Vor Staging und unmittelbar vor Start LoadState=not-found für exakt eigene Laufkennung verlangen. Bestehende Einheit bleibt unverändert. |
| Staging | Fester Zielbereich /var/tmp/aurelia-t3/<run-id>; exklusive neue Unterablage. Bekannte Dateien kopieren, fsync, explizit 0644 für spätere DynamicUser-Lesbarkeit. Rootbesitz, keine Gruppen-/Fremdschreibrechte, keine Symlinks oder mehrfach verlinkten Paketdateien. |
| Paketbindung | Vor und nach Kopie sowie vor Start Hashprüfung; fremde Dateien, Drift und vorhandenes Ziel sperren. Fehler lassen Zwischenbelege bestehen, keine automatische rekursive Bereinigung. |
| Start | Nur eine der drei exakt generierten systemd-run-Argumentlisten. Höchstens ein Startversuch pro Backendinstanz, auch bei Timeout. Eigene Invocation-/Boot-/cgroup-Identität wird gelesen und durch Beobachter geprüft. |
| Stop | Identität aus frischer Beobachtung kann auch nach Controllerwiederaufnahme gebunden werden. Stop nur für exakt passende laufende Instanz; keine Wildcards oder freien Shellbefehle. |
| Paketentfernung | Erneute geschützte Pfad-/Paketprüfung und passender Endebefund erforderlich. Nur linux_worker.py, manifest.json und dann das leere eigene Verzeichnis entfernen. Zusätzliche Datei verhindert jede Löschung. Quellpaket bleibt bestehen. |

RED/GREEN: fehlendes Backend zuerst nachgewiesen. Weitere Negativtests zeigten leere Runtimeausgabe, fehlende Recovery-Identitätsbindung und möglichen wiederholten Start nach Timeout. Diese Fälle behoben. Zusätzlicher Test zur expliziten Lesbarkeit bei restriktiver umask zunächst rot, anschließend ergänzt. Vollsuite nach letzter Änderung erfolgreich.

## Noch vor der Serverfreigabe

Das Backend ist implementiert, aber das **vollständige aufrufbare Controllerpaket fehlt noch**. Nächster Schritt ist der feste Einstiegspunkt mit geschütztem Journal-/Sperrpfad, Berichtsausgabe, Bindung an Paketanker und klarer Normalende-/Recoverybehandlung. Controller, Backend und Beobachter müssen dabei zusammen in Integrationstests geprüft werden. Ein Workerpaket allein reicht nicht für die Serverfreigabe.

Die Paketentfernung beendet oder entlädt keine systemd-Einheit und löscht kein Journal. Fremddienst-Vorher-/Nachhervergleich, Berichtssicherung und Unit-Lebenszyklusabschluss bleiben Bestandteil des Runners. Vollständige Crash-/OOM-/CPU-/Kindprozessprüfungen bleiben T3c; Linux-Transportwiederholung bleibt T3d.

Bekannte Grenzen: fehlende cgroup ergibt weiterhin keine Endefreigabe; Sicherheitsprüfungen sind keine atomare Sperre gegen fremde Root-Aktionen. Teilweise entfernte Dateien bei einem I/O-Fehler werden nicht als erfolgreiche Rücknahme ausgegeben. Die lokale Testumleitung von Root-/Rechteprüfungen darf nicht als Serverprüfung dargestellt werden. Kein Schutzversprechen gegen manipulierte Betriebssystemtools oder böswillige privilegierte Administratoren.

Keine Serververbindung/-änderung in diesem Schritt, keine neue Sicherung oder Produktfreigabe. Das historische Workerpaket bleibt unverändert.

| Datei | SHA256 |
|---|---|
| contract_lab/linux_backend.py | 8d519e9d74485bc7ee828afcf4373e22d707b51e8f23089670481e28c1a660d8 |
| tests/test_contract_linux_backend.py | d455267605f5dad767c02161b730dd0e414bab57933ec4c8f6d6025ff2e6a013 |

# T3 – Prozessbeobachter und Recovery-Verbindung

20.09.2026: **121 lokale Tests bestanden, 0 Fehler, 0 Skips, 39,173 Sekunden**. 17 neue Beobachter-/Recoveryprüfungen. Quellstand Windows/Python; systemd-/cgroup-Antworten in den neuen Tests sind ausdrücklich synthetische Fixtures. Kein Ubuntu-Ausführungsnachweis.

```powershell
& 'C:/Users/Hubert111/AppData/Local/Programs/Python/Python312/python.exe' -B -m unittest discover -s tests -p 'test_contract*.py' -q
```

## Verhalten

| Bereich | Implementierung / Nachweis |
|---|---|
| Identität | Vor OS-Zugriff exakte Lauf-/Invocation-/Boot-/cgroup-Bindung validieren. Unit-ID und geladener Zustand müssen passen. Ungültige Belege lösen keine Abfrage aus. |
| Lesender Adapter | Fester systemctl-show-Aufruf, begrenzte Eigenschaftsliste, drei Sekunden Timeout. Begrenzte Lesezugriffe auf Boot-ID und genau zugeordnete cgroup-Dateien. Keine Stop-/Start-/Kill-/Löschaktion im Beobachter. |
| Konsistenz | systemd-Zustand und Boot-ID vor und nach cgroup-Lesung vergleichen. Wechselnde Instanz, PID oder Bootkennung führt zu unbelegtem Zustand. |
| Grenzen | Tatsächliche cgroup-Limitwerte werden gegen die synthetischen Testgrenzen geprüft; unbegrenzte Ressourcen sperren den Befund. |
| Laufend | Geladene passende Unit active/running, MainPID ungleich null und in cgroup.procs erforderlich. PID allein reicht nicht. |
| Ende | MainPID=0, leere direkte Prozessliste, hierarchisches cgroup.events populated=0 und terminaler Unit-Zustand erforderlich. Übrig gebliebene Kinder oder belegte Untergruppen verhindern Freigabe. |
| Fehlende Beobachtung | Fehlende cgroup, nicht geladene Unit, doppelte/fehlende Eigenschaften, übergroße Ausgabe oder widersprüchliche Prozesse führen zu Fehler beziehungsweise unknown; niemals erfundener Endebeleg. |
| Fachlicher Ausgang | Signalbeendigung ist getrennt vom technischen Ende sichtbar. Keine automatische Übersetzung von ended in succeeded. |
| Recovery-Verbindung | `release_observed` verlangt ended aus Beobachtung und übergibt exakt gebundene Identität an das Journal. running/fehlende Beobachtung verändern den Journalstand nicht. Technische Freigabe endet mit released_unknown. |

RED/GREEN: fehlendes Beobachtermodul und anschließend fehlende Recovery-Verbindung jeweils vor Implementierung nachgewiesen. Alle neuen sowie bisherigen Vertragsprüfungen gemeinsam bestanden.

## Grenzen / nächste Arbeit

- Die Adapterpfade für echte Linux-Beobachtung sind implementiert, wurden hier aber **nicht auf Ubuntu ausgeführt**. Test-Seams dürfen nur vom kontrollierten Testcode kommen, niemals aus HTTP-/Modellantworten.
- Zweifache Zustandserfassung ist keine atomare Sperre gegen fremde Root-Aktionen oder Zustandswechsel nach der Beobachtung. Der Controller muss Instanzexklusivität und erneute Kontrolle unmittelbar vor Aktionen gewährleisten.
- Wenn systemd eine cgroup nach Prozessende entfernt, verweigert diese konservative Fassung die Freigabe. Ein alternativer Nachweis braucht gesonderte konkrete Belege; Abwesenheit wird nicht mit sicherem Ende gleichgesetzt.
- Effiziente sichere Paketablage, Runtimeprüfung, Start-/Beleglücke, Controllerexklusivität, Stop-Aufruf und Dateirücknahme sind noch nicht im vollständigen Runner verbunden. Kein Root-Aufruf zur Ausführung freigegeben.
- Paket `artifacts/rest-t3b-20260920` bleibt unverändert und enthält nur den Worker; dieser neue Beobachter ist noch kein Bestandteil eines vollständigen Serverpakets.

Nächster Schritt: Controller und gezielte Rücknahme um die vorhandenen Paket-, Journal- und Beobachterbausteine ergänzen; danach vollständiges konkret geprüftes Paket für die Serverfreigabe bereitstellen. B07–B09 bleiben hinsichtlich echter Ubuntu-Wirkung offen. Keine Server-/Produktänderung, kein neues Backup. Governor health weiterhin ok, Version 0.5.0.

## Quellenbindung

| Datei | SHA256 |
|---|---|
| contract_lab/linux_observer.py | a72af342e807a85293fee27446330dbf82305696e1feb295cc5bbedd2bc13ddc |
| tests/test_contract_linux_observer.py | 7c310937df1531b6c47139fc85238d1ef4563d8c54962267a54b4ceb2d9564b8 |

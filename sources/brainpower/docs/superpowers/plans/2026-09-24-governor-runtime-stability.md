# Governor-Laufzeit und Live-Start

Ziel: die vorhandenen HTTP-/Prozess-Timeouts nachvollziehbar beheben, die offenen Prüfungen abschließen und Governor mit unveränderten Betreiberpräferenzen sichtbar starten. Nutzer hat Fortsetzung und Öffnen ausdrücklich beauftragt; Reasoning Medium. Kein neuer Produktauftrag oder Modellversand.

Ansatz: Nach exakter Git-Wurzelprüfung HEAD, Zweig, Status sowie geänderte/staged Pfade gemeinsam aus Porcelain v2 lesen. Den gemeldeten Commit explizit für ls-tree und SHA256-Inhaltsprüfung verwenden. Damit höchstens drei Metadaten-Prozessstarts; die getrennten Inhaltsnachweise bleiben erhalten. Fehler bleiben unvollständige Evidenz; keine Lockerung von Gate-, Hash- oder Shutdownprüfungen. Test für begrenzte Prozesszahl/Wurzelgrenze/Fehler vor Änderung rot. Das vorherige Parallelitätsexperiment wurde nach realer Messung verworfen; es ist nicht der finale Code. Prozesstest prüft Startbudget und schnelle Bereinigung getrennt, sofern Messung den Start als Ursache bestätigt; Generische Ausführungsgrenzen unverändert; Profilbereitschaft wird bei eigenem Messnachweis separat korrigiert. Bestehender Checkpoint bleibt unverändert, keine pauschalen Git-Operationen im übergeordneten Home-Repository.

- [x] Historische Fehler und aktuelle Start-/Bereinigungszeiten prüfen.
- [x] Negativen Regressionstest für zusammengefasste Metadatenabfragen ausführen.
- [x] Minimale Umsetzung mit vorhandenen Quellen-/Shutdown-/HTTP-Tests abnehmen.
- [x] Prozessbaumprüfung mit eigenem Bereinigungsnachweis stabilisieren.
- [x] Offene Regressionen abschließen; unabhängige Prüfung und Dokumentation.
- [x] Gespeicherte Einstellungen prüfen, Governor starten, Live-Oberfläche öffnen und prüfen.

Messung ohne konkurrierenden Testlauf: Parallelitätsexperiment 28,859s; direkter Git-Einstieg 19,860s. Beides nicht ausreichend. Finale Lösung reduziert Aufrufzahl statt nur Aufrufe nebeneinander zu starten. Referenz: https://git-scm.com/docs/git-status (Porcelain v2, NUL-Format). Prozessprüfungen erhalten 12s begrenztes Kaltstartfenster; nach Exit/Abbruch/Callbackfehler eigener Nachweis innerhalb 2s, Kernelhandle- und Eigentümergrenzen unverändert. Expliziter .2s-Timeouttest bleibt erhalten.

Ergänzung: vollständig gelesene Original-Commitdaten werden nach Wurzel/Commit begrenzt gecacht. `--no-replace-objects` schließt veränderliche Git-Ersetzungen aus; echter Regressionstest zuerst rot, danach grün. Index/Arbeitsbaum bleiben frisch. Gemeinsamer HTTP-Testwartehelfer 60s pro Einzelauftrag, 120s für die zweistufige serielle Prüffolge; Endzustände und fachliche Prüfungen unverändert. Generische Ausführungsgrenzen nicht angehoben; anschließend separat gemessener Bereitschaftsfehler des eingebauten Profils: 6,016s bis gültiger Antwort, bisheriges 5s-Fenster auf 12s korrigiert. HTTP-Testclient an unveränderte 25s-Browserfrist angeglichen. Aktuelle Ergebnisse und Grenzen stehen in `docs/verification/GOVERNOR_RUNTIME_2026-09-24.md`.

Abschluss: synchrone Reparaturvorprüfung nach gemessenen 27,125s in den vorhandenen einzelnen Worker verlegt; aktuelle Quellen-/Versand-/Bindungsprüfung vor Modellaufrufen und Speicherung erhalten. Durchgängiger Reparatur-/Übernahme-/Folgetest-/Rollbacklauf plus elf Reparaturprüfungen bestanden. Teilnachweise und deren Grenzen im Abschlussbericht; keine neue Provider-Inferenz.

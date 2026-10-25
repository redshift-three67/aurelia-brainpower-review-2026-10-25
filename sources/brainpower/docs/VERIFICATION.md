# Verifikation und Aussagegrenzen

Nachtrag 11.09.2026, 23:23 MESZ: Der Betreiber hat die zuvor blockierte Übermittlung ausdrücklich erlaubt. Beide realen Fünf-Projekt-Läufe mit Sol beziehungsweise Astra sind inzwischen abgeschlossen. Der unten beschriebene Übermittlungsblock ist ein historischer Zwischenstand. Aktueller Befund: [Soll/Ist und reale Projektprüfung](SOLL_IST_LIVE_2026-09-11.md).

## Funktional nachgewiesen

- Abschließende Anwendungssuite: 58 Tests erfolgreich in 15,085 Sekunden. Darunter ein echter Start-/Stop-Test mit separatem Serverprozess; Stop wartet auf die Freigabe der Instanzsperre. Der produktive Dienst wurde anschließend über die Windows-Aufgabe erneut gestartet und per HTTP geprüft.
- Lokale Datei-/Git-Beobachtung der fünf angegebenen Projektpfade; richtiger Morphic-Worktree und tatsächlicher Snapshot-Pfad aufgelöst.
- Konflikt- und Sicherungsverhalten des Editors mit isolierten Testdateien; keine Originalgedächtnisse zu Testzwecken überschrieben.
- Automatisierte Tests für Pfadgrenzen, staged/committed/current-Inhalte, große Dateidrift, Konfigurationsabhängigkeiten, Job-Deduplikation, Neustartstatus, Prozessabbruch und lokale HTTP-Sicherheitsgrenzen.
- Browserprüfung mit Chromium bei 1440 und390 Pixeln: fünf Projekte, tatsächlicher Gedächtnisabruf, Supervisor-Auswahl und Wiederherstellung, ungespeicherte Entwürfe, SSE-Wiederverbindung/Fallback. Keine JavaScript-Seitenfehler und kein horizontaler Seitenüberlauf in diesen Prüfungen.
- Beobachtungsfehler und veraltete Ergebnisse werden sichtbar dargestellt; nicht nur in Roh-JSON oder Hovertext verborgen.
- Echter RadiWorks-Testauftrag über `/api/actions`:205 Tests,0 Fehler,0 Fehler beim Testaufbau,0 übersprungen; Exitcode0. Lauf vom11.09.2026 19:25:22 bis19:26:14 UTC. Vorher-/Nachher-Evidenz unverändert. Ergebnis liegt auf dem Entwicklungsrechner unter `artifacts/radiworks_ui_test.json` und im Governor-Journal.
- Echte synthetische Modellprüfungen: Terra+Sol und Terra+Astra jeweils4/4 definierte Governance-Fälle. Separate hybride Schutzprüfungen blockierten fehlende Freigaben und veraltete Grundlagen. Exakte angeforderte Modellnamen wurden in Routerantworten bestätigt.
- Tatsächliche Hermes-Python-API-Integration mit null aufgelösten Werkzeugen, isoliertem Home und unabhängiger Supervisor-Anfrage. Zusätzlich isolierter Offline-Fähigkeitstest ohne Netzwerkzugriff.
- Windows-Aufgabe `GovernorWorkbench-Local` erstellt und tatsächlich gestartet; läuft mit `pythonw.exe` unter dem aktuellen Benutzer, ohne sichtbares Terminal. Autostart bei Anmeldung und bis zu drei Fehlerneustarts konfiguriert.

## Unabhängige Prüfung

Eine unabhängige Codeprüfung fand Fehler bei statischen Governance-Aussagen, Dateidriftgrenzen und Git-Content-Zuordnung. Diese wurden mit Regressionstests nachvollzogen und korrigiert. Eine separate UI-Prüfung fand unauffällige Fehler-/Veraltetanzeigen und eine abweichende Eingabelängengrenze; diese wurden korrigiert und mit Browserfixtures erneut geprüft.

Die Designprüfung verwendete einen unabhängigen Agentenkontext desselben Modellanbieters, da kein anderer Anbieter als Review-Agent verfügbar war. Die synthetischen Produktmodellvergleiche verwendeten die tatsächlich konfigurierten Modelle über CC Switch. Keines davon ist ein statistischer Nachweis weltweiter Optimalität oder allgemeiner Fehlerfreiheit.

## Nicht als erledigt behauptet

**Echter Projektinhalt wurde für den vorgesehenen neuen Fünf-Projekt-Review nicht an die Modelle gesendet.** Die automatische Freigabeprüfung lehnte die konkrete Übermittlung von Gedächtnis-/Governance-Auszügen über den Router an die Modelle einschließlich Astra ab. Deshalb bleibt dieser Review ausstehend und automatische Modellreviews sind ausgeschaltet. Die lokale Beobachtung läuft weiter. Der lokale vorgeschlagene Inhalt steht zur gesonderten Freigabe in `artifacts/proposed-real-review-payload.json`.

Die Workbench implementiert keine autonome Produkt-Codeänderung, keinen Commit-/Migrationsautomaten und keine Serverbereitstellung. Die jeweiligen bestehenden Projektgates bleiben bestehen. Geplante Module sind nachvollziehbare Planungsobjekte, keine vorgetäuschten Prototypen.

Keine vollständige interaktive RadiWorks-End-to-End-Abnahme, kein Aurelia-Server-/Restore-Test und keine Hardwareprüfung wurden hinzugefügt. Es wurde kein anderer physischer Windows-PC getestet. Die frische portable Installation wird lokal in einem separaten Ordner und Python-Environment geprüft; die Ziel-PC-Anmeldung und dortige Hermes-/CC-Switch-Installation müssen zusätzlich vor Ort geprüft werden.

## Reproduzierbare Prüfungen

Die jeweils aktuelle lokale Suite wird mit `python -m unittest discover -s tests -v` ausgeführt; ihre Ausgabe wird bei der Übergabe unter `artifacts/unit-tests.txt` abgelegt. Browserbilder liegen unter `artifacts/ui-desktop.png` und `artifacts/ui-mobile.png`. Das Release-ZIP besitzt einen SHA-256-Prüfwert und ein Inhaltsmanifest. Personalisierte Konfigurationen, Token-Dateien, echte Kontextpakete und Laufzeitdaten werden nicht in das Release aufgenommen.

Eine kurze Leerlaufmessung des tatsächlichen Windows-Prozesses wird unter `artifacts/idle-resource-observation.json` dokumentiert. Sie beschreibt ausschließlich diese lokale Stichprobe; Modellläufe und RadiWorks-Tests können deutlich höhere Ressourcen verwenden.

Die 20,02-Sekunden-Stichprobe ergab 17,08 MiB Working Set und 0,08 Prozent eines CPU-Kerns. Diese Messung umfasst keinen Modell- oder Testauftrag und erlaubt keine allgemeine Hardwareprognose.

# Installation und Einrichtung auf einem anderen Windows-PC

## Ergänzung für Version 0.3

Der aktuelle Funktionsumfang und die Grenzen stehen in [Governor 0.3](GOVERNOR_0_3.md). Ein erfolgreicher Installationstest ist keine fachliche Abnahme Ihrer Projekte.

Bei einem Update zuerst den Dienst beenden und den gesamten bisherigen Workbench-Ordner einschließlich `runtime` und `config.local.json` sichern. Dann die neuen Programmdateien übernehmen; lokale Konfiguration und Journal behalten. Ein Downgrade verwendet eine zusammengehörige Sicherung aus Programm und Journal. Kein zweiter Prozess darf dasselbe Journal öffnen.

Beim ersten Start wird `projects` einmalig in das dauerhafte Register übernommen. Danach neue Projektordner über „Projekte & Gruppen“ registrieren. Spätere Änderungen der ursprünglichen `projects`-Liste aktualisieren bestehende Registerpfade nicht automatisch. Ein PC-Umzug vorhandener Registerdaten auf andere Pfade ist noch kein unterstützter Migrationsassistent: auf dem neuen PC zunächst ein separates frisches Journal und die korrekten Pfade verwenden; alte Entscheidungen nur nach Quellenabgleich neu bestätigen.

1. Die fünf bekannten IDs werden als „Aurelia Integration“ mit Hauptprojekt, drei Modulen und Vertragsprojekt übernommen. Andere Projekte beginnen eigenständig. Gruppenmitgliedschaft und Rolle sind dauerhaft.
2. `legacy_review_egress_authorized` bleibt auf neuen PCs `false`. Versandfreigaben bewusst je Projekt speichern. Keine fremden Freigaben oder Anmeldedateien aus einem Release übernehmen.
3. Optional `vault_root` auf den eigenen Vault setzen und konkrete Markdown-Dateien einem Projekt oder einer Gruppe zuordnen. Keine automatische Gesamtübernahme alter Vault-Statusdateien. Der schreibende Vault-Spiegel ist noch offen.
4. Aufnahme prüfen und Anforderungen, Teststrategie, Abhängigkeiten und offene Nachweise bestätigen. Eine Vorlage allein ermöglicht keinen Matrixplan.
5. Den Hybridplan entwerfen lassen, Prioritäten und Voraussetzungen prüfen und die sichtbare Planauswahl bestätigen. Diese Auswahl startet keine Produktänderung.
6. `staging_pilot_roots` bleibt standardmäßig `[]`. Für den begrenzten Python-Piloten höchstens fünf vorhandene, kanonische absolute Verzeichnisse eigener isolierter Single-Beispielprojekte konfigurieren. Keine Junctions oder produktiven Gruppenprojekte. Nur explizit gestagte Dateien und `tests/test*.py` mit Standardbibliothek werden geprüft. Originaldateien werden nicht zurückgeschrieben.

Die lokale Gruppenbeobachtung prüft pro Zyklus einen Umfang reihum. Bei zehn Umfängen und 15 Sekunden Intervall dauert eine Runde mindestens etwa 150 Sekunden zuzüglich Prüfzeit. Automatische Modellreviews bleiben auf den bisherigen konfigurierten Umfang begrenzt; neue Gruppen erhalten dadurch keine automatische Versand- oder Ausführungsfreigabe.

## 1. Voraussetzungen und Verantwortlichkeiten

Getestete Entwicklungsumgebung: Windows, Python 3.12, Git, CC Switch 3.20.2 und Hermes 21.1. Der Governor selbst verwendet ausschließlich die Python-Standardbibliothek. Die Hermes-Integration ist zusätzlich an die vorhandene Hermes-Python-API gebunden und überprüft ihre Schutzbedingungen bei jedem Lauf. Ein anderes Hermes-Release muss vor Freigabe erneut geprüft werden.

Benötigt werden ein normaler Windows-Benutzer, Python 3.11 oder neuer, Git und ein aktueller Browser. Für die hybriden Modellfunktionen zusätzlich CC Switch, eine funktionierende eigene Anmeldung für die Modelle und eine funktionsfähige Hermes-Installation mit ihrem eigenen Python-Environment. Administratorrechte sind für den Governor-Lauf und den vorgesehenen Benutzer-Autostart nicht erforderlich; Unternehmensrichtlinien können die Aufgabenplanung dennoch einschränken.

**Keine fremden Anmeldedateien übernehmen.** Auf jedem PC mit dem vorgesehenen eigenen Konto anmelden. Der Governor kopiert keine Tokens. Projektdateien und deren fachliche Freigaben müssen unabhängig vom Governor korrekt übertragen bzw. aus ihren Repositories wiederhergestellt werden.

## 2. Empfohlene Terminalumgebung

Windows Terminal ist die empfohlene Anzeige mit Tabs, geteilten Ansichten und Unicode-/UTF-8-Unterstützung. Es hostet die gewünschte Shell. Für vorhandene Windows-Projektpfade und PowerShell-Skripte empfiehlt sich PowerShell 7. Windows PowerShell 5.1 bleibt für die mitgelieferten Startskripte verwendbar. Ein Wechsel zu WSL würde Linux-/Windows-Pfade und zusätzliche Prozesse einführen; für diesen Governor ist er nicht erforderlich.

Herstellerquellen: [Windows Terminal](https://learn.microsoft.com/en-us/windows/terminal/), [PowerShell-Versionen](https://learn.microsoft.com/en-us/powershell/scripting/what-is-windows-powershell?view=powershell-7.6). Die Workbench selbst benötigt kein dauerhaft geöffnetes Terminal.

## 3. Paket ablegen und Grundinstallation

1. Das Release-ZIP in einen lokalen, vom Benutzer beschreibbaren Ordner entpacken, zum Beispiel `C:\Tools\GovernorWorkbench`. Nicht in einen schreibgeschützten Ordner wie `Program Files` und möglichst nicht in ein laufend synchronisiertes Cloudverzeichnis entpacken.
2. In diesem Ordner `Install-Governor.cmd` ausführen. Alternativ in einer PowerShell:

   ```powershell
   .\scripts\Install-Windows.ps1
   ```

   Bei abweichender Python-Installation:

   ```powershell
   .\scripts\Install-Windows.ps1 -PythonExe 'C:\Pfad\zu\python.exe'
   ```

3. Der Installer erstellt `runtime-python.json`, kopiert nur eine noch nicht vorhandene `config.local.json` aus dem Beispiel und führt die enthaltenen lokalen Tests aus. Er überschreibt keine bestehende Konfiguration und lädt keine zusätzlichen Pakete nach.
4. Ein Testfehler beendet die Installation mit einer Fehlermeldung. Zuerst diesen Fehler beheben, bevor der Dienst eingerichtet wird.

Die `.cmd`-Launcher verwenden eine nur für ihren Prozess geltende PowerShell-Ausführungsrichtlinie. Sie ändern die systemweite Richtlinie nicht. Bei einer verbindlichen Unternehmensrichtlinie muss das Skript über den vorgesehenen internen Freigabeweg ausgeführt werden.

## 4. Konfiguration an diesen PC anpassen

`config.local.json` in einem Texteditor öffnen. Das Format ist JSON; Backslashes müssen darin doppelt geschrieben werden. Einfacher sind Pfade mit `/`. `${USERPROFILE}` und `${LOCALAPPDATA}` werden anhand des aktuell angemeldeten Benutzers aufgelöst. Relative Pfade werden relativ zur Konfigurationsdatei aufgelöst.

| Feld | Bedeutung / notwendige Prüfung |
|---|---|
| `projects` | Für jedes bestehende Projekt eindeutige ID, Name, tatsächlicher lokaler Pfad, dokumentierter Gateplan und bekannte Abhängigkeiten. |
| `projects[].path` | Bei Morphic den richtigen Worktree angeben, nicht versehentlich nur das Hauptrepository. |
| `governor_dir` | Ordner mit bestehendem Manifest, Zielen und Governance-Dokumenten. |
| `snapshot_dir` | Tatsächlicher Snapshot-Ordner dieses PCs. Fehlt er, wird die Evidenzlücke sichtbar. |
| `hermes_path` | Wirkliche `hermes.exe`, üblicherweise unter `AppData/Local/hermes/hermes-agent/venv/Scripts`. Nicht anhand eines ähnlich benannten zweiten Checkouts raten. |
| `router_url` | Bei der geprüften Hermes-Integration `http://127.0.0.1:3000/v1`. Der Router muss lokal sein. |
| `codex_auth_path` | Pfad zur Anmeldedatei des eigenen Kontos, üblicherweise `${USERPROFILE}/.codex/auth.json`. Kein Tokenwert in die Governor-Konfiguration schreiben. |
| `router_api_key_env` | Optionaler Name einer bereits gesetzten Umgebungsvariable für den direkten Router-Transport. Standard: `GOVERNOR_ROUTER_API_KEY`. |
| `orchestrator_transport` | `hermes` erhält Hermes als Terra-Ausführungsebene. `router` ist ein expliziter direkter API-Betriebsmodus, kein automatischer Fallback. |
| `supervisor` | `gpt-5.6-sol` oder `gpt-6-astra`; die Oberfläche speichert eine spätere Auswahl im lokalen Journal. |
| `port` | Freier Governor-Port, Standard 8787. Nicht den CC-Switch-Port 3000 verwenden. |
| `data_dir` | Lokales Journal, Testausgaben und Gedächtnissicherungen; Standard `runtime` im Installationsordner. |
| `monitor_interval`, `git_interval` | Standard 15 bzw. 60 Sekunden; nicht ohne Bedarf reduzieren. |

Auf einem anderen PC existieren möglicherweise noch nicht alle Projekte. Fehlende Pfade bleiben sichtbar und führen nicht zu einer grünen Freigabe. Neue Ideen ohne Prototyp über die Oberfläche als **geplante Module** erfassen; dafür keinen existierenden Projektpfad vortäuschen.

## 5. Lokale Diagnose

Im Installationsordner:

```powershell
py -3.12 -m governor_workbench doctor --config config.local.json
```

Bei einem anderen Interpreter denselben ausdrücklich gewählten Python-Pfad wie beim Installer verwenden. Die Diagnose zeigt Python/Git, Hermes-Version, Pfadverfügbarkeit, Port und das Vorhandensein der Anmeldedatei. Sie zeigt keine Tokens und führt keine Inferenz aus. Ein bereits laufender Governor belegt seinen eigenen Port; `port_free=false` ist dann erwartbar.

Bei zwei Hermes-Installationen `Get-Command hermes` prüfen und den tatsächlichen Launcher auflösen. Der Governor ändert die ursprüngliche Hermes-Konfiguration nicht. CC Switch und die zugehörige Anmeldung müssen unabhängig funktionieren.

## 6. Start und Funktionsprüfung

1. CC Switch starten und die eigene Anmeldung prüfen.
2. `Start-Governor.cmd` doppelklicken. Der Browser öffnet die lokale Oberfläche. Alternativ `scripts/Start-Governor.ps1 -NoBrowser`.
3. Fünf Projektpfade und Quellen kontrollieren. Dokumentierter Plan, Git-Beobachtung und ausgeführte Prüfung sind unterschiedliche Nachweise.
4. **Hermes prüfen** führt Versions- und isolierte Werkzeugprüfung aus. Das Ergebnis muss null aktivierte Werkzeuge bestätigen; es wird dabei keine Inferenz benötigt.
5. **Modelle prüfen** führt einen kleinen synthetischen Governance-Vergleich aus. Dies nutzt das Modellkonto, überträgt aber keine echten Projektgedächtnisse. Ein 200-Gesundheitscheck allein genügt nicht.
6. **RadiWorks-Tests** nur bei korrekt eingerichteter RadiWorks-Testumgebung ausführen. Ihr Interpreter wird unter `radiworks_port/engine/.venv/Scripts/python.exe` erwartet. Die produktspezifischen Abhängigkeiten gehören zur RadiWorks-Installation.
7. Gedächtnisdatei zunächst nur lesen. Schreib-/Konfliktverhalten mit einem ausdrücklich dafür vorgesehenen Testprojekt prüfen, nicht mit wertvollen Originaldateien.
8. Einen echten Hybrid-Review erst nach Prüfung und Freigabe der zu übermittelnden Projektinhalte auslösen. Der Hinweis unter der Aktion benennt die Übermittlung. Die Auswahl des Supervisors bestimmt den zweiten, unabhängigen Modellaufruf.

Die synthetische Modellprüfung ist kein allgemeiner Nachweis maximaler Genauigkeit. Bei der hier geprüften Installation bestanden beide Kombinationen dieselben vier Fälle. Auf jedem neuen PC müssen Authentifizierung, Modelle und Routerantworten erneut geprüft werden.

## 7. Dauerbetrieb und Autostart

Nach erfolgreicher Prüfung im Installationsordner ausführen:

```powershell
.\scripts\Enable-Autostart.ps1
```

Dies registriert `GovernorWorkbench-Local` für die Anmeldung des aktuellen Benutzers. Die Aufgabe startet `pythonw.exe` direkt, ohne sichtbares Terminal, mit begrenzten Benutzerrechten. Nach einem Fehler sind bis zu drei Neustarts im Minutenabstand vorgesehen. Der vorhandene Instanzlock verhindert zwei Governor-Instanzen auf demselben Datenordner. CC Switch muss separat verfügbar sein; sein Ausfall beendet die lokale Beobachtung nicht.

Prüfen:

```powershell
Get-ScheduledTask -TaskName GovernorWorkbench-Local
Get-ScheduledTaskInfo -TaskName GovernorWorkbench-Local
```

Die Überwachung läuft bei eingeschaltetem, angemeldetem PC. Während Windows-Schlafzustand, Abmeldung oder ausgeschaltetem Rechner findet keine Beobachtung statt. Nach Rückkehr wird erneut gelesen; das ist kein Dienst auf einem externen Server.

**Automatische Modellreviews:** Standard aus. Erst nach ausdrücklicher Freigabe der echten Projektinhalte in der Oberfläche aktivieren. Dann gelten Mindestabstand 15 Minuten, maximal vier automatische Reviews pro UTC-Tag, ein Auftrag gleichzeitig, keine automatischen Produktänderungen und kein automatisches Weiterlaufen bei unvollständiger Vergleichsevidenz. Bereits fehlgeschlagene Versuche zählen zum Limit.

Autostart entfernen:

```powershell
.\scripts\Enable-Autostart.ps1 -Disable
```

Das entfernt die Aufgabe, löscht keine Daten und beendet einen laufenden Governor nicht. Dafür `Stop-Governor.cmd` verwenden.

## 8. Sicherung, Update und Wiederherstellung

Vor einem Update regulär stoppen. Den Installationsordner einschließlich `config.local.json`, `runtime-python.json` und dem konfigurierten `data_dir` lokal sichern. Bei einem benutzerdefinierten Datenordner diesen zusätzlich berücksichtigen. `.codex/auth.json` wird nicht als transportable Governor-Konfiguration mitgesichert oder auf fremde PCs verteilt.

Neue Programmdateien einspielen; die persönliche Konfiguration und Laufzeitdaten erhalten. Installer/Tests erneut ausführen, Diagnose prüfen und starten. Nach einem Versionswechsel auch Hermes-Isolation und synthetische Modellprüfung wiederholen. Unterbrochene Aufträge werden beim Neustart als unterbrochen gekennzeichnet und nicht automatisch erneut ausgeführt.

Gedächtnissicherungen liegen unter `data_dir/backups/PROJEKT-ID/`. Die Anwendung legt sie vor dem Schreiben an. Wiederherstellung ist eine bewusste Dateientscheidung: Originalstand prüfen, betroffene Bearbeitung stoppen, passenden Sicherungsinhalt übernehmen und danach Hash/Git-Status erneut prüfen. Ein kompletter Produkt-/Serverrestore ist davon unabhängig und wird nicht durch diesen Governor zertifiziert.

## 9. Häufige Fehler

- **Port belegt:** Den tatsächlich laufenden Dienst prüfen; einen fremden Prozess nicht beenden. Governor-Port in der Konfiguration ändern, bei Autostart anschließend die Aufgabe erneut registrieren.
- **401/403 bei Modellen:** Eigene Anmeldung prüfen. Keine Tokens in Chat, Logs oder Konfigurationsbeispiele kopieren. Der Governor aktualisiert Tokens nicht selbst und versucht kein anderes Modell im Hintergrund.
- **Hermes-Isolation scheitert:** Versions-/API-Kompatibilität prüfen. Nicht als Reparatur alle Werkzeuge aktivieren. Der explizite `router`-Modus kann für reine Modellreviews verwendet werden, verändert aber die Ausführungsebene.
- **Speicherkonflikt:** Datei wurde seit dem Laden geändert. Entwurf vergleichen und neu laden; der alte Stand wurde nicht blind überschrieben.
- **Review veraltet:** Quellen oder relevante Planmetadaten haben sich geändert oder konnten nicht vollständig gehasht werden. Neue Prüfung auf aktuellem Stand erforderlich.
- **Autostart abgelehnt:** Aufgabenplanungsrechte bzw. Unternehmensrichtlinien prüfen. Der manuelle lokale Start funktioniert unabhängig davon.

Ein anderer Windows-PC wurde im Entwicklungsdurchlauf nicht physisch getestet. Das Release wird zusätzlich aus einem frischen Ordner mit Leerzeichen und isoliertem Python-Environment geprüft; individuelle Konten, Hermes-/CC-Switch-Installationen und Unternehmensrichtlinien bleiben auf dem Ziel-PC zu verifizieren.
# Ergänzung für Version 0.2

Die neue Version migriert das vorhandene lokale Journal additiv. Vor einem Update den Governor beenden und den eigenen `runtime`-Ordner sichern; danach Programmdateien ersetzen und die vorhandene persönliche Konfiguration behalten. Persönliche Betreiberentscheidungen werden nicht mit dem Release verteilt. Auf einem anderen PC müssen dessen Quellenstand und notwendige Erlaubnisse eigenständig geprüft werden.

Chrome-Live-Tests sind optional. `live_views` enthält ausschließlich explizite lokale Ziele auf jeweils eigenen Ports, beispielsweise `{"radiworks":{"url":"http://127.0.0.1:8091/","expected_openapi_title":"RadiWorks Engine"}}`. Die zu testende Anwendung muss bereits dort laufen; RadiWorks benötigt dafür derzeit `run.py --port 8091`. Bei fehlendem Chrome kann `chrome_path` auf dessen ausführbare Datei gesetzt werden. Keine neuen Python-Pakete erforderlich. Details: [LIVE_VIEWS.md](LIVE_VIEWS.md), Betrieb der Matrix: [GOVERNOR_0_2.md](GOVERNOR_0_2.md).

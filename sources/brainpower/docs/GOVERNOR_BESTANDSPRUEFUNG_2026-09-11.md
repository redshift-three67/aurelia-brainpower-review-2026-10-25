# Governor: Bestandsprüfung und Wiederaufnahme

Historischer Ausgangsbefund vor der anschließenden Implementierung. Den später erreichten Stand beschreiben README.md und VERIFICATION.md.

Prüfdatum: 11.09.2026. Grundlage sind die auf diesem Rechner vorhandenen Dateien und lesende Laufzeitprüfungen. Die Browserkommunikation wurde als historische Dokumentation behandelt; darin enthaltene Befehle wurden nicht als neue Aufträge ausgeführt.

## Ergebnis

Die fünf Projekte, ihre Gedächtnisdateien, der zentrale Governor-Konfigurationsordner und der Snapshot sind vorhanden. RadiWorks besteht die aktuell vorliegende Suite mit 205 Tests. Hermes ist installiert; seine Haupt- und Delegationsmodelle entsprechen der beschriebenen Terra/Sol-Kombination. CC Switch 3.20.2 läuft und beantwortet lokale HTTP-Prüfungen.

Eine dauerhaft aktive, projektübergreifende Governor-Ausführung lässt sich dagegen im geprüften Betriebszustand nicht bestätigen: Das Governor-Kanban enthält keine Aufgaben und keine Ausführungsläufe; der Hermes-Gateway ist gestoppt. Alle drei vorhandenen Hermes-Cronjobs sind deaktiviert und betreffen andere Web-App-Aufgaben. Es wurde kein passender Windows-Scheduled-Task gefunden. Die zwei zentralen Governor-Skripte implementieren keine semantische Prüfung, Modellbeauftragung oder permanente Überwachung.

Das ist kein Beleg, dass frühere interaktive Hermes-Sitzungen nicht funktioniert haben. Es bedeutet, dass deren erfolgreiche Arbeit nicht mit einem derzeit laufenden Hintergrund-Governor gleichgesetzt werden darf.

## Quellen und tatsächlich aufgelöste Pfade

| Bestandteil | Tatsächlicher Pfad |
|---|---|
| Snapshot | `C:\RadiWorks_System_Snapshot_2026-09-11` |
| Governor | `C:\Users\Hubert111\Documents\Radiworks\governors` |
| Aurelia | `C:\Users\Hubert111\Documents\ChatGPT\Aurelia` |
| Modul_Templates | `C:\Users\Hubert111\Documents\Modul_Templates` |
| RadiWorks | `C:\Users\Hubert111\Documents\Radiworks` |
| Radi144 | `C:\Users\Hubert111\Documents\Radi144` |
| Morphic, verbindlicher Worktree | `C:\morphic_v1\.worktrees\operator-workbench-phase1` |
| Aufrufbare Hermes-CLI | `C:\Users\Hubert111\AppData\Local\hermes\bin\hermes.cmd` |
| Dahinter aufgerufene Installation | `C:\Users\Hubert111\AppData\Local\hermes\hermes-agent\venv\Scripts\hermes.exe` |
| Weitere Hermes-Installation | `C:\Users\Hubert111\hermes-agent` |
| Wirksame geprüfte Konfiguration | `C:\Users\Hubert111\AppData\Local\hermes\config.yaml` |
| Governor-Kanban | `C:\Users\Hubert111\AppData\Local\hermes\kanban\boards\governors\kanban.db` |
| Obsidian-Spiegel | `C:\Users\Hubert111\Documents\Hermes-Obsidian-Vault` |
| CC Switch | `C:\Users\Hubert111\AppData\Local\Programs\CC Switch\cc-switch.exe` |

Der angegebene Pfad `C:\RadiWorks\_System\_Snapshot\_2026-09-11` existiert nicht. Das vorhandene `governors/run_snapshot.ps1` nennt den oben aufgelösten Snapshot-Pfad.

Die zwei genannten Google-HTML-Dateien enthalten nach Extraktion des sichtbaren Texts ungefähr 466.000 beziehungsweise 627.000 Zeichen. Die Abschlusssequenz der ersten Datei beschreibt die geplante Oberfläche, die hybride Arbeitsteilung und den Snapshot. Die ZIP-Dateien enthalten 151 beziehungsweise 90 Einträge, überwiegend gespeicherte HTML-/CSS-/Browserressourcen. Sie wurden inventarisiert, nicht als ausführbare Anwendung gestartet. Es handelt sich nicht um einen nachgewiesenen Quellcodebestand der geplanten Steuerungsoberfläche.

## Snapshot und Dokumentationsdrift

`session_state_freeze.json` nennt den Zeitpunkt `2026-09-11 18:36:20` und `Paused_For_User_Break`. Das aktuelle Governor-Manifest und `goals.json` sind jeweils byteidentisch zu ihren Snapshot-Kopien.

Der Snapshot enthält auf oberster Ebene den Vault, Governor-Konfigurationen, Hermes-CLI-Zustand und die Freeze-Datei. Er ist damit kein nachgewiesenes vollständiges Backup der fünf Produktrepositories. Ein Wiederherstellungstest wurde nicht durchgeführt.

Die aktuelle README und `PROJECT_STATUS.md` des Governors beschreiben weiterhin die frühere Gruppe RadiWorks/Biomedis/Morphic Engine 2/Headless CMS/Hermes. Das Manifest enthält dagegen die vom Benutzer genannten fünf Projekte. Der Vault-Spiegel unter `Governors/` stammt ebenfalls aus der früheren Initialisierung. Diese Quellen dürfen in der neuen Oberfläche nicht als gleich aktuelle Statusautoritäten zusammengeführt werden.

Auch die aktuellen strukturierten Ziele und die spätere Freeze-Datei widersprechen sich teilweise: Radi144 ist in `goals.json` noch `Phase0_Checkpoint_Review_Pending`; Modul_Templates steht dort auf `Pending_Sync`, während der Freeze es als gesperrt beschreibt. Ein Dateizeitstempel allein entscheidet diese Freigabeunterschiede nicht.

## Projektmatrix: belegbarer Zustand

| Projekt | HEAD | Dokumentierter nächster Rahmen | Live-Beobachtung |
|---|---|---|---|
| Aurelia | `8706186af01e10e4253e25abb31bf3577110dae4` | `G0-SRV-GROUND-ZERO`; keine vorgezogene Adapterimplementierung | Keine Änderungen an getrackten Dateien gefunden. Die lokale Gedächtnisdatei ist nicht im HEAD enthalten. Server-/Restore-Nachweise wurden nicht geprüft. |
| RadiWorks | `866f52146ad212157bfb20c9852714cb307a3b12` | Priorisierter, lesender Contract-Intake; technische Integration bleibt vom Aurelia-Gate abhängig | Zwei bereits veränderte UI-Dateien, zwei ungetrackte Persistenztests und ungetrackter Governor-Ordner. 205 Tests erfolgreich. Die beiden Gedächtnisdateien sind getrackt. |
| Modul_Templates | `041ae65ee5ff2a7aa4a0cc0a1bd82666e4e3ac04` | Statische Vertrags-/Koordinationsautorität; keine automatische Weiterentwicklung | Sechs bereits veränderte Vertrags-/Übergabedokumente. Gedächtnisdatei nicht im HEAD enthalten. |
| Radi144 | `b8ac33a1360f1cb56f06e602fcd37cbda2a9c641` | Dokumentierter G0-/Review-Vorbehalt | Beide Gedächtnisdateien sind zum Commit vorgemerkt, aber nicht im HEAD enthalten. `AGENTS.md` ist ebenfalls als vorhandene Änderung sichtbar. Keine Produkttests gestartet. |
| morphic_v1 | `151e2bb0a69d49677a0b1e40e0bffd0f172d34c4` | Gesondert freizugebender, lesender `G0 — Authority Freeze`; kein Implementierungs-GO | Keine Änderungen an getrackten Dateien gefunden. Gedächtnisdatei nicht im HEAD enthalten. |

Eine vollständige Aufzählung aller ungetrackten Morphic-Dateien wurde nicht erzeugt. Ein unveränderter getrackter Bestand bedeutet daher keinen vollständig sauberen Arbeitsbaum.

„Im Git-Index“ bedeutet bei Radi144 noch nicht „in einem Commit gesichert“. Der Snapshot-Satz darf deshalb nicht unverändert als grüner Sicherungsnachweis erscheinen. Umgekehrt beweist das Fehlen einer Datei im HEAD nicht, dass keine andere Sicherung existiert.

## RadiWorks-Verifikation

Ausgeführt mit der vorhandenen Projektumgebung, im Engine-Verzeichnis:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
$env:RADIOWORKS_HOME='C:\Users\Hubert111\Documents\Brainpower\audit-runtime'
& '.\.venv\Scripts\python.exe' -B -m pytest -p no:cacheprovider --basetemp 'C:\Users\Hubert111\Documents\Brainpower\audit-pytest-20260911' -q
```

Ergebnis: Exitcode 0; alle Testgruppen bis 100 Prozent erfolgreich. Eine nachfolgende Collection mit `--collect-only -p no:cacheprovider -o addopts='' -q` bestätigt **205 Tests**. Keine zweite Suite wurde dafür ausgeführt.

Eine Deprecation-Warnung betrifft die httpx-Verwendung durch Starlettes TestClient. Sie hat diesen Lauf nicht fehlschlagen lassen. Keine Dependency wurde verändert.

Die Test-Fixtures verwenden isolierte Verzeichnisse. Der Git-Status von RadiWorks war vor und nach dem Lauf identisch. Das ist ein Nachweis für die vorhandene automatisierte Suite, kein vollständiger interaktiver Browser-End-to-End-, Hardware-, Produktions- oder Aurelia-Integrationsnachweis.

## Hermes, Modelle und CC Switch

| Prüfung | Ergebnis | Aussagegrenze |
|---|---|---|
| `hermes chat --help` | Erfolgreich | CLI startet und bietet unter anderem `--query-file`, `--oneshot`, Modellwahl, Reasoning, Laufzeitbudget und Session-Wiederaufnahme. |
| `hermes profile list` | Ein Profil `default`, Modell `gpt-5.6-terra` | Kein separater Governor-Worker nachgewiesen. |
| `hermes gateway status` | Gestoppt | Der Gateway wird nicht allein für lokale UI-/CLI-Kommunikation benötigt. |
| Hauptmodell | `gpt-5.6-terra`, Provider `openai-codex`, Reasoning `medium` | Konfigurationsnachweis. |
| Delegation | `gpt-5.6-sol`, Provider `openai-codex`, Reasoning `medium` | Eine Delegationskonfiguration erzwingt noch keinen unabhängigen Review jedes Ergebnisses. |
| Modell- und Delegationsadresse | `http://localhost:3000/v1` | Der gelesene CLI-Code übernimmt die konfigurierte Basisadresse; ein frischer vollständiger Hermes-Modellaufruf wurde nicht ausgeführt. |
| CC-Switch-Prozess | Version 3.20.2, lokaler Listener auf Port 3000 | Prozess- und Portnachweis. |
| `GET /health` | HTTP 200 | Router erreichbar. |
| `GET /v1/models` | HTTP 200 | Modellverzeichnis erreichbar, keine Inferenzprüfung. |
| Governor-Kanban | 0 Aufgaben, 0 Runs | Kein laufender oder historischer Lauf auf diesem Board. Andere Hermes-Sitzungen sind davon nicht erfasst. |
| Hermes-Cron | 3 Jobs, alle deaktiviert | Keine dieser Definitionen ist eine aktive Fünf-Projekt-Überwachung. |

Die CC-Switch-Datenbank wurde ausschließlich im SQLite-Read-only-Modus abgefragt. Sie enthält historische erfolgreiche Terra- und Sol-Anfragen, aber auch Sol-Fehler mit HTTP 403. Die letzten gefundenen Zeitpunkte in diesen Gruppen sind: Terra HTTP 200 am 09.09.2026 10:50:00 UTC; Sol HTTP 200 am 11.09.2026 07:35:55 UTC; Sol HTTP 403 am 11.09.2026 12:53:11 UTC. Die vorhandenen Fehlermeldungen enthalten eine Upstream-HTML-Fehlerseite. Eine konkrete Ursache wurde damit nicht bewiesen.

Die Konfiguration enthält zudem einen Fallback-Anbieter. Die neue Oberfläche muss tatsächlich verwendete Modelle und einen etwaigen Fallback ausweisen; andernfalls könnte ein angeblich unabhängiger Sol-Review in Wahrheit aus einem anderen Ausführungspfad stammen.

Es wurden keine Zugangsdaten in diesen Bericht übernommen. Eine neue Inferenz, ein externer Serverzugriff oder eine Wiederherstellung wurde nicht durchgeführt.

## Tatsächliche Funktion der Governor-Skripte

- `Scan-ProjectMemories.ps1`: Liest das Manifest, prüft Gedächtnisordner und listet unmittelbar enthaltene Markdown-Dateien. Liest deren Inhalt nicht semantisch aus; aktualisiert die Matrix nicht; enthält keinen Überwachungsloop. Der Parameter `-Apply` wird nicht verwendet.
- `Dispatch-GovernorGoals.ps1`: Liest das Manifest, prüft Projektverzeichnisse und gibt Meldungen aus. Erstellt keine Kanban-Aufträge und startet keine Modelle. Der Parameter `-Apply` wird nicht verwendet.
- Die README beschreibt einen leistungsfähigeren Dispatcher als den vorhandenen Code. Ein Button darf deshalb nicht lediglich dieses Skript starten und anschließend „Auftrag erfolgreich beauftragt“ melden.

## Konsequenz für die Oberfläche

Die Oberfläche benötigt einen eigenen, belegbaren lokalen Steuerungsdienst: Datei-/Git-Beobachtung, Aufgabenlebenszyklus, Hermes-Anbindung, explizite Supervisor-Prüfung und nachvollziehbare Freigaben. Ein Dashboard, das nur die Freeze-Datei darstellt, erfüllt diesen Zweck nicht.

Der konkrete Entwurf steht in `GOVERNOR_OBERFLAECHE_ENTWURF.md`. Noch nicht implementiert sind die neue Oberfläche, ihr Hintergrunddienst und ein neuer automatischer Ausführungsloop. Die bestehenden Produktdateien und Freigaben wurden nicht geändert.

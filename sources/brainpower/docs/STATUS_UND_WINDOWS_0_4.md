# Status und Einrichtung auf einem anderen Windows-PC — 0.4

Stand 12.09.2026. Entwicklungsabschätzung: **etwa 55 Prozent des vereinbarten Gesamtumfangs**, grobe Bandbreite 50–60 Prozent. Das ist keine gemessene Testabdeckung und keine Prognose der verbleibenden Arbeitszeit. Oberfläche und Reviewbasis sind weit fortgeschritten; allgemeine Ausführung, Fortschrittssteuerung, Integration und Erstinstallation machen einen erheblichen Rest aus. Das zurückgestellte echte Terminal wird nicht als Pflichtumfang mitgezählt.

| Nr. der offenen Liste | Arbeitspaket | Stand / verbleibende Arbeit |
|---|---|---|
| 1 | Aufnahme und Beziehungen | Register/Rollen vorhanden; vollständige bestätigte Aufnahme aller fünf Mitglieder offen |
| 2 | Gruppenreview und Strategie | Bereichsreviews/Planentwürfe vorhanden; verbindliche Übernahme geprüfter Ergebnisse in Gruppenstrategie/Matrix offen |
| 3 | Ausführungsfreigaben | Planauswahl und gesonderte Pilotfreigabe vorhanden; allgemeine Produkt- und Folgenfreigaben offen |
| 4 | Rückübernahme | Isolierter Pilot geprüft; Erweiterung auf konkrete Produktumfänge offen |
| 5 | Korrekturschleifen | Begrenzte automatische Reparaturen mit unveränderten Akzeptanzkriterien offen |
| 6 | Fortschritt/Folgeschritte | Nachweis abgeschlossener Vorgänger und kontrollierte automatische Folgen offen |
| 7 | Rückfragen | Planung/Pilot-Patch umgesetzt; Anschluss an künftige Ausführungsadapter offen |
| 8 | Echtes Terminal | Auf Nutzerwunsch derzeit zurückgestellt; strukturierte Antworten reichen aus |
| 9 | Tests/Live-Adapter | unittest-Pilot und konfigurierte CDP-Ziele vorhanden; allgemeine projektspezifische Testadapter offen |
| 10 | Gedächtnis/Vault | Quellenzuordnung und Editor vorhanden; versionierte Strategieübernahme und kontrollierte Rückspiegelung offen |
| 11 | Projektlebenszyklus | Ordnerregistrierung/Gruppen vorhanden; neuer Projektaufbau und kontrollierte Pfadmigration offen |
| 12 | Automatik/Robustheit | Ein Worker, lokale Beobachtung und begrenzte bisherige Reviewautomatik vorhanden; vollständige Mehrgruppenbudgets/-abnahme offen |
| 13 | Darstellung | Hell/Dunkel/System umgesetzt und geprüft |
| 14 | Gesamtabnahme | Regressionen und synthetische Modellpiloten geprüft; vollständige Produktabläufe noch nicht abgenommen |
| 15 | Windows-Erstinstaller | Manuelles portables Setup vorhanden; automatische Voraussetzungeninstallation und Abnahme auf sauberem Fremd-PC offen |

## Kann ich die fünf Projekte reviewen?

Ja: Auf der Übersicht Supervisor Sol oder Astra wählen und **Alle Projekte reviewen** starten. Das sendet den kontrollierten Kontext der konfigurierten Projekte an die Modelle und speichert deren Review. Unter Projekte & Gruppen ist außerdem ein Review des gewählten Gruppen- oder Einzelumfangs möglich. Modellversandfreigaben und vorhandene Quellen müssen stimmen. Ein Modell- oder Routerfehler bleibt sichtbar; es gibt keinen stillen Fallback.

Die lokale Aktualisierung liest die dokumentierten Quellen und Entscheidungsregeln für die bestehende Matrix neu ein. Ein Hybridreview ist ein zusätzlicher Befund, keine automatische Produktfreigabe. Ein neuer Matrixplan benötigt die vollständige bestätigte Aufnahme jedes Mitglieds. Auch ein akzeptierter Planentwurf wird heute noch nicht automatisch zur verbindlich fortgeschriebenen Gruppenstrategie. Eine vollständige stabile Gesamtneuverifikation aller Produktfunktionen ist daher noch nicht zugesichert. Die echten Sol-/Astra-Nachweise in VERIFICATION_0_4.md betreffen kleine synthetische Fälle.

## Installation auf einem vorbereiteten Windows-PC

Das Paket `GovernorWorkbench-0.4.0-Windows.zip` enthält Oberfläche, Python-Backend, Tests, Dokumentation und Einrichtungsskripte. Es wurde entpackt und mit ausgewählten Integrationstests geprüft; ein zweiter physischer Windows-PC wurde nicht getestet. **Es ist noch kein Alles-in-einem-Erstinstaller.**

1. Auf dem Ziel-PC Python 3.11+ (Entwicklungsstand 3.12), Git und einen Browser bereitstellen. Für hybride Reviews zusätzlich eine funktionierende Hermes-Installation mit eigenem Python-Environment, CC Switch V3 und eine eigene Modellanmeldung einrichten. Fehlende Komponenten lädt dieses Paket nicht nach.
2. ZIP beispielsweise nach `C:\Tools\GovernorWorkbench` entpacken. Für neue Projekte ein frisches Paket verwenden; nicht das persönliche Backup samt Journal und Freigaben übernehmen.
3. PowerShell im entpackten Ordner öffnen. Den tatsächlichen Python-Pfad explizit verwenden, damit ein fehlender oder defekter `py`-Launcher keine Rolle spielt:

   ```powershell
   .\scripts\Install-Windows.ps1 -PythonExe 'C:\Pfad\zur\Pythoninstallation\python.exe'
   ```

   Das Skript prüft Python, erstellt `runtime-python.json`, legt eine noch fehlende `config.local.json` an und führt die lokalen Tests aus. Bei Fehlern zuerst den gemeldeten Grund beheben. Es startet den Dienst noch nicht.
4. **Vor dem ersten Start** `config.local.json` anpassen. Die Beispieldatei enthält die bisherigen fünf Projekte: diese Einträge durch die eigenen tatsächlich vorhandenen Projektverzeichnisse ersetzen. Keine alten fachlichen Gates oder fremden Freigaben übernehmen. Für ein eigenes Projekt genügt in der `projects`-Liste beispielsweise `{"id":"mein_projekt","name":"Mein Projekt","path":"C:/Projekte/MeinProjekt","depends_on":[]}`. Fehlende Statusfelder werden als ungeprüft initialisiert. Der Ordner muss zuvor vorhanden sein; ein Projektgerüst erzeugt der Governor noch nicht automatisch.
5. Eigenen `hermes_path` (tatsächliche hermes.exe), `codex_auth_path` (nur Pfad zur eigenen Anmeldung), `router_url` (`http://127.0.0.1:3000/v1`), `orchestrator_transport` (`hermes`), Terra/Sol oder Terra/Astra und `reasoning: "medium"` prüfen. `data_dir: "runtime"`, freien Port 8787 und die ressourcenschonenden Intervalle 15/60 Sekunden beibehalten. Alte `live_views` entfernen oder korrekt auf eigene lokale Testziele setzen. `governor_dir`, `snapshot_dir`, `vault_root` nur auf tatsächlich passende eigene Quellen setzen, sonst leer lassen. `legacy_review_egress_authorized` bleibt `false`, `staging_pilot_roots` bleibt `[]`.
6. Diagnose mit demselben Interpreter:

   ```powershell
   & 'C:\Pfad\zur\Pythoninstallation\python.exe' -m governor_workbench doctor --config config.local.json
   ```

7. CC Switch starten, dann `Start-Governor.cmd`. In der Oberfläche erst **Hermes prüfen** (null Werkzeuge), dann **Modelle prüfen** (echte synthetische Modellaufrufe, mögliche Kontingentkosten). Erst nach erfolgreichen Prüfungen echte Projektinhalte ausdrücklich zum Versand freigeben.
8. Projektquellen und Gedächtnis erfassen, Aufnahme prüfen und Anforderungen, Teststrategie, Abhängigkeiten sowie offene Nachweise bestätigen. Gruppen nur bewusst zuweisen; die Zugehörigkeit ist dauerhaft. Bei unvollständigem Kontext darf kein fertiger Matrixplan erwartet werden.
9. Autostart erst nach erfolgreicher Einrichtung gemäß `WINDOWS_INSTALLATION.md` aktivieren. Automatische Reviews auf neuen Installationen ausgeschaltet lassen, bis deren Umfang bewusst freigegeben wurde.

Der spätere vollständige Installer soll die Vorbereitung weitgehend übernehmen. CC Switch V3 bleibt ausdrücklich von der automatischen Installation ausgenommen. Ein persönliches Backup dient der Wiederherstellung des bisherigen Betriebs; es ist kein anonymisiertes Installationspaket für andere Nutzer.

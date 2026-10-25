# RadiWorks Cloud-/CI-Fähigkeitsnachweis – Implementation Plan

**Neue Betreiberentscheidung25.10.2026:** Cloudvergleich zurueckgestellt; HauptwegCLI/Desktop + GitHubCI + LinuxPilotserver freigegeben. Die frueherePflicht eines fertigenCloudvergleichs vorStrategieentscheidung ist ausdruecklich ueberholt. CP1 erfolgreich; weiter mit `2026-10-25-radiworks-ci-cp2a.md`. Keine neueMaterial-/Kostenfreigabe aus der Strategiewahl ableiten.

> **For agentic workers:** Execute this approved plan task-by-task using superpowers:executing-plans. Preserve the separate execution/cost gate.

**Goal:** Einen kleinen, tatsächlich ausführbaren Nachweis vorbereiten, dass die bestehende RadiWorks-Basis in einer frischen CI-VM gebaut und mit synthetischen Daten geprüft werden kann.

**Architecture:** Cloud dient künftig der Entwicklung, eine wegwerfbare CI-VM baut/testet, der VPS übernimmt später die Browserabnahme des gebundenen Artefakts. CP1 prüft zunächst Build, vorhandene Analyse-/Goldwert-/Katalogtests und synthetische REST-Analyse. CP1 ersetzt weder SQLite-Fix noch vollständige Regression, Browser-, Geräte-, Mandanten- oder Zielserverabnahme.

**Tech Stack:** Standard-library Python für Vorbereitung/Prüfer; bestehendes digestgebundenes Python-Image und hashgebundene Wheels; manueller GitHub-Actions-Job auf ubuntu-24.04. Keine neue Governor-Laufzeitabhängigkeit.

## Genehmigtes Design und Schutzgrenzen

Betreiberentscheidung 25.10.2026: neue Cloud-/CI-Strategie vorbereiten; alten Importlauf zurückstellen; vor kostenpflichtigen Läufen Umfang und Kosten zeigen. Keine Ausführungsfreigabe aus dieser Vorbereitung ableiten.

- Import I `4c6fc2ce83d6d9347e7181c7cb27bd515c046c0234337fd5d4ede5ff4626c220`, `prepared-v3`, bleibt ungestartet erhalten. Keine Marker, Mounts oder alten Pakete ändern. E1 bleibt bestehen; keine automatische Bereinigung.
- Private Quelle ausschließlich `redshift-three67/radiworks-pilot`, Commit `d1eb34260179a499e2b0362bf609ce96957b78aa` (`fix/saved-session-catalog`). `main` ist älter. Unveränderte Algorithmen und R6 bleiben erhalten.
- Kein Übertragen des Governor-Repositories, der Heimverzeichnis-Historie, lokaler Cloud-SQL-Definitionen, Datenbanken, Klientendaten, Medien oder Zugangsschlüssel.
- CP1 verwendet die bekannte alte SQLite-Basis ausschließlich isoliert/synthetisch für vorhandene serielle Funktionstests. Kein absichtlicher WAL-/Checkpoint-Stress, keine Übernahme als sichere Laufzeit. Der belegte SQLite-Fix bleibt Voraussetzung für CP2 und spätere Live-Aktivierung.
- Keine Veröffentlichung/Workflow-Installation, Ausführung, automatische Wiederholung, Security-Scan, Registry-Upload oder VPS-Änderung in diesem Vorbereitungspaket.
- Frühere VPS-Speichergrenzen werden nicht erhöht. Für die neue wegwerfbare CI-VM werden abweichende Ressourcen ausdrücklich im späteren Umfang ausgewiesen; kein heimliches Übertragen alter Freigaben.

## Dateien und Arbeitsschritte

Paketpfad: `runtime/rw-cloud-ci-capability-prep-20261025`.

- [x] Reine Zugangs-/Quellenprüfung speichern: Remote-Branch/Tree, lokale unveränderte Produktpfade, fehlende CI-Workflows, Dokumentationspreise. Netzwerkfehler des lokalen gh-Clients getrennt von erfolgreichem Connectorzugriff ausweisen.
- [x] `SOURCE_LOCK.json` aus kanonischen Git-Blobs des festen Commits ableiten und gegen den vollständigen Remote-Tree vergleichen; keine Produktkopie erzeugen.
- [x] `test_guard.py` zuerst schreiben und erwartetes Rot dokumentieren: Hashdrift, Zusatzdateien, Symlinks, Pfadflucht, Wheel-Abweichung, falscher Commit/fehlende Daten, JUnit-Fehler/Skips.
- [x] `guard.py`, `run-ci.sh`, `capability.yml` als ausschließlich lokale Kandidaten erstellen. Ein Job, nur workflow_dispatch, minimale Tokenrechte, SHA-gebundenes Checkout, keine Zugangsschlüssel/Artefaktuploads/Caches. 30 Minuten Jobfrist; begrenzte Einzelschritte; keine Wiederholung.
- [x] Offline-Tests und Bash-Syntaxprüfung ausführen. Der Windows-PC baut/startet keine Linux-Produktruntime. Unit-Tests sind keine native CI-Abnahme.
- [x] Unabhängigen Astra/medium-Review des begrenzten Pakets einholen, Befunde beheben und betroffene Tests erneut prüfen.
- [x] Aktuellen Einstieg aktualisieren; alte eingefrorene Belege unangetastet lassen. Neue Paketidentität und präzise verbleibende Gates speichern.

## Vorgesehener erster Lauf – erst nach eigener konkreter Freigabe

1. Privates CI-Kontrollpaket veröffentlichen, ohne automatischen Trigger. Veröffentlichungscommit und Paketbytes vor Dispatch erneut binden. Veröffentlichung allein ist keine Startfreigabe.
2. Genau ein manueller CP1-Job: frische Standard-Ubuntu-24.04-x64-VM (private Repositories laut GitHub: 2 vCPU, 8 GB RAM, 14 GB SSD; Verfügbarkeit/Kontingent vor Start prüfen), maximal 30 Minuten. Docker-Build ist durch die gesamte VM und Zeit begrenzt, nicht durch die alten VPS-cgroups.
3. Nur festes Basisimage und 34 bereits gebundene Wheels laden, Hashes/Paketliste prüfen; bestehendes Dockerfile unverändert/netzlos bauen. Downloadcontainer maximal 1 CPU/1 GiB/128 Prozesse. Tests in einem netzlosen Container, read-only Quellmounts/Root, maximal 1 CPU/1 GiB/128 Prozesse, 256 MiB tmpfs, 360 Sekunden.
4. Vorhandene Tests `test_analysis.py`, `test_rates.py`, `test_gold_parity.py`, `test_bootstrap.py`. JUnit muss Tests > 0, Fehler = 0, Fehlschläge = 0 und Skips = 0 ausweisen. Syntaxprüfung der vorhandenen Web-JS/MJS mit vorhandener Node-Laufzeit. Kein Headless-/interaktiver Browsernachweis in CP1.
5. Nur begrenzte Test-/Versions-/Image-/Hashzusammenfassung im privaten Jobprotokoll. Kein Imageexport, Registry-Push, Artefaktupload oder Cache. Kostenpflichtiges Wiederholen braucht neue Abklärung.

GitHub-Listenpreis am 25.10.2026: Linux x64 Standard 2-Core **0,006 USD/Minute**; 30 Minuten ergeben **0,18 USD reine Runnerzeit**, falls kein Inklusivkontingent verfügbar ist. Rundung je Job und mögliche Abbruchverzögerung beachten: keine Cent-genaue Gesamtkostengarantie. Kontoplan, Restminuten, Steuern und Kontosperren sind noch unbekannt. Keine zusätzlichen Security-/Modell-API-Läufe in CP1.

Codex Cloud: separates vorbereitetes Nur-Lese-Probeskript; **noch keine Cloud-Umgebung/Task gestartet**. Preis/Restguthaben nicht aus API-Tokenpreisen ableiten. Docker-Daemon-/Headless-Browser-Verfügbarkeit im konkreten Cloud-Konto bleibt unbewiesen; deshalb hängt CP1 nicht von dieser Annahme ab.

## Folgereihenfolge

CP1 messen → CP2 korrigierte SQLite-Bibliothek, tatsächliche Loaderbindung, vollständige Python-/JS-/synthetische Browserregression und Fehler-/Recoveryfälle → Imageidentität/gezielte VPS-Stagingprüfung → Betreiber-Livetest → RadiWorks-Restpunkte in getrennten Paketen. Gemeinsame CI-Verträge danach für weitere Module wiederverwenden. P3/P4/P5, zentrale DB-Entscheidung, Modul_Templates/Governors und Aurelia bleiben eigenständige Produktgates.

## Offizielle Grundlagen

- https://learn.chatgpt.com/docs/environments/cloud-environments
- https://learn.chatgpt.com/docs/pricing
- https://docs.github.com/en/actions/reference/runners/github-hosted-runners
- https://docs.github.com/en/billing/reference/actions-runner-pricing

Vorbereitungsstand: CP1-Paket 223d933c1e69b2d9a6128f9a00a8a784e6510ca5b4c8764873dcb0f294b7e73f; 21 lokale Tests, 0 Fehler/Skips, 3 Python-/2 Bash-Syntaxprüfungen. Noch kein nativer Lauf. Untersuchung zunächst auf höchstens vier aktive Arbeitsstunden begrenzt; das ist eine Entscheidungsgrenze, keine zugesagte Fertigstellungszeit.

Unabhängiger Astra/medium-Abschlussreview: keine offenen konkreten P1/P2-Befunde. Genau ein neuer Dispatch ist organisatorisch zu zählen; run_attempt==1 sperrt nur Re-runs desselben Runs. Alle Ausführungs-/Kontingent-/Produktgates bleiben offen.

## Verbindliche Betreiberpräzisierung: zwei praktische Vergleichstests

Am 25.10.2026 präzisiert: zunächst CP1 wie vorbereitet; danach zusätzlich ein praktischer Test „Codex Cloud plus Linux-Pilotserver“. Erst anschließend entscheidet der Betreiber über die weitere Strategie. Diese Präzisierung hat Vorrang vor der bisherigen direkten Folge CP1 → CP2; Sicherheits-/Produktgates entfallen dadurch nicht.

- **A / CP1:** vorhandenes CI-Paket, unveränderter Umfang und gesonderte noch offene Veröffentlichungs-/Kosten-/Startfreigabe.
- **B / Cloud plus Pilotserver:** nach A ein eigenes, begrenztes Ausführungspaket konkret vorbereiten. Ein echter Cloud-Arbeitsschritt und die tatsächliche überprüfbare Übergabe bzw. Steuerung zum Linux-Pilotserver gehören zum Nachweis; allein Dokumentenvergleich oder cloud-audit genügt nicht. Verfügbarkeit/Netz-/SSH-/Dockerrechte und sichere Zugangsmethode zunächst belegen; fehlende Fähigkeiten ausdrücklich als Testgrenze ausweisen, keine erfolgreiche Kopplung behaupten. Keine neue Build-VM oder Ausweitung bestehender Serverbudgets daraus ableiten.
- **Vergleichbarkeit:** nach Möglichkeit derselbe gebundene RadiWorks-Quellstand und dieselben synthetischen Tests; Abweichungen der Bibliotheken/SQLite-Kandidaten und Ressourcen dokumentieren. Laufzeit, tatsächlich erreichte Funktionen, Artefakthashes, Sicherheit/Isolation, Abbruch-/Abschlussverhalten sowie gemessene Kosten und manuellen Pflegeaufwand gegenüberstellen. Ein Test mit bekannter alter SQLite-Basis bleibt ausschließlich isoliert/synthetisch und ohne zusätzlichen WAL-Stress; keine Live-Aktivierung ableiten.
- **Abgrenzung:** GitHub Actions als Ausführungsplattform und GitHub als Quellhosting getrennt beurteilen; Cloudzugang ohne GitHub nicht ungeprüft voraussetzen. Für B tatsächliche Konto-/Plattformmöglichkeiten und Kosten frisch prüfen. Vor kostenpflichtiger Cloud-Einrichtung oder Server-/Materialstart den konkreten Umfang und Kosten vorlegen und bestehende Freigabegrenzen wahren.
- **Danach:** Betreiber entscheidet anhand A und B. Erst mit dieser Entscheidung den Ausführungsweg für CP2/SQLite-Fix, volle Regression, Staging und Livetest festlegen. B ersetzt weder diese fachlichen Abnahmen noch P3/P4/P5 bzw. die zentrale DB-/Modulentscheidung.

In dieser Präzisierung wurden nur Plan/Status gespeichert; kein neuer Cloud-/CI-/Server-/Securitylauf und keine Veröffentlichung begonnen.

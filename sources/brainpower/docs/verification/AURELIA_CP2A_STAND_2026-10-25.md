# Aurelia und RadiWorks – Stand nach CP2A am 25.10.2026

## Ergebnis des freigegebenen Laufs

Genau ein neuer CI-Lauf wurde gestartet: [40196634387](https://github.com/redshift-three67/radiworks-pilot/actions/runs/40196634387), Workflow 395985265, Versuch 1, Ereignis workflow_dispatch. Der tatsächliche Kontrollcommit war der freigegebene `7058764d9ef899535b3fabc672967f5dfb1474ca`; Produktreferenz unverändert `d1eb34260179a499e2b0362bf609ce96957b78aa`. Der Betreiber hat die nicht atomare Auflösung der Referenz main ausdrücklich akzeptiert; keine unveränderliche Dispatch-Bindung behaupten.

Der Lauf scheiterte an CRLF-Zeilenenden beim ersten `set -euo pipefail` in run-ci.sh, Exit 2. Noch kein Source-Guard, Arbeitsverzeichnis oder Trap; kein Docker-Aufruf, Pull, SQLite-Download, Build oder Probe. Beide Checkouts und ihre Post-Schritte erfolgreich. Vollständiger VM-Teardown nicht unabhängig attestiert. Einmalfreigabe verbraucht; kein Retry. Produktdateien, laufende Pilotinstanz und Serverkonfiguration wurden durch diese Arbeit nicht geändert. Das ist kein bestandener SQLite- oder Funktionsnachweis.

Die frühere Prüflücke war Teil unserer Vorbereitung: bash -n führt set nicht aus; die Cleanup-Tests lesen textnormalisiert und ersetzen den Scriptstart. Git Bash akzeptiert auf diesem Windows-System CRLF auch bei ausgeschaltetem igncr. Seine Startup-Prüfung allein ist kein Linux-Nachweis.

## Begrenzte lokale Korrektur

Separater Kandidat: runtime/rw-ci-cp2a-lf-fix-prep-20261025. Ausschließlich run-ci.sh (111 CR entfernt) und build-sqlite.sh (23 CR entfernt) sind exakt CRLF→LF konvertiert. Die zehn übrigen operativen Dateien und vier vorhandenen Testdateien bleiben bytegleich. Sieben neue Tests prüfen Rohbytes/CR/BOM, die Abweisung beider Originale und einen begrenzten Headerstart. Der erste Rotlauf dokumentiert die Git-Bash-Grenze; der korrigierte Prüfaufbau zeigt vor der Korrektur sieben Tests mit vier erwarteten Fehlern. Anschließend 65 Tests ohne Fehler/Skips sowie zwei Shell-Syntaxprüfungen erfolgreich. Native Build-/Loader-/Optionsparität bleibt offen.

Unabhängiger Astra/medium-Review bestätigt Fehlerursache, rein bytebegrenzten Delta und Paketbindung; kein konkreter Blocker zur Vorlage einer neuen Freigabe. Kein erneuter CI-Lauf oder weitere Veröffentlichung erfolgt. Paket-SHA256: `290997bf071d3c5a3aa5d7e5a6c8279da01ff2a343990faccb31be92ac583dfb`.

## Strategie und nächste Reihenfolge

Beschlossen bleibt: Codex CLI/Desktop steuert, privates GitHub CI baut und prüft, der getrennte Linux-Pilotserver erhält anschließend gebundene Artefakte für Browser-, Workflow- und Betriebsprüfungen. Cloudvergleich und alter Import-I-Lauf bleiben zurückgestellt. Keine zusätzliche Build-VM. Der Test-VPS nimmt Module schrittweise auf; er muss nicht den vollständigen Mehrmodulbetrieb tragen. Die umfassenden 25-Nutzer-/Mischlast-/Kapazitätsprofile gehören später auf den gesondert geprüften Hauptserver. Keine automatische Mandanten-, Produktions- oder Integrationsfreigabe durch Einzeltests.

Nächster konkreter Schritt: neue ausdrückliche Freigabe für einen privaten Commit mit genau den beiden LF-Korrekturen und genau einen weiteren manuellen CI-Lauf bis 30 Minuten, einschließlich der erneut offengelegten main-Referenzgrenze und Commitabgleich vor/nach Start. Vor Ausführung Kontingent und Zielstand prüfen; bei unbekanntem Ausgang nicht erneut senden. Danach, nur bei erfolgreichem CP2A-Nachweis: CP2B mit vollständiger Regression, optionalen CPU-Profilen getrennt, Browser-/Recoveryprüfungen; anschließend gebundene Artefaktübernahme und Nutzerabnahme auf dem Pilotserver. Diese Folgegates sind noch nicht ausgeführt.

## Fortschritt der aktuellen CI-Strecke

| Schritt | Stand | Aussagegrenze |
|---|---:|---|
| CP1: begrenzter CI-Fähigkeitsnachweis | 100 % | Erfolgreicher früherer Lauf: 33 Tests, 55 JS-Syntaxprüfungen, Originalbuild; keine Vollabnahme |
| CP2A: ursprüngliche Vorbereitung und Veröffentlichung | 100 % durchgeführt | Der native Lauf hat trotz lokaler Tests eine Prüflücke nachgewiesen |
| CP2A: LF-Reparatur lokal vorbereiten/testen/reviewen | 100 % dieses begrenzten Pakets | Noch nicht veröffentlicht oder nativ geprüft |
| CP2A: erfolgreicher SQLite-Build und Loader-/Optionsnachweis | 0 % bestanden | Lauf vor Beginn dieser Stufen abgebrochen |
| CP2B und neue Artefakt-/Pilotübernahme | Noch nicht begonnen | Historische RadiWorks-Pilotnachweise bleiben eigenständige Belege |

## Gesamtphasen – belegter Arbeitsstand

Für P0–P7 fehlt eine nachvollziehbare Aufwandsgewichtung der erledigten und offenen Teilaufgaben. Deshalb sind dafür derzeit keine belastbaren Arbeitsprozente vorhanden. RadiWorks-Testergebnisse ergeben insbesondere keinen Prozentfortschritt der Explorer-/Thom-Referenzumgebungen in P1/P2. Bezifferbar sind die oben benannten abgeschlossenen Prüfschritte sowie die sieben von sieben im Bestand aufgeführten Module; das ist keine vollständige Funktionsabnahme. Primäre Basis ist der konsolidierte Phasenplan mit seinen P3-Teilbelegen, ergänzt um die aktuelle CI-Strategie und diesen Lauf.

| Phase | Belegter Arbeitsstand / Prozentgrenze | Bereits vorhanden | Für den Abschluss noch erforderlich |
|---|---:|---|---|
| P0 – Quellen, Referenzen, Machbarkeit | Teilweise belegt; Arbeitsprozente unbekannt | Sieben von sieben Modulen im Bestand aufgeführt, Baselines/Abhängigkeiten und viele Prüfquellen dokumentiert; RadiWorks-Pilotbasis vorhanden | Offene Original-/Hardware-/Versionsgrenzen und Zielumgebungen vollständig binden |
| P1 – Strukturtreue Referenzumgebungen | Vorbereitet; vollständige Explorer-/Thom-Abnahme offen | Infrastruktur und Quellen; RadiWorks-Pilot ist ein separater Vorläufer | Explorer mit Copen/Bohm und Thom samt tatsächlich benötigten Backenddiensten isoliert reproduzieren; keine komplette Umgebung dafür abgenommen |
| P2 – Funktion und Parität | Teilreferenzen; vollständiger Abschluss offen | Begrenzte Originalproben der weiteren Module; historische RadiWorks-Referenz separat | Persönliche CPU-/Numerik- und Viermodiparität, aktive Dienste, Fehler-/Restart-/Medienwege und weitere Originalreferenzen schließen |
| P3 – Sechs Modul-Reasonings | Umfangreiche Teilbelege; Arbeitsprozente unbekannt | Quellen-/Workflow-/Datenverträge und Teilreferenzen für Radi144, Morphic, RMF und Lovable-Module | Restliche Original-/Runtimebelege; Morphic-Quellentscheidung und Grenzen; RadiFarben-RMF-Originalabnahme bleibt zunächst zurückgestellt |
| P4 – Gemeinsame Bedarfsmatrix | Bestand konsolidiert; finale Matrix offen | Siebenmodulbestand, Domänen und Anforderungen mit Aurelia/Modul_Templates | Vollständig gegengeprüfte Writer-/Rechte-/Job-/Asset-/Betriebsmatrix und entscheidungsreife Alternativen |
| P5 – Zentrale Datenstruktur | Vorbereitet; noch kein endgültiger Beschluss | Anforderungen, Verantwortungsfragen und technische Optionen | Ausdrückliche Entscheidung über Identitäten, Rechte/Abo, Jobs, Revisionen, DB/Objekte/Zeitreihen, Restore und Betrieb |
| P6 – Aurelia-Kern und Modul_Templates | Grundlagen vorhanden; neuer Zielvertrag offen | Bestehende Grundlagen und normative Vorlagen | Neue beschlossene zentrale Verträge implementieren, Templates abstimmen und Rechte-/Restorebelege führen |
| P7 – Module integrierbar vorbereiten | RadiWorks-Pilot fortgeschritten; keine vollständige Adapterabnahme | RadiWorks als weitester funktionaler Pilot; Quellen der übrigen Module | Je Modul versionierter Adapter, gemeinsame UX-Verträge, Regression, Rechte/Recovery und Betreiberabnahme |
| P8 – Gemeinsame Plattformabnahme | 0 % als Gesamtplattform bestanden | Einzelne Modul-/Infrastrukturtests sind Vorarbeiten | Echte Mandanten-/Abo-/Mehrmodul-/Last-/Restore-/Zielserverabnahme; keine Ableitung aus Einzelpilot |

Die Plattform ist noch keine produktionsreife Mehrmandantenintegration. Bestehende RadiWorks-Funktionalität und deren frühere Tests dürfen nicht mit dem heutigen CI-Nachweis verwechselt werden: Die gespeicherte Pilotbaseline weist 897 erfolgreiche Python-Tests, 19 übersprungene Python-Tests und 100/100 erfolgreiche JS-Tests aus; diese wurden heute nicht erneut als Produktsuite ausgeführt. Die 65 Tests dieses Reparaturpakets sind Infrastruktur-/Helferprüfungen.

Die Entscheidung über die zentrale Datenstruktur folgt nach dem Schließen der entscheidungsrelevanten P3-Lücken und der P4-Gegenüberstellung. Sie hängt nicht davon ab, sämtliche späteren Bedienerweiterungen oder die vollständige Hauptserverlast schon umzusetzen.

## Weiterhin eingeplante Anforderungen

RadiWorks: persönliche CPU-/Viermodireferenz und Stochastik; CopyGuard-Erklärung und begrenzter Admin-Testmodus; Vollkatalog-/Ergebnissuche, Sortierung, Buttonzustände und Resonanzliste; TXT/XLSX-Import mit Vorschau, Rechten, Revision und CopyGuard; optionale Ergebnisse über 105 ohne Änderung des Standardalgorithmus; manuelle Listen mit Impuls/Pause/Wiederholung und getrennte Analyserundenschleife; Medien-, Langlauf- und Recoveryabnahme. Nicht als bereits umgesetzt ausgeben.

Aurelia/Module/Templates: zentrale Administration/Therapeuten/Abos/Status/Ressourcen/Services, modulübergreifende Favoriten/Trends/Archive und kontrollierte Trigger, systemweiter Frequenzgenerator/Frequenzreihen, verlustfreie Originalmedien mit fünf versionierten Layern und sichtbarer oberster Ebene, Audioverwaltung, PDF/OCR-/XLSX/XLS-/JSON-Import/Export sowie Tenant-/Modul-/Jobrechte und gemessene Ressourcenbudgets. RadiFarben richtet sich nach der höchsten zentralen RMF-Ausgangsversion; weitere Versionen bleiben bis zur Integration versioniert übernehmbar. Keine echte Klientenmigration oder Algorithmusersetzung.

## Gültige LLM-Route

Dies bestätigt die bestehende Projektvorgabe, keine neue Aussage über Modellverfügbarkeit, Preise oder eine technisch erfolgte Hauptchatumschaltung.

| Aufgabe | Freigegebene Auswahl |
|---|---|
| Zusammenführung geklärter Belege, normale Testplanung, normale Abgleiche | GPT-6.1 Sol / medium |
| Fehlerketten, Recovery, Nebenläufigkeit, Sicherheit, Mandanten-/Rechte-/Daten-/Jobverträge | GPT-6.1 Sol / high |
| Begrenzte Inventar-/Schema-/Tabellenextraktion | Luna / low oder medium mit unabhängiger Quellen-/Hashprüfung |
| Anspruchsvolle begrenzte Konsistenzprüfung mit konkretem Zusatznutzen | Luna / max |
| Unabhängige kritische Schlussprüfung | Astra / medium |
| Kritischer ungelöster Widerspruch | Astra / high nur ausdrücklich gewählt |

Im heutigen Fehler-/Korrekturpaket wurde Astra/medium für die unabhängigen Prüfungen verwendet; keine Luna-Delegation, kein neuer Hermes-Anwendungsauftrag, keine behauptete Änderung der Hauptchat-Laufzeiteinstellung. Der aktuelle Fehler-/Freigabeblock ist Sol/high-geeignet; reine Zusammenführung geklärter Befunde ist medium-geeignet.

## Quellen und Grenzen

- [Native Laufdaten und vollständiges Protokoll](../../runtime/rw-ci-cp2a-execution-20261025/RESULT.json), [unabhängige Fehlerprüfung](../../runtime/rw-ci-cp2a-execution-20261025/NATIVE_FAILURE_REVIEW.json).
- [LF-Delta](../../runtime/rw-ci-cp2a-lf-fix-prep-20261025/EOL_DELTA.json), [lokale Prüfung](../../runtime/rw-ci-cp2a-lf-fix-prep-20261025/LOCAL_VERIFICATION.json), [neuer konkreter Umfang](../../runtime/rw-ci-cp2a-lf-fix-prep-20261025/APPROVAL_SCOPE.json).
- [Gesamtplan, insbesondere P0–P8 und offene Anforderungen](../superpowers/plans/2026-10-10-aurelia-module-lokale-referenz-und-datenstruktur.md), [Mandanten-/Kapazitätsplanung](../AURELIA_MANDANTEN_KAPAZITAET_2026-10-16.md), [gültige Chatroute](../CODEX_CHAT_VARIANTE_B.md).
- Letzte vom Betreiber abgelesene GitHub-Werte vor diesem Lauf: 2/2.000 Actions-Minuten und 0/0,5 GB Storage. Der kurze Einjoblauf dürfte auf eine Inklusivminute gerundet werden; aktueller Abrechnungsstand nicht erneut abgelesen, keine Rechnungsgarantie. Neuer vorgeschlagener Lauf voraussichtlich 0 USD zusätzlich im verbleibenden Kontingent; nominell 0,18 USD für 30 Minuten ohne Inklusivminuten nach gespeicherter Tarifprüfung, kein harter Kostencap.
- Lokale Speicherstichprobe nach dem Lauf: C: 9,30 GiB, F: 358,53 GiB frei. Keine Verschiebung/Löschung oder Laufwerksänderung in diesem Paket; keine vollständige Verursacherzuordnung.

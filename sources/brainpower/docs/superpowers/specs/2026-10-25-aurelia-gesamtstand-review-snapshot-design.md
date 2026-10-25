# Aurelia/Brainpower: vollständiger Projektstand für Sicherung und Review

Stand: 25.10.2026. Bestandsbefund und konkreter Entwurf; noch kein erstellter Gesamtsnapshot, kein neues GitHub-Repository und keine Veröffentlichung. Die Betreiberergänzung verlangt ausdrücklich den gesamten Projektverbund einschließlich Governors, Plattform, Modul_Templates, Module und deren Templates, Serverstand, Anforderungen und geplanter Integrationen. Teilpakete dürfen nicht als Gesamtclone bezeichnet werden.

## 1. Nachgewiesener Ausgangspunkt

- Brainpower hat keinen eigenständigen Git-Root: Git löst auf `C:/Users/Hubert111` auf. Die auf `Documents/Brainpower` begrenzte Indexabfrage enthält genau eine Spezifikationsdatei. Ein Clone dieses übergeordneten Repositories wäre weder ein vollständiger Brainpower-Export noch eine geeignete Datenschutzgrenze.
- Die aktuelle Metadateninventur zählt in `governor_workbench` 64 Dateien und in `tests` 129 Dateien, ohne Caches. Das ist eine Bestandszählung, kein frischer Funktionstest oder Vollständigkeitsnachweis für alle externen Komponenten.
- Die transportablen Workbench-Releases schließen laut Entwickleranleitung externe Produktrepositories, Laufzeitdaten und echte Review-Payloads aus. Die vorhandene 0.5.0-ZIP ersetzt deshalb keinen Projektverbund-Snapshot.
- `artifacts/latest-full-backup.json` verweist auf einen Workbench-0.4.0-Backupstand vom 12.09.2026. Zusätzlich existieren neuere F:-Archivverzeichnisse vom 09.10.2026. Weder deren heutige Hashintegrität noch die Abdeckung aller Änderungen bis 25.10.2026 wurde hier erneut bewiesen.
- Der aktuelle CP2A-Checkpoint erfasst einen begrenzten RadiWorks-/CI-Arbeitsblock. Er ist kein vollständiger Plattform- oder Serverclone.
- Frische Git-Metadaten zeigen Änderungen in allen fünf untersuchten externen Git-Bäumen: Aurelia, RadiWorks, Modul_Templates, Radi144 und Morphic-Root. Beobachtete getrackte Pfadzahlen: 161 / 15.835 / 14 / 218 / 610. Die mit `--untracked-files=normal` gezählten NUL-Einträge sind keine vollständige Dateiinventur: ungetrackte Verzeichnisse können zusammengefasst und Rename-Einträge mehrteilig sein. Die Arbeitsstände müssen zusätzlich zum Commit gesichert werden.
- Der lesende Stat-Aufruf auf `F:/Hauptprojekt/Governors/20261009-005558/COMPLETE.txt` scheiterte mit WinError 5. Das Archivverzeichnis ist sichtbar, sein Abschlussmarker wurde nicht gelesen. Weitere Archivmarker wurden in diesem abgebrochenen Aufruf nicht geprüft; daraus folgt weder Defekt noch Vollständigkeit des Archivs. Keine ACL-Änderung oder Umgehung vorgenommen.
- Aktuelle Freiplatzstichprobe: C: 9,15 GiB, D: 10,32 GiB, E: 5,62 GiB, F: 358,53 GiB. Noch keine Größenbilanz des Gesamtclones, keine Reservierung oder Dateiverlagerung.

## 2. Vollständiger Pflichtumfang

| Bereich | Einzubeziehender Stand | Aktueller Nachweis / offene Grenze |
|---|---|---|
| Governors / Brainpower | Workbench-Code, UI, Tests, Werkzeuge, Verträge, Dokumentation, Gedächtnisse, Anforderungen, Entscheidungen, Prüfbelege und Wiederaufnahme | Quellen lokal vorhanden; keine eigenständige Git-Historie für den vollständigen aktuellen Workbench-Baum nachgewiesen |
| Externe Governors und Steuerung | `Documents/Radiworks/governors`, zugehörige Skripte, Manifeste und Governance-Referenzen; erforderliche Hermes-/Routerverträge und Versionen | Externes Governors-Verzeichnis vorhanden; geheime Authentisierung bleibt ausschließlich im geschützten Sicherungsteil |
| Aurelia | Plattformcode, Migrationen, UI-/Designreferenzen, Server-/API-Verträge, Tests, aktive Arbeitsstände und geplante Integrationen | Eigener Git-Root; beobachteter HEAD `8706186af01e10e4253e25abb31bf3577110dae4`; aktuelle Dateien sind zusätzlich zu Git zu sichern |
| Modul_Templates | Gemeinsame Standards, Registry, alle Modulverzeichnisse, additive Nachträge, lokale Profilentwürfe, Adapter und Referenzen | Eigener Git-Root; beobachteter HEAD `041ae65ee5ff2a7aa4a0cc0a1bd82666e4e3ac04`; vorhandenes `modules/radiworks` belegt keine fertigen Templates für alle übrigen Module |
| RadiWorks | Kanonischer lokaler Baum, dessen Templates und Governors, freigegebene Produktstände, aktueller GitHub-Pilot, CI-/Docker-Dateien sowie unveröffentlichte Kandidaten getrennt | Lokaler Git-HEAD `866f52146ad212157bfb20c9852714cb307a3b12`; CI-Produktpin `d1eb34260179a499e2b0362bf609ce96957b78aa` ist ein eigener Bezug |
| Radi144 | Quellbaum, Tests, Templates, Berechnungs-/Workflowverträge, synthetische Referenzen und Dokumentation | Eigener Git-Root; beobachteter HEAD `b8ac33a1360f1cb56f06e602fcd37cbda2a9c641` |
| RadiMorphic | Root und registrierter Worktree als getrennte Quellen, alle jeweiligen Templates und Verträge | Root-HEAD `411ff09ff8964f820b7d15839994b1ad3502675a`; Worktree-HEAD in dieser Prüfung durch Timeout unbekannt; keine automatische Auswahl eines autoritativen Standes |
| RadiFarben | Original-ACCDB geschützt bytegetreu, vorhandene Text-/VBA-/Formular-/Query-/Schemaexporte mit Versionsbindung, RMF-Workflows und offene Abnahmegrenzen | Aktuelle ACCDB-Metadaten: 86.585.344 Bytes, abweichend vom älteren Bericht; kein frischer Hash-/Semantiknachweis. Höchstes zentrales RMF ist die Entwicklungsbasis; weitere RMF-Versionen bleiben separat |
| Copen / Bohm | Gemeinsame Explorer-Anwendung mit beiden Modulen, allen Varianten, Templates, Migrationen, Funktionen, Assets und Backendverträgen | Historischer Pin `c69d5aa224018b0484efd90ae456a10aecc78a77`; öffentliche Originalquelle `radiquant/resonance-research-explorer` lesbar. Geschützte lokale Kopie aktuell mit Zugriff verweigert |
| Thom | Eigene Anwendung, Templates, Migrationen, Funktionen, 3D-/Audio-/Assetreferenzen, Backend- und Hardwareanforderungen | Historischer Pin `18e6c12c238985da698f9a46743d893b30d61ba7`; öffentliche Originalquelle `radiquant/morpho-field-nexus` lesbar. Lokaler geschützter Stand nicht frisch verifiziert |
| Linux-Pilotserver | System-/Paket-/Dienstversionen, effektive Units, Ressourcenlimits, Container-/Imageidentitäten, Netz-/IPv4-/Proxy-/Storage-/Mount-/Backupkonfiguration, persistente Datenschemata, Betriebs-/Restoreanleitung | Bisherige Belege lokal vorhanden; kein frischer vollständiger Serverabzug in diesem Auftrag. Websiteprojekt nur hinsichtlich gemeinsamer Hostgrenzen, ohne dessen fremde Projektinhalte |
| Geplanter Hauptserver | Hardwareziel, Betriebssystem-/GPU-/Treiberanforderungen, Speicher-/Netz-/Restore-/Lastziele und Abgrenzung zum Test-VPS | Planungsstand getrennt vom tatsächlich installierten Pilotserver und vom aktuell nicht verifizierten früheren Root |
| Integration und Gesamtanforderungen | P0–P8, zentrale Datenstruktur, Mandanten/Abo/Rechte, Jobs/Events/Assets, Ressourcenmessung, Modulverträge, bekannte Lücken, Benutzerwünsche und Freigaben | Geplant, implementiert, getestet und abgenommen bleiben getrennte Zustände; Snapshot erzeugt keine neue Integrationsfreigabe |

Die Quellenliste ist vor Export gegen tatsächliche Projektregistrierung, eigene Git-Roots, Worktrees, Submodule, LFS-Verweise, verlinkte Pflichtassets und Dokumentverweise abzugleichen. Fehlende Einträge werden als Lücke erfasst und nicht durch angenommene Gleichheit ersetzt.

## 3. Geeignete Form: geschützte Sicherung plus lesbares Review-Repository

**Empfehlung:** Zwei zusammengehörige Ausgaben mit einer geschützten Zuordnung und getrennten Manifesten. Das vollständige Sicherungsmanifest bleibt geschützt; das Reviewmanifest enthält ausschließlich veröffentlichbare Metadaten. Auch Dateinamen, Pfade, Hashes, Ausschlusslisten und Belegberichte unterliegen der Veröffentlichungsprüfung. Für ausgeschlossene Geheimnisse und persönliche Inhalte nennt die Reviewfassung nur neutrale Kennungen/Kategorien und die Abdeckungsgrenze, keine sensiblen Originalpfade oder Geheimnishashes.

1. **Geschützter Erhaltungsstand:** Bytegetreue Originalquellen und erlaubte Originalartefakte, lokale Änderungen, erforderliche Git-Objekte/Refs, Originaldatenbanken und persönliche Konfiguration ausschließlich unter geeignetem lokalem Zugriffsschutz. Geheimnisse und Datenbanken werden nicht an Reviewmodelle oder ins GitHub-Repository gegeben. Konsistente laufende Datenbanken benötigen ein geeignetes Online-Backup bzw. einen gesondert kontrollierten Sicherungsweg; kein blindes Kopieren von DB/WAL-Dateien und keine automatische Writer-Unterbrechung. Für vollständige Maschinenwiederherstellung ist zusätzlich ein geeigneter Server-/Providerbackupweg erforderlich.
2. **Privates Review-Repository:** Alle freigegebenen Quelltexte, Templates, Schemas/Migrationen, Tests, Abhängigkeitsbindungen, Architektur-/Workflow-/Anforderungsdokumente und zulässigen Prüfbelege. Persönliche Konfiguration wird als eindeutig gekennzeichnete, nicht direkt ausführbare bereinigte Darstellung abgebildet. Nicht veröffentlichbare Quellen erhalten einen präzisen Eintrag mit Grund, lokalem Nachweis und Auswirkung auf die Reviewabdeckung. Keine Behauptung, ein bereinigter Reviewstand sei eine bitgleiche Komplettsicherung.

Zum Erhalt gehören auch die ermittelten historischen Baselines, Kandidaten, Ref-/Tagstände und relevanten F:-Archive, insbesondere die genannten Governors- und Aurelia-Archive. Sie werden explizit inventarisiert und im lesbaren erlaubten Umfang hashgeprüft; Originalarchive bleiben unverändert. Bereits vorhandene Archive werden nicht allein aufgrund ihres Namens oder eines alten Abschlussmarkers als erneut verifiziert ausgegeben. Jeder nicht aufgenommene historische Pflichtstand erhält einen begründeten geschützten Inventareintrag. Arbeitsbaum, separat gespeicherter Indexinhalt und Git-Historie/Refs müssen getrennt rekonstruierbar bleiben; ein Patch gegen HEAD allein genügt dafür nicht. Ein kompletter persönlicher Profil-Git-Root gehört nicht zum Projektexport.

Alternativen: Ein reiner Git-Clone verpasst ungetrackte Dateien, externe Quellen und Runtimezustände. Ein ungefilterter Komplettupload vermischt Quellcode mit Geheimnissen, Falldaten und historischen Berechtigungsgrenzen. Beide erfüllen das Ziel nicht.

Vorhandene Freigaben für geschützte Live-SQL-Definitionen erlauben ausschließlich die damalige begrenzte lokale Speicherung und keinen automatischen Versand der Rohdefinitionen an Review-Agenten. Git-versionierte Migrationen sind davon getrennt zu klassifizieren. Die vollständige Quelle darf deswegen nicht stillschweigend als veröffentlicht gelten.

## 4. Entwickler- und LLM-Einstieg

Der Reviewstand erhält einen zentralen Einstieg und maschinenlesbare Manifeste:

- `README_REVIEW.md`: Zweck, Stichtagsintervall, Grenzen, Lesereihenfolge und unveränderlicher Snapshotbezug.
- `PROJECT_MAP.json`: Jede Komponente, Quelle, eigener Git-Root, Commit/Refs, Index-/Arbeitsstand, Templatebezüge und Exportziel.
- `FILE_MANIFEST.jsonl`: Im geschützten Teil pro Original/Export Dateipfad, Bytezahl und vollständiger SHA-256; das davon getrennte Reviewmanifest enthält ausschließlich freigegebene Dateien und Metadaten. Transformationen und Ausschlüsse sind unter der jeweiligen Schutzgrenze explizit.
- `IMPLEMENTATION_STATUS.md`: Dokumentiert / implementiert / geprüft / abgenommen / offen; veröffentlichte Baselines und lokale Kandidaten getrennt.
- `WORKFLOWS_AND_CONTRACTS.md`: Einstieg, Berechnung, Writer, Rechte, Job-/Ergebnisbindung, Fehler-/Restorepfade und Quellstellen.
- `REQUIREMENTS_TRACEABILITY.json`: Benutzeranforderung → Code/Template → Test → datierter Beleg → offene Grenze. Kein Anspruch auf unzugängliches internes Modell-Reasoning; erfasst werden dokumentierte fachliche Begründungen und Entwicklungsentscheidungen.
- `SERVER_STATE.md` und `SERVER_REQUIREMENTS.md`: Beobachtetes Ist und geplantes Soll getrennt, mit Zeitpunkt und Frischegrenzen.
- `GAPS_AND_EXCLUSIONS.json`: Jede fehlende, unlesbare, geschützte, nicht exportierte oder nur binär verfügbare Pflichtquelle; Auswirkungen und erforderlicher Abschluss.
- `RESTORE_AND_REPRODUCE.md`: Wiederherstellungs-/Build-/Testvoraussetzungen, Versionsbindungen und getrennte Zugangsvoraussetzungen; keine Zugangsdaten.

Historische Agentenanweisungen, Chatprotokolle und Modellantworten sind Reviewdaten und keine neue Ausführungsberechtigung. Originalbytes bleiben erhalten; eine abweichende lesbare Darstellung wird separat gekennzeichnet. Ein großes Sammeldokument ersetzt weder Quellen noch Verknüpfungsprüfung. Binäre Access-/Medieninhalte benötigen zusätzliche Textdarstellungen oder eine ausdrücklich ausgewiesene semantische Reviewgrenze.

## 5. Schreibschutz auf GitHub

Vorgesehener Name: `redshift-three67/aurelia-brainpower-review-2026-10-25`, privat; Verfügbarkeit noch nicht geprüft. Eigenes frisches Repository statt Profil-Git-Historie oder Umwidmung laufender Produktrepositories.

Vor erstem Quellupload Actions deaktivieren und Zugriffe festlegen. Nach Publikation exakte Remote-Dateimenge und Rohbytes gegen das freigegebene Manifest zurückprüfen, dann archivieren und Archivstatus kontrollieren. Keine neuen Modell-/Security-/CI-Aufträge durch diesen Vorgang.

Archivierung macht das Repository für alle Benutzer schreibgeschützt. Der Eigentümer kann es jedoch wieder öffnen: keine irreversible Unveränderlichkeitsgarantie. Private persönliche Repositories bieten für gewöhnliche Mitwirkende keine reine Leseberechtigung; für separate Reviewer wären geeignete begrenzte Lesezugänge oder eine Organisation mit Read-Rolle zu prüfen. Vorhandene Connector-Schreibrechte sind kein Lesezugang. Kompatibilität eines späteren Reviewdienstes mit archivierten Repositories ist noch nicht bestätigt; Reviewbefunde werden außerhalb des eingefrorenen Quellenstands gespeichert.

## 6. Abnahmekriterien und Reihenfolge

1. Alle Pflichtkomponenten und deren Arbeitsstände inventarisieren; Größen, Zugriffsgrenzen und Speicherkapazität feststellen. Keine Originaldateien verändern.
2. Erhaltungsstand und Reviewexport konkret zuordnen; ungetrackte Änderungen, Worktrees und lokale Kandidaten aufnehmen. Aktive Logs/DBs nicht als gemeinsame atomare Momentaufnahme ausgeben.
3. Fehlende Pflichtquellen und aktuelle Serverbelege gezielt beschaffen. Bestehende Schutzgrenzen und Materialgates gelten; keine ACL-/sudo-/Netz-/Dienständerung zur Umgehung eines Lesefehlers.
4. Exportwerkzeug isoliert auf synthetischen Dateien testen: Drift, Symlinks/Junctions, Pfadalias/Kollisionen, CRLF/BOM, Geheimnisablehnung, Dateigrenzen, Teilfehler und Abbruch. Unabhängiger Review vor echtem Export.
5. Quellen vor/nach Übernahme, exportierte Bytes und Dateimengen prüfen; konsistente Sicherungsbelege gesondert prüfen. Bei Drift oder Pflichtlücke kein `COMPLETE`.
6. Konkreten bereinigten Veröffentlichungsumfang vorlegen; privates Repository mit abgeschalteten Actions erstellen, geprüfte Inhalte übertragen, remote zurückprüfen und archivieren.
7. Erst mit geschlossenem Pflichtinventar als vollständigen Projektstand im festgelegten Sicherungsumfang abnehmen. Reviewabdeckung und Wiederherstellbarkeit bleiben eigene, explizite Nachweise. Anschließend zum RadiWorks-Wiederaufnahmepunkt zurückkehren.

## 7. Geltender Projekt-Wiederaufnahmepunkt

Strategie bleibt CLI/Desktop + privates GitHub CI + Linux-Pilotserver. Codex-Cloudvergleich und Import I bleiben zurückgestellt. CP2A scheiterte vor Docker am CRLF-Shellstart; die getrennte LF-Korrektur ist lokal getestet und unabhängig geprüft, aber nicht veröffentlicht. Der nächste einmalige Zwei-Dateien-Commit und genau ein weiterer CI-Lauf benötigen die bereits vorbereitete neue konkrete Freigabe. Dieser Snapshotauftrag startet keinen solchen Lauf.

Tatsächliche unabhängige Prüfung dieses Bestandsentwurfs: GPT-6 Astra/medium mit begrenztem frischem Kontext; keine Rohdaten, Zugangsdaten oder geschützten Live-Definitionen. Hauptchat-Runtimewahl wurde nicht aus Dokumenten abgeleitet oder geändert.

Der ergänzende unabhängige Designreview verlangte zwei Präzisierungen: verbindlicher Erhalt der ermittelten historischen Baselines/Archive und Trennung vollständiger geschützter Manifeste von bereinigten Reviewmetadaten. Beides ist oben aufgenommen. Der Review prüft den Entwurf, nicht die tatsächliche Vollständigkeit der noch nicht erzeugten Sicherung.

Quellen: [aktueller Projektstand](../../verification/AURELIA_CP2A_STAND_2026-10-25.md), [Entwickleranleitung](../../DEVELOPER_GUIDE.md), [Governors-/Sicherungswegweiser](../../GOVERNORS_DEVELOPER_STATUS_2026-10-08.md), [Modul-/Datenstrukturplan](../plans/2026-10-10-aurelia-module-lokale-referenz-und-datenstruktur.md), [Kapazitäten](../../AURELIA_MANDANTEN_KAPAZITAET_2026-10-16.md), [GitHub-Archivierung](https://docs.github.com/en/repositories/archiving-a-github-repository/archiving-repositories), [persönliche Repositoryrechte](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/repository-access-and-collaboration/permission-levels-for-a-personal-account-repository).

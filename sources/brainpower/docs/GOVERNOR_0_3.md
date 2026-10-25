# Governor 0.3: umgesetzter Teilstand und Betriebsgrenzen

Stand: 12.09.2026. Diese Beschreibung gilt für den aktuellen Quellcode. Die früheren Bestands-, Soll/Ist- und Versionsberichte bleiben historische Nachweise. Ein gespeicherter Plan oder eine bestätigte Schrittauswahl bedeutet nicht, dass alle Phasen A–D umgesetzt oder abgenommen sind.

Die Workbench bleibt ein lokaler Dienst mit Python-Standardbibliothek, SQLite und einer Oberfläche aus JavaScript/CSS ohne Produktions-Buildkette. HTTP bleibt auf Loopback beschränkt; Host-, Origin-, Session- und CSRF-Prüfungen gelten auch für die neuen Schreibendpunkte. Ein begrenzter Job-Worker verarbeitet Modell- und Testaufträge nacheinander.

## A: Projektregister, Gruppen, lokale Beobachtung und Vault

`registry.py` speichert Projekte, Gruppen und dauerhafte Mitgliedschaften getrennt von der ursprünglichen Konfiguration. Bestehende Projekt-IDs und ursprüngliche Quellenmetadaten bleiben erhalten. Neue Registrierungen benötigen ein vorhandenes absolutes Projektverzeichnis; kanonische Pfadduplikate und überlappende Projektwurzeln werden abgelehnt. Es werden keine Produkt-Repositories angelegt. Maximal 50 Projekte und 50 Gruppen einschließlich archivierter Einträge sind vorgesehen.

Ein Projekt gehört höchstens einer Gruppe an. Mitgliedschaft und Rolle sind in dieser Version unveränderlich; Archivierung bewahrt die Zugehörigkeit. Erlaubte Rollen sind `parent`, `module`, `contracts` und `member`. Eine Gruppe kann höchstens ein Elternprojekt haben, auch wenn dieses archiviert ist. Sind die fünf bekannten IDs vorhanden, erhält die erste Migration die Gruppe `aurelia-integration`: Aurelia als Elternprojekt, Modul_Templates als Vertragsprojekt, RadiWorks, Radi144 und Morphic als Module. Andere konfigurierte Projekte bleiben zunächst Singles. Eine spätere Konfigurationsänderung schreibt die bereits migrierten Registerdaten nicht stillschweigend um.

Die Rollen dokumentieren die Zugehörigkeit. Sie sind noch kein allgemeiner Gate- oder Integrationsworkflow für beliebige neue Gruppen. Die vorhandene berechnete Governance-Matrix der ursprünglichen Produkte bleibt davon getrennt.

Die ausdrückliche Zuordnung über die Oberfläche beziehungsweise `/api/registry/memberships` versucht zusätzlich, ein Strategiegedächtnis zuzuordnen. Genau eine vorhandene `project_memories/strategy_project*.md` wird unverändert verwendet. Mehrere passende Dateien sind mehrdeutig und werden abgelehnt. Fehlt eine solche Datei, wird exklusiv ein unvollständiges Template mit stabiler Registernummer erstellt. Ein Fehler bei diesem zweiten Schritt hebt die bereits gespeicherte Mitgliedschaft nicht auf; die Antwort enthält eine Warnung. `/api/registry/memory` erlaubt einen erneuten ausdrücklichen Versuch. Erfolgreiche Zuordnung setzt `memory_provisioning=provisioned_incomplete`, nicht eine fachliche Abnahme. Für Singles legt dieser Weg kein Template an; eine vollständige Aufnahme benötigt ein vorhandenes Gedächtnis.

`scope_monitor.py` beobachtet Gruppen und unzugeordnete aktive Singles lokal in Rotation. Pro Monitor-Durchlauf wird höchstens ein Scope untersucht; mit mehr Scopes verlängert sich der Abstand zwischen deren Beobachtungen. Fehler werden als veralteter beziehungsweise unvollständiger Stand angezeigt. Dieser Monitor startet weder Modelle noch Planung oder Produktausführung. Die bisherigen Beobachtungen der konfigurierten Produkte bleiben bestehen.

`vault.py` liest ausschließlich ausdrücklich zugeordnete Markdown-Dateien unter `vault_root`. Es gibt keine automatische Vault-Suche, keine globalen Ersatzquellen und keine implizite Übernahme von `system_prompts.md` als Anweisung. Gruppen erhalten ihre eigenen Zuordnungen sowie ausdrücklich ihren Mitgliedern zugeordnete Quellen; ein Single erhält seine eigenen Quellen. Maximal zehn Dateien je Zuordnungsscope, 512 KiB je Datei und insgesamt 64 KiB UTF-8-Auszüge je Vault-Kontext sind vorgesehen. Originalpfad, vollständiger Dateihash und Kürzung bleiben sichtbar. Pfadumleitungen werden abgelehnt. Ein kontrollierter Export oder bidirektionaler Vault-Abgleich ist noch nicht implementiert.

## Modellübermittlung und Automatik

Neue Projekte und Vault-Zuordnungen starten mit `model_egress=false`. Die erste Migration übernimmt die ausdrücklich genehmigte Übermittlung der fünf vorhandenen Produkte nur bei `legacy_review_egress_authorized=true`; bekannte IDs allein erteilen keine Erlaubnis. Neue Installationen haben diesen Schalter standardmäßig aus. Spätere Projektfreigaben werden ausdrücklich über die Projektoptionen gespeichert. Alle beteiligten Projekt- und Vault-Quellen müssen für einen Modellauftrag freigegeben sein.

Die bisherige Automatik ist im aktuellen Betreiberzustand pausiert. Ihre vorhandenen Einstellungen, Zähler und Begrenzungen bleiben erhalten; dieser Versionsstand aktiviert sie nicht erneut. Neue Gruppen lösen keine automatischen Modellaufrufe aus. Lokale Beobachtung und Router-Erreichbarkeit sind keine Modellinferenz. Historische echte Reviews belegen nicht, dass die neuen Planungs- oder Staging-Abläufe bereits mit echten Produkten und Modellen abgenommen wurden.

## B: bestätigte Aufnahme, Planrevisionen und Auswahl

`intake.py` speichert eine ausdrückliche Betreiberbewertung mit Anforderungen, Teststrategie, Abhängigkeiten und offenen Nachweisen. Alle vier Felder benötigen Text. Die Annahme ist an den angezeigten Scope-Hash und den aktuellen Projektquellenstand gebunden. `plan_ready` setzt für jedes betroffene Projekt eine aktuelle Annahme, vorhandene Gedächtnisse und vollständige Beobachtung innerhalb der dokumentierten Scan-Grenzen voraus. Ein Template, ein erfolgreicher Scan oder ausgefüllte Registrierungsanforderungen allein reichen nicht.

`planning_llm.py` fordert von Terra einen strukturierten Plan an. Ungültige Strukturen, fremde Projekt-IDs oder zyklische Abhängigkeiten werden vor dem Supervisor-Aufruf abgelehnt. Sol oder Astra erhält denselben Rohkontext und den exakten Vorschlag zur unabhängigen Bewertung. Nur ein aktueller, strukturell gültiger Plan mit `REVIEW_ONLY`, ohne Befunde und ohne offene Nachweisanforderungen kann als Kandidat gespeichert werden.

`plans.py` bewahrt Kandidaten als unveränderliche Revisionen. Schritte enthalten IDs, Prioritäten, Abhängigkeiten, relative Dateipfade, Testbeschreibungen und eine Aktion aus `clarify`, `review`, `test`, `change`. Betreiber können einen einzelnen Schritt oder eine topologisch geordnete Folge auswählen. Diese Auswahl ist `plan_selection_only`: Sie ersetzt keine Produktgates und führt selbst nichts aus. Neue Quellen oder eine neue Planrevision machen ältere Auswahlen unbrauchbar. Es gibt noch keine allgemeine Fortschrittsführung, die abgeschlossene Schritte für eine abhängige Ausführungsfolge bestätigt.

## C: begrenzter isolierter Python-Pilot

Der umgesetzte Pilot ist enger als ein allgemeiner Executor. Er benötigt eine zusätzliche ausdrückliche Verzeichnisfreigabe in `staging_pilot_roots`, aktuelle Aufnahme und Planauswahl sowie einen unabhängigen `change`-Schritt ohne Abhängigkeiten. Nur ein isoliertes Single-Projekt ist zulässig. Gruppen und die fünf ursprünglichen Produkte sind ausgeschlossen. Die Konfiguration enthält standardmäßig keine Pilotwurzeln.

`scope_patch` lässt Terra einen Änderungsvorschlag für die exakt erlaubten Dateien erzeugen und den ausgewählten Supervisor prüfen. Nur ein Vorschlag ohne offene Supervisor-Befunde wird in eine frische Staging-Umgebung übernommen. `execution_workspace.py` kopiert ausschließlich den ausgewählten Umfang und schreibt die vorgeschlagenen Bytes in diese Kopie. Grenzen: 20 Dateien, 256 KiB je UTF-8-Datei und 1 MiB Gesamtumfang; fehlende Originaldateien benötigen ein ausdrückliches `None` als Vorhash. Original-WIP wird nicht überschrieben. Manifest, Vorher-/Nachher-Hashes, Verzeichnisidentität und Unified Diffs machen den Vorschlag prüfbar. Der Manifest-Hash wird unabhängig im Job gespeichert; spätere Quellen- oder Staging-Änderungen verhindern eine erfolgreiche Prüfung. Fehlgeschlagene Vorbereitungen können unversiegelte Staging-Verzeichnisse hinterlassen.

`stage_test` führt ausschließlich den vorhandenen Python-Interpreter mit `-I -S -B` und dem festen Standardbibliothek-Adapter für `unittest discover` im gestagten `tests`-Ordner aus. Es gibt ein 60-Sekunden-Limit und eine getrennte temporäre Schreibfläche. Ein Python-Audit-Guard beschränkt gewöhnliche Dateioperationen, Netzwerk- und Prozesszugriffe; gestagte Quellen bleiben schreibgeschützt. Das ist **keine Betriebssystem-Sandbox gegen bösartigen Python- oder nativen Code**. Gleichprozess-Introspektion und native Umgehungen werden dadurch nicht zuverlässig isoliert. Andere Testframeworks und beliebige Kommandos sind nicht unterstützt.

Ein grüner Rückgabecode allein reicht nicht: Ein separater Abschlussdatensatz außerhalb der Test-Schreibfläche muss vorliegen, Tests müssen tatsächlich gezählt sein und `count > skipped` gelten. Null Tests, ausschließlich übersprungene Tests, fehlender Abschlussdatensatz, Fehler oder veränderte Quellen sind kein Erfolg. Stdout ist nur Protokoll; eine ausgegebene Erfolgsmeldung mit anschließendem vorzeitigem Prozessende ist kein Abschlussnachweis.

Danach erhält Sol oder Astra tatsächliche Diffs, Hashes und Testbelege sowie `FULL_STAGED_SOURCES`: den vollständigen, gegen die versiegelten Hashes geprüften UTF-8-Inhalt jeder Umfangsdatei. Auch unveränderte Tests mit leerem Diff und ihre tatsächlichen Assertions werden übergeben. Fehlende, doppelte, fremde oder hashabweichende Quellen werden vor dem Modellaufruf abgelehnt; zu große Gesamtprompts werden nicht stillschweigend gekürzt. Der Review bewertet genau dieses isolierte Staging und behauptet keine Produktlaufzeit- oder Integrationsabnahme. `verified=true` erfordert erfolgreiche überprüfte Tests einschließlich Abschlussnachweis, einen aktuellen Quellenstand und einen unabhängigen Review ohne Befunde oder offene Nachweise. Modellfehler machen den tatsächlichen Testbericht nicht ungeschehen; der Schritt bleibt unverifiziert. Modelle dürfen fehlgeschlagene Tests nicht zu Erfolg erklären.

**Nicht implementiert:** Rückübertragung in Produktdateien, automatische Reparaturschleifen, allgemeine Ausführung abhängiger Sequenzen, automatische Fortschrittsfortschreibung, Commit/Merge/Deployment und eine universelle sichere Ausführungsumgebung. Ein verifiziertes Pilotartefakt ist keine Freigabe dafür.

## D: bestehende Live-Ansichten

Die bisherigen ausdrücklich konfigurierten lokalen Chrome/CDP-Ziele mit Start, Aufnahme und Stop bleiben erhalten. Neue Registerprojekte erhalten nicht automatisch eine Browser- oder App-Anbindung. Ein allgemeines Adapter-System für neue Anwendungen, autonome End-to-End-Bedienung und eine aus Live-Ansichten abgeleitete Produktabnahme sind nicht Bestandteil dieser Lieferung.

## Neue Konfigurationsfelder

| Feld | Standard und Bedeutung |
|---|---|
| `legacy_review_egress_authorized` | `false`; ausdrücklich genehmigte Übermittlung der bekannten fünf Projekte bei erster Registermigration übernehmen. |
| `vault_root` | Leere Zeichenfolge; ohne ausdrückliche Wurzel können keine Vault-Dateien zugeordnet oder gelesen werden. |
| `staging_pilot_roots` | `[]`; maximal fünf ausdrückliche absolute Pilotverzeichnisse. Ein Eintrag ersetzt Aufnahme, Planauswahl und Modellfreigabe nicht. |

Die vorhandenen Modell-, Automatik-, Loopback- und CDP-Felder bleiben bestehen. Zugangsdaten gehören weiterhin weder in diese Konfiguration noch in exportierte Artefakte.

## Neue HTTP-Schnittstellen

Alle POST-Routen benötigen die bestehenden Session-/Origin-/CSRF-Prüfungen. Registeränderungen setzen einen freien Job-Worker voraus; während eines Auftrags werden sie mit einem Konflikt abgelehnt. Die vorhandenen Endpunkte bleiben erhalten; `/api/projects` ist weiterhin nur der frühere Planungsnotiz-Endpunkt.

| Route | Nutzlast beziehungsweise Ergebnis |
|---|---|
| `GET /api/state` | Zusätzlich `registry.projects`, `registry.groups`, `registry.observations` und begrenzte `execution_capabilities`. |
| `GET /api/scope?kind=project\|group&id=ID` | Lokaler ausgewählter Kontext ohne Modellversand. |
| `GET /api/plans?kind=project\|group&id=ID` | Planrevisionen des ausgewählten Scopes. |
| `POST /api/registry/projects` | `name`, `path`, optional `requirements`, `model_egress`; vorhandenes Verzeichnis registrieren. |
| `POST /api/registry/groups` | `name`; Gruppe anlegen. |
| `POST /api/registry/memberships` | `project_id`, `group_id`, optional `role`; dauerhafte Zuordnung und begrenzter Gedächtnisversuch. |
| `POST /api/registry/memory` | `project_id`; Strategiegedächtnis ausdrücklich zuordnen beziehungsweise exklusiv erstellen. |
| `POST /api/registry/archive` | `project_id`; archivieren, Zugehörigkeit bewahren. |
| `POST /api/registry/policy` | `project_id`, optional `requirements`, `model_egress`; nur ausdrücklich übergebene Felder ändern. |
| `POST /api/vault/sources` | `scope_kind`, `scope_id`, `path`, optional `model_egress`; explizite Zuordnung. |
| `POST /api/intake` | `scope_kind`, `scope_id`, `scope_hash`, `project_id`, `fields` mit `requirements`, `test_strategy`, `dependencies`, `open_evidence`. |
| `POST /api/plans/approve` | `scope_kind`, `scope_id`, `scope_hash`, `candidate_id`, `selected_step_ids`, `mode=single\|sequence`; nur Auswahl protokollieren. |
| `POST /api/actions` | Zusätzlich `scope_review`, `scope_compare`, `scope_plan` mit `scope_kind`, `scope_id`; optional ausgewählter `supervisor`. |
| `POST /api/actions` | `scope_patch` mit `scope_kind`, `scope_id`, `candidate_id`, `step_id`; ausschließlich zulässiger Pilot. |
| `POST /api/actions` | `stage_test` mit `stage_job_id`; begrenzte Tests und anschließender unabhängiger Review. |

## Verifikationsstand

Der [Verifikationsbericht 0.3](VERIFICATION_0_3.md) dokumentiert die Gesamtsuite mit 264 Fällen, davon zwei übersprungen, die beobachteten Browserabläufe, die unveränderten Legacy-Fingerprints beim Umstieg auf 0.3.0 sowie den echten isolierten Modell-/Testpilot r3. Darin wurden Hermes/Terra mit Sol und Hermes/Terra mit Astra jeweils durch einen tatsächlich ausgeführten unittest und einen abschließenden Review verifiziert. Das Pilotprojekt und sein vorgegebener Betreiberplan waren synthetisch; dies ist weder ein Nachweis modellgenerierter Gesamtplanung noch eine Abnahme der fünf Produkte. Kleine Modellversuche erlauben keine allgemeine Rangfolge oder Aussage über optimalen Dauerbetrieb. A–D bleiben ein teilweise umgesetzter Ausbauplan mit den oben ausdrücklich genannten Grenzen.

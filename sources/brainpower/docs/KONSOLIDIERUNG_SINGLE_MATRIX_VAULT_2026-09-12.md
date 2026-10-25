# Einzelprojekte, Matrixgruppen und gemeinsames Gedächtnis

Status: A→B→C→D am 12.09.2026 ausdrücklich vom Betreiber freigegeben; Umsetzung auf dessen Wunsch bis nach der Pause angehalten. Die nachfolgenden Ergänzungen werden beim nächsten Gespräch besprochen. Noch nicht implementiert.
Grundlage: Betreiberbeschreibung vom 12.09.2026 und lesender Abgleich mit Governor0.2 sowie dem vorhandenen Hermes-Obsidian-Vault. Dieser Vorschlag verändert weder laufende Freigaben noch Originalprojekte oder Vault-Dateien.

## 1. Gemeinsames Zielbild

Jedes Projekt besitzt eine eigenständige Identität, einen registrierten Arbeitsordner, eigenes Gedächtnis, Anforderungen, Nachweise und eine hybride Review-/Umsetzungsschleife. Es kann ohne Matrixgruppe betrieben werden. Der Betreiber entscheidet ausdrücklich, ob und welcher Gruppe ein Projekt zugeordnet wird. Die bestehenden fünf Projekte bilden bei der Migration die erste Gruppe; ihre bisherigen IDs, Nachweise und Freigaben bleiben erhalten und werden nachvollziehbar auf den neuen Geltungsbereich übertragen.

Empfehlung: höchstens eine feste Matrixgruppe je Projekt. Auch ein Gruppenmitglied lässt sich einzeln öffnen und bearbeiten; seine Gruppenmitgliedschaft und betroffenen gemeinsamen Gates gelten weiter. Derselbe Windows-Ordner darf nicht unter einem anderen Namen als unabhängiges zweites Projekt registriert werden. Pfadnormalisierung, Groß-/Kleinschreibung, Junctions/Symlinks und Git-Worktrees müssen berücksichtigt werden. Unterschiedliche Worktrees desselben Repositories teilen Ressourcen; dafür ist eine gemeinsame Ausführungssperre nötig.

Die normale Bedienung bietet keinen stillen Gruppenwechsel und kein Entfernen bereits zugeordneter Projekte. Archivierung bewahrt Zugehörigkeit und Historie. Ein verschobener Ordner wird nach geprüftem Pfadabgleich derselben Projekt-ID zugeordnet. Fehlende Ordner bleiben als fehlend sichtbar; sie werden nicht automatisch aus der Matrix entfernt.

## 2. Geprüfter Istzustand

| Gewünschte Eigenschaft | Governor0.2 |
|---|---|
| Einzelnes bestehendes Projekt reviewen | Vorhanden, aber kein vollständig isolierter Single-Kontext: zentrale Governance-Quellen, Entscheidungen und Matrix werden zusätzlich übergeben. |
| Allgemeiner hybrider Review–Korrektur–Test-Zyklus | Nicht vorhanden. Hermes ist im Review absichtlich ohne Werkzeuge initialisiert; die allgemeine Produktänderung ist nicht implementiert. |
| Neue echte Projektordner über UI verwalten | Nicht vorhanden. Neue UI-Einträge sind geplante Module, keine registrierten ausführbaren Projekte. |
| Mehrere Matrixgruppen | Nicht vorhanden. Es gibt eine globale Projektliste und einen festen Katalog mit neun Schritten, keine Gruppenentitäten. |
| Dauerhafte Gruppenmitgliedschaft | Noch kein Datenmodell dafür. |
| strategy_project*.md bei Zuordnung erstellen | Nicht vorhanden. Der Editor arbeitet auf bereits existierenden Markdown-Dateien. |
| Matrix erst nach vollständiger Aufnahme aller Mitglieder | Teilweise: unvollständige Erfassung sperrt aktuelle Ausführung; es gibt keine vollständige gruppenspezifische Aufnahmeregel. |
| Automatisch ausführen, solange genehmigter Plan unverändert bleibt | Nicht vorhanden. Automatische Reviews sind vorhanden, automatische Produktausführung nicht. |
| Obsidian-Vault im Kontext | Nicht aktiv eingebunden. Kein Vault-Pfad/Leser in der Workbench-Konfiguration; die isolierte Hermes-Instanz lädt ihr normales Langzeitgedächtnis nicht. |
| Sichtbarer Chrome-Test | Vorhanden für konfigurierte, bereits laufende lokale Anwendungen. Screenshot-/Log-Erfassung ist noch kein vollständiger fachlicher Browsertest. |

Der geprüfte Vault ist `C:/Users/Hubert111/Documents/Hermes-Obsidian-Vault`. Sein `Governors/Project Status.md` vom11.09.2026 13:32 nennt RadiWorks, Biomedis, Morphic Engine2, Headless CMS und Hermes. Dies ist nicht die aktuelle Fünfergruppe Aurelia/RadiWorks/Modul_Templates/Radi144/morphic_v1. Die Datei bleibt historische Evidenz. Der Vault enthält zusätzlich `project_memories` und `system_prompts`; deren Existenz ist keine gültige automatische Zuordnung zu den aktuellen Projekten und keine Freigabe zur Ausführung enthaltener Anweisungen.

## 3. Gedächtnis und Quellenautorität

Ein Einzelprojekt erhält ein eigenes strukturiertes Gedächtnis mit Projekt-ID, Anforderungen, Quellen, Entscheidungen, Prüfungen, offenen Punkten und nächsten Schritten. Bei Gruppenaufnahme wird die geforderte Datei `project_memories/strategy_project_<stabile_nummer>.md` angelegt, falls keine passende Datei existiert. Für bestehende Projekte werden die bereits vorhandenen Dateien übernommen und geprüft, nicht neu nummeriert oder überschrieben. Uneindeutige Zuordnungen werden zur Klärung angezeigt. Leere Vorlagen gelten nicht als vollständige Projektdaten.

Empfohlene Autoritäten:

- Projektdateien, Projektgedächtnis und tatsächliche Testartefakte: fachliche Quellen.
- Entscheidungsjournal: wer welchen konkreten Umfang auf welcher Grundlage freigegeben oder abgenommen hat.
- Gruppengedächtnis: versionierter Plan, Beziehungen und zusammengeführte Nachweise, mit Referenzen auf die Quellen.
- Vault: gezielt eingebundene Hintergrundquellen und nachvollziehbarer Spiegel; kein zweiter konkurrierender Matrixzustand.

Für den Vault werden Projekt-/Gruppenbereiche explizit zugeordnet. Nicht zugeordnete Altbestände bleiben in einer Prüfliste. Relevante Inhalte werden mit Pfad, Hash, Stand und Geltungsbereich in den Kontext übernommen. Single-Projekte erhalten keine fremden Gruppeninhalte. `system_prompts` werden nicht ungeprüft als aktive Regeln geladen; ihre Übernahme erfordert eine gesonderte Konfiguration.

Schreibfluss zunächst eindeutig: Workbench schreibt Projekt-/Gruppenergebnisse kontrolliert, der Vault erhält einen markierten Spiegel mit Herkunft und Prüfsumme. Externe Vault-Änderungen werden als Änderungskandidaten importiert und geprüft, nicht automatisch zurückgeschrieben. Das vermeidet Synchronisationsschleifen und stilles Überschreiben. Jeder Schreibvorgang verwendet Versionsprüfung, Sicherung und Konfliktmeldung.

## 4. Wann ein Matrixplan entsteht

Vor einer Planung sieht der Betreiber eine Aufnahmeübersicht aller Gruppenmitglieder. Pro Projekt sind mindestens Identität/Pfad, Ziel und Anforderungen, relevante Gedächtnisquellen, aktueller Quellenstand, Abhängigkeiten, gültige Entscheidungen, Testmöglichkeiten und bekannte offene Nachweise erfasst. Fachlich unbekannte Punkte dürfen ausdrücklich unbekannt bleiben und zu einem Klärungsschritt führen; sie dürfen nicht als erfüllt erscheinen.

Erst wenn für jedes Mitglied diese Aufnahme vollständig ist, darf der Governor einen gruppenweiten Planentwurf vorlegen. Terra erstellt den Vorschlag; Sol oder Astra prüft Anforderungen, Schritte, Abhängigkeiten und Nachweise unabhängig. Ein Vergleich beider Supervisoren nutzt denselben Terra-Vorschlag. Ein Regelprüfer kontrolliert anschließend IDs, Quellenbezüge, Zyklen, ausführbare Aktionen und Freigabegrenzen. Modelltext allein wird nicht zum ausführbaren Plan.

Die Oberfläche zeigt geordnet: nächsten Schritt, Zweck, betroffene Projekte, Voraussetzungen, geplante Änderungen, Tests, Sperrgründe und Freigabestatus. Der Plan wartet auf die vorgesehene Nutzerfreigabe. Bei später fehlenden Daten bleibt der letzte gültige Plan als historisch sichtbar; betroffene Ausführung wird angehalten, bis der Stand wieder geklärt ist.

## 5. Freigabe und automatische Fortsetzung

Entscheidend ist die Trennung zwischen erwartetem Fortschritt und einer echten Planänderung. Jeder erfolgreiche Arbeitsschritt verändert Dateien oder Status. Würde jede Hashänderung als neuer Plan gelten, wäre die gewünschte automatische Fortsetzung unmöglich.

**Fortschritt:** ein freigegebener Schritt liefert das vorgesehene Ergebnis; Prüfungen bestehen; Umfang, Reihenfolge und Voraussetzungen der übrigen Schritte bleiben innerhalb des genehmigten Plans.

**Planänderung:** neue Anforderungen, neue/entfallende Schritte, geänderte Reihenfolge oder Abhängigkeiten, zusätzliche betroffene Projekte/Dateibereiche, fehlgeschlagene Prüfungen, neue Risiken oder widersprüchliche relevante Quellen.

Empfohlene UI-Freigaben:

1. **Diesen Schritt freigeben:** genau eine Ausführung plus zugehörige Prüfungen/Korrekturschleife im definierten Umfang; danach Halt.
2. **Diese Schrittfolge freigeben:** eine vorher sichtbare, begrenzte Folge mit Zeit-/Aufrufbudget. Automatische Fortsetzung nur innerhalb dieser Folge und bei unverändertem Plan.

Das Setzen einer Marke „Plan unverändert“ durch ein Modell genügt nicht. Der Controller vergleicht strukturierte Aufgaben, Umfang, Voraussetzungen, Akzeptanzkriterien und erwartete Ausgaben. Externe Änderungen werden getrennt von eigenen erwarteten Änderungen erfasst. Bei Unklarheit wird angehalten.

Nach einer Planänderung werden Matrix und Gruppengedächtnis nach erfolgreicher Verifikation aktualisiert, die Differenz angezeigt und eine neue Freigabe angefordert. Eine Einzelschrittfreigabe wird nicht stillschweigend auf weitere Schritte ausgedehnt. Scheitern Tests, läuft nur eine bereits genehmigte, begrenzte Reparaturschleife; bei neuer fachlicher Entscheidung oder ausgeschöpftem Budget hält sie an.

## 6. Reale hybride Umsetzung und Live-Abnahme

Der fehlende Ausführungsadapter ist eine eigene zentrale Erweiterung. Vorgesehene Schleife:

Anforderungen und gebundene Quellen → Terra-Plan → Supervisor-Prüfung → Nutzerfreigabe → isolierte Änderung → automatisierte Tests → Supervisor-Prüfung des tatsächlichen Diffs und der Testergebnisse → gegebenenfalls begrenzte Korrektur → konfigurierte Live-Tests → Nachweise und Matrixfortschreibung.

Planer und Supervisor bleiben vom schreibenden Ausführer getrennt. Ein erfolgreicher Planreview bestätigt nicht die spätere Implementierung. Der Ausführer arbeitet auf genau freigegebenen Dateibereichen, bewahrt vorhandene WIP, hat Rücksetz-/Sicherungsnachweise und führt nur konfigurierte Projektaktionen aus. Kein allgemeiner Shellbefehl wird aus einem Modelltext übernommen. Commit, Migration und Deployment sind jeweils eigene Aktionsklassen mit ihren Voraussetzungen.

Jedes Projekt erhält einen Testadapter: Start-/Stop-Kommando, freie lokale Ports, Testdaten, erwartete Prüfungen und Abnahmekriterien. Browserprojekte verwenden sichtbare Chrome/CDP-Prüfungen samt Interaktions- und Ergebnisprüfungen, nicht nur Screenshots. CLI-/Backend-Projekte benötigen entsprechende andere Nachweise. Externe Infrastruktur oder Hardware kann nicht allein durch einen lokalen Browsertest als abgenommen gelten.

## 7. Mehrere Gruppen: machbar mit getrennter Zuständigkeit

Empfohlenes Datenmodell: `projects`, `groups`, unveränderliche `memberships`, projektbezogene Quellen, gruppen-/projektbezogene Pläne und Entscheidungen, Ausführungen und Artefakte. Aktuelle globale IDs werden bei Migration explizit zugeordnet. Der bestehende Zustand wird zuvor gesichert; ein Trockenlauf zeigt die Übernahme, bevor der Schreibbetrieb umgestellt wird.

Jede Gruppe besitzt eigene Planrevisionen, Kontextgrenzen, Entscheidungen und Datenvollständigkeit. Änderungen in GruppeA dürfen nicht pauschal Nachweise in GruppeB veralten lassen. Explizit gemeinsam genutzte Vertragsquellen sind eine Ausnahme: ihre Änderung betrifft gezielt alle registrierten Verbraucher. Gruppenzugehörigkeit und Ressourcenbesitz werden unabhängig von Anzeigenamen verwaltet.

Für Windows zunächst ein zentraler Ausführungsworker über alle Gruppen, dazu eine faire Warteschlange, projekt-/repositorybezogene Sperren, zusammengefasste Dateiereignisse und ein globales Modellbudget. Keine dauerhafte Browserinstanz je Projekt; Live-Tests starten bei Bedarf und enden kontrolliert. Eine Unterbrechung oder ein Neustart setzt mutierende Aufträge nicht ungeprüft fort.

Damit sind mehrere Gruppen grundsätzlich realisierbar. Eine konkrete Kapazitätszusage folgt erst aus Lasttests. Nicht empfohlen sind unkontrollierte Mehrfachmitgliedschaft desselben Ordners, globaler Kontext für alle Gruppen oder mehrere gleichzeitig schreibende Agenten auf derselben Arbeitskopie.

## 8. Freigabepaket und Umsetzungsreihenfolge

**A – Grundlage:** echte Projektregistrierung, Single-Modus, Gruppenverwaltung, permanente Zugehörigkeit, vorhandene Fünfergruppe migrieren, Gedächtnisdateien kontrolliert anlegen/zuordnen, Vault-Bereiche lesend einbinden und Spiegelregeln einrichten.

**B – Planung:** Aufnahmekriterien je Mitglied, gruppenbezogene Planversionen, aus Projektdaten abgeleitete validierte Schritte statt ausschließlich festem Neuner-Katalog, Geltungsbereiche der Entscheidungen, sichtbare Planänderungen und begrenzte Freigabefolgen.

**C – Umsetzung:** schreibender Ausführungsadapter mit isoliertem Arbeitsstand, Tests, tatsächlichem Diff-Review und begrenzter Reparaturschleife; zuerst an einem isolierten Beispielprojekt abnehmen, danach gezielt auf bestehende Produkte anwenden.

**D – Live und Robustheit:** projektspezifische Server-/CLI-/Browseradapter, Ende-zu-Ende-Abnahme, Neustart-/Konflikt-/Lasttests für mehrere Gruppen, Windows-Anleitung und LLM-Betriebsvertrag aktualisieren.

Abnahmefälle: unabhängiges Single-Projekt ohne Gruppe; zwei Gruppen ohne Kontextvermischung; fehlendes Mitglied verhindert Planfreigabe; Gruppenaufnahme erzeugt genau eine passende Gedächtnisdatei; vorhandene Dateien werden bewahrt; Vault-Altbestand überschreibt keine aktuellen Fakten; Einzelschritt hält danach an; freigegebene unveränderte Folge fährt fort; Planänderung stoppt; externer Edit stoppt betroffene Ausführung; Neustart verdoppelt keine Mutation; fehlgeschlagener Test wird nicht als bestanden dargestellt.

Die bisherige automatische Reviewfreigabe bezieht sich auf die vorhandenen fünf Projekte. Neue Projekte, neue Gruppen und bisher nicht verwendete Vault-Bereiche benötigen bei Aufnahme eine sichtbare Festlegung ihrer Modellübermittlung und Automatikgrenzen. Diese Einstellung wird danach gespeichert und nicht bei jedem unveränderten Aufruf erneut abgefragt.

## 9. Empfehlung zur Entscheidung

Das beschriebene Ziel ist mit diesen Grenzen sinnvoll umsetzbar. Empfohlen wird A→B→C→D, unter Beibehaltung des vorhandenen Designs. Zur Freigabe stehen die Erweiterungen dieses Dokuments, insbesondere ein Projekt pro Gruppe, explizite Schrittfolgenfreigabe und der getrennte schreibende Ausführungsadapter. Fachliche Produktgates werden damit nicht pauschal abgenommen.

## 10. Betreiberfreigabe und Ergänzungen vor der Pause

Der Betreiber hat den empfohlenen Umfang A→B→C→D ausdrücklich freigegeben und zugleich eine Pause angeordnet. Es wurde keine Umsetzung dieser Erweiterung begonnen. Zum Pausenbeginn liefen keine Aufträge. Automatische Modellreviews wurden ausgeschaltet; die lokale Beobachtung und Oberfläche bleiben aktiv. Die bisherige grundsätzliche Erlaubnis für automatische Reviews wird dadurch nicht widerrufen; der Betriebsmodus bleibt bis zur Wiederaufnahme pausiert.

### Sichtbare Priorisierung vor der Freigabe

Verbindliche Ergänzung des Betreibers: In der Gruppenmatrix müssen Priorität, Reihenfolge und Abhängigkeiten der Gates und nächsten Schritte vor dem Freigabebutton deutlich erkennbar sein. Vorgesehen sind nummerierte Schritte, klare Statuskennzeichnung mit Text statt ausschließlich Farbe, Begründung der Priorität, betroffene Projekte, Voraussetzungen sowie Umfang und Tests der freizugebenden Aktion. Bei einer Schrittfolge muss die gesamte freigegebene Folge sichtbar sein. Diese Anforderung gehört in PhaseB und deren Browserabnahme.

### Vollständiger Gruppen-Review: Empfehlung zur Besprechung

Empfohlen wird eine eigene Aktion „Gesamte Gruppe neu abgleichen“. Sie nimmt alle Gruppenmitglieder mit gebundenen Quellenständen auf, lässt Terra einen konsolidierten Status-/Strategieentwurf erstellen und Sol oder Astra unabhängig gegenprüfen. Fehlende Daten und nicht ausgeführte Tests bleiben ausdrücklich offen. Ein Review allein garantiert keine vollständige 1:1-Abbildung des tatsächlichen Laufzeitverhaltens.

Der Abgleich erstellt zunächst einen neuen Plan- und Gedächtniskandidaten mit sichtbarer Differenz zum bisherigen Stand. Historie, bestehende Freigaben und alte Strategieversionen werden nicht überschrieben. Erst nach Prüfung und der erforderlichen Bestätigung wird die neue Version maßgeblich. Ändern sich Quellen während des Abgleichs, wird der Kandidat als überholt markiert und nicht als aktueller Gesamtstatus übernommen. Die genaue Bedienung und der Übernahmeprozess werden nach der Pause besprochen.

### Gruppenrollen und Integrationsbeziehungen

Vom Betreiber für die vorhandene Gruppe ausdrücklich klargestellt:

- Aurelia ist das übergeordnete Integrationsziel.
- RadiWorks, Radi144 und morphic_v1 sind die drei vorgesehenen Module mit eigenen Funktionalitäten und Kernengines.
- Modul_Templates übernimmt den Vertrags-/Anforderungsabgleich zur Vorbereitung auf Aurelia.
- Gemeinsame Integrationsanforderungen müssen abgeglichen werden, ohne daraus eine Vereinheitlichung der unterschiedlichen Kernengines abzuleiten.

Empfehlung: Diese Rollen und gerichteten Integrationsbeziehungen werden explizite Gruppendaten. Ein Review darf Beziehungen aus Quellen vorschlagen und Inkonsistenzen melden; er soll die führende Rolle oder Integrationsrichtung nicht stillschweigend festlegen. Für diese Gruppe ist die obige Nutzerangabe die maßgebliche Zuordnung. Bei neuen Gruppen fragt die Aufnahme nach Führungsprojekt, Modulen und gegebenenfalls Vertragsautorität; Gruppen ohne Führungsprojekt bleiben möglich.

Das Datenmodell benötigt neben der dauerhaften Mitgliedschaft Rollen und typisierte Beziehungen, beispielsweise „integriert in“ und „Vertragsabgleich durch“. Planer und Supervisor berücksichtigen sowohl projektspezifische Anforderungen als auch gemeinsame Integrationsverträge. Der genaue Umfang der gemeinsamen Schnittstellen wird aus den gültigen Aurelia-/Modulverträgen ermittelt und belegt, nicht aus der bloßen Gruppenmitgliedschaft erfunden. Diese Ergänzung gehört in PhaseA/B.

Nächste Besprechung: Darstellung der Prioritäten, Gesamtabgleich mit versionierter Gedächtnisübernahme und explizite Rollen der Gruppenmitglieder. Keine neue pauschale Fachfreigabe oder Umsetzung während der Pause.

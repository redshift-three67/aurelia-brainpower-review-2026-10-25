# Governor 0.5 – Aufnahme und Strategieübernahme

Die nachfolgende Bedienfolge beschreibt die vorhandene Fähigkeit zur Matrixplanung, nicht ihren jetzigen Starttermin. Nach der Betreiberentscheidung vom 25.09.2026 werden zuerst beide Hermes-Modellwege je Auftrag ausdrücklich wählbar geprüft, danach RadiWorks, Radi144, `morphic_v1` und ein neues Modul als getrennte Prototypen finalisiert. Erst anschließend werden die aktuellen Aufnahmen bestätigt und der vollständige Produkt-Matrixplan erstellt; siehe [Modulübergang](MODULUEBERGANG_UND_BETREIBERPRUEFUNG.md). Die ältere Fünfergruppenaufnahme und frühere Planentwürfe sind historische Belege.

## Bedienung

Fünf lokale Aufnahmeentwürfe sind aus den sieben vollständig gelesenen Gedächtnissen und zentralen Governance-Quellen vorbereitet. Sie trennen Anforderungen, Teststrategie, Abhängigkeiten und offene Nachweise. Historische Testzahlen sind keine neuen Testläufe. Vollständige Gedächtnislektüre beweist nicht die Aktualität des gesamten Produktcodes.

1. **Projekte & Gruppen** öffnen und bei der Integrationsgruppe mit fünf Mitgliedern **Aufnahme prüfen** anklicken.
2. Im Aufnahmeformular ein Projekt auswählen, **Aufnahmeentwurf laden**, die vier Felder und Quellenhashes prüfen und gegebenenfalls korrigieren. **Projektaufnahme bestätigen** für jedes Mitglied ausdrücklich durchführen. Damit wird die Beschreibung als Planungsbasis angenommen; offene Nachweise bleiben offen. Keine Produktabnahme.

   Für einen neuen Aurelia-Gruppenplan ist zusätzlich der [Design-Template-Strang D0–D4](AURELIA_DESIGN_TEMPLATE.md) in den Anforderungen von Aurelia und jedem betroffenen Modul zu prüfen und ausdrücklich als Aufnahmeinhalt zu bestätigen. Die Matrix zeigt diese Vorgabe als **offene Planung außerhalb der abgenommenen Gate-Zählung**. Die Dokumentation allein ändert keine schon bestätigte Aufnahme und keinen vorhandenen Modellplan; für einen quellengebundenen neuen Plan muss die Anforderung im jeweiligen aktuellen Aufnahmeumfang enthalten sein.
3. Den vorhandenen aktuellen Quellenabgleich unter **Governance → Quellen und Statusaussagen abgleichen** anhand des Berichts prüfen und ausdrücklich annehmen, wenn er zutrifft. Eine lesbare Zusammenfassung liegt lokal in `artifacts/QUELLENABGLEICH_0_5.md`. Diese Abnahme ist ein anderer Vorgang als die Projektaufnahme. Empfehlenswerte Reihenfolge: zunächst die fünf Aufnahmen, danach diese Governance-Entscheidung. Änderungen an der Entscheidungsgrundlage können noch unbestätigte Entwürfe veralten lassen.
4. Nach fünf aktuellen Aufnahmebestätigungen wird **Matrixplan hybrid entwerfen** verfügbar. **Gruppe hybrid reviewen** liefert zusätzlich einen beratenden Abgleich. Beide verwenden Terra und den ausgewählten Sol-/Astra-Supervisor, sind aber unterschiedliche Aufträge.
5. **Kandidaten & Strategie laden**, Kandidatenversion auswählen, Rangfolge, Abhängigkeiten, Begründungen, Dateiumfang, Tests und unabhängigen Review prüfen.
6. **Kandidaten als Strategie übernehmen (keine Ausführung)** speichert eine unveränderliche Revision. Quellenänderungen, neue Aufnahme, anderer neuester Kandidat oder konkurrierende Übernahme sperren veraltete Bestätigungen.

Die neue Strategie liegt im Register-/Planbereich. Die historische Governance-Matrix wird nicht überschrieben. Die gesonderte Planauswahl erteilt weiterhin keine allgemeine Ausführungserlaubnis. Produktexecutor, automatische Fortschrittsübernahme und Schrittfolgen bleiben weitere Ausbaustufen.

## Entwicklervertrag

- `IntakeDrafts` speichert append-only in `intake_drafts`. GET/POST `/api/intake/drafts`; das Speichern selbst bestätigt nichts und ruft keine Modelle auf. POST bindet Umfang, Projekt, vier Felder und Quellenname/SHA-256. Quellen anderer Projekte sind nur innerhalb der tatsächlich gewählten Gruppe zulässig.
- Aktuelle, noch nicht angenommene Entwürfe gehen als `intake_proposals` mit `status=unconfirmed_draft` in einen ausdrücklich gestarteten scoped Review ein. Sie binden dessen Umfangshash, sind keine Betreiberentscheidungen und werden im Auftragsresultat festgehalten. Angenommene Aufnahmen stehen stattdessen in `intake_records`; veraltete oder fremde Entwürfe werden ausgeschlossen.
- `ScopeService.intake_source_hash` trennt Quellen-/Entscheidungsbasis von Aufnahmebestätigungen. Andere Bestätigungen bei unveränderten Quellen invalidieren vorbereitete Entwürfe nicht. Die vollständigen `intake_records` gehen weiterhin in den Planungshash ein.
- `StrategyBook` speichert append-only `strategy_revisions`: Kandidat, Review, ursprünglicher Auftrag, Hashes, Projekt-/Aufnahmeherkunft und Betreiberzeitpunkt. UPDATE-/DELETE-Trigger schützen die Historie. Eindeutiger Kandidat und eindeutige scoped Versionen.
- GET `/api/strategies?kind=project|group&id=...`; POST `/api/strategies/adopt` mit `scope_kind`, `scope_id`, `candidate_id`, `scope_hash`, `expected_previous_id` (erste Revision: null).
- Übernahme unter `BEGIN IMMEDIATE`: neuester aktueller Kandidat, abgeschlossener nicht veralteter `scope_plan`, exakt passender Vorschlag/Review, sauberes unabhängiges Urteil und aktuelle Aufnahmeherkunft erforderlich. Neueste Datenbankaufnahmen werden innerhalb derselben Transaktion erneut verglichen. CAS schützt die vorherige Revision.
- HTTP-Übernahme und Aufnahmebestätigung serialisieren interne Quellenerfassung mit dem Store-Lock. Host/Origin/Session/CSRF bleiben aktiv; GET benötigt Sitzung.
- `current` beim GET ist eine Momentaufnahme des erneut gelesenen Quellenstands. Externe Dateisysteme sind nicht transaktional gesperrt; spätere Aktionen müssen erneut prüfen.
- Der historische Gruppenpfad setzt nun auch den Entscheidungsfingerprint vor der Matrixableitung. Sonst wurden vorhandene aktuelle Berichte im Gruppenmodellkontext nicht erkannt, obwohl die Hauptmatrix sie korrekt als zur Betreiberprüfung bereit darstellte. Regression prüft Berichtswiederverwendung und echte Entscheidungsdrift. Kein Umschreiben früherer Freigaben oder Modellresultate.
- Die Hauptmatrix nutzt dieselbe begrenzte Historie von 200 Aufträgen wie Aktionsprüfung und Gruppenreview; die Oberfläche zeigt weiterhin nur die letzten 40. Eine Regression hält einen aktuellen Bericht außerhalb des sichtbaren Fensters wirksam. Eine unbegrenzte Auftrags-/Nachweisarchivierung ist damit nicht implementiert.
- `tools/import_intake_drafts.py` prüft Audit-Quellhashes und importiert nur unbestätigte Entwürfe über die API. Auditdaten bleiben unter `artifacts`. Ein gleichnamiges Gedächtnis wird anhand des jeweiligen Projekt-Hashes zugeordnet. Historische Workbench-Berichte bleiben Hintergrundmaterial und werden nicht zur Projektquellenautorität erklärt.
- `tools/prepare_strategy_preview.py` erzeugt ausschließlich synthetische Browserfixtures; deren Reviews sind Testdaten, keine Modellnachweise.

## Prüfung und Grenzen

Abschließende Suite: 343 Anwendungstests, davon 341 bestanden und zwei Windows-Symlinkprüfungen ausgelassen (`artifacts/unit-tests-v05-release.txt`). JavaScript-Syntaxprüfung bestanden. Isolierte Browserprüfung: Entwurf laden, manuelle Eingabe bei erneuter Aufnahme erhalten, Kandidat auswählen, Strategie übernehmen, aktuelle Revision anzeigen, Hellmodus. Keine JavaScript-Fehler im geprüften Browserprotokoll. Ein gleichzeitiger Kontextabruf wurde erwartungsgemäß abgewiesen; erneutes Laden nach Abschluss des ersten Abrufs funktionierte.

Echter Gruppenvergleich mit allen fünf unbestätigten Aufnahmen: Auftrag `1b278124a55f4effb8864ab05a1f0b9d`, Terra über Hermes mit null Werkzeugen, danach Sol und Astra. Alle drei Aufrufe erfolgreich, beide Supervisoren `REVIEW_ONLY`, bei abschließender Prüfung keine Quellendrift. Beide benennen weiterhin offene Nachweise und Betreiberabnahmen; dies ist kein sauber abgenommener Matrixplan. Der vorherige Vergleich `bf8b78a429544b5fbfdf38e1a781bf80` nutzte noch die anschließend korrigierte Gruppenmatrix und ist als historische Diagnose zu behandeln. Modelltexte wurden nicht nachträglich geändert.

Vor dem zweiten Vergleich stimmten sämtliche Arbeitsschritte des Gruppenmodellkontexts exakt mit der Hauptmatrix überein. Kontextumfang: 90.827 Zeichen innerhalb des Limits von 95.000. Raw-Evidenz-, Regel-/Matrix-, Entscheidungs- und Reviewumfangshash haben verschiedene Bedeutungen: Der Matrixhash bindet Quellen plus Schrittrules; der Entscheidungshash bindet das Journal; der Reviewhash bindet zusätzlich Registry, Vault, Aufnahme und Entwürfe. Ein alter Hash im Autorisierungsjournal ist keine implizite zeitliche Sperre. Die Annahme eines Nachweises braucht dessen aktuelle eigene Hashbindung.

Keine neuen Produkttests oder Produktänderungen in dieser Runde. Reale Modellprüfungen sind begrenzte Evaluierungen; eine allgemein optimale Kombination ist nicht bewiesen. Die bestehenden 0.4-Pilotnachweise bleiben gesonderte Evidenz.

Der Installer richtet die Workbench ein. Vollständige Nullinstallation inklusive Hermes/Routing auf einem fremden Windows-PC bleibt offen; CC Switch bleibt separat. Paketversion ist keine vollständige A–D-Abnahme.

# S2 — Genehmigte reine Testketten im isolierten Pilot

Status: Betreiberbestätigung am 17.09.2026 liegt vor. S2a sowie S2b/S2c implementiert. Vorschau bleibt ohne Ausführungsfreigabe; Start erfordert eine separate aktuelle gebundene Zustimmung. Journal-/Controller-/HTTP- und Browserprüfungen bestehen. Detaillierte abschließende Testergebnisse stehen in WIEDERAUFNAHME.md und HERMES_APP_ABSCHLUSS.md.

## Nachgewiesener Ausgangspunkt

- `execution_policy.require_staging_pilot` sperrt abhängige Änderungsschritte weiterhin ausdrücklich. Testschritte sind möglich, wenn der aufrufende Adapter ihre Vorgänger separat validiert.
- `plan_tests.preflight` verlangt aktuelle Auswahl, aktuellen Quellenstand und sämtliche aktuellen Vorgängerbelege. `run` testet eine versiegelte unveränderte Kopie und schreibt technische Abschlussbelege. `attempt_policy` zählt höchstens drei Aufträge pro Kandidat/Testschritt; alle Zustände zählen.
- `PlanBook.dependency_report` validiert Vorgänger rekursiv, einschließlich Beleg-IDs, Auswahl, Quellen und Adapter. Ein erfolgreicher Job allein ersetzt keinen Abschlussbeleg.
- `change_chain.confirm` erlaubt bislang genau einen Quellenübergang pro Kandidat, für einen unabhängigen Änderungsschritt. `PlanBook.execution_permission` sperrt weitere Änderungsausführung nach diesem Übergang. Diese Regeln einfach zu entfernen wäre keine sichere Erweiterung.
- S1 verwendet ein festes Profil, eine eindeutige Stage-Referenz und zwei feste Kindpositionen. Dieses Schema darf nicht stillschweigend für beliebige Testketten umgedeutet werden.

## Alternativen und Empfehlung

| Weg | Nutzen | Begrenzung / Aufwand |
|---|---|---|
| **S2: reine Testkette** | Prüft echte allgemeine Vorgängerfortsetzung mit bestehenden Testbelegen, ohne Modelle oder Zieländerungen. | Neues begrenztes Profil und Journal nötig; löst abhängige Änderungen noch nicht. Empfohlen. |
| Sofort mehrere abhängige Änderungen | Nähert sich allgemeiner Implementierungsfolge. | Benötigt Mehrfach-Quellenübergänge, zustandsabhängige Belegketten und Rollback-Semantik; deutlich größere Änderung der Sicherheitsgrenzen. Zurückstellen. |
| Sofort weitere Produkt-/Sprachadapter | Erweitert ausführbare Projektarten. | Erfordert explizite Zielprofile, Werkzeuge und Isolationsnachweise; löst die Vorgängersteuerung nicht. Anschließend separat planen. |

## Begrenztes Zielbild

Explizit ausgewählte zwei bis höchstens fünf noch nicht aktuell abgeschlossene `test`-Schritte aus genau einer aktuellen Planrevision eines aktiven, unabhängig erlaubten Single-Piloten. Keine Gruppen oder historischen Produktprojekte, keine frei formulierten Kommandos, kein Modellaufruf und keine Originaldateiänderung. Der vorhandene Standardbibliothek-unittest-Adapter bleibt die einzige Ausführung.

Ein zulässiger bereits bestätigter Quellenübergang darf über den bestehenden Dependency-Report berücksichtigt werden. S2 erzeugt keinen weiteren Übergang. Jeder Test benötigt seinen eigenen noch verfügbaren Versuch; vorhandene Limits werden weder erhöht noch durch neue Auswahl zurückgesetzt.

Ausführung strikt nacheinander im vorhandenen Einzel-Worker. Die serverseitige Reihenfolge ist topologisch; Gleichstände folgen der Reihenfolge der Schritte im gespeicherten Plan. Die UI zeigt diese Reihenfolge vor der Zustimmung. Außerhalb der Kette liegende Vorgänger müssen bereits aktuell abgeschlossen sein. Innerhalb der Kette liegende Vorgänger dürfen ausschließlich frühere Testschritte dieser Kette sein.

## Vorschau und gebundene Zustimmung

Neues, getrenntes Profil `plan_test_chain_v1`; S1-API und S1-Journal bleiben kompatibel.

Implementierte geschützte Routen:

- `POST /api/test-chains/preview`: exakt `{candidate_id, step_ids}`.
- `POST /api/test-chains/start`: exakt `{candidate_id, step_ids, binding_hash, note}`; nichtleere Begründung bis 2000 Zeichen.
- `POST /api/test-chains/cancel`: exakt `{chain_id}`.

Vorschau ohne Job-/Beleganlage, ohne Modellversand und ohne Ausführungsfreigabe. Sie prüft bei späteren Schritten die strukturelle Erreichbarkeit; deren Laufzeitbereitschaft bleibt ausdrücklich bedingt, bis ihre Vorgänger erfolgreich abgeschlossen sind. Keine simulierten oder vorab erzeugten Erfolgsbelege.

Bindung umfasst Profil-/Adapteridentität, Kandidat/Planrevision, Auswahl-ID, effektiven aktuellen Quellenstand und gegebenenfalls Quellenübergangs-ID, geordnete Schritt-IDs/-Hashes, registrierte Wurzel und deren Identität, explizite Dateiumfänge und aktuelle Bytes, aktuelle externe Vorgängerbeleg-IDs, jüngste Testversuche und verbliebene Budgets je Schritt. Eine neue Auswahl oder ein neuer fremder Versuch verändert die Bindung. Keine Zugangsdaten.

Start berechnet die Vorschau neu und verlangt exakte Übereinstimmung. Keine automatische Aufnahme, Auswahl, Nachweisannahme oder Freigabe. Modell-Egress wird für dieses ausschließlich lokale Profil weder benötigt noch erweitert.

## Persistenz, Fortsetzung und Abbruch

Eigenes additives Journal für Testketten mit unveränderlicher Zustimmung, festen Kindverweisen und append-only Ereignissen. Die globale Reservierungsprüfung muss S1, S2, manuelle Aufträge, automatische Reviews und Rückfrageantworten gemeinsam berücksichtigen. Startprüfung und Reservierung erfolgen in einer SQLite-Schreibtransaktion; kein zweiter Worker.

Höchstens eine Kettenaktivierung pro Auswahl-ID und kanonischer geordneter Schrittliste. Identische Wiederholung liefert nur Historie; abweichende Wiederverwendung wird abgewiesen. Eine spätere neue ausdrückliche Auswahl darf eine neue Aktivierung ermöglichen, verbrauchte Testversuche bleiben gezählt. Diese Regel ersetzt nicht das globale Drei-Versuche-Limit.

Kindanlage und Budgetprüfung müssen atomar sein. Nur der Controller erzeugt den exakt nächsten `plan_test`-Auftrag. Keine vorzeitige Anlage aller Kinder, da sie sonst Testsbudgets und Aktualität beeinflussen würde.

Nach jedem Kind: echte erfolgreiche Testevidenz, aktuelle Adapter-/Dateibindung und vom vorhandenen Adapter erzeugter Abschlussbeleg erforderlich. Erst nach terminalem erfolgreichem Jobstatus erkennt der Dependency-Report diesen Beleg als aktuellen Vorgänger. Deshalb wird der Kindabschluss zuerst dauerhaft gespeichert, während die Kettenreservierung bestehen bleibt; dann wird die aktuelle Vorgängerlage erneut geprüft und höchstens ein nächstes Kind atomar angelegt. Bei Crash in dieser Zwischenphase: Unterbrechung, kein Replay. Kein künstliches Vorziehen eines erfolgreichen Jobstatus oder Erfinden von Belegen.

Während der Folge werden ausschließlich die Referenzen auf eigene Versuche/Abschlussbelege gezielt fortgeschrieben. Andere Bindungsänderungen sperren die Fortsetzung. Budget- und Vorgängerprüfung außerdem unmittelbar vor jeder Adapterausführung.

Abbruch stoppt nur zugehörige eigene Arbeit. Ein laufendes Kind hält die Reservierung bis zur bestätigten Beendigung. Neustart unterbricht aktive Ketten/Kinder ohne automatische Wiederaufnahme. Bereits gespeicherte Belege bleiben historische Fakten; ihre Verwendbarkeit wird ausschließlich durch die bestehenden aktuellen Belegprüfungen entschieden. Keine automatische Löschung oder Rücknahme fremder Nachweise.

Terminale Zustände: `completed`, `blocked`, `failed`, `cancelled`, `interrupted`. `completed` bestätigt nur die freigegebene Testkette, niemals Produktgates, Änderungsausführung oder Deployment.

## Oberfläche und Abnahme

Explizite Testauswahl, Vorschau der Reihenfolge mit bedingten späteren Schritten, Pflichtbegründung, Start, Abbruch, Kindbelege und historische Zustände. Navigation/Neuladen startet nichts. Begründung und Auswahl dürfen bei periodischem State-Refresh nicht verloren gehen.

Erforderliche Nachweise mit echten temporären Dateien und echten Tests:

1. Zwei abhängige Tests erfolgreich; zweiter startet erst nach aktuellem Abschlussbeleg des ersten. Verzweigte Vorgänger und externe bereits abgeschlossene Vorgänger ebenfalls prüfen.
2. Fehlgeschlagener, leerer, nur übersprungener oder unvollständig belegter Test verhindert jedes weitere Kind.
3. Quellen-/Datei-/Adapter-/Auswahldrift, widerrufene oder ersetzte Vorgänger, fremder neuer Versuch und erschöpftes Budget sperren Start/Fortsetzung.
4. Abbruch vor Start, während jedes Kindes und zwischen Abschluss und nächster Anlage; Neustart an denselben Grenzen ohne Replay.
5. Gleichzeitige Starts S1/S2/manuell sowie Rückfrageantworten: genau ein reservierter Ausführungsplatz; keine Budgetumgehung.
6. Separat bestätigter bestehender Quellenübergang bleibt nutzbar, dessen Rollback entwertet die abhängige Kette.
7. Host/Origin/Sitzung/CSRF, strikte Anfragefelder, unveränderte Originalbytes, null Modellaufrufe, Browser-Neuladen ohne Start und vollständige Regression.

## Geplante Umsetzungsschnitte

- **S2a:** ausschließlich schreibfreie gebundene Vorschau und Negativtests. Keine Änderung bestehender Ausführungsrechte.
- **S2b:** separates additives Kettenjournal, gemeinsame Reservierung und atomare Budget-/Kindanlage; Konkurrenz-/Neustarttests.
- **S2c:** vorhandenen `plan_test`-Adapter anbinden, UI und durchgängige HTTP-/Worker-/Browser-Abnahme.

Betroffene bestehende Verträge: `plans.py`, `plan_tests.py`, `sequence_store.require_idle`, `jobs.py`, `server.py`, Jobs-/Planoberfläche. Neue Profil-/Journalmodule getrennt von S1 halten. S2a-Implementierungsplan: `../plans/2026-09-17-plan-test-chain-preview.md`; keine automatische Delegation, Modellumschaltung oder Produktintegration.

Selbstprüfung: spätere Vorgänger sind in der Vorschau nur bedingt erreichbar; keine erfundenen Belege. Abschlussbelege benötigen terminale Jobs, daher reservierte Zwischenphase implementiert. Vorhandene Budgets, Quellenübergangsgrenzen und S1-Schema bleiben erhalten. Betreiberzustimmung zum begrenzten S2-Profil liegt vor; Umsetzung und Abnahmen sind im Plan `../plans/2026-09-17-test-chain-execution.md` dokumentiert. Allgemeine abhängige Änderungen und Produktadapter bleiben außerhalb dieses Profils.

# Governor 0.2 – Entscheidungswissen, Schrittmatrix und hybride Gegenprüfung

## Betriebsmodell

Die am 12.09.2026 beauftragte Weiterentwicklung ergänzt die bisherige Beobachtung um ein Entscheidungsjournal und neun konkrete Arbeitsschritte. Die Matrix wird bei jedem Abruf aus Quellenstand, Journal und vorhandenen Aufträgen berechnet. Die Originalprojekte und der Snapshot werden dabei nicht überschrieben.

Die vier lesenden Schritte Quellenabgleich, RadiWorks-Intake, Radi144-Checkpoint und Morphic-Authority-Prüfung wurden entsprechend dem ausdrücklichen Fortsetzungsauftrag autorisiert. Es wurde keine fachliche Abnahme und keine Produktimplementierungsfreigabe erfunden. Auf anderen Installationen wird diese persönliche Autorisierung nicht automatisch gesetzt.

Der Betreiber hat zusätzlich den erweiterten Modellkontext und den dauerhaften Versand bei zukünftigen Änderungen ausdrücklich bestätigt. Automatische Reviews sind auf diesem Rechner aktiv, höchstens vier Versuche pro UTC-Tag und mindestens 15 Minuten auseinander. Unvollständige Evidenz löst keinen Lauf aus. Fehler zählen gegen das Limit. Beim Einschalten wird der aktuelle Stand als Ausgangspunkt übernommen; erst eine spätere Quellen-/Regel- oder Journaländerung löst einen neuen Lauf aus. Neue Installationen bleiben standardmäßig manuell.

## Bedienfolge

1. In **Governance** den priorisierten Schritt und seine Voraussetzungen prüfen.
2. Für einen noch nicht erlaubten Schritt **Autorisieren** mit konkreter Begründung wählen. **Abnehmen** bedeutet etwas anderes: Der Betreiber erklärt, dass die aufgeführten Nachweiskriterien tatsächlich erfüllt sind.
3. Einen angebotenen **Quellenbericht** ausführen. Er erzeugt im lokalen Laufverzeichnis ein JSON-Artefakt mit Quellen, Entscheidungen und Matrix. Dieses Inventar ist kein vollständiger fachlicher Contract-Intake.
4. **Alle Projekte reviewen** verwendet Terra und den ausgewählten Supervisor. **Sol / Astra vergleichen** erzeugt einen Terra-Plan und übergibt ihn mit identischem Kontext separat an beide Supervisoren.
5. Die lesbaren Ergebnisse, offenen Nachweise und Modellunterschiede prüfen. Die Herkunft und Quellenbindung bleiben im Auftrag sichtbar.
6. Erst nach tatsächlicher Prüfung der konkreten Kriterien die fachliche Abnahme mit Begründung im Journal erfassen. Danach wird die Reihenfolge der weiteren Schritte neu berechnet.

Für einen vollständigen RadiWorks-Intake bleiben die vollständige ABI-Feldmatrix und zwei unabhängige Prüfungen des exakt gebundenen Berichts erforderlich. Der allgemeine projektübergreifende Vergleich ersetzt diese Fachprüfung nicht.

## Regeln

- Die Source-Hashbindung enthält keine Betreiberentscheidungen: Eine Abnahme macht sich nicht selbst veraltet.
- Ein separater Entscheidungsfingerprint bindet Modellberichte und Quellenberichte an den verwendeten Journalstand.
- Die Gate-Definitionen sind ebenfalls an den Evidenzstand gebunden. Ein separater Source-Hash erhält unveränderte Produkt-Testnachweise auch bei geänderten Governor-Regeln. Testnachweise werden gezielt aus den letzten 100 Testaufträgen gelesen; spätere Browser-/Reviewaufträge verdrängen sie nicht.
- Widerrufe und Zurückweisungen werden angehängt. Frühere Einträge bleiben nachvollziehbar.
- Fehlende oder veraltete Voraussetzungen sperren nachgelagerte Schritte. Fachliche Abnahmen gelten nur für den aktuellen Quellenstand.
- Lesender RadiWorks-Intake benötigt den Quellenabgleich, aber keine bereits abgeschlossene Aurelia-Infrastrukturabnahme. Die spätere Integration benötigt die entsprechenden fachlichen Gates.
- Prioritäten sind eine explizite, deterministische Reihenfolge. Sie sind kein mathematischer Beweis einer global optimalen Projektplanung.
- Dokumentierte historische Aussagen und alte Reviews bleiben als Wissen mit Herkunft erhalten. Sie werden nicht allein wegen eines Stichworts wie „GO“ als aktuelle Abnahme übernommen.
- Ein Modell erteilt keine neue Erlaubnis. `approval_granted=false` bedeutet ausdrücklich nicht, dass der Betreiber zuvor keine lesende Prüfung erlaubt hat.
- Der aktuelle Reviewauftrag wird im Modellkontext als eigene begrenzte Autorität übergeben. Historische Snapshot-Pausen können ihn nicht aufheben.

## Technische Schnittstellen

`POST /api/decisions`: `step_id`, `kind` (`authorize`, `revoke`, `accept`, `reject`), `reason`, bei Abnahme zwingend `evidence_hash`. Die bestehenden Session-/Origin-/CSRF-Prüfungen gelten. Veraltete Quellenbindung ergibt HTTP409. Entscheidungsvalidierung und Speicherung sind gegenüber anderen Journalschreibvorgängen serialisiert.

`GET /api/state`: zusätzliche Felder `governor`, `decisions`, `evidence_hash`, `decision_hash` und `live_views`. Die Projektzeilen enthalten berechnete Werte; ursprüngliche Planungswerte bleiben als `documented_status` und `documented_next_step` erhalten.

`POST /api/actions`: zusätzlich `compare_reviews`, `governance_report` mit `step_id`, `live_start` mit `project_id`, `live_capture`/`live_stop` mit `live_id`. Es gibt weiterhin keine Eingabe beliebiger Shellbefehle.

`governance.py` bleibt eine reine Funktion ohne Dateischreibzugriffe oder Modellaufrufe. `store.py` migriert das bestehende SQLite-Journal additiv. Alte Aufträge bleiben lesbar.

## Grenzen

Die Anwendung implementiert weiterhin keine autonome Änderung fremden Produktcodes, keinen Git-Commit und keine Aurelia-Servermigration. Fachliche Implementierungszeilen zeigen Bereitschaft und Voraussetzungen, besitzen aber keinen allgemeinen Ausführungsadapter. Korrekturen am Gedächtnis erfolgen über den vorhandenen Editor; danach werden Quellen und Reviews erneut bewertet.

Neue Module lassen sich planen; individuelle ausführbare Schritte benötigen eine bewusste Erweiterung des Schrittkatalogs. Abhängigkeiten und Nachweiskriterien dürfen nicht aus unvollständigem Modelltext erfunden werden.

Chrome-Live-Views starten ein separates sichtbares Testfenster für bereits laufende konfigurierte lokale Anwendungen. Sie starten keine Produktserver automatisch. Details und Verifikationsgrenzen stehen in LIVE_VIEWS.md.

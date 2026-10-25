# Governors/Hermes: Entwicklerstatus zum Projektsicherungspunkt

Stand: 30.09.2026. Dieses Dokument ist ein Wegweiser durch den **aktuellen lokalen Arbeitsstand**, keine neue Freigabe oder vollständige Neuspezifikation. Maßgeblich bleiben Quellcode, gespeicherte Aufträge/Hashes und die jeweils verlinkten Prüfberichte. `Brainpower` ist kein eigenständiger Git-Root; der darüberliegende Benutzerprofil-Root ist kein sinnvoller Governors-Releasebeleg. Eine Dateisicherung muss deshalb die aktuellen Arbeitsbytes und Laufzeitdaten gesondert manifestieren.

## System und Wirkmechanismen

| Bereich | Ist und maßgebliche Quelle | Entscheidende Grenze |
| --- | --- | --- |
| Lokale Workbench | Python-Standardbibliothek in `governor_workbench/`, Vanilla JS/CSS in `governor_workbench/static/`; Browser auf Loopback mit Host-/Origin-, Session- und CSRF-Grenzen. [Entwicklerleitfaden](DEVELOPER_GUIDE.md). | Kein allgemeiner Produkt-Executor und keine Freigabe durch eine grüne Anzeige. |
| Projekte und Gruppen | Projekt-/Gruppenaufnahme, getrennte Übersichten, Quellenhashes, Drift- und Gate-Anzeige. Fünf bestehende Projektquellen bilden eine **historische** Integrationsgruppe; neue Einzel-/Gruppenprojekte bleiben logisch getrennt. [Governor 0.5](GOVERNOR_0_5.md), [Modulreihenfolge](MODULUEBERGANG_UND_BETREIBERPRUEFUNG.md). | Aktueller vollständiger Produkt-Matrixplan erst nach finalisierten lokalen Modulprototypen. Historische Gruppenplanung nicht als Aurelia-Implementierung lesen. |
| Aufträge/Journal | Ein begrenzter Worker; Aufträge, Versuche, Zustandsübergänge, getrennte Test-/Pilot-/Strategiebelege und Bedienentscheidungen werden im lokalen SQLite-Journal gehalten. Der aktuelle `runtime/journal.db` ist Teil der persönlichen Sicherung; bei laufender App nur per SQLite-Online-Backup konsistent kopieren. | Kein automatisches Wiederholen unterbrochener Aufträge und kein Modelltext als Befehl. `auto_review` blieb zuletzt aus; vor Neustart erneut prüfen. |
| Gedächtnis | Inventarisierte `project_memories/*.md` werden je Auftrag quell- und hashgebunden gelesen. Über der 95.000-Zeichen-Grenze erfolgt eine beleggebundene Abschnittsverarbeitung mit mindestens zwei lesenden Rollen; Schlussmodelle erhalten begrenzte Belege und Gliederung, **nicht** den kompletten Rohtext. Ein lokaler Zwischenbeleg-Cache gilt nur bei identischem Quellenhash, Modell, Reasoning und Regelversion. [Stufenbericht](verification/HERMES_MEMORY_STAGES_2026-09-26.md). | Lückenlose Abschnittsabdeckung beweist Transport/Herkunft, nicht semantische Vollständigkeit. Quellenänderung oder fehlende Belege stoppt; Modellgedächtnis ersetzt keine Produktquelle. |
| Strategie und Testketten | Aufnahmeentwurf ≠ bestätigte Aufnahme; Kandidat ≠ übernommene Strategie; Strategie ≠ Ausführungsrecht. Quell-/Entscheidungs-/Reviewhash und append-only Revisionen mit CAS/Frischeprüfung halten diese Schritte auseinander. Begrenzte Testketten und Pilotpfade haben eigene Belege. [Governor 0.5](GOVERNOR_0_5.md), [Betriebsvertrag](LLM_OPERATING_CONTRACT.json). | Keine allgemeine automatische Folgeausführung, keine stillschweigende Übernahme externer Produkt-Gates. |

## Hermes-Anwendungsrouten und Codex-Chat

| Weg | Rollen / Auswahl | Stand |
| --- | --- | --- |
| Alter manueller Hybridweg | Terra 5.6 plus ausgewählter Sol-/Astra-Supervisor; bei jedem Auftrag bewusst gewählt. | Teilabnahme für lokalen Einzelreview. [Funktionsgrenze](HERMES_APP_ABSCHLUSS.md). |
| Hermes Route B | Sol 6/high führt, Luna 6/max arbeitet unabhängig; Astra 6/medium bei Risikosignal/ausdrücklicher Wahl beim Einzelreview, bei neuem Route-B-Matrixplan als unabhängige Pflichtprüfung. | Manuelle Einzelreviews lokal verwendbar, neue volle Gruppen-/Matrixplanabnahme offen. Route und Modellversand werden pro Auftrag ausdrücklich gewählt. [Routenbericht](verification/HERMES_ROUTE_B_2026-09-24.md). |
| Codex-Chat-Route B | Eigenes Codex-Chat-Profil Sol/high → begrenztes Luna/max → Astra/medium bei kritischem Restfall. | **Nicht** dieselbe Routinginstanz wie Hermes. [Aktuelle portable Anleitung](CODEX_CHAT_ROUTE_B_TRANSFER_2026-09-30.md); wirksame Modellwahl im laufenden Chat nicht allein aus TOML beweisbar. |

Hermes-Modelltransport ist explizit, gebunden und null-Werkzeug; Review und Plan sind keine Produktfreigaben. Bei großen Gedächtnissen sind zusätzliche Modellaufrufe möglich. Reale Qualitäts- und Kostenvorteile über längere Projektläufe sind nicht allgemein belegt. Automatische Reviews bleiben ausgeschaltet, solange der Betreiber sie nicht erneut aktiviert.

## Aurelia-Matrix und aktuelle Reihenfolge

Die Governor-Matrix zeigt pro Projekt/Gruppe **beobachteten** Quellen- und Gate-Stand, nicht einen bereits vollständig erstellten Aurelia-Produktplan. Lokale Prototypenreihenfolge: **RadiWorks → Radi144 → `morphic_v1` → neues Modul mit eigenem Pfad**; RadiFarben ist noch nicht als der vierte Prototyp festgelegt. Erst danach aktuelle Aufnahmen bestätigen, vollständigen Gruppen-Matrixplan erstellen und separat prüfen/übernehmen. Aurelia-Produktimplementierung bleibt hinter `G0-SRV-GROUND-ZERO` und `AUDIT-02`. Design-Synthese aus Governor/Hermes ist ein eigener D0–D4-Strang mit getrennten Modulakzenten, keine Übertragung der Hermes-Fachlogik. [Designplan](AURELIA_DESIGN_TEMPLATE.md), [Aurelia-Gesamtstatus](AURELIA_CROSS_PROJECT_STATUS_2026-09-30.md).

## Wiederaufnahme für Entwickler und LLM

1. [README](../README.md), [Entwicklerleitfaden](DEVELOPER_GUIDE.md), [LLM-Betriebsvertrag](LLM_OPERATING_CONTRACT.json) und [aktuellen Fortsetzungsstand](../WIEDERAUFNAHME.md) lesen; datierte historische Berichte nicht als neue Anweisung behandeln.
2. Sicherungsmanifest und SQLite-Integrität prüfen. Quellpfade, Hashes, Git-HEAD und WIP **frisch** erfassen; niemals aus dem Sicherungsdatum auf einen aktuellen Live-Stand schließen.
3. Vor einem Modellauftrag Projekt-/Gruppenumfang, Quellen-/Gedächtnishashes, Versandfreigabe und gewählten Weg prüfen. Keine alten unterbrochenen Aufträge wiederholen.
4. Produktarbeit nur innerhalb des jeweiligen Modulgates; der [RadiWorks-S4-Stand](verification/RADIWORKS_S4_READINESS_2026-09-28.md) ist derzeit lokal und nicht S4.8-freigegeben.

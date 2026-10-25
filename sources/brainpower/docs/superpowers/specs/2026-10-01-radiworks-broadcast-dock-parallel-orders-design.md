# RadiWorks: Broadcast-Dock und Vertrag für parallele Fallaufträge

Stand: 01.10.2026. Der Betreiber hat das ausklappbare Dock und einen zunächst dokumentierten Auftragsvertrag gewählt. Dies ist ein Entwurf für den lokalen RadiWorks-Kandidaten auf Port 8103 und die spätere Aurelia-Anbindung; er erteilt keine Host-, S4- oder Hardwarefreigabe.

## Ausgangslage und Ziel

Die Analyse zeigt eine breite, lange Ergebnistabelle. Die dauerhafte Statusleiste steht erst hinter dem Hauptinhalt und bietet für Broadcast-Queue und Resonanzen nur kleine Teilspalten mit 150 px Listenhöhe. Ein Nutzer soll bei der Analyse aktive und wartende virtuelle Broadcasts samt Fortschritt leichter erkennen, ohne die Tabelle schmaler oder die vorhandene Broadcast-Detailseite unzugänglich zu machen.

Der lokale Engine-Prozess besitzt einen gemeinsamen aktiven Fall, eine gemeinsame GV-Runde und eine gemeinsame Broadcast-Queue. Die Queue kann mehrere virtuelle Elemente tragen (`MAX_ACTIVE = 8`), aber deren Gleichzeitigkeit beweist keine voneinander getrennten Aufträge für denselben Fall. Neue Analysen ersetzen den gemeinsamen GV-Rundenzustand. `WorkflowRegistry` partitioniert nur einen Teil der Daten und ist kein aktiver paralleler Hostmanager.

## Geprüfte Layoutwege

1. **Nur Statusleiste vergrößern:** Wenig Code, aber die Leiste bleibt bei langer Analyse unterhalb des sichtbaren Bereichs.
2. **Ausklappbares Broadcast-Dock (gewählt):** Während der Analyse eine schmale, sichtbare Zusammenfassung am unteren Fensterrand; auf Wunsch eine größere Ansicht mit Queue, Fortschritt und Resonanz. Die Analyse bleibt breit, die Broadcast-Detailseite bleibt erhalten.
3. **Analyse und Broadcast nebeneinander:** Zeigt beides gleichzeitig, drängt aber die bereits zehnspaltige Ergebnistabelle in eine schmale Fläche und verschlechtert Reflow.

## Dock-Verhalten

- Nur in der Analyseansicht wird die bestehende Statusleiste als Dock präsentiert; auf anderen Ansichten bleibt sie im bisherigen Dokumentfluss. Es gibt keine zweite Queue und keine neue Broadcast-Aktion.
- Im eingeklappten Zustand zeigt eine etwa 48 px hohe Zeile den Status „Broadcast“, Anzahl aktiv/wartend und einen eindeutig benannten Schalter „Broadcast-Status öffnen“. Im erweiterten Zustand werden Queue und Fortschritt deutlich größer gezeigt; Resonated Rates, LEDs und GV bleiben vorhanden. Die tatsächlichen Werte stammen weiterhin aus den bestehenden API-/WebSocket-Daten.
- Desktop: Das erweiterte Dock nutzt höchstens etwa 30 % der Fensterhöhe und lässt der Ergebnistabelle den übrigen Raum. Schmale Ansichten starten eingeklappt und erweitern sich innerhalb des Viewports. Der Seiteninhalt erhält passenden unteren Abstand, damit die letzte Ergebniszeile und Bedienelemente erreichbar bleiben.
- Der Schalter nutzt `aria-expanded`/`aria-controls`; Tastaturfokus, Escape zum Einklappen, sichtbarer Fokus und reduzierte Bewegung werden geprüft. Bestehende Statusmeldungen und Lesereihenfolge bleiben erhalten. Ein neuer Zustand wird nur im aktuellen Browser gehalten; nach Neuladen ist das Dock eingeklappt.
- Die Broadcast-Detailseite und ihre virtuellen Funktionen bleiben unverändert. Port 8102, Radi144/8090 und Governor/8787 bleiben unangetastet.

## Vertrag für mehrere getrennte Aufträge pro Fall

Der lokale Kandidat aktiviert **keine** parallelen Fallaufträge. Der versionierte Modul-/Aurelia-Vertrag soll vor einer Implementierung Folgendes festlegen:

- Ein Fall bekommt einen stabilen opaken `case_id`, unabhängig vom Anzeigenamen; jeder Auftrag hat eine eigene `job_id` und eine vom Host gebundene Idempotenzkennung. Autorität kommt serverseitig aus verifizierter Sitzung, Mandant, Klient und Rolle, nie aus frei gesetzten Browserfeldern.
- Jeder Auftrag bindet einen unveränderlichen Katalog-Release, Analyse- und GV-Zustand, Draft, Passport, Entropie-Journal, Recovery-Marker und seine Events. Der gemeinsame Fall führt mehrere Aufträge über revisionsgesicherte Sitzungen oder append-only Ereignisse zusammen; ein Auftrag darf einen anderen weder überschreiben noch stoppen.
- Broadcast-Queue, Stop-Befehle, Auto-Modus, Replay-Cursor und WebSocket-Verbindungen werden pro Auftrag/Scope autorisiert. Quoten und Fairness für mehrere aktive Aufträge werden vor Freigabe festgelegt; das lokale `MAX_ACTIVE = 8` ist kein Aurelia-Kapazitätsversprechen.
- Synthetische Parallel-, Abbruch-, Widerrufs-, Neustart-, Doppel-POST- und identische-Namen/IDs-Negativtests müssen Daten- und Wirkungsisolation nachweisen. Die aktuelle feste `AppState`-Instanz und die nur teilweise verwendete `WorkflowRegistry` erfüllen diesen Nachweis nicht.
- Die Modulreferenz in `Modul_Templates` erhält einen versionierten Delta-/Profilvermerk. Die konkrete Hostarchitektur (Engine je Scope oder nachweislich partitionierter gemeinsamer Host) wird nach Aurelias G0-SRV-GROUND-ZERO, AUDIT-02 und Hostautoritätsentscheidung festgelegt. Bis dahin bleibt echte Parallelität gesperrt.

## Umsetzung und Prüfung nach Entwurfsabnahme

1. Dock ausschließlich im getrennten 8103-Kandidaten implementieren; keine Engine-, Queue- oder Datenmigration.
2. Mit künstlichen Daten Desktop und 320/390-px-Ansichten, Ein-/Ausklappen, Tastatur, Fokus, fehlende/aktive Queue, Ergebnisende und reduzierte Bewegung prüfen; bestehende Engine-/Browserchecks passend wiederholen.
3. Den parallelen Auftragsvertrag im RadiWorks-Hostprofil und als `Modul_Templates`-Delta dokumentieren, ohne den normativen API-Vertrag oder die produktiven Repositories stillschweigend umzuschreiben.
4. Betreiber-Nachtest auf 8103; erst danach Kandidaten-/Template-Referenzen synchronisieren und eine eigene S4.8-Entscheidung vorbereiten.

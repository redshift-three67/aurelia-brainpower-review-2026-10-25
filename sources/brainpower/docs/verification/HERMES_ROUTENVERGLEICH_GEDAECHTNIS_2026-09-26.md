# Hermes: aktueller RadiWorks-Paarvergleich nach Gedächtnisänderung

Stand: 26.09.2026. Zwei ausdrücklich manuell und nacheinander gestartete Einzelreviews. Der Betreiber hat die Ursache des Rechnerproblems als eigenen, behobenen Fehler eingeordnet. Dieser Bericht prüft Hermes-Auftragsbelege, nicht die allgemeine Rechnerstabilität.

## Gemeinsame Bindung und Bedienung

Vor beiden Starts und danach lieferte der frische RadiWorks-Scan denselben Scope-SHA-256: 9a07a4dc02dc9696cc12cbde95f23972737ff690f2b548a6b31ac95db153d917. Beide Aufträge endeten ohne Fehler und mit stale=false. Ihre Gedächtnisbelege melden full und enthalten dieselben SHA-256-Werte für die vollständig gelesenen Dateien proposed_strategy.md (25.513 Bytes) und strategy_project_2.md (33.648 Bytes). Die Modellkontext-Hashes unterscheiden sich zwischen den Routen; identische gesamte Modellprompts sind damit nicht belegt. Full bestätigt die technische Zuführung der ausgewählten Dateien, nicht semantisch lückenloses Modellverständnis.

Im laufenden lokalen Governor öffnete die Gruppenkachel die Gruppenübersicht und RadiWorks seine eigene Projektübersicht. Für beide Umfänge waren alter Hybridreview und Route-B-Review sichtbar und aktiv, beide Planaktionen bei plan_ready=false gesperrt. Die Browserprüfung löste keinen POST aus. Automatische Reviews blieben deaktiviert.

| Merkmal | Alter Hybrid | Route B |
|---|---|---|
| Auftrag | 90834259978c475e95e94ec68b06fa78 | f5d6d17a81224c47b718c8ac9e3792c6 |
| Aufgerufene Rollen | Terra 5.6/medium, Sol 5.6/medium | Sol 6/high, Luna 6/max, Astra 6/medium |
| Dritte unabhängige Rolle | Keine in diesem Einzelreview | Astra ausdrücklich angefordert; eigener kritischer Bericht |
| Gesamttokens laut Auftragsbeleg | 40.896 | 63.321 |
| Summe der Modelllaufzeiten laut Beleg | 45,359 s | 140,531 s |
| Ergebnis | REVIEW_ONLY | REVIEW_ONLY |
| Produkt-/Strategiefreigabe | Keine | Keine |

Die Route-B-Bindungsbelege weisen route-b-v2 und die drei tatsächlichen Rollen samt Reasoning aus. Beim alten Weg wurden Terra und Sol tatsächlich aufgerufen. Beide Wege erkannten die wesentlichen Sperren: unbestätigte beziehungsweise nicht HEAD-gebundene Strategie-/Quellnachweise, fehlende angenommene hashgebundene Aufnahme und unabhängige Reviews, Aurelia-G0-/Gruppenvoraussetzungen sowie fehlende Implementierungsfreigabe. Der alte Bericht formulierte 15 strukturierte Befunde und neun erforderliche Belege; Route B formulierte null strukturierte Befunde und vier Planblocker. Daraus folgt keine Qualitätsrangfolge: Die relevanten Sperren stehen bei Route B im Plan, aber der ältere Bericht ist in diesem Einzelfall detaillierter.

Route B verbrauchte in diesem Lauf 22.425 Tokens beziehungsweise rund 55 % mehr. Das ist kein fairer Zwei-Routen-Kostenvergleich, weil dort Astra als dritte Rolle ausdrücklich hinzugeschaltet war. Die Auftragsbelege meldeten für alle Modellaufrufe null Cache-Tokens. Ein Einzelfall belegt weder allgemeine Kostenersparnis noch langfristige Zuverlässigkeit.

## Abnahmegrenze

Technisch belegt sind für RadiWorks die manuelle Auswahl beider Reviewwege, vollständige Zuführung der beiden ausgewählten Gedächtnisdateien, tatsächliche Modellrollen, Hash-/Driftbindung und intakte REVIEW_ONLY-Sperren. Das ist eine begrenzte technische Teilprüfung für Einzelreviews. Ein echter vollständiger Mehrstufen-Gruppenlauf mit übergroßem Gedächtnis ist weiterhin nicht belegt; vorhandene synthetische Tests ersetzen ihn nicht. Ein echter Matrixplan bleibt bei plan_ready=false absichtlich gesperrt und folgt gemäß Betreiberreihenfolge erst nach den vier finalisierten Modulprototypen. Formelle Betreiberabnahme und jede Produkt- oder Serverfreigabe sind separat.

Siehe [Funktionsabnahme](HERMES_FUNKTIONSABNAHME_2026-09-25.md) und [Modulübergang](../MODULUEBERGANG_UND_BETREIBERPRUEFUNG.md).

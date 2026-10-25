# RadiWorks-Review — 11 verifizierte Befunde

- **Checkpoint-ID:** `20260904T210517Z-radiworks-review-11`
- **Status:** statische, streng read-only Prüfung; keine Tests ausgeführt.
- **Verwendungsregel:** Dieses Dokument ist technische Evidenz. Plattformweite Anforderungen werden erst durch einen expliziten Aurelia-Freigabeprozess verbindlich.

## RW-01 — Pfad-Traversal beim Speichern von Fällen

- **Evidenz:** `radiworks_port/engine/src/radiworks/api/routes.py:802`; `radiworks_port/engine/src/radiworks/core/cases.py:36,59`
- **Fehlerszenario:** `POST /cases` mit einem Namen wie `../drafts/poc` wird ohne Pfadbegrenzung in einen Dateipfad umgesetzt.
- **Auswirkung:** JSON-Dateien außerhalb des Fallverzeichnisses können in erreichbaren Verzeichnissen erstellt oder überschrieben werden.
- **Konfidenz:** Hoch
- **Relevanz:** lokal und plattformübergreifend — sichere Artefaktpfade.

## RW-02 — Inkonsistenter `max_hits`-Vertrag

- **Evidenz:** `radiworks_port/engine/src/radiworks/api/routes.py:287-292`; `radiworks_port/engine/src/radiworks/core/analysis.py:172-173`
- **Fehlerszenario:** Eine Analyse mit gültiger Datenbank und `max_hits: 101` passiert die Request-Validierung, löst aber in der Analyse `ValueError` aus.
- **Auswirkung:** Ein laut API gültiger Request kann als Serverfehler statt als Client-Validierungsfehler enden.
- **Konfidenz:** Hoch
- **Relevanz:** lokal und plattformübergreifend — ABI-/Validierungsvertrag.

## RW-03 — Bild-Broadcast kann den Worker blockieren

- **Evidenz:** `radiworks_port/engine/src/radiworks/api/routes.py:616-626`; `radiworks_port/engine/src/radiworks/core/broadcast.py:237-281,346-351`
- **Fehlerszenario:** Ein Bild-Broadcast mit nichtleerem MD5 und `multiplier: -6765` wird akzeptiert; die nachfolgende Zufallsziehung erhält eine Obergrenze von null.
- **Auswirkung:** Der Broadcast-Worker kann enden, während das fehlerhafte Element aktiv bleibt; spätere Broadcasts werden nicht zuverlässig verarbeitet.
- **Konfidenz:** Hoch
- **Relevanz:** lokal und plattformübergreifend — Eingangsvalidierung und fehlertolerante Worker-Lebenszyklen.

## RW-04 — GV-Runden werden nicht persistiert

- **Evidenz:** `radiworks_port/engine/src/radiworks/api/routes.py:470,500-507,511-520`
- **Fehlerszenario:** Nach einer Analyse wird eine GV-Runde ausgeführt und danach die aktuelle Analyse geladen oder der Prozess neu gestartet.
- **Auswirkung:** Persistierter Draft und Fall enthalten Werte vor der GV-Runde; die Mutation existiert nur im flüchtigen Arbeitsspeicher.
- **Konfidenz:** Hoch
- **Relevanz:** lokal und plattformübergreifend — persistente Artefakte und Wiederanlauffähigkeit.

## RW-05 — Manifest und Ergebnis-Payload sind ABI-inkompatibel

- **Evidenz:** `radiworks_port/engine/src/radiworks/manifest.py:38-54`; `radiworks_port/engine/src/radiworks/core/analysis.py:107-112`
- **Fehlerszenario:** Ein Client validiert oder deserialisiert eine Analyseantwort anhand des über `/manifest` veröffentlichten Output-Schemas.
- **Auswirkung:** Das Schema erwartet snake_case, die tatsächliche Payload verwendet camelCase.
- **Konfidenz:** Hoch
- **Relevanz:** lokal und plattformübergreifend — selbstbeschreibende Kernel-ABI.

## RW-06 — Gold-Paritätstest deckt den produktiven Entropiepfad nicht ab

- **Evidenz:** `radiworks_port/engine/src/radiworks/entropy.py:42-46,174-185`; `radiworks_port/engine/tests/test_gold_parity.py:28-60`
- **Fehlerszenario:** Eine produktive Analyse mit dem Gold-Fixture-Seed verwendet Python `random.Random`, der Test injiziert dagegen `JavaRandom`.
- **Auswirkung:** Ein erfolgreicher Goldtest belegt nur die Analyse mit Test-Adapter, nicht die Java-Parität des produktiven REST-Pfads.
- **Konfidenz:** Hoch
- **Relevanz:** lokal und plattformübergreifend — reproduzierbare Kernelausführung und Testbeleg.

## RW-07 — Passport-Seed ist nicht reproduktionsfähig

- **Evidenz:** `radiworks_port/engine/src/radiworks/passport.py:65-67`; `radiworks_port/engine/src/radiworks/entropy.py:211-214`
- **Fehlerszenario:** Der im Passport ausgegebene `seed` wird für einen identischen Folgeaufruf wiederverwendet.
- **Auswirkung:** Der Folgeaufruf erhält eine andere Entropiesequenz, weil der Passport einen abgeleiteten Hashwert statt des wirksamen Eingabeseeds führt.
- **Konfidenz:** Hoch
- **Relevanz:** lokal und plattformübergreifend — Computation-Passport und Auditierbarkeit.

## RW-08 — CopyGuard-Nachweis fehlt im Passport

- **Evidenz:** `radiworks_port/engine/src/radiworks/core/draft.py:60-79`; `radiworks_port/engine/src/radiworks/passport.py:40,88-105`
- **Fehlerszenario:** Passport und erzeugter Draft derselben Analyse werden verglichen.
- **Auswirkung:** Der Draft enthält den berechneten CopyGuard-Digest, der Passport serialisiert ihn jedoch als `null`; der geprüfte sichtbare Textbestand ist im Passport nicht nachweisbar gebunden.
- **Konfidenz:** Hoch
- **Relevanz:** lokal und plattformübergreifend — Artefaktprovenienz und Auditierbarkeit.

## RW-09 — Ungültiger persistierter Entropiemodus verhält sich inkonsistent

- **Evidenz:** `radiworks_port/engine/src/radiworks/api/routes.py:572-588,113-120,761-770`; `radiworks_port/engine/src/radiworks/entropy.py:138-145`
- **Fehlerszenario:** `entropy.defaultMode` wird auf einen ungültigen String gesetzt und `/gv` ohne Request-Modus aufgerufen.
- **Auswirkung:** Der Live-Pfad endet mit `ValueError`, andere Pfade normalisieren den gleichen ungültigen Wert stillschweigend auf `seeded`.
- **Konfidenz:** Hoch
- **Relevanz:** lokal und plattformübergreifend — Konfigurationsvalidierung und deterministisches Fehlerverhalten.

## RW-10 — Wiederholte Analysen überschreiben die letzte Fall-Session

- **Evidenz:** `radiworks_port/engine/src/radiworks/core/cases.py:107-122`
- **Fehlerszenario:** Für einen geladenen Fall mit bestehender Session-Liste werden zwei Analysen ausgeführt.
- **Auswirkung:** Analyseergebnis und Passport der letzten Session werden überschrieben; das vorherige Ergebnis ist im Fall nicht mehr abrufbar.
- **Konfidenz:** Hoch
- **Relevanz:** lokal und plattformübergreifend — Versions-/Session-Semantik persistenter Fachartefakte.

## RW-11 — Sensible Falldaten liegen im Projektbaum

- **Evidenz:** Repository-lokales Fallartefakt unter `radiworks_port/engine/radiworks_home/cases/` (Pfad und Werte in diesem Evidenzdokument absichtlich redigiert).
- **Fehlerszenario:** Der Projektbaum wird kopiert, archiviert, verteilt oder in einen Build-Kontext aufgenommen.
- **Auswirkung:** Direkt identifizierende Angaben können gemeinsam mit einer gesundheitsbezogenen Beschreibung offengelegt werden.
- **Konfidenz:** Hoch
- **Relevanz:** lokal und plattformübergreifend — Datenminimierung, Sanitierung und Freigabegates für externe Evidenz.

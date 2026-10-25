# RadiWorks – geprüfte Restpunkt-Roadmap

Stand: 31. August 2026. Diese Liste trennt den aktuell laufenden Reliability-Sprint von größeren Vertrags-, Persistenz- und Produktentscheidungen. Sie ersetzt keine fachliche Freigabe und enthält keine automatische Zusage für Git-Historienänderungen oder externe Veröffentlichungen.

## R0 – Reliability-Sprint abschließen

- Auto-Modus aus dem Leerlauf linear starten und alte Analyse-Worker von weiteren Entropiezügen abhalten.
- Broadcast-Instanzen über `broadcastId` trennen; Stop Current und Stop All vollständig ausführen.
- WebSocket-Handshakes begrenzen, Send-Timeouts anwenden und Replay-Lücken signalisieren.
- Frontend nach Timeout, Replay-Lücke und Engine-Neustart über REST reconciliieren.
- Threads, WebSocket-Sender und Clients beim App-Shutdown begrenzt beenden.
- Gezielte Tests, vollständige Engine-Suite, JavaScript-Parsing und Browser-Abnahme bestehen.

## R1 – Integrität und belastbare Verträge

### Datenschutz und Repository-Hygiene

- Die bereits getrackten Dateien unter `webapp/docs/screenshots/` einzeln auf Fallnamen, Absichten oder andere personenbezogene Inhalte prüfen.
- Erst danach entscheiden: nur ersetzen/entfernen oder mit gesonderter Freigabe die Git-Historie bereinigen.
- Getrackte Build-Artefakte (`*.egg-info`, Gold-Harness-Ausgaben) prüfen und Ignore-Regeln für den verschachtelten Engine-Pfad korrigieren.

### Java-/Python-Parität

- Eine Paritätsmatrix pro Algorithmus und Laufzeitpfad erstellen, statt eine pauschale 1:1-Aussage zu verwenden.
- Java-PRNG, Java-HashMap-Reihenfolge und Grenzen des Gold-Harness explizit ausweisen.
- Den normalen REST-Produktionspfad separat gegen Goldwerte testen; Testadapter nicht mit Produktionsparität gleichsetzen.
- Produktentscheidung: seeded Kernalgorithmen erhalten Java-Parität nur mit unabhängigen JDK-Orakeln; REST-Hülle, Persistenz und stochastic bleiben separat spezifiziert.

### Kernel ABI und Computation Passport

- REST-ABI v1 beschreibt `/analysis` mit camelCase-Ergebnis, Passport und Draft; der frühere Core-Callable-Eintrag bleibt bis zu einem ausdrücklich freigegebenen Major-Gate als deprecated compatibility metadata erhalten.
- Passports v2 führen wirksamen Replay-Seed, aufgelösten Entropie-Modus im `input_hash`, `input_hash_scheme` und `replayable`; historische Passports ohne diese Kennzeichnung bleiben Legacy-v1-Artefakte.
- CopyGuard-Digest ist im Passport enthalten und gegen den Draft contract-getestet.
- `signatur` ist explizit `unsigned`; ein vollständiger Signaturvertrag ist ein separates, freigabepflichtiges Vorhaben.
- Versionierte JDK-Orakel-Fixtures belegen den seeded 300-Raten-REST-Pfad für zwei Seeds bei `max_hits=100` sowie einen Seed bei `max_hits=1000`. Kollisions-/Treeify-Grenzen und Hilfsalgorithmen bleiben separate Gates.

## R2 – Persistenz und Laufzeitkonsistenz

### Cases, Sessions und GV-Runden

- Pro Analyse/GV-Runde nachvollziehbare Session-Versionen persistieren, statt nur die letzte Session fortzuschreiben.
- GV-Schritte und Reset in Draft/Case speichern und Wiederaufnahme testen.
- `recurring` fallübergreifend berechnen, persistieren und in der REC-Spalte belegen.

### Datenbereitstellung

- Einen reproduzierbaren, lizenzierten und datenschutzsicheren Import-/Bootstrap-Weg für Rate-Daten dokumentieren oder implementieren.
- Clean-Checkout- und First-Run-Verhalten testen; lokale Betreiber-Daten bleiben außerhalb des Repositories.

### Settings, Entropie und Drafts

- Jeden sichtbaren Settings-Schalter entweder wirksam verdrahten oder als nicht unterstützt kennzeichnen.
- UI-Texte, `/entropy/status`, Default-Modus, Random.org-Stufe und tatsächlichen Provider konsistent machen.
- Draft-Detailroute, Sieben-Tage-TTL und Archiv-/Bereinigungsverhalten definieren und testen.

## R3 – Bewusste Produktentscheidungen und Wartung

Für jeden Punkt ist vor Implementierung festzulegen, ob er Produktumfang oder explizites Nicht-Ziel ist:

- Card Generator
- Resonanzprotokoll-Persistenz
- 500-ms-Duplicate-Start-Guard des Originals
- MapDesign/OpenLayers
- Watchlist-Startverhalten
- Materia-Medica-Suche per SQLite FTS5

Anschließend:

- Root- und Port-README auf den tatsächlichen RadiWorks-Stand bringen.
- Fehlende/veraltete Verweise auf nicht vorhandene `Modul_Templates`- und `docs/*`-Dokumente korrigieren.
- Generierte Artefakte aus dem getrackten Quellbestand entfernen, ohne lokale Betreiber-Daten anzutasten.

## Freigabepunkte

Folgende Schritte erfolgen nicht implizit:

1. Commit, Branch, Push oder Remote-Konfiguration.
2. Entfernung oder Umschreiben von Git-Historie.
3. Festlegung exakter Java-Parität gegenüber Aurelia-Abweichungen.
4. Aufnahme der optionalen R3-Funktionen in den Produktumfang.

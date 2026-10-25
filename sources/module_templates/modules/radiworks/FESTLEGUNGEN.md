# RadiWorks — Festlegungen (verbindlich)

> Abgestimmt mit dem Betreiber am 2026-08-29. Diese Festlegungen sind für alle
> RadiX-Module vorbildlich: Originalmechanik bleibt erhalten und wird erweitert;
> Aurelia-Pflichten werden per konfigurierbarem Default erfüllt, nicht durch
> Entfernung von Funktionalität.

## Festlegung 1 — Entropie: Settings-gesteuert

| Aspekt | Festlegung |
|---|---|
| Factory-Default | `seeded` (Aurelia Hard Rule 7: strikte Reproduzierbarkeit ist Default) |
| Arbeitsmodus | Settings-Schlüssel **`entropy.defaultMode`** = `seeded` \| `stochastic` (config/Settings.json) |
| Original-Hotbits | Unter `stochastic`: Webcam-/Hotbits-FIFO → random.org → OS-CSPRNG; `seeded` löst keinen Netzverkehr aus |
| Seed-Semantik | Die Java-PRNG-/HashMap-Mechanik ist nur im in `Radiworks/radiworks_port/engine/PARITY_MATRIX.md` beschriebenen Fixture-Umfang als Java-Orakelparität belegt; keine allgemeine Bitidentitätsbehauptung |
| Provenienz | Neue Passports protokollieren wirksamen Seed, `replayable` und `seed_scheme`; stochastic ist `seed: null` und nicht replaybar |
| Überschreibung | `mode` im Request überschreibt die Einstellung fallweise; ungültige Modi → HTTP 422 |

## Festlegung 2 — Broadcast-Mix: beide Wege, Settings-wählbar

| Aspekt | Festlegung |
|---|---|
| Default | **Zweiklick** (Aurelia D18): Draft sichtbar prüfen → `POST /drafts/{id}/promote` |
| Legacy-Modus | Settings-Schalter **`broadcast.legacyMixMode`** = `true` → **Ein-Klick** wie Original: `POST /broadcast/mix` erzeugt Draft-Kette (draft → ready → promoted) automatisch |
| CopyGuard | gilt in BEIDEN Wegen fail-closed vor Promote (HTTP 409 bei Block) — auch im Einklick |
| Mix-Algorithmus | 1:1 aus Original `broadcastMix` (nur Raten mit gv > caseGV, Sortierung gv desc, dann energetischer Wert; ohne gemessene gv-Werte: energiestärkste Raten als dokumentierter Fallback) |
| Direkt-Broadcast | `POST /broadcast` (BROADCAST NOW-Äquivalent) bleibt direkter Operator-Befehl ohne Draft — bewusster Befehl ist kein „stiller Copy" |

## Festlegung 3 — Emitter: VirtualEmitter (Original-Choreografie als Events)

| Aspekt | Festlegung |
|---|---|
| Mechanik | `core/emitter.py`: exakter Port von `BroadCastService.broadcastNow` — Signatur-Bereinigung (`(`, `)`, `-`, Leerzeichen), `abs(ord(c)-48)`, mehrstellige Werte ziffernweise, LED-Gruppen whites[0,9]/infrared[1,6]/reds[2,5]/greens[3,7]/blues[4,8], Blink-Rhythmus delay 25 ms, repeat |
| Clear-Modus | exakt Original: Zahlenliste `infrared` [1,6] treibt den **ULTRAVIOLET-Pin** (Java-Zeile 72); die UV-Liste [1,2,3,5,8] ist im Original tote Daten und wird als solche dokumentiert |
| Ausgabe | Event `emitter.sequence` über den WebSocket-Fachkanal (komplette Choreografie je Broadcast-Start); Webapp kann als LED-Visualisierung animieren |
| Hardware | `isHardwareActivatable: false` — physische Aktivierung ausschließlich später via `aurelia-emitterd` (Lease → Arming → ACK, Hard Rule 11) |
| Analyse-Rhythmus | CONTROL-Pin-Toggle des Originals (je Anreicherungsschritt, 30 ms) ist in `numberOfTrials` sichtbar (= Toggle-Anzahl) |

## Java-Orakelparität (evidenzgebundene Grenze)

- Belegt sind ausschließlich drei versionierte seeded `POST /analysis`-Fixtures
  mit 300 synthetischen Raten: Seed 42 bei `max_hits=100`, Seed 20260829 bei
  `max_hits=100` und Seed 42 bei `max_hits=1000` (JDK 24.0.1).
- Verglichen werden `generalVitality`, `numberOfTrials` und `rateObjects`.
  Andere Kataloge, Treeify-/Kollisionsfälle, Hilfsalgorithmen, Persistenz und
  stochastic sind nicht Teil dieser Aussage.
- Details, Fixtures und offene Gates stehen in
  `Radiworks/radiworks_port/engine/PARITY_MATRIX.md`.

## Status der Umsetzung

- [x] Festlegung 1 implementiert (`entropy.defaultMode`, Tests `test_festlegungen.py`)
- [x] Festlegung 2 implementiert (`broadcast.legacyMixMode`, `/broadcast/mix`)
- [x] Festlegung 3 implementiert (`core/emitter.py`, Event `emitter.sequence`)
- [x] Lokaler Engine-Testnachweis; keine feste historische Testzahl und kein S4-Nachweis.

## Ergänzung 2026-09-05 — Entropie-Parität, Egress und Passport-Semantik

> Betreiber- und Egress-Freigabe dokumentiert; als Muster für weitere Module
> nur nach jeweiliger Quellen-, Datenschutz- und Betriebsfreigabe übernehmen.

| Aspekt | Festlegung |
|---|---|
| Java-Parität | Produktive deterministische Entropie verwendet Java-Master-PRNG, `JavaRandom(raw_seed)` und Java-HashMap-Reihenfolge. Änderungen bestehender seeded Ergebnisse sind intentional. |
| Stochastic-Reihenfolge | Webcam-/Hotbits-FIFO → random.org → OS-CSPRNG. Jede Quelle liefert ausschließlich Roh-Seeds; die zweite PRNG-Stufe bleibt Java-kompatibel. |
| Egress | random.org ist nur im expliziten Modus `stochastic` zulässig; Seeded darf niemals Netzverkehr auslösen. Der Transport ist zeitbegrenzt, validiert Antworten und fällt bei Ausfall auf OS-CSPRNG zurück. |
| Settings | `entropy.defaultMode` ist ausschließlich `seeded` oder `stochastic`; ungültige Werte sind ein kontrollierter 422-Fehler, kein stiller Fallback. |
| Passport | Neue Passports speichern effektiven Seed, `replayable` und `seed_scheme=effective-v2`; stochastic ist nicht replaybar (`seed: null`). Fehlende neue Felder kennzeichnen historische, nicht rückwirkend umgedeutete Derived-Seed-Passports. |
| CopyGuard | Derselbe Digest der final sichtbaren Raten bindet Passport und Draft. |

## Ergänzung 2026-09-05 — S3 Session-, GV- und Entropiejournal-Integrität

| Aspekt | Festlegung |
|---|---|
| Sessionen | Jede Analyse appendet eine stabile `sessionId`; historische Sessionen werden nicht überschrieben. Numerische Navigation bleibt während der Lazy-Migration lesbar. |
| GV | Jeder Zug/Reset wird als Ereignis mit materialisiertem Ergebnis gesichert. An der Runden-Grenze wird die vorherige Session erhalten und ein Child mit `parentSessionId` angelegt. |
| Drafts | Nur `draft` und `client_review` dürfen die Session-Projektion aktualisieren. Terminale Drafts bleiben unverändert; ein Child-Session-Fork erhält einen neuen unreviewten Nachfolge-Draft. |
| Stochastic Recovery | Roh-Seeds bleiben ausschließlich in einem verschlüsselten privaten Runtime-Journal. Nach Neustart ist die gesicherte Historie wiederherstellbar; die erste neue Ziehung beginnt einen explizit markierten neuen Quellabschnitt. |
| Schlüssel und Retention | `RADIOWORKS_JOURNAL_KEY` ist ein Deployment-Secret außerhalb von Repo, Runtime-Daten, Fallartefakten und Logs. Journale bleiben bis zur expliziten Falllöschung erhalten. |
| Legacy | Keine Bulk-Migration und keine Mutation beim Lesen. Additive Felder entstehen nur bei der ersten legitimen Änderung der betroffenen Session. |

## Ergänzung 2026-09-05 — Rate-Katalog ist vom Runtime-Home getrennt

| Aspekt | Festlegung |
|---|---|
| Katalogpfad | `RADIOWORKS_DATA_DIR` benennt den expliziten read-only Rate-Katalog. Ohne Variable gilt `${RADIOWORKS_HOME}/data` aus Kompatibilitätsgründen. |
| Datenminimierung | Cases, Drafts, Konfiguration und Entropiejournale bleiben im separaten schreibbaren `RADIOWORKS_HOME`; der Rate-Katalog wird weder kopiert noch als impliziter Projektpfad übernommen. |
| Betrieb | Ein Katalogwechsel wird erst beim kontrollierten Prozessstart indiziert. Vor einer Analyse ist `GET /databases` der nichtmutierende Readiness-Nachweis. |

## Ergänzung 2026-09-05 — GV-Rundenende wie Original

| Aspekt | Festlegung |
|---|---|
| Einzeltrigger | Der reguläre GV-Trigger zieht Fall-GV, danach genau einen Rate-GV je Trigger; die Originalseite umfasst 21 Indizes (`0–20`), kein implizites Batch. |
| Rundenende | Der Boundary-Trigger säubert/forked nur die Child-Session und persistiert `round-boundary`; er verbraucht keine Entropie und zieht keinen neuen Fall-GV. Erst der nächste Trigger zieht den Child-Fall-GV. |

## Nachweisstand und Integrationsgrenze — 2026-09-30

Der getrennte RadiWorks-Kandidat `a242d24758d53e86ab290454ae4772f0827acc06` enthält den aktuellen lokalen Engine-/Webapp-Stand. Der isolierte synthetische Browser-Smoke bestand 19/19; der Betreiber bestätigte bei zwei geschützten künstlichen Fällen sichtbare Aktionsmeldungen, hörbar unterschiedliche Fallnummern, sichtbaren Tastaturfokus und keine vorgelesenen Rohbezeichnungen. Die vollständige Engine-Suite wurde auf dem Python-produktgleichen Vorgänger lokal unter Windows sowie Ubuntu WSL2 26.04 geprüft; das vorgesehene Ubuntu Server 24.04.4 bleibt ungeprüft. Quellen und Grenzen: Brainpower `docs/verification/RADIWORKS_RELEASE_BOUNDARY_2026-09-29.md`.

Diese Festlegungen bewahren lokale Original-/Prototypwege; daraus folgt keine Exposition der Direkt-Broadcast-, Bild-, Auto- oder Legacy-Wege im späteren Aurelia-Host. Das [RadiWorks-Profil v1.1 als Entwurf](../../standards/RADIOWORKS_LOCAL_PROFILE_V1_1_DRAFT.md) hält Analyse-Body, Scope- und Hostabweichungen zum gemeinsamen API-v1-Soll fest. S4 ist nicht zertifiziert, S5 und physische Aktivierung sind nicht begonnen.


## Betriebs- und Nachweisnachtrag 03.10.2026

Sieben getrennte lokale Runtime-/Fall-Scopes auf 8103–8109 sind über Windows-Aufgaben eingerichtet; Entwicklung ab 8110. Der Wiederanlauf nach Anmeldung ist konfiguriert, die Windows-Warmstartprobe noch offen. Mehrere Aufträge pro Fall innerhalb derselben Engine sind dadurch nicht freigegeben. Peggotty-Duplikatlabels werden live mit HTTP 422 abgewiesen; fünf gezielte Regressionstests bestanden. GV-RE zählt identische nicht-null Raten-GV im vollständigen Ergebnis und ist kein zeitlicher Trend. Periodische GV-Verläufe benötigen vor Aktivierung eine geprüfte Fall-/Sitzungs-/Broadcast-Zuordnung und getrennte Entropie. Kamera/Stochastic-Langlauf und S4.8 bleiben offen. Maßgeblicher Bericht: `C:\Users\Hubert111\Documents\Brainpower\docs\verification\RADIWORKS_SIEBEN_INSTANZEN_CHAT_NETZWERK_2026-10-03.md`. Gemeinsame ABI, Host-/Mandantenautorität und Reifegradregeln werden durch diesen Nachtrag nicht geändert.

# API_CONTRACT — standardisierter Modul-Contract (v1)

> Soll für RadiX-Module: Dieser Contract wird 1:1 implementiert oder eine
> quellengebundene, versionierte Abweichung bleibt bis zur Abstimmung offen. Er vereint:
> (a) Aurelia Kernel-ABI v1 (`docs/06-kernel-abi.md`), (b) den bewährten AetherOnePi-Endpunktstil
> (`Radiworks/docs/FUNKTIONSANALYSE.md §8`), (c) Aurelias Live-Regel (WebSocket).

**RadiWorks-Abgleich, 30.09.2026:** Die nachfolgenden v1-Zeilen sind ein gemeinsamer Sollvertrag und beschreiben nicht durchgehend die aktuelle lokale RadiWorks-API. Das [versionierte lokale Profil](RADIOWORKS_LOCAL_PROFILE_V1_1_DRAFT.md) bindet den Kandidaten `a242d247` und kennzeichnet die noch offene Hostabstimmung: Insbesondere akzeptiert `POST /analysis` lokal **keine** `tenant_id`-/`client_id`-Body-Felder, und `/cases/current` plus `/analysis/current` decken nicht jeden Zustand ab. Dieser Entwurf ändert den gemeinsamen v1-Vertrag nicht, erteilt keine Hostfreigabe und macht RadiWorks nicht automatisch S4-reif.

Alle Engines serveen: `{apiBase}/…` — apiBase ist konfigurierbar, nie hardcodet.

## 0. Infrastruktur-Endpunkte

| Methode | Route | Antwort |
|---|---|---|
| GET | `/ping` | `{"result":"pong", "module":"<id>", "version":"<semver>"}` |
| GET | `/manifest` | Kernel-ABI-v1-Objekt (siehe §5) |

## 1. Entropie

| Methode | Route | Beschreibung |
|---|---|---|
| GET | `/entropy/status` | `defaultMode`, `factoryDefault`, `modes`, `activeSource`, `chain`, `note`; Feed-Größe separat unter `/entropy/feed` |
| POST | `/entropy/acquire` | manuelles Nachfüllen (bei RadiWorks: Webcam-/QRNG-Pakete) |

## 2. Analyse (Fachkern)

| Methode | Route | Request | Antwort |
|---|---|---|---|
| GET | `/databases` | – | verfügbare Raten-Datenbanken (bei RadiWorks: `rates`-Endpunktäquivalent) |
| POST | `/analysis` | `{"database": str, "seed": int?, "mode": "seeded"\|"stochastic"?, "max_hits": 100\|1000?, "tenant_id": str?, "client_id": str?}` | `{passport, result, draft}` — Passport- und Draft-Pflicht |
| GET | `/analysis/current` | – | letztes Ergebnis (AetherOnePi: `analysis`) |
| POST | `/gv` | `{"seed": int?, "mode"?: …}` | `{"gv": int, "source": "derived"}` General Vitality |
| POST | `/search-anomaly` | `{"width": int, "height": int}` | GV-Matrix |

**Reproduzierbarkeit (Aurelia Hard Rule 7, Festlegung RadiWorks 2026-08-29):**
Factory-Default ist `seeded`; der Arbeitsmodus wird über Settings
`entropy.defaultMode` (`seeded` | `stochastic`) gesteuert, ein `mode` im
Request überschreibt fallweise. `stochastic` ist die Original-Entropie-Kette
(Hotbits). Jede Antwort trägt einen Computation Passport (`run_id`,
`kernel_hash`, `input_hash`, `seed`, `dauer_ms`, Quellenangaben je Zahl,
`entropy_mode`).

## 2b. AnalysisDraft / Zwischenablage (D18-Pflicht)

| Methode | Route | Beschreibung |
|---|---|---|
| GET | `/drafts` | Draft-Liste (optional `?status=`) |
| GET | `/drafts/{id}` | Draft-Metadaten ohne `payload` |
| POST | `/drafts/{id}/transition` | `{"status": "client_review"\|"ready"\|"discarded"}` — Statusmaschine `draft → client_review → ready → promoted\|discarded` |
| POST | `/drafts/{id}/promote` | **Einziger Weg** von der Analyse zu Broadcast/Harmonisierung; CopyGuard fail-closed vor Promote (409 bei Block) |
| POST | `/drafts/{id}/discard` | Verwerfen |

Draftfelder lt. Aurelia `docs/18-clipboard.md`: `id, tenant_id, client_id,
practitioner_id, source_kernel, source_run_id, payload, copyguard_digest,
client_editable_fields, status, Zeitstempel`.

## 2c. GV-Runde (Aether_4-Äquivalent: „GV (runs = n)")

| Methode | Route | Beschreibung |
|---|---|---|
| POST | `/analysis/gv-round` | `{"seed"?, "mode"?}` — ein GV-Zug: 1. Zug = Fall-GV, weitere = nächste Rate (inkl. GV-RE-Berechnung); nach 21 Zügen neue Runde |
| POST | `/analysis/gv-round/reset` | Runde zurücksetzen (alle Raten-GVs auf 0) |
| GET | `/analysis/gv-round` | Zustand (`generalVitality`, `counter`, `totalRuns`) |

## 2d. Essenzielle Fragen (GV-Orakel)

| Methode | Route | Beschreibung |
|---|---|---|
| POST | `/essential-questions` | `{"seed"?, "mode"?}` → `{"report": str}` — deutsche, CopyGuard-geprüfte Formulierung; Logik identisch zum Original (Schwellen GV > 500, Zeitprognose aus 7 Optionen) |

## 2e. Stick-Pad (Aether_6-Äquivalent)

| Methode | Route | Beschreibung |
|---|---|---|
| POST | `/stickpad/position` | `{"x": int, "y": int}` — Position sammeln |
| POST | `/stickpad/analyze` | `{"database": str}` → AnalysisResult; Positionszuordnung ist deterministisch, keine allgemeine Java-Paritätsbehauptung |
| POST | `/stickpad/gv` | Stick-Pad-GV mit Positionsverbrauch im Bonusfall |
| DELETE | `/stickpad` | Positionen verwerfen |

## 2f. Settings (Aether_3-Äquivalent)

| Methode | Route | Beschreibung |
|---|---|---|
| GET | `/settings` | Settings-Store (kanonische Original-Schalter werden beim ersten Abruf mit Defaults belegt — Selbst-Default wie im Original) |
| PUT | `/settings` | Teil-Update `{booleans?, integers?, strings?}` mit Typ-Prüfung (422 bei Verstoß) |

## 2g. Bild, Statistik, Skript (Stufe-3-Erweiterungen, Aether_5/9)

| Methode | Route | Beschreibung |
|---|---|---|
| POST | `/images/analyze` | `{"count": n, "seed"?, "mode"?}` → GV je Schicht (256 Züge, Runden bis max ≥ 162 wie im Original); Bilder bleiben im Client |
| POST | `/images/broadcast` | `{"md5": str, "seconds"?: int, "multiplier"?: int}` → Broadcast `IMAGE:<md5>` |
| GET | `/cases/{name}/statistics` | StatisticsGenerator-Port (occurrence/GV-Summe/EV-Summe, Top 10); schreibt `topTenList` in den Fall |
| POST | `/script/execute` | RadionicScript/PEGGOTTY: `{"script": text}` oder `{"name": str}` (`var = ANALYZE db.txt`, PRINT, GOTO, `label:`, `##`) |
| GET | `/scripts`, `/scripts/{name}` | Skriptliste/-inhalt (`data/*.rscript`) |

## 3. Session / Case

| Methode | Route | Beschreibung |
|---|---|---|
| GET | `/cases` | Namensliste |
| POST | `/cases` | Case anlegen/speichern (JSON-Contract) |
| GET | `/cases/{name}` | Case laden |
| GET | `/cases/current` | aktuell geladener Case (RAM) |

## 4. Broadcast / Live

| Methode | Route | Beschreibung |
|---|---|---|
| POST | `/broadcast` | `{"signature": str, "seconds": int, "multiplier"?: int, "clear"?: bool, "delay_ms"?: int, "repeat"?: int}` — bewusster Operator-Befehl (kein stiller Copy); Sammel-Broadcasts laufen NUR über Draft-Promote (§2b) oder `/broadcast/mix` im Legacy-Modus |
| POST | `/broadcast/mix` | `{"draft_id": str, "max_rates"?: int, "seconds_per_rate"?: int, "multiplier"?: int}` — Original „BROADCAST MIX"-Einklick; nur aktiv wenn Settings `broadcast.legacyMixMode=true`, sonst 409 (Zweiklick-Pflicht nach D18). CopyGuard fail-closed in beiden Wegen |
| GET | `/broadcast/queue` | Queue-Zustand (queued/active/Resonanz-Zähler) |
| DELETE | `/broadcast/current` | laufenden Broadcast stoppen |
| DELETE | `/broadcast/all` | alle stoppen |
| WS | `/ws` | Fachkanal, Server ist die Uhr; Umschlag `{"v": 1, "id": int, "boot": str, "type": str, "payload": obj, "ts": ms}`. Kontrollereignisse haben `id: 0`, Fachereignisse positive IDs. Die Verbindung beginnt mit `server.hello`; Reconnect verwendet `last_event_id` und `last_boot`, bei Lücken folgt `server.replay_gap`. Ereignisse umfassen u. a. `analysis.update`, `broadcast.progress`, `broadcast.resonance` und `emitter.sequence`; keine feste Fortschrittsfrequenz wird zugesichert. |

**VirtualEmitter (Festlegung RadiWorks 2026-08-29):** die Hardware-Choreografie
des Originalmoduls (Signatur → Ziffern → LED-Gruppen → Blink-Rhythmus) wird
1:1 als Event-Datenstrom portiert statt entfernt; physische Aktivierung bleibt
ausschließlich dem späteren `aurelia-emitterd`-Connector vorbehalten
(`isHardwareActivatable: false`).

## 5. `/manifest` — Kernel-ABI v1 (RadiWorks-Implementierungsprofil)

Autoritative Quelle ist
`Radiworks/radiworks_port/engine/src/radiworks/manifest.py`; der Hash wird zur
Laufzeit aus den Python-Quellen berechnet und darf nicht als fester Dokumentwert
kopiert werden.

```json
{
  "id": "radiworks.engine",
  "version": "0.2.0",
  "hash": "sha256:<dynamisch aus /manifest>",
  "class": "cpu",
  "repro": "seeded",
  "budget": { "vram_mb": 0, "cpu_ms_est": 5000, "max_batch": 1 },
  "abi_surface": "rest",
  "abi_version": "v1",
  "operations": [{ "id": "analysis", "method": "POST", "path": "/analysis", "version": "v1" }],
  "entry": "radiworks.core.analysis:analyse_rate_list",
  "entry_status": "deprecated-compatibility",
  "isHardwareActivatable": false
}
```

Die Ein-/Ausgabe-Schemas und die `copy`-Stringliste stammen vollständig aus dem
live abgerufenen Manifest. Neue Integrationen verwenden ausschließlich die
versionierte REST-Operation `POST /analysis`; `entry` bleibt Übergangsmetadatum.

## 6. Konventionen

1. **Kein Hidden State:** jede zustandsändernde Operation ist über `/cases/current` + `/analysis/current` introspektierbar.
2. **Seed-Transparenz:** jede Zufallsoperation akzeptiert optional `seed`; ohne Seed nutzt der EntropyProvider die echte Quelle.
3. **Fehler:** `{"error": {"code": str, "message": str}}` + korrekter HTTP-Status.
4. **Mandant:** Phase 1 ohne Auth (lokaler Prototyp); `tenant_id`/`client_id`
   sind im Analysis-Request sowie in Passport und Draft nullable geführt. Dies
   ist kein Nachweis von Authentifizierung oder tenant-scoped Queries.
5. **CORS:** Prototyp erlaubt `localhost:*`; bei Aurelia-Integration gilt deren Same-Site-Abschottung (`isolation.server.ts`) — die webapp wird dann same-origin/iframe eingebettet, nicht cross-origin gerufen.

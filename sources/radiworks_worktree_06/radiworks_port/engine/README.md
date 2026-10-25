# RadiWorks Engine (Prototyp, Stufe 2)

Python-Port der AetherOnePi-Kernlogik als Kernel-ABI-v1-konformer FastAPI-Dienst.
**Wellbeing-Dokumentationssoftware — kein Medizinprodukt, keine Diagnose, keine Therapie.**

## Installieren & Starten

```bash
cd engine
py -3 -m venv .venv
.venv/Scripts/pip install -e ".[dev]"      # Windows/Git-Bash
.venv/Scripts/pytest                        # Testlauf

.venv/Scripts/python.exe run.py             # Server auf 127.0.0.1:8090
# alternativ (ohne Heimat-Pfadlogik):
.venv/Scripts/uvicorn "radiworks.main:create_app" --factory --port 8090
```

- REST-Basis: `http://127.0.0.1:8090/` (Endpunkte: `docs/../../Modul_Templates/standards/API_CONTRACT.md`)
- WebSocket-Fachkanal: `ws://127.0.0.1:8090/ws` (Umschlag `{v:1, id, type, payload, ts}`)
- Selbstbeschreibung: `GET /manifest` (Kernel-ABI v1, Aurelia docs/06-kernel-abi.md)
- Heimatverzeichnis (Daten/Cases/Drafts): `./radiworks_home` bzw. `create_app(base_dir=...)`

## Architektur-Entscheidungen (abweichend vom Java-Original, aurelia-begründet)

| Entscheidung | Grund |
|---|---|
| Entropie **seeded** als Default; `stochastic` explizit per Request | Aurelia Hard Rule 7: strikte Reproduzierbarkeit ist Default |
| Analyse erzeugt **AnalysisDraft** (Status `draft → client_review → ready → promoted`) | D18: Harmonisierung startet nur nach Promote aus der Zwischenablage |
| **Computation Passport** je Lauf (`run_id`, `kernel_hash`, `input_hash`, `seed`, `dauer_ms`, Quellen) | docs/04-compute.md — Verträge leben länger als Libraries |
| WebSocket-Umschlag `v:1` mit monotoner Event-ID + Reconnect an letzter ID | docs/15-live.md |
| Broadcast rein ereignisbasiert (`isHardwareActivatable: false`) | Hard Rule 4/10: Server ist die Uhr, keine USB-/GPIO-Aktivierung |
| LED-Gruppen des Pi nur als Datenstruktur (`BROADCAST_LED_GROUPS`) | späterer `aurelia-emitterd`-Anschluss (Lease → Arming → ACK) |
| CopyGuard-Lexikon fail-closed im Kernel (LLM-Stufe bleibt Plattform) | docs/16-wellbeing.md — Klartext nie in fremde Systeme |
| Draft/Case-Schemas mit `tenant_id`/`client_id` (nullable) | Hard Rule 8: Scoping-Pflicht vorbereitet |

## Verhältnis zum Java-Original

Alle Algorithmen sind 1:1-portiert und in `tests/` gegen die in
`Radiworks/docs/FUNKTIONSANALYSE.md` dokumentierte Bytecode-Logik getestet
(Seed-Determinismus ersetzt die Hotbit-Abhängigkeit in Tests). Bewusste,
dokumentierte Bereinigungen: Regex-Injection im Such-Highlighting, tote
Nitrite-Datenbankpfad, Doppelimplementierung HotbitsClient/HotbitsHandler.

## Grenzen des Prototyps

- Materia-Medica-Suche: gewichtete Token-Suche (Lucene-Ersatz minimal); FTS-Upgrade offen.
- Broadcast-Visualisierung (Fibonacci-Ästhetik) liegt in der Webapp (P3), nicht hier.
- Kopie der Rate-Datenbanken und Clarke-Korpora: beim Start in `radiworks_home/` einzuspielen
  (Quellordner: `Radiworks/materiaMedica/Clarke`, `data/` aus radionics-rates).

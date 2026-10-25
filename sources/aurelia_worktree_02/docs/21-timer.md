# Virtuelle Timer und Persistenz (D20)

## Anforderung (Operator, 2026-08-23)

- „20 Klienten“ ist ein **Beispiel** gleichzeitiger Plattformnutzung.
- Klienten haben unterschiedliche Analyse- und Harmonisationsjobs, auch parallel.
- Keine Interferenzen zwischen Klienten **und** zwischen den Jobs desselben Klienten.
- Viele virtuelle Timer pro Klient sind gewollt.
- Zustand muss **nach Server-Reset akkurat** weiterlaufen.
- GPU wäre „schöner“, RAM ist Alternative — Entscheidung nach Analyse.

## Analyse GPU vs RAM vs Disk

| Ort | Echtzeit-DSP | Überlebt Reset | Isolation | Kapazität Timer-Zustand | Rolle |
|---|---|---|---|---|---|
| VRAM (Ada 16 GB Pool) | ja | **nein** (Reboot, Driver-Reset, Prozessende) | Streams, aber flüchtig | verschwendet Job-Speicher | nur DSP-Slice eines Ticks |
| RAM (timerd) | Kontrolle ja | nein ohne Spiegel | gut, billig | Hunderte bis Tausende Kanäle à wenige KB | Hot path, 50 ms UI-Ticks |
| Postgres WAL | nein (ms) | **ja** | RLS + SKIP LOCKED | Millionen Zeilen | **Source of Truth** |

VRAM als Ledger erfüllt die selbst gestellte Reset-Pflicht nicht. Deshalb:

```
Postgres WAL  = dauerhafte Uhr und Kanalzustand
timerd RAM    = 50 ms Ticks, Zustandsmaschine
Ada gpud      = optionaler DSP/Waveform-Job je Kanal, Arena (tenant, client, job/channel)
```

## Checkpoint, nicht jeder UI-Tick

- Zustandswechsel (start/pause/stop/arm): sofort fsync.
- Laufende Kanäle: `last_tick` alle **500–1000 ms**.
- UI darf 50 ms aus RAM sehen (U08).
- 320 Kanäle × 20 fsync/s wäre Schreibamplifikation ohne Genauigkeitsgewinn nach dem Crash.

Nach Reset: `running|paused|armed` laden, Lücke `now − last_checkpoint` in den Passport, **nicht** heimlich aufholen (D06, X20).

## Isolation

Schlüssel: `(tenant_id, client_id, channel_id)` bzw. `job_id`.
Kein gemeinsamer Default-Stream, kein gemeinsames RNG, kein gemeinsamer Buffer
zwischen zwei Analysen, zwischen Analyse und Harmonisierung, zwischen zwei
Kanälen desselben Klienten.

## Quota

Default 16 Kanäle/Klient, hebbar (D09). Emitter bleibt 1 (D14).
GPU-DSP 1–4 Occupancies. Idle-Timer kosten **kein** VRAM.

## Redis

AOF als Cache vor Postgres zulässig, nicht statt WAL.

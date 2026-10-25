# Echtzeit-Compute

Hardware: [14-hardware.md](14-hardware.md). Scheduler: [17-cuda.md](17-cuda.md).
Live: [15-live.md](15-live.md). Kozyrev: [19-kozyrev.md](19-kozyrev.md).

## Rollen (gesetzt C01–C03, D20)

| Ressource | Aufgabe |
|---|---|
| NVIDIA RTX 4000 SFF Ada, 20 GB | Job-Pool: Analyse, Harmonisierung, optionales Quantum. **Kein** LLM. **Kein** MIG |
| VRAM-Vorschlag | 2 GB Runtime · 16 GB Jobs · 2 GB Kopf — kein Overcommit |
| AMD Ryzen 5 9600X | API, Postgres, Redis, timerd, emitterd, gpud-Orchestrierung, CopyGuard-Runtime, AVX-512 |
| RAM | **128 GB DDR5** — CopyGuard, Puffer |
| Netz | 2× 1 Gbit/s, Backbone-nah — RTT nutzen, Compute nicht verlagern |

## Pipeline

1. Ingest (Schema, Envelope)
2. Normierung (AVIF/Opus, Hash)
3. CPU-Orchestrierung (Fair-Queue, Budget)
4. CUDA tenant-isoliert (FFT, Haar/p-adisch, Harmonisierungspfad)
5. Optional Quantum (gleicher Pool, eigener Modus)
6. CopyGuard **im RAM** + Passport (`copyguard_digest`)
7. Optional Promote in Harmonisierungsspur ([18-clipboard.md](18-clipboard.md))

## aurelia-timerd

Zustandsmaschine der Spur:

`queued → armed → running ⇄ paused → stopped → archived | deleted`

Zeit: chrony/NTP + monotonic. Nach Reboot Fortsetzung am letzten Tick; Lücken
im Ausweis. `setInterval` im Browser ist keine Uhr.

## Passport

`run_id`, `tenant_id`, `modus`, `kernel`, `kernel_hash`, `input_hash`, `seed`,
`gpu_attest`, `vram_mb`, `copyguard_digest`, `dauer_ms`, `signatur`.
Quelle jeder Zahl: `simulated` / `measured` / `derived` / `manual` / `ai-generated`.
Build 0 bleibt `executable: false` / `isHardwareActivatable: false` bis Gate.

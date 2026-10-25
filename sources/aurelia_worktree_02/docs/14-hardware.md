# GPU Server M G1

Belegt durch Betreiber-Screenshot 2026-08-23.

| Ressource | Wert |
|---|---|
| CPU | AMD Ryzen 5 9600X, 6C/12T, 3900/5400 MHz, AVX-512 (Zen 5) |
| GPU | NVIDIA RTX 4000 SFF Ada, 20 GB, **kein MIG** |
| RAM | 128 GB DDR5 |
| Storage | 2× 1 TB NVMe |
| Netz | 2× 1 Gbit/s, Backbone-nah |
| Betrieb | IPMI, redundantes Netzteil, Debian Bookworm Root |

Anbieter-Scores (Llama 3.1 8B 507, Qwen2.5 14B 268) sind **kein** Betriebsmodus.

## VRAM-Budget — gesetzt (C03)

Ersetzt das frühere 3/3/12/2.

| Anteil | Zweck |
|---|---|
| 2 GB | Runtime, Treiber |
| 16 GB | Job-Pool (Analyse, Harmonisierung, Quantum) |
| 2 GB | Kopf, kein Overcommit |
| 0 GB | CopyGuard — sitzt in RAM/NVMe |

NVMe: Akten-Spiegel plus Modell-Replica.
20 parallele Occupancies: nein. Siehe [17-cuda.md](17-cuda.md).

# GPU Server M G1

Ursprünglich durch Betreiber-Screenshot 2026-08-23 belegt; CPU, GPU, RAM,
Mainboard und Laufwerksgrößen am 25. August 2026 zusätzlich read-only
inventarisiert.

| Ressource | Wert |
|---|---|
| CPU | AMD Ryzen 5 9600X, 6C/12T, 3900/5400 MHz, AVX-512 (Zen 5) |
| GPU | NVIDIA RTX 4000 SFF Ada, 20 GB, **kein MIG** |
| RAM | 128 GB DDR5; Board/CPU ECC-fähig, aktiver ECC-Betrieb noch nicht bewiesen |
| Storage | 2×2 TB WD_BLACK SN850X NVMe; RAID1/LUKS2/LVM geplant, noch nicht ausgeführt |
| Netz | 2× 1 Gbit/s, Backbone-nah |
| Mainboard | Supermicro H13SAE-MF, UEFI, TPM2, dediziertes IPMI/BMC |
| Betrieb Ziel | Ubuntu Server 24.04.4 LTS amd64 plus minimales GNOME |
| Resilienz | redundantes Netzteil, Anbieter-USV, separates Backupsystem, Anbieter-DDoS-Schutz |

Anbieter-Scores (Llama 3.1 8B 507, Qwen2.5 14B 268) sind **kein** Betriebsmodus.

## VRAM-Budget — gesetzt (C03)

Ersetzt das frühere 3/3/12/2.

| Anteil | Zweck |
|---|---|
| 2 GB | Runtime, Treiber |
| 16 GB | Job-Pool (Analyse, Harmonisierung, Quantum) |
| 2 GB | Kopf, kein Overcommit |
| 0 GB | CopyGuard — sitzt in RAM/NVMe |

Geplant ist RAID1/LUKS2/LVM für den Ausfall eines einzelnen Laufwerks und die
Verschlüsselungs-/Volume-Grenze. Dieser Plan ist noch nicht ausgeführt. RAID ist
kein Backup und ersetzt weder Offsite-Sicherung noch Restore-Test. Die SN850X wird
mangels dokumentierter Enterprise-Power-Loss-Protection nicht als PLP-SSD
klassifiziert; eine getestete USV ist Pflicht, Enterprise-NVMe mit PLP bleibt
vor Art.-9-Regelbetrieb empfohlen.
20 parallele Occupancies: nein. Siehe [17-cuda.md](17-cuda.md).

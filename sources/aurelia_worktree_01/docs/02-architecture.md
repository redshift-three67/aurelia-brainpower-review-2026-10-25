# Architektur

## Leitentscheidung

Souveräner Kern auf **GPU Server M G1** (Debian Bookworm).
Schlanke öffentliche Kante **aus demselben AURELIA-Baum** (Caddy auf M G1).
Lovable Cloud **nicht** in der Laufzeit (H1–H3, D24 gesetzt).

```
[Browser]
    │ TLS 1.3  ·  WebSocket-Fachkanal (Progress, Ticks, ACK)
[Öffentliche Schicht]  Website, Login-UI, PWA — TanStack Start
    │
[Control Plane · Debian EU]  Auth, Mandanten, RBAC, Abos, Audit-Index
    │ intern mTLS / NATS
[Data + Compute · GPU Server M G1]
    Postgres/Timescale/pgvector, MinIO, Redis,
    aurelia-gpud (16 GB Job-Pool, tenant-isoliert),
    aurelia-timerd, aurelia-emitterd,
    CopyGuard im RAM/NVMe
```

Neben Spur: Lovable-Projekt `ccecde78-…` an `radiquant-cloud-build` /
Branch `radiquant4`. Preview und Gestaltung. Kein Disconnect, kein Publish.

## Vertrauensgrenzen

- Öffentliches HTTPS endet am Reverse Proxy auf Debian (Caddy/Nginx).
- Worker haben kein direktes Internet.
- Tenant-Keys im Keystore (LUKS/TPM, später HSM-fähig).
- Logs ohne Zeugenpayload und ohne Klarnamen (OpenTelemetry).
- Backups mandantenfähig, verschlüsselt, Restore getestet.
- Spooky2 / Generator X Pro nur über `aurelia-emitterd` (CP210x). Kein WebUSB.
- CUDA-Buffer tragen `tenant_id`. Kein MIG auf dieser Karte.

## Geplante Laufzeit (nicht Phase 0)

| Teil | Wahl | Grund |
|---|---|---|
| Frontend | React 19 + TanStack Start | Ist bereits die Codebasis |
| API | FastAPI | CUDA, PennyLane, cuQuantum sind Python-nativ |
| Jobs | Redis + ARQ oder NATS + aurelia-gpud | Parallele GPU-Jobs, Drain, Fair-Queue |
| Realtime | WebSocket-Fachkanal; kein WebRTC | Analyse + Harmonisierung, Server ist Uhr |
| CopyGuard | Phi-4-mini Q4 / Gemma 3 4B **im RAM** | Ada bleibt Job-Pool (C02) |

## Hardware

Siehe [14-hardware.md](14-hardware.md). VRAM-Vorschlag 2 / 16 / 2 GB (C03).

## Verträge, die länger leben als Libraries

Kernel-ABI, Computation Passport (inkl. `copyguard_digest`, `tenant_id`),
WebSocket-Schema `v:1`, Emitter-Lease, AnalysisDraft, HarmonizationLane.
CUDA- oder QPU-Backends tauschen hinter derselben ABI, Archive bleiben lesbar.

# AURELIA — Architektur- und Codebasis-Audit

Stand: 2026-08-25  
Gegenstand: Codebestand, Bibliotheken, Laufzeitverträge und Systemarchitektur  

---

## 1. Status Quo der Codebasis

### 1.1 Aktuelle Komponenten im Workspace
Die aktuelle Codebasis (`redshift-three67/aurelia`) ist primär eine interaktive **Konzept-, Verfassungs- und Vorbereitungs-Webanwendung** auf Basis von:
- **Framework:** React 19.2 + TanStack Start (Nitro 3 Engine, Vite 8)
- **Routing:** `@tanstack/react-router` (File-based routing in `src/routes/`)
- **Datenbank-Layer:** Hybrid-Treiber (`src/lib/db.ts`): PGLite (WASM Postgres im Browser/Node-Memory) für Preview/Lokalbetrieb vs. Neon/pg für Remote Postgres.
- **Authentifizierung:** Better-Auth 1.6 mit Grok Auth Broker Integration und lokaler Email/Passwort-Option (`migrations/0001_auth.sql`, `migrations/0002_tenants.sql`).
- **UI & Tokens:** Tailwind CSS v4, Radix UI Primitives, Fraunces Display Font, Source Sans 3 Body Font, Farbpalette: Pergament (`#F3EFE6`), Tinte (`#1C241E`), Sage (`#2C4A3E`).

### 1.2 Bewertung des Bestands

```text
[Bereits exzellent vorhanden]
├── Präzise Formulierung aller Leitentscheidungen (D01–D24) in TypeScript-Typen
├── Vollständige interaktive UI für alle Aspekte der Systemverfassung (/freigabe, /entscheidungen, /kozyrev, /architektur, /daten, /compute, /sicherheit, etc.)
├── Datenbank-Migrationspipeline (_migrations Tabelle, deterministischer Ablauf)
├── Tenant- und Membership-Datenstrukturen (Phase 1 Gehäuse)
└── Verfassungstests und Invarianten-Checker

[Noch nicht vorhanden / Zukünftige Schichten]
├── aurelia-gpud (CUDA C++/Python-Daemon mit Job-Queue und Scheduler)
├── aurelia-timerd (High-Resolution Timer-Service mit 50ms UI Ticks und 500-1000ms Postgres-WAL Checkpoints)
├── aurelia-emitterd (Serieller CP210x Hardware-Dienst für Spooky2 mit Lease-Protokoll)
├── CopyGuard-Engine (RAM-basiertes Fail-Closed Regex-Lexikon + lokales GGUF-LLM wie Phi-4-mini/Gemma 3)
├── Kernel-ABI v1 Ausführungs-Engine (Radi144, RadiWorks, RadiMorphic, etc.)
├── DSGVO Art. 9 RLS-Sicherheitslayer mit Envelope-Encryption
└── WebSocket-Fachkanal (v:1 Protokoll)
```

---

## 2. Detaillierte Architektur-Analyse

### 2.1 Zielarchitektur auf dem GPU Server M G1
Die geplante Zielarchitektur trennt das Gesamtsystem in klare Sicherheits- und Privilegien-Zonen:

```text
                              ┌────────────────────────┐
                              │     Browser / PWA      │
                              └───────────┬────────────┘
                                          │ TLS 1.3 / WebSocket (WSS)
                                          ▼
                              ┌────────────────────────┐
                              │     Caddy Proxy        │ (Debian Bookworm)
                              │ TLS, Rate-Limit, Sec-H │
                              └───────────┬────────────┘
                                          │ Unix Domain Socket / Localhost
                     ┌────────────────────┴────────────────────┐
                     │                                         │
                     ▼                                         ▼
      ┌──────────────────────────────┐          ┌──────────────────────────────┐
      │  TanStack Web-App / Control  │          │    FastAPI / NATS RPC API    │
      │  (Node 22 / SSR / Auth/RBAC) │          │  (Orchestrierung & Dispatch) │
      └──────────────┬───────────────┘          └──────────────┬───────────────┘
                     │                                         │
       ┌─────────────┴─────────────┐                           │
       ▼                           ▼                           │
┌──────────────┐            ┌──────────────┐                   │
│  PostgreSQL  │            │    Redis     │                   │
│ (Timescale + │            │ (State Cache │                   │
│   pgvector)  │            │  + Pub/Sub)  │                   │
└──────▲───────┘            └──────▲───────┘                   │
       │                           │                           │
       └─────────────┬─────────────┘                           │
                     │                                         │
                     ├─────────────────────────────────────────┤
                     │                                         │
                     ▼                                         ▼
      ┌──────────────────────────────┐          ┌──────────────────────────────┐
      │       aurelia-timerd         │          │        CopyGuard (RAM)       │
      │  (C++/Rust/Go - Monotonic)   │          │  (Phi-4-mini / Gemma Q4)     │
      │  50ms RAM / 1s WAL Checkp.   │          │  AVX-512 CPU-only, 0 GB VRAM │
      └──────────────────────────────┘          └──────────────────────────────┘
                     │
                     ├─────────────────────────────────────────┐
                     ▼                                         ▼
      ┌──────────────────────────────┐          ┌──────────────────────────────┐
      │        aurelia-gpud          │          │       aurelia-emitterd       │
      │   (CUDA C++ / PyTorch C++)   │          │  (CP210x Serial Driver)      │
      │   16 GB Pool, Stream-Isolat. │          │  Hardware Lease, Exclusive   │
      │   Key: (tenant,client,job)   │          │  Fail-closed, No WebUSB      │
      └──────────────┬───────────────┘          └──────────────┬───────────────┘
                     ▼                                         ▼
      ┌──────────────────────────────┐          ┌──────────────────────────────┐
      │    NVIDIA RTX 4000 Ada       │          │   Spooky2 / Generator X Pro  │
      │       (20 GB VRAM)           │          │   (USB /dev/ttyUSB*)         │
      └──────────────────────────────┘          └──────────────────────────────┘
```

### 2.2 Analyse der Kernverträge

#### 1. VRAM-Budget & Scheduler (C03, D17)
- **Zuweisung:** 2 GB Runtime/Treiber, 16 GB Job-Pool, 2 GB Sicherheitsabstand.
- **Befund:** Exzellent durchdacht. Da die Ada 20GB kein MIG (Multi-Instance GPU) unterstützt, ist ein Software-Scheduler mit CUDA-Streams unumgänglich.
- **Sicherheitsisolation:** Jeder Job erhält einen dedizierten CUDA-Stream und isolierte Speicher-Arenen, adressiert über `(tenant_id, client_id, job_id)`. Kein Puffer-Sharing!

#### 2. Der "Timerd"-Zustandsautomat & Persistenz (D20, 21-timer.md)
- **Problemstellung:** Timer-Zustände dürfen nach einem Crash/Reboot nicht verloren gehen. VRAM ist flüchtig, dauernde fsyncs bei 50ms Ticks würden jedoch die NVMe zerstören (Schreibamplifikation).
- **Lösungsarchitektur:** 
  - Hot Path: 50 ms Ticks im Arbeitsspeicher (RAM).
  - Persistenz: Checkpointing in PostgreSQL WAL alle 500–1000 ms.
  - Reset-Verhalten: Nach Neustart wird ab dem letzten Checkpoint fortgesetzt; die Zeitlücke (`now - last_checkpoint`) wird transparent im Passport protokolliert, anstatt Zeit heimlich "nachzuholen".
- **Befund:** Industriestandard für fehlertolerante Prozesssteuerung.

#### 3. CopyGuard (C02, D13, 16-wellbeing.md)
- **Zwei Stufen:**
  1. *Stufe 1:* Deterministisches Regex-Lexikon (Fail-Closed für verbotene Heil-/Diagnose-Begriffe).
  2. *Stufe 2:* Lokales GGUF-Modell (z.B. Phi-4-mini oder Gemma 3 4B) rein über CPU (AMD Ryzen 5 9600X mit AVX-512) im 128 GB DDR5 RAM.
- **Befund:** Die Entscheidung, kein LLM im VRAM zu halten, rettet die 16 GB für radionische DSP-Kerne und schützt sensible Klientendaten vor externen Cloud-LLM-Leaks.

#### 4. Kernel-ABI v1 (06-kernel-abi.md)
- **Vertrag:** Stabile SemVer-Versionierung, SHA-256 Hash des Binär-Artefakts, JSON-Schema für In/Out, `repro`-Level (`strict` / `seeded` / `stochastic`), VRAM/CPU-Budget.
- **Befund:** Ermöglicht die saubere Kapselung historischer Prototypen (RadiMorphic etc.) und neuer Kozyrev-Module, ohne Altlasten in den Core-Code zu schleppen.

---

## 3. Bewertung des Tech-Stacks

| Technologie | Eignung | Stärken | Herausforderungen / Risiken |
|---|---|---|---|
| **Debian 12 Bookworm** | **Hervorragend (10/10)** | Felsenfeste Stabilität, LTS, perfekte NVIDIA-Treiber & Container-Unterstützung | Konfiguration von Root/LUKS/TPM muss akribisch automatisiert werden. |
| **AMD Ryzen 5 9600X (Zen 5)** | **Sehr gut (9/10)** | Hervorragende Single-Thread-Leistung, volles AVX-512 für schnelles CPU-LLM & FFT | 6 Kerne / 12 Threads erfordern striktes CPU-Core-Pinning für Daemons. |
| **RTX 4000 SFF Ada (20GB)** | **Sehr gut (9/10)** | Hohe Effizienz (70W), 20GB VRAM, ECC-Support, Tensor-Cores | Kein MIG; Software-Scheduling zwingend erforderlich. |
| **PostgreSQL 16 + Timescale** | **Hervorragend (10/10)** | Perfekt für transaktionale Mandantendaten + Zeitreihen-Ticks & pgvector | WAL-Archivierung und Offsite-Sync müssen gehärtet werden. |
| **TanStack Start / React 19** | **Gut (8/10)** | Modernstes Frontend, SSR, Typsicherheit end-to-end | Framework befindet sich in rascher Weiterentwicklung; Breaking Changes monitoren. |
| **FastAPI / Python (Compute)** | **Hervorragend (10/10)** | De-facto-Standard für CUDA, PyTorch, PennyLane, cuQuantum | Prozess-Isolation und IPC (ZeroMQ / Unix Sockets) sauber definieren. |
| **Caddy 2** | **Hervorragend (10/10)** | Automatisches TLS, einfacher Reverse-Proxy, sichere Defaults | Konfiguration von mTLS und WebSocket-Timeouts beachten. |

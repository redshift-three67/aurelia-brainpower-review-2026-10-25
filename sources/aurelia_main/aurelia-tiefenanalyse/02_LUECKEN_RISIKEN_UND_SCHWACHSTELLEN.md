# AURELIA — Lücken, Risiken und Schwachstellen-Analyse

Stand: 2026-08-25  
Fokus: Kritische Prüfung, Identifikation blinder Flecken und Risikomatrix  

---

## 1. Übersicht der identifizierten Lücken

Obwohl die Dokumentation und die Verfassung außergewöhnlich detailliert und präzise sind, offenbart ein schonungsloser technischer Audit mehrere **Architektur- und Implementierungslücken**, die vor einem Produktivbetrieb geschlossen werden müssen.

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        IDENTIFIZIERTE LÜCKEN                           │
├────────────────────────────────┬───────────────────────────────────────┤
│ 1. Kryptographie & RLS         │ Fehlende KMS-Spezifikation für         │
│    (DSGVO Art. 9)              │ Envelope Encryption & Key Derivation   │
├────────────────────────────────┼───────────────────────────────────────┤
│ 2. IPC & Prozessgrenzen        │ Unkonkretes Protokoll zwischen        │
│                                │ Web-App (Node) und Daemonen (Debian)  │
├────────────────────────────────┼───────────────────────────────────────┤
│ 3. CPU Core-Contention         │ 6-Kern CPU muss 5 schwere Dienste     │
│                                │ bedienen (LLM, DB, Timer, Web, OS)    │
├────────────────────────────────┼───────────────────────────────────────┤
│ 4. Single-Server SPOF          │ M G1 ist Single Point of Failure;      │
│                                │ Backup-Restore-Prozess unvollständig  │
├────────────────────────────────┼───────────────────────────────────────┤
│ 5. Testing & Test-Harness      │ Echte CUDA-/Serial-Mocks und negative │
│                                │ Mandanten-Isolationstests fehlen      │
└────────────────────────────────┴───────────────────────────────────────┘
```

---

## 2. Detaillierte Risiko- und Lückenanalyse

### Lücke 1: Kryptographie & Key-Management für DSGVO Art. 9 Daten
* **Problem:** In `03-security-dsgvo.md` wird Envelope-Encryption mit Tenant-Keys gefordert. Es fehlt jedoch eine exakte Definition:
  - Wie werden die Tenant-Keys (`DEK` / `KEK`) abgeleitet (HKDF, Argon2id)?
  - Wo liegt der Master-Key? (LUKS-Passphrase, TPM 2.0 nvram, oder hardware-gebundenes Secret?)
  - Wie verhält sich die Suche über verschlüsselte Felder (z.B. deterministisches vs. randomisiertes AES-GCM / ChaCha20-Poly1305)?
* **Risiko:** Wenn Entwickler diesen Teil ad-hoc bauen, drohen Implementierungsfehler (z.B. IV/Nonce-Reuse bei AES-GCM) oder Leistungseinbrüche beim Entschlüsseln im RAM.
* **Empfehlung:** Spezifikation eines festen Kryptoschemas (z.B. AES-256-GCM mit libsodium / Tink) und Bereitstellung einer gehärteten `aurelia-crypto`-Bibliothek.

---

### Lücke 2: IPC & Micro-Daemon-Orchestrierung auf Debian
* **Problem:** Die Dokumente nennen `aurelia-gpud`, `aurelia-timerd`, `aurelia-emitterd` und CopyGuard. Es fehlt jedoch die exakte Definition der Inter-Process Communication (IPC):
  - Kommunizieren die Daemons über Unix Domain Sockets (UDS), NATS oder Redis Streams?
  - Wer überwacht Abstürze (Systemd Watchdogs, Supervisord)?
  - Was passiert, wenn `aurelia-gpud` während eines 5-minütigen Harmonisierungs-DSP-Jobs abstürzt?
* **Risiko:** Zombie-Prozesse, hängende Locks auf `/dev/ttyUSB0` (Spooky2 Emitter) oder unvollständige Computation Passports.
* **Empfehlung:** Definition von Protobuf- oder MessagePack-basierten UDS-Schnittstellen mit striktem Time-to-Live (TTL) Heartbeat und Systemd Socket-Activation.

---

### Lücke 3: CPU-Ressourcen-Budgetierung (AMD Ryzen 5 9600X)
* **Problem:** Der Ryzen 5 9600X besitzt 6 physikalische Kerne (12 Threads). Auf diesem Server laufen gleichzeitig:
  1. Linux OS & Caddy Reverse Proxy
  2. PostgreSQL 16 + TimescaleDB (Disk-I/O & Queries)
  3. Node.js (TanStack Start Web-App)
  4. CopyGuard LLM (Phi-4-mini / Gemma 3 mit AVX-512)
  5. `aurelia-timerd` (50ms Realtime-Schleife für bis zu Hunderte Kanäle)
  6. `aurelia-gpud` Host-Prozess & CUDA Driver Dispatch
* **Risiko:** Wenn das CopyGuard-LLM auf allen 6 Kernen rechnet, bricht die 50ms-Timer-Genauigkeit von `aurelia-timerd` ein (Jitter).
* **Empfehlung:** Strikte CPU-Affinität (`taskset` / `cgroups` / Systemd `CPUAffinity`):
  - *Cores 0-1:* `aurelia-timerd` (Echtzeit-Priorität / `SCHED_FIFO` oder isolierte Cores)
  - *Cores 2-3:* PostgreSQL & Redis
  - *Cores 4-5:* Node.js Web-App, Caddy & CopyGuard LLM (gedrosselt auf max 2 Threads).

---

### Lücke 4: Hardware-Emitter Exklusivität & Race Conditions
* **Problem:** `aurelia-emitterd` steuert ein serielles Gerät (`/dev/ttyUSB0`). Serieller Zugriff ist naturgemäß strikt exklusiv.
* **Risiko:** Wenn zwei Therapeuten gleichzeitig eine Harmonisierung mit Hardware-Lease anfordern, muss die Warteschlange deterministisch und transparent sein. Ein unsauberer Disconnect kann den USB-Serial-Port blockieren.
* **Empfehlung:** Hardware-Lease-Manager mit Software-Locking via `flock` auf OS-Ebene und automatischer Port-Reset-Logik (DTR/RTS Toggle oder USB-Cycle via `uhubctl`), falls der Emitter nicht mehr antwortet.

---

### Lücke 5: Desaster-Recovery & Restore-Validierung (P1 Pilot)
* **Problem:** M G1 ist ein Single Server. Ein Defekt des Mainboards oder beider NVMes legt das System lahm. In `docs/26-wiedervorlage.md` ist WV01 ("Backup vor erstem Art. 9") vermerkt, aber noch nicht als automatisierter Test implementiert.
* **Risiko:** Datenverlust oder wochenlanger Ausfall, wenn kein automatisierter Restore-Test auf einer Zweitmaschine existiert.
* **Empfehlung:** Implementierung eines wöchentlichen, automatisierten "Headless Restore Tests" auf einem Test-Container/VPS, der die verschlüsselten WAL-Dateien und MinIO-Snapshots zieht, einspielt und per Smoke-Test validiert.

---

## 3. Risikomatrix (Likelihood vs. Impact)

| Risiko-ID | Titel / Beschreibung | Eintritts-wahrscheinlichkeit | Schadens-ausmaß | Gesamtrisiko | Gegenmaßnahme |
|---|---|---|---|---|---|
| **R-01** | **Heilversprechen / HWG-Verstoß** durch Benutzertexte | Mittel | Kritisch | **HOCH** | CopyGuard Fail-Closed Filter zwingend in RAM vor jeder Textanzeige/PDF. |
| **R-02** | **Cross-Tenant Datenleck** auf GPU/DB | Gering | Katastrophal | **HOCH** | RLS in Postgres + CUDA Buffer Zeroing + Isolation Key `(tenant,client,job)`. |
| **R-03** | **Totalausfall Server M G1** (Hardware) | Mittel | Hoch | **MITTEL-HOCH** | P1-Betriebsziel (RPO 15min, RTO 8h) mit verschlüsseltem Offsite-WAL-Backup. |
| **R-04** | **Timer-Drift / CPU Jitter** durch LLM-Last | Hoch | Mittel | **MITTEL** | CPU-Core Pinning (`CPUAffinity`) für `aurelia-timerd`. |
| **R-05** | **USB-Blockade Spooky2** durch Verbindungsabbruch | Mittel | Gering | **GERING-MITTEL** | Hardware-Lease Watchdog mit automatischem Serial-Port Cycle. |
| **R-06** | **Regulatorische Einstufung als Medizinprodukt** | Gering | Katastrophal | **HOCH** | Reine Dokumentations- & Berechnungssoftware; keine Diagnosen. |

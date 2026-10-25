# AURELIA — Master-Umsetzungsplan (Phasen & Subschritte)

Stand: 2026-08-25  
Projekt: AURELIA  
Methodik: Sequenzielle Stop-Gate-Entwicklung, Test-Driven Development (TDD), Fail-Closed Governance  

---

## 1. Phasenübersicht & Stop-Gate-Architektur

```text
┌──────────────────────────────────────────────────────────────────────────────────┐
│                             AURELIA PHASEN-ROADMAP                               │
├─────────┬──────────────────────────────┬──────────────────┬──────────────────────┤
│ Phase   │ Bezeichnung                  │ Status           │ Kritisches Gate      │
├─────────┼──────────────────────────────┼──────────────────┼──────────────────────┤
│ Phase 0 │ Verfassung & Kanonbereinigung│ ABGENOMMEN       │ C-Locks & X-Katalog  │
│ Phase 1 │ Gehäuse, Auth & Mandanten-ISO│ IN ARBEIT        │ Mandanten-Isolation  │
│ Phase 2 │ Praxisorganisation & Art. 9  │ GEPLANT          │ WV01 Backup + RLS    │
│ Phase 3 │ Kernel-ABI v1 & Modul-Labor  │ GEPLANT          │ Schema & Hash Replay │
│ Phase 4 │ Analyse-Engine & CUDA-Sched. │ GEPLANT          │ 16GB VRAM Pool / Key │
│ Phase 5 │ Harmonisierung & timerd/emit.│ GEPLANT          │ Reset-Lücke & Lease  │
│ Phase 6 │ Archiv, Trends & PDF-Report  │ GEPLANT          │ CopyGuard Audit-Pass │
│ Phase 7 │ GPU-Härtung & Last-Tests     │ GEPLANT          │ 20 Client Concurrency│
│ Phase 8 │ Quantum-Opt-in (cuQuantum)   │ GEPLANT          │ Getrennter Modus     │
│ Phase 9 │ Video/WebRTC                 │ GESTRICHEN (D10) │ —                    │
│ Phase 10│ Produktiver Pilotbetrieb     │ GEPLANT          │ WV02/WV03 Restore    │
└─────────┴──────────────────────────────┴──────────────────┴──────────────────────┘
```

---

## 2. Detaillierte Phasen- und Subschritt-Dokumentation

---

### PHASE 1: Gehäuse, Authentifizierung & Mandanten-Isolation (LÄUFT)
**Ziel:** Felsenfeste Multi-Tenant-Schale mit vollständiger Daten- und Identitätsisolation (rein synthetische Daten).

* [ ] **Subschritt 1.1: Kanon- und Textbereinigung abschließen**
  - Durchführung aller Aufgaben aus `docs/superpowers/plans/2026-08-24-aurelia-kanonbereinigung.md`.
  - Bereinigung veralteter WebRTC/Video-Texte in allen Dokumenten und UI-Routen.
  - Implementierung und Bestehen von `scripts/canon-contract.mjs`.
* [ ] **Subschritt 1.2: Bereinigung der Test-Suite & Typecheck**
  - Behebung des `@tanstack/react-start` Modulauflösungsfehlers in `app-data.test.ts`.
  - Sicherstellung, dass `npm test`, `npm run typecheck` und `npm run check:auth` fehlerfrei durchlaufen.
* [ ] **Subschritt 1.3: Mandanten-Isolationstest auf Datenbank-Ebene**
  - Erstellung automatisierter Integrationstests für 2 isolierte synthetische Mandanten.
  - Verifikation: Mandant A darf niemals Daten von Mandant B lesen oder manipulieren (Negative-Testing).
* [ ] **Subschritt 1.4: Multi-Tenant RBAC-Modell im Frontend spiegeln**
  - Implementierung der Rollenprüfung (`platform_admin`, `tenant_admin`, `therapist`, `assistant`, `client`).
  - Verifikation der UI-Sichtbarkeit gemäß Rollenmatrix.
* **Stop-Gate Phase 1:** Automatisierte Mandanten-Isolationstests grün; kein Klardatenzugriff möglich; Verfassungsprüfung fehlerfrei.

---

### PHASE 2: Praxisorganisation, Einwilligungen & Art. 9 DSGVO-Vorbereitung
**Ziel:** Sichere Akten- und Zeugenverwaltung, rechtssichere Einwilligungspfade, Vorbereitung der Envelope-Encryption.

* [ ] **Subschritt 2.1: WV01 — Backup- und Restore-Nachweis**
  - Definition des verschlüsselten externen Backup-Ziels (EU-Server / S3-kompatibler verschlüsselter Speicher).
  - Automatisierter Restore-Test mit synthetischen Test-Dumps vor Einspielung des ersten Art. 9 Datenmodells.
* [ ] **Subschritt 2.2: Datenbank-Schema für Praxisorganisation (`0003_praxis.sql`)**
  - Tabellen: `clients` (Klientenakten), `witnesses` (Zeugendaten), `consents` (Einwilligungen nach Art. 9 Abs. 2 lit. a), `groups` (Praxisgruppen).
  - Jede Tabelle enthält zwingend `tenant_id`, `encryption_key_id` und Postgres Row Level Security (RLS) Policies.
* [ ] **Subschritt 2.3: Envelope-Encryption-Layer (`aurelia-crypto`)**
  - Implementierung des Schlüsselableitungs- und Verschlüsselungsschemas (AES-256-GCM / libsodium).
  - Ver- und Entschlüsselung sensibler Zeugendaten ausschließlich im RAM des autorisierten Workers.
* [ ] **Subschritt 2.4: Zwischenablage (`AnalysisDraft`) & Workflows**
  - Implementierung der Tabelle `analysis_drafts` und des Status-Automaten (`draft` → `client_review` → `ready` → `promoted` | `discarded`).
  - Rollenprüfung: Klienten sehen nur `client_editable_fields` (C12).
* **Stop-Gate Phase 2:** Restore-Test erfolgreich protokolliert; RLS verhindert Mandantenübergriffe; Art. 9 Einwilligungspfad lückenlos auditiert.

---

### PHASE 3: Kernel-ABI v1, Registry & Modul-Labor
**Ziel:** Kapselung historischer Prototypen und neuer Rechenmodule hinter einer unveränderlichen, versionierten Schnittstelle.

* [ ] **Subschritt 3.1: Kernel-ABI Spezifikations-Engine (`aurelia-kernel-abi`)**
  - Erstellung der JSON-Schema-Validatoren für In/Out-Payloads.
  - Implementierung des SHA-256-Hash-Prüfers für alle Binär-/Python-Artefakte.
* [ ] **Subschritt 3.2: Modul-Adapter für historische Prototypen (Labor-Modus)**
  - Read-Only Import von `RadiMorphic` (aus `/opt/Prototypen/Radimorphic` @ `217dcf9`).
  - Kapselung in `RadiMorphicV1Adapter` mit striktem Budget (`vram_mb`, `cpu_ms_est`).
  - Markierung aller ungetesteten Module als `executable: false` / `isHardwareActivatable: false`.
* [ ] **Subschritt 3.3: Kozyrev-Rechenmodule im Labor (`K1–K5`)**
  - Implementierung von `kozyrev.padic.haar.v1` (p-adische Haar-DWT auf CPU AVX-512 & GPU).
  - Implementierung des administrativen 3-Stufen-Schalters (Platform AND Tenant AND Session).
  - Strikte Sperrung von `K6–K8` (keine IDs, kein Code).
* [ ] **Subschritt 3.4: Determinismus- & Replay-Test-Suite**
  - Verifikation: Gleicher Seed + Gleicher Kernel + Gleiche Eingabe = Exakt identischer Output-Hash.
* **Stop-Gate Phase 3:** Alle aktiven Kernel erfüllen die ABI v1 Spezifikation; SHA-256 Hashes stimmen überein; 100% Determinismus im Replay-Test.

---

### PHASE 4: Analyse-Engine, CUDA-Scheduler (`aurelia-gpud`) & Computation Passport
**Ziel:** Hochleistungsfähige, isolierte Ausführung von Rechenjobs auf der RTX 4000 SFF Ada mit vollem Nachweis.

* [ ] **Subschritt 4.1: CPU-Referenzimplementierung aller Rechenkerne**
  - Vollständige Lauffähigkeit aller Analysekerne auf CPU (Fallback & Verifikationsbasis).
* [ ] **Subschritt 4.2: CUDA Job-Pool & Scheduler (`aurelia-gpud`)**
  - Implementierung des 16 GB Job-Pool-Allocators (kein MIG).
  - Zuweisung exklusiver CUDA-Streams pro `(tenant_id, client_id, job_id)`.
  - Zeroing von VRAM-Puffern nach Job-Abschluss (Schutz vor Datenüberbleibseln).
* [ ] **Subschritt 4.3: Computation Passport Generator**
  - Generierung der unmanipulierbaren Ausweise (`run_id`, `kernel_hash`, `input_hash`, `seed`, `copyguard_digest`, `gpu_attest`, `dauer_ms`, `signatur`).
* [ ] **Subschritt 4.4: CopyGuard RAM-Integration**
  - Stufe 1: Regex-Lexikon (Fail-Closed).
  - Stufe 2: Lokales CPU-LLM (Phi-4-mini / Gemma 3 in RAM/NVMe mit AVX-512).
  - Prüfung jedes Analyseergebnisses vor Übertrag in den `AnalysisDraft`.
* **Stop-Gate Phase 4:** Parallele CUDA-Cross-Tenant-Tests beweisen 100% Puffer-Isolation; VRAM-Budget (16 GB Pool) wird niemals überbucht; Passport-Signaturen valide.

---

### PHASE 5: Harmonisierungs-Spur, `aurelia-timerd` & `aurelia-emitterd`
**Ziel:** Robuste, serverautoritative Echtzeit-Harmonisierung mit Ausfallsicherheit und sicherer Hardwareanbindung.

* [ ] **Subschritt 5.1: `aurelia-timerd` Daemon-Implementierung**
  - Hochpräzise Zeitsteuerung über Monotonic Clock / chrony NTP.
  - Zustandsautomat: `queued → armed → running ⇄ paused → stopped → archived | deleted`.
  - 50 ms UI-Ticks im RAM / 500–1000 ms persistente Checkpoints in PostgreSQL WAL.
* [ ] **Subschritt 5.2: Server-Reset & Lückenprotokollierung (D20)**
  - Implementierung der Crash-Recovery: Wiederaufnahme am letzten Checkpoint.
  - Dokumentation der Ausfallzeit (`gap_ms`) im Passport; kein heimliches Nachholen.
* [ ] **Subschritt 5.3: WebSocket-Fachkanal (`v:1` Protokoll)**
  - Bidirektionale Kommunikation für Ticks, State-Changes und Command-ACKs.
  - Reconnect-Handling mit Event-ID-Wiederaufnahme. Keine sensiblen Klardaten über den Socket!
* [ ] **Subschritt 5.4: Hardware-Emitter-Dienst (`aurelia-emitterd`)**
  - Serieller Treiber für Spooky2 / Generator X Pro (`/dev/ttyUSB*` via CP210x).
  - Exklusives Lease-Protokoll: `Lease → Arming → ACK → Emission → Reset`.
  - Bis zum physischen Hardware-Gate: `isHardwareActivatable: false`.
* [ ] **Subschritt 5.5: D21 HRV-Ohrclip Sensorkanal**
  - Datenaufnahme von RR-Intervallen über Web-Bluetooth oder lokalen USB-Relay.
  - Reine mathematische FFT- & Wavelet-Berechnung; strikt keine medizinische Diagnostik.
* **Stop-Gate Phase 5:** Simulierter Server-Kill beweist akkurate Lückenprotokollierung; Emitter-Lease verhindert Doppelzugriffe; WebSocket-Ticks laufen stabil mit 50ms.

---

### PHASE 6: Archiv, Langzeittrends & PDF-Report-Generierung
**Ziel:** Performante historische Auswertungen und rechtssichere, ansprechende PDF-Exporte.

* [ ] **Subschritt 6.1: Timescale Continuous Aggregates & pgvector Indizierung**
  - Automatische Aggregation von Harmonisierungs-Verläufen (Stunden/Tage/Monate).
  - Ähnlichkeitssuche von Ratenmustern strikt *innerhalb* desselben Mandanten via `pgvector`.
* [ ] **Subschritt 6.2: WV06 — Medien- & Codec-Spezifikation**
  - Standardisierung von AVIF (Bilder), Opus (Audio-Cues 24–48 kbit/s), FLAC (Archivton).
  - Speicherung in MinIO mit mandantenspezifischer Verschlüsselung; Zeugendaten niemals im CDN.
* [ ] **Subschritt 6.3: PDF-Report-Generator mit integriertem CopyGuard**
  - Generierung von eleganten Praxisberichten im Pergament/Tinte/Sage-Design.
  - Jeder Textbaustein durchläuft vor dem Rendern den CopyGuard-Filter.
  - Einbettung des signierten Merkle-Passports als Verifikations-QR-Code.
* [ ] **Subschritt 6.4: DSGVO-Auskunfts- und Export-Job**
  - Vollständiger Mandanten- und Klienten-Datenexport (JSON/ZIP) als asynchroner Hintergrundjob.
* **Stop-Gate Phase 6:** DSGVO-Export entspricht 1:1 den gespeicherten Daten; kein PDF enthält verbotene Heilversprechen; Archiv-Queries bleiben unter 100ms.

---

### PHASE 7: GPU-Härtung, Last- & Penetrationstests
**Ziel:** Nachweis von Stabilität, Sicherheit und Performance unter praxisnaher Spitzenlast.

* [ ] **Subschritt 7.1: Multimandanten-Lasttest (20 Klienten Concurrency)**
  - Simulation von 20 gleichzeitigen Klienten mit gemischten Analyse- und Harmonisierungs-Workloads.
  - Nachweis: Keine VRAM-Überbuchung (VRAM bleibt $\le$ 16 GB), keine Timer-Jitter $> 10\%$.
* [ ] **Subschritt 7.2: CPU-Affinitäts- & CGroup-Härtung**
  - Festes Pinning von `aurelia-timerd` auf isolierte CPU-Kerne.
  - Drosselung von CopyGuard-LLM-Inferenz auf Nebenthreads.
* [ ] **Subschritt 7.3: Automatisierter Sicherheitsscan & Penetrationstest**
  - Statische Codeanalyse (Semgrep, CodeQL), Dependency-Audits.
  - Dynamischer API-Penetrationstest (OWASP Top 10, Auth-Bypass-Versuche, RLS-Bypass).
* **Stop-Gate Phase 7:** System besteht 24-Stunden-Dauerstresstest ohne Memory-Leaks oder Abstürze; Zero High/Critical Security Findings.

---

### PHASE 8: Quantum-Opt-in Modul (`cuQuantum` / `PennyLane`)
**Ziel:** Optionale quanteninspirierte Rechenkerne hinter der stabilen Kernel-ABI.

* [ ] **Subschritt 8.1: Quanten-Kernel Spezifikation**
  - Einbindung von `cuQuantum` / `PennyLane` State-Vector-Simulationen auf der Ada GPU.
  - Strikte Trennung vom Standard-Berechnungspfad (eigener Modus-Parameter im Passport).
* [ ] **Subschritt 8.2: Transparente Kennzeichnung & CopyGuard**
  - Alle Quanten-Ausgaben tragen die Quelle `simulated_quantum`.
  - Ausschluss jeglicher pseudowissenschaftlicher Behauptungen ("Verschränkung mit dem Klienten").
* **Stop-Gate Phase 8:** Quantenkerne teilen sich sicher den 16 GB VRAM-Pool; vollständige Reproduzierbarkeit bei gleichem Seed.

---

### PHASE 9: WebRTC & Video (GESTRICHEN)
*Status: Gemäß Leitentscheidung D10 und O08 dauerhaft gestrichen.* Keine Entwicklung oder Bereitstellung.

---

### PHASE 10: Produktiver Pilotbetrieb, Debian-Härtung & Rollout
**Ziel:** Geordneter Produktivstart für ausgewählte Praxis-Piloten auf dem GPU Server M G1.

* [ ] **Subschritt 10.1: WV03 — Passkeys & WebAuthn auf Debian schalten**
  - Produktive Aktivierung von Passkeys (FIDO2/WebAuthn) mit TOTP-Fallback.
  - Deaktivierung aller Entwicklungs-/Preview-Logins.
* [ ] **Subschritt 10.2: WV02 — Abo- & Quota-Aktivierung**
  - Aktivierung der technischen Quotas (VRAM-Limits, parallele Timer-Kanäle).
  - Stripe/Zahlungs-Integration für Praxis-Abonnements.
* [ ] **Subschritt 10.3: Debian Bookworm Produktions-Härtung**
  - Konfiguration von Caddy mit HSTS, CSP, mTLS für interne Dienste, UFW Firewall.
  - Systemd-Unit-Hardening (`ProtectSystem=strict`, `NoNewPrivileges=true`, `PrivateTmp=true`).
* [ ] **Subschritt 10.4: Betreiber-Abnahme & Pilotstart**
  - Formale Unterzeichnung der Betriebsdokumentation, des Risikoregisters und der TOMs.
  - Freigabe für die ersten 5 Pilot-Praxen.
* **Stop-Gate Phase 10:** Vollständiger Restore-Test erfolgreich auf M G1 protokolliert; Caddy A+ SSL-Rating; Pilotbetreiber bestätigt reibungslosen Ablauf.

# 06 — Phasenplan mit Subschritten (2026-08-25)

Legende je Subschritt: **[A] Abnahmekriterium** (messbar), **[≈] Aufwandsschätzung** (erfahrener Entwickler, Bandbreite). Gate-Regel: Keine Phase beginnt vor formal erfülltem Gate der vorigen (Verfassung/09-roadmap).

---

## Phase 0 — Konzept & Kanon (ABGENOMMEN 2026-08-23/24)
Verifiziert: Verfassung, C01–C12, X-Katalog, D-Set, K1–K5, H1–H3, WV01–WV06 stehen und sind konsistent dokumentiert. **Kein Handlungsbedarf außer Ausführung des Bereinigungsplans (→1.1).**

---

## Phase 1 — Gehäuse: Auth, Mandanten, Isolation (LÄUFT; Restschätzung ~2 Wochen)

- [ ] **1.1 Kanonbereinigung ausführen** (Plan `docs/superpowers/plans/2026-08-24-aurelia-kanonbereinigung.md`, Tasks 1–8: canon-contract.mjs + Tests, D08–D12-Statusharmonisierung, Docs/UI-Bereinigung, CI-Hook).
  - **[A]** `npm run check:canon` existiert und ist grün; keine WebRTC-Restformulierung in aktiven Flächen.
  - **[≈]** 1–2 Tage.
- [ ] **1.2 Qualitätsschleife grün** (fixt DEF-01/02/03): Test-Runner-Migration (vitest/tsx), tsconfig ohne `baseUrl` + vite/client-Types, `check:auth` statisch prüfbar; Windows-/Linux-Glob-Portabilität.
  - **[A]** `npm test`, `npm run typecheck`, `npm run check:canon` → Exit 0 auf CI (Linux) und lokal.
  - **[≈]** 1–2 Tage.
- [ ] **1.3 Mandanten-Isolationstest automatisieren**: zwei synthetische Mandanten; Negativtests (Mandant A kann B nie lesen/schreiben, auch nicht über manipulierte Parameter); Rollenmatrix (`platform_admin`…`client`) als Testtabelle.
  - **[A]** Tests rot bei absichtlichem Cross-Zugriff, grün im Normalfall; dokumentierter Isolationsnachweis.
  - **[≈]** 2–3 Tage.
- [ ] **1.4 data_class-Guard zentralisieren** (GAP-12): jede Serverfunktion, die Aktendaten berührt, erzwingt `assertSynthetic(tenantId)` fail-closed.
  - **[A]** Unit-Test: Anfrage mit `data_class≠synthetic` wirft.
  - **[≈]** 0,5–1 Tag.
- [ ] **1.5 Phase-1-Gate**: Abnahme durch Betreiber (Startwort Phase 2 gemäß 11-llm-handoff.md).
  - **[A]** Schriftliche Freigabe; STATUS.md aktualisiert.

---

## Phase 2 — Praxisorganisation & Art.-9-Vorbereitung (~4–6 Wochen)

- [ ] **2.1 Krypto-Spezifikation** (GAP-01): `docs/27-crypto-spec.md` (KEK/TPM-LUKS, DEK/HKDF je Mandant, AES-256-GCM, Rotation, Conformance-Tests). **[A]** Betreiber + DSB-Review bestanden. **[≈]** 2–3 Tage.
- [ ] **2.2 WV01 Backup/Restore-Design + Nachweis** (GAP-06): pgBackRest, verschlüsseltes EU-Offsite, RPO 15/60 min dokumentiert; **Restore-Test auf Zweitinstanz** mit Protokoll. **[A]** Isolierter Restore erfolgreich + Protokoll signiert. **[≈]** 3–5 Tage.
- [ ] **2.3 Schema `0003_praxis.sql`**: `clients`, `witnesses` (encrypted_payload bytea, hash), `consents` (purpose, granted/revoked), `groups`; alles mit `tenant_id`; **RLS-Policies** je Tabelle. **[A]** Negative RLS-Tests (GAP-09) grün. **[≈]** 3–4 Tage.
- [ ] **2.4 Envelope-Crypto-Bibliothek** `src/lib/crypto/` (bzw. Server-Gegenstück) inkl. Keyring-Anbindung TPM/LUKS und Rotation-Job. **[A]** Conformance-Vektoren grün; Roundtrip-Test. **[≈]** 3–4 Tage.
- [ ] **2.5 AnalysisDraft + Einwilligungspfad UI/Server**: Statusautomat draft→client_review→ready→promoted|discarded; `client_editable_fields` (C12); TTL 7 Tage mit Archiv-Vorschlag (U10). **[A]** E2E-Test Einwilligung→Draft→Promote-ACK. **[≈]** 1 Woche.
- [ ] **2.6 Gate**: Art.-9-Einwilligungspfad lückenlos auditiert; Restore nachgewiesen; **erst dann** Art.-9-Klartext überhaupt möglich.

---

## Phase 3 — Kernel-ABI & Modul-Labor (~4–5 Wochen)

- [ ] **3.1 Manifest-Schema + Registry** (IN-02): `kernel-manifest.schema.json`, Validator-CLI, Registry-Tabelle. **[A]** Invalides Manifest → Registry-Lehne ab. **[≈]** 2–3 Tage.
- [ ] **3.2 IPC-/Daemon-Vertrag** `docs/28-daemon-ipc.md` (GAP-02; bewusst hier, weil die Labor-Adapter ihn als Erste brauchen): UDS+Protobuf/JSON-RPC, Heartbeat/TTL, Abbruchsemantik. **[A]** Review freigegeben; Dummy-Daemon-Roundtrip-Test. **[≈]** 2–3 Tage.
- [ ] **3.3 Labor-Adapter RadiMorphic** (read-only aus `/opt/Prototypen/Radimorphic` @217dcf9, verifiziert vorhanden) + Radi144: Budgets gesetzt, `executable:false` bis Gate. **[A]** Manifest + Hash registriert; Lauf nur im Labor-Mandanten. **[≈]** 1 Woche.
- [ ] **3.4 Kozyrev K1–K5**: `kozyrev.padic.haar.v1` (Default an), REG/p3/p5/K5 aus; Drei-Ebenen-Schalter (platform∧tenant∧session, auditiert, Admit prüft vor VRAM). **[A]** Schalter-Testkette: fehlendes Flag = aus, ohne Fallback. **[≈]** 1 Woche.
- [ ] **3.5 Replay/Golden-Files** (IN-03): CI-Test strict-Repro. **[A]** Bitidentische Output-Hashes bei gleichem Seed. **[≈]** 2–3 Tage.
- [ ] **3.6 Gate**: „Schema + Hash" für alle aktiven Kernel erfüllt.

---

## Phase 4 — Analyse strikt: CPU-Referenz, CUDA-Scheduler, Passport (~5–7 Wochen)

- [ ] **4.1 Server-CUDA-Gate** (SRV-01/02): Reboot → NVML-Sync, Toolkit-Installation, deviceQuery. **[A]** `nvidia-smi` + Beispielkernel grün. **[≈]** 0,5 Tag + Wartungsfenster.
- [ ] **4.2 CPU-Referenz aller Kerne** (inkl. AVX-512-Pfad IN-04). **[A]** Parität CPU↔Golden-Files. **[≈]** 1–2 Wochen.
- [ ] **4.3 `aurelia-gpud`**: 16-GB-Pool-Allocator, Streams/Arenen je (tenant,client,job), VRAM-Zeroing nach Job, Fair-Queue, Drain. **[A]** Cross-Tenant-GPU-Test (Buffer zweier Jobs überlappen nie; nach Job kein Datenrest lesbar). **[≈]** 2–3 Wochen.
- [ ] **4.4 Computation Passport** (signiert, mit copyguard_digest, Quellenangabe je Zahl). **[A]** Manipulationstest: geänderter Input → anderer Hash → Verifikation schlägt aus. **[≈]** 3–4 Tage.
- [ ] **4.5 CopyGuard Stufe 1+2** (Lexikon fail-closed + RAM-LLM mit GBNF, IN-06); Digest in Draft/Passport. **[A]** Lexikon-Blocktest; LLM-Formattest; Latenzbudget. **[≈]** 1 Woche.
- [ ] **4.6 Gate**: Replay-Test + Cross-Tenant-GPU-Test bestanden.

---

## Phase 5 — Harmonisierung: timerd, Fachkanal, emitterd (~5–7 Wochen)

- [ ] **5.1 CPU-Pinning-Plan umsetzen** (GAP-04): systemd AllowedCPUs/SCHED_FIFO. **[A]** Jitter-Soak < 10 % über 24 h. **[≈]** 2–3 Tage.
- [ ] **5.2 `aurelia-timerd`**: Zustandsautomat, 50-ms-RAM-Ticks, 500–1000-ms-WAL-Checkpoints, Restart am letzten Checkpoint, Lücke in Passport (D20: nicht nachholen!). **[A]** Kill-9-Test: Lücke exakt = now−last_checkpoint, dokumentiert. **[≈]** 2–3 Wochen.
- [ ] **5.3 WebSocket-Fachkanal v:1**: analysis.progress, clipboard.updated, harm.tick/state/command→ack; Reconnect an letzter Event-ID; kein Zeugenklartext. **[A]** Reconnect-Test + Payload-Scan-Test (kein Klartext-Token auf dem Socket). **[≈]** 1–2 Wochen.
- [ ] **5.4 `aurelia-emitterd`** (noch ohne Hardware): Lease→Arming→ACK→Emission→Reset als Protokoll-Implementierung + Simulator; `isHardwareActivatable:false` bleibt. **[A]** Zwei konkurrierende Lease-Anfragen → deterministisch eine wartet. **[≈]** 1 Woche.
- [ ] **5.5 Gate**: Tick-Lücke im Ausweis; Leases getrennt (GPU-Job ≠ Emitter).

---

## Phase 6 — Archiv/Trend/Report (~3–4 Wochen)

- [ ] **6.1 Continuous Aggregates + pgvector** (mandantenintern). **[A]** Query-P95 < 100 ms unter Last. **[≈]** 3–4 Tage.
- [ ] **6.2 WV06-Codec-Entscheidung** + MinIO-Ablage (mandantenverschlüsselt, nie CDN). **[≈]** 2 Tage.
- [ ] **6.3 PDF-Report** im Designsystem, CopyGuard auf jeden Satz, Merkle-QR (IN-05). **[A]** Kein Report ohne CopyGuard-Digest. **[≈]** 1 Woche.
- [ ] **6.4 DSGVO-Auskunft/Export/Löschung als Jobs** mit Protokoll. **[A]** Export ≡ gespeicherter Datenstand (Differenztest leer). **[≈]** 3–4 Tage.

---

## Phase 7 — GPU-Härtung & Last (~2–3 Wochen)

- [ ] **7.1 20-Kunden-Soak** (gemischte Jobs): VRAM ≤ 16 GB, kein OOM, kein Leak (RSS stabil 24 h). **[≈]** 1 Woche.
- [ ] **7.2 Security-Tests**: SAST/Dependency/Secret-Scan, API-Pentest (OWASP, RLS-Bypass). **[A]** Zero High/Critical. **[≈]** 1 Woche.

---

## Phase 8 — Quantum opt-in (~2–3 Wochen, optional verschiebbar)

- [ ] **8.1** cuQuantum/PennyLane hinter ABI, eigener Modus im Passport (`simulated_quantum`), CopyGuard gegen Verschränkungs-Rhetorik. **[A]** Getrennter Modus nachweisbar; Seed-Repro.

## Phase 9 — Video/WebRTC: **GESTRICHEN (D10/O08).** Keine Arbeit.

---

## Phase 10 — Betrieb & Pilot (~3–4 Wochen + laufend)

- [ ] **10.1 WV03 Passkeys auf Debian** (WebAuthn primär, TOTP Fallback; Preview-Login aus). **[≈]** 3–4 Tage.
- [ ] **10.2 WV02 Preise/Abos** (Quotas scharf; Selbstbedienung erst nach Kündigungs-/Löschfristen-Sitz). **[≈]** 1 Woche (ohne Preiskalkül).
- [ ] **10.3 Debian-Härtung & Monitoring**: Caddy (HSTS/CSP/Rate), systemd-Sandboxing, Alerting (GAP-11), Port-/Rechte-Hygiene (SRV-03/04: keine root-Uvicorns mehr, Alt-Ports bereinigt). **[≈]** 1 Woche.
- [ ] **10.4 Pilotfreigabe**: Restore-Test auf M G1 protokolliert; TOMs/Risikoregister unterschrieben; 5 Pilot-Praxen.
- **[A] End-Gate:** Quartals-Restore-Ritual eingerichtet; Betriebsvereinbarung P1 (keine 24/7-Zusage) wirksam.

---

## Gesamtbandbreite

| Szenario | Dauer bis Phase 10 |
|---|---|
| 1 erfahrener Vollzeit-DEV | ~9–12 Monate |
| Agentengestützt + Betreiber-Reviews | ~12–20 Monate |
| Nur Wochenenden | > 24 Monate (nicht empfohlen: Phasen 4/5 brauchen zusammenhängende Fokuszeit) |

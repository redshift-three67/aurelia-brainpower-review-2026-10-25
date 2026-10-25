# 06 — Phasenplan V3 mit Subschritten (2026-08-25 17:33 CEST)

Konvention je Subschritt: **[A]** = messbares Abnahmekriterium, **[≈]** = Aufwandsband (erfahrener Einzelentwickler). Gate-Regel: keine Phase vor erfülltem Gate der vorigen (Kanon 09-roadmap). Neu in V3: **Phase 1.5 „Serverhärtung"** als eigenständiges Gate zwischen Gehäuse und Art.-9.

---

## Phase 0 — Konzept (ABGENOMMEN 2026-08-23/24)
Kein Handlungsbedarf; Ausführung des Bereinigungsplans läuft unter 1.1.

---

## Phase 1 — Gehäuse: Auth, Mandanten, Isolation (LÄUFT; Rest ≈ 2 Wochen)

- [ ] **1.1 Kanonbereinigung ausführen** (freigegebener Plan, Tasks 1–8: `canon-contract.mjs` + Tests, D08–D12-Harmonisierung, Docs/UI-WebRTC-Reste, npm-Script `check:canon`). **[A]** `npm run check:canon` grün; keine Restformulierung in aktiven Flächen. **[≈]** 1–2 T.
- [ ] **1.2 Qualitätsschleife grün** (fixt DEF-01/02/03): tsconfig (baseUrl raus, vite/client-Types), Test-Runner vitest/tsx + Mocks für Server-Only-Module, portabler Glob, `check:auth` statisch. **[A]** `test`+`typecheck`+`check:canon` Exit 0 lokal und CI. **[≈]** 1–2 T.
- [ ] **1.3 Mandanten-Isolation automatisiert testen**: zwei synthetische Mandanten; **negative** Tests (manipulierte Parameter, Cross-Zugriff muss scheitern); Rollenmatrix als Testtabelle. **[A]** Rot bei absichtlichem Cross-Zugriff, grün im Normalfall. **[≈]** 2–3 T.
- [ ] **1.4 `assertSynthetic`-Guard zentral** (GAP-12): jede Aktendaten berührende Serverfunktion erzwingt `data_class='synthetic'` fail-closed. **[A]** Unit-Test: fremde data_class → throw. **[≈]** 0,5–1 T.
- [ ] **1.5 Phase-1-Gate**: Isolationstest-Dokumentation + Betreiber-Startwort Phase 1.5/2 (11-llm-handoff).

---

## Phase 1.5 — Serverhärtung M G1 (**neu in V3**; ≈ 2–3 Tage + 1 Wartungsfenster)

- [ ] **SH-1 SSH:** `PermitRootLogin no`; Key-only; Admin-Konto statt klaus999-Allmacht. **[A]** `sshd -T` zeigt `permitrootlogin no`; Anmeldung als root unmöglich. **[≈]** 2 h.
- [ ] **SH-2 Sudo:** `NOPASSWD: ALL` entfernen; Whitelist (systemctl, iptables, virsh …) mit Kommentar; jede Eskalation geloggt. **[A]** `sudo -n -l` zeigt nur Whitelist. **[≈]** 1–2 h.
- [ ] **SH-3 Cron-Secrets:** PGPASSWORD aus crontab entfernen → `.pgpass` 0600; **Passwort rotieren**. **[A]** `crontab -l` enthält kein Secret. **[≈]** 1 h.
- [ ] **SH-4 Orchestrierung konsolidieren:** 9 failed Units disable/mask (oder repair); Strapi-Crashloop stoppen; **eine** Ebene (Empfehlung: Docker-Compose-File versioniert im Repo). **[A]** `systemctl --failed` leer; keine Restart-Loops. **[≈]** 0,5 T.
- [ ] **SH-5 Netz/Ports:** Alt-API 8000 → Loopback; xRDP 3389 → Admin-IPs/Firewall; Portplan AURELIA (Caddy :443 außen, App 127.0.0.1:8081, DB nur UDS/localhost); iptables-Persistenz via netfilter-persistent testen. **[A]** `ss -tulpn` zeigt keinen unnötig öffentlichen Port; Regeln überstehen Reboot. **[≈]** 0,5 T.
- [ ] **SH-6 GPU-Fenster:** Reboot (NVML-Sync) → `nvidia-smi`-Smoke → CUDA-Toolkit (12.2-kompatibel zu 535) → `deviceQuery`. **[A]** `nvidia-smi` + Beispielkernel grün. **[≈]** 0,5 T + Fenster.
- [ ] **SH-7 Speicher-Hygiene:** Docker-Prune (185 GB) **nach** Image-Listen-Archiv (Heritage-Beweissicherung); Build-Cache leer; `/opt`-Swapfile entfernen (Betreiber-Freigabe). **[A]** `/`-Belegung < 45 %; `docker system df` schlank. **[≈]** 0,5 T.
- [ ] **SH-8 Gate:** Härtungsprotokoll unterschrieben; Server neu inventiert (Vergleich gegen dieses Dokument 03).

---

## Phase 2 — Praxisorganisation & Art.-9-Vorbereitung (≈ 4–6 Wochen)

- [ ] **2.1 Krypto-Spezifikation** `docs/27-crypto-spec.md` (KEK aus LUKS/TPM, DEK je Mandant via HKDF-SHA256, AES-256-GCM/XChaCha20, deterministische Verschlüsselung nur für Suchindizes, Rotation als Job, Conformance-Tests). **[A]** Review Betreiber(+DSB) bestanden. **[≈]** 2–3 T.
- [ ] **2.2 WV01 Backup real:** pgBackRest + verschlüsseltes EU-Offsite-Ziel; RPO-DB 15 min/WAL-Archiv, Objekte 60 min; **isolierter Restore-Test** mit Protokoll. **[A]** Restore erfolgreich + signiert; danach quartalsweise Ritual. **[≈]** 3–5 T.
- [ ] **2.3 `0003_praxis.sql`:** `clients`, `witnesses` (encrypted_payload, hash), `consents` (purpose/granted/revoked), `groups`; alles `tenant_id` + **RLS-Policies**; negative RLS-Tests. **[A]** Cross-Tenant-Select unter falschem Context = leere Menge, Test grün. **[≈]** 3–4 T.
- [ ] **2.4 Crypto-Bibliothek** `src/lib/crypto/` + TPM/LUKS-Keyring + Rotation. **[A]** NIST-Vektoren grün; Roundtrip. **[≈]** 3–4 T.
- [ ] **2.5 AnalysisDraft + Einwilligungspfad:** Statusautomat draft→client_review→ready→promoted|discarded; `client_editable_fields` (C12); TTL 7 T + Archiv-Vorschlag (U10). **[A]** E2E: Einwilligung→Draft→Promote-ACK. **[≈]** 1 W.
- [ ] **2.6 Gate:** Art.-9-Pfad lückenlos auditiert; Restore nachgewiesen.

---

## Phase 3 — Kernel-ABI & Labor (≈ 4–5 Wochen)

- [ ] **3.1 Manifest-Schema+Registry** (IN-02). **[A]** Invalides Manifest wird abgelehnt. **[≈]** 2–3 T.
- [ ] **3.2 IPC-/Daemon-Vertrag** `docs/28-daemon-ipc.md` (GAP-02) + Dummy-Daemon-Roundtrip. **[A]** Review + Test grün. **[≈]** 2–3 T.
- [ ] **3.3 Labor-Adapter** RadiMorphic (read-only `/opt/Prototypen/Radimorphic` @217dcf9, verifiziert vorhanden) + Radi144; Budgets; `executable:false` bis Gate. **[A]** Manifest+Hash registriert; Lauf nur Labor-Mandant. **[≈]** 1 W.
- [ ] **3.4 Kozyrev K1–K5:** `kozyrev.padic.haar.v1` (Default an); Drei-Ebenen-Schalter platform∧tenant∧session, auditiert, Admit prüft vor VRAM; K6–K8 ohne Code. **[A]** Fehlendes Flag = aus, kein UI-Fallback. **[≈]** 1 W.
- [ ] **3.5 Golden-Files** (IN-03). **[A]** Bitidentische Hashes bei gleichem Seed. **[≈]** 2–3 T.
- [ ] **3.6 Gate:** „Schema+Hash" für alle aktiven Kernel.

---

## Phase 4 — Analyse strikt: CPU-Referenz, gpud, Passport (≈ 5–7 Wochen)

- [ ] **4.1 CPU-Referenz aller Kerne** (inkl. IN-04 AVX-512-Pfad). **[A]** Parität zu Golden-Files. **[≈]** 1–2 W.
- [ ] **4.2 `aurelia-gpud`:** 16-GB-Allocator; Streams/Arenen je `(tenant,client,job)`; VRAM-Zeroing nach Job; Fair-Queue/Drain. **[A]** Cross-Tenant-GPU-Test: kein Buffer-Overlap, kein Datenrest lesbar; VRAM ≤ 16 GB unter Last. **[≈]** 2–3 W.
- [ ] **4.3 Computation Passport** (signiert; Quelle je Zahl `simulated/measured/derived/manual/ai-generated`). **[A]** Manipulationstest: geänderter Input → Hash-Änderung → Verifikation schlägt aus. **[≈]** 3–4 T.
- [ ] **4.4 CopyGuard Stufe 1+2** (Lexikon fail-closed; RAM-LLM mit GBNF IN-06); Digest in Draft/Passport. **[A]** Lexikon-Blocktest; LLM-Formattest; Latenzbudget. **[≈]** 1 W.
- [ ] **4.5 Gate:** Replay + Cross-Tenant-GPU grün.

---

## Phase 5 — Harmonisierung: timerd, Fachkanal, emitterd (≈ 5–7 Wochen)

- [ ] **5.1 CPU-Pinning** (GAP-04): timerd Cores 0–1 `SCHED_FIFO`; DB 2–3; Web+LLM 4–5 mit Thread-Cap. **[A]** 24-h-Jitter-Soak < 10 %. **[≈]** 2–3 T.
- [ ] **5.2 `aurelia-timerd`:** Zustandsautomat; 50 ms RAM; 500–1000 ms WAL-Checkpoints; Resume am letzten Checkpoint; Lücke in Passport (D20: nie nachholen). **[A]** Kill-9-Test: Lücke = now−last_checkpoint exakt. **[≈]** 2–3 W.
- [ ] **5.3 WebSocket v:1:** progress/clipboard/harm.tick/state/command→ack; Reconnect an Event-ID; kein Zeugenklartext. **[A]** Reconnect-Test + Socket-Payload-Scan. **[≈]** 1–2 W.
- [ ] **5.4 `aurelia-emitterd` (Simulator):** Lease→Arming→ACK→Emission→Reset; `isHardwareActivatable:false` bleibt. **[A]** Konkurrierende Leases deterministisch geordnet. **[≈]** 1 W.
- [ ] **5.5 Gate:** Tick-Lücke im Ausweis; GPU-Lease ≠ Emitter-Lease.

---

## Phase 6 — Archiv/Trend/Report (≈ 3–4 Wochen)
- [ ] **6.1** Continuous Aggregates + pgvector (mandantenintern). **[A]** P95 < 100 ms. **[≈]** 3–4 T.
- [ ] **6.2** WV06-Codecs + MinIO (mandantenverschlüsselt; nie CDN). **[≈]** 2 T.
- [ ] **6.3** PDF-Report mit CopyGuard + Merkle-QR (IN-05). **[A]** Kein Report ohne Digest. **[≈]** 1 W.
- [ ] **6.4** DSGVO-Auskunft/Löschung als Jobs. **[A]** Export ≡ Datenbestand (Differenztest leer). **[≈]** 3–4 T.

## Phase 7 — Härtung & Last (≈ 2–3 Wochen)
- [ ] **7.1** 20-Kunden-Soak: VRAM ≤ 16 GB, RSS stabil 24 h. **[≈]** 1 W.
- [ ] **7.2** SAST/Dependency/Secret-Scan + Pentest. **[A]** Zero High/Critical. **[≈]** 1 W.

## Phase 8 — Quantum opt-in (≈ 2–3 Wochen)
- [ ] cuQuantum/PennyLane hinter ABI; Modus `simulated_quantum` im Passport; CopyGuard gegen Verschränkungs-Rhetorik. **[A]** Getrennter Modus nachweisbar; Seed-Repro.

## Phase 9 — Video/WebRTC: **GESTRICHEN (D10/O08).**

## Phase 10 — Betrieb & Pilot (≈ 3–4 Wochen + laufend)
- [ ] **10.1** WV03 Passkeys auf Debian (WebAuthn+TOTP; Preview-Login aus). **[≈]** 3–4 T.
- [ ] **10.2** WV02 Abos/Quotas scharf (Selbstbedienung erst nach Kündigungs-/Löschfristen). **[≈]** 1 W.
- [ ] **10.3** Monitoring/Alerting (GAP-11; Portplan beachten), Caddy-Härtung (HSTS/CSP/Rate), systemd-Sandbox; Quartals-Restore-Ritual. **[≈]** 1 W.
- [ ] **10.4** Pilotfreigabe: TOMs/Risikoregister unterschrieben; 5 Pilot-Praxen. **[A]** P1-Vereinbarung wirksam (keine 24/7-Zusage).

---

## Gesamtdauer-Szenarien (bis Phase 10)
| Szenario | Dauer |
|---|---|
| 1 erfahrener Vollzeit-DEV | ~9–12 Monate |
| Agentengestützt + Betreiber-Reviews | ~12–20 Monate |
| Nur Wochenende | >24 Monate (ungeeignet für 4/5) |

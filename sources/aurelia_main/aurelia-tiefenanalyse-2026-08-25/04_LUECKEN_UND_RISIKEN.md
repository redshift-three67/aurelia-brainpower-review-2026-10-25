# 04 — Lücken & Risiken (2026-08-25)

Sortiert nach Schwere. Jede Lücke enthält Nachweis, Wirkung und Gegenmaßnahme.

---

## A. Kritische Lücken (vor Phase 2 schließen)

### GAP-01: Kryptographie-Spezifikation für Art. 9 fehlt
- **Nachweis:** `docs/03-security-dsgvo.md` fordert Envelope-Encryption + Tenant-Keys + `encryption_key_id`; eine technische Spezifikation (Algorithmen, Key-Derivation, Rotation, Wiederherstellung) existiert in keinem Dokument und keinem Code.
- **Wirkung:** Ohne Spezifikation wird Phase 2 ad-hoc-verschlüsselt → IV/Nonce-Fehler, nicht rotierbare Keys, nicht testbarer Löschweg. DSGVO-Auskunft/Löschung (Pflicht als Jobs) nicht einklagbar.
- **Gegenmaßnahme:** Design-Doc `docs/27-crypto-spec.md` **vor** `0003_praxis.sql`: KEK im LUKS/TPM-Keystore, DEK je Mandant via HKDF-SHA256, AES-256-GCM (oder XChaCha20-Poly1305), deterministische Verschlüsselung nur für Suchindizes, Key-Rotation als Job, „Crypto-Conformance-Tests" (NIST-Vektoren) als Gate.

### GAP-02: IPC-/Daemon-Vertrag fehlt (Node ↔ timerd/gpud/emitterd/CopyGuard)
- **Nachweis:** Kein Dokument definiert Transport (UDS? NATS? Redis-Streams?), Serialisierung (JSON-RPC? Protobuf?), Authentisierung zwischen Prozessen, Timeouts/Heartbeats, Absturzverhalten.
- **Wirkung:** Phase 4/5 nicht planbar; Gefahr von Zombie-Jobs, hängenden Emitter-Locks (Seriell ist exklusiv!), unvollständigen Passports.
- **Gegenmaßnahme:** Design-Doc `docs/28-daemon-ipc.md`: UDS + Längenpräfix-Protobuf/JSON, mTLS oder Shared-Socket-Permissions (0600, eigene Gruppe `aurelia`), TTL-Heartbeat, `systemd`-Watchdog + Socket-Activation, definierte Abbruch-Semantik je Daemon (gpud: Job-Abort + VRAM-Zeroing; emitterd: Lease-Invalidierung + DTR-Reset).

### GAP-03: Qualitätsschleife rot (verifiziert DEF-01..03)
- **Wirkung:** Stop-Gates sind nicht automatisiert prüfbar; „ehrliche Abnahme der vorigen Phase" (Roadmap-Prinzip) technisch nicht möglich.
- **Gegenmaßnahme:** Sofortmaßnahme im Phasenplan (Subschritt 1.2): Vitest-Migration, tsconfig-Fix, check:auth statisch; danach CI (GitHub Actions) mit `test`, `typecheck`, `check:canon`, `check:auth` als Pflicht-Gates.

---

## B. Hohe Lücken (vor Phase 4/5 schließen)

### GAP-04: CPU-Budget-Plan für 6 Kerne fehlt
- **Nachweis:** Verfassung verteilt Dienste auf die CPU, aber nirgends steht ein Core-Plan; CopyGuard-LLM (CPU, AVX-512) und timerd (50 ms) konkurrieren.
- **Gegenmaßnahme:** Betriebsvorgabe: Core 0–1 `aurelia-timerd` (+ IRQ-Affinität), Core 2–3 PostgreSQL/Redis, Core 4–5 Web+LLM (Thread-Cap). Umsetzung via systemd `CPUAffinity`/`AllowedCPUs` + `SCHED_FIFO` für timerd. Messbar machen: Jitter-Budget < 10 % pro Tick als Soak-Test-Kriterium.

### GAP-05: GPU-Treiber-Mismatch + fehlendes CUDA-Toolkit (verifiziert SRV-01/02)
- **Gegenmaßnahme:** Wartungsfenster: Reboot → `nvidia-smi`-Smoke → Toolkit-Installation → `deviceQuery`-Test. Vor Phase 3 als „CUDA-Gate" dokumentieren.

### GAP-06: Backup/Restore (WV01) ist nur Termin, kein Design
- **Nachweis:** WV01 an Phase 2 gebunden;Restore-Ziele (RPO 15 min DB / 60 min Objekte, RTO 8 h) stehen in der Vorbereitungs-Spezifikation, Werkzeugwahl (pgBackRest vs. wal-g), Ziel (EU-Offsite, verschlüsselt), Restore-Test-Ritual fehlen.
- **Gegenmaßnahme:** Subschritt 2.1 konkretisiert: pgBackRest auf M G1, verschlüsseltes S3-kompatibles EU-Ziel, Restore-Test als Skript + Protokollvorlage.

---

## C. Mittlere Lücken

| ID | Lücke | Wirkung | Gegenmaßnahme |
|---|---|---|---|
| GAP-07 | **Keine Zeitschätzungen/Ressourcenplanung** in der Roadmap | Planbarkeit für den Betreiber unvollständig; kritischer Pfad unsichtbar | Phasenplan (Dokument 06) enthält Aufwandsbänder; monatlich gegen Ist stellen |
| GAP-08 | **Port-/Namenskollisionen mit Alt-System** (8080, 8000, 5432 belegt; verifizert) | Preview-/Deploy-Konflikte, Sicherheitsfläche | AURELIA-Portplan festlegen (z. B. 8081 intern, Caddy :443 außen), Alt-API auf Loopback binden |
| GAP-09 | **RLS erst „wo nötig" formuliert**, aber keine Testmethode definiert | Isolation könnte versehentlich nur im App-Code, nicht in der DB durchgesetzt werden | Negative Isolationstests als ausführbare Abnahmetests (falscher Tenant-Context muss leere Menge liefern) — bereits in Spezifikation gefordert, muss in Phase 2 real werden |
| GAP-10 | **Kernel-Aufnahme-Prüfung ist Textpflicht, noch keine Checkliste als Code** | Phase 3 „Schema + Hash"-Abnahme braucht ausführbare Form | `kernel-manifest.schema.json` + Validierer bauen (Subschritt 3.1) |
| GAP-11 | **Monitoring/Alerting-Design offengeblendet** (nur „OpenTelemetry, Logs ohne Payload") | P1-Betriebsziele (24 h max. Unterbrechung) nicht überwachbar | Subschritt 10.3: Prometheus+Alertmanager (bereits 9090 offen — prüfen, ob Alt-Nutzung), Alert-Routing, On-Call-Ritual |
| GAP-12 | **DSGVO-Art.-9-Fail-Closed im UI** gefordert, aber kein Feature-Flag-Mechanismus definiert, der reale Nutzung verhindert | Versehentliche echte Klientendaten vor Freigabe | `data_class`-Guard zentral in Serverfunktionen erzwingen: `assertSynthetic(context.tenantId)` — fail-closed außer nach dokumentierter Betreiberfreigabe |

---

## D. Risikomatrix (Eintritt × Schaden)

| ID | Risiko | E | S | Score | Primärkontrolle |
|---|---|---|---|---|---|
| R-01 | HWG-/MDR-Claim rutscht in sichtbaren Text | M | Kritisch | **Hoch** | CopyGuard 2-Stufen, fail-closed (C02/D13) — bauen in Phase 4, Lexikon schon Phase 2 |
| R-02 | Cross-Tenant-Leck (DB oder GPU-Buffer) | G | Katastrophal | **Hoch** | RLS + Isolation-Key (tenant,client,job) + negative Tests (Phase 2/4-Gates) |
| R-03 | Totalausfall M G1 | M | Hoch | **Hoch** | WV01/Backup-Design + Restore-Nachweis vor Art. 9 (GAP-06) |
| R-04 | Timer-Jitter durch LLM-Last | H | Mittel | **Mittel** | CPU-Pinning (GAP-04) + Soak-Test |
| R-05 | Emitter-Deadlock (Serial exklusiv) | M | Gering | **Mittel** | Lease+Watchdog+DTR-Reset (GAP-02) |
| R-06 | Regulatorische Umdeutung zum Medizinprodukt | G | Katastrophal | **Mittel** | Verfassung D01 + Funktions-/Claim-Matrix (Arbeitspaket G der Spezifikation) |
| R-07 | Alt-/Neu-System-Verwechslung auf dem Server | M | Mittel | **Mittel** | Portplan, getrennte systemd-Units, Namenskonvention `aurelia-*` (GAP-08) |

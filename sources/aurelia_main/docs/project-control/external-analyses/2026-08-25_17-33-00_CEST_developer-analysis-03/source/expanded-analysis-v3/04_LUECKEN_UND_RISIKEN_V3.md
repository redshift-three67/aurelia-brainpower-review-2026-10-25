# 04 — Lücken & Risiken V3 (Projekt + Server kombiniert, 2026-08-25 17:33 CEST)

Schweregrade: KRITISCH (vor nächstem Milestone zwingend) · HOCH (vor Phasen-Gate) · MITTEL (einplanen). IDs: DEF = Codebasis-Defekt, GAP = konzeptionelle Lücke, SRV = Server-Befund.

---

## 1. KRITISCH

### SRV-06/07 — SSH/Sudo-Überhöhung
`PermitRootLogin yes` + `klaus999 (ALL) NOPASSWD: ALL`. Jeder Kompromittierungsfall = sofort Root. Bei 23.292 SSH-Fehlversuchen kein theoretisches Risiko.
→ **Maßnahme:** `PermitRootLogin no`; Sudo auf dokumentierte Whitelist (`virsh, systemctl, iptables …`) reduzieren; separates Admin-Konto; anschließend Fail2ban-Bilanz weiter beobachten.

### SRV-08 — Klartext-Passwort im Cron
`PGPASSWORD=radiquant4_dev` in `crontab -l` sichtbar (für jeden lesbar mit Log-Zugriff).
→ **Maßnahme:** `~/.pgpass` (0600) oder Secret-File; Passwort **rotieren** (war lesbar).

### SRV-01/02 — CUDA unbenutzbar (NVML-Mismatch, kein Toolkit)
Blockiert Phase 3/4 vollständig.
→ **Maßnahme:** Wartungsfenster: Reboot → NVML-Sync prüfen → Toolkit installieren → Smoke-Test.

### GAP-01 — Krypto-Spezifikation für Art. 9 fehlt
Envelope-Encryption ist gefordert, aber nicht spezifiziert (KEK-Quelle, DEK-Derivation, AEAD-Verfahren, Rotation, deterministische Suche, Lösch-Nachweis).
→ **Maßnahme:** `docs/27-crypto-spec.md` **vor** `0003_praxis.sql` (siehe 06, Subschritt 2.1).

### GAP-02 — IPC-/Daemon-Vertrag fehlt
Kein Dokument definiert Transport/Serialisierung/Authentisierung/Timeout/Abbruch zwischen Node-App und `timerd`/`gpud`/`emitterd`/CopyGuard.
→ **Maßnahme:** `docs/28-daemon-ipc.md` **vor** Phase 3 (UDS + Protobuf/JSON-RPC, TTL-Heartbeat, systemd-Watchdog, Abbruchsemantik je Daemon).

---

## 2. HOCH

| ID | Lücke/Risiko | Wirkung | Gegenmaßnahme (Termin) |
|---|---|---|---|
| SRV-05 | Kein Offsite-Backup (alles auf md3) | WV01 unerfüllt; Totalverlust bei Hardware-Defekt | pgBackRest/S3-EU-Ziel + Restore-Test (Phase 2, Subschritt 2.2) |
| SRV-04/03 | 9 failed Units (inkl. `iptables-restore`), Doppelorchestrierung, Strapi-Crashloop | Instabile Betriebsplattform; Firewall-Persistenz nach Reboot fragil | Ein Orchestrierungs-Layer; Units disable/mask; iptables-Persistenz via netfilter-persistent (Serverhärtung SH-4) |
| SRV-11 | Öffentliche Ports 8000/3389/9090/3001/6556 | Angriffsfläche | Alt-API auf Loopback; xRDP an Admin-IPs; Portplan für AURELIA (SH-5) |
| DEF-01..04 | Test/Typecheck rot; Kanonplan unausgeführt | Stop-Gates nicht automatisierbar | Qualitätsschleife grün (Subschritt 1.1/1.2) |
| GAP-04 | Kein CPU-Core-Budgetplan (6 Kerne, timerd 50 ms vs. LLM) | Timer-Jitter unter Last | Pinning-Vorgabe (Subschritt 5.1) + Soak-Gate |
| R-01 | HWG-/MDR-Claim in sichtbarem Text | Rechtlich kritisch | CopyGuard 2-stufig fail-closed (Phase 4; Lexikon ab Phase 2) |
| R-02 | Cross-Tenant-Leak (DB/GPU) | Katastrophal (Art. 9) | RLS + `(tenant,client,job)`-Arenen + **negative** Isolationstests als Gates (Phase 2/4) |

---

## 3. MITTEL

| ID | Lücke | Gegenmaßnahme |
|---|---|---|
| GAP-07 | Keine Aufwandsbänder/Ressourcenplanung im Kanon | In 06 ergänzt; monatlich Ist/Soll stellen |
| GAP-08 | Port-/Namenskollisionen Alt↔Neu (8000/8080/5432 belegt) | AURELIA-Portplan (Caddy außen, App 8081+ intern) in SH-5 |
| GAP-09 | RLS nur „wo nötig", keine Testmethodik | Negative Tests als ausführbare Abnahmetests definieren (2.3) |
| GAP-10 | Modulaufnahme nur Textpflicht | `kernel-manifest.schema.json` + Validator (3.1) |
| GAP-11 | Monitoring/Alerting undesignt (P1-Ziele nicht überwachbar) | Prometheus/Alertmanager + Ritual (10.3); Port 9090 ist bereits belegt (Alt) |
| GAP-12 | Art.-9-Fail-Closed im Code nicht zentral erzwungen | `assertSynthetic(tenantId)` in jeder Serverfunktion (1.4) |
| SRV-12/13/14 | Host-PG15 statt 16; Redis unter dnsmasq-User; Desktop-Snaps | Aufräumen im Serverhärtungsfenster |
| SRV-15 | 32-GB-Swapfile in `/opt` (doppelt zu md2) | Entfernen (Freigabe durch Betreiber) |
| R-04/R-05 | Timer-Jitter; Emitter-Deadlock | GAP-04-Pinning; Lease+Watchdog+DTR-Reset (5.4) |
| R-06 | Regulatorische Umdeutung zum Medizinprodukt | Funktions-/Claim-Matrix (Arbeitspaket G) als Release-Gate |

---

## 4. Risikomatrix (Eintritt × Schaden, V3)

| # | Risiko | E | S | Score | Primärkontrolle |
|---|---|---|---|---|---|
| R-01 | Claim-Rutschig ins UI/PDF | M | Kritisch | **Hoch** | CopyGuard fail-closed (Phase 4) |
| R-02 | Cross-Tenant-Leak | G | Katastrophal | **Hoch** | RLS+Arena-Isolation+Negative Tests |
| R-03 | Totalausfall M G1 **ohne Offsite** | M | Katastrophal | **Sehr hoch (bis SH/2.2)** | WV01 real umsetzen |
| R-08 | Server-Kompromittierung (SSH-Exposition + Root-Paths) | M | Katastrophal | **Sehr hoch (bis SH-1/2)** | Härtung SH-1…SH-3 sofort |
| R-04 | Timer-Jitter | H | Mittel | Mittel | Pinning + Soak |
| R-05 | Emitter-Deadlock | M | Gering | Mittel | Lease/Watchdog |
| R-06 | MDR-Umdeutung | G | Katastrophal | Mittel | Claim-Matrix |
| R-07 | Alt/Neu-Verwechslung auf Server | M | Mittel | Mittel | Portplan, `aurelia-*`-Namensraum |

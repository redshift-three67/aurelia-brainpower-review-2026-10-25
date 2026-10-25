# AURELIA — Project constitution (LLM + human)

This file is the **product source of truth** for any developer or coding agent.
Host-sandbox rules in `AGENTS.md` do not override this file for product decisions.

```yaml
product: AURELIA
phase: 1
phase_name: Gehäuse
phase0: abgenommen
phase1_shell: technically-present
status: phase-1-shell-present-product-work-paused
current_server_gate: G0-SRV-0
pause_until: G0-SRV-12
pending: g0-backup-restore-proof-and-wiedervorlage-WV01-WV06
owner_github: redshift-three67
repo: redshift-three67/aurelia
language_ui: de
wellbeing_not_medical_device: true
auth: on
database: on
next_phase: resume-audit-02-after-documented-G0-SRV-12-pass
target_os: Ubuntu Server 24.04.4 LTS amd64 plus minimal GNOME
hardware: GPU Server M G1 (Ryzen 5 9600X, RTX 4000 SFF Ada 20GB, 128GB DDR5)
planned_storage: 2x2TB WD_BLACK SN850X with RAID1/LUKS2/LVM
memory_ecc: hardware-capable-but-active-ecc-not-yet-proven
cuda: locked
cuda_purpose_after_gate: analysis-harmonisation-optional-quantum
copyguard_place: ram-nvme
```

## What this is

Wellbeing- and documentation software for trained practitioners. Modular,
GDPR-compliant, server-authoritative analysis and harmonisation.

**Not** a medical device, not diagnosis, not a cure, not a physics proof.

## Heritage (do not confuse)

| Tree | Role | Write? |
|---|---|---|
| `redshift-three67/aurelia` | This constitution / Grok session | **Yes** |
| `redshift-three67/radiquant-cloud-build` branch `radiquant4` | Previous product. Git HEAD `7dae98e` (docs-only). `src/` unchanged since `5b51b29`. Build 0 code `65868a6`, 151 tests | Not this session |
| `redshift-three67/radiquant4` and `/opt/radiquant4` | Old FastAPI+Astro+engines, `cd9e9b4f` | **Never** |
| Lovable `ccecde78-…` | Preview of cloud-build, empty control plane | No disconnect, no publish |

There is **no** repo `redshift-cloud-build`. Codename `radiquant4` is the
**branch** of cloud-build, not the old GitHub repo.

Do **not** redo Build 0 from scratch. Do **not** start a module adapter now.

## Hard rules

1. MUST NOT claim diagnosis, therapy, cure, or clinical efficacy.
2. MUST run CopyGuard (lexicon fail-closed + local slim LLM **in RAM/NVMe**, not VRAM)
   on every visible sentence including clipboard drafts.
3. MUST keep Art. 9 data and compute on GPU Server M G1 (EU). Never plaintext
   in Lovable/US cloud.
4. MUST treat the server as clock: timers, analysis, emitter lease. No WebUSB.
5. MUST version compute as kernels (Radi144 → Works → Morphic → Blohm → Thoms → Copen).
6. MUST emit a Computation Passport including `copyguard_digest` and `tenant_id`.
7. MUST default to strict reproducibility. Stochastic/quantum explicit.
8. MUST scope every query **and every CUDA buffer** by `(tenant_id, client_id, job_id)`. `client` fail-closed.
9. MUST keep WCAG 2.2 AA / BFSG and sage/parchment tokens.
10. MUST NOT activate USB/GPU emission, publish Lovable, force-push `radiquant4`,
    or write `/opt/radiquant4`.
11. Spooky2 / Generator X Pro only via `aurelia-emitterd` (CP210x). Lease → Arming → ACK.
    Emitter lease ≠ GPU job lease.
12. Live: WebSocket is the analysis+harmonisation channel. Witness cache `no-store`.
13. CUDA is a 16 GB job pool with a software scheduler. No MIG on this card.
    Isolation key is (tenant_id, client_id, job_id). 20 clients is occupancy,
    not GPU occupancy. Virtual timers are many and cheap (D20). No overcommit.
14. Analysis goes to clipboard (`AnalysisDraft`) before `HarmonizationLane`.
15. Timer ledger is Postgres WAL + timerd RAM. GPU never stores the clock.
    After reset: resume from last_checkpoint, record the gap, do not invent time.
16. HRV ear-clip (D21) lives on the person, not the rack. No EEG. CopyGuard on text.
17. Kozyrev: K1–K5 locked and admin-toggleable (D22/D23). K6–K8 have **no**
    kernel id and **no** flag. Do not scaffold 3-tier / remedy / PPS-as-c2.
18. Kernel flags: platform AND tenant AND session, fail-closed, audited.
    Missing flag = off. `kozyrev.lab.*` stays `executable: false` without a new lock.
19. X-catalogue is **accepted** (2026-08-24). Do not silently drop IDs; do not implement them.
20. Video und WebRTC sind vollständig ausgeschlossen (D10, O08). Phase 9 nicht anlegen.
21. Phase 1 shell is ON: auth + tenant membership, `data_class=synthetic`.
    No real clients, no CUDA, no USB. Production Passkeys wait for M G1 (WV03).
22. Wiedervorlage: `docs/26-wiedervorlage.md` (backup before Art. 9, prices, codecs).
23. Das freigegebene Produktionsziel ist Ubuntu Server 24.04.4 LTS amd64 mit
    minimalem GNOME. Ältere Betriebssystemprofile sind historisch und nicht
    ausführbar.
24. MUST NOT löschen, neu partitionieren oder reinstallieren, bevor das Gate
    `G0-SRV-0` einen externen Backup- und Restore-Nachweis enthaelt.
25. ChatGPT/Codex auf M G1 läuft nur als unprivilegierter Entwicklungsnutzer
    mit Quellcode und synthetischen Daten. Kein Zugriff auf Art.-9-Daten,
    Produktionssecrets, Datenbank-Credentials oder produktive Objektpfade.
26. Kein öffentliches SSH, RDP, PostgreSQL, Redis/Valkey, Monitoring oder
    Alternativ-API. Administration nach dem Bootstrap nur ueber den
    freigegebenen Managementpfad/VPN; IPMI bleibt in einem getrennten
    Managementnetz.

## VRAM budget (gesetzt C03)

2 GB runtime · 16 GB jobs · 2 GB headroom. CopyGuard = 0 GB VRAM.

## Locked vs pending

- **Gesetzt:** D01–D08, D10, D12–D24. C01–C12. X-Katalog. K1–K5. H1–H3. Phase 1.
- **Empfohlen / Wiedervorlage:** D09 Preise, D11 Codecs
- **Gesperrt:** K6–K8, H5–H8, Video/WebRTC
- **Offen später:** WV01–WV06 (`docs/26-wiedervorlage.md`)

See `docs/20-freigabe.md` and `docs/10-decisions.md`.

## Phase-1-Schale (vorhanden; Produktarbeit pausiert)

Identity shell technically present. Auth ON. Database ON. Synthetic tenants only.
Further product work is paused until `G0-SRV-12` is documented as passed;
AUDIT-02 resumes only afterward. No fake GPU, no USB, no real clients.

## Read next

1. `docs/project-control/README.md`
2. `docs/STATUS.md`
3. `docs/superpowers/specs/2026-08-25-aurelia-ground-zero-server-design.md`
4. `docs/26-wiedervorlage.md`
5. `docs/20-freigabe.md`
6. `docs/10-decisions.md`
7. `docs/11-llm-handoff.md`

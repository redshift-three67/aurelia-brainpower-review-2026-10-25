# 05 — Ergänzende Innovationen (2026-08-25)

Alle Vorschläge sind **vorab gegen die Verfassung geprüft**: kein medizinischer Claim, kein Cloud-LLM für Akten, kein VRAM für CopyGuard, kein Video/WebUSB. Reihenfolge = empfohlene Priorität.

---

## IN-01: Kanon als ausführbarer Vertrag („Canon-as-Code") — *Priorität 1, sofort*
- **Idee:** Den bereits geplanten `canon-contract.mjs` erweitern: Der Validator prüft nicht nur Textregeln, sondern **Statuskonsistenz aller IDs** (D/C/X/U/K/H/O/WV) gegen `src/lib/concept/*` und gegen `docs/*.md` — bei jedem CI-Lauf.
- **Mehrwert:** Governance wird automatisch. Widersprüche (wie die früheren WebRTC-Reste) können nie wieder unbemerkt einziehen.
- **Aufwand:** 2–3 Tage (Plan existiert zu 80 %).
- **Verfassungskonform:** ✅ (rein lesend, kein Produktverhalten).

## IN-02: `kernel-manifest` Schema + Registry von Tag 1 an — *Priorität 2 (Phase 3)*
- **Idee:** JSON-Schema für Kernel-Manifeste (id, semver, sha256, input/output-schema, class, repro, budget, copy-Flächen) + CLI-Validator + Registry-Tabelle in Postgres. Der „Modulaufnahmevertrag" (Arbeitspaket F der Vorbereitungsspezifikation) wird so ausführbar statt handgehalten.
- **Mehrwert:** Phase-3-Gate („Schema + Hash") wird automatisiert testbar; `executable:false` ist ein Datenbankeintrag, kein Kommentar.

## IN-03: Deterministische Replay-Datenbank (Golden Files) — *Priorität 3 (Phase 3/4)*
- **Idee:** Für jeden Kernel einen Satz signierter Golden-Files (Input, Seed, erwarteter Output-Hash). CI führt CPU-Referenz gegen Golden-Files aus; CUDA-Ergebnisse müssen bitidentisch sein (bei `repro: strict`).
- **Mehrwert:** Beweist die Kernversprechen „strikte Reproduzierbarkeit" und „kein stiller Fake-Messwert" (D06/X20) bei jedem Build — nicht nur einmalig.

## IN-04: AVX-512-CPU-Pfad für kleine N (Haar/p-adisch) — *Priorität 4 (Phase 4)*
- **Idee:** Die laut 19-kozyrev.md ohnehin geplante Kleine-N-CPU-Filterbank als **Rust-Core mit runtime-detektierter AVX-512-VNNI/BF16-Dispatch** (verifiziert: CPU beherrscht avx512_vnni/vbmi2/bf16). Ersetzt teure GPU-Roundtrips für N ≤ 2048; GPU bleibt für Batches.
- **Mehrwert:** Deutlich höherer Analyse-Durchsatz ohne VRAM-Verbrauch; entlastet den Job-Pool; nutzt die Zen-5-Stärke des Servers gezielt.

## IN-05: Merkle-basierte Berechnungs-Audit-Spur im Passport — *Priorität 5 (Phase 6)*
- **Idee:** Computation Passport um Merkle-Root über (kernel_hash, input_hash, seed, Teilschritt-Digests, copyguard_digest) erweitern; Ed25519-signiert; QR im PDF-Report erlaubt Dritten die Verifikation **ohne** Klartext-Zeugen.
- **Mehrwert:** Nachvollziehbarkeit (Kern-Versprechen der Vision) wird kryptographisch, nicht rhetorisch. Schützt Betreiber gegen „Willkürwerte"-Vorwürfe.

## IN-06: GBNF-gebundener CopyGuard-LLM — *Priorität 6 (Phase 4)*
- **Idee:** Das RAM-LLM (Phi-4-mini/Gemma-3 Q4, llama.cpp) mit **GBNF-Grammatik** betreiben: Ausgabe strikt auf `{verdict, reason_code, cleaned_text}`-JSON beschränkt; verbotene Tokens auf Logit-Ebene maskiert.
- **Mehrwert:** Fail-Closed wird strukturell: Das Modell *kann* keine abweichende Form erzeugen. Kombiniert mit Lexikon-Stufe 1 entsteht ein zweischichtiges, deterministisches Kontrollsystem.

## IN-07: Offline-fähige Aktenvorbereitung (PGLite im Browser) — *Optional, Phase 6+*
- **Idee:** Service-Worker + `@electric-sql/pglite` (bereits im Stack!) für offline Zeugen-Vorbereitung; Sync ausschließlich nach Auth gegen M G1, konfliktfrei (Last-Writer-wins pro Feldgruppe, Konfliktliste für den Praktiker).
- **Mehrwert:** Praxisrealität (funkarme Räume) ohne Cloud-Umweg. **Achtung Verfassung:** Art.-9-Klartext im Browser nur nach Art.-9-Freigabe und mit Wisch-Konzept (15-live.md) — daher bewusst spät terminiert.

## IN-08: HRV-RR-Mathematikmodul (D21) als Kernel hinter der ABI — *Optional, Phase 5*
- **Idee:** Poincaré/SD1/SD2, p-adische Entropie, LF/HF-Power als reine Kennzahl-Kernel (`hrv.metrics.v1`), Quelle immer `derived`, CopyGuard auf allen Begleittexten.
- **Mehrwert:** Nutzt die bereits gesetzte D21-Entscheidung ohne neue Claim-Fläche; Kennzahlen sind Mathematik, keine Diagnostik.

---

## Abgelehnte „Innovationen" (bewusst NICHT vorgeschlagen)
Begründung jeweils Verfassung: Blockchain-Audit-Öffentlichkeit (Art. 9 vs. öffentliche Ketten), Cloud-Co-Pilot für Akten (D13), WebGPU-Compute im Client (Zeugenklartext im Browser ohne Nutzen), automatische „Wirkungs"-Statistiken (HWG-Risiko), 3-Tier-KI-Analyse (X05/K6 gesperrt).

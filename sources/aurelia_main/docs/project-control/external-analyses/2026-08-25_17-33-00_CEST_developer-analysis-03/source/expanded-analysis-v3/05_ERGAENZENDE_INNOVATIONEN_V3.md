# 05 — Ergänzende Innovationen V3 (verfassungsgeprüft, 2026-08-25 17:33 CEST)

Prüfkriterium je Vorschlag: kein medizinischer Claim, kein Cloud-LLM für Akten, kein VRAM für CopyGuard, kein Video/WebUSB, keine Umgehung von Sperren (X/K6–K8/H5–H8). Priorität = empfohlene Bau-Reihenfolge.

---

## IN-01: Canon-as-Code (Priorität 1 — sofort)
Den geplanten `canon-contract.mjs` zu einem vollständigen Status-Synchronizitäts-Prüfer ausbauen: alle IDs (D/C/X/U/K/H/O/WV) gegen `src/lib/concept/*` **und** `docs/*.md`; Lauf in CI. *Mehrwert:* Governance wird automatisch einklagbar; Widersprüche können nie wieder unbemerkt einziehen. *Aufwand:* 2–3 Tage (Plan existiert zu ~80 %).

## IN-02: `kernel-manifest` Schema + Registry (Priorität 2 — Phase 3)
JSON-Schema (id, semver, sha256, in/out-Schema, class, repro, budget, copy-Flächen) + CLI-Validator + Registry-Tabelle. Der Modulaufnahmevertrag (Arbeitspaket F) wird ausführbar; `executable:false` wird Datenbanzzustand statt Kommentar. *Aufwand:* 2–3 Tage.

## IN-03: Golden-File-Replay-Datenbank (Priorität 3 — Phase 3/4)
Pro Kernel signierte Referenzvektoren (Input/Seed/Output-Hash); CI läuft CPU-Referenz dagegen; `repro: strict`-CUDA muss bitidentisch sein. *Mehrwert:* Beweist D06/X20 („kein stiller Fake-Messwert") bei **jedem** Build. *Aufwand:* 2–3 Tage + Pflege.

## IN-04: Rust-Kern mit AVX-512-Dispatch für kleine N (Priorität 4 — Phase 4)
Haar/p-adische Filterbank für N ≤ 2048 auf der CPU, zur Laufzeit detektiert zwischen AVX2/AVX-512-VNNI/BF16 (CPU beherrscht es, verifiziert). GPU bleibt für Batches. *Mehrwert:* Hoher Analyse-Durchsatz ohne VRAM-Verbrauch; nutzt die Zen-5-Stärke genau dort, wo der Kanon sie vorsieht (19-kozyrev.md). *Aufwand:* 1–2 Wochen.

## IN-05: Merkle-Audit-Spur im Computation Passport (Priorität 5 — Phase 6)
Merkle-Root über (kernel_hash, input_hash, seed, Teilschritt-Digests, copyguard_digest), Ed25519-signiert; QR im PDF erlaubt Dritten Verifikation **ohne Klartext-Zeugen**. *Mehrwert:* Das Vision-Versprechen „Nachvollziehbarkeit durch Berechnungsausweis" wird kryptographisch statt rhetorisch. *Aufwand:* 3–4 Tage.

## IN-06: GBNF-gebundener CopyGuard (Priorität 6 — Phase 4)
RAM-LLM (llama.cpp, Phi-4-mini/Gemma-3 Q4) mit GBNF-Grammatik: Ausgabe strikt `{verdict, reason_code, cleaned_text}`; verbotene Token logit-maskiert. *Mehrwert:* Fail-closed wird strukturell (das Modell *kann* nicht abweichen). *Aufwand:* 2–3 Tage auf dem Lexikon aufbauend.

## IN-07: Offline-Aktenvorbereitung via PGLite-Service-Worker (Optional — Phase 6+)
`@electric-sql/pglite` (bereits im Stack) im Service Worker; Sync nur nach Auth gegen M G1; Konfliktliste statt silent merge. **Verfassungsvorbehalt:** nur nach Art.-9-Freigabe und mit Wisch-Konzept (15-live.md) — daher bewusst spät.

## IN-08: HRV-RR-Metriken als Kernel (Optional — Phase 5)
`hrv.metrics.v1` (Poincaré SD1/SD2, p-adische Entropie, LF/HF-Power) hinter der ABI; Quelle immer `derived`; CopyGuard auf Begleittexte. Nutzt D21 ohne neue Claim-Fläche.

---

## Bewusst abgelehnt (Verfassungs-Kollision)
Blockchain-öffentliche Audit-Ketten (Art. 9), Cloud-Co-Pilot für Akten (D13), WebGPU-Compute im Client (Zeugenklartext im Browser), „Wirkungsstatistiken" (HWG), 3-Tier-KI (X05/K6),automatische Kernel-„Optimierung" per LLM (verletzt `repro: strict`).

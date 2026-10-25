# RadiWorks VF-2: persönlicher Kontext und feste Auftragsbindung

> For agentic workers: execute sequentially with superpowers:executing-plans, TDD and an independent consequential-boundary review. No live migration.

**Goal:** Validated personal context for new local analyses; no alteration of original numerical algorithms or old sessions.
**Architecture:** New isolated candidate runtime/rw-vf2-20261004 copied from103 verified GV2 files. First bounded package VF2-A supplies strict context schema, stable server-owned identity and version, immutable detached snapshots on sessions/drafts/promoted queue; VF2-B supplies browser fields and safe local image handling. VF3 and EXP1 remain separate.
**Tech Stack:** Existing Python/FastAPI/Pydantic, stdlib validation, vanillaJS; no new analysis dependency.

## Approved baseline and boundaries
- Existing runtime/rw-gv2-20261004 and manual pilot8110 must remain byte-identical. Never touch real homes/keys, seven tasks or8103–8109.
- Name remains legacy file locator; personal identity fields never inferred from it. Optional image only validated reference metadata in VF2-A, not image upload/decoder support.
- Context is documentation/input for later explicit EXP1, never original seeded calculation.
- Old sessions remain unbound, not enriched retroactively. GV successors inherit their parent snapshot; genuinely new analyses take current case context.
- Auto/direct/image virtual broadcasts have no session-bound context unless separately implemented; no invented ownership.
- No full snapshot personal payload in queue/WS; expose only immutable reference digest and identity, resolve locally through source draft/session.

## VF2-A execution
- [x] Copy manifest and preserve parent hashes (tools/prepare_radiworks_vf2_candidate.py); already copied103files.
- [x] RED: engine/tests/test_personal_context.py asserts validation, Unicode/date normalization, input preservation, server identity/version, legacy read unchanged, alias immunity, tamper rejection, snapshots unchanged after metadata edit, same original analysis for same seed, inherited GV successors and promoted queue reference.
- [x] Implement engine/src/radiworks/core/personal_context.py: exact versioned schema, string/date limits and optional image reference (sha256/mediaType/byteLength), canonical digest and immutable serialized context/reference.
- [x] Integrate core/cases.py; routes.py metadata and session/draft linking; core/draft.py successors/promotion; core/broadcast.py immutable reference (not raw personal fields).
- [x] GREEN targeted suite then full engine regression; no weak fallback on malformed new context.
- [x] Independent Astra spec and correctness review; fix and rerun affected tests.
- [x] Record candidate manifest, parent equality, live listener read-only check, bounded checkpoint and status report. No migration/release claim.

## VF2-B — abgeschlossen im isolierten Kandidaten
Accessible explicit first/last name/date/place fields with legacy label/description retained, focus and optional locally decoded bounded image; UI validation/focus/error feedback and restart persistence. Browser probe uses synthetic cases and8111+ only. First VF2-A completion is not full VF2/UI completion.

## Final follow-up sequence
VF2-B → VF3 explained heuristic catalog suggestions → EXP1 pinned Radi144 heuristic separately selectable → remaining real trend/camera/recovery/Peggotty/Area regression → operator acceptance → canonical/template consolidation → Windows10 five-instance rc package and target validation → encrypted consistent completeF backup/isolated restore → Radi144. S4.8 remains closed.

## Verification commands
From candidate engine, set PYTHONPATH to candidate src and use C:/Users/Hubert111/Documents/Radiworks/radiworks_port/engine/.venv/Scripts/python.exe -m pytest tests/test_personal_context.py -q; capture expected RED assertion errors then GREEN. Full: same interpreter -m pytest tests -q --junitxml=../vf2-engine.xml with synthetic --basetemp under candidate/test-temp. Compare parent PRODUCT_MANIFEST SHA256 and record all7loopback listeners read-only. No remote/model product requests.


## Verifizierter VF2-A-Abschluss
468 Engine-PASS/3 Windows-Skips,37 neue Kontextfälle,22/22 Browserabschnitte; Astra-Befunde geschlossen.103 Elternhashes/23 Webappdateien unverändert.105 Kandidatendateien gepinnt. Backend abgeschlossen;VF2-B nun abgeschlossen,siehe aktuellenBericht. Einzelbelege und Grenzen: [VF2-A-Abschluss](RADIWORKS_VF2_A_ABSCHLUSS_2026-10-04.md).

## Aktueller Nachtrag
VF2-B abgeschlossen:109Produktdateien,494Engine-PASS/3Windows-Skips,28Browserabschnitte mitgeprüfterKandidatenbindung. Alter22erVF2-A-Browserlauf hatte falscheEnginebindung;keinBackendnachweis. [Aktueller Bericht](RADIWORKS_VF2_B_ABSCHLUSS_2026-10-04.md). VF3nächsterSchritt,keineLiveübernahme.

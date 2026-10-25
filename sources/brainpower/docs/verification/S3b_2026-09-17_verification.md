# S3b verification — 2026-09-17

Approved design: `../superpowers/specs/2026-09-17-dependent-change-design.md`.

Delivered: internal append-only journal and evidence integrity/reconstruction layer. No API writer, execution controller changes, model calls, live journal activation or original product writes. Legacy plan transitions and current execution restrictions remain unchanged.

## Evidence

- First journal test failed with ModuleNotFoundError before implementation (red).
- Initial ten journal tests passed after implementation.
- An additional mid-inspection head-change test failed because the head was not reread; implementation now rechecks the head after file observation. This test passes.
- Final scoped run: **87 tests, all passed**, 16.752 seconds. No skips. Full verbose log: `S3b_2026-09-17_unittest.log`.
- Modules: `test_change_journal` (16 new tests), `test_change_chain_preview`, `test_change_chain`, `test_technical_completion`, `test_pilot_apply`, `test_pilot_actions`.
- Operating contract JSON parsed successfully.

Journal tests cover two edges and reconstructed intermediate hash maps; historical validity versus current file/root/scope/adapter drift; disjoint scopes; latest-edge-first rollback and permanent no-reexecution after rollback; immutable tables; exact/conflicting retries; stale heads; two independent SQLite clients racing (one winner); insert abort preserving the previous journal head; interrupted/partial evidence; swapped step/source and third-edge rejection; sealed manifest and receipt binding errors; restart without replay; legacy non-import; tamper detection.

The compatibility test uses the actual existing staging, apply, post-apply verification, technical-completion and rollback implementations on temporary files. Its upstream successful test/review reports are fixtures, not live model results. The two-edge journal tests also use synthetic evidence snapshots and explicitly written temporary files. They do not demonstrate end-to-end dependent execution, which remains S3c.

## Boundaries

S3b validates internal archived snapshots; it does not independently authenticate the caller, current plan selection or provenance of supplied evidence. S3c must collect trusted fresh evidence, obtain separate operator decisions, check current allowlists/selection, reserve the shared worker, and guard rollback order before physical writes. `execution_authorized` is always false. `tip_current` means observed explicit file/root/scope/adapter consistency, not current test approval. Historical intermediate states retain hashes, not new executable instructions or automatic restoration data. Physical restore continues to require separately verified backups.

No whole-application suite, UI test or server deployment was performed for this isolated internal layer. No existing UI behavior changed; the running local service need not be restarted. Hash chains and repeated observations are not an atomic filesystem snapshot or protection against a hostile local database owner. No completeness claim for the whole Hermes app or five products.

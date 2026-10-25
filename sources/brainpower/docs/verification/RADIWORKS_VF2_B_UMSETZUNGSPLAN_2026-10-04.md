# RadiWorks VF2-B: persönliche Felder und lokales Fokusbild

> For agentic workers: execute sequentially with TDD, bounded Luna image helper and independent Astra boundary review. Approved continuation of VF2 design; no live migration.

Goal: Accessible personal fields and safely persisted optional local focus image, preserving original algorithms and VF2-A history.
Architecture: Isolated runtime/rw-vf2b-20261004 from105 verified VF2-A files. Cases UI sends bounded metadata with expected context version; images only on explicit save. Browser validates input headers/dimensions, decodes and reencodes bounded PNG without file name/metadata. New content-addressed per-scope PNG store validates CRC/IHDR/zlib/raster bounds before atomic writing; read returns no-store/nosniff. Historical snapshots keep image reference.
Tech: existing vanillaJS/CSS/Python stdlib/FastAPI; no new production decoder dependency.

- [x] RED engine tests: upload/validation, scope/path rejection, restart content equality, metadata/snapshot retention.
- [x] Root implement core/context_images.py and bounded POST/GET /context-images.
- [x] Luna owns only webapp/js/context-image.js and focus_image_browser.mjs; real synthetic decoder tests and cleanup.
- [x] RED browser flow against missing fields; add firstName,lastName,birthDate,place and optionalimage selection/removal.
- [x] Root owns index.html, cases.js, api.js, additive CSS; control names, helpful text and preserve form draft on failed save.
- [x] Save all context only by explicit click, disable conflicting controls while saving/preparing; no stale response applying to a switched case. expected_context_version accompanies updates. Old fields/history retained.
- [x] GREEN engine tests and full regression; original same seed unchanged. Browser valid/invalid/image removal/reload/case switch/serverrestart with synthetic data and 320px reflow.
- [x] Astra reviews scoped bytes/image/reference/privacy boundary. Correct concrete findings and rerun affected checks.
- [x] Verify pinned parents/live listeners read-only; freeze productmanifest, report, bounded localcheckpoint, update Wiedereinstieg. No F:-backup/templates/release.

Limits: image is optional and stored locally as a normalized PNG referenced by SHA256; no anonymous/medical/scientific meaning, no original numeric weighting. Private assets must accompany future real data backups; this bounded code checkpoint excludes runtime homes/images/keys. API raw-image length/dimension/type constraints cannot be bypassed via client. Original personal text retained server-side; CopyGuard projection placeholders must not be overwritten as originals. Existing scope remains single local operator; no Aurelia host authority assumed. VF3/EXP1/realcamera/longtrend/template/package/F:/S4.8 gates separate.


Abschluss: [VF2-B-Bericht](RADIWORKS_VF2_B_ABSCHLUSS_2026-10-04.md).494Engine-PASS/3Windows-Skips;28gebundeneBrowserabschnitte;2Race-Gegenproben;Bildformatprüfung/18JS-Syntaxchecks. KeineLiveübernahme. HistorischerVF2-A-Browserbeleg korrigiert.

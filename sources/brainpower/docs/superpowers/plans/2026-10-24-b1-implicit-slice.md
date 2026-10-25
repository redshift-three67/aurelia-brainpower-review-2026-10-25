# B1 implicit-slice admission implementation plan

> Execute sequentially with regression tests and independent Astra/medium review. No native action without a fresh concrete approval.

**Goal:** Correct the confirmed universal not-found assumption for own slices while rejecting configuration, identity, transient, pending-job and cgroup collisions.
**Architecture:** Additive isolated copy in `runtime/rw-b1-pristine-20261024`. Existing product, original frozen packets, job plan, unit names, one-shot claims, resource limits and native failure receipts remain unchanged. Service absence remains strict. Only a fully observed pristine inactive own slice can pass. No metadata observation grants execution authority.
**Tech stack:** Python standard library; existing hash-bound systemd v255 / IPv4 SSH bootstrap.

- [x] Preserve and hash-validate native unit-property evidence and all predecessor indices.
- [x] Clone only runtime sources and required JSON inputs; preserve copied-source hashes and original packet index.
- [x] RED: reproduce loaded/inactive no-fragment slice; require rejection of configured/transient/job/identity/partial/active/cgroup conflicts before any lifecycle action.
- [x] GREEN: exact slice field set and values, retain strict service and all existing protection/headroom/claim/cgroup/reserve gates; no production algorithm changes.
- [x] Generate four bounded reproducible scripts; run relevant full offline tests with process/network audit guard and source/hash validation.
- [x] Freeze review inputs; independent Astra/medium review of native evidence and correction. Repair concrete findings and rerun affected tests.
- [x] Verify actual bound loader offline, save final checkpoint and update current entry. Present exact once-only native preflight scope for approval. No start, archive-content read, extraction, build or paid scan.

**Limits:** Unit properties are sequential observations, not an atomic lease. Missing/invalid fields fail closed. Upstream v255 analysis is not a native binary attestation. Passing local tests does not prove the actual slice has no configured source; the new native preflight must establish that. Existing common.props capture lacks a hard raw-memory cap. A new worker start remains a separate gate.

**Completion:** Local preparation and independent review complete; native preflight not executed. New operator approval pending at NEXT_NATIVE_GATE.json. Frozen candidate index SHA256 `b4bf2db9d2093b4a59ca22fbcdd0a0f8bfeedad8a0c8eb63477333ac9b5f2da4`.

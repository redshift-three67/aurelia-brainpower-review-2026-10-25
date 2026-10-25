# Fixed own-unit metadata follow-up

**Goal:** Prepare one read-only native observation of the two exact B1 units after the earlier diagnostic pinpointed a property-dictionary mismatch at linux_job.py:108. Actual unit/field values remain unknown; no guard changes or native calls in this preparation.
**Architecture:** Additive runtime/rw-b1-unit-properties-20261024. Load exact frozen original bootstrap with its CLI disabled; never call its action/preflight/start/status. Under the existing directory lock, call unchanged remote_common.props at most twice, for rwb1archivev1.service (LoadState/ActiveState/MainPID) and rwb1archivev1.slice (LoadState/ActiveState). Export only fixed fields with presence/validity and allowlisted values, counts and exact expectation-comparison flags. Unknown fields/values never leave the server. Failed query remains explicit, no retry.

- [x] Bind original/diagnostic/execution evidence, preserving466 overlapping predecessor index references.
- [x] RED/GREEN pure normalization/filter/observation tests: missing PID distinct from zero, unexpected fields and invalid values sanitized, exact types, fixed order/queries, no authority or mutation.
- [x] Reproducible bounded server script and one-shot pinned IPv4 client, source/index/review binding, timeout/persistence/low-space/source-drift tests. 60sSSH observation budget for at most2x10sunit commands; no hard IO guarantee.
- [x] Full local verification and independent Astra/medium review. Freeze checkpoint and present exact new one-call gate; no execution without new approval.

**Limits:** Observations are sequential, not atomic, and describe the new probe time rather than automatically explaining the prior call. No full preflight or protection gate is rerun, no archive content/client data read, no own server files or units created/stopped, no product/config/ACL/budget/routing/algorithm changes or paid scan. Ordinary SSH/service logging and directory locking remain. Existing failed markers and reports are retained. A successful metadata delivery never supplies normal B1 admission.

**Lokaler Abschluss:**37Tests0Fehler/Failures/Skips,466Indexreferenzen unverändert,7kompilierteQuellen. Astra/medium-Review0materielleBefunde. RealePaketlader-/Reproduktionsprüfung offline erfolgreich; keine Profil-/Serveraktion dieses Pakets. NativeEinzelfreigabe offen.

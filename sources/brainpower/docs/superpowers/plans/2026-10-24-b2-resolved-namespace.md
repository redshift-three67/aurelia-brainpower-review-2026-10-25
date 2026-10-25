# B2 resolved namespace and metadata observer implementation plan

**Goal:** Prepare one coherent read-only proof observer; do not materialize or grant storage admission.
**Architecture:** Separate copy of accepted B2 lifecycle. Pure Linux-path namespace model accepts only the source-checked syscall-parent-safe subset; unresolved parent symlinks, unsupported operations, cycles and bounds produce explicit unknown/error, never invented closure. Ordered layers include removal, hardlinks without final dereference, direct metadata, parent paths and deferred full directory-time resolution. Aggregate event hash/counters only. Fixed read-only host/config/binary/own metadata observations are separate from effective future daemon state.
**Tech stack:** Python standard library, existing strict streaming TAR reader and resource/identity/persistence lifecycle. No host extraction or new production dependency.

- [x] Bind exact continuity RootPath and Linux metadata source; preserve all previous frozen packets.
- [x] RED adversarial pure-model tests: inherited redirect, relative/absolute/.., parent-symlink host-dependence rejection, hardlink-to-symlink, alias/self collision, subtree replacement, deferred directory touch, cycles, deadlines/limits. Implement pure model and source-checked validation.
- [x] RED fixed metadata observer tests: canonical/no-follow identity, byte caps, file changes, unsupported/missing/denied evidence explicit, no raw config/credentials, fixed path whitelist, numeric validation. Implement read-only collection.
- [x] Integrate streaming headers and one metadata collection into cloned lifecycle; new unit/slice/owned directory and plan/package. Preserve limits, locks, identity/protection, safe stop/finalization, no-replay. Generate bounded chunk-compressed worker embedding if needed to keep262144byte ceiling.
- [x] Full relevant suite, offline generated-source/transport validation, frozen hashes and independent Astra/medium review; correct findings before freezing.
- [x] Show exact proposed once-only preflight/start/bounded-status scope for fresh approval. No native/extraction/import/container/build/paidscan/resourcechange now.

**Admission remains separate:** Even successful supported namespace closure and metadata observations do not constitute a complete physical allocation bound. Effective future rootless options, FS/DB growth, transaction/temp coexistence and explicit proven reserves must be adjudicated from observations; unknown values remain unknown. No arbitrary metadata buffer as proof.

**Verified preparation24.10.2026:**207tests pass,0skip/process/network;718older references unchanged. Independent Astra/medium final review0materialblockers after22initial+18delta tests. Both nonblocking findings fixed test-first. Bound client offline validated.89filecheckpoint SHA2560fc9d63194c4cb74d5c55abdf0d697a9de664abc200e96de6745da690b9cc567; packageca0906d4d4b92892664128a6422d30b6a01d20dfebf9e2758285d078bfdedc04. Native authority remains false; next exact once-only scope in runtime/rw-b2-proof-runtime-20261024/NEXT_NATIVE_GATE.json requires fresh operator approval. No physical storage admission.

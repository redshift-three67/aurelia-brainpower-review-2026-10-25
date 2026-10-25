# Technical Production GO Review v5-2

## Findings

| Severity | Issue | Location |
|---|---|---|
| P1 | Harmonization authority is still not collision-safe tenant/operator scoped. `main._start_operation_owner()` uses raw delimiter concatenation for harmonization (`tenant:operator`), so `(tenant="a:b", operator="c")` and `(tenant="a", operator="b:c")` map to the same start-operation owner. The lower harmonization process authority also replays/starts with bare `operator_id`, omitting tenant scope entirely. This leaves RV4-02/RV4-04 only partially closed and allows cross-tenant idempotency/process-authority collisions or pending-claim hijack/DoS in shared runtime roots. | `apps/web/main.py:758-762`, `apps/web/main.py:794-798`, `services/harmonization_worker.py:1686-1708`, `apps/web/start_operations.py:134-141` |

## Details

### P1: Harmonization Start/Process Authority Omits Collision-Safe Tenant Scope

`_start_operation_owner("scan")` correctly uses `operator_owner_scope(context)`, but harmonization falls back to:

```python
return f"{context.tenant_id}:{context.operator_id}"
```

That reintroduces the delimiter-collision class the v5 plan explicitly closed for scan ownership. Because `StartOperationStore` hashes the supplied owner string, the two distinct tuples below collide to the same operation record/job authority when key/request match:

```text
tenant="a:b", operator="c"   -> "a:b:c"
tenant="a",   operator="b:c" -> "a:b:c"
```

The lower harmonization process authority has the same class of gap because `_reconcile_harmonization_start_locked()` calls the scan-process authority with only `operator_id`:

```python
expected_owner_id=operator_id
owner_id=operator_id
```

The persisted harmonization job record does perform exact `tenant_id`/`operator_id` checks, so some completed replay paths fail closed. The unresolved gap is still material: pending start-operation claims can be consumed by a colliding tuple, and the process-authority layer itself is not tenant-bound if the same `authority_job_id` is reached.

Suggested fix: use the same collision-safe owner scope for harmonization start operations and harmonization process authority that scan jobs use, then add regression coverage for `(tenant="a:b", operator="c")` versus `(tenant="a", operator="b:c")`, plus same-operator/different-tenant harmonization replay/start cases.

## Drift And Manifest Checks

Start hashes matched expected values:

| Item | SHA-256 |
|---|---|
| v5 manifest file | `919857a3e90c6106d839c99f1b74e5b48e804c808e1c92ccb6779e86f0cb4983` |
| v5 record | `703c60ddffc949b91f410e2c3db94a213e95fb9dea8c54e0a7edb640bc0d610f` |

Manifest validation at start and end:

| Check | Result |
|---|---:|
| Manifest lines | 113 |
| Final LF | yes |
| CR bytes | 0 |
| Syntax errors | 0 |
| Uppercase hashes | 0 |
| Duplicate paths | 0 |
| Ordinal-order mismatches | 0 |
| Missing files | 0 |
| Non-regular files | 0 |
| Reparse files | 0 |
| Entry hash mismatches | 0 |

Scope review:

| Scope Check | Result |
|---|---:|
| v4 manifest paths included | 90/90 |
| v4 freeze files included | yes |
| v5 remediation plan included | yes |
| Current modified/untracked source/test/static candidates under `apps/core/services/tools/tests` missing from v5 | 0 |
| Exclusions reviewed | reasonable |

End hashes matched the same values and all 113 entry hashes recomputed with zero drift.

## Verdict

```text
REQUEST CHANGES
start drift: 0
end drift: 0
P0: 0
P1: 1
P2: 0
P3: 0
```

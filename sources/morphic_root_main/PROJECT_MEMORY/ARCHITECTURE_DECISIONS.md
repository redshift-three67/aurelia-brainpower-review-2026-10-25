# Morphic V1 - Architecture Decisions Log
**Last Updated:** 2025-12-16 20:10 UTC+1  
**Purpose:** Record all major architectural decisions + rationale + implications

---

## DECISION 1: Core Algorithm Protection
**Date:** 2025-12-16  
**Category:** Data Integrity / Design  
**Status:** ✅ ACTIVE

### Decision
All core analysis and harmonization algorithms MUST NOT be changed except with explicit user approval.

### Protected Modules
- core/levels/level_resonance.py - 13-Ebenen-Resonanz calculation
- core/profiles/profile.py - Client profile encoding
- core/nls/ - NLS 3D mapping and scoring
- core/morphic_field/ - Morphic field coherence
- core/quantum_synergy/ - Remedy synergy engine
- core/harmonization/ - Report generation logic
- services/analysis_service.py - Main analysis engine
- providers/hardware/ - Entropy/H_level calculation

### Rationale
- These are the scientific foundation of morphic_v1
- Changes here directly impact analysis reliability
- Any modification requires validation + testing
- User is domain expert; AI should not auto-change

### Implications
- Refactoring limited to non-core helper functions
- Performance optimizations require testing
- New features must integrate without modifying core
- All changes go through explicit approval gate

### Risk Mitigation
- Standalone test (Run-MultiplexScan.ps1) validates unchanged behavior
- Git commits track all changes
- Rollback capability maintained
- User review before merging

---

## DECISION 2: Modularization Strategy
**Date:** 2025-12-16  
**Category:** Code Organization  
**Status:** ✅ IN PROGRESS

### Decision
Move non-essential CLI functions out of main.py while preserving core logic.

### Approach
1. ✅ Task 2B: analyze_remedy_synergies → synergy_helpers.py (DONE)
2. ✅ Task 2C: multiplex_scan → field.py (DONE)
3. Remaining: ~30 helper functions → organized helpers/ modules

### Result
- main.py: 9,543 → 3,220 lines (-66.2%)
- Improved code navigation
- Easier testing
- Clear command structure

### Implications
- Commands still work via field_app, synergy_app, etc.
- No API changes
- All algorithms preserved
- Cleaner architecture for RadionicsWebApp integration

---

## DECISION 3: Hybrid Database Strategy
**Date:** 2025-12-16  
**Category:** Infrastructure  
**Status:** 🔄 PENDING APPROVAL

### Decision
Keep SQLite for standalone mode. Introduce PostgreSQL only for RadionicsWebApp integration.
**Migration is OPTIONAL** - only if it doesn't destabilize core analysis.

### Strategy
```
DEVELOPMENT / STANDALONE:
└── SQLite (current, no changes)
    ├── resonance.db
    ├── descriptions.db
    ├── remedies.db
    └── item_descriptions.db

PRODUCTION (RadionicsWebApp):
└── PostgreSQL (only when needed)
    ├── Multi-tenant schema
    ├── DSGVO audit logging
    └── Shared with RadionicsWebApp
```

### Go/No-Go Criteria
- ✓ GO if: No destabilization of core algorithms
- ✓ GO if: Performance impact < 10%
- ✓ GO if: All tests pass
- ❌ NO-GO if: Core reliability affected
- ❌ NO-GO if: Significant performance degradation
- ❌ NO-GO if: Test failures

### Decision Gates
1. **Gate 1 (NOW):** Standalone test passes
2. **Gate 2 (Week 2):** Database abstraction layer designed
3. **Gate 3 (Week 3):** PostgreSQL schema tested in isolation
4. **Gate 4 (Week 4):** RadionicsWebApp integration planning

### Implications
- No forced migration of existing code
- Flexibility to abandon if problems arise
- Clear rollback points at each gate
- User approval required at each gate

---

## DECISION 4: Test-Driven Validation
**Date:** 2025-12-16  
**Category:** Quality Assurance  
**Status:** ✅ ACTIVE

### Decision
Before any major architectural change, run comprehensive standalone test.

### Test Plan
1. Phase 1: Import & CLI validation (5 min)
2. Phase 2: Database layer access (5 min)
3. Phase 3: Service layer test (5 min)
4. Phase 4: Field test command (10 min)
5. Phase 5: Multiplex scan (20 min)
6. Phase 6: Core algorithm integrity (10 min)

**Total Time:** ~60 minutes

### Success Criteria
- All CLI commands work
- Multiplex scan produces valid output
- Core algorithms unchanged
- Performance acceptable (< 10% degradation)

### Implications
- No architecture changes without passing tests
- Test results logged + documented
- Blockers identified early
- User can make informed decisions

---

## DECISION 5: Protocol & Documentation
**Date:** 2025-12-16  
**Category:** Process / Governance  
**Status:** ✅ ACTIVE

### Decision
All decisions, tests, issues, and resolutions are documented in PROJECT_MEMORY.

### Documentation Structure
```
PROJECT_MEMORY/
├── 00_CURRENT_STATE.md         # Current status
├── 02_CHANGES_LOG.md            # Commit log
├── ARCHITECTURE_DECISIONS.md    # This file
├── STANDALONE_TEST_PROTOCOL.md  # Test plan
├── STANDALONE_TEST_RESULTS.md   # Test results (to be filled)
├── ISSUES_AND_RESOLUTIONS.md    # Problem tracking
└── INTEGRATION_ANALYSE_20251216.md # Original analysis
```

### What Gets Logged
- ✅ All major decisions
- ✅ Decision rationale
- ✅ Implications & risks
- ✅ Approval status
- ✅ Test results
- ✅ Issues & fixes
- ✅ Rollback points

### Implications
- Full audit trail
- Traceability of changes
- Context preserved across sessions
- User can review history

---

## DECISION 6: Approval Gates
**Date:** 2025-12-16  
**Category:** Governance  
**Status:** ✅ ACTIVE

### Decision
All major changes require explicit user approval.

### Gate Levels
| Gate | Scope | Approval |
|------|-------|----------|
| 1 | Code refactoring (non-core) | Implicit (documented) |
| 2 | Core algorithm changes | Explicit (must ask) |
| 3 | Database schema migration | Explicit (must ask) |
| 4 | API/CLI changes | Implicit (backward compatible) |
| 5 | Dependency additions | Implicit (must document) |
| 6 | Test failures | Explicit (must diagnose) |

### Process
1. Identify if change requires approval
2. Document in PROJECT_MEMORY
3. Ask user for confirmation
4. Document decision & rationale
5. Execute with approval
6. Log results

### Implications
- User maintains control
- No surprise changes
- Clear decision trail
- Reversible changes

---

## DECISION 7: Failure Handling
**Date:** 2025-12-16  
**Category:** Risk Management  
**Status:** ✅ ACTIVE

### Decision
If standalone tests fail, STOP and diagnose before proceeding.

### Failure Protocol
1. Capture error output
2. Identify root cause
3. Check git history
4. Determine if rollback needed
5. Ask user for approval
6. Fix issue
7. Retest

### Implications
- No proceeding with known issues
- User informed at every step
- Rollback capability maintained
- System stability prioritized

---

## DECISION 8: Run-MultiplexScan.ps1 as Validation
**Date:** 2025-12-16  
**Category:** Testing / Validation  
**Status:** ✅ ACTIVE

### Decision
Use Run-MultiplexScan.ps1 (from original Windows setup) to test morphic_v1 standalone.

### Setup
1. Create isolated copy of morphic_v1
2. Run all test phases via PowerShell
3. Log all outputs
4. Validate against expected behavior
5. Document findings

### Why This Approach
- Same environment as production Windows setup
- Tests actual multiplex_scan functionality
- Validates all integrations
- Can be repeated anytime
- Low-risk validation

### Implications
- Standalone morphic_v1 can be certified "working"
- Safe to proceed with Docker/K8s setup
- Can generate baseline performance metrics
- Useful for future regressions

---

## APPROVAL SUMMARY

| Decision | User Approval | Status |
|----------|---------------|--------|
| 1. Core Algorithm Protection | ✅ Explicit | ACTIVE |
| 2. Modularization Strategy | ✅ Implicit | IN PROGRESS |
| 3. Hybrid Database Strategy | ⏳ Pending | PENDING TESTS |
| 4. Test-Driven Validation | ✅ Implicit | ACTIVE |
| 5. Protocol & Documentation | ✅ Explicit | ACTIVE |
| 6. Approval Gates | ✅ Explicit | ACTIVE |
| 7. Failure Handling | ✅ Implicit | ACTIVE |
| 8. Run-MultiplexScan.ps1 | ⏳ Explicit | PENDING |

---

## NEXT DECISION POINTS

### Decision 9 (After Standalone Test)
- ✓ If all tests pass: Proceed to Docker setup
- ✗ If tests fail: Fix issues, retest
- ? If partial failure: Identify & scope fix

### Decision 10 (Docker Phase)
- Create Dockerfile for morphic_v1
- Decide on base image (python:3.11-slim)
- Determine volume mounts for data/

### Decision 11 (K8s Phase)
- HAL integration approach
- Hardware detection per-node
- StatefulSet vs Deployment

### Decision 12 (RadionicsWebApp Integration)
- Database connection strategy
- Tenant isolation implementation
- Audit logging requirements

---


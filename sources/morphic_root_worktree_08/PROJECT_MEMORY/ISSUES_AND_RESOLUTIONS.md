# Morphic V1 - Issues & Resolutions Log
**Last Updated:** 2025-12-16 20:10 UTC+1  
**Purpose:** Track all issues found during refactoring + resolutions

---

## OPEN ISSUES (To Be Found During Standalone Test)

### Issue Category: Core Module Functionality
_Waiting for Run-MultiplexScan.ps1 standalone test results_

---

## RESOLVED ISSUES (Phase 3 Refactoring)

### Issue #3-001: Duplicate Functions in main.py
**Date:** 2025-12-16 06:16  
**Severity:** 🟡 MEDIUM  
**Status:** ✅ RESOLVED

**Problem:**
- `client_trends()` was in both main.py and trend.py
- `nls_3d_export()` was in both main.py and scan.py

**Impact:**
- Code duplication
- Maintenance confusion
- Unclear which version is used

**Resolution:**
- ✅ Removed duplicates from main.py
- ✅ Kept versions in respective command modules
- ✅ Updated imports to use modularized versions

**Commit:** 1bb0c6a (2025-12-16 00:45)

**Verification:**
```bash
grep -r "def client_trends" apps/cli/ core/ --include="*.py"
# Now should only appear in trend.py
```

---

### Issue #3-002: analyze_remedy_synergies Not Exported
**Date:** 2025-12-16 19:27  
**Severity:** 🟡 MEDIUM  
**Status:** ✅ RESOLVED

**Problem:**
- Created synergy_helpers.py with analyze_remedy_synergies
- Function wasn't exported from helpers/__init__.py
- main.py imports would fail

**Impact:**
- Import errors
- CLI commands using synergy would crash

**Resolution:**
- ✅ Added analyze_remedy_synergies to helpers/__init__.py
- ✅ Added to __all__ list
- ✅ Updated import in main.py
- ✅ Verified syntax with py_compile

**Commit:** 4fc9d9a (2025-12-16 19:28)

**Verification:**
```bash
python3 -c "from apps.cli.commands.helpers import analyze_remedy_synergies; print('✓')"
```

---

### Issue #3-003: _clamp Function Ambiguity
**Date:** 2025-12-16 19:50  
**Severity:** 🟡 MEDIUM  
**Status:** ✅ RESOLVED

**Problem:**
- multiplex_scan in field.py needed _clamp function
- _clamp defined in scan.py, not exported from main.py
- Creating circular import if importing from main.py

**Impact:**
- Import failed in field.py
- multiplex-scan command broken

**Resolution:**
- ✅ Import _clamp from apps.cli.commands.scan (where it's defined)
- ✅ Applied to both field_test and multiplex_scan
- ✅ Verified py_compile

**Commit:** 1715d2e (2025-12-16 19:52)

**Files Changed:**
- apps/cli/commands/field.py (lines 57, 794)

---

### Issue #3-004: Missing Imports in field.py for multiplex_scan
**Date:** 2025-12-16 19:48  
**Severity:** 🟡 MEDIUM  
**Status:** ✅ RESOLVED

**Problem:**
- multiplex_scan function added to field.py
- Many dependencies not imported at module level:
  - time, json, datetime
  - get_full_system_report
  - get_groups_for_profile
  - list_groups
  - NLS3D_POINTS, map_item_to_point
  - MorphicFieldConfig, calculate_morphic_field

**Impact:**
- Runtime errors when multiplex_scan called
- Missing core functionality

**Resolution:**
- ✅ Added all missing imports to top of field.py
- ✅ Organized imports by category
- ✅ Added Optional, Iterable to typing imports
- ✅ Verified syntax

**Commit:** 1715d2e (2025-12-16 19:52)

**Files Changed:**
- apps/cli/commands/field.py (lines 2-23)

---

### Issue #3-005: Multiplex Scan Dependencies in field.py
**Date:** 2025-12-16 19:49  
**Severity:** 🟡 MEDIUM  
**Status:** ✅ RESOLVED

**Problem:**
- multiplex_scan function uses internal helper functions
- These helpers also in main.py:
  - _interpret_level
  - _render_basic_html
  - _render_multiplex_txt
  - _compute_influence_multiplier_for_item
  - _build_influence_factors
  - etc.

**Impact:**
- Code duplication
- maintenance issue
- But necessary until helpers extracted

**Resolution:**
- ✅ Added local import of helpers in multiplex_scan function
- ✅ Imports from apps.cli.main (where helpers still live)
- ✅ Imports from apps.cli.commands.helpers (for analyze_remedy_synergies)
- ✅ Temporary solution until Phase 4 (helper extraction)

**Commit:** 1715d2e (2025-12-16 19:52)

**Temporary Nature:**
Phase 4 will extract remaining helpers to helper modules, eliminating duplication

**Files Changed:**
- apps/cli/commands/field.py (lines 794-804)

---

## KNOWN LIMITATIONS (Not Issues, But Design Constraints)

### Limitation #1: SQLite Not Multi-Tenant
**Status:** 🔵 ACKNOWLEDGED  
**Impact:** Requires PostgreSQL for RadionicsWebApp integration  
**Timeline:** Week 2-3 (optional)

### Limitation #2: Core Algorithms Protected
**Status:** 🟢 INTENTIONAL  
**Impact:** Refactoring limited to non-core functions  
**Benefit:** Preserves scientific integrity

### Limitation #3: No Docker Setup Yet
**Status:** 🔵 ACKNOWLEDGED  
**Impact:** Can't deploy to K8s yet  
**Timeline:** Week 2 (after standalone test)

### Limitation #4: No HAL Integration Yet
**Status:** 🔵 ACKNOWLEDGED  
**Impact:** Hardware detection per-node not available  
**Timeline:** Week 3-4 (K8s phase)

---

## ISSUE ESCALATION PROCESS

### If Issue Found During Standalone Test

**Step 1: Capture Error**
```powershell
# All logs saved to C:\temp\morphic_test_results\
$logFile = "$testDir\error_$(Get-Date -Format 'HHmmss').log"
$errorOutput | Tee-Object -FilePath $logFile
```

**Step 2: Diagnose**
```bash
# Check git history
git log --oneline -20

# Identify which commit introduced issue
git bisect start  # if needed

# Check affected module
grep -n "error message" apps/cli/*.py core/*.py
```

**Step 3: Escalate**
- Document in this file (ISSUES_AND_RESOLUTIONS.md)
- Mark severity: 🔴 CRITICAL / 🟠 HIGH / 🟡 MEDIUM / 🟢 LOW
- Ask user for approval to fix

**Step 4: Fix & Verify**
- Make minimal fix
- Re-run failing test
- Verify no new issues
- Commit with reference to issue

**Step 5: Document Resolution**
- Add to RESOLVED ISSUES section
- Mark status: ✅ RESOLVED
- Include commit hash

---

## SEVERITY LEVELS

🔴 **CRITICAL** - System cannot function
- Import errors
- Multiplex scan crashes
- Database access broken

🟠 **HIGH** - Significant functionality broken
- One command doesn't work
- Performance severely degraded

🟡 **MEDIUM** - Partial functionality broken
- One option doesn't work
- Code duplication
- Minor performance issue

🟢 **LOW** - Cosmetic or future concern
- Help text unclear
- Unused import
- Code cleanup needed

---

## RESOLUTION TEMPLATE (For Future Issues)

```markdown
### Issue #3-XXX: [Short Title]
**Date:** YYYY-MM-DD HH:MM  
**Severity:** 🔴 / 🟠 / 🟡 / 🟢  
**Status:** 🔄 OPEN / ✅ RESOLVED / ❌ WONT FIX

**Problem:**
[What went wrong?]

**Impact:**
[What breaks?]

**Root Cause:**
[Why did it happen?]

**Resolution:**
[What was done?]

**Verification:**
[How to confirm it's fixed?]

**Commit:** [Git hash or PR]
```

---


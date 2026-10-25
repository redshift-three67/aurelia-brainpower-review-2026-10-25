# Morphic V1 - Standalone Test Protocol
**Date:** 2025-12-16 20:10 UTC+1  
**Purpose:** Pre-migration validation of morphic_v1 functionality  
**Environment:** Windows PowerShell with Run-MultiplexScan.ps1  
**Policy:** Core algorithms PROTECTED - must not change

---

## TEST EXECUTION PLAN

### Prerequisites
- [ ] Copy morphic_v1 folder to isolated location (e.g., `morphic_v1_test`)
- [ ] Verify Python 3.11+ available
- [ ] Verify all dependencies installed (numpy, typer, sqlalchemy, etc.)
- [ ] Create log directory for test results

### Test Phase 1: Import & CLI Validation (5 min)

**Test 1.1: Core Module Imports**
```powershell
python -c "
from core.levels.level_resonance import calculate_level_resonance
from core.profiles.profile import ClientProfile
from core.morphic_field import MorphicFieldConfig
from core.nls.nls_db import NLS_DB
from services.analysis_service import AnalysisService
print('✓ All core modules import successfully')
" 2>&1 | Tee-Object -FilePath "$logDir\test_1_1_imports.log"
```
**Expected:** No errors  
**Pass/Fail:** ☐

**Test 1.2: CLI Help Commands**
```powershell
python -m apps.cli.main --help 2>&1 | Tee-Object -FilePath "$logDir\test_1_2_help.log"
python -m apps.cli.main field multiplex-scan --help 2>&1 | Tee-Object -FilePath "$logDir\test_1_2_multiplex_help.log"
```
**Expected:** Help text displayed, no errors  
**Pass/Fail:** ☐

### Test Phase 2: Database Layer Test (5 min)

**Test 2.1: Descriptions Database Access**
```powershell
python -c "
from core.db.descriptions_db import DescriptionsDB
db = DescriptionsDB()
items = db.get_all_items()
print(f'✓ Loaded {len(items)} items from descriptions.db')
if len(items) > 0:
    print(f'  Sample item: {items[0]}')
" 2>&1 | Tee-Object -FilePath "$logDir\test_2_1_descriptions_db.log"
```
**Expected:** Positive number of items, sample item printed  
**Pass/Fail:** ☐

**Test 2.2: NLS Database Access**
```powershell
python -c "
from core.nls.nls_db import NLS_DB
nls_db = NLS_DB()
points = nls_db.get_3d_points()
print(f'✓ Loaded {len(points)} NLS 3D points')
" 2>&1 | Tee-Object -FilePath "$logDir\test_2_2_nls_db.log"
```
**Expected:** Positive number of points  
**Pass/Fail:** ☐

### Test Phase 3: Service Layer Test (5 min)

**Test 3.1: Service Instantiation**
```powershell
python -c "
from services.analysis_service import AnalysisService
from services.subgroup_service import SubgroupService
from services.nls_service import NlsService
analysis = AnalysisService({})
subgroups = SubgroupService()
print('✓ All services instantiated successfully')
" 2>&1 | Tee-Object -FilePath "$logDir\test_3_1_services.log"
```
**Expected:** All services initialized without errors  
**Pass/Fail:** ☐

### Test Phase 4: Field Test Command (10 min)

**Test 4.1: Field Test Execution**
```powershell
$testDir = "C:\temp\morphic_test_results"
New-Item -ItemType Directory -Path $testDir -Force | Out-Null

python -m apps.cli.main field field-test `
  "Testmann" "Morphic" `
  --birth-date "01011990" `
  --birth-place "Berlin" `
  --p-emotion 0.6 `
  --p-physisch 0.7 `
  --p-mental 0.5 `
  --p-astral 0.4 `
  --top-k 5 `
  --export "$testDir\field_test_result.json" `
  2>&1 | Tee-Object -FilePath "$logDir\test_4_1_field_test.log"
```
**Expected:** JSON file created, no errors  
**Pass/Fail:** ☐

**Validation:**
```powershell
if (Test-Path "$testDir\field_test_result.json") {
    $json = Get-Content "$testDir\field_test_result.json" | ConvertFrom-Json
    Write-Host "✓ Valid JSON generated"
    Write-Host "  Top level keys: $($json.PSObject.Properties.Name -join ', ')"
} else {
    Write-Host "✗ JSON file not created"
}
```

### Test Phase 5: Multiplex Scan (High-Impact) (20 min)

**Test 5.1: Basic Multiplex Scan**
```powershell
python -m apps.cli.main field multiplex-scan `
  "Testmann" "Morphic" `
  --birth-date "01011990" `
  --birth-place "Berlin" `
  --profile "pathogen" `
  --top-k 10 `
  --seed "test-seed" `
  --export "$testDir\multiplex_pathogen.json" `
  2>&1 | Tee-Object -FilePath "$logDir\test_5_1_multiplex_basic.log"
```
**Expected:** JSON file created, valid structure  
**Pass/Fail:** ☐

**Test 5.2: Multiplex Scan with Advanced Options**
```powershell
python -m apps.cli.main field multiplex-scan `
  "Testmann" "Morphic" `
  --birth-date "01011990" `
  --birth-place "Berlin" `
  --profile "full" `
  --top-k 20 `
  --synergy `
  --morphic-field `
  --db-analysis `
  --influence-compare `
  --export "$testDir\multiplex_full.json" `
  --export-3d `
  2>&1 | Tee-Object -FilePath "$logDir\test_5_2_multiplex_advanced.log"
```
**Expected:** JSON + 3D export files, all analyses included  
**Pass/Fail:** ☐

**Test 5.3: Output Validation**
```powershell
foreach ($file in @("$testDir\multiplex_pathogen.json", "$testDir\multiplex_full.json")) {
    if (Test-Path $file) {
        $json = Get-Content $file | ConvertFrom-Json
        $size = (Get-Item $file).Length
        Write-Host "✓ $([System.IO.Path]::GetFileName($file)): $size bytes"
        Write-Host "  Sections: $($json.PSObject.Properties.Name -join ', ')" | Head -1
    }
}
```

### Test Phase 6: Core Algorithm Integrity (10 min)

**Test 6.1: Verify Resonance Calculation**
```powershell
python -c "
from core.levels.level_resonance import calculate_level_resonance
import numpy as np

# Test data
test_rates = np.array([0.5, 0.7])
result = calculate_level_resonance(test_rates)
print(f'✓ Resonance calculation works: {result}')
if isinstance(result, (float, int)):
    print('✓ Returns numeric value')
" 2>&1 | Tee-Object -FilePath "$logDir\test_6_1_resonance.log"
```
**Expected:** Numeric result returned  
**Pass/Fail:** ☐

**Test 6.2: Verify Profile Encoding**
```powershell
python -c "
from core.profiles.profile import ClientProfile, RateEncoder

profile = ClientProfile(
    name='Test',
    first_name='Client',
    birth_date='01011990',
    birth_place='Berlin',
    personal_profile={'emotion': 0.5, 'physisch': 0.6, 'mental': 0.7, 'astral': 0.4}
)
encoder = RateEncoder()
vector = encoder.personal_profile_to_vector(profile.personal_profile)
print(f'✓ Profile encoding works: vector shape {vector.shape}')
" 2>&1 | Tee-Object -FilePath "$logDir\test_6_2_profile.log"
```
**Expected:** Profile vector created successfully  
**Pass/Fail:** ☐

---

## RESULT COLLECTION

### Log File Locations
All test results saved to:
```
C:\temp\morphic_test_results\
├── test_1_1_imports.log
├── test_1_2_help.log
├── test_2_1_descriptions_db.log
├── test_2_2_nls_db.log
├── test_3_1_services.log
├── test_4_1_field_test.log
├── test_4_1_field_test.json  (output)
├── test_5_1_multiplex_basic.log
├── test_5_1_multiplex_pathogen.json  (output)
├── test_5_2_multiplex_advanced.log
├── test_5_2_multiplex_full.json  (output)
├── test_5_2_multiplex_3d.json  (output if generated)
├── test_6_1_resonance.log
└── test_6_2_profile.log
```

### Success Scoring
Count passed tests:
- 0/12 = ❌ FAIL - Stop, debug
- 1-6/12 = ⚠️ PARTIAL - Identify issues
- 7-11/12 = ✓ MOSTLY OK - Minor issues
- 12/12 = ✅ SUCCESS - Proceed to Phase 2

---

## ROLLBACK PLAN (If Tests Fail)

If any test fails:
1. Capture error output
2. Check recent changes (git log)
3. Identify which module causes failure
4. Roll back last commit if needed
5. Fix issue with user approval
6. Retest

```powershell
# Rollback to last known good commit
git log --oneline -10
git reset --hard <commit_hash>  # Only if user approves
```

---

## SIGN-OFF

- [ ] All tests executed
- [ ] Results logged
- [ ] Core algorithms verified unchanged
- [ ] User approval obtained
- [ ] Ready for Phase 2 (Docker setup)

---


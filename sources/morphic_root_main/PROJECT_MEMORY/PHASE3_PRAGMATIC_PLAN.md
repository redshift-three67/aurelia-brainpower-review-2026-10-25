# Phase 3 - Pragmatic Refactoring Plan
## Morphic Engine V1 - Realistic Approach (Based on Session 6 Learnings)

**Status:** Updated 2025-12-16 19:18 UTC+1  
**Original Plan:** Overly optimistic (28 helpers einzeln)  
**Realistic Plan:** Impact-focused (2 big commands first)

---

## 🎯 REVISED STRATEGY

### Why Automation Failed
```
❌ Attempted: Automated extraction of 28 helper functions
❌ Problem: Function interdependencies make regex/ast parsing error-prone
❌ Example:
   _build_db_analysis_summary() → calls _summarize_axis_items()
   _build_influence_factors() → calls _compute_influence_multiplier_for_item()
   
✅ Solution: Focus on high-impact commands with dependencies tracked manually
```

### New Approach: High-Impact First

Instead of:
```
28 small helpers → 2 commands → main.py cleanup
```

Do this:
```
2 BIG Commands (with dependencies) → Helpers (if needed) → main.py cleanup
```

**Result:**
- `multiplex_scan` (3403 Zeilen) = BIGGEST impact
- `analyze_remedy_synergies` (143 Zeilen) = NEXT impact
- Together: **3546 Zeilen** → main.py wird von 6762 → ~3200 Zeilen
- That's already **53% reduction**!

---

## 📋 REALISTIC WEEK 1 PLAN

### TASK 2B: analyze_remedy_synergies Migration (2-3 Stunden)

**File:** Zeile 442-584 in main.py  
**Size:** 143 Zeilen  
**Dependencies:** Minimal (built-in Python only)  
**Target:** `apps/cli/commands/synergy.py`

**Steps:**
1. Copy lines 442-584 von main.py
2. Create synergy.py mit funktion
3. Add to synergy_app command
4. Test: `python -m apps.cli.main synergy analyze-remedy --help`
5. Remove von main.py
6. Git commit

**ETA:** 45 Min

---

### TASK 2C: multiplex_scan Migration (4-6 Stunden)

**File:** Zeile 3361-6763 in main.py  
**Size:** 3403 Zeilen  
**Dependencies:** ~15 helper functions (will be moved with it or created as dependencies)  
**Target:** `apps/cli/commands/field.py` (oder split auf multiple files)

**Complexity:** 🔴 HOCH
- Viele interne Helfer referenziert
- Zyklische Dependencies möglich
- Extensive testing notwendig

**Strategie für multiplex_scan:**
```
1. Kopiere multiplex_scan + alle direkt-aufgerufenen Helfer zusammen
2. Erstelle "local_helpers" im field.py
3. Test incrementally (parts → whole)
4. Refactor zu helpers/ MODULE später
5. Remove von main.py
6. Git commit pro 500 Zeilen (für bisect safety)
```

**ETA:** 4-6 Stunden (+ testing)

---

## 📊 REALISTIC WEEK 1 RESULT

### Before
- main.py: 6762 Zeilen (100%)
- Commands: 2831 Zeilen (6 modules)

### After (End of Week 1)
- main.py: ~3200 Zeilen (-53%)
- Commands: ~5900 Zeilen (8 modules + synergy + field)
- Helper-Struktur: Aufgebaut für zukünftige Refactoring

### SUCCESS METRICS
```
✅ multiplex_scan funktioniert in field.py
✅ analyze_remedy_synergies funktioniert in synergy.py  
✅ Alle Tests bestehen
✅ CLI funktioniert komplett
✅ Git history ist sauber (pro-Command commits)
✅ main.py < 50% der Original-Größe
```

---

## 🛠️ IMPLEMENTATION (JETZT)

### Step 1: analyze_remedy_synergies (JETZT STARTEN)

```bash
# 1. Extract from main.py (Zeilen 442-584)
sed -n '442,584p' /opt/morphic_v1/apps/cli/main.py > /tmp/remedy_synergies_extracted.py

# 2. Review dependencies
grep -o '[a-z_][a-z0-9_]*(' /tmp/remedy_synergies_extracted.py | sort -u

# 3. Create synergy.py with function
# 4. Add to synergy_app (in commands/synergy.py)
# 5. Test
# 6. Remove from main.py
# 7. Git commit
```

### Step 2: multiplex_scan (NACH ANALYSE)
```
1. Analysiere multiplex_scan dependencies
2. Bestimme Migrationsgruppe (scan + helpers)
3. Erstelle field.py mit all
4. Test in parts
5. Integrate
6. Remove von main.py
7. Git commits pro 500 Zeilen
```

---

## ⚠️ KNOWLEDGE FOR RADIONICSWEBAPP

**Diese Lektion für übergeordnetes Projekt:**
1. **Pre-Migration Analysis:** Dependency graph BEFORE automation
2. **AST-Based Refactoring:** Nutze sichere Python AST-Parsing, nicht Regex
3. **Incremental Testing:** Test nach jeder 200-300 Zeilen
4. **Manual Review:** Für komplexe Monolithen immer manuell reviewen
5. **Fallback Plan:** Wenn Automation fehlschlägt → manueller Ansatz

---

## 📅 WEEK 1 TIMELINE

```
Mon 16 Dec:
  - Analysis & Planning ✅
  - Helper-Structure aufbauen ✅
  - 1-2 Stunden Arbeit

Tue 17 Dec:
  - analyze_remedy_synergies migrieren (3h)
  - Testing (1h)
  - GIT Commit

Wed 18 Dec:
  - multiplex_scan Analyse (2h)
  - multiplex_scan First Part (2h)
  - Testing (1h)

Thu 19 Dec:
  - multiplex_scan Rest (2h)
  - Helfer-Integration (1h)
  - Final Testing (1h)

Fri 20 Dec:
  - Main.py Cleanup (1h)
  - Final Validation (1h)
  - PROJECT_MEMORY Update (1h)
```

---

## 🎯 GO/NO-GO DECISION POINTS

### Per Command:
- [ ] Code extracted successfully
- [ ] Dependencies identified
- [ ] All imports work
- [ ] CLI tests pass
- [ ] Git commit clean

### End of Week:
- [ ] main.py < 50% original
- [ ] 2 large commands migrated
- [ ] Helper structure ready for next phase
- [ ] All tests pass
- [ ] Documentation updated

---

**Nächster Schritt:** Task 2B starten - analyze_remedy_synergies extraction  
**Protokollierung:** Nach jedem Commit updaten  
**Backup:** Before each major step!


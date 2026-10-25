# SESSION: Phase 3 Week 1 - Refactoring Continuation
## Morphic Engine V1 - Main.py Migration

**Datum:** 2025-12-16 19:12 UTC+1  
**Session Ziel:** Funktionen 6-15 migrieren (~2000 Zeilen)  
**Protokollierung:** Nach morphic_v1 PROJECT_MEMORY Standard

---

## 📊 ANALYSE-ERGEBNISSE

### Verbleibende Funktionen in main.py (31 Total)
```
✅ DONE (8 Funktionen):
   • groups_overview, hw_diagnostics, top3_scan
   • analyze_trends, client_trends
   • batch_scan, bat_area_scan, analyze

⏳ PENDING (23 Funktionen):
   ├─ PUBLIC COMMANDS (2):
   │  ├─ analyze_remedy_synergies (143 Zeilen) - PRIORITY 2
   │  └─ multiplex_scan (3403 Zeilen) - PRIORITY 3 (GROSSE AUFGABE!)
   │
   └─ HELPER FUNCTIONS (28):
      ├─ Database Helpers (7) - PRIORITY 1A
      ├─ Potency Helpers (5) - PRIORITY 1B
      ├─ Interpretation Helpers (2) - PRIORITY 1B
      ├─ Utility Helpers (8) - PRIORITY 1C
      ├─ Influence/Focus Helpers (3) - PRIORITY 1C
      └─ Harmonization Helpers (3) - PRIORITY 1C
```

### Umfang dieser Woche
```
HELPERS ONLY (kein multiplex_scan diese Woche!):
  • 28 Helper-Funktionen (~1120 Zeilen)
  • 6 neue Helper-Module in commands/helpers/
  • Strukturierte Migration mit Tests

DANN:
  • analyze_remedy_synergies (143 Zeilen)
  • main.py auf ~3500 Zeilen reduzieren
  → multiplex_scan bleibt für NÄCHSTE WOCHE
```

---

## 🎯 MIGRATION STRATEGIE (Week 1)

### PHASE 1: Helper-Modul Struktur aufbauen
**Dauer:** 30 Min

```
/opt/morphic_v1/apps/cli/commands/
└── helpers/
    ├── __init__.py
    ├── database_helpers.py      (7 Funktionen, ~280 Zeilen)
    ├── potency_helpers.py       (5 Funktionen, ~200 Zeilen)
    ├── interpretation_helpers.py (2 Funktionen, ~80 Zeilen)
    ├── utility_helpers.py       (8 Funktionen, ~320 Zeilen)
    ├── influence_helpers.py     (3 Funktionen, ~120 Zeilen)
    └── harmonization_helpers.py (3 Funktionen, ~120 Zeilen)
```

### PHASE 2: Helper-Funktionen migrieren
**Dauer:** 90 Min

Workflow pro Helper-Modul:
1. Zielmodule erstellen (mit Imports)
2. Funktionen kopieren (mit Dependecies)
3. Import-Statements überprüfen
4. Test: `python -c "from apps.cli.commands.helpers import ..."`

### PHASE 3: analyze_remedy_synergies migrieren
**Dauer:** 60 Min

1. Zu: `commands/synergy.py` (oder neues Modul)
2. Dependencies prüfen (nur built-in, keine main.py imports)
3. Test: `python -m pytest tests/test_synergy.py`

### PHASE 4: main.py bereinigen + Validierung
**Dauer:** 30 Min

1. Helfer + analyze_remedy_synergies aus main.py entfernen
2. CLI-Test: `python -m apps.cli.main --help`
3. Befehlstests: `python -m apps.cli.main scan --help`
4. Protokollierung: CHANGES_LOG updaten

---

## ✅ SUCCESS CRITERIA für diese Woche

- [ ] Alle 28 Helper-Funktionen in 6 Modulen
- [ ] analyze_remedy_synergies migriert & funktioniert
- [ ] main.py <3500 Zeilen (von 6762)
- [ ] Alle Befehle testen erfolgreich
- [ ] Git Commits mit aussagekräftigen Messages
- [ ] PROJECT_MEMORY aktualisiert

---

## 📝 GIT COMMIT PLAN

```bash
# Commit 1: Helper-Module Struktur
git commit -m "refactor: create helpers module structure (6 submodules)"

# Commits 2-7: Pro Helper-Modul
git commit -m "refactor: migrate database_helpers to helpers/database_helpers.py"
git commit -m "refactor: migrate potency_helpers to helpers/potency_helpers.py"
# ... etc

# Commit 8: analyze_remedy_synergies
git commit -m "refactor: migrate analyze_remedy_synergies to synergy.py"

# Commit 9: main.py cleanup
git commit -m "refactor: remove migrated helpers and commands from main.py"

# Commit 10: CHANGES_LOG + STATE
git commit -m "docs: update PROJECT_MEMORY for Phase 3 Week 1 completion"
```

---

## 📊 ESTIMATED TIMELINE

```
PHASE 1: Setup              30 Min ✓
PHASE 2: Helpers (6x)      90 Min (15 Min pro Modul)
PHASE 3: analyze_remedy    60 Min
PHASE 4: Cleanup + Tests   30 Min
─────────────────────────────────
TOTAL:                      210 Min (3.5 Stunden)

+ Puffer für Fehlerbehandlung: +30 Min
REALISTISCHE ETA: 4 Stunden
```

---

## 🚀 NÄCHSTER SCHRITT

**JETZT:** Phase 1 starten → Helper-Modul Struktur aufbauen

**Danach:** Phase 2-4 der Reihe nach durchführen

---

**Protokoll-Standard:** Nach morphic_v1 PROJECT_MEMORY System  
**Auto-Update:** Nach jedem Git Commit  
**Nächstes Update:** Nach Phase 1 Completion


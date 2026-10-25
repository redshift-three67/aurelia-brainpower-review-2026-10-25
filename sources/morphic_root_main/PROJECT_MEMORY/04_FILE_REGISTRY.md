# MORPHIC ENGINE V1 - DATEI-REGISTRY

**Zweck:** Überblick über alle wichtigen Dateien und deren Status  
**Auto-Update:** Nach strukturellen Änderungen  
**Letztes Update:** 2025-12-15 21:18

---

## STATISTIKEN

**Python Files:** ~150+ Dateien  
**Total Lines:** ~50.000+ Zeilen  
**Größte Datei:** apps/cli/main.py (9543 Zeilen, 378 KB)

---

## KERN-DATEIEN (KRITISCH)

### CLI Entry-Points
| Datei | Zeilen | Status | Priorität | Notizen |
|-------|--------|--------|-----------|---------|
| `apps/cli/main.py` | 9543 | 🔴 MONOLITH | P0 | Refactoring Phase 3 |
| `apps/cli/commands/scan.py` | ~500 | ✅ OK | P1 | Neu refactored |
| `apps/cli/commands/trend.py` | ~400 | ✅ OK | P1 | Neu refactored |
| `apps/cli/commands/harmonize.py` | ~350 | ✅ OK | P1 | Neu refactored |
| `apps/cli/commands/synergy.py` | ~600 | ✅ OK | P1 | Neu refactored |
| `apps/cli/commands/descriptions.py` | ~300 | ✅ OK | P1 | Neu refactored |

### Core Logic
| Datei | Zeilen | Status | Priorität | Notizen |
|-------|--------|--------|-----------|---------|
| `core/quantum_synergy.py` | ~800 | ✅ OK | P0 | Grover-Algorithmus |
| `core/morphic_field.py` | ~600 | ✅ OK | P0 | Copen-Raten |
| `core/levels/level_resonance.py` | ~400 | ✅ OK | P0 | 15-Ebenen-System |
| `core/profiles/profile.py` | ~500 | ✅ OK | P0 | Profil-Management |
| `core/nls3d_points_new.py` | ~1200 | ✅ OK | P1 | 3D Punkt-Mapping |
| `core/remedy_group_registry.py` | ~300 | ✅ OK | P1 | Gruppen-Registry |

### Hardware Integration
| Datei | Zeilen | Status | Priorität | Notizen |
|-------|--------|--------|-----------|---------|
| `config/hardware_profiles.py` | 584 | ✅ OK | P0 | DEV/PROD Profile |
| `config/detected_hardware.yaml` | 90 | ✅ OK | P1 | Auto-generiert |
| `providers/hardware/hardware_entropy.py` | ~400 | ✅ OK | P1 | Entropy-Provider |
| `providers/hardware/entropy_sources.py` | ~600 | ✅ OK | P1 | Quartz/Voltage/WS |
| `core/hardware/system_info.py` | ~200 | ⚠️ DUPLIKAT | P2 | → providers/ |

### LLM Integration
| Datei | Zeilen | Status | Priorität | Notizen |
|-------|--------|--------|-----------|---------|
| `core/llm/ollama_client.py` | 295 | ✅ OK | P1 | Ollama API |
| `core/item_description_generator.py` | ~400 | ✅ OK | P1 | LLM Wrapper |
| `tools/batch_descriptions.py` | ~300 | ✅ OK | P2 | Batch Processing |

### WebSocket & Streaming
| Datei | Zeilen | Status | Priorität | Notizen |
|-------|--------|--------|-----------|---------|
| `apps/server/websocket_server.py` | 351 | ✅ OK | P1 | WS Server |
| `core/realtime_streaming.py` | ~250 | ✅ OK | P1 | Stream Manager |
| `services/hardware_modulation.py` | ~500 | ✅ OK | P1 | Hardware WS Bridge |

### Datenbanken
| Datei | Zeilen | Status | Priorität | Notizen |
|-------|--------|--------|-----------|---------|
| `core/db/descriptions_db.py` | ~200 | ⚠️ FRAGMENT | P2 | Phase 5: Konsolidieren |
| `core/db/trend_db.py` | ~150 | ⚠️ FRAGMENT | P2 | Phase 5: Konsolidieren |
| `data/descriptions.db` | N/A | 💾 DB | P1 | SQLite |
| `data/trend.db` | N/A | 💾 DB | P1 | SQLite |

---

## KONFIGURATIONSDATEIEN

| Datei | Status | Priorität | Notizen |
|-------|--------|-----------|---------|
| `requirements.txt` | ✅ UPDATED | P0 | Phase 2: +9 Pakete |
| `pyproject.toml` | ⚠️ MINIMAL | P2 | Phase 6: Migration |
| `.gitignore` | ✅ OK | P1 | Backup-Filter aktiv |
| `config/paths.yaml` | ✅ OK | P1 | Produktions-Pfade |

---

## DOKUMENTATION

| Datei | Status | Priorität | Notizen |
|-------|--------|-----------|---------|
| `PROJECT_STATE.md` | ⚠️ ALT | P1 | → PROJECT_MEMORY/ |
| `MORPHIC_ENGINE_V1_ANALYSE.md` | ✅ OK | P0 | Ursprungsanalyse |
| `PROJECT_MEMORY/00_CURRENT_STATE.md` | ✅ NEU | P0 | Memory-System |
| `PROJECT_MEMORY/01_ARCHITECTURE.md` | ✅ NEU | P0 | Architektur-Docs |
| `PROJECT_MEMORY/02_CHANGES_LOG.md` | ✅ NEU | P0 | Änderungs-Log |
| `PROJECT_MEMORY/03_DECISIONS.md` | ✅ NEU | P0 | ADR-ähnlich |
| `README.md` | ⚠️ VERALTET | P2 | Phase 7: Update |

---

## TESTING

| Datei | Status | Priorität | Notizen |
|-------|--------|-----------|---------|
| `tests/test_*.py` | ⚠️ MINIMAL | P1 | Phase 4: Erweitern |
| `tests/exploratory/*.py` | ✅ OK | P2 | Experimentell |
| `pytest.ini` | ❌ FEHLT | P1 | Phase 4: Erstellen |
| `.coveragerc` | ❌ FEHLT | P2 | Phase 4: Coverage |

---

## SCRIPTS & TOOLS

| Datei | Status | Priorität | Notizen |
|-------|--------|-----------|---------|
| `CLEANUP_MASTER.ps1` | ✅ OK | P0 | Phase 1 ✅ |
| `cleanup_backups.ps1` | ✅ OK | P1 | Phase 1 ✅ |
| `cleanup_root.ps1` | ✅ OK | P1 | Phase 1 ✅ |
| `UPDATE_MEMORY.ps1` | ⏸️ PENDING | P0 | Phase 2 (TODO) |
| `tools/create_snapshot.py` | ⏸️ PENDING | P0 | Phase 2 (TODO) |
| `SERVER_INVENTORY_CHECKLIST.sh` | ✅ OK | P1 | Phase 8 (Linux) |

---

## EXPERIMENTELL / OPTIONAL

| Datei/Ordner | Status | Priorität | Notizen |
|--------------|--------|-----------|---------|
| `kozyrev-diodes-research/` | ⚠️ SEPARAT | P3 | Eigenes Projekt |
| `apps/viewer/z_anatomy_bridge.py` | ⚠️ EXPERIMENTAL | P3 | 3D Viewer |
| `core/viewer_3d.py` | ⚠️ EXPERIMENTAL | P3 | 3D Logik |

---

## ZU LÖSCHENDE DATEIEN (Phase 6)

| Datei | Grund | Phase |
|-------|-------|-------|
| `core/hardware/*.py` | Duplikat zu providers/hardware/ | 6 |
| `*.bak*` | Backups (bereits gelöscht ✅) | 1 ✅ |
| `*.shadow_*` | Backups (bereits gelöscht ✅) | 1 ✅ |
| `*.damaged_*` | Backups (bereits gelöscht ✅) | 1 ✅ |

---

## DEPLOYMENT-DATEIEN (Phase 8)

| Datei | Status | Priorität | Notizen |
|-------|--------|-----------|---------|
| `Dockerfile` | ❌ FEHLT | P0 | Phase 8 |
| `docker-compose.yml` | ❌ FEHLT | P0 | Phase 8 |
| `systemd/morphic-engine.service` | ❌ FEHLT | P0 | Phase 8 (Linux) |
| `.dockerignore` | ❌ FEHLT | P1 | Phase 8 |
| `scripts/deploy.sh` | ❌ FEHLT | P1 | Phase 8 |

---

## DATEI-STATUS-LEGENDE

- ✅ **OK:** Datei ist sauber und aktuell
- ⚠️ **PROBLEM:** Datei braucht Aufmerksamkeit (siehe Notizen)
- 🔴 **KRITISCH:** Blockiert weitere Entwicklung
- ❌ **FEHLT:** Datei sollte existieren, tut es aber nicht
- ⏸️ **PENDING:** In Arbeit / geplant
- 💾 **DB:** Datenbank-Datei (nicht editierbar)

## PRIORITÄTEN

- **P0:** Kritisch für Core-Funktionalität
- **P1:** Wichtig für Stabilität
- **P2:** Nice-to-have, nicht blockierend
- **P3:** Optional / Experimentell

---

**Nächstes Update:** Nach Phase 3 (main.py Refactoring)  
**Auto-Generierung geplant:** Phase 7 (File-Tracking-Script)

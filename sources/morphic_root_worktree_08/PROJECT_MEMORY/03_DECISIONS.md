# MORPHIC ENGINE V1 - ENTSCHEIDUNGEN

**Zweck:** Dokumentation aller wichtigen Architektur- und Design-Entscheidungen  
**Format:** ADR-ähnlich (Architecture Decision Record)

---

## ADR-001: Hybrid Memory-System (A+C+B)

**Datum:** 2025-12-15  
**Status:** ✅ Akzeptiert  
**Kontext:** Lange Refactoring-Sessions führen zu Context-Loss bei LLM

**Problem:**
- LLM Context-Limit bei großen Projekten
- Wissen geht bei Session-Wechsel verloren
- Keine Dokumentation von Entscheidungen

**Entscheidung:**
Hybrid-System aus:
- **A:** Strukturierte Markdown-Dateien (00_CURRENT_STATE.md, 01_ARCHITECTURE.md, etc.)
- **C:** Git Tags + Snapshots nach jeder Phase
- **B:** JSON Session-Logs (session_log.jsonl)

**Alternativen:**
1. Nur Git-basiert → zu wenig strukturierte Info
2. Nur Markdown → keine Automatisierung
3. Parallele LLM-Instanz → zu komplex für Start

**Konsequenzen:**
- ✅ Vollständige Projekt-Historie
- ✅ Context-Persistenz über Sessions
- ✅ Automatisierbar via UPDATE_MEMORY.ps1
- ⚠️ Manueller Overhead bei kleinen Änderungen

---

## ADR-002: requirements.txt statt pyproject.toml

**Datum:** 2025-12-15  
**Status:** ✅ Akzeptiert (vorerst)  
**Kontext:** Projekt nutzt requirements.txt, pyproject.toml existiert aber minimal

**Problem:**
- pyproject.toml ist moderner Standard (PEP 621)
- requirements.txt ist Legacy, aber weit verbreitet
- Beide Dateien existieren, inkonsistent

**Entscheidung:**
Phase 2 nutzt `requirements.txt`, Migration zu `pyproject.toml` in Phase 6

**Begründung:**
- Bestehende Struktur nicht sofort brechen
- requirements.txt funktioniert für Deployment
- pyproject.toml Migration braucht Testing (Poetry/PDM/Hatch?)

**Konsequenzen:**
- ✅ Schnelle Phase 2 Abschluss
- ⚠️ Technische Schuld bleibt vorerst

---

## ADR-003: cupy-cuda12x nur PROD, nicht DEV

**Datum:** 2025-12-15  
**Status:** ✅ Akzeptiert  
**Kontext:** cupy benötigt CUDA + NVIDIA GPU

**Problem:**
- DEV: AMD iGPU (keine CUDA-Unterstützung)
- PROD: NVIDIA RTX 4000 SFF Ada (CUDA 12.x)
- cupy Installation schlägt auf DEV fehl

**Entscheidung:**
```python
# requirements.txt
# cupy-cuda12x>=12.0  # Commented, uncomment on PROD
```

**Alternativen:**
1. requirements-dev.txt vs requirements-prod.txt
2. Optional dependencies: `pip install .[cuda]`
3. Runtime-Check und graceful fallback

**Gewählt:** Option 1 (einfachste Lösung für Phase 2)

**Konsequenzen:**
- ✅ DEV-Installation funktioniert
- ✅ PROD aktiviert manuell via uncomment
- ⚠️ Deployment-Dokumentation notwendig

---

## ADR-004: Ollama via requests, kein pip package

**Datum:** 2025-12-15  
**Status:** ✅ Akzeptiert  
**Kontext:** Code nutzt `ollama`, aber keine pip-Installation nötig

**Problem:**
- `ollama` Python-Package existiert (von Ollama Inc.)
- Code nutzt aber nur REST API via `requests`
- Kein `import ollama` gefunden (nur requests)

**Entscheidung:**
Kein `ollama` Package in requirements.txt

**Begründung:**
```python
# core/llm/ollama_client.py
import requests  # ✅ Bereits in requirements.txt
response = requests.post(f"{base_url}/api/generate", ...)
```

**Konsequenzen:**
- ✅ Kleinere Dependencies
- ✅ Funktioniert mit jedem Ollama-kompatiblen Endpoint

---

## ADR-005: pytest-asyncio für WebSocket Tests

**Datum:** 2025-12-15  
**Status:** ✅ Akzeptiert  
**Kontext:** WebSocket-Server nutzt asyncio

**Problem:**
- `apps/server/websocket_server.py` nutzt async/await
- Standard pytest kann async nicht testen
- Tests würden ohne pytest-asyncio fehlschlagen

**Entscheidung:**
```python
# requirements.txt
pytest>=7.4
pytest-asyncio>=0.21
```

**Alternativen:**
1. asyncio.run() manuell in Tests
2. pytest-trio (anderes async Framework)
3. Keine async Tests (⛔ schlecht)

**Konsequenzen:**
- ✅ Async Tests möglich
- ✅ Clean Test-Syntax mit @pytest.mark.asyncio

---

## ADR-006: Phase 1 vor Server-Deployment

**Datum:** 2025-12-15  
**Status:** ✅ Akzeptiert  
**Kontext:** Frage: Lokal cleanen oder Server analysieren zuerst?

**Problem:**
- Server (PROD) wartet auf Deployment
- Lokaler Code (DEV) hat 189 Backups + Monolith
- Deployment von "schmutzigem" Code riskant

**Entscheidung:**
**Hybrid-Strategie:** Lokal cleanen → dann Server deployen

**Begründung:**
- 189 Backups nicht auf Server deployen
- main.py Refactoring lokal testen
- Sauberer Code = einfacheres PROD Debugging

**Phasen-Reihenfolge:**
1. Phase 1-3: Lokal (Cleanup, Dependencies, Refactoring)
2. Phase 4: Tests (mit PROD-Hardware-Mocks)
3. Phase 5-6: DB + Module (lokal)
4. Phase 7: Monitoring (lokal + PROD)
5. Phase 8: Server-Deployment (Docker + systemd)

**Konsequenzen:**
- ✅ Saubere Codebase für PROD
- ⏱️ Server-Deployment verzögert (~4 Wochen)

---

## Offene Entscheidungen (TBD)

### TBD-001: main.py Refactoring-Strategie
**Phase:** 3  
**Frage:** Big-Bang vs Inkrementell?  
**Optionen:**
- A: Alles auf einmal refactoren (2 Wochen)
- B: Befehl für Befehl migrieren (4 Wochen, safer)

### TBD-002: Datenbank-Konsolidierung
**Phase:** 5  
**Frage:** 4 DBs → 1 DB oder 1 DB pro Domain?  
**Optionen:**
- A: 1 monolithische DB (einfacher)
- B: 1 DB mit Schemas (cleaner)
- C: Separate DBs beibehalten (Status Quo)

### TBD-003: Docker vs Bare-Metal
**Phase:** 8  
**Frage:** PROD Deployment als Docker oder direkt?  
**Optionen:**
- A: Docker + NVIDIA Container Runtime
- B: Bare-Metal systemd Service
- C: Hybrid (Docker für Isolation, systemd für Autostart)

---

**Nächstes Update:** Nach Phase 3 Start

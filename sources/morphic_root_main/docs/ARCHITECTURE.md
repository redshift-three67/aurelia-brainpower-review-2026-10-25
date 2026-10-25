# Morphic Engine V1 – Architekturüberblick

## Leitprinzipien
- **Layered/Hexagonal Design:** saubere Trennung zwischen Domain-Core, Services, Adaptern.
- **Provider-Plugins:** Hardware-, Daten- und Quantum-Adapter registrieren sich dynamisch und sind hot-swappable.
- **Realtime & Streaming:** jede Pipeline ist async-fähig und kann kontinuierliche Sensor-Events verarbeiten.
- **Deterministische Protokollierung:** jede Berechnung ist reproduzierbar (Seed-Management, Audit-Trail).

## Verzeichnisstruktur
```
apps/
  cli/          # Typer-CLI, orchestriert Analysen & Sessions
  api/          # FastAPI (REST/WebSocket) für Live-Dashboards
  ui/           # optionale GUI/Frontend-Adaptionen
core/
  profiles/     # Profile, RateEncoder, ImageSignatures
  resonance/    # MorphicFieldResonator, Potency Heuristics
  harmonization/# Inversion, adaptive loops, holographische Optimierung
  subgroups/    # Kandidatengeneratoren, Multiplex/Hadamard, Balanced Top-K
  nls/          # DB-Lader, Scorer, Parameter-Tuning
  sessions/     # Zeitbasiertes Harmonizing, RL/Quantum Hooks
  utils/        # Numerik, Formatierer, seeding helpers
providers/
  hardware/     # QRNG, HID, CPU, Biofeedback-Sensoren
  data/         # JSON/Procedural/ML-Quellen, Schemen, Validatoren
  quantum/      # QAOA/VQE-Clients, Random-Walk-Optimierer
services/
  analysis_service.py
  subgroup_service.py
  nls_service.py
  harmonization_service.py
  session_service.py
infra/
  config/       # Pydantic Settings, Secrets
  logging/telemetry/
  persistence/  # History Store, Graph DB Connector
  orchestration/# Queue/Scheduler/Worker-Flows
```

## Datenfluss (High-Level)
1. `apps` nehmen Requests entgegen, validieren Input und rufen Services auf.
2. Services orchestrieren Core-Engines und fordern benötigte Provider an (Dependency Injection).
3. Provider liefern Messwerte (h-Level, Biofeedback, DB-Items) oder schreiben Ergebnisse (History, Telemetrie).
4. Ergebnisse werden standardisiert an `apps` zurückgegeben (DTOs/Response-Objekte).

## Roadmap (Initial)
1. **Core Profiles & Resonance** portieren, inklusive GPU/NumPy-Abstraktion.
2. **Hardware Provider Interface** entkoppeln (EntropyProvider, SensorTelemetry).
3. **Services** für Analyse + Subgruppen erstellen, CLI-Entry bereitstellen.
4. **Infra**: Settings, Logging, Speicherpfade + Tests.

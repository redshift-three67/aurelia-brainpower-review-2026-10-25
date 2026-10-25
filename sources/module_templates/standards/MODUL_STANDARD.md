# MODUL_STANDARD — die verbindliche „Linie" für alle RadiX-Module

> Abgeleitet aus: Aurelia `docs/06-kernel-abi.md` (ABI), `AGENTS.project.md` (Hard Rules),
> `docs/08-ui-a11y.md` (UI), `docs/02-architecture.md` (FastAPI als geplante API-Schicht).
> Gültig für: RadiWorks, Radi144, RadiMorphic, RadiBlohm, RadiThoms, RadiCopen.

**Ist-Abgleich 30.09.2026:** Diese Vorlage beschreibt das gemeinsame Ziel, keine automatische Ist-Konformität. RadiWorks meldet lokal `id=radiworks.engine`, `version=0.2.0` und getrennt `abi_version=v1`; [lokale Vertragsabweichungen](RADIOWORKS_LOCAL_PROFILE_V1_1_DRAFT.md) und Host-Gates sind dokumentiert. Die unten genannten Designfarben sind ein älterer Basissatz; Brainpower `docs/AURELIA_DESIGN_TEMPLATE.md` fordert vor einer plattformweiten Übernahme den D0/D1-Abgleich mit der Hermes-/Governor-Gestaltung und getrennte Modulakzente.

## 1. Zweiteiliges Modulmodell

Jedes Modul besteht aus genau zwei Artefakten:

```
<modul-name>/
├── engine/          ← Python (FastAPI): Fachlogik, implementiert den API_CONTRACT + Kernel-ABI v1
└── webapp/          ← HTML-Applikation: eigenständige UI, spricht ausschließlich den API_CONTRACT
```

- **engine/** = Port der jeweiligen Kernfunktionalität (bei RadiWorks: AetherOnePi-Engine aus `Documents\Radiworks`).
- **webapp/** = die „exakte HTML-Applikation" — ersetzt die alte Desktop-/Bundle-Frontend-Welt (bei RadiWorks: Processing-GUI + Angular + Vue → **eine** App).
- Die webapp enthält **keine Fachlogik**; alle Berechnungen laufen in der Engine (Single Source of Truth, testbar, ABI-fähig).

## 2. Engine-Standard (Python)

| Aspekt | Vorgabe |
|---|---|
| Framework | FastAPI + Uvicorn (entspricht Aurelias geplanter API-Schicht, `docs/02-architecture.md:41`) |
| Python | ≥ 3.12, `pyproject.toml`, kein System-Gedöns, venv-basiert |
| Live-Kanal | WebSocket (`/ws`) — Pflicht laut `AGENTS.project.md:65` |
| Zufall/Entropie | zentrale Provider-Abstraktion `EntropyProvider` (fail-closed-Fallback-Kette, seedbar für `repro: seeded`) |
| Persistenz | JSON-Dateien (Contract-Format) Phase 1; PostgreSQL-Schema mit `tenant_id` erst bei Aurelia-Integration |
| Manifest | `GET /manifest` liefert das Kernel-ABI-v1-Objekt (id, version, hash, schemas, class, repro, budget, entry) |
| Tests | pytest; Algorithmen mit fixiertem Seed deterministisch testbar |
| Verbot | keine Anlehnung an `/opt/radiquant4` (TABU, `AGENTS.project.md:40`); keine versteckten Netzaufrufe (`docs/06-kernel-abi.md`) |

## 3. Webapp-Standard (HTML)

| Aspekt | Vorgabe |
|---|---|
| Basis | Vanilla HTML/JS (ES-Module) oder Vite-Build — **keine** Framework-Abhängigkeit, die Aurelia excluded |
| Sprache | Deutsch (Aurelia: „deutsche UI") |
| Barrierefreiheit | WCAG 2.2 AA: Tastaturbedienung, 44-px-Ziele, Skip-Link, `prefers-reduced-motion` |
| Design | Aurelia-Tokens: Pergament `#F3EFE6`, Tinte `#1C241E`, Sage `#2C4A3E`; kein Lila, kein Gold-Glow, kein Neon, keine Emoji-Icons |
| CopyGuard | Jeder sichtbare Satz läuft durch CopyGuard (keine Diagnose-/Therapie-/Heilungsformulierungen) — `AGENTS.project.md:52` |
| Konfiguration | API-Basis-URL via `window.__MODULE_CONFIG__.apiBase` oder `?api=`-Parameter — **nie hardcoden** (Fehler des AetherOnePi-Vue-Frontends) |
| Einbettung | App läuft solo (Prototyp) UND ist als `<iframe>`/`<embed>` in Aurelias Preview-Host integrierbar (`preview-host-bridge.tsx` existiert dort bereits) |

## 4. Einheitliche Modulstruktur (Vorlage)

```
<modul-name>/
├── engine/
│   ├── pyproject.toml
│   ├── src/<modul>/main.py           # FastAPI-App-Factory: create_app()
│   ├── src/<modul>/api/routes.py     # API_CONTRACT-Endpunkte
│   ├── src/<modul>/core/             # Fachlogik (Port)
│   ├── src/<modul>/entropy.py        # EntropyProvider-Kette
│   ├── src/<modul>/manifest.py       # Kernel-ABI-v1-Objekt
│   ├── data/                         # Raten-DBs, Korpora (bei RadiWorks: 1008 Clarke-JSONs + radionics-rates)
│   └── tests/
└── webapp/
    ├── index.html
    ├── css/tokens.css                # Aurelia-Design-Tokens
    ├── js/                           # ES-Module, API-Client, Views
    └── README.md
```

## 5. Namens- und ID-Konventionen

- Modul-ID und Version sind getrennte Manifestfelder: lokal `radiworks.engine` / `0.2.0`; die REST-ABI-Version steht getrennt in `abi_version=v1`. Kennungen anderer Module werden erst aus deren belegtem Manifest übernommen.
- Kernel-Klasse: `cpu` (alle sechs initially; `cuda`/`quantum` nur mit Budget-Nachweis)
- Reproducibility: `seeded` als Ziel (EntropyProvider mit Seed-Modus), `stochastic` nur wenn unvermeidbar
- Git: jedes Modulprojekt = eigenes Repo (nie im Home-Dir-Repo mischen)

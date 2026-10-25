# Initial Project Status

Observed: 2026-09-11T13:32:05+02:00
Scope: live Git state and local Hermes state only. `NO_GIT` means that no Git metadata existed at the inspected directory.

| Project | Location | Git branch / revision | Working state | Governor action |
|---|---|---|---|---|
| Radiworks | `C:/Users/Hubert111/Documents/Radiworks` | `backup/radiworks_final_polish` / `866f5214` | Modified: `radiworks_port/webapp/js/views/analyze.js`, `radiworks_port/webapp/js/views/cases.js`; untracked: `radiworks_port/engine/tests/test_webapp_active_case_persistence.py`, `radiworks_port/engine/tests/test_webapp_database_persistence.py` | Preserve WIP; require scope-specific review before any mutation. |
| Biomedis Field Resonance Lab | `C:/Users/Hubert111/Documents/Biomedis/field_resonance_lab` | `wellenreiter` / `da90a93` | Clean according to `git status --short --branch`. | Read-only status/port-preflight goal only until an explicit task is approved. |
| Morphic Engine 2 | `D:/RadiMorphic_V2/Morphic_Engine_2` | `wellenreiter` / `787078d` | Clean according to `git status --short --branch`. | Preserve current branch; use its own gated workflow for changes. |
| Headless Platform CMS | `C:/Projekte/Headless_Platform_CMS` | `main...origin/main` / `2d23356` | Extensive tracked and untracked multi-domain refactor WIP; includes `.audit-temp/`, `data/`, `docker/`, `docs/`, `migrations/`, new site/form/runtime paths, and many modified source/config files. | Do not reformat, stage, or mix unrelated fixes; status/reporting goals must remain read-only. |
| Hermes Agent | `C:/Users/Hubert111/AppData/Local/hermes/hermes-agent` | `main...origin/main [behind 345]` / `167448edca` | Clean according to `git status --short --branch`; CLI reported an update available. | Do not update as part of Governors initialization; review release notes and compatibility separately. |

## Shared orchestration facts

- Hermes profile inventory: only `default` is available.
- Hermes gateway: stopped.
- Governors Kanban board: created as `governors`; its default workspace is this directory.
- No status goal has been dispatched during initialization.
- The initial Vault had six Hermes-oriented notes in `project_memories/`, while Radiworks had two distinct source memory notes; neither set was overwritten.

## Verification source commands

```powershell
# Run individually before acting on a project.
git -C C:/Users/Hubert111/Documents/Radiworks status --short --branch
git -C C:/Users/Hubert111/Documents/Biomedis/field_resonance_lab status --short --branch
git -C D:/RadiMorphic_V2/Morphic_Engine_2 status --short --branch
git -C C:/Projekte/Headless_Platform_CMS status --short --branch
git -C C:/Users/Hubert111/AppData/Local/hermes/hermes-agent status --short --branch
hermes profile list
hermes gateway status
hermes kanban boards list
```

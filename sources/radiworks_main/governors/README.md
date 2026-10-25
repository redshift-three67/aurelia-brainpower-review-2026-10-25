# Governors Central

Cross-project governance workspace for five locally discovered projects. It is documentation and routing only: it must not mutate a governed repository unless a dispatched goal explicitly authorizes that scope.

## Managed projects

1. Radiworks — `C:/Users/Hubert111/Documents/Radiworks`
2. Biomedis Field Resonance Lab — `C:/Users/Hubert111/Documents/Biomedis/field_resonance_lab`
3. Morphic Engine 2 — `D:/RadiMorphic_V2/Morphic_Engine_2`
4. Headless Platform CMS — `C:/Projekte/Headless_Platform_CMS`
5. Hermes Agent — `C:/Users/Hubert111/AppData/Local/hermes/hermes-agent`

The initial evidence snapshot is in [PROJECT_STATUS.md](PROJECT_STATUS.md). The Obsidian mirror is `C:/Users/Hubert111/Documents/Hermes-Obsidian-Vault/Governors/`.

## Hermes routing

- Kanban board: `governors`
- Board database: `C:/Users/Hubert111/AppData/Local/hermes/kanban/boards/governors/kanban.db`
- Available execution profile at initialization: `default`
- Gateway state at initialization: stopped

`goals.json` holds one explicit, read-only goal template per project. `scripts/Dispatch-GovernorGoals.ps1` validates the local Hermes profile and produces a dry run by default. With `-Apply`, it creates idempotent `--goal` Kanban cards on the `governors` board. Hermes Kanban goal mode is the durable equivalent of a `/goal` loop; it retains acceptance criteria and blocks for review instead of silently ending when its turn budget is exhausted.

## Safe use

```powershell
Set-Location C:\Users\Hubert111\Documents\Radiworks\governors
.\scripts\Dispatch-GovernorGoals.ps1
.\scripts\Dispatch-GovernorGoals.ps1 -Apply
hermes kanban --board governors list
```

Do not start the gateway merely to route these local cards. Starting a gateway is a separate operational decision.

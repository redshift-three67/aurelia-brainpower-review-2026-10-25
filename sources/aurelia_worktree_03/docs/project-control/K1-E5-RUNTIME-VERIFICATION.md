# K1 E5 – lokale Runtime-Evidenz

```yaml
recorded_at: 2026-09-08T10:49:13+02:00
worktree: .worktrees/aurelia-konsolidierung
branch: codex/aurelia-konsolidierung
observed_head: 1185a68ed984b525686764f995513355701929e3
runtime_authority: explicitly_granted_by_operator
listener: 127.0.0.1:8080 only
child_environment: minimal allowlist plus ephemeral instance identifier
migration_script_executed: false
server_mutation: false
publication_mutation: false
```

## Ergebnis

`npm run check:auth` wurde nach separater Betreiberfreigabe ausgeführt und
lieferte:

```json
{"status":"match","devAuthEnabled":true,"buildAuthEnabled":true}
```

Der Prüfer startete ausschließlich sein eigenes lokales Wrapper-/Vite-Kind auf
`127.0.0.1:8080`, bestätigte die flüchtige Instanzkennung am dev-only
`/__app-env`-Endpunkt, verlangte Auth-on für Dev und Build und wartete auf die
Beendigung seines eigenen Kindes. Es wurde kein fremder Prozess adressiert.

Die Kindumgebung war auf Betriebssystempfad-/Temp-Variablen und eine nicht-
`VITE_`-Instanzkennung begrenzt; `DATABASE_URL`, Auth-Overrides und geerbte
Produktions-Credentials wurden nicht weitergereicht. Der reguläre Build und
`scripts/migrate.mjs` wurden nicht ausgeführt. Die vereinbarte potenzielle
in-memory-PGLite-Wirkung des lokalen Dev-Starts war zugelassen; es wurde keine
persistente Datenbank-, Server- oder Publikationsmutation beobachtet.

| Prüfung | Ergebnis |
|---|---|
| E5 fokussierte Unit-/Invarianten-Tests | PASS: 22 Tests |
| `npm run check:auth` | PASS |
| `npm test` | PASS: 334 Tests, 332 PASS, 2 begründete Capability-Skips |
| `npm run lint` | PASS |
| `npm run typecheck` | PASS |
| `npm run check:canon` | PASS |
| `npm run check:k1-control` | PASS |
| `git diff --check` | PASS |

Dieser Nachweis ist auf den lokalen Windows-Worktree begrenzt. Er ist keine
Linux-, Produktions-, Mandantenisolations-, Server- oder Publikationsabnahme.

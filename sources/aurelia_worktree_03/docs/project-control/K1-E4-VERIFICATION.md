# K1 E4 – lokale Toolchain-Evidenz

```yaml
recorded_at: 2026-09-08T08:46:36+02:00
worktree: .worktrees/aurelia-konsolidierung
branch: codex/aurelia-konsolidierung
observed_head: 1185a68ed984b525686764f995513355701929e3
platform: Windows 10 x64
runtime: Node.js 22
build_command: npm run build:dev
regular_build_executed: false
migration_script_executed: false
server_mutation: false
publication_mutation: false
verification_result: indeterminate
verification_reason: Linux toolchain evidence remains outstanding
```

## Autorisierter lokaler Windows-Nachweis

Der Betreiber hat den begrenzten Synthesebuild ausdrücklich freigegeben. Er lief
unter `env -i` mit ausschließlich `PATH`, `HOME`, `USERPROFILE`, `TMP` und
`TEMP`; `DATABASE_URL` und die geerbten Produktions-Credential-Variablen wurden
nicht an npm, den Wrapper oder Vite übergeben. Der reguläre Befehl `npm run build`
und damit `scripts/migrate.mjs` wurden nicht ausgeführt.

| Prüfung | Ergebnis |
|---|---|
| `node --test scripts/with-app-env.test.mjs` | PASS: 16 Tests |
| gezieltes ESLint für Wrapper und Tests | PASS |
| `npm run check:k1-control` | PASS |
| `npm test` | PASS |
| `npm run check:canon` | PASS |
| `npm run typecheck` | PASS |
| `git diff --check` | PASS |
| `env -i … npm run build:dev` | PASS: Vite-Client, SSR und Nitro/Vercel-Ausgabe erstellt |

Der Wrapper löst `vite` jetzt aus dessen Paketmetadaten auf, startet den
installierten JavaScript-CLI-Einstieg mit `process.execPath` und setzt `shell: false`
explizit. Fehlende oder ungültige CLI-Metadaten verhindern den Spawn fail-closed.

## Wirkung und Grenzen

- `build:dev` erzeugte ignorierte lokale `.vercel/output`-Artefakte. Die
  Buildausgabe markierte außerdem `src/routeTree.gen.ts` ohne semantischen Diff
  als Arbeitsbaumänderung; nach ausdrücklicher Betreiberentscheidung wurde
  **nur diese** erzeugte Änderung auf `HEAD` zurückgesetzt.
- Die Buildausgabe enthielt keinen Aufruf von `scripts/migrate.mjs` und keinen
  sichtbaren Datenbank- oder Netzwerkzugriff. Dies ist keine beweisbare
  Netzsperre: Die hier genutzte lokale Umgebung erzwingt keine technische
  Egress-Blockade.
- Der Nachweis gilt nur für Windows. CLI-Auflösung, Signalweitergabe und
  `build:dev` unter Linux sind offen; deshalb ist der Gesamtstatus bewusst
  `indeterminate`, nicht PASS.
- Kein Schluss auf Produktionsreife, Serverabnahme, Plattformassets oder
  Publikationsfreigabe ist zulässig.

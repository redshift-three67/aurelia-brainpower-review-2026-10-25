# K1 E2/E3 – lokale Testevidenz

```yaml
recorded_at: 2026-09-08T08:25:21+02:00
worktree: .worktrees/aurelia-konsolidierung
branch: codex/aurelia-konsolidierung
observed_head: 1185a68ed984b525686764f995513355701929e3
scope:
  - E2 fail-closed Test-Runner
  - E3 Auth-on-, Migrations-, PWA-Fixture- und Symlink-Testverträge
server_mutation: false
publication_mutation: false
migration_executed: false
production_build_executed: false
```

## Ergebnis

Die fokussierten E2- und E3-Verträge sowie die vollständige lokale Testsuite
sind am oben gebundenen Snapshot grün. Die Tests haben ausschließlich temporäre
Fixture-Verzeichnisse unter dem Betriebssystem-Tempverzeichnis angelegt und
automatisch bereinigt. Es wurden keine Plattformassets erzeugt, keine Migration
ausgeführt und keine Server- oder Publikationsaktion vorgenommen.

| Prüfung | Ergebnis |
|---|---|
| `node --test scripts/test-runner.test.mjs` | PASS: 15 Tests, 14 PASS, 1 begründeter EPERM-Symlink-Capability-Skip |
| `npx eslint scripts/test-runner.mjs scripts/test-runner.test.mjs` | PASS |
| `npm run check:canon` | PASS |
| `npm run check:k1-control` | PASS |
| `npm run typecheck` | PASS |
| `git diff --check` | PASS |
| `node --test scripts/with-app-env.test.mjs scripts/check-auth-invariant.test.mjs scripts/migration-plan.test.mjs scripts/grok-pwa-plugin.test.mjs` | PASS: 77 Tests |
| `npm test` vor E3 | FAIL: 319 Tests, 302 PASS, 15 erwartungs- bzw. assetgekoppelte Altverträge; Ursache E3/E7, kein Runnerfehler |
| `npm test` nach E3 | PASS: 319 Tests, 317 PASS, 2 begründete Symlink-Capability-Skips |

## Geprüfte Vertragsgrenzen

- Fehlende App-Environment-Datei erzeugt keinen Auth-off-Override; Auth bleibt
  ohne explizite Einstellung an.
- Die Root-Migrationsdiscovery enthält `0001_auth.sql` und `0002_tenants.sql`;
  die Auth-Schema-Kopie bleibt byteidentisch zur Quelle.
- PWA-Unit-Tests verwenden einen temporären, leeren Workspace statt realer
  `public/__grok`-Assets. Das ist **kein** Nachweis, dass verwaltete
  Plattformassets verfügbar sind; deren reales Gate bleibt E7.
- Nur `EPERM` oder `EACCES` erlauben einen Symlink-Capability-Skip. Andere
  Link-, Pfad- oder CLI-Fehler bleiben fail-closed.
- Der Test-Runner entdeckt alle MJS-Tests unter `scripts` sowie ausschließlich
  die zwei festen TypeScript-Pflichttests; leere Gruppen, direkte Links und
  verlinkte TS-Vorfahren verhindern den Spawn.

## Dirty-Datei-Hashes für E2/E3

```text
package.json                                      54f18ea804c96b8349845f52c1c5c51a1a81939e7eba486953a08926fda3dfc8
scripts/test-runner.mjs                           b29d883b992193c9974839960a4ecf43a4f1fd6a73bf413d10b79c5d3633bb88
scripts/test-runner.test.mjs                      44a4a940951be6efb42ec6fece7f3c86c9895bc809de988721f4f95c86d52c64
scripts/with-app-env.test.mjs                     0b0e20443ef088ac51f2e9ffbbbfd3d7c48ffbb3d334aae5c82f4fbbefc6a91c
scripts/check-auth-invariant.test.mjs             75cf9cf3708a6d2ba9c44491e8701f8561badd2ced190db7b02ffb1a43724856
scripts/migration-plan.test.mjs                   075f1edc553be56d5578e51bb5a91ef0b28ae2057b833fd10a187da9404f5909
scripts/grok-pwa-plugin.test.mjs                  9727b73137f25e6cd3be41394d876a3124b89ff941daaabc1601a3ee5fb8e8ae
scripts/test-support/symlink-capability.mjs       47dbcff63c8a2a54cdc0e95cdf8c00a06f9822efbeaa89f4716872e4cf7e08d2
```

Diese Evidenz belegt einen lokalen, synthetischen K1-Testscope. Sie ist weder
eine Produktions-, Plattformasset-, Server-, Sicherheitsabnahme noch eine
Publikations- oder Commitfreigabe.

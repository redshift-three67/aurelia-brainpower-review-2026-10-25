# K1 E5 – isolierte TDD-Evidenz

```yaml
recorded_at: 2026-09-08T09:23:32+02:00
worktree: .worktrees/aurelia-konsolidierung
branch: codex/aurelia-konsolidierung
observed_head: 1185a68ed984b525686764f995513355701929e3
runtime_check_auth_executed: false
vite_dev_started: false
migration_executed: false
server_mutation: false
publication_mutation: false
verification_result: indeterminate
verification_reason: real E5 runtime scope remains explicitly ungranted
```

## Isolierter TDD-Nachweis

| Prüfung | Ergebnis |
|---|---|
| `node --test scripts/check-auth-with-dev-server.test.mjs scripts/check-auth-invariant.test.mjs` | PASS: 21 Tests |
| gezieltes ESLint für E5-Quell- und Testdateien | PASS |
| `npm test` | PASS: 333 Tests, 331 PASS, 2 begründete Capability-Skips |
| `npm run check:canon` | PASS |
| `npm run check:k1-control` | PASS |
| `npm run typecheck` | PASS |
| `git diff --check` | PASS |

Die E5-Tests verwenden ausschließlich Fake-Spawn, Fake-Fetch, Fake-Child und
einen simulierten Dev-Endpunkt. Sie starten weder einen Vite-Prozess noch einen
Listener und führen keine Migration aus.

## Belegte Verträge

- Nur die vier benannten Optionen werden akzeptiert; unbekannte Optionen starten
  keinen Prozess.
- Ein Kind wird ausschließlich über `process.execPath`, den lokalen Wrapper,
  `vite dev`, `127.0.0.1` und einen expliziten Port gestartet; `shell: false`.
- Die zufällige Kennung bleibt nicht-`VITE_`, nur im Child-Environment und im
  Speicher der Prüfroutine. Ohne exakte Endpunktattestierung ist Erfolg unmöglich.
- Dev und Build müssen beide Auth-on sein. Auth-off-Gleichheit ist kein Erfolg.
- Früher Child-Exit, fremde oder fehlende Attestierung, Timeout, synchroner und
  asynchroner Spawnfehler sowie nicht bestätigtes Cleanup sind fail-closed.
- Der Endpunkt `/__app-env` bleibt dev-only und fügt die Kennung nur ein, wenn
  sie beim Plugin ausdrücklich vorhanden ist.

## Offene Runtime-Grenze

`package.json` und der bestehende `check:auth`-Befehl wurden bewusst nicht auf
den neuen Realprozess-Check umgestellt. Ein echter Vite-Dev-Start kann den
PGLite-Bootstrap und lokale Migrationen auslösen. Ohne gesonderte Entscheidung
zu zulässiger in-memory-Migrationswirkung, minimalem Child-Environment und
Datei-/Netzwerkmatrix bleibt der Runtime-Lauf ausgeschlossen. Dieses Dokument
belegt daher nur die TDD-Implementierung, keine echte Auth-Instanz, keine
Produktionsauthentisierung und keine Mandantenisolation.

# K1 E1 – Status- und Steuerungsvertrag

```yaml
package: E1
recorded_at: 2026-09-07T16:18:21+02:00
worktree: .worktrees/aurelia-konsolidierung
branch: codex/aurelia-konsolidierung
observed_head: 1185a68ed984b525686764f995513355701929e3
implementation_authority: Betreiberanweisung im Entwicklungsgespräch vom 2026-09-07
commit_authority: separate Betreiberentscheidung je vollständig abgenommenem Paket
publication_authority: false
server_authority: false
```

## Ziel

Die aktuelle operative K1-Lage wird getrennt von historischen Snapshots geführt.
`K1-CURRENT.json` ist die maschinenlesbare Quelle für den gegenwärtig beobachteten
lokalen Arbeitsstand. `K1-STATUS.md` bleibt unveränderter historischer
Pre-Sync-Nachweis mit einer klaren Verweisgrenze. Weder ein lokaler Commit noch
ein Testerfolg erzeugt eine Publikations-, Server- oder Produktionsfreigabe.

## Zulässiger Scope

- Neue aktuelle Statusquelle: `docs/project-control/K1-CURRENT.json`.
- Dieser Vertrag, der Project-Control-Einstieg und die historische
  `K1-STATUS.md`-Einordnung.
- Fail-closed-Prüfung und Tests in `scripts/check-project-control-k1.mjs` und
  `scripts/check-project-control-k1.test.mjs`.
- Die vorhandenen Task-7-Dateien sowie die Änderung an `package.json` werden
  ausschließlich inventarisiert; sie werden in E1 nicht ersetzt oder formatiert.

## Nichtziele und Grenzen

- Kein Reset, Clean, Checkout zum Verwerfen, Merge, Rebase, Push, PR,
  Credentialwechsel, Serverzugriff, Datenbankmigration oder Produktionsbuild.
- `G0-SRV-0` bleibt unverändert und allein durch
  `ground-zero/GATE-STATUS.md` autorisiert.
- Die aktuelle Quelle behauptet keinen frisch ausgeführten Test. Ihr
  Ausgangszustand ist `implementation: in_progress`,
  `verification.result: not_run` und `verification.freshness: unknown`.
- Der reguläre Befehl `npm run build` bleibt ausgeschlossen, da er `db:migrate`
  verkettet.

## Schema- und Fail-closed-Regeln

`K1-CURRENT.json` enthält genau die versionierte operative Struktur: Arbeitsstrom,
Task, beobachteten Branch/HEAD, vollständige Dirty-Pfade, Implementierungsstatus,
Prüfergebnis/Aktualität/Evidenz, Gate-Referenz und getrennte
Implementierungs-/Commit-/Publikationsreferenzen.

Der Kontrollvalidator muss mit Exit 1 scheitern bei fehlenden Pflichtfeldern,
unbekannten Feldern oder Werten, inkonsistentem Prüfergebnis, einer PASS-Aussage
ohne Evidenz oder bei einer nicht in der Quelle erfassten Dirty-Datei. Ein
unbestimmbarer Git- oder Dateizustand bleibt Exit 2. Die Statusquelle darf keinen
eigenen Dateihash verlangen; das wäre selbstreferenziell.

## Abnahme

1. Die fokussierten Negativtests laufen grün.
2. Der reale `check:k1-control`-Lauf akzeptiert nur die frische, vollständige
   aktuelle Inventur.
3. Historische und aktuelle Aussagen sind voneinander verlinkt, aber nicht
   überschrieben.
4. Anschließend erfolgt ein begrenztes Spec-Review und erst nach PASS ein
   separates Quality-/Security-Review. Vor einem lokalen Commit wird der
   vollständige Diff dem Betreiber vorgelegt.

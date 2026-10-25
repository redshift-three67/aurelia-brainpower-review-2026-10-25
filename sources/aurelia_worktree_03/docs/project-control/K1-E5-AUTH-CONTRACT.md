# K1 E5 – lokaler Auth-Instanz-Prüfvertrag

```yaml
package: E5
recorded_at: 2026-09-08T08:55:00+02:00
worktree: .worktrees/aurelia-konsolidierung
branch: codex/aurelia-konsolidierung
observed_head: 1185a68ed984b525686764f995513355701929e3
implementation_authority: Betreiberanweisung zur vollständigen lokalen Review-Umsetzung sowie bestätigte E5-Empfehlung
runtime_authority: not_granted
commit_authority: separate Betreiberentscheidung je vollständig abgenommenem Paket
publication_authority: false
server_authority: false
```

## Ziel

`check:auth` soll ausschließlich eine selbst gestartete lokale Vite-Dev-Instanz
als Prüfziel akzeptieren. Erfolg verlangt eine passende flüchtige Instanzkennung,
Auth-on im Dev-Prozess, Auth-on in der Build-Auflösung und bestätigtes Aufräumen
des eigenen Kindes. Eine Antwort eines fremden Prozesses auf demselben Port darf
niemals Erfolg bedeuten.

## Zulässiger TDD-Scope

- Neu: `scripts/check-auth-with-dev-server.mjs` und dessen Testdatei.
- Anpassung: `scripts/app-env-plugin.mjs` nur für den Dev-only-Attestierungswert.
- Anpassung: `package.json` nur zur lokalen Check-Verkettung.

Die Testausführung verwendet ausschließlich Fake-Spawn, Fake-Fetch und Fake-
Child-Prozesse. Sie startet keinen Vite-Prozess, keinen Listener und führt keine
Migration aus.

## Vertragsregeln

- Öffentliche Optionen sind ausschließlich `spawnImpl`, `fetchImpl`, `timeoutMs`
  und `port`; unbekannte Optionen werden abgelehnt.
- Der Prüfer erzeugt die Kennung kryptographisch zufällig und hält sie nur im
  Arbeitsspeicher. Sie ist keine Berechtigung, kein Secret und kein dauerhafter
  Identifier.
- Das Kind erhält die Kennung ausschließlich als nicht-`VITE_`-Environmentwert.
  Sie erscheint nicht in CLI-Argumenten, Dateien, Logs oder Rückgabewerten.
- Der vorhandene Dev-only-Endpunkt `/__app-env` ergänzt die Antwort nur für das
  gestartete Kind um das feste Attestierungsfeld. Ohne exakte Kennung ist die
  Antwort fremd oder unzureichend.
- Erfolg bedeutet ausschließlich: passende eigene Instanz, Dev-Auth `true`,
  Build-Auth `true` und bestätigter Exit des eigenen Kindes.
- Belegter Port, früher Child-Exit, fremde Antwort, Timeout, synchroner oder
  asynchroner Spawnfehler, Abbruch und Cleanupfehler sind fail-closed.
- Cleanup adressiert nur das unmittelbar gestartete Child (`SIGTERM` und
  beobachteter Exit). Keine PID-Suche, kein Prozessgruppen- oder Fremdprozesskill.

## Harte Grenzen

Kein echter `check:auth`-Lauf in diesem Paket. Der vorhandene Vite-Dev-Start kann
PGLite-Migrationen auslösen; dafür fehlt eine gesonderte Runtime-Freigabe samt
minimaler Child-Environment- und Nebenwirkungsmatrix. Kein Server-, Datenbank-,
Produktions-, Migrations-, Push-, Commit- oder Publikationsschritt.

## Abnahme

1. Red/Green der isolierten Unit-Tests ohne echte Netz- oder Prozesswirkung.
2. Fokussiertes Spec-Review, danach separates Quality-/Securityreview.
3. Erst danach entscheidet der Betreiber separat über eine echte lokale
   Runtime-Prüfung und über einen lokalen Commit.

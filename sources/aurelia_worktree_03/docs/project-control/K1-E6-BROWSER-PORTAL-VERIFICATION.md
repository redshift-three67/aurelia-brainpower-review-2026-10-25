# K1 E6 – lokale Browser-Runtime-Evidenz

```yaml
recorded_at: 2026-09-09T09:17:41+02:00
worktree: .worktrees/aurelia-konsolidierung
branch: codex/aurelia-konsolidierung
observed_head: 1185a68ed984b525686764f995513355701929e3
runtime_authority: explicitly_granted_by_operator
verification_result: indeterminate
browser_started: true
portal_matrix_executed: false
```

## Versuch vom 9. September

Der feste, attestierte E6-Runner startete die lokale Runtime und Chromium. Der
Ausführungs-Host beendete den Lauf nach drei Minuten mit Exit-Code 143, bevor
der Runner sein Verdict-JSON schreiben und die Matrix abschließen konnte. Es
liegt daher weder ein PASS noch ein vollständiges FAIL-Verdict vor.

Vor dem Abbruch entstanden ausschließlich diese elf tatsächlichen lokalen PNGs
unter `screenshots/e6/`:

- `/`: Desktop und Mobil
- `/roadmap`: Desktop und Mobil
- `/offen`: Desktop und Mobil
- `/entscheidungen`: Desktop und Mobil
- `/hardware`: Desktop und Mobil
- `/live`: nur Desktop

Für `/live` Mobil sowie `/sicherheit` in Desktop und Mobil existiert kein
Screenshot. Es existiert kein `screenshots/e6/verdict.json`. Die PNGs belegen
nur, dass diese Teilansichten erreicht wurden; sie ersetzen weder die pro
Sicht erforderlichen Observations noch den aggregierten Matrix-Verdict.

Die anschließende Loopback-Prüfung zeigte nur `TimeWait`-Einträge für Port
4176 und keinen lauschenden Prozess. Kein fremder Prozess wurde adressiert
oder beendet.

## Historischer Versuch vom 8. September

Der vorherige autorisierte E6-Lauf brach beim zugelassenen PGLite-Bootstrap vor
`/__app-env`-Readiness mit folgendem lokalen Ressourcenfehler ab:

```text
RangeError: Array buffer allocation failed
```

Damals wurden kein Playwright-Browser, keine Portalroute und keine Screenshots
ausgeführt. Der Fehler ist kein Asset-, Portal- oder Authentisierungs-PASS.

## Schlussfolgerung

E6 bleibt unvollständig. Ein weiterer Lauf darf nicht automatisch folgen:
Die vorhandenen deterministischen Artefaktnamen verhindern bewusst ein
Überschreiben der Teil-Evidenz. Vor einem neuen, ausdrücklich freigegebenen
Versuch müssen die Abbruchursache beziehungsweise ein sicherer Umgang mit den
bestehenden Artefakten und die Laufzeitgrenze separat entschieden werden.

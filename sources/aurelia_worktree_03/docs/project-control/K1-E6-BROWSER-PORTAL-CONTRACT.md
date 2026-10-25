# K1 E6 – lokaler Browser-/Portalvertrag

```yaml
package: E6
recorded_at: 2026-09-08T11:05:00+02:00
worktree: .worktrees/aurelia-konsolidierung
branch: codex/aurelia-konsolidierung
observed_head: 1185a68ed984b525686764f995513355701929e3
runtime_authority: explicitly_granted_by_operator
scope: local Windows dev server plus Playwright portal matrix
publication_authority: false
server_authority: false
```

## Zulässige Runtime-Wirkungen

- Genau ein selbst gestarteter, attestierter Vite-Dev-Prozess auf `127.0.0.1`.
- Lokaler Playwright-Chromium gegen diese Instanz, ohne CDP und ohne externen
  Browserverkehr.
- Vierzehn PNGs sowie lokale Verdict-JSONs ausschließlich unter `screenshots/e6/`.
- Die bereits für E5 freigegebene mögliche flüchtige in-memory-PGLite-Wirkung.

## Fester Matrix-Runner

- Ausschließlich `node scripts/browser-portal-matrix.mjs` ist der E6-Runtime-Einstieg.
  Er startet einen eigenen Vite-Prozess mit `--host 127.0.0.1` und `--strictPort`,
  attestiert ihn vor Chromium über `/__app-env` und beendet ausschließlich diesen
  selbst gestarteten Kindprozess.
- Route, Origin, Port, Viewports und Ausgabepfade sind im Runner fest verdrahtet;
  es gibt keine URL-, Host-, Port- oder Output-Overrides.
- Chromium darf ausschließlich Anfragen an den attestierten eigenen
  `http://127.0.0.1:<port>`-Origin ausführen. Jeder andere Request wird sichtbar
  blockiert und macht die betroffene Beobachtung fehlerhaft.
- Der Runner schreibt genau vierzehn deterministisch benannte PNGs und ein
  Verdict-JSON ausschließlich relativ unter `screenshots/e6/`.

## Verbote und Ergebnisgrenzen

Kein regulärer Build, Preview, Serverzugriff, Push, PR, Produktion, Migration-
Skript, fremder Prozesskill, externer HTTP-Request oder Plattformasset-Ersatz.
Ein Asset-, Ressourcen- oder Browserfehler bleibt sichtbar und verhindert einen
uneingeschränkten E6-PASS. Der Nachweis gilt nur lokal unter Windows; keine
Linux-, Build-/Preview- oder Produktionsaussage.

## Pflichtmatrix

`/`, `/roadmap`, `/offen`, `/entscheidungen`, `/hardware`, `/live` und
`/sicherheit`, jeweils 1280×800 und 390×844. Pro Sicht: HTTP-Erfolg, sichtbares
`main`, Statusbanner mit Produktpause bis `G0-SRV-12`, kein horizontaler
Überlauf, keine Console-/Page-Fehler, aktive Navigation. Mobil wird zusätzlich
das Kapitelmenü geöffnet und die aktive Route geprüft.

## Abnahme

TDD der Pfad-, Matrix- und Verdict-Helfer; danach Runtime nur gegen die eigene
attestierte Instanz. Spezifikationsreview vor getrenntem Quality-/Securityreview.

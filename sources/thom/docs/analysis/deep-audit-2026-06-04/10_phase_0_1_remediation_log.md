# 10 Phase 0/1 Remediation Log – ShadowCopy und reproduzierbare npm-Baseline

Stand: 2026-06-08
Repository: `/opt/radithoms`
Commit-Basis: `64b9a38f0544bfcc1ea473010013bafe9b804904`
Remote: `https://github.com/radiquant/morpho-field-nexus.git`

## Ziel

Start der priorisierten Remediation nach dem Deep Audit:

1. vor Änderungen eine lokale ShadowCopy herstellen,
2. Baseline vor Änderungen erneut real prüfen,
3. `package-lock.json` synchronisieren,
4. `npm ci` grün machen,
5. Build/TypeScript/Lint/Audit erneut prüfen.

## Phase 0 – ShadowCopy vor Änderungen

Erstellt:

```text
/opt/radithoms-shadowcopies/radithoms-before-remediation-20260608-233808/
```

Manifest:

```text
/opt/radithoms-shadowcopies/radithoms-before-remediation-20260608-233808/SHADOWCOPY_MANIFEST.md
```

Die ShadowCopy enthält den Quell-/Git-/Dokumentationsstand inklusive ungetrackter Analyseberichte. Ausgeschlossen wurden bewusst reproduzierbare/schwere Artefakte:

- `node_modules/`
- `dist/`
- `.cache/`
- `coverage/`

Begründung: Diese Ordner sind reproduzierbar bzw. Build-/Runtime-Artefakte und sollten nicht als dauerhafte Sicherheitskopie von Source/Config/Docs geführt werden.

## Portstatus vor Arbeiten

Geprüft:

```text
Port 5173: free
Port 5174: free
Port 8080: IN USE
```

Es wurde für diese Phase kein Dev-Server gestartet.

## Baseline vor Änderungen

### `npm ci`

Ergebnis vor Lockfile-Synchronisierung: fehlgeschlagen.

Zentraler Fehler:

```text
npm error `npm ci` can only install packages when your package.json and package-lock.json or npm-shrinkwrap.json are in sync.
npm error Missing: tus-js-client@4.3.1 from lock file
```

Weitere fehlende transitive Dependencies u.a.:

- `buffer-from`
- `combine-errors`
- `is-stream`
- `js-base64`
- `lodash.throttle`
- `proper-lockfile`
- `url-parse`

### `npm run build`

Ergebnis vor Änderung: erfolgreich.

Bekannte Warnungen:

- ungültige CSS-Syntax bei `.dark @keyframes chreode-pulse`
- großes Hauptbundle > 500 kB

### `npx tsc --noEmit`

Ergebnis vor Änderung: erfolgreich.

### `npm run lint`

Ergebnis vor Änderung: fehlgeschlagen.

```text
95 problems (71 errors, 24 warnings)
```

### `npm audit --omit=dev --json`

Ergebnis vor Änderung: fehlgeschlagen.

```text
11 vulnerabilities total
7 high
4 moderate
```

## Phase 1 – package-lock synchronisiert

Ausgeführt:

```bash
npm install
```

Ergebnis:

```text
added 51 packages, removed 31 packages, changed 173 packages, and audited 479 packages in 2s
17 vulnerabilities (8 moderate, 9 high)
```

Geänderte Datei:

```text
package-lock.json
```

Diff-Stat:

```text
package-lock.json | 282 +++++++++++++++++++++++++++++++++---------------------
1 file changed, 175 insertions(+), 107 deletions(-)
```

Wesentliche Änderung:

- `tus-js-client` wurde korrekt in `package-lock.json` ergänzt.
- transitive Dependencies für `tus-js-client` wurden ergänzt.
- npm hat Lockfile-Metadaten/Dev-Markierungen aktualisiert.

`package.json` wurde nicht geändert.

## Verifikation nach Lockfile-Synchronisierung

### `npm ci`

Ergebnis nach Lockfile-Synchronisierung: erfolgreich.

```text
added 478 packages, and audited 479 packages in 2s
17 vulnerabilities (8 moderate, 9 high)
```

Wichtiger Befund:

- Das ursprüngliche Phase-1-Ziel `npm ci grün` ist erreicht.
- Dependency Vulnerabilities bleiben bestehen und gehören in die nächste Security-/Dependency-Phase.

### `npm run build`

Ergebnis: erfolgreich.

```text
vite v5.4.19 building for production...
Generated WHO meridian exports: public/exports/who-meridian-points.json and public/exports/who-meridian-points.csv (296 points)
✓ 3674 modules transformed.
✓ built in 7.05s
```

Warnungen bleiben:

```text
Unexpected "@keyframes"
.dark @keyframes chreode-pulse
Unexpected "0%"
Unexpected "50%"
Some chunks are larger than 500 kB after minification.
```

Zusätzlicher Hinweis:

```text
Browserslist: browsers data (caniuse-lite) is 12 months old.
```

### `npx tsc --noEmit`

Ergebnis: erfolgreich, keine Ausgabe.

### `npm run lint`

Ergebnis: weiterhin fehlgeschlagen.

```text
96 problems (71 errors, 25 warnings)
```

Änderung gegenüber Audit:

- Vorher: 95 Probleme, 71 Errors, 24 Warnings.
- Nach Lockfile-Sync: 96 Probleme, 71 Errors, 25 Warnings.
- Die neue zusätzliche Warning betrifft Fast Refresh in `src/components/anatomy/GLBModelLoader.tsx` und ist vermutlich durch aktualisierte transitive Tooling-/Analyseauflösung sichtbar geworden, nicht durch Produktcodeänderung.

### `npm audit --omit=dev --json`

Ergebnis: weiterhin fehlgeschlagen.

```text
11 vulnerabilities total
7 high
4 moderate
```

Wichtig:

- `npm install` ohne `--omit=dev` meldet insgesamt 17 Vulnerabilities.
- Der produktive Audit mit `--omit=dev` bleibt bei 11 Findings.

## Git-Status nach Phase 1

```text
## main...origin/main
 M package-lock.json
?? docs/analysis/
```

Produktiv-Code wurde nicht geändert. Geändert wurde nur:

- `package-lock.json`
- neue/erweiterte Markdown-Analyse-/Remediation-Dokumente unter `docs/analysis/`

## Bewertung Phase 1

### Erreicht

- ShadowCopy vor Änderungen erstellt.
- Baseline vor Änderungen erneut verifiziert.
- `package-lock.json` synchronisiert.
- `npm ci` von rot auf grün gebracht.
- Build bleibt grün.
- TypeScript bleibt grün.

### Nicht Ziel dieser Phase / weiterhin offen

- Lint bleibt rot.
- Dependency Audit bleibt rot.
- CSS-Keyframe-Warnung bleibt offen.
- Bundle-Größenwarnung bleibt offen.
- Edge Function Auth/CORS, RLS, Storage und `.env` wurden noch nicht geändert.

## Nächste empfohlene Phase

Nächste optimale Reihenfolge:

1. Nach-Phase-1 ShadowCopy erstellen.
2. Kleine technische Hotfix-Phase starten:
   - CSS `.dark @keyframes` korrigieren.
   - einfache Lint-Fehlerklassen beheben (`no-case-declarations`, leere Catch-Blöcke), ohne fachliche Logik zu verändern.
3. Danach Dependency Security:
   - React Router/PostCSS/Transitive Vulnerabilities kontrolliert aktualisieren.
4. Danach P0-Security:
   - `.env` aus Git entfernen.
   - Edge `verify_jwt=true` und CORS Whitelist.
   - RLS `user_id IS NULL` Strategie.
   - Storage `client-photos` privat.

## Lokale Logdateien dieser Phase

Temporäre Tool-Logs:

```text
/tmp/radithoms-baseline-npm-ci.log
/tmp/radithoms-baseline-build.log
/tmp/radithoms-baseline-tsc.log
/tmp/radithoms-baseline-lint.log
/tmp/radithoms-baseline-audit.json
/tmp/radithoms-phase1-npm-install.log
/tmp/radithoms-phase1-npm-ci-after-install.log
/tmp/radithoms-phase1-build.log
/tmp/radithoms-phase1-tsc.log
/tmp/radithoms-phase1-lint.log
/tmp/radithoms-phase1-audit.json
```

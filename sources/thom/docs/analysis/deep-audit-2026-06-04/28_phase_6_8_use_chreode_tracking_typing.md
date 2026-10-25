# Phase 6 Teil 8 — useChreodeTracking Typ-Stabilisierung

Datum: 2026-06-14
Projekt: `/opt/radithoms`
Datei: `src/hooks/useChreodeTracking.ts`

## Ziel

Fortsetzung von Phase 6: systematischer Abbau der verbleibenden `no-explicit-any` Errors nach Runtime-/Datenfluss-Risiko.

Priorisierter Kandidat war `useChreodeTracking.ts`, weil der Hook Chreode-/Tracking-Daten an der Supabase-Tabelle `chreode_trajectories` schreibt und lädt.

## Ausgangsbefund

Gezielte ESLint-Prüfung vor der Änderung:

```text
/opt/radithoms/src/hooks/useChreodeTracking.ts
  35:41  error  Unexpected any. Specify a different type
  60:41  error  Unexpected any. Specify a different type
  68:45  error  Unexpected any. Specify a different type

✖ 3 problems (3 errors, 0 warnings)
```

## Root Cause

Die Tabelle `chreode_trajectories` ist in den generierten Supabase-Typen vorhanden, aber der Hook nutzte noch ältere Escape-Hatches:

```ts
.from('chreode_trajectories' as any)
(data || []).map((row: any) => ...)
```

Dadurch wurden die vorhandenen Tabellenverträge für `Row` und `Insert` nicht genutzt. Zusätzlich zeigte der generierte `Row`-Typ, dass mehrere Werte aus der Datenbank nullable sind (`bifurcation_risk`, `stability`, `phase`, `chreode_alignment`, `attractor_distance`), während das lokale Export-Interface diese Werte bislang streng nicht-null typisierte.

## Umsetzung

Minimaler Typ-Fix ohne Änderung an Query-, Insert-, Fehler- oder Hook-Logik:

- Supabase-`Database`-Typ importiert.
- Tabellenverträge abgeleitet:

```ts
type ChreodeTrajectoryRow = Database['public']['Tables']['chreode_trajectories']['Row'];
type ChreodeTrajectoryInsert = Database['public']['Tables']['chreode_trajectories']['Insert'];
```

- `recordPoint`-Insert-Payload als `ChreodeTrajectoryInsert` typisiert.
- `.from('chreode_trajectories' as any)` durch `.from('chreode_trajectories')` ersetzt.
- `loadTrajectories`-Mapper auf `ChreodeTrajectoryRow` typisiert.
- `ChreodeTrajectoryPoint` an die realen nullable DB-Felder angepasst:

```ts
bifurcationRisk: number | null;
stability: number | null;
phase: string | null;
chreodeAlignment: number | null;
attractorDistance: number | null;
```

## Geändertes Verhalten

Beabsichtigt keine fachliche Runtime-Änderung.

Unverändert bleiben:

- `recordPoint` schreibt weiterhin `client_id`, `session_id`, Dimensionen, Entropie-Modulation, Attraktorwerte und berechnete Distanz.
- `entropyModulation || []` bleibt unverändert.
- Attraktor-Distanz-Berechnung bleibt unverändert.
- Insert-Fehler werden weiterhin nur geloggt.
- `loadTrajectories` lädt weiterhin nach `client_id`, sortiert nach `timestamp` aufsteigend und limitiert standardmäßig auf 200.
- Rückgabe bei Ladefehler bleibt `[]`.
- Keine neuen Logs, Uploads, E-Mails oder Persistenzpfade für Patientendaten.

Hinweis: Die nullable Anpassung des Export-Interfaces ist eine Typkorrektur an den realen Datenbankvertrag. Sie verhindert, dass mögliche DB-Nullwerte durch TypeScript als garantiert nicht-null ausgegeben werden.

## Verifikation

### Ziel-ESLint

```bash
npx eslint src/hooks/useChreodeTracking.ts
```

Ergebnis:

```text
PASS, exit_code 0
```

### TypeScript

```bash
npx tsc --noEmit
```

Ergebnis:

```text
PASS, exit_code 0
```

### Production Build

```bash
npm run build
```

Ergebnis:

```text
✓ 3674 modules transformed.
✓ built in 5.58s
```

Bekannte, unveränderte Build-Hinweise:

```text
Browserslist data is 12 months old
Some chunks are larger than 500 kB after minification
```

### Gesamt-Lint nach Phase 6 Teil 8

```text
✖ 24 problems (11 errors, 13 warnings)
```

Vergleich zu Phase 6 Teil 7:

```text
Vorher: 27 problems (14 errors, 13 warnings)
Nachher: 24 problems (11 errors, 13 warnings)
Verbesserung: -3 errors, 0 neue warnings/errors
```

### Browser-/Runtime-Smoke

Vor Start wurde Port 5173 geprüft:

```text
5173 free
5174 free
5175 free
4173 free
```

Dev Server:

```text
VITE v5.4.21 ready in 178 ms
Local: http://127.0.0.1:5173/
```

HTTP-Smoke:

```text
HTTP_STATUS 200
CONTENT_TYPE text/html
BYTES 1285
```

Browser-Smoke:

```text
URL-Aufruf: http://127.0.0.1:5173/analyse?phase6_8=use-chreode-tracking
Login-/Auth-Seite sichtbar
Console messages: []
JS errors: []
total_errors: 0
```

## Ergebnis

Phase 6 Teil 8 ist abgeschlossen.

- `src/hooks/useChreodeTracking.ts`: gezielter ESLint sauber.
- 3 `no-explicit-any` Errors entfernt.
- TypeScript sauber.
- Production Build sauber.
- Gesamt-Lint von 27 auf 24 Probleme verbessert.
- Browser-Smoke ohne Console-/JS-Fehler.

## Nächster empfohlener Schritt

Weiter mit Phase 6 Teil 9 nach Runtime-/Datenfluss-Risiko:

1. `src/hooks/useOrganLandmarks.ts`
   - 3 `no-explicit-any` Errors.
   - Organ-/Anatomie-Landmark-Datenfluss.

Danach:

2. `src/hooks/useSpooky2.ts`
   - 2 `no-explicit-any` Errors.
   - Geräte-/Frequenz-Integration.

3. `src/hooks/useOrganScanPoints.ts`
   - 1 `no-explicit-any` Error.
   - Organ-Scanpoint-Datenfluss.

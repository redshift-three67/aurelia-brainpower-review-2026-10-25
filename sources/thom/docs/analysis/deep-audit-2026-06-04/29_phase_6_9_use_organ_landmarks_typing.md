# Phase 6 Teil 9 — useOrganLandmarks Typ-Stabilisierung

Datum: 2026-06-14
Projekt: `/opt/radithoms`
Datei: `src/hooks/useOrganLandmarks.ts`

## Ziel

Fortsetzung von Phase 6: systematischer Abbau der verbleibenden `no-explicit-any` Errors nach Runtime-/Datenfluss-Risiko.

Priorisierter Kandidat war `useOrganLandmarks.ts`, weil der Hook Organ-Schemas und Organ-Landmarks aus Supabase lädt, auf lokale Anatomie-Pilotdaten zurückfällt und daraus ScanPoint-kompatible Daten ableitet.

## Ausgangsbefund

Gezielte ESLint-Prüfung vor der Änderung:

```text
/opt/radithoms/src/hooks/useOrganLandmarks.ts
   83:63  error  Unexpected any. Specify a different type
  111:77  error  Unexpected any. Specify a different type
  159:19  error  Unexpected any. Specify a different type

✖ 3 problems (3 errors, 0 warnings)
```

## Root Cause

Die Supabase-Tabellen `organ_schemas` und `organ_landmarks` sind in den generierten Supabase-Typen vorhanden, aber die Mapper nutzten noch lokale `any`-Escape-Hatches:

```ts
schemaData.map((s: any) => ...)
(landmarkData || []).map((l: any) => ...)
lms.map((l: any, i: number) => ...)
```

Damit waren die realen Datenbankverträge für `Row` nicht genutzt. Zusätzlich sind einige DB-Felder als `Json` modelliert (`regions`, `sampling_config`, `validation_config`), weshalb an der JSON-Grenze schmale defensive Helfer sinnvoller sind als breite Casts im Mapper.

## Umsetzung

Minimaler Typ-Fix ohne Änderung an Query-, Fallback-, Fehler- oder Hook-Logik:

- Supabase-`Database`- und `Json`-Typ importiert.
- Tabellenverträge abgeleitet:

```ts
type OrganSchemaRow = Database['public']['Tables']['organ_schemas']['Row'];
type OrganLandmarkRow = Database['public']['Tables']['organ_landmarks']['Row'];
```

- Lokalen `OrganRegion`-Typ ergänzt.
- JSON-Grenzen über kleine Helfer typisiert:

```ts
const isJsonRecord = (value: Json | null): value is Record<string, unknown> =>
  typeof value === 'object' && value !== null && !Array.isArray(value);

const toJsonRecord = (value: Json | null): Record<string, unknown> =>
  isJsonRecord(value) ? value : {};

const toOrganRegions = (value: Json): OrganRegion[] =>
  Array.isArray(value) ? (value as OrganRegion[]) : [];
```

- Organ-Schema-Mapper auf `OrganSchemaRow` typisiert.
- Organ-Landmark-Mapper auf `OrganLandmarkRow` typisiert.
- Pilotdaten-Mapper ohne `any` typisiert, indem die vorhandene Inferenz der Pilotdaten genutzt wird.
- Surface-Normal-Erstellung defensiv auf vollständige X/Y/Z-Werte geprüft.

## Geändertes Verhalten

Beabsichtigt keine fachliche Runtime-Änderung.

Unverändert bleiben:

- Laden von `organ_schemas`, sortiert nach `organ_code`.
- Fallback auf lokale Pilotdaten, wenn die DB leer ist oder Laden fehlschlägt.
- Laden von `organ_landmarks` für die gefundenen Schema-IDs.
- Sortierung nach `point_id`.
- Mapping der Felder in `OrganSchema` und `OrganLandmark`.
- Filterung nach ausgewähltem Organ.
- Ableitung von A-/S-Landmarks.
- Ableitung von `toScanPoints`.
- Console-Hinweis beim Pilotdaten-Fallback bleibt unverändert.
- Keine neuen Logs, Uploads, E-Mails oder Persistenzpfade für Patientendaten.

Hinweis: Die JSON-Helfer begrenzen die Typisierung auf die tatsächlich konsumierten Strukturen. Sie ersetzen keine fachliche Validierung und ändern die bisherige Fallback-Strategie nicht.

## Verifikation

### Ziel-ESLint

```bash
npx eslint src/hooks/useOrganLandmarks.ts
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
✓ built in 5.61s
```

Bekannte, unveränderte Build-Hinweise:

```text
Browserslist data is 12 months old
Some chunks are larger than 500 kB after minification
```

### Gesamt-Lint nach Phase 6 Teil 9

```text
✖ 21 problems (8 errors, 13 warnings)
```

Vergleich zu Phase 6 Teil 8:

```text
Vorher: 24 problems (11 errors, 13 warnings)
Nachher: 21 problems (8 errors, 13 warnings)
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
VITE v5.4.21 ready in 171 ms
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
URL-Aufruf: http://127.0.0.1:5173/analyse?phase6_9=use-organ-landmarks
Redirect/Ziel: http://127.0.0.1:5173/login
Login-/Auth-Seite sichtbar
Console messages: []
JS errors: []
total_errors: 0
```

## Ergebnis

Phase 6 Teil 9 ist abgeschlossen.

- `src/hooks/useOrganLandmarks.ts`: gezielter ESLint sauber.
- 3 `no-explicit-any` Errors entfernt.
- TypeScript sauber.
- Production Build sauber.
- Gesamt-Lint von 24 auf 21 Probleme verbessert.
- Browser-Smoke ohne Console-/JS-Fehler.

## Nächster empfohlener Schritt

Weiter mit Phase 6 Teil 10 nach Runtime-/Datenfluss-Risiko:

1. `src/hooks/useSpooky2.ts`
   - 2 `no-explicit-any` Errors.
   - Geräte-/Frequenz-Integration.

Danach:

2. `src/hooks/useOrganScanPoints.ts`
   - 1 `no-explicit-any` Error.
   - Organ-ScanPoint-Datenfluss.

3. `src/components/anatomy/ModelSelector.tsx`
   - 1 `no-explicit-any` Error.
   - Anatomie-Modell-Auswahl.

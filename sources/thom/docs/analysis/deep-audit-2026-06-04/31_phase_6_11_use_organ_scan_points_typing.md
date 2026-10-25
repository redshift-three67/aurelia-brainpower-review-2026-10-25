# Phase 6 Teil 11 — useOrganScanPoints Typ-Stabilisierung

Datum: 2026-06-14
Projekt: `/opt/radithoms`
Datei: `src/hooks/useOrganScanPoints.ts`

## Ziel

Fortsetzung von Phase 6: systematischer Abbau der verbleibenden `no-explicit-any` Errors nach Runtime-/Datenfluss-Risiko.

Priorisierter Kandidat war `useOrganScanPoints.ts`, weil der Hook Organ-ScanPoint-Daten aus Supabase lädt, nach Organ filtert, gruppiert und für UI-/Analysefunktionen bereitstellt.

## Ausgangsbefund

Gezielte ESLint-Prüfung vor der Änderung:

```text
/opt/radithoms/src/hooks/useOrganScanPoints.ts
  105:61  error  Unexpected any. Specify a different type

✖ 1 problem (1 error, 0 warnings)
```

## Root Cause

Die Tabelle `organ_scan_points` ist in den generierten Supabase-Typen vorhanden, aber der Row-Mapper nutzte noch einen lokalen `any`-Escape-Hatch:

```ts
(data || []).map((p: any) => ...)
```

Damit war der vorhandene Datenbankvertrag für die Row-Felder nicht genutzt.

## Umsetzung

Minimaler Typ-Fix ohne Änderung an Query-, Filter-, Mapping-, Fehler- oder Hook-Logik:

```ts
import type { Database } from '@/integrations/supabase/types';

type OrganScanPointRow =
  Database['public']['Tables']['organ_scan_points']['Row'];
```

Anschließend wurde der Mapper auf den generierten Row-Typ umgestellt:

```ts
const mapped: OrganScanPoint[] =
  (data || []).map((p: OrganScanPointRow) => ({
    id: p.id,
    organSystem: p.organ_system,
    organNameDe: p.organ_name_de,
    organNameLatin: p.organ_name_latin,
    pointIndex: p.point_index,
    pointName: p.point_name,
    scanFrequency: p.scan_frequency,
    harmonicFrequencies: p.harmonic_frequencies || [],
    x: p.x_position,
    y: p.y_position,
    z: p.z_position,
    tissueType: p.tissue_type,
    dysregulationThreshold: p.dysregulation_threshold || 1.5,
    bodyRegion: p.body_region,
    layerDepth: p.layer_depth || 'surface',
    description: p.description,
  }));
```

## Geändertes Verhalten

Beabsichtigt keine fachliche Runtime-Änderung.

Unverändert bleiben:

- Supabase-Abfrage auf `organ_scan_points`.
- Sortierung nach `organ_system` und `point_index`.
- Optionaler Filter `eq('organ_system', organSystem)`.
- Fehlerbehandlung mit bestehendem Console-Error.
- Mapping in das lokale `OrganScanPoint` Interface.
- Fallback für `harmonic_frequencies || []`.
- Fallback für `dysregulation_threshold || 1.5`.
- Fallback für `layer_depth || 'surface'`.
- Gruppierung über `organGroups`.
- Filterung über `selectedOrgan`.
- Ableitung von `organSystems`.
- Keine neuen Logs, Uploads, E-Mails oder Persistenzpfade für Patientendaten.

## Verifikation

### Ziel-ESLint

```bash
npx eslint src/hooks/useOrganScanPoints.ts
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
✓ built in 5.60s
```

Bekannte, unveränderte Build-Hinweise:

```text
Browserslist data is 12 months old
Some chunks are larger than 500 kB after minification
```

### Gesamt-Lint nach Phase 6 Teil 11

```text
✖ 18 problems (5 errors, 13 warnings)
```

Vergleich zu Phase 6 Teil 10:

```text
Vorher: 19 problems (6 errors, 13 warnings)
Nachher: 18 problems (5 errors, 13 warnings)
Verbesserung: -1 error, 0 neue warnings/errors
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
VITE v5.4.21 ready in 172 ms
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
URL-Aufruf: http://127.0.0.1:5173/analyse?phase6_11=use-organ-scan-points
Login-/Auth-Seite sichtbar
Console messages: []
JS errors: []
total_errors: 0
```

## Ergebnis

Phase 6 Teil 11 ist abgeschlossen.

- `src/hooks/useOrganScanPoints.ts`: gezielter ESLint sauber.
- 1 `no-explicit-any` Error entfernt.
- TypeScript sauber.
- Production Build sauber.
- Gesamt-Lint von 19 auf 18 Probleme verbessert.
- Browser-Smoke ohne Console-/JS-Fehler.

## Nächster empfohlener Schritt

Weiter mit Phase 6 Teil 12 nach Runtime-/Datenfluss-Risiko:

1. `src/components/anatomy/ModelSelector.tsx`
   - 1 `no-explicit-any` Error.
   - Anatomie-Modell-Auswahl.

Danach:

2. `src/components/anatomy/ModelUpload.tsx`
   - 1 `no-explicit-any` Error.
   - Anatomie-Modell-Upload.

3. `src/pages/Login.tsx`
   - 1 `no-explicit-any` Error.
   - Auth-Fehlerbehandlung.

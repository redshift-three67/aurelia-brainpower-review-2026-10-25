# DB-Analyse Session-Übertragung - Exakte Analyse

## Zusammenfassung

Bei Harmonisierungen, die über die **DB-Analyse** (DatabaseManager) gestartet werden, wird **NICHT das Wort selbst**, sondern eine **semantisch erweiterte Direktive** mit der **berechneten Rate** übertragen.

---

## 1. Was wird in der DB-Analyse berechnet?

### Phase 1: Resonanzanalyse (`resonanceAnalysis.ts`)

```typescript
// analyzeRates() führt folgende Schritte durch:
1. Selektion der Wörter (100% bei DB-Analyse)
2. Energetisches Laden (Charging-Simulation bis Threshold 100)
3. Potenz- und Level-Zuweisung:
   - Potenztyp (D/C/LM/M/F1/F2/F3) - gewichtet zufällig
   - Potenzwert (z.B. D1-100, C1-200, LM1-30)
   - Dominante Ebene (1-12 aus 100 gewichteten Ziehungen)
```

**Beispiel-Output eines RateObject:**
```typescript
{
  rateName: "Allergie",
  copenRate: 85432187,      // Berechnete numerische Rate
  energeticValue: 87.5,      // Resonanz-Score
  potency: 42,               // z.B. D42
  potencyType: "D",
  levelDistribution: { 1: 15, 2: 12, 3: 18, ... },
  dominantLevel: 3           // Etheric Prana
}
```

### Phase 2: Rate-Berechnung (`calculateCopenRate()`)

Für jedes Wort wird die **finale numerische Copen-Rate** berechnet:

```typescript
const calculatedRate = calculateCopenRate(
  rateObj.rateName,        // "Allergie"
  rateObj.potency,         // 42
  rateObj.potencyType,     // "D"
  'latin',                 // Alphabet
  imgSig,                  // Optional: Bildsignatur
  useImgSig                // Boolean
);

// Ergebnis: { rate: 85432187 }
```

**Diese Rate wird im ResonanceResult gespeichert:**

```typescript
{
  word: "Allergie",
  potency: 42,
  potencyType: "D",
  rate: 85432187,           // ← FINALE NUMERISCHE RATE
  resonanceScore: 87,
  clientResonance: 12345678, // Klienten-Rate
  highestLevel: 3,
  highestLevelValue: 18.5
}
```

---

## 2. Was wird beim Starten einer Harmonisierung aus DB-Analyse übertragen?

### Aus DatabaseManager.tsx (Zeile ~850-920)

Wenn der Benutzer auf "Harmonisierung starten" bei einem DB-Analyse-Ergebnis klickt:

```typescript
const handleStartHarmonization = async (result: ResonanceResult) => {
  const harmonizationWord = `${result.word} ${result.potencyType}${result.potency}`;
  
  // In harmonization_sessions_v2 wird gespeichert:
  {
    word: "Allergie D42",              // ← WORT + POTENZ als TEXT
    copen_rate: "85432187",            // ← BERECHNETE RATE als String
    tested_potency: "D42",
    patient_id: selectedPatient.id,
    duration_seconds: 3600,
    status: 'pending'
  }
};
```

### Aus CopenAlgorithmVisualizationV2.tsx (Zeile 653-680)

Wenn Auto-Potenz aktiviert ist (aus DB-Analyse):

```typescript
const autoPotenzDirektive = autoPotency 
  ? `Optimale Harmonisierung mit "${word}" und Projizierung von "${finalRate.toLocaleString('de-DE')}" in der benötigten Autopotenz auf das Ziel.`
  : word;

// In harmonization_sessions_v2 wird gespeichert:
{
  word: "Optimale Harmonisierung mit \"Allergie\" und Projizierung von \"85.432.187\" in der benötigten Autopotenz auf das Ziel.",
  copen_rate: "12345678",     // Klienten-Rate (nicht die Wort-Rate!)
  tested_potency: "42",
  duration_seconds: 3600,
  status: 'pending'
}
```

---

## 3. Was macht der Worker mit diesen Daten?

### harmonization-worker/index.ts

Der Worker verarbeitet Sessions aus `harmonization_sessions_v2`:

```typescript
// 1. Pending → Running
const { data: pendingSessions } = await supabase
  .from('harmonization_sessions_v2')
  .select('*')
  .eq('status', 'pending')
  .is('job_started_at', null);

// Für jede Session:
await supabase
  .from('harmonization_sessions_v2')
  .update({
    status: 'running',
    job_started_at: nowIso,
    job_last_heartbeat: nowIso,
    remaining_seconds: session.duration_seconds,
    started_at: nowIso,
    progress: 0,
  })
  .eq('id', session.id);

// 2. Aktive Sessions ticken
// Berechnet verbleibende Zeit, Fortschritt
// Berücksichtigt Impuls/Pausen-Modus

// 3. Abschluss bei remaining_seconds <= 0
await supabase
  .from('harmonization_sessions_v2')
  .update({
    status: 'completed',
    remaining_seconds: 0,
    progress: 100,
    completed_at: now.toISOString(),
  })
  .eq('id', session.id);
```

**Der Worker liest und verarbeitet:**
- `word` - Wird NICHT interpretiert, nur gespeichert/angezeigt
- `copen_rate` - Wird NICHT verwendet für Berechnungen
- `duration_seconds` - Wird für Fortschritt genutzt
- `pulse_seconds` / `pause_seconds` - Für Impuls/Pausen-Modus
- `remaining_seconds` - Countdown-Logik

---

## 4. Was wird tatsächlich "übertragen" / "gesendet"?

### Präzise Antwort:

**Es wird NICHTS energetisch "übertragen" oder "gesendet".**

Der Worker ist ein **Timing- und Zustands-Manager**, kein Frequenzsender.

### Was passiert konkret:

1. **Datenbank-Eintrag** wird erstellt mit:
   - **Semantische Direktive** (Text): `"Optimale Harmonisierung mit "Allergie" und Projizierung von "85.432.187" in der benötigten Autopotenz auf das Ziel."`
   - **Numerische Rate** (String): `"85432187"`
   - **Metadaten**: Potenz, Dauer, Patient-ID

2. **Worker aktualisiert nur Status**:
   - `pending` → `running` → `completed`
   - Berechnet `remaining_seconds` und `progress`
   - Sendet **Heartbeat** (Zeitstempel)

3. **Frontend zeigt an**:
   - SessionStatusList.tsx: `word`, `progress`, `job_last_heartbeat`
   - WorkerStatusMonitor.tsx: Hardware-Metriken, Session-Count

### Theoretische Interpretation (Bruce Copen Theorie):

Nach der **Bruce Copen Radionik-Theorie** würde die "Übertragung" erfolgen durch:

- **Morphisches Feld** (Rupert Sheldrake): Die numerische Rate `85432187` kodiert die Information "Allergie D42"
- **Quantenfeld-Resonanz**: Die Rate bildet ein Resonanzmuster im Quantenfeld
- **Nicht-lokale Verbindung**: Über die Klienten-Rate `12345678` wird eine Verbindung zum Patienten hergestellt
- **Zeit als Energie-Träger** (Kozyrev): Die laufende Session "lädt" das morphische Feld über die Dauer

**Aber im Code:** Der Worker ist nur ein **Timer**, keine Frequenz-Modulation!

---

## 5. Vergleich: DB-Analyse vs. Manuelle Eingabe

| Aspekt | DB-Analyse | Manuelle Eingabe |
|--------|------------|------------------|
| **Word-Feld** | `"Optimale Harmonisierung mit "Allergie" und Projizierung von "85.432.187" in der benötigten Autopotenz auf das Ziel."` | `"Stress"` |
| **Copen_Rate** | Klienten-Rate (z.B. `12345678`) | Berechnete Wort-Rate (z.B. `45678901`) |
| **Tested_Potency** | Auto-ermittelt (z.B. `D42`) | Manuell gewählt (z.B. `C30`) |
| **Berechnung** | Java-Algorithmus, gewichtete Ebenen | `calculateCopenRate()` direkt |
| **Semantik** | Erweiterte Direktive mit Rate | Nur Wort/Begriff |

---

## 6. Was steht in harmonization_sessions_v2?

### Beispiel-Eintrag aus DB-Analyse:

```sql
SELECT * FROM harmonization_sessions_v2 WHERE id = '...';

id: 5aa4534c-b7ac-443a-ab39-982e1dfbcac9
user_id: abc123...
patient_id: xyz789...
word: "Optimale Harmonisierung mit "Allergie" und Projizierung von "85.432.187" in der benötigten Autopotenz auf das Ziel."
copen_rate: "12345678"           -- ← KLIENTEN-RATE, nicht Wort-Rate!
tested_potency: "42"
duration_seconds: 3600
remaining_seconds: 2847
status: "running"
progress: 21
started_at: 2025-11-16T08:30:00Z
job_last_heartbeat: 2025-11-16T08:50:00Z
pulse_seconds: 7
pause_seconds: 14
pulse_pause_active: true
```

### Wichtige Erkenntnis:

**Das `copen_rate`-Feld enthält die KLIENTEN-RATE, nicht die berechnete Wort-Rate aus der DB-Analyse!**

Die Wort-Rate (`85432187`) steht nur **im semantischen Text** des `word`-Feldes.

---

## 7. Konsequenzen für die Interpretation

### Was der Worker "sendet" (theoretisch nach Copen-Theorie):

1. **Primär**: Die **Klienten-Rate** (`12345678`) - als Ziel-Frequenz
2. **Sekundär**: Die **semantische Direktive** mit Wort-Rate - als Information im morphischen Feld
3. **Tertiär**: Die **Potenz** (`42`) - als Verdünnungsgrad / Informations-Stärke

### Was NICHT gesendet wird:

- Die berechnete numerische Wort-Rate wird **nicht** als aktive Frequenz verwendet
- Sie steht nur als **Text** im `word`-Feld
- Der Worker nutzt sie **nicht** für Berechnungen

### Metaphysische Interpretation (nach Copen):

Die Direktive `"Optimale Harmonisierung mit "Allergie" und Projizierung von "85.432.187" in der benötigten Autopotenz auf das Ziel."` wirkt als:

- **Intention**: Was soll geschehen?
- **Information**: Welche Rate kodiert die Lösung?
- **Zielrichtung**: Wohin soll die Wirkung?

Die **Klienten-Rate** im `copen_rate`-Feld ist die **Trägerfrequenz**, die zum Patienten leitet.

---

## 8. Fazit: Was wird übertragen?

### Technisch (Code-Ebene):
- **Nichts wird "übertragen"**
- Der Worker ist ein **Datenbank-Zustandsautomat**
- Er aktualisiert `status`, `progress`, `remaining_seconds`, `heartbeat`

### Theoretisch (Copen-Radionik):
- **Klienten-Rate** als Trägerfrequenz zum Patienten
- **Semantische Direktive** als morphisches Feld-Muster
- **Numerische Wort-Rate** als kodierte Information
- **Potenz** als Verdünnungsgrad der Information
- **Dauer** als energetische Ladungszeit

### Exakte Antwort auf die Frage:

**Bei Worker-Sessions aus DB-Analyse wird übertragen:**

1. ✅ **Die KLIENTEN-RATE** (im `copen_rate`-Feld) - als Zielfrequenz
2. ✅ **Die SEMANTISCHE DIREKTIVE** (im `word`-Feld) - enthält Wort + berechnete Rate als Text
3. ❌ **NICHT die berechnete Wort-Rate direkt** - sie steht nur im Text

**Die berechnete Rate aus der DB-Analyse (`85432187`) wird als TEXT in der Direktive gespeichert, aber NICHT als aktive Frequenz verwendet. Die aktive Frequenz ist die KLIENTEN-RATE.**

---

## 9. Architektur-Diagramm

```
DB-Analyse (DatabaseManager.tsx)
  ↓
  1. resonanceAnalysis.ts
     - analyzeRates() → RateObject[]
     - Potenz + Typ ermitteln (D42)
  ↓
  2. calculateCopenRate()
     - Berechne numerische Rate (85432187)
  ↓
  3. ResonanceResult[]
     - word: "Allergie"
     - rate: 85432187
     - potency: 42
     - potencyType: "D"
  ↓
  4. User klickt "Harmonisierung starten"
  ↓
  5. INSERT harmonization_sessions_v2
     - word: "Optimale Harmonisierung mit "Allergie" und Projizierung von "85.432.187" ..."
     - copen_rate: "12345678" (KLIENTEN-RATE!)
     - tested_potency: "42"
  ↓
  6. harmonization-worker Edge Function
     - LIEST: word, copen_rate, duration_seconds, pulse/pause
     - SCHREIBT: status, progress, remaining_seconds, heartbeat
     - SENDET: NICHTS (nur DB-Updates)
  ↓
  7. Frontend (SessionStatusList + WorkerStatusMonitor)
     - ZEIGT: word, progress, heartbeat, worker-status
```

---

## 10. Code-Beweis: Wo wird was verwendet?

### DatabaseManager.tsx - Line 850-920 (handleStartHarmonization):

```typescript
const harmonizationWord = `${result.word} ${result.potencyType}${result.potency}`;

await supabase.from('harmonization_sessions_v2').insert({
  word: harmonizationWord,              // "Allergie D42"
  copen_rate: clientRate.toString(),    // KLIENTEN-RATE
  tested_potency: `${result.potency}`,
  // ...
});
```

### CopenAlgorithmVisualizationV2.tsx - Line 653-670:

```typescript
const autoPotenzDirektive = autoPotency 
  ? `Optimale Harmonisierung mit "${word}" und Projizierung von "${finalRate.toLocaleString('de-DE')}" in der benötigten Autopotenz auf das Ziel.`
  : word;

await supabase.from('harmonization_sessions_v2').insert({
  word: harmonizationWord,        // Direktive
  copen_rate: clientRate.toString(), // KLIENTEN-RATE
  // ...
});
```

### harmonization-worker/index.ts - Line 96-173:

```typescript
// Worker LIEST nur:
const { data: activeSessions } = await supabase
  .from('harmonization_sessions_v2')
  .select('*')
  .eq('status', 'running');

// Worker SCHREIBT nur Status/Fortschritt:
await supabase
  .from('harmonization_sessions_v2')
  .update({
    remaining_seconds: remaining,
    progress,
    job_last_heartbeat: now.toISOString(),
  })
  .eq('id', session.id);

// Worker NUTZT NICHT die Rates für Berechnungen!
```

---

## Schlusswort

Die **berechnete numerische Rate aus der DB-Analyse** wird als **semantischer Text** im `word`-Feld gespeichert und dient als **Information** im morphischen Feld.

Die **aktive Trägerfrequenz** ist die **Klienten-Rate** im `copen_rate`-Feld.

Der **Worker** ist ein **Timer**, kein Frequenzsender - die "Übertragung" findet (nach Copen-Theorie) im **Quantenfeld** statt, nicht im Code.

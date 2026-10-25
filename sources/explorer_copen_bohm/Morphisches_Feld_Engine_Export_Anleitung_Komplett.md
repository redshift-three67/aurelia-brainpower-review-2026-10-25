# Morphische Feld-Engine - Vollständiger Export für Neues Projekt

**Version:** 1.0  
**Datum:** 2025-12-31  
**Zweck:** Auslagerung der kompletten Morphischen Feld-Engine in ein eigenständiges Lovable-Projekt

---

## 📋 Inhaltsverzeichnis

1. [Übersicht](#übersicht)
2. [Neues Projekt erstellen](#neues-projekt-erstellen)
3. [Erforderliche Dateien](#erforderliche-dateien)
4. [Datenbank-Schema](#datenbank-schema)
5. [Dependencies](#dependencies)
6. [Schritt-für-Schritt Anleitung](#schritt-für-schritt-anleitung)
7. [Deaktivierung im Resonanz Explorer](#deaktivierung-im-resonanz-explorer)

---

## Übersicht

Die Morphische Feld-Engine ist ein eigenständiges Modul basierend auf der Formel:

```
Ψ_total(x,t) = Σn αn |ψn⟩ e^(-iEnt/ℏ) × C(numerical_sequence) × G(geometric_forms) × I(intention)
```

### Enthaltene Funktionalitäten:
- Standard-Morphische-Feldberechnung mit Quantensuperposition
- Klienten-Feldalgorithmus mit TCM/5-Elemente-Integration
- Bohm'sche Ordnung Integration
- Hardware-Modulation (Kozyrev-Torsionsfelder)
- Patienten-Integration aus Cloud-Datenbank
- Bild-Signatur Upload

---

## Neues Projekt erstellen

1. Gehe zu [lovable.dev/new](https://lovable.dev) und erstelle ein neues Projekt
2. Aktiviere "Lovable Cloud" für Datenbank-Funktionen
3. Nenne das Projekt z.B. "Morphisches Feld Engine"

---

## Erforderliche Dateien

### 📁 Dateistruktur im neuen Projekt:

```
src/
├── components/
│   ├── MorphicFieldCalculator.tsx      # Hauptrechner
│   ├── ClientFieldCalculator.tsx       # Klienten-Algorithmus
│   └── ui/                             # Shadcn UI Komponenten (werden automatisch generiert)
├── pages/
│   └── MorphicFieldPage.tsx            # Hauptseite (wird Index.tsx)
├── utils/
│   ├── morphicFieldEngine.ts           # Kern-Engine
│   ├── clientFieldAlgorithms.ts        # Klienten-Algorithmen
│   ├── copenRateGenerator.ts           # Copen-Rate Berechnung
│   ├── hardwareAlgorithms.ts           # Kozyrev-Hardware
│   └── alphabetSystems.ts              # Alphabet-Systeme
├── hooks/
│   └── use-toast.ts                    # Toast-Hook
└── integrations/
    └── supabase/
        └── client.ts                   # (wird automatisch generiert)
```

---

## 1. Utility-Dateien

### `src/utils/alphabetSystems.ts`
```typescript
export type AlphabetType = 'latin' | 'altdeutsch-gotisch' | 'altdeutsch-mittelhochdeutsch' | 'runisch';

export interface AlphabetSystem {
  name: string;
  description: string;
  letterValues: Record<string, number>;
}

export const alphabetSystems: Record<AlphabetType, AlphabetSystem> = {
  'latin': {
    name: 'Lateinisches Alphabet',
    description: 'Standard A=1, B=2, C=3... (Original Copen)',
    letterValues: {
      'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 9, 'J': 10,
      'K': 11, 'L': 12, 'M': 13, 'N': 14, 'O': 15, 'P': 16, 'Q': 17, 'R': 18, 'S': 19, 'T': 20,
      'U': 21, 'V': 22, 'W': 23, 'X': 24, 'Y': 25, 'Z': 26
    }
  },
  'altdeutsch-gotisch': {
    name: 'Altdeutsch (Gotische Schrift)',
    description: 'Fraktur-Alphabet mit 26 Buchstaben',
    letterValues: {
      'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 9, 'J': 10,
      'K': 11, 'L': 12, 'M': 13, 'N': 14, 'O': 15, 'P': 16, 'Q': 17, 'R': 18, 'S': 19, 'T': 20,
      'U': 21, 'V': 22, 'W': 23, 'X': 24, 'Y': 25, 'Z': 26,
      'Ä': 27, 'Ö': 28, 'Ü': 29, 'ß': 30
    }
  },
  'altdeutsch-mittelhochdeutsch': {
    name: 'Altdeutsch (Mittelhochdeutsch)',
    description: 'Historisches Alphabet ohne J,Q,V,X,Y (21 Buchstaben)',
    letterValues: {
      'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 9,
      'K': 10, 'L': 11, 'M': 12, 'N': 13, 'O': 14, 'P': 15, 'R': 16, 'S': 17, 'T': 18,
      'U': 19, 'W': 20, 'Z': 21, 'Ä': 22, 'Ö': 23, 'Ü': 24
    }
  },
  'runisch': {
    name: 'Runenschrift (Elder Futhark)',
    description: 'Germanische Runen mit 24 Zeichen',
    letterValues: {
      'F': 1, 'U': 2, 'TH': 3, 'A': 4, 'R': 5, 'K': 6, 'G': 7, 'W': 8, 'H': 9, 'N': 10,
      'I': 11, 'J': 12, 'EI': 13, 'P': 14, 'Z': 15, 'S': 16, 'T': 17, 'B': 18, 'E': 19,
      'M': 20, 'L': 21, 'NG': 22, 'D': 23, 'O': 24
    }
  }
};

export const calculateLetterSum = (word: string, alphabetType: AlphabetType = 'latin'): number => {
  const system = alphabetSystems[alphabetType];
  
  const numberMatches = word.match(/\d+/g);
  let numberSum = 0;
  if (numberMatches) {
    numberSum = numberMatches.reduce((sum, num) => sum + parseInt(num), 0);
  }
  
  const cleanWord = word.toUpperCase().replace(/[^A-ZÜÄÖ]/g, '');
  
  let sum = 0;
  for (const char of cleanWord) {
    const value = system.letterValues[char];
    if (value) {
      sum += value;
    }
  }
  
  return sum + numberSum;
};
```

---

## 2. Datenbank-Schema (SQL Migration)

Führe diese Migration im neuen Projekt aus, um die erforderlichen Tabellen zu erstellen:

```sql
-- =====================================================
-- MORPHISCHES FELD ENGINE - DATENBANK SCHEMA
-- =====================================================

-- 1. PATIENTEN TABELLE (Standalone Version)
CREATE TABLE public.patients (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL,
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  birth_date TEXT NOT NULL,
  birth_place TEXT NOT NULL,
  image_signature TEXT,
  image_signature_active BOOLEAN DEFAULT true,
  personal_rate TEXT,
  hardware_config JSONB,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Enable RLS
ALTER TABLE public.patients ENABLE ROW LEVEL SECURITY;

-- RLS Policies for patients
CREATE POLICY "Users can view their own patients" 
ON public.patients FOR SELECT 
USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own patients" 
ON public.patients FOR INSERT 
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own patients" 
ON public.patients FOR UPDATE 
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own patients" 
ON public.patients FOR DELETE 
USING (auth.uid() = user_id);

-- 2. MORPHISCHE FELD BERECHNUNGEN ARCHIV
CREATE TABLE public.morphic_field_calculations (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL,
  patient_id UUID REFERENCES public.patients(id),
  input_word TEXT NOT NULL,
  geometric_form TEXT NOT NULL,
  intention TEXT NOT NULL,
  total_wave_function NUMERIC NOT NULL,
  field_strength NUMERIC NOT NULL,
  coherence NUMERIC NOT NULL,
  resonance_frequency NUMERIC NOT NULL,
  quantum_component NUMERIC,
  numerical_factor NUMERIC,
  geometric_factor NUMERIC,
  intention_factor NUMERIC,
  hardware_factor NUMERIC,
  client_wave_function NUMERIC,
  tcm_analysis JSONB,
  bohm_integration JSONB,
  personal_signature JSONB,
  recommendations JSONB,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Enable RLS
ALTER TABLE public.morphic_field_calculations ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view their own calculations" 
ON public.morphic_field_calculations FOR SELECT 
USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own calculations" 
ON public.morphic_field_calculations FOR INSERT 
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own calculations" 
ON public.morphic_field_calculations FOR DELETE 
USING (auth.uid() = user_id);

-- 3. STORAGE BUCKET FÜR KLIENTEN-BILDER
INSERT INTO storage.buckets (id, name, public) 
VALUES ('client-signatures', 'client-signatures', false)
ON CONFLICT (id) DO NOTHING;

-- Storage Policies
CREATE POLICY "Users can upload their own signatures"
ON storage.objects FOR INSERT
WITH CHECK (
  bucket_id = 'client-signatures' AND 
  auth.uid()::text = (storage.foldername(name))[1]
);

CREATE POLICY "Users can view their own signatures"
ON storage.objects FOR SELECT
USING (
  bucket_id = 'client-signatures' AND 
  auth.uid()::text = (storage.foldername(name))[1]
);

CREATE POLICY "Users can delete their own signatures"
ON storage.objects FOR DELETE
USING (
  bucket_id = 'client-signatures' AND 
  auth.uid()::text = (storage.foldername(name))[1]
);

-- 4. Updated_at Trigger
CREATE OR REPLACE FUNCTION public.handle_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_patients_updated_at
BEFORE UPDATE ON public.patients
FOR EACH ROW
EXECUTE FUNCTION public.handle_updated_at();
```

---

## 3. Dependencies (package.json)

Das neue Projekt benötigt folgende Abhängigkeiten:

```json
{
  "dependencies": {
    "@radix-ui/react-accordion": "^1.2.0",
    "@radix-ui/react-dialog": "^1.1.2",
    "@radix-ui/react-label": "^2.1.0",
    "@radix-ui/react-progress": "^1.1.0",
    "@radix-ui/react-select": "^2.1.1",
    "@radix-ui/react-switch": "^1.1.0",
    "@radix-ui/react-tabs": "^1.1.0",
    "@radix-ui/react-tooltip": "^1.1.4",
    "@supabase/supabase-js": "^2.75.1",
    "@tanstack/react-query": "^5.56.2",
    "class-variance-authority": "^0.7.1",
    "clsx": "^2.1.1",
    "lucide-react": "^0.462.0",
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^6.26.2",
    "sonner": "^1.5.0",
    "tailwind-merge": "^2.5.2",
    "tailwindcss-animate": "^1.0.7"
  }
}
```

---

## 4. Schritt-für-Schritt Anleitung

### Phase 1: Projekt Setup (5 Minuten)

1. **Neues Lovable Projekt erstellen** unter [lovable.dev](https://lovable.dev)
2. **Lovable Cloud aktivieren** (für Supabase-Integration)
3. **Auth konfigurieren**: Auto-Confirm Email aktivieren

### Phase 2: Dateien Kopieren (15 Minuten)

Sage im Chat des neuen Projekts:

```
Erstelle mir bitte folgende Dateien für eine Morphische Feld-Engine:

1. src/utils/alphabetSystems.ts - Alphabet-Systeme für Copen-Rate Berechnung
2. src/utils/hardwareAlgorithms.ts - Kozyrev Hardware-Modulation  
3. src/utils/copenRateGenerator.ts - Bruce Copen Raten-Generator
4. src/utils/morphicFieldEngine.ts - Kern-Engine für Morphische Felder
5. src/utils/clientFieldAlgorithms.ts - Klienten-Algorithmen mit TCM
6. src/components/MorphicFieldCalculator.tsx - Hauptrechner-Komponente
7. src/components/ClientFieldCalculator.tsx - Klienten-Feld-Rechner
8. src/pages/Index.tsx - Hauptseite mit beiden Rechnern

Die Formel ist: Ψ_total(x,t) = Σn αn |ψn⟩ e^(-iEnt/ℏ) × C × G × I
```

Dann **kopiere den Inhalt jeder Datei** aus dieser Dokumentation oder dem originalen Projekt.

### Phase 3: Datenbank einrichten (5 Minuten)

Sage im Chat:

```
Erstelle bitte die Datenbank-Tabellen:
1. patients - für Klientendaten mit RLS
2. morphic_field_calculations - für Berechnungsarchiv
3. Storage Bucket 'client-signatures' für Bild-Uploads
```

### Phase 4: Test (5 Minuten)

1. Registriere einen Test-User
2. Erstelle einen Test-Patienten
3. Führe eine Standard-Berechnung durch
4. Führe eine Klienten-Feldberechnung durch
5. Lade ein Test-Bild hoch

---

## 5. Deaktivierung im Resonanz Explorer

Nach erfolgreichem Test im neuen Projekt, sage im **Resonanz Explorer**:

```
Bitte deaktiviere die Morphische Feld-Engine Route (/morphic-field) und entferne alle Links zur Morphic Field Page aus der Navigation. Die Engine wurde in ein separates Projekt ausgelagert.
```

Dies wird:
- Die Route `/morphic-field` aus `App.tsx` entfernen
- Alle Navigations-Links zur Morphic Field Page entfernen
- Die Dateien können optional gelöscht oder archiviert werden

---

## 6. Wichtige Hinweise

### Daten-Isolation
Die neue Engine hat eine **komplett separate Datenbank** und keine Verbindung zum Resonanz Explorer. Es gibt keine Überschneidungen bei:
- Harmonisierungs-Sessions
- Patienten-Daten
- Berechnungs-Archive

### Patienten-Migration (Optional)
Falls existierende Patienten übernommen werden sollen:

```sql
-- Im NEUEN Projekt ausführen nach Export aus altem Projekt
INSERT INTO patients (id, user_id, first_name, last_name, birth_date, birth_place, ...)
SELECT id, user_id, first_name, last_name, birth_date, birth_place, ...
FROM exported_patients_data;
```

### Authentifizierung
Das neue Projekt hat ein **eigenes Auth-System**. Benutzer müssen sich neu registrieren.

---

## 7. Zusammenfassung der zu kopierenden Dateien

| Datei | Zeilen | Beschreibung |
|-------|--------|--------------|
| `src/utils/alphabetSystems.ts` | 72 | Alphabet-Werte für Rate-Berechnung |
| `src/utils/hardwareAlgorithms.ts` | 412 | Kozyrev-Hardware-Modulation |
| `src/utils/copenRateGenerator.ts` | 723 | Bruce Copen V4 Algorithmus |
| `src/utils/morphicFieldEngine.ts` | 355 | Kern-Engine mit Quantenformel |
| `src/utils/clientFieldAlgorithms.ts` | 468 | TCM/Bohm-Integration |
| `src/components/MorphicFieldCalculator.tsx` | 299 | Standard-Rechner UI |
| `src/components/ClientFieldCalculator.tsx` | 997 | Klienten-Rechner UI |
| `src/pages/MorphicFieldPage.tsx` | 253 | Hauptseite mit Tabs |

**Gesamt: ~3.579 Zeilen Code**

---

## 8. Support

Bei Fragen zur Migration oder technischen Problemen:
1. Überprüfe die Konsole auf Fehler
2. Stelle sicher, dass alle Dependencies installiert sind
3. Überprüfe die RLS-Policies in der Datenbank
4. Teste die Auth-Konfiguration

---

**Erstellt:** 2025-12-31  
**Für:** Resonanz Explorer v2  
**Von:** Lovable AI Assistant

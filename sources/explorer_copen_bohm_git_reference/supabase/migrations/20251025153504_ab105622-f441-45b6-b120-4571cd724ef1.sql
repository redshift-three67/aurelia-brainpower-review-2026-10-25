-- Füge optionales Feld für personalisierte Rate in patients_v2 Tabelle hinzu
ALTER TABLE public.patients_v2
ADD COLUMN IF NOT EXISTS personal_rate TEXT CHECK (LENGTH(personal_rate) >= 8 AND LENGTH(personal_rate) <= 12);

COMMENT ON COLUMN public.patients_v2.personal_rate IS 'Optionale personalisierte Rate (8-12 Stellen) für Klientenberechnungen';
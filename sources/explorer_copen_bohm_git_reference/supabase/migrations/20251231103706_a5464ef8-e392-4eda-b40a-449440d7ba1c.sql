-- Füge source_module Feld zur harmonization_sessions_v2 Tabelle hinzu
ALTER TABLE public.harmonization_sessions_v2 
ADD COLUMN source_module text DEFAULT 'word_energy';

-- Kommentar für Dokumentation
COMMENT ON COLUMN public.harmonization_sessions_v2.source_module IS 'Ursprungsmodul: copen_v2, morphic_field, word_energy, database_manager';
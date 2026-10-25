-- Füge image_signature_active Feld zur patients Tabelle hinzu
ALTER TABLE public.patients 
ADD COLUMN IF NOT EXISTS image_signature_active BOOLEAN DEFAULT true;
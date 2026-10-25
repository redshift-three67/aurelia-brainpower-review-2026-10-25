-- Add image_signature field to patients table for storing AI-generated image signatures
ALTER TABLE public.patients
ADD COLUMN image_signature TEXT;

COMMENT ON COLUMN public.patients.image_signature IS 'AI-generated signature/description of patient image via Ollama llava';
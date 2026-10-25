-- Fix: Set search_path für handle_updated_at Funktion
DROP FUNCTION IF EXISTS public.handle_updated_at() CASCADE;

CREATE OR REPLACE FUNCTION public.handle_updated_at()
RETURNS TRIGGER 
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$;

-- Trigger erneut erstellen
CREATE TRIGGER set_patients_updated_at
  BEFORE UPDATE ON public.patients
  FOR EACH ROW
  EXECUTE FUNCTION public.handle_updated_at();

CREATE TRIGGER set_harmonization_sessions_updated_at
  BEFORE UPDATE ON public.harmonization_sessions
  FOR EACH ROW
  EXECUTE FUNCTION public.handle_updated_at();
-- Tabelle für Patienten (ersetzt IndexedDB)
CREATE TABLE IF NOT EXISTS public.patients (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  birth_date TEXT NOT NULL,
  birth_place TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Tabelle für Harmonisierungs-Sessions mit Background-Job-Support
CREATE TABLE IF NOT EXISTS public.harmonization_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  patient_id UUID NOT NULL REFERENCES public.patients(id) ON DELETE CASCADE,
  word TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'paused', 'cancelled')),
  tested_potency TEXT,
  progress INTEGER DEFAULT 0,
  duration_seconds INTEGER NOT NULL,
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  -- Background job tracking
  job_started_at TIMESTAMPTZ,
  job_last_heartbeat TIMESTAMPTZ,
  remaining_seconds INTEGER
);

-- Enable Row Level Security
ALTER TABLE public.patients ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.harmonization_sessions ENABLE ROW LEVEL SECURITY;

-- Öffentliche Policies (da keine Auth implementiert ist)
CREATE POLICY "Allow all access to patients"
  ON public.patients
  FOR ALL
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Allow all access to harmonization_sessions"
  ON public.harmonization_sessions
  FOR ALL
  USING (true)
  WITH CHECK (true);

-- Funktion für automatische updated_at Aktualisierung
CREATE OR REPLACE FUNCTION public.handle_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger für patients
CREATE TRIGGER set_patients_updated_at
  BEFORE UPDATE ON public.patients
  FOR EACH ROW
  EXECUTE FUNCTION public.handle_updated_at();

-- Trigger für harmonization_sessions
CREATE TRIGGER set_harmonization_sessions_updated_at
  BEFORE UPDATE ON public.harmonization_sessions
  FOR EACH ROW
  EXECUTE FUNCTION public.handle_updated_at();

-- Enable Realtime für Status-Updates
ALTER PUBLICATION supabase_realtime ADD TABLE public.harmonization_sessions;
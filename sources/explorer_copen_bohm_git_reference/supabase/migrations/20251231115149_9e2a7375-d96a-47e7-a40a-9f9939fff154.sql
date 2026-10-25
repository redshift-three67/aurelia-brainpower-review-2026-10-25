-- =====================================================
-- SEPARATE TABELLE FÜR MORPHISCHES FELD ENGINE
-- Option 2: Vollständige Daten-Isolation
-- =====================================================

-- 1. Neue Tabelle für Morphic Field Sessions erstellen
CREATE TABLE public.morphic_field_sessions (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL,
  patient_id UUID NOT NULL,
  word TEXT NOT NULL,
  copen_rate TEXT,
  tested_potency TEXT,
  duration_seconds INTEGER NOT NULL,
  remaining_seconds INTEGER,
  progress INTEGER DEFAULT 0,
  status TEXT NOT NULL DEFAULT 'pending',
  started_at TIMESTAMP WITH TIME ZONE,
  completed_at TIMESTAMP WITH TIME ZONE,
  job_started_at TIMESTAMP WITH TIME ZONE,
  job_last_heartbeat TIMESTAMP WITH TIME ZONE,
  pulse_seconds INTEGER,
  pause_seconds INTEGER,
  pulse_pause_active BOOLEAN DEFAULT FALSE,
  batch_id UUID,
  -- Morphic Field spezifische Felder
  field_intensity NUMERIC,
  coherence NUMERIC,
  geometric_form TEXT,
  intention_type TEXT,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- 2. Index für Performance
CREATE INDEX idx_morphic_field_sessions_user_id ON public.morphic_field_sessions(user_id);
CREATE INDEX idx_morphic_field_sessions_patient_id ON public.morphic_field_sessions(patient_id);
CREATE INDEX idx_morphic_field_sessions_status ON public.morphic_field_sessions(status);
CREATE INDEX idx_morphic_field_sessions_created_at ON public.morphic_field_sessions(created_at DESC);

-- 3. RLS aktivieren
ALTER TABLE public.morphic_field_sessions ENABLE ROW LEVEL SECURITY;

-- 4. RLS Policies erstellen
CREATE POLICY "Users can view their own morphic field sessions"
ON public.morphic_field_sessions
FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own morphic field sessions"
ON public.morphic_field_sessions
FOR INSERT
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own morphic field sessions"
ON public.morphic_field_sessions
FOR UPDATE
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own morphic field sessions"
ON public.morphic_field_sessions
FOR DELETE
USING (auth.uid() = user_id);

CREATE POLICY "Admins can view all morphic field sessions"
ON public.morphic_field_sessions
FOR SELECT
USING (has_role(auth.uid(), 'admin'::app_role));

-- 5. Updated_at Trigger
CREATE TRIGGER update_morphic_field_sessions_updated_at
BEFORE UPDATE ON public.morphic_field_sessions
FOR EACH ROW
EXECUTE FUNCTION public.handle_updated_at();

-- 6. Bestehende Morphic Field Sessions migrieren (Daten kopieren, nicht löschen!)
INSERT INTO public.morphic_field_sessions (
  id, user_id, patient_id, word, copen_rate, tested_potency,
  duration_seconds, remaining_seconds, progress, status,
  started_at, completed_at, job_started_at, job_last_heartbeat,
  pulse_seconds, pause_seconds, pulse_pause_active, batch_id,
  created_at, updated_at
)
SELECT 
  id, user_id, patient_id, word, copen_rate, tested_potency,
  duration_seconds, remaining_seconds, progress, status,
  started_at, completed_at, job_started_at, job_last_heartbeat,
  pulse_seconds, pause_seconds, pulse_pause_active, batch_id,
  created_at, updated_at
FROM public.harmonization_sessions_v2
WHERE source_module = 'morphic_field';

-- 7. Neue Tabelle für Morphic Field Calculations (Berechnungsergebnisse)
CREATE TABLE public.morphic_field_calculations (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL,
  patient_id UUID,
  client_name TEXT NOT NULL,
  field_intensity NUMERIC NOT NULL,
  coherence NUMERIC NOT NULL,
  resonance_frequency NUMERIC NOT NULL,
  geometric_form TEXT,
  intention_type TEXT,
  numerical_sequence JSONB,
  quantum_states JSONB,
  tcm_analysis JSONB,
  bohm_integration JSONB,
  recommendations JSONB,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- 8. RLS für Calculations
ALTER TABLE public.morphic_field_calculations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own morphic field calculations"
ON public.morphic_field_calculations
FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own morphic field calculations"
ON public.morphic_field_calculations
FOR INSERT
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own morphic field calculations"
ON public.morphic_field_calculations
FOR DELETE
USING (auth.uid() = user_id);

CREATE POLICY "Admins can view all morphic field calculations"
ON public.morphic_field_calculations
FOR SELECT
USING (has_role(auth.uid(), 'admin'::app_role));

-- Index für Calculations
CREATE INDEX idx_morphic_field_calculations_user_id ON public.morphic_field_calculations(user_id);
CREATE INDEX idx_morphic_field_calculations_patient_id ON public.morphic_field_calculations(patient_id);
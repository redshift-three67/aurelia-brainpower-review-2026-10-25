-- =========================================
-- Bruce Copen Algorithmus Visualisierung V2
-- Separate Datenbank-Tabellen für V2-Version
-- =========================================

-- 1) Patienten V2
CREATE TABLE IF NOT EXISTS public.patients_v2 (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  birth_date TEXT NOT NULL,
  birth_place TEXT NOT NULL,
  image_signature TEXT,
  image_signature_active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Enable RLS for patients_v2
ALTER TABLE public.patients_v2 ENABLE ROW LEVEL SECURITY;

-- RLS Policies for patients_v2
CREATE POLICY "Users can view their own patients v2"
  ON public.patients_v2
  FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own patients v2"
  ON public.patients_v2
  FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own patients v2"
  ON public.patients_v2
  FOR UPDATE
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own patients v2"
  ON public.patients_v2
  FOR DELETE
  USING (auth.uid() = user_id);

CREATE POLICY "Admins can view all patients v2"
  ON public.patients_v2
  FOR SELECT
  USING (has_role(auth.uid(), 'admin'::app_role));

-- Updated_at trigger for patients_v2
CREATE TRIGGER update_patients_v2_updated_at
  BEFORE UPDATE ON public.patients_v2
  FOR EACH ROW
  EXECUTE FUNCTION public.handle_updated_at();

-- 2) Harmonization Sessions V2
CREATE TABLE IF NOT EXISTS public.harmonization_sessions_v2 (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID,
  patient_id UUID NOT NULL,
  word TEXT NOT NULL,
  copen_rate TEXT,
  tested_potency TEXT,
  status TEXT NOT NULL DEFAULT 'pending'::text,
  duration_seconds INTEGER NOT NULL,
  remaining_seconds INTEGER,
  progress INTEGER DEFAULT 0,
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  job_started_at TIMESTAMPTZ,
  job_last_heartbeat TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Enable RLS for harmonization_sessions_v2
ALTER TABLE public.harmonization_sessions_v2 ENABLE ROW LEVEL SECURITY;

-- RLS Policies for harmonization_sessions_v2
CREATE POLICY "Users can view their own harmonization sessions v2"
  ON public.harmonization_sessions_v2
  FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own harmonization sessions v2"
  ON public.harmonization_sessions_v2
  FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own harmonization sessions v2"
  ON public.harmonization_sessions_v2
  FOR UPDATE
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own harmonization sessions v2"
  ON public.harmonization_sessions_v2
  FOR DELETE
  USING (auth.uid() = user_id);

CREATE POLICY "Admins can view all harmonization sessions v2"
  ON public.harmonization_sessions_v2
  FOR SELECT
  USING (has_role(auth.uid(), 'admin'::app_role));

-- Updated_at trigger for harmonization_sessions_v2
CREATE TRIGGER update_harmonization_sessions_v2_updated_at
  BEFORE UPDATE ON public.harmonization_sessions_v2
  FOR EACH ROW
  EXECUTE FUNCTION public.handle_updated_at();

-- 3) Harmonization Templates V2
CREATE TABLE IF NOT EXISTS public.harmonization_templates_v2 (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  patient_id UUID NOT NULL,
  name TEXT NOT NULL,
  description TEXT,
  sessions JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Enable RLS for harmonization_templates_v2
ALTER TABLE public.harmonization_templates_v2 ENABLE ROW LEVEL SECURITY;

-- RLS Policies for harmonization_templates_v2
CREATE POLICY "Users can view their own templates v2"
  ON public.harmonization_templates_v2
  FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own templates v2"
  ON public.harmonization_templates_v2
  FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own templates v2"
  ON public.harmonization_templates_v2
  FOR UPDATE
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own templates v2"
  ON public.harmonization_templates_v2
  FOR DELETE
  USING (auth.uid() = user_id);

CREATE POLICY "Admins can view all templates v2"
  ON public.harmonization_templates_v2
  FOR SELECT
  USING (has_role(auth.uid(), 'admin'::app_role));

-- Updated_at trigger for harmonization_templates_v2
CREATE TRIGGER update_harmonization_templates_v2_updated_at
  BEFORE UPDATE ON public.harmonization_templates_v2
  FOR EACH ROW
  EXECUTE FUNCTION public.handle_updated_at();

-- 4) Analysis Archives V2
CREATE TABLE IF NOT EXISTS public.analysis_archives_v2 (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  patient_id UUID,
  word TEXT NOT NULL,
  copen_rate TEXT NOT NULL,
  tested_potency TEXT,
  level_1_physical_particles NUMERIC,
  level_2_physical_structure NUMERIC,
  level_3_etheric_prana NUMERIC,
  level_4_etheric_meridians NUMERIC,
  level_5_astral_emotions NUMERIC,
  level_6_astral_thoughts NUMERIC,
  level_7_mental_time NUMERIC,
  level_8_mental_constructs NUMERIC,
  level_9_causal_blueprints NUMERIC,
  level_10_causal_alchemy NUMERIC,
  level_11_atmic_identity NUMERIC,
  level_12_atmic_love NUMERIC,
  level_13_creator NUMERIC,
  highest_resonance_level INTEGER,
  highest_resonance_value NUMERIC,
  analysis_timestamp TIMESTAMPTZ NOT NULL DEFAULT now(),
  patient_data JSONB,
  database_entries TEXT[],
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Enable RLS for analysis_archives_v2
ALTER TABLE public.analysis_archives_v2 ENABLE ROW LEVEL SECURITY;

-- RLS Policies for analysis_archives_v2
CREATE POLICY "Users can view their own analysis archives v2"
  ON public.analysis_archives_v2
  FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own analysis archives v2"
  ON public.analysis_archives_v2
  FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own analysis archives v2"
  ON public.analysis_archives_v2
  FOR UPDATE
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own analysis archives v2"
  ON public.analysis_archives_v2
  FOR DELETE
  USING (auth.uid() = user_id);

CREATE POLICY "Admins can view all analysis archives v2"
  ON public.analysis_archives_v2
  FOR SELECT
  USING (has_role(auth.uid(), 'admin'::app_role));

-- Updated_at trigger for analysis_archives_v2
CREATE TRIGGER update_analysis_archives_v2_updated_at
  BEFORE UPDATE ON public.analysis_archives_v2
  FOR EACH ROW
  EXECUTE FUNCTION public.handle_updated_at();
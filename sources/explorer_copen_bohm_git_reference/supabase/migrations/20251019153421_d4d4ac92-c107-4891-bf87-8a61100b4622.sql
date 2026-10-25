-- Erstelle Tabelle für Analysearchiv mit Ebenen-basierter Resonanz
CREATE TABLE IF NOT EXISTS public.analysis_archives (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL,
  patient_id UUID,
  word TEXT NOT NULL,
  copen_rate TEXT NOT NULL,
  tested_potency TEXT,
  
  -- Ebenen-basierte Resonanzwerte (1-13)
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
  
  -- Höchste Resonanzebene
  highest_resonance_level INTEGER,
  highest_resonance_value NUMERIC,
  
  -- Zusätzliche Metadaten
  analysis_timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  patient_data JSONB,
  database_entries TEXT[],
  
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Enable Row Level Security
ALTER TABLE public.analysis_archives ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view their own analysis archives"
ON public.analysis_archives
FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own analysis archives"
ON public.analysis_archives
FOR INSERT
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own analysis archives"
ON public.analysis_archives
FOR UPDATE
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own analysis archives"
ON public.analysis_archives
FOR DELETE
USING (auth.uid() = user_id);

CREATE POLICY "Admins can view all analysis archives"
ON public.analysis_archives
FOR SELECT
USING (has_role(auth.uid(), 'admin'::app_role));

-- Trigger für updated_at
CREATE TRIGGER update_analysis_archives_updated_at
BEFORE UPDATE ON public.analysis_archives
FOR EACH ROW
EXECUTE FUNCTION public.handle_updated_at();
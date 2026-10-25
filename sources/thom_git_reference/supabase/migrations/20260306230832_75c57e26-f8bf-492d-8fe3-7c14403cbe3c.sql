
-- Phase 4b: Remedy-Datenbank
CREATE TABLE public.remedies (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  name_latin TEXT,
  category TEXT NOT NULL DEFAULT 'homeopathy',
  potency TEXT,
  frequency NUMERIC,
  meridian_associations TEXT[] DEFAULT '{}',
  organ_associations TEXT[] DEFAULT '{}',
  element TEXT,
  emotional_pattern TEXT,
  description TEXT,
  contraindications TEXT,
  source TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE public.remedies ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Remedies are viewable by authenticated users"
ON public.remedies FOR SELECT TO authenticated USING (true);

CREATE POLICY "Remedies are insertable by authenticated users"
ON public.remedies FOR INSERT TO authenticated WITH CHECK (true);

-- Chreode-Pfad-Tracking: Vektor-Trajektorien über Sessions
CREATE TABLE public.chreode_trajectories (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id UUID REFERENCES public.clients(id) ON DELETE CASCADE NOT NULL,
  session_id UUID REFERENCES public.treatment_sessions(id) ON DELETE CASCADE NOT NULL,
  timestamp TIMESTAMPTZ NOT NULL DEFAULT now(),
  dimensions NUMERIC[] NOT NULL,
  entropy_modulation NUMERIC[] DEFAULT '{}',
  bifurcation_risk NUMERIC DEFAULT 0,
  stability NUMERIC DEFAULT 0,
  phase TEXT DEFAULT 'approach',
  chreode_alignment NUMERIC DEFAULT 0,
  attractor_distance NUMERIC DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE public.chreode_trajectories ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Chreode trajectories viewable by authenticated users"
ON public.chreode_trajectories FOR SELECT TO authenticated USING (true);

CREATE POLICY "Chreode trajectories insertable by authenticated users"
ON public.chreode_trajectories FOR INSERT TO authenticated WITH CHECK (true);

-- Index für performante Session-Abfragen
CREATE INDEX idx_chreode_trajectories_client ON public.chreode_trajectories(client_id);
CREATE INDEX idx_chreode_trajectories_session ON public.chreode_trajectories(session_id);
CREATE INDEX idx_remedies_category ON public.remedies(category);
CREATE INDEX idx_remedies_meridian ON public.remedies USING GIN(meridian_associations);

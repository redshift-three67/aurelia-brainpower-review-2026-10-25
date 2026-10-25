
-- Phase 4: Resonanz-Ergebnis-Datenbank
CREATE TABLE public.resonance_results (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id uuid REFERENCES public.treatment_sessions(id) ON DELETE CASCADE NOT NULL,
  client_id uuid REFERENCES public.clients(id) ON DELETE CASCADE NOT NULL,
  scan_point_id uuid REFERENCES public.organ_scan_points(id) ON DELETE SET NULL,
  organ_system text NOT NULL,
  organ_name text NOT NULL,
  body_region text NOT NULL,
  scan_frequency double precision NOT NULL,
  intensity double precision NOT NULL DEFAULT 0,
  polarity text NOT NULL DEFAULT 'neutral',
  dysregulation_score double precision DEFAULT 0,
  harmonic_pattern double precision[] DEFAULT '{}',
  notes text,
  created_at timestamptz NOT NULL DEFAULT now()
);

-- Indizes
CREATE INDEX idx_resonance_results_session ON public.resonance_results(session_id);
CREATE INDEX idx_resonance_results_client ON public.resonance_results(client_id);
CREATE INDEX idx_resonance_results_organ ON public.resonance_results(organ_system);

-- RLS
ALTER TABLE public.resonance_results ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own resonance_results"
  ON public.resonance_results FOR SELECT TO authenticated
  USING (client_id IN (SELECT id FROM public.clients WHERE user_id = auth.uid()));

CREATE POLICY "Users can insert own resonance_results"
  ON public.resonance_results FOR INSERT TO authenticated
  WITH CHECK (client_id IN (SELECT id FROM public.clients WHERE user_id = auth.uid()));

CREATE POLICY "Users can update own resonance_results"
  ON public.resonance_results FOR UPDATE TO authenticated
  USING (client_id IN (SELECT id FROM public.clients WHERE user_id = auth.uid()))
  WITH CHECK (client_id IN (SELECT id FROM public.clients WHERE user_id = auth.uid()));

CREATE POLICY "Users can delete own resonance_results"
  ON public.resonance_results FOR DELETE TO authenticated
  USING (client_id IN (SELECT id FROM public.clients WHERE user_id = auth.uid()));

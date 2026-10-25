
-- Treatment Sessions table for session management
CREATE TABLE public.treatment_sessions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id uuid NOT NULL REFERENCES public.clients(id) ON DELETE CASCADE,
  session_number integer NOT NULL DEFAULT 1,
  session_date timestamp with time zone NOT NULL DEFAULT now(),
  status text NOT NULL DEFAULT 'active',
  notes text,
  vector_snapshot jsonb,
  diagnosis_snapshot jsonb,
  treatment_summary jsonb,
  duration_seconds integer,
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  updated_at timestamp with time zone NOT NULL DEFAULT now()
);

-- Enable RLS
ALTER TABLE public.treatment_sessions ENABLE ROW LEVEL SECURITY;

-- RLS policies: users can only access sessions for their own clients
CREATE POLICY "Users can view own treatment_sessions"
  ON public.treatment_sessions FOR SELECT TO authenticated
  USING (client_id IN (SELECT id FROM public.clients WHERE user_id = auth.uid()));

CREATE POLICY "Users can insert own treatment_sessions"
  ON public.treatment_sessions FOR INSERT TO authenticated
  WITH CHECK (client_id IN (SELECT id FROM public.clients WHERE user_id = auth.uid()));

CREATE POLICY "Users can update own treatment_sessions"
  ON public.treatment_sessions FOR UPDATE TO authenticated
  USING (client_id IN (SELECT id FROM public.clients WHERE user_id = auth.uid()))
  WITH CHECK (client_id IN (SELECT id FROM public.clients WHERE user_id = auth.uid()));

CREATE POLICY "Users can delete own treatment_sessions"
  ON public.treatment_sessions FOR DELETE TO authenticated
  USING (client_id IN (SELECT id FROM public.clients WHERE user_id = auth.uid()));

-- Auto-update updated_at
CREATE TRIGGER update_treatment_sessions_updated_at
  BEFORE UPDATE ON public.treatment_sessions
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

-- Index for fast lookup
CREATE INDEX idx_treatment_sessions_client_id ON public.treatment_sessions(client_id);
CREATE INDEX idx_treatment_sessions_session_date ON public.treatment_sessions(session_date DESC);

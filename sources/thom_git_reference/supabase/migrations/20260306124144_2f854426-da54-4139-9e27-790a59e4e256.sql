
-- Word Energy Collections for multi-focus analysis
CREATE TABLE public.word_energy_collections (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL,
  name TEXT NOT NULL,
  words TEXT[] NOT NULL DEFAULT '{}',
  description TEXT,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

ALTER TABLE public.word_energy_collections ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own collections" ON public.word_energy_collections FOR SELECT TO authenticated USING (user_id = auth.uid());
CREATE POLICY "Users can insert own collections" ON public.word_energy_collections FOR INSERT TO authenticated WITH CHECK (user_id = auth.uid());
CREATE POLICY "Users can update own collections" ON public.word_energy_collections FOR UPDATE TO authenticated USING (user_id = auth.uid()) WITH CHECK (user_id = auth.uid());
CREATE POLICY "Users can delete own collections" ON public.word_energy_collections FOR DELETE TO authenticated USING (user_id = auth.uid());

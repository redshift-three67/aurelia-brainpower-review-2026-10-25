-- Tabelle für persistente Wortenergie-Datenbanken
CREATE TABLE IF NOT EXISTS public.word_databases (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL,
  name TEXT NOT NULL,
  entries TEXT[] NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- RLS aktivieren
ALTER TABLE public.word_databases ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view their own databases"
ON public.word_databases
FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Users can create their own databases"
ON public.word_databases
FOR INSERT
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own databases"
ON public.word_databases
FOR UPDATE
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own databases"
ON public.word_databases
FOR DELETE
USING (auth.uid() = user_id);

-- Admin kann alles sehen
CREATE POLICY "Admins can view all databases"
ON public.word_databases
FOR SELECT
USING (has_role(auth.uid(), 'admin'::app_role));

-- Trigger für updated_at
CREATE TRIGGER update_word_databases_updated_at
BEFORE UPDATE ON public.word_databases
FOR EACH ROW
EXECUTE FUNCTION public.handle_updated_at();

-- Index für Performance
CREATE INDEX idx_word_databases_user_id ON public.word_databases(user_id);
CREATE INDEX idx_word_databases_created_at ON public.word_databases(created_at DESC);
-- Tabelle für Word-Energy Test-Archive
CREATE TABLE public.word_energy_archives (
  id uuid NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id uuid NOT NULL,
  patient_id uuid NOT NULL,
  client_name text NOT NULL,
  client_wellenfunktion numeric,
  results jsonb NOT NULL,
  total_words integer NOT NULL DEFAULT 0,
  average_resonance numeric,
  top_items jsonb,
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  updated_at timestamp with time zone NOT NULL DEFAULT now()
);

-- Enable Row Level Security
ALTER TABLE public.word_energy_archives ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view their own word energy archives" 
ON public.word_energy_archives 
FOR SELECT 
USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own word energy archives" 
ON public.word_energy_archives 
FOR INSERT 
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own word energy archives" 
ON public.word_energy_archives 
FOR UPDATE 
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own word energy archives" 
ON public.word_energy_archives 
FOR DELETE 
USING (auth.uid() = user_id);

CREATE POLICY "Admins can view all word energy archives" 
ON public.word_energy_archives 
FOR SELECT 
USING (has_role(auth.uid(), 'admin'::app_role));

-- Trigger für updated_at
CREATE TRIGGER update_word_energy_archives_updated_at
BEFORE UPDATE ON public.word_energy_archives
FOR EACH ROW
EXECUTE FUNCTION public.handle_updated_at();
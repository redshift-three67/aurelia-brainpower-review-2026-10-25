-- Tabelle für klientenbezogene Harmonisierungs-Templates
CREATE TABLE IF NOT EXISTS public.harmonization_templates (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL,
  patient_id UUID NOT NULL,
  name TEXT NOT NULL,
  description TEXT,
  sessions JSONB NOT NULL, -- Array von Session-Daten
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- RLS aktivieren
ALTER TABLE public.harmonization_templates ENABLE ROW LEVEL SECURITY;

-- RLS-Policies
CREATE POLICY "Users can view their own templates" 
ON public.harmonization_templates 
FOR SELECT 
USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own templates" 
ON public.harmonization_templates 
FOR INSERT 
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own templates" 
ON public.harmonization_templates 
FOR UPDATE 
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own templates" 
ON public.harmonization_templates 
FOR DELETE 
USING (auth.uid() = user_id);

-- Admins können alle Templates sehen
CREATE POLICY "Admins can view all templates" 
ON public.harmonization_templates 
FOR SELECT 
USING (has_role(auth.uid(), 'admin'::app_role));

-- Trigger für updated_at
CREATE TRIGGER update_harmonization_templates_updated_at
BEFORE UPDATE ON public.harmonization_templates
FOR EACH ROW
EXECUTE FUNCTION public.handle_updated_at();
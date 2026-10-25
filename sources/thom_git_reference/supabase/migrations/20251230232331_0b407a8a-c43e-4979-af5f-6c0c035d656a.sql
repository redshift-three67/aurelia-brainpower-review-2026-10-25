-- Word Energies / Resonance Patterns Table
CREATE TABLE public.word_energies (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  word TEXT NOT NULL,
  language TEXT DEFAULT 'de',
  frequency DOUBLE PRECISION NOT NULL,
  amplitude DOUBLE PRECISION DEFAULT 0.5,
  category TEXT NOT NULL,
  organ_system TEXT,
  chakra TEXT,
  meridian TEXT,
  emotional_quality TEXT,
  description TEXT,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Enable RLS
ALTER TABLE public.word_energies ENABLE ROW LEVEL SECURITY;

-- Public read access for word energies (reference data)
CREATE POLICY "Word energies are publicly readable"
ON public.word_energies
FOR SELECT
USING (true);

-- Anatomy Resonance Points Table
CREATE TABLE public.anatomy_resonance_points (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  name TEXT NOT NULL,
  name_latin TEXT,
  body_region TEXT NOT NULL,
  x_position DOUBLE PRECISION NOT NULL,
  y_position DOUBLE PRECISION NOT NULL,
  z_position DOUBLE PRECISION NOT NULL,
  primary_frequency DOUBLE PRECISION NOT NULL,
  harmonic_frequencies DOUBLE PRECISION[],
  organ_associations TEXT[],
  meridian_associations TEXT[],
  emotional_associations TEXT[],
  description TEXT,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Enable RLS
ALTER TABLE public.anatomy_resonance_points ENABLE ROW LEVEL SECURITY;

-- Public read access
CREATE POLICY "Anatomy points are publicly readable"
ON public.anatomy_resonance_points
FOR SELECT
USING (true);

-- Harmonization Jobs Table
CREATE TABLE public.harmonization_jobs (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  client_id UUID NOT NULL REFERENCES public.clients(id) ON DELETE CASCADE,
  vector_id UUID REFERENCES public.client_vectors(id),
  protocol_id UUID REFERENCES public.harmonization_protocols(id),
  job_type TEXT NOT NULL DEFAULT 'harmonization',
  status TEXT NOT NULL DEFAULT 'pending',
  priority INTEGER DEFAULT 1,
  target_frequencies DOUBLE PRECISION[],
  target_anatomy_points UUID[],
  target_word_energies UUID[],
  progress DOUBLE PRECISION DEFAULT 0,
  result_data JSONB,
  error_message TEXT,
  started_at TIMESTAMP WITH TIME ZONE,
  completed_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Enable RLS
ALTER TABLE public.harmonization_jobs ENABLE ROW LEVEL SECURITY;

-- Allow all operations on jobs
CREATE POLICY "Allow all operations on harmonization_jobs"
ON public.harmonization_jobs
FOR ALL
USING (true)
WITH CHECK (true);

-- Insert sample word energies for resonance analysis
INSERT INTO public.word_energies (word, frequency, category, organ_system, chakra, emotional_quality, description) VALUES
('Liebe', 528, 'positive', 'heart', 'heart', 'love', 'Solfeggio MI - DNA Reparatur'),
('Frieden', 639, 'positive', 'thymus', 'heart', 'peace', 'Solfeggio FA - Harmonisierung'),
('Harmonie', 741, 'positive', 'thyroid', 'throat', 'balance', 'Solfeggio SOL - Ausdruck'),
('Gesundheit', 852, 'positive', 'pineal', 'third_eye', 'clarity', 'Solfeggio LA - Intuition'),
('Kraft', 174, 'positive', 'adrenal', 'root', 'strength', 'Solfeggio UT - Erdung'),
('Freude', 396, 'positive', 'sacral', 'sacral', 'joy', 'Solfeggio RE - Befreiung'),
('Angst', 20, 'negative', 'adrenal', 'root', 'fear', 'Niedrige Frequenz - Blockade'),
('Wut', 35, 'negative', 'liver', 'solar_plexus', 'anger', 'Niedrige Frequenz - Stau'),
('Trauer', 15, 'negative', 'lungs', 'heart', 'grief', 'Niedrige Frequenz - Schwere'),
('Stress', 25, 'negative', 'nervous_system', 'solar_plexus', 'tension', 'Niedrige Frequenz - Überlastung');

-- Insert sample anatomy resonance points
INSERT INTO public.anatomy_resonance_points (name, name_latin, body_region, x_position, y_position, z_position, primary_frequency, harmonic_frequencies, organ_associations, meridian_associations) VALUES
('Herz', 'Cor', 'thorax', 0.0, 0.6, 0.1, 528, ARRAY[396.0, 639.0, 741.0], ARRAY['heart', 'pericardium'], ARRAY['heart', 'small_intestine']),
('Leber', 'Hepar', 'abdomen', 0.15, 0.45, 0.05, 317.83, ARRAY[174.0, 285.0], ARRAY['liver', 'gallbladder'], ARRAY['liver', 'gallbladder']),
('Niere Links', 'Ren sinister', 'retroperitoneum', -0.1, 0.4, -0.1, 319.88, ARRAY[396.0, 417.0], ARRAY['kidney', 'adrenal'], ARRAY['kidney', 'bladder']),
('Niere Rechts', 'Ren dexter', 'retroperitoneum', 0.1, 0.38, -0.1, 319.88, ARRAY[396.0, 417.0], ARRAY['kidney', 'adrenal'], ARRAY['kidney', 'bladder']),
('Lunge Links', 'Pulmo sinister', 'thorax', -0.12, 0.65, 0.0, 220, ARRAY[440.0, 330.0], ARRAY['lung'], ARRAY['lung', 'large_intestine']),
('Lunge Rechts', 'Pulmo dexter', 'thorax', 0.12, 0.65, 0.0, 220, ARRAY[440.0, 330.0], ARRAY['lung'], ARRAY['lung', 'large_intestine']),
('Magen', 'Gaster', 'abdomen', -0.05, 0.5, 0.08, 110, ARRAY[220.0, 330.0], ARRAY['stomach'], ARRAY['stomach', 'spleen']),
('Gehirn', 'Cerebrum', 'head', 0.0, 0.9, 0.0, 40, ARRAY[7.83, 14.0, 21.0], ARRAY['brain', 'pineal', 'pituitary'], ARRAY['governing_vessel', 'conception_vessel']),
('Thymus', 'Thymus', 'thorax', 0.0, 0.7, 0.05, 639, ARRAY[528.0, 741.0], ARRAY['thymus'], ARRAY['heart', 'pericardium']),
('Schilddrüse', 'Glandula thyroidea', 'neck', 0.0, 0.8, 0.05, 741, ARRAY[528.0, 852.0], ARRAY['thyroid', 'parathyroid'], ARRAY['triple_warmer']);
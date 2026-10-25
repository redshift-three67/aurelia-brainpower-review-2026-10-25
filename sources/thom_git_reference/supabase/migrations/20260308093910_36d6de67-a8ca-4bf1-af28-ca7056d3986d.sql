
-- Organ-Schemas: Definiert Regionen, Sampling-Regeln und Validierung pro Organ
CREATE TABLE public.organ_schemas (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  organ_code TEXT NOT NULL UNIQUE,
  organ_name TEXT NOT NULL,
  source_dataset TEXT NOT NULL DEFAULT 'BodyParts3D',
  source_concept_id TEXT,
  coordinate_system TEXT NOT NULL DEFAULT 'RAS',
  regions JSONB NOT NULL DEFAULT '[]'::jsonb,
  point_classes TEXT[] NOT NULL DEFAULT ARRAY['A', 'S', 'V']::text[],
  sampling_config JSONB DEFAULT '{}'::jsonb,
  validation_config JSONB DEFAULT '{}'::jsonb,
  mesh_file TEXT,
  version TEXT NOT NULL DEFAULT 'v1.0',
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Organ-Landmarks: Konkrete Punkte mit Koordinaten, Region und Klasse
CREATE TABLE public.organ_landmarks (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  organ_schema_id UUID NOT NULL REFERENCES public.organ_schemas(id) ON DELETE CASCADE,
  point_id TEXT NOT NULL,
  label TEXT NOT NULL,
  point_class TEXT NOT NULL DEFAULT 'A',
  region_code TEXT NOT NULL,
  structure_concept_id TEXT,
  x_position DOUBLE PRECISION NOT NULL,
  y_position DOUBLE PRECISION NOT NULL,
  z_position DOUBLE PRECISION NOT NULL,
  surface_normal_x DOUBLE PRECISION,
  surface_normal_y DOUBLE PRECISION,
  surface_normal_z DOUBLE PRECISION,
  scan_frequency DOUBLE PRECISION,
  harmonic_frequencies DOUBLE PRECISION[] DEFAULT '{}'::double precision[],
  placement_method TEXT NOT NULL DEFAULT 'manual',
  confidence DOUBLE PRECISION NOT NULL DEFAULT 1.0,
  mirror_pair TEXT,
  notes TEXT,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  UNIQUE(organ_schema_id, point_id)
);

-- Indexes für schnelle Abfragen
CREATE INDEX idx_organ_landmarks_schema ON public.organ_landmarks(organ_schema_id);
CREATE INDEX idx_organ_landmarks_organ_class ON public.organ_landmarks(point_class);
CREATE INDEX idx_organ_landmarks_region ON public.organ_landmarks(region_code);

-- RLS aktivieren
ALTER TABLE public.organ_schemas ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.organ_landmarks ENABLE ROW LEVEL SECURITY;

-- Referenzdaten: öffentlich lesbar
CREATE POLICY "Organ schemas are publicly readable"
  ON public.organ_schemas FOR SELECT
  USING (true);

CREATE POLICY "Organ landmarks are publicly readable"
  ON public.organ_landmarks FOR SELECT
  USING (true);

-- Authentifizierte Nutzer können Schemas/Landmarks verwalten
CREATE POLICY "Authenticated users can insert organ_schemas"
  ON public.organ_schemas FOR INSERT
  TO authenticated
  WITH CHECK (true);

CREATE POLICY "Authenticated users can update organ_schemas"
  ON public.organ_schemas FOR UPDATE
  TO authenticated
  USING (true) WITH CHECK (true);

CREATE POLICY "Authenticated users can delete organ_schemas"
  ON public.organ_schemas FOR DELETE
  TO authenticated
  USING (true);

CREATE POLICY "Authenticated users can insert organ_landmarks"
  ON public.organ_landmarks FOR INSERT
  TO authenticated
  WITH CHECK (true);

CREATE POLICY "Authenticated users can update organ_landmarks"
  ON public.organ_landmarks FOR UPDATE
  TO authenticated
  USING (true) WITH CHECK (true);

CREATE POLICY "Authenticated users can delete organ_landmarks"
  ON public.organ_landmarks FOR DELETE
  TO authenticated
  USING (true);

-- Updated_at trigger
CREATE TRIGGER update_organ_schemas_updated_at
  BEFORE UPDATE ON public.organ_schemas
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

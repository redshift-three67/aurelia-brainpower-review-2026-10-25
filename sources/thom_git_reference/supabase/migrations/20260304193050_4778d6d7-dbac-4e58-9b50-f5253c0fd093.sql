-- Anatomie-Modell-Datenbank
CREATE TABLE public.anatomy_models (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL,
  description text,
  source text NOT NULL DEFAULT 'custom',  -- 'z-anatomy', 'bodyparts3d', 'sketchfab', 'custom'
  category text NOT NULL DEFAULT 'full_body',  -- 'full_body', 'organ', 'skeleton', 'meridian_template'
  gender text DEFAULT 'neutral',  -- 'male', 'female', 'neutral'
  file_path text NOT NULL,  -- relativer Pfad in Storage oder public/
  storage_type text NOT NULL DEFAULT 'local',  -- 'local' (public/), 'cloud' (storage bucket)
  file_size_bytes bigint,
  thumbnail_url text,
  license text DEFAULT 'CC-BY-SA',
  license_url text,
  author text,
  version text DEFAULT '1.0',
  supports_meridian_mapping boolean DEFAULT false,
  supports_organ_layers boolean DEFAULT false,
  supports_skeleton boolean DEFAULT false,
  draco_compressed boolean DEFAULT false,
  polygon_count integer,
  body_height_normalized boolean DEFAULT true,  -- ob auf y:-0.15..0.95 normalisiert
  metadata jsonb DEFAULT '{}',
  is_default boolean DEFAULT false,
  sort_order integer DEFAULT 0,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

-- RLS: Öffentlich lesbar, nur Admin kann schreiben
ALTER TABLE public.anatomy_models ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anatomy models are publicly readable"
  ON public.anatomy_models FOR SELECT
  USING (true);

-- Updated-at Trigger
CREATE TRIGGER update_anatomy_models_updated_at
  BEFORE UPDATE ON public.anatomy_models
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

-- Storage Bucket für 3D-Modelle
INSERT INTO storage.buckets (id, name, public)
VALUES ('3d-models', '3d-models', true);

-- Storage RLS: Öffentlich lesbar
CREATE POLICY "3D models are publicly readable"
  ON storage.objects FOR SELECT
  USING (bucket_id = '3d-models');

-- Authentifizierte Benutzer können hochladen
CREATE POLICY "Authenticated users can upload 3D models"
  ON storage.objects FOR INSERT
  TO authenticated
  WITH CHECK (bucket_id = '3d-models');

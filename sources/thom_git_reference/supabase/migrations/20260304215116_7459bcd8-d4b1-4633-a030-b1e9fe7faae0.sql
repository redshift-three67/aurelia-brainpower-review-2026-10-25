
-- NLS Organ-Scan-Punkt-Tabelle
-- Enthält vordefinierte Scan-/Messpunkte pro Organ mit NLS-typischen Frequenzen
CREATE TABLE public.organ_scan_points (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  organ_system text NOT NULL,          -- z.B. 'heart', 'liver', 'kidney'
  organ_name_de text NOT NULL,         -- Deutscher Name
  organ_name_latin text,               -- Lateinischer Name
  point_index integer NOT NULL,        -- Laufende Nummer pro Organ
  point_name text NOT NULL,            -- Beschreibender Name des Scan-Punkts
  scan_frequency double precision NOT NULL,  -- NLS Scan-Frequenz in Hz
  harmonic_frequencies double precision[] DEFAULT '{}',
  x_position double precision NOT NULL,
  y_position double precision NOT NULL,
  z_position double precision NOT NULL,
  tissue_type text,                    -- 'myocardium', 'parenchyma', 'cortex' etc.
  dysregulation_threshold double precision DEFAULT 1.5,
  body_region text NOT NULL,           -- 'thorax', 'abdomen', 'head' etc.
  layer_depth text DEFAULT 'surface',  -- 'surface', 'middle', 'deep'
  description text,
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE(organ_system, point_index)
);

-- RLS: öffentlich lesbar
ALTER TABLE public.organ_scan_points ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Organ scan points are publicly readable"
  ON public.organ_scan_points FOR SELECT
  TO authenticated, anon
  USING (true);

-- Index für schnelle Organ-Abfragen
CREATE INDEX idx_organ_scan_points_organ ON public.organ_scan_points(organ_system);
CREATE INDEX idx_organ_scan_points_region ON public.organ_scan_points(body_region);

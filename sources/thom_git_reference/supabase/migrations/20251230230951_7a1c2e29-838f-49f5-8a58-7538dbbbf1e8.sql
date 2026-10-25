-- Klienten-Tabelle mit biometrischen Identifikationsdaten
CREATE TABLE public.clients (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Biometrische Identifikation (Thom-Feldengine)
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  birth_date DATE NOT NULL,
  birth_place TEXT NOT NULL,
  
  -- Optionales Foto (nur URL/Referenz, nicht das Bild selbst)
  photo_url TEXT,
  
  -- Berechneter Feld-Signatur-Hash (basierend auf biometrischen Daten)
  field_signature TEXT,
  
  -- Zusätzliche Metadaten
  notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Klienten-Vektoren für Trajektorien-Tracking
CREATE TABLE public.client_vectors (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id UUID NOT NULL REFERENCES public.clients(id) ON DELETE CASCADE,
  
  -- 5-dimensionaler Zustandsvektor (normalisiert auf [-1, 1])
  dimension_physical FLOAT NOT NULL,
  dimension_emotional FLOAT NOT NULL,
  dimension_mental FLOAT NOT NULL,
  dimension_energy FLOAT NOT NULL,
  dimension_stress FLOAT NOT NULL,
  
  -- Trajektorie-Metadaten
  attractor_distance FLOAT,
  phase TEXT CHECK (phase IN ('approach', 'transition', 'stable')),
  
  -- Anamnese-Daten
  primary_concern TEXT,
  notes TEXT,
  
  -- Sensor-Daten (optional)
  hrv_value FLOAT,
  gsr_value FLOAT,
  sensor_data JSONB,
  
  -- Session-Info
  session_id TEXT NOT NULL,
  input_method TEXT DEFAULT 'manual' CHECK (input_method IN ('manual', 'sensor', 'hybrid')),
  
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Harmonisierungs-Protokolle
CREATE TABLE public.harmonization_protocols (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id UUID NOT NULL REFERENCES public.clients(id) ON DELETE CASCADE,
  vector_id UUID REFERENCES public.client_vectors(id) ON DELETE SET NULL,
  
  -- Frequenz-Konfiguration
  frequency FLOAT NOT NULL,
  amplitude FLOAT NOT NULL DEFAULT 0.5,
  waveform TEXT NOT NULL DEFAULT 'sine' CHECK (waveform IN ('sine', 'square', 'triangle', 'sawtooth')),
  duration_seconds INTEGER,
  
  -- Output-Modus
  output_type TEXT NOT NULL DEFAULT 'audio' CHECK (output_type IN ('audio', 'electromagnetic', 'dual')),
  
  -- Modulation
  modulation_enabled BOOLEAN DEFAULT false,
  modulation_type TEXT CHECK (modulation_type IN ('am', 'fm', 'pwm')),
  modulation_frequency FLOAT,
  modulation_depth FLOAT,
  
  -- Status
  status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'active', 'completed', 'cancelled')),
  
  -- Ergebnis
  result_notes TEXT,
  effectiveness_rating INTEGER CHECK (effectiveness_rating BETWEEN 1 AND 10),
  
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Indizes für Performance
CREATE INDEX idx_clients_birth_date ON public.clients(birth_date);
CREATE INDEX idx_clients_field_signature ON public.clients(field_signature);
CREATE INDEX idx_client_vectors_client_id ON public.client_vectors(client_id);
CREATE INDEX idx_client_vectors_created_at ON public.client_vectors(created_at DESC);
CREATE INDEX idx_harmonization_client_id ON public.harmonization_protocols(client_id);

-- RLS aktivieren
ALTER TABLE public.clients ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.client_vectors ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.harmonization_protocols ENABLE ROW LEVEL SECURITY;

-- Öffentliche Policies für das lokale NLS-System (ohne Auth)
-- HINWEIS: In Produktion sollten diese durch Auth-basierte Policies ersetzt werden
CREATE POLICY "Allow all operations on clients" ON public.clients FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all operations on client_vectors" ON public.client_vectors FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all operations on harmonization_protocols" ON public.harmonization_protocols FOR ALL USING (true) WITH CHECK (true);

-- Trigger für updated_at
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_clients_updated_at
  BEFORE UPDATE ON public.clients
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

-- Realtime aktivieren
ALTER PUBLICATION supabase_realtime ADD TABLE public.clients;
ALTER PUBLICATION supabase_realtime ADD TABLE public.client_vectors;
ALTER PUBLICATION supabase_realtime ADD TABLE public.harmonization_protocols;
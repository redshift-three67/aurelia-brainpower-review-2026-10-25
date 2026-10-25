-- Erweitere harmonization_sessions_v2 um Impuls/Pausen-Modi
ALTER TABLE harmonization_sessions_v2 
ADD COLUMN IF NOT EXISTS pulse_seconds integer DEFAULT NULL,
ADD COLUMN IF NOT EXISTS pause_seconds integer DEFAULT NULL,
ADD COLUMN IF NOT EXISTS pulse_pause_active boolean DEFAULT false;

-- Kommentar zur Erklärung
COMMENT ON COLUMN harmonization_sessions_v2.pulse_seconds IS 'Impulsdauer in Sekunden (z.B. 3 für 3s Impuls)';
COMMENT ON COLUMN harmonization_sessions_v2.pause_seconds IS 'Pausendauer in Sekunden (z.B. 7 für 7s Pause)';
COMMENT ON COLUMN harmonization_sessions_v2.pulse_pause_active IS 'Ob Impuls/Pausen-Modus aktiv ist';
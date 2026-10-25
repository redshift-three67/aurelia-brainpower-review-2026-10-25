
-- Add visible_layers and applicable_organ_systems to anatomy_models
ALTER TABLE public.anatomy_models 
ADD COLUMN IF NOT EXISTS visible_layers text[] DEFAULT ARRAY['meridians', 'chakras', 'resonance_points', 'nls_scan']::text[],
ADD COLUMN IF NOT EXISTS applicable_organ_systems text[] DEFAULT NULL;

-- Update existing models: full_body models get all layers
UPDATE public.anatomy_models 
SET visible_layers = ARRAY['meridians', 'chakras', 'resonance_points', 'nls_scan']
WHERE category = 'full_body';

-- Organ-specific models should only show NLS for their organ
UPDATE public.anatomy_models 
SET visible_layers = ARRAY['nls_scan'],
    applicable_organ_systems = ARRAY['heart']
WHERE category = 'organ' AND LOWER(name) LIKE '%herz%' OR LOWER(name) LIKE '%heart%';

COMMENT ON COLUMN public.anatomy_models.visible_layers IS 'Which visualization layers are applicable for this model: meridians, chakras, resonance_points, nls_scan';
COMMENT ON COLUMN public.anatomy_models.applicable_organ_systems IS 'Which organ systems NLS points to show (null = all)';

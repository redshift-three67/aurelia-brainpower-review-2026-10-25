-- Fix user-uploaded Herz: category, visible_layers, applicable_organ_systems
UPDATE public.anatomy_models 
SET category = 'organ',
    visible_layers = ARRAY['nls_scan'],
    applicable_organ_systems = ARRAY['heart']
WHERE id = '21ba99ac-9d78-4c85-9acf-d5dd235d61a5';

-- Fix user-uploaded Gehirn: category, visible_layers, applicable_organ_systems  
UPDATE public.anatomy_models 
SET category = 'organ',
    visible_layers = ARRAY['nls_scan'],
    applicable_organ_systems = ARRAY['brain']
WHERE id = '5da847e2-3610-47cf-973d-9753a7689856';

-- Fix pre-seeded organ models missing applicable_organ_systems
UPDATE public.anatomy_models 
SET applicable_organ_systems = ARRAY['brain']
WHERE id = '9b0b01bc-bd54-4a6d-97b9-dff88cfa1c14';

UPDATE public.anatomy_models 
SET applicable_organ_systems = ARRAY['liver']
WHERE id = '5b365108-53e4-449a-b9af-5c2d4a03c0b7';

UPDATE public.anatomy_models 
SET applicable_organ_systems = ARRAY['kidney']
WHERE id = '633335cf-2cfe-4df4-8954-4b580c858063';

-- Fix visible_layers for all organ models to only show nls_scan
UPDATE public.anatomy_models 
SET visible_layers = ARRAY['nls_scan']
WHERE category = 'organ';
-- Fix mirrored x-coordinates for all organ scan points
UPDATE public.organ_scan_points
SET x_position = -x_position
WHERE x_position != 0;
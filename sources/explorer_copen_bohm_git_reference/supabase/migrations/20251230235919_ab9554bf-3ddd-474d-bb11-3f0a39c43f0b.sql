-- Add batch_id column to group sessions from the same analysis
ALTER TABLE public.harmonization_sessions_v2 
ADD COLUMN IF NOT EXISTS batch_id uuid DEFAULT NULL;

-- Add index for efficient batch queries
CREATE INDEX IF NOT EXISTS idx_harmonization_sessions_v2_batch_id 
ON public.harmonization_sessions_v2(batch_id);

-- Add comment for documentation
COMMENT ON COLUMN public.harmonization_sessions_v2.batch_id IS 'Groups sessions created together from a single analysis run';
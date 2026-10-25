-- Add copen_rate column to harmonization_sessions table to store the calculated patient rate
ALTER TABLE public.harmonization_sessions 
ADD COLUMN copen_rate text;
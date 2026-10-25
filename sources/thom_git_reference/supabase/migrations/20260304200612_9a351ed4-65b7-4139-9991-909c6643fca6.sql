CREATE POLICY "Authenticated users can insert anatomy_models"
ON public.anatomy_models FOR INSERT TO authenticated
WITH CHECK (true);

CREATE POLICY "Authenticated users can update anatomy_models"
ON public.anatomy_models FOR UPDATE TO authenticated
USING (true) WITH CHECK (true);

CREATE POLICY "Authenticated users can delete anatomy_models"
ON public.anatomy_models FOR DELETE TO authenticated
USING (true);

-- Security Audit: Fix duplicate policies
DROP POLICY IF EXISTS "Users can view own clients" ON public.clients;
DROP POLICY IF EXISTS "Users can insert own clients" ON public.clients;
DROP POLICY IF EXISTS "Users can update own clients" ON public.clients;
DROP POLICY IF EXISTS "Users can delete own clients" ON public.clients;

CREATE POLICY "Users can view own clients"
ON public.clients FOR SELECT TO authenticated
USING (user_id = auth.uid() OR user_id IS NULL);

CREATE POLICY "Users can insert own clients"
ON public.clients FOR INSERT TO authenticated
WITH CHECK (user_id = auth.uid());

CREATE POLICY "Users can update own clients"
ON public.clients FOR UPDATE TO authenticated
USING (user_id = auth.uid() OR user_id IS NULL)
WITH CHECK (user_id = auth.uid());

CREATE POLICY "Users can delete own clients"
ON public.clients FOR DELETE TO authenticated
USING (user_id = auth.uid());

-- client_vectors
DROP POLICY IF EXISTS "Users can view own client vectors" ON public.client_vectors;
DROP POLICY IF EXISTS "Users can insert own client vectors" ON public.client_vectors;

CREATE POLICY "Users can view own client vectors"
ON public.client_vectors FOR SELECT TO authenticated
USING (EXISTS (
  SELECT 1 FROM public.clients c WHERE c.id = client_vectors.client_id AND (c.user_id = auth.uid() OR c.user_id IS NULL)
));

CREATE POLICY "Users can insert own client vectors"
ON public.client_vectors FOR INSERT TO authenticated
WITH CHECK (EXISTS (
  SELECT 1 FROM public.clients c WHERE c.id = client_vectors.client_id AND (c.user_id = auth.uid() OR c.user_id IS NULL)
));

-- harmonization_protocols
DROP POLICY IF EXISTS "Users can manage own harmonization protocols" ON public.harmonization_protocols;

CREATE POLICY "Users can manage own harmonization protocols"
ON public.harmonization_protocols FOR ALL TO authenticated
USING (EXISTS (SELECT 1 FROM public.clients c WHERE c.id = harmonization_protocols.client_id AND (c.user_id = auth.uid() OR c.user_id IS NULL)))
WITH CHECK (EXISTS (SELECT 1 FROM public.clients c WHERE c.id = harmonization_protocols.client_id AND (c.user_id = auth.uid() OR c.user_id IS NULL)));

-- harmonization_jobs
DROP POLICY IF EXISTS "Users can manage own harmonization jobs" ON public.harmonization_jobs;

CREATE POLICY "Users can manage own harmonization jobs"
ON public.harmonization_jobs FOR ALL TO authenticated
USING (EXISTS (SELECT 1 FROM public.clients c WHERE c.id = harmonization_jobs.client_id AND (c.user_id = auth.uid() OR c.user_id IS NULL)))
WITH CHECK (EXISTS (SELECT 1 FROM public.clients c WHERE c.id = harmonization_jobs.client_id AND (c.user_id = auth.uid() OR c.user_id IS NULL)));

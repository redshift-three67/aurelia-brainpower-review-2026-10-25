-- 1. Add user_id column to clients table
ALTER TABLE public.clients 
  ADD COLUMN user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE;

-- 2. Create index for performance
CREATE INDEX idx_clients_user_id ON public.clients(user_id);

-- 3. Drop old permissive policies
DROP POLICY IF EXISTS "Allow all operations on clients" ON public.clients;
DROP POLICY IF EXISTS "Allow all operations on client_vectors" ON public.client_vectors;
DROP POLICY IF EXISTS "Allow all operations on harmonization_protocols" ON public.harmonization_protocols;
DROP POLICY IF EXISTS "Allow all operations on harmonization_jobs" ON public.harmonization_jobs;

-- 4. Create secure RLS policies for clients
CREATE POLICY "Users can view own clients"
  ON public.clients FOR SELECT
  TO authenticated
  USING (user_id = auth.uid());

CREATE POLICY "Users can insert own clients"
  ON public.clients FOR INSERT
  TO authenticated
  WITH CHECK (user_id = auth.uid());

CREATE POLICY "Users can update own clients"
  ON public.clients FOR UPDATE
  TO authenticated
  USING (user_id = auth.uid())
  WITH CHECK (user_id = auth.uid());

CREATE POLICY "Users can delete own clients"
  ON public.clients FOR DELETE
  TO authenticated
  USING (user_id = auth.uid());

-- 5. Create secure RLS policies for client_vectors (via client ownership)
CREATE POLICY "Users can view own client_vectors"
  ON public.client_vectors FOR SELECT
  TO authenticated
  USING (client_id IN (SELECT id FROM public.clients WHERE user_id = auth.uid()));

CREATE POLICY "Users can insert own client_vectors"
  ON public.client_vectors FOR INSERT
  TO authenticated
  WITH CHECK (client_id IN (SELECT id FROM public.clients WHERE user_id = auth.uid()));

CREATE POLICY "Users can update own client_vectors"
  ON public.client_vectors FOR UPDATE
  TO authenticated
  USING (client_id IN (SELECT id FROM public.clients WHERE user_id = auth.uid()))
  WITH CHECK (client_id IN (SELECT id FROM public.clients WHERE user_id = auth.uid()));

CREATE POLICY "Users can delete own client_vectors"
  ON public.client_vectors FOR DELETE
  TO authenticated
  USING (client_id IN (SELECT id FROM public.clients WHERE user_id = auth.uid()));

-- 6. Create secure RLS policies for harmonization_protocols
CREATE POLICY "Users can view own harmonization_protocols"
  ON public.harmonization_protocols FOR SELECT
  TO authenticated
  USING (client_id IN (SELECT id FROM public.clients WHERE user_id = auth.uid()));

CREATE POLICY "Users can insert own harmonization_protocols"
  ON public.harmonization_protocols FOR INSERT
  TO authenticated
  WITH CHECK (client_id IN (SELECT id FROM public.clients WHERE user_id = auth.uid()));

CREATE POLICY "Users can update own harmonization_protocols"
  ON public.harmonization_protocols FOR UPDATE
  TO authenticated
  USING (client_id IN (SELECT id FROM public.clients WHERE user_id = auth.uid()))
  WITH CHECK (client_id IN (SELECT id FROM public.clients WHERE user_id = auth.uid()));

CREATE POLICY "Users can delete own harmonization_protocols"
  ON public.harmonization_protocols FOR DELETE
  TO authenticated
  USING (client_id IN (SELECT id FROM public.clients WHERE user_id = auth.uid()));

-- 7. Create secure RLS policies for harmonization_jobs
CREATE POLICY "Users can view own harmonization_jobs"
  ON public.harmonization_jobs FOR SELECT
  TO authenticated
  USING (client_id IN (SELECT id FROM public.clients WHERE user_id = auth.uid()));

CREATE POLICY "Users can insert own harmonization_jobs"
  ON public.harmonization_jobs FOR INSERT
  TO authenticated
  WITH CHECK (client_id IN (SELECT id FROM public.clients WHERE user_id = auth.uid()));

CREATE POLICY "Users can update own harmonization_jobs"
  ON public.harmonization_jobs FOR UPDATE
  TO authenticated
  USING (client_id IN (SELECT id FROM public.clients WHERE user_id = auth.uid()))
  WITH CHECK (client_id IN (SELECT id FROM public.clients WHERE user_id = auth.uid()));

CREATE POLICY "Users can delete own harmonization_jobs"
  ON public.harmonization_jobs FOR DELETE
  TO authenticated
  USING (client_id IN (SELECT id FROM public.clients WHERE user_id = auth.uid()));
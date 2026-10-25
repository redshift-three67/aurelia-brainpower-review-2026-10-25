
-- 1. Roles infrastructure
DO $$ BEGIN
  CREATE TYPE public.app_role AS ENUM ('admin', 'moderator', 'user');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

CREATE TABLE IF NOT EXISTS public.user_roles (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  role public.app_role NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (user_id, role)
);

GRANT SELECT ON public.user_roles TO authenticated;
GRANT ALL ON public.user_roles TO service_role;

ALTER TABLE public.user_roles ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view their own roles" ON public.user_roles;
CREATE POLICY "Users can view their own roles" ON public.user_roles
  FOR SELECT TO authenticated USING (user_id = auth.uid());

CREATE OR REPLACE FUNCTION public.has_role(_user_id uuid, _role public.app_role)
RETURNS boolean
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public
AS $$
  SELECT EXISTS (
    SELECT 1 FROM public.user_roles
    WHERE user_id = _user_id AND role = _role
  )
$$;

-- 2. Restrict write policies on reference tables to admins
-- anatomy_models
DROP POLICY IF EXISTS "Authenticated users can insert anatomy_models" ON public.anatomy_models;
DROP POLICY IF EXISTS "Authenticated users can update anatomy_models" ON public.anatomy_models;
DROP POLICY IF EXISTS "Authenticated users can delete anatomy_models" ON public.anatomy_models;
CREATE POLICY "Admins can insert anatomy_models" ON public.anatomy_models
  FOR INSERT TO authenticated WITH CHECK (public.has_role(auth.uid(), 'admin'));
CREATE POLICY "Admins can update anatomy_models" ON public.anatomy_models
  FOR UPDATE TO authenticated USING (public.has_role(auth.uid(), 'admin')) WITH CHECK (public.has_role(auth.uid(), 'admin'));
CREATE POLICY "Admins can delete anatomy_models" ON public.anatomy_models
  FOR DELETE TO authenticated USING (public.has_role(auth.uid(), 'admin'));

-- organ_landmarks
DROP POLICY IF EXISTS "Authenticated users can insert organ_landmarks" ON public.organ_landmarks;
DROP POLICY IF EXISTS "Authenticated users can update organ_landmarks" ON public.organ_landmarks;
DROP POLICY IF EXISTS "Authenticated users can delete organ_landmarks" ON public.organ_landmarks;
CREATE POLICY "Admins can insert organ_landmarks" ON public.organ_landmarks
  FOR INSERT TO authenticated WITH CHECK (public.has_role(auth.uid(), 'admin'));
CREATE POLICY "Admins can update organ_landmarks" ON public.organ_landmarks
  FOR UPDATE TO authenticated USING (public.has_role(auth.uid(), 'admin')) WITH CHECK (public.has_role(auth.uid(), 'admin'));
CREATE POLICY "Admins can delete organ_landmarks" ON public.organ_landmarks
  FOR DELETE TO authenticated USING (public.has_role(auth.uid(), 'admin'));

-- organ_schemas
DROP POLICY IF EXISTS "Authenticated users can insert organ_schemas" ON public.organ_schemas;
DROP POLICY IF EXISTS "Authenticated users can update organ_schemas" ON public.organ_schemas;
DROP POLICY IF EXISTS "Authenticated users can delete organ_schemas" ON public.organ_schemas;
CREATE POLICY "Admins can insert organ_schemas" ON public.organ_schemas
  FOR INSERT TO authenticated WITH CHECK (public.has_role(auth.uid(), 'admin'));
CREATE POLICY "Admins can update organ_schemas" ON public.organ_schemas
  FOR UPDATE TO authenticated USING (public.has_role(auth.uid(), 'admin')) WITH CHECK (public.has_role(auth.uid(), 'admin'));
CREATE POLICY "Admins can delete organ_schemas" ON public.organ_schemas
  FOR DELETE TO authenticated USING (public.has_role(auth.uid(), 'admin'));

-- remedies
DROP POLICY IF EXISTS "Remedies are insertable by authenticated users" ON public.remedies;
CREATE POLICY "Admins can insert remedies" ON public.remedies
  FOR INSERT TO authenticated WITH CHECK (public.has_role(auth.uid(), 'admin'));

-- chreode_trajectories: tie insert to ownership via client
DROP POLICY IF EXISTS "Chreode trajectories insertable by authenticated users" ON public.chreode_trajectories;
CREATE POLICY "Users can insert chreode_trajectories for own clients" ON public.chreode_trajectories
  FOR INSERT TO authenticated
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM public.clients c
      WHERE c.id = chreode_trajectories.client_id
        AND c.user_id = auth.uid()
    )
  );

-- 3. Remove legacy "user_id IS NULL" exposure on clients / client_vectors
DROP POLICY IF EXISTS "Users can view own clients" ON public.clients;
CREATE POLICY "Users can view own clients" ON public.clients
  FOR SELECT TO authenticated USING (user_id = auth.uid());

DROP POLICY IF EXISTS "Users can update own clients" ON public.clients;
CREATE POLICY "Users can update own clients" ON public.clients
  FOR UPDATE TO authenticated USING (user_id = auth.uid()) WITH CHECK (user_id = auth.uid());

-- Remove duplicate / null-owner client_vectors policies
DROP POLICY IF EXISTS "Users can view own client vectors" ON public.client_vectors;
DROP POLICY IF EXISTS "Users can insert own client vectors" ON public.client_vectors;

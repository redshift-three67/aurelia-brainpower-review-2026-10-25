-- DSGVO-konforme Datenstruktur mit sicheren RLS-Policies

-- 1. App-Rollen Enum (DSGVO: Zugriffskontrolle)
CREATE TYPE public.app_role AS ENUM ('admin', 'user');

-- 2. User Roles Tabelle (getrennt von Profilen!)
CREATE TABLE public.user_roles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  role app_role NOT NULL DEFAULT 'user',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(user_id, role)
);

-- 3. Enable RLS auf user_roles
ALTER TABLE public.user_roles ENABLE ROW LEVEL SECURITY;

-- 4. Security Definer Funktion (verhindert rekursive RLS)
CREATE OR REPLACE FUNCTION public.has_role(_user_id UUID, _role app_role)
RETURNS BOOLEAN
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public
AS $$
  SELECT EXISTS (
    SELECT 1
    FROM public.user_roles
    WHERE user_id = _user_id AND role = _role
  )
$$;

-- 5. Sichere RLS-Policy für user_roles
CREATE POLICY "Users can view their own roles"
  ON public.user_roles
  FOR SELECT
  TO authenticated
  USING (auth.uid() = user_id);

CREATE POLICY "Admins can manage all roles"
  ON public.user_roles
  FOR ALL
  TO authenticated
  USING (public.has_role(auth.uid(), 'admin'))
  WITH CHECK (public.has_role(auth.uid(), 'admin'));

-- 6. DSGVO: User-ID Spalte zu Tabellen hinzufügen
ALTER TABLE public.patients ADD COLUMN user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE;
ALTER TABLE public.harmonization_sessions ADD COLUMN user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE;

-- 7. Update RLS-Policies: Nur eigene Daten sichtbar (DSGVO Datenschutz)
DROP POLICY IF EXISTS "Allow all access to patients" ON public.patients;
DROP POLICY IF EXISTS "Allow all access to harmonization_sessions" ON public.harmonization_sessions;

-- Patients: Nur eigene Patienten sehen/bearbeiten
CREATE POLICY "Users can view their own patients"
  ON public.patients
  FOR SELECT
  TO authenticated
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own patients"
  ON public.patients
  FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own patients"
  ON public.patients
  FOR UPDATE
  TO authenticated
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own patients"
  ON public.patients
  FOR DELETE
  TO authenticated
  USING (auth.uid() = user_id);

-- Admins können alle Patienten sehen
CREATE POLICY "Admins can view all patients"
  ON public.patients
  FOR SELECT
  TO authenticated
  USING (public.has_role(auth.uid(), 'admin'));

-- Harmonization Sessions: Nur eigene Sessions
CREATE POLICY "Users can view their own harmonization sessions"
  ON public.harmonization_sessions
  FOR SELECT
  TO authenticated
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own harmonization sessions"
  ON public.harmonization_sessions
  FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own harmonization sessions"
  ON public.harmonization_sessions
  FOR UPDATE
  TO authenticated
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own harmonization sessions"
  ON public.harmonization_sessions
  FOR DELETE
  TO authenticated
  USING (auth.uid() = user_id);

-- Admins können alle Sessions sehen
CREATE POLICY "Admins can view all harmonization sessions"
  ON public.harmonization_sessions
  FOR SELECT
  TO authenticated
  USING (public.has_role(auth.uid(), 'admin'));
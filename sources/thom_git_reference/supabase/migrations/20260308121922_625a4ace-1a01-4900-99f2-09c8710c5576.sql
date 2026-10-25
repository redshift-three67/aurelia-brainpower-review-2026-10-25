
-- Gruppen-Tabelle
CREATE TABLE public.client_groups (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL,
  name text NOT NULL,
  description text,
  color text DEFAULT '#6366f1',
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

-- n:m Zuordnungstabelle
CREATE TABLE public.client_group_members (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  group_id uuid NOT NULL REFERENCES public.client_groups(id) ON DELETE CASCADE,
  client_id uuid NOT NULL REFERENCES public.clients(id) ON DELETE CASCADE,
  added_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE(group_id, client_id)
);

-- RLS aktivieren
ALTER TABLE public.client_groups ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.client_group_members ENABLE ROW LEVEL SECURITY;

-- RLS Policies für client_groups
CREATE POLICY "Users can view own groups" ON public.client_groups FOR SELECT USING (user_id = auth.uid());
CREATE POLICY "Users can insert own groups" ON public.client_groups FOR INSERT WITH CHECK (user_id = auth.uid());
CREATE POLICY "Users can update own groups" ON public.client_groups FOR UPDATE USING (user_id = auth.uid()) WITH CHECK (user_id = auth.uid());
CREATE POLICY "Users can delete own groups" ON public.client_groups FOR DELETE USING (user_id = auth.uid());

-- RLS Policies für client_group_members (über group ownership)
CREATE POLICY "Users can view own group members" ON public.client_group_members FOR SELECT USING (
  group_id IN (SELECT id FROM public.client_groups WHERE user_id = auth.uid())
);
CREATE POLICY "Users can insert own group members" ON public.client_group_members FOR INSERT WITH CHECK (
  group_id IN (SELECT id FROM public.client_groups WHERE user_id = auth.uid())
);
CREATE POLICY "Users can delete own group members" ON public.client_group_members FOR DELETE USING (
  group_id IN (SELECT id FROM public.client_groups WHERE user_id = auth.uid())
);

-- Updated_at trigger
CREATE TRIGGER update_client_groups_updated_at BEFORE UPDATE ON public.client_groups
  FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

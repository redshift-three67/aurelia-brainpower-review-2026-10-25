/**
 * Hook für Klienten-Gruppen-Verwaltung
 * CRUD-Operationen für Gruppen und Mitgliedschaften
 * Vektor-basierte Gruppenanalyse
 */
import { useState, useCallback } from 'react';
import { supabase } from '@/integrations/supabase/client';
import { toast } from 'sonner';

export interface ClientGroup {
  id: string;
  name: string;
  description: string | null;
  color: string;
  memberCount: number;
  createdAt: Date;
}

export interface GroupMember {
  id: string;
  clientId: string;
  firstName: string;
  lastName: string;
  addedAt: Date;
}

export interface GroupVectorSummary {
  groupId: string;
  groupName: string;
  memberCount: number;
  avgDimensions: number[];
  dimensionLabels: string[];
  members: {
    clientId: string;
    name: string;
    dimensions: number[];
    phase: string;
  }[];
}

export function useClientGroups() {
  const [groups, setGroups] = useState<ClientGroup[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const loadGroups = useCallback(async () => {
    setIsLoading(true);
    try {
      // Load groups with member count
      const { data: groupData, error } = await supabase
        .from('client_groups')
        .select('*')
        .order('created_at', { ascending: false });

      if (error) throw error;

      // Get member counts
      const groupsWithCounts: ClientGroup[] = [];
      for (const g of groupData || []) {
        const { count } = await supabase
          .from('client_group_members')
          .select('*', { count: 'exact', head: true })
          .eq('group_id', g.id);

        groupsWithCounts.push({
          id: g.id,
          name: g.name,
          description: g.description,
          color: g.color || '#6366f1',
          memberCount: count || 0,
          createdAt: new Date(g.created_at),
        });
      }

      setGroups(groupsWithCounts);
      return groupsWithCounts;
    } catch (error) {
      console.error('Error loading groups:', error);
      toast.error('Fehler beim Laden der Gruppen');
      return [];
    } finally {
      setIsLoading(false);
    }
  }, []);

  const createGroup = useCallback(async (
    name: string,
    description?: string,
    color?: string
  ): Promise<ClientGroup | null> => {
    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session?.user) throw new Error('Nicht authentifiziert');

      const { data, error } = await supabase
        .from('client_groups')
        .insert({
          name,
          description: description || null,
          color: color || '#6366f1',
          user_id: session.user.id,
        })
        .select()
        .single();

      if (error) throw error;

      const group: ClientGroup = {
        id: data.id,
        name: data.name,
        description: data.description,
        color: data.color || '#6366f1',
        memberCount: 0,
        createdAt: new Date(data.created_at),
      };

      toast.success(`Gruppe "${name}" erstellt`);
      await loadGroups();
      return group;
    } catch (error) {
      console.error('Error creating group:', error);
      toast.error('Fehler beim Erstellen der Gruppe');
      return null;
    }
  }, [loadGroups]);

  const deleteGroup = useCallback(async (groupId: string): Promise<boolean> => {
    try {
      const { error } = await supabase
        .from('client_groups')
        .delete()
        .eq('id', groupId);

      if (error) throw error;
      toast.success('Gruppe gelöscht');
      await loadGroups();
      return true;
    } catch (error) {
      console.error('Error deleting group:', error);
      toast.error('Fehler beim Löschen');
      return false;
    }
  }, [loadGroups]);

  const loadGroupMembers = useCallback(async (groupId: string): Promise<GroupMember[]> => {
    try {
      const { data, error } = await supabase
        .from('client_group_members')
        .select('id, client_id, added_at')
        .eq('group_id', groupId);

      if (error) throw error;

      // Load client names
      const clientIds = (data || []).map(m => m.client_id);
      if (clientIds.length === 0) return [];

      const { data: clients } = await supabase
        .from('clients')
        .select('id, first_name, last_name')
        .in('id', clientIds);

      const clientMap = new Map((clients || []).map(c => [c.id, c]));

      return (data || []).map(m => {
        const client = clientMap.get(m.client_id);
        return {
          id: m.id,
          clientId: m.client_id,
          firstName: client?.first_name || '?',
          lastName: client?.last_name || '?',
          addedAt: new Date(m.added_at),
        };
      });
    } catch (error) {
      console.error('Error loading members:', error);
      return [];
    }
  }, []);

  const addMember = useCallback(async (groupId: string, clientId: string): Promise<boolean> => {
    try {
      const { error } = await supabase
        .from('client_group_members')
        .insert({ group_id: groupId, client_id: clientId });

      if (error) {
        if (error.code === '23505') {
          toast.info('Klient ist bereits in dieser Gruppe');
          return false;
        }
        throw error;
      }
      toast.success('Klient zur Gruppe hinzugefügt');
      await loadGroups();
      return true;
    } catch (error) {
      console.error('Error adding member:', error);
      toast.error('Fehler beim Hinzufügen');
      return false;
    }
  }, [loadGroups]);

  const removeMember = useCallback(async (memberId: string): Promise<boolean> => {
    try {
      const { error } = await supabase
        .from('client_group_members')
        .delete()
        .eq('id', memberId);

      if (error) throw error;
      toast.success('Klient aus Gruppe entfernt');
      await loadGroups();
      return true;
    } catch (error) {
      console.error('Error removing member:', error);
      toast.error('Fehler beim Entfernen');
      return false;
    }
  }, [loadGroups]);

  // Gruppenvektor-Analyse: Alle Vektoren der Gruppenmitglieder laden und aggregieren
  const getGroupVectorSummary = useCallback(async (groupId: string): Promise<GroupVectorSummary | null> => {
    try {
      const group = groups.find(g => g.id === groupId);
      if (!group) return null;

      const members = await loadGroupMembers(groupId);
      if (members.length === 0) return null;

      const clientIds = members.map(m => m.clientId);

      // Neueste Vektoren je Klient laden
      const memberVectors: GroupVectorSummary['members'] = [];
      const allDims: number[][] = [];

      for (const cId of clientIds) {
        const { data } = await supabase
          .from('client_vectors')
          .select('*')
          .eq('client_id', cId)
          .order('created_at', { ascending: false })
          .limit(1);

        if (data && data.length > 0) {
          const v = data[0];
          const dims = [
            v.dimension_physical,
            v.dimension_emotional,
            v.dimension_mental,
            v.dimension_energy,
            v.dimension_stress,
          ];
          allDims.push(dims);
          const member = members.find(m => m.clientId === cId);
          memberVectors.push({
            clientId: cId,
            name: member ? `${member.firstName} ${member.lastName}` : cId,
            dimensions: dims,
            phase: v.phase || 'unknown',
          });
        }
      }

      if (allDims.length === 0) return null;

      // Durchschnittswerte berechnen
      const avgDimensions = [0, 0, 0, 0, 0].map((_, i) =>
        allDims.reduce((sum, d) => sum + d[i], 0) / allDims.length
      );

      return {
        groupId,
        groupName: group.name,
        memberCount: memberVectors.length,
        avgDimensions,
        dimensionLabels: ['Physisch', 'Emotional', 'Mental', 'Energie', 'Stress'],
        members: memberVectors,
      };
    } catch (error) {
      console.error('Error computing group vectors:', error);
      toast.error('Fehler bei der Gruppenanalyse');
      return null;
    }
  }, [groups, loadGroupMembers]);

  return {
    groups,
    isLoading,
    loadGroups,
    createGroup,
    deleteGroup,
    loadGroupMembers,
    addMember,
    removeMember,
    getGroupVectorSummary,
  };
}

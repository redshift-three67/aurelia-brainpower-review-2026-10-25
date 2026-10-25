/**
 * Remedy-Datenbank Hook
 * Verwaltet homöopathische Mittel, Bachblüten, Nosoden mit Frequenzzuordnung
 */
import { useState, useCallback } from 'react';
import { supabase } from '@/integrations/supabase/client';
import { toast } from 'sonner';
import type { Database } from '@/integrations/supabase/types';

type RemedyRow = Database['public']['Tables']['remedies']['Row'];
type RemedyInsert = Database['public']['Tables']['remedies']['Insert'];

export interface Remedy {
  id: string;
  name: string;
  nameLatin: string | null;
  category: string;
  potency: string | null;
  frequency: number | null;
  meridianAssociations: string[];
  organAssociations: string[];
  element: string | null;
  emotionalPattern: string | null;
  description: string | null;
  contraindications: string | null;
  source: string | null;
  createdAt: Date;
}

export type RemedyCategory = 'homeopathy' | 'bach_flower' | 'nosode' | 'tissue_salt' | 'herbal' | 'other';

const CATEGORY_LABELS: Record<string, string> = {
  homeopathy: 'Homöopathie',
  bach_flower: 'Bachblüte',
  nosode: 'Nosode',
  tissue_salt: 'Schüßler-Salz',
  herbal: 'Phytotherapie',
  other: 'Sonstiges',
};

export function useRemedyDatabase() {
  const [remedies, setRemedies] = useState<Remedy[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const mapRow = (row: RemedyRow): Remedy => ({
    id: row.id,
    name: row.name,
    nameLatin: row.name_latin,
    category: row.category,
    potency: row.potency,
    frequency: row.frequency ? Number(row.frequency) : null,
    meridianAssociations: row.meridian_associations || [],
    organAssociations: row.organ_associations || [],
    element: row.element,
    emotionalPattern: row.emotional_pattern,
    description: row.description,
    contraindications: row.contraindications,
    source: row.source,
    createdAt: new Date(row.created_at),
  });

  const loadRemedies = useCallback(async (category?: string, search?: string) => {
    setIsLoading(true);
    try {
      let query = supabase
        .from('remedies')
        .select('*')
        .order('name', { ascending: true })
        .limit(500);

      if (category) {
        query = query.eq('category', category);
      }
      if (search) {
        query = query.or(`name.ilike.%${search}%,name_latin.ilike.%${search}%,description.ilike.%${search}%`);
      }

      const { data, error } = await query;
      if (error) throw error;

      const mapped = (data || []).map(mapRow);
      setRemedies(mapped);
      return mapped;
    } catch (err) {
      console.error('Load remedies error:', err);
      return [];
    } finally {
      setIsLoading(false);
    }
  }, []);

  const addRemedy = useCallback(async (remedy: Omit<Remedy, 'id' | 'createdAt'>) => {
    try {
      const newRemedy: RemedyInsert = {
        name: remedy.name,
        name_latin: remedy.nameLatin,
        category: remedy.category,
        potency: remedy.potency,
        frequency: remedy.frequency,
        meridian_associations: remedy.meridianAssociations,
        organ_associations: remedy.organAssociations,
        element: remedy.element,
        emotional_pattern: remedy.emotionalPattern,
        description: remedy.description,
        contraindications: remedy.contraindications,
        source: remedy.source,
      };

      const { data, error } = await supabase
        .from('remedies')
        .insert(newRemedy)
        .select()
        .single();

      if (error) throw error;

      const mapped = mapRow(data);
      setRemedies(prev => [...prev, mapped].sort((a, b) => a.name.localeCompare(b.name)));
      toast.success(`Mittel "${remedy.name}" hinzugefügt`);
      return mapped;
    } catch (err) {
      console.error('Add remedy error:', err);
      toast.error('Fehler beim Hinzufügen');
      return null;
    }
  }, []);

  const findByFrequency = useCallback(async (frequency: number, tolerance = 5) => {
    try {
      const { data, error } = await supabase
        .from('remedies')
        .select('*')
        .gte('frequency', frequency - tolerance)
        .lte('frequency', frequency + tolerance)
        .order('frequency', { ascending: true });

      if (error) throw error;
      return (data || []).map(mapRow);
    } catch (err) {
      console.error('Find by frequency error:', err);
      return [];
    }
  }, []);

  const findByMeridian = useCallback(async (meridian: string) => {
    try {
      const { data, error } = await supabase
        .from('remedies')
        .select('*')
        .contains('meridian_associations', [meridian]);

      if (error) throw error;
      return (data || []).map(mapRow);
    } catch (err) {
      console.error('Find by meridian error:', err);
      return [];
    }
  }, []);

  return {
    remedies,
    isLoading,
    loadRemedies,
    addRemedy,
    findByFrequency,
    findByMeridian,
    categoryLabels: CATEGORY_LABELS,
  };
}

export default useRemedyDatabase;

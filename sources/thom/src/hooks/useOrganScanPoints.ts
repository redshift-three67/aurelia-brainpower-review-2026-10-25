/**
 * Hook für NLS Organ-Scan-Punkte
 * Lädt vordefinierte Scan-Punkte pro Organ aus der Datenbank
 */
import { useState, useCallback, useMemo } from 'react';
import { supabase } from '@/integrations/supabase/client';
import type { Database } from '@/integrations/supabase/types';

type OrganScanPointRow = Database['public']['Tables']['organ_scan_points']['Row'];

export interface OrganScanPoint {
  id: string;
  organSystem: string;
  organNameDe: string;
  organNameLatin: string | null;
  pointIndex: number;
  pointName: string;
  scanFrequency: number;
  harmonicFrequencies: number[];
  x: number;
  y: number;
  z: number;
  tissueType: string | null;
  dysregulationThreshold: number;
  bodyRegion: string;
  layerDepth: string;
  description: string | null;
}

export interface OrganGroup {
  organSystem: string;
  organNameDe: string;
  organNameLatin: string | null;
  bodyRegion: string;
  points: OrganScanPoint[];
}

const ORGAN_COLORS: Record<string, string> = {
  heart: '#ef4444',
  liver: '#22c55e',
  kidney: '#3b82f6',
  lung: '#94a3b8',
  spleen: '#f59e0b',
  stomach: '#fbbf24',
  pancreas: '#a855f7',
  brain: '#ec4899',
  thyroid: '#06b6d4',
  intestine: '#f97316',
  spine: '#78716c',
  lymph: '#34d399',
  urogenital: '#fb923c',
  adrenal: '#e879f9',
  sensory: '#38bdf8',
};

const TISSUE_ICONS: Record<string, string> = {
  myocardium: '💓',
  parenchyma: '🫁',
  cortex: '🧠',
  node: '⚡',
  valve: '🔄',
  vessel: '🩸',
  gland: '🔬',
  mucosa: '🧫',
  membrane: '🛡️',
  duct: '🔧',
  conduction: '⚡',
  sphincter: '🔒',
  hilum: '🎯',
  endocrine: '💊',
  airway: '💨',
  nucleus: '🧬',
  brainstem: '🧠',
  lymphoid: '🛡️',
  junction: '🔗',
};

export function getOrganColor(organSystem: string): string {
  return ORGAN_COLORS[organSystem] || '#a78bfa';
}

export function getTissueIcon(tissueType: string | null): string {
  return tissueType ? (TISSUE_ICONS[tissueType] || '📍') : '📍';
}

export function useOrganScanPoints() {
  const [points, setPoints] = useState<OrganScanPoint[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedOrgan, setSelectedOrgan] = useState<string | null>(null);
  const [activePoint, setActivePoint] = useState<OrganScanPoint | null>(null);

  const loadPoints = useCallback(async (organSystem?: string) => {
    setIsLoading(true);
    try {
      let query = supabase
        .from('organ_scan_points')
        .select('*')
        .order('organ_system')
        .order('point_index');

      if (organSystem) {
        query = query.eq('organ_system', organSystem);
      }

      const { data, error } = await query;
      if (error) throw error;

      const mapped: OrganScanPoint[] = (data || []).map((p: OrganScanPointRow) => ({
        id: p.id,
        organSystem: p.organ_system,
        organNameDe: p.organ_name_de,
        organNameLatin: p.organ_name_latin,
        pointIndex: p.point_index,
        pointName: p.point_name,
        scanFrequency: p.scan_frequency,
        harmonicFrequencies: p.harmonic_frequencies || [],
        x: p.x_position,
        y: p.y_position,
        z: p.z_position,
        tissueType: p.tissue_type,
        dysregulationThreshold: p.dysregulation_threshold || 1.5,
        bodyRegion: p.body_region,
        layerDepth: p.layer_depth || 'surface',
        description: p.description,
      }));

      setPoints(mapped);
    } catch (err) {
      console.error('Fehler beim Laden der Organ-Scan-Punkte:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const organGroups = useMemo<OrganGroup[]>(() => {
    const groups = new Map<string, OrganGroup>();
    for (const p of points) {
      if (!groups.has(p.organSystem)) {
        groups.set(p.organSystem, {
          organSystem: p.organSystem,
          organNameDe: p.organNameDe,
          organNameLatin: p.organNameLatin,
          bodyRegion: p.bodyRegion,
          points: [],
        });
      }
      groups.get(p.organSystem)!.points.push(p);
    }
    return Array.from(groups.values());
  }, [points]);

  const filteredPoints = useMemo(() => {
    if (!selectedOrgan) return points;
    return points.filter(p => p.organSystem === selectedOrgan);
  }, [points, selectedOrgan]);

  const organSystems = useMemo(() => 
    [...new Set(points.map(p => p.organSystem))],
  [points]);

  return {
    points,
    filteredPoints,
    organGroups,
    organSystems,
    isLoading,
    selectedOrgan,
    setSelectedOrgan,
    activePoint,
    setActivePoint,
    loadPoints,
  };
}

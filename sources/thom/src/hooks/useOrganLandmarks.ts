/**
 * Hook für Organ-Landmarks (definierte anatomische Punkte)
 * Lädt Organ-Schemas und zugehörige Landmarks aus der Datenbank
 * Fallback auf lokale Pilotdaten wenn DB leer
 */
import { useState, useCallback, useMemo } from 'react';
import { supabase } from '@/integrations/supabase/client';
import type { Database, Json } from '@/integrations/supabase/types';
import {
  HEART_SCHEMA, HEART_LANDMARKS,
  BRAIN_SCHEMA, BRAIN_LANDMARKS,
  LIVER_SCHEMA, LIVER_LANDMARKS,
  KIDNEY_SCHEMA, KIDNEY_LANDMARKS,
  LUNG_SCHEMA, LUNG_LANDMARKS,
  SPINE_SCHEMA, SPINE_LANDMARKS,
  WHOLEBODY_SCHEMA, WHOLEBODY_LANDMARKS,
  TCM_SCHEMA, TCM_LANDMARKS,
} from '@/data/anatomy-pilots';

type OrganSchemaRow = Database['public']['Tables']['organ_schemas']['Row'];
type OrganLandmarkRow = Database['public']['Tables']['organ_landmarks']['Row'];
type OrganRegion = { region_code: string; name: string };

const isJsonRecord = (value: Json | null): value is { [key: string]: Json | undefined } =>
  typeof value === 'object' && value !== null && !Array.isArray(value);

const toJsonRecord = (value: Json | null): Record<string, unknown> =>
  isJsonRecord(value) ? (value as Record<string, unknown>) : {};

const toOrganRegions = (value: Json): OrganRegion[] =>
  Array.isArray(value) ? (value as OrganRegion[]) : [];

const hasFullSurfaceNormal = (landmark: OrganLandmarkRow): boolean =>
  landmark.surface_normal_x != null &&
  landmark.surface_normal_y != null &&
  landmark.surface_normal_z != null;

export interface OrganSchema {
  id: string;
  organCode: string;
  organName: string;
  sourceDataset: string;
  sourceConceptId: string | null;
  coordinateSystem: string;
  regions: OrganRegion[];
  pointClasses: string[];
  samplingConfig: Record<string, unknown>;
  validationConfig: Record<string, unknown>;
  meshFile: string | null;
  version: string;
}

export interface OrganLandmark {
  id: string;
  organSchemaId: string;
  pointId: string;
  label: string;
  pointClass: string;
  regionCode: string;
  structureConceptId: string | null;
  x: number;
  y: number;
  z: number;
  surfaceNormal?: [number, number, number];
  scanFrequency: number | null;
  harmonicFrequencies: number[];
  placementMethod: string;
  confidence: number;
  mirrorPair: string | null;
  notes: string | null;
  organCode?: string;
}

const ALL_PILOT_SCHEMAS = [
  { schema: HEART_SCHEMA, landmarks: HEART_LANDMARKS, id: 'pilot-heart' },
  { schema: BRAIN_SCHEMA, landmarks: BRAIN_LANDMARKS, id: 'pilot-brain' },
  { schema: LIVER_SCHEMA, landmarks: LIVER_LANDMARKS, id: 'pilot-liver' },
  { schema: KIDNEY_SCHEMA, landmarks: KIDNEY_LANDMARKS, id: 'pilot-kidney' },
  { schema: LUNG_SCHEMA, landmarks: LUNG_LANDMARKS, id: 'pilot-lung' },
  { schema: SPINE_SCHEMA, landmarks: SPINE_LANDMARKS, id: 'pilot-spine' },
  { schema: WHOLEBODY_SCHEMA, landmarks: WHOLEBODY_LANDMARKS, id: 'pilot-wholebody' },
  { schema: TCM_SCHEMA, landmarks: TCM_LANDMARKS, id: 'pilot-tcm' },
];

export function useOrganLandmarks() {
  const [schemas, setSchemas] = useState<OrganSchema[]>([]);
  const [landmarks, setLandmarks] = useState<OrganLandmark[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedOrgan, setSelectedOrgan] = useState<string | null>(null);
  const [activeLandmark, setActiveLandmark] = useState<OrganLandmark | null>(null);

  const loadFromDatabase = useCallback(async (): Promise<boolean> => {
    try {
      const { data: schemaData, error: schemaError } = await supabase
        .from('organ_schemas')
        .select('*')
        .order('organ_code');

      if (schemaError) throw schemaError;
      if (!schemaData || schemaData.length === 0) return false;

      const mappedSchemas: OrganSchema[] = schemaData.map((s: OrganSchemaRow) => ({
        id: s.id,
        organCode: s.organ_code,
        organName: s.organ_name,
        sourceDataset: s.source_dataset,
        sourceConceptId: s.source_concept_id,
        coordinateSystem: s.coordinate_system,
        regions: toOrganRegions(s.regions),
        pointClasses: s.point_classes || ['A', 'S', 'V'],
        samplingConfig: toJsonRecord(s.sampling_config),
        validationConfig: toJsonRecord(s.validation_config),
        meshFile: s.mesh_file,
        version: s.version,
      }));

      setSchemas(mappedSchemas);

      const schemaIds = mappedSchemas.map(s => s.id);
      const { data: landmarkData, error: landmarkError } = await supabase
        .from('organ_landmarks')
        .select('*')
        .in('organ_schema_id', schemaIds)
        .order('point_id');

      if (landmarkError) throw landmarkError;

      const schemaMap = new Map(mappedSchemas.map(s => [s.id, s.organCode]));

      const mappedLandmarks: OrganLandmark[] = (landmarkData || []).map((l: OrganLandmarkRow) => ({
        id: l.id,
        organSchemaId: l.organ_schema_id,
        pointId: l.point_id,
        label: l.label,
        pointClass: l.point_class,
        regionCode: l.region_code,
        structureConceptId: l.structure_concept_id,
        x: l.x_position,
        y: l.y_position,
        z: l.z_position,
        surfaceNormal: hasFullSurfaceNormal(l)
          ? [l.surface_normal_x!, l.surface_normal_y!, l.surface_normal_z!]
          : undefined,
        scanFrequency: l.scan_frequency,
        harmonicFrequencies: l.harmonic_frequencies || [],
        placementMethod: l.placement_method,
        confidence: l.confidence,
        mirrorPair: l.mirror_pair,
        notes: l.notes,
        organCode: schemaMap.get(l.organ_schema_id),
      }));

      setLandmarks(mappedLandmarks);
      return true;
    } catch (err) {
      console.error('[OrganLandmarks] DB-Ladefehler:', err);
      return false;
    }
  }, []);

  const loadFromPilotData = useCallback(() => {
    const pilotSchemas: OrganSchema[] = ALL_PILOT_SCHEMAS.map(({ schema, id }) => ({
      id,
      organCode: schema.organ_code,
      organName: schema.organ_name,
      sourceDataset: schema.source_dataset,
      sourceConceptId: schema.source_concept_id || null,
      coordinateSystem: schema.coordinate_system,
      regions: schema.regions as { region_code: string; name: string }[],
      pointClasses: [...schema.point_classes],
      samplingConfig: schema.sampling_config || {},
      validationConfig: schema.validation_config || {},
      meshFile: null,
      version: schema.version,
    }));

    const pilotLandmarks: OrganLandmark[] = ALL_PILOT_SCHEMAS.flatMap(({ schema, landmarks: lms, id: schemaId }) =>
      lms.map((l, i: number) => ({
        id: `${schemaId}-${i}`,
        organSchemaId: schemaId,
        pointId: l.point_id,
        label: l.label,
        pointClass: l.point_class,
        regionCode: l.region_code,
        structureConceptId: l.structure_concept_id || null,
        x: l.x,
        y: l.y,
        z: l.z,
        scanFrequency: l.scan_frequency || null,
        harmonicFrequencies: [],
        placementMethod: l.placement_method,
        confidence: l.confidence,
        mirrorPair: l.mirror_pair || null,
        notes: l.notes || null,
        organCode: schema.organ_code,
      }))
    );

    setSchemas(pilotSchemas);
    setLandmarks(pilotLandmarks);
    console.log('[OrganLandmarks] Pilotdaten geladen:', pilotLandmarks.length, 'Punkte aus', pilotSchemas.length, 'Organsystemen');
  }, []);

  const loadLandmarks = useCallback(async () => {
    setIsLoading(true);
    try {
      const loaded = await loadFromDatabase();
      if (!loaded) {
        loadFromPilotData();
      }
    } finally {
      setIsLoading(false);
    }
  }, [loadFromDatabase, loadFromPilotData]);

  const filteredLandmarks = useMemo(() => {
    if (!selectedOrgan) return landmarks;
    return landmarks.filter(l => l.organCode === selectedOrgan);
  }, [landmarks, selectedOrgan]);

  const aLandmarks = useMemo(() =>
    filteredLandmarks.filter(l => l.pointClass === 'A'),
  [filteredLandmarks]);

  const sLandmarks = useMemo(() =>
    filteredLandmarks.filter(l => l.pointClass === 'S'),
  [filteredLandmarks]);

  const organCodes = useMemo(() =>
    [...new Set(landmarks.map(l => l.organCode).filter(Boolean))] as string[],
  [landmarks]);

  const getSchema = useCallback((organCode: string) =>
    schemas.find(s => s.organCode === organCode),
  [schemas]);

  const toScanPoints = useMemo(() => {
    return filteredLandmarks.map(l => ({
      id: l.id,
      organSystem: l.organCode?.toLowerCase() || 'unknown',
      organNameDe: l.label,
      organNameLatin: l.structureConceptId,
      pointIndex: parseInt(l.pointId.split('_').pop() || '0', 10),
      pointName: `${l.pointId}: ${l.label}`,
      scanFrequency: l.scanFrequency || 528,
      harmonicFrequencies: l.harmonicFrequencies,
      x: l.x,
      y: l.y,
      z: l.z,
      tissueType: l.pointClass === 'A' ? 'landmark' : 'scan',
      dysregulationThreshold: 1.5,
      bodyRegion: l.regionCode,
      layerDepth: 'surface' as const,
      description: l.notes,
    }));
  }, [filteredLandmarks]);

  return {
    schemas,
    landmarks,
    filteredLandmarks,
    aLandmarks,
    sLandmarks,
    organCodes,
    isLoading,
    selectedOrgan,
    setSelectedOrgan,
    activeLandmark,
    setActiveLandmark,
    loadLandmarks,
    getSchema,
    toScanPoints,
  };
}

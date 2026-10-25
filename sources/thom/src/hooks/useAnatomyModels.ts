/**
 * Hook für die Anatomie-Modell-Datenbank
 * Lädt verfügbare 3D-Modelle aus der DB und löst Pfade auf
 */
import { useState, useCallback, useEffect } from 'react';
import { supabase } from '@/integrations/supabase/client';

export interface AnatomyModel {
  id: string;
  name: string;
  description: string | null;
  source: string;
  category: string;
  gender: string;
  filePath: string;
  storageType: string;
  fileSize: number | null;
  thumbnailUrl: string | null;
  license: string | null;
  author: string | null;
  version: string | null;
  supportsMeridianMapping: boolean;
  supportsOrganLayers: boolean;
  supportsSkeleton: boolean;
  dracoCompressed: boolean;
  polygonCount: number | null;
  bodyHeightNormalized: boolean;
  isDefault: boolean;
  isAvailable: boolean; // ob die GLB-Datei tatsächlich existiert
  resolvedUrl: string; // aufgelöster URL zum Laden
  visibleLayers: string[]; // which visualization layers are applicable
  applicableOrganSystems: string[] | null; // which organ systems NLS points to show
}

interface AnatomyModelRow {
  id: string;
  name: string;
  description: string | null;
  source: string;
  category: string;
  gender: string;
  storage_type: string | null;
  file_path: string | null;
  file_size_bytes: number | null;
  thumbnail_url: string | null;
  license: string | null;
  author: string | null;
  version: string | null;
  supports_meridian_mapping: boolean | null;
  supports_organ_layers: boolean | null;
  supports_skeleton: boolean | null;
  draco_compressed: boolean | null;
  polygon_count: number | null;
  body_height_normalized: boolean | null;
  is_default: boolean | null;
  visible_layers: string[] | null;
  applicable_organ_systems: string[] | null;
}

const CATEGORY_LABELS: Record<string, string> = {
  full_body: 'Ganzkörper',
  organ: 'Organe',
  skeleton: 'Skelett & Muskulatur',
  meridian_template: 'Meridian-Schablonen',
};

const SOURCE_LABELS: Record<string, string> = {
  'z-anatomy': 'Z-Anatomy',
  'bodyparts3d': 'BodyParts3D (RIKEN)',
  'sketchfab': 'Sketchfab Medical',
  'custom': 'Eigenes Modell',
};

export function getCategoryLabel(category: string) {
  return CATEGORY_LABELS[category] || category;
}

export function getSourceLabel(source: string) {
  return SOURCE_LABELS[source] || source;
}

export function useAnatomyModels() {
  const [models, setModels] = useState<AnatomyModel[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedModel, setSelectedModel] = useState<AnatomyModel | null>(null);

  const resolveModelUrl = useCallback((filePath: string, storageType: string): string => {
    if (storageType === 'local') {
      return filePath; // z.B. /models/human-body.glb
    }
    // Cloud storage URL
    const { data } = supabase.storage.from('3d-models').getPublicUrl(
      filePath.replace('3d-models/', '')
    );
    return data.publicUrl;
  }, []);

  const loadModels = useCallback(async (category?: string) => {
    setIsLoading(true);
    try {
      let query = supabase.from('anatomy_models').select('*').order('sort_order');
      
      if (category) {
        query = query.eq('category', category);
      }

      const { data, error } = await query;
      if (error) throw error;

      // Check which files actually exist in cloud storage
      const { data: storageFiles } = await supabase.storage.from('3d-models').list('', { limit: 500 });
      const existingFiles = new Set((storageFiles || []).map(f => f.name));

      const mapped: AnatomyModel[] = (data || []).map((m: AnatomyModelRow) => {
        const storageType = m.storage_type || 'local';
        const filePath = m.file_path || '';
        const resolvedUrl = resolveModelUrl(filePath, storageType);
        // Local models always available; cloud models only if file actually exists in bucket
        const cloudFileName = filePath.replace('3d-models/', '');
        const isAvailable = storageType === 'local' || existingFiles.has(cloudFileName);

        return {
          id: m.id,
          name: m.name,
          description: m.description,
          source: m.source,
          category: m.category,
          gender: m.gender,
          filePath,
          storageType,
          fileSize: m.file_size_bytes,
          thumbnailUrl: m.thumbnail_url,
          license: m.license,
          author: m.author,
          version: m.version,
          supportsMeridianMapping: m.supports_meridian_mapping ?? false,
          supportsOrganLayers: m.supports_organ_layers ?? false,
          supportsSkeleton: m.supports_skeleton ?? false,
          dracoCompressed: m.draco_compressed ?? false,
          polygonCount: m.polygon_count,
          bodyHeightNormalized: m.body_height_normalized ?? true,
          isDefault: m.is_default ?? false,
          isAvailable,
          resolvedUrl,
          visibleLayers: m.visible_layers || ['meridians', 'chakras', 'resonance_points', 'nls_scan'],
          applicableOrganSystems: m.applicable_organ_systems || null,
        };
      });

      setModels(mapped);

      // Auto-select default model
      setSelectedModel(prev => {
        if (prev) return prev;
        return mapped.find(m => m.isDefault && m.isAvailable) || null;
      });
    } catch (err) {
      console.error('Fehler beim Laden der Modelle:', err);
    } finally {
      setIsLoading(false);
    }
  }, [resolveModelUrl]);

  useEffect(() => {
    loadModels();
  }, [loadModels]);

  const categories = [...new Set(models.map(m => m.category))];

  return {
    models,
    selectedModel,
    setSelectedModel,
    isLoading,
    loadModels,
    categories,
  };
}

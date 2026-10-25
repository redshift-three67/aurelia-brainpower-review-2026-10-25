export const LUNG_SCHEMA = {
  organ_code: 'LUNG_PAIR',
  organ_name: 'Lungs',
  source_dataset: 'BodyParts3D',
  source_concept_id: 'FMA_7195',
  coordinate_system: 'RAS',
  regions: [
    { region_code: 'LUL', name: 'Left Upper Lobe' },
    { region_code: 'LLL', name: 'Left Lower Lobe' },
    { region_code: 'RUL', name: 'Right Upper Lobe' },
    { region_code: 'RML', name: 'Right Middle Lobe' },
    { region_code: 'RLL', name: 'Right Lower Lobe' },
    { region_code: 'TRACHEAL_REF', name: 'Tracheal Reference' },
  ],
  point_classes: ['A', 'S', 'V'] as const,
  sampling_config: {
    method: 'region_geodesic_fps',
    min_surface_distance_mm: 10.0,
    target_points_per_region: { LUL: 5, LLL: 5, RUL: 5, RML: 4, RLL: 5, TRACHEAL_REF: 2 },
  },
  validation_config: {
    must_be_on_surface: true,
    max_projection_error_mm: 1.0,
    require_unique_labels: true,
    require_region_assignment: true,
    mirror_pairs_checked: true,
  },
  version: 'v1.0',
};

export const LUNG_LANDMARKS = [
  { point_id: 'LUNG_A_001', label: 'Left apex', point_class: 'A', region_code: 'LUL', structure_concept_id: 'FMA_7195', x: 54.0, y: 24.0, z: 92.0, scan_frequency: 220.0, placement_method: 'manual', confidence: 1.0, mirror_pair: 'LUNG_A_004', notes: 'Left apex' },
  { point_id: 'LUNG_A_002', label: 'Left base', point_class: 'A', region_code: 'LLL', structure_concept_id: 'FMA_7195', x: 48.0, y: -18.0, z: -72.0, scan_frequency: 220.0, placement_method: 'manual', confidence: 1.0, mirror_pair: 'LUNG_A_005', notes: 'Left base' },
  { point_id: 'LUNG_A_003', label: 'Left hilum ref', point_class: 'A', region_code: 'LUL', structure_concept_id: 'FMA_7195', x: 30.0, y: 4.0, z: 4.0, scan_frequency: 220.0, placement_method: 'manual', confidence: 1.0, mirror_pair: 'LUNG_A_006', notes: 'Left hilum' },
  { point_id: 'LUNG_A_004', label: 'Right apex', point_class: 'A', region_code: 'RUL', structure_concept_id: 'FMA_7195', x: -54.0, y: 24.0, z: 92.0, scan_frequency: 220.0, placement_method: 'mirrored', confidence: 1.0, mirror_pair: 'LUNG_A_001', notes: 'Right apex' },
  { point_id: 'LUNG_A_005', label: 'Right base', point_class: 'A', region_code: 'RLL', structure_concept_id: 'FMA_7195', x: -48.0, y: -18.0, z: -72.0, scan_frequency: 220.0, placement_method: 'mirrored', confidence: 1.0, mirror_pair: 'LUNG_A_002', notes: 'Right base' },
  { point_id: 'LUNG_A_006', label: 'Right hilum ref', point_class: 'A', region_code: 'RUL', structure_concept_id: 'FMA_7195', x: -30.0, y: 4.0, z: 4.0, scan_frequency: 220.0, placement_method: 'mirrored', confidence: 1.0, mirror_pair: 'LUNG_A_003', notes: 'Right hilum' },
  { point_id: 'LUNG_A_007', label: 'Tracheal bifurcation ref', point_class: 'A', region_code: 'TRACHEAL_REF', structure_concept_id: 'FMA_7195', x: 0.0, y: 10.0, z: 36.0, scan_frequency: 220.0, placement_method: 'manual', confidence: 1.0, notes: 'Central airway reference' },
];

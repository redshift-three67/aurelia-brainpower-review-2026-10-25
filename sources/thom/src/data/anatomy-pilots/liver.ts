export const LIVER_SCHEMA = {
  organ_code: 'LIVER',
  organ_name: 'Liver',
  source_dataset: 'BodyParts3D',
  source_concept_id: 'FMA_7197',
  coordinate_system: 'RAS',
  regions: [
    { region_code: 'LEFT_LOBE', name: 'Left Lobe' },
    { region_code: 'RIGHT_LOBE', name: 'Right Lobe' },
    { region_code: 'CAUDATE', name: 'Caudate Lobe' },
    { region_code: 'QUADRATE', name: 'Quadrate Lobe' },
    { region_code: 'HILUM', name: 'Porta Hepatis' },
    { region_code: 'DOME', name: 'Dome' },
  ],
  point_classes: ['A', 'S', 'V'] as const,
  sampling_config: {
    method: 'region_geodesic_fps',
    min_surface_distance_mm: 10.0,
    target_points_per_region: { LEFT_LOBE: 5, RIGHT_LOBE: 8, CAUDATE: 3, QUADRATE: 3, HILUM: 3, DOME: 4 },
  },
  validation_config: {
    must_be_on_surface: true,
    max_projection_error_mm: 1.0,
    require_unique_labels: true,
    require_region_assignment: true,
  },
  version: 'v1.0',
};

export const LIVER_LANDMARKS = [
  { point_id: 'LIVER_A_001', label: 'Liver dome superior', point_class: 'A', region_code: 'DOME', structure_concept_id: 'FMA_7197', x: 0.0, y: 18.0, z: 72.0, scan_frequency: 317.83, placement_method: 'manual', confidence: 1.0, notes: 'Superior dome anchor' },
  { point_id: 'LIVER_A_002', label: 'Left lobe lateral max', point_class: 'A', region_code: 'LEFT_LOBE', structure_concept_id: 'FMA_7197', x: 58.0, y: 8.0, z: 22.0, scan_frequency: 317.83, placement_method: 'manual', confidence: 1.0, notes: 'Left extent' },
  { point_id: 'LIVER_A_003', label: 'Right lobe lateral max', point_class: 'A', region_code: 'RIGHT_LOBE', structure_concept_id: 'FMA_7197', x: -74.0, y: 2.0, z: 18.0, scan_frequency: 317.83, placement_method: 'manual', confidence: 1.0, notes: 'Right extent' },
  { point_id: 'LIVER_A_004', label: 'Inferior border mid', point_class: 'A', region_code: 'RIGHT_LOBE', structure_concept_id: 'FMA_7197', x: -8.0, y: -36.0, z: -12.0, scan_frequency: 317.83, placement_method: 'manual', confidence: 1.0, notes: 'Inferior margin' },
  { point_id: 'LIVER_A_005', label: 'Porta hepatis ref', point_class: 'A', region_code: 'HILUM', structure_concept_id: 'FMA_7197', x: 6.0, y: -10.0, z: 6.0, scan_frequency: 317.83, placement_method: 'manual', confidence: 1.0, notes: 'Hilum reference' },
  { point_id: 'LIVER_A_006', label: 'Caudate reference', point_class: 'A', region_code: 'CAUDATE', structure_concept_id: 'FMA_7197', x: -6.0, y: -2.0, z: 18.0, scan_frequency: 317.83, placement_method: 'manual', confidence: 1.0, notes: 'Caudate lobe anchor' },
];

export const KIDNEY_SCHEMA = {
  organ_code: 'KIDNEY_PAIR',
  organ_name: 'Kidneys',
  source_dataset: 'BodyParts3D',
  source_concept_id: 'FMA_7203',
  coordinate_system: 'RAS',
  regions: [
    { region_code: 'LK_SUP', name: 'Left Kidney Superior' },
    { region_code: 'LK_INF', name: 'Left Kidney Inferior' },
    { region_code: 'LK_HILUM', name: 'Left Kidney Hilum' },
    { region_code: 'RK_SUP', name: 'Right Kidney Superior' },
    { region_code: 'RK_INF', name: 'Right Kidney Inferior' },
    { region_code: 'RK_HILUM', name: 'Right Kidney Hilum' },
    { region_code: 'MIDLINE', name: 'Midline' },
  ],
  point_classes: ['A', 'S', 'V'] as const,
  sampling_config: {
    method: 'region_geodesic_fps',
    min_surface_distance_mm: 6.0,
    target_points_per_region: { LK_SUP: 3, LK_INF: 3, LK_HILUM: 2, RK_SUP: 3, RK_INF: 3, RK_HILUM: 2, MIDLINE: 2 },
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

export const KIDNEY_LANDMARKS = [
  { point_id: 'KIDNEY_A_001', label: 'Left kidney superior pole', point_class: 'A', region_code: 'LK_SUP', structure_concept_id: 'FMA_7203', x: 46.0, y: 12.0, z: 38.0, scan_frequency: 319.88, placement_method: 'manual', confidence: 1.0, mirror_pair: 'KIDNEY_A_004', notes: 'Left superior pole' },
  { point_id: 'KIDNEY_A_002', label: 'Left kidney inferior pole', point_class: 'A', region_code: 'LK_INF', structure_concept_id: 'FMA_7203', x: 42.0, y: -18.0, z: -28.0, scan_frequency: 319.88, placement_method: 'manual', confidence: 1.0, mirror_pair: 'KIDNEY_A_005', notes: 'Left inferior pole' },
  { point_id: 'KIDNEY_A_003', label: 'Left hilum ref', point_class: 'A', region_code: 'LK_HILUM', structure_concept_id: 'FMA_7203', x: 26.0, y: -2.0, z: 6.0, scan_frequency: 319.88, placement_method: 'manual', confidence: 1.0, mirror_pair: 'KIDNEY_A_006', notes: 'Left hilum' },
  { point_id: 'KIDNEY_A_004', label: 'Right kidney superior pole', point_class: 'A', region_code: 'RK_SUP', structure_concept_id: 'FMA_7203', x: -46.0, y: 12.0, z: 38.0, scan_frequency: 319.88, placement_method: 'mirrored', confidence: 1.0, mirror_pair: 'KIDNEY_A_001', notes: 'Right superior pole' },
  { point_id: 'KIDNEY_A_005', label: 'Right kidney inferior pole', point_class: 'A', region_code: 'RK_INF', structure_concept_id: 'FMA_7203', x: -42.0, y: -18.0, z: -28.0, scan_frequency: 319.88, placement_method: 'mirrored', confidence: 1.0, mirror_pair: 'KIDNEY_A_002', notes: 'Right inferior pole' },
  { point_id: 'KIDNEY_A_006', label: 'Right hilum ref', point_class: 'A', region_code: 'RK_HILUM', structure_concept_id: 'FMA_7203', x: -26.0, y: -2.0, z: 6.0, scan_frequency: 319.88, placement_method: 'mirrored', confidence: 1.0, mirror_pair: 'KIDNEY_A_003', notes: 'Right hilum' },
];

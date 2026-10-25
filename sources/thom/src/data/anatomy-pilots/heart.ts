export const HEART_SCHEMA = {
  organ_code: 'HEART',
  organ_name: 'Heart',
  source_dataset: 'BodyParts3D',
  source_concept_id: 'FMA_7088',
  coordinate_system: 'RAS',
  regions: [
    { region_code: 'APEX', name: 'Apex' },
    { region_code: 'BASE', name: 'Base' },
    { region_code: 'LV', name: 'Left Ventricle' },
    { region_code: 'RV', name: 'Right Ventricle' },
    { region_code: 'LA', name: 'Left Atrium' },
    { region_code: 'RA', name: 'Right Atrium' },
    { region_code: 'SEPT', name: 'Septum' },
  ],
  point_classes: ['A', 'S', 'V'] as const,
  sampling_config: {
    method: 'region_geodesic_fps',
    min_surface_distance_mm: 8.0,
    target_points_per_region: { APEX: 2, BASE: 6, LV: 8, RV: 8, LA: 4, RA: 4, SEPT: 4 },
  },
  validation_config: {
    must_be_on_surface: true,
    max_projection_error_mm: 1.0,
    require_unique_labels: true,
    require_region_assignment: true,
  },
  version: 'v1.0',
};

export const HEART_LANDMARKS = [
  { point_id: 'HEART_A_001', label: 'Apex cordis', point_class: 'A', region_code: 'APEX', structure_concept_id: 'FMA_7088', x: 0.0, y: -45.0, z: -80.0, scan_frequency: 528, placement_method: 'manual', confidence: 1.0, notes: 'Primary apex landmark' },
  { point_id: 'HEART_A_002', label: 'Base ventral mid', point_class: 'A', region_code: 'BASE', structure_concept_id: 'FMA_7088', x: 0.0, y: 35.0, z: 55.0, scan_frequency: 528, placement_method: 'manual', confidence: 1.0, notes: 'Anterior base anchor' },
  { point_id: 'HEART_A_003', label: 'Base dorsal mid', point_class: 'A', region_code: 'BASE', structure_concept_id: 'FMA_7088', x: 0.0, y: 15.0, z: 60.0, scan_frequency: 528, placement_method: 'manual', confidence: 1.0, notes: 'Posterior base anchor' },
  { point_id: 'HEART_A_004', label: 'Left lateral max', point_class: 'A', region_code: 'LV', structure_concept_id: 'FMA_7101', x: 42.0, y: 0.0, z: 0.0, scan_frequency: 528, placement_method: 'manual', confidence: 1.0, mirror_pair: 'HEART_A_005', notes: 'Left extent' },
  { point_id: 'HEART_A_005', label: 'Right lateral max', point_class: 'A', region_code: 'RV', structure_concept_id: 'FMA_7098', x: -38.0, y: 0.0, z: 0.0, scan_frequency: 528, placement_method: 'manual', confidence: 1.0, mirror_pair: 'HEART_A_004', notes: 'Right extent' },
  { point_id: 'HEART_A_006', label: 'Septum superior', point_class: 'A', region_code: 'SEPT', structure_concept_id: 'FMA_7133', x: 0.0, y: 8.0, z: 28.0, scan_frequency: 528, placement_method: 'manual', confidence: 1.0, notes: 'Superior septum' },
  { point_id: 'HEART_A_007', label: 'Septum inferior', point_class: 'A', region_code: 'SEPT', structure_concept_id: 'FMA_7133', x: 0.0, y: -18.0, z: -18.0, scan_frequency: 528, placement_method: 'manual', confidence: 1.0, notes: 'Inferior septum' },
  { point_id: 'HEART_A_008', label: 'Aortic root ref', point_class: 'A', region_code: 'BASE', structure_concept_id: 'FMA_3740', x: 10.0, y: 32.0, z: 62.0, scan_frequency: 528, placement_method: 'manual', confidence: 1.0, notes: 'Aortic root reference' },
  { point_id: 'HEART_A_009', label: 'Pulmonary trunk ref', point_class: 'A', region_code: 'BASE', structure_concept_id: 'FMA_8612', x: -8.0, y: 30.0, z: 58.0, scan_frequency: 528, placement_method: 'manual', confidence: 1.0, notes: 'Pulmonary trunk reference' },
];

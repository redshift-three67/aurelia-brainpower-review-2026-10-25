export const WHOLEBODY_SCHEMA = {
  organ_code: 'WHOLEBODY',
  organ_name: 'Whole-body scaffold',
  source_dataset: 'BodyParts3D',
  source_concept_id: 'FMA_20394',
  coordinate_system: 'RAS',
  regions: [
    { region_code: 'HEAD', name: 'Head' },
    { region_code: 'THORAX', name: 'Thorax' },
    { region_code: 'ABDOMEN', name: 'Abdomen' },
    { region_code: 'PELVIS', name: 'Pelvis' },
    { region_code: 'LEFT_UPPER', name: 'Left Upper Limb' },
    { region_code: 'RIGHT_UPPER', name: 'Right Upper Limb' },
    { region_code: 'LEFT_LOWER', name: 'Left Lower Limb' },
    { region_code: 'RIGHT_LOWER', name: 'Right Lower Limb' },
  ],
  point_classes: ['A', 'S', 'V'] as const,
  sampling_config: {
    method: 'region_geodesic_fps',
    min_surface_distance_mm: 20.0,
    target_points_per_region: { HEAD: 4, THORAX: 6, ABDOMEN: 6, PELVIS: 4, LEFT_UPPER: 4, RIGHT_UPPER: 4, LEFT_LOWER: 4, RIGHT_LOWER: 4 },
  },
  validation_config: {
    must_be_on_surface: true,
    require_unique_labels: true,
    require_region_assignment: true,
    mirror_pairs_checked: true,
  },
  version: 'v1.0',
};

export const WHOLEBODY_LANDMARKS = [
  { point_id: 'BODY_A_001', label: 'Vertex body ref', point_class: 'A', region_code: 'HEAD', structure_concept_id: 'FMA_20394', x: 0.0, y: 0.0, z: 168.0, scan_frequency: 136.1, placement_method: 'manual', confidence: 1.0, notes: 'Global superior anchor' },
  { point_id: 'BODY_A_002', label: 'Sternal mid ref', point_class: 'A', region_code: 'THORAX', structure_concept_id: 'FMA_20394', x: 0.0, y: 18.0, z: 58.0, scan_frequency: 136.1, placement_method: 'manual', confidence: 1.0, notes: 'Thoracic center' },
  { point_id: 'BODY_A_003', label: 'Umbilical ref', point_class: 'A', region_code: 'ABDOMEN', structure_concept_id: 'FMA_20394', x: 0.0, y: -6.0, z: 2.0, scan_frequency: 136.1, placement_method: 'manual', confidence: 1.0, notes: 'Abdominal center' },
  { point_id: 'BODY_A_004', label: 'Pelvic mid ref', point_class: 'A', region_code: 'PELVIS', structure_concept_id: 'FMA_20394', x: 0.0, y: -18.0, z: -34.0, scan_frequency: 136.1, placement_method: 'manual', confidence: 1.0, notes: 'Pelvic center' },
  { point_id: 'BODY_A_005', label: 'Left acromion ref', point_class: 'A', region_code: 'LEFT_UPPER', structure_concept_id: 'FMA_20394', x: 78.0, y: 16.0, z: 74.0, scan_frequency: 136.1, placement_method: 'manual', confidence: 1.0, mirror_pair: 'BODY_A_006', notes: 'Left upper limb anchor' },
  { point_id: 'BODY_A_006', label: 'Right acromion ref', point_class: 'A', region_code: 'RIGHT_UPPER', structure_concept_id: 'FMA_20394', x: -78.0, y: 16.0, z: 74.0, scan_frequency: 136.1, placement_method: 'mirrored', confidence: 1.0, mirror_pair: 'BODY_A_005', notes: 'Right upper limb anchor' },
  { point_id: 'BODY_A_007', label: 'Left greater trochanter ref', point_class: 'A', region_code: 'LEFT_LOWER', structure_concept_id: 'FMA_20394', x: 34.0, y: -26.0, z: -62.0, scan_frequency: 136.1, placement_method: 'manual', confidence: 1.0, mirror_pair: 'BODY_A_008', notes: 'Left lower limb anchor' },
  { point_id: 'BODY_A_008', label: 'Right greater trochanter ref', point_class: 'A', region_code: 'RIGHT_LOWER', structure_concept_id: 'FMA_20394', x: -34.0, y: -26.0, z: -62.0, scan_frequency: 136.1, placement_method: 'mirrored', confidence: 1.0, mirror_pair: 'BODY_A_007', notes: 'Right lower limb anchor' },
];

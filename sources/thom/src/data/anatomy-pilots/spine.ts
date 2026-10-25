export const SPINE_SCHEMA = {
  organ_code: 'SPINE_PELVIS',
  organ_name: 'Spine and Pelvis',
  source_dataset: 'BodyParts3D',
  source_concept_id: 'FMA_11966',
  coordinate_system: 'RAS',
  regions: [
    { region_code: 'CERVICAL', name: 'Cervical Spine' },
    { region_code: 'THORACIC', name: 'Thoracic Spine' },
    { region_code: 'LUMBAR', name: 'Lumbar Spine' },
    { region_code: 'SACRUM', name: 'Sacrum' },
    { region_code: 'LEFT_ILIAC', name: 'Left Iliac' },
    { region_code: 'RIGHT_ILIAC', name: 'Right Iliac' },
  ],
  point_classes: ['A', 'S', 'V'] as const,
  sampling_config: {
    method: 'region_geodesic_fps',
    min_surface_distance_mm: 12.0,
    target_points_per_region: { CERVICAL: 4, THORACIC: 6, LUMBAR: 4, SACRUM: 3, LEFT_ILIAC: 3, RIGHT_ILIAC: 3 },
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

export const SPINE_LANDMARKS = [
  { point_id: 'SPINE_A_001', label: 'C7 spinous ref', point_class: 'A', region_code: 'CERVICAL', structure_concept_id: 'FMA_11966', x: 0.0, y: 26.0, z: 118.0, scan_frequency: 194.18, placement_method: 'manual', confidence: 1.0, notes: 'Cervical anchor' },
  { point_id: 'SPINE_A_002', label: 'T12 ref', point_class: 'A', region_code: 'THORACIC', structure_concept_id: 'FMA_11966', x: 0.0, y: 8.0, z: 42.0, scan_frequency: 194.18, placement_method: 'manual', confidence: 1.0, notes: 'Thoracolumbar junction' },
  { point_id: 'SPINE_A_003', label: 'L5 ref', point_class: 'A', region_code: 'LUMBAR', structure_concept_id: 'FMA_11966', x: 0.0, y: -6.0, z: -18.0, scan_frequency: 194.18, placement_method: 'manual', confidence: 1.0, notes: 'Lower lumbar anchor' },
  { point_id: 'SPINE_A_004', label: 'Sacral promontory ref', point_class: 'A', region_code: 'SACRUM', structure_concept_id: 'FMA_11966', x: 0.0, y: -18.0, z: -34.0, scan_frequency: 194.18, placement_method: 'manual', confidence: 1.0, notes: 'Sacral anchor' },
  { point_id: 'SPINE_A_005', label: 'Left ASIS', point_class: 'A', region_code: 'LEFT_ILIAC', structure_concept_id: 'FMA_11966', x: 62.0, y: -22.0, z: -28.0, scan_frequency: 194.18, placement_method: 'manual', confidence: 1.0, mirror_pair: 'SPINE_A_006', notes: 'Left pelvic anchor' },
  { point_id: 'SPINE_A_006', label: 'Right ASIS', point_class: 'A', region_code: 'RIGHT_ILIAC', structure_concept_id: 'FMA_11966', x: -62.0, y: -22.0, z: -28.0, scan_frequency: 194.18, placement_method: 'mirrored', confidence: 1.0, mirror_pair: 'SPINE_A_005', notes: 'Right pelvic anchor' },
];

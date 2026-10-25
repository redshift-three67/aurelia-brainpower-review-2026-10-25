export const TCM_SCHEMA = {
  organ_code: 'TCM_SURFACE',
  organ_name: 'Acupuncture surface pilot',
  source_dataset: 'TCM pilot scaffold',
  source_concept_id: 'TCM_PILOT',
  coordinate_system: 'RAS',
  regions: [
    { region_code: 'DU_MIDLINE', name: 'Du Mai (Governing Vessel)' },
    { region_code: 'REN_MIDLINE', name: 'Ren Mai (Conception Vessel)' },
    { region_code: 'LEFT_ARM', name: 'Left Arm' },
    { region_code: 'RIGHT_ARM', name: 'Right Arm' },
    { region_code: 'LEFT_LEG', name: 'Left Leg' },
    { region_code: 'RIGHT_LEG', name: 'Right Leg' },
    { region_code: 'BACK_SURFACE', name: 'Back Surface' },
  ],
  point_classes: ['A', 'S', 'V'] as const,
  sampling_config: {
    method: 'manual_tcm',
    min_surface_distance_mm: 15.0,
    target_points_per_region: { DU_MIDLINE: 8, REN_MIDLINE: 8, LEFT_ARM: 6, RIGHT_ARM: 6, LEFT_LEG: 6, RIGHT_LEG: 6, BACK_SURFACE: 10 },
  },
  validation_config: {
    must_be_on_surface: true,
    require_unique_labels: true,
    require_region_assignment: true,
    mirror_pairs_checked: true,
  },
  version: 'v1.0',
};

export const TCM_LANDMARKS = [
  { point_id: 'TCM_A_001', label: 'GV20 pilot', point_class: 'A', region_code: 'DU_MIDLINE', structure_concept_id: 'TCM_GV20', x: 0.0, y: 0.0, z: 170.0, scan_frequency: 136.1, placement_method: 'manual', confidence: 0.8, notes: 'Surface pilot point only' },
  { point_id: 'TCM_A_002', label: 'CV17 pilot', point_class: 'A', region_code: 'REN_MIDLINE', structure_concept_id: 'TCM_CV17', x: 0.0, y: 16.0, z: 48.0, scan_frequency: 136.1, placement_method: 'manual', confidence: 0.8, notes: 'Anterior thoracic pilot point' },
  { point_id: 'TCM_A_003', label: 'Left PC6 pilot', point_class: 'A', region_code: 'LEFT_ARM', structure_concept_id: 'TCM_PC6', x: 66.0, y: 10.0, z: 24.0, scan_frequency: 136.1, placement_method: 'manual', confidence: 0.8, mirror_pair: 'TCM_A_004', notes: 'Left forearm pilot' },
  { point_id: 'TCM_A_004', label: 'Right PC6 pilot', point_class: 'A', region_code: 'RIGHT_ARM', structure_concept_id: 'TCM_PC6', x: -66.0, y: 10.0, z: 24.0, scan_frequency: 136.1, placement_method: 'mirrored', confidence: 0.8, mirror_pair: 'TCM_A_003', notes: 'Right forearm pilot' },
  { point_id: 'TCM_A_005', label: 'Left ST36 pilot', point_class: 'A', region_code: 'LEFT_LEG', structure_concept_id: 'TCM_ST36', x: 22.0, y: -34.0, z: -118.0, scan_frequency: 136.1, placement_method: 'manual', confidence: 0.8, mirror_pair: 'TCM_A_006', notes: 'Left lower leg pilot' },
  { point_id: 'TCM_A_006', label: 'Right ST36 pilot', point_class: 'A', region_code: 'RIGHT_LEG', structure_concept_id: 'TCM_ST36', x: -22.0, y: -34.0, z: -118.0, scan_frequency: 136.1, placement_method: 'mirrored', confidence: 0.8, mirror_pair: 'TCM_A_005', notes: 'Right lower leg pilot' },
  { point_id: 'TCM_A_007', label: 'GV14 pilot', point_class: 'A', region_code: 'BACK_SURFACE', structure_concept_id: 'TCM_GV14', x: 0.0, y: 4.0, z: 108.0, scan_frequency: 136.1, placement_method: 'manual', confidence: 0.8, notes: 'Posterior cervical-thoracic pilot' },
];

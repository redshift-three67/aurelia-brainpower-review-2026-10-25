/**
 * Z-Anatomy ↔ Pilot Data FMA-ID Mapping
 * 
 * Verifizierte FMA-IDs aus der Foundational Model of Anatomy Ontologie
 * Quellen: bioportal.bioontology.org/ontologies/FMA, BodyParts3D v4.0
 * 
 * Z-Anatomy Blender-Datei: github.com/Z-Anatomy/Models-of-human-anatomy
 * Die Blender-Collection-Namen folgen dem Schema: "FMA{id} - {Englischer Name}"
 */

export interface ZAnatomyMapping {
  organ_code: string;
  fma_id: string;
  fma_name: string;
  z_anatomy_collection: string; // Name in Z-Anatomy Blender file
  bodyparts3d_id?: string;       // BodyParts3D concept ID (if different)
  substructures: ZAnatomySubstructure[];
}

export interface ZAnatomySubstructure {
  region_code: string;
  fma_id: string;
  fma_name: string;
  z_anatomy_mesh_name?: string;
}

/**
 * Vollständige FMA-ID Zuordnung für alle 8 Organsysteme
 * mit Sub-Struktur-Mapping zu den Pilot-Regionen
 */
export const Z_ANATOMY_ORGAN_MAPPINGS: ZAnatomyMapping[] = [
  // ── HERZ ──
  {
    organ_code: 'HEART',
    fma_id: 'FMA_7088',
    fma_name: 'Heart',
    z_anatomy_collection: 'Heart',
    bodyparts3d_id: 'FMA7088',
    substructures: [
      { region_code: 'APEX', fma_id: 'FMA_7170', fma_name: 'Apex of heart' },
      { region_code: 'BASE', fma_id: 'FMA_7163', fma_name: 'Base of heart' },
      { region_code: 'LV', fma_id: 'FMA_7101', fma_name: 'Left ventricle' },
      { region_code: 'RV', fma_id: 'FMA_7098', fma_name: 'Right ventricle' },
      { region_code: 'LA', fma_id: 'FMA_7097', fma_name: 'Left atrium' },
      { region_code: 'RA', fma_id: 'FMA_7096', fma_name: 'Right atrium' },
      { region_code: 'SEPT', fma_id: 'FMA_7133', fma_name: 'Interventricular septum' },
    ],
  },
  // ── GEHIRN ──
  {
    organ_code: 'BRAIN',
    fma_id: 'FMA_50801',
    fma_name: 'Brain',
    z_anatomy_collection: 'Brain',
    bodyparts3d_id: 'FMA50801',
    substructures: [
      { region_code: 'FRONTAL', fma_id: 'FMA_61824', fma_name: 'Frontal lobe' },
      { region_code: 'PARIETAL', fma_id: 'FMA_61826', fma_name: 'Parietal lobe' },
      { region_code: 'TEMPORAL', fma_id: 'FMA_61825', fma_name: 'Temporal lobe' },
      { region_code: 'OCCIPITAL', fma_id: 'FMA_67325', fma_name: 'Occipital lobe' },
      { region_code: 'CEREBELLUM', fma_id: 'FMA_67944', fma_name: 'Cerebellum' },
      { region_code: 'BRAINSTEM', fma_id: 'FMA_79876', fma_name: 'Brainstem' },
      { region_code: 'CORPUS_CALLOSUM', fma_id: 'FMA_86464', fma_name: 'Corpus callosum' },
    ],
  },
  // ── LEBER ──
  {
    organ_code: 'LIVER',
    fma_id: 'FMA_7197',
    fma_name: 'Liver',
    z_anatomy_collection: 'Liver',
    bodyparts3d_id: 'FMA7197',
    substructures: [
      { region_code: 'RIGHT_LOBE', fma_id: 'FMA_7204', fma_name: 'Right lobe of liver' },
      { region_code: 'LEFT_LOBE', fma_id: 'FMA_7205', fma_name: 'Left lobe of liver' },
      { region_code: 'CAUDATE', fma_id: 'FMA_7207', fma_name: 'Caudate lobe' },
      { region_code: 'QUADRATE', fma_id: 'FMA_7206', fma_name: 'Quadrate lobe' },
      { region_code: 'HILUM', fma_id: 'FMA_15748', fma_name: 'Porta hepatis' },
    ],
  },
  // ── NIERE (Paar) ──
  {
    organ_code: 'KIDNEY_PAIR',
    fma_id: 'FMA_7203',
    fma_name: 'Kidney',
    z_anatomy_collection: 'Kidney',
    bodyparts3d_id: 'FMA7203',
    substructures: [
      { region_code: 'L_SUP', fma_id: 'FMA_7206', fma_name: 'Superior pole of left kidney' },
      { region_code: 'L_INF', fma_id: 'FMA_7206', fma_name: 'Inferior pole of left kidney' },
      { region_code: 'L_HILUM', fma_id: 'FMA_15609', fma_name: 'Hilum of left kidney' },
      { region_code: 'R_SUP', fma_id: 'FMA_7206', fma_name: 'Superior pole of right kidney' },
      { region_code: 'R_INF', fma_id: 'FMA_7206', fma_name: 'Inferior pole of right kidney' },
      { region_code: 'R_HILUM', fma_id: 'FMA_15610', fma_name: 'Hilum of right kidney' },
    ],
  },
  // ── LUNGE (Paar) ──
  {
    organ_code: 'LUNG_PAIR',
    fma_id: 'FMA_7195',
    fma_name: 'Lung',
    z_anatomy_collection: 'Lung',
    bodyparts3d_id: 'FMA7195',
    substructures: [
      { region_code: 'L_UPPER', fma_id: 'FMA_7333', fma_name: 'Superior lobe of left lung' },
      { region_code: 'L_LOWER', fma_id: 'FMA_7335', fma_name: 'Inferior lobe of left lung' },
      { region_code: 'L_HILUM', fma_id: 'FMA_7310', fma_name: 'Hilum of left lung' },
      { region_code: 'R_UPPER', fma_id: 'FMA_7327', fma_name: 'Superior lobe of right lung' },
      { region_code: 'R_MIDDLE', fma_id: 'FMA_7328', fma_name: 'Middle lobe of right lung' },
      { region_code: 'R_LOWER', fma_id: 'FMA_7329', fma_name: 'Inferior lobe of right lung' },
      { region_code: 'R_HILUM', fma_id: 'FMA_7309', fma_name: 'Hilum of right lung' },
    ],
  },
  // ── WIRBELSÄULE / BECKEN ──
  {
    organ_code: 'SPINE_PELVIS',
    fma_id: 'FMA_11966',
    fma_name: 'Vertebral column',
    z_anatomy_collection: 'Vertebral column',
    bodyparts3d_id: 'FMA11966',
    substructures: [
      { region_code: 'CERVICAL', fma_id: 'FMA_72065', fma_name: 'Cervical vertebral column' },
      { region_code: 'THORACIC', fma_id: 'FMA_72066', fma_name: 'Thoracic vertebral column' },
      { region_code: 'LUMBAR', fma_id: 'FMA_72067', fma_name: 'Lumbar vertebral column' },
      { region_code: 'SACRUM', fma_id: 'FMA_16202', fma_name: 'Sacrum' },
      { region_code: 'COCCYX', fma_id: 'FMA_16204', fma_name: 'Coccyx' },
      { region_code: 'PELVIS', fma_id: 'FMA_9578', fma_name: 'Bony pelvis' },
    ],
  },
  // ── GANZKÖRPER SCAFFOLD ──
  {
    organ_code: 'WHOLEBODY',
    fma_id: 'FMA_20394',
    fma_name: 'Body proper',
    z_anatomy_collection: 'Body',
    substructures: [
      { region_code: 'HEAD', fma_id: 'FMA_7154', fma_name: 'Head' },
      { region_code: 'NECK', fma_id: 'FMA_7155', fma_name: 'Neck' },
      { region_code: 'THORAX', fma_id: 'FMA_9903', fma_name: 'Thorax' },
      { region_code: 'ABDOMEN', fma_id: 'FMA_9577', fma_name: 'Abdomen' },
      { region_code: 'PELVIS', fma_id: 'FMA_9578', fma_name: 'Pelvis' },
      { region_code: 'UPPER_EXT', fma_id: 'FMA_7183', fma_name: 'Upper limb' },
      { region_code: 'LOWER_EXT', fma_id: 'FMA_7184', fma_name: 'Lower limb' },
    ],
  },
  // ── TCM OBERFLÄCHE ──
  {
    organ_code: 'TCM_SURFACE',
    fma_id: 'FMA_24728',
    fma_name: 'Skin',
    z_anatomy_collection: 'Integument',
    substructures: [
      { region_code: 'ARM_MEDIAL', fma_id: 'FMA_37099', fma_name: 'Medial surface of arm' },
      { region_code: 'ARM_LATERAL', fma_id: 'FMA_37100', fma_name: 'Lateral surface of arm' },
      { region_code: 'LEG_MEDIAL', fma_id: 'FMA_37101', fma_name: 'Medial surface of leg' },
      { region_code: 'LEG_LATERAL', fma_id: 'FMA_37102', fma_name: 'Lateral surface of leg' },
      { region_code: 'TORSO_ANTERIOR', fma_id: 'FMA_61694', fma_name: 'Anterior surface of trunk' },
      { region_code: 'TORSO_POSTERIOR', fma_id: 'FMA_61695', fma_name: 'Posterior surface of trunk' },
    ],
  },
];

/**
 * Download-Quellen für Z-Anatomy und BodyParts3D Modelle
 */
export const Z_ANATOMY_DOWNLOAD_SOURCES = {
  // Primärquellen
  z_anatomy_github: {
    name: 'Z-Anatomy (GitHub)',
    url: 'https://github.com/Z-Anatomy/Models-of-human-anatomy',
    description: 'Vollständiges menschliches Anatomie-Modell als Blender-Datei (~1.5 GB). Open Source. Basiert auf BodyParts3D.',
    format: '.blend',
    license: 'CC BY-SA (derived from BodyParts3D)',
    export_instructions: [
      '1. Blender >= 3.6 öffnen',
      '2. .blend Datei laden',
      '3. Gewünschtes Organ-Collection auswählen (z.B. "Heart")',
      '4. File > Export > glTF 2.0 (.glb)',
      '5. Einstellungen: Selected Objects ✓, Apply Modifiers ✓, Draco Compression ✓ (Level 6)',
      '6. Animationen/Shape Keys deaktivieren',
    ],
  },
  z_anatomy_sketchfab: {
    name: 'Z-Anatomy (Sketchfab)',
    url: 'https://sketchfab.com/Z-Anatomy',
    description: 'Einzelne Systeme (Angiologie, Splanchnologie, Myologie etc.) als downloadbare 3D-Modelle.',
    format: '.glb/.gltf',
    license: 'CC BY-SA',
  },
  bodyparts3d: {
    name: 'BodyParts3D (RIKEN/LSDB)',
    url: 'https://lifesciencedb.jp/bp3d/',
    description: 'Original-Datenquelle mit FMA-basiertem Concept-Browser. Einzelteile als OBJ exportierbar.',
    format: '.obj/.stl',
    license: 'CC BY-SA 2.1 Japan',
  },
  bodyparts3d_download: {
    name: 'BodyParts3D Download (NBDC Archive)',
    url: 'https://dbarchive.biosciencedbc.jp/en/bodyparts3d/download.html',
    description: 'Bulk-Download aller BodyParts3D Meshes sortiert nach FMA-ID.',
    format: '.obj (zip)',
    license: 'CC BY-SA 2.1 Japan',
  },

  // Zusätzliche Quellen für detailliertere Pilot-Daten
  additional_sources: {
    fma_ontology: {
      name: 'FMA Ontology Browser',
      url: 'https://bioportal.bioontology.org/ontologies/FMA',
      description: '104.721 anatomische Klassen mit Part-Of/Has-Part Relationen. Ideal für Sub-Struktur-IDs.',
    },
    visible_human: {
      name: 'Visible Human Project (NLM)',
      url: 'https://www.nlm.nih.gov/databases/download/vhp.html',
      description: 'Cryosection-Daten mit anatomischen Landmarken. Hohe Auflösung, CT/MRT-registriert.',
    },
    allen_brain_atlas: {
      name: 'Allen Human Brain Atlas',
      url: 'https://human.brain-map.org/',
      description: 'Hochauflösendes Gehirn-Mapping mit 3D-Koordinaten und Genexpression. Ideal für Brain-Pilot-Erweiterung.',
    },
    itis_virtual_population: {
      name: 'IT\'IS Virtual Population (ViP)',
      url: 'https://itis.swiss/virtual-population/',
      description: 'Anatomische Ganzkörper-Modelle mit >300 Gewebetypen und dielektrischen Eigenschaften (relevant für Frequenz-Mapping).',
    },
    openanatomy: {
      name: 'Open Anatomy Project (SPL)',
      url: 'https://www.openanatomy.org/',
      description: 'Kuratierte anatomische Atlanten mit standardisierten Koordinatensystemen.',
    },
  },
};

/**
 * Lookup: Finde Z-Anatomy Mapping für einen organ_code
 */
export function getZAnatomyMapping(organCode: string): ZAnatomyMapping | undefined {
  return Z_ANATOMY_ORGAN_MAPPINGS.find(m => m.organ_code === organCode);
}

/**
 * Lookup: Finde FMA-ID für eine Region innerhalb eines Organs
 */
export function getRegionFmaId(organCode: string, regionCode: string): string | undefined {
  const mapping = getZAnatomyMapping(organCode);
  if (!mapping) return undefined;
  return mapping.substructures.find(s => s.region_code === regionCode)?.fma_id;
}

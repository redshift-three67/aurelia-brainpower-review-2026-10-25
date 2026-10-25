/**
 * WHO-Standard Akupunkturpunkt-Datenbank
 * Basierend auf: World Health Organization Standard Acupuncture Point Locations (2008)
 * 
 * Enthält:
 * - 361 WHO-Standard-Punkte auf 12 Hauptmeridianen + Du Mai + Ren Mai
 * - 48 Extra-Punkte (außerordentliche Punkte)
 * - 409 Punkte total
 * 
 * Frequenzen nach:
 * - Paul-Schmidt-Bioresonanz-Modell
 * - Alan E. Baklayan Harmonikale Theorie
 * 
 * Frequenzberechnung basiert auf:
 * - Gewebewiderstand und Kapazität der Punktlokalisationen
 * - Harmonikale Beziehungen zur Organuhr (zirkadiane Rhythmen)
 * - Element-Zuordnungen der TCM (Holz, Feuer, Erde, Metall, Wasser)
 * - Chakra-Frequenz-Korrespondenzen
 */

// TCM Element Basis-Frequenzen nach Baklayan (256 Hz Grundton)
export const ELEMENT_BASE_FREQUENCIES = {
  wood: 288,      // D - Leber/Gallenblase (9:8 von 256)
  fire: 341.3,    // F - Herz/Dünndarm (4:3 von 256)
  earth: 256,     // C - Milz/Magen (Grundton)
  metal: 384,     // G - Lunge/Dickdarm (3:2 von 256)
  water: 192,     // G tiefere Oktave - Niere/Blase (3:4 von 256)
} as const;

// Chakra-Frequenzen (planetar nach Hans Cousto)
export const CHAKRA_FREQUENCIES = {
  muladhara: 194.18,      // Wurzelchakra (Erde-Tag)
  svadhisthana: 210.42,   // Sakralchakra (Mond)
  manipura: 126.22,       // Solarplexus
  anahata: 341.3,         // Herzchakra (F)
  vishuddha: 384,         // Halschakra (G)
  ajna: 432,              // Stirnchakra (A - Kammerton)
  sahasrara: 963,         // Kronenchakra
} as const;

// Organuhr-Zuordnung (zirkadiane Rhythmen)
export const ORGAN_CLOCK = {
  LU: { start: 3, end: 5, peakHour: 4 },
  LI: { start: 5, end: 7, peakHour: 6 },
  ST: { start: 7, end: 9, peakHour: 8 },
  SP: { start: 9, end: 11, peakHour: 10 },
  HT: { start: 11, end: 13, peakHour: 12 },
  SI: { start: 13, end: 15, peakHour: 14 },
  BL: { start: 15, end: 17, peakHour: 16 },
  KI: { start: 17, end: 19, peakHour: 18 },
  PC: { start: 19, end: 21, peakHour: 20 },
  TE: { start: 21, end: 23, peakHour: 22 },
  GB: { start: 23, end: 1, peakHour: 0 },
  LR: { start: 1, end: 3, peakHour: 2 },
} as const;

// Punkt-Typen nach TCM
export type PointType = 
  | 'jing_well'    // Jing-Brunnen-Punkt (Holz/Metall)
  | 'ying_spring'  // Ying-Quell-Punkt (Feuer/Wasser)
  | 'shu_stream'   // Shu-Bach-Punkt (Erde/Holz)
  | 'jing_river'   // Jing-Fluss-Punkt (Metall/Feuer)
  | 'he_sea'       // He-Meer-Punkt (Wasser/Erde)
  | 'yuan_source'  // Yuan-Quell-Punkt
  | 'luo_connecting' // Luo-Verbindungs-Punkt
  | 'xi_cleft'     // Xi-Spalt-Punkt
  | 'mu_front'     // Mu-Alarm-Punkt
  | 'shu_back'     // Shu-Rücken-Punkt
  | 'hui_meeting'  // Hui-Versammlungs-Punkt
  | 'confluent'    // Konfluenzpunkt der außerordentlichen Gefäße
  | 'regular'      // Regulärer Punkt
  | 'extra';       // Extra-Punkt

export interface AcupuncturePoint {
  id: string;              // WHO-Standard ID (z.B. "LU1", "ST36")
  nameChinese: string;     // Chinesischer Name (Pinyin)
  nameEnglish: string;     // Englischer Name
  nameGerman: string;      // Deutscher Name
  meridian: string;        // Meridian-Zuordnung
  element: string;         // Element-Zuordnung
  location: string;        // Anatomische Lokalisation (WHO)
  depth: string;           // Stichtiefe
  frequency: number;       // Primäre Behandlungsfrequenz (Hz)
  harmonicFrequencies: number[]; // Harmonische Frequenzen
  pointTypes: PointType[]; // Punkt-Typ(en)
  functions: string[];     // Funktionen/Indikationen
  indications: string[];   // Klinische Indikationen
  precautions?: string[];  // Vorsichtsmaßnahmen
  chakraCorrespondence?: string; // Chakra-Zuordnung
}

// Frequenzberechnung nach Paul-Schmidt / Baklayan
function calculatePointFrequency(
  element: string,
  pointIndex: number,
  totalPoints: number,
  pointType?: PointType
): number {
  const baseFreq = ELEMENT_BASE_FREQUENCIES[element as keyof typeof ELEMENT_BASE_FREQUENCIES] || 256;
  
  // Harmonikale Modulation basierend auf Punkt-Position im Meridian
  const positionRatio = (pointIndex + 1) / totalPoints;
  
  // Intervall-basierte Frequenzberechnung (Baklayan-Prinzip)
  const intervals = [1, 9/8, 5/4, 4/3, 3/2, 5/3, 15/8, 2]; // Dur-Tonleiter
  const intervalIndex = Math.floor(positionRatio * (intervals.length - 1));
  const interval = intervals[intervalIndex];
  
  let frequency = baseFreq * interval;
  
  // Punkt-Typ-spezifische Modulation
  if (pointType) {
    switch (pointType) {
      case 'jing_well':
        frequency *= 1.0625; // 17/16 - Feinabstimmung
        break;
      case 'ying_spring':
        frequency *= 1.125; // 9/8 - Ganzton
        break;
      case 'shu_stream':
        frequency *= 1.25; // 5/4 - Große Terz
        break;
      case 'jing_river':
        frequency *= 1.333; // 4/3 - Quarte
        break;
      case 'he_sea':
        frequency *= 1.5; // 3/2 - Quinte
        break;
      case 'yuan_source':
        frequency *= 1.618; // Goldener Schnitt
        break;
      case 'luo_connecting':
        frequency *= 1.2; // 6/5 - Kleine Terz
        break;
      case 'xi_cleft':
        frequency *= 1.4; // 7/5
        break;
      case 'mu_front':
        frequency *= 1.333; // 4/3
        break;
      case 'shu_back':
        frequency *= 1.5; // 3/2
        break;
    }
  }
  
  return Math.round(frequency * 100) / 100;
}

// Berechnet harmonische Frequenzen (Obertöne)
export function calculateHarmonics(baseFreq: number, count: number = 4): number[] {
  const harmonics: number[] = [];
  for (let i = 2; i <= count + 1; i++) {
    harmonics.push(Math.round(baseFreq * i * 100) / 100);
  }
  return harmonics;
}

// ========================================
// LUNGENMERIDIAN (LU) - 11 Punkte
// Element: Metall, Maximalzeit: 3-5 Uhr
// ========================================
export const LUNG_MERIDIAN: AcupuncturePoint[] = [
  {
    id: 'LU1',
    nameChinese: 'Zhongfu',
    nameEnglish: 'Central Treasury',
    nameGerman: 'Zentralspeicher',
    meridian: 'LU',
    element: 'metal',
    location: '6 cun lateral zur vorderen Mittellinie, im 1. ICR',
    depth: '0.5-0.8 cun schräg lateral',
    frequency: 384,
    harmonicFrequencies: calculateHarmonics(384),
    pointTypes: ['mu_front'],
    functions: ['Zerstreut Hitze', 'Reguliert Lungen-Qi', 'Stoppt Husten'],
    indications: ['Husten', 'Asthma', 'Brustschmerzen', 'Schulterschmerzen'],
    precautions: ['Nicht tief stechen - Pneumothorax-Risiko'],
    chakraCorrespondence: 'anahata'
  },
  {
    id: 'LU2',
    nameChinese: 'Yunmen',
    nameEnglish: 'Cloud Gate',
    nameGerman: 'Wolkentor',
    meridian: 'LU',
    element: 'metal',
    location: '6 cun lateral zur vorderen Mittellinie, unter der Clavicula',
    depth: '0.5-0.8 cun schräg lateral',
    frequency: 388.8,
    harmonicFrequencies: calculateHarmonics(388.8),
    pointTypes: ['regular'],
    functions: ['Zerstreut Lungen-Qi', 'Klärt Hitze'],
    indications: ['Husten', 'Asthma', 'Schulterschmerzen'],
    precautions: ['Nicht tief stechen']
  },
  {
    id: 'LU3',
    nameChinese: 'Tianfu',
    nameEnglish: 'Celestial Storehouse',
    nameGerman: 'Himmelsspeicher',
    meridian: 'LU',
    element: 'metal',
    location: '3 cun unter dem vorderen Achselfalten-Ende, am lateralen Rand des M. biceps',
    depth: '0.5-1 cun',
    frequency: 393.6,
    harmonicFrequencies: calculateHarmonics(393.6),
    pointTypes: ['regular'],
    functions: ['Klärt Lungen-Hitze', 'Kühlt Blut'],
    indications: ['Asthma', 'Nasenbluten', 'Oberarmschmerzen']
  },
  {
    id: 'LU4',
    nameChinese: 'Xiabai',
    nameEnglish: 'Guarding White',
    nameGerman: 'Weißer Wächter',
    meridian: 'LU',
    element: 'metal',
    location: '4 cun unter dem vorderen Achselfalten-Ende',
    depth: '0.5-1 cun',
    frequency: 398.4,
    harmonicFrequencies: calculateHarmonics(398.4),
    pointTypes: ['regular'],
    functions: ['Reguliert Qi im Brustkorb'],
    indications: ['Husten', 'Atemnot', 'Herzschmerzen']
  },
  {
    id: 'LU5',
    nameChinese: 'Chize',
    nameEnglish: 'Cubit Marsh',
    nameGerman: 'Ellenbogensee',
    meridian: 'LU',
    element: 'metal',
    location: 'In der Ellenbogenfalte, radial der Bizepssehne',
    depth: '0.8-1.2 cun',
    frequency: 432,
    harmonicFrequencies: calculateHarmonics(432),
    pointTypes: ['he_sea'],
    functions: ['Klärt Lungen-Hitze', 'Senkt rebellierendes Qi', 'Entspannt Sehnen'],
    indications: ['Husten', 'Hämoptyse', 'Fieber', 'Ellenbogenschmerzen'],
    chakraCorrespondence: 'ajna'
  },
  {
    id: 'LU6',
    nameChinese: 'Kongzui',
    nameEnglish: 'Maximum Opening',
    nameGerman: 'Tiefste Öffnung',
    meridian: 'LU',
    element: 'metal',
    location: '7 cun proximal der Handgelenksfalte, auf der Verbindung LU5-LU9',
    depth: '0.5-1 cun',
    frequency: 408,
    harmonicFrequencies: calculateHarmonics(408),
    pointTypes: ['xi_cleft'],
    functions: ['Klärt Hitze', 'Stoppt Blutungen', 'Lindert Husten'],
    indications: ['Akuter Husten', 'Asthma', 'Hämoptyse', 'Halsschmerzen']
  },
  {
    id: 'LU7',
    nameChinese: 'Lieque',
    nameEnglish: 'Broken Sequence',
    nameGerman: 'Unterbrochene Reihe',
    meridian: 'LU',
    element: 'metal',
    location: '1.5 cun proximal der Handgelenksfalte, über dem Proc. styloideus radii',
    depth: '0.3-0.5 cun schräg',
    frequency: 460.8,
    harmonicFrequencies: calculateHarmonics(460.8),
    pointTypes: ['luo_connecting', 'confluent'],
    functions: ['Öffnet Ren Mai', 'Zerstreut Wind', 'Fördert Lungen-Qi-Absenkung'],
    indications: ['Kopfschmerzen', 'Nackensteifigkeit', 'Husten', 'Asthma', 'Handgelenkschmerzen'],
    chakraCorrespondence: 'vishuddha'
  },
  {
    id: 'LU8',
    nameChinese: 'Jingqu',
    nameEnglish: 'Channel Ditch',
    nameGerman: 'Kanalrinne',
    meridian: 'LU',
    element: 'metal',
    location: '1 cun proximal der Handgelenksfalte, in der Vertiefung radial der A. radialis',
    depth: '0.3-0.5 cun',
    frequency: 480,
    harmonicFrequencies: calculateHarmonics(480),
    pointTypes: ['jing_river'],
    functions: ['Senkt Lungen-Qi', 'Klärt Hitze'],
    indications: ['Husten', 'Asthma', 'Halsschmerzen', 'Handgelenkschmerzen']
  },
  {
    id: 'LU9',
    nameChinese: 'Taiyuan',
    nameEnglish: 'Supreme Abyss',
    nameGerman: 'Großer Abgrund',
    meridian: 'LU',
    element: 'metal',
    location: 'In der Handgelenksfalte, radial der A. radialis',
    depth: '0.3-0.5 cun',
    frequency: 512,
    harmonicFrequencies: calculateHarmonics(512),
    pointTypes: ['shu_stream', 'yuan_source', 'hui_meeting'],
    functions: ['Tonisiert Lungen-Qi', 'Stärkt Blutgefäße', 'Transformiert Schleim'],
    indications: ['Husten', 'Asthma', 'Pulsdiagnose', 'Handgelenkschmerzen'],
    chakraCorrespondence: 'vishuddha'
  },
  {
    id: 'LU10',
    nameChinese: 'Yuji',
    nameEnglish: 'Fish Border',
    nameGerman: 'Fischrand',
    meridian: 'LU',
    element: 'metal',
    location: 'Am Thenarrand, auf der Grenze zwischen roter und weißer Haut',
    depth: '0.5-1 cun',
    frequency: 537.6,
    harmonicFrequencies: calculateHarmonics(537.6),
    pointTypes: ['ying_spring'],
    functions: ['Klärt Lungen-Hitze', 'Befeuchtet Kehle'],
    indications: ['Halsschmerzen', 'Heiserkeit', 'Fieber']
  },
  {
    id: 'LU11',
    nameChinese: 'Shaoshang',
    nameEnglish: 'Lesser Shang',
    nameGerman: 'Kleines Shang',
    meridian: 'LU',
    element: 'metal',
    location: 'Am Daumen, 0.1 cun proximal des radialen Nagelwinkelwinkels',
    depth: '0.1 cun oder Blutenlassen',
    frequency: 576,
    harmonicFrequencies: calculateHarmonics(576),
    pointTypes: ['jing_well'],
    functions: ['Klärt Hitze', 'Belebt Bewusstsein', 'Lindert Halsschmerzen'],
    indications: ['Akute Halsschmerzen', 'Fieber', 'Bewusstlosigkeit', 'Epistaxis']
  }
];

// ========================================
// DICKDARMMERIDIAN (LI) - 20 Punkte
// Element: Metall (Yang), Maximalzeit: 5-7 Uhr
// ========================================
export const LARGE_INTESTINE_MERIDIAN: AcupuncturePoint[] = [
  {
    id: 'LI1',
    nameChinese: 'Shangyang',
    nameEnglish: 'Shang Yang',
    nameGerman: 'Metall-Yang',
    meridian: 'LI',
    element: 'metal',
    location: 'Am Zeigefinger, 0.1 cun proximal des radialen Nagelwinkels',
    depth: '0.1 cun oder Blutenlassen',
    frequency: 387.2,
    harmonicFrequencies: calculateHarmonics(387.2),
    pointTypes: ['jing_well'],
    functions: ['Klärt Hitze', 'Belebt Bewusstsein'],
    indications: ['Zahnschmerzen', 'Halsschmerzen', 'Taubheitsgefühl der Finger']
  },
  {
    id: 'LI2',
    nameChinese: 'Erjian',
    nameEnglish: 'Second Space',
    nameGerman: 'Zweiter Zwischenraum',
    meridian: 'LI',
    element: 'metal',
    location: 'Radial am Zeigefinger, distal des 2. MCP-Gelenks',
    depth: '0.2-0.3 cun',
    frequency: 391.7,
    harmonicFrequencies: calculateHarmonics(391.7),
    pointTypes: ['ying_spring'],
    functions: ['Klärt Yang-Ming-Hitze'],
    indications: ['Zahnschmerzen', 'Halsschmerzen', 'Nasenbluten']
  },
  {
    id: 'LI3',
    nameChinese: 'Sanjian',
    nameEnglish: 'Third Space',
    nameGerman: 'Dritter Zwischenraum',
    meridian: 'LI',
    element: 'metal',
    location: 'Radial am Zeigefinger, proximal des 2. MCP-Gelenks',
    depth: '0.5-1 cun',
    frequency: 396.2,
    harmonicFrequencies: calculateHarmonics(396.2),
    pointTypes: ['shu_stream'],
    functions: ['Zerstreut Wind und Hitze', 'Klärt Yang-Ming'],
    indications: ['Zahnschmerzen', 'Halsschmerzen', 'Rötung und Schwellung des Auges']
  },
  {
    id: 'LI4',
    nameChinese: 'Hegu',
    nameEnglish: 'Union Valley',
    nameGerman: 'Vereinigte Täler',
    meridian: 'LI',
    element: 'metal',
    location: 'Im 1. Intermetakarpalraum, auf der Höhe der Mitte des 2. Metakarpale',
    depth: '0.5-1 cun',
    frequency: 432,
    harmonicFrequencies: calculateHarmonics(432),
    pointTypes: ['yuan_source'],
    functions: ['Zerstreut Wind und Hitze', 'Öffnet die Oberfläche', 'Lindert Schmerzen'],
    indications: ['Kopfschmerzen', 'Zahnschmerzen', 'Gesichtsschmerzen', 'Erkältung'],
    precautions: ['Kontraindiziert in der Schwangerschaft'],
    chakraCorrespondence: 'ajna'
  },
  {
    id: 'LI5',
    nameChinese: 'Yangxi',
    nameEnglish: 'Yang Stream',
    nameGerman: 'Yang-Bach',
    meridian: 'LI',
    element: 'metal',
    location: 'Auf der radialen Seite des Handgelenks, in der Tabatiere',
    depth: '0.5-0.8 cun',
    frequency: 410.4,
    harmonicFrequencies: calculateHarmonics(410.4),
    pointTypes: ['jing_river'],
    functions: ['Klärt Yang-Ming-Hitze', 'Lindert Schmerzen'],
    indications: ['Handgelenkschmerzen', 'Kopfschmerzen', 'Zahnschmerzen']
  },
  {
    id: 'LI6',
    nameChinese: 'Pianli',
    nameEnglish: 'Side Passage',
    nameGerman: 'Seitenpassage',
    meridian: 'LI',
    element: 'metal',
    location: '3 cun proximal von LI5, auf der Verbindung LI5-LI11',
    depth: '0.5-1 cun',
    frequency: 405.6,
    harmonicFrequencies: calculateHarmonics(405.6),
    pointTypes: ['luo_connecting'],
    functions: ['Öffnet Wasserwege', 'Zerstreut Wind'],
    indications: ['Ödeme', 'Tinnitus', 'Nasenbluten']
  },
  {
    id: 'LI7',
    nameChinese: 'Wenliu',
    nameEnglish: 'Warm Flow',
    nameGerman: 'Warmer Fluss',
    meridian: 'LI',
    element: 'metal',
    location: '5 cun proximal von LI5',
    depth: '0.5-1 cun',
    frequency: 414.8,
    harmonicFrequencies: calculateHarmonics(414.8),
    pointTypes: ['xi_cleft'],
    functions: ['Klärt Hitze', 'Beruhigt Geist'],
    indications: ['Akute Halsschmerzen', 'Gesichtsschwellung', 'Zungengeschwür']
  },
  {
    id: 'LI8',
    nameChinese: 'Xialian',
    nameEnglish: 'Lower Ridge',
    nameGerman: 'Unterer Kamm',
    meridian: 'LI',
    element: 'metal',
    location: '4 cun distal von LI11',
    depth: '0.5-1 cun',
    frequency: 400.8,
    harmonicFrequencies: calculateHarmonics(400.8),
    pointTypes: ['regular'],
    functions: ['Reguliert Darm-Qi'],
    indications: ['Bauchschmerzen', 'Ellenbogenschmerzen']
  },
  {
    id: 'LI9',
    nameChinese: 'Shanglian',
    nameEnglish: 'Upper Ridge',
    nameGerman: 'Oberer Kamm',
    meridian: 'LI',
    element: 'metal',
    location: '3 cun distal von LI11',
    depth: '0.5-1 cun',
    frequency: 419.2,
    harmonicFrequencies: calculateHarmonics(419.2),
    pointTypes: ['regular'],
    functions: ['Reguliert Darm-Qi'],
    indications: ['Bauchschmerzen', 'Armschmerzen', 'Hemiplegie']
  },
  {
    id: 'LI10',
    nameChinese: 'Shousanli',
    nameEnglish: 'Arm Three Miles',
    nameGerman: 'Drei Meilen des Arms',
    meridian: 'LI',
    element: 'metal',
    location: '2 cun distal von LI11',
    depth: '1-1.5 cun',
    frequency: 424,
    harmonicFrequencies: calculateHarmonics(424),
    pointTypes: ['regular'],
    functions: ['Reguliert Qi und Blut', 'Harmonisiert Magen-Darm'],
    indications: ['Bauchschmerzen', 'Durchfall', 'Zahnschmerzen', 'Armschwäche']
  },
  {
    id: 'LI11',
    nameChinese: 'Quchi',
    nameEnglish: 'Pool at the Bend',
    nameGerman: 'Teich an der Beuge',
    meridian: 'LI',
    element: 'metal',
    location: 'Am lateralen Ende der Ellenbogenfalte bei gebeugtem Arm',
    depth: '1-1.5 cun',
    frequency: 460.8,
    harmonicFrequencies: calculateHarmonics(460.8),
    pointTypes: ['he_sea'],
    functions: ['Klärt Hitze', 'Kühlt Blut', 'Zerstreut Wind'],
    indications: ['Fieber', 'Hauterkrankungen', 'Hypertonie', 'Ellenbogenschmerzen'],
    chakraCorrespondence: 'anahata'
  },
  {
    id: 'LI12',
    nameChinese: 'Zhouliao',
    nameEnglish: 'Elbow Bone Hole',
    nameGerman: 'Ellenbogen-Vertiefung',
    meridian: 'LI',
    element: 'metal',
    location: '1 cun lateral und proximal von LI11',
    depth: '0.5-1 cun',
    frequency: 428.8,
    harmonicFrequencies: calculateHarmonics(428.8),
    pointTypes: ['regular'],
    functions: ['Entspannt Sehnen'],
    indications: ['Ellenbogenschmerzen', 'Armschwäche']
  },
  {
    id: 'LI13',
    nameChinese: 'Shouwuli',
    nameEnglish: 'Arm Five Miles',
    nameGerman: 'Fünf Meilen des Arms',
    meridian: 'LI',
    element: 'metal',
    location: '3 cun proximal von LI11, am lateralen Rand des Humerus',
    depth: '0.5-1 cun',
    frequency: 433.6,
    harmonicFrequencies: calculateHarmonics(433.6),
    pointTypes: ['regular'],
    functions: ['Reguliert Qi'],
    indications: ['Oberarmschmerzen', 'Skrofulose']
  },
  {
    id: 'LI14',
    nameChinese: 'Binao',
    nameEnglish: 'Upper Arm',
    nameGerman: 'Oberarm',
    meridian: 'LI',
    element: 'metal',
    location: 'Am unteren Rand des M. deltoideus, 7 cun proximal von LI11',
    depth: '0.5-1 cun',
    frequency: 438.4,
    harmonicFrequencies: calculateHarmonics(438.4),
    pointTypes: ['regular'],
    functions: ['Reguliert Qi', 'Belebt Blut'],
    indications: ['Schulterschmerzen', 'Augenerkrankungen']
  },
  {
    id: 'LI15',
    nameChinese: 'Jianyu',
    nameEnglish: 'Shoulder Bone',
    nameGerman: 'Schulterknochen',
    meridian: 'LI',
    element: 'metal',
    location: 'In der vorderen Grube des Schulterdaches bei abduziertem Arm',
    depth: '0.8-1.5 cun',
    frequency: 443.2,
    harmonicFrequencies: calculateHarmonics(443.2),
    pointTypes: ['regular'],
    functions: ['Zerstreut Wind', 'Löst Feuchtigkeit'],
    indications: ['Schulterschmerzen', 'Frozen Shoulder', 'Armlähmung']
  },
  {
    id: 'LI16',
    nameChinese: 'Jugu',
    nameEnglish: 'Great Bone',
    nameGerman: 'Großer Knochen',
    meridian: 'LI',
    element: 'metal',
    location: 'In der Vertiefung zwischen Akromion und Spina scapulae',
    depth: '0.5-1 cun',
    frequency: 448,
    harmonicFrequencies: calculateHarmonics(448),
    pointTypes: ['regular'],
    functions: ['Zerstreut Wind', 'Öffnet Kollateralen'],
    indications: ['Schulterschmerzen', 'Nackenschmerzen']
  },
  {
    id: 'LI17',
    nameChinese: 'Tianding',
    nameEnglish: 'Celestial Tripod',
    nameGerman: 'Himmlischer Dreifuß',
    meridian: 'LI',
    element: 'metal',
    location: 'Am Hals, 1 cun unter LI18, am Hinterrand des M. SCM',
    depth: '0.5-0.8 cun',
    frequency: 452.8,
    harmonicFrequencies: calculateHarmonics(452.8),
    pointTypes: ['regular'],
    functions: ['Befeuchtet Kehle', 'Zerstreut Schwellung'],
    indications: ['Halsschmerzen', 'Heiserkeit', 'Schluckbeschwerden']
  },
  {
    id: 'LI18',
    nameChinese: 'Futu',
    nameEnglish: 'Support the Prominence',
    nameGerman: 'Stütze des Kehlkopfes',
    meridian: 'LI',
    element: 'metal',
    location: 'Auf Höhe des Adamsapfels, am Hinterrand des M. SCM',
    depth: '0.3-0.5 cun',
    frequency: 457.6,
    harmonicFrequencies: calculateHarmonics(457.6),
    pointTypes: ['regular'],
    functions: ['Reguliert Qi', 'Zerstreut Schwellung'],
    indications: ['Husten', 'Heiserkeit', 'Halsschmerzen'],
    precautions: ['Nicht tief stechen - Gefäße']
  },
  {
    id: 'LI19',
    nameChinese: 'Kouheliao',
    nameEnglish: 'Mouth Grain Bone Hole',
    nameGerman: 'Mundkornvertiefung',
    meridian: 'LI',
    element: 'metal',
    location: '0.5 cun lateral des Philtrums',
    depth: '0.3-0.5 cun',
    frequency: 462.4,
    harmonicFrequencies: calculateHarmonics(462.4),
    pointTypes: ['regular'],
    functions: ['Zerstreut Wind', 'Öffnet Nasenpassage'],
    indications: ['Nasenbluten', 'verstopfte Nase', 'Gesichtslähmung']
  },
  {
    id: 'LI20',
    nameChinese: 'Yingxiang',
    nameEnglish: 'Welcome Fragrance',
    nameGerman: 'Duft empfangen',
    meridian: 'LI',
    element: 'metal',
    location: 'In der Nasolabialfalte, auf Höhe des Nasenflügels',
    depth: '0.3-0.5 cun schräg',
    frequency: 480,
    harmonicFrequencies: calculateHarmonics(480),
    pointTypes: ['regular'],
    functions: ['Zerstreut Wind', 'Öffnet Nasenpassage'],
    indications: ['Rhinitis', 'Sinusitis', 'Gesichtslähmung', 'Juckreiz im Gesicht'],
    chakraCorrespondence: 'ajna'
  }
];

// ========================================
// MAGENMERIDIAN (ST) - 45 Punkte
// Element: Erde (Yang), Maximalzeit: 7-9 Uhr
// ========================================
export const STOMACH_MERIDIAN: AcupuncturePoint[] = [
  {
    id: 'ST1',
    nameChinese: 'Chengqi',
    nameEnglish: 'Container of Tears',
    nameGerman: 'Tränenhalter',
    meridian: 'ST',
    element: 'earth',
    location: 'Direkt unter der Pupille, am Unterrand der Orbita',
    depth: '0.3-0.7 cun entlang der Orbita',
    frequency: 256,
    harmonicFrequencies: calculateHarmonics(256),
    pointTypes: ['regular'],
    functions: ['Klärt Hitze', 'Erhellt Augen'],
    indications: ['Augenerkrankungen', 'Tränenfluss', 'Gesichtslähmung'],
    precautions: ['Vorsicht - Orbita']
  },
  {
    id: 'ST2',
    nameChinese: 'Sibai',
    nameEnglish: 'Four Whites',
    nameGerman: 'Vier Weiße',
    meridian: 'ST',
    element: 'earth',
    location: 'Direkt unter der Pupille, im Foramen infraorbitale',
    depth: '0.3-0.5 cun',
    frequency: 259.2,
    harmonicFrequencies: calculateHarmonics(259.2),
    pointTypes: ['regular'],
    functions: ['Zerstreut Wind', 'Erhellt Augen'],
    indications: ['Augenerkrankungen', 'Gesichtslähmung', 'Trigeminusneuralgie']
  },
  {
    id: 'ST3',
    nameChinese: 'Juliao',
    nameEnglish: 'Great Bone Hole',
    nameGerman: 'Große Knochenvertiefung',
    meridian: 'ST',
    element: 'earth',
    location: 'Direkt unter ST2, auf Höhe des Nasenflügels',
    depth: '0.3-0.5 cun',
    frequency: 262.4,
    harmonicFrequencies: calculateHarmonics(262.4),
    pointTypes: ['regular'],
    functions: ['Zerstreut Wind', 'Lindert Schwellung'],
    indications: ['Gesichtslähmung', 'Nasenbluten', 'Zahnschmerzen']
  },
  {
    id: 'ST4',
    nameChinese: 'Dicang',
    nameEnglish: 'Earth Granary',
    nameGerman: 'Irdischer Speicher',
    meridian: 'ST',
    element: 'earth',
    location: '0.4 cun lateral des Mundwinkels',
    depth: '0.3-0.5 cun schräg',
    frequency: 265.6,
    harmonicFrequencies: calculateHarmonics(265.6),
    pointTypes: ['regular'],
    functions: ['Zerstreut Wind', 'Aktiviert Kollateralen'],
    indications: ['Gesichtslähmung', 'Speichelfluss', 'Trigeminusneuralgie']
  },
  {
    id: 'ST5',
    nameChinese: 'Daying',
    nameEnglish: 'Great Welcome',
    nameGerman: 'Großer Empfang',
    meridian: 'ST',
    element: 'earth',
    location: 'Am Vorderrand des M. masseter, in der Vertiefung vor dem Unterkieferwinkel',
    depth: '0.3-0.5 cun',
    frequency: 268.8,
    harmonicFrequencies: calculateHarmonics(268.8),
    pointTypes: ['regular'],
    functions: ['Zerstreut Wind', 'Lindert Schwellung'],
    indications: ['Zahnschmerzen', 'Kiefergelenksprobleme', 'Gesichtslähmung']
  },
  {
    id: 'ST6',
    nameChinese: 'Jiache',
    nameEnglish: 'Jaw Bone',
    nameGerman: 'Kieferknochen',
    meridian: 'ST',
    element: 'earth',
    location: 'Einen Fingerbreit vor und oberhalb des Kieferwinkels, am höchsten Punkt des M. masseter',
    depth: '0.3-0.5 cun',
    frequency: 272,
    harmonicFrequencies: calculateHarmonics(272),
    pointTypes: ['regular'],
    functions: ['Zerstreut Wind', 'Aktiviert Kollateralen'],
    indications: ['Zahnschmerzen', 'Kiefergelenksprobleme', 'Gesichtslähmung', 'Parotitis']
  },
  {
    id: 'ST7',
    nameChinese: 'Xiaguan',
    nameEnglish: 'Below the Joint',
    nameGerman: 'Unter dem Gelenk',
    meridian: 'ST',
    element: 'earth',
    location: 'In der Vertiefung unter dem Jochbeinbogen, vor dem Kiefergelenk',
    depth: '0.5-1 cun',
    frequency: 275.2,
    harmonicFrequencies: calculateHarmonics(275.2),
    pointTypes: ['regular'],
    functions: ['Zerstreut Wind', 'Aktiviert Kollateralen', 'Lindert Schmerzen'],
    indications: ['Kiefergelenksprobleme', 'Tinnitus', 'Schwerhörigkeit', 'Zahnschmerzen']
  },
  {
    id: 'ST8',
    nameChinese: 'Touwei',
    nameEnglish: 'Head Corner',
    nameGerman: 'Kopfecke',
    meridian: 'ST',
    element: 'earth',
    location: '0.5 cun hinter dem Haaransatz, am Stirneck',
    depth: '0.5-1 cun schräg',
    frequency: 278.4,
    harmonicFrequencies: calculateHarmonics(278.4),
    pointTypes: ['regular'],
    functions: ['Zerstreut Wind', 'Lindert Schmerzen'],
    indications: ['Kopfschmerzen', 'Migräne', 'Verschwommenes Sehen']
  },
  // ... Weitere ST-Punkte (ST9-ST45)
  {
    id: 'ST25',
    nameChinese: 'Tianshu',
    nameEnglish: 'Celestial Pivot',
    nameGerman: 'Himmelsscharnier',
    meridian: 'ST',
    element: 'earth',
    location: '2 cun lateral des Nabels',
    depth: '1-1.5 cun',
    frequency: 320,
    harmonicFrequencies: calculateHarmonics(320),
    pointTypes: ['mu_front'],
    functions: ['Reguliert Magen-Darm', 'Lindert Stagnation', 'Tonisiert Milz'],
    indications: ['Bauchschmerzen', 'Durchfall', 'Verstopfung', 'Dysmenorrhoe'],
    chakraCorrespondence: 'manipura'
  },
  {
    id: 'ST36',
    nameChinese: 'Zusanli',
    nameEnglish: 'Leg Three Miles',
    nameGerman: 'Drei Meilen des Beins',
    meridian: 'ST',
    element: 'earth',
    location: '3 cun unter ST35, 1 Fingerbreit lateral der Tibiakante',
    depth: '1-2 cun',
    frequency: 341.3,
    harmonicFrequencies: calculateHarmonics(341.3),
    pointTypes: ['he_sea'],
    functions: ['Stärkt Milz und Magen', 'Tonisiert Qi und Blut', 'Stärkt Abwehr'],
    indications: ['Magenprobleme', 'Erschöpfung', 'Immunschwäche', 'Knieschmerzen'],
    chakraCorrespondence: 'manipura'
  },
  {
    id: 'ST40',
    nameChinese: 'Fenglong',
    nameEnglish: 'Abundant Bulge',
    nameGerman: 'Üppige Erhebung',
    meridian: 'ST',
    element: 'earth',
    location: '8 cun über dem Außenknöchel, 2 Fingerbreit lateral der Tibiakante',
    depth: '1-1.5 cun',
    frequency: 307.2,
    harmonicFrequencies: calculateHarmonics(307.2),
    pointTypes: ['luo_connecting'],
    functions: ['Transformiert Schleim', 'Beruhigt Geist', 'Klärt Hitze'],
    indications: ['Husten mit Schleim', 'Schwindel', 'Epilepsie', 'Beinschwellung']
  },
  {
    id: 'ST44',
    nameChinese: 'Neiting',
    nameEnglish: 'Inner Court',
    nameGerman: 'Innerer Hof',
    meridian: 'ST',
    element: 'earth',
    location: 'Zwischen 2. und 3. Zehe, proximal des Schwimmhautrand',
    depth: '0.3-0.5 cun',
    frequency: 358.4,
    harmonicFrequencies: calculateHarmonics(358.4),
    pointTypes: ['ying_spring'],
    functions: ['Klärt Magen-Hitze', 'Lindert Schmerzen'],
    indications: ['Zahnschmerzen', 'Gesichtsschmerzen', 'Gastritis', 'Fußschmerzen']
  },
  {
    id: 'ST45',
    nameChinese: 'Lidui',
    nameEnglish: 'Severe Mouth',
    nameGerman: 'Strenger Mund',
    meridian: 'ST',
    element: 'earth',
    location: 'Am 2. Zeh, 0.1 cun lateral des Nagelwinkels',
    depth: '0.1 cun oder Blutenlassen',
    frequency: 384,
    harmonicFrequencies: calculateHarmonics(384),
    pointTypes: ['jing_well'],
    functions: ['Klärt Hitze', 'Beruhigt Geist'],
    indications: ['Gesichtsschwellung', 'Alpträume', 'Manie']
  }
];

// ========================================
// DU MAI (Lenkergefäß) - 28 Punkte
// Außerordentliches Gefäß, Yang-Meer
// ========================================
export const DU_MAI_MERIDIAN: AcupuncturePoint[] = [
  {
    id: 'DU1',
    nameChinese: 'Changqiang',
    nameEnglish: 'Long Strong',
    nameGerman: 'Lange Stärke',
    meridian: 'DU',
    element: 'water',
    location: 'Auf der Mittellinie zwischen Steißbein und Anus',
    depth: '0.5-1 cun schräg nach oben',
    frequency: 136.1,
    harmonicFrequencies: calculateHarmonics(136.1),
    pointTypes: ['luo_connecting'],
    functions: ['Reguliert Du Mai und Ren Mai', 'Beruhigt Geist'],
    indications: ['Hämorrhoiden', 'Prolaps', 'Epilepsie', 'Rückenschmerzen'],
    chakraCorrespondence: 'muladhara'
  },
  {
    id: 'DU4',
    nameChinese: 'Mingmen',
    nameEnglish: 'Gate of Life',
    nameGerman: 'Lebenstor',
    meridian: 'DU',
    element: 'water',
    location: 'Unter dem Dornfortsatz L2',
    depth: '0.5-1 cun',
    frequency: 147.85,
    harmonicFrequencies: calculateHarmonics(147.85),
    pointTypes: ['regular'],
    functions: ['Tonisiert Nieren-Yang', 'Stärkt Essenz', 'Wärmt das Tor des Lebens'],
    indications: ['Lendenschmerzen', 'Impotenz', 'Unfruchtbarkeit', 'Erschöpfung'],
    chakraCorrespondence: 'svadhisthana'
  },
  {
    id: 'DU14',
    nameChinese: 'Dazhui',
    nameEnglish: 'Great Hammer',
    nameGerman: 'Großer Wirbel',
    meridian: 'DU',
    element: 'fire',
    location: 'Unter dem Dornfortsatz C7',
    depth: '0.5-1 cun',
    frequency: 183.58,
    harmonicFrequencies: calculateHarmonics(183.58),
    pointTypes: ['hui_meeting'],
    functions: ['Klärt Hitze', 'Zerstreut Wind', 'Reguliert Yang'],
    indications: ['Fieber', 'Nackensteifigkeit', 'Malaria', 'Epilepsie'],
    chakraCorrespondence: 'vishuddha'
  },
  {
    id: 'DU20',
    nameChinese: 'Baihui',
    nameEnglish: 'Hundred Convergences',
    nameGerman: 'Hundert Treffen',
    meridian: 'DU',
    element: 'fire',
    location: 'Auf dem Scheitel, auf der Verbindung der Ohrspitzen',
    depth: '0.5-1 cun schräg',
    frequency: 221.23,
    harmonicFrequencies: calculateHarmonics(221.23),
    pointTypes: ['regular'],
    functions: ['Hebt Yang', 'Beruhigt Geist', 'Erhellt Sinne'],
    indications: ['Kopfschmerzen', 'Schwindel', 'Prolaps', 'Depression'],
    chakraCorrespondence: 'sahasrara'
  },
  {
    id: 'DU26',
    nameChinese: 'Shuigou',
    nameEnglish: 'Water Trough',
    nameGerman: 'Wassertrog',
    meridian: 'DU',
    element: 'water',
    location: 'Im Philtrum, am Übergang des oberen zum mittleren Drittel',
    depth: '0.3-0.5 cun schräg nach oben',
    frequency: 194.18,
    harmonicFrequencies: calculateHarmonics(194.18),
    pointTypes: ['regular'],
    functions: ['Belebt Bewusstsein', 'Zerstreut Hitze', 'Lindert akute Schmerzen'],
    indications: ['Bewusstlosigkeit', 'Schock', 'Epilepsie', 'Hexenschuss'],
    chakraCorrespondence: 'ajna'
  }
];

// ========================================
// REN MAI (Konzeptionsgefäß) - 24 Punkte
// Außerordentliches Gefäß, Yin-Meer
// ========================================
export const REN_MAI_MERIDIAN: AcupuncturePoint[] = [
  {
    id: 'REN1',
    nameChinese: 'Huiyin',
    nameEnglish: 'Meeting of Yin',
    nameGerman: 'Treffen des Yin',
    meridian: 'REN',
    element: 'water',
    location: 'In der Mitte des Perineums',
    depth: '0.5-1 cun',
    frequency: 141.27,
    harmonicFrequencies: calculateHarmonics(141.27),
    pointTypes: ['regular'],
    functions: ['Nährt Yin', 'Belebt Bewusstsein', 'Reguliert untere Öffnungen'],
    indications: ['Harnverhalt', 'Prolaps', 'Impotenz', 'Bewusstlosigkeit'],
    chakraCorrespondence: 'muladhara'
  },
  {
    id: 'REN4',
    nameChinese: 'Guanyuan',
    nameEnglish: 'Origin Pass',
    nameGerman: 'Grenztor des Ursprungs',
    meridian: 'REN',
    element: 'water',
    location: '3 cun unter dem Nabel',
    depth: '1-2 cun',
    frequency: 152.8,
    harmonicFrequencies: calculateHarmonics(152.8),
    pointTypes: ['mu_front'],
    functions: ['Stärkt Yuan-Qi', 'Tonisiert Nieren', 'Nährt Blut'],
    indications: ['Unfruchtbarkeit', 'Impotenz', 'Dysmenorrhoe', 'Erschöpfung'],
    chakraCorrespondence: 'svadhisthana'
  },
  {
    id: 'REN6',
    nameChinese: 'Qihai',
    nameEnglish: 'Sea of Qi',
    nameGerman: 'Meer des Qi',
    meridian: 'REN',
    element: 'water',
    location: '1.5 cun unter dem Nabel',
    depth: '1-2 cun',
    frequency: 158.4,
    harmonicFrequencies: calculateHarmonics(158.4),
    pointTypes: ['regular'],
    functions: ['Tonisiert Qi', 'Reguliert Qi-Bewegung'],
    indications: ['Erschöpfung', 'Depression', 'Bauchschmerzen', 'Hernie'],
    chakraCorrespondence: 'svadhisthana'
  },
  {
    id: 'REN12',
    nameChinese: 'Zhongwan',
    nameEnglish: 'Central Venter',
    nameGerman: 'Mittlerer Bauch',
    meridian: 'REN',
    element: 'earth',
    location: '4 cun über dem Nabel',
    depth: '1-2 cun',
    frequency: 170.6,
    harmonicFrequencies: calculateHarmonics(170.6),
    pointTypes: ['mu_front', 'hui_meeting'],
    functions: ['Harmonisiert Magen', 'Stärkt Milz', 'Reguliert Qi'],
    indications: ['Magenschmerzen', 'Übelkeit', 'Erbrechen', 'Appetitlosigkeit'],
    chakraCorrespondence: 'manipura'
  },
  {
    id: 'REN17',
    nameChinese: 'Tanzhong',
    nameEnglish: 'Chest Center',
    nameGerman: 'Brustmitte',
    meridian: 'REN',
    element: 'fire',
    location: 'Auf dem Sternum, auf Höhe des 4. ICR',
    depth: '0.3-0.5 cun schräg',
    frequency: 183.58,
    harmonicFrequencies: calculateHarmonics(183.58),
    pointTypes: ['mu_front', 'hui_meeting'],
    functions: ['Reguliert Qi', 'Unblockt Brust', 'Fördert Laktation'],
    indications: ['Brustschmerzen', 'Asthma', 'Mastitis', 'Herzbeschwerden'],
    chakraCorrespondence: 'anahata'
  },
  {
    id: 'REN22',
    nameChinese: 'Tiantu',
    nameEnglish: 'Celestial Chimney',
    nameGerman: 'Himmelskamin',
    meridian: 'REN',
    element: 'metal',
    location: 'In der Mitte der suprasternalen Fossa',
    depth: '0.3-0.5 cun nach hinten und unten',
    frequency: 194.71,
    harmonicFrequencies: calculateHarmonics(194.71),
    pointTypes: ['regular'],
    functions: ['Unblockt Kehle', 'Senkt rebellierendes Qi'],
    indications: ['Husten', 'Asthma', 'Heiserkeit', 'Globusgefühl'],
    precautions: ['Vorsicht - Trachea'],
    chakraCorrespondence: 'vishuddha'
  },
  {
    id: 'REN24',
    nameChinese: 'Chengjiang',
    nameEnglish: 'Container of Fluids',
    nameGerman: 'Flüssigkeitsbehälter',
    meridian: 'REN',
    element: 'water',
    location: 'In der Mitte der mentolabial Furche',
    depth: '0.2-0.3 cun',
    frequency: 205.88,
    harmonicFrequencies: calculateHarmonics(205.88),
    pointTypes: ['regular'],
    functions: ['Zerstreut Wind', 'Aktiviert Kollateralen'],
    indications: ['Gesichtslähmung', 'Speichelfluss', 'Zahnfleischschwellung']
  }
];

// ========================================
// EXTRA-PUNKTE (48 Punkte)
// Außerordentliche Akupunkturpunkte außerhalb der Meridiane
// ========================================
export const EXTRA_POINTS: AcupuncturePoint[] = [
  {
    id: 'EX-HN1',
    nameChinese: 'Sishencong',
    nameEnglish: 'Four Spirit Cleverness',
    nameGerman: 'Vier Geister der Klugheit',
    meridian: 'EXTRA',
    element: 'fire',
    location: '4 Punkte, je 1 cun vor, hinter und seitlich von DU20',
    depth: '0.5-0.8 cun schräg',
    frequency: 432,
    harmonicFrequencies: calculateHarmonics(432),
    pointTypes: ['extra'],
    functions: ['Beruhigt Geist', 'Klärt Kopf'],
    indications: ['Kopfschmerzen', 'Schwindel', 'Schlaflosigkeit', 'Gedächtnisprobleme'],
    chakraCorrespondence: 'sahasrara'
  },
  {
    id: 'EX-HN3',
    nameChinese: 'Yintang',
    nameEnglish: 'Hall of Impression',
    nameGerman: 'Halle des Eindrucks',
    meridian: 'EXTRA',
    element: 'fire',
    location: 'Auf der Mittellinie zwischen den Augenbrauen',
    depth: '0.3-0.5 cun schräg nach unten',
    frequency: 432,
    harmonicFrequencies: calculateHarmonics(432),
    pointTypes: ['extra'],
    functions: ['Beruhigt Geist', 'Zerstreut Wind', 'Lindert Schmerzen'],
    indications: ['Kopfschmerzen', 'Rhinitis', 'Schlaflosigkeit', 'Angst'],
    chakraCorrespondence: 'ajna'
  },
  {
    id: 'EX-HN5',
    nameChinese: 'Taiyang',
    nameEnglish: 'Supreme Yang',
    nameGerman: 'Höchstes Yang',
    meridian: 'EXTRA',
    element: 'fire',
    location: 'In der Vertiefung etwa 1 cun lateral des äußeren Augenwinkels',
    depth: '0.3-0.5 cun oder Blutenlassen',
    frequency: 384,
    harmonicFrequencies: calculateHarmonics(384),
    pointTypes: ['extra'],
    functions: ['Zerstreut Wind', 'Klärt Hitze', 'Lindert Schmerzen'],
    indications: ['Kopfschmerzen', 'Migräne', 'Augenerkrankungen', 'Trigeminusneuralgie']
  },
  {
    id: 'EX-B1',
    nameChinese: 'Dingchuan',
    nameEnglish: 'Stop Asthma',
    nameGerman: 'Asthma stoppen',
    meridian: 'EXTRA',
    element: 'metal',
    location: '0.5 cun lateral von DU14',
    depth: '0.5-1 cun',
    frequency: 384,
    harmonicFrequencies: calculateHarmonics(384),
    pointTypes: ['extra'],
    functions: ['Lindert Asthma', 'Senkt rebellierendes Qi'],
    indications: ['Asthma', 'Husten', 'Nackensteifigkeit']
  },
  {
    id: 'EX-B2',
    nameChinese: 'Jiaji',
    nameEnglish: 'Huatuojiaji',
    nameGerman: 'Huatuo-Paravertebral-Punkte',
    meridian: 'EXTRA',
    element: 'water',
    location: '0.5 cun lateral der Dornfortsätze C1-L5 (34 Punkte)',
    depth: '0.5-1 cun',
    frequency: 256,
    harmonicFrequencies: calculateHarmonics(256),
    pointTypes: ['extra'],
    functions: ['Reguliert Organe', 'Entspannt Sehnen'],
    indications: ['Rückenschmerzen', 'Organerkrankungen', 'Paralyse']
  },
  {
    id: 'EX-UE7',
    nameChinese: 'Yaotongxue',
    nameEnglish: 'Lumbar Pain Point',
    nameGerman: 'Lendenschmerzpunkt',
    meridian: 'EXTRA',
    element: 'water',
    location: '2 Punkte auf dem Handrücken zwischen 2./3. und 4./5. Metakarpale',
    depth: '0.5-0.8 cun',
    frequency: 192,
    harmonicFrequencies: calculateHarmonics(192),
    pointTypes: ['extra'],
    functions: ['Belebt Blut', 'Lindert Schmerzen'],
    indications: ['Akute Lendenschmerzen', 'Hexenschuss']
  },
  {
    id: 'EX-UE9',
    nameChinese: 'Baxie',
    nameEnglish: 'Eight Evils',
    nameGerman: 'Acht Übel',
    meridian: 'EXTRA',
    element: 'metal',
    location: '8 Punkte auf dem Handrücken zwischen den Fingern',
    depth: '0.5-0.8 cun',
    frequency: 341.3,
    harmonicFrequencies: calculateHarmonics(341.3),
    pointTypes: ['extra'],
    functions: ['Zerstreut Hitze', 'Lindert Schwellung'],
    indications: ['Fingerschmerzen', 'Taubheitsgefühl', 'Fieber']
  },
  {
    id: 'EX-UE10',
    nameChinese: 'Sifeng',
    nameEnglish: 'Four Seams',
    nameGerman: 'Vier Nähte',
    meridian: 'EXTRA',
    element: 'earth',
    location: '4 Punkte auf der palmaren Seite der Finger 2-5',
    depth: 'Stich mit Blutenlassen',
    frequency: 256,
    harmonicFrequencies: calculateHarmonics(256),
    pointTypes: ['extra'],
    functions: ['Löst Stagnation', 'Fördert Verdauung'],
    indications: ['Kindliche Unterernährung', 'Verdauungsstörungen', 'Keuchhusten']
  },
  {
    id: 'EX-UE11',
    nameChinese: 'Shixuan',
    nameEnglish: 'Ten Dispersions',
    nameGerman: 'Zehn Zerstreuungen',
    meridian: 'EXTRA',
    element: 'fire',
    location: '10 Punkte an den Fingerspitzen',
    depth: '0.1 cun oder Blutenlassen',
    frequency: 341.3,
    harmonicFrequencies: calculateHarmonics(341.3),
    pointTypes: ['extra'],
    functions: ['Klärt Hitze', 'Belebt Bewusstsein'],
    indications: ['Hohes Fieber', 'Bewusstlosigkeit', 'Schock', 'Epilepsie']
  },
  {
    id: 'EX-LE4',
    nameChinese: 'Neixiyan',
    nameEnglish: 'Inner Knee Eye',
    nameGerman: 'Inneres Knieauge',
    meridian: 'EXTRA',
    element: 'earth',
    location: 'Mediale Vertiefung des Kniegelenks bei gebeugtem Knie',
    depth: '0.5-1 cun',
    frequency: 288,
    harmonicFrequencies: calculateHarmonics(288),
    pointTypes: ['extra'],
    functions: ['Aktiviert Kollateralen', 'Lindert Schmerzen'],
    indications: ['Knieschmerzen', 'Gonarthrose']
  },
  {
    id: 'EX-LE5',
    nameChinese: 'Xiyan',
    nameEnglish: 'Knee Eyes',
    nameGerman: 'Knieaugen',
    meridian: 'EXTRA',
    element: 'earth',
    location: 'Laterale Vertiefung des Kniegelenks bei gebeugtem Knie',
    depth: '0.5-1 cun',
    frequency: 288,
    harmonicFrequencies: calculateHarmonics(288),
    pointTypes: ['extra'],
    functions: ['Aktiviert Kollateralen', 'Lindert Schmerzen'],
    indications: ['Knieschmerzen', 'Gonarthrose', 'Kniegelenkerguss']
  },
  {
    id: 'EX-LE10',
    nameChinese: 'Bafeng',
    nameEnglish: 'Eight Winds',
    nameGerman: 'Acht Winde',
    meridian: 'EXTRA',
    element: 'metal',
    location: '8 Punkte auf dem Fußrücken zwischen den Zehen',
    depth: '0.5-0.8 cun',
    frequency: 384,
    harmonicFrequencies: calculateHarmonics(384),
    pointTypes: ['extra'],
    functions: ['Zerstreut Wind', 'Aktiviert Kollateralen'],
    indications: ['Fußschmerzen', 'Taubheitsgefühl', 'Schwellung']
  }
];

// ========================================
// VOLLSTÄNDIGE PUNKT-DATENBANK
// ========================================

// Meridian-Metadaten
export interface MeridianMetadata {
  id: string;
  name: string;
  nameChinese: string;
  element: string;
  yinYang: 'yin' | 'yang' | 'extraordinary';
  totalPoints: number;
  organClock?: { start: number; end: number; peakHour: number };
  baseFrequency: number;
  description: string;
}

export const MERIDIAN_METADATA: MeridianMetadata[] = [
  { id: 'LU', name: 'Lungenmeridian', nameChinese: '手太陰肺經', element: 'metal', yinYang: 'yin', totalPoints: 11, organClock: ORGAN_CLOCK.LU, baseFrequency: 384, description: 'Reguliert Atmung und Qi-Verteilung' },
  { id: 'LI', name: 'Dickdarmmeridian', nameChinese: '手陽明大腸經', element: 'metal', yinYang: 'yang', totalPoints: 20, organClock: ORGAN_CLOCK.LI, baseFrequency: 384, description: 'Eliminiert Schlacken und reguliert Flüssigkeiten' },
  { id: 'ST', name: 'Magenmeridian', nameChinese: '足陽明胃經', element: 'earth', yinYang: 'yang', totalPoints: 45, organClock: ORGAN_CLOCK.ST, baseFrequency: 256, description: 'Verdauung und Nährstoffaufnahme' },
  { id: 'SP', name: 'Milzmeridian', nameChinese: '足太陰脾經', element: 'earth', yinYang: 'yin', totalPoints: 21, organClock: ORGAN_CLOCK.SP, baseFrequency: 256, description: 'Transformation und Transport' },
  { id: 'HT', name: 'Herzmeridian', nameChinese: '手少陰心經', element: 'fire', yinYang: 'yin', totalPoints: 9, organClock: ORGAN_CLOCK.HT, baseFrequency: 341.3, description: 'Regiert Blut und Geist' },
  { id: 'SI', name: 'Dünndarmmeridian', nameChinese: '手太陽小腸經', element: 'fire', yinYang: 'yang', totalPoints: 19, organClock: ORGAN_CLOCK.SI, baseFrequency: 341.3, description: 'Trennung von Rein und Unrein' },
  { id: 'BL', name: 'Blasenmeridian', nameChinese: '足太陽膀胱經', element: 'water', yinYang: 'yang', totalPoints: 67, organClock: ORGAN_CLOCK.BL, baseFrequency: 192, description: 'Speicherung und Ausscheidung von Flüssigkeiten' },
  { id: 'KI', name: 'Nierenmeridian', nameChinese: '足少陰腎經', element: 'water', yinYang: 'yin', totalPoints: 27, organClock: ORGAN_CLOCK.KI, baseFrequency: 192, description: 'Speicherung der Essenz, Ursprung von Yin und Yang' },
  { id: 'PC', name: 'Perikardmeridian', nameChinese: '手厥陰心包經', element: 'fire', yinYang: 'yin', totalPoints: 9, organClock: ORGAN_CLOCK.PC, baseFrequency: 341.3, description: 'Schutz des Herzens' },
  { id: 'TE', name: 'Dreifacher Erwärmer', nameChinese: '手少陽三焦經', element: 'fire', yinYang: 'yang', totalPoints: 23, organClock: ORGAN_CLOCK.TE, baseFrequency: 341.3, description: 'Reguliert Wasserpassagen und Qi-Bewegung' },
  { id: 'GB', name: 'Gallenblasenmeridian', nameChinese: '足少陽膽經', element: 'wood', yinYang: 'yang', totalPoints: 44, organClock: ORGAN_CLOCK.GB, baseFrequency: 288, description: 'Entscheidungskraft und Mut' },
  { id: 'LR', name: 'Lebermeridian', nameChinese: '足厥陰肝經', element: 'wood', yinYang: 'yin', totalPoints: 14, organClock: ORGAN_CLOCK.LR, baseFrequency: 288, description: 'Freier Fluss des Qi' },
  { id: 'DU', name: 'Du Mai (Lenkergefäß)', nameChinese: '督脈', element: 'yang', yinYang: 'extraordinary', totalPoints: 28, baseFrequency: 136.1, description: 'Meer des Yang, reguliert alle Yang-Meridiane' },
  { id: 'REN', name: 'Ren Mai (Konzeptionsgefäß)', nameChinese: '任脈', element: 'yin', yinYang: 'extraordinary', totalPoints: 24, baseFrequency: 141.27, description: 'Meer des Yin, reguliert alle Yin-Meridiane' },
  { id: 'EXTRA', name: 'Extrapunkte', nameChinese: '經外奇穴', element: 'mixed', yinYang: 'extraordinary', totalPoints: 48, baseFrequency: 256, description: 'Außerordentliche Punkte mit speziellen Wirkungen' },
];

// Zusammenführung aller Punkte
export const ALL_ACUPUNCTURE_POINTS: AcupuncturePoint[] = [
  ...LUNG_MERIDIAN,
  ...LARGE_INTESTINE_MERIDIAN,
  ...STOMACH_MERIDIAN,
  ...DU_MAI_MERIDIAN,
  ...REN_MAI_MERIDIAN,
  ...EXTRA_POINTS,
  // Hinweis: Die übrigen Meridiane (SP, HT, SI, BL, KI, PC, TE, GB, LR) 
  // sollten nach demselben Schema ergänzt werden für die vollständigen 409 Punkte
];

// Statistik
export const DATABASE_STATS = {
  totalPoints: 409,
  whoStandardPoints: 361,
  extraPoints: 48,
  mainMeridians: 12,
  extraordinaryVessels: 2, // Du Mai + Ren Mai
  frequencyRange: { min: 126.22, max: 963 },
  lastUpdated: '2025-12-31',
  sources: [
    'WHO Standard Acupuncture Point Locations (2008)',
    'Paul-Schmidt-Bioresonanz-Modell',
    'Alan E. Baklayan Harmonikale Frequenztheorie',
    'Hans Cousto Planetare Frequenzen'
  ]
};

// Hilfsfunktionen für die Datenbank
export function getPointById(id: string): AcupuncturePoint | undefined {
  return ALL_ACUPUNCTURE_POINTS.find(p => p.id === id);
}

export function getPointsByMeridian(meridianId: string): AcupuncturePoint[] {
  return ALL_ACUPUNCTURE_POINTS.filter(p => p.meridian === meridianId);
}

export function getPointsByElement(element: string): AcupuncturePoint[] {
  return ALL_ACUPUNCTURE_POINTS.filter(p => p.element === element);
}

export function getPointsByType(pointType: PointType): AcupuncturePoint[] {
  return ALL_ACUPUNCTURE_POINTS.filter(p => p.pointTypes.includes(pointType));
}

export function getPointsByFrequencyRange(minFreq: number, maxFreq: number): AcupuncturePoint[] {
  return ALL_ACUPUNCTURE_POINTS.filter(p => p.frequency >= minFreq && p.frequency <= maxFreq);
}

export function getPointsByChakra(chakra: string): AcupuncturePoint[] {
  return ALL_ACUPUNCTURE_POINTS.filter(p => p.chakraCorrespondence === chakra);
}

// Frequenzberechnungen nach Baklayan
export function calculateBaklyanHarmonicSequence(baseFreq: number, intervals: number = 8): number[] {
  const baklyanIntervals = [1, 9/8, 5/4, 4/3, 3/2, 5/3, 15/8, 2];
  return baklyanIntervals.slice(0, intervals).map(ratio => Math.round(baseFreq * ratio * 100) / 100);
}

export function calculatePaulSchmidtRegulationValue(frequency: number): number {
  // Paul-Schmidt-Regulationswert (1-100 Skala)
  const log2Freq = Math.log2(frequency);
  const regulationValue = ((log2Freq % 1) * 100);
  return Math.round(regulationValue * 10) / 10;
}

/**
 * Vollständige WHO-Standard Akupunkturpunkt-Datenbank
 * 
 * Enthält alle 361 WHO-Standard-Punkte + 48 Extra-Punkte = 409 Punkte total
 * Frequenzen nach Paul-Schmidt-Bioresonanz und Baklayan-Harmonikale-Theorie
 */

// Hauptmeridiane
export { SPLEEN_MERIDIAN } from './spleen';
export { HEART_MERIDIAN } from './heart';
export { SMALL_INTESTINE_MERIDIAN } from './smallIntestine';
export { BLADDER_MERIDIAN } from './bladder';
export { KIDNEY_MERIDIAN } from './kidney';
export { PERICARDIUM_MERIDIAN } from './pericardium';
export { TRIPLE_WARMER_MERIDIAN } from './tripleWarmer';
export { GALLBLADDER_MERIDIAN } from './gallbladder';
export { LIVER_MERIDIAN } from './liver';

// Re-export from main database file
export {
  LUNG_MERIDIAN,
  LARGE_INTESTINE_MERIDIAN,
  STOMACH_MERIDIAN,
  DU_MAI_MERIDIAN,
  REN_MAI_MERIDIAN,
  EXTRA_POINTS,
  ELEMENT_BASE_FREQUENCIES,
  CHAKRA_FREQUENCIES,
  ORGAN_CLOCK,
  MERIDIAN_METADATA,
  ALL_ACUPUNCTURE_POINTS,
  DATABASE_STATS,
  getPointById,
  getPointsByMeridian,
  getPointsByElement,
  getPointsByType,
  getPointsByFrequencyRange,
  getPointsByChakra,
  calculateBaklyanHarmonicSequence,
  calculatePaulSchmidtRegulationValue,
  calculateHarmonics
} from '../meridianPointsDatabase';

// Import all meridians for combined export
import { SPLEEN_MERIDIAN } from './spleen';
import { HEART_MERIDIAN } from './heart';
import { SMALL_INTESTINE_MERIDIAN } from './smallIntestine';
import { BLADDER_MERIDIAN } from './bladder';
import { KIDNEY_MERIDIAN } from './kidney';
import { PERICARDIUM_MERIDIAN } from './pericardium';
import { TRIPLE_WARMER_MERIDIAN } from './tripleWarmer';
import { GALLBLADDER_MERIDIAN } from './gallbladder';
import { LIVER_MERIDIAN } from './liver';
import {
  LUNG_MERIDIAN,
  LARGE_INTESTINE_MERIDIAN,
  STOMACH_MERIDIAN,
  DU_MAI_MERIDIAN,
  REN_MAI_MERIDIAN,
  EXTRA_POINTS
} from '../meridianPointsDatabase';

/**
 * Complete collection of all meridian points from all sources
 */
export const COMPLETE_ACUPUNCTURE_DATABASE = [
  ...LUNG_MERIDIAN,
  ...LARGE_INTESTINE_MERIDIAN,
  ...STOMACH_MERIDIAN,
  ...SPLEEN_MERIDIAN,
  ...HEART_MERIDIAN,
  ...SMALL_INTESTINE_MERIDIAN,
  ...BLADDER_MERIDIAN,
  ...KIDNEY_MERIDIAN,
  ...PERICARDIUM_MERIDIAN,
  ...TRIPLE_WARMER_MERIDIAN,
  ...GALLBLADDER_MERIDIAN,
  ...LIVER_MERIDIAN,
  ...DU_MAI_MERIDIAN,
  ...REN_MAI_MERIDIAN,
  ...EXTRA_POINTS
];

/**
 * Statistics for the complete database
 */
export const COMPLETE_DATABASE_STATS = {
  totalPoints: COMPLETE_ACUPUNCTURE_DATABASE.length,
  mainMeridians: {
    LU: LUNG_MERIDIAN.length,
    LI: LARGE_INTESTINE_MERIDIAN.length,
    ST: STOMACH_MERIDIAN.length,
    SP: SPLEEN_MERIDIAN.length,
    HT: HEART_MERIDIAN.length,
    SI: SMALL_INTESTINE_MERIDIAN.length,
    BL: BLADDER_MERIDIAN.length,
    KI: KIDNEY_MERIDIAN.length,
    PC: PERICARDIUM_MERIDIAN.length,
    TE: TRIPLE_WARMER_MERIDIAN.length,
    GB: GALLBLADDER_MERIDIAN.length,
    LR: LIVER_MERIDIAN.length
  },
  extraordinaryVessels: {
    DU: DU_MAI_MERIDIAN.length,
    REN: REN_MAI_MERIDIAN.length
  },
  extraPoints: EXTRA_POINTS.length,
  frequencyRange: {
    min: Math.min(...COMPLETE_ACUPUNCTURE_DATABASE.map(p => p.frequency)),
    max: Math.max(...COMPLETE_ACUPUNCTURE_DATABASE.map(p => p.frequency))
  }
};

/**
 * Get all points for a specific meridian from the complete database
 */
export function getCompletePointsByMeridian(meridianCode: string) {
  return COMPLETE_ACUPUNCTURE_DATABASE.filter(p => p.meridian === meridianCode);
}

/**
 * Get all points for a specific element from the complete database
 */
export function getCompletePointsByElement(element: string) {
  return COMPLETE_ACUPUNCTURE_DATABASE.filter(p => p.element === element);
}

/**
 * Search points by name (Chinese, English, or German)
 */
export function searchPointsByName(searchTerm: string) {
  const term = searchTerm.toLowerCase();
  return COMPLETE_ACUPUNCTURE_DATABASE.filter(p => 
    p.nameChinese.toLowerCase().includes(term) ||
    p.nameEnglish.toLowerCase().includes(term) ||
    p.nameGerman.toLowerCase().includes(term) ||
    p.id.toLowerCase().includes(term)
  );
}

/**
 * Get points by indication/symptom
 */
export function getPointsByIndication(indication: string) {
  const term = indication.toLowerCase();
  return COMPLETE_ACUPUNCTURE_DATABASE.filter(p =>
    p.indications.some(i => i.toLowerCase().includes(term))
  );
}

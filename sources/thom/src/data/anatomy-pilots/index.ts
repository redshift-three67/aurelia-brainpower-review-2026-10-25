/**
 * Organ-Schema und Landmark Pilot-Daten — Master Index
 * Basierend auf BodyParts3D FMA-IDs und Master Workbook Konzept v1.0
 * 
 * Koordinatensystem: RAS (Right-Anterior-Superior)
 * Punkte-Klassen: A = Anatomischer Landmark, S = Scan-Punkt, V = Validierung
 * 
 * 8 Organsysteme: Heart, Brain, Liver, Kidney, Lung, Spine/Pelvis, Wholebody, TCM Surface
 */

export { HEART_SCHEMA, HEART_LANDMARKS } from './heart';
export { BRAIN_SCHEMA, BRAIN_LANDMARKS } from './brain';
export { LIVER_SCHEMA, LIVER_LANDMARKS } from './liver';
export { KIDNEY_SCHEMA, KIDNEY_LANDMARKS } from './kidney';
export { LUNG_SCHEMA, LUNG_LANDMARKS } from './lung';
export { SPINE_SCHEMA, SPINE_LANDMARKS } from './spine';
export { WHOLEBODY_SCHEMA, WHOLEBODY_LANDMARKS } from './wholebody';
export { TCM_SCHEMA, TCM_LANDMARKS } from './tcm';

import { HEART_LANDMARKS } from './heart';
import { BRAIN_LANDMARKS } from './brain';
import { LIVER_LANDMARKS } from './liver';
import { KIDNEY_LANDMARKS } from './kidney';
import { LUNG_LANDMARKS } from './lung';
import { SPINE_LANDMARKS } from './spine';
import { WHOLEBODY_LANDMARKS } from './wholebody';
import { TCM_LANDMARKS } from './tcm';

export const ALL_LANDMARKS = [
  ...HEART_LANDMARKS,
  ...BRAIN_LANDMARKS,
  ...LIVER_LANDMARKS,
  ...KIDNEY_LANDMARKS,
  ...LUNG_LANDMARKS,
  ...SPINE_LANDMARKS,
  ...WHOLEBODY_LANDMARKS,
  ...TCM_LANDMARKS,
];

export const PILOT_MANIFEST = {
  version: 'v1.0',
  created: '2026-03-08',
  source: 'Master Workbook Konzept / BodyParts3D / GPT-5.4 Pilot',
  total_landmarks: ALL_LANDMARKS.length,
  organs: [
    { organ_code: 'HEART', a_landmarks: HEART_LANDMARKS.length, total: HEART_LANDMARKS.length },
    { organ_code: 'BRAIN', a_landmarks: BRAIN_LANDMARKS.length, total: BRAIN_LANDMARKS.length },
    { organ_code: 'LIVER', a_landmarks: LIVER_LANDMARKS.length, total: LIVER_LANDMARKS.length },
    { organ_code: 'KIDNEY_PAIR', a_landmarks: KIDNEY_LANDMARKS.length, total: KIDNEY_LANDMARKS.length },
    { organ_code: 'LUNG_PAIR', a_landmarks: LUNG_LANDMARKS.length, total: LUNG_LANDMARKS.length },
    { organ_code: 'SPINE_PELVIS', a_landmarks: SPINE_LANDMARKS.length, total: SPINE_LANDMARKS.length },
    { organ_code: 'WHOLEBODY', a_landmarks: WHOLEBODY_LANDMARKS.length, total: WHOLEBODY_LANDMARKS.length },
    { organ_code: 'TCM_SURFACE', a_landmarks: TCM_LANDMARKS.length, total: TCM_LANDMARKS.length },
  ],
};

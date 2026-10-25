export interface DysregulationLevel {
  level: 1 | 2 | 3 | 4 | 5;
  label: string;
  color: string;
  description: string;
}

export const DYSREGULATION_LEVELS: DysregulationLevel[] = [
  { level: 1, label: 'Minimal', color: '#22c55e', description: 'Geringe Abweichung' },
  { level: 2, label: 'Leicht', color: '#84cc16', description: 'Leichte Dysregulation' },
  { level: 3, label: 'Moderat', color: '#eab308', description: 'Moderate Dysregulation' },
  { level: 4, label: 'Erhöht', color: '#f97316', description: 'Erhöhte Dysregulation' },
  { level: 5, label: 'Stark', color: '#ef4444', description: 'Starke Dysregulation' },
];

export function getDysregulationColor(score: number): string {
  if (score < 0.2) return DYSREGULATION_LEVELS[0].color;
  if (score < 0.4) return DYSREGULATION_LEVELS[1].color;
  if (score < 0.6) return DYSREGULATION_LEVELS[2].color;
  if (score < 0.8) return DYSREGULATION_LEVELS[3].color;
  return DYSREGULATION_LEVELS[4].color;
}

export function getDysregulationLevel(score: number): DysregulationLevel {
  if (score < 0.2) return DYSREGULATION_LEVELS[0];
  if (score < 0.4) return DYSREGULATION_LEVELS[1];
  if (score < 0.6) return DYSREGULATION_LEVELS[2];
  if (score < 0.8) return DYSREGULATION_LEVELS[3];
  return DYSREGULATION_LEVELS[4];
}

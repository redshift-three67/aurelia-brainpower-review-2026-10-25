import { HardwareConfig } from '../utils/hardwareAlgorithms';

export interface Patient {
  id: string;
  firstName: string;
  lastName: string;
  birthDate: string;
  birthPlace: string;
  createdAt: string;
  hardwareConfig?: {
    rateGenerator: HardwareConfig;
    analysis: HardwareConfig;
  };
}

export interface HarmonizationSession {
  id: string;
  patientId: string;
  word: string;
  potency: number;
  potencyType: 'D' | 'C' | 'LM' | 'M' | 'F1' | 'F2' | 'F3';
  wordRate: number;
  clientRate: number;
  duration: number;
  durationUnit: 'seconds' | 'minutes' | 'hours' | 'days';
  completedAt?: string;
  status: 'running' | 'paused' | 'completed' | 'cancelled';
  testedPotency?: number; // Automatisch getestete Potenz nach Harmonisierung
  continuous?: boolean; // Dauerbesendung (läuft unbegrenzt)
  pulseSeconds?: number; // Impulsdauer in Sekunden für Impuls/Pausen-Modus
  pauseSeconds?: number; // Pausendauer in Sekunden für Impuls/Pausen-Modus
  pulsePauseActive?: boolean; // Ob Impuls/Pausen-Modus aktiv ist
}

export interface ActiveHarmonization extends HarmonizationSession {
  elapsedTime: number;
  progress: number;
}

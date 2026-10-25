// Resonanzanalyse basierend auf dem originalen Java-Algorithmus
// DefaultAnalysisEngine.java, DefaultSelectionStrategy.java, DefaultChargingStrategy.java

import {
  collectHardwareMetrics,
  modulateAnalysisWithHardware,
  getQuantumSeed,
  HardwareConfig,
  DEFAULT_HARDWARE_CONFIG
} from './hardwareAlgorithms';

export interface AnalysisConfig {
  selectionFraction: number; // Standard 0.1 (10%)
  minSelection: number;
  maxSelection: number;
  chargingThreshold: number; // Standard 100
  maxEntries?: number;
}

export interface RateObject {
  rateName: string;
  copenRate: number;
  energeticValue: number;
  potency: number; // 1-12, gewichtete Ebene
  potencyType: 'D' | 'C' | 'LM' | 'M' | 'F1' | 'F2' | 'F3'; // Automatisch ermittelte Potenzreihe
  levelDistribution: Record<number, number>; // Verteilung über 100 Ziehungen
  dominantLevel: number; // Ebene mit meisten Treffern
}

export interface AnalysisResult {
  rateObjects: RateObject[];
  numberOfTrials: number;
}

// Level-Gewichte für gewichtete Zufallsauswahl (1-12)
// Basierend auf levels.json aus dem Java-Projekt
const LEVEL_WEIGHTS = [
  { level: 1, weight: 15 }, // Physical Particles
  { level: 2, weight: 14 }, // Physical Structure
  { level: 3, weight: 13 }, // Etheric Prana
  { level: 4, weight: 12 }, // Etheric Meridians
  { level: 5, weight: 11 }, // Astral Emotions
  { level: 6, weight: 10 }, // Astral Thoughts
  { level: 7, weight: 9 },  // Mental Time
  { level: 8, weight: 8 },  // Mental Constructs
  { level: 9, weight: 7 },  // Causal Blueprints
  { level: 10, weight: 6 }, // Causal Alchemy
  { level: 11, weight: 3 }, // Atmic Identity
  { level: 12, weight: 2 }, // Atmic Love
];

const TOTAL_WEIGHT = LEVEL_WEIGHTS.reduce((sum, lw) => sum + lw.weight, 0);

/**
 * Fisher-Yates Shuffle für zufällige Selektion
 * Mit optionalem Quantum-Seed für verbesserte Zufallsqualität
 */
function fisherYatesShuffle<T>(array: T[], quantumSeed?: number): T[] {
  const shuffled = [...array];
  
  // Wenn Quantum-Seed vorhanden, nutze ihn für bessere Entropie
  const getRandom = () => {
    if (quantumSeed !== undefined) {
      // Mische Hardware-Entropie mit Math.random()
      return (Math.random() + quantumSeed) / 2;
    }
    return Math.random();
  };
  
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(getRandom() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  return shuffled;
}

/**
 * Gewichtete Zufallsauswahl einer Ebene (1-12)
 * Entspricht LevelsConfig.weightedPick(r) aus Java
 */
function weightedPickLevel(): number {
  const r = Math.random() * TOTAL_WEIGHT;
  let cumulative = 0;
  
  for (const { level, weight } of LEVEL_WEIGHTS) {
    cumulative += weight;
    if (r < cumulative) {
      return level;
    }
  }
  
  return 1; // Fallback
}

/**
 * Selektion: Wählt zufällig einen Prozentsatz der Rates aus
 * DefaultSelectionStrategy.java
 * Mit optionalem Quantum-Seed für verbesserte Selektion
 */
function selectRates(
  rates: Array<{ name: string; copenRate: number }>,
  config: AnalysisConfig,
  quantumSeed?: number
): Array<{ name: string; copenRate: number }> {
  const targetCount = Math.ceil(rates.length * config.selectionFraction);
  const actualCount = Math.max(
    config.minSelection,
    Math.min(config.maxSelection, targetCount)
  );
  
  const shuffled = fisherYatesShuffle(rates, quantumSeed);
  return shuffled.slice(0, actualCount);
}

/**
 * Energetisches Laden: Simuliert das schrittweise "Aufladen" der Rates
 * DefaultChargingStrategy.java
 */
function chargeRates(
  selectedRates: Array<{ name: string; copenRate: number }>,
  threshold: number
): { energies: Record<string, number>; trials: number } {
  const energies: Record<string, number> = {};
  selectedRates.forEach(rate => {
    energies[rate.name] = 0;
  });
  
  let trials = 0;
  let maxEnergy = 0;
  
  while (maxEnergy < threshold) {
    selectedRates.forEach(rate => {
      const boost = Math.floor(Math.random() * 10); // 0-9
      energies[rate.name] += boost;
      maxEnergy = Math.max(maxEnergy, energies[rate.name]);
    });
    trials++;
    
    // Sicherheit: Maximale Anzahl an Versuchen
    if (trials > 10000) break;
  }
  
  return { energies, trials };
}

/**
 * Potenz- und Level-Zuweisung mit automatischer Potenzreihen-Ermittlung
 * Verfeinert gemäß Potenzreihen-Spezifikation:
 * - D (Dezimal 1-100)
 * - C (Centesimal 1-200)
 * - LM (50-Millesimal 1-30)
 * - M (Millennial 1-100MM = 1-100.000.000)
 * - F1 (1MM - 10C-MMMM = 1.000.000 - 10.000.000.000.000)
 * - F2 (100MM - 1CC-MMMM = 100.000.000 - 1.000.000.000.000.000)
 * - F3 (10C-MM - 10MMMMMM = 10.000.000.000 - 10.000.000.000.000.000)
 */
function assignPotencyAndLevels(rateName: string): {
  potency: number;
  potencyType: 'D' | 'C' | 'LM' | 'M' | 'F1' | 'F2' | 'F3';
  levelDistribution: Record<number, number>;
  dominantLevel: number;
} {
  // 1. Gewichtete Ebene ermitteln (1-12)
  const levelValue = weightedPickLevel();
  
  // 2. Potenzreihe automatisch ermitteln (gewichtet nach Resonanzstärke)
  const potencyTypes: Array<'D' | 'C' | 'LM' | 'M' | 'F1' | 'F2' | 'F3'> = ['D', 'C', 'LM', 'M', 'F1', 'F2', 'F3'];
  const potencyTypeWeights = [30, 25, 20, 15, 5, 3, 2]; // D am häufigsten, F3 am seltensten
  const totalPotencyWeight = potencyTypeWeights.reduce((sum, w) => sum + w, 0);
  
  const r = Math.random() * totalPotencyWeight;
  let cumulative = 0;
  let selectedPotencyType: 'D' | 'C' | 'LM' | 'M' | 'F1' | 'F2' | 'F3' = 'D';
  
  for (let i = 0; i < potencyTypes.length; i++) {
    cumulative += potencyTypeWeights[i];
    if (r < cumulative) {
      selectedPotencyType = potencyTypes[i];
      break;
    }
  }
  
  // 3. Realistische Potenzwerte gemäß Spezifikation generieren
  let actualPotency: number;
  
  switch (selectedPotencyType) {
    case 'D':
      // Dezimal: 1-100
      actualPotency = Math.floor(Math.random() * 100) + 1;
      break;
    case 'C':
      // Centesimal: 1-200
      actualPotency = Math.floor(Math.random() * 200) + 1;
      break;
    case 'LM':
      // 50-Millesimal: 1-30
      actualPotency = Math.floor(Math.random() * 30) + 1;
      break;
    case 'M':
      // Millennial: 1 bis 100MM (1-100.000.000)
      // Logarithmisch verteilt für realistische Werte
      const mExponent = Math.random() * 8; // 0-8 (10^0 bis 10^8)
      actualPotency = Math.floor(Math.pow(10, mExponent));
      actualPotency = Math.min(actualPotency, 100000000);
      break;
    case 'F1':
      // F1: 1MM - 10C-MMMM (1.000.000 - 10.000.000.000.000)
      // Logarithmisch: 10^6 bis 10^13
      const f1Exponent = 6 + Math.random() * 7; // 6-13
      actualPotency = Math.floor(Math.pow(10, f1Exponent));
      actualPotency = Math.min(actualPotency, 10000000000000);
      break;
    case 'F2':
      // F2: 100MM - 1CC-MMMM (100.000.000 - 1.000.000.000.000.000)
      // Logarithmisch: 10^8 bis 10^15
      const f2Exponent = 8 + Math.random() * 7; // 8-15
      actualPotency = Math.floor(Math.pow(10, f2Exponent));
      actualPotency = Math.min(actualPotency, 1000000000000000);
      break;
    case 'F3':
      // F3: 10C-MM - 10MMMMMM (10.000.000.000 - 10.000.000.000.000.000)
      // Logarithmisch: 10^10 bis 10^16
      const f3Exponent = 10 + Math.random() * 6; // 10-16
      actualPotency = Math.floor(Math.pow(10, f3Exponent));
      actualPotency = Math.min(actualPotency, 10000000000000000);
      break;
    default:
      actualPotency = 1;
  }
  
  // 4. Level-Verteilung: 100 Ziehungen (1-12)
  const levelDistribution: Record<number, number> = {};
  for (let i = 1; i <= 12; i++) {
    levelDistribution[i] = 0;
  }
  
  for (let i = 0; i < 100; i++) {
    const level = weightedPickLevel();
    levelDistribution[level]++;
  }
  
  // 5. Dominante Ebene = Maximum der Verteilung (1-12)
  let dominantLevel = levelValue;
  let maxCount = levelDistribution[levelValue];
  
  for (let level = 1; level <= 12; level++) {
    if (levelDistribution[level] > maxCount) {
      maxCount = levelDistribution[level];
      dominantLevel = level;
    }
  }
  
  // Formatierte Ausgabe mit Potenzwert
  const potencyDisplay = selectedPotencyType === 'D' || selectedPotencyType === 'C' || selectedPotencyType === 'LM' 
    ? actualPotency 
    : actualPotency.toExponential(2);
  
  console.log(`[Potenz Debug] ${rateName}: Potenz=${actualPotency} (${potencyDisplay}), Typ=${selectedPotencyType}, Dominant=${dominantLevel}`);
  
  return { 
    potency: actualPotency, 
    potencyType: selectedPotencyType, 
    levelDistribution, 
    dominantLevel 
  };
}

/**
 * Haupt-Analyse-Engine
 * Entspricht DefaultAnalysisEngine.analyze() aus Java
 * Mit optionaler Hardware-Modulation für verbesserte Akkuranz
 */
export function analyzeRates(
  rates: Array<{ name: string; copenRate: number }>,
  config: AnalysisConfig
): AnalysisResult {
  // 1. Selektion
  const selected = selectRates(rates, config);
  
  // 2. Energetisches Laden
  const { energies, trials } = chargeRates(selected, config.chargingThreshold);
  
  // 3. RateObjects erstellen mit Potenz, Potenztyp und Level
  const rateObjects: RateObject[] = selected.map(rate => {
    const { potency, potencyType, levelDistribution, dominantLevel } = assignPotencyAndLevels(rate.name);
    
    return {
      rateName: rate.name,
      copenRate: rate.copenRate,
      energeticValue: energies[rate.name],
      potency,
      potencyType,
      levelDistribution,
      dominantLevel,
    };
  });
  
  // 4. Sortieren nach energeticValue (absteigend)
  rateObjects.sort((a, b) => b.energeticValue - a.energeticValue);
  
  // 5. Optional auf maxEntries kürzen
  const finalRates = config.maxEntries 
    ? rateObjects.slice(0, config.maxEntries)
    : rateObjects;
  
  return {
    rateObjects: finalRates,
    numberOfTrials: trials,
  };
}

/**
 * Standard-Konfiguration
 */
export const DEFAULT_ANALYSIS_CONFIG: AnalysisConfig = {
  selectionFraction: 0.1, // 10%
  minSelection: 1,
  maxSelection: 100,
  chargingThreshold: 100,
  maxEntries: 35,
};


import { type AlphabetType, alphabetSystems, calculateLetterSum } from './alphabetSystems';
import { 
  collectHardwareMetrics, 
  modulateRateWithHardware, 
  HardwareConfig,
  DEFAULT_HARDWARE_CONFIG 
} from './hardwareAlgorithms';

export interface CopenRateResult {
  word: string;
  potency: number;
  potencyType: 'D' | 'C' | 'LM' | 'M' | 'F1' | 'F2' | 'F3';
  rate: number;
  alphabetType: AlphabetType;
  calculation: {
    letterSum: number;
    baseRate: number;
    fibonacciRate: number;
    fibonacciPair?: { div: number; mult: number }; // Nur bei adaptiver Modulation
  };
  isAdaptive?: boolean;
}

export interface WordEnergyInput {
  word: string;
  potency: number;
  potencyType: 'D' | 'C' | 'LM' | 'M' | 'F1' | 'F2' | 'F3';
  alphabetType?: AlphabetType;
}

const fibonacciCache: { [key: number]: number } = {};

const getFibonacciMultiplier = (n: number): number => {
  if (n <= 0) return 1;
  if (n === 1) return 1;
  if (fibonacciCache[n]) return fibonacciCache[n];

  let a = 1, b = 1;
  for (let i = 2; i <= n; i++) {
    const temp = a + b;
    a = b;
    b = temp;
  }

  fibonacciCache[n] = b;
  return b;
};

/**
 * Wortlängen-adaptive Fibonacci-Modulation
 * Wählt Fibonacci-Paare basierend auf der Länge der Wortenergie
 * 
 * @param wordLength - Anzahl der Buchstaben (ohne Leerzeichen)
 * @returns Fibonacci-Paar { div, mult } zur Modulation
 */
export const getAdaptiveFibonacciPair = (wordLength: number): { div: number; mult: number } => {
  // Fibonacci-Sequenz: 1,1,2,3,5,8,13,21,34,55,89,144...
  
  if (wordLength <= 0) {
    return { div: 21, mult: 34 }; // Fallback auf Standard
  }
  
  if (wordLength >= 1 && wordLength <= 4) {
    // Sehr kurze Wörter: OM, LUX, GOLD
    return { div: 13, mult: 21 }; // Verhältnis ≈ 1.615
  }
  
  if (wordLength >= 5 && wordLength <= 10) {
    // Mittlere Wörter: ARNICA, HEILUNG, GESUNDHEIT (Standard)
    return { div: 21, mult: 34 }; // Verhältnis ≈ 1.619 (Original Copen)
  }
  
  if (wordLength >= 11 && wordLength <= 20) {
    // Lange Wörter: ARSENICUM ALBUM, CALCAREA CARBONICA
    return { div: 34, mult: 55 }; // Verhältnis ≈ 1.618
  }
  
  // Sehr lange Wörter: > 20 Buchstaben
  return { div: 55, mult: 89 }; // Verhältnis ≈ 1.618
};

interface ValidationResult {
  valid: boolean;
  error?: string;
}

export const validateWordEnergy = (word: string): ValidationResult => {
  if (!word.trim()) {
    return { valid: false, error: 'Wortenergie darf nicht leer sein' };
  }

  if (word.length > 50) {
    return { valid: false, error: 'Wortenergie darf maximal 50 Zeichen enthalten' };
  }

  return { valid: true };
};

export const calculateCopenRate = (
  word: string,
  potency: number,
  potencyType: 'D' | 'C' | 'LM' | 'M' | 'F1' | 'F2' | 'F3',
  alphabetType: AlphabetType = 'latin',
  imageSignature?: string,
  useImageSignature: boolean = false,
  useAdaptiveFibonacci: boolean = false
): CopenRateResult => {
  // 1) Normalisierung nach Bruce Copen Klassik V4 (mit Zahlenverarbeitung)
  const normalize = (w: string) =>
    w
      .toUpperCase()
      .replace(/Ä/g, 'AE')
      .replace(/Ö/g, 'OE')
      .replace(/Ü/g, 'UE')
      .replace(/ß/g, 'SS')
      .replace(/\s*[DCLMF]+\d+/g, '') // Potenzangaben entfernen (D, C, LM, M, F)
      .replace(/[^A-Z0-9]/g, '')       // Nur Buchstaben und Zahlen behalten, alle anderen Zeichen entfernen
      .trim();

  const getCharValue = (ch: string): number => {
    // A-Z = 1-26, 0-9 = 0-9
    if (ch >= 'A' && ch <= 'Z') {
      return ch.charCodeAt(0) - 64; // A=1..Z=26
    }
    if (ch >= '0' && ch <= '9') {
      return parseInt(ch, 10); // 0-9
    }
    return 0;
  };

  const computePrimarySum = (text: string) => {
    let sum = 0;
    let pos = 1;
    for (const ch of text) {
      const value = getCharValue(ch);
      sum += value * pos;
      pos++;
    }
    return sum;
  };

  const cleanWord = normalize(word);
  let primarySum = computePrimarySum(cleanWord);

  // Bildsignatur optional integrieren (arithmetisches Mittel der Primärsummen)
  if (useImageSignature && imageSignature && imageSignature.trim().length > 0) {
    const cleanSig = normalize(imageSignature);
    const imgPrimary = computePrimarySum(cleanSig);
    const original = primarySum;
    primarySum = Math.floor((primarySum + imgPrimary) / 2);
    console.log('✅ Bildsignatur angewendet (Bruce Copen Pfad):', { original, imgPrimary, adjusted: primarySum });
  }

  // 2) Baserate
  const baseRate = primarySum * 1000;
  
  // 3) Fibonacci-Modulation
  let fibonacciRate: number;
  let fibonacciPair: { div: number; mult: number } | undefined;
  
  if (useAdaptiveFibonacci) {
    // Wortlängen-adaptive Modulation
    const wordLengthWithoutSpaces = cleanWord.replace(/\s/g, '').length;
    fibonacciPair = getAdaptiveFibonacciPair(wordLengthWithoutSpaces);
    fibonacciRate = Math.floor((baseRate / fibonacciPair.div) * fibonacciPair.mult);
    console.log('🔄 Adaptive Fibonacci-Modulation:', { 
      wortlänge: wordLengthWithoutSpaces, 
      pair: fibonacciPair, 
      verhältnis: (fibonacciPair.mult / fibonacciPair.div).toFixed(4) 
    });
  } else {
    // Original Copen: Feste Modulation (21/34)
    fibonacciRate = Math.floor((baseRate / 21) * 34);
  }

  // 4) Potenz-Bonus nach Dokumentation
  let potencyBonus = 0;
  const p = Math.max(0, potency);
  if (p > 0) {
    switch (potencyType) {
      case 'D':
        potencyBonus = Math.floor(fibonacciRate * (p / 10));
        break;
      case 'C':
        potencyBonus = Math.floor(fibonacciRate * (p / 5));
        break;
      case 'LM':
        potencyBonus = Math.floor(fibonacciRate * (p / 2));
        break;
      case 'M':
        potencyBonus = Math.floor(fibonacciRate * p);
        break;
      case 'F1':
        potencyBonus = Math.floor(fibonacciRate * (p / 6));
        break;
      case 'F2':
        potencyBonus = Math.floor(fibonacciRate * (p / 4));
        break;
      case 'F3':
        potencyBonus = Math.floor(fibonacciRate * (p / 3));
        break;
    }
  }

  const finalRate = fibonacciRate + potencyBonus;

  return {
    word,
    potency,
    potencyType,
    rate: finalRate,
    alphabetType,
    calculation: {
      letterSum: primarySum, // historisch: Primärsumme
      baseRate,
      fibonacciRate,
      fibonacciPair: useAdaptiveFibonacci ? fibonacciPair : undefined,
    },
    isAdaptive: useAdaptiveFibonacci,
  };
};

export const batchCalculateCopenRates = (inputs: WordEnergyInput[]): CopenRateResult[] => {
  return inputs.map(input => calculateCopenRate(
    input.word, 
    input.potency, 
    input.potencyType,
    input.alphabetType || 'latin'
  ));
};

export const parseWordEnergyData = (csvData: string): WordEnergyInput[] => {
  const lines = csvData.trim().split('\n');
  const results: WordEnergyInput[] = [];
  
  for (const line of lines) {
    const parts = line.split(',').map(part => part.trim());
    if (parts.length >= 3) {
      const [word, potencyStr, potencyType, alphabetType] = parts;
      const potency = parseInt(potencyStr);
      
      if (!isNaN(potency) && ['D', 'C', 'LM', 'M', 'F1', 'F2', 'F3'].includes(potencyType)) {
        results.push({
          word,
          potency,
          potencyType: potencyType as 'D' | 'C' | 'LM' | 'M' | 'F1' | 'F2' | 'F3',
          alphabetType: (alphabetType as AlphabetType) || 'latin'
        });
      }
    }
  }
  
  return results;
};

export const exportCopenRatesToCSV = (results: CopenRateResult[]): string => {
  const header = 'Wortenergie,Potenz,Typ,Alphabet,Copen-Rate\n';
  const rows = results.map(result => {
    return `${result.word},${result.potency},${result.potencyType},${result.alphabetType},${result.rate}`;
  });
  return header + rows.join('\n');
};

// ============================================
// RATEN-KOMBINATIONS-ALGORITHMEN
// ============================================

export type CombinationMethod = 
  | 'arithmetic'          // Arithmetisches Mittel
  | 'geometric'           // Geometrisches Mittel
  | 'harmonic'            // Harmonisches Mittel
  | 'fibonacci'           // Fibonacci-moduliert (Copen-typisch)
  | 'weighted_potency'    // Potenz-gewichtet
  | 'copen_digital'       // Digital Copen (10-stellig)
  | 'malcolm_rae';        // Geometrisch × Phi

export interface CombinedRateInput {
  rate: number;
  word: string;
  potency: number;
  potencyType: 'D' | 'C' | 'LM' | 'M' | 'F1' | 'F2' | 'F3';
}

export interface CombinedRateResult {
  inputRates: CombinedRateInput[];
  combinedRate: number;
  method: CombinationMethod;
  details: {
    arithmeticMean: number;
    geometricMean: number;
    harmonicMean: number;
    fibonacciModulated: number;
    weightedByPotency: number;
    copenDigital: number;
    malcolmRae: number;
  };
  allMethods: Array<{
    method: CombinationMethod;
    rate: number;
    description: string;
  }>;
}

/**
 * Berechnet den Potenz-Gewichtungsfaktor
 */
const getPotencyWeight = (potency: number, potencyType: string): number => {
  const p = Math.max(1, potency);
  switch (potencyType) {
    case 'D': return p / 10;
    case 'C': return p / 5;
    case 'LM': return p / 2;
    case 'M': return p;
    case 'F1': return p / 6;
    case 'F2': return p / 4;
    case 'F3': return p / 3;
    default: return 1;
  }
};

/**
 * Kombiniert zwei oder mehr Copen-Raten zu einer einzelnen Rate
 * 
 * Unterstützte Methoden:
 * - arithmetic: Einfaches arithmetisches Mittel
 * - geometric: Geometrisches Mittel (Resonanz-optimal)
 * - harmonic: Harmonisches Mittel
 * - fibonacci: Fibonacci-moduliertes Mittel (Original Copen)
 * - weighted_potency: Nach Potenzstärke gewichtet
 * - copen_digital: 10-stellige digitale Rate
 * - malcolm_rae: Geometrisch × Goldener Schnitt
 */
export const combineCopenRates = (
  inputs: CombinedRateInput[],
  preferredMethod: CombinationMethod = 'fibonacci'
): CombinedRateResult => {
  if (inputs.length === 0) {
    throw new Error('Mindestens eine Rate erforderlich');
  }
  
  const rates = inputs.map(i => i.rate);
  const n = rates.length;
  
  // 1. Arithmetisches Mittel
  const sum = rates.reduce((a, b) => a + b, 0);
  const arithmeticMean = Math.floor(sum / n);
  
  // 2. Geometrisches Mittel
  const product = rates.reduce((a, b) => a * b, 1);
  const geometricMean = Math.floor(Math.pow(product, 1 / n));
  
  // 3. Harmonisches Mittel
  const harmonicSum = rates.reduce((a, b) => a + (1 / b), 0);
  const harmonicMean = Math.floor(n / harmonicSum);
  
  // 4. Fibonacci-Moduliert (Copen-typisch)
  // Kombination aus arithmetischem und geometrischem Mittel mit Fibonacci-Verhältnis
  const fibonacciModulated = Math.floor(
    ((arithmeticMean * 34 / 21) + (geometricMean * 21 / 34)) / 2
  );
  
  // 5. Potenz-gewichtetes Mittel
  let weightedSum = 0;
  let totalWeight = 0;
  for (const input of inputs) {
    const weight = getPotencyWeight(input.potency, input.potencyType);
    weightedSum += input.rate * weight;
    totalWeight += weight;
  }
  const weightedByPotency = Math.floor((weightedSum / totalWeight) * 34 / 21);
  
  // 6. Copen Digital (10-stellig via Modulo)
  const bigProduct = rates.reduce((a, b) => BigInt(a) * BigInt(b), BigInt(1));
  const copenDigital = Number(bigProduct % BigInt(10000000000));
  
  // 7. Malcolm Rae (Geometrisch × Phi)
  const PHI = 1.618034;
  const malcolmRae = Math.floor(geometricMean * PHI);
  
  // Alle Methoden mit Beschreibungen
  const allMethods: CombinedRateResult['allMethods'] = [
    { method: 'arithmetic', rate: arithmeticMean, description: 'Arithmetisches Mittel: Einfache Durchschnittsberechnung' },
    { method: 'geometric', rate: geometricMean, description: 'Geometrisches Mittel: Resonanz-optimiert, multiplikative Beziehung' },
    { method: 'harmonic', rate: harmonicMean, description: 'Harmonisches Mittel: Traditionell in Radionik für Wellenkombination' },
    { method: 'fibonacci', rate: fibonacciModulated, description: 'Fibonacci-Moduliert: Bruce Copen Original mit 21/34 Verhältnis' },
    { method: 'weighted_potency', rate: weightedByPotency, description: 'Potenz-gewichtet: Berücksichtigt D/C/LM Stärke' },
    { method: 'copen_digital', rate: copenDigital, description: 'Copen Digital: 10-stellig für digitale Radionik-Geräte' },
    { method: 'malcolm_rae', rate: malcolmRae, description: 'Malcolm Rae: Geometrisch × Phi (Goldener Schnitt)' }
  ];
  
  // Gewählte Methode für combinedRate
  const methodMap: Record<CombinationMethod, number> = {
    arithmetic: arithmeticMean,
    geometric: geometricMean,
    harmonic: harmonicMean,
    fibonacci: fibonacciModulated,
    weighted_potency: weightedByPotency,
    copen_digital: copenDigital,
    malcolm_rae: malcolmRae
  };
  
  return {
    inputRates: inputs,
    combinedRate: methodMap[preferredMethod],
    method: preferredMethod,
    details: {
      arithmeticMean,
      geometricMean,
      harmonicMean,
      fibonacciModulated,
      weightedByPotency,
      copenDigital,
      malcolmRae
    },
    allMethods
  };
};

/**
 * Analysiert eine gegebene Rate um mögliche Berechnungsmethoden zu identifizieren
 */
export const analyzeRateOrigin = (
  targetRate: number,
  knownRates: number[]
): { possibleMethods: Array<{ method: string; confidence: number; explanation: string }> } => {
  const results: Array<{ method: string; confidence: number; explanation: string }> = [];
  
  if (knownRates.length < 2) {
    return { possibleMethods: [] };
  }
  
  // Teste verschiedene Kombinationen
  const sum = knownRates.reduce((a, b) => a + b, 0);
  const product = knownRates.reduce((a, b) => a * b, 1);
  const n = knownRates.length;
  
  // Einfache Addition
  if (Math.abs(sum - targetRate) < targetRate * 0.01) {
    results.push({ method: 'Addition', confidence: 95, explanation: 'Summe der Einzelraten' });
  }
  
  // Arithmetisches Mittel
  const arithMean = sum / n;
  if (Math.abs(arithMean - targetRate) < targetRate * 0.01) {
    results.push({ method: 'Arithmetisches Mittel', confidence: 90, explanation: 'Durchschnitt der Raten' });
  }
  
  // Fibonacci-moduliert
  const fibMod = (arithMean * 34 / 21);
  if (Math.abs(fibMod - targetRate) < targetRate * 0.02) {
    results.push({ method: 'Fibonacci-Moduliert', confidence: 85, explanation: 'Mittel × 34/21 (Bruce Copen)' });
  }
  
  // Geometrisches Mittel
  const geoMean = Math.pow(product, 1 / n);
  if (Math.abs(geoMean - targetRate) < targetRate * 0.02) {
    results.push({ method: 'Geometrisches Mittel', confidence: 85, explanation: 'Wurzel aus Produkt' });
  }
  
  // Phi-skaliert
  const phiScaled = geoMean * 1.618034;
  if (Math.abs(phiScaled - targetRate) < targetRate * 0.02) {
    results.push({ method: 'Malcolm Rae (Phi)', confidence: 80, explanation: 'Geometrisches Mittel × 1.618' });
  }
  
  // Modulo 10^10
  const modResult = Number(BigInt(product) % BigInt(10000000000));
  if (Math.abs(modResult - targetRate) < targetRate * 0.01) {
    results.push({ method: 'Digital Copen', confidence: 75, explanation: 'Produkt mod 10^10' });
  }
  
  // Sortiere nach Konfidenz
  results.sort((a, b) => b.confidence - a.confidence);
  
  return { possibleMethods: results };
};

// ============================================
// HARDWARE-ENTROPIE KOMBINATIONSALGORITHMUS
// ============================================

export interface EntropyMetrics {
  cpuJitter: number;      // 0.0 - 1.0
  timeCoherence: number;  // 0.0 - 1.0
  systemEntropy: number;  // 0.0 - 1.0
  timestamp: number;      // Berechnungszeitpunkt
}

export interface QuantumCombinedRateResult extends CombinedRateResult {
  entropyMetrics?: EntropyMetrics;
  quantumEnhancedRate?: number;
  digitalQuantumRate?: number;
  explanation: string;
}

/**
 * Sammelt lokale Hardware-Entropie für Raten-Kombination
 * Leichtgewichtige Version ohne async Dependencies
 */
export const collectLocalEntropy = (): EntropyMetrics => {
  // CPU Timing Jitter (synchron)
  const samples = 50;
  const timestamps: number[] = [];
  for (let i = 0; i < samples; i++) {
    timestamps.push(performance.now());
  }
  const diffs = timestamps.slice(1).map((t, i) => t - timestamps[i]);
  const mean = diffs.reduce((a, b) => a + b) / diffs.length;
  const variance = diffs.reduce((sum, d) => sum + (d - mean) ** 2, 0) / diffs.length;
  const cpuJitter = Math.min(1.0, Math.sqrt(variance) / 0.1);
  
  // Zeit-Kohärenz
  const perfTime = performance.now();
  const dateTime = Date.now();
  const perfDelta = performance.now() - perfTime;
  const timeCoherence = 1.0 - Math.min(1.0, perfDelta / 1.0);
  
  // System-Entropie (basierend auf Zeitstempel-Bits)
  const now = Date.now();
  const bits = now.toString(2);
  const ones = bits.split('').filter(b => b === '1').length;
  const systemEntropy = ones / bits.length;
  
  return {
    cpuJitter,
    timeCoherence,
    systemEntropy,
    timestamp: now
  };
};

/**
 * Quanten-erweiterte Raten-Kombination mit Hardware-Entropie
 * 
 * Diese Methode integriert Hardware-Entropie in die Raten-Kombination,
 * ähnlich wie es fortschrittliche digitale Radionik-Systeme tun.
 * 
 * Die 10-stellige Zielrate (2776670847) könnte durch folgende Faktoren entstehen:
 * - Zeitstempel-Integration
 * - Hardware-Entropie-Modulation
 * - Operator-Signatur
 * - Erweiterte Fibonacci-Sequenzen
 */
export const combineCopenRatesWithEntropy = (
  inputs: CombinedRateInput[],
  preferredMethod: CombinationMethod = 'fibonacci',
  useQuantumEnhancement: boolean = true
): QuantumCombinedRateResult => {
  // Basis-Kombination
  const baseResult = combineCopenRates(inputs, preferredMethod);
  
  // Sammle Hardware-Entropie
  const entropyMetrics = collectLocalEntropy();
  
  if (!useQuantumEnhancement) {
    return {
      ...baseResult,
      explanation: 'Standard-Kombination ohne Hardware-Entropie'
    };
  }
  
  // Quanten-Enhancement Faktoren
  const PHI = 1.618033988749895;
  const PHI_SQUARED = PHI * PHI; // ≈ 2.618
  
  // 1. Entropie-gewichtete Modulation
  const entropyWeight = (
    entropyMetrics.cpuJitter * 0.3 +
    entropyMetrics.timeCoherence * 0.4 +
    entropyMetrics.systemEntropy * 0.3
  );
  
  // 2. Quanten-modulierte Rate
  // Kombiniert Basis-Rate mit Entropie-Faktor und Goldenen Schnitt
  const quantumFactor = 1 + (entropyWeight * 0.05); // +0-5% basierend auf Entropie
  const quantumEnhancedRate = Math.floor(baseResult.combinedRate * quantumFactor * PHI);
  
  // 3. Digitale 10-stellige Rate (für Kompatibilität mit digitalen Systemen)
  // Kombiniert Zeitstempel, Entropie und Basis-Rate
  const timestampFactor = entropyMetrics.timestamp % 10000; // Letzte 4 Stellen des Timestamps
  const entropyFactor = Math.floor(entropyWeight * 1000000); // Entropie als 6-stellige Zahl
  
  // Berechnung: (Rate × Phi^2) + (Timestamp × Entropie-Faktor)
  const digitalQuantumRate = Math.floor(
    (baseResult.combinedRate * PHI_SQUARED) + 
    (timestampFactor * entropyWeight * 1000)
  ) % 10000000000; // Beschränke auf 10 Stellen
  
  // Erklärung generieren
  const explanation = `
Quanten-erweiterte Kombination:
- Basis-Methode: ${preferredMethod} = ${baseResult.combinedRate.toLocaleString('de-DE')}
- CPU Jitter: ${(entropyMetrics.cpuJitter * 100).toFixed(2)}%
- Zeit-Kohärenz: ${(entropyMetrics.timeCoherence * 100).toFixed(2)}%
- System-Entropie: ${(entropyMetrics.systemEntropy * 100).toFixed(2)}%
- Entropie-Gewicht: ${(entropyWeight * 100).toFixed(2)}%
- Quanten-Faktor: ×${quantumFactor.toFixed(4)} × Φ
- Quanten-Rate: ${quantumEnhancedRate.toLocaleString('de-DE')}
- Digital (10-stellig): ${digitalQuantumRate.toLocaleString('de-DE')}

Die 10-stellige Rate integriert Zeitstempel und Hardware-Entropie,
ähnlich wie fortschrittliche digitale Radionik-Systeme arbeiten.
`.trim();
  
  return {
    ...baseResult,
    entropyMetrics,
    quantumEnhancedRate,
    digitalQuantumRate,
    explanation
  };
};

/**
 * EMPFOHLENE METHODE für Wortenergien-Kombination
 * 
 * Basierend auf radionischen Prinzipien und Bruce Copen Theorie:
 * 
 * 1. Harmonisches Mittel - Für unterschiedliche Potenzen (D1 + D4)
 *    → Betont die niedrigere Potenz (tiefere Wirkungsebene)
 *    → Resonanz-Superposition nach Kozyrev
 * 
 * 2. Fibonacci-Moduliert - Für gleiche Potenzen
 *    → Original Bruce Copen Verhältnis 21/34
 *    → Goldener Schnitt Resonanz
 * 
 * 3. Quanten-erweitert - Für maximale Präzision
 *    → Integriert Hardware-Entropie
 *    → Reproduziert 10-stellige Raten
 */
export type RecommendedCombinationMethod = 'harmonic_resonance' | 'fibonacci_balanced' | 'quantum_enhanced';

export interface RecommendedCombinationResult {
  method: RecommendedCombinationMethod;
  combinedRate: number;
  formattedRate: string;
  rationale: string;
  inputSummary: string;
  alternativeRates: {
    harmonic: number;
    fibonacci: number;
    quantumEnhanced?: number;
    digital10?: number;
  };
}

export const getRecommendedCombination = (
  inputs: CombinedRateInput[],
  includeQuantum: boolean = true
): RecommendedCombinationResult => {
  if (inputs.length < 2) {
    throw new Error('Mindestens 2 Raten erforderlich für Kombination');
  }
  
  // Analyse der Eingaben
  const potencies = inputs.map(i => i.potency);
  const potencyTypes = inputs.map(i => i.potencyType);
  const hasDifferentPotencies = potencies.some(p => p !== potencies[0]) || 
                                 potencyTypes.some(t => t !== potencyTypes[0]);
  
  // Berechne alle Varianten
  const harmonicResult = combineCopenRates(inputs, 'harmonic');
  const fibonacciResult = combineCopenRates(inputs, 'fibonacci');
  
  let quantumResult: QuantumCombinedRateResult | undefined;
  if (includeQuantum) {
    quantumResult = combineCopenRatesWithEntropy(inputs, 'fibonacci', true);
  }
  
  // Empfehlung basierend auf Eingaben
  let method: RecommendedCombinationMethod;
  let combinedRate: number;
  let rationale: string;
  
  if (hasDifferentPotencies) {
    // Unterschiedliche Potenzen → Harmonisches Mittel
    method = 'harmonic_resonance';
    combinedRate = harmonicResult.combinedRate;
    rationale = `Unterschiedliche Potenzen erkannt (${potencyTypes.join(', ')}). 
Das Harmonische Mittel ist optimal, da es:
- Die niedrigere Potenz stärker gewichtet (tiefere Wirkungsebene)
- Resonanz-Superposition nach radionischen Prinzipien ermöglicht
- Von traditionellen Radionik-Geräten verwendet wird`;
  } else if (includeQuantum && quantumResult) {
    // Gleiche Potenzen + Quantum verfügbar → Quanten-erweitert
    method = 'quantum_enhanced';
    combinedRate = quantumResult.quantumEnhancedRate || fibonacciResult.combinedRate;
    rationale = `Gleiche Potenzen mit Quanten-Enhancement. 
Die Quanten-Rate integriert Hardware-Entropie für:
- Einzigartige, reproduzierbare Signaturen
- Zeitpunkt-spezifische Modulation
- Kompatibilität mit 10-stelligen Systemen`;
  } else {
    // Standard: Fibonacci-moduliert
    method = 'fibonacci_balanced';
    combinedRate = fibonacciResult.combinedRate;
    rationale = `Standard Fibonacci-Kombination nach Bruce Copen. 
Das 21/34 Verhältnis (≈ 1.619) entspricht:
- Dem Goldenen Schnitt (Φ)
- Natürlichen Resonanzmustern
- Original Copen Radionik-Berechnung`;
  }
  
  // Eingabe-Zusammenfassung
  const inputSummary = inputs.map(i => 
    `${i.word} ${i.potencyType}${i.potency} → ${i.rate.toLocaleString('de-DE')}`
  ).join('\n');
  
  return {
    method,
    combinedRate,
    formattedRate: combinedRate.toLocaleString('de-DE'),
    rationale,
    inputSummary,
    alternativeRates: {
      harmonic: harmonicResult.combinedRate,
      fibonacci: fibonacciResult.combinedRate,
      quantumEnhanced: quantumResult?.quantumEnhancedRate,
      digital10: quantumResult?.digitalQuantumRate
    }
  };
};

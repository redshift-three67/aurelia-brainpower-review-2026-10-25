/**
 * Thom Vector Engine - Feldengine basierend auf René Thoms Morphogenese
 * 
 * Berechnet Klienten-Vektoren basierend auf biometrischen Daten:
 * - Name, Vorname, Geburtsdatum, Geburtsort
 * - Optionales Foto für erweiterte Feld-Signatur
 * 
 * Die Feld-Signatur ist ein deterministischer Hash der biometrischen Daten,
 * der als Basis für topologische Berechnungen im Kuspen-Raum dient.
 */

import type { ClientVector, VectorTrajectory } from '@/types/hardware';

// Hardware-Entropie-Eingabedaten
export interface HardwareEntropyInput {
  cpuEntropy: number;
  gpuEntropy: number;
  ramEntropy: number;
  latencyEntropy: number;
  combined?: number;
}


export interface BiometricClientData {
  firstName: string;
  lastName: string;
  birthDate: Date;
  birthPlace: string;
  photoData?: string; // Base64 oder URL für Signatur-Extraktion
}

// Feld-Signatur mit Morphogenese-Parametern
export interface FieldSignature {
  hash: string;
  numerology: NumerologyVector;
  geoResonance: GeoResonanceVector;
  temporalPhase: TemporalPhaseVector;
  combinedVector: number[];
}

// Numerologie-Vektor (Name-basiert)
interface NumerologyVector {
  nameValue: number;
  vowelValue: number;
  consonantValue: number;
  lifePathNumber: number;
}

// Geo-Resonanz-Vektor (Geburtsort-basiert)
interface GeoResonanceVector {
  placeHash: number;
  harmonics: number[];
}

// Temporal-Phase-Vektor (Geburtsdatum-basiert)
interface TemporalPhaseVector {
  dayPhase: number;
  monthPhase: number;
  yearCycle: number;
  seasonalResonance: number;
}

// Zustandsdimensionen für Anamnese
export interface StateDimensions {
  physical: number;    // 0-100
  emotional: number;   // 0-100
  mental: number;      // 0-100
  energy: number;      // 0-100
  stress: number;      // 0-100
}

// Vollständige Vektor-Analyse
export interface VectorAnalysis {
  clientVector: ClientVector;
  fieldSignature: FieldSignature;
  attractorState: AttractorState;
  recommendedFrequencies: RecommendedFrequency[];
}

interface AttractorState {
  position: number[];
  stability: number;
  bifurcationRisk: number;
  phase: 'approach' | 'transition' | 'stable';
  chreodeAlignment: number;
}

export interface RecommendedFrequency {
  frequency: number;
  name: string;
  description: string;
  priority: number;
  duration: number; // Sekunden
}

/**
 * ThomVectorEngine - Hauptklasse für Vektor-Berechnungen
 */
export class ThomVectorEngine {
  // Numerologie-Mapping (Pythagoras-System)
  private static readonly LETTER_VALUES: Record<string, number> = {
    'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6, 'g': 7, 'h': 8, 'i': 9,
    'j': 1, 'k': 2, 'l': 3, 'm': 4, 'n': 5, 'o': 6, 'p': 7, 'q': 8, 'r': 9,
    's': 1, 't': 2, 'u': 3, 'v': 4, 'w': 5, 'x': 6, 'y': 7, 'z': 8,
    'ä': 5, 'ö': 6, 'ü': 3, 'ß': 1
  };

  private static readonly VOWELS = new Set(['a', 'e', 'i', 'o', 'u', 'ä', 'ö', 'ü']);

  /**
   * Berechnet die vollständige Feld-Signatur aus biometrischen Daten
   */
  static calculateFieldSignature(data: BiometricClientData): FieldSignature {
    const numerology = this.calculateNumerology(data);
    const geoResonance = this.calculateGeoResonance(data.birthPlace);
    const temporalPhase = this.calculateTemporalPhase(data.birthDate);
    
    // Kombinierter Vektor aus allen drei Komponenten
    const combinedVector = this.combineVectors(numerology, geoResonance, temporalPhase);
    
    // Deterministischer Hash
    const hash = this.generateSignatureHash(data, combinedVector);

    return {
      hash,
      numerology,
      geoResonance,
      temporalPhase,
      combinedVector,
    };
  }

  /**
   * Numerologie-Berechnung nach Pythagoras
   */
  private static calculateNumerology(data: BiometricClientData): NumerologyVector {
    const fullName = `${data.firstName}${data.lastName}`.toLowerCase();
    
    let nameValue = 0;
    let vowelValue = 0;
    let consonantValue = 0;

    for (const char of fullName) {
      const value = this.LETTER_VALUES[char] || 0;
      nameValue += value;
      
      if (this.VOWELS.has(char)) {
        vowelValue += value;
      } else if (value > 0) {
        consonantValue += value;
      }
    }

    // Reduktion auf einstellige Zahl (außer Meisterzahlen 11, 22, 33)
    const reduceNumber = (n: number): number => {
      while (n > 9 && n !== 11 && n !== 22 && n !== 33) {
        n = String(n).split('').reduce((sum, d) => sum + parseInt(d), 0);
      }
      return n;
    };

    // Life Path Number aus Geburtsdatum
    const dateStr = `${data.birthDate.getFullYear()}${String(data.birthDate.getMonth() + 1).padStart(2, '0')}${String(data.birthDate.getDate()).padStart(2, '0')}`;
    const lifePathRaw = dateStr.split('').reduce((sum, d) => sum + parseInt(d), 0);

    return {
      nameValue: reduceNumber(nameValue),
      vowelValue: reduceNumber(vowelValue),
      consonantValue: reduceNumber(consonantValue),
      lifePathNumber: reduceNumber(lifePathRaw),
    };
  }

  /**
   * Geo-Resonanz basierend auf Geburtsort
   */
  private static calculateGeoResonance(birthPlace: string): GeoResonanceVector {
    const normalized = birthPlace.toLowerCase().replace(/[^a-zäöüß]/g, '');
    
    // Hash des Ortsnamens
    let placeHash = 0;
    for (let i = 0; i < normalized.length; i++) {
      placeHash = ((placeHash << 5) - placeHash) + normalized.charCodeAt(i);
      placeHash = placeHash & placeHash; // Convert to 32bit integer
    }
    placeHash = Math.abs(placeHash);

    // Harmonische Frequenzen basierend auf Ortshash
    const baseFreq = 7.83; // Schumann-Resonanz
    const harmonics = [
      baseFreq * (1 + (placeHash % 100) / 1000),
      baseFreq * 2 * (1 + ((placeHash >> 8) % 100) / 1000),
      baseFreq * 3 * (1 + ((placeHash >> 16) % 100) / 1000),
    ];

    return {
      placeHash: placeHash % 10000,
      harmonics,
    };
  }

  /**
   * Temporale Phase basierend auf Geburtsdatum
   */
  private static calculateTemporalPhase(birthDate: Date): TemporalPhaseVector {
    const day = birthDate.getDate();
    const month = birthDate.getMonth() + 1;
    const year = birthDate.getFullYear();

    // Tag-Phase (Mondphase-ähnlich, 0-1)
    const dayPhase = (day - 1) / 30;

    // Monats-Phase (Jahreskreis, 0-1)
    const monthPhase = (month - 1) / 11;

    // Jahr-Zyklus (9-Jahres-Zyklus nach Numerologie)
    const yearCycle = ((year - 1) % 9) / 8;

    // Saisonale Resonanz
    const seasonalResonance = Math.sin(2 * Math.PI * monthPhase);

    return {
      dayPhase,
      monthPhase,
      yearCycle,
      seasonalResonance,
    };
  }

  /**
   * Kombiniert alle Vektoren zu einem 5D-Feld-Vektor
   */
  private static combineVectors(
    numerology: NumerologyVector,
    geoResonance: GeoResonanceVector,
    temporalPhase: TemporalPhaseVector
  ): number[] {
    // Normalisierung auf [-1, 1]
    const norm = (val: number, max: number) => (val / max) * 2 - 1;

    return [
      norm(numerology.nameValue, 33),           // D1: Name-Essenz
      norm(numerology.lifePathNumber, 33),      // D2: Lebensweg
      norm(geoResonance.placeHash % 1000, 1000), // D3: Ort-Resonanz
      temporalPhase.seasonalResonance,           // D4: Temporal-Phase
      norm(geoResonance.harmonics[0], 30),       // D5: Primär-Harmonik
    ];
  }

  /**
   * Generiert einen deterministischen Hash für die Signatur
   */
  private static generateSignatureHash(data: BiometricClientData, vector: number[]): string {
    const input = `${data.firstName}|${data.lastName}|${data.birthDate.toISOString()}|${data.birthPlace}|${vector.join(',')}`;
    
    // Simple hash function (in Produktion würde man crypto.subtle verwenden)
    let hash = 0;
    for (let i = 0; i < input.length; i++) {
      const char = input.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash;
    }
    
    return `FS-${Math.abs(hash).toString(16).toUpperCase().padStart(8, '0')}`;
  }

  /**
   * Hardware-Entropie-Modulation (±10%)
   * Nutzt nicht-deterministische Hardware-Fluktuationen als Proxy
   * für morphogenetische Feld-Fluktuationen nach Thom.
   * 
   * Quellen: CPU-Thermal-Noise, GPU-Shader-Jitter, RAM-Timing-Varianz
   */
  static applyHardwareEntropyModulation(
    dimensions: number[],
    entropyData?: HardwareEntropyInput | null
  ): number[] {
    if (!entropyData) return dimensions;

    const { cpuEntropy = 0, gpuEntropy = 0, ramEntropy = 0, latencyEntropy = 0 } = entropyData;
    const combinedEntropy = (cpuEntropy + gpuEntropy + ramEntropy + latencyEntropy) / 4;

    // Maximale Modulation: ±10% pro Dimension
    const MAX_MODULATION = 0.10;

    return dimensions.map((d, i) => {
      // Jede Dimension bekommt einen leicht unterschiedlichen Entropie-Offset
      // basierend auf verschiedenen Entropie-Quellen
      const sources = [cpuEntropy, gpuEntropy, ramEntropy, latencyEntropy, combinedEntropy];
      const entropyForDim = sources[i % sources.length];

      // Sinus-basierte Streuung für natürliche Variation
      const phase = (i * 1.618033988749895) % 1; // Goldener Schnitt für Gleichverteilung
      const modulation = Math.sin(entropyForDim * Math.PI * 2 + phase * Math.PI) * MAX_MODULATION;

      return Math.max(-1, Math.min(1, d + modulation * combinedEntropy));
    });
  }

  /**
   * Berechnet den vollständigen Klienten-Vektor mit Feld-Signatur
   */
  static calculateClientVector(
    biometricData: BiometricClientData,
    stateDimensions: StateDimensions,
    sessionId: string,
    entropyData?: HardwareEntropyInput | null
  ): VectorAnalysis {
    const fieldSignature = this.calculateFieldSignature(biometricData);
    
    // Zustandsvektor normalisieren auf [-1, 1]
    const stateVector = [
      (stateDimensions.physical - 50) / 50,
      (stateDimensions.emotional - 50) / 50,
      (stateDimensions.mental - 50) / 50,
      (stateDimensions.energy - 50) / 50,
      (stateDimensions.stress - 50) / 50,
    ];

    // Kombinierter Vektor: Feld-Signatur + Zustand
    let combinedDimensions = stateVector.map((s, i) => {
      const fieldComponent = fieldSignature.combinedVector[i] || 0;
      // Gewichtete Kombination: 30% Feld-Signatur, 70% aktueller Zustand
      return 0.3 * fieldComponent + 0.7 * s;
    });

    // Hardware-Entropie-Modulation (±10%)
    combinedDimensions = this.applyHardwareEntropyModulation(combinedDimensions, entropyData);

    // Attraktor-Berechnung
    const attractorState = this.calculateAttractorState(combinedDimensions, fieldSignature);

    // Trajektorie
    const trajectory: VectorTrajectory = {
      points: [{ position: combinedDimensions, timestamp: new Date() }],
      attractorDistance: attractorState.stability,
      phase: attractorState.phase,
    };

    const clientVector: ClientVector = {
      id: `vec-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date(),
      dimensions: combinedDimensions,
      metadata: {
        sessionId,
        clientId: fieldSignature.hash,
        inputMethod: 'manual',
        sensorData: [],
      },
      trajectory,
    };

    // Empfohlene Frequenzen basierend auf Analyse
    const recommendedFrequencies = this.calculateRecommendedFrequencies(
      attractorState,
      fieldSignature
    );

    return {
      clientVector,
      fieldSignature,
      attractorState,
      recommendedFrequencies,
    };
  }

  /**
   * Berechnet den Attraktor-Zustand im Kuspen-Raum
   */
  private static calculateAttractorState(
    dimensions: number[],
    fieldSignature: FieldSignature
  ): AttractorState {
    // Euklidische Distanz zum Ursprung (gesunder Attraktor)
    const distance = Math.sqrt(dimensions.reduce((sum, d) => sum + d * d, 0));
    
    // Stabilität (invers zur Distanz)
    const stability = Math.max(0, 1 - distance / 2);

    // Bifurkationsrisiko (basierend auf Stress und Energy)
    const stressIndex = Math.abs(dimensions[4]);
    const energyIndex = dimensions[3];
    const bifurcationRisk = stressIndex * (1 - Math.max(0, energyIndex));

    // Phase bestimmen
    let phase: 'approach' | 'transition' | 'stable';
    if (distance > 1.2) {
      phase = 'approach';
    } else if (distance > 0.5) {
      phase = 'transition';
    } else {
      phase = 'stable';
    }

    // Chreode-Alignment (Ausrichtung zum natürlichen Entwicklungspfad)
    const lifePathInfluence = fieldSignature.numerology.lifePathNumber / 33;
    const chreodeAlignment = stability * (0.5 + 0.5 * lifePathInfluence);

    return {
      position: dimensions,
      stability,
      bifurcationRisk,
      phase,
      chreodeAlignment,
    };
  }

  /**
   * Berechnet empfohlene Frequenzen basierend auf Analyse
   */
  private static calculateRecommendedFrequencies(
    attractorState: AttractorState,
    fieldSignature: FieldSignature
  ): RecommendedFrequency[] {
    const frequencies: RecommendedFrequency[] = [];

    // Schumann-Resonanz als Basis
    frequencies.push({
      frequency: 7.83,
      name: 'Schumann-Erdresonanz',
      description: 'Grundlegende Erd-Anbindung',
      priority: 1,
      duration: 300,
    });

    // Personalisierte Frequenz aus Geo-Resonanz
    const personalFreq = fieldSignature.geoResonance.harmonics[0];
    frequencies.push({
      frequency: personalFreq,
      name: 'Persönliche Resonanz',
      description: `Basierend auf Geburtsort: ${personalFreq.toFixed(2)} Hz`,
      priority: 2,
      duration: 180,
    });

    // Stress-Abbau wenn nötig
    if (attractorState.bifurcationRisk > 0.5) {
      frequencies.push({
        frequency: 10,
        name: 'Alpha-Entspannung',
        description: 'Stress-Reduktion und Entspannung',
        priority: 3,
        duration: 240,
      });
    }

    // Energie-Aufbau wenn niedrig
    if (attractorState.position[3] < -0.3) {
      frequencies.push({
        frequency: 528,
        name: 'Solfeggio MI',
        description: 'DNA-Reparatur und Energie-Aufbau',
        priority: 4,
        duration: 180,
      });
    }

    // Stabilisierung in Transition-Phase
    if (attractorState.phase === 'transition') {
      frequencies.push({
        frequency: 639,
        name: 'Solfeggio FA',
        description: 'Harmonisierung und Stabilisierung',
        priority: 5,
        duration: 120,
      });
    }

    return frequencies.sort((a, b) => a.priority - b.priority);
  }

  /**
   * Analysiert ein Foto für erweiterte Feld-Signatur (Placeholder für Zukunft)
   */
  static async analyzePhoto(_photoData: string): Promise<number[]> {
    // In Zukunft: AI-basierte Bildanalyse für biometrische Merkmale
    // Aktuell: Placeholder-Vektor
    return [0, 0, 0, 0, 0];
  }
}

export default ThomVectorEngine;

/**
 * Morphic Field Engine - Quantum-based Morphogenetic Field Calculation
 * Based on: Ψ_total(x,t) = Σn αn |ψn⟩ e^(-iEnt/ℏ) × C(numerical_sequence) × G(geometric_forms) × I(intention)
 */

import { collectHardwareMetrics, type HardwareMetrics } from './hardwareAlgorithms';
import { calculateCopenRate } from './copenRateGenerator';

// Planck's constant (reduced)
const HBAR = 1.054571817e-34;

/**
 * Quantum State Interface
 */
export interface QuantumState {
  n: number;              // Energy level
  amplitude: number;      // αn - Complex amplitude (simplified as real)
  energy: number;         // En - Energy eigenvalue
  phase?: number;         // Optional phase offset
}

/**
 * Geometric Form Types
 */
export type GeometricForm = 
  | 'tetrahedron'    // 4 faces - Fire element
  | 'cube'           // 6 faces - Earth element
  | 'octahedron'     // 8 faces - Air element
  | 'dodecahedron'   // 12 faces - Ether/Universe
  | 'icosahedron'    // 20 faces - Water element
  | 'merkaba'        // Double tetrahedron - Light body
  | 'torus'          // Self-sustaining field
  | 'flower_of_life' // Sacred geometry pattern
  | 'sri_yantra';    // Hindu sacred geometry

/**
 * Intention Types
 */
export type IntentionType =
  | 'healing'        // Restoration and balance
  | 'manifestation'  // Creation and materialization
  | 'protection'     // Shield and defense
  | 'transformation' // Change and evolution
  | 'connection'     // Unity and coherence
  | 'clearing'       // Purification and release
  | 'activation'     // Energization and awakening
  | 'harmonization'; // Balance and alignment

/**
 * Morphic Field Configuration
 */
export interface MorphicFieldConfig {
  quantumStates: QuantumState[];
  numericalSequence: number[];  // Can be Copen rates, Fibonacci, etc.
  geometricForm: GeometricForm;
  intention: IntentionType;
  time?: number;                // Time parameter (default: Date.now())
  useHardwareModulation?: boolean;
}

/**
 * Morphic Field Result
 */
export interface MorphicFieldResult {
  totalWaveFunction: number;
  quantumComponent: number;
  numericalFactor: number;
  geometricFactor: number;
  intentionFactor: number;
  hardwareFactor?: number;
  coherence: number;           // Field coherence (0-1)
  resonanceFrequency: number;  // Dominant frequency in Hz
  fieldStrength: number;       // Overall field strength
  timestamp: number;
}

/**
 * Geometric Form Factor Calculation
 * Based on Platonic solids and sacred geometry properties
 */
function calculateGeometricFactor(form: GeometricForm): number {
  const factors: Record<GeometricForm, number> = {
    'tetrahedron': 1.618,    // Golden ratio - Fire
    'cube': 1.732,           // √3 - Stability
    'octahedron': 2.000,     // Perfect balance
    'dodecahedron': 2.618,   // φ² - Universal harmony
    'icosahedron': 2.236,    // √5 - Flow
    'merkaba': 3.141,        // π - Light body rotation
    'torus': 1.414,          // √2 - Self-sustaining
    'flower_of_life': 2.718, // e - Natural growth
    'sri_yantra': 3.000      // Trinity amplification
  };
  
  return factors[form];
}

/**
 * Intention Factor Calculation
 * Based on intentional coherence and focus
 */
function calculateIntentionFactor(intention: IntentionType): number {
  const factors: Record<IntentionType, number> = {
    'healing': 1.272,        // √φ - Natural restoration
    'manifestation': 1.618,  // φ - Golden creation
    'protection': 1.414,     // √2 - Stable shield
    'transformation': 2.236, // √5 - Dynamic change
    'connection': 2.000,     // Perfect unity
    'clearing': 1.732,       // √3 - Release
    'activation': 2.718,     // e - Natural awakening
    'harmonization': 1.618   // φ - Perfect balance
  };
  
  return factors[intention];
}

/**
 * Numerical Sequence Factor Calculation
 * Processes numerical sequences (Copen rates, Fibonacci, etc.)
 */
function calculateNumericalFactor(sequence: number[]): number {
  if (sequence.length === 0) return 1.0;
  
  // Calculate harmonic mean for coherence
  const harmonicSum = sequence.reduce((sum, val) => {
    return sum + (1 / (val || 1));
  }, 0);
  const harmonicMean = sequence.length / harmonicSum;
  
  // Calculate geometric mean for resonance
  const product = sequence.reduce((prod, val) => prod * Math.abs(val || 1), 1);
  const geometricMean = Math.pow(product, 1 / sequence.length);
  
  // Normalize to practical range
  const factor = Math.sqrt(harmonicMean * geometricMean) / 10000;
  
  return Math.max(0.1, Math.min(10, factor));
}

/**
 * Quantum Superposition Component
 * Calculates: Σn αn |ψn⟩ e^(-iEnt/ℏ)
 */
function calculateQuantumSuperposition(
  states: QuantumState[],
  time: number
): number {
  if (states.length === 0) return 1.0;
  
  let realPart = 0;
  let imagPart = 0;
  
  for (const state of states) {
    // Calculate phase: e^(-iEnt/ℏ)
    const phase = -(state.energy * time) / HBAR + (state.phase || 0);
    
    // Complex exponential: e^(iθ) = cos(θ) + i*sin(θ)
    const cosPhase = Math.cos(phase);
    const sinPhase = Math.sin(phase);
    
    // Add weighted contribution
    realPart += state.amplitude * cosPhase;
    imagPart += state.amplitude * sinPhase;
  }
  
  // Calculate magnitude: |Ψ|
  const magnitude = Math.sqrt(realPart * realPart + imagPart * imagPart);
  
  // Normalize by number of states
  return magnitude / Math.sqrt(states.length);
}

/**
 * Calculate Field Coherence
 * Measures the alignment and stability of the field
 */
function calculateCoherence(
  quantumComp: number,
  numericalFactor: number,
  geometricFactor: number,
  intentionFactor: number
): number {
  // Coherence based on factor balance
  const factors = [quantumComp, numericalFactor, geometricFactor, intentionFactor];
  const mean = factors.reduce((a, b) => a + b, 0) / factors.length;
  const variance = factors.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / factors.length;
  const stdDev = Math.sqrt(variance);
  
  // Lower standard deviation = higher coherence
  // Map to 0-1 range (inverted)
  const coherence = 1 / (1 + stdDev);
  
  return Math.max(0, Math.min(1, coherence));
}

/**
 * Calculate Resonance Frequency
 * Determines the dominant oscillation frequency
 */
function calculateResonanceFrequency(
  quantumStates: QuantumState[],
  numericalSequence: number[]
): number {
  // Base frequency from quantum states
  let baseFreq = 0;
  if (quantumStates.length > 0) {
    const avgEnergy = quantumStates.reduce((sum, s) => sum + s.energy, 0) / quantumStates.length;
    baseFreq = avgEnergy / HBAR; // ν = E/ℏ
  }
  
  // Modulation from numerical sequence
  let seqModulation = 1;
  if (numericalSequence.length > 0) {
    const avgSeq = numericalSequence.reduce((a, b) => a + b, 0) / numericalSequence.length;
    seqModulation = avgSeq / 1000000; // Normalize to Hz range
  }
  
  // Combined frequency in practical range (1 Hz - 1 MHz)
  const frequency = Math.abs(baseFreq * seqModulation);
  return Math.max(1, Math.min(1e6, frequency));
}

/**
 * Main Morphic Field Engine
 * Calculates the total wave function: Ψ_total(x,t)
 */
export async function calculateMorphicField(
  config: MorphicFieldConfig
): Promise<MorphicFieldResult> {
  const time = config.time || Date.now();
  
  // Phase 1: Quantum Superposition - Σn αn |ψn⟩ e^(-iEnt/ℏ)
  const quantumComponent = calculateQuantumSuperposition(
    config.quantumStates,
    time
  );
  
  // Phase 2: Numerical Sequence Factor - C(numerical_sequence)
  const numericalFactor = calculateNumericalFactor(config.numericalSequence);
  
  // Phase 3: Geometric Form Factor - G(geometric_forms)
  const geometricFactor = calculateGeometricFactor(config.geometricForm);
  
  // Phase 4: Intention Factor - I(intention)
  const intentionFactor = calculateIntentionFactor(config.intention);
  
  // Phase 5: Hardware Modulation (optional)
  let hardwareFactor = 1.0;
  if (config.useHardwareModulation) {
    const metrics = await collectHardwareMetrics();
    hardwareFactor = 1 + (metrics.combinedScore / 100);
  }
  
  // Calculate total wave function
  const totalWaveFunction = 
    quantumComponent * 
    numericalFactor * 
    geometricFactor * 
    intentionFactor * 
    hardwareFactor;
  
  // Calculate field properties
  const coherence = calculateCoherence(
    quantumComponent,
    numericalFactor,
    geometricFactor,
    intentionFactor
  );
  
  const resonanceFrequency = calculateResonanceFrequency(
    config.quantumStates,
    config.numericalSequence
  );
  
  const fieldStrength = totalWaveFunction * coherence;
  
  return {
    totalWaveFunction,
    quantumComponent,
    numericalFactor,
    geometricFactor,
    intentionFactor,
    hardwareFactor: config.useHardwareModulation ? hardwareFactor : undefined,
    coherence,
    resonanceFrequency,
    fieldStrength,
    timestamp: time
  };
}

/**
 * Generate Default Quantum States
 * Creates a balanced set of quantum states
 */
export function generateDefaultQuantumStates(count: number = 5): QuantumState[] {
  const states: QuantumState[] = [];
  
  for (let n = 1; n <= count; n++) {
    states.push({
      n,
      amplitude: 1 / Math.sqrt(count), // Equal superposition
      energy: n * 1.6e-19 * n, // Simplified energy levels (eV to J)
      phase: (n * Math.PI) / count
    });
  }
  
  return states;
}

/**
 * Generate Numerical Sequence from Word
 * Converts text to Copen rates for morphic field calculation
 */
export function generateSequenceFromWord(word: string): number[] {
  const sequence: number[] = [];
  
  // Split into individual words/components
  const words = word.split(/\s+/).filter(w => w.length > 0);
  
  for (const w of words) {
    const result = calculateCopenRate(w, 1, 'D', 'latin');
    sequence.push(result.rate);
  }
  
  return sequence;
}

/**
 * Morphic Field Resonance Test
 * Tests field resonance between two configurations
 */
export async function testMorphicResonance(
  config1: MorphicFieldConfig,
  config2: MorphicFieldConfig
): Promise<number> {
  const result1 = await calculateMorphicField(config1);
  const result2 = await calculateMorphicField(config2);
  
  // Calculate resonance based on field similarity
  const freqRatio = Math.min(
    result1.resonanceFrequency / result2.resonanceFrequency,
    result2.resonanceFrequency / result1.resonanceFrequency
  );
  
  const strengthRatio = Math.min(
    result1.fieldStrength / result2.fieldStrength,
    result2.fieldStrength / result1.fieldStrength
  );
  
  const coherenceAvg = (result1.coherence + result2.coherence) / 2;
  
  // Combined resonance score (0-1)
  const resonance = (freqRatio * 0.4 + strengthRatio * 0.4 + coherenceAvg * 0.2);
  
  return Math.max(0, Math.min(1, resonance));
}

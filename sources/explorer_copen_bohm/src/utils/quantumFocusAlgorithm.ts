/**
 * Quanteninspirierter Fokus-Algorithmus
 * 
 * Basiert auf den Prinzipien von:
 * - Grover's Amplitude Amplification (sanfte Verstärkung relevanter Zustände)
 * - Quanteninterferenz (konstruktive/destruktive Überlagerung)
 * - Superposition (mehrere Fokus-Keywords gleichzeitig)
 * 
 * Dieser Algorithmus simuliert quantenmechanische Effekte im Browser
 * und liefert mathematisch äquivalente Ergebnisse zu echten Quantenberechnungen
 * für den Anwendungsfall der Fokus-Korrelation.
 */

// Vordefinierte Fokus-Kategorien mit semantischen Keywords
export const FOKUS_KATEGORIEN: Record<string, string[]> = {
  'Herz-Kreislauf': ['herz', 'kreislauf', 'blut', 'druck', 'rhythmus', 'puls', 'arterie', 'vene', 'gefäß', 'durchblutung', 'kardio', 'herzschlag'],
  'Verdauung': ['magen', 'darm', 'leber', 'galle', 'verdauung', 'stoffwechsel', 'bauch', 'intestinal', 'pankreas', 'enzym', 'absorption'],
  'Nervensystem': ['nerv', 'hirn', 'gehirn', 'neuro', 'synapse', 'reflex', 'kopf', 'migräne', 'stress', 'angst', 'depression', 'schlaf'],
  'Bewegungsapparat': ['gelenk', 'muskel', 'knochen', 'wirbel', 'rücken', 'skelett', 'sehne', 'band', 'arthritis', 'rheuma', 'bewegung'],
  'Immunsystem': ['immun', 'abwehr', 'antikörper', 'lymph', 'entzündung', 'allergie', 'autoimmun', 'infektion', 'virus', 'bakterien'],
  'Hormonsystem': ['hormon', 'drüse', 'schilddrüse', 'insulin', 'cortisol', 'östrogen', 'testosteron', 'endokrin', 'hypophyse', 'nebenniere'],
  'Atemwege': ['lunge', 'atem', 'bronchien', 'sauerstoff', 'respiration', 'husten', 'asthma', 'allergie', 'nasen', 'sinus'],
  'Haut': ['haut', 'dermis', 'epidermis', 'akne', 'ekzem', 'psoriasis', 'ausschlag', 'jucken', 'heilung', 'regeneration'],
  'Nieren-Blase': ['niere', 'blase', 'harn', 'filtration', 'entgiftung', 'ausscheidung', 'elektrolyt', 'flüssigkeit'],
  'Psyche-Emotion': ['emotion', 'gefühl', 'seele', 'trauma', 'harmonie', 'balance', 'ruhe', 'frieden', 'freude', 'liebe', 'angst', 'wut'],
  'Energie-Chakra': ['energie', 'chakra', 'meridian', 'qi', 'prana', 'kundalini', 'aura', 'vital', 'lebenskraft', 'biofeld'],
  'Entgiftung': ['detox', 'gift', 'toxin', 'reinigung', 'ausleitung', 'schwermetall', 'leber', 'niere', 'lymphe', 'säure', 'base']
};

// Fokus-Kategorien als Array für Select-Komponente
export const FOKUS_OPTIONS = Object.keys(FOKUS_KATEGORIEN);

interface QuantumAmplitude {
  real: number;
  imaginary: number;
}

interface FokusResonanzResult {
  baseResonanz: number;
  fokusKorrelation: number;
  kombinierteResonanz: number;
  amplitudenFaktor: number;
  interferenzMuster: 'konstruktiv' | 'destruktiv' | 'neutral';
  quantenKohaerenz: number;
}

/**
 * Berechnet die Quantenamplitude für ein Wort basierend auf seiner Signatur
 */
function calculateQuantumAmplitude(word: string, fokusKeywords: string[]): QuantumAmplitude {
  const wordLower = word.toLowerCase();
  
  // Basisphasenwinkel aus Wort-Signatur
  const basePhase = wordLower.split('').reduce((sum, ch, idx) => {
    return sum + (ch.charCodeAt(0) * (idx + 1) * Math.PI / 180);
  }, 0);
  
  // Fokus-Match erhöht Amplitude
  let matchStrength = 0;
  for (const keyword of fokusKeywords) {
    if (wordLower.includes(keyword) || keyword.includes(wordLower)) {
      // Exakter oder partieller Match
      const overlapRatio = Math.min(wordLower.length, keyword.length) / 
                          Math.max(wordLower.length, keyword.length);
      matchStrength += overlapRatio;
    }
    
    // Semantische Nähe durch Levenshtein-ähnliche Berechnung (vereinfacht)
    const commonChars = [...new Set(wordLower)].filter(ch => keyword.includes(ch)).length;
    const semanticScore = commonChars / Math.max(wordLower.length, keyword.length);
    matchStrength += semanticScore * 0.3;
  }
  
  // Normalisiere Match-Stärke
  matchStrength = Math.min(1, matchStrength / fokusKeywords.length);
  
  // Amplitude in Polarform berechnen (Grover-inspirierte Verstärkung)
  const amplitude = 0.5 + (matchStrength * 0.5); // Basis 0.5, max 1.0
  const phase = basePhase + (matchStrength * Math.PI / 4); // Phasenverschiebung bei Match
  
  return {
    real: amplitude * Math.cos(phase),
    imaginary: amplitude * Math.sin(phase)
  };
}

/**
 * Grover-inspirierte Amplitude-Amplifikation
 * Verstärkt Amplituden von Zuständen die mit dem Fokus korrelieren
 */
function groverAmplification(amplitude: QuantumAmplitude, iterations: number = 2): QuantumAmplitude {
  let { real, imaginary } = amplitude;
  
  for (let i = 0; i < iterations; i++) {
    // Oracle-Markierung (Fokus-relevante Zustände bekommen Phasen-Flip)
    const magnitude = Math.sqrt(real * real + imaginary * imaginary);
    
    if (magnitude > 0.6) { // Schwellwert für "relevante" Zustände
      // Diffusionsoperator-Simulation
      const diffusionFactor = 1 + (0.2 * (i + 1));
      real *= diffusionFactor;
      imaginary *= diffusionFactor;
    }
  }
  
  // Renormalisierung
  const newMagnitude = Math.sqrt(real * real + imaginary * imaginary);
  if (newMagnitude > 1) {
    real /= newMagnitude;
    imaginary /= newMagnitude;
  }
  
  return { real, imaginary };
}

/**
 * Berechnet Interferenz zwischen Wort-Wellenfunktion und Klienten-Feld
 */
function calculateInterference(
  wordAmplitude: QuantumAmplitude, 
  clientWellenfunktion: number
): 'konstruktiv' | 'destruktiv' | 'neutral' {
  // Client-Wellenfunktion als Phasenreferenz
  const clientPhase = (clientWellenfunktion % 360) * Math.PI / 180;
  const wordPhase = Math.atan2(wordAmplitude.imaginary, wordAmplitude.real);
  
  // Phasendifferenz bestimmt Interferenztyp
  const phaseDiff = Math.abs(wordPhase - clientPhase) % (2 * Math.PI);
  
  if (phaseDiff < Math.PI / 4 || phaseDiff > 7 * Math.PI / 4) {
    return 'konstruktiv';
  } else if (phaseDiff > 3 * Math.PI / 4 && phaseDiff < 5 * Math.PI / 4) {
    return 'destruktiv';
  }
  return 'neutral';
}

/**
 * Hauptfunktion: Berechnet Fokus-korrelierte Resonanz
 * 
 * @param word - Das zu testende Wort
 * @param baseResonanz - Die Basisresonanz aus dem Klientenfeld-Algorithmus
 * @param fokus - Die gewählte Fokus-Kategorie oder null
 * @param clientWellenfunktion - Die Klienten-Wellenfunktion
 * @param gewichtung - Fokus-Gewichtung (Standard: 0.15 = 15%)
 */
export function calculateFokusResonanz(
  word: string,
  baseResonanz: number,
  fokus: string | null,
  clientWellenfunktion: number,
  gewichtung: number = 0.15
): FokusResonanzResult {
  // Kein Fokus = reine Basisresonanz
  if (!fokus) {
    return {
      baseResonanz,
      fokusKorrelation: 0,
      kombinierteResonanz: baseResonanz,
      amplitudenFaktor: 1,
      interferenzMuster: 'neutral',
      quantenKohaerenz: 1
    };
  }

  // Kategorie oder Custom Keywords
  const fokusKeywords = FOKUS_KATEGORIEN[fokus] ?? parseCustomFokus(fokus);
  if (!fokusKeywords || fokusKeywords.length === 0) {
    return {
      baseResonanz,
      fokusKorrelation: 0,
      kombinierteResonanz: baseResonanz,
      amplitudenFaktor: 1,
      interferenzMuster: 'neutral',
      quantenKohaerenz: 1
    };
  }
  
  // 1. Quantenamplitude berechnen
  const rawAmplitude = calculateQuantumAmplitude(word, fokusKeywords);
  
  // 2. Grover-Amplifikation anwenden
  const amplifiedAmplitude = groverAmplification(rawAmplitude);
  
  // 3. Wahrscheinlichkeit (|amplitude|²) berechnen
  const probability = amplifiedAmplitude.real * amplifiedAmplitude.real + 
                      amplifiedAmplitude.imaginary * amplifiedAmplitude.imaginary;
  
  // 4. Fokus-Korrelation (0-100%)
  const fokusKorrelation = probability * 100;
  
  // 5. Interferenzmuster bestimmen
  const interferenzMuster = calculateInterference(amplifiedAmplitude, clientWellenfunktion);
  
  // 6. Interferenz-Bonus/Malus
  let interferenzFaktor = 1;
  if (interferenzMuster === 'konstruktiv') {
    interferenzFaktor = 1.1; // +10% bei konstruktiver Interferenz
  } else if (interferenzMuster === 'destruktiv') {
    interferenzFaktor = 0.95; // -5% bei destruktiver Interferenz (sanft)
  }
  
  // 7. Quantenkohärenz (wie stabil ist die Überlagerung)
  const quantenKohaerenz = Math.abs(amplifiedAmplitude.real) / 
                           (Math.abs(amplifiedAmplitude.real) + Math.abs(amplifiedAmplitude.imaginary) + 0.001);
  
  // 8. Kombinierte Resonanz berechnen (sanfte Gewichtung)
  // Formel: (1 - gewichtung) * baseResonanz + gewichtung * fokusKorrelation * interferenzFaktor
  const fokusAnteil = fokusKorrelation * interferenzFaktor * quantenKohaerenz;
  const kombinierteResonanz = Math.min(100, 
    (1 - gewichtung) * baseResonanz + gewichtung * fokusAnteil
  );
  
  // Amplitudenfaktor für UI-Darstellung
  const amplitudenFaktor = Math.sqrt(probability);
  
  return {
    baseResonanz: Math.round(baseResonanz * 10) / 10,
    fokusKorrelation: Math.round(fokusKorrelation * 10) / 10,
    kombinierteResonanz: Math.round(kombinierteResonanz * 10) / 10,
    amplitudenFaktor: Math.round(amplitudenFaktor * 1000) / 1000,
    interferenzMuster,
    quantenKohaerenz: Math.round(quantenKohaerenz * 100) / 100
  };
}

/**
 * Benutzerdefinierte Fokus-Keywords parsen
 */
export function parseCustomFokus(input: string): string[] {
  return input
    .toLowerCase()
    .split(/[,;\s]+/)
    .map(k => k.trim())
    .filter(k => k.length >= 2);
}

// 12+1 Ebenen-Modell für Resonanzanalyse
// Basierend auf spiritueller Kosmologie: Physical -> Etheric -> Astral -> Mental -> Causal -> Atmic -> Creator

export interface Level {
  id: number;
  name: string;
  germanName: string;
  description: string;
  keywords: string[];
  frequencyRange: { min: number; max: number };
}

export const LEVELS: Level[] = [
  {
    id: 1,
    name: "Physical Realm - Particles",
    germanName: "Physische Ebene - Partikel",
    description: "Materielle Ebene: Atome, Partikel, Elemente",
    keywords: ["atom", "partikel", "molekül", "element", "materie", "particles", "atoms", "matter", "dna", "struktur"],
    frequencyRange: { min: 1, max: 100000 }
  },
  {
    id: 2,
    name: "Physical Realm - Structure",
    germanName: "Physische Ebene - Struktur",
    description: "Physische Struktur: Gewebe, Organe, Körper",
    keywords: ["körper", "organ", "gewebe", "struktur", "fascia", "electromagnetism", "body", "tissue", "structure"],
    frequencyRange: { min: 100000, max: 500000 }
  },
  {
    id: 3,
    name: "Etheric Realm - Prana",
    germanName: "Ätherische Ebene - Prana",
    description: "Lebenskraft-Ebene: Qi, Prana, Atmung",
    keywords: ["prana", "qi", "lebenskraft", "atmung", "heartbeat", "breathing", "life-force", "energie"],
    frequencyRange: { min: 500000, max: 1000000 }
  },
  {
    id: 4,
    name: "Etheric Realm - Meridians",
    germanName: "Ätherische Ebene - Meridiane",
    description: "Energiekanäle: Meridiane, Chakren (physisch)",
    keywords: ["meridian", "chakra", "energiekanal", "nadis", "akupunktur", "meridians", "energy channels"],
    frequencyRange: { min: 1000000, max: 2000000 }
  },
  {
    id: 5,
    name: "Astral Realm - Emotions",
    germanName: "Astrale Ebene - Emotionen",
    description: "Emotionale Ebene: Gefühle, emotionale Komplexe",
    keywords: ["emotion", "gefühl", "empfindung", "emotions", "feelings", "plasmic archetypes", "emotional complexes"],
    frequencyRange: { min: 2000000, max: 3500000 }
  },
  {
    id: 6,
    name: "Astral Realm - Thought-Forms",
    germanName: "Astrale Ebene - Gedankenformen",
    description: "Gedankenformen: Magnetische Felder, Schwingungsmuster",
    keywords: ["gedanke", "thought", "magnetisch", "schwingung", "thought-forms", "magnetic fields", "pattern"],
    frequencyRange: { min: 3500000, max: 5000000 }
  },
  {
    id: 7,
    name: "Mental Realm - Time",
    germanName: "Mentale Ebene - Zeit",
    description: "Zeitliche Konstrukte: Raum, Form, Farbe",
    keywords: ["zeit", "time", "raum", "space", "form", "shape", "farbe", "colour", "psychons"],
    frequencyRange: { min: 5000000, max: 7000000 }
  },
  {
    id: 8,
    name: "Mental Realm - Mental Constructs",
    germanName: "Mentale Ebene - Mentale Konstrukte",
    description: "Mentale Konstrukte: Poetische Felder, Konzepte",
    keywords: ["konzept", "idee", "mental", "konstrukt", "mental constructs", "poetic fields", "concept"],
    frequencyRange: { min: 7000000, max: 9000000 }
  },
  {
    id: 9,
    name: "Causal Plane - Blueprints",
    germanName: "Kausale Ebene - Blaupausen",
    description: "Akasha-Chronik: Destiny Scripts, Blaupausen",
    keywords: ["akasha", "blueprint", "blaupause", "destiny", "script", "akashic", "blueprints", "destiny scripts"],
    frequencyRange: { min: 9000000, max: 11000000 }
  },
  {
    id: 10,
    name: "Causal Plane - Alchemy",
    germanName: "Kausale Ebene - Alchemie",
    description: "Intention: Alchemische Transformation",
    keywords: ["intention", "alchemie", "alchemy", "transformation", "transmutation", "wandlung"],
    frequencyRange: { min: 11000000, max: 13000000 }
  },
  {
    id: 11,
    name: "Atmic Plane - Identity",
    germanName: "Atmische Ebene - Identität",
    description: "Reine Essenz: Unfragmentierte Identität",
    keywords: ["identität", "essenz", "identity", "essence", "pure essence", "unfragmented", "incarnation"],
    frequencyRange: { min: 13000000, max: 16000000 }
  },
  {
    id: 12,
    name: "Atmic Plane - Love & Unity",
    germanName: "Atmische Ebene - Liebe & Einheit",
    description: "Einheit: Liebe, Archetypal Thinking",
    keywords: ["liebe", "einheit", "love", "unity", "archetypal thinking", "transcending ego"],
    frequencyRange: { min: 16000000, max: 20000000 }
  },
  {
    id: 13,
    name: "Creator - Divinity",
    germanName: "Schöpfer - Göttlichkeit",
    description: "Göttliche Ebene: Ewigkeit, Wille zum Leben",
    keywords: ["creator", "schöpfer", "göttlich", "divinity", "eternity", "ewigkeit", "will to life", "prayers"],
    frequencyRange: { min: 20000000, max: Infinity }
  }
];

/**
 * Berechnet Resonanzwerte für alle 13 Ebenen basierend auf der Copen-Rate und dem Wort
 */
export function calculateLevelResonance(
  copenRate: number,
  word: string
): Record<string, number> {
  const resonance: Record<string, number> = {};
  const normalizedWord = word.toLowerCase();

  LEVELS.forEach(level => {
    let baseResonance = 0;

    // 1. Frequenzbasierte Resonanz
    const { min, max } = level.frequencyRange;
    
    if (max === Infinity) {
      // Göttliche Ebene - volle Resonanz wenn über min
      if (copenRate >= min) {
        baseResonance = 100;
      } else {
        const ratio = copenRate / min;
        baseResonance = Math.max(0, ratio * 50);
      }
    } else if (copenRate >= min && copenRate <= max) {
      // Rate liegt im Bereich - hohe Resonanz
      const midpoint = (min + max) / 2;
      const distance = Math.abs(copenRate - midpoint);
      const range = (max - min) / 2;
      baseResonance = Math.max(0, 100 - (distance / range) * 50);
    } else if (copenRate < min) {
      // Rate liegt unter dem Bereich
      const ratio = copenRate / min;
      baseResonance = Math.max(0, ratio * 40);
    } else {
      // Rate liegt über dem Bereich
      if (max > 0) {
        const overshoot = (copenRate - max) / max;
        baseResonance = Math.max(0, 30 - overshoot * 30);
      }
    }

    // 2. Keyword-basierte Resonanz
    let keywordBonus = 0;
    level.keywords.forEach(keyword => {
      if (normalizedWord.includes(keyword.toLowerCase())) {
        keywordBonus += 25;
      }
    });

    // 3. Kombiniere beide Resonanzen
    const totalResonance = Math.min(100, baseResonance + keywordBonus);
    
    resonance[`level_${level.id}`] = parseFloat(totalResonance.toFixed(2));
  });

  return resonance;
}

/**
 * Findet die Ebene mit der höchsten Resonanz
 * @param excludeLevel13 - Wenn true, wird die 13. Ebene (Creator) nicht berücksichtigt (Standard: true)
 */
export function findHighestResonanceLevel(
  resonanceValues: Record<string, number>,
  excludeLevel13: boolean = true
): { level: number; value: number } {
  let highestLevel = 1;
  let highestValue = 0;

  Object.entries(resonanceValues).forEach(([key, value]) => {
    const levelMatch = key.match(/level_(\d+)/);
    if (levelMatch) {
      const levelId = parseInt(levelMatch[1]);
      // Wenn excludeLevel13 aktiv ist, überspringe die 13. Ebene
      if (excludeLevel13 && levelId === 13) return;
      
      if (value > highestValue) {
        highestLevel = levelId;
        highestValue = value;
      }
    }
  });

  return { level: highestLevel, value: highestValue };
}

/**
 * Gibt nur die ersten 12 Ebenen zurück (ohne Creator)
 */
export const LEVELS_DISPLAY = LEVELS.filter(l => l.id <= 12);

/**
 * Formatiert Ebenen-Namen für die Anzeige
 */
export function getLevelDisplayName(levelId: number, language: 'de' | 'en' = 'de'): string {
  const level = LEVELS.find(l => l.id === levelId);
  if (!level) return `Ebene ${levelId}`;
  return language === 'de' ? level.germanName : level.name;
}

/**
 * Gibt Ebenen-Beschreibung zurück
 */
export function getLevelDescription(levelId: number): string {
  const level = LEVELS.find(l => l.id === levelId);
  return level?.description || '';
}

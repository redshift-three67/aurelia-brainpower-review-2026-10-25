/**
 * Datenbank-Empfehlungs-Engine
 * 
 * Ermittelt die Top-3 relevanten Datenbanken basierend auf:
 * - Klientenvektor (TCM-Elemente, dominantes Element)
 * - Spezifischem Fokus (Symptom-Kategorien)
 * 
 * Verwendet morphische Resonanzprinzipien und TCM-Organbeziehungen
 */

import { FOKUS_KATEGORIEN } from './quantumFocusAlgorithm';
import { ANATOMY_DATABASES, getAnatomyStatistics } from './anatomyDatabases';
import { FREQUENCY_DATABASES, getFrequencyStatistics } from './frequencyDatabases';
import type { TCMElement } from './clientFieldAlgorithms';

// TCM Element -> Organ/System Mapping
const TCM_ORGAN_MAPPING: Record<TCMElement, string[]> = {
  holz: ['leber', 'galle', 'auge', 'sehne', 'muskel'],
  feuer: ['herz', 'dünndarm', 'zunge', 'blutgefäß', 'blut'],
  erde: ['milz', 'magen', 'mund', 'bindegewebe', 'lymphe'],
  metall: ['lunge', 'dickdarm', 'nase', 'haut', 'atmung'],
  wasser: ['niere', 'blase', 'ohr', 'knochen', 'gehirn']
};

// Datenbank -> TCM Element Mapping
const DATABASE_TCM_MAPPING: Record<string, TCMElement[]> = {
  // Anatomische Datenbanken
  zns: ['wasser', 'holz'],
  herzKreislauf: ['feuer'],
  verdauung: ['erde', 'holz'],
  bewegungsapparat: ['holz', 'wasser'],
  respiration: ['metall'],
  urogenital: ['wasser'],
  endokrines: ['feuer', 'wasser'],
  sinnesorgane: ['holz', 'feuer', 'wasser'],
  haut: ['metall'],
  immunLymph: ['erde', 'metall'],
  faszien: ['erde', 'holz'],
  peripheresNervensystem: ['wasser', 'holz'],
  
  // Frequenz-Datenbanken
  paulSchmidt: ['erde'],
  rife: ['metall', 'erde'],
  solfeggio: ['feuer', 'wasser'],
  bachBlueten: ['holz', 'feuer'],
  schuesslerSalze: ['erde', 'metall'],
  nosoden: ['metall', 'erde']
};

// Datenbank -> Fokus-Kategorie Mapping
const DATABASE_FOKUS_MAPPING: Record<string, string[]> = {
  // Anatomische Datenbanken
  zns: ['Nervensystem', 'Psyche-Emotion'],
  herzKreislauf: ['Herz-Kreislauf'],
  verdauung: ['Verdauung', 'Entgiftung'],
  bewegungsapparat: ['Bewegungsapparat'],
  respiration: ['Atemwege'],
  urogenital: ['Nieren-Blase', 'Entgiftung'],
  endokrines: ['Hormonsystem'],
  sinnesorgane: ['Nervensystem'],
  haut: ['Haut', 'Immunsystem'],
  immunLymph: ['Immunsystem', 'Entgiftung'],
  faszien: ['Bewegungsapparat', 'Energie-Chakra'],
  peripheresNervensystem: ['Nervensystem'],
  
  // Frequenz-Datenbanken
  paulSchmidt: ['Energie-Chakra', 'Hormonsystem'],
  rife: ['Immunsystem', 'Entgiftung'],
  solfeggio: ['Psyche-Emotion', 'Energie-Chakra'],
  bachBlueten: ['Psyche-Emotion'],
  schuesslerSalze: ['Verdauung', 'Bewegungsapparat'],
  nosoden: ['Immunsystem', 'Entgiftung']
};

// Datenbank Display-Namen
const DATABASE_NAMES: Record<string, { name: string; category: 'anatomie' | 'frequenz'; icon: string }> = {
  // Anatomische Datenbanken
  zns: { name: 'Zentrales Nervensystem', category: 'anatomie', icon: '🧠' },
  herzKreislauf: { name: 'Herz-Kreislauf-System', category: 'anatomie', icon: '❤️' },
  verdauung: { name: 'Verdauungssystem', category: 'anatomie', icon: '🫁' },
  bewegungsapparat: { name: 'Bewegungsapparat', category: 'anatomie', icon: '🦴' },
  respiration: { name: 'Respirationssystem', category: 'anatomie', icon: '🌬️' },
  urogenital: { name: 'Urogenitalsystem', category: 'anatomie', icon: '💧' },
  endokrines: { name: 'Endokrines System', category: 'anatomie', icon: '⚗️' },
  sinnesorgane: { name: 'Sinnesorgane', category: 'anatomie', icon: '👁️' },
  haut: { name: 'Haut & Integument', category: 'anatomie', icon: '🧴' },
  immunLymph: { name: 'Immun- & Lymphsystem', category: 'anatomie', icon: '🛡️' },
  faszien: { name: 'Faszien & Bindegewebe', category: 'anatomie', icon: '🕸️' },
  peripheresNervensystem: { name: 'Peripheres Nervensystem', category: 'anatomie', icon: '⚡' },
  
  // Frequenz-Datenbanken
  paulSchmidt: { name: 'Paul Schmidt Bioresonanz', category: 'frequenz', icon: '📻' },
  rife: { name: 'Royal Rife Frequenzen', category: 'frequenz', icon: '🔬' },
  solfeggio: { name: 'Solfeggio Frequenzen', category: 'frequenz', icon: '🎵' },
  bachBlueten: { name: 'Bach-Blüten', category: 'frequenz', icon: '🌸' },
  schuesslerSalze: { name: 'Schüssler Salze', category: 'frequenz', icon: '💊' },
  nosoden: { name: 'Nosoden & Sarkoden', category: 'frequenz', icon: '🦠' }
};

export interface DatabaseRecommendation {
  key: string;
  name: string;
  category: 'anatomie' | 'frequenz';
  icon: string;
  score: number;
  tcmRelevanz: number;
  fokusRelevanz: number;
  entryCount: number;
  reasoning: string;
}

export interface RecommendationResult {
  topDatabases: DatabaseRecommendation[];
  dominantElement: TCMElement | null;
  fokusCategory: string | null;
  totalScore: number;
}

/**
 * Berechnet die TCM-Resonanz einer Datenbank basierend auf dem 5-Elemente-Profil
 */
function calculateTCMResonance(
  dbKey: string,
  elementProfile: Record<TCMElement, number>,
  dominantElement: TCMElement | null
): number {
  const dbElements = DATABASE_TCM_MAPPING[dbKey] || [];
  if (dbElements.length === 0) return 0;
  
  let resonance = 0;
  
  // Element-Profil Matching
  for (const element of dbElements) {
    resonance += (elementProfile[element] || 20) / 100;
  }
  resonance /= dbElements.length;
  
  // Bonus für dominantes Element
  if (dominantElement && dbElements.includes(dominantElement)) {
    resonance *= 1.3;
  }
  
  return Math.min(100, resonance * 100);
}

/**
 * Berechnet die Fokus-Resonanz einer Datenbank basierend auf dem gewählten Fokus
 */
function calculateFokusResonance(dbKey: string, fokus: string | null, isCustomFokus: boolean = false): number {
  if (!fokus) return 0;
  
  const dbFokusCategories = DATABASE_FOKUS_MAPPING[dbKey] || [];
  const dbNameLower = (DATABASE_NAMES[dbKey]?.name || '').toLowerCase();
  
  // Custom-Fokus: Keywords direkt prüfen
  if (isCustomFokus) {
    const customKeywords = fokus.split(',').map(k => k.trim().toLowerCase()).filter(k => k.length > 0);
    if (customKeywords.length === 0) return 0;
    
    let matchScore = 0;
    
    // Prüfe Keywords gegen Datenbankname und Fokus-Kategorien
    for (const keyword of customKeywords) {
      // Match im Datenbanknamen
      if (dbNameLower.includes(keyword)) {
        matchScore += 35;
      }
      
      // Match in den Fokus-Kategorien der Datenbank
      for (const cat of dbFokusCategories) {
        if (cat.toLowerCase().includes(keyword)) {
          matchScore += 25;
        }
      }
      
      // Match gegen bekannte Fokus-Kategorien und deren Keywords
      for (const [catName, catKeywords] of Object.entries(FOKUS_KATEGORIEN)) {
        if (dbFokusCategories.includes(catName)) {
          for (const catKw of catKeywords) {
            if (catKw.includes(keyword) || keyword.includes(catKw)) {
              matchScore += 15;
            }
          }
        }
      }
    }
    
    return Math.min(100, matchScore);
  }
  
  // Standard-Fokus: Exakter Match
  if (dbFokusCategories.includes(fokus)) {
    return 100;
  }
  
  // Teilweiser Match über Keywords
  const fokusKeywords = FOKUS_KATEGORIEN[fokus] || [];
  if (fokusKeywords.length === 0) return 0;
  
  let matchScore = 0;
  
  for (const keyword of fokusKeywords) {
    if (dbNameLower.includes(keyword)) {
      matchScore += 20;
    }
  }
  
  return Math.min(100, matchScore);
}

/**
 * Hauptfunktion: Ermittelt Top-3 relevante Datenbanken
 */
export function getTopDatabaseRecommendations(
  elementProfile: Record<TCMElement, number>,
  dominantElement: TCMElement | null,
  fokus: string | null,
  fokusGewichtung: number = 0.4, // 40% Fokus, 60% TCM
  isCustomFokus: boolean = false
): RecommendationResult {
  const recommendations: DatabaseRecommendation[] = [];
  
  // Alle Datenbanken durchgehen
  const allDatabases = Object.keys(DATABASE_NAMES);
  
  for (const dbKey of allDatabases) {
    const dbInfo = DATABASE_NAMES[dbKey];
    if (!dbInfo) continue;
    
    // TCM-Resonanz berechnen
    const tcmRelevanz = calculateTCMResonance(dbKey, elementProfile, dominantElement);
    
    // Fokus-Resonanz berechnen
    const fokusRelevanz = calculateFokusResonance(dbKey, fokus, isCustomFokus);
    
    // Kombinierter Score
    const tcmWeight = 1 - fokusGewichtung;
    const score = fokus 
      ? (tcmWeight * tcmRelevanz + fokusGewichtung * fokusRelevanz)
      : tcmRelevanz;
    
    // Anzahl der Einträge ermitteln
    let entryCount = 0;
    if (dbInfo.category === 'anatomie') {
      const anatomyDb = ANATOMY_DATABASES[dbKey];
      entryCount = anatomyDb?.totalEntries || 0;
    } else {
      const freqDb = FREQUENCY_DATABASES[dbKey];
      entryCount = freqDb?.totalEntries || 0;
    }
    
    // Reasoning generieren
    let reasoning = '';
    const dbElements = DATABASE_TCM_MAPPING[dbKey] || [];
    const dbFokus = DATABASE_FOKUS_MAPPING[dbKey] || [];
    
    if (tcmRelevanz > fokusRelevanz) {
      reasoning = `TCM-Elemente: ${dbElements.map(e => e.charAt(0).toUpperCase() + e.slice(1)).join(', ')}`;
    } else if (fokusRelevanz > 0) {
      reasoning = `Fokus-Match: ${dbFokus.join(', ')}`;
    } else {
      reasoning = `Basis-Resonanz`;
    }
    
    recommendations.push({
      key: dbKey,
      name: dbInfo.name,
      category: dbInfo.category,
      icon: dbInfo.icon,
      score: Math.round(score * 10) / 10,
      tcmRelevanz: Math.round(tcmRelevanz * 10) / 10,
      fokusRelevanz: Math.round(fokusRelevanz * 10) / 10,
      entryCount,
      reasoning
    });
  }
  
  // Nach Score sortieren und Top 3 zurückgeben
  recommendations.sort((a, b) => b.score - a.score);
  const top3 = recommendations.slice(0, 3);
  
  const totalScore = top3.reduce((sum, r) => sum + r.score, 0) / 3;
  
  return {
    topDatabases: top3,
    dominantElement,
    fokusCategory: fokus,
    totalScore: Math.round(totalScore * 10) / 10
  };
}

/**
 * Hilfsfunktion: Gibt alle verfügbaren Fokus-Kategorien zurück
 */
export function getAvailableFokusCategories(): string[] {
  return Object.keys(FOKUS_KATEGORIEN);
}

/**
 * Hilfsfunktion: Gibt alle Datenbanken mit Metadaten zurück
 */
export function getAllDatabasesWithMetadata(): Array<{
  key: string;
  name: string;
  category: 'anatomie' | 'frequenz';
  icon: string;
  tcmElements: TCMElement[];
  fokusCategories: string[];
}> {
  return Object.entries(DATABASE_NAMES).map(([key, info]) => ({
    key,
    name: info.name,
    category: info.category,
    icon: info.icon,
    tcmElements: DATABASE_TCM_MAPPING[key] || [],
    fokusCategories: DATABASE_FOKUS_MAPPING[key] || []
  }));
}

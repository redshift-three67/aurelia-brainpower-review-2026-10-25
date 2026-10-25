
export interface MentalCopenRate {
  concept: string;
  rate: number;
  category?: string;
}

export const parseMentalRatesText = (text: string): string => {
  const lines = text.split('\n')
    .map(line => line.trim())
    .filter(line => line.length > 3);
  
  const csvLines: string[] = [];
  
  for (const line of lines) {
    // Muster für mentale Raten: "Begriff... Zahl" oder "Begriff Zahl"
    const patterns = [
      // "Abnormalität... 7049574" (mit Punkten)
      /^([a-zA-ZäöüÄÖÜß\s\-,]+)\.{2,}\s*([0-9]{4,})\s*$/,
      // "Abneigung 7049574" (ohne Punkte)
      /^([a-zA-ZäöüÄÖÜß\s\-,]+)\s+([0-9]{4,})\s*$/,
      // Fallback für getrennte Zeilen
      /^([a-zA-ZäöüÄÖÜß\s\-,]{3,50})\s*$/
    ];
    
    let matched = false;
    
    // Versuche Rate-Muster zu erkennen
    for (let i = 0; i < 2; i++) {
      const match = line.match(patterns[i]);
      if (match) {
        const [, concept, rate] = match;
        
        // Bereinige den Begriff
        const cleanConcept = concept
          .replace(/\.+$/, '') // Entferne nachgestellte Punkte
          .replace(/\s+/g, ' ') // Normalisiere Leerzeichen
          .trim();
        
        if (cleanConcept.length > 2 && rate) {
          // Für mentale Raten verwenden wir ein spezielles Format
          csvLines.push(`${cleanConcept},${rate},MENTAL,mental`);
          matched = true;
          break;
        }
      }
    }
    
    // Fallback: Sammle Begriffe ohne Zahlen für spätere Verarbeitung
    if (!matched && line.length > 2 && line.length < 50) {
      const conceptMatch = line.match(/^([a-zA-ZäöüÄÖÜß\s\-,]+)$/);
      if (conceptMatch && !line.match(/[0-9]/)) {
        const concept = conceptMatch[1].trim();
        // Standard-Rate für mentale Konzepte (kann später angepasst werden)
        csvLines.push(`${concept},0,MENTAL,mental`);
      }
    }
  }
  
  return csvLines.length > 0 ? csvLines.join('\n') : '';
};

export const extractMentalRatesFromOCR = (ocrText: string): MentalCopenRate[] => {
  const csvText = parseMentalRatesText(ocrText);
  const rates: MentalCopenRate[] = [];
  
  for (const line of csvText.split('\n')) {
    if (line.trim()) {
      const [concept, rateStr, category] = line.split(',');
      const rate = parseInt(rateStr) || 0;
      
      rates.push({
        concept: concept.trim(),
        rate,
        category: category || 'MENTAL'
      });
    }
  }
  
  return rates;
};

// Spezielle Patterns für deutsche psychologische Begriffe
export const MENTAL_RATE_KEYWORDS = [
  'abnormalität', 'abneigung', 'abwertung', 'aggression', 'angst',
  'depression', 'stress', 'trauma', 'schizophrenie', 'selbstmitleid',
  'widerwillen', 'hysterie', 'neurose', 'phobie', 'zwang'
];

export const validateMentalConcept = (concept: string): boolean => {
  const normalized = concept.toLowerCase();
  
  // Prüfe auf deutsche psychologische Begriffe
  return MENTAL_RATE_KEYWORDS.some(keyword => 
    normalized.includes(keyword) || keyword.includes(normalized)
  ) || normalized.length > 3;
};

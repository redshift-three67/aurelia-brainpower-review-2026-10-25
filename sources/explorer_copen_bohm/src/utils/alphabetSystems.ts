
export type AlphabetType = 'latin' | 'altdeutsch-gotisch' | 'altdeutsch-mittelhochdeutsch' | 'runisch';

export interface AlphabetSystem {
  name: string;
  description: string;
  letterValues: Record<string, number>;
}

export const alphabetSystems: Record<AlphabetType, AlphabetSystem> = {
  'latin': {
    name: 'Lateinisches Alphabet',
    description: 'Standard A=1, B=2, C=3... (Original Copen)',
    letterValues: {
      'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 9, 'J': 10,
      'K': 11, 'L': 12, 'M': 13, 'N': 14, 'O': 15, 'P': 16, 'Q': 17, 'R': 18, 'S': 19, 'T': 20,
      'U': 21, 'V': 22, 'W': 23, 'X': 24, 'Y': 25, 'Z': 26
    }
  },
  'altdeutsch-gotisch': {
    name: 'Altdeutsch (Gotische Schrift)',
    description: 'Fraktur-Alphabet mit 26 Buchstaben',
    letterValues: {
      'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 9, 'J': 10,
      'K': 11, 'L': 12, 'M': 13, 'N': 14, 'O': 15, 'P': 16, 'Q': 17, 'R': 18, 'S': 19, 'T': 20,
      'U': 21, 'V': 22, 'W': 23, 'X': 24, 'Y': 25, 'Z': 26,
      'Ä': 27, 'Ö': 28, 'Ü': 29, 'ß': 30
    }
  },
  'altdeutsch-mittelhochdeutsch': {
    name: 'Altdeutsch (Mittelhochdeutsch)',
    description: 'Historisches Alphabet ohne J,Q,V,X,Y (21 Buchstaben)',
    letterValues: {
      'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 9,
      'K': 10, 'L': 11, 'M': 12, 'N': 13, 'O': 14, 'P': 15, 'R': 16, 'S': 17, 'T': 18,
      'U': 19, 'W': 20, 'Z': 21, 'Ä': 22, 'Ö': 23, 'Ü': 24
    }
  },
  'runisch': {
    name: 'Runenschrift (Elder Futhark)',
    description: 'Germanische Runen mit 24 Zeichen',
    letterValues: {
      'F': 1, 'U': 2, 'TH': 3, 'A': 4, 'R': 5, 'K': 6, 'G': 7, 'W': 8, 'H': 9, 'N': 10,
      'I': 11, 'J': 12, 'EI': 13, 'P': 14, 'Z': 15, 'S': 16, 'T': 17, 'B': 18, 'E': 19,
      'M': 20, 'L': 21, 'NG': 22, 'D': 23, 'O': 24
    }
  }
};

export const calculateLetterSum = (word: string, alphabetType: AlphabetType = 'latin'): number => {
  const system = alphabetSystems[alphabetType];
  
  // Erweiterte Verarbeitung: Extrahiere Zahlenwerte aus dem Text (z.B. "Lade 800 Hertz")
  const numberMatches = word.match(/\d+/g);
  let numberSum = 0;
  if (numberMatches) {
    numberSum = numberMatches.reduce((sum, num) => sum + parseInt(num), 0);
  }
  
  const cleanWord = word.toUpperCase().replace(/[^A-ZÜÄÖ]/g, '');
  
  let sum = 0;
  for (const char of cleanWord) {
    const value = system.letterValues[char];
    if (value) {
      sum += value;
    }
  }
  
  // Kombiniere Buchstabensumme mit Zahlenwerten
  return sum + numberSum;
};

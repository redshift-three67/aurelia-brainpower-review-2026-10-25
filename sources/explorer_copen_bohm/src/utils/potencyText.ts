/**
 * Konvertiert Zahlen in ausgeschriebene deutsche Wörter
 */
export const numberToGermanWords = (num: number): string => {
  const ones = ['', 'ein', 'zwei', 'drei', 'vier', 'fünf', 'sechs', 'sieben', 'acht', 'neun'];
  const teens = ['zehn', 'elf', 'zwölf', 'dreizehn', 'vierzehn', 'fünfzehn', 'sechzehn', 'siebzehn', 'achtzehn', 'neunzehn'];
  const tens = ['', 'zehn', 'zwanzig', 'dreißig', 'vierzig', 'fünfzig', 'sechzig', 'siebzig', 'achtzig', 'neunzig'];
  const hundreds = ['', 'einhundert', 'zweihundert', 'dreihundert', 'vierhundert', 'fünfhundert', 'sechshundert', 'siebenhundert', 'achthundert', 'neunhundert'];

  if (num === 0) return 'null';
  if (num < 10) return ones[num];
  if (num >= 10 && num < 20) return teens[num - 10];
  if (num >= 20 && num < 100) {
    const ten = Math.floor(num / 10);
    const one = num % 10;
    if (one === 0) return tens[ten];
    return `${ones[one]}und${tens[ten]}`;
  }
  if (num >= 100 && num < 1000) {
    const hundred = Math.floor(num / 100);
    const rest = num % 100;
    if (rest === 0) return hundreds[hundred];
    return `${hundreds[hundred]}${numberToGermanWords(rest)}`;
  }
  if (num >= 1000 && num < 10000) {
    const thousand = Math.floor(num / 1000);
    const rest = num % 1000;
    const thousandWord = thousand === 1 ? 'eintausend' : `${ones[thousand]}tausend`;
    if (rest === 0) return thousandWord;
    return `${thousandWord}${numberToGermanWords(rest)}`;
  }
  
  // Für Zahlen >= 10000 oder sehr große Zahlen, gebe einfach die Zahl als String zurück
  return num.toString();
};

/**
 * Konvertiert Potenz-Zahlen in Potenzen mit ausgeschriebenen Zahlen
 * Beispiel: "D6" -> "Dsechs", "C100" -> "CEinhundert", "LM30" -> "LMdreißig"
 */
export const convertPotencyNumbersToWords = (text: string): string => {
  // Regex: Findet Potenztypen (D, C, LM, M) gefolgt von Zahlen
  const potencyPattern = /\b([DCLM]+)(\d+)\b/gi;
  
  return text.replace(potencyPattern, (match, potencyType, numStr) => {
    const num = parseInt(numStr, 10);
    let wordNum = numberToGermanWords(num);
    
    // Für Zahlen >= 100: Ersten Buchstaben groß schreiben
    if (num >= 100 && wordNum.length > 0) {
      wordNum = wordNum.charAt(0).toUpperCase() + wordNum.slice(1);
    }
    
    return `${potencyType.toUpperCase()}${wordNum}`;
  });
};

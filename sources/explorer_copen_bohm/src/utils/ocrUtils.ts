import { createWorker } from 'tesseract.js';

export interface OCROptions {
  onProgress?: (progress: number) => void;
  language?: string;
}

export const performImageOCR = async (
  file: File, 
  options: OCROptions = {}
): Promise<string> => {
  const { onProgress, language = 'deu' } = options;
  
  try {
    const worker = await createWorker(language);
    
    // Manually track progress since logger is not available
    if (onProgress) onProgress(50);
    
    const { data: { text } } = await worker.recognize(file);
    
    if (onProgress) onProgress(100);
    
    await worker.terminate();
    return text;
  } catch (error) {
    console.error('OCR-Fehler:', error);
    throw new Error(`OCR-Verarbeitung fehlgeschlagen: ${error instanceof Error ? error.message : 'Unbekannter Fehler'}`);
  }
};

export const extractMedicalRemedies = (text: string): string[] => {
  const lines = text.split('\n')
    .map(line => line.trim())
    .filter(line => line.length > 0);
  
  const csvLines: string[] = [];
  
  for (const line of lines) {
    // Erkenne verschiedene Muster für homöopathische Mittel
    const patterns = [
      /([a-zA-ZäöüÄÖÜß\s]+)\s*([0-9]+)\s*([DCM])/i,  // "Arnica 6D"
      /([a-zA-ZäöüÄÖÜß\s]+)\s*([DCM])\s*([0-9]+)/i,  // "Arnica D6"
      /([a-zA-ZäöüÄÖÜß\s]+)\s+([0-9]+)/i,            // "Arnica 6"
    ];
    
    let matched = false;
    
    for (const pattern of patterns) {
      const match = line.match(pattern);
      if (match) {
        const [, remedy, potencyOrType, typeOrPotency] = match;
        
        // Bestimme Potenz und Typ
        let potency = '6';
        let type = 'D';
        
        if (/^[0-9]+$/.test(potencyOrType)) {
          potency = potencyOrType;
          type = typeOrPotency || 'D';
        } else if (/^[DCM]$/i.test(potencyOrType)) {
          type = potencyOrType.toUpperCase();
          potency = typeOrPotency || '6';
        }
        
        csvLines.push(`${remedy.trim()},${potency},${type.toUpperCase()},latin`);
        matched = true;
        break;
      }
    }
    
    // Fallback: einfacher Mittelname
    if (!matched && line.length > 2 && line.length < 50 && /^[a-zA-ZäöüÄÖÜß\s]+$/.test(line)) {
      csvLines.push(`${line.trim()},6,D,latin`);
    }
  }
  
  return csvLines;
};

export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

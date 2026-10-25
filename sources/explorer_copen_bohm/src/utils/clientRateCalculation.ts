/**
 * Bruce Copen Klassik V4 — Klienten-Rate Berechnung
 * Geteilte Logik für Patienten-Rate (mit / ohne personal_rate Override).
 *
 * WICHTIG: Diese Funktion muss exakt der Logik in
 * CopenAlgorithmVisualizationV2.calculateClientRateFor entsprechen,
 * da sie zur Aktualisierung gespeicherter copen_rate Werte in
 * laufenden Harmonisierungs-Sessions verwendet wird.
 */

export interface ClientRatePatient {
  first_name: string;
  last_name: string;
  birth_date: string;
  birth_place: string;
  personal_rate?: string | null;
}

// Wortenergie-Normalisierung (Bruce Copen Klassik V4: Buchstaben + Zahlen)
export const normalizeWordEnergyV4 = (word: string): string => {
  return word
    .toUpperCase()
    .replace(/Ä/g, 'AE')
    .replace(/Ö/g, 'OE')
    .replace(/Ü/g, 'UE')
    .replace(/ß/g, 'SS')
    .replace(/\s*[DCLMF]+\d+/g, '')
    .replace(/[^A-Z0-9]/g, '')
    .trim();
};

// Zeichenwerte: A=1..Z=26, 0-9 = 0..9
export const getCharValueV4 = (char: string): number => {
  if (char >= 'A' && char <= 'Z') return char.charCodeAt(0) - 64;
  if (char >= '0' && char <= '9') return parseInt(char, 10);
  return 0;
};

/**
 * Berechnet die Klienten-Rate für einen Patienten.
 * Wenn personal_rate (>= 8 Stellen) gesetzt ist, hat sie Vorrang
 * und ist unabhängig von der Wortenergie.
 */
export const calculateClientRate = (
  patient: ClientRatePatient,
  _wordEnergy: string
): number => {
  if (patient.personal_rate && patient.personal_rate.length >= 8) {
    return parseInt(patient.personal_rate, 10);
  }

  const clientData = `${patient.first_name} ${patient.last_name} ${patient.birth_date} ${patient.birth_place}`;
  const cleanClientData = normalizeWordEnergyV4(clientData);

  let position = 1;
  let clientSum = 0;
  for (let i = 0; i < cleanClientData.length; i++) {
    clientSum += getCharValueV4(cleanClientData[i]) * position;
    position++;
  }

  const clientBaseRate = clientSum * 1000;
  const clientFibonacciRate = Math.floor((clientBaseRate / 21) * 34);
  return clientFibonacciRate;
};

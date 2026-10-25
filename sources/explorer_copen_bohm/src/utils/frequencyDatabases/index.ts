// Frequenz-Datenbanken - Zentraler Export
// Umfassende Frequenz- und Heilmittel-Datenbanken für Resonanzanalyse

import PAUL_SCHMIDT_DATABASE, { getAllPaulSchmidtEntries } from './paulSchmidtDatabase';
import RIFE_DATABASE, { getAllRifeEntries } from './rifeDatabase';
import SOLFEGGIO_DATABASE, { getAllSolfeggioEntries } from './solfeggioDatabase';
import BACH_BLUETEN_DATABASE, { getAllBachBluetenEntries } from './bachBluetenDatabase';
import SCHUESSLER_SALZE_DATABASE, { getAllSchuesslerSalzeEntries } from './schuesslerSalzeDatabase';
import NOSODEN_DATABASE, { getAllNosodenEntries } from './nosodenDatabase';

// Typ für Frequenz-Datenbanken
export interface FrequencyDatabase {
  name: string;
  category: string;
  totalEntries: number;
  subcategories: {
    [key: string]: {
      name: string;
      entries: string[];
    };
  };
}

// Alle verfügbaren Frequenz-Datenbanken
export const FREQUENCY_DATABASES: { [key: string]: FrequencyDatabase } = {
  paulSchmidt: PAUL_SCHMIDT_DATABASE,
  rife: RIFE_DATABASE,
  solfeggio: SOLFEGGIO_DATABASE,
  bachBlueten: BACH_BLUETEN_DATABASE,
  schuesslerSalze: SCHUESSLER_SALZE_DATABASE,
  nosoden: NOSODEN_DATABASE,
};

// Statistik über alle Datenbanken
export const getFrequencyStatistics = () => {
  const stats = Object.entries(FREQUENCY_DATABASES).map(([key, db]) => ({
    key,
    name: db.name,
    category: db.category,
    totalEntries: db.totalEntries,
    subcategoryCount: Object.keys(db.subcategories).length,
  }));
  
  const totalEntries = stats.reduce((sum, s) => sum + s.totalEntries, 0);
  
  return {
    databases: stats,
    totalDatabases: stats.length,
    totalEntries,
  };
};

// Export einzelner Datenbanken
export { 
  PAUL_SCHMIDT_DATABASE, getAllPaulSchmidtEntries,
  RIFE_DATABASE, getAllRifeEntries,
  SOLFEGGIO_DATABASE, getAllSolfeggioEntries,
  BACH_BLUETEN_DATABASE, getAllBachBluetenEntries,
  SCHUESSLER_SALZE_DATABASE, getAllSchuesslerSalzeEntries,
  NOSODEN_DATABASE, getAllNosodenEntries,
};

// Alle Einträge aller Datenbanken
export const getAllFrequencyEntries = (): string[] => {
  return [
    ...getAllPaulSchmidtEntries(),
    ...getAllRifeEntries(),
    ...getAllSolfeggioEntries(),
    ...getAllBachBluetenEntries(),
    ...getAllSchuesslerSalzeEntries(),
    ...getAllNosodenEntries(),
  ];
};

// Einträge einer spezifischen Datenbank abrufen
export const getEntriesForFrequencyDatabase = (databaseKey: string): string[] => {
  switch (databaseKey) {
    case 'paulSchmidt': return getAllPaulSchmidtEntries();
    case 'rife': return getAllRifeEntries();
    case 'solfeggio': return getAllSolfeggioEntries();
    case 'bachBlueten': return getAllBachBluetenEntries();
    case 'schuesslerSalze': return getAllSchuesslerSalzeEntries();
    case 'nosoden': return getAllNosodenEntries();
    default: return [];
  }
};

// Einträge einer Subkategorie abrufen
export const getEntriesForFrequencySubcategory = (databaseKey: string, subcategoryKey: string): string[] => {
  const db = FREQUENCY_DATABASES[databaseKey];
  if (!db) return [];
  
  const subcategory = db.subcategories[subcategoryKey];
  if (!subcategory) return [];
  
  return subcategory.entries;
};

export default FREQUENCY_DATABASES;

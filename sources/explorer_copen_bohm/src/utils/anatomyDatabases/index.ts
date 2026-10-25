// Anatomische Datenbanken - Zentraler Export
// Höchst detaillierte anatomische Strukturen basierend auf Terminologia Anatomica (TA2)

import ZNS_DATABASE, { getAllZNSEntries } from './znsDatabase';
import HERZ_KREISLAUF_DATABASE, { getAllHerzKreislaufEntries } from './herzKreislaufDatabase';
import VERDAUUNG_DATABASE, { getAllVerdauungEntries } from './verdauungDatabase';
import BEWEGUNGSAPPARAT_DATABASE, { getAllBewegungsapparatEntries } from './bewegungsapparatDatabase';
import RESPIRATION_DATABASE, { getAllRespirationEntries } from './respirationDatabase';
import UROGENITAL_DATABASE, { getAllUrogenitalEntries } from './urogenitalDatabase';
import ENDOKRINES_DATABASE, { getAllEndokrinesEntries } from './endokrinesDatabase';
import SINNESORGANE_DATABASE, { getAllSinnesorganeEntries } from './sinnesorganeDatabase';
import HAUT_DATABASE, { getAllHautEntries } from './hautDatabase';
import IMMUN_LYMPH_DATABASE, { getAllImmunLymphEntries } from './immunLymphDatabase';
import FASZIEN_DATABASE, { getAllFaszienEntries } from './faszienDatabase';
import PERIPHERES_NERVENSYSTEM_DATABASE, { getAllPeripheresNervensystemEntries } from './peripheresNervensystemDatabase';

// Typ für anatomische Datenbanken
export interface AnatomyDatabase {
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

// Alle verfügbaren anatomischen Datenbanken
export const ANATOMY_DATABASES: { [key: string]: AnatomyDatabase } = {
  zns: ZNS_DATABASE,
  herzKreislauf: HERZ_KREISLAUF_DATABASE,
  verdauung: VERDAUUNG_DATABASE,
  bewegungsapparat: BEWEGUNGSAPPARAT_DATABASE,
  respiration: RESPIRATION_DATABASE,
  urogenital: UROGENITAL_DATABASE,
  endokrines: ENDOKRINES_DATABASE,
  sinnesorgane: SINNESORGANE_DATABASE,
  haut: HAUT_DATABASE,
  immunLymph: IMMUN_LYMPH_DATABASE,
  faszien: FASZIEN_DATABASE,
  peripheresNervensystem: PERIPHERES_NERVENSYSTEM_DATABASE,
};

// Statistik über alle Datenbanken
export const getAnatomyStatistics = () => {
  const stats = Object.entries(ANATOMY_DATABASES).map(([key, db]) => ({
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
  ZNS_DATABASE, getAllZNSEntries,
  HERZ_KREISLAUF_DATABASE, getAllHerzKreislaufEntries,
  VERDAUUNG_DATABASE, getAllVerdauungEntries,
  BEWEGUNGSAPPARAT_DATABASE, getAllBewegungsapparatEntries,
  RESPIRATION_DATABASE, getAllRespirationEntries,
  UROGENITAL_DATABASE, getAllUrogenitalEntries,
  ENDOKRINES_DATABASE, getAllEndokrinesEntries,
  SINNESORGANE_DATABASE, getAllSinnesorganeEntries,
  HAUT_DATABASE, getAllHautEntries,
  IMMUN_LYMPH_DATABASE, getAllImmunLymphEntries,
  FASZIEN_DATABASE, getAllFaszienEntries,
  PERIPHERES_NERVENSYSTEM_DATABASE, getAllPeripheresNervensystemEntries,
};

// Alle Einträge aller Datenbanken
export const getAllAnatomyEntries = (): string[] => {
  return [
    ...getAllZNSEntries(),
    ...getAllHerzKreislaufEntries(),
    ...getAllVerdauungEntries(),
    ...getAllBewegungsapparatEntries(),
    ...getAllRespirationEntries(),
    ...getAllUrogenitalEntries(),
    ...getAllEndokrinesEntries(),
    ...getAllSinnesorganeEntries(),
    ...getAllHautEntries(),
    ...getAllImmunLymphEntries(),
    ...getAllFaszienEntries(),
    ...getAllPeripheresNervensystemEntries(),
  ];
};

// Einträge einer spezifischen Datenbank abrufen
export const getEntriesForDatabase = (databaseKey: string): string[] => {
  switch (databaseKey) {
    case 'zns': return getAllZNSEntries();
    case 'herzKreislauf': return getAllHerzKreislaufEntries();
    case 'verdauung': return getAllVerdauungEntries();
    case 'bewegungsapparat': return getAllBewegungsapparatEntries();
    case 'respiration': return getAllRespirationEntries();
    case 'urogenital': return getAllUrogenitalEntries();
    case 'endokrines': return getAllEndokrinesEntries();
    case 'sinnesorgane': return getAllSinnesorganeEntries();
    case 'haut': return getAllHautEntries();
    case 'immunLymph': return getAllImmunLymphEntries();
    case 'faszien': return getAllFaszienEntries();
    case 'peripheresNervensystem': return getAllPeripheresNervensystemEntries();
    default: return [];
  }
};

// Einträge einer Subkategorie abrufen
export const getEntriesForSubcategory = (databaseKey: string, subcategoryKey: string): string[] => {
  const db = ANATOMY_DATABASES[databaseKey];
  if (!db) return [];
  
  const subcategory = db.subcategories[subcategoryKey];
  if (!subcategory) return [];
  
  return subcategory.entries;
};

export default ANATOMY_DATABASES;
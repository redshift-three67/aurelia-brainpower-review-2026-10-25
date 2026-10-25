/**
 * Klienten-basierte Morphische Feldalgorithmen
 * Integration von Bohm'scher Ordnung, TCM 5-Elemente und persönlicher Signatur
 */

import { calculateCopenRate } from './copenRateGenerator';
import { 
  calculateMorphicField, 
  generateDefaultQuantumStates,
  type MorphicFieldResult,
  type GeometricForm,
  type IntentionType 
} from './morphicFieldEngine';

// ============= Typen =============

export type TCMElement = 'holz' | 'feuer' | 'erde' | 'metall' | 'wasser';
export type Planet = 'sonne' | 'mond' | 'merkur' | 'venus' | 'mars' | 'jupiter' | 'saturn' | 'uranus' | 'neptun' | 'pluto';

export interface FünfElementeProfile {
  holz: number;   // 0-100
  feuer: number;
  erde: number;
  metall: number;
  wasser: number;
}

export interface KlientenDaten {
  // Obligatorisch
  nachname: string;
  vornamen: string[];
  geburtsdatum: Date;
  geburtsort: string;
  
  // Optional
  bildSignatur?: string;
  tcmTyp?: TCMElement;
  geburtsplanet?: Planet;
  fünfElemente?: FünfElementeProfile;
}

export interface BohmIntegration {
  impliziteOrdnung: {
    ahnenfeld: number;
    karmischePotenziale: number;
    ortsbindung: number;
    seelenplan: number;
  };
  holomovement: {
    rate: number;
    phase: number;
    kohärenz: number;
  };
  expliziteOrdnung: {
    symptome: string[];
    resonanzpunkte: number[];
    harmonisierungsbedarf: number;
  };
  gesamtFaktor: number;
}

export interface TCMAnalyse {
  dominantesElement: TCMElement;
  elementVerteilung: FünfElementeProfile;
  shengFaktor: number;
  keFaktor: number;
  meridianEmpfehlungen: MeridianPunkt[];
  frequenzbereich: { min: number; max: number };
  gesamtFaktor: number;
}

export interface MeridianPunkt {
  name: string;
  kürzel: string;
  nummer: number;
  element: TCMElement;
  typ: 'xi-cleft' | 'shu' | 'source' | 'luo';
}

export interface PersönlicheSignatur {
  nachnameRate: number;
  vornamenRates: number[];
  vornamenMittel: number;
  zeitFaktor: number;
  geoFaktor: number;
  bildBonus: number;
  copenSequenz: number[];
  gesamtFaktor: number;
}

export interface KlientenFeldErgebnis extends MorphicFieldResult {
  persönlicheSignatur: PersönlicheSignatur;
  bohmIntegration: BohmIntegration;
  tcmAnalyse: TCMAnalyse;
  klientenWellenfunktion: number;
  empfehlungen: {
    geometrie: GeometricForm;
    intention: IntentionType;
    meridianPunkte: MeridianPunkt[];
    frequenzen: number[];
  };
}

// ============= Konstanten =============

const ELEMENT_FAKTOREN: Record<TCMElement, number> = {
  holz: 1.618,      // φ - Goldener Schnitt
  feuer: 2.236,     // √5
  erde: 1.732,      // √3
  metall: 1.414,    // √2
  wasser: 0.865     // e/π
};

const ELEMENT_FREQUENZEN: Record<TCMElement, { min: number; max: number }> = {
  holz: { min: 3, max: 7 },
  feuer: { min: 8, max: 12 },
  erde: { min: 0, max: 3 },
  metall: { min: 13, max: 30 },
  wasser: { min: 0.5, max: 3 }
};

const ELEMENT_GEOMETRIE: Record<TCMElement, GeometricForm> = {
  holz: 'tetrahedron',
  feuer: 'octahedron',
  erde: 'cube',
  metall: 'icosahedron',
  wasser: 'dodecahedron'
};

const SHENG_ZYKLUS: TCMElement[] = ['holz', 'feuer', 'erde', 'metall', 'wasser'];
const KE_ZYKLUS: Record<TCMElement, TCMElement> = {
  holz: 'erde',
  feuer: 'metall',
  erde: 'wasser',
  metall: 'holz',
  wasser: 'feuer'
};

const MERIDIAN_PUNKTE: MeridianPunkt[] = [
  // Holz
  { name: 'Taichong', kürzel: 'LV', nummer: 3, element: 'holz', typ: 'source' },
  { name: 'Zhongfeng', kürzel: 'LV', nummer: 4, element: 'holz', typ: 'xi-cleft' },
  { name: 'Yanglingquan', kürzel: 'GB', nummer: 34, element: 'holz', typ: 'shu' },
  // Feuer
  { name: 'Shenmen', kürzel: 'HT', nummer: 7, element: 'feuer', typ: 'source' },
  { name: 'Yinxi', kürzel: 'HT', nummer: 6, element: 'feuer', typ: 'xi-cleft' },
  { name: 'Houxi', kürzel: 'SI', nummer: 3, element: 'feuer', typ: 'source' },
  // Erde
  { name: 'Taibai', kürzel: 'SP', nummer: 3, element: 'erde', typ: 'source' },
  { name: 'Diji', kürzel: 'SP', nummer: 8, element: 'erde', typ: 'xi-cleft' },
  { name: 'Zusanli', kürzel: 'ST', nummer: 36, element: 'erde', typ: 'shu' },
  // Metall
  { name: 'Taiyuan', kürzel: 'LU', nummer: 9, element: 'metall', typ: 'source' },
  { name: 'Kongzui', kürzel: 'LU', nummer: 6, element: 'metall', typ: 'xi-cleft' },
  { name: 'Hegu', kürzel: 'LI', nummer: 4, element: 'metall', typ: 'source' },
  // Wasser
  { name: 'Taixi', kürzel: 'KI', nummer: 3, element: 'wasser', typ: 'source' },
  { name: 'Shuiquan', kürzel: 'KI', nummer: 5, element: 'wasser', typ: 'xi-cleft' },
  { name: 'Zhiyin', kürzel: 'BL', nummer: 67, element: 'wasser', typ: 'source' }
];

const PLANET_FAKTOREN: Record<Planet, number> = {
  sonne: 1.0,
  mond: 0.272,
  merkur: 0.055,
  venus: 0.815,
  mars: 0.532,
  jupiter: 11.209,
  saturn: 9.449,
  uranus: 4.007,
  neptun: 3.883,
  pluto: 0.178
};

// ============= Signatur-Berechnung =============

export function berechnePersönlicheSignatur(klient: KlientenDaten): PersönlicheSignatur {
  // Nachnamen-Rate
  const nachnameResult = calculateCopenRate(klient.nachname, 1, 'D', 'latin');
  const nachnameRate = nachnameResult.rate;
  
  // Vornamen-Raten
  const vornamenRates = klient.vornamen.map(v => 
    calculateCopenRate(v, 1, 'D', 'latin').rate
  );
  const vornamenMittel = vornamenRates.reduce((a, b) => a + b, 0) / vornamenRates.length;
  
  // Zeit-Faktor basierend auf Geburtsdatum
  const dayOfYear = getDayOfYear(klient.geburtsdatum);
  const hourOfBirth = klient.geburtsdatum.getHours() || 12; // Default: Mittag
  const zeitFaktor = Math.cos(2 * Math.PI * dayOfYear / 365) * 
                     Math.sin(2 * Math.PI * hourOfBirth / 24) * 0.5 + 0.5;
  
  // Geo-Faktor (vereinfacht durch Orts-Hash)
  const geoFaktor = berechneGeoFaktor(klient.geburtsort);
  
  // Bild-Bonus
  const bildBonus = klient.bildSignatur ? 0.1 : 0;
  
  // Copen-Sequenz aus allen Namen
  const copenSequenz = [nachnameRate, ...vornamenRates];
  
  // Gesamt-Faktor: √(Nachname × Vornamen-Mittel) × Zeit × Geo × (1 + Bild)
  const gesamtFaktor = Math.sqrt(nachnameRate * vornamenMittel) / 1e9 * 
                       (0.5 + zeitFaktor * 0.5) * 
                       (0.5 + geoFaktor * 0.5) * 
                       (1 + bildBonus);
  
  return {
    nachnameRate,
    vornamenRates,
    vornamenMittel,
    zeitFaktor,
    geoFaktor,
    bildBonus,
    copenSequenz,
    gesamtFaktor
  };
}

function getDayOfYear(date: Date): number {
  const start = new Date(date.getFullYear(), 0, 0);
  const diff = date.getTime() - start.getTime();
  const oneDay = 1000 * 60 * 60 * 24;
  return Math.floor(diff / oneDay);
}

function berechneGeoFaktor(ort: string): number {
  // Hash-basierte Berechnung für Geo-Faktor
  let hash = 0;
  for (let i = 0; i < ort.length; i++) {
    const char = ort.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash;
  }
  return Math.abs(Math.sin(hash)) * 0.8 + 0.2;
}

// ============= Bohm-Integration =============

export function berechneBohmIntegration(
  signatur: PersönlicheSignatur,
  klient: KlientenDaten
): BohmIntegration {
  // Implizite Ordnung
  const ahnenfeld = signatur.nachnameRate / 1e10;
  const karmischePotenziale = signatur.zeitFaktor * 0.8 + 0.2;
  const ortsbindung = signatur.geoFaktor;
  const seelenplan = signatur.vornamenMittel / 1e10;
  
  // Holomovement
  const currentTime = Date.now();
  const rate = 7.83; // Schumann-Resonanz
  const phase = (currentTime % (2 * Math.PI * 1000)) / 1000;
  const kohärenz = 1 / (1 + Math.abs(ahnenfeld - seelenplan) * 10);
  
  // Explizite Ordnung
  const resonanzpunkte = signatur.copenSequenz.map(r => r % 1000);
  const harmonisierungsbedarf = 1 - kohärenz;
  
  // Gesamt-Faktor: (Ψ_impl^0.618 × Ψ_expl^0.382) × cos(ωt)
  const psi_impl = ahnenfeld * karmischePotenziale * ortsbindung;
  const psi_expl = seelenplan * signatur.zeitFaktor;
  const gesamtFaktor = Math.pow(psi_impl, 0.618) * Math.pow(psi_expl, 0.382) * 
                       Math.cos(rate * phase) * 1e5;
  
  return {
    impliziteOrdnung: {
      ahnenfeld,
      karmischePotenziale,
      ortsbindung,
      seelenplan
    },
    holomovement: {
      rate,
      phase,
      kohärenz
    },
    expliziteOrdnung: {
      symptome: [],
      resonanzpunkte,
      harmonisierungsbedarf
    },
    gesamtFaktor: Math.max(0.1, Math.min(10, gesamtFaktor))
  };
}

// ============= TCM/5-Elemente Analyse =============

export function berechneTCMAnalyse(klient: KlientenDaten): TCMAnalyse {
  // Element-Profil bestimmen
  let elementVerteilung: FünfElementeProfile;
  
  if (klient.fünfElemente) {
    elementVerteilung = klient.fünfElemente;
  } else if (klient.tcmTyp) {
    elementVerteilung = erstelleElementProfilAusTyp(klient.tcmTyp);
  } else {
    elementVerteilung = berechneElementeAusGeburt(klient.geburtsdatum);
  }
  
  // Dominantes Element
  const dominantesElement = (Object.entries(elementVerteilung) as [TCMElement, number][])
    .sort((a, b) => b[1] - a[1])[0][0];
  
  // Sheng-Faktor (nährendes Element)
  const shengIndex = (SHENG_ZYKLUS.indexOf(dominantesElement) - 1 + 5) % 5;
  const nährendesElement = SHENG_ZYKLUS[shengIndex];
  const shengFaktor = ELEMENT_FAKTOREN[nährendesElement] * 1.272;
  
  // Ke-Faktor (kontrollierendes Element)
  const kontrollierendesElement = Object.entries(KE_ZYKLUS)
    .find(([_, v]) => v === dominantesElement)?.[0] as TCMElement || 'holz';
  const keFaktor = ELEMENT_FAKTOREN[kontrollierendesElement] / 
                   ELEMENT_FAKTOREN[dominantesElement] * 0.786;
  
  // Meridian-Empfehlungen
  const meridianEmpfehlungen = MERIDIAN_PUNKTE.filter(m => 
    m.element === dominantesElement || m.element === nährendesElement
  );
  
  // Frequenzbereich
  const frequenzbereich = ELEMENT_FREQUENZEN[dominantesElement];
  
  // Gesamt-Faktor: E_dom × (1 + Σ_sheng/5 - Σ_ke/5)
  const gesamtFaktor = ELEMENT_FAKTOREN[dominantesElement] * 
                       (1 + shengFaktor / 5 - keFaktor / 5);
  
  return {
    dominantesElement,
    elementVerteilung,
    shengFaktor,
    keFaktor,
    meridianEmpfehlungen,
    frequenzbereich,
    gesamtFaktor
  };
}

function erstelleElementProfilAusTyp(typ: TCMElement): FünfElementeProfile {
  const base = 10;
  const dominant = 50;
  return {
    holz: typ === 'holz' ? dominant : base,
    feuer: typ === 'feuer' ? dominant : base,
    erde: typ === 'erde' ? dominant : base,
    metall: typ === 'metall' ? dominant : base,
    wasser: typ === 'wasser' ? dominant : base
  };
}

function berechneElementeAusGeburt(datum: Date): FünfElementeProfile {
  const monat = datum.getMonth() + 1;
  
  // Jahreszeit-basierte Element-Zuweisung
  if (monat >= 2 && monat <= 4) { // Frühling → Holz
    return { holz: 40, feuer: 25, erde: 15, metall: 10, wasser: 10 };
  } else if (monat >= 5 && monat <= 7) { // Sommer → Feuer
    return { holz: 10, feuer: 40, erde: 25, metall: 15, wasser: 10 };
  } else if (monat === 8) { // Spätsommer → Erde
    return { holz: 15, feuer: 10, erde: 40, metall: 25, wasser: 10 };
  } else if (monat >= 9 && monat <= 10) { // Herbst → Metall
    return { holz: 10, feuer: 15, erde: 10, metall: 40, wasser: 25 };
  } else { // Winter → Wasser
    return { holz: 25, feuer: 10, erde: 15, metall: 10, wasser: 40 };
  }
}

// ============= Haupt-Berechnung =============

export async function berechneKlientenFeld(
  klient: KlientenDaten,
  intention: IntentionType = 'harmonization',
  geometrie?: GeometricForm
): Promise<KlientenFeldErgebnis> {
  // 1. Persönliche Signatur
  const persönlicheSignatur = berechnePersönlicheSignatur(klient);
  
  // 2. Bohm-Integration
  const bohmIntegration = berechneBohmIntegration(persönlicheSignatur, klient);
  
  // 3. TCM-Analyse
  const tcmAnalyse = berechneTCMAnalyse(klient);
  
  // 4. Geometrie bestimmen (falls nicht angegeben)
  const verwendeteGeometrie = geometrie || ELEMENT_GEOMETRIE[tcmAnalyse.dominantesElement];
  
  // 5. Morphisches Feld berechnen
  const feldErgebnis = await calculateMorphicField({
    quantumStates: generateDefaultQuantumStates(5),
    numericalSequence: persönlicheSignatur.copenSequenz,
    geometricForm: verwendeteGeometrie,
    intention,
    useHardwareModulation: true
  });
  
  // 6. Klienten-Wellenfunktion
  const klientenWellenfunktion = feldErgebnis.totalWaveFunction * 
                                  persönlicheSignatur.gesamtFaktor * 
                                  bohmIntegration.gesamtFaktor * 
                                  tcmAnalyse.gesamtFaktor;
  
  // 7. Empfehlungen generieren
  const empfehlungen = generiereEmpfehlungen(tcmAnalyse, bohmIntegration);
  
  return {
    ...feldErgebnis,
    persönlicheSignatur,
    bohmIntegration,
    tcmAnalyse,
    klientenWellenfunktion,
    empfehlungen
  };
}

function generiereEmpfehlungen(
  tcm: TCMAnalyse,
  bohm: BohmIntegration
): KlientenFeldErgebnis['empfehlungen'] {
  // Empfohlene Geometrie basierend auf dominantem Element
  const geometrie = ELEMENT_GEOMETRIE[tcm.dominantesElement];
  
  // Intention basierend auf Harmonisierungsbedarf
  let intention: IntentionType = 'harmonization';
  if (bohm.expliziteOrdnung.harmonisierungsbedarf > 0.7) {
    intention = 'healing';
  } else if (bohm.expliziteOrdnung.harmonisierungsbedarf > 0.5) {
    intention = 'clearing';
  } else if (bohm.expliziteOrdnung.harmonisierungsbedarf > 0.3) {
    intention = 'activation';
  }
  
  // Frequenzen im optimalen Bereich
  const frequenzen = [];
  const { min, max } = tcm.frequenzbereich;
  for (let f = min; f <= max; f += (max - min) / 4) {
    frequenzen.push(Math.round(f * 100) / 100);
  }
  
  return {
    geometrie,
    intention,
    meridianPunkte: tcm.meridianEmpfehlungen.slice(0, 5),
    frequenzen
  };
}

// ============= Export-Helfer =============

export function getElementFaktor(element: TCMElement): number {
  return ELEMENT_FAKTOREN[element];
}

export function getElementGeometrie(element: TCMElement): GeometricForm {
  return ELEMENT_GEOMETRIE[element];
}

export function getElementFrequenzen(element: TCMElement): { min: number; max: number } {
  return ELEMENT_FREQUENZEN[element];
}

export function getAllMeridianPunkte(): MeridianPunkt[] {
  return MERIDIAN_PUNKTE;
}

export function getMeridianPunkteByElement(element: TCMElement): MeridianPunkt[] {
  return MERIDIAN_PUNKTE.filter(m => m.element === element);
}

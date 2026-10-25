/**
 * Meridian-Diagnose Hook
 * Analysiert Client-Vektoren und identifiziert unausgeglichene Meridiane
 * Nutzt die vollständige WHO-409-Punkte-Datenbank
 */
import { useState, useCallback } from 'react';
import { toast } from 'sonner';
import type { VectorAnalysis } from '@/services/feldengine';
import {
  getCompletePointsByMeridian,
  COMPLETE_DATABASE_STATS
} from '@/utils/meridianPoints';

// TCM Elemente mit ihren Zuordnungen
const ELEMENT_MERIDIAN_MAP = {
  wood: {
    yin: 'LR', yang: 'GB',
    emotions: ['anger', 'frustration', 'resentment'],
    physical: ['eyes', 'tendons', 'nails'],
    season: 'spring'
  },
  fire: {
    yin: 'HT', yang: 'SI',
    emotions: ['joy', 'anxiety', 'mania'],
    physical: ['tongue', 'blood vessels', 'complexion'],
    season: 'summer'
  },
  fire_ministerial: {
    yin: 'PC', yang: 'TE',
    emotions: ['elation', 'shock'],
    physical: ['circulation', 'hormones'],
    season: 'summer'
  },
  earth: {
    yin: 'SP', yang: 'ST',
    emotions: ['worry', 'pensiveness', 'overthinking'],
    physical: ['muscles', 'mouth', 'lips'],
    season: 'late_summer'
  },
  metal: {
    yin: 'LU', yang: 'LI',
    emotions: ['grief', 'sadness', 'letting_go'],
    physical: ['skin', 'nose', 'body_hair'],
    season: 'autumn'
  },
  water: {
    yin: 'KI', yang: 'BL',
    emotions: ['fear', 'willpower', 'wisdom'],
    physical: ['bones', 'ears', 'head_hair'],
    season: 'winter'
  },
};

export interface MeridianImbalance {
  meridianId: string;
  meridianName: string;
  element: string;
  yinYang: 'yin' | 'yang';
  imbalanceScore: number;
  imbalanceType: 'excess' | 'deficiency' | 'stagnation';
  affectedOrgan: string;
  recommendedPoints: string[];
  frequency: number;
}

export interface DiagnosisResult {
  imbalances: MeridianImbalance[];
  primaryElement: string;
  controllingElement: string;
  supportingElement: string;
  overallPattern: string;
  aiRecommendation?: string;
}

/**
 * Generiert dynamisch Meridian-Daten aus der WHO-Datenbank
 * Nutzt die tatsächlichen Frequenzen und Punkttypen aus der vollständigen Datenbank
 */
const getMeridianDataFromDatabase = () => {
  const meridianConfigs: Record<string, {
    name: string;
    organ: string;
    element: string;
    yinYang: 'yin' | 'yang';
  }> = {
    LU: { name: 'Lungen-Meridian', organ: 'Lunge', element: 'metal', yinYang: 'yin' },
    LI: { name: 'Dickdarm-Meridian', organ: 'Dickdarm', element: 'metal', yinYang: 'yang' },
    ST: { name: 'Magen-Meridian', organ: 'Magen', element: 'earth', yinYang: 'yang' },
    SP: { name: 'Milz-Meridian', organ: 'Milz', element: 'earth', yinYang: 'yin' },
    HT: { name: 'Herz-Meridian', organ: 'Herz', element: 'fire', yinYang: 'yin' },
    SI: { name: 'Dünndarm-Meridian', organ: 'Dünndarm', element: 'fire', yinYang: 'yang' },
    BL: { name: 'Blasen-Meridian', organ: 'Blase', element: 'water', yinYang: 'yang' },
    KI: { name: 'Nieren-Meridian', organ: 'Niere', element: 'water', yinYang: 'yin' },
    PC: { name: 'Perikard-Meridian', organ: 'Perikard', element: 'fire', yinYang: 'yin' },
    TE: { name: 'Dreifacher Erwärmer', organ: 'San Jiao', element: 'fire', yinYang: 'yang' },
    GB: { name: 'Gallenblasen-Meridian', organ: 'Gallenblase', element: 'wood', yinYang: 'yang' },
    LR: { name: 'Leber-Meridian', organ: 'Leber', element: 'wood', yinYang: 'yin' },
  };

  const meridianData: Record<string, {
    name: string;
    organ: string;
    element: string;
    yinYang: 'yin' | 'yang';
    frequency: number;
    keyPoints: string[];
    totalPoints: number;
  }> = {};

  Object.entries(meridianConfigs).forEach(([id, config]) => {
    const points = getCompletePointsByMeridian(id);

    // Berechne Durchschnittsfrequenz aus allen Punkten
    const avgFrequency = points.length > 0
      ? points.reduce((sum, p) => sum + p.frequency, 0) / points.length
      : 100;

    // Finde die wichtigsten Punkte (Yuan-Source, He-Sea, Shu-Stream)
    const keyPoints = points
      .filter(p => p.pointTypes?.some(t =>
        ['yuan_source', 'he_sea', 'shu_stream', 'luo_connecting'].includes(t)
      ))
      .slice(0, 3)
      .map(p => p.id);

    // Fallback auf erste 3 Punkte
    const finalKeyPoints = keyPoints.length > 0
      ? keyPoints
      : points.slice(0, 3).map(p => p.id);

    meridianData[id] = {
      ...config,
      frequency: Math.round(avgFrequency * 10) / 10,
      keyPoints: finalKeyPoints,
      totalPoints: points.length,
    };
  });

  return meridianData;
};

// Initialisiere Meridian-Daten aus der WHO-Datenbank
const MERIDIAN_DATA = getMeridianDataFromDatabase();

// 8 Außerordentliche Gefäße (Qi Jing Ba Mai)
export const EXTRAORDINARY_VESSELS: Record<string, {
  name: string;
  nameChinese: string;
  description: string;
  openingPoint: string;
  coupledPoint: string;
  frequency: number;
  keyPoints: string[];
  function: string;
  indications: string[];
}> = {
  DU: {
    name: 'Du Mai (Lenkergefäß)',
    nameChinese: '督脈',
    description: 'Meer des Yang - verläuft entlang der Wirbelsäule zum Kopf',
    openingPoint: 'SI3',
    coupledPoint: 'BL62',
    frequency: 136.1,
    keyPoints: ['DU4', 'DU14', 'DU20', 'DU26'],
    function: 'Regiert alle Yang-Meridiane, stärkt Wirbelsäule und Gehirn',
    indications: ['Rückenschmerzen', 'Epilepsie', 'mentale Störungen', 'Steifheit der Wirbelsäule'],
  },
  REN: {
    name: 'Ren Mai (Konzeptionsgefäß)',
    nameChinese: '任脈',
    description: 'Meer des Yin - verläuft entlang der vorderen Mittellinie',
    openingPoint: 'LU7',
    coupledPoint: 'KI6',
    frequency: 141.3,
    keyPoints: ['REN4', 'REN6', 'REN12', 'REN17'],
    function: 'Regiert alle Yin-Meridiane, nährt Yin und Blut',
    indications: ['Menstruationsstörungen', 'Unfruchtbarkeit', 'Hernie', 'Atemnot'],
  },
  CHONG: {
    name: 'Chong Mai (Durchdringungsgefäß)',
    nameChinese: '衝脈',
    description: 'Meer des Blutes - verbindet oberes und unteres Dantian',
    openingPoint: 'SP4',
    coupledPoint: 'PC6',
    frequency: 144.7,
    keyPoints: ['REN1', 'ST30', 'KI11-21'],
    function: 'Reguliert Qi und Blut, Verbindung zwischen Vor- und Nachgeburt',
    indications: ['Blutmangel', 'unregelmäßige Menstruation', 'Herzbeschwerden', 'Brustschmerzen'],
  },
  DAI: {
    name: 'Dai Mai (Gürtelgefäß)',
    nameChinese: '帶脈',
    description: 'Einziger horizontal verlaufender Meridian um die Taille',
    openingPoint: 'GB41',
    coupledPoint: 'TE5',
    frequency: 147.9,
    keyPoints: ['GB26', 'GB27', 'GB28', 'LR13'],
    function: 'Bindet alle vertikalen Meridiane, reguliert Unterleib',
    indications: ['Leukorrhoe', 'Prolaps', 'Hüftschmerzen', 'Schwäche der Beine'],
  },
  YANGQIAO: {
    name: 'Yang Qiao Mai (Yang-Fersengefäß)',
    nameChinese: '陽蹻脈',
    description: 'Reguliert Yang der unteren Extremität und Augen',
    openingPoint: 'BL62',
    coupledPoint: 'SI3',
    frequency: 152.8,
    keyPoints: ['BL62', 'BL59', 'GB29', 'BL1'],
    function: 'Kontrolliert Schlaf-Wach-Rhythmus, stärkt Yang',
    indications: ['Schlaflosigkeit', 'Epilepsie', 'Augenschmerzen', 'laterale Beinschmerzen'],
  },
  YINQIAO: {
    name: 'Yin Qiao Mai (Yin-Fersengefäß)',
    nameChinese: '陰蹻脈',
    description: 'Reguliert Yin der unteren Extremität',
    openingPoint: 'KI6',
    coupledPoint: 'LU7',
    frequency: 158.4,
    keyPoints: ['KI6', 'KI8', 'ST12', 'BL1'],
    function: 'Fördert Schlaf, nährt Yin, befeuchtet Augen',
    indications: ['Hypersomnie', 'trockene Augen', 'mediale Beinschmerzen', 'Harnprobleme'],
  },
  YANGWEI: {
    name: 'Yang Wei Mai (Yang-Verbindungsgefäß)',
    nameChinese: '陽維脈',
    description: 'Verbindet alle Yang-Meridiane, reguliert Außen',
    openingPoint: 'TE5',
    coupledPoint: 'GB41',
    frequency: 164.2,
    keyPoints: ['TE5', 'GB35', 'SI10', 'GB20', 'DU16'],
    function: 'Verteidigt gegen äußere pathogene Faktoren',
    indications: ['Fieber', 'Schüttelfrost', 'Kopfschmerzen', 'Nackensteifigkeit'],
  },
  YINWEI: {
    name: 'Yin Wei Mai (Yin-Verbindungsgefäß)',
    nameChinese: '陰維脈',
    description: 'Verbindet alle Yin-Meridiane, reguliert Innen',
    openingPoint: 'PC6',
    coupledPoint: 'SP4',
    frequency: 170.6,
    keyPoints: ['PC6', 'KI9', 'SP13-16', 'REN22-23'],
    function: 'Reguliert Herz und Brust, beruhigt den Geist',
    indications: ['Herzschmerzen', 'Brustbeklemmung', 'Magenschmerzen', 'Angst'],
  },
};

// Wu Xing Zyklen
const GENERATION_CYCLE = ['wood', 'fire', 'earth', 'metal', 'water']; // Sheng-Zyklus
const CONTROL_CYCLE = { // Ke-Zyklus
  wood: 'earth',
  fire: 'metal',
  earth: 'water',
  metal: 'wood',
  water: 'fire',
};

export function useMeridianDiagnosis() {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [diagnosisResult, setDiagnosisResult] = useState<DiagnosisResult | null>(null);
  const [aiRecommendation, setAiRecommendation] = useState<string>('');
  const [isLoadingAI, setIsLoadingAI] = useState(false);

  /**
   * Berechnet Meridian-Imbalancen basierend auf dem Client-Vektor
   */
  const calculateImbalances = useCallback((vectorAnalysis: VectorAnalysis): MeridianImbalance[] => {
    const imbalances: MeridianImbalance[] = [];
    const dimensions = vectorAnalysis.clientVector.dimensions;

    // Extrahiere Dimensionswerte
    const physical = dimensions[0] || 0;
    const emotional = dimensions[1] || 0;
    const stress = dimensions[2] || 0;
    const energy = dimensions[3] || 0;
    const mental = dimensions[4] || 0;

    // Analysiere jeden Meridian basierend auf den Dimensionen
    Object.entries(MERIDIAN_DATA).forEach(([id, data]) => {
      let score = 0;
      let type: 'excess' | 'deficiency' | 'stagnation' = 'stagnation';

      switch (data.element) {
        case 'wood':
          // Holz: beeinflusst durch Stress und unterdrückte Emotionen
          score = Math.abs(stress) * 0.4 + Math.abs(emotional) * 0.3 + Math.abs(physical) * 0.2;
          type = stress > 0.3 ? 'excess' : (emotional < -0.3 ? 'stagnation' : 'deficiency');
          break;

        case 'fire':
        case 'fire_ministerial':
          // Feuer: beeinflusst durch emotionale Zustände und Energie
          score = Math.abs(emotional) * 0.4 + Math.abs(energy) * 0.3 + Math.abs(mental) * 0.2;
          type = emotional > 0.3 ? 'excess' : (energy < -0.3 ? 'deficiency' : 'stagnation');
          break;

        case 'earth':
          // Erde: beeinflusst durch mentale Aktivität und Verdauung
          score = Math.abs(mental) * 0.4 + Math.abs(physical) * 0.3 + Math.abs(stress) * 0.2;
          type = mental > 0.3 ? 'excess' : (physical < -0.3 ? 'deficiency' : 'stagnation');
          break;

        case 'metal':
          // Metall: beeinflusst durch Trauer, Loslassen, Atmung
          score = Math.abs(emotional) * 0.3 + Math.abs(physical) * 0.4 + Math.abs(energy) * 0.2;
          type = physical > 0.2 && emotional < 0 ? 'deficiency' : (stress > 0.3 ? 'stagnation' : 'excess');
          break;

        case 'water':
          // Wasser: beeinflusst durch Angst, Willenskraft, Essenz
          score = Math.abs(stress) * 0.3 + Math.abs(energy) * 0.4 + Math.abs(mental) * 0.2;
          type = energy < -0.3 ? 'deficiency' : (stress > 0.4 ? 'excess' : 'stagnation');
          break;
      }

      // Adjustiere Score basierend auf Bifurkationsrisiko
      const attractorFactor = vectorAnalysis.attractorState.bifurcationRisk * 0.3;
      score = Math.min(1, score + attractorFactor);

      // Nur signifikante Imbalancen hinzufügen
      if (score > 0.2) {
        imbalances.push({
          meridianId: id,
          meridianName: data.name,
          element: data.element,
          yinYang: data.yinYang,
          imbalanceScore: score,
          imbalanceType: type,
          affectedOrgan: data.organ,
          recommendedPoints: data.keyPoints,
          frequency: data.frequency,
        });
      }
    });

    // Sortiere nach Score (höchste zuerst)
    return imbalances.sort((a, b) => b.imbalanceScore - a.imbalanceScore);
  }, []);

  /**
   * Identifiziert das primäre Element-Muster
   */
  const identifyElementPattern = useCallback((imbalances: MeridianImbalance[]): {
    primary: string;
    controlling: string;
    supporting: string;
    pattern: string;
  } => {
    // Zähle Element-Häufigkeiten gewichtet nach Score
    const elementScores: Record<string, number> = {};

    imbalances.forEach(imb => {
      const elem = imb.element === 'fire_ministerial' ? 'fire' : imb.element;
      elementScores[elem] = (elementScores[elem] || 0) + imb.imbalanceScore;
    });

    // Finde primäres Element
    const sortedElements = Object.entries(elementScores)
      .sort(([, a], [, b]) => b - a);

    const primary = sortedElements[0]?.[0] || 'earth';
    const primaryIndex = GENERATION_CYCLE.indexOf(primary);

    // Kontrollierendes Element (Ke-Zyklus)
    const controlling = CONTROL_CYCLE[primary as keyof typeof CONTROL_CYCLE] || 'water';

    // Unterstützendes Element (Sheng-Zyklus - vorheriges Element)
    const supportingIndex = (primaryIndex - 1 + 5) % 5;
    const supporting = GENERATION_CYCLE[supportingIndex];

    // Bestimme Muster
    let pattern = 'Gemischtes Muster';
    const topImbalance = imbalances[0];
    if (topImbalance) {
      if (topImbalance.imbalanceType === 'excess') {
        pattern = `${primary.charAt(0).toUpperCase() + primary.slice(1)}-Überschuss mit ${controlling}-Kontrolle`;
      } else if (topImbalance.imbalanceType === 'deficiency') {
        pattern = `${primary.charAt(0).toUpperCase() + primary.slice(1)}-Mangel, ${supporting} stärken`;
      } else {
        pattern = `${primary.charAt(0).toUpperCase() + primary.slice(1)}-Stagnation, Qi bewegen`;
      }
    }

    return { primary, controlling, supporting, pattern };
  }, []);

  /**
   * Holt KI-basierte Behandlungsempfehlungen
   */
  const fetchAIRecommendation = useCallback(async (
    vectorAnalysis: VectorAnalysis,
    imbalances: MeridianImbalance[]
  ) => {
    setIsLoadingAI(true);

    try {
      const clientVector = {
        physical: vectorAnalysis.clientVector.dimensions[0] || 0,
        emotional: vectorAnalysis.clientVector.dimensions[1] || 0,
        stress: vectorAnalysis.clientVector.dimensions[2] || 0,
        energy: vectorAnalysis.clientVector.dimensions[3] || 0,
        mental: vectorAnalysis.clientVector.dimensions[4] || 0,
      };

      const response = await fetch(
        `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/meridian-diagnosis`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY}`,
          },
          body: JSON.stringify({ clientVector, imbalances }),
        }
      );

      if (!response.ok) {
        if (response.status === 429) {
          toast.error('Rate-Limit erreicht. Bitte warten Sie einen Moment.');
          return;
        }
        if (response.status === 402) {
          toast.error('KI-Guthaben erschöpft.');
          return;
        }
        throw new Error('Failed to fetch AI recommendation');
      }

      // Stream verarbeiten
      const reader = response.body?.getReader();
      if (!reader) throw new Error('No response body');

      const decoder = new TextDecoder();
      let fullText = '';
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        let newlineIndex: number;
        while ((newlineIndex = buffer.indexOf('\n')) !== -1) {
          let line = buffer.slice(0, newlineIndex);
          buffer = buffer.slice(newlineIndex + 1);

          if (line.endsWith('\r')) line = line.slice(0, -1);
          if (line.startsWith(':') || line.trim() === '') continue;
          if (!line.startsWith('data: ')) continue;

          const jsonStr = line.slice(6).trim();
          if (jsonStr === '[DONE]') break;

          try {
            const parsed = JSON.parse(jsonStr);
            const content = parsed.choices?.[0]?.delta?.content as string | undefined;
            if (content) {
              fullText += content;
              setAiRecommendation(fullText);
            }
          } catch {
            buffer = line + '\n' + buffer;
            break;
          }
        }
      }

    } catch (error) {
      console.error('AI recommendation error:', error);
      toast.error('Fehler beim Laden der KI-Empfehlung');
    } finally {
      setIsLoadingAI(false);
    }
  }, []);

  /**
   * Führt die vollständige Diagnose durch
   */
  const analyzeMeridians = useCallback(async (vectorAnalysis: VectorAnalysis) => {
    setIsAnalyzing(true);
    setAiRecommendation('');

    try {
      // Berechne Imbalancen
      const imbalances = calculateImbalances(vectorAnalysis);

      // Identifiziere Element-Muster
      const { primary, controlling, supporting, pattern } = identifyElementPattern(imbalances);

      const result: DiagnosisResult = {
        imbalances,
        primaryElement: primary,
        controllingElement: controlling,
        supportingElement: supporting,
        overallPattern: pattern,
      };

      setDiagnosisResult(result);

      // Hole KI-Empfehlung
      await fetchAIRecommendation(vectorAnalysis, imbalances);

      return result;
    } catch (error) {
      console.error('Meridian analysis error:', error);
      toast.error('Fehler bei der Meridian-Analyse');
      return null;
    } finally {
      setIsAnalyzing(false);
    }
  }, [calculateImbalances, identifyElementPattern, fetchAIRecommendation]);

  return {
    isAnalyzing,
    isLoadingAI,
    diagnosisResult,
    aiRecommendation,
    analyzeMeridians,
    calculateImbalances,
  };
}

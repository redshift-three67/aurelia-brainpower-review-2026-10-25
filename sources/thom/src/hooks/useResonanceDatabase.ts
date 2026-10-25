/**
 * Hook für Zugriff auf Resonanz-Datenbank (Word Energies & Anatomy Points)
 */
import { useState, useCallback } from 'react';
import { supabase } from '@/integrations/supabase/client';

// Types
export interface WordEnergy {
  id: string;
  word: string;
  language: string;
  frequency: number;
  amplitude: number;
  category: 'positive' | 'negative' | 'neutral';
  organSystem: string | null;
  chakra: string | null;
  meridian: string | null;
  emotionalQuality: string | null;
  description: string | null;
}

export interface AnatomyResonancePoint {
  id: string;
  name: string;
  nameLatin: string | null;
  bodyRegion: string;
  position: { x: number; y: number; z: number };
  primaryFrequency: number;
  harmonicFrequencies: number[];
  organAssociations: string[];
  meridianAssociations: string[];
  emotionalAssociations: string[];
  description: string | null;
}

export interface ResonanceAnalysisResult {
  matchedWords: Array<{
    word: WordEnergy;
    resonanceScore: number;
  }>;
  matchedAnatomyPoints: Array<{
    point: AnatomyResonancePoint;
    resonanceScore: number;
  }>;
  overallResonance: number;
  recommendedFrequencies: number[];
}

export function useResonanceDatabase() {
  const [isLoading, setIsLoading] = useState(false);
  const [wordEnergies, setWordEnergies] = useState<WordEnergy[]>([]);
  const [anatomyPoints, setAnatomyPoints] = useState<AnatomyResonancePoint[]>([]);

  // Word Energies laden
  const loadWordEnergies = useCallback(async (category?: string) => {
    setIsLoading(true);
    try {
      let query = supabase.from('word_energies').select('*');
      
      if (category) {
        query = query.eq('category', category);
      }

      const { data, error } = await query;
      
      if (error) throw error;

      const mapped: WordEnergy[] = (data || []).map(w => ({
        id: w.id,
        word: w.word,
        language: w.language || 'de',
        frequency: w.frequency,
        amplitude: w.amplitude || 0.5,
        category: w.category as 'positive' | 'negative' | 'neutral',
        organSystem: w.organ_system,
        chakra: w.chakra,
        meridian: w.meridian,
        emotionalQuality: w.emotional_quality,
        description: w.description,
      }));

      setWordEnergies(mapped);
      return mapped;
    } catch (error) {
      console.error('Error loading word energies:', error);
      return [];
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Anatomy Points laden
  const loadAnatomyPoints = useCallback(async (bodyRegion?: string) => {
    setIsLoading(true);
    try {
      let query = supabase.from('anatomy_resonance_points').select('*');
      
      if (bodyRegion) {
        query = query.eq('body_region', bodyRegion);
      }

      const { data, error } = await query;
      
      if (error) throw error;

      const mapped: AnatomyResonancePoint[] = (data || []).map(p => ({
        id: p.id,
        name: p.name,
        nameLatin: p.name_latin,
        bodyRegion: p.body_region,
        position: { x: p.x_position, y: p.y_position, z: p.z_position },
        primaryFrequency: p.primary_frequency,
        harmonicFrequencies: p.harmonic_frequencies || [],
        organAssociations: p.organ_associations || [],
        meridianAssociations: p.meridian_associations || [],
        emotionalAssociations: p.emotional_associations || [],
        description: p.description,
      }));

      setAnatomyPoints(mapped);
      return mapped;
    } catch (error) {
      console.error('Error loading anatomy points:', error);
      return [];
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Resonanz-Analyse durchführen
  const analyzeResonance = useCallback(async (
    clientVector: number[],
    targetFrequency?: number
  ): Promise<ResonanceAnalysisResult> => {
    // Lade Daten falls nicht vorhanden
    const words = wordEnergies.length > 0 ? wordEnergies : await loadWordEnergies();
    const points = anatomyPoints.length > 0 ? anatomyPoints : await loadAnatomyPoints();

    // Berechne Resonanz-Scores für Words
    const matchedWords = words.map(word => {
      // Resonanz-Score basierend auf Vektor-Nähe und Frequenz-Harmonie
      const energyMatch = Math.abs(clientVector[3] || 0); // Energy dimension
      const emotionalMatch = Math.abs(clientVector[1] || 0); // Emotional dimension
      
      let resonanceScore = 0;
      
      if (word.category === 'positive') {
        resonanceScore = 0.5 + (1 - energyMatch) * 0.3 + (1 - emotionalMatch) * 0.2;
      } else {
        resonanceScore = 0.5 + energyMatch * 0.3 + emotionalMatch * 0.2;
      }

      // Frequenz-Harmonik prüfen
      if (targetFrequency) {
        const harmonic = word.frequency / targetFrequency;
        const isHarmonic = Math.abs(harmonic - Math.round(harmonic)) < 0.1;
        if (isHarmonic) resonanceScore += 0.2;
      }

      return { word, resonanceScore: Math.min(1, resonanceScore) };
    }).sort((a, b) => b.resonanceScore - a.resonanceScore);

    // Berechne Resonanz-Scores für Anatomy Points
    const matchedAnatomyPoints = points.map(point => {
      // Score basierend auf Vektor-Dimensionen und Organ-Zuordnungen
      const physicalMatch = Math.abs(clientVector[0] || 0);
      const stressMatch = Math.abs(clientVector[4] || 0);
      
      let resonanceScore = 0.5;

      // Stress-korrelierte Organe
      if (stressMatch > 0.3 && point.organAssociations.includes('adrenal')) {
        resonanceScore += 0.3;
      }

      // Energetisch relevante Organe
      if (point.organAssociations.includes('heart') || point.organAssociations.includes('thymus')) {
        resonanceScore += 0.2 * (1 - physicalMatch);
      }

      return { point, resonanceScore: Math.min(1, resonanceScore) };
    }).sort((a, b) => b.resonanceScore - a.resonanceScore);

    // Empfohlene Frequenzen extrahieren
    const recommendedFrequencies = [
      ...matchedWords.slice(0, 3).map(w => w.word.frequency),
      ...matchedAnatomyPoints.slice(0, 3).map(p => p.point.primaryFrequency),
    ].filter((freq, i, arr) => arr.indexOf(freq) === i);

    // Gesamt-Resonanz berechnen
    const overallResonance = (
      matchedWords.slice(0, 5).reduce((sum, w) => sum + w.resonanceScore, 0) / 5 +
      matchedAnatomyPoints.slice(0, 5).reduce((sum, p) => sum + p.resonanceScore, 0) / 5
    ) / 2;

    return {
      matchedWords: matchedWords.slice(0, 10),
      matchedAnatomyPoints: matchedAnatomyPoints.slice(0, 10),
      overallResonance,
      recommendedFrequencies: recommendedFrequencies.slice(0, 5),
    };
  }, [wordEnergies, anatomyPoints, loadWordEnergies, loadAnatomyPoints]);

  // Word Energy suchen
  const searchWordEnergy = useCallback(async (searchTerm: string) => {
    const { data, error } = await supabase
      .from('word_energies')
      .select('*')
      .ilike('word', `%${searchTerm}%`)
      .limit(10);

    if (error) {
      console.error('Search error:', error);
      return [];
    }

    return data || [];
  }, []);

  return {
    isLoading,
    wordEnergies,
    anatomyPoints,
    loadWordEnergies,
    loadAnatomyPoints,
    analyzeResonance,
    searchWordEnergy,
  };
}

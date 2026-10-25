// Hybrid-Ansatz: LLM für Interpretationen und Vorschläge
// Code für präzise Berechnungen, LLM für semantische Analyse

export interface AnalysisInterpretation {
  summary: string;
  insights: string[];
  recommendations: string[];
}

/**
 * Nutzt LLM (Ollama) für semantische Interpretation der Analyse-Ergebnisse
 */
export async function interpretAnalysisResults(
  results: Array<{
    word: string;
    resonanceScore: number;
    highestLevel: number;
    testedPotency: string;
  }>,
  patientName?: string
): Promise<AnalysisInterpretation> {
  // Bereite Kontext für LLM vor
  const topResults = results.slice(0, 10);
  const context = `
Analysiere folgende Resonanz-Ergebnisse${patientName ? ` für ${patientName}` : ''}:

${topResults.map((r, i) => 
  `${i + 1}. "${r.word}" - Resonanz: ${r.resonanceScore.toFixed(1)}%, Ebene: ${r.highestLevel}, Potenz: ${r.testedPotency}`
).join('\n')}

Ebenen-Bedeutung:
- Ebenen 1-2: Physische Ebene (Partikel, Struktur)
- Ebenen 3-4: Ätherische Ebene (Prana, Meridiane)
- Ebenen 5-6: Astrale Ebene (Emotionen, Gedanken)
- Ebenen 7-8: Mentale Ebene (Zeit, Konstrukte)
- Ebenen 9-10: Kausale Ebene (Blaupausen, Alchemie)
- Ebenen 11-12: Atmische Ebene (Identität, Liebe)

Erstelle eine kurze Zusammenfassung (max 3 Sätze), 3-5 wichtige Erkenntnisse und 3-5 Empfehlungen für die Harmonisierung.
`;

  try {
    // Nutze Ollama für Textgenerierung
    const response = await fetch('http://localhost:11434/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: 'llama2',
        prompt: context,
        stream: false
      })
    });

    if (!response.ok) throw new Error('Ollama nicht verfügbar');
    
    const data = await response.json();
    const text = data.response || '';
    
    // Parse LLM Response (einfaches Parsing)
    const lines = text.split('\n').filter((l: string) => l.trim());
    
    return {
      summary: lines[0] || 'Analyse abgeschlossen',
      insights: lines.slice(1, 6).filter((l: string) => l.length > 0),
      recommendations: lines.slice(6, 11).filter((l: string) => l.length > 0)
    };
  } catch (error) {
    console.error('LLM Interpretation fehlgeschlagen:', error);
    
    // Fallback: Regel-basierte Interpretation
    const avgLevel = results.reduce((sum, r) => sum + r.highestLevel, 0) / results.length;
    const topResonance = results[0];
    
    return {
      summary: `${results.length} Einträge analysiert. Durchschnittliche Ebene: ${avgLevel.toFixed(1)}`,
      insights: [
        `Höchste Resonanz: "${topResonance.word}" (${topResonance.resonanceScore.toFixed(1)}%)`,
        `Dominante Ebene: ${topResonance.highestLevel} (${getLevelName(topResonance.highestLevel)})`,
        `${results.filter(r => r.highestLevel >= 9).length} Einträge auf kausaler/atmischer Ebene`
      ],
      recommendations: [
        'Konzentriere dich auf die Top-5 Resonanzen für maximale Wirkung',
        'Berücksichtige die dominante Ebene bei der Harmonisierung',
        'Prüfe Wechselwirkungen zwischen den Einträgen'
      ]
    };
  }
}

function getLevelName(level: number): string {
  const names: Record<number, string> = {
    1: 'Physical Particles',
    2: 'Physical Structure',
    3: 'Etheric Prana',
    4: 'Etheric Meridians',
    5: 'Astral Emotions',
    6: 'Astral Thoughts',
    7: 'Mental Time',
    8: 'Mental Constructs',
    9: 'Causal Blueprints',
    10: 'Causal Alchemy',
    11: 'Atmic Identity',
    12: 'Atmic Love'
  };
  return names[level] || 'Unknown';
}

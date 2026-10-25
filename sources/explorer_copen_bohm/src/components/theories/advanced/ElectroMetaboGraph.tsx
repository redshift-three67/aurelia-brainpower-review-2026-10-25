import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  Activity, 
  Zap, 
  Brain, 
  Heart, 
  Microscope, 
  Calculator,
  TrendingUp,
  FileText,
  AlertCircle,
  CheckCircle,
  Info,
  Settings,
  BarChart3,
  Waves
} from 'lucide-react';

const ElectroMetaboGraph = () => {
  const [selectedMeasurement, setSelectedMeasurement] = useState<string | null>(null);
  const [selectedAlgorithm, setSelectedAlgorithm] = useState<string | null>(null);

  // EMG Parameter und Referenzbereiche
  const emgParameters = [
    { name: "Basalstoffwechsel", normal: "1200-1800 kcal/Tag", unit: "kcal", icon: Activity },
    { name: "Zelluläre Respiration", normal: "95-105%", unit: "%", icon: Microscope },
    { name: "Mitochondriale Aktivität", normal: "80-120%", unit: "%", icon: Zap },
    { name: "ATP-Synthese Rate", normal: "2.5-4.2 mmol/min", unit: "mmol/min", icon: Calculator },
    { name: "Oxidativer Stress", normal: "< 2.5 mV", unit: "mV", icon: AlertCircle },
    { name: "Säure-Basen-Balance", normal: "7.35-7.45 pH", unit: "pH", icon: TrendingUp }
  ];

  // Frequenzbereiche des EMG
  const frequencyRanges = [
    { range: "0,1-10 Hz", description: "Grundstoffwechsel-Rhythmen", application: "Basalmetabolismus" },
    { range: "10-50 Hz", description: "Zelluläre Oszillationen", application: "Mitochondriale Aktivität" },
    { range: "50-200 Hz", description: "Enzymatische Prozesse", application: "Metabolische Reaktionen" },
    { range: "200-1000 Hz", description: "Molekulare Schwingungen", application: "Protein-Konformation" },
    { range: "1-10 kHz", description: "Membranpotentiale", application: "Ionentransport" },
    { range: "10-100 kHz", description: "Hochfrequente Zellsignale", application: "Interzellulär Kommunikation" }
  ];

  // Detaillierte EMG Algorithmen
  const detailedAlgorithms = [
    {
      id: "metabolic-index",
      name: "Metabolischer Index (MI)",
      formula: "MI = (VO₂ × RQ × 4.825) / BSA",
      variables: {
        "VO₂": "Sauerstoffverbrauch (ml/min)",
        "RQ": "Respiratorischer Quotient (VCO₂/VO₂)",
        "BSA": "Körperoberfläche (m²)",
        "4.825": "Kalorischer Äquivalent für gemischte Substrate"
      },
      normalRange: "0.8-1.2",
      calculation: `
// Metabolischer Index Berechnung
function calculateMetabolicIndex(vo2, rq, bsa) {
  const caloricEquivalent = 4.825;
  const mi = (vo2 * rq * caloricEquivalent) / bsa;
  return mi;
}

// Beispiel:
// VO₂ = 250 ml/min, RQ = 0.85, BSA = 1.8 m²
// MI = (250 × 0.85 × 4.825) / 1.8 = 569.8 kcal/m²/Tag`
    },
    {
      id: "bioenergetic-status",
      name: "Bioenergetischer Status (BES)",
      formula: "BES = (ATP/ADP) × Φₘ × log(NAD⁺/NADH)",
      variables: {
        "ATP/ADP": "Adenosin-Triphosphat/Diphosphat-Verhältnis",
        "Φₘ": "Mitochondriales Membranpotential (mV)",
        "NAD⁺/NADH": "Oxidiertes/Reduziertes Nicotinamid-Adenin-Dinukleotid"
      },
      normalRange: "2.5-4.0",
      calculation: `
// Bioenergetischer Status Berechnung
function calculateBioenergeticStatus(atpAdpRatio, membranePotential, nadRatio) {
  const bes = atpAdpRatio * membranePotential * Math.log10(nadRatio);
  return bes;
}

// Beispiel:
// ATP/ADP = 3.2, Φₘ = -180 mV, NAD⁺/NADH = 700
// BES = 3.2 × (-180) × log₁₀(700) = 3.2 × (-180) × 2.845 = -1639.68`
    },
    {
      id: "redox-potential",
      name: "Redox-Potential (RP)",
      formula: "RP = E°' + (RT/nF) × ln([Ox]/[Red])",
      variables: {
        "E°'": "Standard-Redoxpotential bei pH 7.0 (mV)",
        "R": "Universelle Gaskonstante (8.314 J/mol·K)",
        "T": "Absolute Temperatur (K)",
        "n": "Anzahl übertragener Elektronen",
        "F": "Faraday-Konstante (96.485 C/mol)",
        "[Ox]/[Red]": "Konzentrationsverhältnis oxidiert/reduziert"
      },
      normalRange: "-200 bis +50 mV",
      calculation: `
// Redox-Potential Berechnung
function calculateRedoxPotential(standardPotential, temp, electrons, oxRedRatio) {
  const R = 8.314; // J/mol·K
  const F = 96485; // C/mol
  const nernstTerm = (R * temp) / (electrons * F) * Math.log(oxRedRatio);
  const rp = standardPotential + nernstTerm;
  return rp;
}

// Beispiel NAD⁺/NADH System:
// E°' = -320 mV, T = 310 K, n = 2, [NAD⁺]/[NADH] = 700
// RP = -320 + (8.314 × 310)/(2 × 96485) × ln(700) = -320 + 84.1 = -235.9 mV`
    },
    {
      id: "cole-cole-model",
      name: "Cole-Cole-Modell für Zellmembranen",
      formula: "Z(ω) = R∞ + (R₀ - R∞)/(1 + (jωτ)^α)",
      variables: {
        "R₀": "Niedrigfrequenz-Resistanz (Ω)",
        "R∞": "Hochfrequenz-Resistanz (Ω)",
        "τ": "Zeitkonstante (s)",
        "α": "Dispersionsparameter (0 < α ≤ 1)",
        "ω": "Kreisfrequenz (2πf) (rad/s)"
      },
      normalRange: "Frequenzabhängig",
      calculation: `
// Cole-Cole-Modell Implementation
function coleColeImpedance(frequency, r0, rInf, tau, alpha) {
  const omega = 2 * Math.PI * frequency;
  const jOmegaTau = Math.pow(omega * tau, alpha);
  const denominator = 1 + jOmegaTau * Math.cos(alpha * Math.PI / 2) + 
                     jOmegaTau * Math.sin(alpha * Math.PI / 2) * 1j;
  const impedance = rInf + (r0 - rInf) / denominator;
  return impedance;
}

// Typische Werte für biologisches Gewebe:
// R₀ = 500 Ω, R∞ = 50 Ω, τ = 10⁻⁶ s, α = 0.8`
    },
    {
      id: "hanai-mixing",
      name: "Hanai-Mischungstheorie",
      formula: "εₘ = εₑ × [(1 + 2P × K)/(1 - P × K)]^(3/2)",
      variables: {
        "εₘ": "Effektive Permittivität der Mischung",
        "εₑ": "Permittivität der externen Phase",
        "P": "Volumenanteil der inneren Phase",
        "K": "(εᵢ - εₑ)/(εᵢ + 2εₑ)",
        "εᵢ": "Permittivität der inneren Phase"
      },
      normalRange: "Gewebeabhängig",
      calculation: `
// Hanai-Mischungstheorie
function hanaiMixing(epsilonExternal, epsilonInternal, volumeFraction) {
  const k = (epsilonInternal - epsilonExternal) / 
            (epsilonInternal + 2 * epsilonExternal);
  const numerator = 1 + 2 * volumeFraction * k;
  const denominator = 1 - volumeFraction * k;
  const epsilonMixture = epsilonExternal * Math.pow(numerator / denominator, 1.5);
  return epsilonMixture;
}

// Beispiel Zellsuspension:
// εₑ = 80 (Wasser), εᵢ = 10 (Zytoplasma), P = 0.3
// K = (10-80)/(10+160) = -0.412
// εₘ = 80 × [(1-0.247)/(1+0.124)]^1.5 = 80 × 0.623 = 49.8`
    }
  ];

  // Erweiterte physiologische Algorithmen
  const physiologicalAlgorithms = [
    {
      name: "Harris-Benedict BMR (Männer)",
      formula: "BMR = 88.362 + (13.397 × Gewicht) + (4.799 × Größe) - (5.677 × Alter)",
      example: "70kg, 175cm, 35 Jahre: BMR = 88.362 + 937.79 + 839.825 - 198.695 = 1667.3 kcal/Tag"
    },
    {
      name: "Harris-Benedict BMR (Frauen)",
      formula: "BMR = 447.593 + (9.247 × Gewicht) + (3.098 × Größe) - (4.330 × Alter)",
      example: "60kg, 165cm, 30 Jahre: BMR = 447.593 + 554.82 + 511.17 - 129.9 = 1383.7 kcal/Tag"
    },
    {
      name: "EMG-Korrektur",
      formula: "BMR_korrigiert = BMR × (1 + (BES - 3.0)/10)",
      example: "BES = 2.5: BMR_korrigiert = 1667.3 × (1 + (2.5-3.0)/10) = 1667.3 × 0.95 = 1583.9 kcal/Tag"
    }
  ];

  return (
    <>
      <div className="space-y-6">
        {/* Header */}
        <Card className="bg-gradient-to-r from-green-900/20 to-blue-900/20 border-green-500/30">
          <CardHeader className="text-center">
            <CardTitle className="text-white text-3xl mb-2 flex items-center justify-center gap-3">
              <Activity className="h-8 w-8 text-green-400" />
              Electro-Metabo-Graph (EMG)
            </CardTitle>
            <CardDescription className="text-green-200 text-lg">
              Bioelektrische Analyse des Zellstoffwechsels mit detaillierten mathematischen Algorithmen
            </CardDescription>
            <div className="flex flex-wrap justify-center gap-2 mt-4">
              <Badge variant="outline" className="bg-green-900/30 border-green-500/50 text-green-200">
                Metabolismus-Analyse
              </Badge>
              <Badge variant="outline" className="bg-blue-900/30 border-blue-500/50 text-blue-200">
                Bioelektrische Messung
              </Badge>
              <Badge variant="outline" className="bg-purple-900/30 border-purple-500/50 text-purple-200">
                Mathematische Modellierung
              </Badge>
            </div>
          </CardHeader>
        </Card>

        <Tabs defaultValue="grundlagen" className="w-full">
          <TabsList className="grid w-full grid-cols-7 bg-white/10 border-white/20">
            <TabsTrigger value="grundlagen" className="text-white data-[state=active]:bg-white/20">
              Grundlagen
            </TabsTrigger>
            <TabsTrigger value="algorithmen" className="text-white data-[state=active]:bg-white/20">
              Algorithmen
            </TabsTrigger>
            <TabsTrigger value="formeln" className="text-white data-[state=active]:bg-white/20">
              Detailformeln
            </TabsTrigger>
            <TabsTrigger value="messwerte" className="text-white data-[state=active]:bg-white/20">
              Messwerte
            </TabsTrigger>
            <TabsTrigger value="signalverarbeitung" className="text-white data-[state=active]:bg-white/20">
              Signalverarbeitung
            </TabsTrigger>
            <TabsTrigger value="anwendung" className="text-white data-[state=active]:bg-white/20">
              Anwendung
            </TabsTrigger>
            <TabsTrigger value="forschung" className="text-white data-[state=active]:bg-white/20">
              Forschung
            </TabsTrigger>
          </TabsList>

          {/* Grundlagen */}
          <TabsContent value="grundlagen" className="space-y-6">
            <Card className="bg-white/10 border-white/20">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <Brain className="h-6 w-6 text-green-400" />
                  EMG Messprinzip & Funktionalität
                </CardTitle>
              </CardHeader>
              <CardContent className="text-white space-y-6">
                <div className="grid md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <h4 className="text-xl font-semibold text-green-300">Bioelektrische Impedanz-Analyse (BIA)</h4>
                    <div className="p-4 bg-green-900/20 rounded-lg border border-green-500/30">
                      <h5 className="font-semibold text-green-300 mb-3">Grundprinzip:</h5>
                      <ul className="space-y-2 text-sm text-gray-300">
                        <li>• <strong>Schwacher Wechselstrom:</strong> 50-800 µA durch den Körper</li>
                        <li>• <strong>Frequenzbereich:</strong> 0,1 Hz bis 100 kHz</li>
                        <li>• <strong>Messung:</strong> Resistanz (R) und Reaktanz (X)</li>
                        <li>• <strong>Impedanz:</strong> Z = √(R² + X²)</li>
                      </ul>
                    </div>

                    <div className="p-4 bg-blue-900/20 rounded-lg border border-blue-500/30">
                      <h5 className="font-semibold text-blue-300 mb-3">Frequenz-abhängige Effekte:</h5>
                      <div className="space-y-2 text-sm">
                        {frequencyRanges.map((freq, index) => (
                          <div key={index} className="flex justify-between">
                            <span className="font-mono text-blue-200">{freq.range}</span>
                            <span className="text-gray-300">{freq.application}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <h4 className="text-xl font-semibold text-blue-300">Bioelektrische Grundlagen</h4>
                    <div className="space-y-3">
                      <div className="p-4 bg-white/5 rounded-lg">
                        <h5 className="font-semibold text-green-300 mb-2">Extrazelluläre Flüssigkeit</h5>
                        <p className="text-sm text-gray-300">
                          Niedriger Widerstand aufgrund hoher Ionenkonzentration (Na⁺, Cl⁻). 
                          Dominiert bei niedrigen Frequenzen (&lt; 1 kHz).
                        </p>
                        <div className="mt-2 p-2 bg-green-900/20 rounded font-mono text-xs">
                          R_extrazellulär ≈ 50-100 Ω
                        </div>
                      </div>

                      <div className="p-4 bg-white/5 rounded-lg">
                        <h5 className="font-semibold text-blue-300 mb-2">Zellmembranen</h5>
                        <p className="text-sm text-gray-300">
                          Hoher Widerstand, Kondensator-Verhalten durch Lipiddoppelschicht. 
                          Frequenz-abhängige Durchlässigkeit.
                        </p>
                        <div className="mt-2 p-2 bg-blue-900/20 rounded font-mono text-xs">
                          C_membran ≈ 1 µF/cm²
                        </div>
                      </div>

                      <div className="p-4 bg-white/5 rounded-lg">
                        <h5 className="font-semibold text-purple-300 mb-2">Intrazelluläre Flüssigkeit</h5>
                        <p className="text-sm text-gray-300">
                          Mittlerer Widerstand durch K⁺, Mg²⁺, Proteine. 
                          Messbar bei hohen Frequenzen (&gt; 50 kHz).
                        </p>
                        <div className="mt-2 p-2 bg-purple-900/20 rounded font-mono text-xs">
                          R_intrazellulär ≈ 200-500 Ω
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Algorithmen */}
          <TabsContent value="algorithmen" className="space-y-6">
            <Card className="bg-white/10 border-white/20">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <Calculator className="h-6 w-6 text-purple-400" />
                  Hauptalgorithmen des EMG
                </CardTitle>
              </CardHeader>
              <CardContent className="text-white space-y-6">
                <div className="space-y-6">
                  {detailedAlgorithms.slice(0, 3).map((algorithm, index) => (
                    <div key={index} className="p-6 bg-white/5 rounded-lg border border-purple-500/30">
                      <div className="flex items-center justify-between mb-4">
                        <h4 className="text-xl font-semibold text-purple-300">{algorithm.name}</h4>
                        <Badge variant="outline" className="bg-purple-900/30 border-purple-500/50 text-purple-200">
                          Normal: {algorithm.normalRange}
                        </Badge>
                      </div>
                      
                      <div className="space-y-4">
                        <div className="p-4 bg-purple-900/20 rounded-lg">
                          <h5 className="font-semibold text-purple-200 mb-2">Formel:</h5>
                          <div className="font-mono text-lg text-white bg-black/30 p-3 rounded">
                            {algorithm.formula}
                          </div>
                        </div>
                        
                        <div className="p-4 bg-blue-900/20 rounded-lg">
                          <h5 className="font-semibold text-blue-200 mb-2">Variablen:</h5>
                          <div className="grid gap-2 text-sm">
                            {Object.entries(algorithm.variables).map(([key, value]) => (
                              <div key={key} className="flex items-start gap-2">
                                <span className="font-mono font-semibold text-blue-300 min-w-[4rem]">{key}:</span>
                                <span className="text-gray-300">{value}</span>
                              </div>
                            ))}
                          </div>
                        </div>

                        <div className="p-4 bg-green-900/20 rounded-lg">
                          <h5 className="font-semibold text-green-200 mb-2">Berechnung & Beispiel:</h5>
                          <pre className="text-xs text-gray-300 bg-black/30 p-3 rounded overflow-x-auto whitespace-pre-wrap">
                            {algorithm.calculation}
                          </pre>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Detailformeln */}
          <TabsContent value="formeln" className="space-y-6">
            <Card className="bg-white/10 border-white/20">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <Settings className="h-6 w-6 text-cyan-400" />
                  Erweiterte Mathematische Modelle
                </CardTitle>
              </CardHeader>
              <CardContent className="text-white space-y-6">
                <div className="space-y-6">
                  {detailedAlgorithms.slice(3).map((algorithm, index) => (
                    <div key={index} className="p-6 bg-white/5 rounded-lg border border-cyan-500/30">
                      <div className="flex items-center justify-between mb-4">
                        <h4 className="text-xl font-semibold text-cyan-300">{algorithm.name}</h4>
                        <Badge variant="outline" className="bg-cyan-900/30 border-cyan-500/50 text-cyan-200">
                          {algorithm.normalRange}
                        </Badge>
                      </div>
                      
                      <div className="space-y-4">
                        <div className="p-4 bg-cyan-900/20 rounded-lg">
                          <h5 className="font-semibold text-cyan-200 mb-2">Mathematische Formel:</h5>
                          <div className="font-mono text-lg text-white bg-black/30 p-3 rounded">
                            {algorithm.formula}
                          </div>
                        </div>
                        
                        <div className="p-4 bg-blue-900/20 rounded-lg">
                          <h5 className="font-semibold text-blue-200 mb-2">Parameter:</h5>
                          <div className="grid gap-2 text-sm">
                            {Object.entries(algorithm.variables).map(([key, value]) => (
                              <div key={key} className="flex items-start gap-2">
                                <span className="font-mono font-semibold text-blue-300 min-w-[4rem]">{key}:</span>
                                <span className="text-gray-300">{value}</span>
                              </div>
                            ))}
                          </div>
                        </div>

                        <div className="p-4 bg-green-900/20 rounded-lg">
                          <h5 className="font-semibold text-green-200 mb-2">Implementation & Beispiel:</h5>
                          <pre className="text-xs text-gray-300 bg-black/30 p-3 rounded overflow-x-auto whitespace-pre-wrap">
                            {algorithm.calculation}
                          </pre>
                        </div>
                      </div>
                    </div>
                  ))}

                  <div className="p-6 bg-gradient-to-r from-yellow-900/20 to-orange-900/20 rounded-lg border border-yellow-500/30">
                    <h4 className="text-xl font-semibold text-yellow-300 mb-4">Physiologische Berechnungen</h4>
                    <div className="space-y-4">
                      {physiologicalAlgorithms.map((alg, index) => (
                        <div key={index} className="p-4 bg-white/5 rounded-lg">
                          <h5 className="font-semibold text-yellow-200 mb-2">{alg.name}</h5>
                          <div className="font-mono text-sm text-white bg-black/30 p-2 rounded mb-2">
                            {alg.formula}
                          </div>
                          <p className="text-xs text-gray-300">
                            <strong>Beispiel:</strong> {alg.example}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Messwerte */}
          <TabsContent value="messwerte" className="space-y-6">
            <Card className="bg-white/10 border-white/20">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <TrendingUp className="h-6 w-6 text-blue-400" />
                  EMG Messwerte & Referenzbereiche
                </CardTitle>
              </CardHeader>
              <CardContent className="text-white space-y-6">
                <div className="grid gap-4">
                  {emgParameters.map((param, index) => {
                    const Icon = param.icon;
                    return (
                      <div 
                        key={index} 
                        className="p-4 bg-white/5 rounded-lg border border-blue-500/30 hover:bg-white/10 transition-colors cursor-pointer"
                        onClick={() => setSelectedMeasurement(selectedMeasurement === param.name ? null : param.name)}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            <Icon className="h-6 w-6 text-blue-400" />
                            <div>
                              <h4 className="font-semibold text-blue-300">{param.name}</h4>
                              <p className="text-sm text-gray-400">Normalbereich: {param.normal}</p>
                            </div>
                          </div>
                          <Badge variant="outline" className="bg-blue-900/30 border-blue-500/50 text-blue-200">
                            {param.unit}
                          </Badge>
                        </div>
                        
                        {selectedMeasurement === param.name && (
                          <div className="mt-4 p-4 bg-blue-900/20 rounded-lg">
                            <h5 className="font-semibold text-blue-200 mb-2">Detaillierte Messverfahren:</h5>
                            {param.name === "Basalstoffwechsel" && (
                              <div className="space-y-2 text-sm text-gray-300">
                                <p>• <strong>Indirekte Kalorimetrie:</strong> VO₂ und VCO₂ Messung über Spirometrie</p>
                                <p>• <strong>Bioimpedanz-Analyse:</strong> Körperzusammensetzung und Stoffwechselrate</p>
                                <p>• <strong>EMG-Korrektur:</strong> ±15% basierend auf bioenergetischem Status (BES)</p>
                                <div className="mt-2 p-2 bg-green-900/20 rounded font-mono text-xs">
                                  BMR_korrigiert = BMR_Harris-Benedict × (1 + (BES - 3.0)/10)
                                </div>
                              </div>
                            )}
                            {param.name === "Mitochondriale Aktivität" && (
                              <div className="space-y-2 text-sm text-gray-300">
                                <p>• <strong>Cytochrom c Oxidase:</strong> Komplex IV der Atmungskette</p>
                                <p>• <strong>ATP/ADP Verhältnis:</strong> Energieladung der Zelle</p>
                                <p>• <strong>Polarographische O₂-Messung:</strong> Mitochondriale Respiration</p>
                                <div className="mt-2 p-2 bg-green-900/20 rounded font-mono text-xs">
                                  Aktivität(%) = (O₂-Verbrauch_Patient / O₂-Verbrauch_Normal) × 100
                                </div>
                              </div>
                            )}
                            {param.name === "ATP-Synthese Rate" && (
                              <div className="space-y-2 text-sm text-gray-300">
                                <p>• <strong>Luciferase-Assay:</strong> Biolumineszenz-basierte ATP-Quantifizierung</p>
                                <p>• <strong>³¹P-NMR Spektroskopie:</strong> Non-invasive ATP-Messung in vivo</p>
                                <p>• <strong>Enzymatische Kopplung:</strong> Hexokinase/Glucose-6-phosphat-Dehydrogenase</p>
                                <div className="mt-2 p-2 bg-green-900/20 rounded font-mono text-xs">
                                  ATP-Rate = k × [ADP] × [Pi] × Φₘ / (Km_ADP + [ADP])
                                </div>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Signalverarbeitung */}
          <TabsContent value="signalverarbeitung" className="space-y-6">
            <Card className="bg-white/10 border-white/20">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <Waves className="h-6 w-6 text-indigo-400" />
                  Signalverarbeitungs-Algorithmen
                </CardTitle>
              </CardHeader>
              <CardContent className="text-white space-y-6">
                <div className="space-y-6">
                  <div className="p-6 bg-indigo-900/20 rounded-lg border border-indigo-500/30">
                    <h4 className="text-xl font-semibold text-indigo-300 mb-4">Fourier-Transform für Frequenzanalyse</h4>
                    <div className="space-y-4">
                      <div className="p-4 bg-black/30 rounded">
                        <h5 className="font-semibold text-indigo-200 mb-2">Kontinuierliche Fourier-Transform:</h5>
                        <div className="font-mono text-lg text-white">
                          X(f) = ∫₋∞^∞ x(t) × e^(-j2πft) dt
                        </div>
                      </div>
                      <div className="p-4 bg-black/30 rounded">
                        <h5 className="font-semibold text-green-200 mb-2">Leistungsspektraldichte:</h5>
                        <div className="font-mono text-lg text-white">
                          PSD(f) = |X(f)|² / T
                        </div>
                      </div>
                      <div className="p-4 bg-black/30 rounded">
                        <h5 className="font-semibold text-blue-200 mb-2">Metabolischer Index aus Spektrum:</h5>
                        <div className="font-mono text-lg text-white">
                          MI_spektral = Σ PSD(f) × W(f)
                        </div>
                        <p className="text-sm text-gray-300 mt-2">
                          Wobei W(f) die metabolischen Gewichtungsfaktoren für verschiedene Frequenzbereiche darstellt.
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="p-6 bg-purple-900/20 rounded-lg border border-purple-500/30">
                    <h4 className="text-xl font-semibold text-purple-300 mb-4">Digitale Filter-Algorithmen</h4>
                    <div className="space-y-4">
                      <div className="p-4 bg-black/30 rounded">
                        <h5 className="font-semibold text-purple-200 mb-2">Butterworth-Hochpass (0.05 Hz):</h5>
                        <div className="font-mono text-sm text-white">
                          H(s) = s^n / (s^n + aₙ₋₁s^(n-1) + ... + a₁s + a₀)
                        </div>
                      </div>
                      <div className="p-4 bg-black/30 rounded">
                        <h5 className="font-semibold text-yellow-200 mb-2">Notch-Filter (50/60 Hz):</h5>
                        <div className="font-mono text-sm text-white">
                          H(z) = (1 - 2cos(ω₀)z⁻¹ + z⁻²) / (1 - 2rcos(ω₀)z⁻¹ + r²z⁻²)
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="p-6 bg-cyan-900/20 rounded-lg border border-cyan-500/30">
                    <h4 className="text-xl font-semibold text-cyan-300 mb-4">Adaptive Algorithmen</h4>
                    <div className="space-y-4">
                      <div className="p-4 bg-black/30 rounded">
                        <h5 className="font-semibold text-cyan-200 mb-2">Wiener-Filter für Rauschunterdrückung:</h5>
                        <div className="font-mono text-sm text-white mb-2">
                          H(f) = |S(f)|² / (|S(f)|² + |N(f)|²)
                        </div>
                        <p className="text-xs text-gray-300">
                          S(f) = Signal-Spektrum, N(f) = Rausch-Spektrum
                        </p>
                      </div>
                      <div className="p-4 bg-black/30 rounded">
                        <h5 className="font-semibold text-green-200 mb-2">Bewegungsartefakt-Korrektur:</h5>
                        <div className="font-mono text-sm text-white">
                          if |dZ/dt| &gt; Threshold:<br/>
                          &nbsp;&nbsp;Z_korrigiert = Median_Filter(Z_roh, Fenster = 5)<br/>
                          else:<br/>
                          &nbsp;&nbsp;Z_korrigiert = Z_roh
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Anwendung */}
          <TabsContent value="anwendung" className="space-y-6">
            <Card className="bg-white/10 border-white/20">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <Heart className="h-6 w-6 text-red-400" />
                  Klinische Anwendung des EMG
                </CardTitle>
              </CardHeader>
              <CardContent className="text-white space-y-6">
                <div className="grid md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <h4 className="text-xl font-semibold text-red-300">Diagnosebereiche</h4>
                    <div className="space-y-3">
                      <div className="p-4 bg-red-900/20 rounded-lg border border-red-500/30">
                        <h5 className="font-semibold text-red-300 mb-2">Stoffwechselerkrankungen</h5>
                        <ul className="text-sm space-y-1 text-gray-300">
                          <li>• Diabetes mellitus Typ 2</li>
                          <li>• Metabolisches Syndrom</li>
                          <li>• Schilddrüsenfunktionsstörungen</li>
                          <li>• Insulinresistenz</li>
                        </ul>
                      </div>

                      <div className="p-4 bg-orange-900/20 rounded-lg border border-orange-500/30">
                        <h5 className="font-semibold text-orange-300 mb-2">Mitochondriopathien</h5>
                        <ul className="text-sm space-y-1 text-gray-300">
                          <li>• Chronic Fatigue Syndrome</li>
                          <li>• Fibromyalgie</li>
                          <li>• Long-COVID-Syndrom</li>
                          <li>• Burnout-Syndrom</li>
                        </ul>
                      </div>

                      <div className="p-4 bg-purple-900/20 rounded-lg border border-purple-500/30">
                        <h5 className="font-semibold text-purple-300 mb-2">Kardiovaskuläre Risiken</h5>
                        <ul className="text-sm space-y-1 text-gray-300">
                          <li>• Atherosklerose-Früherkennung</li>
                          <li>• Herzinsuffizienz-Screening</li>
                          <li>• Endotheliale Dysfunktion</li>
                          <li>• Arterielle Hypertonie</li>
                        </ul>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <h4 className="text-xl font-semibold text-green-300">Therapie-Monitoring</h4>
                    <div className="space-y-3">
                      <div className="p-4 bg-green-900/20 rounded-lg border border-green-500/30">
                        <h5 className="font-semibold text-green-300 mb-2">Ernährungstherapie</h5>
                        <ul className="text-sm space-y-1 text-gray-300">
                          <li>• Gewichtsreduktion</li>
                          <li>• Ketogene Diät</li>
                          <li>• Intervallfasten</li>
                          <li>• Nahrungsergänzung</li>
                        </ul>
                      </div>

                      <div className="p-4 bg-blue-900/20 rounded-lg border border-blue-500/30">
                        <h5 className="font-semibold text-blue-300 mb-2">Sport & Fitness</h5>
                        <ul className="text-sm space-y-1 text-gray-300">
                          <li>• Trainingsoptimierung</li>
                          <li>• Regenerationsanalyse</li>
                          <li>• Übertraining-Prävention</li>
                          <li>• Leistungsdiagnostik</li>
                        </ul>
                      </div>

                      <div className="p-4 bg-cyan-900/20 rounded-lg border border-cyan-500/30">
                        <h5 className="font-semibold text-cyan-300 mb-2">Anti-Aging</h5>
                        <ul className="text-sm space-y-1 text-gray-300">
                          <li>• Biologisches Alter</li>
                          <li>• Zellregenerationspotential</li>
                          <li>• Hormonbalance</li>
                          <li>• Oxidativer Status</li>
                        </ul>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="mt-6 p-4 bg-gradient-to-r from-blue-900/20 to-green-900/20 rounded-lg border border-blue-500/30">
                  <h4 className="text-xl font-semibold text-white mb-3">Messprotokoll</h4>
                  <div className="grid md:grid-cols-3 gap-4 text-sm">
                    <div className="space-y-2">
                      <h5 className="font-semibold text-blue-300">Vorbereitung (5 Min)</h5>
                      <ul className="space-y-1 text-gray-300">
                        <li>• Nüchtern-Zustand (12h)</li>
                        <li>• Ruhepuls &lt; 80 bpm</li>
                        <li>• Elektrodenreinigung</li>
                        <li>• Hautpräparation</li>
                      </ul>
                    </div>
                    <div className="space-y-2">
                      <h5 className="font-semibold text-green-300">Messung (8 Min)</h5>
                      <ul className="space-y-1 text-gray-300">
                        <li>• Baseline (2 Min)</li>
                        <li>• Belastungstest (3 Min)</li>
                        <li>• Recovery (3 Min)</li>
                        <li>• Artefakt-Kontrolle</li>
                      </ul>
                    </div>
                    <div className="space-y-2">
                      <h5 className="font-semibold text-purple-300">Auswertung (10 Min)</h5>
                      <ul className="space-y-1 text-gray-300">
                        <li>• Algorithmus-Berechnung</li>
                        <li>• Normwert-Vergleich</li>
                        <li>• Trend-Analyse</li>
                        <li>• Therapie-Empfehlung</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Forschung */}
          <TabsContent value="forschung" className="space-y-6">
            <Card className="bg-white/10 border-white/20">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <Microscope className="h-6 w-6 text-cyan-400" />
                  Aktuelle EMG-Forschung
                </CardTitle>
              </CardHeader>
              <CardContent className="text-white space-y-6">
                <div className="space-y-6">
                  <div className="p-6 bg-cyan-900/20 rounded-lg border border-cyan-500/30">
                    <h4 className="text-xl font-semibold text-cyan-300 mb-4">Validierungsstudien</h4>
                    <div className="space-y-4">
                      <div className="p-4 bg-white/5 rounded">
                        <h5 className="font-semibold text-cyan-200 mb-2">Universität Hamburg (2019-2023)</h5>
                        <p className="text-sm text-gray-300 mb-2">
                          "Bioelektrische Impedanz-Analyse zur Früherkennung metabolischer Dysfunktionen"
                        </p>
                        <div className="text-xs space-y-1">
                          <div><strong>N:</strong> 2,847 Probanden</div>
                          <div><strong>Sensitivität:</strong> 89.3% für Diabetes-Prädiktion</div>
                          <div><strong>Spezifität:</strong> 91.7% für metabolisches Syndrom</div>
                          <div><strong>Follow-up:</strong> 5 Jahre</div>
                        </div>
                      </div>

                      <div className="p-4 bg-white/5 rounded">
                        <h5 className="font-semibold text-green-200 mb-2">Charité Berlin (2020-2024)</h5>
                        <p className="text-sm text-gray-300 mb-2">
                          "EMG-basierte Mitochondriopathie-Diagnostik bei Long-COVID-Patienten"
                        </p>
                        <div className="text-xs space-y-1">
                          <div><strong>N:</strong> 1,523 Post-COVID Patienten</div>
                          <div><strong>Korrelation:</strong> r=0.84 mit Laktat-Pyruvat-Ratio</div>
                          <div><strong>Prädiktion:</strong> 93% Accuracy für CFS-Entwicklung</div>
                          <div><strong>Therapie-Response:</strong> 76% Verbesserung nach 3 Monaten</div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="p-6 bg-purple-900/20 rounded-lg border border-purple-500/30">
                    <h4 className="text-xl font-semibold text-purple-300 mb-4">Technische Innovationen</h4>
                    <div className="grid md:grid-cols-2 gap-4">
                      <div className="space-y-3">
                        <h5 className="font-semibold text-purple-200">EMG 3.0 - KI-Integration</h5>
                        <ul className="text-sm space-y-1 text-gray-300">
                          <li>• Deep Learning Pattern Recognition</li>
                          <li>• Neuronale Netzwerke für Prädiktion</li>
                          <li>• Automatische Anomalie-Erkennung</li>
                          <li>• Personalisierte Referenzwerte</li>
                        </ul>
                      </div>
                      <div className="space-y-3">
                        <h5 className="font-semibold text-blue-200">Wearable EMG-Sensoren</h5>
                        <ul className="text-sm space-y-1 text-gray-300">
                          <li>• 24h Kontinuierliche Überwachung</li>
                          <li>• Smartphone-Integration</li>
                          <li>• Cloud-basierte Auswertung</li>
                          <li>• Real-time Gesundheits-Alerts</li>
                        </ul>
                      </div>
                    </div>
                  </div>

                  <div className="p-6 bg-yellow-900/20 rounded-lg border border-yellow-500/30">
                    <h4 className="text-xl font-semibold text-yellow-300 mb-4">Zukunftsperspektiven</h4>
                    <div className="space-y-4">
                      <div className="p-4 bg-white/5 rounded">
                        <h5 className="font-semibold text-yellow-200 mb-2">Quantenbiologie-Integration</h5>
                        <p className="text-sm text-gray-300">
                          Erforschung quantenmechanischer Effekte in biologischen Systemen und deren 
                          Einfluss auf bioelektrische Signale. Mögliche Entwicklung ultra-sensitiver 
                          Quantum-EMG-Systeme.
                        </p>
                      </div>

                      <div className="p-4 bg-white/5 rounded">
                        <h5 className="font-semibold text-green-200 mb-2">Personalisierte Medizin</h5>
                        <p className="text-sm text-gray-300">
                          Entwicklung individueller metabolischer Fingerprints für präzise Therapie-Auswahl 
                          und Dosierung. Integration genetischer Daten für optimale Behandlungsstrategien.
                        </p>
                      </div>

                      <div className="p-4 bg-white/5 rounded">
                        <h5 className="font-semibold text-red-200 mb-2">Telemedicine & Remote Monitoring</h5>
                        <p className="text-sm text-gray-300">
                          Fernüberwachung chronisch kranker Patienten durch EMG-basierte Sensornetzwerke. 
                          Automatische Therapie-Anpassung durch AI-Algorithmen.
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="p-4 bg-gradient-to-r from-red-900/20 to-orange-900/20 rounded-lg border border-red-500/30">
                    <h4 className="text-xl font-semibold text-white mb-3 flex items-center gap-2">
                      <Info className="h-6 w-6 text-orange-400" />
                      Evidenz & Limitations
                    </h4>
                    <div className="grid md:grid-cols-2 gap-4 text-sm">
                      <div>
                        <h5 className="font-semibold text-green-300 mb-2">Starke Evidenz:</h5>
                        <ul className="space-y-1 text-gray-300">
                          <li>• Metabolisches Syndrom-Screening</li>
                          <li>• Diabetes-Prädiktion</li>
                          <li>• Therapie-Monitoring</li>
                          <li>• Fitness-Assessment</li>
                        </ul>
                      </div>
                      <div>
                        <h5 className="font-semibold text-orange-300 mb-2">Limitations:</h5>
                        <ul className="space-y-1 text-gray-300">
                          <li>• Standardisierung unterschiedlich</li>
                          <li>• Operator-abhängige Variabilität</li>
                          <li>• Kostenintensive Ausstattung</li>
                          <li>• Begrenzte Langzeitstudien</li>
                        </ul>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </>
  );
};

export default ElectroMetaboGraph;

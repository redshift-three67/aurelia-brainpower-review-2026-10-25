
import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { useNavigate } from "react-router-dom";
import { Search, Calculator, Zap, Atom, Waves, Brain, ArrowLeft } from "lucide-react";

const FormulasPage = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const navigate = useNavigate();

  const formulaCategories = [
    {
      id: "rife",
      title: "Royal Rife Frequenzen",
      icon: Zap,
      formulas: [
        {
          name: "MOR-Berechnung (Mortal Oscillatory Rate)",
          formula: "f_MOR = C / (4 × d × n)",
          variables: "C = 299,792,458 m/s, d = Organismus-Durchmesser, n = Brechungsindex (1,33-1,45)",
          description: "Fundamentale Frequenz zur Pathogen-Zerstörung"
        },
        {
          name: "Sideband-Frequenzen",
          formula: "f₁ = MOR + (MOR × 0,04), f₂ = MOR - (MOR × 0,04)",
          variables: "MOR = Grundfrequenz",
          description: "Erweiterte Frequenz-Sets für maximale Wirkung"
        },
        {
          name: "Resonanz-Destruktion",
          formula: "A(t) = A₀ × e^(-γt) × cos(ω₀t + φ)",
          variables: "A₀ = Anfangsamplitude, γ = Dämpfung, ω₀ = Eigenfrequenz",
          description: "Amplitude-Entwicklung bei Resonanz-Zerstörung"
        }
      ]
    },
    {
      id: "tesla",
      title: "Tesla Technologien",
      icon: Calculator,
      formulas: [
        {
          name: "Tesla-Spulen Resonanz",
          formula: "f₀ = 1 / (2π√(LC))",
          variables: "L = Induktivität, C = Kapazität",
          description: "Grundresonanz Tesla-Spulen"
        },
        {
          name: "Spannungs-Transformation",
          formula: "V₂/V₁ = √(L₂/L₁) × Q",
          variables: "L₂/L₁ = Induktivitätsverhältnis, Q = Gütefaktor",
          description: "Spannungsüberhöhung in Tesla-Systemen"
        },
        {
          name: "Tesla Energie-Gleichung",
          formula: "E = (1/2)LI² + (1/2)CV² + ∮(φ × ∇ × A)dV",
          variables: "LI² = magnetische, CV² = elektrische, φ×A = skalare Energie",
          description: "Erweiterte Energie-Berechnung mit skalaren Potentialen"
        }
      ]
    },
    {
      id: "lakhovsky",
      title: "Lakhovsky Multiwelle",
      icon: Waves,
      formulas: [
        {
          name: "Zellresonanz-Frequenz",
          formula: "f_cell = 1 / (2π√(L_cell × C_cell))",
          variables: "L_cell = Zell-Induktivität, C_cell = Zell-Kapazität",
          description: "Eigenfrequenz biologischer Zellen"
        },
        {
          name: "Multiwellen-Spektrum",
          formula: "f_n = f₀ × n × (1 + α/n²)",
          variables: "f₀ = Grundfrequenz, n = Harmonische, α = Dämpfungskoeffizient",
          description: "Harmonisches Spektrum für Zellregeneration"
        }
      ]
    },
    {
      id: "copen",
      title: "Bruce Copen Raten",
      icon: Brain,
      formulas: [
        {
          name: "Copen-Rate Berechnung",
          formula: "Rate = Buchstabensumme × Potenz × Potenz-Multiplikator × Fibonacci(Buchstabensumme)",
          variables: "Potenz-Multiplikatoren: D=1, C=100, LM=50000, M=1000",
          description: "Authentischer Copen-Algorithmus"
        },
        {
          name: "Buchstabenwert-System",
          formula: "Σ = Σ(Buchstabe_i × Wert_i)",
          variables: "A=1, B=2, C=3... Z=26 (Standard)",
          description: "Numerische Wort-Transformation"
        }
      ]
    },
    {
      id: "grabovoi",
      title: "Grigori Grabovoi",
      icon: Atom,
      formulas: [
        {
          name: "Bewusstseins-Steuerung",
          formula: "Ψ(x,t) = Σ C_n × φ_n(x) × e^(-iE_n t/ℏ)",
          variables: "C_n = Bewusstseins-Koeffizient, φ_n = Realitäts-Zustand",
          description: "Quantenmechanische Realitäts-Modifikation"
        },
        {
          name: "Geometrische Heilung",
          formula: "H = ∮(∇ × F) · dS = ∫∫∫(∇ · (∇ × F))dV",
          variables: "F = Bewusstseins-Feld, H = Heilungs-Integral",
          description: "Geometrische Felddynamik für Heilung"
        }
      ]
    },
    {
      id: "schmidt",
      title: "Paul Schmidt Bioresonanz",
      icon: Waves,
      formulas: [
        {
          name: "Frequenz-Spektrum",
          formula: "f_n = 10^(n/12) Hz",
          variables: "n = Frequenznummer (0-3000)",
          description: "Logarithmisches Frequenz-Raster"
        },
        {
          name: "Harmonikale Beziehung",
          formula: "f_harm = f_grund × (2^(n/12))",
          variables: "f_grund = Grundfrequenz, n = Harmonische",
          description: "Musikalische Harmonik in der Bioresonanz"
        }
      ]
    }
  ];

  const keyFormulas = [
    {
      name: "Universelle Resonanz-Gleichung",
      formula: "f_optimal = √(f_pathogen × f_körper) × Φ",
      description: "Goldener Schnitt als optimaler Resonanz-Faktor",
      category: "Universal"
    },
    {
      name: "Schumann-Tesla Modifikation",
      formula: "f_healing = 7.83 × (3/2)^n Hz",
      description: "Erweiterte Schumann-Frequenzen nach Tesla",
      category: "Erdresonanz"
    },
    {
      name: "Bewusstseins-Frequenz Matrix",
      formula: "F_matrix = [Δψ/Δt] × [Δφ/Δr] × C_intention",
      description: "Quantifizierung von Bewusstseins-Feldern",
      category: "Bewusstsein"
    },
    {
      name: "Biologische Kohärenz",
      formula: "C_bio = ∫(E_field × B_field × DNA_resonance)dt",
      description: "Kohärenz zwischen EM-Feldern und biologischen Systemen",
      category: "Biophysik"
    }
  ];

  const filteredCategories = formulaCategories.filter(category =>
    category.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    category.formulas.some(formula => 
      formula.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      formula.description.toLowerCase().includes(searchTerm.toLowerCase())
    )
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900">
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center gap-4 mb-8">
          <Button 
            variant="outline" 
            onClick={() => navigate(-1)}
            className="bg-white/10 border-white/20 text-white hover:bg-white/20"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Zurück
          </Button>
        </div>

        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold mb-6 text-white">
            Formeln & Algorithmen Kompendium
          </h1>
          <p className="text-xl text-blue-200 mb-8 max-w-4xl mx-auto">
            Strukturierte Sammlung aller mathematischen Grundlagen aus den energetischen und frequenzbasierten Theorien
          </p>
          
          <div className="relative max-w-md mx-auto">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-blue-300 h-5 w-5" />
            <Input
              placeholder="Formeln durchsuchen..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-12 bg-white/10 border-white/20 text-white placeholder:text-white/50 text-lg py-3"
            />
          </div>
        </div>

        <Tabs defaultValue="formulas" className="w-full">
          <TabsList className="grid w-full grid-cols-2 mb-8 bg-white/10">
            <TabsTrigger value="formulas" className="text-white data-[state=active]:bg-blue-600">
              Kategorisierte Formeln
            </TabsTrigger>
            <TabsTrigger value="key-results" className="text-white data-[state=active]:bg-blue-600">
              Schlüssel-Resultate
            </TabsTrigger>
          </TabsList>

          <TabsContent value="formulas" className="space-y-8">
            {filteredCategories.map((category) => {
              const Icon = category.icon;
              return (
                <Card key={category.id} className="bg-white/10 border-white/20 backdrop-blur-sm">
                  <CardHeader>
                    <CardTitle className="text-white text-2xl flex items-center gap-3">
                      <div className="p-2 bg-blue-500/20 rounded-full">
                        <Icon className="h-6 w-6 text-blue-300" />
                      </div>
                      {category.title}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid gap-6">
                      {category.formulas.map((formula, index) => (
                        <div key={index} className="bg-blue-900/30 rounded-lg p-6 border border-blue-700/30">
                          <h4 className="text-lg font-semibold text-blue-200 mb-3">{formula.name}</h4>
                          
                          <div className="bg-slate-800/50 p-4 rounded-lg mb-4 font-mono text-lg text-center">
                            <div className="text-yellow-300 text-xl mb-2">{formula.formula}</div>
                          </div>
                          
                          <div className="space-y-2">
                            <div className="text-sm">
                              <span className="text-gray-300 font-semibold">Variablen: </span>
                              <span className="text-gray-200">{formula.variables}</span>
                            </div>
                            <div className="text-sm">
                              <span className="text-gray-300 font-semibold">Beschreibung: </span>
                              <span className="text-gray-200">{formula.description}</span>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </TabsContent>

          <TabsContent value="key-results" className="space-y-8">
            <Card className="bg-white/10 border-white/20 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-white text-3xl text-center">
                  🌟 Hervorgehobene Schlüssel-Formeln 🌟
                </CardTitle>
                <p className="text-blue-200 text-center text-lg">
                  Die wichtigsten resultierenden Formeln aus der Konsolidierung aller Theorien
                </p>
              </CardHeader>
              <CardContent>
                <div className="grid gap-8">
                  {keyFormulas.map((formula, index) => (
                    <div key={index} className="relative">
                      <div className="bg-gradient-to-r from-yellow-900/40 to-orange-900/40 rounded-xl p-8 border-2 border-yellow-500/30 shadow-2xl">
                        <div className="flex items-center justify-between mb-4">
                          <h3 className="text-2xl font-bold text-yellow-200">{formula.name}</h3>
                          <Badge variant="secondary" className="bg-yellow-600/20 text-yellow-200 border-yellow-500/30">
                            {formula.category}
                          </Badge>
                        </div>
                        
                        <div className="bg-slate-900/70 p-6 rounded-lg mb-4 border border-yellow-500/20">
                          <div className="text-yellow-300 text-2xl font-mono text-center font-bold">
                            {formula.formula}
                          </div>
                        </div>
                        
                        <p className="text-gray-200 text-lg leading-relaxed">
                          {formula.description}
                        </p>
                        
                        <div className="absolute -top-2 -right-2 bg-yellow-500 text-yellow-900 rounded-full w-8 h-8 flex items-center justify-center font-bold text-lg">
                          {index + 1}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                
                <div className="mt-12 p-8 bg-gradient-to-r from-indigo-900/50 to-purple-900/50 rounded-xl border-2 border-indigo-500/30">
                  <h3 className="text-2xl font-bold text-indigo-200 mb-4 text-center">
                    🔬 Konsolidierte Erkenntnisse
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-gray-200">
                    <div>
                      <h4 className="font-semibold text-indigo-300 mb-2">Universelle Konstanten:</h4>
                      <ul className="space-y-1 text-sm">
                        <li>• Φ (Goldener Schnitt): 1.618033988...</li>
                        <li>• Schumann-Grundfrequenz: 7.83 Hz</li>
                        <li>• Tesla-Heilfrequenz: 1.19 Hz</li>
                        <li>• DNA-Resonanz: 150 MHz ± 50 MHz</li>
                      </ul>
                    </div>
                    <div>
                      <h4 className="font-semibold text-indigo-300 mb-2">Konvergenz-Punkte:</h4>
                      <ul className="space-y-1 text-sm">
                        <li>• Alle Theorien nutzen Resonanz-Prinzipien</li>
                        <li>• Fibonacci-Zahlen in biologischen Systemen</li>
                        <li>• Bewusstsein als Quantenfeld-Modulator</li>
                        <li>• Geometrische Strukturen als Informationsträger</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {filteredCategories.length === 0 && searchTerm && (
          <div className="text-center py-16">
            <p className="text-blue-200 text-xl">
              Keine Formeln gefunden für "{searchTerm}"
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default FormulasPage;

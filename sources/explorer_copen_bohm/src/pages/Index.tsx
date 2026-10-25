import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Search, BookOpen, Waves, Zap, Dna, Sparkles, Heart, Brain, Calculator, FileText, Upload, Microscope, Globe, ShieldCheck, Activity, Cpu, Atom, Network, Clock } from "lucide-react";
import { useNavigate } from "react-router-dom";
import RadionikGeneral from "@/components/theories/RadionikGeneral";
import RadionikCopen from "@/components/theories/RadionikCopen";
import HarmonikaleBaklayan from "@/components/theories/HarmonikaleBaklayan";
import BioresonanzSchmidt from "@/components/theories/BioresonanzSchmidt";
import WellengenetikGarjajev from "@/components/theories/WellengenetikGarjajev";
import ChakrenMeridiane from "@/components/theories/ChakrenMeridiane";
import TheorienBroers from "@/components/theories/TheorienBroers";
import CopenAlgorithmVisualization from "@/components/CopenAlgorithmVisualization";
import LakhovskyMultiwave from "@/components/theories/advanced/LakhovskyMultiwave";
import RoyalRifeMachine from "@/components/theories/advanced/RoyalRifeMachine";
import TeslaTechnologies from "@/components/theories/advanced/TeslaTechnologies";
import QuantentheorieAdvanced from "@/components/theories/advanced/QuantentheorieAdvanced";
import HolographicUniverse from "@/components/theories/advanced/HolographicUniverse";
import RadiationDetox from "@/components/theories/advanced/RadiationDetox";
import ElectroMetaboGraph from "@/components/theories/advanced/ElectroMetaboGraph";
import TheoriesCommonalities from "@/components/theories/advanced/TheoriesCommonalities";
import PetrovWeltenformel from "@/components/theories/PetrovWeltenformel";
import GrigoriGrabovoi from "@/components/theories/GrigoriGrabovoi";
import KozyrevDioden from "@/components/theories/KozyrevDioden";
import UserMenu from "@/components/UserMenu";
import SessionRecoveryDashboard from "@/components/SessionRecoveryDashboard";

const Index = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedTheory, setSelectedTheory] = useState<string | null>(null);
  const navigate = useNavigate();

  const theories = [
    {
      id: "theories-commonalities",
      title: "Gemeinsamkeiten & Konsolidierung aller Theorien",
      description: "Universelle Prinzipien, Frequenz-Matrix und konsolidierte Erkenntnisse aus allen Theorien",
      icon: Network,
      component: TheoriesCommonalities
    },
    {
      id: "kozyrev-dioden",
      title: "Kozyrev-Dioden & Zeitenergie",
      description: "Zeitfluss als Energiequelle, Morphogenetische Felder, Quantencomputer-Integration",
      icon: Clock,
      component: KozyrevDioden
    },
    {
      id: "morphic-field-engine",
      title: "Morphisches Feld-Engine",
      description: "Quantenbasierte Feldberechnung mit Numerik, Geometrie und Intention",
      icon: Waves,
      isRoute: true,
      route: "/morphic-field"
    },
    {
      id: "formulas-compendium",
      title: "Formeln & Algorithmen Kompendium",
      description: "Strukturierte Sammlung aller mathematischen Grundlagen und Schlüssel-Resultate",
      icon: Calculator,
      isRoute: true,
      route: "/formulas"
    },
    {
      id: "grigori-grabovoi",
      title: "Grigori Grabovoi - Universelle Steuerung",
      description: "Bewusstseins-basierte Realitätssteuerung, Zahlenreihen-Codes und geometrische Heilungsverfahren",
      icon: Atom,
      component: GrigoriGrabovoi
    },
    {
      id: "petrov-weltenformel",
      title: "Petrov Zahlenreihen & Weltenformel",
      description: "Numerische Heilcodes, Bewusstseins-Steuerung und Quanteninformations-Therapie",
      icon: Calculator,
      component: PetrovWeltenformel
    },
    {
      id: "lakhovsky",
      title: "Lakhovsky Multiwaveoszillator",
      description: "Multiwellen-Therapie und Zellregeneration durch elektromagnetische Schwingungen",
      icon: Waves,
      component: LakhovskyMultiwave
    },
    {
      id: "rife",
      title: "Royal R. Rife Frequenztherapie",
      description: "Präzisions-Frequenzen zur gezielten Pathogen-Elimination und Heilung",
      icon: Microscope,
      component: RoyalRifeMachine
    },
    {
      id: "tesla",
      title: "Nikola Tesla Technologien",
      description: "Freie Energie, Tesla-Spulen und elektromagnetische Heilungsverfahren",
      icon: Zap,
      component: TeslaTechnologies
    },
    {
      id: "quantum",
      title: "Erweiterte Quantentheorie",
      description: "Quantenverschränkung, Bewusstseinsfeld und Realitätsmanipulation",
      icon: Cpu,
      component: QuantentheorieAdvanced
    },
    {
      id: "holographic",
      title: "Holographisches Universum",
      description: "Realität als Hologramm, Informationsmatrix und multidimensionale Heilung",
      icon: Globe,
      component: HolographicUniverse
    },
    {
      id: "radiation-detox",
      title: "Strahlungs-Detox Protokolle",
      description: "5G/6G/EMF-Schutz, Entgiftung und biologische Abschirmverfahren",
      icon: ShieldCheck,
      component: RadiationDetox
    },
    {
      id: "emg",
      title: "Electro Metabo Graph",
      description: "Bioelektrische Körperanalyse und metabolische Optimierung",
      icon: Activity,
      component: ElectroMetaboGraph
    },
    {
      id: "copen-rate-generator",
      title: "Bruce Copen Raten-Generator",
      description: "Praktischer Generator für Copen-Raten mit Alphabet-Auswahl",
      icon: Calculator,
      isRoute: true,
      route: "/copen-generator"
    },
    {
      id: "import-center",
      title: "Daten Import Center",
      description: "PDF, Bilder und CSV-Dateien importieren und verarbeiten",
      icon: Upload,
      isRoute: true,
      route: "/import"
    },
    {
      id: "copen-algorithm",
      title: "Bruce Copen Algorithmus Visualisierung",
      description: "Grafische Darstellung des authentischen Copen-Algorithmus",
      icon: Zap,
      component: CopenAlgorithmVisualization
    },
    {
      id: "copen-algorithm-v2",
      title: "Bruce Copen Algorithmus Visualisierung V2",
      description: "Version 2 mit separater Datenbank und erweiterten Funktionen",
      icon: Zap,
      isRoute: true,
      route: "/copen-visualisierung-v2"
    },
    {
      id: "radionik-general",
      title: "Radionik Allgemein",
      description: "Grundlagen und Prinzipien der Radionik als energetische Heilmethode",
      icon: Waves,
      component: RadionikGeneral
    },
    {
      id: "radionik-copen",
      title: "Radionik nach Bruce Copen",
      description: "Spezifische Methoden und Geräte nach Bruce Copen",
      icon: Zap,
      component: RadionikCopen
    },
    {
      id: "harmonikale-baklayan",
      title: "Harmonikale Frequenzanwendung nach Alan Baklayan",
      description: "Frequenztherapie und harmonikale Prinzipien",
      icon: Sparkles,
      component: HarmonikaleBaklayan
    },
    {
      id: "bioresonanz-schmidt",
      title: "Bioresonanz nach Paul Schmidt - Rayonex",
      description: "Bioresonanz-Methoden und Rayonex-Technologie",
      icon: Heart,
      component: BioresonanzSchmidt
    },
    {
      id: "wellengenetik-garjajev",
      title: "Wellengenetik nach Dr. Pjotr Garjajev",
      description: "DNA-Wellengenetik und Quantenbiologie",
      icon: Dna,
      component: WellengenetikGarjajev
    },
    {
      id: "chakren-meridiane",
      title: "Erweiterte Theorien zu Chakren und Meridianen",
      description: "Energiezentren, Frequenzen und spirituelle Ebenen",
      icon: Brain,
      component: ChakrenMeridiane
    },
    {
      id: "theorien-broers",
      title: "Theorien und Prinzipien nach Dieter Broers",
      description: "Bewusstseinsforschung und elektromagnetische Felder",
      icon: BookOpen,
      component: TheorienBroers
    }
  ];

  const filteredTheories = theories.filter(theory =>
    theory.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    theory.description.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleTheoryClick = (theory: any) => {
    if (theory.isRoute && theory.route) {
      navigate(theory.route);
    } else {
      setSelectedTheory(theory.id);
    }
  };

  if (selectedTheory) {
    const theory = theories.find(t => t.id === selectedTheory);
    if (theory && theory.component) {
      const Component = theory.component;
      return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900">
          <div className="container mx-auto px-4 py-8">
            <Button 
              variant="outline" 
              onClick={() => setSelectedTheory(null)}
              className="mb-6 bg-white/10 border-white/20 text-white hover:bg-white/20"
            >
              ← Zurück zur Übersicht
            </Button>
            <Component />
          </div>
        </div>
      );
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900">
      <div className="container mx-auto px-4 py-8">
        <div className="absolute top-4 right-4">
          <UserMenu />
        </div>
        
        {/* Session Recovery Dashboard */}
        <div className="mb-8">
          <SessionRecoveryDashboard />
        </div>

        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold mb-6 text-white">
            Resonanz Forschungs-Explorer
          </h1>
          <p className="text-xl text-blue-200 mb-8 max-w-3xl mx-auto">
            Umfassende Sammlung energetischer und frequenzbasierter Theorien mit modernen Analyse-Tools
          </p>
          
          <div className="relative max-w-md mx-auto">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-blue-300 h-5 w-5" />
            <Input
              placeholder="Theorien durchsuchen..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-12 bg-white/10 border-white/20 text-white placeholder:text-white/50 text-lg py-3"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {filteredTheories.map((theory) => {
            const Icon = theory.icon;
            return (
              <Card 
                key={theory.id} 
                className="bg-white/10 border-white/20 backdrop-blur-sm hover:bg-white/15 transition-all duration-300 cursor-pointer group hover:scale-105"
                onClick={() => handleTheoryClick(theory)}
              >
                <CardHeader className="text-center">
                  <div className="flex justify-center mb-4">
                    <div className="p-4 bg-blue-500/20 rounded-full group-hover:bg-blue-400/30 transition-colors">
                      <Icon className="h-10 w-10 text-blue-300 group-hover:text-blue-200 transition-colors" />
                    </div>
                  </div>
                  <CardTitle className="text-xl text-white group-hover:text-blue-200 transition-colors">
                    {theory.title}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-blue-200 text-center text-base leading-relaxed">
                    {theory.description}
                  </CardDescription>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {filteredTheories.length === 0 && (
          <div className="text-center py-16">
            <p className="text-blue-200 text-xl">
              Keine Theorien gefunden für "{searchTerm}"
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Index;

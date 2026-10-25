import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { HardwareConfig, DEFAULT_HARDWARE_CONFIG } from "@/utils/hardwareAlgorithms";
import { Info } from "lucide-react";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";

interface PatientHardwareConfigProps {
  patientName: string;
  config?: {
    rateGenerator: HardwareConfig;
    analysis: HardwareConfig;
  };
  onChange: (config: { rateGenerator: HardwareConfig; analysis: HardwareConfig }) => void;
  rateGeneratorEnabled: boolean;
  analysisEnabled: boolean;
}

const algorithmInfo = {
  cpuQuantumJitter: {
    name: "CPU Quantum Jitter",
    boost: "+2-3%",
    description: "Nutzt Mikro-Variationen in CPU-Timing als Quantenrauschen"
  },
  ramEntropy: {
    name: "RAM Entropy",
    boost: "+1-2%",
    description: "Nutzt Speicher-Fragmentierung als Entropiequelle"
  },
  timeSourceCoherence: {
    name: "Time Source Coherence",
    boost: "+3-4%",
    description: "Synchronisiert mit System-Zeit-Drift (Kozyrev-Zeitfluss)"
  },
  gpuRenderingEntropy: {
    name: "GPU Rendering Entropy",
    boost: "+2-3%",
    description: "Nutzt GPU-Rendering-Variationen für morphogenetisches Feld"
  },
  networkLatency: {
    name: "Network Latency",
    boost: "+1-2%",
    description: "Nutzt Netzwerk-Jitter für Torsionsfeld-Modulation"
  },
  combinedAlgorithm: {
    name: "Combined Algorithm",
    boost: "+3-5%",
    description: "Gewichtete Kombination aller Metriken (synergistisch)"
  }
};

export const PatientHardwareConfig = ({
  patientName,
  config,
  onChange,
  rateGeneratorEnabled,
  analysisEnabled
}: PatientHardwareConfigProps) => {
  const currentConfig = config || {
    rateGenerator: DEFAULT_HARDWARE_CONFIG,
    analysis: DEFAULT_HARDWARE_CONFIG
  };

  const [rateGenConfig, setRateGenConfig] = useState<HardwareConfig>(currentConfig.rateGenerator);
  const [analysisConfig, setAnalysisConfig] = useState<HardwareConfig>(currentConfig.analysis);

  const updateRateGenConfig = (key: keyof HardwareConfig, value: 'auto' | 'on' | 'off') => {
    const newConfig = { ...rateGenConfig, [key]: value };
    setRateGenConfig(newConfig);
    // Immediate callback to parent
    onChange({ rateGenerator: newConfig, analysis: analysisConfig });
  };

  const updateAnalysisConfig = (key: keyof HardwareConfig, value: 'auto' | 'on' | 'off') => {
    const newConfig = { ...analysisConfig, [key]: value };
    setAnalysisConfig(newConfig);
    // Immediate callback to parent
    onChange({ rateGenerator: rateGenConfig, analysis: newConfig });
  };

  const AlgorithmSelect = ({ 
    algorithm, 
    value, 
    onChange, 
    disabled 
  }: { 
    algorithm: keyof typeof algorithmInfo; 
    value: 'auto' | 'on' | 'off'; 
    onChange: (value: 'auto' | 'on' | 'off') => void;
    disabled: boolean;
  }) => {
    const info = algorithmInfo[algorithm];
    
    return (
      <div className="flex items-center gap-2 mb-3">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <Label className="text-sm font-medium">{info.name}</Label>
            <span className="text-xs text-muted-foreground">{info.boost}</span>
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Info className="h-3 w-3 text-muted-foreground cursor-help" />
                </TooltipTrigger>
                <TooltipContent>
                  <p className="max-w-xs text-xs">{info.description}</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>
        </div>
        <Select 
          value={value} 
          onValueChange={(val) => {
            onChange(val as 'auto' | 'on' | 'off');
          }} 
          disabled={disabled}
        >
          <SelectTrigger className="w-28">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="off">AUS</SelectItem>
            <SelectItem value="auto">AUTO</SelectItem>
            <SelectItem value="on">AN</SelectItem>
          </SelectContent>
        </Select>
      </div>
    );
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Hardware-Algorithmen Konfiguration</CardTitle>
        <CardDescription>
          Patientenspezifische Feinsteuerung für {patientName}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Ratengenerator Gruppe */}
        <div className={!rateGeneratorEnabled ? "opacity-50" : ""}>
          <div className="mb-4">
            <h4 className="text-sm font-semibold mb-1">🔧 Ratengenerator</h4>
            <p className="text-xs text-muted-foreground">
              {rateGeneratorEnabled 
                ? "Globaler Schalter: AN - Konfiguration aktiv"
                : "Globaler Schalter: AUS - Konfiguration inaktiv"}
            </p>
          </div>
          
          <div className="space-y-2 pl-4 border-l-2 border-muted">
            {(Object.keys(algorithmInfo) as Array<keyof typeof algorithmInfo>).map((algo) => (
              <AlgorithmSelect
                key={`rategen-${algo}`}
                algorithm={algo}
                value={rateGenConfig[algo]}
                onChange={(value) => updateRateGenConfig(algo, value)}
                disabled={!rateGeneratorEnabled}
              />
            ))}
          </div>
        </div>

        {/* Datenbankanalyse Gruppe */}
        <div className={!analysisEnabled ? "opacity-50" : ""}>
          <div className="mb-4">
            <h4 className="text-sm font-semibold mb-1">📊 Datenbankanalyse</h4>
            <p className="text-xs text-muted-foreground">
              {analysisEnabled 
                ? "Globaler Schalter: AN - Konfiguration aktiv"
                : "Globaler Schalter: AUS - Konfiguration inaktiv"}
            </p>
          </div>
          
          <div className="space-y-2 pl-4 border-l-2 border-muted">
            {(Object.keys(algorithmInfo) as Array<keyof typeof algorithmInfo>).map((algo) => (
              <AlgorithmSelect
                key={`analysis-${algo}`}
                algorithm={algo}
                value={analysisConfig[algo]}
                onChange={(value) => updateAnalysisConfig(algo, value)}
                disabled={!analysisEnabled}
              />
            ))}
          </div>
        </div>

        <div className="mt-4 p-3 bg-muted/50 rounded-lg">
          <p className="text-xs text-muted-foreground">
            <strong>OFF:</strong> Algorithmus nie verwenden<br />
            <strong>AUTO:</strong> System wählt automatisch basierend auf Verfügbarkeit<br />
            <strong>AN:</strong> Algorithmus erzwingen (Fallback zu Pseudo-Werten)
          </p>
        </div>
      </CardContent>
    </Card>
  );
};

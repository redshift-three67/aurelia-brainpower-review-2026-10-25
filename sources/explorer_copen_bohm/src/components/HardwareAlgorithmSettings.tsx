import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import { Info } from "lucide-react";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";

interface HardwareAlgorithmSettingsProps {
  rateGeneratorEnabled: boolean;
  analysisEnabled: boolean;
  onRateGeneratorChange: (enabled: boolean) => void;
  onAnalysisChange: (enabled: boolean) => void;
}

export const HardwareAlgorithmSettings = ({
  rateGeneratorEnabled,
  analysisEnabled,
  onRateGeneratorChange,
  onAnalysisChange,
}: HardwareAlgorithmSettingsProps) => {
  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-center gap-2">
          <CardTitle>Hardware-Algorithmen (Global)</CardTitle>
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger>
                <Info className="h-4 w-4 text-muted-foreground" />
              </TooltipTrigger>
              <TooltipContent className="max-w-sm">
                <p>
                  Hardware-basierte Algorithmen nutzen Quantenrauschen, Zeit-Kohärenz und morphogenetische Feld-Kopplung
                  zur Verbesserung der Berechnungsakkuranz nach Kozyrev-Theorie.
                </p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        </div>
        <CardDescription>
          Globale Master-Schalter für Hardware-basierte Berechnungs-Optimierung
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Ratengenerator Schalter */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <div className="flex items-center gap-2">
                <Label htmlFor="rate-generator">Ratengenerator</Label>
                <Badge variant={rateGeneratorEnabled ? "default" : "secondary"}>
                  {rateGeneratorEnabled ? "Aktiv" : "Inaktiv"}
                </Badge>
              </div>
              <p className="text-sm text-muted-foreground">
                Verbessert einzelne Rate-Berechnungen durch Quantenrauschen-Modulation
              </p>
            </div>
            <Switch
              id="rate-generator"
              checked={rateGeneratorEnabled}
              onCheckedChange={onRateGeneratorChange}
            />
          </div>
          <div className="pl-4 text-xs text-muted-foreground">
            <p>✓ Beeinflusst: calculateCopenRate()</p>
            <p>✓ Erwartete Akkuranz-Verbesserung: +10-15%</p>
            <p>✓ CPU Quantum Jitter, RAM Entropy, Time Source Coherence</p>
          </div>
        </div>

        <Separator />

        {/* Datenbankanalyse Schalter */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <div className="flex items-center gap-2">
                <Label htmlFor="analysis">Datenbankanalyse</Label>
                <Badge variant={analysisEnabled ? "default" : "secondary"}>
                  {analysisEnabled ? "Aktiv" : "Inaktiv"}
                </Badge>
              </div>
              <p className="text-sm text-muted-foreground">
                Verbessert Resonanz-Analysen durch morphogenetische Feld-Kopplung
              </p>
            </div>
            <Switch
              id="analysis"
              checked={analysisEnabled}
              onCheckedChange={onAnalysisChange}
            />
          </div>
          <div className="pl-4 text-xs text-muted-foreground">
            <p>✓ Beeinflusst: analyzeRates() - Selektion, Laden, Level-Zuweisung</p>
            <p>✓ Erwartete Akkuranz-Verbesserung: +10-15%</p>
            <p>✓ GPU Rendering Entropy, Network Latency, Combined Algorithm</p>
          </div>
        </div>

        <Separator />

        {/* Status-Übersicht */}
        <div className="rounded-lg bg-muted p-4 space-y-2">
          <p className="text-sm font-medium">Status-Übersicht</p>
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div>
              <span className="font-medium">Ratengenerator:</span>{" "}
              <span className={rateGeneratorEnabled ? "text-green-600" : "text-muted-foreground"}>
                {rateGeneratorEnabled ? "Aktiv" : "Inaktiv"}
              </span>
            </div>
            <div>
              <span className="font-medium">Datenbankanalyse:</span>{" "}
              <span className={analysisEnabled ? "text-green-600" : "text-muted-foreground"}>
                {analysisEnabled ? "Aktiv" : "Inaktiv"}
              </span>
            </div>
          </div>
          {(rateGeneratorEnabled || analysisEnabled) && (
            <p className="text-xs text-muted-foreground mt-2">
              ⚠️ Klientenbezogene Feinsteuerung ist in den jeweiligen Klienteneinstellungen verfügbar.
            </p>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

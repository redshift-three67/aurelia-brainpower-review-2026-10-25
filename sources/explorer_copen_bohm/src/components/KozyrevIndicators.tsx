import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Zap, Clock, Atom, Network, Activity } from 'lucide-react';

interface CloudPatient {
  id: string;
  first_name: string;
  last_name: string;
  birth_date: string;
  birth_place: string;
}

interface KozyrevIndicatorsProps {
  selectedPatient: CloudPatient | null;
  wordEnergy: string;
  autoPotency: boolean;
}

const KozyrevIndicators: React.FC<KozyrevIndicatorsProps> = ({ 
  selectedPatient, 
  wordEnergy,
  autoPotency 
}) => {
  if (!selectedPatient || !autoPotency) return null;

  // Berechne Kozyrev-Parameter
  const birthDate = new Date(selectedPatient.birth_date);
  const now = new Date();
  const ageInDays = (now.getTime() - birthDate.getTime()) / (1000 * 60 * 60 * 24);
  
  // 7-Jahres-Rhythmus
  const sevenYearCycle = (ageInDays / 365.25) / 7;
  const cyclePhase = sevenYearCycle % 1;
  const timeFlowFactor = 1 + (0.15 * Math.sin(2 * Math.PI * sevenYearCycle));
  
  // Tageszeit
  const hourOfDay = now.getHours();
  const diurnalFactor = 1 + (0.1 * Math.sin(2 * Math.PI * (hourOfDay / 24)));
  
  // Morphische Resonanz (vereinfacht)
  const firstName = selectedPatient.first_name.toUpperCase();
  const nameVowels = (firstName.match(/[AEIOU]/g) || []).length;
  const nameConsonants = (firstName.match(/[BCDFGHJKLMNPQRSTVWXYZ]/g) || []).length;
  const phoneticRatio = nameVowels / (nameConsonants + 1);
  
  // Quantum Seed
  const t1 = performance.now();
  const t2 = performance.now();
  const quantumJitter = Math.abs(t2 - t1) * 1000000;
  
  const getPhaseColor = (phase: number): string => {
    if (phase < 0.25) return 'text-blue-600';
    if (phase < 0.5) return 'text-green-600';
    if (phase < 0.75) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getStrengthBadge = (value: number): { variant: 'default' | 'secondary' | 'destructive' | 'outline', text: string } => {
    if (value > 1.1) return { variant: 'default', text: 'Stark' };
    if (value > 0.95) return { variant: 'secondary', text: 'Optimal' };
    return { variant: 'outline', text: 'Schwach' };
  };

  return (
    <Card className="border-2 border-purple-200 bg-purple-50/50">
      <CardHeader>
        <CardTitle className="text-lg flex items-center gap-2">
          <Atom className="h-5 w-5 text-purple-600" />
          Kozyrev-Zeitenergie-Modulation 🌀
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
          {/* Zeitfluss-Faktor */}
          <div className="bg-white p-3 rounded-lg border border-purple-200">
            <div className="flex items-center gap-2 mb-1">
              <Clock className="h-4 w-4 text-purple-600" />
              <span className="text-xs font-semibold text-muted-foreground">Zeitfluss</span>
            </div>
            <div className="text-2xl font-bold text-purple-700">
              {timeFlowFactor.toFixed(3)}
            </div>
            <Badge {...getStrengthBadge(timeFlowFactor)} className="mt-1 text-xs">
              {getStrengthBadge(timeFlowFactor).text}
            </Badge>
          </div>

          {/* 7-Jahres-Zyklus */}
          <div className="bg-white p-3 rounded-lg border border-purple-200">
            <div className="flex items-center gap-2 mb-1">
              <Activity className="h-4 w-4 text-purple-600" />
              <span className="text-xs font-semibold text-muted-foreground">7-Jahr-Phase</span>
            </div>
            <div className={`text-2xl font-bold ${getPhaseColor(cyclePhase)}`}>
              {(cyclePhase * 100).toFixed(0)}%
            </div>
            <div className="text-xs text-muted-foreground mt-1">
              Zyklus {Math.floor(sevenYearCycle) + 1}
            </div>
          </div>

          {/* Tageszeit-Modulation */}
          <div className="bg-white p-3 rounded-lg border border-purple-200">
            <div className="flex items-center gap-2 mb-1">
              <Zap className="h-4 w-4 text-purple-600" />
              <span className="text-xs font-semibold text-muted-foreground">Tageszeit</span>
            </div>
            <div className="text-2xl font-bold text-purple-700">
              {diurnalFactor.toFixed(3)}
            </div>
            <div className="text-xs text-muted-foreground mt-1">
              {hourOfDay}:00 Uhr
            </div>
          </div>

          {/* Morphische Resonanz */}
          <div className="bg-white p-3 rounded-lg border border-purple-200">
            <div className="flex items-center gap-2 mb-1">
              <Network className="h-4 w-4 text-purple-600" />
              <span className="text-xs font-semibold text-muted-foreground">Morphisch</span>
            </div>
            <div className="text-2xl font-bold text-purple-700">
              {phoneticRatio.toFixed(2)}
            </div>
            <div className="text-xs text-muted-foreground mt-1">
              V:{nameVowels} K:{nameConsonants}
            </div>
          </div>
        </div>

        {/* Quantum Hardware Info */}
        <div className="mt-3 p-2 bg-gradient-to-r from-purple-100 to-blue-100 rounded text-xs">
          <div className="flex items-center justify-between">
            <span className="font-semibold">⚛️ Quantum-Hardware-Jitter:</span>
            <span className="font-mono">{quantumJitter.toFixed(2)} µs</span>
          </div>
          <div className="text-muted-foreground mt-1">
            CPU-Zeitstempel nutzen echte Quantenfluktuationen für Feinabstimmung
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default KozyrevIndicators;

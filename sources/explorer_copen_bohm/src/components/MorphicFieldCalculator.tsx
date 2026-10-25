import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Loader2, Zap, Activity, Waves, Target, TrendingUp } from 'lucide-react';
import { 
  calculateMorphicField, 
  generateDefaultQuantumStates,
  generateSequenceFromWord,
  type MorphicFieldResult,
  type GeometricForm,
  type IntentionType 
} from '@/utils/morphicFieldEngine';
import { Progress } from '@/components/ui/progress';

const MorphicFieldCalculator = () => {
  const [inputWord, setInputWord] = useState('');
  const [geometricForm, setGeometricForm] = useState<GeometricForm>('flower_of_life');
  const [intention, setIntention] = useState<IntentionType>('harmonization');
  const [useHardware, setUseHardware] = useState(true);
  const [isCalculating, setIsCalculating] = useState(false);
  const [result, setResult] = useState<MorphicFieldResult | null>(null);

  const handleCalculate = async () => {
    if (!inputWord.trim()) return;

    setIsCalculating(true);
    try {
      const numericalSequence = generateSequenceFromWord(inputWord);
      const quantumStates = generateDefaultQuantumStates(5);

      const fieldResult = await calculateMorphicField({
        quantumStates,
        numericalSequence,
        geometricForm,
        intention,
        useHardwareModulation: useHardware
      });

      setResult(fieldResult);
    } catch (error) {
      console.error('Fehler bei morphischer Feldberechnung:', error);
    } finally {
      setIsCalculating(false);
    }
  };

  const formatScientific = (num: number) => {
    if (num === 0) return '0';
    const exp = Math.floor(Math.log10(Math.abs(num)));
    const mantissa = (num / Math.pow(10, exp)).toFixed(3);
    return `${mantissa} × 10^${exp}`;
  };

  const formatNumber = (num: number) => {
    if (num < 0.01) return formatScientific(num);
    return num.toFixed(4);
  };

  return (
    <div className="space-y-6">
      <Card className="border-primary/20">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Waves className="w-6 h-6 text-primary" />
            Morphische Feld-Engine
          </CardTitle>
          <CardDescription>
            Quantenbasierte Berechnung nach Ψ_total(x,t) = Σn αn |ψn⟩ e^(-iEnt/ℏ) × C × G × I
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Input Section */}
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="word-input">Eingabe (Wort/Phrase)</Label>
              <Input
                id="word-input"
                placeholder="z.B. Heilung, Transformation, Liebe..."
                value={inputWord}
                onChange={(e) => setInputWord(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleCalculate()}
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="geometric-form">Geometrische Form (G)</Label>
                <Select value={geometricForm} onValueChange={(v) => setGeometricForm(v as GeometricForm)}>
                  <SelectTrigger id="geometric-form">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="tetrahedron">Tetraeder (Feuer)</SelectItem>
                    <SelectItem value="cube">Würfel (Erde)</SelectItem>
                    <SelectItem value="octahedron">Oktaeder (Luft)</SelectItem>
                    <SelectItem value="dodecahedron">Dodekaeder (Äther)</SelectItem>
                    <SelectItem value="icosahedron">Ikosaeder (Wasser)</SelectItem>
                    <SelectItem value="merkaba">Merkaba (Lichtkörper)</SelectItem>
                    <SelectItem value="torus">Torus (Selbsterhaltung)</SelectItem>
                    <SelectItem value="flower_of_life">Blume des Lebens</SelectItem>
                    <SelectItem value="sri_yantra">Sri Yantra</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="intention">Intention (I)</Label>
                <Select value={intention} onValueChange={(v) => setIntention(v as IntentionType)}>
                  <SelectTrigger id="intention">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="healing">Heilung</SelectItem>
                    <SelectItem value="manifestation">Manifestation</SelectItem>
                    <SelectItem value="protection">Schutz</SelectItem>
                    <SelectItem value="transformation">Transformation</SelectItem>
                    <SelectItem value="connection">Verbindung</SelectItem>
                    <SelectItem value="clearing">Klärung</SelectItem>
                    <SelectItem value="activation">Aktivierung</SelectItem>
                    <SelectItem value="harmonization">Harmonisierung</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="flex items-center justify-between p-4 bg-muted/50 rounded-lg">
              <div className="space-y-0.5">
                <Label htmlFor="hardware-switch" className="text-sm font-medium">
                  Hardware-Modulation
                </Label>
                <p className="text-xs text-muted-foreground">
                  Kozyrev-Torsionsfeld-Algorithmen aktivieren
                </p>
              </div>
              <Switch
                id="hardware-switch"
                checked={useHardware}
                onCheckedChange={setUseHardware}
              />
            </div>

            <Button 
              onClick={handleCalculate} 
              disabled={!inputWord.trim() || isCalculating}
              className="w-full"
              size="lg"
            >
              {isCalculating ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Berechne Morphisches Feld...
                </>
              ) : (
                <>
                  <Zap className="w-4 h-4 mr-2" />
                  Feld Berechnen
                </>
              )}
            </Button>
          </div>

          {/* Results Section */}
          {result && (
            <div className="space-y-4 pt-6 border-t">
              <h3 className="text-lg font-semibold flex items-center gap-2">
                <Activity className="w-5 h-5 text-primary" />
                Feldanalyse Ergebnis
              </h3>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Card className="bg-gradient-to-br from-primary/5 to-primary/10">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm font-medium text-muted-foreground">
                      Gesamt-Wellenfunktion Ψ
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-2xl font-bold text-primary">
                      {formatNumber(result.totalWaveFunction)}
                    </p>
                  </CardContent>
                </Card>

                <Card className="bg-gradient-to-br from-secondary/5 to-secondary/10">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm font-medium text-muted-foreground">
                      Feldstärke
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-2xl font-bold text-secondary">
                      {formatNumber(result.fieldStrength)}
                    </p>
                  </CardContent>
                </Card>
              </div>

              <Card>
                <CardHeader>
                  <CardTitle className="text-sm flex items-center gap-2">
                    <Target className="w-4 h-4" />
                    Kohärenz
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  <Progress value={result.coherence * 100} className="h-3" />
                  <p className="text-sm text-muted-foreground text-right">
                    {(result.coherence * 100).toFixed(1)}% Feldkohärenz
                  </p>
                </CardContent>
              </Card>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
                <Card className="bg-muted/30">
                  <CardContent className="pt-6">
                    <div className="space-y-1">
                      <p className="text-xs text-muted-foreground">Quanten-Komponente</p>
                      <p className="text-lg font-semibold">{formatNumber(result.quantumComponent)}</p>
                    </div>
                  </CardContent>
                </Card>

                <Card className="bg-muted/30">
                  <CardContent className="pt-6">
                    <div className="space-y-1">
                      <p className="text-xs text-muted-foreground">Numerischer Faktor (C)</p>
                      <p className="text-lg font-semibold">{formatNumber(result.numericalFactor)}</p>
                    </div>
                  </CardContent>
                </Card>

                <Card className="bg-muted/30">
                  <CardContent className="pt-6">
                    <div className="space-y-1">
                      <p className="text-xs text-muted-foreground">Geometrischer Faktor (G)</p>
                      <p className="text-lg font-semibold">{formatNumber(result.geometricFactor)}</p>
                    </div>
                  </CardContent>
                </Card>

                <Card className="bg-muted/30">
                  <CardContent className="pt-6">
                    <div className="space-y-1">
                      <p className="text-xs text-muted-foreground">Intentions-Faktor (I)</p>
                      <p className="text-lg font-semibold">{formatNumber(result.intentionFactor)}</p>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {result.hardwareFactor && (
                <Card className="border-primary/30 bg-primary/5">
                  <CardContent className="pt-6">
                    <div className="flex items-center justify-between">
                      <div className="space-y-1">
                        <p className="text-sm font-medium">Hardware-Modulation (Kozyrev)</p>
                        <p className="text-xs text-muted-foreground">Torsionsfeld-Verstärkung</p>
                      </div>
                      <div className="text-right">
                        <p className="text-2xl font-bold text-primary">
                          {formatNumber(result.hardwareFactor)}×
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}

              <Card className="bg-gradient-to-br from-accent/10 to-accent/5">
                <CardHeader>
                  <CardTitle className="text-sm flex items-center gap-2">
                    <TrendingUp className="w-4 h-4" />
                    Resonanzfrequenz
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-baseline gap-2">
                    <p className="text-3xl font-bold">{result.resonanceFrequency.toFixed(2)}</p>
                    <p className="text-sm text-muted-foreground">Hz</p>
                  </div>
                </CardContent>
              </Card>

              <div className="text-xs text-muted-foreground text-center pt-2">
                Berechnung durchgeführt am {new Date(result.timestamp).toLocaleString('de-DE')}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default MorphicFieldCalculator;

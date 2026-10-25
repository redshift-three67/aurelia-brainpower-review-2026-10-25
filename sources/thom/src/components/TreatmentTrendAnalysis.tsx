/**
 * Trend-Analyse Komponente
 * Zeigt Veränderungen nach Behandlungssequenz
 */
import { useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { TrendingUp, TrendingDown, Minus, Activity, Clock, Target } from 'lucide-react';

interface DimensionChange {
  name: string;
  before: number;
  after: number;
  change: number;
  percentage: number;
}

interface TreatmentTrendProps {
  beforeDimensions: number[];
  afterDimensions: number[];
  treatmentDuration: number;
  cyclesCompleted: number;
  pointsProcessed: number;
}

const DIMENSION_NAMES = ['Körperlich', 'Emotional', 'Mental', 'Energie', 'Stress'];

export function TreatmentTrendAnalysis({
  beforeDimensions,
  afterDimensions,
  treatmentDuration,
  cyclesCompleted,
  pointsProcessed,
}: TreatmentTrendProps) {
  const dimensionChanges = useMemo((): DimensionChange[] => {
    return DIMENSION_NAMES.map((name, index) => {
      const before = beforeDimensions[index] || 50;
      const after = afterDimensions[index] || 50;
      const change = after - before;
      const percentage = before > 0 ? (change / before) * 100 : 0;
      return { name, before, after, change, percentage };
    });
  }, [beforeDimensions, afterDimensions]);

  const overallImprovement = useMemo(() => {
    // Stress sollte sinken, andere sollten sich der Mitte nähern
    const stressImprovement = dimensionChanges[4] ? -dimensionChanges[4].change : 0;
    
    // Für andere Dimensionen: Nähe zu 50 ist besser
    const balanceImprovement = dimensionChanges.slice(0, 4).reduce((sum, d) => {
      const beforeDistance = Math.abs(d.before - 50);
      const afterDistance = Math.abs(d.after - 50);
      return sum + (beforeDistance - afterDistance);
    }, 0);

    return (stressImprovement * 0.3 + balanceImprovement * 0.175) / 5;
  }, [dimensionChanges]);

  const getTrendIcon = (change: number, isStress: boolean = false) => {
    // Für Stress ist Abnahme gut, für andere ist Bewegung zur Mitte gut
    if (Math.abs(change) < 2) {
      return <Minus className="w-4 h-4 text-muted-foreground" />;
    }
    if (isStress) {
      return change < 0 
        ? <TrendingDown className="w-4 h-4 text-green-500" />
        : <TrendingUp className="w-4 h-4 text-red-500" />;
    }
    return change > 0 
      ? <TrendingUp className="w-4 h-4 text-primary" />
      : <TrendingDown className="w-4 h-4 text-muted-foreground" />;
  };

  const getChangeColor = (change: number, isStress: boolean = false) => {
    if (Math.abs(change) < 2) return 'text-muted-foreground';
    if (isStress) {
      return change < 0 ? 'text-green-500' : 'text-red-500';
    }
    return 'text-primary';
  };

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <Card className="border-primary/20 bg-gradient-to-br from-primary/5 to-secondary/5">
      <CardHeader className="pb-4">
        <CardTitle className="flex items-center gap-2 text-lg">
          <Activity className="w-5 h-5 text-primary" />
          Behandlungs-Trendanalyse
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Zusammenfassung */}
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center p-3 bg-background/50 rounded-lg">
            <Clock className="w-5 h-5 mx-auto mb-1 text-muted-foreground" />
            <div className="text-lg font-semibold">{formatDuration(treatmentDuration)}</div>
            <div className="text-xs text-muted-foreground">Behandlungsdauer</div>
          </div>
          <div className="text-center p-3 bg-background/50 rounded-lg">
            <Target className="w-5 h-5 mx-auto mb-1 text-muted-foreground" />
            <div className="text-lg font-semibold">{pointsProcessed}</div>
            <div className="text-xs text-muted-foreground">Punkte behandelt</div>
          </div>
          <div className="text-center p-3 bg-background/50 rounded-lg">
            <Activity className="w-5 h-5 mx-auto mb-1 text-muted-foreground" />
            <div className="text-lg font-semibold">{cyclesCompleted}</div>
            <div className="text-xs text-muted-foreground">Zyklen</div>
          </div>
        </div>

        {/* Gesamt-Verbesserung */}
        <div className="flex items-center justify-between p-4 bg-background/80 rounded-lg border">
          <span className="font-medium">Gesamt-Harmonisierung</span>
          <Badge variant={overallImprovement > 0 ? 'default' : 'secondary'}>
            {overallImprovement > 0 ? '+' : ''}{overallImprovement.toFixed(1)}%
          </Badge>
        </div>

        {/* Dimensions-Änderungen */}
        <div className="space-y-3">
          <h4 className="text-sm font-medium text-muted-foreground">Dimensionen</h4>
          {dimensionChanges.map((dim, index) => (
            <div key={dim.name} className="flex items-center gap-3 p-3 bg-background/50 rounded-lg">
              <div className="w-24 text-sm font-medium">{dim.name}</div>
              
              <div className="flex-1 flex items-center gap-2">
                <div className="w-16 text-right text-sm text-muted-foreground">
                  {dim.before.toFixed(0)}%
                </div>
                <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-gradient-to-r from-muted-foreground to-primary transition-all"
                    style={{ width: `${dim.after}%` }}
                  />
                </div>
                <div className="w-16 text-sm font-medium">
                  {dim.after.toFixed(0)}%
                </div>
              </div>

              <div className={`flex items-center gap-1 w-20 justify-end ${getChangeColor(dim.change, index === 4)}`}>
                {getTrendIcon(dim.change, index === 4)}
                <span className="text-sm font-medium">
                  {dim.change > 0 ? '+' : ''}{dim.change.toFixed(1)}
                </span>
              </div>
            </div>
          ))}
        </div>

        {/* Empfehlungen */}
        <div className="p-4 bg-primary/10 rounded-lg border border-primary/20">
          <h4 className="text-sm font-medium mb-2">Empfehlung</h4>
          <p className="text-sm text-muted-foreground">
            {overallImprovement > 5 
              ? 'Deutliche Verbesserung der Feldbalance. Empfohlen: Stabilisierungsphase vor nächster Behandlung.'
              : overallImprovement > 0 
                ? 'Leichte Harmonisierung erkennbar. Eine Folgebehandlung nach 24h kann die Wirkung verstärken.'
                : 'Geringe Veränderung. Überprüfen Sie die Meridian-Auswahl oder erhöhen Sie die Behandlungsdauer.'}
          </p>
        </div>
      </CardContent>
    </Card>
  );
}

export default TreatmentTrendAnalysis;

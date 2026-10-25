/**
 * BifurcationDetector – Echtzeit-Bifurkationsdetektion nach René Thom & Scheffer et al.
 * 
 * Implementiert drei Frühwarnsignale für nahende Zustandsübergänge:
 * 1. Varianz-Analyse (steigende Varianz → nahende Bifurkation)
 * 2. Autokorrelation (steigende AC → kritische Verlangsamung)
 * 3. Flickering-Detektion (schnelle Oszillation zwischen Attraktorbecken)
 * 
 * Basierend auf: Scheffer et al., "Early-warning signals for critical transitions" (Nature, 2009)
 * Mathematische Grundlage: V(x; a, b) = x⁴ + ax² + bx (Kuspen-Katastrophe)
 */

// ─── Typen ──────────────────────────────────────────────────────────

export interface BifurcationEvent {
  type: BifurcationType;
  risk: number;                    // 0–1 Gesamtrisiko
  varianceScore: number;           // Normalisierte Varianz
  autocorrelationScore: number;    // Lag-1 Autokorrelation
  flickeringScore: number;         // Flickering-Intensität
  estimatedTimeToEvent: number;    // Geschätzte Sekunden bis Bifurkation
  recommendedAction: RecommendedAction;
  affectedDimensions: number[];    // Indizes der kritischen Dimensionen
  timestamp: Date;
}

export type BifurcationType =
  | 'cusp_bifurcation'        // Kuspen-Katastrophe (bistabil)
  | 'fold_bifurcation'        // Falten-Katastrophe (Schwelle)
  | 'critical_slowing_down'   // Vorbote, noch keine volle Bifurkation
  | 'flickering';             // Schnelles Pendeln zwischen Zuständen

export type RecommendedAction =
  | 'stabilize_with_10hz_alpha'
  | 'reduce_frequency_intensity'
  | 'apply_schumann_grounding'
  | 'pause_and_reassess'
  | 'continue_monitoring';

// Konfigurierbare Schwellenwerte
export interface BifurcationConfig {
  windowSize: number;              // Analyse-Fenster (Samples)
  varianceThreshold: number;       // Ab wann Varianz kritisch ist (0–1)
  autocorrelationThreshold: number;// Ab wann AC kritisch ist (0–1)
  flickeringThreshold: number;     // Ab wann Flickering erkannt wird
  samplingIntervalMs: number;      // Erwartetes Sampling-Intervall
  dimensionWeights: number[];      // Gewichtung der 5 Dimensionen
}

// Statistiken für Monitoring
export interface DetectorStatistics {
  samplesCollected: number;
  eventsDetected: number;
  currentVariance: number[];
  currentAutocorrelation: number[];
  currentFlickering: number;
  isWarning: boolean;
  riskTrend: 'increasing' | 'decreasing' | 'stable';
  lastEvent: BifurcationEvent | null;
}

// ─── Standardkonfiguration ──────────────────────────────────────────

const DEFAULT_CONFIG: BifurcationConfig = {
  windowSize: 32,
  varianceThreshold: 0.5,
  autocorrelationThreshold: 0.8,
  flickeringThreshold: 3,
  samplingIntervalMs: 250,
  // Physical, Emotional, Mental, Energy, Stress
  dimensionWeights: [0.2, 0.2, 0.15, 0.25, 0.2],
};

// ─── Hauptklasse ────────────────────────────────────────────────────

export class BifurcationDetector {
  private history: number[][] = [];
  private config: BifurcationConfig;
  private eventCount = 0;
  private lastEvent: BifurcationEvent | null = null;
  private riskHistory: number[] = [];

  constructor(config?: Partial<BifurcationConfig>) {
    this.config = { ...DEFAULT_CONFIG, ...config };
  }

  // ─── Hauptmethode: Vektor analysieren ───────────────────────────

  /**
   * Analysiert einen neuen Zustandsvektor auf Bifurkationssignale.
   * Muss mit jedem neuen Sample (z.B. alle 250ms) aufgerufen werden.
   */
  detect(currentVector: number[]): BifurcationEvent | null {
    this.history.push([...currentVector]);

    // Fenster aufbauen
    if (this.history.length < this.config.windowSize) return null;

    // Sliding Window
    while (this.history.length > this.config.windowSize) {
      this.history.shift();
    }

    // 1. Varianz-Analyse pro Dimension
    const variances = this.calculateDimensionVariances();
    const weightedVariance = this.weightedMean(variances);

    // 2. Autokorrelation (Lag-1) pro Dimension
    const autocorrelations = this.calculateDimensionAutocorrelations();
    const weightedAC = this.weightedMean(autocorrelations);

    // 3. Flickering-Detektion
    const flickeringScore = this.detectFlickering();

    // Risiko-Berechnung
    const risk = this.calculateRisk(weightedVariance, weightedAC, flickeringScore);
    this.riskHistory.push(risk);
    if (this.riskHistory.length > 64) this.riskHistory.shift();

    // Kritische Dimensionen identifizieren
    const affectedDimensions = this.identifyCriticalDimensions(variances, autocorrelations);

    // Bifurkationstyp und Empfehlung bestimmen
    const event = this.evaluateThresholds(
      weightedVariance,
      weightedAC,
      flickeringScore,
      risk,
      affectedDimensions
    );

    if (event) {
      this.eventCount++;
      this.lastEvent = event;
    }

    return event;
  }

  // ─── Varianz-Analyse ────────────────────────────────────────────

  /**
   * Berechnet die Varianz jeder Dimension über das Analysefenster.
   * Steigende Varianz = System nähert sich Bifurkation (Scheffer 2009).
   * 
   * σ²(d) = (1/N) Σ(x_i,d - μ_d)²
   */
  private calculateDimensionVariances(): number[] {
    const numDims = this.history[0].length;
    const variances: number[] = [];

    for (let d = 0; d < numDims; d++) {
      const values = this.history.map(v => v[d]);
      const mean = values.reduce((s, v) => s + v, 0) / values.length;
      const variance = values.reduce((s, v) => s + (v - mean) ** 2, 0) / values.length;
      // Normalisierung: Werte ∈ [-1,1] → max theoretische Varianz = 1
      variances.push(Math.min(variance, 1));
    }

    return variances;
  }

  // ─── Autokorrelation (Lag-1) ────────────────────────────────────

  /**
   * Lag-1 Autokorrelation pro Dimension.
   * Steigende Autokorrelation = kritische Verlangsamung (critical slowing down).
   * Das System braucht länger, um zu seinem Attraktor zurückzukehren.
   * 
   * AC(d) = Σ((x_t,d - μ)(x_{t+1},d - μ)) / Σ(x_t,d - μ)²
   */
  private calculateDimensionAutocorrelations(): number[] {
    const numDims = this.history[0].length;
    const autocorrelations: number[] = [];

    for (let d = 0; d < numDims; d++) {
      const values = this.history.map(v => v[d]);
      const mean = values.reduce((s, v) => s + v, 0) / values.length;

      let numerator = 0;
      let denominator = 0;

      for (let t = 0; t < values.length - 1; t++) {
        const dev = values[t] - mean;
        const devNext = values[t + 1] - mean;
        numerator += dev * devNext;
        denominator += dev * dev;
      }

      // Vermeide Division durch 0 bei konstantem Signal
      const ac = denominator > 1e-10 ? numerator / denominator : 0;
      // Clamp auf [0, 1] – negative AC ist unkritisch
      autocorrelations.push(Math.max(0, Math.min(ac, 1)));
    }

    return autocorrelations;
  }

  // ─── Flickering-Detektion ───────────────────────────────────────

  /**
   * Erkennt schnelles Oszillieren zwischen zwei Attraktorbecken.
   * Flickering = häufige Vorzeichenwechsel in der Ableitung.
   * 
   * Gezählt werden Richtungswechsel (Δx wechselt Vorzeichen)
   * über alle Dimensionen, normalisiert auf die Fenstergröße.
   */
  private detectFlickering(): number {
    const numDims = this.history[0].length;
    let totalReversals = 0;

    for (let d = 0; d < numDims; d++) {
      const values = this.history.map(v => v[d]);
      let reversals = 0;

      for (let t = 2; t < values.length; t++) {
        const prevDelta = values[t - 1] - values[t - 2];
        const currDelta = values[t] - values[t - 1];
        // Vorzeichenwechsel der Ableitung
        if (prevDelta * currDelta < 0) {
          reversals++;
        }
      }

      totalReversals += reversals;
    }

    // Normalisierung: max mögliche Reversals = (window-2) * numDims
    const maxReversals = (this.config.windowSize - 2) * numDims;
    return maxReversals > 0 ? totalReversals / maxReversals : 0;
  }

  // ─── Risiko-Berechnung ──────────────────────────────────────────

  /**
   * Gesamtrisiko als gewichtete Kombination der drei Indikatoren.
   * 
   * Gewichtung nach Scheffer et al.:
   * - Varianz:         40% (stärkstes Frühwarnsignal)
   * - Autokorrelation: 40% (kritische Verlangsamung)
   * - Flickering:      20% (Spätsignal, aber spezifisch)
   */
  private calculateRisk(variance: number, autocorrelation: number, flickering: number): number {
    const normalizedVariance = Math.min(variance / this.config.varianceThreshold, 1);
    const normalizedAC = Math.min(autocorrelation / this.config.autocorrelationThreshold, 1);
    const normalizedFlicker = Math.min(flickering * 10 / this.config.flickeringThreshold, 1);

    return 0.4 * normalizedVariance + 0.4 * normalizedAC + 0.2 * normalizedFlicker;
  }

  // ─── Schwellenwert-Auswertung ───────────────────────────────────

  private evaluateThresholds(
    variance: number,
    autocorrelation: number,
    flickering: number,
    risk: number,
    affectedDimensions: number[]
  ): BifurcationEvent | null {
    // Unterhalb jeglicher Schwelle → kein Event
    if (risk < 0.3) return null;

    let type: BifurcationType;
    let action: RecommendedAction;

    if (variance > this.config.varianceThreshold && autocorrelation > this.config.autocorrelationThreshold) {
      if (flickering > 0.5) {
        // Volles Bifurkationsmuster: hohe Varianz + hohe AC + Flickering
        type = 'cusp_bifurcation';
        action = 'pause_and_reassess';
      } else {
        // Klassische kritische Verlangsamung ohne Flickering
        type = 'fold_bifurcation';
        action = 'stabilize_with_10hz_alpha';
      }
    } else if (flickering > 0.6) {
      // Flickering dominant → System pendelt zwischen Becken
      type = 'flickering';
      action = 'apply_schumann_grounding';
    } else if (autocorrelation > this.config.autocorrelationThreshold * 0.7) {
      // Vorbote: AC steigt, aber Varianz noch nicht kritisch
      type = 'critical_slowing_down';
      action = 'reduce_frequency_intensity';
    } else {
      // Schwacher Anstieg → nur Monitoring
      type = 'critical_slowing_down';
      action = 'continue_monitoring';
    }

    return {
      type,
      risk,
      varianceScore: variance,
      autocorrelationScore: autocorrelation,
      flickeringScore: flickering,
      estimatedTimeToEvent: this.estimateTimeToEvent(),
      recommendedAction: action,
      affectedDimensions,
      timestamp: new Date(),
    };
  }

  // ─── Zeitschätzung bis Bifurkation ──────────────────────────────

  /**
   * Schätzt die verbleibende Zeit bis zur Bifurkation basierend
   * auf der Steigung des Risiko-Trends.
   * 
   * Methode: Lineare Extrapolation des Risiko-Anstiegs auf risk = 1.0
   */
  private estimateTimeToEvent(): number {
    if (this.riskHistory.length < 4) return Infinity;

    // Lineare Regression über letzte 16 Samples (oder weniger)
    const recentRisk = this.riskHistory.slice(-16);
    const n = recentRisk.length;

    let sumX = 0, sumY = 0, sumXY = 0, sumXX = 0;
    for (let i = 0; i < n; i++) {
      sumX += i;
      sumY += recentRisk[i];
      sumXY += i * recentRisk[i];
      sumXX += i * i;
    }

    const slope = (n * sumXY - sumX * sumY) / (n * sumXX - sumX * sumX);

    // Wenn Risiko nicht steigt → kein absehbares Event
    if (slope <= 0.001) return Infinity;

    const currentRisk = recentRisk[n - 1];
    const samplesUntilEvent = (1.0 - currentRisk) / slope;
    const secondsUntilEvent = (samplesUntilEvent * this.config.samplingIntervalMs) / 1000;

    return Math.max(0, secondsUntilEvent);
  }

  // ─── Kritische Dimensionen ──────────────────────────────────────

  /**
   * Identifiziert welche Dimensionen am stärksten zur Instabilität beitragen.
   * Gibt Indizes zurück, sortiert nach Kritikalität.
   */
  private identifyCriticalDimensions(variances: number[], autocorrelations: number[]): number[] {
    const scores = variances.map((v, i) => ({
      index: i,
      score: v * 0.5 + (autocorrelations[i] || 0) * 0.5,
    }));

    return scores
      .sort((a, b) => b.score - a.score)
      .filter(s => s.score > 0.2)
      .map(s => s.index);
  }

  // ─── Gewichteter Mittelwert ─────────────────────────────────────

  private weightedMean(values: number[]): number {
    const weights = this.config.dimensionWeights;
    let sum = 0;
    let weightSum = 0;

    for (let i = 0; i < values.length; i++) {
      const w = weights[i] ?? (1 / values.length);
      sum += values[i] * w;
      weightSum += w;
    }

    return weightSum > 0 ? sum / weightSum : 0;
  }

  // ─── Öffentliche API ────────────────────────────────────────────

  /** Statistiken für Dashboard / Monitoring */
  getStatistics(): DetectorStatistics {
    const variances = this.history.length >= this.config.windowSize
      ? this.calculateDimensionVariances()
      : [];
    const autocorrelations = this.history.length >= this.config.windowSize
      ? this.calculateDimensionAutocorrelations()
      : [];
    const flickering = this.history.length >= this.config.windowSize
      ? this.detectFlickering()
      : 0;

    // Trend aus letzten 8 Risiko-Werten
    let riskTrend: 'increasing' | 'decreasing' | 'stable' = 'stable';
    if (this.riskHistory.length >= 8) {
      const recent = this.riskHistory.slice(-8);
      const firstHalf = recent.slice(0, 4).reduce((s, v) => s + v, 0) / 4;
      const secondHalf = recent.slice(4).reduce((s, v) => s + v, 0) / 4;
      const diff = secondHalf - firstHalf;
      if (diff > 0.05) riskTrend = 'increasing';
      else if (diff < -0.05) riskTrend = 'decreasing';
    }

    return {
      samplesCollected: this.history.length,
      eventsDetected: this.eventCount,
      currentVariance: variances,
      currentAutocorrelation: autocorrelations,
      currentFlickering: flickering,
      isWarning: this.riskHistory.length > 0 && this.riskHistory[this.riskHistory.length - 1] > 0.3,
      riskTrend,
      lastEvent: this.lastEvent,
    };
  }

  /** Detektor zurücksetzen (z.B. bei neuem Klient) */
  reset(): void {
    this.history = [];
    this.riskHistory = [];
    this.eventCount = 0;
    this.lastEvent = null;
  }

  /** Konfiguration dynamisch anpassen */
  updateConfig(config: Partial<BifurcationConfig>): void {
    this.config = { ...this.config, ...config };
  }

  /** Aktuelle Konfiguration lesen */
  getConfig(): Readonly<BifurcationConfig> {
    return { ...this.config };
  }

  /** Vollständige Trajektorie-Historie */
  getHistory(): ReadonlyArray<readonly number[]> {
    return this.history;
  }

  /** Aktuelles Risiko-Level (0–1) */
  getCurrentRisk(): number {
    return this.riskHistory.length > 0
      ? this.riskHistory[this.riskHistory.length - 1]
      : 0;
  }
}

export default BifurcationDetector;

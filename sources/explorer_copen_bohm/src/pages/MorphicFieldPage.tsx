import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Home, BookOpen } from 'lucide-react';
import ClientFieldCalculator from '@/components/ClientFieldCalculator';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import SessionRecoveryDashboard from '@/components/SessionRecoveryDashboard';

const MorphicFieldPage = () => {
  const [showTheory, setShowTheory] = useState(false);
  const [selectedPatientId, setSelectedPatientId] = useState<string | null>(null);

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-primary/5">
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <Link to="/">
              <Button variant="outline" size="icon">
                <Home className="w-4 h-4" />
              </Button>
            </Link>
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
                Morphisches Feld-Engine
              </h1>
              <p className="text-sm text-muted-foreground mt-1">
                Quantenbasierte Feldberechnung nach erweiterter Wellenfunktion
              </p>
            </div>
          </div>
          <Button
            variant={showTheory ? "default" : "outline"}
            onClick={() => setShowTheory(!showTheory)}
          >
            <BookOpen className="w-4 h-4 mr-2" />
            {showTheory ? 'Theorie ausblenden' : 'Theorie anzeigen'}
          </Button>
        </div>

        {/* Theory Section */}
        {showTheory && (
          <Card className="mb-8 border-primary/20">
            <CardHeader>
              <CardTitle>Theoretische Grundlage</CardTitle>
              <CardDescription>
                Die Morphische Feld-Engine basiert auf einer erweiterten quantenmechanischen Wellenfunktion
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="bg-muted/50 p-6 rounded-lg">
                <h3 className="font-mono text-lg mb-4 text-center">
                  Ψ<sub>total</sub>(x,t) = Σ<sub>n</sub> α<sub>n</sub> |ψ<sub>n</sub>⟩ e<sup>(-iE<sub>n</sub>t/ℏ)</sup> × C(numerical_sequence) × G(geometric_forms) × I(intention)
                </h3>
              </div>

              <Accordion type="single" collapsible className="w-full">
                <AccordionItem value="quantum">
                  <AccordionTrigger>
                    <span className="font-semibold">Quantenmechanische Komponente: Σ<sub>n</sub> α<sub>n</sub> |ψ<sub>n</sub>⟩ e<sup>(-iE<sub>n</sub>t/ℏ)</sup></span>
                  </AccordionTrigger>
                  <AccordionContent className="space-y-2 text-sm">
                    <p>
                      Die Superposition von Quantenzuständen beschreibt das fundamentale Wellenverhalten des morphischen Feldes:
                    </p>
                    <ul className="list-disc pl-6 space-y-1">
                      <li><strong>α<sub>n</sub></strong>: Amplituden-Koeffizient für Zustand n</li>
                      <li><strong>|ψ<sub>n</sub>⟩</strong>: Quantenzustand mit Energie E<sub>n</sub></li>
                      <li><strong>e<sup>(-iE<sub>n</sub>t/ℏ)</sup></strong>: Zeitliche Evolution (Phasenrotation)</li>
                      <li><strong>ℏ</strong>: Reduzierte Planck-Konstante (1.054×10<sup>-34</sup> J·s)</li>
                    </ul>
                    <p className="pt-2 text-muted-foreground">
                      Diese Komponente erzeugt Interferenzmuster und Resonanzphänomene, die das Fundament der morphischen Feldwirkung bilden.
                    </p>
                  </AccordionContent>
                </AccordionItem>

                <AccordionItem value="numerical">
                  <AccordionTrigger>
                    <span className="font-semibold">Numerischer Faktor: C(numerical_sequence)</span>
                  </AccordionTrigger>
                  <AccordionContent className="space-y-2 text-sm">
                    <p>
                      Verarbeitet numerische Sequenzen zur Feldmodulation:
                    </p>
                    <ul className="list-disc pl-6 space-y-1">
                      <li><strong>Copen-Raten</strong>: Bruce Copen Algorithmus für Wortenergien</li>
                      <li><strong>Harmonisches Mittel</strong>: Kohärenz der Sequenz</li>
                      <li><strong>Geometrisches Mittel</strong>: Resonanzstärke</li>
                    </ul>
                    <p className="pt-2 text-muted-foreground">
                      Die Engine konvertiert Eingabewörter automatisch in numerische Sequenzen mittels des V4-Algorithmus.
                    </p>
                  </AccordionContent>
                </AccordionItem>

                <AccordionItem value="geometric">
                  <AccordionTrigger>
                    <span className="font-semibold">Geometrischer Faktor: G(geometric_forms)</span>
                  </AccordionTrigger>
                  <AccordionContent className="space-y-2 text-sm">
                    <p>
                      Heilige Geometrie als Feldstruktur-Verstärker:
                    </p>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2 py-2">
                      <div className="bg-muted/30 p-3 rounded">
                        <strong>Platonische Körper:</strong>
                        <ul className="list-none pl-2 text-xs space-y-0.5 mt-1">
                          <li>• Tetraeder (φ ≈ 1.618) - Feuer</li>
                          <li>• Würfel (√3 ≈ 1.732) - Erde</li>
                          <li>• Oktaeder (2.000) - Luft</li>
                          <li>• Dodekaeder (φ² ≈ 2.618) - Äther</li>
                          <li>• Ikosaeder (√5 ≈ 2.236) - Wasser</li>
                        </ul>
                      </div>
                      <div className="bg-muted/30 p-3 rounded">
                        <strong>Erweiterte Geometrie:</strong>
                        <ul className="list-none pl-2 text-xs space-y-0.5 mt-1">
                          <li>• Merkaba (π ≈ 3.141) - Lichtkörper</li>
                          <li>• Torus (√2 ≈ 1.414) - Selbsterhaltung</li>
                          <li>• Blume des Lebens (e ≈ 2.718)</li>
                          <li>• Sri Yantra (3.000) - Trinität</li>
                        </ul>
                      </div>
                    </div>
                  </AccordionContent>
                </AccordionItem>

                <AccordionItem value="intention">
                  <AccordionTrigger>
                    <span className="font-semibold">Intentions-Faktor: I(intention)</span>
                  </AccordionTrigger>
                  <AccordionContent className="space-y-2 text-sm">
                    <p>
                      Bewusste Intention als Feldmodulator:
                    </p>
                    <div className="grid grid-cols-2 gap-2 py-2 text-xs">
                      <div className="bg-muted/30 p-2 rounded">
                        <strong>Heilung</strong> (√φ ≈ 1.272)<br/>
                        <span className="text-muted-foreground">Natürliche Wiederherstellung</span>
                      </div>
                      <div className="bg-muted/30 p-2 rounded">
                        <strong>Manifestation</strong> (φ ≈ 1.618)<br/>
                        <span className="text-muted-foreground">Goldene Schöpfung</span>
                      </div>
                      <div className="bg-muted/30 p-2 rounded">
                        <strong>Schutz</strong> (√2 ≈ 1.414)<br/>
                        <span className="text-muted-foreground">Stabiler Schild</span>
                      </div>
                      <div className="bg-muted/30 p-2 rounded">
                        <strong>Transformation</strong> (√5 ≈ 2.236)<br/>
                        <span className="text-muted-foreground">Dynamische Veränderung</span>
                      </div>
                      <div className="bg-muted/30 p-2 rounded">
                        <strong>Verbindung</strong> (2.000)<br/>
                        <span className="text-muted-foreground">Perfekte Einheit</span>
                      </div>
                      <div className="bg-muted/30 p-2 rounded">
                        <strong>Klärung</strong> (√3 ≈ 1.732)<br/>
                        <span className="text-muted-foreground">Reinigung</span>
                      </div>
                      <div className="bg-muted/30 p-2 rounded">
                        <strong>Aktivierung</strong> (e ≈ 2.718)<br/>
                        <span className="text-muted-foreground">Natürliches Erwachen</span>
                      </div>
                      <div className="bg-muted/30 p-2 rounded">
                        <strong>Harmonisierung</strong> (φ ≈ 1.618)<br/>
                        <span className="text-muted-foreground">Perfekte Balance</span>
                      </div>
                    </div>
                  </AccordionContent>
                </AccordionItem>

                <AccordionItem value="hardware">
                  <AccordionTrigger>
                    <span className="font-semibold">Hardware-Modulation (Kozyrev-Torsionsfelder)</span>
                  </AccordionTrigger>
                  <AccordionContent className="space-y-2 text-sm">
                    <p>
                      Optionale Integration von Kozyrev-basierten Hardware-Algorithmen:
                    </p>
                    <ul className="list-disc pl-6 space-y-1">
                      <li><strong>CPU Quantum Jitter</strong>: Zeitliche Mikrofluktuationen</li>
                      <li><strong>RAM Entropy</strong>: Speicher-Kohärenz</li>
                      <li><strong>Time Source Coherence</strong>: Zeit-Drift-Messung</li>
                      <li><strong>GPU Rendering Entropy</strong>: Grafische Entropie</li>
                      <li><strong>Network Latency</strong>: Kommunikations-Jitter</li>
                    </ul>
                    <p className="pt-2 text-muted-foreground">
                      Diese Metriken modulieren das Feld basierend auf der aktuellen System-Kohärenz und simulieren Torsionsfeld-Effekte.
                    </p>
                  </AccordionContent>
                </AccordionItem>

                <AccordionItem value="integration">
                  <AccordionTrigger>
                    <span className="font-semibold">Integration mit bestehenden Systemen</span>
                  </AccordionTrigger>
                  <AccordionContent className="space-y-2 text-sm">
                    <p>
                      Die Morphische Feld-Engine integriert nahtlos mit:
                    </p>
                    <ul className="list-disc pl-6 space-y-1">
                      <li><strong>Bruce Copen Algorithmus V4</strong>: Numerische Sequenzgenerierung</li>
                      <li><strong>Kozyrev-Dioden</strong>: Hardware-Torsionsfeld-Modulation</li>
                      <li><strong>13-Ebenen-Resonanzmodell</strong>: Kompatible Frequenzbereiche</li>
                      <li><strong>Morphogenetische Feldtheorie</strong>: Sheldrake-Integration</li>
                    </ul>
                    <p className="pt-2 bg-primary/10 p-3 rounded">
                      <strong>Anwendungsgebiete:</strong> Resonanztherapie, Fernbehandlung, Intentionsarbeit, 
                      Morphische Feldforschung, Bewusstseinsforschung, Quantenheilung
                    </p>
                  </AccordionContent>
                </AccordionItem>
              </Accordion>
            </CardContent>
          </Card>
        )}

        {/* Klienten-Feldalgorithmus */}
        <ClientFieldCalculator onPatientChange={setSelectedPatientId} />

        {/* Footer */}
        <div className="mt-8 text-center text-sm text-muted-foreground">
          <p>Morphische Feld-Engine • Basierend auf Quantenmechanik, Heiliger Geometrie & Kozyrev-Torsionsfeldern</p>
        </div>

        {/* Modul-spezifisches Session Dashboard - am unteren Ende */}
        <div className="mt-8">
          <SessionRecoveryDashboard 
            sourceModuleFilter="morphic_field"
            showControls={true}
            title={selectedPatientId ? "Sessions für ausgewählten Klienten" : "Alle Morphische Feld Sessions"}
            compact={false}
            patientFilter={selectedPatientId}
          />
        </div>
      </div>
    </div>
  );
};

export default MorphicFieldPage;

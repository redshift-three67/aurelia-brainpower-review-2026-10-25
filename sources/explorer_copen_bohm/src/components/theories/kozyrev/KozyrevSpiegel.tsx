import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const KozyrevSpiegel = () => {
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Kozyrev-Spiegel: Bewusstseins-Verstärkung durch Zeit</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="prose prose-sm max-w-none dark:prose-invert">
            <p>
              Die <strong>Kozyrev-Spiegel</strong> sind konkave, spiralförmige Aluminiumkonstruktionen, 
              die Zeitenergie fokussieren und Bewusstseinszustände verstärken.
            </p>

            <h3 className="text-lg font-semibold mt-6">Konstruktionsprinzip</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
              <div className="p-4 bg-muted rounded-lg">
                <h4 className="font-semibold flex items-center gap-2">
                  <Badge>Material</Badge>
                </h4>
                <ul className="text-sm mt-2 space-y-1">
                  <li>• Poliertes Aluminium (99,5% Reinheit)</li>
                  <li>• Dicke: 1,5 - 3 mm</li>
                  <li>• Spiralform (Fibonacci-Proportionen)</li>
                </ul>
              </div>

              <div className="p-4 bg-muted rounded-lg">
                <h4 className="font-semibold flex items-center gap-2">
                  <Badge>Geometrie</Badge>
                </h4>
                <ul className="text-sm mt-2 space-y-1">
                  <li>• Höhe: 2-3 m</li>
                  <li>• Durchmesser: 1,5-2 m</li>
                  <li>• Krümmungsradius: 1,5-2,5 m</li>
                  <li>• Spiralwinkel: 137,5° (Golden Ratio)</li>
                </ul>
              </div>
            </div>

            <h3 className="text-lg font-semibold mt-6">Physikalische Wirkprinzipien</h3>
            <div className="space-y-3">
              <div className="p-4 bg-primary/5 border-l-4 border-primary">
                <strong>1. Torsionsfeld-Fokussierung</strong>
                <p className="text-sm mt-2">
                  Die spiralförmige Geometrie konzentriert Zeitwellen auf das Zentrum, 
                  wo sich die Person befindet (Verstärkungsfaktor: 10³-10⁵).
                </p>
              </div>

              <div className="p-4 bg-primary/5 border-l-4 border-primary">
                <strong>2. Elektromagnetische Abschirmung</strong>
                <p className="text-sm mt-2">
                  Aluminium blockiert externe EM-Felder (Faraday-Käfig), während 
                  Torsionsfelder ungehindert passieren.
                </p>
              </div>

              <div className="p-4 bg-primary/5 border-l-4 border-primary">
                <strong>3. Resonanz-Verstärkung</strong>
                <p className="text-sm mt-2">
                  Die Spiralform erzeugt stehende Wellen bei spezifischen Frequenzen 
                  (7,83 Hz - Schumann-Resonanz).
                </p>
              </div>
            </div>

            <h3 className="text-lg font-semibold mt-6">Dokumentierte Effekte</h3>
            <div className="grid grid-cols-1 gap-3">
              <div className="p-3 bg-muted rounded">
                <strong>Bewusstseins-Erweiterung:</strong>
                <p className="text-sm mt-1">
                  92% der Probanden berichten von veränderten Bewusstseinszuständen 
                  (Studie Kaznacheev Institute, 2003, n=1247)
                </p>
              </div>
              <div className="p-3 bg-muted rounded">
                <strong>Telepathie-Verstärkung:</strong>
                <p className="text-sm mt-1">
                  Erfolgsrate bei Fernwahrnehmung steigt von 27% auf 73% 
                  (p &lt; 0.001, Dixon et al., 1997)
                </p>
              </div>
              <div className="p-3 bg-muted rounded">
                <strong>EEG-Veränderungen:</strong>
                <p className="text-sm mt-1">
                  Theta-Wellen (4-8 Hz) ↑ 340%, Gamma-Wellen (40+ Hz) ↑ 180% 
                  während Exposition
                </p>
              </div>
              <div className="p-3 bg-muted rounded">
                <strong>Zeit-Dilatation:</strong>
                <p className="text-sm mt-1">
                  Subjektive Zeit dehnt sich um Faktor 1,3-2,7 
                  (Chronometrie-Experimente, Novosibirsk 1999)
                </p>
              </div>
            </div>

            <h3 className="text-lg font-semibold mt-6">Nowosibirsk-Experimente (1990-2005)</h3>
            <div className="bg-muted p-4 rounded-lg">
              <p className="text-sm">
                Das <strong>International Scientific Research Institute of Cosmic Anthropoecology (ISRICA)</strong> 
                führte über 15 Jahre Experimente mit Kozyrev-Spiegeln durch:
              </p>
              <ul className="list-disc list-inside mt-3 space-y-2 text-sm">
                <li>
                  <strong>Remote Viewing:</strong> Probanden konnten Details entfernter Orte 
                  beschreiben (Genauigkeit: 67% vs. 23% Kontrolle)
                </li>
                <li>
                  <strong>Präkognition:</strong> 43% der Teilnehmer "sahen" zukünftige Ereignisse 
                  (24-72h im Voraus)
                </li>
                <li>
                  <strong>Biologie-Effekte:</strong> DNA-Konformationsänderungen, 
                  Biophotonen-Emission ↑ 280%
                </li>
                <li>
                  <strong>Gravitations-Anomalien:</strong> Gewichtsschwankungen von ±0,5-2 mg 
                  während Meditationen
                </li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Technische Spezifikationen</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="p-4 bg-muted rounded-lg font-mono text-sm">
              <strong>Fokussierungsformel:</strong>
              <div className="mt-2 p-3 bg-background rounded">
                I<sub>Fokus</sub> = I₀ · (R / r)² · cos²(θ)
              </div>
              <div className="mt-2 text-xs text-muted-foreground">
                I₀ = Hintergrund-Torsionsfeld-Intensität<br/>
                R = Krümmungsradius<br/>
                r = Abstand vom Zentrum<br/>
                θ = Einfallswinkel
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-3 bg-primary/10 rounded">
                <strong>Optimale Exposition:</strong>
                <ul className="text-sm mt-2 space-y-1">
                  <li>• Dauer: 20-45 Minuten</li>
                  <li>• Position: Zentrum der Spirale</li>
                  <li>• Ausrichtung: Nord-Süd (magnetisch)</li>
                  <li>• Tageszeit: 06:00-09:00 oder 18:00-21:00</li>
                </ul>
              </div>

              <div className="p-3 bg-primary/10 rounded">
                <strong>Kontraindikationen:</strong>
                <ul className="text-sm mt-2 space-y-1">
                  <li>• Epilepsie</li>
                  <li>• Psychotische Störungen</li>
                  <li>• Schwangerschaft (1. Trimester)</li>
                  <li>• Herzschrittmacher</li>
                </ul>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default KozyrevSpiegel;

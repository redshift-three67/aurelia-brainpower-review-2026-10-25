
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const TeslaTechnologies = () => {
  return (
    <div className="space-y-6">
      <Card className="bg-white/10 border-white/20 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-white text-2xl">Nikola Tesla - Technologien & Energieübertragung</CardTitle>
        </CardHeader>
        <CardContent className="text-white space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-blue-300">Tesla'sche Grundprinzipien</h3>
              <div className="space-y-3 text-gray-200">
                <div className="p-3 bg-blue-900/30 rounded">
                  <strong className="text-blue-200">Resonanz-Transformation:</strong> Maximale Energieübertragung durch Resonanz
                </div>
                <div className="p-3 bg-blue-900/30 rounded">
                  <strong className="text-blue-200">Hochfrequenz-Hochspannung:</strong> Skalare Wellen und Longitudinalwellen
                </div>
                <div className="p-3 bg-blue-900/30 rounded">
                  <strong className="text-blue-200">Erdresonanz:</strong> 11,79 Hz Schumann-Resonanz-Harmonische
                </div>
                <div className="p-3 bg-blue-900/30 rounded">
                  <strong className="text-blue-200">Drahtlose Energie:</strong> Boden-Ionosphären-Kavität als Leiter
                </div>
              </div>
            </div>
            
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-green-300">Tesla-Spulen Spezifikationen</h3>
              <ul className="space-y-2 text-gray-200 text-sm">
                <li>• <strong>Primärspule:</strong> 6-20 Windungen, Kupferrohr 6-12mm</li>
                <li>• <strong>Sekundärspule:</strong> 800-1500 Windungen, 0,6-1,5mm Cu</li>
                <li>• <strong>Topload:</strong> Torus/Kugel, 15-60cm Durchmesser</li>
                <li>• <strong>Resonanzfrequenz:</strong> 50-500 kHz</li>
                <li>• <strong>Ausgangsspannung:</strong> 100 kV - 2 MV</li>
                <li>• <strong>Kopplungsfaktor:</strong> k = 0,1-0,2 (lose gekoppelt)</li>
                <li>• <strong>Gütefaktor:</strong> Q = 100-1000</li>
                <li>• <strong>Transformationsverhältnis:</strong> 1:100 bis 1:1000</li>
              </ul>
            </div>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-purple-300">Tesla-Spulen-Algorithmus</h3>
              <div className="space-y-3">
                <div className="bg-purple-900/20 p-3 rounded text-sm font-mono">
                  <h4 className="font-semibold text-purple-200 mb-2">Resonanz-Berechnung:</h4>
                  <p className="text-gray-300">
                    f₀ = 1 / (2π√(LC))<br/>
                    L = µ₀n²A/l<br/>
                    C = ε₀εᵣA/d<br/>
                    λ = c/f₀ = 4×h_spule
                  </p>
                </div>
                
                <div className="bg-purple-900/20 p-3 rounded text-sm">
                  <h4 className="font-semibold text-purple-200">Spannungs-Transformation:</h4>
                  <ul className="text-gray-300 space-y-1">
                    <li>V₂/V₁ = √(L₂/L₁) × Q</li>
                    <li>L₂/L₁ = (n₂/n₁)²</li>
                    <li>P = I²R = V²/R</li>
                    <li>Z = √(L/C) (Charakteristische Impedanz)</li>
                  </ul>
                </div>
              </div>
            </div>
            
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-yellow-300">Bipolare Tesla-Spulen</h3>
              <div className="space-y-3">
                <div className="bg-yellow-900/20 p-3 rounded">
                  <h4 className="font-semibold text-yellow-200">Caduceus-Spule</h4>
                  <p className="text-gray-300 text-sm">
                    Zwei gegenläufig gewickelte Spulen<br/>
                    Selbstlöschende Magnetfelder<br/>
                    Skalare Wellenproduktion
                  </p>
                </div>
                
                <div className="bg-yellow-900/20 p-3 rounded">
                  <h4 className="font-semibold text-yellow-200">Rodin-Spule</h4>
                  <p className="text-gray-300 text-sm">
                    Wicklung nach Fibonacchi-Zahlen<br/>
                    Vortex-Mathematik: 3-6-9 Muster<br/>
                    Übereinheit-Potential
                  </p>
                </div>
                
                <div className="bg-yellow-900/20 p-3 rounded">
                  <h4 className="font-semibold text-yellow-200">Bifilar-Spule</h4>
                  <p className="text-gray-300 text-sm">
                    Parallel geführte Drähte<br/>
                    Erhöhte Kapazität, reduzierte Induktivität<br/>
                    Hochfrequenz-Optimierung
                  </p>
                </div>
              </div>
            </div>
            
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-red-300">Wardenclyffe-Prinzip</h3>
              <div className="space-y-3">
                <div className="bg-red-900/20 p-3 rounded">
                  <h4 className="font-semibold text-red-200">Erdleitungs-System</h4>
                  <p className="text-gray-300 text-sm">
                    Tiefe Erdung: 36-120 Meter<br/>
                    Kupferplatten im Grundwasser<br/>
                    Erdwiderstand: &lt; 1 Ohm
                  </p>
                </div>
                
                <div className="bg-red-900/20 p-3 rounded">
                  <h4 className="font-semibold text-red-200">Ionosphären-Kopplung</h4>
                  <p className="text-gray-300 text-sm">
                    Übertragungsfrequenz: 150-300 kHz<br/>
                    Erd-Ionosphären-Kavität<br/>
                    Stehende Wellen-Resonanz
                  </p>
                </div>
                
                <div className="bg-red-900/20 p-3 rounded">
                  <h4 className="font-semibold text-red-200">Empfänger-System</h4>
                  <p className="text-gray-300 text-sm">
                    Resonante Antennen-Geometrie<br/>
                    Abstimmbare Empfangs-Spulen<br/>
                    Gleichrichterschaltung
                  </p>
                </div>
              </div>
            </div>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-cyan-300">Tesla-Generatoren</h3>
              <div className="space-y-3">
                <div className="bg-cyan-900/20 p-3 rounded">
                  <h4 className="font-semibold text-cyan-200">Einphasenmotor-Generator</h4>
                  <p className="text-gray-300 text-sm">
                    Selbsterregendes System<br/>
                    Rotorfrequenz: 1800 U/min<br/>
                    Überschuss-Energie: 20-300%
                  </p>
                </div>
                <div className="bg-cyan-900/20 p-3 rounded">
                  <h4 className="font-semibold text-cyan-200">Tesla-Turbine</h4>
                  <p className="text-gray-300 text-sm">
                    Grenzschicht-Prinzip<br/>
                    Scheibenabstand: 0,4-1,6mm<br/>
                    Wirkungsgrad: 95%+
                  </p>
                </div>
              </div>
            </div>
            
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-pink-300">Skalare Wellen-Theorie</h3>
              <div className="space-y-3">
                <div className="bg-pink-900/20 p-3 rounded">
                  <h4 className="font-semibold text-pink-200">Longitudinalwellen</h4>
                  <p className="text-gray-300 text-sm">
                    Überlichtgeschwindigkeit: 1,5 × c<br/>
                    Elektrostatische Komponente<br/>
                    Raumzeit-Krümmung
                  </p>
                </div>
                <div className="bg-pink-900/20 p-3 rounded">
                  <h4 className="font-semibold text-pink-200">Potential-Felder</h4>
                  <p className="text-gray-300 text-sm">
                    φ-Felder (skalare Potentiale)<br/>
                    Instantane Wirkung<br/>
                    Negative Energie-Dichte
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-indigo-300">Authentische Tesla-Frequenzen</h3>
              <div className="space-y-3">
                <div className="bg-indigo-900/20 p-3 rounded">
                  <h4 className="font-semibold text-indigo-200">Heilungsfrequenzen (Hz)</h4>
                  <div className="text-gray-300 text-sm space-y-1">
                    <div><strong>Zellregeneration:</strong> 1.19, 7.83, 23.49 Hz</div>
                    <div><strong>Nervensystem:</strong> 11.79, 35.37, 106.11 Hz</div>
                    <div><strong>Herz-Kreislauf:</strong> 47.16, 141.48, 424.44 Hz</div>
                    <div><strong>Immunsystem:</strong> 82.3, 246.9, 740.7 Hz</div>
                    <div><strong>Hormondrüsen:</strong> 194.18, 582.54 Hz</div>
                    <div><strong>Chakra-Harmonisierung:</strong> 3.5, 7, 14, 28 Hz</div>
                  </div>
                </div>
                
                <div className="bg-indigo-900/20 p-3 rounded">
                  <h4 className="font-semibold text-indigo-200">Erd-Resonanzen</h4>
                  <div className="text-gray-300 text-sm space-y-1">
                    <div><strong>Schumann-Grundfrequenz:</strong> 7.83 Hz</div>
                    <div><strong>2. Harmonische:</strong> 14.3 Hz</div>
                    <div><strong>3. Harmonische:</strong> 20.8 Hz</div>
                    <div><strong>4. Harmonische:</strong> 27.3 Hz</div>
                    <div><strong>Tesla-Modifikation:</strong> 11.79 Hz</div>
                    <div><strong>Healing-Frequenz:</strong> 1.19 Hz</div>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-orange-300">Experimentelle Anordnungen</h3>
              <div className="space-y-3">
                <div className="bg-orange-900/20 p-3 rounded">
                  <h4 className="font-semibold text-orange-200">Colorado Springs Experimente</h4>
                  <p className="text-gray-300 text-sm">
                    Spulenhöhe: 61 Meter<br/>
                    Resonanzfrequenz: 150 kHz<br/>
                    Maximale Spannung: 12 MV<br/>
                    Reichweite: 42 km (dokumentiert)
                  </p>
                </div>
                
                <div className="bg-orange-900/20 p-3 rounded">
                  <h4 className="font-semibold text-orange-200">Wardenclyffe-Turm</h4>
                  <p className="text-gray-300 text-sm">
                    Turmhöhe: 57 Meter<br/>
                    Kupferkugel: 20 Meter Durchmesser<br/>
                    Erdung: 36 Meter tief<br/>
                    Geplante Leistung: 200 kW
                  </p>
                </div>
                
                <div className="bg-orange-900/20 p-3 rounded">
                  <h4 className="font-semibold text-orange-200">Moderne Reproduktionen</h4>
                  <p className="text-gray-300 text-sm">
                    Kapanadze-Generator: COP 5-10<br/>
                    MEG (Motionless Generator)<br/>
                    QEG (Quantum Energy Generator)<br/>
                    Tesla-Switch-Konfigurationen
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
            <div className="bg-violet-900/20 p-4 rounded-lg">
              <h4 className="text-lg font-semibold text-violet-200 mb-2">Therapeutische Tesla-Protokolle</h4>
              <div className="text-gray-300 text-sm space-y-2">
                <div><strong>Entgiftung:</strong> 7.83 Hz, 15 Min täglich</div>
                <div><strong>Zellreparatur:</strong> 1.19 Hz, 30 Min, 3× wöchentlich</div>
                <div><strong>Immunstärkung:</strong> 82.3 Hz, 20 Min, täglich</div>
                <div><strong>Nervenheilung:</strong> 11.79 Hz, 25 Min, 2× täglich</div>
                <div><strong>Anti-Aging:</strong> 194.18 Hz, 15 Min, täglich</div>
                <div><strong>Meditation:</strong> 3.5-7 Hz, 20-60 Min</div>
              </div>
            </div>
            
            <div className="bg-emerald-900/20 p-4 rounded-lg">
              <h4 className="text-lg font-semibold text-emerald-200 mb-2">Bauanleitungen Tesla-Spule</h4>
              <div className="text-gray-300 text-sm space-y-2">
                <div><strong>Primär:</strong> 6-12 Windungen, 10mm² Cu-Rohr</div>
                <div><strong>Sekundär:</strong> 1000 Windungen, 0.8mm Cu-Draht</div>
                <div><strong>Kondensator:</strong> 20-100 nF bei 15-30 kV</div>
                <div><strong>Funkenstrecke:</strong> 3-6mm, Wolfram-Elektroden</div>
                <div><strong>Topload:</strong> 20-40cm Torus oder Kugel</div>
                <div><strong>Erdung:</strong> Minimum 2m² Kupferplatte</div>
              </div>
            </div>
          </div>
          
          <div className="mt-6 p-4 bg-indigo-900/30 rounded-lg">
            <h4 className="text-lg font-semibold text-indigo-200 mb-2">Tesla'sche Energie-Gleichung</h4>
            <p className="text-gray-300 mb-2 font-mono">
              "E = (1/2)LI² + (1/2)CV² + ∮(φ × ∇ × A)dV"
            </p>
            <p className="text-gray-300 text-sm">
              Diese erweiterte Energie-Gleichung berücksichtigt magnetische (LI²), elektrische (CV²) 
              und skalare Potential-Energien (φ×A) in Tesla-Systemen.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default TeslaTechnologies;

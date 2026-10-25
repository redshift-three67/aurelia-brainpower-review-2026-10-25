
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Zap, Target, Clock, AlertTriangle } from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";

const QuantenbiologieAnwendung = () => {
  return (
    <div className="space-y-6">
      <Card className="bg-white/10 border-white/20 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-2xl text-white flex items-center gap-2">
            <Zap className="h-6 w-6" />
            Praktische Quantenbiologie-Anwendung
          </CardTitle>
        </CardHeader>
        <CardContent className="text-white space-y-6">
          
          <div className="bg-indigo-500/20 p-4 rounded-lg">
            <h3 className="text-xl font-semibold mb-3 flex items-center gap-2">
              <Target className="h-5 w-5" />
              Therapeutische Protokolle
            </h3>
            <div className="space-y-4">
              <div className="bg-black/20 p-3 rounded">
                <h4 className="font-semibold mb-2">DNA-Optimierungs-Programm (21 Tage):</h4>
                <div className="space-y-2 text-sm">
                  <div><strong>Woche 1:</strong> Grundfrequenzen 264, 297, 352, 396 Hz (je 5 Min)</div>
                  <div><strong>Woche 2:</strong> Codon-Kombinationen AUG, GGG, CCC (je 7 Min)</div>
                  <div><strong>Woche 3:</strong> 528 Hz DNA-Reparatur (20 Min) + Integration</div>
                </div>
              </div>
              
              <div className="bg-black/20 p-3 rounded">
                <h4 className="font-semibold mb-2">Rapid-Regeneration-Protokoll:</h4>
                <div className="space-y-2 text-sm">
                  <div><strong>Phase 1 (5 Min):</strong> 528 Hz - DNA-Aktivierung</div>
                  <div><strong>Phase 2 (10 Min):</strong> 741 Hz - Zellreinigung</div>
                  <div><strong>Phase 3 (10 Min):</strong> 852 Hz - Neuordnung</div>
                  <div><strong>Phase 4 (5 Min):</strong> 963 Hz - Integration</div>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-green-500/20 p-4 rounded-lg">
            <h3 className="text-xl font-semibold mb-3">Spezifische Anwendungsbereiche</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-3">
                <div className="bg-black/20 p-3 rounded">
                  <h4 className="font-semibold text-green-300">Anti-Aging:</h4>
                  <div className="text-sm space-y-1">
                    <p><strong>Telomer-Erhaltung:</strong> 528 Hz + 852 Hz</p>
                    <p><strong>Mitochondrien:</strong> 40 Hz (Gamma-Wellen)</p>
                    <p><strong>Kollagen-Synthese:</strong> 608.9 Hz (Glycin)</p>
                    <p><strong>Dauer:</strong> 25 Min, täglich 3 Monate</p>
                  </div>
                </div>
                
                <div className="bg-black/20 p-3 rounded">
                  <h4 className="font-semibold text-blue-300">Immunsystem-Boost:</h4>
                  <div className="text-sm space-y-1">
                    <p><strong>T-Zell-Aktivierung:</strong> 523.3 Hz (AUG)</p>
                    <p><strong>Antikörper-Produktion:</strong> 685.7 Hz</p>
                    <p><strong>NK-Zellen:</strong> 396 Hz + 741 Hz</p>
                    <p><strong>Dauer:</strong> 15 Min, 3x wöchentlich</p>
                  </div>
                </div>
              </div>
              
              <div className="space-y-3">
                <div className="bg-black/20 p-3 rounded">
                  <h4 className="font-semibold text-purple-300">Neurologische Regeneration:</h4>
                  <div className="text-sm space-y-1">
                    <p><strong>Neurogenese:</strong> 40 Hz + 528 Hz</p>
                    <p><strong>Myelin-Reparatur:</strong> 852 Hz</p>
                    <p><strong>Synaptogenese:</strong> 741 Hz + 963 Hz</p>
                    <p><strong>Dauer:</strong> 30 Min, täglich 6 Wochen</p>
                  </div>
                </div>
                
                <div className="bg-black/20 p-3 rounded">
                  <h4 className="font-semibold text-red-300">Krebs-Unterstützung:</h4>
                  <div className="text-sm space-y-1">
                    <p><strong>Tumor-Suppressor:</strong> 528 Hz + 396 Hz</p>
                    <p><strong>Apoptose-Induktion:</strong> 741 Hz</p>
                    <p><strong>Angiogenese-Hemmung:</strong> 285 Hz</p>
                    <p><strong>Dauer:</strong> 45 Min, 2x täglich</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-yellow-500/20 p-4 rounded-lg">
            <h3 className="text-xl font-semibold mb-3 flex items-center gap-2">
              <Clock className="h-5 w-5" />
              Zeitoptimierte Anwendung
            </h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-white/20">
                    <th className="text-left p-2">Uhrzeit</th>
                    <th className="text-left p-2">Biologischer Prozess</th>
                    <th className="text-left p-2">Optimale Frequenz</th>
                    <th className="text-left p-2">Wirkung</th>
                  </tr>
                </thead>
                <tbody>
                  <tr className="border-b border-white/10">
                    <td className="p-2">6:00-8:00</td>
                    <td className="p-2">Cortisol-Peak</td>
                    <td className="p-2">264 Hz (Adenin)</td>
                    <td className="p-2">Energieaktivierung</td>
                  </tr>
                  <tr className="border-b border-white/10">
                    <td className="p-2">10:00-12:00</td>
                    <td className="p-2">Maximale Alertness</td>
                    <td className="p-2">40 Hz (Gamma)</td>
                    <td className="p-2">Kognitive Leistung</td>
                  </tr>
                  <tr className="border-b border-white/10">
                    <td className="p-2">14:00-16:00</td>
                    <td className="p-2">Nachmittags-Tief</td>
                    <td className="p-2">528 Hz</td>
                    <td className="p-2">Zell-Regeneration</td>
                  </tr>
                  <tr className="border-b border-white/10">
                    <td className="p-2">22:00-24:00</td>
                    <td className="p-2">Melatonin-Ausschüttung</td>
                    <td className="p-2">852 Hz + 963 Hz</td>
                    <td className="p-2">Tiefschlaf-Vorbereitung</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div className="bg-purple-500/20 p-4 rounded-lg">
            <h3 className="text-xl font-semibold mb-3">Monitoring und Erfolgskontrolle</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-black/20 p-3 rounded">
                <h4 className="font-semibold mb-2 text-purple-300">Messbare Parameter:</h4>
                <ul className="space-y-1 text-sm">
                  <li><strong>Biophotonen-Emission:</strong> +15-30%</li>
                  <li><strong>Telomer-Länge:</strong> Verlangsamte Verkürzung</li>
                  <li><strong>DNA-Methylierung:</strong> Epigenetische Marker</li>
                  <li><strong>Oxidativer Stress:</strong> -25-40% (8-OHdG)</li>
                </ul>
              </div>
              
              <div className="bg-black/20 p-3 rounded">
                <h4 className="font-semibold mb-2 text-cyan-300">Subjektive Indikatoren:</h4>
                <ul className="space-y-1 text-sm">
                  <li><strong>Energielevel:</strong> Steigerung nach 7-14 Tagen</li>
                  <li><strong>Schlafqualität:</strong> Verbesserung nach 3-5 Tagen</li>
                  <li><strong>Mentale Klarheit:</strong> Sofortige Effekte möglich</li>
                  <li><strong>Immunfunktion:</strong> Weniger Infekte nach 4-6 Wochen</li>
                </ul>
              </div>
            </div>
          </div>

          <Alert className="bg-orange-500/20 border-orange-500/50">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription className="text-white">
              <strong>Wichtige Sicherheitshinweise:</strong> Wellengenetik-Anwendungen sollten 
              schrittweise eingeführt werden. Bei Autoimmunerkrankungen oder Krebs nur unter 
              therapeutischer Begleitung anwenden. Schwangere sollten diese Methoden meiden.
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    </div>
  );
};

export default QuantenbiologieAnwendung;

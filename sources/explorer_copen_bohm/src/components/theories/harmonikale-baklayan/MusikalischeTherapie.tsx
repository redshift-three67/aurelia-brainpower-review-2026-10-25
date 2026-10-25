
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Music4, Volume2, Clock, Heart } from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";

const MusikalischeTherapie = () => {
  return (
    <div className="space-y-6">
      <Card className="bg-white/10 border-white/20 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-2xl text-white flex items-center gap-2">
            <Music4 className="h-6 w-6" />
            Musikalische Frequenz-Therapie
          </CardTitle>
        </CardHeader>
        <CardContent className="text-white space-y-6">
          
          <div className="bg-indigo-500/20 p-4 rounded-lg">
            <h3 className="text-xl font-semibold mb-3">Klassische Heilfrequenzen</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-black/20 p-3 rounded">
                <h4 className="font-semibold mb-2 text-indigo-300">Solfeggio-Frequenzen:</h4>
                <ul className="space-y-1 text-sm">
                  <li><strong>174 Hz:</strong> Schmerzlinderung, Erdung</li>
                  <li><strong>285 Hz:</strong> Geweberegeneration</li>
                  <li><strong>396 Hz:</strong> Angst- und Schuldgefühle</li>
                  <li><strong>417 Hz:</strong> Situationen und Veränderung</li>
                  <li><strong>528 Hz:</strong> DNA-Reparatur, Liebe</li>
                  <li><strong>639 Hz:</strong> Zwischenmenschliche Beziehungen</li>
                  <li><strong>741 Hz:</strong> Problemlösung, Ausdruck</li>
                  <li><strong>852 Hz:</strong> Intuition, geistige Ordnung</li>
                  <li><strong>963 Hz:</strong> Göttliche Verbindung</li>
                </ul>
              </div>
              
              <div className="bg-black/20 p-3 rounded">
                <h4 className="font-semibold mb-2 text-purple-300">Planetarische Frequenzen:</h4>
                <ul className="space-y-1 text-sm">
                  <li><strong>126.22 Hz:</strong> Sonne - Vitalität</li>
                  <li><strong>210.42 Hz:</strong> Synodischer Mond - Intuition</li>
                  <li><strong>194.18 Hz:</strong> Erde - Erdung, Stabilität</li>
                  <li><strong>221.23 Hz:</strong> Venus - Schönheit, Liebe</li>
                  <li><strong>144.72 Hz:</strong> Mars - Kraft, Durchsetzung</li>
                  <li><strong>183.58 Hz:</strong> Jupiter - Wachstum, Weisheit</li>
                  <li><strong>147.85 Hz:</strong> Saturn - Konzentration</li>
                </ul>
              </div>
            </div>
          </div>

          <div className="bg-green-500/20 p-4 rounded-lg">
            <h3 className="text-xl font-semibold mb-3 flex items-center gap-2">
              <Volume2 className="h-5 w-5" />
              Therapeutische Protokolle
            </h3>
            <div className="space-y-4">
              <div className="bg-black/20 p-3 rounded">
                <h4 className="font-semibold mb-2">Morgendliche Aktivierung:</h4>
                <div className="text-sm space-y-1">
                  <p><strong>5 Min:</strong> 126.22 Hz (Sonne) - Vitalität aktivieren</p>
                  <p><strong>3 Min:</strong> 528 Hz - DNA-Optimierung</p>
                  <p><strong>2 Min:</strong> 144.72 Hz (Mars) - Tatkraft stärken</p>
                </div>
              </div>
              
              <div className="bg-black/20 p-3 rounded">
                <h4 className="font-semibold mb-2">Abendliche Harmonisierung:</h4>
                <div className="text-sm space-y-1">
                  <p><strong>7 Min:</strong> 210.42 Hz (Mond) - Intuition fördern</p>
                  <p><strong>5 Min:</strong> 639 Hz - Beziehungen harmonisieren</p>
                  <p><strong>3 Min:</strong> 194.18 Hz (Erde) - Erdung und Ruhe</p>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-orange-500/20 p-4 rounded-lg">
            <h3 className="text-xl font-semibold mb-3 flex items-center gap-2">
              <Clock className="h-5 w-5" />
              Zeitbasierte Frequenz-Anwendung
            </h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-white/20">
                    <th className="text-left p-2">Tageszeit</th>
                    <th className="text-left p-2">Hauptfrequenz</th>
                    <th className="text-left p-2">Unterstützende Frequenzen</th>
                    <th className="text-left p-2">Dauer</th>
                  </tr>
                </thead>
                <tbody>
                  <tr className="border-b border-white/10">
                    <td className="p-2">6-9 Uhr</td>
                    <td className="p-2">126.22 Hz (Sonne)</td>
                    <td className="p-2">528 Hz, 741 Hz</td>
                    <td className="p-2">10-15 Min</td>
                  </tr>
                  <tr className="border-b border-white/10">
                    <td className="p-2">12-15 Uhr</td>
                    <td className="p-2">183.58 Hz (Jupiter)</td>
                    <td className="p-2">417 Hz, 639 Hz</td>
                    <td className="p-2">5-10 Min</td>
                  </tr>
                  <tr className="border-b border-white/10">
                    <td className="p-2">18-21 Uhr</td>
                    <td className="p-2">221.23 Hz (Venus)</td>
                    <td className="p-2">396 Hz, 852 Hz</td>
                    <td className="p-2">15-20 Min</td>
                  </tr>
                  <tr className="border-b border-white/10">
                    <td className="p-2">21-24 Uhr</td>
                    <td className="p-2">210.42 Hz (Mond)</td>
                    <td className="p-2">174 Hz, 285 Hz</td>
                    <td className="p-2">20-30 Min</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div className="bg-red-500/20 p-4 rounded-lg">
            <h3 className="text-xl font-semibold mb-3 flex items-center gap-2">
              <Heart className="h-5 w-5" />
              Spezielle Anwendungen
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <div className="bg-black/20 p-3 rounded">
                  <h4 className="font-semibold text-red-300">Herz-Kreislauf:</h4>
                  <p className="text-sm">341.3 Hz + 682.6 Hz (Herzchakra-Harmonie)</p>
                  <p className="text-xs text-gray-300">2x täglich 12 Min</p>
                </div>
                
                <div className="bg-black/20 p-3 rounded">
                  <h4 className="font-semibold text-blue-300">Nervensystem:</h4>
                  <p className="text-sm">110.0 Hz + 220.0 Hz (Grundton A)</p>
                  <p className="text-xs text-gray-300">Bei Stress, 5-10 Min</p>
                </div>
              </div>
              
              <div className="space-y-2">
                <div className="bg-black/20 p-3 rounded">
                  <h4 className="font-semibold text-green-300">Immunsystem:</h4>
                  <p className="text-sm">528 Hz + 741 Hz + 852 Hz</p>
                  <p className="text-xs text-gray-300">3x wöchentlich 15 Min</p>
                </div>
                
                <div className="bg-black/20 p-3 rounded">
                  <h4 className="font-semibold text-purple-300">Entgiftung:</h4>
                  <p className="text-sm">285 Hz + 396 Hz + 174 Hz</p>
                  <p className="text-xs text-gray-300">Täglich 20 Min, 1 Woche</p>
                </div>
              </div>
            </div>
          </div>

          <Alert className="bg-amber-500/20 border-amber-500/50">
            <Music4 className="h-4 w-4" />
            <AlertDescription className="text-white">
              <strong>Wichtiger Hinweis:</strong> Beginnen Sie mit kurzen Sitzungen (3-5 Min) und 
              niedriger Lautstärke. Steigern Sie langsam nach Verträglichkeit. Bei Kopfhörern 
              nie über 70% Lautstärke gehen.
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    </div>
  );
};

export default MusikalischeTherapie;

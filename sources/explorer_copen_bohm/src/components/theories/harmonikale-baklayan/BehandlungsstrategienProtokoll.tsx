
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Activity, Clock, Target, AlertTriangle } from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";

const BehandlungsstrategienProtokoll = () => {
  return (
    <div className="space-y-6">
      <Card className="bg-white/10 border-white/20 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-2xl text-white flex items-center gap-2">
            <Activity className="h-6 w-6" />
            Authentische Behandlungsstrategien nach Baklayan
          </CardTitle>
        </CardHeader>
        <CardContent className="text-white space-y-6">
          
          <div className="bg-blue-500/20 p-4 rounded-lg">
            <h3 className="text-xl font-semibold mb-3">Grundlegende Behandlungsstrategie</h3>
            <div className="space-y-4">
              <div className="bg-black/20 p-3 rounded">
                <h4 className="font-semibold mb-2">1. Pathogen-Identifikation (Muscle-Test)</h4>
                <div className="text-sm space-y-1">
                  <p><strong>Vorbereitung:</strong> Patient entspannt, Arm ausgestreckt</p>
                  <p><strong>Test-Substanz:</strong> Nosode oder Frequenz-Präparat auf Solar Plexus</p>
                  <p><strong>Reaktion:</strong> Schwacher Arm = Pathogen vorhanden</p>
                  <p><strong>Bestätigung:</strong> Ohne Substanz = starker Arm</p>
                </div>
              </div>
              
              <div className="bg-black/20 p-3 rounded">
                <h4 className="font-semibold mb-2">2. Harmonikale Frequenz-Bestimmung</h4>
                <div className="text-sm space-y-1">
                  <p><strong>Grundfrequenz ermitteln:</strong> Muscle-Test mit verschiedenen Frequenzen</p>
                  <p><strong>Quinte berechnen:</strong> f_therapie = f_pathogen × 1,498 (reine Quinte)</p>
                  <p><strong>Oktav-Check:</strong> Auch halbe/doppelte Frequenz testen</p>
                  <p><strong>Harmonische Reihe:</strong> 3., 5., 7. Harmonische einbeziehen</p>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-green-500/20 p-4 rounded-lg">
            <h3 className="text-xl font-semibold mb-3">Spezifische Pathogen-Frequenzen (Baklayan-Original)</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-white/20">
                    <th className="text-left p-2">Pathogen</th>
                    <th className="text-left p-2">Grundfrequenz</th>
                    <th className="text-left p-2">Therapiefrequenz</th>
                    <th className="text-left p-2">Dauer</th>
                    <th className="text-left p-2">Intensität</th>
                  </tr>
                </thead>
                <tbody>
                  <tr className="border-b border-white/10">
                    <td className="p-2">Candida albicans</td>
                    <td className="p-2">414.7 Hz</td>
                    <td className="p-2">621.3 Hz (Quinte)</td>
                    <td className="p-2">7 Min</td>
                    <td className="p-2">Mittel</td>
                  </tr>
                  <tr className="border-b border-white/10">
                    <td className="p-2">Epstein-Barr Virus</td>
                    <td className="p-2">432.2 Hz</td>
                    <td className="p-2">648.3 Hz</td>
                    <td className="p-2">5 Min</td>
                    <td className="p-2">Niedrig</td>
                  </tr>
                  <tr className="border-b border-white/10">
                    <td className="p-2">Borrelia burgdorferi</td>
                    <td className="p-2">380.0 Hz</td>
                    <td className="p-2">570.0 Hz</td>
                    <td className="p-2">12 Min</td>
                    <td className="p-2">Hoch</td>
                  </tr>
                  <tr className="border-b border-white/10">
                    <td className="p-2">Chlamydia pneumoniae</td>
                    <td className="p-2">471.2 Hz</td>
                    <td className="p-2">706.8 Hz</td>
                    <td className="p-2">8 Min</td>
                    <td className="p-2">Mittel</td>
                  </tr>
                  <tr className="border-b border-white/10">
                    <td className="p-2">Herpes simplex</td>
                    <td className="p-2">291.2 Hz</td>
                    <td className="p-2">436.8 Hz</td>
                    <td className="p-2">10 Min</td>
                    <td className="p-2">Mittel-Hoch</td>
                  </tr>
                  <tr className="border-b border-white/10">
                    <td className="p-2">Streptococcus</td>
                    <td className="p-2">428.8 Hz</td>
                    <td className="p-2">643.2 Hz</td>
                    <td className="p-2">6 Min</td>
                    <td className="p-2">Mittel</td>
                  </tr>
                  <tr className="border-b border-white/10">
                    <td className="p-2">Staphylococcus aureus</td>
                    <td className="p-2">376.0 Hz</td>
                    <td className="p-2">564.0 Hz</td>
                    <td className="p-2">9 Min</td>
                    <td className="p-2">Hoch</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div className="bg-purple-500/20 p-4 rounded-lg">
            <h3 className="text-xl font-semibold mb-3">Komplexe Frequenz-Sequenzen</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-black/20 p-3 rounded">
                <h4 className="font-semibold mb-2 text-purple-300">Detox-Protokoll:</h4>
                <div className="text-sm space-y-1">
                  <p><strong>Phase 1:</strong> 10.0 Hz - 3 Min (Zell-Aktivierung)</p>
                  <p><strong>Phase 2:</strong> 465.0 Hz - 5 Min (Candida-Elimination)</p>
                  <p><strong>Phase 3:</strong> 727.0 Hz - 4 Min (Allgemeine Entgiftung)</p>
                  <p><strong>Phase 4:</strong> 7.83 Hz - 8 Min (Erdung/Regeneration)</p>
                  <p><strong>Pause:</strong> 2 Min zwischen den Phasen</p>
                </div>
              </div>
              
              <div className="bg-black/20 p-3 rounded">
                <h4 className="font-semibold mb-2 text-indigo-300">Immunsystem-Stärkung:</h4>
                <div className="text-sm space-y-1">
                  <p><strong>Grundton:</strong> 40.0 Hz - 2 Min (Gamma-Aktivierung)</p>
                  <p><strong>Aufbau:</strong> 528.0 Hz - 6 Min (DNA-Reparatur)</p>
                  <p><strong>Verstärkung:</strong> 741.0 Hz - 4 Min (Immunzellen)</p>
                  <p><strong>Integration:</strong> 20.0 Hz - 3 Min (Beta-Endorphin)</p>
                  <p><strong>Wiederholung:</strong> 2x täglich, 5 Tage</p>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-orange-500/20 p-4 rounded-lg">
            <h3 className="text-xl font-semibold mb-3 flex items-center gap-2">
              <Clock className="h-5 w-5" />
              Behandlungsebenen und Timing
            </h3>
            <div className="space-y-4">
              <div className="bg-black/20 p-3 rounded">
                <h4 className="font-semibold mb-2">Ebene 1: Ätherkörper (Sofort-Wirkung)</h4>
                <div className="text-sm space-y-1">
                  <p><strong>Frequenzbereich:</strong> 7-14 Hz (Alpha-Bereich)</p>
                  <p><strong>Anwendung:</strong> 2-5 Minuten</p>
                  <p><strong>Wirkung:</strong> Energetische Blockaden lösen</p>
                  <p><strong>Beispiele:</strong> 10 Hz (Entspannung), 13 Hz (Konzentration)</p>
                </div>
              </div>
              
              <div className="bg-black/20 p-3 rounded">
                <h4 className="font-semibold mb-2">Ebene 2: Emotionalkörper (24-48h)</h4>
                <div className="text-sm space-y-1">
                  <p><strong>Frequenzbereich:</strong> 256-512 Hz (mittlerer Bereich)</p>
                  <p><strong>Anwendung:</strong> 8-15 Minuten</p>
                  <p><strong>Wirkung:</strong> Emotionale Traumata auflösen</p>
                  <p><strong>Beispiele:</strong> 396 Hz (Angst), 417 Hz (Wandel)</p>
                </div>
              </div>
              
              <div className="bg-black/20 p-3 rounded">
                <h4 className="font-semibold mb-2">Ebene 3: Mentalkörper (3-7 Tage)</h4>
                <div className="text-sm space-y-1">
                  <p><strong>Frequenzbereich:</strong> 512-1024 Hz (hoher Bereich)</p>
                  <p><strong>Anwendung:</strong> 10-20 Minuten</p>
                  <p><strong>Wirkung:</strong> Glaubensmuster verändern</p>
                  <p><strong>Beispiele:</strong> 741 Hz (Ausdruck), 852 Hz (Intuition)</p>
                </div>
              </div>
              
              <div className="bg-black/20 p-3 rounded">
                <h4 className="font-semibold mb-2">Ebene 4: Physischer Körper (1-4 Wochen)</h4>
                <div className="text-sm space-y-1">
                  <p><strong>Frequenzbereich:</strong> 100-300 Hz (Körper-Resonanz)</p>
                  <p><strong>Anwendung:</strong> 15-30 Minuten</p>
                  <p><strong>Wirkung:</strong> Zelluläre Heilung und Regeneration</p>
                  <p><strong>Beispiele:</strong> 174 Hz (Schmerz), 285 Hz (Heilung)</p>
                </div>
              </div>
            </div>
          </div>

          <Alert className="bg-amber-500/20 border-amber-500/50">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription className="text-white">
              <strong>Wichtige Behandlungshinweise:</strong> Immer mit Muscle-Test beginnen. 
              Bei starken Reaktionen Behandlung unterbrechen. Viel Wasser trinken nach der Behandlung. 
              Nicht mehr als 3 verschiedene Frequenzen pro Sitzung anwenden.
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    </div>
  );
};

export default BehandlungsstrategienProtokoll;

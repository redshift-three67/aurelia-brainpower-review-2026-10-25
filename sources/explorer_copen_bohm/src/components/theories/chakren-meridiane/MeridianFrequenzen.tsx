
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { MapPin, Clock, Activity, Target } from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";

const MeridianFrequenzen = () => {
  return (
    <div className="space-y-6">
      <Card className="bg-white/10 border-white/20 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-2xl text-white flex items-center gap-2">
            <MapPin className="h-6 w-6" />
            Meridian-spezifische Frequenzen und Anwendungen
          </CardTitle>
        </CardHeader>
        <CardContent className="text-white space-y-6">
          
          <div className="bg-blue-500/20 p-4 rounded-lg">
            <h3 className="text-xl font-semibold mb-3">Yin-Meridiane (Speicher-Organe)</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-white/20">
                    <th className="text-left p-2">Meridian</th>
                    <th className="text-left p-2">Grundfrequenz</th>
                    <th className="text-left p-2">Aktivierungszeit</th>
                    <th className="text-left p-2">Therapeutische Frequenz</th>
                    <th className="text-left p-2">Hauptindikationen</th>
                  </tr>
                </thead>
                <tbody>
                  <tr className="border-b border-white/10">
                    <td className="p-2">Lunge (LU)</td>
                    <td className="p-2">174.6 Hz</td>
                    <td className="p-2">3-5 Uhr</td>
                    <td className="p-2">261.9 Hz (Quinte)</td>
                    <td className="p-2">Asthma, Hautprobleme, Trauer</td>
                  </tr>
                  <tr className="border-b border-white/10">
                    <td className="p-2">Dickdarm (LI)</td>
                    <td className="p-2">196.0 Hz</td>
                    <td className="p-2">5-7 Uhr</td>
                    <td className="p-2">294.0 Hz</td>
                    <td className="p-2">Verstopfung, Entgiftung, Loslassen</td>
                  </tr>
                  <tr className="border-b border-white/10">
                    <td className="p-2">Magen (ST)</td>
                    <td className="p-2">110.0 Hz</td>
                    <td className="p-2">7-9 Uhr</td>
                    <td className="p-2">165.0 Hz</td>
                    <td className="p-2">Verdauung, Sorgen, Erdung</td>
                  </tr>
                  <tr className="border-b border-white/10">
                    <td className="p-2">Milz (SP)</td>
                    <td className="p-2">136.1 Hz</td>
                    <td className="p-2">9-11 Uhr</td>
                    <td className="p-2">204.15 Hz</td>
                    <td className="p-2">Müdigkeit, Blutmangel, Grübeln</td>
                  </tr>
                  <tr className="border-b border-white/10">
                    <td className="p-2">Herz (HE)</td>
                    <td className="p-2">341.3 Hz</td>
                    <td className="p-2">11-13 Uhr</td>
                    <td className="p-2">512.0 Hz</td>
                    <td className="p-2">Herzrhythmus, Freude, Bewusstsein</td>
                  </tr>
                  <tr className="border-b border-white/10">
                    <td className="p-2">Dünndarm (SI)</td>
                    <td className="p-2">319.9 Hz</td>
                    <td className="p-2">13-15 Uhr</td>
                    <td className="p-2">479.85 Hz</td>
                    <td className="p-2">Nährstoffaufnahme, Unterscheidung</td>
                  </tr>
                  <tr className="border-b border-white/10">
                    <td className="p-2">Blase (BL)</td>
                    <td className="p-2">256.0 Hz</td>
                    <td className="p-2">15-17 Uhr</td>
                    <td className="p-2">384.0 Hz</td>
                    <td className="p-2">Wasserstoffwechsel, Angst, Flexibilität</td>
                  </tr>
                  <tr className="border-b border-white/10">
                    <td className="p-2">Niere (KI)</td>
                    <td className="p-2">194.18 Hz</td>
                    <td className="p-2">17-19 Uhr</td>
                    <td className="p-2">291.27 Hz</td>
                    <td className="p-2">Erschöpfung, Willenskraft, Lebensessenz</td>
                  </tr>
                  <tr className="border-b border-white/10">
                    <td className="p-2">Perikard (PC)</td>
                    <td className="p-2">432.0 Hz</td>
                    <td className="p-2">19-21 Uhr</td>
                    <td className="p-2">648.0 Hz</td>
                    <td className="p-2">Herzschutz, Entspannung, Beziehungen</td>
                  </tr>
                  <tr className="border-b border-white/10">
                    <td className="p-2">3-Erwärmer (TE)</td>
                    <td className="p-2">384.0 Hz</td>
                    <td className="p-2">21-23 Uhr</td>
                    <td className="p-2">576.0 Hz</td>
                    <td className="p-2">Thermoregulation, Lymphsystem</td>
                  </tr>
                  <tr className="border-b border-white/10">
                    <td className="p-2">Gallenblase (GB)</td>
                    <td className="p-2">183.58 Hz</td>
                    <td className="p-2">23-1 Uhr</td>
                    <td className="p-2">275.37 Hz</td>
                    <td className="p-2">Entscheidungen, Mut, Sehstörungen</td>
                  </tr>
                  <tr className="border-b border-white/10">
                    <td className="p-2">Leber (LV)</td>
                    <td className="p-2">183.58 Hz</td>
                    <td className="p-2">1-3 Uhr</td>
                    <td className="p-2">275.37 Hz</td>
                    <td className="p-2">Entgiftung, Wut, Flexibilität</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div className="bg-green-500/20 p-4 rounded-lg">
            <h3 className="text-xl font-semibold mb-3 flex items-center gap-2">
              <Clock className="h-5 w-5" />
              Chronotherapie - Zeitbasierte Meridian-Behandlung
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-black/20 p-3 rounded">
                <h4 className="font-semibold mb-2 text-green-300">Morgenstunden (3-11 Uhr):</h4>
                <div className="text-sm space-y-1">
                  <p><strong>3-5 Uhr Lunge:</strong> 261.9 Hz - Atemprobleme</p>
                  <p><strong>5-7 Uhr Dickdarm:</strong> 294.0 Hz - Entgiftung</p>
                  <p><strong>7-9 Uhr Magen:</strong> 165.0 Hz - Verdauungsstart</p>
                  <p><strong>9-11 Uhr Milz:</strong> 204.15 Hz - Energieaufbau</p>
                </div>
                <p className="text-xs mt-2 text-green-200">
                  <strong>Optimum:</strong> Yang-Energie steigt, Reinigung und Aktivierung
                </p>
              </div>
              
              <div className="bg-black/20 p-3 rounded">
                <h4 className="font-semibold mb-2 text-blue-300">Abendstunden (15-23 Uhr):</h4>
                <div className="text-sm space-y-1">
                  <p><strong>15-17 Uhr Blase:</strong> 384.0 Hz - Ausscheidung</p>
                  <p><strong>17-19 Uhr Niere:</strong> 291.27 Hz - Regeneration</p>
                  <p><strong>19-21 Uhr Perikard:</strong> 648.0 Hz - Entspannung</p>
                  <p><strong>21-23 Uhr 3-Erwärmer:</strong> 576.0 Hz - Wärmeregulation</p>
                </div>
                <p className="text-xs mt-2 text-blue-200">
                  <strong>Optimum:</strong> Yin-Energie dominiert, Entspannung und Heilung
                </p>
              </div>
            </div>
          </div>

          <div className="bg-purple-500/20 p-4 rounded-lg">
            <h3 className="text-xl font-semibold mb-3">Spezielle Meridian-Frequenz-Kombinationen</h3>
            <div className="space-y-4">
              <div className="bg-black/20 p-3 rounded">
                <h4 className="font-semibold mb-2">Gekoppelte Meridiane (Yin-Yang-Paare):</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <div className="space-y-1 text-sm">
                    <p><strong>Lunge-Dickdarm:</strong> 174.6 + 196.0 Hz</p>
                    <p><strong>Magen-Milz:</strong> 110.0 + 136.1 Hz</p>
                    <p><strong>Herz-Dünndarm:</strong> 341.3 + 319.9 Hz</p>
                    <p><strong>Blase-Niere:</strong> 256.0 + 194.18 Hz</p>
                  </div>
                  <div className="space-y-1 text-sm">
                    <p><strong>Perikard-3E:</strong> 432.0 + 384.0 Hz</p>
                    <p><strong>Gallenblase-Leber:</strong> 183.58 + 183.58 Hz*</p>
                    <p className="text-xs text-gray-300">*Resonanz-Verstärkung</p>
                  </div>
                </div>
              </div>
              
              <div className="bg-black/20 p-3 rounded">
                <h4 className="font-semibold mb-2">Elementare Meridian-Gruppen:</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <div className="bg-red-900/30 p-2 rounded">
                    <h5 className="font-semibold text-red-300">Feuer-Element:</h5>
                    <p className="text-sm">Herz (341.3) + Dünndarm (319.9) + Perikard (432.0) + 3E (384.0) Hz</p>
                    <p className="text-xs">Freude, Bewusstsein, Kommunikation</p>
                  </div>
                  <div className="bg-yellow-900/30 p-2 rounded">
                    <h5 className="font-semibold text-yellow-300">Erde-Element:</h5>
                    <p className="text-sm">Magen (110.0) + Milz (136.1) Hz</p>
                    <p className="text-xs">Verdauung, Sorgen, Mitgefühl</p>
                  </div>
                  <div className="bg-gray-700/30 p-2 rounded">
                    <h5 className="font-semibold text-gray-300">Metall-Element:</h5>
                    <p className="text-sm">Lunge (174.6) + Dickdarm (196.0) Hz</p>
                    <p className="text-xs">Atmung, Haut, Trauer, Loslassen</p>
                  </div>
                  <div className="bg-blue-900/30 p-2 rounded">
                    <h5 className="font-semibold text-blue-300">Wasser-Element:</h5>
                    <p className="text-sm">Niere (194.18) + Blase (256.0) Hz</p>
                    <p className="text-xs">Willenskraft, Angst, Lebensessenz</p>
                  </div>
                  <div className="bg-green-900/30 p-2 rounded">
                    <h5 className="font-semibold text-green-300">Holz-Element:</h5>
                    <p className="text-sm">Leber (183.58) + Gallenblase (183.58) Hz</p>
                    <p className="text-xs">Flexibilität, Wut, Planung</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-orange-500/20 p-4 rounded-lg">
            <h3 className="text-xl font-semibold mb-3 flex items-center gap-2">
              <Activity className="h-5 w-5" />
              Meridian-Diagnoseverfahren und Frequenz-Anpassung
            </h3>
            <div className="space-y-4">
              <div className="bg-black/20 p-3 rounded">
                <h4 className="font-semibold mb-2">Ryodoraku-Messung zur Frequenz-Bestimmung:</h4>
                <div className="overflow-x-auto">
                  <table className="w-full text-xs">
                    <thead>
                      <tr className="border-b border-white/20">
                        <th className="text-left p-1">Messwert (µA)</th>
                        <th className="text-left p-1">Energiezustand</th>
                        <th className="text-left p-1">Frequenz-Anpassung</th>
                        <th className="text-left p-1">Behandlungsdauer</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr className="border-b border-white/10">
                        <td className="p-1">&lt; 20 µA</td>
                        <td className="p-1">Sehr schwach (Kyo)</td>
                        <td className="p-1">Grundfrequenz × 0.5</td>
                        <td className="p-1">15-20 Min</td>
                      </tr>
                      <tr className="border-b border-white/10">
                        <td className="p-1">20-40 µA</td>
                        <td className="p-1">Schwach</td>
                        <td className="p-1">Grundfrequenz × 0.75</td>
                        <td className="p-1">12-15 Min</td>
                      </tr>
                      <tr className="border-b border-white/10">
                        <td className="p-1">40-80 µA</td>
                        <td className="p-1">Normal</td>
                        <td className="p-1">Grundfrequenz × 1.0</td>
                        <td className="p-1">8-10 Min</td>
                      </tr>
                      <tr className="border-b border-white/10">
                        <td className="p-1">80-120 µA</td>
                        <td className="p-1">Überaktiv</td>
                        <td className="p-1">Grundfrequenz × 1.25</td>
                        <td className="p-1">5-8 Min</td>
                      </tr>
                      <tr className="border-b border-white/10">
                        <td className="p-1">&gt; 120 µA</td>
                        <td className="p-1">Sehr überaktiv (Jitsu)</td>
                        <td className="p-1">Grundfrequenz × 1.5</td>
                        <td className="p-1">3-5 Min</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
              
              <div className="bg-black/20 p-3 rounded">
                <h4 className="font-semibold mb-2">Puls-Diagnose und Frequenz-Modulation:</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  <div className="text-sm">
                    <p><strong>Schwacher Puls:</strong></p>
                    <p>Grundfrequenz + Subharmonische</p>
                    <p>z.B. 174.6 + 87.3 Hz</p>
                  </div>
                  <div className="text-sm">
                    <p><strong>Starker Puls:</strong></p>
                    <p>Grundfrequenz + Beruhigung</p>
                    <p>z.B. 174.6 + 116.4 Hz (2/3)</p>
                  </div>
                  <div className="text-sm">
                    <p><strong>Unregelmäßiger Puls:</strong></p>
                    <p>Modulierte Frequenz</p>
                    <p>z.B. 174.6 Hz ± 3-7 Hz/sek</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-red-500/20 p-4 rounded-lg">
            <h3 className="text-xl font-semibold mb-3 flex items-center gap-2">
              <Target className="h-5 w-5" />
              Praktische Meridian-Frequenz-Protokolle
            </h3>
            <div className="space-y-4">
              <div className="bg-black/20 p-3 rounded">
                <h4 className="font-semibold mb-2">Tägliche Meridian-Pflege (20 Min Programm):</h4>
                <div className="text-sm space-y-1">
                  <p><strong>06:00-06:05:</strong> Dickdarm 294.0 Hz - Ausscheidung aktivieren</p>
                  <p><strong>06:05-06:10:</strong> Magen 165.0 Hz - Verdauung vorbereiten</p>
                  <p><strong>06:10-06:15:</strong> Milz 204.15 Hz - Energie aufbauen</p>
                  <p><strong>06:15-06:20:</strong> Alle Meridiane 183.58 Hz - Harmonisierung</p>
                </div>
              </div>
              
              <div className="bg-black/20 p-3 rounded">
                <h4 className="font-semibold mb-2">Stress-Abbau-Protokoll:</h4>
                <div className="text-sm space-y-1">
                  <p><strong>Phase 1:</strong> Leber 183.58 Hz - 5 Min (Wut abbauen)</p>
                  <p><strong>Phase 2:</strong> Herz 341.3 Hz - 8 Min (Ruhe finden)</p>
                  <p><strong>Phase 3:</strong> Niere 194.18 Hz - 7 Min (Kraft sammeln)</p>
                  <p><strong>Integration:</strong> Alle drei gleichzeitig - 5 Min</p>
                </div>
              </div>
              
              <div className="bg-black/20 p-3 rounded">
                <h4 className="font-semibold mb-2">Immunsystem-Stärkung:</h4>
                <div className="text-sm space-y-1">
                  <p><strong>Morgens:</strong> Milz 204.15 Hz + Magen 165.0 Hz (10 Min)</p>
                  <p><strong>Mittags:</strong> Herz 341.3 Hz + Dünndarm 319.9 Hz (8 Min)</p>
                  <p><strong>Abends:</strong> Niere 194.18 Hz + Lunge 174.6 Hz (12 Min)</p>
                </div>
              </div>
            </div>
          </div>

          <Alert className="bg-amber-500/20 border-amber-500/50">
            <MapPin className="h-4 w-4" />
            <AlertDescription className="text-white">
              <strong>Meridian-Behandlung Hinweise:</strong> Behandeln Sie nie mehr als 3 Meridiane 
              gleichzeitig. Beachten Sie die natürlichen Aktivitätszeiten der Organe. 
              Bei akuten Beschwerden immer zuerst das betroffene Organ-Meridian-Paar behandeln.
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    </div>
  );
};

export default MeridianFrequenzen;

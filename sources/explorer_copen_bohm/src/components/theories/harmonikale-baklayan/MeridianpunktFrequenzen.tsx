
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { MapPin, Zap, Target, Activity } from "lucide-react";

const MeridianpunktFrequenzen = () => {
  return (
    <div className="space-y-6">
      <Card className="bg-white/10 border-white/20 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-2xl text-white flex items-center gap-2">
            <MapPin className="h-6 w-6" />
            Meridianpunkt-Frequenzen nach Baklayan
          </CardTitle>
        </CardHeader>
        <CardContent className="text-white space-y-6">
          
          <div className="bg-red-500/20 p-4 rounded-lg">
            <h3 className="text-xl font-semibold mb-3">Haupt-Akupunkturpunkte mit spezifischen Frequenzen</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-white/20">
                    <th className="text-left p-2">Punkt</th>
                    <th className="text-left p-2">Meridian</th>
                    <th className="text-left p-2">Frequenz (Hz)</th>
                    <th className="text-left p-2">Hauptwirkung</th>
                    <th className="text-left p-2">Behandlungszeit</th>
                  </tr>
                </thead>
                <tbody>
                  <tr className="border-b border-white/10">
                    <td className="p-2">LG 20 (Baihui)</td>
                    <td className="p-2">Lenkergefäß</td>
                    <td className="p-2">1000.0 Hz</td>
                    <td className="p-2">Geistige Klarheit, Kronenchakra</td>
                    <td className="p-2">3-5 Min</td>
                  </tr>
                  <tr className="border-b border-white/10">
                    <td className="p-2">EX-HN 3 (Yintang)</td>
                    <td className="p-2">Extrapunkt</td>
                    <td className="p-2">852.0 Hz</td>
                    <td className="p-2">Drittes Auge, Intuition</td>
                    <td className="p-2">4-6 Min</td>
                  </tr>
                  <tr className="border-b border-white/10">
                    <td className="p-2">CV 17 (Shanzhong)</td>
                    <td className="p-2">Konzeptionsgefäß</td>
                    <td className="p-2">639.0 Hz</td>
                    <td className="p-2">Herzchakra, Emotionen</td>
                    <td className="p-2">5-8 Min</td>
                  </tr>
                  <tr className="border-b border-white/10">
                    <td className="p-2">CV 12 (Zhongwan)</td>
                    <td className="p-2">Konzeptionsgefäß</td>
                    <td className="p-2">528.0 Hz</td>
                    <td className="p-2">Solarplexus, Verdauung</td>
                    <td className="p-2">6-10 Min</td>
                  </tr>
                  <tr className="border-b border-white/10">
                    <td className="p-2">CV 6 (Qihai)</td>
                    <td className="p-2">Konzeptionsgefäß</td>
                    <td className="p-2">417.0 Hz</td>
                    <td className="p-2">Sakralchakra, Lebensenergie</td>
                    <td className="p-2">8-12 Min</td>
                  </tr>
                  <tr className="border-b border-white/10">
                    <td className="p-2">CV 4 (Guanyuan)</td>
                    <td className="p-2">Konzeptionsgefäß</td>
                    <td className="p-2">396.0 Hz</td>
                    <td className="p-2">Wurzelchakra, Erdung</td>
                    <td className="p-2">10-15 Min</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div className="bg-blue-500/20 p-4 rounded-lg">
            <h3 className="text-xl font-semibold mb-3">Organsystem-spezifische Punkte</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-3">
                <div className="bg-black/20 p-3 rounded">
                  <h4 className="font-semibold mb-2 text-blue-300">Lungen-System:</h4>
                  <div className="text-sm space-y-1">
                    <p><strong>LU 9 (Taiyuan):</strong> 174.6 Hz - Atemwege öffnen</p>
                    <p><strong>LU 5 (Chize):</strong> 220.0 Hz - Bronchien entspannen</p>
                    <p><strong>LU 1 (Zhongfu):</strong> 293.7 Hz - Lungenentzündung</p>
                    <p><strong>Behandlung:</strong> 5-8 Min pro Punkt</p>
                  </div>
                </div>
                
                <div className="bg-black/20 p-3 rounded">
                  <h4 className="font-semibold mb-2 text-green-300">Herz-System:</h4>
                  <div className="text-sm space-y-1">
                    <p><strong>HE 7 (Shenmen):</strong> 341.3 Hz - Herzrhythmus</p>
                    <p><strong>HE 3 (Shaohai):</strong> 256.0 Hz - Blutdruck</p>
                    <p><strong>PC 6 (Neiguan):</strong> 432.0 Hz - Herzschutz</p>
                    <p><strong>Behandlung:</strong> 3-6 Min pro Punkt</p>
                  </div>
                </div>
              </div>
              
              <div className="space-y-3">
                <div className="bg-black/20 p-3 rounded">
                  <h4 className="font-semibold mb-2 text-yellow-300">Verdauungs-System:</h4>
                  <div className="text-sm space-y-1">
                    <p><strong>ST 36 (Zusanli):</strong> 110.0 Hz - Immunsystem</p>
                    <p><strong>SP 6 (Sanyinjiao):</strong> 136.1 Hz - Milz stärken</p>
                    <p><strong>ST 6 (Jiache):</strong> 147.0 Hz - Magen regulieren</p>
                    <p><strong>Behandlung:</strong> 8-12 Min pro Punkt</p>
                  </div>
                </div>
                
                <div className="bg-black/20 p-3 rounded">
                  <h4 className="font-semibold mb-2 text-purple-300">Nieren-System:</h4>
                  <div className="text-sm space-y-1">
                    <p><strong>KI 3 (Taixi):</strong> 194.2 Hz - Nierenenergie</p>
                    <p><strong>KI 1 (Yongquan):</strong> 68.05 Hz - Erdung</p>
                    <p><strong>BL 23 (Shenshu):</strong> 210.4 Hz - Rückenstärkung</p>
                    <p><strong>Behandlung:</strong> 6-10 Min pro Punkt</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-green-500/20 p-4 rounded-lg">
            <h3 className="text-xl font-semibold mb-3 flex items-center gap-2">
              <Zap className="h-5 w-5" />
              Meister-Punkte mit Harmonikalen Frequenzen
            </h3>
            <div className="space-y-4">
              <div className="bg-black/20 p-3 rounded">
                <h4 className="font-semibold mb-2">Die 8 Einflussreichen Punkte (Ba Hui Xue)</h4>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-white/20">
                        <th className="text-left p-2">Punkt</th>
                        <th className="text-left p-2">Beeinflusst</th>
                        <th className="text-left p-2">Grundfrequenz</th>
                        <th className="text-left p-2">Harmonische</th>
                        <th className="text-left p-2">Therapiefrequenz</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr className="border-b border-white/10">
                        <td className="p-2">LU 9</td>
                        <td className="p-2">Gefäße</td>
                        <td className="p-2">174.6 Hz</td>
                        <td className="p-2">349.2, 698.4</td>
                        <td className="p-2">261.9 Hz (Quinte)</td>
                      </tr>
                      <tr className="border-b border-white/10">
                        <td className="p-2">GB 34</td>
                        <td className="p-2">Sehnen</td>
                        <td className="p-2">183.6 Hz</td>
                        <td className="p-2">367.2, 734.4</td>
                        <td className="p-2">275.4 Hz</td>
                      </tr>
                      <tr className="border-b border-white/10">
                        <td className="p-2">BL 11</td>
                        <td className="p-2">Knochen</td>
                        <td className="p-2">126.2 Hz</td>
                        <td className="p-2">252.4, 504.8</td>
                        <td className="p-2">189.3 Hz</td>
                      </tr>
                      <tr className="border-b border-white/10">
                        <td className="p-2">ST 36</td>
                        <td className="p-2">Qi & Blut</td>
                        <td className="p-2">110.0 Hz</td>
                        <td className="p-2">220.0, 440.0</td>
                        <td className="p-2">165.0 Hz</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-orange-500/20 p-4 rounded-lg">
            <h3 className="text-xl font-semibold mb-3 flex items-center gap-2">
              <Target className="h-5 w-5" />
              Behandlungsebenen der Meridianpunkte
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-black/20 p-3 rounded">
                <h4 className="font-semibold mb-2 text-orange-300">Oberflächenebene (Wei)</h4>
                <div className="text-sm space-y-1">
                  <p><strong>Frequenzbereich:</strong> 7-30 Hz</p>
                  <p><strong>Eindringtiefe:</strong> 2-5 mm</p>
                  <p><strong>Wirkungsdauer:</strong> Sofort-2h</p>
                  <p><strong>Anwendung:</strong> Akute Symptome</p>
                  <p><strong>Punkte:</strong> Ashi-Punkte, lokale Schmerzpunkte</p>
                </div>
              </div>
              
              <div className="bg-black/20 p-3 rounded">
                <h4 className="font-semibold mb-2 text-blue-300">Meridianebene (Jing)</h4>
                <div className="text-sm space-y-1">
                  <p><strong>Frequenzbereich:</strong> 50-300 Hz</p>
                  <p><strong>Eindringtiefe:</strong> 1-3 cm</p>
                  <p><strong>Wirkungsdauer:</strong> 2-24h</p>
                  <p><strong>Anwendung:</strong> Funktionsstörungen</p>
                  <p><strong>Punkte:</strong> Yuan-Punkte, Shu-Punkte</p>
                </div>
              </div>
              
              <div className="bg-black/20 p-3 rounded">
                <h4 className="font-semibold mb-2 text-purple-300">Organebene (Zang-Fu)</h4>
                <div className="text-sm space-y-1">
                  <p><strong>Frequenzbereich:</strong> 400-2000 Hz</p>
                  <p><strong>Eindringtiefe:</strong> 5-15 cm</p>
                  <p><strong>Wirkungsdauer:</strong> 1-7 Tage</p>
                  <p><strong>Anwendung:</strong> Chronische Leiden</p>
                  <p><strong>Punkte:</strong> Mu-Punkte, Shu-Punkte des Rückens</p>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-purple-500/20 p-4 rounded-lg">
            <h3 className="text-xl font-semibold mb-3">Spezielle Frequenz-Kombinationen für Punktgruppen</h3>
            <div className="space-y-3">
              <div className="bg-black/20 p-3 rounded">
                <h4 className="font-semibold mb-2">Vier Große Punkte (Si Da Xue):</h4>
                <div className="text-sm space-y-1">
                  <p><strong>Hegu (LI 4):</strong> 256.0 Hz + Taichong (LV 3): 183.6 Hz</p>
                  <p><strong>Kombination:</strong> Binaurale Beats mit 72.4 Hz Differenz</p>
                  <p><strong>Wirkung:</strong> Qi-Regulation im ganzen Körper</p>
                  <p><strong>Behandlung:</strong> Beide Punkte gleichzeitig, 15 Min</p>
                </div>
              </div>
              
              <div className="bg-black/20 p-3 rounded">
                <h4 className="font-semibold mb-2">Himmlische Pfeilern (Tianmen):</h4>
                <div className="text-sm space-y-1">
                  <p><strong>Fengchi (GB 20):</strong> 110.0 Hz</p>
                  <p><strong>Baihui (GV 20):</strong> 1000.0 Hz</p>
                  <p><strong>Sequenz:</strong> Aufsteigend von 110 zu 1000 Hz über 10 Min</p>
                  <p><strong>Wirkung:</strong> Bewusstseinserweiterung, Kopfschmerzen</p>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default MeridianpunktFrequenzen;


import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Settings, Zap, Gauge, Radio } from "lucide-react";

const GeraeteTechnologie = () => {
  return (
    <div className="space-y-6">
      <Card className="bg-white/10 border-white/20 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-2xl text-white flex items-center gap-2">
            <Settings className="h-6 w-6" />
            Rayonex Geräte-Technologie
          </CardTitle>
        </CardHeader>
        <CardContent className="text-white space-y-6">
          
          <div className="bg-blue-500/20 p-4 rounded-lg">
            <h3 className="text-xl font-semibold mb-3 flex items-center gap-2">
              <Zap className="h-5 w-5" />
              PS 1000 polar - Technische Spezifikationen
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-black/20 p-3 rounded">
                <h4 className="font-semibold mb-2 text-blue-300">Frequenz-Parameter:</h4>
                <ul className="space-y-1 text-sm">
                  <li><strong>Frequenzbereich:</strong> 0,1 Hz - 10 MHz</li>
                  <li><strong>Auflösung:</strong> 0,1 Hz (Feinabstimmung)</li>
                  <li><strong>Genauigkeit:</strong> ±0,01% (Quarz-referenziert)</li>
                  <li><strong>Stabilität:</strong> ±1 ppm über 24h</li>
                  <li><strong>Bereiche:</strong> 7 Dekaden abdeckend</li>
                </ul>
              </div>
              
              <div className="bg-black/20 p-3 rounded">
                <h4 className="font-semibold mb-2 text-green-300">Hardware-Spezifikationen:</h4>
                <ul className="space-y-1 text-sm">
                  <li><strong>Ausgangsleistung:</strong> 0,1-10 mW einstellbar</li>
                  <li><strong>Impedanz:</strong> 50 Ω / 75 Ω schaltbar</li>
                  <li><strong>Modulationen:</strong> AM (0,1-100 Hz), FM (±10 Hz)</li>
                  <li><strong>Rauschunterdrückung:</strong> &gt;60 dB</li>
                  <li><strong>Steuerung:</strong> 32-Bit Mikrocontroller</li>
                </ul>
              </div>
            </div>
          </div>

          <div className="bg-green-500/20 p-4 rounded-lg">
            <h3 className="text-xl font-semibold mb-3 flex items-center gap-2">
              <Radio className="h-5 w-5" />
              Dipol-Antennen-System
            </h3>
            <div className="space-y-4">
              <div className="bg-black/20 p-3 rounded">
                <h4 className="font-semibold mb-2">Antennen-Konfiguration:</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                  <div>
                    <strong>Sende-Antenne:</strong>
                    <ul className="list-disc pl-4 mt-1">
                      <li>λ/4 Monopol bei Grundfrequenz</li>
                      <li>Automatische Anpassung 0,1 Hz - 10 MHz</li>
                      <li>SWR &lt; 1,2 über gesamten Bereich</li>
                      <li>Abstrahlcharakteristik: Rundstrahl</li>
                    </ul>
                  </div>
                  <div>
                    <strong>Empfangs-Antenne:</strong>
                    <ul className="list-disc pl-4 mt-1">
                      <li>Ferrit-Rahmen für LF/MF</li>
                      <li>Teleskop-Dipol für HF</li>
                      <li>Empfindlichkeit: -120 dBm</li>
                      <li>Bandbreite: ±0,1% um Sollfrequenz</li>
                    </ul>
                  </div>
                </div>
              </div>
              
              <div className="bg-black/20 p-3 rounded">
                <h4 className="font-semibold mb-2">Resonanz-Detektion:</h4>
                <div className="font-mono text-sm space-y-1">
                  <div><strong>Reflexionsfaktor:</strong> Γ = (Z_L - Z_0)/(Z_L + Z_0)</div>
                  <div><strong>Resonanz-Kriterium:</strong> |Γ| &lt; 0,1 (SWR &lt; 1,22)</div>
                  <div><strong>Phasen-Messung:</strong> Genauigkeit ±0,1° bei f &gt; 1 MHz</div>
                  <div><strong>Amplituden-Stabilität:</strong> ±0,1 dB über Temperaturbereich</div>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-purple-500/20 p-4 rounded-lg">
            <h3 className="text-xl font-semibold mb-3 flex items-center gap-2">
              <Gauge className="h-5 w-5" />
              Kalibrierung und Qualitätskontrolle
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-black/20 p-3 rounded">
                <h4 className="font-semibold mb-2 text-purple-300">Automatische Kalibrierung:</h4>
                <ul className="space-y-1 text-sm">
                  <li><strong>Frequenz-Referenz:</strong> 10 MHz Quarz-Oszillator</li>
                  <li><strong>Selbsttest:</strong> Alle 24h automatisch</li>
                  <li><strong>Standard-Kalibrierung:</strong> 50 Ω Referenz-Last</li>
                  <li><strong>Biologische Kalibrierung:</strong> H₂O-Standard</li>
                  <li><strong>Zertifizierung:</strong> NIST-rückführbar</li>
                </ul>
              </div>
              
              <div className="bg-black/20 p-3 rounded">
                <h4 className="font-semibold mb-2 text-yellow-300">Wartungsintervalle:</h4>
                <ul className="space-y-1 text-sm">
                  <li><strong>Täglich:</strong> Funktionstest, Selbstkalibrierung</li>
                  <li><strong>Wöchentlich:</strong> Antennen-Reinigung</li>
                  <li><strong>Monatlich:</strong> Vollständige Kalibrierung</li>
                  <li><strong>Jährlich:</strong> Werks-Kalibrierung</li>
                  <li><strong>Bei Bedarf:</strong> Reparatur/Austausch</li>
                </ul>
              </div>
            </div>
          </div>

          <div className="bg-teal-500/20 p-4 rounded-lg">
            <h3 className="text-xl font-semibold mb-3">Geräte-Vergleich</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-white/20">
                    <th className="text-left p-2">Modell</th>
                    <th className="text-left p-2">Frequenzbereich</th>
                    <th className="text-left p-2">Leistung</th>
                    <th className="text-left p-2">Anwendung</th>
                    <th className="text-left p-2">Preis-Segment</th>
                  </tr>
                </thead>
                <tbody>
                  <tr className="border-b border-white/10">
                    <td className="p-2 font-medium">PS 10</td>
                    <td className="p-2">0,1 Hz - 1 MHz</td>
                    <td className="p-2">0,1-1 mW</td>
                    <td className="p-2">Basis-Diagnostik</td>
                    <td className="p-2">Einsteiger</td>
                  </tr>
                  <tr className="border-b border-white/10">
                    <td className="p-2 font-medium">PS 1000 polar</td>
                    <td className="p-2">0,1 Hz - 10 MHz</td>
                    <td className="p-2">0,1-10 mW</td>
                    <td className="p-2">Profi-Diagnostik/Therapie</td>
                    <td className="p-2">Professional</td>
                  </tr>
                  <tr className="border-b border-white/10">
                    <td className="p-2 font-medium">Rayocomp PS 1000</td>
                    <td className="p-2">0,1 Hz - 10 MHz</td>
                    <td className="p-2">0,1-50 mW</td>
                    <td className="p-2">Klinik/Praxis</td>
                    <td className="p-2">Premium</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card className="bg-white/10 border-white/20 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-xl text-white">
            Software und Datenbank-Integration
          </CardTitle>
        </CardHeader>
        <CardContent className="text-white space-y-4">
          <div className="bg-indigo-500/20 p-4 rounded-lg">
            <h4 className="font-semibold mb-2">RAH-Software Features:</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div>
                <strong>Diagnostik-Module:</strong>
                <ul className="list-disc pl-4 mt-1">
                  <li>Automatischer Frequenz-Scan</li>
                  <li>Pathogen-Datenbank (&gt;10.000 Einträge)</li>
                  <li>Harmonische Analyse</li>
                  <li>Verlaufsdokumentation</li>
                </ul>
              </div>
              <div>
                <strong>Therapie-Module:</strong>
                <ul className="list-disc pl-4 mt-1">
                  <li>Programmierbare Behandlungssequenzen</li>
                  <li>Individuelle Frequenz-Listen</li>
                  <li>Timer und Dosierung</li>
                  <li>Behandlungsprotokolle</li>
                </ul>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default GeraeteTechnologie;

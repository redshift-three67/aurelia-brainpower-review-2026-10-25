
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const ElektromagnetischeFelder = () => {
  return (
    <div className="space-y-6">
      <Card className="bg-white/10 border-white/20 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-white text-2xl">Elektromagnetische Felder & Biologie</CardTitle>
        </CardHeader>
        <CardContent className="text-white space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-blue-300">Bioelektromagnetismus nach Broers</h3>
              <div className="space-y-3 text-gray-200">
                <div className="p-3 bg-blue-900/30 rounded">
                  <strong className="text-blue-200">Zellmembran-Potentiale:</strong> -70mV Ruhepotential
                </div>
                <div className="p-3 bg-blue-900/30 rounded">
                  <strong className="text-blue-200">DNA-Frequenzen:</strong> 150 MHz Resonanz
                </div>
                <div className="p-3 bg-blue-900/30 rounded">
                  <strong className="text-blue-200">Mikrotubuli:</strong> 40 GHz Schwingungen
                </div>
                <div className="p-3 bg-blue-900/30 rounded">
                  <strong className="text-blue-200">Herzfeld:</strong> 2,5m Radius um Körper
                </div>
              </div>
            </div>
            
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-green-300">Therapeutische Frequenzen</h3>
              <ul className="space-y-2 text-gray-200">
                <li>• 7,83 Hz - Schumann-Resonanz (Erdfeld)</li>
                <li>• 10 Hz - Alpha-Synchronisation</li>
                <li>• 40 Hz - Gamma-Bewusstsein</li>
                <li>• 528 Hz - DNA-Reparatur-Frequenz</li>
                <li>• 741 Hz - Zellentgiftung</li>
                <li>• 963 Hz - Pinealdrüsen-Aktivierung</li>
              </ul>
            </div>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-purple-300">ELF-Felder (Extremely Low Frequency)</h3>
              <div className="space-y-3">
                <div className="bg-purple-900/20 p-3 rounded">
                  <h4 className="font-semibold text-purple-200">0,1 - 30 Hz</h4>
                  <p className="text-gray-300 text-sm">
                    Beeinflussen Melatonin-Produktion und circadiane Rhythmen
                  </p>
                </div>
                <div className="bg-purple-900/20 p-3 rounded">
                  <h4 className="font-semibold text-purple-200">Biologische Wirkung</h4>
                  <p className="text-gray-300 text-sm">
                    Modulation von Calcium-Ionen-Fluss in Zellmembranen
                  </p>
                </div>
              </div>
            </div>
            
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-yellow-300">VLF-Felder (Very Low Frequency)</h3>
              <div className="space-y-3">
                <div className="bg-yellow-900/20 p-3 rounded">
                  <h4 className="font-semibold text-yellow-200">3 - 30 kHz</h4>
                  <p className="text-gray-300 text-sm">
                    Resonanz mit Protein-Strukturen und Enzymsystemen
                  </p>
                </div>
                <div className="bg-yellow-900/20 p-3 rounded">
                  <h4 className="font-semibold text-yellow-200">Zelluläre Effekte</h4>
                  <p className="text-gray-300 text-sm">
                    Aktivierung von Reparatur-Mechanismen und Immunsystem
                  </p>
                </div>
              </div>
            </div>
            
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-red-300">HF-Felder (High Frequency)</h3>
              <div className="space-y-3">
                <div className="bg-red-900/20 p-3 rounded">
                  <h4 className="font-semibold text-red-200">30 kHz - 300 GHz</h4>
                  <p className="text-gray-300 text-sm">
                    Mikrowellen-Resonanz mit Wassermolekülen
                  </p>
                </div>
                <div className="bg-red-900/20 p-3 rounded">
                  <h4 className="font-semibold text-red-200">Molekulare Ebene</h4>
                  <p className="text-gray-300 text-sm">
                    Beeinflussung von Biomolekülen und Zellkommunikation
                  </p>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ElektromagnetischeFelder;

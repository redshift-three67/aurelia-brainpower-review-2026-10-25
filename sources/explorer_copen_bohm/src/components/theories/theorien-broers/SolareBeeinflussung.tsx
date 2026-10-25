
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const SolareBeeinflussung = () => {
  return (
    <div className="space-y-6">
      <Card className="bg-white/10 border-white/20 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-white text-2xl">Solare Beeinflussung des Bewusstseins</CardTitle>
        </CardHeader>
        <CardContent className="text-white space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-blue-300">Sonnenaktivität & Gehirn</h3>
              <div className="space-y-3 text-gray-200">
                <div className="p-3 bg-blue-900/30 rounded">
                  <strong className="text-blue-200">Sonnenflecken-Zyklus:</strong> 11-Jahres-Rhythmus
                </div>
                <div className="p-3 bg-blue-900/30 rounded">
                  <strong className="text-blue-200">Solare Stürme:</strong> Magnetfeld-Schwankungen
                </div>
                <div className="p-3 bg-blue-900/30 rounded">
                  <strong className="text-blue-200">Koronale Massenauswürfe:</strong> Erdmagnetfeld-Störungen
                </div>
                <div className="p-3 bg-blue-900/30 rounded">
                  <strong className="text-blue-200">Schumann-Resonanz:</strong> Variable Intensität
                </div>
              </div>
            </div>
            
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-green-300">Biologische Korrelationen</h3>
              <ul className="space-y-2 text-gray-200">
                <li>• Herzrhythmus-Variabilität (+35% bei Solarstürmen)</li>
                <li>• Melatonin-Suppression (-40% bei hoher Aktivität)</li>
                <li>• EEG-Alpha-Reduktion (-25% Amplitude)</li>
                <li>• Blutdruck-Erhöhung (+8% systolisch)</li>
                <li>• Reaktionszeit-Verlangsamung (+12%)</li>
                <li>• Epilepsie-Anfälle (+67% Häufigkeit)</li>
              </ul>
            </div>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-purple-300">Broers' Solare Hypothese</h3>
              <div className="space-y-3">
                <div className="bg-purple-900/20 p-3 rounded">
                  <h4 className="font-semibold text-purple-200">Evolutionärer Trigger</h4>
                  <p className="text-gray-300 text-sm">
                    Solare Maxima lösen Bewusstseinssprünge in der menschlichen Evolution aus.
                  </p>
                </div>
                
                <div className="bg-purple-900/20 p-3 rounded">
                  <h4 className="font-semibold text-purple-200">DNA-Aktivierung</h4>
                  <p className="text-gray-300 text-sm">
                    Elektromagnetische Solar-Impulse aktivieren "schlafende" DNA-Sequenzen.
                  </p>
                </div>
                
                <div className="bg-purple-900/20 p-3 rounded">
                  <h4 className="font-semibold text-purple-200">Kollektives Bewusstsein</h4>
                  <p className="text-gray-300 text-sm">
                    Globale Synchronisation menschlicher Gehirnaktivität durch Erdmagnetfeld.
                  </p>
                </div>
              </div>
            </div>
            
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-yellow-300">Historische Korrelationen</h3>
              <div className="space-y-3">
                <div className="bg-yellow-900/20 p-3 rounded">
                  <h4 className="font-semibold text-yellow-200">1859 - Carrington-Event</h4>
                  <p className="text-gray-300 text-sm">
                    Stärkster dokumentierter Sonnensturm, zeitgleich mit Darwin's Evolutionstheorie
                  </p>
                </div>
                
                <div className="bg-yellow-900/20 p-3 rounded">
                  <h4 className="font-semibold text-yellow-200">1969 - Apollo 11</h4>
                  <p className="text-gray-300 text-sm">
                    Mondlandung während Solar-Maximum, technologischer Durchbruch
                  </p>
                </div>
                
                <div className="bg-yellow-900/20 p-3 rounded">
                  <h4 className="font-semibold text-yellow-200">2012 - Maya-Kalender</h4>
                  <p className="text-gray-300 text-sm">
                    Zeitenwende-Prophezeiung korreliert mit 11-Jahres-Sonnenzyklus
                  </p>
                </div>
              </div>
            </div>
          </div>
          
          <div className="mt-6 p-4 bg-red-900/30 rounded-lg">
            <h4 className="text-lg font-semibold text-red-200 mb-2">Broers'sche Solar-Formel</h4>
            <p className="text-gray-300 mb-2">
              "Bewusstseins-Evolution ∝ (Sonnenflecken × Magnetfeld-Intensität) / Erdmagnetfeld-Stabilität"
            </p>
            <p className="text-gray-300 text-sm">
              Diese Gleichung beschreibt die Korrelation zwischen solarer Aktivität und 
              evolutionären Bewusstseinssprüngen der Menschheit.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default SolareBeeinflussung;

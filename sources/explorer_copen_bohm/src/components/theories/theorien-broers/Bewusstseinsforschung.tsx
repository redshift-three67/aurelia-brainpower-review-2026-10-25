
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const Bewusstseinsforschung = () => {
  return (
    <div className="space-y-6">
      <Card className="bg-white/10 border-white/20 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-white text-2xl">Bewusstseinsforschung nach Broers</CardTitle>
        </CardHeader>
        <CardContent className="text-white space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-blue-300">Bewusstsein als Feldphänomen</h3>
              <div className="space-y-3 text-gray-200">
                <div className="p-3 bg-blue-900/30 rounded">
                  <strong className="text-blue-200">Grundthese:</strong> Bewusstsein entsteht durch kohärente elektromagnetische Felder im Gehirn
                </div>
                <div className="p-3 bg-blue-900/30 rounded">
                  <strong className="text-blue-200">Messbarkeit:</strong> EEG-Gamma-Wellen (40-100Hz) als Bewusstseins-Marker
                </div>
                <div className="p-3 bg-blue-900/30 rounded">
                  <strong className="text-blue-200">Resonanz:</strong> Synchronisation verschiedener Gehirnregionen
                </div>
              </div>
            </div>
            
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-green-300">Bewusstseinsebenen</h3>
              <ul className="space-y-2 text-gray-200">
                <li>• Beta-Bewusstsein (14-30 Hz) - Wachzustand</li>
                <li>• Alpha-Bewusstsein (8-13 Hz) - Entspannung</li>
                <li>• Theta-Bewusstsein (4-7 Hz) - Meditation</li>
                <li>• Delta-Bewusstsein (0,5-3 Hz) - Tiefschlaf</li>
                <li>• Gamma-Bewusstsein (40+ Hz) - Erweiterte Zustände</li>
              </ul>
            </div>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-purple-300">Experimentelle Befunde</h3>
              <div className="space-y-3">
                <div className="bg-purple-900/20 p-3 rounded">
                  <h4 className="font-semibold text-purple-200">Kohärenz-Messungen</h4>
                  <p className="text-gray-300 text-sm">
                    Höhere Bewusstseinszustände zeigen erhöhte Gamma-Kohärenz zwischen Frontal- und Parietallappen.
                  </p>
                </div>
                
                <div className="bg-purple-900/20 p-3 rounded">
                  <h4 className="font-semibold text-purple-200">Feldstärke-Korrelation</h4>
                  <p className="text-gray-300 text-sm">
                    Bewusstseins-Klarheit korreliert mit elektromagnetischer Feldstärke (r=0,73).
                  </p>
                </div>
              </div>
            </div>
            
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-yellow-300">Praktische Anwendungen</h3>
              <div className="space-y-3">
                <div className="bg-yellow-900/20 p-3 rounded">
                  <h4 className="font-semibold text-yellow-200">Neurofeedback</h4>
                  <p className="text-gray-300 text-sm">
                    Gezieltes Training spezifischer Frequenzbänder zur Bewusstseinserweiterung.
                  </p>
                </div>
                
                <div className="bg-yellow-900/20 p-3 rounded">
                  <h4 className="font-semibold text-yellow-200">Meditation-Enhancement</h4>
                  <p className="text-gray-300 text-sm">
                    Externe Frequenzgeneratoren unterstützen Eintritt in meditative Zustände.
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

export default Bewusstseinsforschung;

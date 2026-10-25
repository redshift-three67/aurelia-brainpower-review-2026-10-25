
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const DiagnoseVerfahren = () => {
  return (
    <div className="space-y-6">
      <Card className="bg-white/10 border-white/20 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-white text-2xl">Radionische Diagnose-Verfahren</CardTitle>
        </CardHeader>
        <CardContent className="text-white space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-green-300">Analyse-Methoden</h3>
              <div className="space-y-3">
                <div className="p-3 bg-green-900/20 rounded">
                  <h4 className="font-semibold text-green-200">Stick-Pad Analyse</h4>
                  <p className="text-gray-300 text-sm">
                    Taktile Reaktion auf der Detektorplatte zur Raten-Bestimmung
                  </p>
                </div>
                <div className="p-3 bg-green-900/20 rounded">
                  <h4 className="font-semibold text-green-200">Pendel-Diagnostik</h4>
                  <p className="text-gray-300 text-sm">
                    Radiästhetische Analyse mit kalibrierten Pendeln
                  </p>
                </div>
                <div className="p-3 bg-green-900/20 rounded">
                  <h4 className="font-semibold text-green-200">Kinesiologische Tests</h4>
                  <p className="text-gray-300 text-sm">
                    Muskelreaktion-basierte Resonanz-Prüfung
                  </p>
                </div>
              </div>
            </div>
            
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-yellow-300">Diagnose-Bereiche</h3>
              <div className="space-y-2 text-gray-200">
                <div className="flex items-center space-x-2">
                  <span className="w-2 h-2 bg-yellow-400 rounded-full"></span>
                  <span>Energetische Körperanalyse</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="w-2 h-2 bg-yellow-400 rounded-full"></span>
                  <span>Organ-System Bewertung</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="w-2 h-2 bg-yellow-400 rounded-full"></span>
                  <span>Toxin- und Allergen-Screening</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="w-2 h-2 bg-yellow-400 rounded-full"></span>
                  <span>Ernährungs-Kompatibilität</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="w-2 h-2 bg-yellow-400 rounded-full"></span>
                  <span>Emotionale Blockaden</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="w-2 h-2 bg-yellow-400 rounded-full"></span>
                  <span>Geistige Potentiale</span>
                </div>
              </div>
            </div>
          </div>
          
          <div className="mt-6 p-4 bg-indigo-900/30 rounded-lg">
            <h4 className="text-lg font-semibold text-indigo-200 mb-2">Ferndiagnose-Prinzip</h4>
            <p className="text-gray-300">
              Durch morphische Feldverbindung ermöglicht die Radionik Diagnosen 
              unabhängig von räumlicher Distanz mit Hilfe von Zeugen (Haare, Blut, Fotos).
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default DiagnoseVerfahren;

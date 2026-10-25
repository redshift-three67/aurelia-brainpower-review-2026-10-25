
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const CopenGrundlagen = () => {
  return (
    <div className="space-y-6">
      <Card className="bg-white/10 border-white/20 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-white text-2xl">Bruce Copen - Historische Grundlagen</CardTitle>
        </CardHeader>
        <CardContent className="text-white space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-blue-300">Biographische Daten</h3>
              <div className="space-y-3 text-gray-200">
                <div className="p-3 bg-blue-900/30 rounded">
                  <strong className="text-blue-200">1915-1998:</strong> Lebenszeit Bruce Copen
                </div>
                <div className="p-3 bg-blue-900/30 rounded">
                  <strong className="text-blue-200">1950er:</strong> Erste radionische Experimente
                </div>
                <div className="p-3 bg-blue-900/30 rounded">
                  <strong className="text-blue-200">1960er:</strong> Entwicklung eigener Geräte
                </div>
                <div className="p-3 bg-blue-900/30 rounded">
                  <strong className="text-blue-200">1978:</strong> Veröffentlichung des Copen-Algorithmus
                </div>
                <div className="p-3 bg-blue-900/30 rounded">
                  <strong className="text-blue-200">1980er-90er:</strong> Weltweite Verbreitung
                </div>
              </div>
            </div>
            
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-green-300">Revolutionäre Beiträge</h3>
              <ul className="space-y-2 text-gray-200">
                <li>• Mathematische Formalisierung der Radionik</li>
                <li>• Entwicklung reproduzierbarer Algorithmen</li>
                <li>• Integration homöopathischer Prinzipien</li>
                <li>• Standardisierung radionischer Raten</li>
                <li>• Konstruktion präziser Messgeräte</li>
                <li>• Fernbehandlungs-Protokolle</li>
              </ul>
            </div>
          </div>
          
          <div className="mt-6 p-4 bg-purple-900/30 rounded-lg">
            <h4 className="text-lg font-semibold text-purple-200 mb-2">Copen'sche Grundprinzipien</h4>
            <p className="text-gray-300">
              "Jede Substanz, jede Krankheit, jeder biologische Zustand besitzt eine charakteristische 
              Schwingungsfrequenz, die durch mathematische Algorithmen präzise bestimmt und 
              therapeutisch genutzt werden kann." - Bruce Copen, 1978
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default CopenGrundlagen;

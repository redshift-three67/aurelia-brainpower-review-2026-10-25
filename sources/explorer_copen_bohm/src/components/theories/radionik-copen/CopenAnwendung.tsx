
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const CopenAnwendung = () => {
  return (
    <div className="space-y-6">
      <Card className="bg-white/10 border-white/20 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-white text-2xl">Praktische Copen-Anwendungen</CardTitle>
        </CardHeader>
        <CardContent className="text-white space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-purple-300">Behandlungsprotokoll</h3>
              <div className="space-y-3">
                <div className="bg-purple-900/20 p-3 rounded">
                  <h4 className="font-semibold text-purple-200">1. Analyse-Phase</h4>
                  <ul className="text-gray-300 text-sm mt-1 space-y-1">
                    <li>• Zeuge (Haar/Blut/Foto) positionieren</li>
                    <li>• Grundzustand testen</li>
                    <li>• Problembereiche identifizieren</li>
                  </ul>
                </div>
                
                <div className="bg-purple-900/20 p-3 rounded">
                  <h4 className="font-semibold text-purple-200">2. Raten-Bestimmung</h4>
                  <ul className="text-gray-300 text-sm mt-1 space-y-1">
                    <li>• Störung als Wortenergie formulieren</li>
                    <li>• Copen-Algorithmus anwenden</li>
                    <li>• Rate instrumentell verifizieren</li>
                  </ul>
                </div>
                
                <div className="bg-purple-900/20 p-3 rounded">
                  <h4 className="font-semibold text-purple-200">3. Behandlung</h4>
                  <ul className="text-gray-300 text-sm mt-1 space-y-1">
                    <li>• Therapeutische Rate einstellen</li>
                    <li>• Behandlungszeit definieren (meist 15-30 Min)</li>
                    <li>• Fernübertragung aktivieren</li>
                  </ul>
                </div>
                
                <div className="bg-purple-900/20 p-3 rounded">
                  <h4 className="font-semibold text-purple-200">4. Kontrolle</h4>
                  <ul className="text-gray-300 text-sm mt-1 space-y-1">
                    <li>• Behandlungserfolg testen</li>
                    <li>• Nachbehandlung falls nötig</li>
                    <li>• Verlaufskontrolle planen</li>
                  </ul>
                </div>
              </div>
            </div>
            
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-red-300">Spezifische Anwendungsbereiche</h3>
              <div className="space-y-3">
                <div className="bg-red-900/20 p-3 rounded">
                  <h4 className="font-semibold text-red-200">Gesundheitsanalyse</h4>
                  <ul className="text-gray-300 text-sm mt-1 space-y-1">
                    <li>• Organsystem-Bewertung</li>
                    <li>• Mineralstoff-/Vitaminmängel</li>
                    <li>• Toxin-Belastungen</li>
                    <li>• Allergen-Screening</li>
                  </ul>
                </div>
                
                <div className="bg-red-900/20 p-3 rounded">
                  <h4 className="font-semibold text-red-200">Homöopathie-Integration</h4>
                  <ul className="text-gray-300 text-sm mt-1 space-y-1">
                    <li>• Mittel-Testung und -Auswahl</li>
                    <li>• Potenz-Optimierung</li>
                    <li>• Kombinationsmittel-Design</li>
                    <li>• Elektronische Potenzierung</li>
                  </ul>
                </div>
                
                <div className="bg-red-900/20 p-3 rounded">
                  <h4 className="font-semibold text-red-200">Landwirtschaft & Veterinär</h4>
                  <ul className="text-gray-300 text-sm mt-1 space-y-1">
                    <li>• Boden-/Pflanzenanalyse</li>
                    <li>• Tiergesundheit-Monitoring</li>
                    <li>• Schädlingsbekämpfung</li>
                    <li>• Ernteertrags-Optimierung</li>
                  </ul>
                </div>
                
                <div className="bg-red-900/20 p-3 rounded">
                  <h4 className="font-semibold text-red-200">Psycho-Emotionale Bereiche</h4>
                  <ul className="text-gray-300 text-sm mt-1 space-y-1">
                    <li>• Stress-/Trauma-Behandlung</li>
                    <li>• Emotionale Blockaden</li>
                    <li>• Lernstörungen</li>
                    <li>• Beziehungsprobleme</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
          
          <div className="mt-6 p-4 bg-teal-900/30 rounded-lg">
            <h4 className="text-lg font-semibold text-teal-200 mb-2">Copens Fernbehandlungs-Prinzip</h4>
            <p className="text-gray-300">
              "Die radionische Behandlung erfolgt über morphische Feldverbindungen, welche durch den 
              Zeugen hergestellt und über präzise Frequenzmuster moduliert werden. Die Distanz ist 
              dabei völlig irrelevant - entscheidend ist die exakte Resonanz-Einstellung." - B. Copen
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default CopenAnwendung;

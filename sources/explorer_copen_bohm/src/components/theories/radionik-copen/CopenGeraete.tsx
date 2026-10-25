
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const CopenGeraete = () => {
  return (
    <div className="space-y-6">
      <Card className="bg-white/10 border-white/20 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-white text-2xl">Bruce Copen Geräte & Technologie</CardTitle>
        </CardHeader>
        <CardContent className="text-white space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-blue-300">Original Copen-Geräte (1950-1998)</h3>
              <div className="space-y-3 text-gray-200">
                <div className="p-3 bg-blue-900/30 rounded">
                  <strong className="text-blue-200">Mark VI Scanner:</strong> Erstes digitales Radionik-Gerät
                </div>
                <div className="p-3 bg-blue-900/30 rounded">
                  <strong className="text-blue-200">2000 Series:</strong> Computer-gesteuerte Analyse
                </div>
                <div className="p-3 bg-blue-900/30 rounded">
                  <strong className="text-blue-200">Therapy Generator:</strong> Frequenz-Übertragungsgerät
                </div>
                <div className="p-3 bg-blue-900/30 rounded">
                  <strong className="text-blue-200">Potency Simulator:</strong> Homöopathische Potenzierung
                </div>
              </div>
            </div>
            
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-green-300">Technische Spezifikationen</h3>
              <ul className="space-y-2 text-gray-200">
                <li>• Frequenzbereich: 0,1 Hz - 10 MHz</li>
                <li>• Raten-Datenbank: 50.000+ Einträge</li>
                <li>• Alphabet-Systeme: 12 verschiedene</li>
                <li>• Ausgabeformen: Audio, Magnetisch, Optisch</li>
                <li>• Messgenauigkeit: ±0,001 Hz</li>
                <li>• Speicherkapazität: 1000 Raten-Sets</li>
              </ul>
            </div>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-purple-300">Copen Mark VI</h3>
              <div className="space-y-3">
                <div className="bg-purple-900/20 p-3 rounded">
                  <h4 className="font-semibold text-purple-200">Design-Merkmale</h4>
                  <p className="text-gray-300 text-sm">
                    10 Drehregler für numerische Rateneingabe, Rubplatte für Proben
                  </p>
                </div>
                <div className="bg-purple-900/20 p-3 rounded">
                  <h4 className="font-semibold text-purple-200">Funktionsweise</h4>
                  <p className="text-gray-300 text-sm">
                    Widerstandsbrücken-Schaltung mit Quarzkristall-Stabilisierung
                  </p>
                </div>
              </div>
            </div>
            
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-yellow-300">Copen 2000 Serie</h3>
              <div className="space-y-3">
                <div className="bg-yellow-900/20 p-3 rounded">
                  <h4 className="font-semibold text-yellow-200">Computer-Interface</h4>
                  <p className="text-gray-300 text-sm">
                    Erste Radionik-Geräte mit PC-Anbindung und Software-Steuerung
                  </p>
                </div>
                <div className="bg-yellow-900/20 p-3 rounded">
                  <h4 className="font-semibold text-yellow-200">Automatisierung</h4>
                  <p className="text-gray-300 text-sm">
                    Vollautomatische Ratenfindung durch elektronische Abtastung
                  </p>
                </div>
              </div>
            </div>
            
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-red-300">Moderne Nachbauten</h3>
              <div className="space-y-3">
                <div className="bg-red-900/20 p-3 rounded">
                  <h4 className="font-semibold text-red-200">SE-5 1000</h4>
                  <p className="text-gray-300 text-sm">
                    Weiterentwicklung des Copen-Designs mit zusätzlichen Funktionen
                  </p>
                </div>
                <div className="bg-red-900/20 p-3 rounded">
                  <h4 className="font-semibol text-red-200">Quantec Pro</h4>
                  <p className="text-gray-300 text-sm">
                    Quantum-Response-Technologie basierend auf Copen-Prinzipien
                  </p>
                </div>
              </div>
            </div>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-cyan-300">Hardware-Komponenten</h3>
              <div className="space-y-3">
                <div className="bg-cyan-900/20 p-3 rounded">
                  <h4 className="font-semibold text-cyan-200">Rubplatte (Stick Pad)</h4>
                  <p className="text-gray-300 text-sm">
                    Kondensator-Platte für taktile Resonanz-Erkennung durch Reibungswiderstand
                  </p>
                </div>
                
                <div className="bg-cyan-900/20 p-3 rounded">
                  <h4 className="font-semibold text-cyan-200">Raten-Drehregler</h4>
                  <p className="text-gray-300 text-sm">
                    10-Position-Potentiometer für präzise numerische Einstellung
                  </p>
                </div>
                
                <div className="bg-cyan-900/20 p-3 rounded">
                  <h4 className="font-semibold text-cyan-200">Proben-Well</h4>
                  <p className="text-gray-300 text-sm">
                    Aluminium-Vertiefung zur Aufnahme biologischer Materialien
                  </p>
                </div>
              </div>
            </div>
            
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-orange-300">Elektronische Schaltung</h3>
              <div className="space-y-3">
                <div className="bg-orange-900/20 p-3 rounded">
                  <h4 className="font-semibold text-orange-200">Brücken-Schaltung</h4>
                  <p className="text-gray-300 text-sm">
                    Wheatstone-Brücke mit variabler Widerstandsmatrix
                  </p>
                </div>
                
                <div className="bg-orange-900/20 p-3 rounded">
                  <h4 className="font-semibold text-orange-200">Oszillator-Stufe</h4>
                  <p className="text-gray-300 text-sm">
                    Quarzkristall-stabilisierter Hochfrequenz-Generator
                  </p>
                </div>
                
                <div className="bg-orange-900/20 p-3 rounded">
                  <h4 className="font-semibold text-orange-200">Ausgabe-Verstärker</h4>
                  <p className="text-gray-300 text-sm">
                    Niederimpedanz-Ausgang für Übertragungsspulen
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

export default CopenGeraete;

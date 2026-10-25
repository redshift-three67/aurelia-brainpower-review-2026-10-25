
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";

const AuthenticFrequencies = () => {
  return (
    <div className="space-y-6">
      <Card className="bg-white/10 border-white/20 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-3xl text-center text-white">
            Konsolidierte Authentische Frequenzen
          </CardTitle>
          <p className="text-center text-blue-200 text-lg">
            Umfassende Sammlung aller wissenschaftlich dokumentierten Heilfrequenzen
          </p>
        </CardHeader>
        <CardContent className="text-white space-y-6">
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-blue-500/20 p-4 rounded-lg">
              <h4 className="font-semibold mb-3 text-blue-200">DNA & Genetische Frequenzen</h4>
              <div className="space-y-2 text-sm font-mono">
                <div className="flex justify-between">
                  <span>528 Hz:</span>
                  <span className="text-blue-300">DNA-Reparatur (Garjajev/Horowitz)</span>
                </div>
                <div className="flex justify-between">
                  <span>741 Hz:</span>
                  <span className="text-blue-300">Genetische Reinigung (Solfeggio)</span>
                </div>
                <div className="flex justify-between">
                  <span>852 Hz:</span>
                  <span className="text-blue-300">DNA-Aktivierung (Wellengenetik)</span>
                </div>
                <div className="flex justify-between">
                  <span>963 Hz:</span>
                  <span className="text-blue-300">Genetische Erweckung (Garjajev)</span>
                </div>
                <div className="flex justify-between">
                  <span>150 MHz:</span>
                  <span className="text-blue-300">DNA-Hauptresonanz (Garjajev)</span>
                </div>
              </div>
            </div>

            <div className="bg-green-500/20 p-4 rounded-lg">
              <h4 className="font-semibold mb-3 text-green-200">Organ-System Frequenzen</h4>
              <div className="space-y-2 text-sm font-mono">
                <div className="flex justify-between">
                  <span>1,2-7,83 Hz:</span>
                  <span className="text-green-300">Herz-Kreislauf (Copen/Schmidt)</span>
                </div>
                <div className="flex justify-between">
                  <span>10 Hz:</span>
                  <span className="text-green-300">Immunsystem (Schmidt)</span>
                </div>
                <div className="flex justify-between">
                  <span>2,5-9,6 Hz:</span>
                  <span className="text-green-300">Verdauung (Radionik)</span>
                </div>
                <div className="flex justify-between">
                  <span>8-13 Hz:</span>
                  <span className="text-green-300">Nervensystem (Broers)</span>
                </div>
                <div className="flex justify-between">
                  <span>35-75 Hz:</span>
                  <span className="text-green-300">Bewegungsapparat (Copen)</span>
                </div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-purple-500/20 p-4 rounded-lg">
              <h4 className="font-semibold mb-3 text-purple-200">Pathogen-Elimination (Hz)</h4>
              <div className="space-y-2 text-sm font-mono">
                <div className="flex justify-between">
                  <span>390-690:</span>
                  <span className="text-purple-300">Bakterien (Rife/Copen)</span>
                </div>
                <div className="flex justify-between">
                  <span>1500-15000:</span>
                  <span className="text-purple-300">Viren (Rife-Frequenzen)</span>
                </div>
                <div className="flex justify-between">
                  <span>414-582:</span>
                  <span className="text-purple-300">Candida (Baklayan)</span>
                </div>
                <div className="flex justify-between">
                  <span>432-864:</span>
                  <span className="text-purple-300">Borrelien (Baklayan)</span>
                </div>
                <div className="flex justify-between">
                  <span>2100-2130:</span>
                  <span className="text-purple-300">Krebs-Zellen (Rife)</span>
                </div>
              </div>
            </div>

            <div className="bg-yellow-500/20 p-4 rounded-lg">
              <h4 className="font-semibold mb-3 text-yellow-200">Bewusstseins-Frequenzen</h4>
              <div className="space-y-2 text-sm font-mono">
                <div className="flex justify-between">
                  <span>7,83 Hz:</span>
                  <span className="text-yellow-300">Schumann-Resonanz (Broers)</span>
                </div>
                <div className="flex justify-between">
                  <span>40-100 Hz:</span>
                  <span className="text-yellow-300">Gamma-Kohärenz (Broers)</span>
                </div>
                <div className="flex justify-between">
                  <span>8-13 Hz:</span>
                  <span className="text-yellow-300">Alpha-Meditation (Broers)</span>
                </div>
                <div className="flex justify-between">
                  <span>4-7 Hz:</span>
                  <span className="text-yellow-300">Theta-Intuition (Broers)</span>
                </div>
                <div className="flex justify-between">
                  <span>432 Hz:</span>
                  <span className="text-yellow-300">Universelle Harmonie</span>
                </div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="bg-red-500/20 p-4 rounded-lg">
              <h4 className="font-semibold mb-3 text-red-200">Chakra-Frequenzen</h4>
              <div className="space-y-1 text-sm font-mono">
                <div>• 194,18 Hz - Wurzel (Mars)</div>
                <div>• 210,42 Hz - Sakral (Mond)</div>
                <div>• 126,22 Hz - Solar (Sonne)</div>
                <div>• 341,3 Hz - Herz (Venus)</div>
                <div>• 141,27 Hz - Kehl (Merkur)</div>
                <div>• 183,58 Hz - Stirn (Jupiter)</div>
                <div>• 172,06 Hz - Krone (Platon)</div>
              </div>
            </div>

            <div className="bg-teal-500/20 p-4 rounded-lg">
              <h4 className="font-semibold mb-3 text-teal-200">Schmidt-Frequenzen</h4>
              <div className="space-y-1 text-sm font-mono">
                <div>• 0,1-10 Hz - Grundregulation</div>
                <div>• 15,85 Hz - Zellstoffwechsel</div>
                <div>• 199,5 Hz - Organfunktion</div>
                <div>• 2.511 Hz - Immunmodulation</div>
                <div>• 31.622 Hz - Entgiftung</div>
                <div>• 398.107 Hz - Regeneration</div>
              </div>
            </div>

            <div className="bg-indigo-500/20 p-4 rounded-lg">
              <h4 className="font-semibold mb-3 text-indigo-200">Solfeggio-Kern</h4>
              <div className="space-y-1 text-sm font-mono">
                <div>• 174 Hz - Schmerz & Trauma</div>
                <div>• 285 Hz - Quantenfeld</div>
                <div>• 396 Hz - Angst befreien</div>
                <div>• 417 Hz - Veränderung</div>
                <div>• 528 Hz - Transformation</div>
                <div>• 639 Hz - Beziehungen</div>
                <div>• 741 Hz - Ausdruck</div>
                <div>• 852 Hz - Spiritualität</div>
                <div>• 963 Hz - Einheit</div>
              </div>
            </div>
          </div>

          <Separator className="bg-white/20" />

          <div className="bg-gradient-to-r from-cyan-500/20 to-blue-500/20 p-4 rounded-lg">
            <h4 className="font-semibold mb-3 text-cyan-200">Mathematische Grundprinzipien</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-black/20 p-3 rounded font-mono text-sm">
                <strong className="text-cyan-300">Harmonische Reihe:</strong><br/>
                f_n = f₀ × n<br/>
                (n = 1, 2, 3, 4, 5...)
              </div>
              <div className="bg-black/20 p-3 rounded font-mono text-sm">
                <strong className="text-cyan-300">Oktav-System:</strong><br/>
                f_oktav = f₀ × 2^n<br/>
                (Frequenz-Verdopplung)
              </div>
              <div className="bg-black/20 p-3 rounded font-mono text-sm">
                <strong className="text-cyan-300">Fibonacci-Frequenzen:</strong><br/>
                f_fib = f₀ × φ^n<br/>
                (φ = 1,618 - Goldener Schnitt)
              </div>
              <div className="bg-black/20 p-3 rounded font-mono text-sm">
                <strong className="text-cyan-300">Logarithmische Skala:</strong><br/>
                f_log = f₀ × 10^(n/10)<br/>
                (Dezimal-Harmonien)
              </div>
            </div>
          </div>

          <div className="bg-orange-500/20 p-4 rounded-lg">
            <h4 className="font-semibold mb-3 text-orange-200">Anwendungs-Richtlinien für Praktiker</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div className="space-y-2">
                <h5 className="font-semibold text-orange-300">Allgemeine Heilung:</h5>
                <ul className="list-disc pl-4 space-y-1">
                  <li>528 Hz - Universelle Heilfrequenz</li>
                  <li>7,83 Hz - Erdung & Grundregulation</li>
                  <li>40 Hz - Zellkommunikation</li>
                  <li>10 Hz - Immunsystem-Stärkung</li>
                </ul>
              </div>
              <div className="space-y-2">
                <h5 className="font-semibold text-orange-300">Akute Beschwerden:</h5>
                <ul className="list-disc pl-4 space-y-1">
                  <li>174 Hz - Schmerzen</li>
                  <li>285 Hz - Wundheilung</li>
                  <li>396 Hz - Angst & Stress</li>
                  <li>741 Hz - Entgiftung</li>
                </ul>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AuthenticFrequencies;

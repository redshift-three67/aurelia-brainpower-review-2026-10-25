
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Atom, Brain, Zap, GitBranch } from "lucide-react";

const WissenschaftlicheGrundlagen = () => {
  return (
    <div className="space-y-6">
      <Card className="bg-white/10 border-white/20 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-2xl text-white flex items-center gap-2">
            <Atom className="h-6 w-6" />
            Wissenschaftliche Grundlagen der Chakren-Meridian-Frequenztherapie
          </CardTitle>
        </CardHeader>
        <CardContent className="text-white space-y-6">
          
          <div className="bg-blue-500/20 p-4 rounded-lg">
            <h3 className="text-xl font-semibold mb-3">Quantenphysikalische Grundlagen</h3>
            <div className="space-y-3">
              <div className="bg-black/20 p-3 rounded border-l-4 border-blue-400">
                <h4 className="font-semibold">Biofeld-Theorie:</h4>
                <p className="text-sm mt-1">
                  Jeder lebende Organismus erzeugt ein kohärentes elektromagnetisches Feld (Biofeld), 
                  das durch spezifische Frequenzen moduliert werden kann. Die Chakren fungieren als 
                  Energiezentren mit charakteristischen Resonanzfrequenzen.
                </p>
              </div>
              
              <div className="bg-black/20 p-3 rounded border-l-4 border-green-400">
                <h4 className="font-semibold">Meridian-Leitfähigkeit:</h4>
                <p className="text-sm mt-1">
                  Akupunkturmeridiane zeigen messbar veränderte elektrische Leitfähigkeit 
                  (Ryodoraku-Messungen). Diese Leitungskanäle entsprechen Frequenz-spezifischen 
                  Übertragungswegen im Körper.
                </p>
              </div>
            </div>
          </div>

          <div className="bg-purple-500/20 p-4 rounded-lg">
            <h3 className="text-xl font-semibold mb-3 flex items-center gap-2">
              <Brain className="h-5 w-5" />
              Neurophysiologische Korrelationen
            </h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-white/20">
                    <th className="text-left p-2">Chakra</th>
                    <th className="text-left p-2">Nervenzentrum</th>
                    <th className="text-left p-2">Gehirnwellen-Korrelation</th>
                    <th className="text-left p-2">Hormon-System</th>
                  </tr>
                </thead>
                <tbody>
                  <tr className="border-b border-white/10">
                    <td className="p-2">Kronenchakra</td>
                    <td className="p-2">Epiphyse (Zirbeldrüse)</td>
                    <td className="p-2">Gamma (40-100 Hz)</td>
                    <td className="p-2">Melatonin, DMT</td>
                  </tr>
                  <tr className="border-b border-white/10">
                    <td className="p-2">Stirnchakra</td>
                    <td className="p-2">Hypophyse</td>
                    <td className="p-2">Beta (13-30 Hz)</td>
                    <td className="p-2">Wachstumshormon, ACTH</td>
                  </tr>
                  <tr className="border-b border-white/10">
                    <td className="p-2">Halschakra</td>
                    <td className="p-2">Schilddrüse</td>
                    <td className="p-2">Alpha (8-13 Hz)</td>
                    <td className="p-2">T3, T4, Calcitonin</td>
                  </tr>
                  <tr className="border-b border-white/10">
                    <td className="p-2">Herzchakra</td>
                    <td className="p-2">Herz-Nervensystem</td>
                    <td className="p-2">Theta (4-8 Hz)</td>
                    <td className="p-2">ANF, Oxytocin</td>
                  </tr>
                  <tr className="border-b border-white/10">
                    <td className="p-2">Solarplexus</td>
                    <td className="p-2">Nebennieren</td>
                    <td className="p-2">Delta (1-4 Hz)</td>
                    <td className="p-2">Adrenalin, Cortisol</td>
                  </tr>
                  <tr className="border-b border-white/10">
                    <td className="p-2">Sakralchakra</td>
                    <td className="p-2">Gonaden</td>
                    <td className="p-2">Infra-Delta (&lt;1 Hz)</td>
                    <td className="p-2">Testosteron, Östrogen</td>
                  </tr>
                  <tr className="border-b border-white/10">
                    <td className="p-2">Wurzelchakra</td>
                    <td className="p-2">Steißbein-Ganglion</td>
                    <td className="p-2">Schumann (7.83 Hz)</td>
                    <td className="p-2">Überlebensmodus-Hormone</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div className="bg-green-500/20 p-4 rounded-lg">
            <h3 className="text-xl font-semibold mb-3">Elektromagnetische Messverfahren</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-black/20 p-3 rounded">
                <h4 className="font-semibold mb-2 text-green-300">Ryodoraku-Messung:</h4>
                <ul className="space-y-1 text-sm">
                  <li><strong>Prinzip:</strong> Hautwiderstand an Akupunkturpunkten</li>
                  <li><strong>Normalwerte:</strong> 50-200 µA bei 12V</li>
                  <li><strong>Abweichungen:</strong> Krankheit = &lt;40 oder &gt;250 µA</li>
                  <li><strong>Meridian-spezifisch:</strong> Jeder Meridian messbar</li>
                </ul>
              </div>
              
              <div className="bg-black/20 p-3 rounded">
                <h4 className="font-semibold mb-2 text-blue-300">GDV-Kirlian-Fotografie:</h4>
                <ul className="space-y-1 text-sm">
                  <li><strong>Hochfrequenz:</strong> 1024 Hz Wechselstrom</li>
                  <li><strong>Aura-Messung:</strong> Korona-Entladung der Finger</li>
                  <li><strong>Chakra-Korrelation:</strong> Organ-spezifische Bereiche</li>
                  <li><strong>Vor/Nach-Vergleich:</strong> Therapie-Kontrolle</li>
                </ul>
              </div>
            </div>
          </div>

          <div className="bg-yellow-500/20 p-4 rounded-lg">
            <h3 className="text-xl font-semibold mb-3 flex items-center gap-2">
              <Zap className="h-5 w-5" />
              Frequenz-Resonanz-Modell
            </h3>
            <div className="space-y-4">
              <div className="bg-black/20 p-3 rounded">
                <h4 className="font-semibold mb-2">Grundgleichung der Chakra-Resonanz:</h4>
                <div className="bg-gray-900/50 p-2 rounded font-mono text-sm">
                  f_chakra = f_basis × 2^(n/12) × k_korrektur<br/>
                  <span className="text-gray-400">
                    f_basis = 256 Hz (C4)<br/>
                    n = Halbtonschritte<br/>
                    k_korrektur = 0.9-1.1 (individuell)
                  </span>
                </div>
              </div>
              
              <div className="bg-black/20 p-3 rounded">
                <h4 className="font-semibold mb-2">Meridian-Frequenz-Berechnung:</h4>
                <div className="bg-gray-900/50 p-2 rounded font-mono text-sm">
                  f_meridian = (Organ-Hz × Tageszeit-Faktor) / Energiezustand<br/>
                  <span className="text-gray-400">
                    Beispiel Lunge: 174.6 Hz × 1.2 (3-5 Uhr) / 0.8 (Schwäche) = 261.9 Hz
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-red-500/20 p-4 rounded-lg">
            <h3 className="text-xl font-semibold mb-3">Quantenfeld-Interaktionen</h3>
            <div className="space-y-3">
              <div className="bg-black/20 p-3 rounded">
                <h4 className="font-semibold">Morphische Resonanz (Sheldrake-Modell):</h4>
                <p className="text-sm mt-1">
                  Chakren und Meridiane sind morphische Felder, die durch spezifische Frequenzen 
                  aktiviert werden. Diese Felder speichern Informationen und können durch 
                  Resonanz-Frequenzen abgerufen und moduliert werden.
                </p>
              </div>
              
              <div className="bg-black/20 p-3 rounded">
                <h4 className="font-semibold">Skalare Wellen-Übertragung:</h4>
                <p className="text-sm mt-1">
                  Meridiane leiten nicht nur elektrische, sondern auch skalare Wellen. 
                  Diese longitudinalen Wellen übertragen Information instantan und können 
                  durch Frequenz-Modulation therapeutisch genutzt werden.
                </p>
              </div>
            </div>
          </div>

          <div className="bg-indigo-500/20 p-4 rounded-lg">
            <h3 className="text-xl font-semibold mb-3 flex items-center gap-2">
              <GitBranch className="h-5 w-5" />
              Systemische Vernetzung
            </h3>
            <div className="bg-black/20 p-3 rounded">
              <h4 className="font-semibold mb-3">Holografisches Körper-Modell:</h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <div className="bg-indigo-800/30 p-2 rounded">
                  <h5 className="font-semibold text-indigo-300">Mikrosystem Ohr:</h5>
                  <p className="text-xs">Jeder Körperteil im Ohr repräsentiert</p>
                  <p className="text-xs">Frequenz-Punktstimulation möglich</p>
                </div>
                <div className="bg-indigo-800/30 p-2 rounded">
                  <h5 className="font-semibold text-purple-300">Mikrosystem Hand:</h5>
                  <p className="text-xs">Reflexzonen der Organe</p>
                  <p className="text-xs">Meridian-Endpunkte konzentriert</p>
                </div>
                <div className="bg-indigo-800/30 p-2 rounded">
                  <h5 className="font-semibold text-pink-300">Mikrosystem Fuß:</h5>
                  <p className="text-xs">Chakra-Projektionszonen</p>
                  <p className="text-xs">Erdung und Energieaufnahme</p>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default WissenschaftlicheGrundlagen;

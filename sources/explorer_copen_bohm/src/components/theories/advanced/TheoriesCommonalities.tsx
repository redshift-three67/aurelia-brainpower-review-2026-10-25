
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import AuthenticFrequencies from "./AuthenticFrequencies";
import AuthenticSources from "./AuthenticSources";

const TheoriesCommonalities = () => {
  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <Card className="bg-white/10 border-white/20 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-4xl text-center text-white">
            Gemeinsamkeiten & Konsolidierung aller Theorien
          </CardTitle>
          <p className="text-center text-blue-200 text-lg">
            Universelle Prinzipien, Authentische Frequenzen und konsolidierte Erkenntnisse
          </p>
        </CardHeader>
      </Card>

      <Tabs defaultValue="frequencies" className="space-y-4">
        <TabsList className="grid w-full grid-cols-4 bg-white/10 border-white/20">
          <TabsTrigger value="frequencies" className="text-white data-[state=active]:bg-white/20">
            Authentische Frequenzen
          </TabsTrigger>
          <TabsTrigger value="sources" className="text-white data-[state=active]:bg-white/20">
            Authentische Quellen
          </TabsTrigger>
          <TabsTrigger value="principles" className="text-white data-[state=active]:bg-white/20">
            Universelle Prinzipien
          </TabsTrigger>
          <TabsTrigger value="matrix" className="text-white data-[state=active]:bg-white/20">
            Frequenz-Matrix
          </TabsTrigger>
        </TabsList>

        <TabsContent value="frequencies">
          <AuthenticFrequencies />
        </TabsContent>

        <TabsContent value="sources">
          <AuthenticSources />
        </TabsContent>

        <TabsContent value="principles">
          <Card className="bg-white/10 border-white/20 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-2xl text-white">Universelle Prinzipien aller Frequenztherapien</CardTitle>
            </CardHeader>
            <CardContent className="text-white space-y-4">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-blue-500/20 p-4 rounded-lg">
                  <h4 className="font-semibold mb-2 text-blue-200">Fundamentale Gesetzmäßigkeiten:</h4>
                  <ul className="list-disc pl-6 space-y-1 text-sm">
                    <li><strong>Resonanzprinzip:</strong> Gleiche Frequenzen verstärken sich</li>
                    <li><strong>Harmonische Gesetze:</strong> Oktaven, Quinten, Fibonacci-Reihen</li>
                    <li><strong>Kohärenz-Effekte:</strong> Synchronisation biologischer Rhythmen</li>
                    <li><strong>Quantenverschränkung:</strong> Nichtlokale Informationsübertragung</li>
                    <li><strong>Morphische Resonanz:</strong> Gedächtnis der Natur</li>
                  </ul>
                </div>
                
                <div className="bg-green-500/20 p-4 rounded-lg">
                  <h4 className="font-semibold mb-2 text-green-200">Biologische Universalien:</h4>
                  <ul className="list-disc pl-6 space-y-1 text-sm">
                    <li><strong>Zelluläre Kommunikation:</strong> 40-100 Hz Gamma-Bereich</li>
                    <li><strong>DNA-Resonanz:</strong> 528 Hz als universelle Reparaturfrequenz</li>
                    <li><strong>Herzrhythmus-Kohärenz:</strong> 0,1 Hz als Grundtakt</li>
                    <li><strong>Gehirnwellen-Entrainment:</strong> 7,83 Hz Schumann-Resonanz</li>
                    <li><strong>Circadiane Rhythmen:</strong> 24-Stunden-Zyklen</li>
                  </ul>
                </div>
              </div>
              
              <div className="bg-purple-500/20 p-4 rounded-lg">
                <h4 className="font-semibold mb-2 text-purple-200">Mathematische Konstanten in allen Systemen:</h4>
                <div className="bg-black/20 p-3 rounded border-l-4 border-purple-400 my-3 font-mono text-sm">
                  <strong>Goldener Schnitt (φ = 1,618):</strong> DNA-Spirale, Fibonacci-Frequenzen<br/>
                  <strong>Euler'sche Zahl (e = 2,718):</strong> Exponentielles Wachstum, Zerfallskurven<br/>
                  <strong>Pi (π = 3,14159):</strong> Kreisfrequenzen, Schwingungsformen<br/>
                  <strong>Schumann-Konstante (7,83 Hz):</strong> Erd-Ionosphären-Resonanz<br/>
                  <strong>Planck-Konstante (h):</strong> Quantenenergie-Frequenz-Relation
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="matrix">
          <Card className="bg-white/10 border-white/20 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-2xl text-white">Konsolidierte Frequenz-Matrix</CardTitle>
            </CardHeader>
            <CardContent className="text-white space-y-4">
              <div className="bg-gradient-to-r from-cyan-500/20 to-blue-500/20 p-4 rounded-lg">
                <h4 className="font-semibold mb-2 text-cyan-200">Master-Frequenz-Gleichung (Alle Systeme vereint):</h4>
                <div className="bg-black/20 p-3 rounded border-l-4 border-cyan-400 my-3 font-mono text-sm">
                  <strong>Universal-Formel:</strong><br/>
                  f_total = Σᵢ [αᵢ × f_base × φⁱ × 2^(nᵢ) × Fib(mᵢ)] × C(consciousness) × Q(quantum)<br/><br/>
                  <strong>Wo:</strong><br/>
                  • αᵢ = Gewichtungsfaktoren der einzelnen Systeme<br/>
                  • f_base = Grundfrequenz (0,1 Hz, 7,83 Hz, 432 Hz, 528 Hz)<br/>
                  • φ = Goldener Schnitt (1,618)<br/>
                  • nᵢ, mᵢ = Harmonische und Fibonacci-Indizes<br/>
                  • C(consciousness) = Bewusstseins-Operator<br/>
                  • Q(quantum) = Quantenfeld-Modulation
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default TheoriesCommonalities;

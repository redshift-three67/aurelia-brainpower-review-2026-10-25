
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const CopenAlgorithmus = () => {
  return (
    <div className="space-y-6">
      <Card className="bg-white/10 border-white/20 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-white text-2xl">Der Authentische Copen-Algorithmus</CardTitle>
        </CardHeader>
        <CardContent className="text-white space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-yellow-300">Berechnungsformel</h3>
              <div className="bg-gray-800/50 p-4 rounded-lg font-mono">
                <div className="text-yellow-200 mb-2">Copen-Rate = (Buchstabensumme × Potenz × Potenz-Faktor) × Fibonacci(Buchstabensumme)</div>
                <div className="text-gray-300 text-sm space-y-1">
                  <div>Potenz-Faktoren:</div>
                  <div>D-Potenzen: × 1</div>
                  <div>C-Potenzen: × 100</div>
                  <div>LM-Potenzen: × 50.000</div>
                  <div>M-Potenzen: × 1.000</div>
                </div>
              </div>
            </div>
            
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-red-300">Fibonacci-Integration</h3>
              <div className="space-y-2 text-gray-200">
                <div className="p-3 bg-red-900/20 rounded">
                  <strong>Grundsequenz:</strong> 1, 1, 2, 3, 5, 8, 13, 21, 34, 55...
                </div>
                <div className="p-3 bg-red-900/20 rounded">
                  <strong>Resonanz-Verstärkung:</strong> Natürliche Harmonik
                </div>
                <div className="p-3 bg-red-900/20 rounded">
                  <strong>Biologische Korrelation:</strong> DNA-Spirale
                </div>
              </div>
            </div>
          </div>
          
          <div className="space-y-4">
            <h3 className="text-xl font-semibold text-blue-300">Praktische Beispiele</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-blue-900/20 p-4 rounded-lg">
                <h4 className="font-semibold text-blue-200 mb-2">LIEBE (D6)</h4>
                <div className="text-sm space-y-1 text-gray-300">
                  <div>L(12) + I(9) + E(5) + B(2) + E(5) = 33</div>
                  <div>33 × 6 × 1 = 198</div>
                  <div>Fibonacci(33) = 3.524.578</div>
                  <div className="text-blue-200 font-bold">Rate: 697.866.444</div>
                </div>
              </div>
              
              <div className="bg-green-900/20 p-4 rounded-lg">
                <h4 className="font-semibold text-green-200 mb-2">HEILUNG (C30)</h4>
                <div className="text-sm space-y-1 text-gray-300">
                  <div>H(8) + E(5) + I(9) + L(12) + U(21) + N(14) + G(7) = 76</div>
                  <div>76 × 30 × 100 = 228.000</div>
                  <div>Fibonacci(76) = 2.111×10¹⁵</div>
                  <div className="text-green-200 font-bold">Rate: 4.813×10²⁰</div>
                </div>
              </div>
              
              <div className="bg-purple-900/20 p-4 rounded-lg">
                <h4 className="font-semibold text-purple-200 mb-2">FREQUENZ (LM6)</h4>
                <div className="text-sm space-y-1 text-gray-300">
                  <div>F(6) + R(18) + E(5) + Q(17) + U(21) + E(5) + N(14) + Z(26) = 112</div>
                  <div>112 × 6 × 50.000 = 33.600.000</div>
                  <div>Fibonacci(112) = 1.249×10²³</div>
                  <div className="text-purple-200 font-bold">Rate: 4.197×10²⁹</div>
                </div>
              </div>
            </div>
          </div>
          
          <div className="mt-6 p-4 bg-indigo-900/30 rounded-lg">
            <h4 className="text-lg font-semibold text-indigo-200 mb-2">Validierung & Kalibrierung</h4>
            <p className="text-gray-300">
              Copen entwickelte spezielle Testverfahren zur Validierung berechneter Raten mittels 
              kinesiologischer Tests, Stick-Pad-Reaktionen und instrumenteller Resonanzmessung.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default CopenAlgorithmus;

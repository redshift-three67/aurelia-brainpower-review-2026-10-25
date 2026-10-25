
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const RatenSysteme = () => {
  return (
    <div className="space-y-6">
      <Card className="bg-white/10 border-white/20 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-white text-2xl">Radionische Raten-Systeme</CardTitle>
        </CardHeader>
        <CardContent className="text-white space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-3">
              <h3 className="text-xl font-semibold text-blue-300">Klassische Raten-Systeme</h3>
              <div className="space-y-2 text-gray-200">
                <div className="p-3 bg-gray-800/50 rounded">
                  <strong>Abrams Raten:</strong> 9-stellige Zahlencodes (z.B. 432187456)
                </div>
                <div className="p-3 bg-gray-800/50 rounded">
                  <strong>Hieronymus Raten:</strong> 3-6 stellige Codes (z.B. 8-49-86)
                </div>
                <div className="p-3 bg-gray-800/50 rounded">
                  <strong>De La Warr Raten:</strong> Dezimale Systeme (z.B. 7.5-22.5)
                </div>
              </div>
            </div>
            <div className="space-y-3">
              <h3 className="text-xl font-semibold text-blue-300">Moderne Raten-Systeme</h3>
              <div className="space-y-2 text-gray-200">
                <div className="p-3 bg-gray-800/50 rounded">
                  <strong>Homöopathische Raten:</strong> Potenz-basierte Codes
                </div>
                <div className="p-3 bg-gray-800/50 rounded">
                  <strong>Frequenz-Raten:</strong> Hz-basierte Systeme
                </div>
                <div className="p-3 bg-gray-800/50 rounded">
                  <strong>Quantenfeld-Raten:</strong> Mehrdimensionale Codes
                </div>
              </div>
            </div>
          </div>
          
          <div className="mt-6 p-4 bg-purple-900/30 rounded-lg">
            <h4 className="text-lg font-semibold text-purple-200 mb-2">Raten-Bestimmung</h4>
            <p className="text-gray-300">
              Radionische Raten werden durch kinesiologische Tests, Pendel-Reaktionen 
              oder instrumentelle Messung der morphischen Feldresonanz bestimmt.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default RatenSysteme;


import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const GeraeteUndTechnologie = () => {
  return (
    <div className="space-y-6">
      <Card className="bg-white/10 border-white/20 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-white text-2xl">Radionische Geräte & Technologie</CardTitle>
        </CardHeader>
        <CardContent className="text-white space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-3">
              <h3 className="text-xl font-semibold text-blue-300">Klassische Radionische Geräte</h3>
              <ul className="space-y-2 text-gray-200">
                <li>• Abrams Box (Original Radionik-Gerät)</li>
                <li>• Hieronymus Maschine</li>
                <li>• De La Warr Kamera</li>
                <li>• SE-5 Intrinsic Data Field Analyzer</li>
                <li>• Quantec Pro System</li>
              </ul>
            </div>
            <div className="space-y-3">
              <h3 className="text-xl font-semibold text-blue-300">Moderne Technologien</h3>
              <ul className="space-y-2 text-gray-200">
                <li>• Computer-basierte Systeme</li>
                <li>• Biofeedback-Integration</li>
                <li>• Digitale Raten-Bibliotheken</li>
                <li>• Remote-Analyse Software</li>
                <li>• Quantenfeld-Modulatoren</li>
              </ul>
            </div>
          </div>
          
          <div className="mt-6 p-4 bg-blue-900/30 rounded-lg">
            <h4 className="text-lg font-semibold text-blue-200 mb-2">Geräte-Kalibrierung</h4>
            <p className="text-gray-300">
              Moderne radionische Geräte erfordern präzise Kalibrierung zur Messung 
              und Übertragung spezifischer Frequenzmuster und Informationsfelder.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default GeraeteUndTechnologie;

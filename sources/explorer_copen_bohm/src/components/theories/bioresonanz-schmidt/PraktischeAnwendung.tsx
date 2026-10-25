import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { AlertTriangle, Clock, Target, Zap } from "lucide-react";

const PraktischeAnwendung = () => {
  return (
    <div className="space-y-6">
      <Card className="bg-white/10 border-white/20 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-2xl text-white flex items-center gap-2">
            <Target className="h-6 w-6" />
            Praktische Behandlungsprotokolle
          </CardTitle>
        </CardHeader>
        <CardContent className="text-white space-y-6">
          
          <div className="bg-green-500/20 p-4 rounded-lg">
            <h3 className="text-xl font-semibold mb-3 flex items-center gap-2">
              <Clock className="h-5 w-5" />
              Standard-Behandlungszeiten
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-black/20 p-3 rounded">
                <h4 className="font-semibold mb-2">Nach Frequenzbereichen:</h4>
                <ul className="space-y-1 text-sm">
                  <li><strong>0,1-10 Hz:</strong> 60-120 Min (Grundregulation)</li>
                  <li><strong>10-100 Hz:</strong> 30-60 Min (Organe)</li>
                  <li><strong>100-500 Hz:</strong> 15-30 Min (Pathogene)</li>
                  <li><strong>500+ Hz:</strong> 10-20 Min (Psyche/Hormone)</li>
                </ul>
              </div>
              <div className="bg-black/20 p-3 rounded">
                <h4 className="font-semibold mb-2">Nach Anwendungsart:</h4>
                <ul className="space-y-1 text-sm">
                  <li><strong>Diagnose:</strong> 5-10 Min pro Frequenz</li>
                  <li><strong>Therapie:</strong> 15-60 Min pro Frequenz</li>
                  <li><strong>Nachbehandlung:</strong> 5-15 Min</li>
                  <li><strong>Prävention:</strong> 30-45 Min gesamt</li>
                </ul>
              </div>
            </div>
          </div>

          <div className="bg-blue-500/20 p-4 rounded-lg">
            <h3 className="text-xl font-semibold mb-3">Schritt-für-Schritt Anleitung</h3>
            <div className="space-y-3">
              <div className="bg-black/20 p-3 rounded border-l-4 border-blue-400">
                <h4 className="font-semibold">Phase 1: Grundregulation (5-10 Min)</h4>
                <p className="text-sm mt-1">
                  Beginnen Sie immer mit 0,1 Hz für 2 Min, dann 1,2 Hz für 3 Min (Immunsystem), 
                  abschließend 7,8 Hz für 5 Min (Gehirn-Grundfrequenz).
                </p>
              </div>
              
              <div className="bg-black/20 p-3 rounded border-l-4 border-green-400">
                <h4 className="font-semibold">Phase 2: Diagnostik (10-20 Min)</h4>
                <p className="text-sm mt-1">
                  Frequenz-Scan von 0,1 Hz bis 1000 Hz in Dekaden-Schritten. 
                  Resonanzen markieren und verfeinern. Pathogene identifizieren.
                </p>
              </div>
              
              <div className="bg-black/20 p-3 rounded border-l-4 border-yellow-400">
                <h4 className="font-semibold">Phase 3: Spezifische Therapie (20-40 Min)</h4>
                <p className="text-sm mt-1">
                  Behandlung der identifizierten Problembereiche mit entsprechenden Frequenzen. 
                  Bei Pathogenen: Elimination mit inversen Frequenzen.
                </p>
              </div>
              
              <div className="bg-black/20 p-3 rounded border-l-4 border-purple-400">
                <h4 className="font-semibold">Phase 4: Harmonisierung (5-10 Min)</h4>
                <p className="text-sm mt-1">
                  Abschluss mit 7,83 Hz (Schumann-Resonanz) für 5-10 Min zur Systemharmonisierung 
                  und Energiebalance.
                </p>
              </div>
            </div>
          </div>

          <div className="bg-purple-500/20 p-4 rounded-lg">
            <h3 className="text-xl font-semibold mb-3">Bewährte Frequenz-Kombinationen</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <div className="bg-black/20 p-3 rounded">
                  <h4 className="font-semibold text-green-300">Immunstärkung:</h4>
                  <p className="text-sm">1,2 Hz + 19,0 Hz + 440,0 Hz</p>
                  <p className="text-xs text-gray-300">Je 15 Min, täglich 1 Woche</p>
                </div>
                
                <div className="bg-black/20 p-3 rounded">
                  <h4 className="font-semibold text-yellow-300">Entgiftung:</h4>
                  <p className="text-sm">0,6 Hz + 26,5 Hz + 47,5 Hz + 71,5 Hz</p>
                  <p className="text-xs text-gray-300">Je 20 Min, 3x wöchentlich</p>
                </div>
              </div>
              
              <div className="space-y-2">
                <div className="bg-black/20 p-3 rounded">
                  <h4 className="font-semibold text-blue-300">Stress-Abbau:</h4>
                  <p className="text-sm">2,4 Hz + 7,8 Hz + 560,0 Hz</p>
                  <p className="text-xs text-gray-300">Je 10 Min, bei Bedarf</p>
                </div>
                
                <div className="bg-black/20 p-3 rounded">
                  <h4 className="font-semibold text-red-300">Schmerztherapie:</h4>
                  <p className="text-sm">40,0 Hz + 72,0 Hz + 10,0 Hz</p>
                  <p className="text-xs text-gray-300">Je 25 Min, 2x täglich</p>
                </div>
              </div>
            </div>
          </div>

          <Alert className="bg-orange-500/20 border-orange-500/50">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription className="text-white">
              <strong>Wichtige Hinweise:</strong> Beginnen Sie immer mit niedrigen Intensitäten. 
              Bei Erstverschlimmerungen Pause einlegen. Ausreichend Wasser trinken zur Entgiftungsunterstützung.
              Bei ernsten Erkrankungen immer zusätzlich ärztlichen Rat einholen.
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>

      <Card className="bg-white/10 border-white/20 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-2xl text-white flex items-center gap-2">
            <Zap className="h-6 w-6" />
            Kontraindikationen und Nebenwirkungen
          </CardTitle>
        </CardHeader>
        <CardContent className="text-white space-y-4">
          <div className="bg-red-500/20 p-4 rounded-lg">
            <h3 className="text-lg font-semibold mb-2">Absolute Kontraindikationen:</h3>
            <ul className="list-disc pl-6 space-y-1">
              <li>Herzschrittmacher und implantierte elektronische Geräte</li>
              <li>Schwangerschaft (besonders erste 12 Wochen)</li>
              <li>Epilepsie und andere Anfallsleiden</li>
              <li>Akute psychotische Zustände</li>
              <li>Offene Tuberkulose</li>
            </ul>
          </div>

          <div className="bg-yellow-500/20 p-4 rounded-lg">
            <h3 className="text-lg font-semibold mb-2">Relative Kontraindikationen:</h3>
            <ul className="list-disc pl-6 space-y-1">
              <li>Hohes Fieber (&gt;38,5°C)</li>
              <li>Akute Infektionen</li>
              <li>Starke Medikation (besonders Psychopharmaka)</li>
              <li>Metallimplantate im Behandlungsbereich</li>
            </ul>
          </div>

          <div className="bg-orange-500/20 p-4 rounded-lg">
            <h3 className="text-lg font-semibold mb-2">Mögliche Nebenwirkungen:</h3>
            <ul className="list-disc pl-6 space-y-1">
              <li><strong>Erstverschlimmerung:</strong> Verstärkung der Symptome in den ersten 24-48h</li>
              <li><strong>Entgiftungsreaktionen:</strong> Müdigkeit, Kopfschmerzen, Hautausschläge</li>
              <li><strong>Emotionale Reaktionen:</strong> Stimmungsschwankungen, lebhafte Träume</li>
              <li><strong>Kreislaufreaktionen:</strong> Schwindel, Benommenheit (selten)</li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default PraktischeAnwendung;

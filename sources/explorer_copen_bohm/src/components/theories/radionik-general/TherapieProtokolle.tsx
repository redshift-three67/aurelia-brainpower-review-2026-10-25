
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const TherapieProtokolle = () => {
  return (
    <div className="space-y-6">
      <Card className="bg-white/10 border-white/20 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-white text-2xl">Radionische Therapie-Protokolle</CardTitle>
        </CardHeader>
        <CardContent className="text-white space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-red-300">Akut-Behandlung</h3>
              <div className="space-y-3">
                <div className="p-3 bg-red-900/20 rounded">
                  <h4 className="font-semibold text-red-200">Schmerz-Protokoll</h4>
                  <p className="text-gray-300 text-sm">
                    Rate: 26-12-84<br/>
                    Dauer: 15-30 Min<br/>
                    Wiederholung: 3x täglich
                  </p>
                </div>
                <div className="p-3 bg-red-900/20 rounded">
                  <h4 className="font-semibold text-red-200">Entzündungs-Protokoll</h4>
                  <p className="text-gray-300 text-sm">
                    Rate: 9-87-43<br/>
                    Dauer: 20 Min<br/>
                    Wiederholung: 4x täglich
                  </p>
                </div>
              </div>
            </div>
            
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-orange-300">Präventiv-Behandlung</h3>
              <div className="space-y-3">
                <div className="p-3 bg-orange-900/20 rounded">
                  <h4 className="font-semibold text-orange-200">Immunsystem-Stärkung</h4>
                  <p className="text-gray-300 text-sm">
                    Rate: 45-78-23<br/>
                    Dauer: 30 Min<br/>
                    Frequenz: Täglich
                  </p>
                </div>
                <div className="p-3 bg-orange-900/20 rounded">
                  <h4 className="font-semibold text-orange-200">Stress-Reduktion</h4>
                  <p className="text-gray-300 text-sm">
                    Rate: 12-56-89<br/>
                    Dauer: 25 Min<br/>
                    Frequenz: 2x täglich
                  </p>
                </div>
              </div>
            </div>
            
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-purple-300">Langzeit-Therapie</h3>
              <div className="space-y-3">
                <div className="p-3 bg-purple-900/20 rounded">
                  <h4 className="font-semibold text-purple-200">Chronische Leiden</h4>
                  <p className="text-gray-300 text-sm">
                    Rate: Variable<br/>
                    Dauer: 45-60 Min<br/>
                    Zyklus: 3 Wochen On/1 Woche Off
                  </p>
                </div>
                <div className="p-3 bg-purple-900/20 rounded">
                  <h4 className="font-semibold text-purple-200">Regenerations-Protokoll</h4>
                  <p className="text-gray-300 text-sm">
                    Rate: 33-77-11<br/>
                    Dauer: 40 Min<br/>
                    Frequenz: Jeden 2. Tag
                  </p>
                </div>
              </div>
            </div>
          </div>
          
          <div className="mt-6 space-y-4">
            <div className="p-4 bg-teal-900/30 rounded-lg">
              <h4 className="text-lg font-semibold text-teal-200 mb-2">Broadcast-Behandlung</h4>
              <p className="text-gray-300">
                Kontinuierliche Übertragung heilender Informationen über radionische 
                Sender-Geräte ermöglicht 24/7 Therapie ohne aktive Patient-Anwesenheit.
              </p>
            </div>
            
            <div className="p-4 bg-cyan-900/30 rounded-lg">
              <h4 className="text-lg font-semibold text-cyan-200 mb-2">Potenzierung & Verstärkung</h4>
              <p className="text-gray-300">
                Durch homöopathische Potenzierung und geometrische Verstärker-Strukturen 
                wird die Wirksamkeit radionischer Behandlungen exponentiell erhöht.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default TherapieProtokolle;

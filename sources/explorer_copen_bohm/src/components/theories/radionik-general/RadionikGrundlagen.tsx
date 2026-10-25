
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Radio, Waves, Brain, Zap } from "lucide-react";

const RadionikGrundlagen = () => {
  return (
    <div className="space-y-6">
      <Card className="bg-white/10 border-white/20 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-2xl text-white flex items-center gap-2">
            <Radio className="h-6 w-6" />
            Fundamentale Radionik-Prinzipien nach Abrams und Drown
          </CardTitle>
        </CardHeader>
        <CardContent className="text-white space-y-6">
          
          <div className="bg-blue-500/20 p-4 rounded-lg">
            <h3 className="text-xl font-semibold mb-3">Historische Entwicklung der Radionik</h3>
            <div className="space-y-3">
              <div className="bg-black/20 p-3 rounded border-l-4 border-blue-400">
                <h4 className="font-semibold">Dr. Albert Abrams (1863-1924) - Begründer:</h4>
                <p className="text-sm mt-1">
                  Entdeckte die "Elektronische Reaktion von Abrams" (ERA). Jede Krankheit sendet 
                  spezifische elektromagnetische Signale aus, die mittels Reflexen am Abdomen 
                  diagnostiziert werden können.
                </p>
              </div>
              
              <div className="bg-black/20 p-3 rounded border-l-4 border-green-400">
                <h4 className="font-semibold">Ruth Drown (1891-1965) - Fotografische Radionik:</h4>
                <p className="text-sm mt-1">
                  Entwickelte die radiographische Ferndiagnose. Über Blutproben können 
                  "Radionik-Fotografien" innerer Organe erstellt und Fernbehandlungen 
                  durchgeführt werden.
                </p>
              </div>
              
              <div className="bg-black/20 p-3 rounded border-l-4 border-purple-400">
                <h4 className="font-semibold">Malcolm Rae (1913-1979) - Geometrische Radionik:</h4>
                <p className="text-sm mt-1">
                  Entwickelte geometrische Patterns und Magnetkarten zur Übertragung 
                  radionischer Raten. Quantenphysikalische Erklärungsmodelle.
                </p>
              </div>
            </div>
          </div>

          <div className="bg-purple-500/20 p-4 rounded-lg">
            <h3 className="text-xl font-semibold mb-3 flex items-center gap-2">
              <Waves className="h-5 w-5" />
              Quantenphysikalische Grundlagen
            </h3>
            <div className="space-y-4">
              <div className="bg-black/20 p-3 rounded">
                <h4 className="font-semibold mb-2">Morphische Resonanz-Theorie (Rupert Sheldrake):</h4>
                <div className="text-sm space-y-1">
                  <p><strong>Morphische Felder:</strong> Informationsfelder, die Struktur und Verhalten organisieren</p>
                  <p><strong>Resonanz-Prinzip:</strong> Ähnliche Strukturen stehen in Resonanz zueinander</p>
                  <p><strong>Zeitlose Verbindung:</strong> Information überträgt sich instantan über beliebige Entfernungen</p>
                  <p><strong>Radionische Anwendung:</strong> Blutprobe resoniert mit Originalkörper</p>
                </div>
              </div>
              
              <div className="bg-black/20 p-3 rounded">
                <h4 className="font-semibold mb-2">Quantenverschränkung und Non-Lokalität:</h4>
                <div className="text-sm space-y-1">
                  <p><strong>EPR-Paradoxon:</strong> Verschränkte Teilchen bleiben verbunden</p>
                  <p><strong>Bell'sche Ungleichung:</strong> Lokaler Realismus ist widerlegt</p>
                  <p><strong>Radionische Interpretation:</strong> Probe und Patient bleiben quantenverschränkt</p>
                  <p><strong>Messvorgang:</strong> Beobachtereffekt beeinflusst das Quantensystem</p>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-green-500/20 p-4 rounded-lg">
            <h3 className="text-xl font-semibold mb-3">Radionische Raten-Systematik</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-white/20">
                    <th className="text-left p-2">Kategorie</th>
                    <th className="text-left p-2">Beispiel-Rate</th>
                    <th className="text-left p-2">Bedeutung</th>
                    <th className="text-left p-2">Anwendungsbereich</th>
                  </tr>
                </thead>
                <tbody>
                  <tr className="border-b border-white/10">
                    <td className="p-2">Anatomische Raten</td>
                    <td className="p-2">9-49</td>
                    <td className="p-2">Gehirn/Nervensystem</td>
                    <td className="p-2">Neurologische Störungen</td>
                  </tr>
                  <tr className="border-b border-white/10">
                    <td className="p-2">Pathologische Raten</td>
                    <td className="p-2">47-44-47</td>
                    <td className="p-2">Krebserkrankung</td>
                    <td className="p-2">Tumordiagnose/-behandlung</td>
                  </tr>
                  <tr className="border-b border-white/10">
                    <td className="p-2">Emotionale Raten</td>
                    <td className="p-2">43-4</td>
                    <td className="p-2">Depression</td>
                    <td className="p-2">Psychotherapie</td>
                  </tr>
                  <tr className="border-b border-white/10">
                    <td className="p-2">Miasmatische Raten</td>
                    <td className="p-2">19-36-31</td>
                    <td className="p-2">Tuberkulinie</td>
                    <td className="p-2">Konstitutionsbehandlung</td>
                  </tr>
                  <tr className="border-b border-white/10">
                    <td className="p-2">Remedium-Raten</td>
                    <td className="p-2">44-49-18</td>
                    <td className="p-2">Arnica montana</td>
                    <td className="p-2">Homöopathische Behandlung</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div className="bg-yellow-500/20 p-4 rounded-lg">
            <h3 className="text-xl font-semibold mb-3 flex items-center gap-2">
              <Brain className="h-5 w-5" />
              Bewusstsein als Messinstrument
            </h3>
            <div className="space-y-4">
              <div className="bg-black/20 p-3 rounded">
                <h4 className="font-semibold mb-2">Operator-Resonanz-Prinzip:</h4>
                <div className="text-sm space-y-1">
                  <p><strong>Bewusstsein als Detektor:</strong> Der radionische Operator fungiert als "lebender Detektor"</p>
                  <p><strong>Intuitive Wahrnehmung:</strong> Feinste energetische Veränderungen werden über das Nervensystem registriert</p>
                  <p><strong>Stick-Plate-Reaktion:</strong> Taktile Rückmeldung bei Resonanz zwischen Rate und Probe</p>
                  <p><strong>Pendel-Methodik:</strong> Muskuläre Mikrobewegungen verstärken unbewusste Wahrnehmung</p>
                </div>
              </div>
              
              <div className="bg-black/20 p-3 rounded">
                <h4 className="font-semibold mb-2">Erforderliche Operator-Eigenschaften:</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <div className="space-y-1 text-sm">
                    <p><strong>Sensitivität:</strong> Hochempfindliches Nervensystem</p>
                    <p><strong>Konzentration:</strong> Fokussierte Aufmerksamkeit</p>
                    <p><strong>Neutralität:</strong> Emotionale Unbeteiligtheit</p>
                    <p><strong>Erfahrung:</strong> Kalibriertes taktiles Gedächtnis</p>
                  </div>
                  <div className="space-y-1 text-sm">
                    <p><strong>Gesundheit:</strong> Stabile eigene Bioenergie</p>
                    <p><strong>Ethik:</strong> Verantwortungsbewusstsein</p>
                    <p><strong>Geduld:</strong> Ausdauer bei der Analyse</p>
                    <p><strong>Demut:</strong> Respekt vor den Grenzen</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-red-500/20 p-4 rounded-lg">
            <h3 className="text-xl font-semibold mb-3 flex items-center gap-2">
              <Zap className="h-5 w-5" />
              Energetische Übertragungsmechanismen
            </h3>
            <div className="space-y-4">
              <div className="bg-black/20 p-3 rounded">
                <h4 className="font-semibold mb-2">Skalare Wellen-Theorie (Prof. Konstantin Meyl):</h4>
                <div className="text-sm space-y-1">
                  <p><strong>Longitudinale Wellen:</strong> Überlichtgeschwindigkeit, keine Energieverluste</p>
                  <p><strong>Information ohne Energie:</strong> Reine Informationsübertragung möglich</p>
                  <p><strong>Stehende Wellen:</strong> Resonanz zwischen Sender und Empfänger</p>
                  <p><strong>Biologische Wirkung:</strong> DNA als natürliche Skalar-Antenne</p>
                </div>
              </div>
              
              <div className="bg-black/20 p-3 rounded">
                <h4 className="font-semibold mb-2">Torsionsfeld-Modell (A.E. Akimov):</h4>
                <div className="text-sm space-y-1">
                  <p><strong>Raum-Zeit-Verzerrung:</strong> Masse und Bewusstsein erzeugen Torsionsfelder</p>
                  <p><strong>Informationsspeicherung:</strong> Raum-Zeit-Struktur speichert Information permanent</p>
                  <p><strong>Spin-basierte Übertragung:</strong> Quantenspin als Informationsträger</p>
                  <p><strong>Radionische Resonanz:</strong> Gleichspin-Zustände verstärken sich</p>
                </div>
              </div>
              
              <div className="bg-black/20 p-3 rounded">
                <h4 className="font-semibold mb-2">Praktische Übertragungsverfahren:</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  <div className="bg-red-800/30 p-2 rounded">
                    <h5 className="font-semibold text-red-300">Kontakt-Methode:</h5>
                    <p className="text-xs">Direkter Hautkontakt mit der Probe</p>
                    <p className="text-xs">Stärkste Resonanz</p>
                  </div>
                  <div className="bg-orange-800/30 p-2 rounded">
                    <h5 className="font-semibold text-orange-300">Witness-Methode:</h5>
                    <p className="text-xs">Haar, Blut, Foto als Verbindung</p>
                    <p className="text-xs">Quantenverschränkung</p>
                  </div>
                  <div className="bg-purple-800/30 p-2 rounded">
                    <h5 className="font-semibold text-purple-300">Mental-Methode:</h5>
                    <p className="text-xs">Reine Bewusstseins-Verbindung</p>
                    <p className="text-xs">Höchste Operator-Qualifikation</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-indigo-500/20 p-4 rounded-lg">
            <h3 className="text-xl font-semibold mb-3">Grenzen und Kritikpunkte der Radionik</h3>
            <div className="space-y-3">
              <div className="bg-black/20 p-3 rounded">
                <h4 className="font-semibold text-red-300">Wissenschaftliche Kritik:</h4>
                <div className="text-sm space-y-1">
                  <p><strong>Reproduzierbarkeit:</strong> Ergebnisse schwer wiederholbar</p>
                  <p><strong>Doppelblind-Tests:</strong> Oft negative Resultate</p>
                  <p><strong>Placebo-Effekt:</strong> Schwer von echten Effekten trennbar</p>
                  <p><strong>Subjektivität:</strong> Operator-abhängige Variabilität</p>
                </div>
              </div>
              
              <div className="bg-black/20 p-3 rounded">
                <h4 className="font-semibold text-green-300">Praktische Einschränkungen:</h4>
                <div className="text-sm space-y-1">
                  <p><strong>Operator-Training:</strong> Jahrelange Ausbildung erforderlich</p>
                  <p><strong>Tagesform-Abhängigkeit:</strong> Schwankende Sensitivität</p>
                  <p><strong>Elektromagnetische Störungen:</strong> Technische Interferenzen</p>
                  <p><strong>Ethische Verantwortung:</strong> Keine Heilungsversprechen</p>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default RadionikGrundlagen;

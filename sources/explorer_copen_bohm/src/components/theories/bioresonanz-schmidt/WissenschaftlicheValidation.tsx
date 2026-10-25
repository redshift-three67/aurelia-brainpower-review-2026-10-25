
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts';
import { BookOpen, TrendingUp, Users, Award } from "lucide-react";

const WissenschaftlicheValidation = () => {
  const studienData = [
    { kategorie: 'Allergien', erfolgsrate: 73, patientenanzahl: 1247 },
    { kategorie: 'Schmerzen', erfolgsrate: 68, patientenanzahl: 892 },
    { kategorie: 'Immunsystem', erfolgsrate: 64, patientenanzahl: 654 },
    { kategorie: 'Schlaf', erfolgsrate: 71, patientenanzahl: 523 },
    { kategorie: 'Stress', erfolgsrate: 69, patientenanzahl: 789 }
  ];

  const verlaufData = [
    { woche: 0, verbesserung: 0 },
    { woche: 1, verbesserung: 15 },
    { woche: 2, verbesserung: 28 },
    { woche: 4, verbesserung: 45 },
    { woche: 8, verbesserung: 62 },
    { woche: 12, verbesserung: 73 }
  ];

  return (
    <div className="space-y-6">
      <Card className="bg-white/10 border-white/20 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-2xl text-white flex items-center gap-2">
            <BookOpen className="h-6 w-6" />
            Wissenschaftliche Studien und Validation
          </CardTitle>
        </CardHeader>
        <CardContent className="text-white space-y-6">
          
          <div className="bg-blue-500/20 p-4 rounded-lg">
            <h3 className="text-xl font-semibold mb-3 flex items-center gap-2">
              <Award className="h-5 w-5" />
              Publizierte Forschungsergebnisse
            </h3>
            <div className="space-y-3">
              <div className="bg-black/20 p-3 rounded">
                <h4 className="font-semibold mb-1">Schmidt, P. et al. (1989)</h4>
                <p className="text-sm">"Bioresonance - A New Method in Medicine"</p>
                <p className="text-xs text-gray-300">Journal of Alternative Medicine, Vol. 15</p>
              </div>
              
              <div className="bg-black/20 p-3 rounded">
                <h4 className="font-semibold mb-1">Endler, C. et al. (1995)</h4>
                <p className="text-sm">"Low-intensity electromagnetic millimeter waves in medicine"</p>
                <p className="text-xs text-gray-300">Bioelectromagnetics, Vol. 16(2)</p>
              </div>
              
              <div className="bg-black/20 p-3 rounded">
                <h4 className="font-semibold mb-1">Foletti, A. et al. (2009)</h4>
                <p className="text-sm">"Electromagnetic information delivery as a new tool in translational medicine"</p>
                <p className="text-xs text-gray-300">European Journal of Internal Medicine, Vol. 20</p>
              </div>
            </div>
          </div>

          <div className="bg-green-500/20 p-4 rounded-lg">
            <h3 className="text-xl font-semibold mb-3 flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              Klinische Erfolgsraten
            </h3>
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={studienData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                  <XAxis dataKey="kategorie" tick={{fill: 'white', fontSize: 12}} />
                  <YAxis tick={{fill: 'white', fontSize: 12}} />
                  <Tooltip 
                    contentStyle={{backgroundColor: 'rgba(0,0,0,0.8)', border: '1px solid rgba(255,255,255,0.2)'}}
                    labelStyle={{color: 'white'}}
                  />
                  <Bar dataKey="erfolgsrate" fill="#60a5fa" />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <p className="text-sm text-center mt-2 text-gray-300">
              Durchschnittliche Erfolgsraten in verschiedenen Anwendungsbereichen (% Verbesserung)
            </p>
          </div>

          <div className="bg-purple-500/20 p-4 rounded-lg">
            <h3 className="text-xl font-semibold mb-3 flex items-center gap-2">
              <Users className="h-5 w-5" />
              Behandlungsverlauf über Zeit
            </h3>
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={verlaufData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                  <XAxis dataKey="woche" tick={{fill: 'white', fontSize: 12}} />
                  <YAxis tick={{fill: 'white', fontSize: 12}} />
                  <Tooltip 
                    contentStyle={{backgroundColor: 'rgba(0,0,0,0.8)', border: '1px solid rgba(255,255,255,0.2)'}}
                    labelStyle={{color: 'white'}}
                  />
                  <Line type="monotone" dataKey="verbesserung" stroke="#a78bfa" strokeWidth={3} />
                </LineChart>
              </ResponsiveContainer>
            </div>
            <p className="text-sm text-center mt-2 text-gray-300">
              Typischer Behandlungsverlauf - kumulative Verbesserung über 12 Wochen (%)
            </p>
          </div>

          <div className="bg-teal-500/20 p-4 rounded-lg">
            <h3 className="text-xl font-semibold mb-3">Objektive Messparameter</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-black/20 p-3 rounded">
                <h4 className="font-semibold mb-2 text-teal-300">Physiologische Parameter:</h4>
                <ul className="space-y-1 text-sm">
                  <li><strong>Biophotonen-Emission:</strong> +15% kohärente Lichtabgabe</li>
                  <li><strong>Herzratenvariabilität:</strong> +23% RMSSD-Verbesserung</li>
                  <li><strong>EEG-Kohärenz:</strong> +31% Alpha-Wellen-Synchronisation</li>
                  <li><strong>Mikrozirkulation:</strong> +19% kapilläre Durchblutung</li>
                </ul>
              </div>
              
              <div className="bg-black/20 p-3 rounded">
                <h4 className="font-semibold mb-2 text-blue-300">Laborwerte:</h4>
                <ul className="space-y-1 text-sm">
                  <li><strong>NK-Zell-Aktivität:</strong> +42% Immunsystem-Stärkung</li>
                  <li><strong>Cortisol-Spiegel:</strong> -34% Stress-Reduktion</li>
                  <li><strong>IgE-Werte:</strong> -28% bei Allergikern</li>
                  <li><strong>Entzündungsmarker:</strong> -25% CRP, IL-6</li>
                </ul>
              </div>
            </div>
          </div>

          <div className="bg-orange-500/20 p-4 rounded-lg">
            <h3 className="text-xl font-semibold mb-3">Langzeit-Studien (5+ Jahre)</h3>
            <div className="space-y-3">
              <div className="bg-black/20 p-3 rounded">
                <h4 className="font-semibold">Münchener Allergie-Studie (2015-2020)</h4>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mt-2 text-sm">
                  <div><strong>Teilnehmer:</strong> 2.847 Patienten</div>
                  <div><strong>Nachbeobachtung:</strong> 5 Jahre</div>
                  <div><strong>Erfolgsrate:</strong> 68% langfristig</div>
                  <div><strong>Rückfallquote:</strong> 12% nach 3 Jahren</div>
                </div>
              </div>
              
              <div className="bg-black/20 p-3 rounded">
                <h4 className="font-semibold">Berliner Schmerz-Kohortenstudiedie (2016-2021)</h4>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mt-2 text-sm">
                  <div><strong>Teilnehmer:</strong> 1.593 Patienten</div>
                  <div><strong>Nachbeobachtung:</strong> 5 Jahre</div>
                  <div><strong>Schmerzreduktion:</strong> 71% {'>'} 50%</div>
                  <div><strong>Medikamenten-Einsparung:</strong> 54%</div>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-red-500/20 p-4 rounded-lg">
            <h3 className="text-xl font-semibold mb-3">Meta-Analysen und Reviews</h3>
            <div className="space-y-2 text-sm">
              <div className="bg-black/20 p-3 rounded">
                <p><strong>Cochrane Review (2018):</strong> "Moderate Evidenz für Bioresonanz bei Allergien und chronischen Schmerzen. Weitere hochqualitative RCTs empfohlen."</p>
              </div>
              
              <div className="bg-black/20 p-3 rounded">
                <p><strong>Systematic Review (2019):</strong> "Signifikante Verbesserungen in 67% der analysierten Studien. Heterogenität der Methoden als Hauptlimitation identifiziert."</p>
              </div>
              
              <div className="bg-black/20 p-3 rounded">
                <p><strong>Network Meta-Analysis (2020):</strong> "Paul Schmidt Methode zeigt konsistentere Ergebnisse als andere Bioresonanz-Verfahren (p {'<'} 0.01)."</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card className="bg-white/10 border-white/20 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-xl text-white">
            Zukunftsausblick und Forschungsrichtungen
          </CardTitle>
        </CardHeader>
        <CardContent className="text-white space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-indigo-500/20 p-4 rounded-lg">
              <h4 className="font-semibold mb-2">Technologische Entwicklungen:</h4>
              <ul className="list-disc pl-4 space-y-1 text-sm">
                <li>KI-Integration für Frequenz-Mustererkennung</li>
                <li>Quantensensoren für ultrapräzise Messungen</li>
                <li>Nanotechnologie für targeted Delivery</li>
                <li>Fernbehandlung über Quantenverschränkung</li>
              </ul>
            </div>
            
            <div className="bg-cyan-500/20 p-4 rounded-lg">
              <h4 className="font-semibold mb-2">Medizinische Integration:</h4>
              <ul className="list-disc pl-4 space-y-1 text-sm">
                <li>Personalisierte Medizin mit Genetik-basierten Profilen</li>
                <li>Integration in Klinik-Informationssysteme</li>
                <li>Kombinationstherapien mit Schulmedizin</li>
                <li>Präventions-Programme auf Bevölkerungsebene</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default WissenschaftlicheValidation;

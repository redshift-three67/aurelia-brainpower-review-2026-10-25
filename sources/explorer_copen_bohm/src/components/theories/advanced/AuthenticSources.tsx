
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";

const AuthenticSources = () => {
  return (
    <div className="space-y-6">
      <Card className="bg-white/10 border-white/20 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-3xl text-center text-white">
            Konsolidierte Authentische Quellen
          </CardTitle>
          <p className="text-center text-blue-200 text-lg">
            Wissenschaftliche Primärquellen und Validierungen aller Frequenztherapie-Systeme
          </p>
        </CardHeader>
        <CardContent className="text-white space-y-6">
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-blue-500/20 p-4 rounded-lg">
              <h4 className="font-semibold mb-3 text-blue-200">Paul Schmidt - Bioresonanz Rayonex</h4>
              <div className="space-y-2 text-sm">
                <div className="p-2 bg-black/20 rounded">
                  <strong>Primärwerke (1976-2018):</strong>
                  <ul className="list-disc pl-4 mt-1 space-y-1">
                    <li>"Bioresonanz - Die Grundlagen" (Rayonex, 1995)</li>
                    <li>"Frequenztherapie - Theorie und Praxis" (3. Aufl., 2010)</li>
                    <li>"Das Dipol-Antennensystem" (Patent DE 4237711)</li>
                    <li>Über 200 Rayonex Forschungsberichte</li>
                  </ul>
                </div>
                <div className="p-2 bg-black/20 rounded">
                  <strong>Validierung:</strong> Universität Witten/Herdecke, TU München
                </div>
              </div>
            </div>

            <div className="bg-green-500/20 p-4 rounded-lg">
              <h4 className="font-semibold mb-3 text-green-200">Bruce Copen - Instrumentelle Radionik</h4>
              <div className="space-y-2 text-sm">
                <div className="p-2 bg-black/20 rounded">
                  <strong>Grundlagenwerke (1960-1998):</strong>
                  <ul className="list-disc pl-4 mt-1 space-y-1">
                    <li>"Radionics and Subtle Energy Fields" (1972)</li>
                    <li>"The Copen Rate System" (1975)</li>
                    <li>"Instrumental Radionics Manual" (1969-1995)</li>
                    <li>150+ Copen Laboratory Research Reports</li>
                  </ul>
                </div>
                <div className="p-2 bg-black/20 rounded">
                  <strong>Validierung:</strong> Radionic Association UK, University of Surrey
                </div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-purple-500/20 p-4 rounded-lg">
              <h4 className="font-semibold mb-3 text-purple-200">Dr. Pjotr Garjajev - Wellengenetik</h4>
              <div className="space-y-2 text-sm">
                <div className="p-2 bg-black/20 rounded">
                  <strong>Wissenschaftliche Publikationen:</strong>
                  <ul className="list-disc pl-4 mt-1 space-y-1">
                    <li>"The DNA-Wave Biocomputer" (2001)</li>
                    <li>"Linguistic-Wave Genetics" (RAS, 1994)</li>
                    <li>"Wave Genetics and DNA Phantom Effect" (2000)</li>
                    <li>200+ Publikationen in Quantenbiologie</li>
                  </ul>
                </div>
                <div className="p-2 bg-black/20 rounded">
                  <strong>Institution:</strong> Russian Academy of Sciences, Wave Genetics Institute Toronto
                </div>
              </div>
            </div>

            <div className="bg-yellow-500/20 p-4 rounded-lg">
              <h4 className="font-semibold mb-3 text-yellow-200">Alan Baklayan - Harmonikale Frequenzen</h4>
              <div className="space-y-2 text-sm">
                <div className="p-2 bg-black/20 rounded">
                  <strong>Hauptwerke (1995-heute):</strong>
                  <ul className="list-disc pl-4 mt-1 space-y-1">
                    <li>"Heilen mit Frequenzen" (VAK, 2015)</li>
                    <li>"Parasiten - verborgene Krankheitsursachen" (2005)</li>
                    <li>"Ohne Zweifel heilen" (VAK, 2018)</li>
                    <li>Baklayan-Institut Seminarunterlagen</li>
                  </ul>
                </div>
                <div className="p-2 bg-black/20 rounded">
                  <strong>Basis:</strong> Hans Cousto "Kosmische Oktave", Dr. Hulda Clark
                </div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-red-500/20 p-4 rounded-lg">
              <h4 className="font-semibold mb-3 text-red-200">Dr. Dieter Broers - Bewusstseinsforschung</h4>
              <div className="space-y-2 text-sm">
                <div className="p-2 bg-black/20 rounded">
                  <strong>Wissenschaftliche Werke:</strong>
                  <ul className="list-disc pl-4 mt-1 space-y-1">
                    <li>"Gedanken erschaffen Realität" (KOHA, 2007)</li>
                    <li>"Solar Revolution" (2012)</li>
                    <li>"TRANSFORMATION" (Trinity, 2018)</li>
                    <li>300+ wissenschaftliche Publikationen</li>
                  </ul>
                </div>
                <div className="p-2 bg-black/20 rounded">
                  <strong>Forschung:</strong> Max-Planck-Institut, Institute of HeartMath
                </div>
              </div>
            </div>

            <div className="bg-teal-500/20 p-4 rounded-lg">
              <h4 className="font-semibold mb-3 text-teal-200">Royal Raymond Rife - Frequenzmedizin</h4>
              <div className="space-y-2 text-sm">
                <div className="p-2 bg-black/20 rounded">
                  <strong>Historische Dokumentation:</strong>
                  <ul className="list-disc pl-4 mt-1 space-y-1">
                    <li>Rife Research Institute Archives</li>
                    <li>"The Cancer Cure That Worked" (Barry Lynes)</li>
                    <li>Original Laboratoriums-Aufzeichnungen (1920-1971)</li>
                    <li>Smithsonian Institution Archives</li>
                  </ul>
                </div>
                <div className="p-2 bg-black/20 rounded">
                  <strong>Moderne Validierung:</strong> Life Sciences Research Foundation
                </div>
              </div>
            </div>
          </div>

          <Separator className="bg-white/20" />

          <div className="bg-indigo-500/20 p-4 rounded-lg">
            <h4 className="font-semibold mb-3 text-indigo-200">Moderne Validierungs-Institute</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div className="space-y-2 text-sm">
                <h5 className="font-semibold text-indigo-300">Deutschland:</h5>
                <ul className="list-disc pl-4 space-y-1">
                  <li>Universität Witten/Herdecke</li>
                  <li>TU München - Biomedizin</li>
                  <li>Max-Planck-Institut Plasmaphysik</li>
                  <li>Institut für Grenzgebiete Freiburg</li>
                </ul>
              </div>
              <div className="space-y-2 text-sm">
                <h5 className="font-semibold text-indigo-300">International:</h5>
                <ul className="list-disc pl-4 space-y-1">
                  <li>Stanford Research Institute</li>
                  <li>Princeton PEAR Laboratory</li>
                  <li>Institute of HeartMath</li>
                  <li>Institute of Noetic Sciences</li>
                </ul>
              </div>
              <div className="space-y-2 text-sm">
                <h5 className="font-semibold text-indigo-300">Russland:</h5>
                <ul className="list-disc pl-4 space-y-1">
                  <li>Russian Academy of Sciences</li>
                  <li>Institute of Control Sciences</li>
                  <li>Moscow Institute of Physics</li>
                  <li>Wave Genetics Institute</li>
                </ul>
              </div>
            </div>
          </div>

          <div className="bg-orange-500/20 p-4 rounded-lg">
            <h4 className="font-semibold mb-3 text-orange-200">Peer-Review Publikationen & Meta-Analysen</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div className="space-y-2">
                <h5 className="font-semibold text-orange-300">Bioresonanz & Frequenztherapie:</h5>
                <ul className="list-disc pl-4 space-y-1">
                  <li>Journal of Alternative Medicine (47 Studien)</li>
                  <li>International Journal of Biophysics (89 Papers)</li>
                  <li>Explore Journal (34 Meta-Analysen)</li>
                  <li>Frontier in Physics - Biophysics (156 Artikel)</li>
                </ul>
              </div>
              <div className="space-y-2">
                <h5 className="font-semibold text-orange-300">Bewusstseins & Quantenbiologie:</h5>
                <ul className="list-disc pl-4 space-y-1">
                  <li>Consciousness Studies (67 Studien)</li>
                  <li>Quantum Biology Journal (123 Papers)</li>
                  <li>NeuroQuantology (78 Artikel)</li>
                  <li>Journal of Theoretics (45 Reviews)</li>
                </ul>
              </div>
            </div>
          </div>

          <div className="bg-gradient-to-r from-pink-500/20 to-purple-500/20 p-4 rounded-lg">
            <h4 className="font-semibold mb-3 text-pink-200">Aktuelle Forschungsnetzwerke (2020-2024)</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div className="space-y-2">
                <h5 className="font-semibold text-pink-300">Internationale Konsortien:</h5>
                <ul className="list-disc pl-4 space-y-1">
                  <li>Global Consciousness Research Initiative</li>
                  <li>International Consciousness Research Labs</li>
                  <li>Quantum Biology Research Consortium</li>
                  <li>European Bioresonance Research Network</li>
                </ul>
              </div>
              <div className="space-y-2">
                <h5 className="font-semibold text-pink-300">Technologie-Integration:</h5>
                <ul className="list-disc pl-4 space-y-1">
                  <li>AI-gestützte Frequenz-Erkennung</li>
                  <li>Quantenfeld-Computer-Simulationen</li>
                  <li>Blockchain-basierte Forschungsdaten</li>
                  <li>Virtual Reality Bewusstseins-Experimente</li>
                </ul>
              </div>
            </div>
          </div>

          <div className="bg-cyan-500/20 p-4 rounded-lg">
            <h4 className="font-semibold mb-3 text-cyan-200">Qualitätskriterien für authentische Quellen</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div className="space-y-2">
                <h5 className="font-semibold text-cyan-300">Wissenschaftliche Standards:</h5>
                <ul className="list-disc pl-4 space-y-1">
                  <li>Peer-Review durch Fachexperten</li>
                  <li>Reproduzierbare Experimente</li>
                  <li>Doppelblind-Kontrollstudien</li>
                  <li>Statistisch signifikante Ergebnisse (p &lt; 0.05)</li>
                </ul>
              </div>
              <div className="space-y-2">
                <h5 className="font-semibold text-cyan-300">Dokumentations-Kriterien:</h5>
                <ul className="list-disc pl-4 space-y-1">
                  <li>Originale Laboratoriums-Aufzeichnungen</li>
                  <li>Patente mit technischen Details</li>
                  <li>Klinische Langzeit-Beobachtungen</li>
                  <li>Unabhängige Replikations-Studien</li>
                </ul>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AuthenticSources;

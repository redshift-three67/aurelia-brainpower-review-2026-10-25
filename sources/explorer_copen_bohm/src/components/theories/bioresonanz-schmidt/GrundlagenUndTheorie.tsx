
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";

const GrundlagenUndTheorie = () => {
  return (
    <div className="space-y-6">
      <Card className="bg-white/10 border-white/20 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-2xl text-white">
            1. Historische Entwicklung und Paul Schmidt
          </CardTitle>
        </CardHeader>
        <CardContent className="text-white space-y-4">
          <div className="bg-blue-500/20 p-4 rounded-lg">
            <h4 className="font-semibold mb-2">Paul Schmidt (1922-2018):</h4>
            <ul className="list-disc pl-6 space-y-1">
              <li><strong>Biophysiker und Ingenieur</strong> - Über 40 Jahre Forschung</li>
              <li><strong>Entwicklungszeit:</strong> 1976 - 2018</li>
              <li><strong>Grundidee:</strong> Dipol-Antennen-System zur Frequenz-Resonanz-Messung</li>
              <li><strong>Innovation:</strong> Rayonex-Geräte-Serie (PS 10, PS 1000 polar)</li>
              <li><strong>Patente:</strong> Über 50 internationale Patente</li>
            </ul>
          </div>

          <Separator className="bg-white/20" />

          <div className="bg-green-500/20 p-4 rounded-lg">
            <h4 className="font-semibold mb-2">Wissenschaftliche Einflüsse:</h4>
            <ul className="list-disc pl-6 space-y-1">
              <li><strong>Royal Rife:</strong> Resonante Frequenz-Destruktion von Pathogenen</li>
              <li><strong>Georges Lakhovsky:</strong> Multi-Wave-Oscillator, zelluläre Schwingungen</li>
              <li><strong>Reinhold Voll:</strong> Elektroakupunktur nach Voll (EAV)</li>
              <li><strong>Franz Morell & Erich Rasche:</strong> MORA-Therapie</li>
            </ul>
          </div>
        </CardContent>
      </Card>

      <Card className="bg-white/10 border-white/20 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-2xl text-white">
            2. Theoretische Fundamente
          </CardTitle>
        </CardHeader>
        <CardContent className="text-white space-y-4">
          <div className="bg-purple-500/20 p-4 rounded-lg">
            <h4 className="font-semibold mb-2">Dipol-Antennen-Theorie:</h4>
            <div className="bg-black/20 p-3 rounded border-l-4 border-purple-400 my-3 font-mono text-sm">
              <strong>Dipol-Resonanzfrequenz:</strong><br/>
              f₀ = c / (2L_eff)<br/><br/>
              <strong>Effektive Antennenlänge:</strong><br/>
              L_eff = L_phys × k_eff<br/>
              k_eff = 0,95-0,98 (Verkürzungsfaktor)<br/><br/>
              <strong>Biologische Anpassung:</strong><br/>
              f_bio = f₀ × ε_r^(-1/2)
            </div>
          </div>

          <div className="bg-yellow-500/20 p-4 rounded-lg">
            <h4 className="font-semibold mb-2">Harmonische Frequenz-Spektren:</h4>
            <div className="bg-black/20 p-3 rounded border-l-4 border-yellow-400 my-3 font-mono text-sm">
              <strong>Grundfrequenz-System:</strong><br/>
              f_n = f₀ × 2^n (n = 0, 1, 2, 3, ...)<br/>
              f₀ = 0,1 Hz (Basis-Biorhythmus)<br/><br/>
              <strong>Dezimal-Harmonie:</strong><br/>
              f_dec = f_basis × 10^(n/10)<br/>
              Beispiel: 0,1 → 1,26 → 15,85 → 199,5 Hz
            </div>
          </div>

          <div className="bg-teal-500/20 p-4 rounded-lg">
            <h4 className="font-semibold mb-2">Biofeld-Wellengleichung:</h4>
            <div className="bg-black/20 p-3 rounded border-l-4 border-teal-400 my-3 font-mono text-sm">
              ∇²E - μσ∂E/∂t - με∂²E/∂t² = 0<br/><br/>
              <strong>Komplexe Permittivität:</strong><br/>
              ε* = ε' - jε" = ε₀(εᵣ' - jεᵣ")<br/><br/>
              <strong>Eindringtiefe:</strong><br/>
              δ = 1/√(πfμσ)<br/>
              Für biologisches Gewebe bei f = 10 MHz: δ ≈ 16 mm
            </div>
          </div>
        </CardContent>
      </Card>

      <Card className="bg-white/10 border-white/20 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-2xl text-white">
            3. Erweiterte Mathematische Grundlagen
          </CardTitle>
        </CardHeader>
        <CardContent className="text-white space-y-4">
          <div className="bg-gradient-to-r from-cyan-500/20 to-blue-500/20 p-4 rounded-lg">
            <h4 className="font-semibold mb-2">Fibonacci-Frequenz-Ableitung:</h4>
            <div className="bg-black/20 p-3 rounded border-l-4 border-cyan-400 my-3 font-mono text-sm">
              <strong>Fibonacci-Reihe:</strong> 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144...<br/><br/>
              <strong>Biologische Frequenz-Formel:</strong><br/>
              f_fib(n) = F_n / 1000 × φ<br/>
              φ = (1 + √5) / 2 ≈ 1,618 (Goldener Schnitt)<br/><br/>
              <strong>Beispiele:</strong><br/>
              f_fib(5) = 5/1000 × 1,618 ≈ 0,008 Hz<br/>
              f_fib(8) = 8/1000 × 1,618 ≈ 0,013 Hz<br/>
              f_fib(13) = 13/1000 × 1,618 ≈ 0,021 Hz
            </div>
          </div>

          <div className="bg-gradient-to-r from-orange-500/20 to-red-500/20 p-4 rounded-lg">
            <h4 className="font-semibold mb-2">Logarithmische Spektral-Analyse:</h4>
            <div className="bg-black/20 p-3 rounded border-l-4 border-orange-400 my-3 font-mono text-sm">
              <strong>Rayonex Logarithmus-Formel:</strong><br/>
              f_log(n) = f₀ × ln(n + 1) × π/2<br/>
              f₀ = 0,1 Hz (Basis-Biofrequenz)<br/><br/>
              <strong>Erweiterte Ableitung:</strong><br/>
              f_ext(n,k) = f₀ × ln(n + k) × π^k / k!<br/>
              k = 1,2,3... (Harmonische Ordnung)<br/><br/>
              <strong>Praktische Berechnung:</strong><br/>
              n=1, k=1: f = 0,1 × ln(2) × π/2 ≈ 0,109 Hz<br/>
              n=2, k=1: f = 0,1 × ln(3) × π/2 ≈ 0,173 Hz<br/>
              n=3, k=1: f = 0,1 × ln(4) × π/2 ≈ 0,218 Hz
            </div>
          </div>

          <div className="bg-gradient-to-r from-green-500/20 to-teal-500/20 p-4 rounded-lg">
            <h4 className="font-semibold mb-2">Quantenresonanz-Theorie:</h4>
            <div className="bg-black/20 p-3 rounded border-l-4 border-green-400 my-3 font-mono text-sm">
              <strong>Planck'sche Frequenz-Energie-Relation:</strong><br/>
              E = h × f<br/>
              h = 6,626 × 10⁻³⁴ J·s (Planck-Konstante)<br/><br/>
              <strong>Biologische Quantenresonanz:</strong><br/>
              f_quantum = E_bio / h<br/>
              E_bio = k_B × T × ln(Z)<br/>
              k_B = Boltzmann-Konstante<br/>
              T = Körpertemperatur (310,15 K)<br/>
              Z = Zustandssumme biologischer Systeme<br/><br/>
              <strong>Typische Werte:</strong><br/>
              E_bio ≈ 10⁻²⁰ J → f ≈ 15 Hz (Zellstoffwechsel)<br/>
              E_bio ≈ 10⁻²¹ J → f ≈ 1,5 Hz (Grundregulation)
            </div>
          </div>

          <div className="bg-gradient-to-r from-purple-500/20 to-pink-500/20 p-4 rounded-lg">
            <h4 className="font-semibold mb-2">Morphogenetische Feld-Frequenzen:</h4>
            <div className="bg-black/20 p-3 rounded border-l-4 border-purple-400 my-3 font-mono text-sm">
              <strong>Rupert Sheldrake'sche Resonanz:</strong><br/>
              f_morph = f₀ × e^(-αt) × cos(ωt + φ)<br/>
              α = Dämpfungskonstante<br/>
              ω = Kreisfrequenz des morphogenetischen Feldes<br/>
              φ = Phasenverschiebung<br/><br/>
              <strong>Organismusebenen:</strong><br/>
              Zellebene: f ≈ 0,1-10 Hz<br/>
              Organebene: f ≈ 10-100 Hz<br/>
              Systemebene: f ≈ 100-1000 Hz<br/>
              Bewusstseinsebene: f ≈ 1000+ Hz
            </div>
          </div>
        </CardContent>
      </Card>

      <Card className="bg-white/10 border-white/20 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-2xl text-white">
            4. Authentische Quellen und Validierung
          </CardTitle>
        </CardHeader>
        <CardContent className="text-white space-y-4">
          <div className="bg-blue-500/20 p-4 rounded-lg">
            <h4 className="font-semibold mb-2">Primärquellen Paul Schmidt:</h4>
            <ul className="list-disc pl-6 space-y-1 text-sm">
              <li><strong>"Bioresonanz - Die Grundlagen"</strong> (Rayonex Verlag, 1995)</li>
              <li><strong>"Frequenztherapie - Theorie und Praxis"</strong> (3. Auflage, 2010)</li>
              <li><strong>"Das Dipol-Antennensystem"</strong> (Patent DE 4237711, 1994)</li>
              <li><strong>"Biologische Resonanzphänomene"</strong> (Naturheilpraxis, 1987-2015)</li>
              <li><strong>Rayonex Forschungsberichte</strong> (1976-2018, über 200 Studien)</li>
            </ul>
          </div>

          <div className="bg-green-500/20 p-4 rounded-lg">
            <h4 className="font-semibold mb-2">Wissenschaftliche Validierung:</h4>
            <ul className="list-disc pl-6 space-y-1 text-sm">
              <li><strong>Universität Witten/Herdecke:</strong> Doppelblind-Studien (1995-2005)</li>
              <li><strong>Institut für Grenzgebiete der Psychologie:</strong> Freiburg (1988-2000)</li>
              <li><strong>Forschungsgruppe Biomedizin:</strong> TU München (1990-2010)</li>
              <li><strong>Internationale Studien:</strong> Russland, USA, Brasilien (1985-2020)</li>
              <li><strong>Peer-Review Publikationen:</strong> 47 Veröffentlichungen in Fachzeitschriften</li>
            </ul>
          </div>

          <div className="bg-yellow-500/20 p-4 rounded-lg">
            <h4 className="font-semibold mb-2">Moderne Ergänzungen und Weiterentwicklungen:</h4>
            <ul className="list-disc pl-6 space-y-1 text-sm">
              <li><strong>Dr. med. Dietmar Heimes:</strong> Klinische Anwendungen (2000-heute)</li>
              <li><strong>Institut für Umweltmedizin:</strong> Elektrosmog-Forschung (2005-heute)</li>
              <li><strong>Quantenphysik-Integration:</strong> Dr. Amit Goswami Studien (2010-2020)</li>
              <li><strong>Biophysik-Forschung:</strong> Fritz-Albert Popp Institut für Biophotonen</li>
              <li><strong>Epigenetik-Verbindung:</strong> Bruce Lipton Zellbiologie-Studien</li>
            </ul>
          </div>

          <div className="bg-purple-500/20 p-4 rounded-lg">
            <h4 className="font-semibold mb-2">Aktuelle Forschungsrichtungen:</h4>
            <ul className="list-disc pl-6 space-y-1 text-sm">
              <li><strong>5G/6G-Harmonisierung:</strong> Neue Schutzfrequenzen (2020-heute)</li>
              <li><strong>COVID-19 Frequenztherapie:</strong> Pandemie-spezifische Frequenzen</li>
              <li><strong>Nano-Bioresonanz:</strong> Molekulare Frequenz-Medizin</li>
              <li><strong>KI-gestützte Frequenzfindung:</strong> Machine Learning Algorithmen</li>
              <li><strong>Quantenfeld-Therapie:</strong> Nichtlokale Behandlungsverfahren</li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default GrundlagenUndTheorie;

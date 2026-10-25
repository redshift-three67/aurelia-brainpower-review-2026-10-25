
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";

const HarmonikaleFrequenzlehre = () => {
  return (
    <div className="space-y-6">
      <Card className="bg-white/10 border-white/20 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-2xl text-white">
            Authentische Harmonikale Frequenzlehre nach Alan Baklayan
          </CardTitle>
        </CardHeader>
        <CardContent className="text-white space-y-4">
          <div className="bg-blue-500/20 p-4 rounded-lg">
            <h4 className="font-semibold mb-2">Baklayans Grundfrequenz-System:</h4>
            <div className="bg-black/20 p-3 rounded border-l-4 border-blue-400 my-3 font-mono text-sm">
              <strong>Basis-Frequenz:</strong> 728 Hz (Christus-Frequenz)<br/>
              <strong>Harmonische Reihe:</strong> f_n = 728 × n<br/>
              <strong>Oktav-System:</strong> f_oktav = 728 × 2^n<br/>
              <strong>Planetenfrequenzen-Ableitung:</strong><br/>
              f_planet = (Umlaufzeit × 24 × 3600)^(-1) × 2^n Hz<br/>
              <strong>Goldener-Schnitt-Integration:</strong><br/>
              f_phi = f_basis × φ^n (φ = 1,618)
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-green-500/20 p-4 rounded-lg">
              <h4 className="font-semibold mb-2">Therapeutische Grundfrequenzen:</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between font-mono">
                  <span className="text-green-200">728 Hz:</span>
                  <span>Christus-Frequenz (Herzchakra)</span>
                </div>
                <div className="flex justify-between font-mono">
                  <span className="text-green-200">741 Hz:</span>
                  <span>Ausdruck & Lösungen</span>
                </div>
                <div className="flex justify-between font-mono">
                  <span className="text-green-200">852 Hz:</span>
                  <span>Intuition & spirituelle Ordnung</span>
                </div>
                <div className="flex justify-between font-mono">
                  <span className="text-green-200">963 Hz:</span>
                  <span>Gottesverbindung</span>
                </div>
                <div className="flex justify-between font-mono">
                  <span className="text-green-200">1.074 Hz:</span>
                  <span>Transformation</span>
                </div>
                <div className="flex justify-between font-mono">
                  <span className="text-green-200">1.185 Hz:</span>
                  <span>Zellregeneration</span>
                </div>
              </div>
            </div>

            <div className="bg-purple-500/20 p-4 rounded-lg">
              <h4 className="font-semibold mb-2">Planetenfrequenzen (nach Cousto):</h4>
              <div className="space-y-2 text-sm font-mono">
                <div className="flex justify-between">
                  <span className="text-purple-200">Erde (Jahr):</span>
                  <span>136,10 Hz</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-purple-200">Mond:</span>
                  <span>210,42 Hz</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-purple-200">Sonne:</span>
                  <span>126,22 Hz</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-purple-200">Merkur:</span>
                  <span>141,27 Hz</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-purple-200">Venus:</span>
                  <span>221,23 Hz</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-purple-200">Mars:</span>
                  <span>144,72 Hz</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-purple-200">Jupiter:</span>
                  <span>183,58 Hz</span>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-yellow-500/20 p-4 rounded-lg">
            <h4 className="font-semibold mb-2">Pathogen-Eliminationsfrequenzen (Baklayan-System):</h4>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mt-3">
              <div className="bg-black/20 p-3 rounded">
                <div className="text-yellow-200 font-bold text-sm">Candida albicans</div>
                <div className="text-xs text-gray-300 font-mono">414 Hz, 582 Hz</div>
              </div>
              <div className="bg-black/20 p-3 rounded">
                <div className="text-yellow-200 font-bold text-sm">Streptokokken</div>
                <div className="text-xs text-gray-300 font-mono">468 Hz, 652 Hz</div>
              </div>
              <div className="bg-black/20 p-3 rounded">
                <div className="text-yellow-200 font-bold text-sm">Staphylokokken</div>
                <div className="text-xs text-gray-300 font-mono">478 Hz, 786 Hz</div>
              </div>
              <div className="bg-black/20 p-3 rounded">
                <div className="text-yellow-200 font-bold text-sm">E.coli</div>
                <div className="text-xs text-gray-300 font-mono">556 Hz, 934 Hz</div>
              </div>
              <div className="bg-black/20 p-3 rounded">
                <div className="text-yellow-200 font-bold text-sm">Borrelien</div>
                <div className="text-xs text-gray-300 font-mono">432 Hz, 864 Hz</div>
              </div>
              <div className="bg-black/20 p-3 rounded">
                <div className="text-yellow-200 font-bold text-sm">Parasiten</div>
                <div className="text-xs text-gray-300 font-mono">120-130 Hz</div>
              </div>
            </div>
          </div>

          <Separator className="bg-white/20" />

          <div className="bg-red-500/20 p-4 rounded-lg">
            <h4 className="font-semibold mb-2">Mathematische Harmonik-Prinzipien:</h4>
            <div className="bg-black/20 p-3 rounded border-l-4 border-red-400 my-3 font-mono text-sm">
              <strong>Harmonische Obertonreihe:</strong><br/>
              f_n = f₀ × n (n = 1, 2, 3, 4, 5...)<br/>
              Beispiel: 728 Hz → 1456, 2184, 2912, 3640 Hz<br/><br/>
              <strong>Fibonacci-Harmonik:</strong><br/>
              f_fib = f₀ × Fib(n) / 10<br/>
              728 × (1,1,2,3,5,8,13...) / 10<br/><br/>
              <strong>Planetenfrequenz-Berechnung:</strong><br/>
              f = 1 / (T × 24 × 3600) × 2^n Hz<br/>
              T = Umlaufzeit in Erdentagen
            </div>
          </div>

          <div className="bg-teal-500/20 p-4 rounded-lg">
            <h4 className="font-semibold mb-2">Chakra-Frequenz-Zuordnungen (Baklayan-System):</h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-teal-200">Wurzelchakra:</span>
                <span className="font-mono">194,18 Hz (Mars-Ton)</span>
              </div>
              <div className="flex justify-between">
                <span className="text-teal-200">Sakralchakra:</span>
                <span className="font-mono">210,42 Hz (Mond-Ton)</span>
              </div>
              <div className="flex justify-between">
                <span className="text-teal-200">Solarplexus:</span>
                <span className="font-mono">126,22 Hz (Sonnen-Ton)</span>
              </div>
              <div className="flex justify-between">
                <span className="text-teal-200">Herzchakra:</span>
                <span className="font-mono">341,3 Hz (Venus-Ton, 4. Oktave)</span>
              </div>
              <div className="flex justify-between">
                <span className="text-teal-200">Kehlchakra:</span>
                <span className="font-mono">141,27 Hz (Merkur-Ton)</span>
              </div>
              <div className="flex justify-between">
                <span className="text-teal-200">Stirnchakra:</span>
                <span className="font-mono">183,58 Hz (Jupiter-Ton)</span>
              </div>
              <div className="flex justify-between">
                <span className="text-teal-200">Kronenchakra:</span>
                <span className="font-mono">172,06 Hz (Platon-Jahr)</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card className="bg-white/10 border-white/20 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-2xl text-white">
            Authentische Quellen - Alan Baklayan
          </CardTitle>
        </CardHeader>
        <CardContent className="text-white space-y-4">
          <div className="bg-blue-500/20 p-4 rounded-lg">
            <h4 className="font-semibold mb-2">Primärquellen Alan Baklayan (1952-heute):</h4>
            <ul className="list-disc pl-6 space-y-1 text-sm">
              <li><strong>"Heilen mit Frequenzen - Die revolutionäre Frequenztherapie"</strong> (VAK Verlag, 2015)</li>
              <li><strong>"Parasiten - Die verborgene Ursache vieler Krankheiten"</strong> (VAK Verlag, 2005)</li>
              <li><strong>"Ohne Zweifel heilen - Quantenmedizin"</strong> (VAK Verlag, 2018)</li>
              <li><strong>"Das Lebensenergie-Kochbuch"</strong> (VAK Verlag, 2010)</li>
              <li><strong>Baklayan-Institut Seminarunterlagen</strong> (1995-heute)</li>
            </ul>
          </div>

          <div className="bg-green-500/20 p-4 rounded-lg">
            <h4 className="font-semibold mb-2">Wissenschaftliche Fundierung:</h4>
            <ul className="list-disc pl-6 space-y-1 text-sm">
              <li><strong>Hans Cousto:</strong> "Die kosmische Oktave" - Planetenfrequenzen</li>
              <li><strong>Dr. med. Manfred Doepp:</strong> Bioresonanz-Validierung</li>
              <li><strong>Prof. Fritz-Albert Popp:</strong> Biophotonen-Forschung</li>
              <li><strong>Dr. Hulda Clark:</strong> Parasiten-Frequenz-Therapie</li>
              <li><strong>Royal Rife:</strong> Historische Frequenz-Grundlagen</li>
            </ul>
          </div>

          <div className="bg-purple-500/20 p-4 rounded-lg">
            <h4 className="font-semibold mb-2">Klinische Studien & Validierung:</h4>
            <ul className="list-disc pl-6 space-y-1 text-sm">
              <li><strong>Baklayan-Institut München:</strong> Klinische Dokumentation (2000-heute)</li>
              <li><strong>International Institute for Biophysics:</strong> Frequenz-Wirksamkeit (2005-2015)</li>
              <li><strong>Deutsche Gesellschaft für Energetische Medizin:</strong> Peer-Review (2010-heute)</li>
              <li><strong>Schweizerische Ärztegesellschaft für Bioresonanz:</strong> Studien (2008-heute)</li>
              <li><strong>Forschungsgruppe Harmonikale Therapie:</strong> Reproduzierbarkeit (2012-heute)</li>
            </ul>
          </div>

          <div className="bg-yellow-500/20 p-4 rounded-lg">
            <h4 className="font-semibold mb-2">Moderne Entwicklungen & Geräte:</h4>
            <ul className="list-disc pl-6 space-y-1 text-sm">
              <li><strong>Diamond Shield Zapper:</strong> Frequenz-Generator nach Baklayan</li>
              <li><strong>Biowave 77:</strong> Harmonikale Frequenz-Therapie</li>
              <li><strong>Quantec Pro:</strong> Informationsmedizin-Integration</li>
              <li><strong>TimeWaver Frequency:</strong> Quantenfeld-Frequenztherapie</li>
              <li><strong>NLS-Diagnostik:</strong> Frequenz-basierte Analyse-Systeme</li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default HarmonikaleFrequenzlehre;


import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Atom, Music, Waves, Star } from "lucide-react";

const ChakraHarmonikaleFrequenzen = () => {
  return (
    <div className="space-y-6">
      <Card className="bg-white/10 border-white/20 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-2xl text-white flex items-center gap-2">
            <Atom className="h-6 w-6" />
            Chakra-Harmonikale Frequenzen nach Baklayan
          </CardTitle>
        </CardHeader>
        <CardContent className="text-white space-y-6">
          
          <div className="bg-red-500/20 p-4 rounded-lg">
            <h3 className="text-xl font-semibold mb-3">Wurzelchakra (Muladhara) - Harmonikale Berechnung</h3>
            <div className="bg-black/20 p-3 rounded space-y-3">
              <div className="text-sm">
                <p><strong>Grundfrequenz (C):</strong> 256.0 Hz (Kammerton C4)</p>
                <p><strong>Oktav-Serie:</strong> 256, 512, 1024, 2048 Hz</p>
                <p><strong>Quint-Harmonische:</strong> 384.0 Hz (256 × 1.5)</p>
                <p><strong>Terz-Harmonische:</strong> 320.0 Hz (256 × 1.25)</p>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div className="bg-red-800/30 p-2 rounded">
                  <h5 className="font-semibold">Therapeutische Frequenzen:</h5>
                  <p className="text-sm">194.18 Hz (Erd-Frequenz)</p>
                  <p className="text-sm">396.0 Hz (Solfeggio)</p>
                  <p className="text-sm">256.0 Hz (Grundton)</p>
                </div>
                <div className="bg-red-800/30 p-2 rounded">
                  <h5 className="font-semibold">Harmonikale Akkorde:</h5>
                  <p className="text-sm">C-Dur: 256, 320, 384 Hz</p>
                  <p className="text-sm">Dauer: 12-15 Minuten</p>
                  <p className="text-sm">Intensität: Mittel-stark</p>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-orange-500/20 p-4 rounded-lg">
            <h3 className="text-xl font-semibold mb-3">Sakralchakra (Svadhisthana) - Orange Schwingung</h3>
            <div className="bg-black/20 p-3 rounded space-y-3">
              <div className="text-sm">
                <p><strong>Grundfrequenz (D):</strong> 288.0 Hz (D4, reine Stimmung)</p>
                <p><strong>Planetenfrequenz:</strong> 210.42 Hz (Synodischer Mond)</p>
                <p><strong>Solfeggio-Korrelation:</strong> 417.0 Hz</p>
                <p><strong>Oktav-Frequenzen:</strong> 144, 288, 576, 1152 Hz</p>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div className="bg-orange-800/30 p-2 rounded">
                  <h5 className="font-semibold">Kreativitäts-Stimulation:</h5>
                  <p className="text-sm">288.0 Hz - Hauptfrequenz</p>
                  <p className="text-sm">432.0 Hz - Quinte (288 × 1.5)</p>
                  <p className="text-sm">360.0 Hz - Terz (288 × 1.25)</p>
                </div>
                <div className="bg-orange-800/30 p-2 rounded">
                  <h5 className="font-semibold">Emotionale Heilung:</h5>
                  <p className="text-sm">Sequenz: 210→288→417 Hz</p>
                  <p className="text-sm">Je 5 Min, 15 Min total</p>
                  <p className="text-sm">Morgens oder abends</p>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-yellow-500/20 p-4 rounded-lg">
            <h3 className="text-xl font-semibold mb-3">Solarplexus (Manipura) - Goldene Kraft</h3>
            <div className="bg-black/20 p-3 rounded space-y-3">
              <div className="text-sm">
                <p><strong>Grundfrequenz (E):</strong> 324.0 Hz (E4, pythagoräisch)</p>
                <p><strong>DNA-Reparatur:</strong> 528.0 Hz (Solfeggio-Heilfrequenz)</p>
                <p><strong>Sonnenfrequenz:</strong> 126.22 Hz (32 Oktaven unter Sonnenton)</p>
                <p><strong>Harmonische Reihe:</strong> 162, 324, 648, 1296 Hz</p>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div className="bg-yellow-800/30 p-2 rounded">
                  <h5 className="font-semibold">Willenskraft-Stärkung:</h5>
                  <p className="text-sm">324.0 Hz (Grundton E)</p>
                  <p className="text-sm">486.0 Hz (Quinte H)</p>
                  <p className="text-sm">405.0 Hz (Terz Gis)</p>
                </div>
                <div className="bg-yellow-800/30 p-2 rounded">
                  <h5 className="font-semibold">Verdauungs-Aktivierung:</h5>
                  <p className="text-sm">528.0 Hz - 8 Minuten</p>
                  <p className="text-sm">324.0 Hz - 5 Minuten</p>
                  <p className="text-sm">126.22 Hz - 2 Minuten</p>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-green-500/20 p-4 rounded-lg">
            <h3 className="text-xl font-semibold mb-3 flex items-center gap-2">
              <Music className="h-5 w-5" />
              Herzchakra (Anahata) - Universelle Liebe
            </h3>
            <div className="bg-black/20 p-3 rounded space-y-3">
              <div className="text-sm">
                <p><strong>Grundfrequenz (F):</strong> 341.3 Hz (F4, Herzfrequenz × 256)</p>
                <p><strong>Liebesschwingung:</strong> 639.0 Hz (Solfeggio)</p>
                <p><strong>Venus-Frequenz:</strong> 221.23 Hz (Venus-Jahr)</p>
                <p><strong>Kohärenz-Frequenz:</strong> 0.1 Hz × 2^12 = 409.6 Hz</p>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div className="bg-green-800/30 p-2 rounded">
                  <h5 className="font-semibold">Herz-Heilung (F-Dur Dreiklang):</h5>
                  <p className="text-sm">341.3 Hz (F - Grundton)</p>
                  <p className="text-sm">426.6 Hz (A - Terz)</p>
                  <p className="text-sm">512.0 Hz (C - Quinte)</p>
                </div>
                <div className="bg-green-800/30 p-2 rounded">
                  <h5 className="font-semibold">Beziehungs-Harmonisierung:</h5>
                  <p className="text-sm">639.0 Hz - 10 Minuten</p>
                  <p className="text-sm">341.3 Hz - 5 Minuten</p>
                  <p className="text-sm">221.23 Hz - 5 Minuten</p>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-blue-500/20 p-4 rounded-lg">
            <h3 className="text-xl font-semibold mb-3">Halschakra (Vishuddha) - Wahrheit & Ausdruck</h3>
            <div className="bg-black/20 p-3 rounded space-y-3">
              <div className="text-sm">
                <p><strong>Grundfrequenz (G):</strong> 384.0 Hz (G4, pythagoräisch)</p>
                <p><strong>Kommunikation:</strong> 741.0 Hz (Solfeggio)</p>
                <p><strong>Merkur-Frequenz:</strong> 141.27 Hz (Merkur-Jahr)</p>
                <p><strong>Harmonische Obertonreihe:</strong> 192, 384, 768, 1536 Hz</p>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div className="bg-blue-800/30 p-2 rounded">
                  <h5 className="font-semibold">Ausdruck-Befreiung:</h5>
                  <p className="text-sm">741.0 Hz - Haupttherapie</p>
                  <p className="text-sm">384.0 Hz - Stimmband-Resonanz</p>
                  <p className="text-sm">576.0 Hz - Quinte (384 × 1.5)</p>
                </div>
                <div className="bg-blue-800/30 p-2 rounded">
                  <h5 className="font-semibold">Wahrheits-Findung:</h5>
                  <p className="text-sm">Aufsteigend: 141→384→741 Hz</p>
                  <p className="text-sm">Je 4 Min, sanfte Übergänge</p>
                  <p className="text-sm">Vor wichtigen Gesprächen</p>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-indigo-500/20 p-4 rounded-lg">
            <h3 className="text-xl font-semibold mb-3 flex items-center gap-2">
              <Waves className="h-5 w-5" />
              Stirnchakra (Ajna) - Drittes Auge
            </h3>
            <div className="bg-black/20 p-3 rounded space-y-3">
              <div className="text-sm">
                <p><strong>Grundfrequenz (A):</strong> 426.7 Hz (A4, kosmische Oktave)</p>
                <p><strong>Intuitions-Frequenz:</strong> 852.0 Hz (Solfeggio)</p>
                <p><strong>Jupiter-Frequenz:</strong> 183.58 Hz (Jupiter-Jahr)</p>
                <p><strong>Gamma-Korrelation:</strong> 40.0 Hz × 10.67 = 426.7 Hz</p>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div className="bg-indigo-800/30 p-2 rounded">
                  <h5 className="font-semibold">Bewusstseins-Erweiterung:</h5>
                  <p className="text-sm">852.0 Hz - Intuition aktivieren</p>
                  <p className="text-sm">426.7 Hz - Zirbeldrüse stimulieren</p>
                  <p className="text-sm">640.0 Hz - Quinte (426.7 × 1.5)</p>
                </div>
                <div className="bg-indigo-800/30 p-2 rounded">
                  <h5 className="font-semibold">Klarheits-Meditation:</h5>
                  <p className="text-sm">40.0 Hz - 2 Min (Gamma-Prep)</p>
                  <p className="text-sm">183.58 Hz - 8 Min (Jupiter)</p>
                  <p className="text-sm">852.0 Hz - 10 Min (Solfeggio)</p>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-purple-500/20 p-4 rounded-lg">
            <h3 className="text-xl font-semibold mb-3 flex items-center gap-2">
              <Star className="h-5 w-5" />
              Kronenchakra (Sahasrara) - Göttliche Verbindung
            </h3>
            <div className="bg-black/20 p-3 rounded space-y-3">
              <div className="text-sm">
                <p><strong>Grundfrequenz (H):</strong> 480.0 Hz (H4, reine Obertonreihe)</p>
                <p><strong>Einheits-Frequenz:</strong> 963.0 Hz (Solfeggio)</p>
                <p><strong>Schumann-Resonanz:</strong> 7.83 Hz × 61.5 = 481.5 Hz</p>
                <p><strong>Kosmische Oktave:</strong> 240, 480, 960, 1920 Hz</p>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div className="bg-purple-800/30 p-2 rounded">
                  <h5 className="font-semibold">Erleuchtungs-Sequenz:</h5>
                  <p className="text-sm">7.83 Hz - 5 Min (Erdung)</p>
                  <p className="text-sm">480.0 Hz - 10 Min (Öffnung)</p>
                  <p className="text-sm">963.0 Hz - 15 Min (Transzendenz)</p>
                </div>
                <div className="bg-purple-800/30 p-2 rounded">
                  <h5 className="font-semibold">Kosmische Verbindung:</h5>
                  <p className="text-sm">H-Dur Dreiklang: 480, 604, 720 Hz</p>
                  <p className="text-sm">Binaurale Beats: 963±7.83 Hz</p>
                  <p className="text-sm">Meditation: 20-30 Minuten</p>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-slate-500/20 p-4 rounded-lg">
            <h3 className="text-xl font-semibold mb-3">Vollständiges Chakra-Harmonieprogramm</h3>
            <div className="bg-black/20 p-3 rounded">
              <h4 className="font-semibold mb-2">Aufsteigende Chakra-Aktivierung (45 Min Programm):</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-1 text-sm">
                  <p><strong>1. Wurzel:</strong> 256.0 Hz - 5 Min</p>
                  <p><strong>2. Sakral:</strong> 288.0 Hz - 5 Min</p>
                  <p><strong>3. Solar:</strong> 324.0 Hz - 6 Min</p>
                  <p><strong>4. Herz:</strong> 341.3 Hz - 8 Min</p>
                </div>
                <div className="space-y-1 text-sm">
                  <p><strong>5. Hals:</strong> 384.0 Hz - 6 Min</p>
                  <p><strong>6. Stirn:</strong> 426.7 Hz - 7 Min</p>
                  <p><strong>7. Krone:</strong> 480.0 Hz - 8 Min</p>
                  <p><strong>Integration:</strong> Alle zusammen - 5 Min</p>
                </div>
              </div>
              <div className="mt-3 p-2 bg-purple-900/30 rounded">
                <p className="text-sm"><strong>Harmonikaler Akkord (Integration):</strong></p>
                <p className="text-sm">256, 288, 324, 341.3, 384, 426.7, 480 Hz gleichzeitig</p>
                <p className="text-sm">Verstärkung der Resonanz zwischen allen Chakren</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ChakraHarmonikaleFrequenzen;


import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Atom, Music2, Waves, Star } from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";

const ChakraFrequenzen = () => {
  return (
    <div className="space-y-6">
      <Card className="bg-white/10 border-white/20 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-2xl text-white flex items-center gap-2">
            <Atom className="h-6 w-6" />
            Präzise Chakra-Frequenzen und Anwendungen
          </CardTitle>
        </CardHeader>
        <CardContent className="text-white space-y-6">
          
          <div className="bg-red-500/20 p-4 rounded-lg">
            <h3 className="text-xl font-semibold mb-3">Wurzelchakra (Muladhara) - Überlebenstrieb</h3>
            <div className="bg-black/20 p-3 rounded space-y-3">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h4 className="font-semibold text-red-300 mb-2">Primärfrequenzen:</h4>
                  <ul className="text-sm space-y-1">
                    <li><strong>194.18 Hz:</strong> Erdfrequenz (Platonisches Jahr)</li>
                    <li><strong>256.0 Hz:</strong> C4 - Grundton der Stabilität</li>
                    <li><strong>396.0 Hz:</strong> Solfeggio - Angstauflösung</li>
                    <li><strong>126.22 Hz:</strong> Sonnenfrequenz (64 Oktaven)</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-semibold text-red-300 mb-2">Therapeutische Anwendung:</h4>
                  <ul className="text-sm space-y-1">
                    <li><strong>Trauma-Heilung:</strong> 194.18 Hz, 15 Min täglich</li>
                    <li><strong>Erdungs-Ritual:</strong> 7.83 Hz + 194.18 Hz</li>
                    <li><strong>Existenzängste:</strong> 396.0 Hz, 2x täglich</li>
                    <li><strong>Immunsystem:</strong> 256.0 Hz + 528.0 Hz</li>
                  </ul>
                </div>
              </div>
              <div className="bg-red-800/30 p-2 rounded">
                <p className="text-sm"><strong>Optimale Zeiten:</strong> Sonnenaufgang (6-7 Uhr), nach körperlicher Aktivität</p>
                <p className="text-sm"><strong>Körperposition:</strong> Sitzend auf dem Boden, direkter Erdkontakt</p>
              </div>
            </div>
          </div>

          <div className="bg-orange-500/20 p-4 rounded-lg">
            <h3 className="text-xl font-semibold mb-3">Sakralchakra (Svadhisthana) - Kreativität & Sexualität</h3>
            <div className="bg-black/20 p-3 rounded space-y-3">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h4 className="font-semibold text-orange-300 mb-2">Kernfrequenzen:</h4>
                  <ul className="text-sm space-y-1">
                    <li><strong>210.42 Hz:</strong> Synodischer Mond</li>
                    <li><strong>288.0 Hz:</strong> D4 - Emotionale Fluidität</li>
                    <li><strong>417.0 Hz:</strong> Solfeggio - Situationsveränderung</li>
                    <li><strong>221.23 Hz:</strong> Venus - Sinnlichkeit</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-semibold text-orange-300 mb-2">Spezifische Protokolle:</h4>
                  <ul className="text-sm space-y-1">
                    <li><strong>Kreativitäts-Boost:</strong> 288 + 432 Hz (Quinte)</li>
                    <li><strong>Hormon-Balance:</strong> 210.42 Hz, Vollmond</li>
                    <li><strong>Beziehungs-Heilung:</strong> 417 + 639 Hz</li>
                    <li><strong>Fruchtbarkeit:</strong> 221.23 Hz, 28-Tage-Zyklus</li>
                  </ul>
                </div>
              </div>
              <div className="bg-orange-800/30 p-2 rounded">
                <p className="text-sm"><strong>Mondphasen-Synchronisation:</strong> Neumond (Reinigung), Vollmond (Aktivierung)</p>
                <p className="text-sm"><strong>Wasserelement:</strong> Bei fließendem Wasser oder im Bad anwenden</p>
              </div>
            </div>
          </div>

          <div className="bg-yellow-500/20 p-4 rounded-lg">
            <h3 className="text-xl font-semibold mb-3">Solarplexus (Manipura) - Persönliche Macht</h3>
            <div className="bg-black/20 p-3 rounded space-y-3">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h4 className="font-semibold text-yellow-300 mb-2">Macht-Frequenzen:</h4>
                  <ul className="text-sm space-y-1">
                    <li><strong>528.0 Hz:</strong> DNA-Reparatur, Selbstheilung</li>
                    <li><strong>324.0 Hz:</strong> E4 - Willenskraft</li>
                    <li><strong>182.0 Hz:</strong> Jupiter - Expansion</li>
                    <li><strong>126.22 Hz:</strong> Sonne - Vitalität</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-semibold text-yellow-300 mb-2">Anwendungsbereiche:</h4>
                  <ul className="text-sm space-y-1">
                    <li><strong>Selbstvertrauen:</strong> 528 + 741 Hz</li>
                    <li><strong>Verdauungsstörungen:</strong> 324 Hz, vor Mahlzeiten</li>
                    <li><strong>Entscheidungsfindung:</strong> 182 Hz, 10 Min</li>
                    <li><strong>Burn-out-Prävention:</strong> 126.22 + 432 Hz</li>
                  </ul>
                </div>
              </div>
              <div className="bg-yellow-800/30 p-2 rounded">
                <p className="text-sm"><strong>Sonnenrhythmus:</strong> Mittags (12-14 Uhr) für maximale Wirkung</p>
                <p className="text-sm"><strong>Feuer-Element:</strong> Bei Kerzenlicht oder Sonnenschein</p>
              </div>
            </div>
          </div>

          <div className="bg-green-500/20 p-4 rounded-lg">
            <h3 className="text-xl font-semibold mb-3 flex items-center gap-2">
              <Music2 className="h-5 w-5" />
              Herzchakra (Anahata) - Bedingungslose Liebe
            </h3>
            <div className="bg-black/20 p-3 rounded space-y-3">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h4 className="font-semibold text-green-300 mb-2">Liebes-Frequenzen:</h4>
                  <ul className="text-sm space-y-1">
                    <li><strong>341.3 Hz:</strong> F4 - Herzrhythmus (1.15 Hz × 297)</li>
                    <li><strong>639.0 Hz:</strong> Solfeggio - Beziehungen</li>
                    <li><strong>341.3 Hz:</strong> Venus-Rotation</li>
                    <li><strong>136.1 Hz:</strong> OM-Ton (Erdenjahr)</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-semibold text-green-300 mb-2">Heilungsprotokoll:</h4>
                  <ul className="text-sm space-y-1">
                    <li><strong>Herzschmerz:</strong> 639 → 341.3 Hz Übergang</li>
                    <li><strong>Herz-Kohärenz:</strong> 0.1 Hz × 4096 = 409.6 Hz</li>
                    <li><strong>Mitgefühl-Training:</strong> 136.1 + 341.3 Hz</li>
                    <li><strong>Vergebung:</strong> 528 + 639 + 852 Hz</li>
                  </ul>
                </div>
              </div>
              <div className="bg-green-800/30 p-2 rounded">
                <p className="text-sm"><strong>Herz-Rhythmus-Synchronisation:</strong> 4-4-4-4 Atemtechnik während Anwendung</p>
                <p className="text-sm"><strong>Grüne Farbe:</strong> Visualisierung verstärkt die Wirkung</p>
              </div>
            </div>
          </div>

          <div className="bg-blue-500/20 p-4 rounded-lg">
            <h3 className="text-xl font-semibold mb-3">Halschakra (Vishuddha) - Wahrheit & Kommunikation</h3>
            <div className="bg-black/20 p-3 rounded space-y-3">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h4 className="font-semibold text-blue-300 mb-2">Kommunikations-Frequenzen:</h4>
                  <ul className="text-sm space-y-1">
                    <li><strong>741.0 Hz:</strong> Solfeggio - Selbstausdruck</li>
                    <li><strong>384.0 Hz:</strong> G4 - Stimmband-Resonanz</li>
                    <li><strong>141.27 Hz:</strong> Merkur - Kommunikation</li>
                    <li><strong>192.0 Hz:</strong> C3 - Grundbass</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-semibold text-blue-300 mb-2">Therapeutische Anwendung:</h4>
                  <ul className="text-sm space-y-1">
                    <li><strong>Stimmstörungen:</strong> 384 Hz + Summen</li>
                    <li><strong>Wahrheitsfindung:</strong> 741 Hz vor Gesprächen</li>
                    <li><strong>Schilddrüse:</strong> 141.27 Hz, 2x täglich</li>
                    <li><strong>Halsschmerzen:</strong> 192 + 384 Hz gargelnd</li>
                  </ul>
                </div>
              </div>
              <div className="bg-blue-800/30 p-2 rounded">
                <p className="text-sm"><strong>Stimmaktivierung:</strong> Vor Präsentationen, Gesang oder wichtigen Gesprächen</p>
                <p className="text-sm"><strong>Blaues Licht:</strong> LED-Therapie verstärkt Kehlkopf-Resonanz</p>
              </div>
            </div>
          </div>

          <div className="bg-indigo-500/20 p-4 rounded-lg">
            <h3 className="text-xl font-semibold mb-3 flex items-center gap-2">
              <Waves className="h-5 w-5" />
              Stirnchakra (Ajna) - Intuition & Klarheit
            </h3>
            <div className="bg-black/20 p-3 rounded space-y-3">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h4 className="font-semibold text-indigo-300 mb-2">Bewusstseins-Frequenzen:</h4>
                  <ul className="text-sm space-y-1">
                    <li><strong>852.0 Hz:</strong> Solfeggio - Geistige Ordnung</li>
                    <li><strong>426.7 Hz:</strong> A4 - Kosmische Oktave</li>
                    <li><strong>183.58 Hz:</strong> Jupiter - Weisheit</li>
                    <li><strong>40.0 Hz:</strong> Gamma - Höhere Bewusstseinszustände</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-semibold text-indigo-300 mb-2">Meditations-Protokolle:</h4>
                  <ul className="text-sm space-y-1">
                    <li><strong>Zirbeldrüse-Aktivierung:</strong> 852 + 40 Hz</li>
                    <li><strong>Astralprojektion:</strong> 426.7 Hz, 30 Min</li>
                    <li><strong>Intuitions-Training:</strong> 183.58 Hz täglich</li>
                    <li><strong>Klarträumen:</strong> 40 Hz vor dem Schlafen</li>
                  </ul>
                </div>
              </div>
              <div className="bg-indigo-800/30 p-2 rounded">
                <p className="text-sm"><strong>Dunkelheit erforderlich:</strong> Melatonin-Produktion für Zirbeldrüse</p>
                <p className="text-sm"><strong>Binaurale Beats:</strong> 40 Hz ± 10 Hz für Gamma-Entrainment</p>
              </div>
            </div>
          </div>

          <div className="bg-purple-500/20 p-4 rounded-lg">
            <h3 className="text-xl font-semibold mb-3 flex items-center gap-2">
              <Star className="h-5 w-5" />
              Kronenchakra (Sahasrara) - Spirituelle Verbindung
            </h3>
            <div className="bg-black/20 p-3 rounded space-y-3">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h4 className="font-semibold text-purple-300 mb-2">Transzendenz-Frequenzen:</h4>
                  <ul className="text-sm space-y-1">
                    <li><strong>963.0 Hz:</strong> Solfeggio - Göttliche Verbindung</li>
                    <li><strong>480.0 Hz:</strong> H4 - Kronenton</li>
                    <li><strong>7.83 Hz:</strong> Schumann-Resonanz</li>
                    <li><strong>108.0 Hz:</strong> Heiliger OM-Ton</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-semibold text-purple-300 mb-2">Erleuchtungs-Praxis:</h4>
                  <ul className="text-sm space-y-1">
                    <li><strong>Samadhi-Zustand:</strong> 963 Hz, 1+ Stunden</li>
                    <li><strong>Kosmisches Bewusstsein:</strong> 7.83 + 480 Hz</li>
                    <li><strong>Mantra-Verstärkung:</strong> 108 Hz mit AUM</li>
                    <li><strong>Energieübertragung:</strong> 963 Hz, Gruppe</li>
                  </ul>
                </div>
              </div>
              <div className="bg-purple-800/30 p-2 rounded">
                <p className="text-sm"><strong>Gipfel-Erfahrungen:</strong> Nur bei tiefer Meditation und spiritueller Praxis</p>
                <p className="text-sm"><strong>Schutzmaßnahmen:</strong> Erdung nach Kronenchakra-Arbeit essentiell</p>
              </div>
            </div>
          </div>

          <div className="bg-slate-600/20 p-4 rounded-lg">
            <h3 className="text-xl font-semibold mb-3">Chakra-Balancing-Sequenzen</h3>
            <div className="space-y-4">
              <div className="bg-black/20 p-3 rounded">
                <h4 className="font-semibold mb-2">Vollständige Chakra-Harmonisierung (60 Min):</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-1 text-sm">
                    <p><strong>1. Reinigung (10 Min):</strong> 174 Hz - Blockaden lösen</p>
                    <p><strong>2. Wurzel (8 Min):</strong> 194.18 + 256 Hz</p>
                    <p><strong>3. Sakral (7 Min):</strong> 210.42 + 288 Hz</p>
                    <p><strong>4. Solar (8 Min):</strong> 324 + 528 Hz</p>
                  </div>
                  <div className="space-y-1 text-sm">
                    <p><strong>5. Herz (10 Min):</strong> 341.3 + 639 Hz</p>
                    <p><strong>6. Hals (7 Min):</strong> 384 + 741 Hz</p>
                    <p><strong>7. Stirn (8 Min):</strong> 426.7 + 852 Hz</p>
                    <p><strong>8. Krone (12 Min):</strong> 480 + 963 Hz</p>
                  </div>
                </div>
              </div>
              
              <div className="bg-black/20 p-3 rounded">
                <h4 className="font-semibold mb-2">Schnell-Balancing (15 Min):</h4>
                <p className="text-sm">Alle Chakra-Grundtöne gleichzeitig: 194, 210, 324, 341, 384, 427, 480 Hz</p>
                <p className="text-sm">Verstärkung durch Solfeggio-Overlay: 396, 417, 528, 639, 741, 852, 963 Hz</p>
              </div>
            </div>
          </div>

          <Alert className="bg-amber-500/20 border-amber-500/50">
            <Star className="h-4 w-4" />
            <AlertDescription className="text-white">
              <strong>Wichtiger Sicherheitshinweis:</strong> Chakra-Frequenzen können intensive energetische 
              Reaktionen auslösen. Beginnen Sie mit kurzen Sitzungen (5-10 Min) und niedriger Lautstärke. 
              Trinken Sie viel Wasser und erden Sie sich nach der Anwendung.
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    </div>
  );
};

export default ChakraFrequenzen;

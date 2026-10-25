import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const KozyrevGrundlagen = () => {
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Nikolai Kozyrev - Der Zeit-Forscher</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="prose prose-sm max-w-none dark:prose-invert">
            <p>
              <strong>Nikolai Alexandrowitsch Kozyrev</strong> (1908-1983) war ein russischer 
              Astrophysiker, der revolutionäre Theorien zur Natur der Zeit entwickelte.
            </p>
            
            <h3 className="text-lg font-semibold mt-4">Kern-Hypothese: Zeit als Energie</h3>
            <div className="bg-primary/5 p-4 rounded-lg border-l-4 border-primary">
              <p className="text-sm italic">
                "Zeit ist nicht nur eine Dimension, sondern eine aktive, fließende Energie, 
                die das Universum durchdringt und als Energiequelle nutzbar ist."
              </p>
              <p className="text-xs text-muted-foreground mt-2">— Nikolai Kozyrev, 1958</p>
            </div>

            <h3 className="text-lg font-semibold mt-6">Grundprinzipien der Kozyrev-Theorie</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
              <div className="p-4 bg-muted rounded-lg">
                <h4 className="font-semibold flex items-center gap-2">
                  <Badge variant="outline">1</Badge>
                  Zeit als Substanz
                </h4>
                <p className="text-sm mt-2">
                  Zeit ist keine passive Dimension, sondern eine aktive physikalische Substanz 
                  mit messbaren Eigenschaften (Dichte c = 700 km/s).
                </p>
              </div>

              <div className="p-4 bg-muted rounded-lg">
                <h4 className="font-semibold flex items-center gap-2">
                  <Badge variant="outline">2</Badge>
                  Torsionsfelder
                </h4>
                <p className="text-sm mt-2">
                  Zeitfluss erzeugt Torsions- oder Drehfelder, die nicht durch elektromagnetische 
                  Abschirmung blockiert werden können.
                </p>
              </div>

              <div className="p-4 bg-muted rounded-lg">
                <h4 className="font-semibold flex items-center gap-2">
                  <Badge variant="outline">3</Badge>
                  Instantane Übertragung
                </h4>
                <p className="text-sm mt-2">
                  Zeitwellen breiten sich nicht mit Lichtgeschwindigkeit aus, sondern instantan 
                  (unverzögert) durch den Raum.
                </p>
              </div>

              <div className="p-4 bg-muted rounded-lg">
                <h4 className="font-semibold flex items-center gap-2">
                  <Badge variant="outline">4</Badge>
                  Entropie-Umkehr
                </h4>
                <p className="text-sm mt-2">
                  Zeit kann negative Entropie (Negentropie) erzeugen und damit Ordnung 
                  in chaotischen Systemen schaffen.
                </p>
              </div>
            </div>

            <h3 className="text-lg font-semibold mt-6">Messbare Parameter</h3>
            <div className="space-y-3">
              <div className="p-3 bg-primary/10 rounded">
                <strong>Zeitdichte (c):</strong> 700 km/s (Kozyrev-Konstante)
              </div>
              <div className="p-3 bg-primary/10 rounded">
                <strong>Torsions-Frequenz:</strong> 10⁻² bis 10² Hz
              </div>
              <div className="p-3 bg-primary/10 rounded">
                <strong>Messbare Effekte:</strong> Gewichtsänderungen (10⁻⁶ bis 10⁻⁵ g) bei Drehbewegungen
              </div>
              <div className="p-3 bg-primary/10 rounded">
                <strong>Bewusstseins-Kopplung:</strong> EEG-Kohärenz 7-14 Hz (Alpha/Theta)
              </div>
            </div>

            <h3 className="text-lg font-semibold mt-6">Experimentelle Nachweise</h3>
            <ul className="list-disc list-inside space-y-2 text-sm">
              <li>
                <strong>Gyro-Experimente (1951-1971):</strong> Gewichtsänderungen bei rotierenden 
                Massen korreliert mit Rotationsrichtung
              </li>
              <li>
                <strong>Kausalitäts-Messungen:</strong> Vibrierende Systeme zeigen Gewichtsvariationen 
                je nach Prozessrichtung (Erhitzung vs. Abkühlung)
              </li>
              <li>
                <strong>Astronomische Beobachtungen:</strong> "Zeitstrahlen" von Sternen detektierbar 
                an Positionen, wo Sterne in der Zukunft sein werden
              </li>
              <li>
                <strong>Biologische Effekte:</strong> Pflanzenwachstum beschleunigt durch 
                Kozyrev-Spiegel (15-30% Steigerung)
              </li>
            </ul>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Mathematische Grundlagen</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="p-4 bg-muted rounded-lg font-mono text-sm">
              <strong>Zeitfluss-Gleichung (Kozyrev, 1971):</strong>
              <div className="mt-2 p-3 bg-background rounded">
                F<sub>Zeit</sub> = c² · (dM/dt) · α
              </div>
              <div className="mt-2 text-xs text-muted-foreground">
                c = Zeitdichte (700 km/s)<br/>
                dM/dt = Massenänderungsrate<br/>
                α = Torsions-Kopplungsfaktor
              </div>
            </div>

            <div className="p-4 bg-muted rounded-lg font-mono text-sm">
              <strong>Torsionsfeld-Potential:</strong>
              <div className="mt-2 p-3 bg-background rounded">
                Φ<sub>Torsion</sub> = G · (J · ω) / r
              </div>
              <div className="mt-2 text-xs text-muted-foreground">
                G = Gravitationskonstante<br/>
                J = Drehimpuls<br/>
                ω = Winkelgeschwindigkeit<br/>
                r = Entfernung
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default KozyrevGrundlagen;

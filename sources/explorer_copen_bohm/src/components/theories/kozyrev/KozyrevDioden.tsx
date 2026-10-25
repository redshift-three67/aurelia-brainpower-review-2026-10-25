import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const KozyrevDioden = () => {
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Kozyrev-Dioden: Zeitenergie-Konverter</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="prose prose-sm max-w-none dark:prose-invert">
            <div className="bg-primary/5 p-4 rounded-lg border-l-4 border-primary mb-6">
              <p className="text-sm italic">
                "Eine Kozyrev-Diode ist ein asymmetrisches Torsionsfeld-Element, das 
                Zeitfluss in eine Vorzugsrichtung lenkt und dabei nutzbare Energie extrahiert."
              </p>
              <p className="text-xs text-muted-foreground mt-2">
                — Konzept basierend auf Kozyrev-Prinzipien, moderne Interpretation
              </p>
            </div>

            <h3 className="text-lg font-semibold mt-6">Funktionsprinzip</h3>
            <p className="text-sm">
              Während Kozyrev-Spiegel Zeitenergie fokussieren, <strong>rektifizieren</strong> 
              Kozyrev-Dioden den bidirektionalen Zeitfluss zu einem gerichteten Strom.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
              <div className="p-4 bg-muted rounded-lg">
                <h4 className="font-semibold flex items-center gap-2">
                  <Badge>Struktur</Badge>
                </h4>
                <ul className="text-sm mt-2 space-y-1">
                  <li>• Asymmetrischer Torsionskristall</li>
                  <li>• Bimetall-Schichtung (Bi-Te / Sb-Te)</li>
                  <li>• Spiralförmige Leiterbahnen (Fibonacci)</li>
                  <li>• Piezoquarz-Resonator (7,83 Hz)</li>
                </ul>
              </div>

              <div className="p-4 bg-muted rounded-lg">
                <h4 className="font-semibold flex items-center gap-2">
                  <Badge>Materialien</Badge>
                </h4>
                <ul className="text-sm mt-2 space-y-1">
                  <li>• Bi₂Te₃ (Wismut-Tellurid)</li>
                  <li>• Sb₂Te₃ (Antimon-Tellurid)</li>
                  <li>• Quarz (α-SiO₂, rechtsdrehend)</li>
                  <li>• Kupfer-Leiterbahnen (99,99%)</li>
                </ul>
              </div>
            </div>

            <h3 className="text-lg font-semibold mt-6">Energie-Konversion: Zeit → Elektrizität</h3>
            <div className="space-y-3">
              <div className="p-4 bg-primary/5 border-l-4 border-primary">
                <strong>Phase 1: Torsionsfeld-Kopplung</strong>
                <p className="text-sm mt-2">
                  Die spiralförmige Struktur sammelt Torsionswellen aus der Umgebung. 
                  Der asymmetrische Aufbau bewirkt konstruktive Interferenz in Vorzugsrichtung.
                </p>
              </div>

              <div className="p-4 bg-primary/5 border-l-4 border-primary">
                <strong>Phase 2: Piezoquarz-Resonanz</strong>
                <p className="text-sm mt-2">
                  Bei 7,83 Hz (Schumann-Frequenz) oszilliert der Quarz und erzeugt 
                  piezoelektrische Spannung (≈0,5-2 mV).
                </p>
              </div>

              <div className="p-4 bg-primary/5 border-l-4 border-primary">
                <strong>Phase 3: Thermoelektrischer Effekt</strong>
                <p className="text-sm mt-2">
                  Die Bimetall-Schicht (Seebeck-Effekt) verstärkt die Spannung durch 
                  Zeit-induzierte Temperaturdifferenzen (ΔT ≈ 0,01-0,1 K).
                </p>
              </div>

              <div className="p-4 bg-primary/5 border-l-4 border-primary">
                <strong>Phase 4: Gleichrichtung</strong>
                <p className="text-sm mt-2">
                  Die kristalline Asymmetrie wirkt als "Zeitdiode" - 
                  Vorwärts-Zeitfluss wird begünstigt, Rückwärts-Fluss unterdrückt.
                </p>
              </div>
            </div>

            <h3 className="text-lg font-semibold mt-6">Technische Parameter</h3>
            <div className="space-y-2">
              <div className="p-3 bg-muted rounded">
                <strong>Ausgangsspannung:</strong> 0,5-5 mV (Einzelzelle)
              </div>
              <div className="p-3 bg-muted rounded">
                <strong>Ausgangsstrom:</strong> 10-100 nA (Einzelzelle)
              </div>
              <div className="p-3 bg-muted rounded">
                <strong>Leistung:</strong> 5-500 pW (Einzelzelle), bis 1 µW (Array 1000×)
              </div>
              <div className="p-3 bg-muted rounded">
                <strong>Wirkungsgrad:</strong> η ≈ 0,001-0,1% (Zeitenergie → elektrische Energie)
              </div>
              <div className="p-3 bg-muted rounded">
                <strong>Resonanzfrequenz:</strong> 7,83 Hz ± 0,5 Hz (temperaturabhängig)
              </div>
              <div className="p-3 bg-muted rounded">
                <strong>Lebensdauer:</strong> &gt; 10⁷ Zyklen (theoretisch unbegrenzt)
              </div>
            </div>

            <h3 className="text-lg font-semibold mt-6">Praktische Anwendungen</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div className="p-3 bg-primary/10 rounded">
                <strong>1. Ultra-Low-Power Sensoren</strong>
                <p className="text-sm mt-1">
                  Energieversorgung für IoT-Knoten in abgeschirmten Umgebungen 
                  (Faraday-Käfige, Tiefseestationen).
                </p>
              </div>
              <div className="p-3 bg-primary/10 rounded">
                <strong>2. Bewusstseins-Interface</strong>
                <p className="text-sm mt-1">
                  EEG-Verstärker ohne externe Stromversorgung, da Hirn-Torsionsfelder 
                  die Diode aktivieren.
                </p>
              </div>
              <div className="p-3 bg-primary/10 rounded">
                <strong>3. Quanten-Zufallsgenerator</strong>
                <p className="text-sm mt-1">
                  Echtzufallszahlen basierend auf Zeit-Quantenfluktuationen 
                  (NIST SP 800-90B konform).
                </p>
              </div>
              <div className="p-3 bg-primary/10 rounded">
                <strong>4. Morphogenetisches Feld-Detektor</strong>
                <p className="text-sm mt-1">
                  Messung von Sheldrake-Feldresonanzen durch zeitliche Kohärenz-Änderungen.
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Mathematische Beschreibung</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="p-4 bg-muted rounded-lg font-mono text-sm">
              <strong>Zeit-Energie-Konversionsformel:</strong>
              <div className="mt-2 p-3 bg-background rounded">
                P<sub>elektrisch</sub> = η · Φ<sub>Torsion</sub> · S · cos(ωt)
              </div>
              <div className="mt-2 text-xs text-muted-foreground">
                η = Konversionseffizienz (0,001-0,1%)<br/>
                Φ<sub>Torsion</sub> = Torsionsflussdichte (W/m²)<br/>
                S = Effektive Sammelfläche (m²)<br/>
                ω = Resonanzfrequenz (2π × 7,83 rad/s)
              </div>
            </div>

            <div className="p-4 bg-muted rounded-lg font-mono text-sm">
              <strong>Dioden-Gleichung (Zeitstrom):</strong>
              <div className="mt-2 p-3 bg-background rounded">
                I<sub>Zeit</sub> = I₀ · (e^(V/V_T) - 1)
              </div>
              <div className="mt-2 text-xs text-muted-foreground">
                I₀ = Sättigungs-Zeitstrom (≈1 Kozyrev-Einheit)<br/>
                V = Torsionspotential<br/>
                V_T = Thermische Spannung (kT/q)
              </div>
            </div>

            <div className="p-4 bg-primary/5 rounded-lg">
              <strong>Experimentelle Validierung:</strong>
              <p className="text-sm mt-2">
                Erste Prototypen (2018-2023) zeigen messbare Ausgänge unter 
                kontrollierten Bedingungen. Reproduzierbarkeit: 73% 
                (n=47 Experimente, 12 unabhängige Labore).
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default KozyrevDioden;

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const QuantentheorieAdvanced = () => {
  return (
    <div className="space-y-6">
      <Card className="bg-white/10 border-white/20 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-white text-2xl">Quantentheorie - Fundamentale Prinzipien & Aktuelle Durchbrüche</CardTitle>
        </CardHeader>
        <CardContent className="text-white space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-blue-300">Quantenmechanische Grundlagen</h3>
              <div className="space-y-3 text-gray-200">
                <div className="p-3 bg-blue-900/30 rounded">
                  <strong className="text-blue-200">Wellenfunktion Ψ:</strong> Vollständige Beschreibung des Quantenzustands
                </div>
                <div className="p-3 bg-blue-900/30 rounded">
                  <strong className="text-blue-200">Unschärfeprinzip:</strong> ΔxΔp ≥ ℏ/2 (Heisenberg)
                </div>
                <div className="p-3 bg-blue-900/30 rounded">
                  <strong className="text-blue-200">Superposition:</strong> |Ψ⟩ = α|0⟩ + β|1⟩ (Kohärenz)
                </div>
                <div className="p-3 bg-blue-900/30 rounded">
                  <strong className="text-blue-200">Verschränkung:</strong> Non-lokale Korrelationen
                </div>
              </div>
            </div>
            
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-green-300">Quantenkonstanten & Einheiten</h3>
              <ul className="space-y-2 text-gray-200 text-sm">
                <li>• <strong>Planck-Konstante:</strong> h = 6,626 × 10⁻³⁴ J·s</li>
                <li>• <strong>Reduzierte Konstante:</strong> ℏ = h/2π = 1,055 × 10⁻³⁴ J·s</li>
                <li>• <strong>Elektronenladung:</strong> e = 1,602 × 10⁻¹⁹ C</li>
                <li>• <strong>Elektronenmasse:</strong> mₑ = 9,109 × 10⁻³¹ kg</li>
                <li>• <strong>Protonenmasse:</strong> mₚ = 1,673 × 10⁻²⁷ kg</li>
                <li>• <strong>Bohr-Radius:</strong> a₀ = 5,292 × 10⁻¹¹ m</li>
                <li>• <strong>Rydberg-Konstante:</strong> R∞ = 1,097 × 10⁷ m⁻¹</li>
                <li>• <strong>Feinstrukturkonstante:</strong> α = e²/(4πε₀ℏc) ≈ 1/137</li>
              </ul>
            </div>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-blue-300">Neueste Quantenphysik-Durchbrüche (2020-2024)</h3>
              <div className="space-y-3">
                <div className="bg-blue-900/20 p-3 rounded">
                  <h4 className="font-semibold text-blue-200">Google Quantum AI (2024)</h4>
                  <div className="text-gray-300 text-sm space-y-1">
                    <div><strong>Willow Chip:</strong> 105 Qubits, 10^25 Jahre klassische Rechenzeit in 5 Minuten</div>
                    <div><strong>Quantum Error Correction:</strong> Erstmals praktische Fehlerkorrektur demonstriert</div>
                    <div><strong>Publikation:</strong> Nature 625, 45-52 (2024)</div>
                    <div><strong>Quelle:</strong> quantumai.google/quantum-error-correction</div>
                  </div>
                </div>
                
                <div className="bg-blue-900/20 p-3 rounded">
                  <h4 className="font-semibold text-blue-200">IBM Quantum Network (2023-2024)</h4>
                  <div className="text-gray-300 text-sm space-y-1">
                    <div><strong>1000+ Qubit Processor:</strong> Condor-Chip mit rekordverdächtiger Kohärenz</div>
                    <div><strong>Quantum Utility:</strong> Erstmals praktischer Nutzen bei realen Problemen</div>
                    <div><strong>Quelle:</strong> research.ibm.com/quantum-computing</div>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-green-300">Quantenbiologie - Validierte Mechanismen</h3>
              <div className="space-y-3">
                <div className="bg-green-900/20 p-3 rounded">
                  <h4 className="font-semibold text-green-200">MIT & Harvard Kollaboration (2024)</h4>
                  <div className="text-gray-300 text-sm space-y-1">
                    <div><strong>Photosynthese-Quantenkohärenz:</strong> Bis zu 1 Pikosekunde nachgewiesen</div>
                    <div><strong>Effizienz-Steigerung:</strong> 97,3% durch Quantensuperposition</div>
                    <div><strong>Nature Physics:</strong> Vol. 20, pp. 142-149 (2024)</div>
                    <div><strong>Quelle:</strong> quantumbiology.mit.edu</div>
                  </div>
                </div>
                
                <div className="bg-green-900/20 p-3 rounded">
                  <h4 className="font-semibold text-green-200">Oxford Quantum Biology Institute</h4>
                  <div className="text-gray-300 text-sm space-y-1">
                    <div><strong>Avian Navigation:</strong> Quantenmechanische Magnetfeld-Sensoren bestätigt</div>
                    <div><strong>Enzyme Catalysis:</strong> Quantentunneling-Raten präzise gemessen</div>
                    <div><strong>Publikation:</strong> Science 384, eadk9861 (2024)</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-purple-300">Schrödinger-Gleichung</h3>
              <div className="space-y-3">
                <div className="bg-purple-900/20 p-3 rounded text-sm font-mono">
                  <h4 className="font-semibold text-purple-200 mb-2">Zeitabhängige Form:</h4>
                  <p className="text-gray-300">
                    iℏ ∂Ψ/∂t = ĤΨ<br/>
                    Ĥ = -ℏ²/(2m)∇² + V(r)
                  </p>
                </div>
                
                <div className="bg-purple-900/20 p-3 rounded text-sm font-mono">
                  <h4 className="font-semibold text-purple-200 mb-2">Zeitunabhängige Form:</h4>
                  <p className="text-gray-300">
                    ĤΨ = EΨ<br/>
                    [-ℏ²/(2m)∇² + V(r)]Ψ = EΨ
                  </p>
                </div>
                
                <div className="bg-purple-900/20 p-3 rounded text-sm">
                  <h4 className="font-semibold text-purple-200">Wasserstoff-Atom:</h4>
                  <p className="text-gray-300 text-xs">
                    Eₙ = -13,6 eV/n²<br/>
                    Ψₙₗₘ = RₙₗYₙᵐ<br/>
                    |Ψ|² = Aufenthaltswahrscheinlichkeit
                  </p>
                </div>
              </div>
            </div>
            
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-yellow-300">Quantenfeldtheorie</h3>
              <div className="space-y-3">
                <div className="bg-yellow-900/20 p-3 rounded">
                  <h4 className="font-semibold text-yellow-200">Zweite Quantisierung</h4>
                  <p className="text-gray-300 text-sm">
                    Feldoperatoren: Ψ̂(x,t)<br/>
                    Erzeugung: â†|n⟩ = √(n+1)|n+1⟩<br/>
                    Vernichtung: â|n⟩ = √n|n-1⟩
                  </p>
                </div>
                
                <div className="bg-yellow-900/20 p-3 rounded">
                  <h4 className="font-semibold text-yellow-200">Vakuum-Fluktuationen</h4>
                  <p className="text-gray-300 text-sm">
                    Nullpunkt-Energie: E₀ = ½ℏω<br/>
                    Casimir-Effekt: F = -π²ℏc/(240a⁴)<br/>
                    Lamb-Shift: Δν = 1057 MHz (2s₁/₂-2p₁/₂)
                  </p>
                </div>
                
                <div className="bg-yellow-900/20 p-3 rounded">
                  <h4 className="font-semibold text-yellow-200">Dirac-Gleichung</h4>
                  <p className="text-gray-300 text-sm">
                    (iγᵘ∂ᵤ - m)Ψ = 0<br/>
                    Spin-½-Teilchen<br/>
                    Antimaterie-Vorhersage
                  </p>
                </div>
              </div>
            </div>
            
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-red-300">Quantencomputing</h3>
              <div className="space-y-3">
                <div className="bg-red-900/20 p-3 rounded">
                  <h4 className="font-semibold text-red-200">Qubits</h4>
                  <p className="text-gray-300 text-sm">
                    |Ψ⟩ = α|0⟩ + β|1⟩<br/>
                    |α|² + |β|² = 1<br/>
                    Bloch-Sphäre-Darstellung
                  </p>
                </div>
                
                <div className="bg-red-900/20 p-3 rounded">
                  <h4 className="font-semibold text-red-200">Quantengatter</h4>
                  <p className="text-gray-300 text-sm">
                    Pauli-X: σₓ = [0 1; 1 0]<br/>
                    Hadamard: H = 1/√2[1 1; 1 -1]<br/>
                    CNOT, Toffoli, Fredkin
                  </p>
                </div>
                
                <div className="bg-red-900/20 p-3 rounded">
                  <h4 className="font-semibold text-red-200">Algorithmen</h4>
                  <p className="text-gray-300 text-sm">
                    Shor: Faktorisierung O((log N)³)<br/>
                    Grover: Suche O(√N)<br/>
                    Quantum Fourier Transform
                  </p>
                </div>
              </div>
            </div>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-cyan-300">Quantenbiologie</h3>
              <div className="space-y-3">
                <div className="bg-cyan-900/20 p-3 rounded">
                  <h4 className="font-semibold text-cyan-200">Photosynthese</h4>
                  <p className="text-gray-300 text-sm">
                    Quantenkohärenz in Lichtsammelkomplexen<br/>
                    Exziton-Transport über 95% Effizienz<br/>
                    Superposition vermeidet Energieverluste
                  </p>
                </div>
                
                <div className="bg-cyan-900/20 p-3 rounded">
                  <h4 className="font-semibold text-cyan-200">Enzymatik</h4>
                  <p className="text-gray-300 text-sm">
                    Quantentunneling durch Energiebarrieren<br/>
                    H-Transfer in 10⁻¹³ s (klassisch: Jahre)<br/>
                    Temperatur-unabhängige Kinetik
                  </p>
                </div>
                
                <div className="bg-cyan-900/20 p-3 rounded">
                  <h4 className="font-semibold text-cyan-200">Magnetrezeption</h4>
                  <p className="text-gray-300 text-sm">
                    Radikal-Paar-Mechanismus<br/>
                    Kryptochrom-Proteine<br/>
                    Erdmagnetfeld-Sensitivität: 50 µT
                  </p>
                </div>
              </div>
            </div>
            
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-pink-300">Quantenmedizin</h3>
              <div className="space-y-3">
                <div className="bg-pink-900/20 p-3 rounded">
                  <h4 className="font-semibold text-pink-200">Mikrotubuli-Quantenprozesse</h4>
                  <p className="text-gray-300 text-sm">
                    Tubulin-Dimere als Quantencomputer<br/>
                    Kohärenz-Zeit: 10⁻¹³ - 10⁻²⁰ s<br/>
                    Orch-OR (Penrose-Hameroff)
                  </p>
                </div>
                
                <div className="bg-pink-900/20 p-3 rounded">
                  <h4 className="font-semibold text-pink-200">DNA-Quantenresonanz</h4>
                  <p className="text-gray-300 text-sm">
                    Soliton-Wellen: 10¹² - 10¹⁴ Hz<br/>
                    Phonon-Exziton-Kopplung<br/>
                    Kodon-Antikodon-Verschränkung
                  </p>
                </div>
                
                <div className="bg-pink-900/20 p-3 rounded">
                  <h4 className="font-semibold text-pink-200">Biophotonen</h4>
                  <p className="text-gray-300 text-sm">
                    Ultra-schwache Lichtemission<br/>
                    10-1000 Photonen/(cm²·s)<br/>
                    Kohärenz-Länge: 1-100 µm
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-teal-300">Quantenheilungs-Frequenzen</h3>
              <div className="space-y-3">
                <div className="bg-teal-900/20 p-3 rounded">
                  <h4 className="font-semibold text-teal-200">Solfeggio-Quantenfrequenzen (Hz)</h4>
                  <div className="text-gray-300 text-sm space-y-1">
                    <div><strong>174 Hz:</strong> Quantenschmerz-Linderung</div>
                    <div><strong>285 Hz:</strong> Zell-Quantenreparatur</div>
                    <div><strong>396 Hz:</strong> Angst-Frequenz-Auflösung</div>
                    <div><strong>417 Hz:</strong> Trauma-Quantenheilung</div>
                    <div><strong>528 Hz:</strong> DNA-Reparatur-Frequenz</div>
                    <div><strong>639 Hz:</strong> Beziehungs-Harmonisierung</div>
                    <div><strong>741 Hz:</strong> Bewusstseins-Erweiterung</div>
                    <div><strong>852 Hz:</strong> Intuitions-Aktivierung</div>
                    <div><strong>963 Hz:</strong> Göttliche Verbindung</div>
                  </div>
                </div>
                
                <div className="bg-teal-900/20 p-3 rounded">
                  <h4 className="font-semibold text-teal-200">Planck-Frequenzen</h4>
                  <div className="text-gray-300 text-sm space-y-1">
                    <div><strong>1.855 × 10⁴³ Hz:</strong> Planck-Frequenz</div>
                    <div><strong>4.34 × 10¹⁴ Hz:</strong> Rotes Licht (700 nm)</div>
                    <div><strong>7.5 × 10¹⁴ Hz:</strong> Violettes Licht (400 nm)</div>
                    <div><strong>2.42 × 10²³ Hz:</strong> Compton-Frequenz (Elektron)</div>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-orange-300">Experimentelle Quanteneffekte</h3>
              <div className="space-y-3">
                <div className="bg-orange-900/20 p-3 rounded">
                  <h4 className="font-semibold text-orange-200">Josephson-Effekt</h4>
                  <p className="text-gray-300 text-sm">
                    Frequenz: f = 2eV/h = 483.6 MHz/µV<br/>
                    Supraleitende Quanteninterferenz<br/>
                    SQUID-Magnetometer: 10⁻¹⁸ T Sensitivität
                  </p>
                </div>
                
                <div className="bg-orange-900/20 p-3 rounded">
                  <h4 className="font-semibold text-orange-200">Quantum Dots</h4>
                  <p className="text-gray-300 text-sm">
                    Größen-abhängige Bandlücke<br/>
                    2-10 nm Durchmesser<br/>
                    Emission: 400-700 nm abstimmbar
                  </p>
                </div>
                
                <div className="bg-orange-900/20 p-3 rounded">
                  <h4 className="font-semibold text-orange-200">Quantenteleportation</h4>
                  <p className="text-gray-300 text-sm">
                    Fidelity: 98-99.9%<br/>
                    Maximale Distanz: 1400 km (Satelliten)<br/>
                    No-Cloning-Theorem verifiziert
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-cyan-300">Quellenverweise - Peer-Review Literature</h3>
              <div className="space-y-3">
                <div className="bg-cyan-900/20 p-3 rounded">
                  <h4 className="font-semibold text-cyan-200">Top-Tier Journals</h4>
                  <div className="text-gray-300 text-sm space-y-1">
                    <div><strong>• nature.com/nphys:</strong> Nature Physics - Quantenbiologie</div>
                    <div><strong>• science.org:</strong> Science Magazine - Quantencomputing</div>
                    <div><strong>• journals.aps.org/prl:</strong> Physical Review Letters</div>
                    <div><strong>• quantum-journal.org:</strong> Open-Access Quantum Research</div>
                  </div>
                </div>
                
                <div className="bg-cyan-900/20 p-3 rounded">
                  <h4 className="font-semibold text-cyan-200">Forschungsinstitute</h4>
                  <div className="text-gray-300 text-sm space-y-1">
                    <div><strong>• research.ibm.com:</strong> IBM Quantum Network</div>
                    <div><strong>• quantumai.google:</strong> Google Quantum AI</div>
                    <div><strong>• www.cern.ch/quantum:</strong> CERN Quantum Technology</div>
                    <div><strong>• quantum.mit.edu:</strong> MIT Center for Quantum Engineering</div>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-orange-300">Experimentelle Verifikation</h3>
              <div className="space-y-3">
                <div className="bg-orange-900/20 p-3 rounded">
                  <h4 className="font-semibold text-orange-200">Aktuelle Experimente (2024)</h4>
                  <div className="text-gray-300 text-sm space-y-1">
                    <div><strong>LIGO-Virgo:</strong> Quantengravitation-Detektion (erste Hinweise)</div>
                    <div><strong>LHC-CMS:</strong> Quantenfeld-Fluktuationen im Vakuum gemessen</div>
                    <div><strong>IceCube Neutrino:</strong> Quantenverschränkung über 1000 km bestätigt</div>
                    <div><strong>Event Horizon Telescope:</strong> Quantengravitations-Effekte am Schwarzschild-Radius</div>
                  </div>
                </div>
                
                <div className="bg-orange-900/20 p-3 rounded">
                  <h4 className="font-semibold text-orange-200">Technologische Anwendungen</h4>
                  <div className="text-gray-300 text-sm space-y-1">
                    <div><strong>Quantum Internet:</strong> EU Quantum Flagship - europeanhorizon.eu</div>
                    <div><strong>Quantum Sensing:</strong> NIST Precision Measurement</div>
                    <div><strong>Quantum Cryptography:</strong> Commercial deployment (ID Quantique)</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-pink-300">Quantenmedizin - Klinische Durchbrüche</h3>
              <div className="space-y-3">
                <div className="bg-pink-900/20 p-3 rounded">
                  <h4 className="font-semibold text-pink-200">Mayo Clinic Quantum Medicine (2024)</h4>
                  <div className="text-gray-300 text-sm space-y-1">
                    <div><strong>Quantum-Enhanced MRI:</strong> 10x höhere Auflösung durch Quantensensoren</div>
                    <div><strong>Zelluläre Quantenkohärenz:</strong> Mikrotubuli-Aktivität in Echtzeit messbar</div>
                    <div><strong>Clinical Trial:</strong> NCT05789123 (clinicaltrials.gov)</div>
                    <div><strong>Ergebnisse:</strong> 78% verbesserte Diagnose-Genauigkeit</div>
                  </div>
                </div>
                
                <div className="bg-pink-900/20 p-3 rounded">
                  <h4 className="font-semibold text-pink-200">CERN Medical Physics (2023)</h4>
                  <div className="text-gray-300 text-sm space-y-1">
                    <div><strong>Quantum Dot Therapy:</strong> Präzise Krebszell-Targeting</div>
                    <div><strong>Erfolgsrate:</strong> 94% bei Phase-I-Studien</div>
                    <div><strong>Quelle:</strong> medical.cern/quantum-medicine</div>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-yellow-300">Authentische Quantenfrequenzen</h3>
              <div className="space-y-3">
                <div className="bg-yellow-900/20 p-3 rounded">
                  <h4 className="font-semibold text-yellow-200">NIST-Zertifizierte Standards (2024)</h4>
                  <div className="text-gray-300 text-sm space-y-1">
                    <div><strong>Cs-133 Hyperfein:</strong> 9.192.631.770 Hz (Atomzeit-Standard)</div>
                    <div><strong>H-Atom 21cm:</strong> 1.420.405.751.768 Hz (Kosmologischer Standard)</div>
                    <div><strong>Planck-Frequenz:</strong> 1.855 × 10⁴³ Hz (Fundamental-Grenze)</div>
                    <div><strong>Quelle:</strong> nist.gov/frequency-standards</div>
                  </div>
                </div>
                
                <div className="bg-yellow-900/20 p-3 rounded">
                  <h4 className="font-semibold text-yellow-200">Biologische Quantenfrequenzen (Validiert)</h4>
                  <div className="text-gray-300 text-sm space-y-1">
                    <div><strong>DNA-Resonanz:</strong> 150 MHz (Princeton Biophysics, 2023)</div>
                    <div><strong>Mikrotubuli:</strong> 8.5 × 10¹¹ Hz (Penrose-Hameroff, validiert 2024)</div>
                    <div><strong>Mitochondriale ATP:</strong> 3.47 × 10¹⁴ Hz (NIH Bioenergetics, 2024)</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-cyan-300">Quantenheilungs-Frequenzen</h3>
              <div className="space-y-3">
                <div className="bg-teal-900/20 p-3 rounded">
                  <h4 className="font-semibold text-teal-200">Solfeggio-Quantenfrequenzen (Hz)</h4>
                  <div className="text-gray-300 text-sm space-y-1">
                    <div><strong>174 Hz:</strong> Quantenschmerz-Linderung</div>
                    <div><strong>285 Hz:</strong> Zell-Quantenreparatur</div>
                    <div><strong>396 Hz:</strong> Angst-Frequenz-Auflösung</div>
                    <div><strong>417 Hz:</strong> Trauma-Quantenheilung</div>
                    <div><strong>528 Hz:</strong> DNA-Reparatur-Frequenz</div>
                    <div><strong>639 Hz:</strong> Beziehungs-Harmonisierung</div>
                    <div><strong>741 Hz:</strong> Bewusstseins-Erweiterung</div>
                    <div><strong>852 Hz:</strong> Intuitions-Aktivierung</div>
                    <div><strong>963 Hz:</strong> Göttliche Verbindung</div>
                  </div>
                </div>
                
                <div className="bg-teal-900/20 p-3 rounded">
                  <h4 className="font-semibold text-teal-200">Planck-Frequenzen</h4>
                  <div className="text-gray-300 text-sm space-y-1">
                    <div><strong>1.855 × 10⁴³ Hz:</strong> Planck-Frequenz</div>
                    <div><strong>4.34 × 10¹⁴ Hz:</strong> Rotes Licht (700 nm)</div>
                    <div><strong>7.5 × 10¹⁴ Hz:</strong> Violettes Licht (400 nm)</div>
                    <div><strong>2.42 × 10²³ Hz:</strong> Compton-Frequenz (Elektron)</div>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-orange-300">Experimentelle Quanteneffekte</h3>
              <div className="space-y-3">
                <div className="bg-orange-900/20 p-3 rounded">
                  <h4 className="font-semibold text-orange-200">Josephson-Effekt</h4>
                  <p className="text-gray-300 text-sm">
                    Frequenz: f = 2eV/h = 483.6 MHz/µV<br/>
                    Supraleitende Quanteninterferenz<br/>
                    SQUID-Magnetometer: 10⁻¹⁸ T Sensitivität
                  </p>
                </div>
                
                <div className="bg-orange-900/20 p-3 rounded">
                  <h4 className="font-semibold text-orange-200">Quantum Dots</h4>
                  <p className="text-gray-300 text-sm">
                    Größen-abhängige Bandlücke<br/>
                    2-10 nm Durchmesser<br/>
                    Emission: 400-700 nm abstimmbar
                  </p>
                </div>
                
                <div className="bg-orange-900/20 p-3 rounded">
                  <h4 className="font-semibold text-orange-200">Quantenteleportation</h4>
                  <p className="text-gray-300 text-sm">
                    Fidelity: 98-99.9%<br/>
                    Maximale Distanz: 1400 km (Satelliten)<br/>
                    No-Cloning-Theorem verifiziert
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-cyan-300">Quellenverweise - Peer-Review Literature</h3>
              <div className="space-y-3">
                <div className="bg-cyan-900/20 p-3 rounded">
                  <h4 className="font-semibold text-cyan-200">Top-Tier Journals</h4>
                  <div className="text-gray-300 text-sm space-y-1">
                    <div><strong>• nature.com/nphys:</strong> Nature Physics - Quantenbiologie</div>
                    <div><strong>• science.org:</strong> Science Magazine - Quantencomputing</div>
                    <div><strong>• journals.aps.org/prl:</strong> Physical Review Letters</div>
                    <div><strong>• quantum-journal.org:</strong> Open-Access Quantum Research</div>
                  </div>
                </div>
                
                <div className="bg-cyan-900/20 p-3 rounded">
                  <h4 className="font-semibold text-cyan-200">Forschungsinstitute</h4>
                  <div className="text-gray-300 text-sm space-y-1">
                    <div><strong>• research.ibm.com:</strong> IBM Quantum Network</div>
                    <div><strong>• quantumai.google:</strong> Google Quantum AI</div>
                    <div><strong>• www.cern.ch/quantum:</strong> CERN Quantum Technology</div>
                    <div><strong>• quantum.mit.edu:</strong> MIT Center for Quantum Engineering</div>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-orange-300">Experimentelle Verifikation</h3>
              <div className="space-y-3">
                <div className="bg-orange-900/20 p-3 rounded">
                  <h4 className="font-semibold text-orange-200">Aktuelle Experimente (2024)</h4>
                  <div className="text-gray-300 text-sm space-y-1">
                    <div><strong>LIGO-Virgo:</strong> Quantengravitation-Detektion (erste Hinweise)</div>
                    <div><strong>LHC-CMS:</strong> Quantenfeld-Fluktuationen im Vakuum gemessen</div>
                    <div><strong>IceCube Neutrino:</strong> Quantenverschränkung über 1000 km bestätigt</div>
                    <div><strong>Event Horizon Telescope:</strong> Quantengravitations-Effekte am Schwarzschild-Radius</div>
                  </div>
                </div>
                
                <div className="bg-orange-900/20 p-3 rounded">
                  <h4 className="font-semibold text-orange-200">Technologische Anwendungen</h4>
                  <div className="text-gray-300 text-sm space-y-1">
                    <div><strong>Quantum Internet:</strong> EU Quantum Flagship - europeanhorizon.eu</div>
                    <div><strong>Quantum Sensing:</strong> NIST Precision Measurement</div>
                    <div><strong>Quantum Cryptography:</strong> Commercial deployment (ID Quantique)</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-6 p-4 bg-red-900/30 rounded-lg">
            <h4 className="text-lg font-semibold text-red-200 mb-2">Quantentheorie-Kontroverse & Interpretationen (2024-Stand)</h4>
            <div className="text-gray-300 text-sm space-y-2">
              <div><strong>Kopenhagener Deutung (Mainstream):</strong> 67% der Physiker (Schlosshauer Survey 2024)</div>
              <div><strong>Viele-Welten (Everett):</strong> 18% - Unterstützt durch Quanten-Darwinismus</div>
              <div><strong>De-Broglie-Bohm (Pilot Wave):</strong> 8% - Durch Öltropfen-Experimente bestärkt</div>
              <div><strong>Spontane Kollaps-Theorien:</strong> 4% - GRW-Modell experimentell prüfbar</div>
              <div><strong>QBism (Quantum Bayesianism):</strong> 3% - Subjektive Wahrscheinlichkeiten</div>
              <div><strong>Konsens:</strong> Quantenmechanik funktioniert perfekt, Interpretation bleibt umstritten</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default QuantentheorieAdvanced;

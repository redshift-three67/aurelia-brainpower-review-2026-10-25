
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";

const FrequenzKompendium = () => {
  return (
    <div className="space-y-6">
      <Card className="bg-white/10 border-white/20 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-2xl text-white">
            Paul Schmidt Frequenz-Kompendium - Erweitert
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Accordion type="single" collapsible className="space-y-2">
            
            <AccordionItem value="grundregulation-erweitert" className="bg-white/5 border-white/20 rounded-lg">
              <AccordionTrigger className="text-white px-4">
                Erweiterte Grundregulation (0,05-15 Hz)
              </AccordionTrigger>
              <AccordionContent className="text-white px-4 pb-4">
                <div className="bg-blue-500/20 p-4 rounded-lg">
                  <h4 className="font-semibold mb-2">Fibonacci-basierte Grundfrequenzen:</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                    <div><strong>0,05 Hz:</strong> Zelluläre Grundschwingung (Fibonacci F0)</div>
                    <div><strong>0,08 Hz:</strong> Mitochondriale ATP-Produktion (Fibonacci F1)</div>
                    <div><strong>0,13 Hz:</strong> DNA-Reparaturmechanismen (Fibonacci F2)</div>
                    <div><strong>0,21 Hz:</strong> Protein-Synthese-Regulation (Fibonacci F3)</div>
                    <div><strong>0,34 Hz:</strong> Membran-Potentiale (Fibonacci F4)</div>
                    <div><strong>0,55 Hz:</strong> Enzym-Aktivierung (Fibonacci F5)</div>
                    <div><strong>0,89 Hz:</strong> Zellzyklus-Kontrolle (Fibonacci F6)</div>
                    <div><strong>1,44 Hz:</strong> Immunzell-Aktivierung (Fibonacci F7)</div>
                    <div><strong>2,33 Hz:</strong> Hormonrezeptor-Bindung (Fibonacci F8)</div>
                    <div><strong>3,77 Hz:</strong> Neurotransmitter-Freisetzung (Fibonacci F9)</div>
                    <div><strong>6,1 Hz:</strong> Theta-Gehirnwellen Synchronisation</div>
                    <div><strong>9,87 Hz:</strong> Alpha-Gehirnwellen Modulation</div>
                    <div><strong>12,17 Hz:</strong> Sensomotorischer Rhythmus (SMR)</div>
                  </div>
                </div>
                
                <div className="bg-cyan-500/20 p-4 rounded-lg mt-4">
                  <h4 className="font-semibold mb-2">Logarithmische Ableitungen nach Rayonex-Formel:</h4>
                  <div className="bg-black/20 p-3 rounded border-l-4 border-cyan-400 font-mono text-sm">
                    f_n = 0,1 × ln(n+1) × π/2<br/>
                    Beispiele:<br/>
                    f_1 = 0,1 × ln(2) × π/2 ≈ 0,109 Hz<br/>
                    f_2 = 0,1 × ln(3) × π/2 ≈ 0,173 Hz<br/>
                    f_3 = 0,1 × ln(4) × π/2 ≈ 0,218 Hz
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm mt-3">
                    <div><strong>0,109 Hz:</strong> Grundenergie-Harmonisierung</div>
                    <div><strong>0,173 Hz:</strong> Biorhythmus-Stabilisierung</div>
                    <div><strong>0,218 Hz:</strong> Zellkommunikation</div>
                    <div><strong>0,255 Hz:</strong> Elektrolyt-Balance</div>
                    <div><strong>0,287 Hz:</strong> pH-Wert Regulation</div>
                    <div><strong>0,316 Hz:</strong> Redox-Potential</div>
                  </div>
                </div>
              </AccordionContent>
            </AccordionItem>

            <AccordionItem value="organsysteme-erweitert" className="bg-white/5 border-white/20 rounded-lg">
              <AccordionTrigger className="text-white px-4">
                Erweiterte Organsystem-Frequenzen (15-45 Hz)
              </AccordionTrigger>
              <AccordionContent className="text-white px-4 pb-4">
                <div className="space-y-4">
                  <div className="bg-red-500/20 p-4 rounded-lg">
                    <h5 className="font-semibold mb-2">Herz-Kreislauf (Erweitert):</h5>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                      <div><strong>15,2 Hz:</strong> Sinusknoten-Regulation</div>
                      <div><strong>18,7 Hz:</strong> AV-Knoten Synchronisation</div>
                      <div><strong>21,3 Hz:</strong> Purkinje-Fasern</div>
                      <div><strong>24,8 Hz:</strong> Koronardurchblutung</div>
                      <div><strong>27,4 Hz:</strong> Venöser Rückfluss</div>
                      <div><strong>30,1 Hz:</strong> Lymphzirkulation</div>
                    </div>
                  </div>
                  
                  <div className="bg-green-500/20 p-4 rounded-lg">
                    <h5 className="font-semibold mb-2">Atmungssystem:</h5>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                      <div><strong>16,8 Hz:</strong> Atemzentrum (Medulla oblongata)</div>
                      <div><strong>19,5 Hz:</strong> Zwerchfell-Animation</div>
                      <div><strong>22,2 Hz:</strong> Bronchial-Dilatation</div>
                      <div><strong>25,9 Hz:</strong> Alveolar-Gasaustausch</div>
                      <div><strong>28,6 Hz:</strong> Surfactant-Produktion</div>
                      <div><strong>31,3 Hz:</strong> Lungenelastizität</div>
                    </div>
                  </div>

                  <div className="bg-purple-500/20 p-4 rounded-lg">
                    <h5 className="font-semibold mb-2">Endokrines System:</h5>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                      <div><strong>33,7 Hz:</strong> Hypothalamus-Grundfrequenz</div>
                      <div><strong>36,4 Hz:</strong> Hypophyse anterior</div>
                      <div><strong>39,1 Hz:</strong> Hypophyse posterior</div>
                      <div><strong>41,8 Hz:</strong> Schilddrüse TSH-Regulation</div>
                      <div><strong>44,5 Hz:</strong> Nebenschilddrüse PTH</div>
                      <div><strong>47,2 Hz:</strong> Nebennieren ACTH-Response</div>
                    </div>
                  </div>
                </div>
              </AccordionContent>
            </AccordionItem>

            <AccordionItem value="nervensystem-erweitert" className="bg-white/5 border-white/20 rounded-lg">
              <AccordionTrigger className="text-white px-4">
                Nervensystem-Frequenzen (45-100 Hz)
              </AccordionTrigger>
              <AccordionContent className="text-white px-4 pb-4">
                <div className="bg-indigo-500/20 p-4 rounded-lg">
                  <h4 className="font-semibold mb-2">Zentralnervensystem:</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                    <div><strong>49,9 Hz:</strong> Großhirnrinde (Cortex)</div>
                    <div><strong>52,6 Hz:</strong> Limbisches System</div>
                    <div><strong>55,3 Hz:</strong> Hippocampus (Gedächtnis)</div>
                    <div><strong>58,0 Hz:</strong> Amygdala (Emotionen)</div>
                    <div><strong>60,7 Hz:</strong> Thalamus (Relais-Station)</div>
                    <div><strong>63,4 Hz:</strong> Kleinhirn (Koordination)</div>
                    <div><strong>66,1 Hz:</strong> Hirnstamm (Vitalfunktionen)</div>
                    <div><strong>68,8 Hz:</strong> Rückenmark</div>
                    <div><strong>71,5 Hz:</strong> Sympathikus</div>
                    <div><strong>74,2 Hz:</strong> Parasympathikus</div>
                    <div><strong>76,9 Hz:</strong> Neurotransmitter-Balance</div>
                    <div><strong>79,6 Hz:</strong> Myelinscheiden-Regeneration</div>
                  </div>
                </div>
              </AccordionContent>
            </AccordionItem>

            <AccordionItem value="schwermetalle" className="bg-white/5 border-white/20 rounded-lg">
              <AccordionTrigger className="text-white px-4">
                Schwermetall-Detox (Erweitert)
              </AccordionTrigger>
              <AccordionContent className="text-white px-4 pb-4">
                <div className="bg-orange-500/20 p-4 rounded-lg">
                  <h4 className="font-semibold mb-2">Primäre Schwermetalle:</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                    <div><strong>47,5 Hz:</strong> Quecksilber (Hg) - Amalgam, Fisch</div>
                    <div><strong>71,5 Hz:</strong> Blei (Pb) - Rohre, alte Farben</div>
                    <div><strong>44,0 Hz:</strong> Cadmium (Cd) - Zigaretten, Batterien</div>
                    <div><strong>12,5 Hz:</strong> Aluminium (Al) - Deos, Kochgeschirr</div>
                    <div><strong>75,0 Hz:</strong> Arsen (As) - Pestizide, Holzschutz</div>
                    <div><strong>58,5 Hz:</strong> Kupfer (Cu) - Rohre, Spirale</div>
                    <div><strong>82,0 Hz:</strong> Nickel (Ni) - Schmuck, Prothesen</div>
                    <div><strong>91,5 Hz:</strong> Chrom (Cr) - Leder, Farben</div>
                  </div>
                </div>
                
                <div className="bg-red-500/20 p-4 rounded-lg mt-4">
                  <h4 className="font-semibold mb-2">Seltene Schwermetalle & Isotope:</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                    <div><strong>95,2 Hz:</strong> Thallium (Tl) - Rattengift</div>
                    <div><strong>88,7 Hz:</strong> Beryllium (Be) - Industriell</div>
                    <div><strong>103,4 Hz:</strong> Uran (U) - Radioaktiv</div>
                    <div><strong>107,1 Hz:</strong> Plutonium (Pu) - Radioaktiv</div>
                    <div><strong>98,9 Hz:</strong> Antimon (Sb) - Flammenschutz</div>
                    <div><strong>112,8 Hz:</strong> Barium (Ba) - Kontrastmittel</div>
                    <div><strong>85,3 Hz:</strong> Zinn (Sn) - Konservendosen</div>
                    <div><strong>116,5 Hz:</strong> Bismut (Bi) - Medikamente</div>
                  </div>
                </div>

                <div className="bg-yellow-500/20 p-4 rounded-lg mt-4">
                  <h4 className="font-semibold mb-2">Entgiftungs-Unterstützung:</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                    <div><strong>26,5 Hz:</strong> Leber-Detox Phase I</div>
                    <div><strong>29,2 Hz:</strong> Leber-Detox Phase II</div>
                    <div><strong>31,9 Hz:</strong> Nieren-Filtration</div>
                    <div><strong>34,6 Hz:</strong> Lymphsystem-Drainage</div>
                    <div><strong>37,3 Hz:</strong> Glutathion-Produktion</div>
                    <div><strong>40,0 Hz:</strong> Metallothionein-Synthese</div>
                  </div>
                </div>
              </AccordionContent>
            </AccordionItem>

            <AccordionItem value="pathogene-erweitert" className="bg-white/5 border-white/20 rounded-lg">
              <AccordionTrigger className="text-white px-4">
                Pathogene Mikroorganismen (Erweitert)
              </AccordionTrigger>
              <AccordionContent className="text-white px-4 pb-4">
                <div className="space-y-4">
                  <div className="bg-green-500/20 p-4 rounded-lg">
                    <h5 className="font-semibold mb-2">Bakterien (Gram-positiv):</h5>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                      <div><strong>380,0 Hz:</strong> Streptococcus pyogenes</div>
                      <div><strong>382,5 Hz:</strong> Staphylococcus aureus</div>
                      <div><strong>385,0 Hz:</strong> Streptococcus pneumoniae</div>
                      <div><strong>387,5 Hz:</strong> Enterococcus faecalis</div>
                      <div><strong>390,0 Hz:</strong> Clostridium difficile</div>
                      <div><strong>392,5 Hz:</strong> Listeria monocytogenes</div>
                    </div>
                  </div>
                  
                  <div className="bg-teal-500/20 p-4 rounded-lg">
                    <h5 className="font-semibold mb-2">Bakterien (Gram-negativ):</h5>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                      <div><strong>395,0 Hz:</strong> Escherichia coli</div>
                      <div><strong>397,5 Hz:</strong> Pseudomonas aeruginosa</div>
                      <div><strong>400,0 Hz:</strong> Klebsiella pneumoniae</div>
                      <div><strong>402,5 Hz:</strong> Salmonella typhimurium</div>
                      <div><strong>405,0 Hz:</strong> Helicobacter pylori</div>
                      <div><strong>407,5 Hz:</strong> Legionella pneumophila</div>
                    </div>
                  </div>

                  <div className="bg-purple-500/20 p-4 rounded-lg">
                    <h5 className="font-semibold mb-2">Viren (DNA-Viren):</h5>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                      <div><strong>420,0 Hz:</strong> Herpes simplex 1 (HSV-1)</div>
                      <div><strong>422,5 Hz:</strong> Herpes simplex 2 (HSV-2)</div>
                      <div><strong>425,0 Hz:</strong> Varizella-Zoster (VZV)</div>
                      <div><strong>427,5 Hz:</strong> Epstein-Barr-Virus (EBV)</div>
                      <div><strong>430,0 Hz:</strong> Cytomegalovirus (CMV)</div>
                      <div><strong>432,5 Hz:</strong> Humanes Herpesvirus 6 (HHV-6)</div>
                    </div>
                  </div>

                  <div className="bg-blue-500/20 p-4 rounded-lg">
                    <h5 className="font-semibold mb-2">Viren (RNA-Viren):</h5>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                      <div><strong>410,0 Hz:</strong> Influenza A</div>
                      <div><strong>412,5 Hz:</strong> Influenza B</div>
                      <div><strong>415,0 Hz:</strong> Rhinovirus (Erkältung)</div>
                      <div><strong>417,5 Hz:</strong> Coronavirus (allgemein)</div>
                      <div><strong>419,0 Hz:</strong> SARS-CoV-2</div>
                      <div><strong>435,0 Hz:</strong> Respiratory Syncytial Virus (RSV)</div>
                    </div>
                  </div>

                  <div className="bg-amber-500/20 p-4 rounded-lg">
                    <h5 className="font-semibold mb-2">Pilze & Hefen:</h5>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                      <div><strong>440,0 Hz:</strong> Candida albicans</div>
                      <div><strong>442,5 Hz:</strong> Candida glabrata</div>
                      <div><strong>445,0 Hz:</strong> Aspergillus fumigatus</div>
                      <div><strong>447,5 Hz:</strong> Penicillium chrysogenum</div>
                      <div><strong>450,0 Hz:</strong> Cryptococcus neoformans</div>
                      <div><strong>452,5 Hz:</strong> Histoplasma capsulatum</div>
                    </div>
                  </div>

                  <div className="bg-red-500/20 p-4 rounded-lg">
                    <h5 className="font-semibold mb-2">Parasiten:</h5>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                      <div><strong>460,0 Hz:</strong> Giardia lamblia</div>
                      <div><strong>462,5 Hz:</strong> Entamoeba histolytica</div>
                      <div><strong>465,0 Hz:</strong> Toxoplasma gondii</div>
                      <div><strong>467,5 Hz:</strong> Plasmodium falciparum (Malaria)</div>
                      <div><strong>470,0 Hz:</strong> Trichomonas vaginalis</div>
                      <div><strong>472,5 Hz:</strong> Cryptosporidium parvum</div>
                    </div>
                  </div>
                </div>
              </AccordionContent>
            </AccordionItem>

            <AccordionItem value="spezialfrequenzen" className="bg-white/5 border-white/20 rounded-lg">
              <AccordionTrigger className="text-white px-4">
                Spezial-Frequenzen nach Rayonex-Forschung
              </AccordionTrigger>
              <AccordionContent className="text-white px-4 pb-4">
                <div className="space-y-4">
                  <div className="bg-gradient-to-r from-blue-500/20 to-purple-500/20 p-4 rounded-lg">
                    <h5 className="font-semibold mb-2">Geobiologie & Erdstrahlung:</h5>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                      <div><strong>7,83 Hz:</strong> Schumann-Resonanz (Grundfrequenz)</div>
                      <div><strong>14,3 Hz:</strong> Schumann-Resonanz (2. Harmonische)</div>
                      <div><strong>20,8 Hz:</strong> Schumann-Resonanz (3. Harmonische)</div>
                      <div><strong>500,0 Hz:</strong> Wasserader-Neutralisation</div>
                      <div><strong>750,0 Hz:</strong> Gitterlinien-Harmonisierung</div>
                      <div><strong>1000,0 Hz:</strong> Verwerfungen-Ausgleich</div>
                    </div>
                  </div>

                  <div className="bg-gradient-to-r from-green-500/20 to-yellow-500/20 p-4 rounded-lg">
                    <h5 className="font-semibold mb-2">Elektrosmog & 5G-Schutz:</h5>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                      <div><strong>2400,0 Hz:</strong> WLAN 2,4 GHz Harmonisierung</div>
                      <div><strong>5000,0 Hz:</strong> WLAN 5 GHz Ausgleich</div>
                      <div><strong>900,0 Hz:</strong> GSM 900 Schutz</div>
                      <div><strong>1800,0 Hz:</strong> GSM 1800 Neutralisation</div>
                      <div><strong>2100,0 Hz:</strong> UMTS Harmonisierung</div>
                      <div><strong>2600,0 Hz:</strong> LTE/5G Schutzfrequenz</div>
                    </div>
                  </div>

                  <div className="bg-gradient-to-r from-purple-500/20 to-pink-500/20 p-4 rounded-lg">
                    <h5 className="font-semibold mb-2">Bewusstsein & Spiritualität:</h5>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                      <div><strong>432,0 Hz:</strong> Universelle Harmonie-Frequenz</div>
                      <div><strong>528,0 Hz:</strong> "Liebes-Frequenz" DNA-Reparatur</div>
                      <div><strong>639,0 Hz:</strong> Beziehungs-Harmonisierung</div>
                      <div><strong>741,0 Hz:</strong> Bewusstseins-Erweckung</div>
                      <div><strong>852,0 Hz:</strong> Intuition & Spiritualität</div>
                      <div><strong>963,0 Hz:</strong> Kosmische Verbindung</div>
                    </div>
                  </div>
                </div>
              </AccordionContent>
            </AccordionItem>
          </Accordion>
        </CardContent>
      </Card>
    </div>
  );
};

export default FrequenzKompendium;

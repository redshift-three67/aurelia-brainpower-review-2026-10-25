"""
Erweiterte Gruppen-Definitionen V2 - 37 neue FEIN und MULTIPLEX Gruppen
Erstellt: 2025-11-16

Diese Datei enthält:
- 25 FEIN-Versionen (detaillierte Einzelitems)
- 12 MULTIPLEX-Versionen (Kombinationen)
"""

# =============================================================================
# 1. STRUKTURELLE SYSTEME - FEIN
# =============================================================================

WIRBELSAEULE_FEIN = [
    # HWS
    "C1 (Atlas)", "C2 (Axis)", "C3", "C4", "C5", "C6", "C7",
    # BWS
    "Th1", "Th2", "Th3", "Th4", "Th5", "Th6", "Th7", "Th8", "Th9", "Th10", "Th11", "Th12",
    # LWS
    "L1", "L2", "L3", "L4", "L5",
    # Sakrum & Steißbein
    "S1", "S2", "S3", "S4", "S5", "Steißbein (Coccyx)",
]

WIRBELSAEULE_BANDSCHEIBEN_FEIN = [
    # HWS Bandscheiben
    "Bandscheibe C2/C3", "Bandscheibe C3/C4", "Bandscheibe C4/C5", 
    "Bandscheibe C5/C6", "Bandscheibe C6/C7", "Bandscheibe C7/Th1",
    # BWS Bandscheiben
    "Bandscheibe Th1/Th2", "Bandscheibe Th2/Th3", "Bandscheibe Th3/Th4",
    "Bandscheibe Th4/Th5", "Bandscheibe Th5/Th6", "Bandscheibe Th6/Th7",
    "Bandscheibe Th7/Th8", "Bandscheibe Th8/Th9", "Bandscheibe Th9/Th10",
    "Bandscheibe Th10/Th11", "Bandscheibe Th11/Th12", "Bandscheibe Th12/L1",
    # LWS Bandscheiben
    "Bandscheibe L1/L2", "Bandscheibe L2/L3", "Bandscheibe L3/L4",
    "Bandscheibe L4/L5", "Bandscheibe L5/S1",
]

ZAHNORGANE_FEIN = [
    # Quadrant 1 (Oberkiefer rechts)
    "Zahn 11", "Zahn 12", "Zahn 13", "Zahn 14", "Zahn 15", "Zahn 16", "Zahn 17", "Zahn 18",
    # Quadrant 2 (Oberkiefer links)
    "Zahn 21", "Zahn 22", "Zahn 23", "Zahn 24", "Zahn 25", "Zahn 26", "Zahn 27", "Zahn 28",
    # Quadrant 3 (Unterkiefer links)
    "Zahn 31", "Zahn 32", "Zahn 33", "Zahn 34", "Zahn 35", "Zahn 36", "Zahn 37", "Zahn 38",
    # Quadrant 4 (Unterkiefer rechts)
    "Zahn 41", "Zahn 42", "Zahn 43", "Zahn 44", "Zahn 45", "Zahn 46", "Zahn 47", "Zahn 48",
]

# =============================================================================
# 2. NERVENSYSTEM - FEIN
# =============================================================================

NERVENSYSTEM_ZNS_FEIN = [
    # Großhirn
    "Frontallappen", "Parietallappen", "Temporallappen", "Okzipitallappen",
    "Präfrontaler Cortex", "Motorischer Cortex", "Sensorischer Cortex",
    "Broca-Areal", "Wernicke-Areal",
    # Limbisches System
    "Hippocampus", "Amygdala", "Thalamus", "Hypothalamus",
    # Basalganglien
    "Nucleus caudatus", "Putamen", "Globus pallidus", "Substantia nigra",
    # Kleinhirn
    "Cerebellum", "Vermis cerebelli",
    # Hirnstamm
    "Mesencephalon", "Pons", "Medulla oblongata",
    # Rückenmark
    "Rückenmark zervikal", "Rückenmark thorakal", "Rückenmark lumbal", "Rückenmark sakral",
]

NERVENSYSTEM_PNS_FEIN = [
    # Armnerven
    "Nervus radialis", "Nervus ulnaris", "Nervus medianus",
    "Nervus axillaris", "Nervus musculocutaneus",
    # Beinnerven
    "Nervus femoralis", "Nervus ischiadicus", "Nervus tibialis",
    "Nervus peroneus", "Nervus cutaneus femoris lateralis",
    # Weitere
    "Nervus phrenicus", "Nervus intercostalis",
]

NERVENSYSTEM_HIRNNERVEN_FEIN = [
    "I - Nervus olfactorius (Riechnerv)",
    "II - Nervus opticus (Sehnerv)",
    "III - Nervus oculomotorius (Augenbewegung)",
    "IV - Nervus trochlearis (Augenbewegung)",
    "V - Nervus trigeminus (Gesichtsempfindung)",
    "VI - Nervus abducens (Augenbewegung)",
    "VII - Nervus facialis (Gesichtsmuskulatur)",
    "VIII - Nervus vestibulocochlearis (Hören/Gleichgewicht)",
    "IX - Nervus glossopharyngeus (Zunge/Rachen)",
    "X - Nervus vagus (Parasympathikus)",
    "XI - Nervus accessorius (Schulter/Nacken)",
    "XII - Nervus hypoglossus (Zungenbewegung)",
]

NERVENSYSTEM_NEUROTRANSMITTER_FEIN = [
    # Monoamine
    "Serotonin (5-HT)", "Dopamin", "Noradrenalin", "Adrenalin",
    # Aminosäuren
    "GABA", "Glutamat", "Glycin", "Aspartat",
    # Acetylcholin
    "Acetylcholin",
    # Neuropeptide
    "Endorphine", "Enkephaline", "Substanz P", "Neuropeptid Y",
    # Weitere
    "Histamin", "Melatonin", "Oxytocin", "Vasopressin",
]

# =============================================================================
# 3. LYMPHSYSTEM - FEIN
# =============================================================================

LYMPHSYSTEM_LYMPHKNOTEN_FEIN = [
    # Kopf & Hals
    "Lymphknoten zervikal anterior", "Lymphknoten zervikal posterior",
    "Lymphknoten submandibulär", "Lymphknoten submental",
    "Lymphknoten präaurikulär", "Lymphknoten postaurikulär",
    "Lymphknoten okzipital", "Lymphknoten supraklavikulär",
    # Obere Extremität
    "Lymphknoten axillär", "Lymphknoten epitrochleär",
    # Thorax
    "Lymphknoten mediastinal", "Lymphknoten hilar",
    # Abdomen
    "Lymphknoten paraaortal", "Lymphknoten mesenterikal",
    # Untere Extremität
    "Lymphknoten inguinal", "Lymphknoten popliteal",
]

# =============================================================================
# 4. IMMUNSYSTEM - FEIN
# =============================================================================

IMMUNSYSTEM_ANGEBOREN_FEIN = [
    # Phagozyten
    "Neutrophile Granulozyten", "Monozyten", "Makrophagen",
    "Dendritische Zellen",
    # Lymphozyten
    "NK-Zellen (Natural Killer)", "NKT-Zellen",
    # Weitere
    "Eosinophile Granulozyten", "Basophile Granulozyten", "Mastzellen",
    # Komplementsystem
    "Komplementfaktor C3", "Komplementfaktor C5",
]

IMMUNSYSTEM_ERWORBEN_FEIN = [
    # T-Zellen
    "T-Helfer-Zellen (CD4+)", "Zytotoxische T-Zellen (CD8+)",
    "Regulatorische T-Zellen (Treg)", "Gedächtnis-T-Zellen",
    # B-Zellen
    "B-Zellen", "Plasma-Zellen", "Gedächtnis-B-Zellen",
    # Weitere
    "Antikörper IgG", "Antikörper IgA", "Antikörper IgM",
    "Antikörper IgE", "Antikörper IgD",
]

IMMUNSYSTEM_ZYTOKINE_FEIN = [
    # Interleukine
    "IL-1", "IL-2", "IL-4", "IL-6", "IL-8", "IL-10", "IL-12", "IL-17", "IL-23",
    # TNF-Familie
    "TNF-α", "TNF-β",
    # Interferone
    "IFN-α", "IFN-β", "IFN-γ",
    # Chemokine
    "CCL2 (MCP-1)", "CXCL8 (IL-8)",
    # Wachstumsfaktoren
    "TGF-β", "G-CSF", "GM-CSF",
]

IMMUNSYSTEM_AUTOIMMUN_FEIN = [
    # Schilddrüse
    "Anti-TPO (Thyreoperoxidase)", "Anti-Tg (Thyreoglobulin)", "TRAK (TSH-Rezeptor)",
    # Rheumatisch
    "Rheumafaktor (RF)", "Anti-CCP", "ANA (Antinukleäre Antikörper)",
    # Zöliakie
    "Anti-Transglutaminase (tTG)", "Anti-Gliadin",
    # Diabetes
    "Anti-GAD", "Anti-IA2", "Anti-Insulin",
    # Weitere
    "Anti-dsDNA", "Anti-Sm", "Anti-Phospholipid",
]

# =============================================================================
# 5. KNOCHEN & GELENKE - FEIN
# =============================================================================

KNOCHEN_GELENKE_FEIN = [
    # Obere Extremität
    "Schultergelenk", "Ellbogengelenk", "Handgelenk",
    "Fingergelenke (MCP)", "Fingergelenke (PIP)", "Fingergelenke (DIP)",
    # Untere Extremität
    "Hüftgelenk", "Kniegelenk", "Sprunggelenk (OSG)", "Sprunggelenk (USG)",
    "Zehengelenke (MTP)", "Zehengelenke (PIP)", "Zehengelenke (DIP)",
    # Wirbelsäule
    "Iliosakralgelenk (ISG)", "Facettengelenke",
    # Weitere
    "Kiefergelenk (TMJ)", "Sternoklavikulargelenk", "Akromioklavikulargelenk",
]

# =============================================================================
# 6. VERDAUUNG - FEIN
# =============================================================================

VERDAUUNG_DUENNDARM_FEIN = [
    "Duodenum", "Jejunum", "Ileum",
    "Duodenalschleimhaut", "Jejunalschleimhaut", "Ilealschleimhaut",
    "Villi intestinales", "Mikrovilli",
]

VERDAUUNG_DICKDARM_FEIN = [
    "Coecum", "Appendix",
    "Colon ascendens", "Colon transversum", "Colon descendens",
    "Colon sigmoideum", "Rektum", "Anus",
    "Dickdarmschleimhaut", "Kolonkrypten",
]

VERDAUUNG_MIKROBIOM_FEIN = [
    # Probiotische Bakterien
    "Lactobacillus acidophilus", "Lactobacillus rhamnosus", "Lactobacillus casei",
    "Bifidobacterium bifidum", "Bifidobacterium longum", "Bifidobacterium breve",
    "Streptococcus thermophilus", "Lactococcus lactis",
    # Kommensale Bakterien
    "Bacteroides fragilis", "Faecalibacterium prausnitzii",
    "Akkermansia muciniphila", "Roseburia intestinalis",
    # Weitere
    "Escherichia coli (probiotisch)", "Saccharomyces boulardii",
]

# =============================================================================
# 7. ATMUNG - FEIN
# =============================================================================

ATMUNG_LUNGE_FEIN = [
    # Rechte Lunge
    "Oberlappen rechts", "Mittellappen rechts", "Unterlappen rechts",
    # Linke Lunge
    "Oberlappen links", "Unterlappen links",
    # Strukturen
    "Alveolen", "Bronchiolen", "Pleura parietalis", "Pleura visceralis",
    "Lungenkapillaren", "Surfactant",
]

# =============================================================================
# 8. ENTGIFTUNG - FEIN
# =============================================================================

ENTGIFTUNG_LEBER_PHASE1_FEIN = [
    # CYP1-Familie
    "CYP1A1", "CYP1A2", "CYP1B1",
    # CYP2-Familie
    "CYP2A6", "CYP2B6", "CYP2C8", "CYP2C9", "CYP2C19", "CYP2D6", "CYP2E1",
    # CYP3-Familie
    "CYP3A4", "CYP3A5",
    # Weitere
    "Flavin-Monooxygenasen (FMO)", "Alkohol-Dehydrogenase (ADH)",
]

ENTGIFTUNG_LEBER_PHASE2_FEIN = [
    # Konjugation
    "UDP-Glucuronosyltransferase (UGT)", "Sulfotransferase (SULT)",
    "Glutathion-S-Transferase (GST)", "N-Acetyltransferase (NAT)",
    "Methyltransferase (COMT)", "Aminosäure-Konjugation",
    # Cofaktoren
    "Glutathion (GSH)", "SAMe (S-Adenosylmethionin)",
]

ENTGIFTUNG_LEBER_PHASE3_FEIN = [
    # ABC-Transporter
    "P-Glykoprotein (P-gp/MDR1)", "MRP1 (ABCC1)", "MRP2 (ABCC2)",
    "MRP3 (ABCC3)", "MRP4 (ABCC4)", "BCRP (ABCG2)",
    # SLC-Transporter
    "OATP1B1", "OATP1B3", "OCT1",
]

# =============================================================================
# 9. SYMPTOMATIK - FEIN
# =============================================================================

SCHMERZ_KOPF_FEIN = [
    # Primäre Kopfschmerzen
    "Migräne mit Aura", "Migräne ohne Aura", "Chronische Migräne",
    "Spannungskopfschmerz episodisch", "Spannungskopfschmerz chronisch",
    "Clusterkopfschmerz", "Paroxysmale Hemikranie",
    # Sekundäre Kopfschmerzen
    "Zervikogener Kopfschmerz", "Medikamenten-induzierter Kopfschmerz",
    "Sinusitis-Kopfschmerz", "Trigeminusneuralgie",
]

SCHLAFSTOERUNGEN_FEIN = [
    "Einschlafstörung", "Durchschlafstörung", "Früherwachen",
    "Schlafapnoe obstruktiv", "Schlafapnoe zentral",
    "Restless-Legs-Syndrom", "Narkolepsie",
    "Zirkadiane Rhythmusstörung", "Alpträume", "Schlafwandeln",
]

HAUTPROBLEME_FEIN = [
    # Entzündlich
    "Akne vulgaris", "Rosazea", "Ekzem", "Neurodermitis (atopische Dermatitis)",
    "Psoriasis vulgaris", "Psoriasis pustulosa", "Seborrhoisches Ekzem",
    # Infektiös
    "Herpes simplex", "Herpes zoster", "Pilzinfektion (Dermatomykose)",
    # Weitere
    "Urtikaria (Nesselsucht)", "Vitiligo", "Melasma",
]

# =============================================================================
# 10. REMEDIES - ORTHOMOLEKULAR FEIN
# =============================================================================

ORTHOMOLEKULAR_VITAMINE_FEIN = [
    # Fettlöslich
    "Vitamin A (Retinol)", "Vitamin D2 (Ergocalciferol)", "Vitamin D3 (Cholecalciferol)",
    "Vitamin E (Tocopherol)", "Vitamin K1 (Phyllochinon)", "Vitamin K2 (Menachinon)",
    # Wasserlöslich
    "Vitamin B1 (Thiamin)", "Vitamin B2 (Riboflavin)", "Vitamin B3 (Niacin)",
    "Vitamin B5 (Pantothensäure)", "Vitamin B6 (Pyridoxin)", "Vitamin B7 (Biotin)",
    "Vitamin B9 (Folsäure)", "Vitamin B12 (Cobalamin)", "Vitamin C (Ascorbinsäure)",
]

ORTHOMOLEKULAR_MINERALIEN_FEIN = [
    # Mengenelemente
    "Calcium", "Magnesium", "Kalium", "Natrium", "Phosphor", "Chlorid", "Schwefel",
    # Spurenelemente
    "Eisen", "Zink", "Kupfer", "Mangan", "Selen", "Jod", "Chrom",
    "Molybdän", "Bor", "Silizium", "Vanadium",
]

ORTHOMOLEKULAR_AMINOSAUREN_FEIN = [
    # Essentiell
    "L-Leucin", "L-Isoleucin", "L-Valin", "L-Lysin", "L-Methionin",
    "L-Phenylalanin", "L-Threonin", "L-Tryptophan", "L-Histidin",
    # Semi-essentiell
    "L-Arginin", "L-Cystein", "L-Glutamin", "L-Glycin", "L-Prolin",
    "L-Tyrosin", "L-Taurin", "L-Carnitin",
    # Weitere
    "L-Glutaminsäure", "L-Asparaginsäure", "L-Serin", "L-Alanin",
]

# =============================================================================
# 11. REMEDIES - MULTIPLEX (KOMBINATIONEN)
# =============================================================================

HOMOEOPATHIE_MULTIPLEX = [
    # Klassische Kombinationen
    "Arnica + Bellis perennis (Trauma)", "Aconitum + Belladonna (Fieber)",
    "Bryonia + Rhus tox (Bewegungsschmerz)", "Nux vomica + Lycopodium (Verdauung)",
    "Pulsatilla + Sepia (Hormone)", "Phosphorus + Carbo vegetabilis (Schwäche)",
    # Organ-Kombinationen
    "Chelidonium + Taraxacum (Leber)", "Solidago + Berberis (Niere)",
    "Crataegus + Cactus (Herz)", "Drosera + Spongia (Atemwege)",
]

TCM_REZEPTUREN_MULTIPLEX = [
    # Kombinierte Rezepturen
    "Liu Wei Di Huang Wan + Bu Zhong Yi Qi Tang", "Xiao Yao San + Si Wu Tang",
    "Ba Zhen Tang + Gui Pi Tang", "Wen Dan Tang + Ban Xia Hou Po Tang",
]

SPAGYRIK_MULTIPLEX = [
    # Organ-Kombinationen
    "Carduus marianus + Taraxacum + Chelidonium (Leber)",
    "Solidago + Equisetum + Juniperus (Niere)",
    "Crataegus + Arnica + Strophanthus (Herz)",
    # Psyche-Kombinationen
    "Hypericum + Melissa + Passiflora (Nervensystem)",
    "Avena sativa + Valeriana + Humulus (Schlaf)",
]

BACHBLUETEN_MULTIPLEX = [
    # 2er-Kombinationen
    "Impatiens + Vervain (Ungeduld)", "Mimulus + Aspen (Angst)",
    "Olive + Hornbeam (Erschöpfung)", "Pine + Crab Apple (Schuld)",
    # 3er-Kombinationen
    "Walnut + Honeysuckle + Wild Rose (Veränderung)",
    "Larch + Cerato + Scleranthus (Selbstvertrauen)",
    # 4er-Kombinationen
    "Gentian + Gorse + Sweet Chestnut + Mustard (Depression)",
]

SCHUESSLER_MULTIPLEX = [
    # 2er-Kombinationen
    "Nr. 3 + Nr. 7 (Magnesium phosphoricum + Ferrum phosphoricum - Schmerz)",
    "Nr. 5 + Nr. 9 (Kalium phosphoricum + Natrium phosphoricum - Nerven)",
    "Nr. 1 + Nr. 11 (Calcium fluoratum + Silicea - Bindegewebe)",
    # 3er-Kombinationen
    "Nr. 2 + Nr. 3 + Nr. 5 (Calcium + Magnesium + Kalium phosphoricum - Krämpfe)",
    "Nr. 4 + Nr. 8 + Nr. 10 (Kalium chloratum + Natrium chloratum + Natrium sulfuricum - Entgiftung)",
    # 4er-Kombinationen
    "Nr. 1 + Nr. 2 + Nr. 11 + Nr. 22 (Knochen-Komplex)",
]

PHYTOTHERAPIE_TEES_MULTIPLEX = [
    # Verdauung
    "Pfefferminze + Kamille + Fenchel (Verdauung)",
    "Anis + Fenchel + Kümmel (Blähungen)",
    # Atemwege
    "Thymian + Spitzwegerich + Eibisch (Husten)",
    "Holunder + Lindenblüten + Mädesüß (Erkältung)",
    # Beruhigung
    "Baldrian + Hopfen + Melisse (Schlaf)",
    "Johanniskraut + Lavendel + Passionsblume (Nervosität)",
]

PHYTOTHERAPIE_TINKTUREN_MULTIPLEX = [
    # Leber
    "Mariendistel + Löwenzahn + Artischocke (Leber)",
    # Niere
    "Goldrute + Birke + Brennnessel (Niere)",
    # Immunsystem
    "Echinacea + Propolis + Taigawurzel (Immunsystem)",
]

AROMATHERAPIE_MULTIPLEX = [
    # Entspannung
    "Lavendel + Bergamotte + Ylang-Ylang (Entspannung)",
    "Kamille römisch + Neroli + Sandelholz (Schlaf)",
    # Konzentration
    "Rosmarin + Pfefferminze + Zitrone (Konzentration)",
    # Atemwege
    "Eukalyptus + Thymian + Teebaum (Atemwege)",
]

ORTHOMOLEKULAR_MULTIPLEX = [
    # Basis-Kombinationen
    "Vitamin D3 + K2 + Magnesium (Knochen)",
    "B-Komplex + Magnesium + Zink (Nerven)",
    "Vitamin C + Zink + Selen (Immunsystem)",
    # Erweiterte Kombinationen
    "Omega-3 + Vitamin E + Coenzym Q10 (Herz)",
    "NAC + Glutathion + Alpha-Liponsäure (Entgiftung)",
]

FREQUENZ_CLARK_MULTIPLEX = [
    "Parasiten-Frequenzen kombiniert", "Bakterien-Frequenzen kombiniert",
    "Viren-Frequenzen kombiniert", "Pilz-Frequenzen kombiniert",
]

FREQUENZ_RIFE_MULTIPLEX = [
    "Krebs-Frequenzen kombiniert", "Lyme-Frequenzen kombiniert",
    "Detox-Frequenzen kombiniert",
]

FREQUENZ_SOLFEGGIO_MULTIPLEX = [
    "174 Hz + 285 Hz (Heilung)", "396 Hz + 417 Hz (Transformation)",
    "528 Hz + 639 Hz (Liebe)", "741 Hz + 852 Hz + 963 Hz (Spiritualität)",
]

# =============================================================================
# PHASE 2 VERFEINERUNGEN - SCHWINDEL, HERZ-KREISLAUF, ENDOKRIN
# =============================================================================

# SCHWINDEL - FEIN
SCHWINDEL_VESTIBULAR_FEIN = [
    "Benigner paroxysmaler Lagerungsschwindel (BPLS)",
    "Morbus Menière",
    "Vestibuläre Migräne",
    "Vestibularisneuritis",
    "Labyrinthitis",
    "Bogengangsdehiszenz",
    "Perilymphfistel",
    "Bilaterale Vestibulopathie",
    "Vestibularisschwannom (Akustikusneurinom)",
]

SCHWINDEL_ZENTRAL_FEIN = [
    "Vertebrobasiläre Insuffizienz",
    "Kleinhirninfarkt",
    "Kleinhirnblutung",
    "Multiple Sklerose (vestibulär)",
    "Basilarismigräne",
    "Hirnstammläsion",
    "Wallenberg-Syndrom",
    "Chiari-Malformation",
]

# HERZ-KREISLAUF - FEIN
KREISLAUF_FEIN = [
    # Arterien - Hauptgefäße
    "Aorta ascendens", "Aorta descendens", "Aortenbogen",
    "Arteria carotis communis", "Arteria carotis interna", "Arteria carotis externa",
    "Arteria vertebralis (links)", "Arteria vertebralis (rechts)",
    "Arteria basilaris",
    
    # Arterien - Koronar
    "Arteria coronaria (links)", "Arteria coronaria (rechts)",
    "Ramus interventricularis anterior", "Ramus circumflexus",
    
    # Arterien - Extremitäten
    "Arteria subclavia", "Arteria axillaris", "Arteria brachialis",
    "Arteria radialis", "Arteria ulnaris",
    "Arteria femoralis", "Arteria poplitea",
    "Arteria tibialis anterior", "Arteria tibialis posterior",
    
    # Venen - Hauptgefäße
    "Vena cava superior", "Vena cava inferior",
    "Vena jugularis interna", "Vena jugularis externa",
    "Vena subclavia", "Vena brachiocephalica",
    
    # Venen - Extremitäten
    "Vena saphena magna", "Vena saphena parva",
    "Vena femoralis", "Vena poplitea",
    
    # Mikrozirkulation
    "Kapillarbett", "Arteriolen", "Venolen",
    "Endothel", "Gefäßwand",
]

HERZ_FEIN = [
    # Vorhöfe
    "Rechter Vorhof", "Linker Vorhof",
    "Vorhofseptum",
    
    # Kammern
    "Rechte Kammer", "Linke Kammer",
    "Kammerseptum",
    
    # Klappen
    "Mitralklappe", "Aortenklappe",
    "Trikuspidalklappe", "Pulmonalklappe",
    
    # Reizleitungssystem
    "Sinusknoten", "AV-Knoten",
    "His-Bündel", "Tawara-Schenkel (links)", "Tawara-Schenkel (rechts)",
    "Purkinje-Fasern",
    
    # Koronarsystem
    "Koronararterien", "Koronarvenen",
    
    # Herzwand
    "Perikard", "Myokard", "Endokard",
    "Papillarmuskeln", "Chordae tendineae",
]

# ENDOKRINE SYSTEME - FEIN
SCHILDDRUESE_FEIN = [
    # Hormone
    "TSH (Thyreoidea-stimulierendes Hormon)",
    "T3 (Trijodthyronin)", "T4 (Thyroxin)",
    "Freies T3 (fT3)", "Freies T4 (fT4)",
    "Reverse T3 (rT3)",
    
    # Rezeptoren & Enzyme
    "TSH-Rezeptor", "Thyreoperoxidase (TPO)",
    "Deiodinase Typ 1 (D1)", "Deiodinase Typ 2 (D2)", "Deiodinase Typ 3 (D3)",
    
    # Strukturen
    "Schilddrüsenfollikel", "Thyreoglobulin",
    "C-Zellen (Calcitonin)",
    
    # Pathologien
    "Hashimoto-Thyreoiditis", "Morbus Basedow",
]

NEBENNIERE_FEIN = [
    # Rinde - Zonen
    "Nebennierenrinde (Zona glomerulosa)",
    "Nebennierenrinde (Zona fasciculata)",
    "Nebennierenrinde (Zona reticularis)",
    
    # Mark
    "Nebennierenmark",
    
    # Hormone - Glukokortikoide
    "Cortisol", "Cortison",
    
    # Hormone - Mineralokortikoide
    "Aldosteron",
    
    # Hormone - Androgene
    "DHEA (Dehydroepiandrosteron)", "DHEA-S",
    "Androstendion",
    
    # Hormone - Katecholamine
    "Adrenalin (Epinephrin)", "Noradrenalin (Norepinephrin)",
    "Dopamin",
    
    # Regulatoren
    "ACTH (Adrenocorticotropes Hormon)",
    "CRH (Corticotropin-Releasing-Hormon)",
]

HYPOPHYSE_FEIN = [
    # Vorderlappen (Adenohypophyse)
    "Hypophysenvorderlappen",
    "ACTH (Adrenocorticotropes Hormon)",
    "TSH (Thyreoidea-stimulierendes Hormon)",
    "FSH (Follikel-stimulierendes Hormon)",
    "LH (Luteinisierendes Hormon)",
    "Prolaktin",
    "Wachstumshormon (GH/Somatotropin)",
    
    # Hinterlappen (Neurohypophyse)
    "Hypophysenhinterlappen",
    "ADH (Antidiuretisches Hormon/Vasopressin)",
    "Oxytocin",
    
    # Regulatoren
    "GnRH (Gonadotropin-Releasing-Hormon)",
    "TRH (Thyrotropin-Releasing-Hormon)",
    "CRH (Corticotropin-Releasing-Hormon)",
    "GHRH (Growth-Hormone-Releasing-Hormon)",
    "Somatostatin",
]

# =============================================================================
# PHASE 3 VERFEINERUNGEN (OPTIONAL) - SINNESORGANE, MUSKULATUR, FASZIEN, BLUT
# =============================================================================

# SINNESORGANE - FEIN
AUGE_FEIN = [
    # Vorderer Augenabschnitt
    "Kornea (Hornhaut)", "Vorderkammer", "Iris", "Pupille",
    "Linse", "Ziliarmuskel", "Zonulafasern",
    
    # Hinterer Augenabschnitt
    "Glaskörper", "Retina (Netzhaut)",
    "Makula", "Fovea centralis",
    "Sehnerv (N. opticus)", "Papille",
    
    # Gefäßsystem
    "Arteria centralis retinae", "Vena centralis retinae",
    "Choroidea (Aderhaut)",
    
    # Augenmuskeln
    "M. rectus superior", "M. rectus inferior",
    "M. rectus medialis", "M. rectus lateralis",
    "M. obliquus superior", "M. obliquus inferior",
    
    # Tränenapparat
    "Tränendrüse", "Tränenkanal",
]

OHR_FEIN = [
    # Äußeres Ohr
    "Ohrmuschel (Auricula)", "Äußerer Gehörgang",
    
    # Mittelohr
    "Trommelfell", "Paukenhöhle",
    "Hammer (Malleus)", "Amboss (Incus)", "Steigbügel (Stapes)",
    "Eustachische Röhre (Tuba auditiva)",
    
    # Innenohr
    "Cochlea (Schnecke)", "Corti-Organ",
    "Vestibulum (Vorhof)", "Utriculus", "Sacculus",
    "Bogengänge (horizontal, anterior, posterior)",
    "Endolymphe", "Perilymphe",
    
    # Nerven
    "Hörnerv (N. cochlearis)",
    "Gleichgewichtsnerv (N. vestibularis)",
    "N. vestibulocochlearis (VIII)",
]

# MUSKULATUR - FEIN
MUSKULATUR_FEIN = [
    # Nacken/HWS
    "M. trapezius (Pars descendens)",
    "M. trapezius (Pars transversa)",
    "M. trapezius (Pars ascendens)",
    "M. sternocleidomastoideus",
    "M. scaleni (anterior, medius, posterior)",
    "M. levator scapulae",
    
    # Rücken
    "M. erector spinae", "M. multifidus",
    "M. latissimus dorsi", "M. rhomboideus",
    "M. serratus posterior",
    
    # Schulter
    "M. deltoideus", "M. supraspinatus",
    "M. infraspinatus", "M. teres minor",
    "M. subscapularis",
    
    # Beckenboden
    "M. levator ani", "M. coccygeus",
    "M. sphincter ani externus",
    
    # Bauch
    "M. rectus abdominis", "M. obliquus externus",
    "M. obliquus internus", "M. transversus abdominis",
]

# FASZIEN - FEIN
FASZIEN_FEIN = [
    # Kopf & Hals
    "Fascia cervicalis (superficialis)",
    "Fascia cervicalis (profunda)",
    
    # Rumpf
    "Fascia thoracolumbalis",
    "Fascia endothoracica",
    "Fascia transversalis",
    
    # Extremitäten
    "Fascia lata (Oberschenkel)",
    "Fascia cruris (Unterschenkel)",
    "Fascia plantaris (Fußsohle)",
    "Fascia antebrachii (Unterarm)",
    
    # Spezielle Faszien
    "Iliotibialband (IT-Band)",
    "Plantarfaszie",
]

# BLUT - FEIN
BLUT_FEIN = [
    # Zelluläre Bestandteile
    "Erythrozyten (rote Blutkörperchen)",
    "Leukozyten (weiße Blutkörperchen)",
    "Thrombozyten (Blutplättchen)",
    
    # Proteine
    "Hämoglobin", "Hämatokrit",
    "Albumin", "Globuline",
    "Fibrinogen", "Transferrin",
    
    # Eisen & Speicher
    "Ferritin", "Serumeisen",
    
    # Gerinnungsfaktoren
    "Faktor VIII", "Faktor IX", "Faktor X",
    "Prothrombin", "Thrombin",
    
    # Blutgruppen
    "ABO-System", "Rhesus-Faktor",
]

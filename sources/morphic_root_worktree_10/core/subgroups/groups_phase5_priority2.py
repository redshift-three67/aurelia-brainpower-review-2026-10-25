"""
Phase 5 - Priorität 2: Nährstoffmängel
Nur Labels - Raten werden automatisch durch Bruce Copen Algorithmen generiert!

6 GRUPPEN:
- Vitamine FEIN (detailliert)
- Mineralien & Spurenelemente FEIN (detailliert)
- Aminosäuren FEIN (detailliert)
- Fettsäuren FEIN (detailliert)
- Nährstoffmangel-Symptome FEIN
- Orthomolekular-Therapie MULTIPLEX
"""

# =============================================================================
# VITAMINE - DETAILLIERT FEIN
# =============================================================================

VITAMINE_DETAILLIERT_FEIN = [
    # Vitamin A
    "Vitamin A (Retinol)",
    "Beta-Carotin",
    "Vitamin A-Mangel",
    
    # B-Vitamine
    "Vitamin B1 (Thiamin)",
    "Vitamin B1-Mangel (Beriberi)",
    "Vitamin B2 (Riboflavin)",
    "Vitamin B2-Mangel",
    "Vitamin B3 (Niacin)",
    "Vitamin B3-Mangel (Pellagra)",
    "Vitamin B5 (Pantothensäure)",
    "Vitamin B5-Mangel",
    "Vitamin B6 (Pyridoxin)",
    "Vitamin B6-Mangel",
    "Vitamin B6-Überschuss",
    "Vitamin B7 (Biotin)",
    "Biotin-Mangel",
    "Vitamin B9 (Folsäure)",
    "Folsäure-Mangel",
    "5-MTHF (aktive Folsäure)",
    "MTHFR-Mutation (Folsäure-Stoffwechsel)",
    "Vitamin B12 (Cobalamin)",
    "Vitamin B12-Mangel",
    "Methylcobalamin (aktives B12)",
    "Adenosylcobalamin",
    "Intrinsic Factor-Mangel",
    
    # Vitamin C
    "Vitamin C (Ascorbinsäure)",
    "Vitamin C-Mangel (Skorbut)",
    "Liposomales Vitamin C",
    
    # Vitamin D
    "Vitamin D3 (Cholecalciferol)",
    "Vitamin D2 (Ergocalciferol)",
    "Vitamin D-Mangel",
    "25-OH-Vitamin D (Speicherform)",
    "1,25-OH-Vitamin D (aktive Form)",
    "Vitamin D-Rezeptor-Polymorphismus",
    
    # Vitamin E
    "Vitamin E (Tocopherol)",
    "Alpha-Tocopherol",
    "Gamma-Tocopherol",
    "Tocotrienole",
    "Vitamin E-Mangel",
    
    # Vitamin K
    "Vitamin K1 (Phyllochinon)",
    "Vitamin K2 (Menachinon)",
    "MK-4 (Menatetrenon)",
    "MK-7 (Menachinon-7)",
    "Vitamin K-Mangel",
]

# =============================================================================
# MINERALIEN & SPURENELEMENTE - DETAILLIERT FEIN
# =============================================================================

MINERALIEN_SPURENELEMENTE_DETAILLIERT_FEIN = [
    # Mengenelemente
    "Calcium",
    "Calcium-Mangel (Hypokalzämie)",
    "Calcium-Überschuss (Hyperkalzämie)",
    "Magnesium",
    "Magnesium-Mangel (Hypomagnesiämie)",
    "Magnesiumcitrat",
    "Magnesiumglycinat",
    "Magnesiummalat",
    "Kalium",
    "Kalium-Mangel (Hypokaliämie)",
    "Kalium-Überschuss (Hyperkaliämie)",
    "Natrium",
    "Natrium-Mangel (Hyponatriämie)",
    "Natrium-Überschuss (Hypernatriämie)",
    "Phosphor",
    "Phosphat-Mangel (Hypophosphatämie)",
    "Chlorid",
    "Schwefel (MSM)",
    
    # Spurenelemente
    "Eisen",
    "Eisen-Mangel (Anämie)",
    "Eisen-Überschuss (Hämochromatose)",
    "Ferritin niedrig",
    "Ferritin erhöht",
    "Zink",
    "Zink-Mangel",
    "Zink-Überschuss",
    "Kupfer",
    "Kupfer-Mangel",
    "Kupfer-Überschuss (Morbus Wilson)",
    "Zink-Kupfer-Ratio gestört",
    "Selen",
    "Selen-Mangel",
    "Selen-Überschuss",
    "Jod",
    "Jod-Mangel",
    "Jod-Überschuss",
    "Mangan",
    "Mangan-Mangel",
    "Chrom",
    "Chrom-Mangel",
    "Molybdän",
    "Molybdän-Mangel",
    "Bor",
    "Bor-Mangel",
    "Silizium",
    "Silizium-Mangel",
    "Lithium (Spurenelement)",
    "Vanadium",
    "Kobalt",
]

# =============================================================================
# AMINOSÄUREN - DETAILLIERT FEIN
# =============================================================================

AMINOSAEUREN_DETAILLIERT_FEIN = [
    # Essentielle Aminosäuren
    "L-Leucin",
    "L-Isoleucin",
    "L-Valin",
    "BCAA (verzweigtkettige Aminosäuren)",
    "L-Lysin",
    "L-Lysin-Mangel",
    "L-Methionin",
    "L-Phenylalanin",
    "L-Threonin",
    "L-Tryptophan",
    "Tryptophan-Mangel",
    "L-Histidin",
    
    # Semi-essentielle Aminosäuren
    "L-Arginin",
    "L-Arginin-Mangel",
    "L-Cystein",
    "N-Acetyl-Cystein (NAC)",
    "L-Tyrosin",
    "Tyrosin-Mangel",
    "L-Glutamin",
    "Glutamin-Mangel",
    
    # Nicht-essentielle Aminosäuren
    "L-Alanin",
    "L-Asparagin",
    "L-Asparaginsäure",
    "L-Glutaminsäure",
    "Glycin",
    "Glycin-Mangel",
    "L-Prolin",
    "L-Serin",
    
    # Spezielle Aminosäuren & Derivate
    "L-Carnitin",
    "Carnitin-Mangel",
    "Acetyl-L-Carnitin",
    "Taurin",
    "Taurin-Mangel",
    "L-Theanin",
    "GABA (Gamma-Aminobuttersäure)",
    "GABA-Mangel",
    "5-HTP (5-Hydroxytryptophan)",
    "SAMe (S-Adenosylmethionin)",
    "Kreatin",
    "Beta-Alanin",
]

# =============================================================================
# FETTSÄUREN - DETAILLIERT FEIN
# =============================================================================

FETTSAEUREN_DETAILLIERT_FEIN = [
    # Omega-3-Fettsäuren
    "Omega-3-Fettsäuren",
    "Omega-3-Mangel",
    "EPA (Eicosapentaensäure)",
    "DHA (Docosahexaensäure)",
    "ALA (Alpha-Linolensäure)",
    "EPA/DHA-Ratio",
    
    # Omega-6-Fettsäuren
    "Omega-6-Fettsäuren",
    "Linolsäure",
    "Gamma-Linolensäure (GLA)",
    "Arachidonsäure",
    "Omega-6/Omega-3-Ratio gestört",
    
    # Omega-9-Fettsäuren
    "Omega-9-Fettsäuren",
    "Ölsäure",
    
    # Weitere essentielle Fettsäuren
    "CLA (Konjugierte Linolsäure)",
    "MCT-Öl (Mittelkettige Triglyceride)",
    "Caprylsäure (C8)",
    "Caprinsäure (C10)",
    "Laurinsäure (C12)",
    
    # Phospholipide
    "Phosphatidylcholin",
    "Phosphatidylserin",
    "Phosphatidylethanolamin",
    "Phosphatidylinositol",
    
    # Spezielle Lipide
    "Sphingomyelin",
    "Cholesterin (essentiell)",
    "Cholesterin-Mangel",
]

# =============================================================================
# NÄHRSTOFFMANGEL-SYMPTOME FEIN
# =============================================================================

NAEHRSTOFFMANGEL_SYMPTOME_FEIN = [
    "Müdigkeit (Nährstoffmangel)",
    "Erschöpfung (chronisch)",
    "Konzentrationsstörungen (Nährstoffmangel)",
    "Gedächtnisstörungen (Nährstoffmangel)",
    "Depressive Verstimmung (Nährstoffmangel)",
    "Reizbarkeit (Nährstoffmangel)",
    "Schlafstörungen (Nährstoffmangel)",
    "Haarausfall (Nährstoffmangel)",
    "Brüchige Nägel",
    "Trockene Haut (Nährstoffmangel)",
    "Hautprobleme (Nährstoffmangel)",
    "Muskelkrämpfe (Nährstoffmangel)",
    "Muskelschwäche (Nährstoffmangel)",
    "Gelenkschmerzen (Nährstoffmangel)",
    "Knochenschmerzen (Nährstoffmangel)",
    "Osteoporose (Nährstoffmangel)",
    "Immunschwäche (Nährstoffmangel)",
    "Infektanfälligkeit (Nährstoffmangel)",
    "Wundheilungsstörungen (Nährstoffmangel)",
    "Blutarmut (Anämie)",
    "Blässe",
    "Schwindel (Nährstoffmangel)",
    "Herzrhythmusstörungen (Nährstoffmangel)",
    "Nervosität (Nährstoffmangel)",
    "Kribbeln (Nährstoffmangel)",
    "Taubheitsgefühle (Nährstoffmangel)",
    "Sehstörungen (Nährstoffmangel)",
    "Nachtblindheit",
    "Zahnfleischbluten (Nährstoffmangel)",
    "Mundwinkelrhagaden",
]

# =============================================================================
# ORTHOMOLEKULAR-THERAPIE MULTIPLEX
# =============================================================================

ORTHOMOLEKULAR_THERAPIE_MULTIPLEX = [
    "Vitamin B-Komplex + Magnesium (Stress)",
    "Vitamin D3 + K2 + Magnesium (Knochen)",
    "Vitamin C + Zink + Selen (Immunsystem)",
    "Omega-3 + Vitamin E (Entzündung)",
    "Eisen + Vitamin C + Folsäure (Anämie)",
    "Magnesium + Vitamin B6 (Nerven)",
    "Calcium + Vitamin D3 + K2 (Osteoporose)",
    "B12 + Folsäure + B6 (Homocystein)",
    "Zink + Selen + Vitamin A (Haut)",
    "Coenzym Q10 + Magnesium (Herz)",
    "NAC + Glutathion + Selen (Entgiftung)",
    "L-Carnitin + Coenzym Q10 (Energie)",
    "5-HTP + Magnesium + B6 (Stimmung)",
    "GABA + L-Theanin + Magnesium (Entspannung)",
    "Kreatin + BCAA + Glutamin (Muskulatur)",
]

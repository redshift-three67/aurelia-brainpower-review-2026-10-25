"""
Phase 5 - Priorität 5: Weitere Systeme (Miasmatik, Umwelt, Organe, Altersspezifisch)
Nur Labels - Raten werden automatisch durch Bruce Copen Algorithmen generiert!

9 GRUPPEN:
- Miasmatik FEIN
- Umweltbelastungen erweitert FEIN
- Urogenitalsystem FEIN
- Haut detailliert FEIN
- Kinderkrankheiten FEIN
- Schwangerschaft & Geburt FEIN
- Wechseljahre detailliert FEIN
- Altersbeschwerden FEIN
- Miasmatik-Remedies MULTIPLEX
"""

# =============================================================================
# MIASMATIK FEIN
# =============================================================================

MIASMATIK_FEIN = [
    # Klassische Miasmen (Hahnemann)
    "Psora-Miasma",
    "Psora (Hautmiasma)",
    "Psora (Mangel-Miasma)",
    "Sykose-Miasma",
    "Sykose (Wucherungs-Miasma)",
    "Sykose (Gonorrhoe-Miasma)",
    "Syphilis-Miasma",
    "Syphilis (Destruktions-Miasma)",
    
    # Moderne Miasmen
    "Tuberkulinie-Miasma",
    "Tuberkulinie (Tuberkulose-Miasma)",
    "Carcinogenie-Miasma",
    "Carcinogenie (Krebs-Miasma)",
    
    # Erb-Belastungen
    "Erb-Belastung (väterlich)",
    "Erb-Belastung (mütterlich)",
    "Transgenerationale Belastung",
    "Epigenetische Belastung",
    
    # Konstitutionelle Schwächen
    "Konstitutionelle Schwäche (Lunge)",
    "Konstitutionelle Schwäche (Verdauung)",
    "Konstitutionelle Schwäche (Nerven)",
    "Konstitutionelle Schwäche (Immunsystem)",
    "Konstitutionelle Schwäche (Knochen)",
]

# =============================================================================
# UMWELTBELASTUNGEN ERWEITERT FEIN
# =============================================================================

UMWELTBELASTUNGEN_ERWEITERT_FEIN = [
    # Wasserbelastungen
    "Chlor (Trinkwasser)",
    "Fluorid (Trinkwasser)",
    "Medikamentenrückstände (Wasser)",
    "Antibiotika-Rückstände (Wasser)",
    "Hormone (Wasser)",
    "Pestizide (Wasser)",
    "Schwermetalle (Wasser)",
    "Mikroplastik (Wasser)",
    "Nitrat (Wasser)",
    "Bakterien (Wasser)",
    
    # Bodenbelastungen
    "Pestizide (Boden)",
    "Herbizide (Boden)",
    "Fungizide (Boden)",
    "Schwermetalle (Boden)",
    "Mikroplastik (Boden)",
    
    # Elektrosmog-Details
    "50 Hz (Netzfrequenz)",
    "16,7 Hz (Bahnstrom)",
    "Dirty Electricity",
    "Elektrosmog (gepulst)",
    "Elektrosmog (moduliert)",
    "Magnetfelder (statisch)",
    "Magnetfelder (wechselnd)",
    
    # Luftverschmutzung
    "Feinstaub PM10",
    "Feinstaub PM2.5",
    "Ultrafeinstaub PM0.1",
    "Stickoxide (NOx)",
    "Schwefeldioxid (SO2)",
    "Ozon (O3)",
    "Kohlenmonoxid (CO)",
    "Ruß",
]

# =============================================================================
# UROGENITALSYSTEM FEIN
# =============================================================================

UROGENITALSYSTEM_FEIN = [
    # Niere (detailliert)
    "Nierensteine",
    "Nierenkolik",
    "Nierenbeckenentzündung (Pyelonephritis)",
    "Glomerulonephritis",
    "Nephrotisches Syndrom",
    "Niereninsuffizienz (akut)",
    "Niereninsuffizienz (chronisch)",
    "Polyzystische Nierenerkrankung",
    
    # Blase
    "Blasenentzündung (Zystitis)",
    "Blasenentzündung (chronisch)",
    "Interstitielle Zystitis",
    "Reizblase",
    "Blasensteine",
    "Blasenschwäche",
    "Harninkontinenz (Belastungsinkontinenz)",
    "Harninkontinenz (Dranginkontinenz)",
    
    # Harnwege
    "Harnwegsinfektion",
    "Harnröhrenentzündung (Urethritis)",
    "Harnleiterentzündung",
    
    # Prostata (Männer)
    "Prostatitis (akut)",
    "Prostatitis (chronisch)",
    "Benigne Prostatahyperplasie (BPH)",
    "Prostatavergrößerung",
    
    # Geschlechtsorgane (Männer)
    "Hodenentzündung (Orchitis)",
    "Nebenhodenentzündung (Epididymitis)",
    "Erektile Dysfunktion",
    "Vorzeitiger Samenerguss",
    "Unfruchtbarkeit (männlich)",
    
    # Geschlechtsorgane (Frauen)
    "Endometriose",
    "Myome (Gebärmutter)",
    "Eierstockzysten",
    "Polyzystisches Ovarialsyndrom (PCOS)",
    "Adnexitis (Eileiterentzündung)",
    "Vaginitis",
    "Scheidenpilz (Candida)",
    "Bakterielle Vaginose",
    "Menstruationsbeschwerden",
    "Prämenstruelles Syndrom (PMS)",
    "Unfruchtbarkeit (weiblich)",
]

# =============================================================================
# HAUT DETAILLIERT FEIN
# =============================================================================

HAUT_DETAILLIERT_FEIN = [
    # Ekzeme
    "Neurodermitis (Atopisches Ekzem)",
    "Kontaktekzem",
    "Seborrhoisches Ekzem",
    "Dyshidrotisches Ekzem",
    "Nummuläres Ekzem",
    
    # Psoriasis
    "Psoriasis vulgaris (Schuppenflechte)",
    "Psoriasis guttata",
    "Psoriasis pustulosa",
    "Psoriasis inversa",
    
    # Akne
    "Akne vulgaris",
    "Akne comedonica",
    "Akne papulopustulosa",
    "Akne conglobata",
    "Akne rosacea (Rosazea)",
    
    # Infektionen
    "Impetigo",
    "Erysipel (Wundrose)",
    "Phlegmone",
    "Abszess (Haut)",
    "Furunkel",
    "Karbunkel",
    "Herpes simplex (Haut)",
    "Herpes zoster (Gürtelrose)",
    "Warzen (viral)",
    "Dellwarzen (Mollusca contagiosa)",
    
    # Pilzinfektionen
    "Fußpilz (Tinea pedis)",
    "Nagelpilz (Onychomykose)",
    "Hautpilz (Tinea corporis)",
    "Kleienpilzflechte (Pityriasis versicolor)",
    
    # Weitere Hauterkrankungen
    "Urtikaria (Nesselsucht)",
    "Vitiligo (Weißfleckenkrankheit)",
    "Lichen ruber",
    "Lichen sclerosus",
]

# =============================================================================
# KINDERKRANKHEITEN FEIN
# =============================================================================

KINDERKRANKHEITEN_FEIN = [
    "Masern",
    "Mumps",
    "Röteln",
    "Windpocken (Varizellen)",
    "Scharlach",
    "Keuchhusten (Pertussis)",
    "Dreitagefieber (Roseola infantum)",
    "Ringelröteln (Parvovirus B19)",
    "Hand-Fuß-Mund-Krankheit",
    "Pfeiffersches Drüsenfieber (EBV)",
    "Pseudokrupp",
    "RS-Virus-Infektion",
    "Kawasaki-Syndrom",
    "Drei-Monats-Koliken",
    "Zahnen",
    "Wachstumsschmerzen",
    "ADHS (Aufmerksamkeitsdefizit)",
    "Autismus-Spektrum-Störung",
]

# =============================================================================
# SCHWANGERSCHAFT & GEBURT FEIN
# =============================================================================

SCHWANGERSCHAFT_GEBURT_FEIN = [
    # Schwangerschaftsbeschwerden
    "Übelkeit (Schwangerschaft)",
    "Erbrechen (Schwangerschaft)",
    "Hyperemesis gravidarum",
    "Sodbrennen (Schwangerschaft)",
    "Verstopfung (Schwangerschaft)",
    "Hämorrhoiden (Schwangerschaft)",
    "Rückenschmerzen (Schwangerschaft)",
    "Ischias (Schwangerschaft)",
    "Wassereinlagerungen (Schwangerschaft)",
    "Krampfadern (Schwangerschaft)",
    "Müdigkeit (Schwangerschaft)",
    "Schlafstörungen (Schwangerschaft)",
    "Stimmungsschwankungen (Schwangerschaft)",
    
    # Schwangerschaftskomplikationen
    "Schwangerschaftsdiabetes",
    "Gestose (Präeklampsie)",
    "HELLP-Syndrom",
    "Plazentainsuffizienz",
    "Vorzeitige Wehen",
    "Frühgeburt-Risiko",
    
    # Geburt
    "Geburtsvorbereitung",
    "Wehenschwäche",
    "Geburtstrauma (Mutter)",
    "Geburtstrauma (Kind)",
    "Dammriss",
    "Kaiserschnitt-Narbe",
    
    # Wochenbett
    "Wochenbett-Depression",
    "Milchstau",
    "Mastitis (Brustentzündung)",
    "Stillprobleme",
    "Rückbildung",
]

# =============================================================================
# WECHSELJAHRE DETAILLIERT FEIN
# =============================================================================

WECHSELJAHRE_DETAILLIERT_FEIN = [
    # Perimenopause
    "Perimenopause",
    "Zyklusstörungen (Perimenopause)",
    "Starke Blutungen (Perimenopause)",
    
    # Menopause
    "Menopause",
    "Hitzewallungen",
    "Nachtschweiß",
    "Schweißausbrüche",
    "Schlafstörungen (Menopause)",
    "Stimmungsschwankungen (Menopause)",
    "Reizbarkeit (Menopause)",
    "Depressive Verstimmung (Menopause)",
    "Angst (Menopause)",
    "Konzentrationsstörungen (Menopause)",
    "Gedächtnisstörungen (Menopause)",
    
    # Körperliche Veränderungen
    "Scheidentrockenheit",
    "Libidoverlust (Menopause)",
    "Gewichtszunahme (Menopause)",
    "Haarausfall (Menopause)",
    "Hautveränderungen (Menopause)",
    "Gelenkschmerzen (Menopause)",
    "Osteoporose (Menopause)",
    "Herzrasen (Menopause)",
    "Schwindel (Menopause)",
    
    # Postmenopause
    "Postmenopause",
    "Urogenitale Atrophie",
]

# =============================================================================
# ALTERSBESCHWERDEN FEIN
# =============================================================================

ALTERSBESCHWERDEN_FEIN = [
    "Altersschwäche (allgemein)",
    "Gebrechlichkeit (Frailty)",
    "Sarkopenie (Muskelabbau)",
    "Osteoporose (Alter)",
    "Arthrose (Alter)",
    "Sturzgefahr",
    "Gangstörungen",
    "Gleichgewichtsstörungen (Alter)",
    "Sehschwäche (Alter)",
    "Makuladegeneration",
    "Grauer Star (Katarakt)",
    "Grüner Star (Glaukom)",
    "Schwerhörigkeit (Alter)",
    "Altersschwerhörigkeit (Presbyakusis)",
    "Gedächtnisstörungen (Alter)",
    "Demenz",
    "Alzheimer-Krankheit",
    "Vaskuläre Demenz",
    "Parkinson-Krankheit",
    "Inkontinenz (Alter)",
    "Prostatavergrößerung (Alter)",
    "Schlafstörungen (Alter)",
    "Appetitlosigkeit (Alter)",
    "Mangelernährung (Alter)",
    "Einsamkeit (Alter)",
    "Depression (Alter)",
]

# =============================================================================
# MIASMATIK-REMEDIES MULTIPLEX
# =============================================================================

MIASMATIK_REMEDIES_MULTIPLEX = [
    "Sulfur + Psorinum (Psora-Miasma)",
    "Thuja + Medorrhinum (Sykose-Miasma)",
    "Mercurius + Syphilinum (Syphilis-Miasma)",
    "Tuberculinum + Bacillinum (Tuberkulinie-Miasma)",
    "Carcinosinum + Scirrhinum (Carcinogenie-Miasma)",
    "Psorinum + Sulfur + Thuja (Miasmen-Kombination)",
]

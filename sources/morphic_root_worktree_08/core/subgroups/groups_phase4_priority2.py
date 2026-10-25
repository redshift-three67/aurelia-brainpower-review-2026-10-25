"""
Phase 4 - Priorität 2: Strahlung, Entgiftung, Verdauung, Toxine
Nur Labels - Raten werden automatisch durch Bruce Copen Algorithmen generiert!

Bereiche:
- C) Strahlung & Geopathie (4 Gruppen)
- D) Entgiftung (3 Gruppen)
- E) Verdauung (3 Gruppen)
- I) Toxine & Schwermetalle (4 Gruppen)
"""

# =============================================================================
# C) STRAHLUNG & GEOPATHIE - 4 GRUPPEN
# =============================================================================

STRAHLUNG_SYMPTOME_FEIN = [
    "Elektrosensibilität",
    "EMF-Kopfschmerzen",
    "EMF-Schlafstörungen",
    "EMF-Müdigkeit",
    "EMF-Konzentrationsstörungen",
    "EMF-Herzrhythmusstörungen",
    "EMF-Tinnitus",
    "Strahlenkater",
    "Oxidativer Stress (EMF)",
    "Zellmembran-Schädigung (EMF)",
    "DNA-Schädigung (EMF)",
    "Mitochondrien-Dysfunktion (EMF)",
]

STRAHLUNG_QUELLEN_FEIN = [
    "WLAN 2.4 GHz",
    "WLAN 5 GHz",
    "WLAN 6 GHz",
    "Mobilfunk 3G (UMTS)",
    "Mobilfunk 4G (LTE)",
    "Mobilfunk 5G (Sub-6 GHz)",
    "Mobilfunk 5G (mmWave)",
    "Bluetooth",
    "DECT-Telefon",
    "Mikrowelle (2.45 GHz)",
    "Radar",
    "Hochspannungsleitung (50 Hz)",
    "Bahnstrom (16.7 Hz)",
    "Transformatoren",
    "Smart Meter",
    "LED-Flimmern",
    "Bildschirm-Strahlung",
    "Röntgenstrahlung (diagnostisch)",
    "CT-Strahlung",
    "Radioaktivität (Radon)",
    "Radioaktivität (Cäsium-137)",
    "Radioaktivität (Strontium-90)",
    "UV-Strahlung (UVA)",
    "UV-Strahlung (UVB)",
    "UV-Strahlung (UVC)",
]

GEOPATHIE_FEIN = [
    "Wasserader (linksdrehend)",
    "Wasserader (rechtsdrehend)",
    "Wasserader-Kreuzung",
    "Verwerfung (geologisch)",
    "Gesteinsbruch",
    "Erdstrahlung",
    "Curry-Gitter",
    "Hartmann-Gitter",
    "Benker-Kuben-System",
    "Globalgitter",
    "Radon-Belastung",
    "Erdmagnetfeld-Anomalie",
]

STRAHLUNG_SCHUTZ_MULTIPLEX = [
    "Cadmium sulfuratum + X-Ray (Röntgen-Schutz)",
    "Radium bromatum + Plutonium (Radioaktivität)",
    "Phosphorus + Silicea (EMF-Schutz)",
    "Kalium phosphoricum + Magnesium phosphoricum (Elektrosensibilität)",
]

# =============================================================================
# D) ENTGIFTUNG - 3 GRUPPEN
# =============================================================================

ENTGIFTUNG_SYMPTOME_FEIN = [
    "Entgiftungs-Kopfschmerzen",
    "Entgiftungs-Müdigkeit",
    "Entgiftungs-Übelkeit",
    "Entgiftungs-Hautausschlag",
    "Entgiftungs-Durchfall",
    "Entgiftungs-Verstopfung",
    "Entgiftungs-Schwitzen",
    "Entgiftungs-Mundgeruch",
    "Entgiftungs-Körpergeruch",
    "Herxheimer-Reaktion",
    "Leberstau",
    "Gallenstau",
    "Nierenstau",
    "Lymphstau",
    "Darmträgheit",
]

ENTGIFTUNG_ORGANE_FEIN = [
    "Leber (Hepatozyten)",
    "Leber (Kupffer-Zellen)",
    "Leber (Gallenkanälchen)",
    "Gallenblase",
    "Gallenwege",
    "Niere (Glomerulus)",
    "Niere (Tubulus)",
    "Niere (Sammelrohr)",
    "Haut (Schweißdrüsen)",
    "Haut (Talgdrüsen)",
    "Lymphe (Lymphknoten)",
    "Lymphe (Lymphgefäße)",
    "Darm (Enterozyten)",
    "Darm (Darmschleimhaut)",
    "Lunge (Alveolen)",
]

ENTGIFTUNG_REMEDIES_MULTIPLEX = [
    "Carduus marianus + Taraxacum (Leber-Entgiftung)",
    "Nux vomica + Lycopodium (Leber-Galle)",
    "Berberis + Solidago (Nieren-Entgiftung)",
    "Sulfur + Graphites (Haut-Entgiftung)",
    "Chelidonium + Carduus marianus (Gallen-Entgiftung)",
]

# =============================================================================
# E) VERDAUUNG - 3 GRUPPEN
# =============================================================================

VERDAUUNG_SYMPTOME_FEIN = [
    "Sodbrennen",
    "Reflux",
    "Übelkeit",
    "Erbrechen",
    "Magenschmerzen",
    "Magenkrämpfe",
    "Völlegefühl",
    "Blähungen (Meteorismus)",
    "Flatulenz",
    "Aufstoßen",
    "Durchfall (akut)",
    "Durchfall (chronisch)",
    "Verstopfung (akut)",
    "Verstopfung (chronisch)",
    "Reizdarm-Syndrom (IBS-D)",
    "Reizdarm-Syndrom (IBS-C)",
    "Reizdarm-Syndrom (IBS-M)",
    "Bauchschmerzen (Oberbauch)",
    "Bauchschmerzen (Unterbauch)",
    "Bauchkrämpfe",
    "Darmgeräusche",
    "Stuhlunregelmäßigkeiten",
    "Blut im Stuhl",
    "Schleim im Stuhl",
    "Fettstuhl (Steatorrhoe)",
    "Unverdaute Nahrung im Stuhl",
]

VERDAUUNG_PATHOLOGIEN_FEIN = [
    "Gastritis (akut)",
    "Gastritis (chronisch)",
    "Gastritis (Typ A - autoimmun)",
    "Gastritis (Typ B - Helicobacter)",
    "Gastritis (Typ C - chemisch)",
    "Magenulkus",
    "Duodenalulkus",
    "Refluxösophagitis",
    "Barrett-Ösophagus",
    "Zöliakie",
    "Laktoseintoleranz",
    "Fruktoseintoleranz",
    "Histaminintoleranz",
    "SIBO (Small Intestinal Bacterial Overgrowth)",
    "Leaky Gut Syndrom",
    "Morbus Crohn",
    "Colitis ulcerosa",
    "Divertikulose",
    "Divertikulitis",
    "Hämorrhoiden",
    "Analfissur",
    "Pankreatitis (akut)",
    "Pankreatitis (chronisch)",
    "Gallensteine",
    "Cholezystitis",
    "Fettleber (NAFLD)",
    "Leberzirrhose",
]

VERDAUUNG_REMEDIES_MULTIPLEX = [
    "Nux vomica + Lycopodium (Verdauungsschwäche)",
    "Carbo vegetabilis + Lycopodium (Blähungen)",
    "Arsenicum album + Veratrum album (Durchfall)",
    "Nux vomica + Bryonia (Verstopfung)",
    "Chamomilla + Colocynthis (Bauchkrämpfe)",
    "Pulsatilla + Nux vomica (Reizdarm)",
]

# =============================================================================
# I) TOXINE & SCHWERMETALLE - 4 GRUPPEN
# =============================================================================

TOXINE_SYMPTOME_FEIN = [
    "Vergiftungs-Kopfschmerzen",
    "Vergiftungs-Übelkeit",
    "Vergiftungs-Erbrechen",
    "Vergiftungs-Durchfall",
    "Vergiftungs-Schwindel",
    "Vergiftungs-Müdigkeit",
    "Vergiftungs-Konzentrationsstörungen",
    "Vergiftungs-Gedächtnisstörungen",
    "Schwermetall-Tremor",
    "Schwermetall-Polyneuropathie",
    "Schwermetall-Hautveränderungen",
    "Schwermetall-Nierenschäden",
    "Schwermetall-Leberschäden",
    "Chemikalien-Sensitivität (MCS)",
    "Chronische Vergiftung",
    "Akute Vergiftung",
    "Metallgeschmack im Mund",
    "Toxische Enzephalopathie",
]

SCHWERMETALLE_DETAILLIERT_FEIN = [
    "Quecksilber (Hg)",
    "Blei (Pb)",
    "Cadmium (Cd)",
    "Arsen (As)",
    "Aluminium (Al)",
    "Nickel (Ni)",
    "Chrom (Cr)",
    "Kupfer (Cu - toxisch)",
    "Zink (Zn - toxisch)",
    "Eisen (Fe - toxisch)",
    "Mangan (Mn - toxisch)",
    "Kobalt (Co)",
    "Thallium (Tl)",
    "Antimon (Sb)",
    "Barium (Ba)",
    "Beryllium (Be)",
    "Platin (Pt)",
    "Palladium (Pd)",
    "Zinn (Sn)",
    "Uran (U)",
]

CHEMIKALIEN_DETAILLIERT_FEIN = [
    "Glyphosat",
    "Organophosphate (Pestizide)",
    "Pyrethroide (Pestizide)",
    "DDT (Dichlordiphenyltrichlorethan)",
    "Atrazin",
    "Formaldehyd",
    "Benzol",
    "Toluol",
    "Xylol",
    "Styrol",
    "Weichmacher (Phthalate)",
    "Bisphenol A (BPA)",
    "Bisphenol S (BPS)",
    "PCB (Polychlorierte Biphenyle)",
    "Dioxine",
    "Furane",
    "PAK (Polyzyklische aromatische Kohlenwasserstoffe)",
    "VOC (Flüchtige organische Verbindungen)",
    "Lösungsmittel (allgemein)",
    "Chlorierte Kohlenwasserstoffe",
]

TOXINE_REMEDIES_MULTIPLEX = [
    "Nux vomica + Sulfur (Allgemeine Entgiftung)",
    "Hepar sulfuris + Silicea (Schwermetall-Ausleitung)",
    "Arsenicum album + Carbo vegetabilis (Akute Vergiftung)",
    "Lycopodium + Chelidonium (Leber-Entgiftung)",
    "Berberis + Solidago (Nieren-Entgiftung)",
    "Graphites + Petroleum (Chemikalien-Sensitivität)",
]

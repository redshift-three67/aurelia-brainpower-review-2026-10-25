"""
Phase 4 - Priorität 3: Knochen, Atmung, Hormone, Luftbelastungen, Nahrungsmittel
Nur Labels - Raten werden automatisch durch Bruce Copen Algorithmen generiert!

Bereiche:
- H) Knochen & Gelenke (3 Gruppen)
- J) Atmung (3 Gruppen)
- K) Hormonelles System (4 Gruppen)
- L) Luftbelastungen & Wohnraumgifte (3 Gruppen)
- M) Nahrungsmittelbelastungen (3 Gruppen)
"""

# =============================================================================
# H) KNOCHEN & GELENKE - 3 GRUPPEN
# =============================================================================

KNOCHEN_SYMPTOME_FEIN = [
    "Knochenschmerzen (generalisiert)",
    "Knochenschmerzen (Wirbelsäule)",
    "Knochenschmerzen (Rippen)",
    "Knochenschmerzen (Becken)",
    "Knochenschmerzen (Oberschenkel)",
    "Knochenschmerzen (Unterschenkel)",
    "Gelenkschmerzen (Schulter)",
    "Gelenkschmerzen (Ellbogen)",
    "Gelenkschmerzen (Handgelenk)",
    "Gelenkschmerzen (Finger)",
    "Gelenkschmerzen (Hüfte)",
    "Gelenkschmerzen (Knie)",
    "Gelenkschmerzen (Sprunggelenk)",
    "Gelenkschmerzen (Zehen)",
    "Gelenkschwellung",
    "Gelenksteifigkeit (morgens)",
    "Gelenkerguss",
    "Knochenbruch-Schmerzen",
    "Knochenheilung verzögert",
]

KNOCHEN_PATHOLOGIEN_FEIN = [
    "Osteoporose (generalisiert)",
    "Osteoporose (Wirbelsäule)",
    "Osteoporose (Hüfte)",
    "Osteopenie",
    "Osteomalazie",
    "Rachitis",
    "Morbus Paget",
    "Osteomyelitis",
    "Arthrose (Schulter)",
    "Arthrose (Ellbogen)",
    "Arthrose (Handgelenk)",
    "Arthrose (Finger)",
    "Arthrose (Hüfte - Coxarthrose)",
    "Arthrose (Knie - Gonarthrose)",
    "Arthrose (Sprunggelenk)",
    "Rheumatoide Arthritis",
    "Psoriasis-Arthritis",
    "Gicht (Hyperurikämie)",
    "Pseudogicht (Chondrokalzinose)",
    "Morbus Bechterew (Spondylitis ankylosans)",
    "Fibromyalgie",
    "Polymyalgia rheumatica",
    "Knochenmetastasen",
]

KNOCHEN_REMEDIES_MULTIPLEX = [
    "Calcium fluoratum + Silicea (Knochen-Stärkung)",
    "Rhus toxicodendron + Bryonia (Gelenkschmerzen)",
    "Symphytum + Calcium phosphoricum (Knochenbruch-Heilung)",
    "Colchicum + Ledum (Gicht)",
    "Ruta + Rhus toxicodendron (Arthrose)",
    "Arnica + Hypericum (Gelenk-Trauma)",
]

# =============================================================================
# J) ATMUNG - 3 GRUPPEN
# =============================================================================

ATMUNG_SYMPTOME_FEIN = [
    "Atemnot (Dyspnoe)",
    "Atemnot bei Belastung",
    "Atemnot in Ruhe",
    "Kurzatmigkeit",
    "Husten (trocken)",
    "Husten (produktiv)",
    "Husten (chronisch)",
    "Husten (nächtlich)",
    "Auswurf (schleimig)",
    "Auswurf (eitrig)",
    "Auswurf (blutig)",
    "Giemen (Wheezing)",
    "Brummen (Bronchialobstruktion)",
    "Pfeifende Atmung",
    "Asthma-Anfall",
    "Erstickungsgefühl",
    "Engegefühl in der Brust",
    "Hyperventilation",
]

ATMUNG_PATHOLOGIEN_FEIN = [
    "Asthma bronchiale",
    "Asthma (allergisch)",
    "Asthma (nicht-allergisch)",
    "COPD (Chronisch obstruktive Lungenerkrankung)",
    "Chronische Bronchitis",
    "Emphysem",
    "Bronchitis (akut)",
    "Bronchitis (chronisch)",
    "Pneumonie (bakteriell)",
    "Pneumonie (viral)",
    "Pneumonie (atypisch)",
    "Lungenembolie",
    "Lungenfibrose",
    "Sarkoidose",
    "Pleuritis",
    "Pleuraerguss",
    "Pneumothorax",
    "Lungenödem",
    "Schlafapnoe",
    "Hyperventilationssyndrom",
]

ATMUNG_REMEDIES_MULTIPLEX = [
    "Antimonium tartaricum + Ipecacuanha (Husten mit Schleim)",
    "Bryonia + Phosphorus (trockener Husten)",
    "Arsenicum album + Carbo vegetabilis (Atemnot)",
    "Drosera + Cuprum metallicum (Krampfhusten)",
    "Spongia + Hepar sulfuris (Krupp-Husten)",
]

# =============================================================================
# K) HORMONELLES SYSTEM - 4 GRUPPEN
# =============================================================================

HORMONE_SYMPTOME_FEIN = [
    "Hormonelle Dysbalance",
    "Hitzewallungen",
    "Nachtschweiß",
    "Stimmungsschwankungen (hormonell)",
    "Gewichtszunahme (hormonell)",
    "Gewichtsabnahme (hormonell)",
    "Libidoverlust",
    "Erektionsstörungen",
    "Zyklusstörungen",
    "Amenorrhoe",
    "Dysmenorrhoe",
    "PMS (Prämenstruelles Syndrom)",
    "PMDS (Prämenstruelle dysphorische Störung)",
    "Unfruchtbarkeit (hormonell)",
    "Haarausfall (hormonell)",
    "Hirsutismus",
    "Akne (hormonell)",
    "Müdigkeit (hormonell)",
    "Schlafstörungen (hormonell)",
    "Depressionen (hormonell)",
    "Angst (hormonell)",
    "Konzentrationsstörungen (hormonell)",
    "Wassereinlagerungen (hormonell)",
    "Brustspannen",
    "Gynäkomastie",
]

HORMONE_SCHILDDRUESE_FEIN = [
    "Hypothyreose",
    "Hyperthyreose",
    "Hashimoto-Thyreoiditis",
    "Morbus Basedow",
    "Struma (Kropf)",
    "Schilddrüsenknoten",
    "Schilddrüsenunterfunktion (subklinisch)",
    "Schilddrüsenüberfunktion (subklinisch)",
    "TSH erhöht",
    "TSH erniedrigt",
    "T3 erniedrigt",
    "T4 erniedrigt",
    "fT3 erniedrigt",
    "fT4 erniedrigt",
    "Schilddrüsen-Antikörper (TPO-AK)",
]

HORMONE_GESCHLECHT_FEIN = [
    "Östrogendominanz",
    "Östrogenmangel",
    "Progesteronmangel",
    "Testosteronmangel (Männer)",
    "Testosteronmangel (Frauen)",
    "Testosteron erhöht (Frauen)",
    "DHEA-Mangel",
    "PCOS (Polyzystisches Ovarialsyndrom)",
    "Endometriose",
    "Wechseljahre (Menopause)",
    "Perimenopause",
    "Prämenopause",
    "Andropause",
    "Nebennierenschwäche",
    "Cortisol erhöht",
    "Cortisol erniedrigt",
    "Insulin-Resistenz",
    "Metabolisches Syndrom",
    "Prolaktin erhöht",
    "FSH erhöht",
    "LH erhöht",
    "Wachstumshormon-Mangel",
]

HORMONE_REMEDIES_MULTIPLEX = [
    "Sepia + Pulsatilla (Hormonelle Dysbalance Frauen)",
    "Lycopus + Fucus vesiculosus (Schilddrüse)",
    "Agnus castus + Pulsatilla (PMS)",
    "Lachesis + Sepia (Wechseljahre)",
    "Damiana + Selenium (Testosteron-Mangel)",
]

# =============================================================================
# L) LUFTBELASTUNGEN & WOHNRAUMGIFTE - 3 GRUPPEN
# =============================================================================

LUFT_SYMPTOME_FEIN = [
    "Luftbelastungs-Kopfschmerzen",
    "Luftbelastungs-Müdigkeit",
    "Luftbelastungs-Konzentrationsstörungen",
    "Luftbelastungs-Reizhusten",
    "Luftbelastungs-Atemnot",
    "Luftbelastungs-Augenbrennen",
    "Luftbelastungs-Nasenlaufen",
    "Luftbelastungs-Hautausschlag",
    "Sick-Building-Syndrom",
    "Chemikalien-Sensitivität (MCS)",
    "Schimmel-Symptome",
    "VOC-Symptome",
    "Formaldehyd-Symptome",
    "Radon-Symptome",
    "Asbest-Symptome",
]

WOHNRAUMGIFTE_FEIN = [
    "Schimmel (Aspergillus)",
    "Schimmel (Penicillium)",
    "Schimmel (Alternaria)",
    "Schimmel (Cladosporium)",
    "Schimmel (Stachybotrys - Schwarzschimmel)",
    "Mykotoxine",
    "VOC (Flüchtige organische Verbindungen)",
    "Formaldehyd",
    "Benzol",
    "Toluol",
    "Xylol",
    "Styrol",
    "Radon",
    "Asbest",
    "Mineralfasern",
    "Holzschutzmittel (PCP)",
    "Holzschutzmittel (Lindan)",
    "PCB (Polychlorierte Biphenyle)",
    "PAK (Polyzyklische aromatische Kohlenwasserstoffe)",
    "Weichmacher (Phthalate)",
    "Flammschutzmittel",
    "Biozide",
    "Lösungsmittel",
    "Farben & Lacke",
    "Klebstoffe",
    "Teppichboden-Ausdünstungen",
    "Möbel-Ausdünstungen",
    "Reinigungsmittel-Dämpfe",
    "Parfüm & Duftstoffe",
    "Zigarettenrauch (Passivrauch)",
]

LUFT_REMEDIES_MULTIPLEX = [
    "Arsenicum album + Carbo vegetabilis (Luftbelastung)",
    "Sulfur + Pulsatilla (Chemikalien-Sensitivität)",
    "Natrium sulfuricum + Dulcamara (Schimmel)",
    "Silicea + Sulfur (Entgiftung Wohnraumgifte)",
    "Phosphorus + Arsenicum album (Sick-Building-Syndrom)",
]

# =============================================================================
# M) NAHRUNGSMITTELBELASTUNGEN - 3 GRUPPEN
# =============================================================================

NAHRUNG_SYMPTOME_FEIN = [
    "Nahrungsmittel-Unverträglichkeit Symptome",
    "Nahrungsmittel-Allergie Symptome",
    "Verdauungsbeschwerden nach Essen",
    "Blähungen nach Essen",
    "Durchfall nach Essen",
    "Verstopfung nach Essen",
    "Übelkeit nach Essen",
    "Bauchschmerzen nach Essen",
    "Hautausschlag nach Essen",
    "Juckreiz nach Essen",
    "Kopfschmerzen nach Essen",
    "Müdigkeit nach Essen",
    "Konzentrationsstörungen nach Essen",
    "Stimmungsschwankungen nach Essen",
    "Gelenkschmerzen nach Essen",
    "Atemnot nach Essen",
    "Herzrasen nach Essen",
    "Schwindel nach Essen",
    "Flush-Symptome (Histamin)",
    "Anaphylaktische Reaktion",
]

NAHRUNG_UNVERTRAEGLICHKEITEN_FEIN = [
    "Gluten-Unverträglichkeit",
    "Zöliakie",
    "Weizen-Sensitivität (nicht-Zöliakie)",
    "Laktose-Intoleranz",
    "Milcheiweiß-Allergie",
    "Fruktose-Intoleranz",
    "Fruktose-Malabsorption",
    "Histamin-Intoleranz",
    "Salicylat-Intoleranz",
    "Glutamat-Unverträglichkeit",
    "Sorbitol-Intoleranz",
    "Saccharose-Intoleranz",
    "Ei-Allergie",
    "Nuss-Allergie (Erdnuss)",
    "Nuss-Allergie (Baumnüsse)",
    "Fisch-Allergie",
    "Meeresfrüchte-Allergie",
    "Soja-Allergie",
    "Sesam-Allergie",
    "Senf-Allergie",
    "Sellerie-Allergie",
    "Lupinen-Allergie",
    "Sulfite-Unverträglichkeit",
    "Benzoate-Unverträglichkeit",
    "Farbstoffe-Unverträglichkeit",
    "Konservierungsstoffe-Unverträglichkeit",
    "Geschmacksverstärker-Unverträglichkeit",
    "Süßstoffe-Unverträglichkeit",
    "Koffein-Unverträglichkeit",
    "Alkohol-Unverträglichkeit",
    "Kreuzallergien (Pollen-Nahrungsmittel)",
    "Latex-Frucht-Syndrom",
]

NAHRUNG_REMEDIES_MULTIPLEX = [
    "Nux vomica + Lycopodium (Nahrungsmittel-Unverträglichkeit)",
    "Pulsatilla + Carbo vegetabilis (Verdauungsbeschwerden)",
    "Arsenicum album + China (Durchfall nach Essen)",
    "Colocynthis + Chamomilla (Bauchkrämpfe nach Essen)",
    "Apis + Urtica urens (Allergische Reaktion)",
]

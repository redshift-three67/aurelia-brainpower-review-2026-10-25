"""
Phase 4 - Priorität 1: Korrekte Gruppen (nur Labels)
Raten werden automatisch durch Bruce Copen Algorithmen generiert!

Bereiche:
- A) Zähne (4 Gruppen)
- B) Wirbelsäule (3 Gruppen) 
- F) Nervensystem (3 Gruppen)
- G) Herz-Kreislauf (4 Gruppen)
"""

# =============================================================================
# A) ZÄHNE - 4 GRUPPEN
# =============================================================================

ZAHN_SYMPTOME_FEIN = [
    "Zahnschmerz akut",
    "Zahnschmerz chronisch", 
    "Zahnfleischbluten",
    "Zahnfleischentzündung (Gingivitis)",
    "Parodontitis",
    "Zahnfleischrückgang",
    "Zahnlockerung",
    "Zahnempfindlichkeit (Kälte)",
    "Zahnempfindlichkeit (Wärme)",
    "Zahnempfindlichkeit (Süß)",
    "Zahnhalsdefekte",
    "Zahnstein",
    "Plaque",
    "Mundgeruch (Halitosis)",
    "Zahnverfärbungen",
    "Zahnabrieb (Abrasion)",
    "Zahnerosion",
    "Kieferschmerzen",
    "Kiefergelenk-Probleme (TMJ)",
    "Knacken im Kiefergelenk",
    "Zähneknirschen (Bruxismus)",
    "Zahnwurzel-Entzündung",
    "Zahnwurzel-Zysten",
    "Zahnfisteln",
    "Zahnabszess",
]

ZAHN_PATHOLOGIEN_FEIN = [
    "Karies (Dentin)",
    "Karies (Schmelz)",
    "Karies (Wurzel)",
    "Pulpitis (reversibel)",
    "Pulpitis (irreversibel)",
    "Pulpanekrose",
    "Apikale Parodontitis",
    "Periapikaler Abszess",
    "Wurzelgranulom",
    "Radikuläre Zyste",
    "Follikuläre Zyste",
    "Ameloblastom",
    "Odontogenes Keratozyste",
    "Zahnresorption (intern)",
    "Zahnresorption (extern)",
    "Zahnfraktur (Schmelz)",
    "Zahnfraktur (Dentin)",
    "Zahnfraktur (Wurzel)",
]

ZAHN_MATERIALIEN_FEIN = [
    "Amalgam (Quecksilber)",
    "Amalgam (Silber)",
    "Amalgam (Zinn)",
    "Amalgam (Kupfer)",
    "Gold-Legierung",
    "Palladium",
    "Nickel",
    "Kobalt-Chrom",
    "Titan",
    "Zirkonoxid",
    "Keramik (Feldspat)",
    "Keramik (Lithium-Disilikat)",
    "Komposit (BisGMA)",
    "Komposit (TEGDMA)",
    "Komposit (UDMA)",
    "Glasionomer-Zement",
    "Zinkoxid-Eugenol",
    "Wurzelfüllmaterial (Guttapercha)",
    "Wurzelfüllmaterial (AH Plus)",
    "Kleber (Adhäsiv)",
]

ZAHN_REMEDIES_MULTIPLEX = [
    "Arnica + Hypericum (Zahntrauma)",
    "Belladonna + Chamomilla (Zahnschmerz akut)",
    "Hepar sulfuris + Silicea (Zahnabszess)",
    "Mercurius solubilis + Kreosotum (Parodontitis)",
    "Calcium fluoratum + Silicea (Zahnschmelz-Stärkung)",
    "Plantago + Chamomilla (Zahnschmerz)",
    "Staphisagria + Arnica (Post-OP Zahn)",
]

# =============================================================================
# B) WIRBELSÄULE - 3 GRUPPEN
# =============================================================================

WIRBELSAEULE_SYMPTOME_FEIN = [
    "Nackenschmerzen akut",
    "Nackenschmerzen chronisch",
    "Nackensteifigkeit",
    "HWS-Syndrom",
    "Zervikale Radikulopathie",
    "Zervikale Myelopathie",
    "Rückenschmerzen akut (BWS)",
    "Rückenschmerzen chronisch (BWS)",
    "BWS-Syndrom",
    "Thorakale Radikulopathie",
    "Interkostalneuralgie",
    "Kreuzschmerzen akut",
    "Kreuzschmerzen chronisch",
    "LWS-Syndrom",
    "Lumbale Radikulopathie (L3)",
    "Lumbale Radikulopathie (L4)",
    "Lumbale Radikulopathie (L5)",
    "Lumbale Radikulopathie (S1)",
    "Ischialgie",
    "Lumboischialgie",
    "Spinalstenose (HWS)",
    "Spinalstenose (LWS)",
    "Facettensyndrom",
    "Iliosakralgelenk-Syndrom (ISG)",
    "Sakroiliakalgelenk-Blockade",
    "Hexenschuss (Lumbago)",
    "Skoliose-Schmerzen",
    "Morbus Bechterew Symptome",
]

WIRBELSAEULE_PATHOLOGIEN_FEIN = [
    "Bandscheibenvorfall C3/4",
    "Bandscheibenvorfall C4/5",
    "Bandscheibenvorfall C5/6",
    "Bandscheibenvorfall C6/7",
    "Bandscheibenvorfall L3/4",
    "Bandscheibenvorfall L4/5",
    "Bandscheibenvorfall L5/S1",
    "Bandscheibenprotrusion HWS",
    "Bandscheibenprotrusion LWS",
    "Bandscheibendegeneration HWS",
    "Bandscheibendegeneration LWS",
    "Spondylose",
    "Spondylarthrose",
    "Osteochondrose",
    "Morbus Scheuermann",
    "Morbus Bechterew",
    "Wirbelgleiten (Spondylolisthesis)",
    "Wirbelkörperfraktur",
    "Spinalkanalstenose",
]

WIRBELSAEULE_REMEDIES_MULTIPLEX = [
    "Rhus toxicodendron + Bryonia (Rückenschmerz)",
    "Arnica + Hypericum (Wirbelsäulen-Trauma)",
    "Ruta + Symphytum (Bandscheiben)",
    "Calcium fluoratum + Silicea (Wirbel-Stabilität)",
    "Colocynthis + Magnesium phosphoricum (Ischias)",
    "Aesculus + Nux vomica (LWS-Syndrom)",
    "Dulcamara + Rhus toxicodendron (chronische Rückenschmerzen)",
]

# =============================================================================
# F) NERVENSYSTEM - 3 GRUPPEN
# =============================================================================

NERVEN_SYMPTOME_FEIN = [
    "Kopfschmerzen (Stirn)",
    "Kopfschmerzen (Schläfen)",
    "Kopfschmerzen (Hinterkopf)",
    "Kopfschmerzen (Scheitel)",
    "Migräne (mit Aura)",
    "Migräne (ohne Aura)",
    "Spannungskopfschmerz",
    "Cluster-Kopfschmerz",
    "Trigeminusneuralgie",
    "Gesichtsneuralgie",
    "Schwindel (vestibulär)",
    "Schwindel (zentral)",
    "Schwindel (orthostatisch)",
    "Benommenheit",
    "Taubheitsgefühl (Gesicht)",
    "Taubheitsgefühl (Arme)",
    "Taubheitsgefühl (Hände)",
    "Taubheitsgefühl (Beine)",
    "Taubheitsgefühl (Füße)",
    "Kribbeln (Parästhesien)",
    "Brennen (neuropathisch)",
    "Zittern (Tremor)",
    "Muskelzucken (Faszikulationen)",
    "Nervenschmerzen (Neuralgie)",
    "Polyneuropathie-Symptome",
    "Restless Legs Syndrom",
    "Konzentrationsstörungen",
    "Gedächtnisstörungen",
    "Wortfindungsstörungen",
    "Verwirrtheit",
]

NERVEN_PATHOLOGIEN_FEIN = [
    "Multiple Sklerose",
    "Parkinson-Krankheit",
    "Alzheimer-Krankheit",
    "Demenz (vaskulär)",
    "Epilepsie",
    "Schlaganfall (ischämisch)",
    "Schlaganfall (hämorrhagisch)",
    "TIA (Transitorische ischämische Attacke)",
    "Polyneuropathie (diabetisch)",
    "Polyneuropathie (alkoholisch)",
    "Polyneuropathie (toxisch)",
    "Karpaltunnelsyndrom",
    "Sulcus-ulnaris-Syndrom",
    "Meralgia paraesthetica",
    "Guillain-Barré-Syndrom",
    "Myasthenia gravis",
    "ALS (Amyotrophe Lateralsklerose)",
    "Hirnhautentzündung (Meningitis)",
    "Gehirnentzündung (Enzephalitis)",
]

NERVEN_REMEDIES_MULTIPLEX = [
    "Hypericum + Arnica (Nervenverletzung)",
    "Gelsemium + Ignatia (Nervenschwäche)",
    "Magnesium phosphoricum + Kalium phosphoricum (Nervenschmerz)",
    "Aconitum + Belladonna (akute Neuralgie)",
    "Nux vomica + Zincum (Nervosität)",
]

# =============================================================================
# G) HERZ-KREISLAUF - 4 GRUPPEN
# =============================================================================

HERZ_SYMPTOME_FEIN = [
    "Herzschmerzen (Angina pectoris)",
    "Herzstechen",
    "Herzdruck",
    "Herzrasen (Tachykardie)",
    "Herzstolpern (Extrasystolen)",
    "Herzrhythmusstörungen",
    "Vorhofflimmern",
    "Herzklopfen (Palpitationen)",
    "Herzinsuffizienz-Symptome",
    "Atemnot bei Belastung",
    "Atemnot in Ruhe",
    "Ödeme (Beine)",
    "Ödeme (Knöchel)",
    "Müdigkeit (kardial)",
    "Schwindel (kardial)",
    "Synkope (Ohnmacht)",
]

KREISLAUF_SYMPTOME_FEIN = [
    "Bluthochdruck (Hypertonie)",
    "Niedriger Blutdruck (Hypotonie)",
    "Orthostatische Dysregulation",
    "Kreislaufkollaps",
    "Durchblutungsstörungen (Arme)",
    "Durchblutungsstörungen (Beine)",
    "Durchblutungsstörungen (Hände)",
    "Durchblutungsstörungen (Füße)",
    "Kalte Hände",
    "Kalte Füße",
    "Raynaud-Syndrom",
    "Venenschwäche",
    "Krampfadern (Varizen)",
    "Thrombose-Symptome",
]

HERZ_PATHOLOGIEN_FEIN = [
    "Koronare Herzkrankheit (KHK)",
    "Herzinfarkt (akut)",
    "Herzinfarkt (Z.n.)",
    "Herzinsuffizienz (systolisch)",
    "Herzinsuffizienz (diastolisch)",
    "Kardiomyopathie (dilatativ)",
    "Kardiomyopathie (hypertrophisch)",
    "Kardiomyopathie (restriktiv)",
    "Myokarditis",
    "Endokarditis",
    "Perikarditis",
    "Herzklappeninsuffizienz (Aorta)",
    "Herzklappeninsuffizienz (Mitral)",
    "Herzklappeninsuffizienz (Trikuspidal)",
    "Herzklappenstenose (Aorta)",
    "Herzklappenstenose (Mitral)",
    "Vorhofflimmern (permanent)",
    "Vorhofflimmern (paroxysmal)",
    "Ventrikuläre Tachykardie",
]

HERZ_REMEDIES_MULTIPLEX = [
    "Crataegus + Cactus (Herzstärkung)",
    "Digitalis + Convallaria (Herzinsuffizienz)",
    "Arnica + Cactus (Herzinfarkt-Nachsorge)",
    "Aurum + Crataegus (Hypertonie)",
    "Glonoinum + Belladonna (Herzklopfen)",
]

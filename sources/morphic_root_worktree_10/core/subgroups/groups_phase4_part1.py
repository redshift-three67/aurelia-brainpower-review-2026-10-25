"""
Phase 4 - Teil 1: Zähne & Wirbelsäule
HINWEIS: Raten [0.0, 0.0] = Platzhalter, müssen vom Anwender ergänzt werden!
"""

# A) ZÄHNE
ZAHN_SYMPTOME_FEIN = {
    "title": "Zahn-Symptome (detailliert)",
    "description": "Alle häufigen Zahn- und Kiefersymptome",
    "items": [
        {"label": "Zahnschmerz akut", "rates": [0.0, 0.0]},
        {"label": "Zahnschmerz chronisch", "rates": [0.0, 0.0]},
        {"label": "Zahnfleischbluten", "rates": [0.0, 0.0]},
        {"label": "Zahnfleischentzündung (Gingivitis)", "rates": [0.0, 0.0]},
        {"label": "Parodontitis", "rates": [0.0, 0.0]},
        {"label": "Zahnfleischrückgang", "rates": [0.0, 0.0]},
        {"label": "Zahnlockerung", "rates": [0.0, 0.0]},
        {"label": "Zahnempfindlichkeit (Kälte)", "rates": [0.0, 0.0]},
        {"label": "Zahnempfindlichkeit (Wärme)", "rates": [0.0, 0.0]},
        {"label": "Zahnempfindlichkeit (Süß)", "rates": [0.0, 0.0]},
        {"label": "Zahnhalsdefekte", "rates": [0.0, 0.0]},
        {"label": "Zahnstein", "rates": [0.0, 0.0]},
        {"label": "Plaque", "rates": [0.0, 0.0]},
        {"label": "Mundgeruch (Halitosis)", "rates": [0.0, 0.0]},
        {"label": "Zahnverfärbungen", "rates": [0.0, 0.0]},
        {"label": "Zahnabrieb (Abrasion)", "rates": [0.0, 0.0]},
        {"label": "Zahnerosion", "rates": [0.0, 0.0]},
        {"label": "Kieferschmerzen", "rates": [0.0, 0.0]},
        {"label": "Kiefergelenk-Probleme (TMJ)", "rates": [0.0, 0.0]},
        {"label": "Knacken im Kiefergelenk", "rates": [0.0, 0.0]},
        {"label": "Zähneknirschen (Bruxismus)", "rates": [0.0, 0.0]},
        {"label": "Zahnwurzel-Entzündung", "rates": [0.0, 0.0]},
        {"label": "Zahnwurzel-Zysten", "rates": [0.0, 0.0]},
        {"label": "Zahnfisteln", "rates": [0.0, 0.0]},
        {"label": "Zahnabszess", "rates": [0.0, 0.0]},
    ]
}

ZAHN_PATHOLOGIEN_FEIN = {
    "title": "Zahn-Pathologien (detailliert)",
    "description": "Alle pathologischen Zahnzustände",
    "items": [
        {"label": "Karies (Dentin)", "rates": [0.0, 0.0]},
        {"label": "Karies (Schmelz)", "rates": [0.0, 0.0]},
        {"label": "Karies (Wurzel)", "rates": [0.0, 0.0]},
        {"label": "Pulpitis (reversibel)", "rates": [0.0, 0.0]},
        {"label": "Pulpitis (irreversibel)", "rates": [0.0, 0.0]},
        {"label": "Pulpanekrose", "rates": [0.0, 0.0]},
        {"label": "Apikale Parodontitis", "rates": [0.0, 0.0]},
        {"label": "Periapikaler Abszess", "rates": [0.0, 0.0]},
        {"label": "Wurzelgranulom", "rates": [0.0, 0.0]},
        {"label": "Radikuläre Zyste", "rates": [0.0, 0.0]},
        {"label": "Follikuläre Zyste", "rates": [0.0, 0.0]},
        {"label": "Ameloblastom", "rates": [0.0, 0.0]},
        {"label": "Odontogenes Keratozyste", "rates": [0.0, 0.0]},
        {"label": "Zahnresorption (intern)", "rates": [0.0, 0.0]},
        {"label": "Zahnresorption (extern)", "rates": [0.0, 0.0]},
        {"label": "Zahnfraktur (Schmelz)", "rates": [0.0, 0.0]},
        {"label": "Zahnfraktur (Dentin)", "rates": [0.0, 0.0]},
        {"label": "Zahnfraktur (Wurzel)", "rates": [0.0, 0.0]},
    ]
}

ZAHN_MATERIALIEN_FEIN = {
    "title": "Zahn-Materialien (detailliert)",
    "description": "Alle Dental-Materialien",
    "items": [
        {"label": "Amalgam (Quecksilber)", "rates": [0.0, 0.0]},
        {"label": "Amalgam (Silber)", "rates": [0.0, 0.0]},
        {"label": "Amalgam (Zinn)", "rates": [0.0, 0.0]},
        {"label": "Amalgam (Kupfer)", "rates": [0.0, 0.0]},
        {"label": "Gold-Legierung", "rates": [0.0, 0.0]},
        {"label": "Palladium", "rates": [0.0, 0.0]},
        {"label": "Nickel", "rates": [0.0, 0.0]},
        {"label": "Kobalt-Chrom", "rates": [0.0, 0.0]},
        {"label": "Titan", "rates": [0.0, 0.0]},
        {"label": "Zirkonoxid", "rates": [0.0, 0.0]},
        {"label": "Keramik (Feldspat)", "rates": [0.0, 0.0]},
        {"label": "Keramik (Lithium-Disilikat)", "rates": [0.0, 0.0]},
        {"label": "Komposit (BisGMA)", "rates": [0.0, 0.0]},
        {"label": "Komposit (TEGDMA)", "rates": [0.0, 0.0]},
        {"label": "Komposit (UDMA)", "rates": [0.0, 0.0]},
        {"label": "Glasionomer-Zement", "rates": [0.0, 0.0]},
        {"label": "Zinkoxid-Eugenol", "rates": [0.0, 0.0]},
        {"label": "Wurzelfüllmaterial (Guttapercha)", "rates": [0.0, 0.0]},
        {"label": "Wurzelfüllmaterial (AH Plus)", "rates": [0.0, 0.0]},
        {"label": "Kleber (Adhäsiv)", "rates": [0.0, 0.0]},
    ]
}

ZAHN_REMEDIES_MULTIPLEX = {
    "title": "Zahn-Remedies (Kombinationen)",
    "description": "Bewährte Kombinationen",
    "items": [
        {"label": "Arnica + Hypericum (Zahntrauma)", "rates": [0.0, 0.0]},
        {"label": "Belladonna + Chamomilla (Zahnschmerz akut)", "rates": [0.0, 0.0]},
        {"label": "Hepar sulfuris + Silicea (Zahnabszess)", "rates": [0.0, 0.0]},
        {"label": "Mercurius solubilis + Kreosotum (Parodontitis)", "rates": [0.0, 0.0]},
        {"label": "Calcium fluoratum + Silicea (Zahnschmelz)", "rates": [0.0, 0.0]},
        {"label": "Plantago + Chamomilla (Zahnschmerz)", "rates": [0.0, 0.0]},
        {"label": "Staphisagria + Arnica (Post-OP)", "rates": [0.0, 0.0]},
    ]
}

# B) WIRBELSÄULE
WIRBELSAEULE_SYMPTOME_FEIN = {
    "title": "Wirbelsäulen-Symptome (detailliert)",
    "description": "Alle Wirbelsäulen-Symptome",
    "items": [
        {"label": "Nackenschmerzen akut", "rates": [0.0, 0.0]},
        {"label": "Nackenschmerzen chronisch", "rates": [0.0, 0.0]},
        {"label": "Nackensteifigkeit", "rates": [0.0, 0.0]},
        {"label": "HWS-Syndrom", "rates": [0.0, 0.0]},
        {"label": "Zervikale Radikulopathie", "rates": [0.0, 0.0]},
        {"label": "Zervikale Myelopathie", "rates": [0.0, 0.0]},
        {"label": "Rückenschmerzen akut (BWS)", "rates": [0.0, 0.0]},
        {"label": "Rückenschmerzen chronisch (BWS)", "rates": [0.0, 0.0]},
        {"label": "BWS-Syndrom", "rates": [0.0, 0.0]},
        {"label": "Thorakale Radikulopathie", "rates": [0.0, 0.0]},
        {"label": "Interkostalneuralgie", "rates": [0.0, 0.0]},
        {"label": "Kreuzschmerzen akut", "rates": [0.0, 0.0]},
        {"label": "Kreuzschmerzen chronisch", "rates": [0.0, 0.0]},
        {"label": "LWS-Syndrom", "rates": [0.0, 0.0]},
        {"label": "Lumbale Radikulopathie (L3)", "rates": [0.0, 0.0]},
        {"label": "Lumbale Radikulopathie (L4)", "rates": [0.0, 0.0]},
        {"label": "Lumbale Radikulopathie (L5)", "rates": [0.0, 0.0]},
        {"label": "Lumbale Radikulopathie (S1)", "rates": [0.0, 0.0]},
        {"label": "Ischialgie", "rates": [0.0, 0.0]},
        {"label": "Lumboischialgie", "rates": [0.0, 0.0]},
        {"label": "Spinalstenose (HWS)", "rates": [0.0, 0.0]},
        {"label": "Spinalstenose (LWS)", "rates": [0.0, 0.0]},
        {"label": "Facettensyndrom", "rates": [0.0, 0.0]},
        {"label": "Iliosakralgelenk-Syndrom (ISG)", "rates": [0.0, 0.0]},
        {"label": "Sakroiliakalgelenk-Blockade", "rates": [0.0, 0.0]},
        {"label": "Hexenschuss (Lumbago)", "rates": [0.0, 0.0]},
        {"label": "Skoliose-Schmerzen", "rates": [0.0, 0.0]},
        {"label": "Morbus Bechterew Symptome", "rates": [0.0, 0.0]},
    ]
}

WIRBELSAEULE_PATHOLOGIEN_FEIN = {
    "title": "Wirbelsäulen-Pathologien (detailliert)",
    "description": "Alle strukturellen Pathologien",
    "items": [
        {"label": "Bandscheibenvorfall C3/4", "rates": [0.0, 0.0]},
        {"label": "Bandscheibenvorfall C4/5", "rates": [0.0, 0.0]},
        {"label": "Bandscheibenvorfall C5/6", "rates": [0.0, 0.0]},
        {"label": "Bandscheibenvorfall C6/7", "rates": [0.0, 0.0]},
        {"label": "Bandscheibenvorfall L3/4", "rates": [0.0, 0.0]},
        {"label": "Bandscheibenvorfall L4/5", "rates": [0.0, 0.0]},
        {"label": "Bandscheibenvorfall L5/S1", "rates": [0.0, 0.0]},
        {"label": "Bandscheibenprotrusion HWS", "rates": [0.0, 0.0]},
        {"label": "Bandscheibenprotrusion LWS", "rates": [0.0, 0.0]},
        {"label": "Bandscheibendegeneration HWS", "rates": [0.0, 0.0]},
        {"label": "Bandscheibendegeneration LWS", "rates": [0.0, 0.0]},
        {"label": "Spondylose", "rates": [0.0, 0.0]},
        {"label": "Spondylarthrose", "rates": [0.0, 0.0]},
        {"label": "Osteochondrose", "rates": [0.0, 0.0]},
        {"label": "Morbus Scheuermann", "rates": [0.0, 0.0]},
        {"label": "Morbus Bechterew", "rates": [0.0, 0.0]},
        {"label": "Wirbelgleiten (Spondylolisthesis)", "rates": [0.0, 0.0]},
        {"label": "Wirbelkörperfraktur", "rates": [0.0, 0.0]},
        {"label": "Spinalkanalstenose", "rates": [0.0, 0.0]},
    ]
}

WIRBELSAEULE_REMEDIES_MULTIPLEX = {
    "title": "Wirbelsäulen-Remedies (Kombinationen)",
    "description": "Bewährte Kombinationen",
    "items": [
        {"label": "Rhus toxicodendron + Bryonia (Rückenschmerz)", "rates": [0.0, 0.0]},
        {"label": "Arnica + Hypericum (Wirbelsäulen-Trauma)", "rates": [0.0, 0.0]},
        {"label": "Ruta + Symphytum (Bandscheiben)", "rates": [0.0, 0.0]},
        {"label": "Calcium fluoratum + Silicea (Wirbel-Stabilität)", "rates": [0.0, 0.0]},
        {"label": "Colocynthis + Magnesium phosphoricum (Ischias)", "rates": [0.0, 0.0]},
        {"label": "Aesculus + Nux vomica (LWS-Syndrom)", "rates": [0.0, 0.0]},
        {"label": "Dulcamara + Rhus toxicodendron (chronisch)", "rates": [0.0, 0.0]},
    ]
}

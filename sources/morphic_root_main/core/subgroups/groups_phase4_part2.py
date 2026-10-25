"""
Phase 4 - Teil 2: Nervensystem & Herz-Kreislauf
HINWEIS: Raten [0.0, 0.0] = Platzhalter, müssen vom Anwender ergänzt werden!
"""

# F) NERVENSYSTEM
NERVEN_SYMPTOME_FEIN = {
    "title": "Nerven-Symptome (detailliert)",
    "description": "Alle neurologischen Symptome",
    "items": [
        {"label": "Kopfschmerzen (Stirn)", "rates": [0.0, 0.0]},
        {"label": "Kopfschmerzen (Schläfen)", "rates": [0.0, 0.0]},
        {"label": "Kopfschmerzen (Hinterkopf)", "rates": [0.0, 0.0]},
        {"label": "Kopfschmerzen (Scheitel)", "rates": [0.0, 0.0]},
        {"label": "Migräne (mit Aura)", "rates": [0.0, 0.0]},
        {"label": "Migräne (ohne Aura)", "rates": [0.0, 0.0]},
        {"label": "Spannungskopfschmerz", "rates": [0.0, 0.0]},
        {"label": "Cluster-Kopfschmerz", "rates": [0.0, 0.0]},
        {"label": "Trigeminusneuralgie", "rates": [0.0, 0.0]},
        {"label": "Gesichtsneuralgie", "rates": [0.0, 0.0]},
        {"label": "Schwindel (vestibulär)", "rates": [0.0, 0.0]},
        {"label": "Schwindel (zentral)", "rates": [0.0, 0.0]},
        {"label": "Schwindel (orthostatisch)", "rates": [0.0, 0.0]},
        {"label": "Benommenheit", "rates": [0.0, 0.0]},
        {"label": "Taubheitsgefühl (Gesicht)", "rates": [0.0, 0.0]},
        {"label": "Taubheitsgefühl (Arme)", "rates": [0.0, 0.0]},
        {"label": "Taubheitsgefühl (Hände)", "rates": [0.0, 0.0]},
        {"label": "Taubheitsgefühl (Beine)", "rates": [0.0, 0.0]},
        {"label": "Taubheitsgefühl (Füße)", "rates": [0.0, 0.0]},
        {"label": "Kribbeln (Parästhesien)", "rates": [0.0, 0.0]},
        {"label": "Brennen (neuropathisch)", "rates": [0.0, 0.0]},
        {"label": "Zittern (Tremor)", "rates": [0.0, 0.0]},
        {"label": "Muskelzucken (Faszikulationen)", "rates": [0.0, 0.0]},
        {"label": "Nervenschmerzen (Neuralgie)", "rates": [0.0, 0.0]},
        {"label": "Polyneuropathie-Symptome", "rates": [0.0, 0.0]},
        {"label": "Restless Legs Syndrom", "rates": [0.0, 0.0]},
        {"label": "Konzentrationsstörungen", "rates": [0.0, 0.0]},
        {"label": "Gedächtnisstörungen", "rates": [0.0, 0.0]},
        {"label": "Wortfindungsstörungen", "rates": [0.0, 0.0]},
        {"label": "Verwirrtheit", "rates": [0.0, 0.0]},
    ]
}

NERVEN_PATHOLOGIEN_FEIN = {
    "title": "Nerven-Pathologien (detailliert)",
    "description": "Alle neurologischen Pathologien",
    "items": [
        {"label": "Multiple Sklerose", "rates": [0.0, 0.0]},
        {"label": "Parkinson-Krankheit", "rates": [0.0, 0.0]},
        {"label": "Alzheimer-Krankheit", "rates": [0.0, 0.0]},
        {"label": "Demenz (vaskulär)", "rates": [0.0, 0.0]},
        {"label": "Epilepsie", "rates": [0.0, 0.0]},
        {"label": "Schlaganfall (ischämisch)", "rates": [0.0, 0.0]},
        {"label": "Schlaganfall (hämorrhagisch)", "rates": [0.0, 0.0]},
        {"label": "TIA (Transitorische ischämische Attacke)", "rates": [0.0, 0.0]},
        {"label": "Polyneuropathie (diabetisch)", "rates": [0.0, 0.0]},
        {"label": "Polyneuropathie (alkoholisch)", "rates": [0.0, 0.0]},
        {"label": "Polyneuropathie (toxisch)", "rates": [0.0, 0.0]},
        {"label": "Karpaltunnelsyndrom", "rates": [0.0, 0.0]},
        {"label": "Sulcus-ulnaris-Syndrom", "rates": [0.0, 0.0]},
        {"label": "Meralgia paraesthetica", "rates": [0.0, 0.0]},
        {"label": "Guillain-Barré-Syndrom", "rates": [0.0, 0.0]},
        {"label": "Myasthenia gravis", "rates": [0.0, 0.0]},
        {"label": "ALS (Amyotrophe Lateralsklerose)", "rates": [0.0, 0.0]},
        {"label": "Hirnhautentzündung (Meningitis)", "rates": [0.0, 0.0]},
        {"label": "Gehirnentzündung (Enzephalitis)", "rates": [0.0, 0.0]},
    ]
}

NERVEN_REMEDIES_MULTIPLEX = {
    "title": "Nerven-Remedies (Kombinationen)",
    "description": "Bewährte Kombinationen",
    "items": [
        {"label": "Hypericum + Arnica (Nervenverletzung)", "rates": [0.0, 0.0]},
        {"label": "Gelsemium + Ignatia (Nervenschwäche)", "rates": [0.0, 0.0]},
        {"label": "Magnesium phosphoricum + Kalium phosphoricum (Nervenschmerz)", "rates": [0.0, 0.0]},
        {"label": "Aconitum + Belladonna (akute Neuralgie)", "rates": [0.0, 0.0]},
        {"label": "Nux vomica + Zincum (Nervosität)", "rates": [0.0, 0.0]},
    ]
}

# G) HERZ-KREISLAUF
HERZ_SYMPTOME_FEIN = {
    "title": "Herz-Symptome (detailliert)",
    "description": "Alle Herz-Symptome",
    "items": [
        {"label": "Herzschmerzen (Angina pectoris)", "rates": [0.0, 0.0]},
        {"label": "Herzstechen", "rates": [0.0, 0.0]},
        {"label": "Herzdruck", "rates": [0.0, 0.0]},
        {"label": "Herzrasen (Tachykardie)", "rates": [0.0, 0.0]},
        {"label": "Herzstolpern (Extrasystolen)", "rates": [0.0, 0.0]},
        {"label": "Herzrhythmusstörungen", "rates": [0.0, 0.0]},
        {"label": "Vorhofflimmern", "rates": [0.0, 0.0]},
        {"label": "Herzklopfen (Palpitationen)", "rates": [0.0, 0.0]},
        {"label": "Herzinsuffizienz-Symptome", "rates": [0.0, 0.0]},
        {"label": "Atemnot bei Belastung", "rates": [0.0, 0.0]},
        {"label": "Atemnot in Ruhe", "rates": [0.0, 0.0]},
        {"label": "Ödeme (Beine)", "rates": [0.0, 0.0]},
        {"label": "Ödeme (Knöchel)", "rates": [0.0, 0.0]},
        {"label": "Müdigkeit (kardial)", "rates": [0.0, 0.0]},
        {"label": "Schwindel (kardial)", "rates": [0.0, 0.0]},
        {"label": "Synkope (Ohnmacht)", "rates": [0.0, 0.0]},
    ]
}

KREISLAUF_SYMPTOME_FEIN = {
    "title": "Kreislauf-Symptome (detailliert)",
    "description": "Alle Kreislauf-Symptome",
    "items": [
        {"label": "Bluthochdruck (Hypertonie)", "rates": [0.0, 0.0]},
        {"label": "Niedriger Blutdruck (Hypotonie)", "rates": [0.0, 0.0]},
        {"label": "Orthostatische Dysregulation", "rates": [0.0, 0.0]},
        {"label": "Kreislaufkollaps", "rates": [0.0, 0.0]},
        {"label": "Durchblutungsstörungen (Arme)", "rates": [0.0, 0.0]},
        {"label": "Durchblutungsstörungen (Beine)", "rates": [0.0, 0.0]},
        {"label": "Durchblutungsstörungen (Hände)", "rates": [0.0, 0.0]},
        {"label": "Durchblutungsstörungen (Füße)", "rates": [0.0, 0.0]},
        {"label": "Kalte Hände", "rates": [0.0, 0.0]},
        {"label": "Kalte Füße", "rates": [0.0, 0.0]},
        {"label": "Raynaud-Syndrom", "rates": [0.0, 0.0]},
        {"label": "Venenschwäche", "rates": [0.0, 0.0]},
        {"label": "Krampfadern (Varizen)", "rates": [0.0, 0.0]},
        {"label": "Thrombose-Symptome", "rates": [0.0, 0.0]},
    ]
}

HERZ_PATHOLOGIEN_FEIN = {
    "title": "Herz-Pathologien (detailliert)",
    "description": "Alle Herz-Pathologien",
    "items": [
        {"label": "Koronare Herzkrankheit (KHK)", "rates": [0.0, 0.0]},
        {"label": "Herzinfarkt (akut)", "rates": [0.0, 0.0]},
        {"label": "Herzinfarkt (Z.n.)", "rates": [0.0, 0.0]},
        {"label": "Herzinsuffizienz (systolisch)", "rates": [0.0, 0.0]},
        {"label": "Herzinsuffizienz (diastolisch)", "rates": [0.0, 0.0]},
        {"label": "Kardiomyopathie (dilatativ)", "rates": [0.0, 0.0]},
        {"label": "Kardiomyopathie (hypertrophisch)", "rates": [0.0, 0.0]},
        {"label": "Kardiomyopathie (restriktiv)", "rates": [0.0, 0.0]},
        {"label": "Myokarditis", "rates": [0.0, 0.0]},
        {"label": "Endokarditis", "rates": [0.0, 0.0]},
        {"label": "Perikarditis", "rates": [0.0, 0.0]},
        {"label": "Herzklappeninsuffizienz (Aorta)", "rates": [0.0, 0.0]},
        {"label": "Herzklappeninsuffizienz (Mitral)", "rates": [0.0, 0.0]},
        {"label": "Herzklappeninsuffizienz (Trikuspidal)", "rates": [0.0, 0.0]},
        {"label": "Herzklappenstenose (Aorta)", "rates": [0.0, 0.0]},
        {"label": "Herzklappenstenose (Mitral)", "rates": [0.0, 0.0]},
        {"label": "Vorhofflimmern (permanent)", "rates": [0.0, 0.0]},
        {"label": "Vorhofflimmern (paroxysmal)", "rates": [0.0, 0.0]},
        {"label": "Ventrikuläre Tachykardie", "rates": [0.0, 0.0]},
    ]
}

HERZ_REMEDIES_MULTIPLEX = {
    "title": "Herz-Remedies (Kombinationen)",
    "description": "Bewährte Kombinationen",
    "items": [
        {"label": "Crataegus + Cactus (Herzstärkung)", "rates": [0.0, 0.0]},
        {"label": "Digitalis + Convallaria (Herzinsuffizienz)", "rates": [0.0, 0.0]},
        {"label": "Arnica + Cactus (Herzinfarkt-Nachsorge)", "rates": [0.0, 0.0]},
        {"label": "Aurum + Crataegus (Hypertonie)", "rates": [0.0, 0.0]},
        {"label": "Glonoinum + Belladonna (Herzklopfen)", "rates": [0.0, 0.0]},
    ]
}

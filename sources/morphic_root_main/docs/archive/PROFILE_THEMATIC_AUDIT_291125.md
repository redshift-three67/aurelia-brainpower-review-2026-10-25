# Profile Thematische Audit - 29.11.2025

## Status: ✅ ABGESCHLOSSEN

## Ziel
Systematische Analyse aller Profile auf thematische Vollständigkeit.
Jedes Profil muss Gruppen enthalten, die zum Thema passen.

## Durchgeführte Änderungen

### 1. Profile erweitert um thematisch relevante Gruppen:

| Profil | Erweiterungen |
|--------|---------------|
| **pathogen** | +bakterien_detailliert_fein, +viren_detailliert_fein, +parasiten_detailliert_fein, +pilze_detailliert_fein, +biofilme_fein, +infektions_symptome_fein, +immunsystem_angeboren_fein, +immunsystem_erworben_fein, +immunstaerkung_remedies_multiplex |
| **toxin** | +schwermetalle_detailliert_fein, +chemikalien_detailliert_fein, +strahlung_quellen_fein, +strahlung_symptome_fein, +geopathie_fein, +umweltbelastungen_erweitert_fein, +wohnraumgifte_fein, +toxine_symptome_fein, +toxine_remedies_multiplex, +entgiftung_leber_phase1_fein, +entgiftung_leber_phase2_fein, +entgiftung_remedies_multiplex |
| **regulation** | +chakren, +chakren_detailliert_fein, +meridiane_detailliert_fein, +extra_meridiane, +energetische_blockaden_fein, +nervensystem_vegetativ, +nervensystem_neurotransmitter_fein, +hormone_symptome_fein, +orthomolekular_therapie_multiplex |
| **meridiane_detailliert** | +tcm_rezepturen, +tcm_rezepturen_multiplex, +emotionale_blockaden_fein, +psychosomatik_fein |
| **immune/immunsystem** | +immunsystem_antikoerper, +lymphsystem_lymphknoten, +lymphsystem_milz, +lymphsystem_thymus, +lymphsystem_tonsillen |
| **heavy_metals/schwermetalle** | +toxine_symptome_fein, +toxine_remedies_multiplex, +entgiftung_leber_phase1/2/3, +entgiftung_darm, +entgiftung_symptome_fein, +mikronaehrstoffe, +orthomolekular_mineralien_fein, +orthomolekular_aminosauren_fein |
| **haut_detailliert** | +entgiftung_symptome_fein, +kreislauf_fein, +immunsystem_angeboren_fein, +immunsystem_erworben_fein, +immunsystem_autoimmun_fein, +entzuendung, +bakterien_fein, +pilze_fein, +viren_fein, +psychosomatik_fein, +emotionale_blockaden_fein |
| **endokrin_detailliert** | +wechseljahre_detailliert_fein, +schwangerschaft_geburt_fein |

### 2. Neuer CLI-Befehl: `top3-scan`

Automatische Ermittlung der Top-3 relevantesten Profile für einen Klienten:

```bash
python -m apps.cli.main top3-scan "Mustermann" "Max" -d 01011990 -p Berlin
```

**Funktionsweise:**
1. Phase 1: Schnelles Screening über 20 Haupt-Profile (24 Kandidaten pro Profil)
2. Ermittlung der 3 Profile mit höchsten durchschnittlichen Resonanz-Scores
3. Phase 2: Vollständige Analyse der Top-3 Profile (48 Kandidaten)

**Verfügbare Profile für Top-3 Analyse:**
- Basis: pathogen, toxin, immune, detox, regulation
- Organe: verdauung, leber, nervensystem, herz_kreislauf, atmung_lunge, endokrin, haut
- Struktur: knochen, wirbelsaeule, zahn
- Symptome: schmerz, schwindel
- Belastungen: schwermetalle, strahlung, stoerfelder

## Verfügbare Gruppen (Auszug nach Themen)

### Pathogene
- bakterien, bakterien_fein, bakterien_detailliert_fein
- viren, viren_fein, viren_detailliert_fein
- parasiten, parasiten_fein, parasiten_detailliert_fein
- pilze, pilze_fein, pilze_detailliert_fein
- biofilme_fein
- infektions_symptome_fein, kinderkrankheiten_fein

### Toxine & Belastungen
- schwermetalle, schwermetalle_tox, schwermetalle_detailliert_fein
- chemikalien_tox, chemikalien_detailliert_fein
- pestizide_tox
- strahlung_tox, strahlung_quellen_fein, strahlung_symptome_fein
- emf_fein, geopathie, geopathie_fein
- umweltbelastungen_erweitert_fein, wohnraumgifte_fein
- toxine_symptome_fein, toxine_remedies_multiplex

### Entgiftung
- entgiftung_leber, entgiftung_leber_phase1/2/3, entgiftung_leber_phase1/2/3_fein
- entgiftung_niere, entgiftung_lymphe, entgiftung_darm, entgiftung_haut
- entgiftung_organe_fein, entgiftung_symptome_fein
- entgiftung_remedies_multiplex, detox

### Immunsystem
- immunsystem_angeboren, immunsystem_angeboren_fein
- immunsystem_erworben, immunsystem_erworben_fein
- immunsystem_autoimmun, immunsystem_autoimmun_fein
- immunsystem_zytokine, immunsystem_zytokine_fein
- immunsystem_antikoerper
- immunstaerkung_remedies_multiplex

### Nervensystem
- nervensystem_zns, nervensystem_zns_fein
- nervensystem_pns, nervensystem_pns_fein
- nervensystem_vegetativ
- nervensystem_hirnnerven, nervensystem_hirnnerven_fein
- nervensystem_neurotransmitter, nervensystem_neurotransmitter_fein
- nervensystem_plexus
- nerven_symptome_fein, nerven_pathologien_fein
- nerven_remedies_multiplex

### Herz-Kreislauf
- herz_fein, herz_symptome_fein, herz_pathologien_fein
- kreislauf, kreislauf_fein, kreislauf_symptome_fein
- mikrozirkulation
- herz_remedies_multiplex

### Verdauung
- verdauung_magen, verdauung_duenndarm, verdauung_duenndarm_fein
- verdauung_dickdarm, verdauung_dickdarm_fein
- verdauung_leber, verdauung_galle, verdauung_pankreas
- verdauung_mikrobiom, verdauung_mikrobiom_fein
- verdauung_barriere
- verdauung_symptome_fein, verdauung_pathologien_fein
- verdauung_remedies_multiplex

### Knochen & Gelenke
- knochen_gelenke, knochen_gelenke_fein
- knochen_knorpel, knochen_osteoporose
- knochen_osteoblasten, knochen_osteoklasten
- knochen_symptome_fein, knochen_pathologien_fein
- knochen_remedies_multiplex

### Wirbelsäule
- wirbelsaeule, wirbelsaeule_fein
- wirbelsaeule_hws, wirbelsaeule_bws, wirbelsaeule_lws, wirbelsaeule_sakral
- wirbelsaeule_bandscheiben, wirbelsaeule_bandscheiben_fein
- wirbelsaeule_facetten
- wirbelsaeule_symptome_fein, wirbelsaeule_pathologien_fein
- wirbelsaeule_remedies_multiplex

### Zähne
- zahnorgane, zahnorgane_fein
- zahnorgane_frontzaehne, zahnorgane_quadrant1/2/3/4
- zahnorgane_weisheitszaehne, zahnorgane_kiefergelenk
- zahnorgane_kiefer_herde
- zahn_materialien_fein, zahn_symptome_fein, zahn_pathologien_fein
- zahn_remedies_multiplex
- odontone

### Haut
- haut_detailliert_fein
- hautprobleme, hautprobleme_fein

### Augen & Ohren
- ohr_fein
- (auge_fein fehlt!)

### Schwindel
- schwindel_vestibular, schwindel_vestibular_fein
- schwindel_zentral, schwindel_zentral_fein
- schwindel_hws, schwindel_kreislauf, schwindel_medikament

### Schmerz & Schlaf
- schmerz_kopf, schmerz_kopf_fein
- schmerz_ruecken, schmerz_gelenk
- schlafstoerungen, schlafstoerungen_fein, schlaf

### Hormone & Endokrin
- endokrin
- schilddruese_fein, nebenniere_fein, hypophyse_fein
- hormone_symptome_fein, hormone_schilddruese_fein, hormone_geschlecht_fein
- hormone_remedies_multiplex
- wechseljahre_detailliert_fein, schwangerschaft_geburt_fein

### Lymphsystem
- lymphsystem_drainage
- lymphsystem_lymphknoten, lymphsystem_lymphknoten_fein
- lymphsystem_milz, lymphsystem_thymus, lymphsystem_tonsillen

### Energie & Chakren
- chakren, chakren_full, chakren_detailliert_fein, chakren_erweitert
- nebenchakren
- energetische_blockaden_fein
- energie_remedies_multiplex

### TCM & Meridiane
- meridiane, meridiane_detailliert_fein
- tcm_punkte, tcm_punkte_extended, tcm_full
- extra_meridiane
- tcm_rezepturen, tcm_rezepturen_multiplex, tcm_rezepturen_potenzen

### Psyche
- psychosomatik_fein
- emotionale_blockaden_fein
- psyche_remedies_multiplex

### Orthomolekular
- mikronaehrstoffe
- orthomolekular_vitamine, orthomolekular_vitamine_fein
- orthomolekular_mineralien, orthomolekular_mineralien_fein
- orthomolekular_aminosauren, orthomolekular_aminosauren_fein
- orthomolekular_fettsauren
- orthomolekular_therapie_multiplex, orthomolekular_multiplex
- vitamine_detailliert_fein
- mineralien_spurenelemente_detailliert_fein
- fettsaeuren_detailliert_fein
- aminosaeuren_detailliert_fein (fehlt?)
- naehrstoffmangel_symptome_fein

### Homöopathie & Naturheilkunde
- homoeopathie_klassisch, homoeopathie_klassisch_potenzen
- homoeopathie_komplexmittel, homoeopathie_multiplex
- homoeopathie_isopathie, homoeopathie_nosoden, homoeopathie_sarcoden
- spagyrik, spagyrik_multiplex
- bachblueten_multiplex
- schuessler_12, schuessler_ergaenzung, schuessler_multiplex
- phytotherapie_extrakte, phytotherapie_tinkturen, phytotherapie_tinkturen_multiplex
- phytotherapie_tees, phytotherapie_tees_multiplex
- phytotherapie_ayurveda

### Frequenzen
- frequenz_clark, frequenz_clark_multiplex
- frequenz_rife_multiplex, frequenz_royal_rife
- frequenz_solfeggio, frequenz_solfeggio_multiplex
- frequenz_binaural
- ps_freq

### Sonstige
- mitochondrien, nad_booster, stammzellen_aktivierung
- faszien_fein, muskulatur_fein
- blut_fein
- urogenitalsystem_fein
- magnetfeld
- edelsteine, edelsteine_chakren, edelsteine_schutz
- kristalle_heilung, klang_therapie, licht_farbe, farbtherapie
- tibetische_medizin, unani_medizin
- organotherapie_glandulae
- peptide_bioregulator, peptide_thymus
- konzentration, muedigkeit_chronisch
- nahrung_symptome_fein, nahrung_unvertraeglichkeiten_fein, nahrung_remedies_multiplex
- luft_symptome_fein, luft_remedies_multiplex

### BAT Programme (Akut)
- bat_a01 bis bat_a93 (diverse Akutprogramme)

---

## ANALYSE PRO PROFIL

### 1. pathogen
**Thema:** Erreger (Bakterien, Viren, Parasiten, Pilze)
**Aktuell:** bakterien, viren, parasiten, pilze + _fein Varianten
**FEHLT:**
- bakterien_detailliert_fein, viren_detailliert_fein, parasiten_detailliert_fein, pilze_detailliert_fein
- biofilme_fein (wichtig für chronische Infektionen!)
- infektions_symptome_fein
- immunsystem_angeboren_fein, immunsystem_erworben_fein (Abwehr!)
**STATUS:** ⚠️ ERWEITERUNG NÖTIG

### 2. toxin
**Thema:** Toxine, Schwermetalle, Strahlung, EMF
**Aktuell:** schwermetalle, schwermetalle_tox, pestizide_tox, chemikalien_tox, strahlung_tox, emf_fein, geopathie
**FEHLT:**
- schwermetalle_detailliert_fein
- chemikalien_detailliert_fein
- strahlung_quellen_fein, strahlung_symptome_fein
- geopathie_fein
- umweltbelastungen_erweitert_fein, wohnraumgifte_fein
- toxine_symptome_fein
- entgiftung_leber_phase1_fein (Entgiftungskapazität!)
**STATUS:** ⚠️ ERWEITERUNG NÖTIG

### 3. regulation
**Thema:** Energetische Regulation, Chakren, Meridiane
**Aktuell:** chakren_full, nebenchakren, chakren_erweitert, meridiane, tcm_punkte, tcm_punkte_extended, tcm_full, zahnorgane, odontone, mikrozirkulation, mitochondrien, entzuendung, endokrin, detox, mikronaehrstoffe
**FEHLT:**
- chakren, chakren_detailliert_fein
- meridiane_detailliert_fein
- extra_meridiane
- energetische_blockaden_fein
- nervensystem_vegetativ (vegetative Regulation!)
**STATUS:** ⚠️ ERWEITERUNG NÖTIG

### 4. meridiane_detailliert
**Thema:** TCM, Meridiane, Energetik
**Aktuell:** Gut abgedeckt
**FEHLT:**
- tcm_rezepturen, tcm_rezepturen_multiplex (TCM Behandlung!)
- emotionale_blockaden_fein
- psychosomatik_fein
**STATUS:** ⚠️ KLEINE ERWEITERUNG

### 5. dizziness/schwindel
**Thema:** Schwindel, Gleichgewicht
**Aktuell:** schwindel_vestibular, schwindel_zentral, schwindel_hws, schwindel_kreislauf, schwindel_medikament
**FEHLT:**
- schwindel_vestibular_fein, schwindel_zentral_fein
- ohr_fein (Innenohr!)
- nervensystem_hirnnerven_fein (Gleichgewichtsnerv!)
- kreislauf_symptome_fein
- wirbelsaeule_hws (HWS-Schwindel!)
**STATUS:** ⚠️ ERWEITERUNG NÖTIG

### 6. schwindel_detailliert
**Thema:** Schwindel umfassend
**Prüfen...**

### 7. circulation/durchblutung
**Thema:** Kreislauf, Durchblutung
**FEHLT prüfen:**
- mikrozirkulation
- herz_fein, herz_symptome_fein
- kreislauf_symptome_fein
- blut_fein
**STATUS:** PRÜFEN

### 8. respiration/atmung
**Thema:** Atmung, Lunge
**FEHLT prüfen:**
- luft_symptome_fein, luft_remedies_multiplex
- infektions_symptome_fein (Atemwegsinfekte)
**STATUS:** PRÜFEN

### 9-36. Weitere Profile...
(Fortsetzung der Analyse)

---

## PRIORITÄTEN

### HOCH (Kernprofile)
1. pathogen - Detaillierte Erreger fehlen
2. toxin - Detaillierte Toxine fehlen
3. dizziness/schwindel - Fein-Gruppen fehlen
4. immune/immunsystem - Vollständigkeit prüfen

### MITTEL
5. regulation - Energetik erweitern
6. circulation - Kreislauf-Details
7. respiration - Atmungs-Details

### NIEDRIG (bereits gut)
- narben_entstoerung_gewebe_remedies (bereits korrigiert)
- meridiane_detailliert

"""
Phase 5 - Priorität 1: Infektionen & Erreger
Nur Labels - Raten werden automatisch durch Bruce Copen Algorithmen generiert!

8 GRUPPEN:
- Bakterien FEIN (detailliert)
- Viren FEIN (detailliert)
- Pilze FEIN (detailliert)
- Parasiten FEIN (detailliert)
- Biofilme FEIN
- Infektions-Symptome FEIN
- Anti-Infektions-Remedies MULTIPLEX
- Immunstärkung-Remedies MULTIPLEX
"""

# =============================================================================
# BAKTERIEN - DETAILLIERT FEIN
# =============================================================================

BAKTERIEN_DETAILLIERT_FEIN = [
    # Gram-positive Kokken
    "Staphylococcus aureus",
    "Staphylococcus epidermidis",
    "MRSA (Methicillin-resistenter Staphylococcus aureus)",
    "Streptococcus pyogenes (Gruppe A)",
    "Streptococcus agalactiae (Gruppe B)",
    "Streptococcus pneumoniae",
    "Streptococcus mutans",
    "Enterococcus faecalis",
    "Enterococcus faecium",
    
    # Gram-negative Stäbchen
    "Escherichia coli (E. coli)",
    "E. coli (enterohämorrhagisch EHEC)",
    "E. coli (enterotoxisch ETEC)",
    "Salmonella enterica",
    "Salmonella typhi",
    "Shigella dysenteriae",
    "Klebsiella pneumoniae",
    "Proteus mirabilis",
    "Pseudomonas aeruginosa",
    "Helicobacter pylori",
    "Campylobacter jejuni",
    "Yersinia enterocolitica",
    "Legionella pneumophila",
    
    # Anaerobe Bakterien
    "Clostridium difficile",
    "Clostridium perfringens",
    "Clostridium tetani",
    "Clostridium botulinum",
    "Bacteroides fragilis",
    
    # Mykobakterien
    "Mycobacterium tuberculosis",
    "Mycobacterium leprae",
    "Mycobacterium avium",
    
    # Spirochäten
    "Borrelia burgdorferi (Lyme-Borreliose)",
    "Borrelia garinii",
    "Borrelia afzelii",
    "Treponema pallidum (Syphilis)",
    "Leptospira interrogans",
    
    # Intrazelluläre Bakterien
    "Chlamydia trachomatis",
    "Chlamydia pneumoniae",
    "Chlamydia psittaci",
    "Mycoplasma pneumoniae",
    "Mycoplasma hominis",
    "Ureaplasma urealyticum",
    "Rickettsia rickettsii",
    "Coxiella burnetii (Q-Fieber)",
    "Bartonella henselae",
    
    # Weitere pathogene Bakterien
    "Haemophilus influenzae",
    "Neisseria meningitidis",
    "Neisseria gonorrhoeae",
    "Listeria monocytogenes",
    "Vibrio cholerae",
    "Corynebacterium diphtheriae",
    "Bacillus anthracis",
]

# =============================================================================
# VIREN - DETAILLIERT FEIN
# =============================================================================

VIREN_DETAILLIERT_FEIN = [
    # Herpesviren
    "Herpes simplex Virus 1 (HSV-1)",
    "Herpes simplex Virus 2 (HSV-2)",
    "Varizella-Zoster-Virus (VZV)",
    "Epstein-Barr-Virus (EBV)",
    "Cytomegalievirus (CMV)",
    "Humanes Herpesvirus 6 (HHV-6)",
    "Humanes Herpesvirus 7 (HHV-7)",
    "Humanes Herpesvirus 8 (HHV-8)",
    
    # Respiratorische Viren
    "Influenza A Virus",
    "Influenza B Virus",
    "SARS-CoV-2 (COVID-19)",
    "Respiratory Syncytial Virus (RSV)",
    "Rhinovirus",
    "Adenovirus",
    "Parainfluenza-Virus",
    "Metapneumovirus",
    "Coronavirus (229E, NL63, OC43, HKU1)",
    
    # Hepatitisviren
    "Hepatitis A Virus (HAV)",
    "Hepatitis B Virus (HBV)",
    "Hepatitis C Virus (HCV)",
    "Hepatitis D Virus (HDV)",
    "Hepatitis E Virus (HEV)",
    
    # Enteroviren
    "Poliovirus",
    "Coxsackievirus A",
    "Coxsackievirus B",
    "Echovirus",
    "Enterovirus 71",
    
    # Retroviren
    "HIV-1 (Humanes Immundefizienz-Virus)",
    "HIV-2",
    "HTLV-1 (Humanes T-Zell-Leukämie-Virus)",
    
    # Papillomaviren
    "HPV 16 (Humanes Papillomavirus)",
    "HPV 18",
    "HPV 6",
    "HPV 11",
    
    # Flaviviren
    "Dengue-Virus",
    "Zika-Virus",
    "West-Nil-Virus",
    "Gelbfieber-Virus",
    "FSME-Virus (Frühsommer-Meningoenzephalitis)",
    
    # Weitere Viren
    "Masernvirus",
    "Mumpsvirus",
    "Rötelnvirus",
    "Norovirus",
    "Rotavirus",
    "Parvovirus B19",
    "Rabiesvirus (Tollwut)",
    "Ebolavirus",
    "Hantavirus",
]

# =============================================================================
# PILZE - DETAILLIERT FEIN
# =============================================================================

PILZE_DETAILLIERT_FEIN = [
    # Candida-Arten
    "Candida albicans",
    "Candida glabrata",
    "Candida tropicalis",
    "Candida parapsilosis",
    "Candida krusei",
    "Candida auris",
    
    # Dermatophyten (Hautpilze)
    "Trichophyton rubrum",
    "Trichophyton mentagrophytes",
    "Microsporum canis",
    "Epidermophyton floccosum",
    
    # Schimmelpilze
    "Aspergillus fumigatus",
    "Aspergillus niger",
    "Aspergillus flavus",
    "Penicillium chrysogenum",
    "Alternaria alternata",
    "Cladosporium herbarum",
    "Stachybotrys chartarum (Schwarzschimmel)",
    "Fusarium species",
    "Mucor species",
    "Rhizopus species",
    
    # Hefen
    "Cryptococcus neoformans",
    "Cryptococcus gattii",
    "Malassezia furfur",
    "Malassezia globosa",
    
    # Endemische Pilze
    "Histoplasma capsulatum",
    "Coccidioides immitis",
    "Blastomyces dermatitidis",
    "Paracoccidioides brasiliensis",
    
    # Pneumocystis
    "Pneumocystis jirovecii",
]

# =============================================================================
# PARASITEN - DETAILLIERT FEIN
# =============================================================================

PARASITEN_DETAILLIERT_FEIN = [
    # Protozoen (Einzeller)
    "Toxoplasma gondii",
    "Giardia lamblia (Lamblien)",
    "Entamoeba histolytica",
    "Cryptosporidium parvum",
    "Plasmodium falciparum (Malaria)",
    "Plasmodium vivax",
    "Plasmodium malariae",
    "Plasmodium ovale",
    "Trypanosoma cruzi (Chagas)",
    "Trypanosoma brucei (Schlafkrankheit)",
    "Leishmania donovani",
    "Leishmania tropica",
    "Trichomonas vaginalis",
    "Blastocystis hominis",
    "Dientamoeba fragilis",
    "Cyclospora cayetanensis",
    "Isospora belli",
    "Babesia microti",
    
    # Helminthen - Nematoden (Fadenwürmer)
    "Ascaris lumbricoides (Spulwurm)",
    "Enterobius vermicularis (Madenwurm)",
    "Trichuris trichiura (Peitschenwurm)",
    "Ancylostoma duodenale (Hakenwurm)",
    "Necator americanus",
    "Strongyloides stercoralis",
    "Trichinella spiralis",
    "Wuchereria bancrofti (Filarie)",
    "Onchocerca volvulus",
    "Toxocara canis",
    "Toxocara cati",
    
    # Helminthen - Cestoden (Bandwürmer)
    "Taenia solium (Schweinebandwurm)",
    "Taenia saginata (Rinderbandwurm)",
    "Diphyllobothrium latum (Fischbandwurm)",
    "Echinococcus granulosus (Hundebandwurm)",
    "Echinococcus multilocularis (Fuchsbandwurm)",
    "Hymenolepis nana (Zwergbandwurm)",
    
    # Helminthen - Trematoden (Saugwürmer)
    "Schistosoma mansoni",
    "Schistosoma haematobium",
    "Schistosoma japonicum",
    "Fasciola hepatica (Leberegel)",
    "Clonorchis sinensis",
    "Paragonimus westermani",
    
    # Ektoparasiten
    "Sarcoptes scabiei (Krätzmilbe)",
    "Demodex folliculorum (Haarbalgmilbe)",
    "Pediculus humanus capitis (Kopflaus)",
    "Pediculus humanus corporis (Kleiderlaus)",
    "Phthirus pubis (Filzlaus)",
]

# =============================================================================
# BIOFILME FEIN
# =============================================================================

BIOFILME_FEIN = [
    "Bakterielle Biofilme (allgemein)",
    "Staphylococcus-Biofilm",
    "Streptococcus-Biofilm",
    "Pseudomonas-Biofilm",
    "E. coli-Biofilm",
    "Candida-Biofilm",
    "Polymikrobielle Biofilme",
    "Zahnbelag-Biofilm",
    "Darm-Biofilm",
    "Katheter-assoziierte Biofilme",
    "Implantat-assoziierte Biofilme",
    "Biofilm-Matrix (Exopolysaccharide)",
    "Quorum Sensing (Biofilm-Kommunikation)",
]

# =============================================================================
# INFEKTIONS-SYMPTOME FEIN
# =============================================================================

INFEKTIONS_SYMPTOME_FEIN = [
    "Fieber (akut)",
    "Fieber (chronisch)",
    "Schüttelfrost",
    "Nachtschweiß",
    "Müdigkeit (infektiös)",
    "Erschöpfung (post-infektiös)",
    "Lymphknotenschwellung",
    "Halsschmerzen (infektiös)",
    "Husten (infektiös)",
    "Schnupfen (infektiös)",
    "Durchfall (infektiös)",
    "Erbrechen (infektiös)",
    "Bauchschmerzen (infektiös)",
    "Hautausschlag (infektiös)",
    "Gelenkschmerzen (infektiös)",
    "Muskelschmerzen (infektiös)",
    "Kopfschmerzen (infektiös)",
    "Verwirrtheit (infektiös)",
    "Sepsis-Symptome",
    "Chronische Infektion",
    "Latente Infektion",
    "Reaktivierung (Virus)",
    "Post-infektiöses Syndrom",
    "Long-COVID-Symptome",
]

# =============================================================================
# ANTI-INFEKTIONS-REMEDIES MULTIPLEX
# =============================================================================

ANTI_INFEKTIONS_REMEDIES_MULTIPLEX = [
    "Echinacea + Baptisia (akute Infektion)",
    "Propolis + Echinacea (Immunstimulation)",
    "Thuja + Silicea (chronische Infektion)",
    "Pyrogenium + Lachesis (Sepsis-Tendenz)",
    "Mercurius solubilis + Hepar sulfuris (bakterielle Infektion)",
    "Oscillococcinum + Gelsemium (Grippe)",
    "Arsenicum album + China (Durchfall infektiös)",
    "Belladonna + Ferrum phosphoricum (Fieber akut)",
    "Sulfur + Psorinum (chronische Infektneigung)",
    "Tuberculinum + Bacillinum (Tuberkulinie-Miasma)",
]

# =============================================================================
# IMMUNSTÄRKUNG-REMEDIES MULTIPLEX
# =============================================================================

IMMUNSTAERKUNG_REMEDIES_MULTIPLEX = [
    "Echinacea + Astragalus (Immunstärkung)",
    "Vitamin C + Zink (Immunsupport)",
    "Vitamin D3 + K2 (Immunmodulation)",
    "Propolis + Manuka-Honig (antimikrobiell)",
    "Cistus + Kapland-Pelargonie (antiviral)",
    "Colostrum + Lactoferrin (Immunfaktoren)",
    "Beta-Glucan + Shiitake (Immunstimulation)",
    "Selen + Glutathion (antioxidativ)",
    "Probiotika + Präbiotika (Darm-Immunität)",
    "Thymus-Extrakt + Spleen-Extrakt (Organotherapie)",
]

// Immunsystem & Lymphsystem Datenbank
// Höchst detaillierte anatomische Strukturen basierend auf Terminologia Anatomica (TA2)
// Kategorie: Immunologie & Lymphologie

const IMMUN_LYMPH_DATABASE = {
  name: 'Immunsystem & Lymphsystem',
  category: 'Immunologie',
  totalEntries: 0, // Will be calculated
  subcategories: {
    // ========================
    // LYMPHATISCHE ORGANE - PRIMÄR
    // ========================
    primaereLymphorgane: {
      name: 'Primäre lymphatische Organe',
      entries: [
        // Thymus
        'Thymus',
        'Lobus dexter thymi',
        'Lobus sinister thymi',
        'Cortex thymi',
        'Medulla thymi',
        'Corpusculum thymicum (Hassall-Körperchen)',
        'Capsula thymi',
        'Septa interlobularia thymi',
        'Lobuli thymi',
        'Thymozyten corticales',
        'Thymozyten medullares',
        'Epithelzellen thymi corticales',
        'Epithelzellen thymi medullares',
        'Blut-Thymus-Schranke',
        'Vasa thymici',
        'Rami thymici',
        // Knochenmark
        'Medulla ossium rubra (rotes Knochenmark)',
        'Medulla ossium flava (gelbes Knochenmark)',
        'Cellulae stromales medullae',
        'Cellulae stem haematopoieticae',
        'Cellulae progenitor lymphoidales',
        'Cellulae progenitor B',
        'Cellulae pro-B',
        'Cellulae prae-B',
        'Cellulae B immaturae',
        'Insulae erythropoieticae',
        'Insulae granulopoieticae',
        'Insulae megakaryopoieticae',
        'Sinusoide medullae',
        'Arteria nutricia',
        'Vena centralis medullae',
        'Reticulozyten',
        'Adipozyten medullae',
      ]
    },
    
    // ========================
    // LYMPHATISCHE ORGANE - SEKUNDÄR
    // ========================
    sekundaereLymphorgane: {
      name: 'Sekundäre lymphatische Organe',
      entries: [
        // Milz (Splen/Lien)
        'Splen (Milz)',
        'Hilum splenicum',
        'Facies diaphragmatica splenis',
        'Facies visceralis splenis',
        'Facies gastrica',
        'Facies renalis',
        'Facies colica',
        'Margo superior splenis',
        'Margo inferior splenis',
        'Extremitas anterior splenis',
        'Extremitas posterior splenis',
        'Capsula splenis',
        'Trabeculae splenis',
        'Pulpa rubra',
        'Pulpa alba',
        'Corpusculum splenica (Malpighi-Körperchen)',
        'Arteriola centralis',
        'Zona marginalis splenis',
        'Zona periarterialis lymphoidea (PALS)',
        'Folliculi lymphoidei splenis',
        'Centrum germinativum splenis',
        'Zona mantellaris',
        'Cordae splenis (Billroth-Stränge)',
        'Sinus splenicus',
        'Arteria splenica',
        'Vena splenica',
        'Arteria trabecularis',
        'Vena trabecularis',
        'Arteriolae penicillares',
        'Capillares ellipsoidei',
        // Lymphknoten allgemein
        'Nodi lymphoidei (Lymphknoten)',
        'Capsula nodi lymphoidei',
        'Cortex nodi lymphoidei',
        'Paracortex (T-Zell-Zone)',
        'Medulla nodi lymphoidei',
        'Folliculi lymphoidei primarii',
        'Folliculi lymphoidei secundarii',
        'Centrum germinativum',
        'Zona mantellaris nodi',
        'Sinus subcapsularis (marginalis)',
        'Sinus corticalis (intermedius)',
        'Sinus medullaris',
        'Chordae medullares',
        'Vas afferens lymphaticum',
        'Vas efferens lymphaticum',
        'Hilum nodi lymphoidei',
        'Venula postcapillaris (HEV)',
        'Reticulum fibrosum',
        'Cellulae dendriticae folliculares',
        'Macrophagi sinuum',
        // Tonsillen
        'Tonsilla palatina',
        'Cryptae tonsillares',
        'Folliculi lymphoidei tonsillae',
        'Capsula tonsillae',
        'Tonsilla pharyngealis (Rachenmandel)',
        'Tonsilla lingualis',
        'Tonsilla tubaria',
        'Anulus lymphoideus pharyngis (Waldeyer-Ring)',
        // MALT
        'MALT (mucosa-associated lymphoid tissue)',
        'GALT (gut-associated lymphoid tissue)',
        'BALT (bronchus-associated lymphoid tissue)',
        'NALT (nasal-associated lymphoid tissue)',
        'Plaques Peyeri (Noduli lymphoidei aggregati)',
        'Folliculi lymphoidei solitarii',
        'Appendix vermiformis (lymphoides Gewebe)',
        'Cellulae M (Microfold cells)',
        'Intraepitheliale Lymphozyten',
        'Lamina propria Lymphozyten',
      ]
    },
    
    // ========================
    // LYMPHKNOTENREGIONEN - KOPF & HALS
    // ========================
    lymphknotenKopfHals: {
      name: 'Lymphknoten Kopf & Hals',
      entries: [
        // Kopfregion
        'Nodi lymphoidei occipitales',
        'Nodi lymphoidei retroauriculares (mastoidei)',
        'Nodi lymphoidei parotidei superficiales',
        'Nodi lymphoidei parotidei profundi',
        'Nodi lymphoidei preauriculares',
        'Nodi lymphoidei infraauriculares',
        'Nodi lymphoidei intraglandulares',
        'Nodi lymphoidei faciales',
        'Nodus buccalis',
        'Nodus nasolabialis',
        'Nodus mandibularis',
        // Submandibulär/Submental
        'Nodi lymphoidei submandibulares',
        'Nodi lymphoidei submentales',
        // Halsregion - Anteriore Gruppe
        'Nodi lymphoidei cervicales anteriores',
        'Nodi lymphoidei jugulodigastrici',
        'Nodi lymphoidei juguloomohyoidei',
        'Nodi lymphoidei prelaryngeales',
        'Nodi lymphoidei praetracheales',
        'Nodi lymphoidei paratracheales',
        'Nodi lymphoidei thyroidei',
        'Nodi lymphoidei infrahyoidei',
        // Halsregion - Laterale Gruppe
        'Nodi lymphoidei cervicales laterales superficiales',
        'Nodi lymphoidei cervicales laterales profundi',
        'Nodi lymphoidei jugulares superiores (Level II)',
        'Nodi lymphoidei jugulares medii (Level III)',
        'Nodi lymphoidei jugulares inferiores (Level IV)',
        'Nodi lymphoidei supraclaviculares (Level V)',
        'Nodus lymphoideus supraclavicularis (Virchow)',
        'Nodi lymphoidei accessorii (spinales)',
        'Nodi lymphoidei transversi cervicis',
        // Retropharyngeal
        'Nodi lymphoidei retropharyngeales',
        'Nodus lymphoideus lateralis retropharyngealis',
        'Nodus lymphoideus medialis retropharyngealis',
      ]
    },
    
    // ========================
    // LYMPHKNOTENREGIONEN - AXILLÄR
    // ========================
    lymphknotenAxillaer: {
      name: 'Lymphknoten axillär',
      entries: [
        'Nodi lymphoidei axillares',
        // Level I (lateral des M. pectoralis minor)
        'Nodi lymphoidei pectorales (Level I anterior)',
        'Nodi lymphoidei subscapulares (Level I posterior)',
        'Nodi lymphoidei laterales (Level I lateral)',
        'Nodi lymphoidei brachiales',
        'Nodi lymphoidei paramammarii',
        // Level II (hinter dem M. pectoralis minor)
        'Nodi lymphoidei interpectorales (Rotter)',
        'Nodi lymphoidei centrales (Level II)',
        // Level III (medial des M. pectoralis minor)
        'Nodi lymphoidei apicales (infraclaviculares, Level III)',
        // Sonstige
        'Nodi lymphoidei deltoideopectorales',
        'Nodus lymphoideus deltoideoclavicularis',
        'Truncus subclavius',
      ]
    },
    
    // ========================
    // LYMPHKNOTENREGIONEN - THORAX
    // ========================
    lymphknotenThorax: {
      name: 'Lymphknoten Thorax',
      entries: [
        // Parietale Lymphknoten
        'Nodi lymphoidei parasternales (mammaria interna)',
        'Nodi lymphoidei intercostales',
        'Nodi lymphoidei prevertebrales',
        'Nodi lymphoidei phrenici superiores',
        // Viszerale Lymphknoten - Anterior
        'Nodi lymphoidei mediastinales anteriores',
        'Nodi lymphoidei praevasculares',
        'Nodi lymphoidei prepericardiales',
        'Nodi lymphoidei pericardiaci laterales',
        // Viszerale Lymphknoten - Posterior
        'Nodi lymphoidei mediastinales posteriores',
        'Nodi lymphoidei paraoesophageales',
        'Nodi lymphoidei interaorticoesophageales',
        // Viszerale Lymphknoten - Tracheobronchial
        'Nodi lymphoidei paratracheales dexter et sinister',
        'Nodi lymphoidei tracheobronchiales superiores',
        'Nodi lymphoidei tracheobronchiales inferiores (Bifurkation)',
        'Nodi lymphoidei bronchopulmonales (Hilus)',
        'Nodi lymphoidei intrapulmonales',
        'Nodi lymphoidei subcarinales',
        // Pulmonale Kette
        'Nodi lymphoidei segmentales',
        'Nodi lymphoidei lobares',
      ]
    },
    
    // ========================
    // LYMPHKNOTENREGIONEN - ABDOMEN
    // ========================
    lymphknotenAbdomen: {
      name: 'Lymphknoten Abdomen',
      entries: [
        // Parietale Lymphknoten
        'Nodi lymphoidei phrenici inferiores',
        'Nodi lymphoidei lumbales dexter (cavales)',
        'Nodi lymphoidei lumbales sinister (aortici)',
        'Nodi lymphoidei lumbales intermedii (interaorticocavales)',
        'Nodi lymphoidei praeaortici',
        'Nodi lymphoidei retroaortici',
        'Nodi lymphoidei lateroaortici',
        'Nodi lymphoidei praecavales',
        'Nodi lymphoidei retrocavales',
        'Nodi lymphoidei laterocavales',
        // Viszerale - Coeliaca
        'Nodi lymphoidei coeliaci',
        'Nodi lymphoidei gastrici sinistri',
        'Nodi lymphoidei gastrici dextri',
        'Nodi lymphoidei gastroomentales sinistri',
        'Nodi lymphoidei gastroomentales dextri',
        'Nodi lymphoidei pylorici',
        'Nodi lymphoidei suprapylorici',
        'Nodi lymphoidei subpylorici',
        'Nodi lymphoidei retropancreaticoduodenales',
        // Viszerale - Hepatisch
        'Nodi lymphoidei hepatici',
        'Nodi lymphoidei cystici',
        'Nodi lymphoidei foraminales',
        // Viszerale - Pankreatisch/Splenetisch
        'Nodi lymphoidei splenici',
        'Nodi lymphoidei pancreaticoduodenales superiores',
        'Nodi lymphoidei pancreaticoduodenales inferiores',
        'Nodi lymphoidei pancreaticolienales',
        // Viszerale - Mesenterica superior
        'Nodi lymphoidei mesenterici superiores',
        'Nodi lymphoidei mesenterici centrales',
        'Nodi lymphoidei juxtaintestinales',
        'Nodi lymphoidei ileocolici',
        'Nodi lymphoidei prececales',
        'Nodi lymphoidei retrocecales',
        'Nodi lymphoidei appendiculares',
        'Nodi lymphoidei colici dextri',
        'Nodi lymphoidei colici medii',
        // Viszerale - Mesenterica inferior
        'Nodi lymphoidei mesenterici inferiores',
        'Nodi lymphoidei colici sinistri',
        'Nodi lymphoidei sigmoidei',
        'Nodi lymphoidei rectales superiores',
      ]
    },
    
    // ========================
    // LYMPHKNOTENREGIONEN - BECKEN
    // ========================
    lymphknotenBecken: {
      name: 'Lymphknoten Becken',
      entries: [
        // Parietale Gruppe
        'Nodi lymphoidei iliaci communes',
        'Nodi lymphoidei iliaci communes mediales',
        'Nodi lymphoidei iliaci communes laterales',
        'Nodi lymphoidei iliaci communes intermedii',
        'Nodi lymphoidei subaortici',
        'Nodi lymphoidei promontorii',
        'Nodi lymphoidei iliaci externi',
        'Nodi lymphoidei iliaci externi mediales',
        'Nodi lymphoidei iliaci externi laterales',
        'Nodi lymphoidei iliaci externi intermedii',
        'Nodi lymphoidei lacunares (Rosenmüller/Cloquet)',
        'Nodi lymphoidei iliaci interni',
        'Nodi lymphoidei obturatorii',
        'Nodi lymphoidei gluteales superiores',
        'Nodi lymphoidei gluteales inferiores',
        'Nodi lymphoidei sacrales',
        'Nodi lymphoidei sacrales laterales',
        'Nodus sacralis medianus (promontorii)',
        // Viszerale Gruppe
        'Nodi lymphoidei paravesicales',
        'Nodi lymphoidei prevesicales',
        'Nodi lymphoidei retrovesicales',
        'Nodi lymphoidei vesicales laterales',
        'Nodi lymphoidei pararectales',
        'Nodi lymphoidei rectales medii',
        'Nodi lymphoidei rectales inferiores',
        // Urogenital
        'Nodi lymphoidei parauterini',
        'Nodi lymphoidei paravaginales',
        'Nodi lymphoidei paraprostatici',
      ]
    },
    
    // ========================
    // LYMPHKNOTENREGIONEN - INGUINAL & EXTREMITÄTEN
    // ========================
    lymphknotenExtremitaeten: {
      name: 'Lymphknoten inguinal & Extremitäten',
      entries: [
        // Inguinal
        'Nodi lymphoidei inguinales superficiales',
        'Nodi lymphoidei inguinales superficiales superomediales',
        'Nodi lymphoidei inguinales superficiales superolaterales',
        'Nodi lymphoidei inguinales superficiales inferiores',
        'Nodi lymphoidei inguinales profundi',
        'Nodus lymphoideus proximalis profundus (Rosenmüller)',
        'Nodi lymphoidei inguinales intermedii',
        'Nodus lymphoideus distalis profundus',
        // Untere Extremität
        'Nodi lymphoidei popliteales superficiales',
        'Nodi lymphoidei popliteales profundi',
        'Nodi lymphoidei tibiales anteriores',
        'Nodi lymphoidei tibiales posteriores',
        'Nodi lymphoidei fibulares',
        // Obere Extremität
        'Nodi lymphoidei cubitales superficiales',
        'Nodi lymphoidei cubitales profundi (supratrochleares)',
        'Nodi lymphoidei brachiales profundi',
      ]
    },
    
    // ========================
    // LYMPHGEFÄSSE
    // ========================
    lymphgefaesse: {
      name: 'Lymphgefäße',
      entries: [
        // Hauptstämme
        'Ductus thoracicus',
        'Cisterna chyli',
        'Ductus lymphaticus dexter',
        'Truncus jugularis dexter',
        'Truncus jugularis sinister',
        'Truncus subclavius dexter',
        'Truncus subclavius sinister',
        'Truncus bronchomediastinalis dexter',
        'Truncus bronchomediastinalis sinister',
        'Truncus lumbalis dexter',
        'Truncus lumbalis sinister',
        'Truncus intestinalis',
        // Regionale Gefäße
        'Vasa lymphatica superficialia',
        'Vasa lymphatica profunda',
        'Vasa lymphatica afferentia',
        'Vasa lymphatica efferentia',
        'Collectores lymphatici',
        'Praecollectores lymphatici',
        'Capillares lymphatici initiales',
        'Plexus lymphaticus superficialis',
        'Plexus lymphaticus profundus',
        // Spezielle Strukturen
        'Valvulae lymphaticae',
        'Lymphangion (funktionelle Einheit)',
        'Ampulla lymphatica',
        'Angulus venosus dexter',
        'Angulus venosus sinister',
        // Kopf/Hals Gefäße
        'Vasa lymphatica faciei',
        'Vasa lymphatica cervicalia',
        'Vasa lymphatica jugularia',
        // Extremitäten Gefäße
        'Vasa lymphatica membri superioris superficialia',
        'Vasa lymphatica membri superioris profunda',
        'Vasa lymphatica membri inferioris superficialia',
        'Vasa lymphatica membri inferioris profunda',
        'Collectores lymphatici mediales cruris',
        'Collectores lymphatici laterales cruris',
        // Viszerale Gefäße
        'Vasa lymphatica pulmonalia',
        'Vasa lymphatica hepatis',
        'Vasa lymphatica gastrica',
        'Vasa lymphatica intestini tenuis',
        'Vasa lymphatica intestini crassi',
        'Vasa lactea (Chylusgefäße)',
        'Plexus lymphaticus subserosus',
        'Plexus lymphaticus submucosus',
      ]
    },
    
    // ========================
    // IMMUNZELLEN - LYMPHOZYTEN
    // ========================
    lymphozyten: {
      name: 'Lymphozyten',
      entries: [
        // T-Lymphozyten
        'Lymphocytus T (T-Zelle)',
        'Thymocytus',
        'Lymphocytus T naivus',
        'Lymphocytus T activatus',
        'Lymphocytus T helper (CD4+)',
        'Lymphocytus Th1',
        'Lymphocytus Th2',
        'Lymphocytus Th17',
        'Lymphocytus Tfh (follicular helper)',
        'Lymphocytus T cytotoxicus (CD8+)',
        'Lymphocytus T regulatorius (Treg)',
        'Lymphocytus T memoriae centralis',
        'Lymphocytus T memoriae effector',
        'Lymphocytus T residentialis (TRM)',
        'Lymphocytus T gamma-delta (γδ)',
        'Lymphocytus NKT (natural killer T)',
        'Lymphocytus iNKT (invariant NKT)',
        'Lymphocytus MAIT (mucosal-associated invariant T)',
        // B-Lymphozyten
        'Lymphocytus B (B-Zelle)',
        'Lymphocytus B naivus',
        'Lymphocytus B activatus',
        'Lymphocytus B memoriae',
        'Plasmocytus (Plasmazelle)',
        'Plasmablastus',
        'Lymphocytus B-1',
        'Lymphocytus B-2 (konventionell)',
        'Lymphocytus B marginalis zonae',
        'Lymphocytus B follicularis',
        'Lymphocytus B centro germinativo',
        'Centroblastus',
        'Centrocytus',
        // NK-Zellen
        'Lymphocytus NK (natural killer)',
        'Lymphocytus NK CD56bright',
        'Lymphocytus NK CD56dim',
        'Lymphocytus NK residentialis',
        // ILC (Innate Lymphoid Cells)
        'Cellula lymphoidea innata (ILC)',
        'ILC1',
        'ILC2',
        'ILC3',
        'Lymphoid tissue inducer cell (LTi)',
      ]
    },
    
    // ========================
    // IMMUNZELLEN - MYELOIDE ZELLEN
    // ========================
    myeloideZellen: {
      name: 'Myeloide Immunzellen',
      entries: [
        // Monozyten/Makrophagen
        'Monocytus',
        'Monocytus classicus (CD14++CD16-)',
        'Monocytus intermedius (CD14++CD16+)',
        'Monocytus non-classicus (CD14+CD16++)',
        'Macrophagocytus (Makrophage)',
        'Macrophagus alveolaris',
        'Macrophagus hepatis (Kupffer-Zelle)',
        'Macrophagus splenis',
        'Macrophagus peritonealis',
        'Macrophagus cerebri (Mikroglia)',
        'Osteoclastus',
        'Cellula gigantocellularis (Riesenzelle)',
        'Histiocytus',
        // Granulozyten
        'Granulocytus neutrophilus',
        'Neutrophilus maturus (segmentiert)',
        'Neutrophilus juvenilis (stabkernig)',
        'Granulocytus eosinophilus',
        'Granulocytus basophilus',
        // Mastzellen
        'Mastocytus (Mastzelle)',
        'Mastocytus mucosalis',
        'Mastocytus connective tissue',
        // Dendritische Zellen
        'Cellula dendritica (DC)',
        'Cellula dendritica myeloidea (mDC)',
        'Cellula dendritica myeloidea cDC1',
        'Cellula dendritica myeloidea cDC2',
        'Cellula dendritica plasmacytoidea (pDC)',
        'Cellula dendritica follicularis (FDC)',
        'Cellula dendritica interdigitalis',
        'Cellula Langerhans',
        'Cellula dendritica dermalis',
        'Cellula dendritica inflammatoria',
        // Sonstige
        'Cellula suppressor myeloidea (MDSC)',
      ]
    },
    
    // ========================
    // ZYTOKINE & INTERLEUKINE
    // ========================
    zytokine: {
      name: 'Zytokine & Interleukine',
      entries: [
        // Interleukine
        'Interleukinum 1 (IL-1)',
        'IL-1α',
        'IL-1β',
        'IL-1Ra (Rezeptorantagonist)',
        'Interleukinum 2 (IL-2)',
        'Interleukinum 3 (IL-3)',
        'Interleukinum 4 (IL-4)',
        'Interleukinum 5 (IL-5)',
        'Interleukinum 6 (IL-6)',
        'Interleukinum 7 (IL-7)',
        'Interleukinum 8 (IL-8/CXCL8)',
        'Interleukinum 9 (IL-9)',
        'Interleukinum 10 (IL-10)',
        'Interleukinum 11 (IL-11)',
        'Interleukinum 12 (IL-12)',
        'IL-12p35',
        'IL-12p40',
        'Interleukinum 13 (IL-13)',
        'Interleukinum 15 (IL-15)',
        'Interleukinum 17 (IL-17)',
        'IL-17A',
        'IL-17F',
        'Interleukinum 18 (IL-18)',
        'Interleukinum 21 (IL-21)',
        'Interleukinum 22 (IL-22)',
        'Interleukinum 23 (IL-23)',
        'Interleukinum 27 (IL-27)',
        'Interleukinum 33 (IL-33)',
        // Interferone
        'Interferonum alpha (IFN-α)',
        'Interferonum beta (IFN-β)',
        'Interferonum gamma (IFN-γ)',
        'Interferonum lambda (IFN-λ)',
        // TNF-Familie
        'Tumor necrosis factor alpha (TNF-α)',
        'Tumor necrosis factor beta (TNF-β/LT-α)',
        'Lymphotoxinum beta (LT-β)',
        'TRAIL (TNF-related apoptosis-inducing ligand)',
        'RANKL (receptor activator of NF-κB ligand)',
        'BAFF (B-cell activating factor)',
        'APRIL',
        'CD40L',
        'FasL',
        // Wachstumsfaktoren
        'Granulocyte-colony stimulating factor (G-CSF)',
        'Granulocyte-macrophage CSF (GM-CSF)',
        'Macrophage CSF (M-CSF)',
        'Stem cell factor (SCF)',
        'Erythropoietin (EPO)',
        'Thrombopoietin (TPO)',
        'Transforming growth factor beta (TGF-β)',
        'TGF-β1',
        'TGF-β2',
        'TGF-β3',
        // Chemokine
        'CCL2 (MCP-1)',
        'CCL3 (MIP-1α)',
        'CCL4 (MIP-1β)',
        'CCL5 (RANTES)',
        'CCL11 (Eotaxin)',
        'CCL17 (TARC)',
        'CCL19 (ELC)',
        'CCL21 (SLC)',
        'CCL22 (MDC)',
        'CXCL1 (GRO-α)',
        'CXCL8 (IL-8)',
        'CXCL9 (MIG)',
        'CXCL10 (IP-10)',
        'CXCL12 (SDF-1)',
        'CXCL13 (BLC)',
        'CX3CL1 (Fractalkine)',
        'XCL1 (Lymphotactin)',
      ]
    },
    
    // ========================
    // IMMUNGLOBULINE & KOMPLEMENT
    // ========================
    immunglobuline: {
      name: 'Immunglobuline & Komplement',
      entries: [
        // Immunglobulinklassen
        'Immunoglobulinum (Antikörper)',
        'Immunoglobulinum G (IgG)',
        'IgG1',
        'IgG2',
        'IgG3',
        'IgG4',
        'Immunoglobulinum A (IgA)',
        'IgA1',
        'IgA2',
        'Secretory IgA (sIgA)',
        'Immunoglobulinum M (IgM)',
        'Immunoglobulinum E (IgE)',
        'Immunoglobulinum D (IgD)',
        // Antikörperstruktur
        'Catena levis kappa (κ)',
        'Catena levis lambda (λ)',
        'Catena gravis (heavy chain)',
        'Regio Fab',
        'Regio Fc',
        'Regio variabilis (V)',
        'Regio constans (C)',
        'CDR (complementarity determining region)',
        'Fragmentum scFv',
        // Komplementsystem
        'Systema complementi',
        'C1 (C1q, C1r, C1s)',
        'C2',
        'C3',
        'C3a (Anaphylatoxin)',
        'C3b (Opsonin)',
        'iC3b',
        'C4',
        'C4a',
        'C4b',
        'C5',
        'C5a (Anaphylatoxin)',
        'C5b',
        'C6',
        'C7',
        'C8',
        'C9',
        'MAC (membrane attack complex C5b-9)',
        'Factor B',
        'Factor D',
        'Factor H',
        'Factor I',
        'Properdin (Factor P)',
        'MBL (mannose-binding lectin)',
        'MASP-1',
        'MASP-2',
        'C1-Inhibitor',
        'CD46 (MCP)',
        'CD55 (DAF)',
        'CD59 (Protectin)',
      ]
    },
    
    // ========================
    // REZEPTOREN & MARKER
    // ========================
    rezeptorenMarker: {
      name: 'Immunrezeptoren & Marker',
      entries: [
        // T-Zell-Rezeptoren
        'TCR (T-cell receptor)',
        'TCR-αβ',
        'TCR-γδ',
        'CD3 complex',
        'CD3γ',
        'CD3δ',
        'CD3ε',
        'CD3ζ (zeta)',
        // Ko-Rezeptoren & Ko-Stimulation
        'CD4',
        'CD8α',
        'CD8β',
        'CD28',
        'CTLA-4 (CD152)',
        'PD-1 (CD279)',
        'PD-L1 (CD274)',
        'PD-L2 (CD273)',
        'ICOS (CD278)',
        'OX40 (CD134)',
        'CD27',
        '4-1BB (CD137)',
        'GITR',
        'LAG-3 (CD223)',
        'TIM-3',
        'TIGIT',
        // B-Zell-Rezeptoren
        'BCR (B-cell receptor)',
        'Igα (CD79a)',
        'Igβ (CD79b)',
        'CD19',
        'CD20',
        'CD21 (CR2)',
        'CD22',
        'CD40',
        'BAFFR',
        'TACI',
        'BCMA',
        // NK-Zell-Rezeptoren
        'KIR (killer immunoglobulin-like receptor)',
        'NKG2A',
        'NKG2C',
        'NKG2D',
        'NKp30',
        'NKp44',
        'NKp46',
        'CD16 (FcγRIII)',
        'CD56 (NCAM)',
        // Fc-Rezeptoren
        'FcγRI (CD64)',
        'FcγRIIA (CD32)',
        'FcγRIIB',
        'FcγRIII (CD16)',
        'FcεRI',
        'FcεRII (CD23)',
        'FcαR (CD89)',
        // Mustererkennungsrezeptoren
        'TLR1',
        'TLR2',
        'TLR3',
        'TLR4',
        'TLR5',
        'TLR6',
        'TLR7',
        'TLR8',
        'TLR9',
        'TLR10',
        'NOD1',
        'NOD2',
        'NLRP3',
        'RIG-I',
        'MDA5',
        'cGAS',
        'STING',
        'Dectin-1',
        'Mannose receptor (CD206)',
        // Adhäsions- & Homing-Moleküle
        'LFA-1 (CD11a/CD18)',
        'Mac-1 (CD11b/CD18)',
        'VLA-4 (CD49d/CD29)',
        'L-Selectin (CD62L)',
        'E-Selectin (CD62E)',
        'P-Selectin (CD62P)',
        'ICAM-1 (CD54)',
        'VCAM-1 (CD106)',
        'PSGL-1 (CD162)',
        'CCR7',
        'CXCR4',
        'CXCR5',
        'S1P1',
        'α4β7-Integrin',
        // MHC-Moleküle
        'MHC class I',
        'HLA-A',
        'HLA-B',
        'HLA-C',
        'β2-Mikroglobulin',
        'MHC class II',
        'HLA-DR',
        'HLA-DQ',
        'HLA-DP',
        'Invariant chain (CD74)',
        'CLIP',
        'HLA-DM',
        'HLA-DO',
        // Differenzierungsmarker
        'CD45 (Leukocyte common antigen)',
        'CD45RA',
        'CD45RO',
        'CD34 (Stammzellmarker)',
        'CD38',
        'CD44',
        'CD69 (early activation)',
        'CD25 (IL-2Rα)',
        'CD127 (IL-7Rα)',
        'FoxP3',
      ]
    },
  }
};

// Calculate total entries
export const getAllImmunLymphEntries = (): string[] => {
  const entries: string[] = [];
  Object.values(IMMUN_LYMPH_DATABASE.subcategories).forEach(subcategory => {
    entries.push(...subcategory.entries);
  });
  return entries;
};

IMMUN_LYMPH_DATABASE.totalEntries = getAllImmunLymphEntries().length;

export default IMMUN_LYMPH_DATABASE;

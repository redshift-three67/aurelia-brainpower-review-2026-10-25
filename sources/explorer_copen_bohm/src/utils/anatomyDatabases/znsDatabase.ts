// Zentrales Nervensystem (ZNS) - Höchst detaillierte anatomische Datenbank
// Basierend auf Terminologia Anatomica (TA2) und FMA Ontology

export const ZNS_DATABASE = {
  name: "Zentrales Nervensystem (ZNS)",
  category: "Neurologie",
  totalEntries: 0, // wird berechnet
  
  subcategories: {
    // ==========================================
    // GROSSHIRN (TELENCEPHALON)
    // ==========================================
    grosshirn: {
      name: "Großhirn (Telencephalon)",
      entries: [
        // Frontallappen
        "Lobus frontalis",
        "Gyrus praecentralis",
        "Gyrus frontalis superior",
        "Gyrus frontalis medius",
        "Gyrus frontalis inferior",
        "Pars orbitalis",
        "Pars triangularis",
        "Pars opercularis",
        "Gyrus rectus",
        "Gyri orbitales",
        "Sulcus praecentralis",
        "Sulcus frontalis superior",
        "Sulcus frontalis inferior",
        "Brodmann-Areal 4 (Primärer motorischer Kortex)",
        "Brodmann-Areal 6 (Prämotorischer Kortex)",
        "Brodmann-Areal 8 (Frontales Augenfeld)",
        "Brodmann-Areal 9 (Dorsolateraler präfrontaler Kortex)",
        "Brodmann-Areal 10 (Frontopolarer Kortex)",
        "Brodmann-Areal 11 (Orbitofrontaler Kortex)",
        "Brodmann-Areal 44 (Broca-Areal pars opercularis)",
        "Brodmann-Areal 45 (Broca-Areal pars triangularis)",
        "Brodmann-Areal 46 (Dorsolateraler präfrontaler Kortex)",
        "Brodmann-Areal 47 (Pars orbitalis)",
        
        // Parietallappen
        "Lobus parietalis",
        "Gyrus postcentralis",
        "Lobulus parietalis superior",
        "Lobulus parietalis inferior",
        "Gyrus supramarginalis",
        "Gyrus angularis",
        "Precuneus",
        "Sulcus postcentralis",
        "Sulcus intraparietalis",
        "Brodmann-Areal 1 (Primärer somatosensorischer Kortex)",
        "Brodmann-Areal 2 (Primärer somatosensorischer Kortex)",
        "Brodmann-Areal 3 (Primärer somatosensorischer Kortex)",
        "Brodmann-Areal 5 (Somatosensorischer Assoziationskortex)",
        "Brodmann-Areal 7 (Somatosensorischer Assoziationskortex)",
        "Brodmann-Areal 39 (Gyrus angularis)",
        "Brodmann-Areal 40 (Gyrus supramarginalis)",
        
        // Temporallappen
        "Lobus temporalis",
        "Gyrus temporalis superior",
        "Gyrus temporalis medius",
        "Gyrus temporalis inferior",
        "Gyrus fusiformis",
        "Gyrus parahippocampalis",
        "Uncus",
        "Planum temporale",
        "Gyrus transversus temporalis (Heschl)",
        "Sulcus temporalis superior",
        "Sulcus temporalis inferior",
        "Sulcus collateralis",
        "Brodmann-Areal 20 (Inferiorer temporaler Kortex)",
        "Brodmann-Areal 21 (Mittlerer temporaler Kortex)",
        "Brodmann-Areal 22 (Superiorer temporaler Kortex)",
        "Brodmann-Areal 37 (Fusiformer Kortex)",
        "Brodmann-Areal 38 (Temporalpol)",
        "Brodmann-Areal 41 (Primärer auditorischer Kortex)",
        "Brodmann-Areal 42 (Auditorischer Assoziationskortex)",
        "Wernicke-Areal",
        
        // Okzipitallappen
        "Lobus occipitalis",
        "Cuneus",
        "Gyrus lingualis",
        "Gyrus occipitalis superior",
        "Gyrus occipitalis medius",
        "Gyrus occipitalis inferior",
        "Sulcus calcarinus",
        "Sulcus parietooccipitalis",
        "Brodmann-Areal 17 (Primärer visueller Kortex V1)",
        "Brodmann-Areal 18 (Sekundärer visueller Kortex V2)",
        "Brodmann-Areal 19 (Visueller Assoziationskortex V3-V5)",
        
        // Limbisches System
        "Gyrus cinguli",
        "Gyrus cinguli anterior",
        "Gyrus cinguli posterior",
        "Isthmus gyri cinguli",
        "Brodmann-Areal 23 (Posteriorer cingulärer Kortex)",
        "Brodmann-Areal 24 (Anteriorer cingulärer Kortex)",
        "Brodmann-Areal 25 (Subgenualer Kortex)",
        "Brodmann-Areal 26 (Retrosplenialer Kortex)",
        "Brodmann-Areal 29 (Retrosplenialer Kortex)",
        "Brodmann-Areal 30 (Retrosplenialer Kortex)",
        "Brodmann-Areal 31 (Dorsaler posteriorer cingulärer Kortex)",
        "Brodmann-Areal 32 (Dorsaler anteriorer cingulärer Kortex)",
        "Brodmann-Areal 33 (Anteriorer cingulärer Kortex)",
        
        // Insula
        "Insula (Inselrinde)",
        "Gyri breves insulae",
        "Gyri longi insulae",
        "Sulcus centralis insulae",
        "Brodmann-Areal 13 (Anteriore Insula)",
        "Brodmann-Areal 14 (Posteriore Insula)",
        "Brodmann-Areal 15 (Anteriore Insula)",
        "Brodmann-Areal 16 (Posteriore Insula)",
        
        // Basalganglien
        "Nucleus caudatus",
        "Caput nuclei caudati",
        "Corpus nuclei caudati",
        "Cauda nuclei caudati",
        "Putamen",
        "Globus pallidus",
        "Globus pallidus externus (GPe)",
        "Globus pallidus internus (GPi)",
        "Striatum (Corpus striatum)",
        "Nucleus accumbens",
        "Claustrum",
        "Substantia innominata",
        "Nucleus basalis Meynert",
        
        // Hippocampus-Formation
        "Hippocampus",
        "Cornu Ammonis (CA1)",
        "Cornu Ammonis (CA2)",
        "Cornu Ammonis (CA3)",
        "Cornu Ammonis (CA4)",
        "Gyrus dentatus",
        "Subiculum",
        "Presubiculum",
        "Parasubiculum",
        "Fimbria hippocampi",
        "Alveus hippocampi",
        "Fornix",
        "Crus fornicis",
        "Corpus fornicis",
        "Columna fornicis",
        
        // Amygdala
        "Corpus amygdaloideum",
        "Nucleus basolateralis amygdalae",
        "Nucleus lateralis amygdalae",
        "Nucleus basalis amygdalae",
        "Nucleus centralis amygdalae",
        "Nucleus medialis amygdalae",
        "Nucleus corticalis amygdalae",
        
        // Kommissuren
        "Corpus callosum",
        "Rostrum corporis callosi",
        "Genu corporis callosi",
        "Truncus corporis callosi",
        "Splenium corporis callosi",
        "Commissura anterior",
        "Commissura posterior",
        "Commissura hippocampi",
        
        // Weiße Substanz
        "Capsula interna",
        "Crus anterius capsulae internae",
        "Genu capsulae internae",
        "Crus posterius capsulae internae",
        "Capsula externa",
        "Capsula extrema",
        "Corona radiata",
        "Centrum semiovale",
        "Fasciculus longitudinalis superior",
        "Fasciculus longitudinalis inferior",
        "Fasciculus arcuatus",
        "Fasciculus uncinatus",
        "Cingulum",
        "Tractus corticospinalis",
        "Radiatio optica"
      ]
    },
    
    // ==========================================
    // ZWISCHENHIRN (DIENCEPHALON)
    // ==========================================
    zwischenhirn: {
      name: "Zwischenhirn (Diencephalon)",
      entries: [
        // Thalamus
        "Thalamus",
        "Pulvinar thalami",
        "Nucleus anterior thalami",
        "Nucleus ventralis anterior (VA)",
        "Nucleus ventralis lateralis (VL)",
        "Nucleus ventralis posterolateralis (VPL)",
        "Nucleus ventralis posteromedialis (VPM)",
        "Nucleus lateralis dorsalis",
        "Nucleus lateralis posterior",
        "Nucleus medialis dorsalis",
        "Nuclei intralaminares thalami",
        "Nucleus centromedianus",
        "Nucleus parafascicularis",
        "Nucleus reticularis thalami",
        "Corpus geniculatum laterale",
        "Corpus geniculatum mediale",
        "Nucleus habenulae medialis",
        "Nucleus habenulae lateralis",
        "Stria medullaris thalami",
        "Adhesio interthalamica",
        
        // Hypothalamus
        "Hypothalamus",
        "Nucleus supraopticus",
        "Nucleus paraventricularis",
        "Nucleus suprachiasmaticus",
        "Nucleus preopticus medialis",
        "Nucleus preopticus lateralis",
        "Nucleus anterior hypothalami",
        "Nucleus dorsomedialis hypothalami",
        "Nucleus ventromedialis hypothalami",
        "Nucleus arcuatus",
        "Nucleus lateralis hypothalami",
        "Nucleus posterior hypothalami",
        "Corpus mamillare",
        "Nucleus mamillaris medialis",
        "Nucleus mamillaris lateralis",
        "Tuber cinereum",
        "Eminentia mediana",
        "Infundibulum",
        "Neurohypophyse",
        "Adenohypophyse",
        
        // Epithalamus
        "Epithalamus",
        "Glandula pinealis (Epiphyse)",
        "Habenula",
        "Commissura habenularum",
        "Commissura posterior",
        
        // Subthalamus
        "Subthalamus",
        "Nucleus subthalamicus",
        "Zona incerta",
        "Nucleus tegmentalis pedunculopontinus"
      ]
    },
    
    // ==========================================
    // MITTELHIRN (MESENCEPHALON)
    // ==========================================
    mittelhirn: {
      name: "Mittelhirn (Mesencephalon)",
      entries: [
        // Tectum
        "Tectum mesencephali",
        "Colliculus superior",
        "Stratum zonale colliculi superioris",
        "Stratum griseum superficiale",
        "Stratum opticum",
        "Stratum griseum intermedium",
        "Stratum griseum profundum",
        "Colliculus inferior",
        "Nucleus centralis colliculi inferioris",
        "Nucleus externus colliculi inferioris",
        "Brachium colliculi superioris",
        "Brachium colliculi inferioris",
        
        // Tegmentum
        "Tegmentum mesencephali",
        "Substantia nigra",
        "Pars compacta substantiae nigrae",
        "Pars reticulata substantiae nigrae",
        "Nucleus ruber",
        "Nucleus oculomotorius",
        "Nucleus Edinger-Westphal",
        "Nucleus trochlearis",
        "Nucleus interpeduncularis",
        "Nucleus raphe dorsalis",
        "Nucleus raphe medianus",
        "Area tegmentalis ventralis (VTA)",
        "Formatio reticularis mesencephali",
        "Locus caeruleus",
        "Nucleus cuneiformis",
        "Nucleus pedunculopontinus",
        "Decussatio tegmenti anterior",
        "Decussatio tegmenti posterior",
        
        // Pedunculi cerebri
        "Pedunculus cerebri",
        "Crus cerebri",
        "Tractus corticospinalis",
        "Tractus corticonuclearis",
        "Tractus corticopontinus",
        "Fossa interpeduncularis",
        
        // Aquädukt
        "Aqueductus cerebri (Sylvii)",
        "Substantia grisea centralis (periaqueductal gray)"
      ]
    },
    
    // ==========================================
    // HINTERHIRN (RHOMBENCEPHALON)
    // ==========================================
    bruecke: {
      name: "Brücke (Pons)",
      entries: [
        // Basis pontis
        "Pons",
        "Basis pontis",
        "Nuclei pontis",
        "Fibrae pontis transversae",
        "Pedunculus cerebellaris medius",
        
        // Tegmentum pontis
        "Tegmentum pontis",
        "Nucleus motorius nervi trigemini",
        "Nucleus principalis nervi trigemini",
        "Nucleus mesencephalicus nervi trigemini",
        "Nucleus nervi abducentis",
        "Nucleus nervi facialis",
        "Nucleus salivatorius superior",
        "Nucleus lacrimalis",
        "Nuclei vestibulares",
        "Nucleus vestibularis superior",
        "Nucleus vestibularis lateralis (Deiters)",
        "Nucleus vestibularis medialis",
        "Nucleus vestibularis inferior",
        "Nuclei cochleares",
        "Nucleus cochlearis ventralis",
        "Nucleus cochlearis dorsalis",
        "Nucleus raphes pontis",
        "Nucleus reticularis pontis oralis",
        "Nucleus reticularis pontis caudalis",
        "Nucleus parabrachialis lateralis",
        "Nucleus parabrachialis medialis",
        "Lemniscus lateralis",
        "Lemniscus medialis",
        "Corpus trapezoideum",
        "Pedunculus cerebellaris superior"
      ]
    },
    
    verlaengertesMark: {
      name: "Verlängertes Mark (Medulla oblongata)",
      entries: [
        // Dorsale Strukturen
        "Medulla oblongata",
        "Nucleus gracilis",
        "Nucleus cuneatus",
        "Nucleus cuneatus accessorius",
        "Tuberculum gracile",
        "Tuberculum cuneatum",
        "Fasciculus gracilis",
        "Fasciculus cuneatus",
        "Obex",
        "Area postrema",
        
        // Hirnnerven-Kerne
        "Nucleus nervi hypoglossi",
        "Nucleus dorsalis nervi vagi",
        "Nucleus ambiguus",
        "Nucleus tractus solitarii",
        "Nucleus salivatorius inferior",
        "Nucleus spinalis nervi trigemini",
        "Nucleus nervi accessorii",
        
        // Olivenkomplex
        "Oliva inferior",
        "Nucleus olivaris principalis",
        "Nucleus olivaris accessorius dorsalis",
        "Nucleus olivaris accessorius medialis",
        
        // Formatio reticularis
        "Formatio reticularis medullae",
        "Nucleus reticularis gigantocellularis",
        "Nucleus reticularis parvocellularis",
        "Nucleus raphes magnus",
        "Nucleus raphes obscurus",
        "Nucleus raphes pallidus",
        
        // Pyramiden
        "Pyramis medullae",
        "Decussatio pyramidum",
        "Tractus corticospinalis lateralis",
        "Tractus corticospinalis anterior",
        
        // Weitere Strukturen
        "Pedunculus cerebellaris inferior",
        "Corpus restiforme",
        "Lemniscus medialis",
        "Fasciculus longitudinalis medialis"
      ]
    },
    
    // ==========================================
    // KLEINHIRN (CEREBELLUM)
    // ==========================================
    kleinhirn: {
      name: "Kleinhirn (Cerebellum)",
      entries: [
        // Vermis
        "Vermis cerebelli",
        "Lingula cerebelli",
        "Lobulus centralis",
        "Culmen",
        "Declive",
        "Folium vermis",
        "Tuber vermis",
        "Pyramis vermis",
        "Uvula vermis",
        "Nodulus",
        
        // Hemisphären anterior
        "Hemisphaerium cerebelli",
        "Lobus anterior cerebelli",
        "Lobulus quadrangularis anterior",
        "Lobulus quadrangularis posterior",
        "Lobulus simplex",
        
        // Hemisphären posterior
        "Lobus posterior cerebelli",
        "Lobulus semilunaris superior",
        "Lobulus semilunaris inferior",
        "Lobulus gracilis",
        "Lobulus biventer",
        "Tonsilla cerebelli",
        "Lobulus parafloccularis",
        
        // Flocculonodularer Lappen
        "Lobus flocculonodularis",
        "Flocculus",
        "Pedunculus flocculi",
        
        // Kleinhirnkerne
        "Nucleus dentatus",
        "Nucleus emboliformis",
        "Nucleus globosus",
        "Nucleus fastigii",
        
        // Kleinhirnrinde
        "Cortex cerebelli",
        "Stratum moleculare",
        "Stratum ganglionare (Purkinje-Zellen)",
        "Stratum granulosum",
        "Cellulae Purkinje",
        "Cellulae granulosae",
        "Cellulae stellatae",
        "Cellulae Golgi",
        "Fibrae parallelae",
        "Fibrae muscoideae (Moosfasern)",
        "Fibrae climbentes (Kletterfasern)",
        
        // Kleinhirnstiele
        "Pedunculus cerebellaris superior",
        "Pedunculus cerebellaris medius",
        "Pedunculus cerebellaris inferior",
        "Velum medullare superius",
        "Velum medullare inferius"
      ]
    },
    
    // ==========================================
    // RÜCKENMARK (MEDULLA SPINALIS)
    // ==========================================
    rueckenmark: {
      name: "Rückenmark (Medulla spinalis)",
      entries: [
        // Segmente
        "Medulla spinalis",
        "Pars cervicalis medullae spinalis",
        "Intumescentia cervicalis",
        "Segmentum cervicale C1",
        "Segmentum cervicale C2",
        "Segmentum cervicale C3",
        "Segmentum cervicale C4",
        "Segmentum cervicale C5",
        "Segmentum cervicale C6",
        "Segmentum cervicale C7",
        "Segmentum cervicale C8",
        "Pars thoracica medullae spinalis",
        "Segmentum thoracicum Th1",
        "Segmentum thoracicum Th2",
        "Segmentum thoracicum Th3",
        "Segmentum thoracicum Th4",
        "Segmentum thoracicum Th5",
        "Segmentum thoracicum Th6",
        "Segmentum thoracicum Th7",
        "Segmentum thoracicum Th8",
        "Segmentum thoracicum Th9",
        "Segmentum thoracicum Th10",
        "Segmentum thoracicum Th11",
        "Segmentum thoracicum Th12",
        "Pars lumbalis medullae spinalis",
        "Intumescentia lumbosacralis",
        "Segmentum lumbale L1",
        "Segmentum lumbale L2",
        "Segmentum lumbale L3",
        "Segmentum lumbale L4",
        "Segmentum lumbale L5",
        "Pars sacralis medullae spinalis",
        "Segmentum sacrale S1",
        "Segmentum sacrale S2",
        "Segmentum sacrale S3",
        "Segmentum sacrale S4",
        "Segmentum sacrale S5",
        "Segmentum coccygeum Co1",
        "Conus medullaris",
        "Filum terminale",
        "Cauda equina",
        
        // Graue Substanz
        "Substantia grisea",
        "Cornu anterius (Vorderhorn)",
        "Cornu posterius (Hinterhorn)",
        "Cornu laterale",
        "Commissura grisea anterior",
        "Commissura grisea posterior",
        "Canalis centralis",
        "Substantia gelatinosa (Rolandi)",
        "Nucleus proprius",
        "Nucleus dorsalis (Clarke)",
        "Nucleus intermediolateralis",
        "Nucleus intermediomedialis",
        
        // Rexed-Laminae
        "Lamina I (Marginalzone)",
        "Lamina II (Substantia gelatinosa)",
        "Lamina III",
        "Lamina IV",
        "Lamina V",
        "Lamina VI",
        "Lamina VII (Nucleus intermedius)",
        "Lamina VIII",
        "Lamina IX (Motoneurone)",
        "Lamina X (Zona centralis)",
        
        // Weiße Substanz
        "Substantia alba",
        "Funiculus anterior",
        "Funiculus lateralis",
        "Funiculus posterior",
        "Commissura alba anterior",
        
        // Aufsteigende Bahnen
        "Tractus spinothalamicus lateralis",
        "Tractus spinothalamicus anterior",
        "Fasciculus gracilis",
        "Fasciculus cuneatus",
        "Tractus spinocerebellaris posterior",
        "Tractus spinocerebellaris anterior",
        "Tractus spinotectalis",
        "Tractus spinoreticularis",
        "Tractus spinoolivaris",
        
        // Absteigende Bahnen
        "Tractus corticospinalis lateralis",
        "Tractus corticospinalis anterior",
        "Tractus rubrospinalis",
        "Tractus vestibulospinalis lateralis",
        "Tractus vestibulospinalis medialis",
        "Tractus reticulospinalis",
        "Tractus tectospinalis",
        "Tractus olivospinalis",
        "Fasciculus longitudinalis medialis"
      ]
    },
    
    // ==========================================
    // HIRNNERVEN (NERVI CRANIALES)
    // ==========================================
    hirnnerven: {
      name: "Hirnnerven (Nervi craniales)",
      entries: [
        // N. I - Olfactorius
        "Nervus olfactorius (I)",
        "Fila olfactoria",
        "Bulbus olfactorius",
        "Tractus olfactorius",
        "Stria olfactoria lateralis",
        "Stria olfactoria medialis",
        "Trigonum olfactorium",
        
        // N. II - Opticus
        "Nervus opticus (II)",
        "Papilla nervi optici",
        "Chiasma opticum",
        "Tractus opticus",
        "Radiatio optica",
        
        // N. III - Oculomotorius
        "Nervus oculomotorius (III)",
        "Nucleus nervi oculomotorii",
        "Nucleus Edinger-Westphal",
        "Ramus superior n. oculomotorii",
        "Ramus inferior n. oculomotorii",
        "Radix parasympathica ganglii ciliaris",
        
        // N. IV - Trochlearis
        "Nervus trochlearis (IV)",
        "Nucleus nervi trochlearis",
        "Decussatio nervorum trochlearium",
        
        // N. V - Trigeminus
        "Nervus trigeminus (V)",
        "Radix sensoria n. trigemini",
        "Radix motoria n. trigemini",
        "Ganglion trigeminale (Gasseri)",
        "Nervus ophthalmicus (V1)",
        "Nervus frontalis",
        "Nervus supraorbitalis",
        "Nervus supratrochlearis",
        "Nervus lacrimalis",
        "Nervus nasociliaris",
        "Nervus ethmoidalis anterior",
        "Nervus ethmoidalis posterior",
        "Nervus infratrochlearis",
        "Nervi ciliares longi",
        "Nervus maxillaris (V2)",
        "Nervus zygomaticus",
        "Nervus infraorbitalis",
        "Nervi alveolares superiores",
        "Rami ganglionares",
        "Nervus mandibularis (V3)",
        "Nervus auriculotemporalis",
        "Nervus lingualis",
        "Nervus alveolaris inferior",
        "Nervus mentalis",
        "Nervus buccalis",
        "Nervus massetericus",
        "Nervi temporales profundi",
        "Nervus pterygoideus lateralis",
        "Nervus pterygoideus medialis",
        "Nervus mylohyoideus",
        
        // N. VI - Abducens
        "Nervus abducens (VI)",
        "Nucleus nervi abducentis",
        
        // N. VII - Facialis
        "Nervus facialis (VII)",
        "Nucleus nervi facialis",
        "Nucleus salivatorius superior",
        "Genu nervi facialis",
        "Ganglion geniculi",
        "Nervus petrosus major",
        "Nervus stapedius",
        "Chorda tympani",
        "Rami temporales",
        "Rami zygomatici",
        "Rami buccales",
        "Ramus marginalis mandibulae",
        "Ramus colli",
        "Nervus auricularis posterior",
        "Nervus intermedius",
        
        // N. VIII - Vestibulocochlearis
        "Nervus vestibulocochlearis (VIII)",
        "Nervus vestibularis",
        "Ganglion vestibulare (Scarpa)",
        "Nervus utricularis",
        "Nervus saccularis",
        "Nervus ampullaris anterior",
        "Nervus ampullaris lateralis",
        "Nervus ampullaris posterior",
        "Nervus cochlearis",
        "Ganglion spirale cochleae",
        
        // N. IX - Glossopharyngeus
        "Nervus glossopharyngeus (IX)",
        "Nucleus ambiguus",
        "Nucleus salivatorius inferior",
        "Nucleus tractus solitarii",
        "Ganglion superius n. glossopharyngei",
        "Ganglion inferius n. glossopharyngei (petrosum)",
        "Nervus tympanicus",
        "Plexus tympanicus",
        "Nervus petrosus minor",
        "Ramus sinus carotici",
        "Rami pharyngei",
        "Rami tonsillares",
        "Rami linguales",
        
        // N. X - Vagus
        "Nervus vagus (X)",
        "Nucleus dorsalis nervi vagi",
        "Nucleus ambiguus",
        "Ganglion superius n. vagi (jugulare)",
        "Ganglion inferius n. vagi (nodosum)",
        "Ramus meningeus",
        "Ramus auricularis",
        "Rami pharyngei",
        "Nervus laryngeus superior",
        "Ramus externus n. laryngei superioris",
        "Ramus internus n. laryngei superioris",
        "Nervus laryngeus recurrens",
        "Rami cardiaci cervicales superiores",
        "Rami cardiaci cervicales inferiores",
        "Rami cardiaci thoracici",
        "Rami bronchiales",
        "Plexus pulmonalis",
        "Plexus oesophageus",
        "Truncus vagalis anterior",
        "Truncus vagalis posterior",
        "Rami gastrici",
        "Rami hepatici",
        "Rami coeliaci",
        "Rami renales",
        
        // N. XI - Accessorius
        "Nervus accessorius (XI)",
        "Radix cranialis n. accessorii",
        "Radix spinalis n. accessorii",
        "Nucleus nervi accessorii",
        "Ramus internus",
        "Ramus externus",
        
        // N. XII - Hypoglossus
        "Nervus hypoglossus (XII)",
        "Nucleus nervi hypoglossi",
        "Rami linguales"
      ]
    },
    
    // ==========================================
    // HIRNHÄUTE UND VENTRIKELSYSTEM
    // ==========================================
    meningen: {
      name: "Hirnhäute und Ventrikelsystem",
      entries: [
        // Meningen
        "Dura mater encephali",
        "Falx cerebri",
        "Tentorium cerebelli",
        "Falx cerebelli",
        "Diaphragma sellae",
        "Sinus durae matris",
        "Sinus sagittalis superior",
        "Sinus sagittalis inferior",
        "Sinus rectus",
        "Confluens sinuum",
        "Sinus transversus",
        "Sinus sigmoideus",
        "Sinus cavernosus",
        "Sinus petrosus superior",
        "Sinus petrosus inferior",
        "Sinus occipitalis",
        "Sinus sphenoparietalis",
        "Dura mater spinalis",
        "Arachnoidea mater",
        "Granulationes arachnoideae (Pacchioni)",
        "Spatium subarachnoideum",
        "Cisterna magna (cerebellomedullaris)",
        "Cisterna pontis",
        "Cisterna interpeduncularis",
        "Cisterna chiasmatica",
        "Cisterna ambiens",
        "Cisterna quadrigemina",
        "Cisterna lumbalis",
        "Pia mater",
        "Tela choroidea",
        
        // Ventrikelsystem
        "Ventriculus lateralis",
        "Cornu frontale (anterius)",
        "Pars centralis",
        "Cornu temporale (inferius)",
        "Cornu occipitale (posterius)",
        "Atrium ventriculi lateralis",
        "Foramen interventriculare (Monroi)",
        "Plexus choroideus ventriculi lateralis",
        "Ventriculus tertius",
        "Recessus supraopticus",
        "Recessus infundibularis",
        "Recessus pinealis",
        "Recessus suprapinealis",
        "Plexus choroideus ventriculi tertii",
        "Aqueductus cerebri (Sylvii)",
        "Ventriculus quartus",
        "Recessus lateralis ventriculi quarti",
        "Apertura lateralis ventriculi quarti (Luschka)",
        "Apertura mediana ventriculi quarti (Magendie)",
        "Plexus choroideus ventriculi quarti",
        "Canalis centralis medullae spinalis",
        
        // Liquor
        "Liquor cerebrospinalis"
      ]
    },
    
    // ==========================================
    // HIRNGEFÄSSE
    // ==========================================
    gefaesse: {
      name: "Hirngefäße",
      entries: [
        // Arterien anterior
        "Arteria carotis interna",
        "Pars cervicalis a. carotidis internae",
        "Pars petrosa a. carotidis internae",
        "Pars cavernosa a. carotidis internae",
        "Pars cerebralis a. carotidis internae",
        "Arteria ophthalmica",
        "Arteria cerebri anterior",
        "Segmentum A1 (precommunicale)",
        "Segmentum A2 (postcommunicale)",
        "Arteria communicans anterior",
        "Arteria frontopolaris",
        "Arteria callosomarginalis",
        "Arteria pericallosa",
        "Arteria cerebri media",
        "Segmentum M1 (sphenoidale)",
        "Segmentum M2 (insulare)",
        "Segmentum M3 (operculare)",
        "Segmentum M4 (corticale)",
        "Arteriae lenticulostriatae",
        "Arteria communicans posterior",
        "Arteria choroidea anterior",
        
        // Arterien posterior
        "Arteria vertebralis",
        "Pars prevertebralis",
        "Pars transversaria",
        "Pars atlantica",
        "Pars intracranialis",
        "Arteria spinalis anterior",
        "Arteriae spinales posteriores",
        "Arteria cerebelli inferior posterior (PICA)",
        "Arteria basilaris",
        "Arteria cerebelli inferior anterior (AICA)",
        "Arteria labyrinthi",
        "Arteriae pontis",
        "Arteria cerebelli superior",
        "Arteria cerebri posterior",
        "Segmentum P1 (precommunicale)",
        "Segmentum P2 (postcommunicale)",
        "Arteriae thalamoperforantes",
        "Arteria choroidea posterior",
        "Arteria occipitalis lateralis",
        "Arteria occipitalis medialis",
        "Arteria calcarina",
        "Arteria parietooccipitalis",
        
        // Circulus arteriosus
        "Circulus arteriosus cerebri (Willisi)",
        
        // Venen
        "Vena cerebri magna (Galeni)",
        "Sinus rectus",
        "Venae cerebri internae",
        "Vena basalis (Rosenthal)",
        "Vena thalamostriata",
        "Venae cerebri superiores",
        "Vena cerebri media superficialis",
        "Vena anastomotica superior (Trolard)",
        "Vena anastomotica inferior (Labbé)",
        "Venae cerebelli",
        "Venae cerebri inferiores"
      ]
    }
  }
};

// Hilfsfunktion zum Extrahieren aller Einträge
export const getAllZNSEntries = (): string[] => {
  const allEntries: string[] = [];
  Object.values(ZNS_DATABASE.subcategories).forEach(subcategory => {
    allEntries.push(...subcategory.entries);
  });
  return allEntries;
};

// Aktualisiere die Gesamtzahl
ZNS_DATABASE.totalEntries = getAllZNSEntries().length;

export default ZNS_DATABASE;

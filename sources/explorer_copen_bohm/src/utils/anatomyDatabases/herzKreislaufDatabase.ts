// Herz-Kreislauf-System - Höchst detaillierte anatomische Datenbank
// Basierend auf Terminologia Anatomica (TA2) und FMA Ontology

export const HERZ_KREISLAUF_DATABASE = {
  name: "Herz-Kreislauf-System",
  category: "Kardiologie",
  totalEntries: 0, // wird berechnet
  
  subcategories: {
    // ==========================================
    // HERZ (COR)
    // ==========================================
    herz: {
      name: "Herz (Cor)",
      entries: [
        // Herzwand
        "Cor (Herz)",
        "Basis cordis",
        "Apex cordis",
        "Facies sternocostalis",
        "Facies diaphragmatica",
        "Facies pulmonalis dextra",
        "Facies pulmonalis sinistra",
        "Sulcus coronarius",
        "Sulcus interventricularis anterior",
        "Sulcus interventricularis posterior",
        
        // Herzschichten
        "Pericardium",
        "Pericardium fibrosum",
        "Pericardium serosum",
        "Lamina parietalis pericardii serosi",
        "Lamina visceralis pericardii serosi (Epicardium)",
        "Cavitas pericardialis",
        "Sinus transversus pericardii",
        "Sinus obliquus pericardii",
        "Epicardium",
        "Myocardium",
        "Endocardium",
        
        // Rechter Vorhof
        "Atrium dextrum",
        "Auricula dextra",
        "Musculi pectinati",
        "Crista terminalis",
        "Sulcus terminalis",
        "Sinus venarum cavarum",
        "Ostium venae cavae superioris",
        "Ostium venae cavae inferioris",
        "Valvula venae cavae inferioris (Eustachii)",
        "Ostium sinus coronarii",
        "Valvula sinus coronarii (Thebesii)",
        "Fossa ovalis",
        "Limbus fossae ovalis",
        "Tuberculum intervenosum (Loweri)",
        "Septum interatriale",
        
        // Linker Vorhof
        "Atrium sinistrum",
        "Auricula sinistra",
        "Ostia venarum pulmonalium",
        "Valvula foraminis ovalis",
        
        // Rechter Ventrikel
        "Ventriculus dexter",
        "Ostium atrioventriculare dextrum",
        "Valva atrioventricularis dextra (tricuspidalis)",
        "Cuspis anterior",
        "Cuspis posterior",
        "Cuspis septalis",
        "Chordae tendineae",
        "Musculus papillaris anterior",
        "Musculus papillaris posterior",
        "Musculus papillaris septalis",
        "Trabeculae carneae",
        "Trabecula septomarginalis (Moderatorband)",
        "Conus arteriosus (Infundibulum)",
        "Crista supraventricularis",
        "Ostium trunci pulmonalis",
        "Valva trunci pulmonalis",
        "Valvula semilunaris anterior",
        "Valvula semilunaris dextra",
        "Valvula semilunaris sinistra",
        "Nodulus valvulae semilunaris (Arantii)",
        "Lunula valvulae semilunaris",
        "Sinus trunci pulmonalis",
        
        // Linker Ventrikel
        "Ventriculus sinister",
        "Ostium atrioventriculare sinistrum",
        "Valva atrioventricularis sinistra (mitralis)",
        "Cuspis anterior (aortalis)",
        "Cuspis posterior (muralis)",
        "Commissura anterolateralis",
        "Commissura posteromedialis",
        "Chordae tendineae",
        "Musculus papillaris anterior",
        "Musculus papillaris posterior",
        "Trabeculae carneae",
        "Vestibulum aortae",
        "Ostium aortae",
        "Valva aortae",
        "Valvula semilunaris dextra (coronaria dextra)",
        "Valvula semilunaris sinistra (coronaria sinistra)",
        "Valvula semilunaris posterior (non-coronaria)",
        "Sinus aortae (Valsalva)",
        "Septum interventriculare",
        "Pars membranacea septi",
        "Pars muscularis septi",
        
        // Herzgewebe
        "Myocardium atriale",
        "Myocardium ventriculare",
        "Kardiomyozyten",
        "Glanzstreifen (Disci intercalares)",
        "Gap junctions",
        "T-Tubuli",
        "Sarkoplasmatisches Retikulum",
        "Mitochondrien der Herzmuskelzellen"
      ]
    },
    
    // ==========================================
    // REIZLEITUNGSSYSTEM
    // ==========================================
    reizleitung: {
      name: "Reizleitungssystem",
      entries: [
        "Systema conducens cordis",
        
        // Sinusknoten
        "Nodus sinuatrialis (Keith-Flack)",
        "Cellulae P (Schrittmacherzellen)",
        "Cellulae transitionis",
        "Arteria nodi sinuatrialis",
        
        // Internodalbahnen
        "Tractus internodales",
        "Fasciculus anterior (Bachmann)",
        "Fasciculus medius (Wenckebach)",
        "Fasciculus posterior (Thorel)",
        
        // AV-Knoten
        "Nodus atrioventricularis (Aschoff-Tawara)",
        "Zona transitoria",
        "Zona compacta",
        "Zona penetrans",
        "Arteria nodi atrioventricularis",
        
        // His-Bündel
        "Fasciculus atrioventricularis (His)",
        "Pars penetrans",
        "Pars membranacea",
        "Truncus fasciculi atrioventricularis",
        
        // Tawara-Schenkel
        "Crus dextrum fasciculi atrioventricularis",
        "Ramus anterior cruris dextri",
        "Ramus posterior cruris dextri",
        "Crus sinistrum fasciculi atrioventricularis",
        "Fasciculus anterior sinister",
        "Fasciculus posterior sinister",
        "Fasciculus septalis sinister",
        
        // Purkinje-Fasern
        "Rami subendocardiales (Purkinje)",
        "Cellulae Purkinje",
        "Rete subendocardiale dextrum",
        "Rete subendocardiale sinistrum",
        
        // Elektrodenstandorte
        "Trigona fibrosa",
        "Trigonum fibrosum dextrum",
        "Trigonum fibrosum sinistrum",
        "Anulus fibrosus dexter",
        "Anulus fibrosus sinister",
        "Tendo infundibuli"
      ]
    },
    
    // ==========================================
    // KORONARARTERIEN
    // ==========================================
    koronararterien: {
      name: "Koronararterien",
      entries: [
        "Arteriae coronariae",
        
        // Rechte Koronararterie
        "Arteria coronaria dextra (RCA)",
        "Ostium arteriae coronariae dextrae",
        "Conus arteriosus branch",
        "Ramus nodi sinuatrialis",
        "Ramus atrialis dexter anterior",
        "Ramus atrialis dexter intermedius",
        "Ramus atrialis dexter posterior",
        "Ramus marginalis dexter",
        "Ramus nodi atrioventricularis",
        "Ramus interventricularis posterior (RIVP)",
        "Rami interventriculares septales posteriores",
        "Ramus posterolateralis dexter",
        
        // Linke Koronararterie
        "Arteria coronaria sinistra (LCA)",
        "Ostium arteriae coronariae sinistrae",
        "Truncus arteriae coronariae sinistrae (LM)",
        
        // LAD (RIVA)
        "Ramus interventricularis anterior (LAD/RIVA)",
        "Rami diagonales (D1, D2, D3)",
        "Ramus diagonalis primus",
        "Ramus diagonalis secundus",
        "Rami interventriculares septales anteriores",
        "Ramus septalis primus",
        "Ramus septalis secundus",
        
        // Ramus circumflexus
        "Ramus circumflexus (RCX/LCX)",
        "Ramus atrialis sinister anterior",
        "Ramus atrialis sinister intermedius",
        "Ramus marginalis sinister (OM)",
        "Ramus marginalis obtusus primus (OM1)",
        "Ramus marginalis obtusus secundus (OM2)",
        "Ramus posterolateralis sinister",
        "Ramus atrialis sinister posterior",
        
        // Varianten
        "Ramus intermedius (Zwischengefäß)",
        "Arteria coronaria conalis",
        
        // Anastomosen
        "Anastomoses coronariae",
        "Collateralkreislauf koronar"
      ]
    },
    
    // ==========================================
    // HERZVENEN
    // ==========================================
    herzvenen: {
      name: "Herzvenen",
      entries: [
        "Venae cordis",
        
        // Sinus coronarius System
        "Sinus coronarius",
        "Ostium sinus coronarii",
        "Valvula sinus coronarii (Thebesii)",
        "Vena cardiaca magna",
        "Vena interventricularis anterior",
        "Vena marginalis sinistra",
        "Vena posterior ventriculi sinistri",
        "Vena cardiaca media",
        "Vena interventricularis posterior",
        "Vena cardiaca parva",
        "Vena obliqua atrii sinistri (Marshall)",
        
        // Vordere Herzvenen
        "Venae cardiacae anteriores",
        "Venae atriales dextrae",
        
        // Thebesian Venen
        "Venae cardiacae minimae (Thebesii)",
        "Foramina venarum minimarum"
      ]
    },
    
    // ==========================================
    // AORTA
    // ==========================================
    aorta: {
      name: "Aorta",
      entries: [
        "Aorta",
        
        // Aorta ascendens
        "Aorta ascendens",
        "Bulbus aortae",
        "Sinus aortae dexter",
        "Sinus aortae sinister",
        "Sinus aortae posterior",
        "Junctio sinotubularis",
        
        // Arcus aortae
        "Arcus aortae",
        "Isthmus aortae",
        "Truncus brachiocephalicus",
        "Arteria carotis communis dextra",
        "Arteria subclavia dextra",
        "Arteria carotis communis sinistra",
        "Arteria subclavia sinistra",
        "Ductus arteriosus (Botalli) - obliteriert",
        "Ligamentum arteriosum",
        
        // Aorta descendens thoracica
        "Aorta descendens",
        "Pars thoracica aortae",
        "Rami bronchiales",
        "Rami oesophageales",
        "Rami mediastinales",
        "Rami pericardiaci",
        "Arteriae intercostales posteriores",
        "Arteria intercostalis suprema",
        "Arteriae subcostales",
        "Arteriae phrenicae superiores",
        
        // Aorta abdominalis
        "Pars abdominalis aortae",
        "Truncus coeliacus",
        "Arteria gastrica sinistra",
        "Arteria hepatica communis",
        "Arteria hepatica propria",
        "Arteria gastroduodenalis",
        "Arteria lienalis (splenica)",
        "Arteria mesenterica superior",
        "Arteria pancreaticoduodenalis inferior",
        "Arteriae jejunales",
        "Arteriae ileales",
        "Arteria ileocolica",
        "Arteria colica dextra",
        "Arteria colica media",
        "Arteriae suprarenales mediae",
        "Arteriae renales",
        "Arteria renalis dextra",
        "Arteria renalis sinistra",
        "Arteriae testiculares/ovaricae",
        "Arteria mesenterica inferior",
        "Arteria colica sinistra",
        "Arteriae sigmoideae",
        "Arteria rectalis superior",
        "Arteriae lumbales",
        "Arteria sacralis mediana",
        
        // Bifurcatio
        "Bifurcatio aortae",
        "Arteria iliaca communis dextra",
        "Arteria iliaca communis sinistra"
      ]
    },
    
    // ==========================================
    // ARTERIEN DER OBEREN EXTREMITÄT
    // ==========================================
    arterienOben: {
      name: "Arterien der oberen Extremität",
      entries: [
        // A. subclavia
        "Arteria subclavia",
        "Arteria vertebralis",
        "Arteria thoracica interna (mammaria)",
        "Arteria pericardiacophrenica",
        "Arteria musculophrenica",
        "Arteria epigastrica superior",
        "Truncus thyrocervicalis",
        "Arteria thyroidea inferior",
        "Arteria cervicalis ascendens",
        "Arteria transversa colli (cervicis)",
        "Arteria suprascapularis",
        "Truncus costocervicalis",
        "Arteria cervicalis profunda",
        "Arteria intercostalis suprema",
        
        // A. axillaris
        "Arteria axillaris",
        "Arteria thoracica superior",
        "Arteria thoracoacromialis",
        "Ramus acromialis",
        "Ramus clavicularis",
        "Ramus deltoideus",
        "Ramus pectoralis",
        "Arteria thoracica lateralis",
        "Arteria subscapularis",
        "Arteria thoracodorsalis",
        "Arteria circumflexa scapulae",
        "Arteria circumflexa humeri anterior",
        "Arteria circumflexa humeri posterior",
        
        // A. brachialis
        "Arteria brachialis",
        "Arteria profunda brachii",
        "Arteria collateralis radialis",
        "Arteria collateralis media",
        "Arteria collateralis ulnaris superior",
        "Arteria collateralis ulnaris inferior",
        "Arteria nutricia humeri",
        
        // A. radialis
        "Arteria radialis",
        "Arteria recurrens radialis",
        "Ramus carpalis palmaris",
        "Ramus palmaris superficialis",
        "Ramus carpalis dorsalis",
        "Arteria metacarpalis dorsalis prima",
        "Arteria princeps pollicis",
        "Arteria radialis indicis",
        "Arcus palmaris profundus",
        
        // A. ulnaris
        "Arteria ulnaris",
        "Arteria recurrens ulnaris anterior",
        "Arteria recurrens ulnaris posterior",
        "Arteria interossea communis",
        "Arteria interossea anterior",
        "Arteria interossea posterior",
        "Arteria interossea recurrens",
        "Ramus carpalis dorsalis",
        "Ramus carpalis palmaris",
        "Ramus palmaris profundus",
        "Arcus palmaris superficialis",
        "Arteriae digitales palmares communes",
        "Arteriae digitales palmares propriae",
        
        // Arterielle Bögen
        "Rete carpale dorsale",
        "Rete carpale palmare",
        "Arteriae metacarpales dorsales",
        "Arteriae metacarpales palmares"
      ]
    },
    
    // ==========================================
    // ARTERIEN DER UNTEREN EXTREMITÄT
    // ==========================================
    arterienUnten: {
      name: "Arterien der unteren Extremität",
      entries: [
        // A. iliaca
        "Arteria iliaca communis",
        "Arteria iliaca interna",
        "Arteria iliaca externa",
        
        // A. iliaca interna Äste
        "Truncus anterior a. iliacae internae",
        "Arteria umbilicalis",
        "Arteria vesicalis superior",
        "Arteria obturatoria",
        "Arteria vesicalis inferior",
        "Arteria rectalis media",
        "Arteria uterina",
        "Arteria vaginalis",
        "Arteria pudenda interna",
        "Arteria glutea inferior",
        "Truncus posterior a. iliacae internae",
        "Arteria iliolumbalis",
        "Arteriae sacrales laterales",
        "Arteria glutea superior",
        
        // A. iliaca externa Äste
        "Arteria epigastrica inferior",
        "Arteria cremasterica",
        "Arteria ligamenti teretis uteri",
        "Arteria circumflexa ilium profunda",
        
        // A. femoralis
        "Arteria femoralis",
        "Arteria epigastrica superficialis",
        "Arteria circumflexa ilium superficialis",
        "Arteriae pudendae externae",
        "Arteria profunda femoris",
        "Arteria circumflexa femoris medialis",
        "Arteria circumflexa femoris lateralis",
        "Ramus ascendens",
        "Ramus descendens",
        "Ramus transversus",
        "Arteriae perforantes",
        "Arteria descendens genus",
        "Ramus saphenus",
        "Ramus articularis",
        
        // A. poplitea
        "Arteria poplitea",
        "Arteria superior lateralis genus",
        "Arteria superior medialis genus",
        "Arteria media genus",
        "Arteriae surales",
        "Arteria inferior lateralis genus",
        "Arteria inferior medialis genus",
        "Rete articulare genus",
        
        // A. tibialis anterior
        "Arteria tibialis anterior",
        "Arteria recurrens tibialis posterior",
        "Arteria recurrens tibialis anterior",
        "Arteria malleolaris anterior lateralis",
        "Arteria malleolaris anterior medialis",
        "Rete malleolare laterale",
        "Rete malleolare mediale",
        "Arteria dorsalis pedis",
        "Arteria tarsalis lateralis",
        "Arteriae tarsales mediales",
        "Arteria arcuata",
        "Arteriae metatarsales dorsales",
        "Arteriae digitales dorsales pedis",
        "Arteria plantaris profunda",
        
        // A. tibialis posterior
        "Arteria tibialis posterior",
        "Ramus circumflexus fibularis",
        "Arteria nutricia tibiae",
        "Arteria fibularis (peronea)",
        "Ramus perforans",
        "Ramus communicans",
        "Arteria malleolaris posterior lateralis",
        "Rami calcanei",
        "Arteria plantaris medialis",
        "Arteria plantaris lateralis",
        "Arcus plantaris profundus",
        "Arteriae metatarsales plantares",
        "Arteriae digitales plantares communes",
        "Arteriae digitales plantares propriae"
      ]
    },
    
    // ==========================================
    // KOPF- UND HALSARTERIEN
    // ==========================================
    arterienKopfHals: {
      name: "Kopf- und Halsarterien",
      entries: [
        // A. carotis communis
        "Arteria carotis communis",
        "Bifurcatio carotidis",
        "Sinus caroticus",
        "Glomus caroticum",
        
        // A. carotis externa
        "Arteria carotis externa",
        "Arteria thyroidea superior",
        "Ramus infrahyoideus",
        "Ramus sternocleidomastoideus",
        "Ramus cricothyroideus",
        "Arteria laryngea superior",
        "Arteria lingualis",
        "Rami dorsales linguae",
        "Arteria sublingualis",
        "Arteria profunda linguae",
        "Arteria facialis",
        "Arteria palatina ascendens",
        "Ramus tonsillaris",
        "Arteria submentalis",
        "Arteria labialis inferior",
        "Arteria labialis superior",
        "Ramus lateralis nasi",
        "Arteria angularis",
        "Arteria occipitalis",
        "Rami sternocleidomastoidei",
        "Ramus mastoideus",
        "Ramus auricularis",
        "Rami occipitales",
        "Ramus descendens",
        "Arteria auricularis posterior",
        "Arteria stylomastoidea",
        "Ramus auricularis",
        "Ramus occipitalis",
        "Arteria pharyngea ascendens",
        "Arteria tympanica inferior",
        "Rami pharyngeales",
        "Arteria meningea posterior",
        "Arteria temporalis superficialis",
        "Ramus parotideus",
        "Arteria transversa faciei",
        "Rami auriculares anteriores",
        "Arteria zygomaticoorbitalis",
        "Arteria temporalis media",
        "Ramus frontalis",
        "Ramus parietalis",
        "Arteria maxillaris",
        "Arteria auricularis profunda",
        "Arteria tympanica anterior",
        "Arteria meningea media",
        "Ramus accessorius",
        "Arteria alveolaris inferior",
        "Ramus mylohyoideus",
        "Arteria mentalis",
        "Arteriae massetericae",
        "Arteriae temporales profundae",
        "Arteria pterygoidea",
        "Arteria buccalis",
        "Arteria alveolaris superior posterior",
        "Arteria infraorbitalis",
        "Arteriae alveolares superiores anteriores",
        "Arteria palatina descendens",
        "Arteria palatina major",
        "Arteriae palatinae minores",
        "Arteria canalis pterygoidei",
        "Arteria sphenopalatina",
        "Arteriae nasales posteriores laterales",
        "Rami septales posteriores",
        
        // A. carotis interna (bereits im ZNS)
        "Arteria carotis interna - Pars cervicalis"
      ]
    },
    
    // ==========================================
    // VENENSYSTEM
    // ==========================================
    venen: {
      name: "Venöses System",
      entries: [
        // Obere Hohlvene
        "Vena cava superior",
        "Vena brachiocephalica dextra",
        "Vena brachiocephalica sinistra",
        "Vena jugularis interna",
        "Bulbus superior venae jugularis",
        "Bulbus inferior venae jugularis",
        "Vena facialis",
        "Vena retromandibularis",
        "Vena lingualis",
        "Vena thyroidea superior",
        "Vena thyroidea media",
        "Vena pharyngealis",
        "Vena jugularis externa",
        "Vena jugularis anterior",
        "Arcus venosus jugularis",
        "Vena subclavia",
        "Vena vertebralis",
        "Vena thoracica interna",
        
        // Armvenen
        "Vena axillaris",
        "Vena brachialis",
        "Venae brachiales",
        "Vena basilica",
        "Vena cephalica",
        "Vena mediana cubiti",
        "Vena mediana antebrachii",
        "Venae radiales",
        "Venae ulnares",
        "Arcus venosus palmaris superficialis",
        "Arcus venosus palmaris profundus",
        "Venae digitales palmares",
        "Rete venosum dorsale manus",
        "Venae metacarpales dorsales",
        
        // Untere Hohlvene
        "Vena cava inferior",
        "Venae hepaticae",
        "Vena hepatica dextra",
        "Vena hepatica media",
        "Vena hepatica sinistra",
        "Venae phrenicae inferiores",
        "Venae suprarenales",
        "Venae renales",
        "Vena testicularis/ovarica dextra",
        "Vena testicularis/ovarica sinistra",
        "Venae lumbales",
        "Vena lumbalis ascendens",
        
        // Pfortadersystem
        "Vena portae hepatis",
        "Vena mesenterica superior",
        "Vena mesenterica inferior",
        "Vena lienalis (splenica)",
        "Vena gastroomentalis dextra",
        "Vena gastroomentalis sinistra",
        "Venae gastricae breves",
        "Vena gastrica sinistra",
        "Vena gastrica dextra",
        "Vena pancreaticoduodenalis",
        "Venae jejunales",
        "Venae ileales",
        "Vena ileocolica",
        "Vena colica dextra",
        "Vena colica media",
        "Vena colica sinistra",
        "Venae sigmoideae",
        "Vena rectalis superior",
        
        // Beckenvenen
        "Vena iliaca communis",
        "Vena iliaca interna",
        "Venae gluteae superiores",
        "Venae gluteae inferiores",
        "Venae obturatoriae",
        "Plexus venosus sacralis",
        "Plexus venosus vesicalis",
        "Plexus venosus prostaticus",
        "Plexus venosus uterinus",
        "Plexus venosus vaginalis",
        "Plexus venosus rectalis",
        "Venae rectales mediae",
        "Venae pudendae internae",
        "Vena iliaca externa",
        
        // Beinvenen
        "Vena femoralis",
        "Vena profunda femoris",
        "Vena saphena magna",
        "Vena saphena accessoria",
        "Venae pudendae externae",
        "Vena circumflexa ilium superficialis",
        "Vena epigastrica superficialis",
        "Vena poplitea",
        "Vena saphena parva",
        "Venae tibiales anteriores",
        "Venae tibiales posteriores",
        "Venae fibulares",
        "Arcus venosus dorsalis pedis",
        "Rete venosum plantare",
        "Venae metatarsales dorsales pedis",
        "Venae digitales dorsales pedis",
        
        // Azygos-System
        "Vena azygos",
        "Vena hemiazygos",
        "Vena hemiazygos accessoria",
        "Venae intercostales posteriores",
        "Venae oesophageales",
        "Venae bronchiales",
        "Venae pericardiacae",
        "Venae mediastinales"
      ]
    },
    
    // ==========================================
    // LYMPHSYSTEM
    // ==========================================
    lymphsystem: {
      name: "Lymphsystem",
      entries: [
        // Lymphbahnen
        "Ductus thoracicus",
        "Cisterna chyli",
        "Trunci lumbales",
        "Truncus intestinalis",
        "Ductus lymphaticus dexter",
        "Truncus jugularis",
        "Truncus subclavius",
        "Truncus bronchomediastinalis",
        
        // Kopf-Hals Lymphknoten
        "Nodi lymphoidei occipitales",
        "Nodi lymphoidei mastoidei",
        "Nodi lymphoidei parotidei",
        "Nodi lymphoidei submandibulares",
        "Nodi lymphoidei submentales",
        "Nodi lymphoidei cervicales anteriores",
        "Nodi lymphoidei cervicales laterales superficiales",
        "Nodi lymphoidei cervicales laterales profundi",
        "Nodi lymphoidei jugulares interni",
        "Nodus jugulodigastricus",
        "Nodus juguloomohyoideus",
        "Nodi lymphoidei supraclaviculares",
        
        // Thorakale Lymphknoten
        "Nodi lymphoidei parasternales",
        "Nodi lymphoidei intercostales",
        "Nodi lymphoidei diaphragmatici",
        "Nodi lymphoidei mediastinales anteriores",
        "Nodi lymphoidei mediastinales posteriores",
        "Nodi lymphoidei tracheobronchiales",
        "Nodi lymphoidei bronchopulmonales",
        "Nodi lymphoidei pulmonales",
        
        // Abdominale Lymphknoten
        "Nodi lymphoidei coeliaci",
        "Nodi lymphoidei gastrici",
        "Nodi lymphoidei hepatici",
        "Nodi lymphoidei pancreatici",
        "Nodi lymphoidei lienales",
        "Nodi lymphoidei mesenterici superiores",
        "Nodi lymphoidei mesenterici inferiores",
        "Nodi lymphoidei lumbales",
        "Nodi lymphoidei aortici laterales",
        "Nodi lymphoidei preaortici",
        "Nodi lymphoidei retroaortici",
        
        // Beckenlymphknoten
        "Nodi lymphoidei iliaci communes",
        "Nodi lymphoidei iliaci externi",
        "Nodi lymphoidei iliaci interni",
        "Nodi lymphoidei sacrales",
        "Nodi lymphoidei inguinales superficiales",
        "Nodi lymphoidei inguinales profundi",
        
        // Arm-Lymphknoten
        "Nodi lymphoidei axillares",
        "Nodi lymphoidei pectorales",
        "Nodi lymphoidei subscapulares",
        "Nodi lymphoidei laterales",
        "Nodi lymphoidei centrales",
        "Nodi lymphoidei apicales",
        "Nodi lymphoidei cubitales",
        
        // Bein-Lymphknoten
        "Nodi lymphoidei poplitei"
      ]
    },
    
    // ==========================================
    // MILZ
    // ==========================================
    milz: {
      name: "Milz (Lien/Splen)",
      entries: [
        "Lien (Splen)",
        "Facies diaphragmatica",
        "Facies visceralis",
        "Facies gastrica",
        "Facies renalis",
        "Facies colica",
        "Margo superior",
        "Margo inferior",
        "Extremitas anterior",
        "Extremitas posterior",
        "Hilum lienale",
        "Capsula lienalis",
        "Trabeculae lienales",
        "Pulpa alba",
        "Noduli lymphoidei lienales",
        "Vagina periarterialis lymphatica",
        "Pulpa rubra",
        "Sinus lienales",
        "Chordae lienales",
        "Arteria lienalis",
        "Arteriae lienales breves",
        "Arteriae centrales",
        "Arteriae penicillares",
        "Vena lienalis"
      ]
    }
  }
};

// Hilfsfunktion zum Extrahieren aller Einträge
export const getAllHerzKreislaufEntries = (): string[] => {
  const allEntries: string[] = [];
  Object.values(HERZ_KREISLAUF_DATABASE.subcategories).forEach(subcategory => {
    allEntries.push(...subcategory.entries);
  });
  return allEntries;
};

// Aktualisiere die Gesamtzahl
HERZ_KREISLAUF_DATABASE.totalEntries = getAllHerzKreislaufEntries().length;

export default HERZ_KREISLAUF_DATABASE;

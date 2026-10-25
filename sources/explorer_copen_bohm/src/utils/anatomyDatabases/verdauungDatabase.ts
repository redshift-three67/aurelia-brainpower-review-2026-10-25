// Verdauungssystem - Detaillierte anatomische Datenbank
// Basierend auf Terminologia Anatomica (TA2) und FMA Ontology
// Höchste Detaillierung für Gastrointestinaltrakt und Nebenorgane

const VERDAUUNG_DATABASE = {
  name: "Verdauungssystem",
  category: "Gastroenterologie",
  totalEntries: 0, // Wird dynamisch berechnet
  subcategories: {
    // MUNDHÖHLE UND RACHEN
    mundhoehle: {
      name: "Mundhöhle (Cavitas oris)",
      entries: [
        // Lippen
        "Oberlippe (Labium superius)",
        "Unterlippe (Labium inferius)",
        "Lippenbändchen (Frenulum labii)",
        "Philtrum",
        "Lippenrot (Vermillion)",
        // Wangen
        "Wange (Bucca)",
        "Wangenfettpolster (Bichat-Fettpfropf)",
        "Wangenschleimhaut",
        // Gaumen
        "Harter Gaumen (Palatum durum)",
        "Weicher Gaumen (Palatum molle)",
        "Gaumensegel (Velum palatinum)",
        "Gaumenzäpfchen (Uvula)",
        "Gaumenbogen anterior (Arcus palatoglossus)",
        "Gaumenbogen posterior (Arcus palatopharyngeus)",
        "Gaumenmandel (Tonsilla palatina)",
        "Rachenmandel (Tonsilla pharyngealis)",
        "Zungenmandel (Tonsilla lingualis)",
        "Tubenmandel (Tonsilla tubaria)",
        "Waldeyer-Rachenring",
        // Mundboden
        "Mundboden (Diaphragma oris)",
        "Musculus mylohyoideus",
        "Musculus geniohyoideus",
        "Musculus digastricus",
        "Sublingualgegend",
        // Speicheldrüsen
        "Ohrspeicheldrüse (Glandula parotis)",
        "Stensen-Gang (Ductus parotideus)",
        "Unterkieferspeicheldrüse (Glandula submandibularis)",
        "Wharton-Gang (Ductus submandibularis)",
        "Unterzungenspeicheldrüse (Glandula sublingualis)",
        "Rivinus-Gänge (Ductus sublinguales minores)",
        "Bartholin-Gang (Ductus sublingualis major)",
        "Kleine Speicheldrüsen (Glandulae salivariae minores)",
        "Lippendrüsen",
        "Wangendrüsen",
        "Gaumendrüsen",
        "Zungendrüsen",
      ]
    },
    zunge: {
      name: "Zunge (Lingua)",
      entries: [
        // Zungenabschnitte
        "Zungenspitze (Apex linguae)",
        "Zungenkörper (Corpus linguae)",
        "Zungenrücken (Dorsum linguae)",
        "Zungenrand (Margo linguae)",
        "Zungenunterseite",
        "Zungenwurzel (Radix linguae)",
        "Zungengrund",
        // Zungenstruktur
        "Sulcus terminalis",
        "Foramen caecum",
        "Ductus thyreoglossus (Rudiment)",
        "Septum linguae",
        "Aponeurosis linguae",
        // Zungenpapillen
        "Papillae filiformes",
        "Papillae fungiformes",
        "Papillae foliatae",
        "Papillae vallatae",
        "Geschmacksknospen",
        "Von-Ebner-Drüsen",
        // Zungenmuskulatur innere
        "Musculus longitudinalis superior",
        "Musculus longitudinalis inferior",
        "Musculus transversus linguae",
        "Musculus verticalis linguae",
        // Zungenmuskulatur äußere
        "Musculus genioglossus",
        "Musculus hyoglossus",
        "Musculus styloglossus",
        "Musculus palatoglossus",
        // Zungenbändchen
        "Zungenbändchen (Frenulum linguae)",
        "Plica fimbriata",
        "Plica sublingualis",
        "Caruncula sublingualis",
      ]
    },
    zaehne: {
      name: "Zähne (Dentes)",
      entries: [
        // Zahntypen
        "Schneidezähne (Dentes incisivi)",
        "Eckzähne (Dentes canini)",
        "Prämolaren (Dentes praemolares)",
        "Molaren (Dentes molares)",
        "Weisheitszähne (Dentes serotini)",
        // Zahnstruktur
        "Zahnschmelz (Enamelum)",
        "Zahnbein (Dentinum)",
        "Zahnmark (Pulpa dentis)",
        "Pulpakammer",
        "Wurzelkanal",
        "Zahnwurzel (Radix dentis)",
        "Zahnkrone (Corona dentis)",
        "Zahnhals (Cervix dentis)",
        "Wurzelspitze (Apex radicis dentis)",
        "Foramen apicis dentis",
        "Zement (Cementum)",
        // Zahnhalteapparat
        "Zahnfleisch (Gingiva)",
        "Desmodont (Ligamentum periodontale)",
        "Sharpey-Fasern",
        "Alveolarknochen",
        "Alveole (Alveolus dentalis)",
        "Zahnfach",
        "Interdentalraum",
        "Interdentalpapille",
        // Milchzähne
        "Milchschneidezähne",
        "Milcheckzähne",
        "Milchmolaren",
      ]
    },
    pharynx: {
      name: "Rachen (Pharynx)",
      entries: [
        // Rachenabschnitte
        "Nasopharynx (Pars nasalis pharyngis)",
        "Oropharynx (Pars oralis pharyngis)",
        "Hypopharynx (Pars laryngea pharyngis)",
        // Nasopharynx-Strukturen
        "Torus tubarius",
        "Recessus pharyngeus (Rosenmueller)",
        "Tuba auditiva Öffnung (Ostium pharyngeum)",
        "Passavant-Wulst",
        // Oropharynx-Strukturen
        "Isthmus faucium",
        "Fossa tonsillaris",
        "Vallecula epiglottica",
        "Plica glossoepiglottica mediana",
        "Plica glossoepiglottica lateralis",
        "Zungengrund-Bereich",
        // Hypopharynx-Strukturen
        "Sinus piriformis",
        "Plica aryepiglottica",
        "Recessus piriformis",
        "Postcricoidregion",
        "Pharynxhinterwand",
        // Pharynxmuskulatur
        "Musculus constrictor pharyngis superior",
        "Musculus constrictor pharyngis medius",
        "Musculus constrictor pharyngis inferior",
        "Musculus stylopharyngeus",
        "Musculus palatopharyngeus",
        "Musculus salpingopharyngeus",
        // Pharynxfaszien
        "Fascia pharyngobasilaris",
        "Fascia buccopharyngealis",
        "Raphe pharyngis",
        "Retropharyngealraum",
        "Parapharyngealraum",
      ]
    },
    // SPEISERÖHRE
    oesophagus: {
      name: "Speiseröhre (Oesophagus)",
      entries: [
        // Abschnitte
        "Pars cervicalis oesophagi",
        "Pars thoracica oesophagi",
        "Pars abdominalis oesophagi",
        // Engstellen
        "Obere Ösophagusenge (Killiansches Dreieck)",
        "Aortenenge",
        "Zwerchfellenge (Hiatus oesophageus)",
        "Untere Ösophagusenge (Kardia)",
        // Wandschichten
        "Tunica mucosa oesophagi",
        "Lamina propria oesophagi",
        "Lamina muscularis mucosae oesophagi",
        "Tela submucosa oesophagi",
        "Tunica muscularis oesophagi",
        "Stratum circulare oesophagi",
        "Stratum longitudinale oesophagi",
        "Tunica adventitia oesophagi",
        // Sphinkter
        "Oberer Ösophagussphinkter (M. cricopharyngeus)",
        "Unterer Ösophagussphinkter (funktionell)",
        "His-Winkel (Ösophago-Magen-Übergang)",
        // Drüsen
        "Glandulae oesophageae",
        "Glandulae cardiacae (Kardia-Drüsen)",
        // Innervation
        "Plexus oesophageus",
        "Plexus myentericus (Auerbach)",
        "Plexus submucosus (Meissner)",
        "Vagusäste zum Ösophagus",
      ]
    },
    // MAGEN
    magen: {
      name: "Magen (Gaster)",
      entries: [
        // Magenabschnitte
        "Kardia (Mageneingang)",
        "Fundus gastricus",
        "Corpus gastricum",
        "Antrum pyloricum",
        "Pylorus (Pförtner)",
        "Canalis pyloricus",
        // Magenwände
        "Paries anterior (Vorderwand)",
        "Paries posterior (Hinterwand)",
        "Curvatura major",
        "Curvatura minor",
        "Incisura angularis",
        "Incisura cardialis",
        // Wandschichten
        "Tunica serosa",
        "Tela subserosa",
        "Tunica muscularis gastrica",
        "Stratum longitudinale",
        "Stratum circulare",
        "Fibrae obliquae",
        "Tela submucosa gastrica",
        "Tunica mucosa gastrica",
        "Lamina muscularis mucosae",
        "Plicae gastricae",
        // Magendrüsen
        "Areae gastricae",
        "Foveolae gastricae (Magengrübchen)",
        "Glandulae gastricae propriae",
        "Hauptzellen (Zymogene Zellen)",
        "Belegzellen (Parietalzellen)",
        "Nebenzellen (Schleimzellen)",
        "Enterochromaffin-ähnliche Zellen (ECL)",
        "G-Zellen (Gastrin-produzierende)",
        "D-Zellen (Somatostatin-produzierende)",
        "Glandulae cardiacae",
        "Glandulae pyloricae",
        // Sphinkter
        "Musculus sphincter pylori",
        "Pylorusklappe (Valvula pylori)",
        // Innervation
        "Plexus gastricus",
        "Nervus vagus anterior",
        "Nervus vagus posterior",
        "Truncus vagalis anterior",
        "Truncus vagalis posterior",
        "Latarjet-Nerv (Ramus gastricus anterior)",
        "Krähenfuß (Pes anserinus)",
        // Blutversorgung
        "Arteria gastrica sinistra",
        "Arteria gastrica dextra",
        "Arteria gastroomentalis sinistra",
        "Arteria gastroomentalis dextra",
        "Arteriae gastricae breves",
        "Vena gastrica sinistra (Vena coronaria ventriculi)",
        "Vena gastrica dextra",
        // Lymphknoten
        "Nodi lymphatici gastrici",
        "Nodi lymphatici pylorici",
        "Nodi lymphatici splenici",
      ]
    },
    // DÜNNDARM
    duenndarm: {
      name: "Dünndarm (Intestinum tenue)",
      entries: [
        // Duodenum
        "Duodenum (Zwölffingerdarm)",
        "Pars superior duodeni (Bulbus duodeni)",
        "Pars descendens duodeni",
        "Pars horizontalis duodeni",
        "Pars ascendens duodeni",
        "Flexura duodeni superior",
        "Flexura duodeni inferior",
        "Flexura duodenojejunalis",
        "Musculus suspensorius duodeni (Treitz)",
        "Papilla duodeni major (Vateri)",
        "Papilla duodeni minor (Santorini)",
        "Ampulla hepatopancreatica",
        "Musculus sphincter ampullae (Oddi)",
        "Plica longitudinalis duodeni",
        "Brunner-Drüsen (Glandulae duodenales)",
        // Jejunum
        "Jejunum (Leerdarm)",
        "Radix mesenterii",
        "Plicae circulares (Kerckring-Falten)",
        "Villi intestinales (Darmzotten)",
        "Microvilli",
        "Cryptae intestinales (Lieberkühn-Krypten)",
        // Ileum
        "Ileum (Krummdarm)",
        "Terminales Ileum",
        "Ileum-Zäkalklappe (Valva ileocaecalis/Bauhin)",
        "Frenulum valvae ileocaecalis",
        "Peyer-Plaques (Folliculi lymphatici aggregati)",
        "Solitäre Lymphfollikel",
        // Wandschichten
        "Tunica serosa intestini tenuis",
        "Tunica muscularis intestini tenuis",
        "Stratum longitudinale intestini",
        "Stratum circulare intestini",
        "Tela submucosa intestini",
        "Tunica mucosa intestini",
        // Zelltypen
        "Enterozyten",
        "Becherzellen",
        "Paneth-Zellen",
        "Enteroendokrine Zellen",
        "M-Zellen (Microfold cells)",
        "Stammzellen der Krypten",
        // Gefäße und Nerven
        "Arteriae jejunales",
        "Arteriae ileales",
        "Arcaden-System",
        "Vasa recta",
        "Plexus myentericus (Auerbach)",
        "Plexus submucosus (Meissner)",
      ]
    },
    // DICKDARM
    dickdarm: {
      name: "Dickdarm (Intestinum crassum)",
      entries: [
        // Caecum
        "Caecum (Blinddarm)",
        "Appendix vermiformis (Wurmfortsatz)",
        "Ostium appendicis vermiformis",
        "Mesenteriolum (Mesoappendix)",
        "McBurney-Punkt",
        "Lanz-Punkt",
        "Gerlach-Klappe",
        // Colon ascendens
        "Colon ascendens",
        "Flexura coli dextra (hepatica)",
        "Sulcus paracolicus dexter",
        // Colon transversum
        "Colon transversum",
        "Mesocolon transversum",
        "Flexura coli sinistra (lienalis)",
        "Ligamentum phrenicocolicum",
        // Colon descendens
        "Colon descendens",
        "Sulcus paracolicus sinister",
        // Colon sigmoideum
        "Colon sigmoideum (S-förmiger Grimmdarm)",
        "Mesocolon sigmoideum",
        "Recessus intersigmoideus",
        // Kolonwandstrukturen
        "Taeniae coli",
        "Taenia libera",
        "Taenia mesocolica",
        "Taenia omentalis",
        "Haustra coli",
        "Plicae semilunares coli",
        "Appendices epiploicae (Omentales)",
        // Wandschichten
        "Tunica serosa coli",
        "Tunica muscularis coli",
        "Stratum longitudinale (Taenien)",
        "Stratum circulare coli",
        "Tela submucosa coli",
        "Tunica mucosa coli",
        "Cryptae coli (Lieberkühn)",
        "Becherzellen des Kolons",
        // Gefäße
        "Arteria ileocolica",
        "Arteria colica dextra",
        "Arteria colica media",
        "Arteria colica sinistra",
        "Arteriae sigmoideae",
        "Riolan-Arkade",
        "Drummond-Arkade",
        "Sudeck-Punkt",
        "Griffith-Punkt",
      ]
    },
    rektum: {
      name: "Rektum und Analkanal",
      entries: [
        // Rektum
        "Rektum (Mastdarm)",
        "Ampulla recti",
        "Flexura sacralis recti",
        "Flexura perinealis recti",
        "Plicae transversales recti (Kohlrausch)",
        "Plica transversalis media (Houston-Falte)",
        "Columna anales (Morgagni-Säulen)",
        "Sinus anales",
        "Valvulae anales (Krypten)",
        "Linea pectinata (Linea dentata)",
        "Linea anocutanea",
        "Zona hemorrhoidalis interna",
        // Analkanal
        "Canalis analis",
        "Pecten analis (Übergangszone)",
        "Zona cutanea ani",
        "Anus",
        // Sphinktersystem
        "Musculus sphincter ani internus",
        "Musculus sphincter ani externus",
        "Pars subcutanea m. sphincteri ani externi",
        "Pars superficialis m. sphincteri ani externi",
        "Pars profunda m. sphincteri ani externi",
        "Musculus puborectalis",
        "Musculus levator ani",
        "Musculus coccygeus",
        "Anorektaler Winkel",
        // Gefäßpolster
        "Corpus cavernosum recti",
        "Arteria rectalis superior",
        "Arteria rectalis media",
        "Arteria rectalis inferior",
        "Plexus venosus rectalis (Hämorrhoidalplexus)",
        // Spatien
        "Fossa ischiorectalis (ischioanalis)",
        "Spatium perianale",
        "Spatium supralevatoricum",
        "Spatium retroanale",
        "Spatium postanal profundum",
      ]
    },
    // LEBER
    leber: {
      name: "Leber (Hepar)",
      entries: [
        // Lappen und Flächen
        "Lobus hepatis dexter",
        "Lobus hepatis sinister",
        "Lobus caudatus (Spigel-Lappen)",
        "Processus caudatus",
        "Processus papillaris",
        "Lobus quadratus",
        "Facies diaphragmatica",
        "Facies visceralis",
        "Margo inferior hepatis",
        "Area nuda (Bare area)",
        "Incisura ligamenti teretis",
        // Leberpforte
        "Porta hepatis (Leberpforte)",
        "Arteria hepatica propria",
        "Arteria hepatica dextra",
        "Arteria hepatica sinistra",
        "Vena portae hepatis",
        "Ramus dexter venae portae",
        "Ramus sinister venae portae",
        "Ductus hepaticus communis",
        "Ductus hepaticus dexter",
        "Ductus hepaticus sinister",
        // Bänder
        "Ligamentum falciforme hepatis",
        "Ligamentum teres hepatis",
        "Ligamentum coronarium",
        "Ligamentum triangulare dextrum",
        "Ligamentum triangulare sinistrum",
        "Ligamentum venosum (Ductus venosus Arantii)",
        "Ligamentum hepatoduodenale",
        "Ligamentum hepatogastricum",
        // Lebersegmente (Couinaud)
        "Segment I (Lobus caudatus)",
        "Segment II (lateraler linker Sektor posterior)",
        "Segment III (lateraler linker Sektor anterior)",
        "Segment IV (medialer linker Sektor)",
        "Segment IVa",
        "Segment IVb",
        "Segment V (anteriorer rechter Sektor inferior)",
        "Segment VI (posteriorer rechter Sektor inferior)",
        "Segment VII (posteriorer rechter Sektor superior)",
        "Segment VIII (anteriorer rechter Sektor superior)",
        // Feinstruktur
        "Leberläppchen (Lobulus hepatis)",
        "Zentralvene (Vena centralis)",
        "Glisson-Trias (Periportalfeld)",
        "Sinusoide (Lebersinusoide)",
        "Kupffer-Zellen",
        "Ito-Zellen (Sternzellen)",
        "Disse-Raum",
        "Gallenkanälchen (Canaliculi biliferi)",
        "Hering-Kanäle",
        // Lebervenen
        "Vena hepatica dextra",
        "Vena hepatica media",
        "Vena hepatica sinistra",
        "Venae hepaticae accessoriae",
      ]
    },
    gallenblase: {
      name: "Gallenblase und Gallenwege",
      entries: [
        // Gallenblase
        "Vesica biliaris (Gallenblase)",
        "Fundus vesicae biliaris",
        "Corpus vesicae biliaris",
        "Collum vesicae biliaris",
        "Infundibulum vesicae biliaris (Hartmann-Tasche)",
        "Ductus cysticus",
        "Plica spiralis (Heister-Klappe)",
        "Tunica mucosa vesicae biliaris",
        "Tunica muscularis vesicae biliaris",
        "Tunica serosa vesicae biliaris",
        "Rokitansky-Aschoff-Sinus",
        // Gallenwege
        "Ductus hepaticus dexter",
        "Ductus hepaticus sinister",
        "Ductus hepaticus communis",
        "Ductus choledochus (Gallengang)",
        "Pars supraduodenalis ductus choledochi",
        "Pars retroduodenalis ductus choledochi",
        "Pars pancreatica ductus choledochi",
        "Pars intramuralis ductus choledochi",
        "Ampulla hepatopancreatica (Vater)",
        "Musculus sphincter ampullae hepatopancreaticae (Oddi)",
        "Musculus sphincter ductus choledochi",
        "Musculus sphincter ductus pancreatici",
        // Calot-Dreieck
        "Trigonum cystohepaticum (Calot-Dreieck)",
        "Arteria cystica",
        "Lymphonodus cysticus",
      ]
    },
    pankreas: {
      name: "Bauchspeicheldrüse (Pancreas)",
      entries: [
        // Abschnitte
        "Caput pancreatis (Pankreaskopf)",
        "Processus uncinatus",
        "Incisura pancreatis",
        "Collum pancreatis",
        "Corpus pancreatis (Pankreaskörper)",
        "Cauda pancreatis (Pankreasschwanz)",
        "Facies anterior pancreatis",
        "Facies posterior pancreatis",
        "Facies inferior pancreatis",
        "Margo superior pancreatis",
        "Margo inferior pancreatis",
        "Margo anterior pancreatis",
        "Tuber omentale",
        // Pankreasgänge
        "Ductus pancreaticus (Wirsung)",
        "Ductus pancreaticus accessorius (Santorini)",
        // Exokrines Pankreas
        "Azinuszellen",
        "Zentroazinäre Zellen",
        "Acini pancreatici",
        "Ductuli interlobulares",
        "Ductuli intralobulares",
        // Endokrines Pankreas
        "Langerhans-Inseln",
        "Alpha-Zellen (Glukagon)",
        "Beta-Zellen (Insulin)",
        "Delta-Zellen (Somatostatin)",
        "PP-Zellen (Pankreatisches Polypeptid)",
        "Epsilon-Zellen (Ghrelin)",
        // Gefäße
        "Arteria pancreaticoduodenalis superior anterior",
        "Arteria pancreaticoduodenalis superior posterior",
        "Arteria pancreaticoduodenalis inferior",
        "Arteria pancreatica magna",
        "Arteria pancreatica dorsalis",
        "Arteria pancreatica inferior",
        "Arteria caudae pancreatis",
        "Vena pancreatica",
        "Vena pancreaticoduodenalis",
      ]
    },
    // PERITONEUM
    peritoneum: {
      name: "Bauchfell (Peritoneum)",
      entries: [
        // Peritonealblätter
        "Peritoneum parietale",
        "Peritoneum viscerale",
        "Cavitas peritonealis",
        // Mesenterien
        "Mesenterium (Dünndarmgekröse)",
        "Radix mesenterii",
        "Mesocolon transversum",
        "Mesocolon sigmoideum",
        "Mesoappendix",
        // Omentum
        "Omentum majus",
        "Ligamentum gastrocolicum",
        "Ligamentum gastrosplenicum",
        "Omentum minus",
        "Ligamentum hepatogastricum",
        "Ligamentum hepatoduodenale",
        // Bursa omentalis
        "Bursa omentalis (Omentalbeutel)",
        "Foramen epiploicum (Foramen omentale/Winslow)",
        "Vestibulum bursae omentalis",
        "Recessus superior omentalis",
        "Recessus inferior omentalis",
        "Recessus splenicus",
        // Peritonealligamente
        "Ligamentum falciforme hepatis",
        "Ligamentum coronarium hepatis",
        "Ligamentum teres hepatis",
        "Ligamentum splenorenal",
        "Ligamentum phrenicocolicum",
        "Ligamentum gastrolienale",
        // Peritonealrezessus
        "Recessus duodenalis superior",
        "Recessus duodenalis inferior",
        "Recessus intersigmoideus",
        "Recessus ileocaecalis superior",
        "Recessus ileocaecalis inferior",
        "Recessus retrocaecalis",
        // Peritonealräume
        "Spatium subphrenicum",
        "Spatium hepatorenale (Morrison-Pouch)",
        "Spatium parietocolicum",
        "Fossa paravesicalis",
        "Excavatio rectouterina (Douglas-Raum)",
        "Excavatio rectovesicalis",
        "Excavatio vesicouterina",
        // Retroperitoneum
        "Retroperitonealraum",
        "Fascia renalis (Gerota-Faszie)",
        "Fascia transversalis",
        "Spatium pararenale anterius",
        "Spatium pararenale posterius",
        "Spatium perirenale",
      ]
    },
  }
};

// Alle Einträge abrufen
export const getAllVerdauungEntries = (): string[] => {
  const allEntries: string[] = [];
  Object.values(VERDAUUNG_DATABASE.subcategories).forEach(subcategory => {
    allEntries.push(...subcategory.entries);
  });
  return allEntries;
};

// Gesamtanzahl berechnen
VERDAUUNG_DATABASE.totalEntries = getAllVerdauungEntries().length;

export default VERDAUUNG_DATABASE;

// Solfeggio & Heilfrequenzen Datenbank
// Klassische Solfeggio-Töne, Planetenfrequenzen und spezielle Heilfrequenzen

const SOLFEGGIO_DATABASE = {
  name: "Solfeggio & Heilfrequenzen",
  category: "Frequenztherapie & Klangtherapie",
  totalEntries: 312,
  subcategories: {
    klassischeSolfeggio: {
      name: "Klassische Solfeggio-Frequenzen",
      entries: [
        "Solfeggio 174Hz UT Schmerzreduktion Sicherheit",
        "Solfeggio 285Hz RE Gewebe Regeneration Heilung",
        "Solfeggio 396Hz MI Befreiung Angst Schuld",
        "Solfeggio 417Hz FA Veränderung Erleichterung Trauma",
        "Solfeggio 528Hz SOL DNA-Reparatur Transformation Wunder",
        "Solfeggio 639Hz LA Beziehungen Verbindung Harmonie",
        "Solfeggio 741Hz SI Ausdruck Kreativität Lösungen",
        "Solfeggio 852Hz Intuition Erwachen Drittes Auge",
        "Solfeggio 963Hz Göttliche Verbindung Einheit Krone"
      ]
    },
    erweitertesSolfeggio: {
      name: "Erweitertes Solfeggio-System",
      entries: [
        "Solfeggio 63Hz Erdung Wurzelchakra Basis",
        "Solfeggio 126Hz Sakralchakra Kreativität Sexualität",
        "Solfeggio 189Hz Solarplexus Willenskraft Selbst",
        "Solfeggio 252Hz Herzchakra Liebe Mitgefühl",
        "Solfeggio 315Hz Kehlchakra Kommunikation Ausdruck",
        "Solfeggio 378Hz Stirnchakra Intuition Vision",
        "Solfeggio 441Hz Kronenchakra Spiritualität Einheit",
        "Solfeggio 504Hz Höheres Herz Universelle Liebe",
        "Solfeggio 567Hz Höherer Ausdruck Wahrheit",
        "Solfeggio 630Hz Kosmische Intuition Weisheit",
        "Solfeggio 693Hz Transzendenz Erleuchtung",
        "Solfeggio 756Hz Göttliches Wissen Akasha",
        "Solfeggio 819Hz Multidimensionales Bewusstsein",
        "Solfeggio 882Hz Kosmische Ordnung Harmonie",
        "Solfeggio 945Hz Meisterfrequenz Integration"
      ]
    },
    schumann: {
      name: "Schumann-Resonanzen",
      entries: [
        "Schumann 7.83Hz Erdfrequenz Grundresonanz",
        "Schumann 14.1Hz Zweite Harmonische Alpha",
        "Schumann 20.3Hz Dritte Harmonische Beta",
        "Schumann 26.4Hz Vierte Harmonische Gamma",
        "Schumann 33.8Hz Fünfte Harmonische Höheres Bewusstsein",
        "Schumann 39.0Hz Sechste Harmonische Fokus",
        "Schumann 45.0Hz Siebte Harmonische Klarheit"
      ]
    },
    planetenfrequenzen: {
      name: "Planetenfrequenzen nach Hans Cousto",
      entries: [
        "Planet Sonne 126.22Hz Vitalität Lebenskraft Zentrum",
        "Planet Mond 210.42Hz Emotionen Intuition Zyklen",
        "Planet Erde Tag 194.18Hz Erdung Stabilität",
        "Planet Erde Jahr 136.10Hz OM-Frequenz Kosmische Ordnung",
        "Planet Merkur 141.27Hz Kommunikation Intellekt Lernen",
        "Planet Venus 221.23Hz Liebe Schönheit Harmonie",
        "Planet Mars 144.72Hz Energie Antrieb Willenskraft",
        "Planet Jupiter 183.58Hz Wachstum Expansion Glück",
        "Planet Saturn 147.85Hz Struktur Disziplin Grenzen",
        "Planet Uranus 207.36Hz Innovation Veränderung Freiheit",
        "Planet Neptun 211.44Hz Spiritualität Träume Intuition",
        "Planet Pluto 140.25Hz Transformation Regeneration Tiefe",
        "Planet Erde Platonisches Jahr 172.06Hz Universelle Liebe",
        "Planet Synodischer Mond 227.43Hz Emotionale Zyklen",
        "Planet Siderischer Mond 227.43Hz Innere Zyklen"
      ]
    },
    gehirnwellen: {
      name: "Gehirnwellen-Frequenzen",
      entries: [
        "Brainwave 0.5Hz Delta Tiefschlaf Heilung",
        "Brainwave 1Hz Delta Tiefe Regeneration",
        "Brainwave 2Hz Delta Unbewusstes Träume",
        "Brainwave 3Hz Delta Tiefenentspannung",
        "Brainwave 4Hz Theta Trance Meditation",
        "Brainwave 5Hz Theta Kreativität Intuition",
        "Brainwave 6Hz Theta Gedächtnis Lernen",
        "Brainwave 7Hz Theta Alpha-Grenze Entspannung",
        "Brainwave 8Hz Alpha Entspannte Wachheit",
        "Brainwave 9Hz Alpha Körperbewusstsein",
        "Brainwave 10Hz Alpha Optimale Entspannung",
        "Brainwave 11Hz Alpha Entspannte Konzentration",
        "Brainwave 12Hz Alpha Kreative Visualisierung",
        "Brainwave 13Hz Beta Aufmerksamkeit Wachheit",
        "Brainwave 15Hz Beta Konzentration Fokus",
        "Brainwave 18Hz Beta Aktives Denken",
        "Brainwave 20Hz Beta Problem-Lösung",
        "Brainwave 25Hz Beta Hohe Aufmerksamkeit",
        "Brainwave 30Hz Beta Maximale Konzentration",
        "Brainwave 40Hz Gamma Peak-Bewusstsein",
        "Brainwave 50Hz Gamma Höhere Kognition",
        "Brainwave 60Hz Gamma Transzendenz",
        "Brainwave 80Hz Gamma Mystische Erfahrung",
        "Brainwave 100Hz Gamma Einheitsbewusstsein"
      ]
    },
    organFrequenzen: {
      name: "Organ-Grundfrequenzen",
      entries: [
        "Organ 528Hz Herz Liebe Transformation",
        "Organ 317.83Hz Leber Entgiftung Erneuerung",
        "Organ 319.88Hz Nieren Reinigung Balance",
        "Organ 176.18Hz Magen Verdauung Verarbeitung",
        "Organ 281.26Hz Lunge Atmung Leichtigkeit",
        "Organ 295.80Hz Milz Immunität Kraft",
        "Organ 330.00Hz Darm Aufnahme Loslassen",
        "Organ 464.00Hz Pankreas Süße Balance",
        "Organ 492.80Hz Gallenblase Entscheidung Mut",
        "Organ 586.00Hz Schilddrüse Stoffwechsel Ausdruck",
        "Organ 537.00Hz Nebennieren Energie Stress",
        "Organ 634.00Hz Hypophyse Steuerung Balance",
        "Organ 662.00Hz Hypothalamus Regulation Homöostase",
        "Organ 688.00Hz Zirbeldrüse Licht Melatonin",
        "Organ 622.00Hz Thymus Immunität Jugend"
      ]
    },
    chakraFrequenzen: {
      name: "Chakra-Frequenzen",
      entries: [
        "Chakra 256Hz Wurzelchakra C Muladhara Rot",
        "Chakra 288Hz Sakralchakra D Svadhisthana Orange",
        "Chakra 320Hz Solarplexuschakra E Manipura Gelb",
        "Chakra 341Hz Herzchakra F Anahata Grün",
        "Chakra 384Hz Halschakra G Vishuddha Blau",
        "Chakra 426Hz Stirnchakra A Ajna Indigo",
        "Chakra 480Hz Kronenchakra H Sahasrara Violett",
        "Chakra 194.18Hz Wurzel Erde Erdung",
        "Chakra 210.42Hz Sakral Mond Emotionen",
        "Chakra 126.22Hz Solarplexus Sonne Kraft",
        "Chakra 136.10Hz Herz OM Liebe",
        "Chakra 141.27Hz Hals Merkur Kommunikation",
        "Chakra 221.23Hz Stirn Venus Intuition",
        "Chakra 172.06Hz Krone Saturn Weisheit"
      ]
    },
    dnaFrequenzen: {
      name: "DNA & Zellregeneration",
      entries: [
        "DNA 528Hz Reparatur Transformation Heilung",
        "DNA 432Hz Natürliche Harmonie Kohärenz",
        "DNA 639Hz Verbindung Kommunikation Zellen",
        "DNA 852Hz Aktivierung Höheres Bewusstsein",
        "DNA 963Hz Pineal Aktivierung Licht",
        "Zelle 10000Hz Regeneration Erneuerung",
        "Zelle 2675Hz Mitochondrien ATP",
        "Zelle 2720Hz Zellmembran Permeabilität",
        "Zelle 2850Hz Ribosomen Proteinsynthese",
        "Zelle 3000Hz Zellkern DNA-Aktivierung",
        "Zelle 3176Hz Golgi-Apparat Transport",
        "Zelle 3300Hz Endoplasmatisches Retikulum",
        "Zelle 3500Hz Lysosomen Reinigung",
        "Zelle 4000Hz Stammzellen Aktivierung",
        "Zelle 5000Hz Telomere Verlängerung"
      ]
    },
    heilendeFrequenzen: {
      name: "Spezielle Heilfrequenzen",
      entries: [
        "Healing 40Hz Gamma Healing Bewusstsein",
        "Healing 111Hz Zellregeneration Beta-Endorphine",
        "Healing 174Hz Schmerzlinderung Betäubung",
        "Healing 285Hz Wundheilung Gewebe",
        "Healing 396Hz Trauma-Befreiung Angst",
        "Healing 417Hz Veränderung Loslassen",
        "Healing 432Hz Universelle Harmonie Natur",
        "Healing 444Hz DNA-Reparatur spirituell",
        "Healing 528Hz Wunderfrequenz Transformation",
        "Healing 639Hz Beziehungsheilung Herz",
        "Healing 741Hz Intuition Erwachen",
        "Healing 777Hz Engelfrequenz Schutz",
        "Healing 852Hz Drittes Auge Klarheit",
        "Healing 888Hz Überfluss Manifestation",
        "Healing 963Hz Kronenchakra Erleuchtung",
        "Healing 999Hz Vollendung Meisterschaft"
      ]
    },
    stimmgabelFrequenzen: {
      name: "Therapeutische Stimmgabel-Frequenzen",
      entries: [
        "Stimmgabel 128Hz C Entspannung Nerven",
        "Stimmgabel 136.10Hz OM Meditation Erdung",
        "Stimmgabel 256Hz C1 Wurzel Balance",
        "Stimmgabel 288Hz D Sakral Kreativität",
        "Stimmgabel 320Hz E Solarplexus Kraft",
        "Stimmgabel 341Hz F Herz Liebe",
        "Stimmgabel 384Hz G Hals Ausdruck",
        "Stimmgabel 426Hz A Stirn Vision",
        "Stimmgabel 480Hz H Krone Spiritualität",
        "Stimmgabel 512Hz C2 Nerven Osteo",
        "Stimmgabel 4096Hz C8 Engel Kristall"
      ]
    },
    wasserkristalle: {
      name: "Wasserkristall-Frequenzen (Emoto)",
      entries: [
        "Wasser 528Hz Liebe Dankbarkeit Schönheit",
        "Wasser 432Hz Natürliche Harmonie Struktur",
        "Wasser 639Hz Verbindung Kohärenz",
        "Wasser 174Hz Basis Stabilität",
        "Wasser 285Hz Regeneration Heilung",
        "Wasser 396Hz Reinigung Klärung",
        "Wasser 417Hz Transformation Veränderung",
        "Wasser 741Hz Ausdruck Kreativität",
        "Wasser 852Hz Intuition Klarheit",
        "Wasser 963Hz Göttlichkeit Licht"
      ]
    },
    kosmischeFrequenzen: {
      name: "Kosmische Frequenzen",
      entries: [
        "Kosmisch 33Hz Christusbewusstsein Meister",
        "Kosmisch 111Hz Engelfrequenz Führung",
        "Kosmisch 222Hz Erzengel Synchronizität",
        "Kosmisch 333Hz Aufgestiegene Meister",
        "Kosmisch 444Hz Engel Schutz Stabilität",
        "Kosmisch 555Hz Veränderung Transformation",
        "Kosmisch 666Hz Balance Erdung Material",
        "Kosmisch 777Hz Spirituelle Vollkommenheit",
        "Kosmisch 888Hz Unendlichkeit Überfluss",
        "Kosmisch 999Hz Vollendung Abschluss",
        "Kosmisch 1111Hz Portal Erwachen",
        "Kosmisch 1212Hz Aufstieg Licht",
        "Kosmisch 1234Hz Sequenz Manifestation",
        "Kosmisch 432Hz Kosmos Harmonie Ursprung",
        "Kosmisch 144Hz Lichtgitter Kristall"
      ]
    },
    tibetischeKlangschalen: {
      name: "Tibetische Klangschalen",
      entries: [
        "Tibet 110Hz Tiefenentspannung Meditation",
        "Tibet 136Hz OM Grundton Erdung",
        "Tibet 172Hz Herzöffnung Mitgefühl",
        "Tibet 194Hz Erdverbindung Wurzel",
        "Tibet 210Hz Emotionale Reinigung",
        "Tibet 256Hz Nervenberuhigung Balance",
        "Tibet 288Hz Kreativität Sakral",
        "Tibet 320Hz Willenskraft Solarplexus",
        "Tibet 341Hz Herzöffnung Liebe",
        "Tibet 384Hz Ausdruck Kommunikation",
        "Tibet 426Hz Intuition Vision",
        "Tibet 480Hz Spiritualität Krone",
        "Tibet 512Hz Klarheit Reinheit"
      ]
    },
    binauralBeats: {
      name: "Binaural Beats",
      entries: [
        "Binaural 1Hz Delta Tiefschlaf Heilung",
        "Binaural 2Hz Delta Regeneration Unbewusst",
        "Binaural 4Hz Theta Trance REM",
        "Binaural 6Hz Theta Kreativität Intuition",
        "Binaural 8Hz Alpha-Theta Entspannung",
        "Binaural 10Hz Alpha Entspannte Wachheit",
        "Binaural 12Hz Alpha Konzentration leicht",
        "Binaural 14Hz SMR Fokus Ruhe",
        "Binaural 18Hz Beta Wachheit Energie",
        "Binaural 20Hz Beta Konzentration stark",
        "Binaural 25Hz Beta Problem-Lösung",
        "Binaural 40Hz Gamma Peak Performance"
      ]
    },
    isochroneTöne: {
      name: "Isochrone Töne",
      entries: [
        "Isochron 0.5Hz Epsilon Ultra-Tiefschlaf",
        "Isochron 1Hz Delta Heilschlaf Regeneration",
        "Isochron 3Hz Delta Tiefste Meditation",
        "Isochron 5Hz Theta Kreative Trance",
        "Isochron 7.83Hz Schumann Erdung",
        "Isochron 10Hz Alpha Entspannung",
        "Isochron 14Hz SMR Körperbewusstsein",
        "Isochron 18Hz Beta Konzentration",
        "Isochron 25Hz Beta Aktives Lernen",
        "Isochron 40Hz Gamma Höchste Klarheit",
        "Isochron 100Hz HyperGamma Mystisch"
      ]
    }
  }
};

export const getAllSolfeggioEntries = (): string[] => {
  return Object.values(SOLFEGGIO_DATABASE.subcategories)
    .flatMap(subcategory => subcategory.entries);
};

export default SOLFEGGIO_DATABASE;

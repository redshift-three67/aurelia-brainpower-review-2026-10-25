// Bach-Blüten Datenbank nach Dr. Edward Bach
// 38 Original-Blütenessenzen mit emotionalen Zuständen und Leitsymptomen

const BACH_BLUETEN_DATABASE = {
  name: "Bach-Blüten Essenzen",
  category: "Blütentherapie nach Dr. Edward Bach",
  totalEntries: 245,
  subcategories: {
    angstGruppe: {
      name: "Angst-Gruppe",
      entries: [
        "Bach 01 Agrimony Agrimonia eupatoria Seelische Qual hinter Maske",
        "Bach 01 Agrimony Innere Unruhe Sorgen verbergen",
        "Bach 01 Agrimony Sucht nach Harmonie Konfliktvermeidung",
        "Bach 01 Agrimony Schlafstörungen durch Gedankenkreisen",
        "Bach 02 Aspen Populus tremula Unbestimmte vage Ängste",
        "Bach 02 Aspen Vorahnungen Ahnungen böses Gefühl",
        "Bach 02 Aspen Angst vor Unbekanntem Paranormale Erlebnisse",
        "Bach 02 Aspen Alpträume nächtliche Ängste",
        "Bach 20 Mimulus Mimulus guttatus Konkrete bekannte Ängste",
        "Bach 20 Mimulus Schüchternheit Furchtsamkeit Zurückhaltung",
        "Bach 20 Mimulus Angst vor Krankheit Armut Alleinsein",
        "Bach 20 Mimulus Phobien spezifische Situationsangst",
        "Bach 25 Red Chestnut Aesculus carnea Übersorge um andere",
        "Bach 25 Red Chestnut Projektive Angst Befürchtungen",
        "Bach 25 Red Chestnut Symbiose übermäßige Bindung",
        "Bach 25 Red Chestnut Katastrophengedanken Angehörige",
        "Bach 26 Rock Rose Helianthemum nummularium Panik Terror Entsetzen",
        "Bach 26 Rock Rose Extreme Angst Schock Unfälle",
        "Bach 26 Rock Rose Albträume Nachtschrecken Notfälle",
        "Bach 26 Rock Rose Frozen Fear Todesangst"
      ]
    },
    unsicherheitGruppe: {
      name: "Unsicherheit-Gruppe",
      entries: [
        "Bach 05 Cerato Ceratostigma willmottiana Mangelndes Selbstvertrauen",
        "Bach 05 Cerato Ständiges Nachfragen andere um Rat",
        "Bach 05 Cerato Zweifelt an eigener Intuition Urteil",
        "Bach 05 Cerato Leicht beeinflussbar Nachahmer",
        "Bach 12 Gentian Gentiana amarella Entmutigung Skepsis Pessimismus",
        "Bach 12 Gentian Zweifel nach Rückschlägen Depression",
        "Bach 12 Gentian Mangelnder Glaube Negativität",
        "Bach 12 Gentian Kleinmut Niedergeschlagenheit",
        "Bach 13 Gorse Ulex europaeus Hoffnungslosigkeit völlige Resignation",
        "Bach 13 Gorse Aufgeben chronische Krankheit Depression",
        "Bach 13 Gorse Warum noch versuchen Fatalismus",
        "Bach 13 Gorse Dunkle Gedanken Aussichtslosigkeit",
        "Bach 17 Hornbeam Carpinus betulus Montags-Morgen-Gefühl Müdigkeit",
        "Bach 17 Hornbeam Geistige Erschöpfung Antriebslosigkeit",
        "Bach 17 Hornbeam Prokrastination Aufschieberitis",
        "Bach 17 Hornbeam Routine-Müdigkeit Langeweile",
        "Bach 28 Scleranthus Scleranthus annuus Unentschlossenheit Schwankung",
        "Bach 28 Scleranthus Stimmungswechsel Sprunghaftigkeit",
        "Bach 28 Scleranthus Zwischen zwei Optionen hin und her",
        "Bach 28 Scleranthus Mangelnde innere Balance",
        "Bach 36 Wild Oat Bromus ramosus Lebensrichtung unklar",
        "Bach 36 Wild Oat Unzufriedenheit Berufung suchen",
        "Bach 36 Wild Oat Viele Talente keine Richtung",
        "Bach 36 Wild Oat Sinn des Lebens Orientierungslosigkeit"
      ]
    },
    gegenwartGruppe: {
      name: "Mangelndes Interesse an der Gegenwart",
      entries: [
        "Bach 07 Chestnut Bud Aesculus hippocastanum Wiederholt gleiche Fehler",
        "Bach 07 Chestnut Bud Lernt nicht aus Erfahrung",
        "Bach 07 Chestnut Bud Oberflächlichkeit Eile Unachtsamkeit",
        "Bach 07 Chestnut Bud Lernblockaden Muster wiederholen",
        "Bach 09 Clematis Clematis vitalba Tagträumer Realitätsflucht",
        "Bach 09 Clematis Unkonzentriert Gedanken woanders",
        "Bach 09 Clematis Schläfrigkeit Ohnmacht Abwesenheit",
        "Bach 09 Clematis Desinteresse am Hier und Jetzt",
        "Bach 16 Honeysuckle Lonicera caprifolium Vergangenheit Nostalgie Heimweh",
        "Bach 16 Honeysuckle Bedauern über Verlorenes Trauer",
        "Bach 16 Honeysuckle Kann nicht loslassen Verstorbene",
        "Bach 16 Honeysuckle Früher war alles besser",
        "Bach 21 Mustard Sinapis arvensis Tiefe Schwermut Depression",
        "Bach 21 Mustard Grundlose Traurigkeit schwarze Wolke",
        "Bach 21 Mustard Melancholie ohne erkennbaren Grund",
        "Bach 21 Mustard Zyklische Depression Düsterkeit",
        "Bach 23 Olive Olea europaea Totale Erschöpfung Burnout",
        "Bach 23 Olive Körperliche geistige Kraftlosigkeit",
        "Bach 23 Olive Nach Krankheit Überarbeitung Stress",
        "Bach 23 Olive Absolute Müdigkeit Regeneration",
        "Bach 35 White Chestnut Aesculus hippocastanum Gedankenkarussell Grübeln",
        "Bach 35 White Chestnut Zwangsgedanken mentale Qual",
        "Bach 35 White Chestnut Schlaflosigkeit innere Unruhe",
        "Bach 35 White Chestnut Obsessive Gedankenmuster"
      ]
    },
    einsamkeitGruppe: {
      name: "Einsamkeit-Gruppe",
      entries: [
        "Bach 14 Heather Calluna vulgaris Übermäßiges Redebedürfnis",
        "Bach 14 Heather Ego-zentriert Einsamkeit Kontaktsuche",
        "Bach 14 Heather Kann nicht zuhören Selbstbezogen",
        "Bach 14 Heather Bedürftigkeit Klammern",
        "Bach 18 Impatiens Impatiens glandulifera Ungeduld Reizbarkeit Hast",
        "Bach 18 Impatiens Schnell frustriert Nervosität",
        "Bach 18 Impatiens Andere zu langsam Intoleranz",
        "Bach 18 Impatiens Explosives Temperament Anspannung",
        "Bach 34 Water Violet Hottonia palustris Stolze Zurückgezogenheit",
        "Bach 34 Water Violet Überlegenheitsgefühl Distanz",
        "Bach 34 Water Violet Schwierigkeit Nähe zuzulassen",
        "Bach 34 Water Violet Arroganz Isolation Einsamkeit"
      ]
    },
    ueberempfindlichkeitGruppe: {
      name: "Überempfindlichkeit-Gruppe",
      entries: [
        "Bach 01 Agrimony Verdeckte Qual fröhliche Maske",
        "Bach 04 Centaury Centaurium umbellatum Willensschwäche Unterwürfigkeit",
        "Bach 04 Centaury Kann nicht nein sagen Ausnutzung",
        "Bach 04 Centaury Vernachlässigt eigene Bedürfnisse",
        "Bach 04 Centaury Übermäßiges Dienen Selbstaufgabe",
        "Bach 15 Holly Ilex aquifolium Eifersucht Neid Hass",
        "Bach 15 Holly Misstrauen Rachsucht Aggression",
        "Bach 15 Holly Herzschmerz Liebesentzug Verletzung",
        "Bach 15 Holly Blockierte Liebe negative Emotionen",
        "Bach 33 Walnut Juglans regia Übergangszeiten Veränderungen",
        "Bach 33 Walnut Schutz vor äußeren Einflüssen",
        "Bach 33 Walnut Neuanfänge Lebensübergänge",
        "Bach 33 Walnut Link-Breaker alte Bindungen lösen"
      ]
    },
    mutlosigkeitGruppe: {
      name: "Mutlosigkeit und Verzweiflung",
      entries: [
        "Bach 10 Crab Apple Malus pumila Reinigung Selbstekel Scham",
        "Bach 10 Crab Apple Perfektionismus Zwanghaftigkeit",
        "Bach 10 Crab Apple Körperliche Unreinheiten Entgiftung",
        "Bach 10 Crab Apple Selbsthass Ablehnung des Körpers",
        "Bach 11 Elm Ulmus procera Überwältigung Verantwortung",
        "Bach 11 Elm Temporäre Erschöpfung bei Kompetenten",
        "Bach 11 Elm Zu viel Aufgaben nicht gewachsen",
        "Bach 11 Elm Burnout bei Leistungsträgern",
        "Bach 19 Larch Larix decidua Minderwertigkeitsgefühle Versagensangst",
        "Bach 19 Larch Mangelndes Selbstvertrauen Fähigkeiten",
        "Bach 19 Larch Erwartet Misserfolg Prüfungsangst",
        "Bach 19 Larch Unterschätzt sich selbst",
        "Bach 22 Oak Quercus robur Pflichttreue bis zur Erschöpfung",
        "Bach 22 Oak Kämpfernatur gibt niemals auf",
        "Bach 22 Oak Überarbeitung Zusammenbruch Sturheit",
        "Bach 22 Oak Ignoriert eigene Grenzen Burnout",
        "Bach 24 Pine Pinus sylvestris Schuldgefühle Selbstvorwürfe",
        "Bach 24 Pine Entschuldigt sich ständig Reue",
        "Bach 24 Pine Nimmt Schuld anderer auf sich",
        "Bach 24 Pine Übertriebene Gewissenhaftigkeit",
        "Bach 29 Star of Bethlehem Ornithogalum umbellatum Schock Trauma Trauer",
        "Bach 29 Star of Bethlehem Unverarbeitete Erlebnisse Verlust",
        "Bach 29 Star of Bethlehem Trost Tröster Seelenschmerz",
        "Bach 29 Star of Bethlehem Alte nicht geheilte Wunden",
        "Bach 30 Sweet Chestnut Castanea sativa Tiefste Verzweiflung Seelenqual",
        "Bach 30 Sweet Chestnut Existenzielle Not Hoffnungslosigkeit",
        "Bach 30 Sweet Chestnut Grenzen der Belastbarkeit",
        "Bach 30 Sweet Chestnut Dunkle Nacht der Seele",
        "Bach 38 Willow Salix vitellina Verbitterung Selbstmitleid Groll",
        "Bach 38 Willow Opferhaltung warum immer ich",
        "Bach 38 Willow Nicht verzeihen können Nachtragen",
        "Bach 38 Willow Ungerechtigkeit Ressentiments"
      ]
    },
    uebermassigeSorgeGruppe: {
      name: "Übermäßige Sorge für andere",
      entries: [
        "Bach 03 Beech Fagus sylvatica Intoleranz Kritik Arroganz",
        "Bach 03 Beech Verurteilung anderer Perfektionismus",
        "Bach 03 Beech Kann Unvollkommenheit nicht ertragen",
        "Bach 03 Beech Überheblichkeit mangelndes Verständnis",
        "Bach 08 Chicory Cichorium intybus Besitzergreifend Selbstmitleid",
        "Bach 08 Chicory Kontrollierend Überfürsorge Manipulation",
        "Bach 08 Chicory Erwartet Dankbarkeit Gegenleistung",
        "Bach 08 Chicory Bedingte Liebe emotionale Erpressung",
        "Bach 27 Rock Water Aqua petra Selbstunterdrückung Rigidität",
        "Bach 27 Rock Water Strenge mit sich selbst Askese",
        "Bach 27 Rock Water Perfektionismus spiritueller Stolz",
        "Bach 27 Rock Water Selbstkasteiung Märtyrer",
        "Bach 31 Vervain Verbena officinalis Übereifer Fanatismus",
        "Bach 31 Vervain Anspannung missionarisch bekehren",
        "Bach 31 Vervain Überarbeitung für die Sache",
        "Bach 31 Vervain Kann nicht entspannen Stress",
        "Bach 32 Vine Vitis vinifera Dominanz Kontrollsucht Tyrannei",
        "Bach 32 Vine Autoritär unnachgiebig Machtmissbrauch",
        "Bach 32 Vine Überzeugt von eigener Überlegenheit",
        "Bach 32 Vine Inflexibilität Diktator"
      ]
    },
    rescueRemedy: {
      name: "Rescue Remedy Notfall-Tropfen",
      entries: [
        "Bach Rescue 5er Kombination Notfall akut",
        "Bach Rescue Star of Bethlehem Schock Trauma",
        "Bach Rescue Rock Rose Panik Terror",
        "Bach Rescue Clematis Bewusstlosigkeit Ohnmacht",
        "Bach Rescue Impatiens Anspannung Stress",
        "Bach Rescue Cherry Plum Kontrollverlust Verzweiflung",
        "Bach Rescue Akute Krisensituationen",
        "Bach Rescue Prüfungsangst Lampenfieber",
        "Bach Rescue Nach Unfällen Schreckerlebnissen",
        "Bach Rescue Vor Operationen medizinischen Eingriffen"
      ]
    },
    kombinationen: {
      name: "Bewährte Kombinationen",
      entries: [
        "Bach Kombi Prüfungsangst Larch Mimulus Rescue",
        "Bach Kombi Burnout Olive Oak Elm Hornbeam",
        "Bach Kombi Depression Mustard Gorse Sweet Chestnut",
        "Bach Kombi Trauer Honeysuckle Star of Bethlehem Walnut",
        "Bach Kombi Beziehungsprobleme Holly Chicory Willow",
        "Bach Kombi Schlafstörungen White Chestnut Agrimony",
        "Bach Kombi Kindheit Chestnut Bud Honeysuckle",
        "Bach Kombi Selbstwert Pine Larch Crab Apple",
        "Bach Kombi Veränderung Walnut Wild Oat Scleranthus",
        "Bach Kombi Abgrenzung Centaury Walnut Agrimony"
      ]
    }
  }
};

export const getAllBachBluetenEntries = (): string[] => {
  return Object.values(BACH_BLUETEN_DATABASE.subcategories)
    .flatMap(subcategory => subcategory.entries);
};

export default BACH_BLUETEN_DATABASE;

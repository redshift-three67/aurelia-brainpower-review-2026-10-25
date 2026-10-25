# RadiWorks EXP1-A — geprüfte Formelgrenzen, 05.10.2026

## Ergebnis und Status
Die notwendige Quellen-/Formelvorprüfung EXP1-A ist abgeschlossen. **23/23 synthetische Quellenproben bestanden**, keine Skips/Fehler. Eine vollständige EXP1-Rankingimplementierung ist noch nicht vorhanden; UI/API/Liveinstanzen unverändert. Genehmigter separater Experimentalmodus und Original als Standard bleiben verbindlich. Für die Umsetzung fehlen zwei fachliche Eingabeentscheidungen: Bedeutung von Ort und erste numerische Bildstrategie. Fragen wurden dem Betreiber gestellt; keine Antwort wird angenommen.

114 VF3-Produktdateien und sechs Referenzquellen wurden vor/nach Prüfung per SHA-256 bytegleich geprüft. 8103–8110 antworteten jeweils HTTP200 auf /ping. Keine Tasks, Prozessstopps, laufenden Aufträge, Keys, Homes, realen Fall-/Bilddaten, kanonischen Modul_Templates/Aurelia-Quellen oder Hermes-Routen verändert. Es wurde kein vollständiger Funktionscheck dieser acht laufenden Instanzen vorgenommen.

## Nachweisumfang
runtime/exp1-source-audit-20261005/{BASELINE.json,VERIFICATION.json,REVIEW.json,test_radi144_contract.py,source-probes.xml,source-probes.log}. Tests laden die exakt hashgeprüften Radi144-Klassen per AST in einem eigenen Prozess, ohne App-Bootstrap oder Engine-Konstruktor. Verwendet wurde die vorhandene Radi144-Testumgebung: Python3.11.12, Torch2.12.0+cpu, NumPy2.4.6. Dies ist **kein Nachweis für den RadiWorks-Zielruntime Python>=3.12**, kein vollständiger Datenbankscan, keine API-/Browserabnahme, kein Win10-Paket. CPU-Probe mit nur64 Matrixkandidaten und synthetischem Kontext; weder Produktionsleistung noch Rankingqualität daraus ableiten. Bestehendes Verhalten wurde geprüft; kein neues Produktverhalten implementiert, daher kein Feature-RED/GREEN behauptet.

## Exakte vorhandene Formelbausteine
Quellen: Radi144 app/algorithms/client_signature.py, resonance_engine.py, app/api/resonance.py. Vollständige SHA-/Bytebelege in BASELINE.json.

- Textfrequenz: (Summe alphabetischer Zeichenwerte + vereinfachte Phonetiksumme)/2 modulo1000. Vokale a440/e330/i550/o220/u165, andere alphabetische Zeichen zweimal Zeichenwert. Reihenfolge kann kollidieren: ab und ba liefern dieselbe Frequenz. Kein semantisches Verständnis oder Genauigkeitsnachweis.
- Geburt: 0.6*(Julianischer Tag modulo1000) + 0.3*(erste vier MD5-Hexzeichen des normalisierten Geburtsorts /65.535) + 0.1*(Geburtszeitminuten/1.44), modulo1000. Ort wirkt nur mit Geburtsdatum. Ort ist hier ausdrücklich birth_place, nicht beliebiger Aufenthaltsort.
- Person: normalisierter gewichteter Mittelwert, Namegewicht0.15/Geburt0.20; die Originalfunktion ergänzt stets die aktuelle Organuhr mit0.10. Optionale vorgegebene Bildfrequenz hätte0.25. Fehlende Identität wird nicht automatisch als Fehler behandelt; der Organuhrwert allein kann ein Ergebnis erzeugen. RadiWorks darf fehlende Angaben nicht erfinden.
- Deterministische lokale Vektoren: MD5-basierte Seeds, Torch-Generator, je256 normalverteilte Werte. Personensaat aus Frequenz und sortierten Komponenten, Fokus aus exakt übergebenem Text. Groß-/Kleinschreibung des Fokus beeinflusst den Vektor. Ein Austausch gegen Python-random wäre ein anderes Zahlenverfahren.
- Matrixscore: Kosinusähnlichkeit der zufälligen Matrixprojektionen mit Ziel client_vector + w*focus_vector; bestes Kandidatenergebnis. Bestehende w: Deaktiviert0/Sanft0.4/Normal1/Stark1.5. Precision setzt einen Masterseed aus Vorname, Geburtsdatum und Fokus. Wiederholbarkeit zusätzlich abhängig von Backend, Bibliotheken, Kandidatenzahl, Bio-Wissen, Zeit und optionaler HRV/EMF-Konfiguration.
- Die Farbpalettenmischung zwei Drittel Person/ein Drittel Fokus ist ausschließlich eine Farbformel. Sie ist **keine bestehende Gewichtung für Ratenranking** und wird nicht dafür übernommen.

## Fokusbefund präzisiert
scan_database ruft calculate_resonance für jeden Datenbankeintrag mit diesem Eintrag als direktem Fokus auf. Der gespeicherte Fokus hat trotzdem **bedingt** einen weiteren Weg: _prepare_precomputed_signature -> vectorise_database_selection sucht dessen ganzen Text als case-insensitive Teilzeichenfolge in der Datenbank. Nur bei positiver Textfrequenz wird die Personensignatur mit der Fokusfrequenz gemittelt; db_frequency_hz und Datenbankdateiname db_source gehen anschließend in die Komponenten ein. Kein Treffer bzw. zusammengesetzter Fokus ohne zusammenhängende Fundstelle bedeutet keine solche Zusatzwirkung. Die Proben bestätigen dies; frühere verkürzte Aussage ohne diesen API-Vorpfad wäre unvollständig.

## Bild- und Ortsgrenzen
Radi144s API-Bildzweig ersetzt die Personensignatur und überschreibt die Namen durch Bildlabel/Bild. Der separate generate_signature-Eingang image_signature_ai kann eine vorausberechnete Frequenz ergänzen, ist aber im betrachteten API-Pfad nicht mit der Bildberechnung verbunden. Eine komplette neue gemeinsame Mischung ist daher keine belegte 1:1-Übernahme.

Radi144s Bildberechnung verarbeitet Originalbytes, RGB/HSV, Pixelentropie und Dateibasisname. VF2B erhält ein geprüftes Bildasset mit Inhaltsadressierung; der persönliche Snapshot speichert SHA/Medientyp/Bytezahl, keinen ursprünglichen Dateibasisnamen. Ein neuer Name oder Decoder-Fallback kann Zahlen ändern. Ein Hash allein reproduziert die gesamte Bildformel nicht. Keine echten Bilder für diese Quellenproben verwendet.

Das vorhandene RadiWorks-Feld place ist als allgemeiner Ort gespeichert; daraus wird nicht stillschweigend Geburtsort. Ort ohne Geburtsdatum erhält nicht heimlich eine neue eigene Frequenz.

## Empfehlung für den ersten numerischen Vergleich
1. Bestehenden Radi144-Matrixscore als eigenen, klar bezeichneten Vergleichsweg erhalten. Keine Vermischung mit Original-EW/Potenz/Level/GV und keine Übertragung von Farbgewichten ins Ranking.
2. Kontext normalisiert aus dem eingefrorenen Snapshot; kein Rückgriff auf inzwischen geänderte Falldaten, alte freie Fallnamen nicht als Identität auslegen. Name/Geburt nur als vorhandene Komponenten. Organuhr standardmäßig aus, wie bereits genehmigt; eigene Formelversion dokumentiert diese Abweichung von Radi144s Default. Uhrzeit bleibt Provenienz, ohne versteckte numerische Wirkung.
3. Ursprüngliche Fokus-Teilzeichenfolgenheuristik beibehalten und anzeigen, ob sie wirkte. Auch exakten Datenbanknamen neben Inhaltsdigest pinnen. Gespeicherter Fokus wird nicht als generell wirksam bezeichnet.
4. Optionales Bild vorerst unveränderlicher Auftragskontext; eigener numerischer Bildvergleich separat, sofern der Betreiber dieser Reihenfolge folgt. Kein Bildverlust und keine heimliche Bild-/Personenmischung.
5. Bestehende feste CPU-Formelparameter/Dependency-Versionen in eigenem Runtimeprofil vor Umsetzung pinnen; vollständige Probe in RadiWorks-Zielversion>=3.12 erforderlich. Keine Torch-/NumPy-Installation oder Änderung an der Live-Engine vorgenommen. Hardwareabhängige adaptive Kandidatenzahlen und Bio/HRV/EMF/Quantum sind für kontrollierte Vergleiche nicht automatisch aktiv.
6. Separate Sessions aus derselben Originalgrundlage, gleiche Katalog-/Quellenbindung und Ausgangsentropie; Experimental-Scores mit eigener Bezeichnung/Version/Parametern/Sourcenachweis. Ursprüngliche Sitzung und laufende Broadcasts unverändert. Stochastic braucht einen vollständig rekonstruktierbaren Ausgangsstand; andernfalls sichtbar ungeeignet statt ungleichen Vergleich vortäuschen.

Diese Empfehlung ist ein begrenzter Implementierungsvertrag in Vorbereitung. Kandidatenzahl, zulässiger Scanumfang, Laufzeitumgebung und Fehler-/Recovery-Vertrag werden vor Produktimplementierung konkret gepinnt;64 aus der Probe ist **kein** Produktdefault. Es wird keine neue Formel ohne Besprechung erfunden.

## Modelle und Fortsetzung
Gewählte Leitung Sol6.1/high (keine aktive Modellwahl durch Konfigurationsdateien behauptet). Luna6/max: begrenzte lesende Formelprüfung; Astra6/medium: unabhängige Prüfung der wesentlichen Formel-/Eingabegrenzen. Root führte alle23 Proben, Hash-/Portprüfungen und Dokumentation aus. Keine gemessene Tokenersparnis oder neue Hermes-Modellanfrage.

| Paket | Stand |
|---|---|
| VF2A/B und VF3 | 100% der begrenzten Kandidatenpakete, noch nicht live übernommen |
| EXP1-A Quellen-/Formelvorprüfung | 100% des abgegrenzten Prüfpakets |
| EXP1 numerischer Produktmodus | 0% Implementierung; Eingabefragen und Detailvertrag offen |
| Restabnahmen/Templates/Windows10-Paket/GesamtsicherungF | offen, unveränderte Folgeplanung |
| S4.8 | 0% Integrationsfreigabe |

Nächster Schritt nach Eingabeklärung: konkreten Formel-/Parametervertrag fertigstellen und EXP1 isoliert implementieren/testen; danach eigenständige Betreiberprobe. Die übrige akzeptierte Modul-/Paket-/Sicherungsreihenfolge bleibt unverändert.

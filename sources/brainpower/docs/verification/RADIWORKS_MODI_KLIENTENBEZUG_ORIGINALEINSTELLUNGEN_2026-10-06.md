# RadiWorks: Klientenbezug, Modi und Originaleinstellungen

Stand: 06.10.2026. Quellenreview und Empfehlung zur Besprechung; keine Implementierung oder Integrationsfreigabe. BC1 und übrige Restarbeiten folgen erst nach dieser Klärung. Zentrale Datenbankstruktur wird separat besprochen. Liveinstanzen, Portable5 und externe Produktquellen wurden nicht geändert.

## Original und Klientenbezug

Im untersuchten AetherOnePi-2.9.0-Analysepfad erhält AnalysisService.analyseRateList eine Ratenliste und arbeitet mit Hotbits-Ziehungen und Analyseparametern. Name, Vorname, Geburtsdatum und Geburtsort gehen nicht als persönliche Zahlenformel ein. AetherOneEventHandler.analyzeDatabase liefert die Katalograten, keinen Personenvektor. checkGeneralVitality erzeugt Werte aus Zufallsziehungen ohne Personenparameter.

Die Herstelleranleitung beschreibt die Registrierung des Ziels durch Fallname/Beschreibung und die Intention/Fokussierung des Bedieners. Das ist der erklärte Bedienablauf, keine im untersuchten Kern nachgewiesene mathematische Umsetzung dieser Intention. Fallname ist Akten-/Zielbezeichnung, kein automatischer Seed. Kein Vollaudit aller JAR-Klassen wird behauptet.

RadiWorks ergänzt Fall-ID, Kontextversion und eingefrorenen Snapshot. Dies bindet die Sitzung an den Fall, verändert aber keine Originalzahlen. Promote übernimmt eine ContextReference nur bei vorhandenem gültigem Snapshot; Legacy-Drafts können ohne bestehen. Direct/Auto/Image besitzen noch keine gemeinsame vollständige Zielbindung (BC1).

| Feld | Originalanalyse heute | Vorhandenes EXP1 |
|---|---|---|
| Fallname/Beschreibung | Kontext, keine Zahlengewichtung | keine Zahlengewichtung |
| Vorname/Nachname | Kontext | Radi144-Namensheuristik; Vorname zusätzlich Matrix-Seed |
| Geburtsdatum | Kontext | Geburtsheuristik und Matrix-Seed |
| Geburtsort | Kontext | nur ausdrücklich gewählter Geburtsort zusammen mit Geburtsdatum |
| Wohn-/Aufenthaltsort | Kontext; nicht zugleich aktiver Geburtsort | keine Ortsgewichtung |
| Fokus | Kontext; Wortsuche schlägt Kataloge vor, Nutzer bestätigt | wortwörtlicher Katalogfund kann vorhandene Signatur ergänzen |
| Fokusbild | eingefrorene Referenz, keine persönliche Pixelgewichtung | Kontext-only |

EXP1 verwendet Namens-/Geburtsbasisgewichte 0,15/0,20, normalisiert über vorhandene Komponenten. Keine semantische KI-Suche oder ungeprüften neuen Formeln. Unterschiedliche Personenfelder müssen nicht zwingend verschiedene Ratenlisten liefern. Zahlenheuristiken sind keine gemessenen körperlichen Frequenzen.

## Verfahren und Zufall sind getrennte Eigenschaften

Original ist nicht gleich deterministisch. Derselbe Originalalgorithmus kann mit festem Seed reproduzierbar oder mit frischen Zufallswerten stochastisch laufen. Ein Personenhash allein erzeugt keine frische Stochastik.

| Pfad | Quellbefund | Grenze |
|---|---|---|
| RadiWorks Original seeded | Originalformeln, Katalog und Seed | gleiche Ergebnisse trotz verschiedener persönlicher Kontextfelder; vorhandene synthetische Belege |
| RadiWorks Original stochastic | Webcam-Feed → random.org → OS-CSPRNG; pro Seed JavaRandom-Ziehung | Analyse implementiert; Kamera nicht abgenommen; Netzwerk-Backoff nur im geprüften Kandidaten |
| RadiWorks EXP1 | persönliche Radi144-Heuristik, lokale deterministische Torch-Generatoren | bis 21 ausdrücklich gebundene Raten; eigener Score, kein vollständiger Analyseersatz/Broadcast/stochastischer EXP1-Eingang |
| Radi144 Precision | persönliche Signatur/Fokus; globaler Torch-Seed aus Vorname+Geburtsdatum+Fokus, später Zustand restauriert | keine Isolation paralleler Global-RNG-Zugriffe; optionales NumPy-HRV bleibt separat zufällig |
| Radi144 Quantum | persönliche Signatur/Fokus, Torch-PRNG ohne Precision-Seed | keine belegte Quantenhardware/Hotbits in Matrixsuche; D-Wave-Verfeinerung ist dort Mock |
| RadiMorphic Standard | Profilkodierung aus Namen, Geburtsdatum/-ort, Bild/Ersatzbild, planet_type | im geprüften Standardpfad kein RNG; getrennte CLI-/BAT-/NLS-Pfade beachten |
| RadiMorphic Multiplex/BAT | je Pfad feste/personenabgeleitete Seeds; Entropiemodi liefern u.a. h_level | Entropie-Skalar ist kein frischer Matrix-Seed; Workspace-Seedutility hat in geprüften Produktverzeichnissen keine Aufrufer |

Radi144 besitzt weitere Signaturen (Geburtszeit, Organuhr, optionale Bilder/Planeten), die nicht vollständig nach RadiWorks portiert sind. Bestehende EXP1-Freigabe umfasst sie nicht automatisch. HRV/Bio/EMF/CUDA bleiben außerhalb des aktuellen EXP1-Vertrags. Der EMF-Seedhelper wird im geprüften Matrixaufruf nicht verwendet; OS-basierte Kompensation beweist keine solche Seedverdrahtung.

## Broadcast ist ein eigener Pfad

RadiWorks erzeugt seinen BroadcastManager mit EntropyProvider(seed=0, mode="seeded"). Die stochastic-Auswahl der Analyse schaltet ihn nicht um. GV2 verwendet wiederum eigene journalisierte OS-Ziehungen.

Broadcast-Resonanz ist heute eine Simulation: Zufallsziehung gegen eine vom Multiplier abhängige Grenze, bei Treffer Zähler erhöhen. Persönliche Felder wirken nicht numerisch auf diese Formel. Promote-Signatur enthält Rate/EW/Potenz; persönlicher Kontext ist eine getrennte Referenz. Software-GV/Zähler sind keine gemessenen Klientenreaktionen oder Wirksamkeitsbelege.

Original-BroadcastElement initialisiert JavaRandom u.a. mit Startzeit bzw. alternativ Hotbits und besitzt einen separaten SecureRandom. RadiWorks-Fixseed 0 bildet diese Quellen nicht vollständig ab. Stochastischer Broadcast könnte diese Abweichung verringern; allein dadurch keine vollständige Originalparität.

Radi144s API kann explizite client_data analysieren und zugleich die Session an client_id spiegeln, ohne in den geprüften Stellen Identitätsabgleich. Kein zu übernehmender Zielvertrag. Morphics synchroner HarmonizationService bindet Profil/Analyse; persistierter HarmonizationWorker enthält Frequenz/Dauer/Intention/Hardware, aber keine Client-/Profil-/Workspace-/Session-ID. Keine vollständig übertragbare gemeinsame Zielbindung.

## Optionen und Empfehlung, noch nicht beschlossen

| Option | Nutzen/Grenze | Empfehlung |
|---|---|---|
| Nur Original + vollständige Zielbindung | Original erhalten, seeded/stochastic wählbar; kein numerischer Personenvektor | Originalreferenz erhalten, allein nicht gesamte persönliche Anforderung |
| Personenfelder nur als Seed hashen | unterschiedliche reproduzierbare Ergebnisse | keine persönliche Gewichtungsheuristik und keine frische Stochastik; nicht Hauptlösung |
| Original + eigener persönlicher Radi144-Heuristikpfad | geprüfte EXP1-Teile weiterverwenden, eigene Quellenwahl | empfohlen; neue versionierte Implementierung und Abnahme |

Zielmodell: zwei Auswahlachsen, verständliche Presets:

| Verfahren | Reproduzierbar | Stochastisch |
|---|---|---|
| Original AetherOne | vorhanden | Analyse vorhanden; Broadcast-End-to-End zu ergänzen/prüfen |
| Persönliche Radi144-Heuristik | derzeit begrenzter EXP1-Vergleich | neuer vollständiger Pfad, noch nicht implementiert |

Der persönliche Weg kann nach technischer Abnahme regulär bedienbar statt bloßer Vergleich sein. Original-EW/GV und Matrixscores bleiben getrennt; keine stille Ersetzung oder Prozentumrechnung. Über 21 Raten hinaus sind Katalog-/Seiten-/Budget-/Canceltests notwendig.

Erste End-to-End-Stufe: persönliche Analyse, bestätigte Ratenauswahl und virtueller Broadcast führen denselben unveränderlichen Zielkontext. Ob persönliche Größen zusätzlich die Broadcast-Zahlenformel ändern sollen, ist gesondert zu entscheiden. Rate+Snapshot schaffen Zuordnung, noch keine numerische persönliche Kopplung der Broadcast-Ziehung. Keine hierfür erfundene Formel.

Vor Aktivierung: BC1 für alle Startwege; ID/Snapshot/Scope serverseitig konsistent; Verfahren/Quellenpolitik pro neuem Auftrag; eigene RNG/Journale statt globaler Torch-Zustände; Quelle/Version/Katalog/Entropie protokollieren; Replay von frischer Erzeugung unterscheiden; Wiederanlauf/Abbruch/parallel getrennte Fälle/Originalregression prüfen. Neue Auswahl bindet laufende Jobs nicht um. Kamera/Fallback sichtbar ausweisen. Original und EXP1 unverändert erhalten. Datenbankausbau später; Identität, Rechte, Auftragsscope und Snapshotvertrag schon vorher.

## Originaleinstellungen

Korrektur älterer Kurzbeschreibungen: power.switch bedeutet im Original endlose Broadcast-Wiederholung, nicht Hardwareaktivierung. RadiWorks speichert heute nur den Wert. Diese Präzisierung ersetzt die unvollständige Hardwarezuordnung im Bericht vom 05.10.; historische Belege bleiben erhalten.

| Schalter | Originalbedeutung | Heute | Stabiler Ausbau |
|---|---|---|---|
| analysis.very.high.max.hit | EW-Abbruchschwelle 100/1000, nicht Ergebnisanzahl | ausdrückliche Analyseauswahl wirkt, alter Schalter nur gespeichert | Auswahl erhalten, optional nachvollziehbare Vorbelegung |
| notification.after.broadcast | lokale Abschlussmeldung | nur gespeichert, Default True | ausdrückliche zugängliche lokale Meldung, kein Mailversand |
| broadcast.single.rates.only | nacheinander statt bis acht gleichzeitig | nur gespeichert, MAX_ACTIVE=8 | explizit 1/8 aktive Jobs, Warteschlange erhalten |
| broadcast.delta.time | bei Sekunden > Fall-GV Differenz, sonst unverändert | Schalter ohne Wirkung; Promote hat eigene Mindestdauer-/Differenzregel | Dauerregel je Startweg mit Vorschau, nicht doppelt anwenden |
| broadcast.embedded | integrierte Anzeige oder separates Javafenster | nur gespeichert; Browserdock funktioniert | Dock erhalten, Zusatzfenster nicht notwendig |
| use.overlay | weichere Originaldarstellung | nur gespeichert; Area-Overlay getrennt | optional Darstellung, Themes/A11y bevorzugen |
| play.binaural.sound | Ton bei Broadcastereignis | Browserfunktion mit Audiofreigabe | optional erhalten, keine Analyseänderung |
| dynamic.adjustments | nach Abschluss neue GV und bedingt verkürzter Folgeauftrag | nur gespeichert; nicht GV2 | eigener begrenzter Folgeauftragsvertrag/Stop/Recovery, zunächst aus |
| power.switch | endlos wiederholen bis Stop, Vorrang vor Adjustments | nur gespeichert | zurückstellen, begrenzte explizite Wiederholung bevorzugen |
| watchlist.activate | Startpfad liestCSV, analysiert/markiert niedrigeGV | nur gespeichert | später Rechte/Listenvertrag, Vorschau/Start; kein ungeprüfter Autostart |
| trng.infinity/trng.esp32 | externe Generatoren | nicht angebunden | optional/zurückgestellt |
| safety.switch/play.sound.advanced | Originaldarstellung/Audiopfad; kein belegter physischer Not-Aus | nicht vollständig übernommen | Zweck/Audioinhalte/Rechte getrennt prüfen |
| EgoCleaner | separat besprochene Audio-Erweiterung | ausgeschlossen, Planerweiterungspunkt | bleibt aus |

Delta-Zeit in der Herstelleranleitung: RateGV-FallGV als Beispiel. Im geprüften konkreten Startpfad wird das Sekundenfeld verwendet; Herkunft je Startweg prüfen. Dynamic Adjustments sind keine periodischen GV2-Beobachtungen. Gespeicherte Altwerte dürfen nicht unbemerkt neue aktive Wirkungen erhalten.

## Quellen und Prüfgrenzen

Frisch: C23 131/131 Produktdateien bytegleich. ManifestSHA256 9ba23c5dbfe856fc6887abf87fe13aba302ec362c1cdd432654d8fa30fe50694. Lokales2.9.0JAR frischSHA256 24090abb6726ddf9a44a38f28f972c349d04311b7d35ef4e3d06bb6078e4d660. Keine neue Engine-/Browser-/Kamera-/Modul-Testsuite ausgeführt; vorhandene Belege gelesen, nicht als neue Tests ausgegeben. Kein JAR gestartet, kein Hermesmodellauftrag.

Root: runtime/rw-c23-fixed-release-20261005/engine/src/radiworks/core/analysis.py:158; entropy.py:124; main.py:151; core/broadcast.py:491; core/experimental_context.py; core/experimental_matrix.py:106; core/draft.py:337; webapp/js/views/settings.js. Originalbytecode: runtime/rw-vector-audit-20261004/jar-bytecode/; CFR runtime/video-review-20261001/aether290-cfr/.../GuiElements.java:224,358; runtime/rw-video-gv-inspect-20261002/BroadcastElement.javap.txt.

Radi144/Luna: C:/Users/Hubert111/Documents/Radi144/app/algorithms/client_signature.py:29-105,304-373,402-414; resonance_engine.py:243-409,481-485,1068-1092,1139-1155; emf_compensator.py:152-204,462-572; app/api/resonance.py:83-125,279-305. Testassertions test_engine_regressions.py:35-49,99-113 vorhanden, hier nicht ausgeführt.

Morphic/Luna: C:/morphic_v1/services/analysis_service.py:27-72; core/profiles/profile.py:183-263; apps/cli/commands/field.py:719-733,2829-2895,2943-3076; apps/cli/commands/scan.py:1209-1231,1360-1391,2009-2013; core/realtime/seed_generator.py:26-88; core/hybrid_entropy.py:108-120; services/harmonization_service.py:23-59; services/harmonization_worker.py:43-61,489-539; apps/web/harmonization.py:68-117. Begrenzte Pfade, kein Vollaudit.

Primärquellen: [v2.9.0 AnalysisService](https://raw.githubusercontent.com/isuretpolos/AetherOnePi/v2.9.0/src/main/java/de/isuret/polos/AetherOnePi/service/AnalysisService.java), [v2.9.0 AetherOneUI](https://raw.githubusercontent.com/isuretpolos/AetherOnePi/v2.9.0/src/main/java/de/isuret/polos/AetherOnePi/processing2/AetherOneUI.java), [Herstelleranleitung](https://radionics.home.blog/aetheonepi/). Intention-/Wirksamkeitsbeschreibungen der Anleitung sind kein technischer oder wissenschaftlicher Nachweis.

| Paket | Fortschritt |
|---|---|
| Begrenzte Modus-/Klienten-/Einstellungsklärung |100% Quellenreview; Besprechung offen|
| Vollständiger persönlicher Stochastikweg |Empfehlung, Umsetzung 0%|
| BC1 |Entwurf, Umsetzung 0%; zurückgestellt|
| Entropie-Backoff |Kandidat geprüft; Liveübernahme 0%|
| Kamera-Hotbits |nicht abgenommen|
| Aurelia S4.8 |0% Freigabe|

Luna 6/max: begrenzter lesender Radi144-/Morphic-Abgleich. Astra 6/medium: unabhängiger C23-/Empfehlungsreview, anschließend Einordnung übermittelter Modulbefunde; nicht alle externen Modulstellen selbst gelesen. Root: Original-/Einstellungsabgleich, Manifestprüfung/Konsolidierung. Keine gemessene Tokenersparnis, keine Routingänderung.

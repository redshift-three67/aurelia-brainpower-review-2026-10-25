# RadiWorks: persÃ¶nliche Laufzeit und Zufallsmodus â€“ 2026-10-07

8112 lÃ¤uft mit dem geprÃ¼ften Kandidaten `runtime/rw-performance-v2-20261007`: 184 Produktdateien, Manifest `ad3c06f9f4a42d1864b10ca0665a7598d8e70e5ae0908f2cf3c51fad6bba4c20`, PID45644. Alle 123 Kataloge sind verfÃ¼gbar. Home, Scope und SchlÃ¼sselpfad bleiben gleich. Gespeicherte FÃ¤lle werden bewusst geladen; alte AuftrÃ¤ge werden nicht automatisch wiederholt. Dauerinstanzen8103â€“8109 und Start5 bleiben unverÃ¤ndert.

## Was geÃ¤ndert wurde

Die persÃ¶nliche Analyse verwendet einen eigenen CPU-Prozess je Auftrag statt je 21er-Block. Formeln und numerische Dateien bleiben bytegleich; weiterhin 80.000 Kandidaten je Rate und ein CPU-Thread. Das binÃ¤re Protokoll begrenzt Eingabe auf 12 MiB, Antwort auf 256 KiB und die Warteschlange auf zwei Frames. GeprÃ¼fte PrÃ¤fixblÃ¶cke werden gespeichert. Der Schlussblock wird erst nach Abschlussnachricht, EOF, erfolgreichem Prozessende und bestÃ¤tigter Bereinigung gespeichert. FolgeauftrÃ¤ge erhalten getrennte Prozesse und Zufallsfolgen.

Die OberflÃ¤che bietet nur â€žReproduzierbarâ€œ und â€žStochastischâ€œ. Sie Ã¼bernimmt beim Ã–ffnen den gespeicherten Serverstandard sichtbar; eine spÃ¤tere manuelle Auswahl wird nicht Ã¼berschrieben. Fehlt der Standard, muss der Nutzer wÃ¤hlen. Backenddefaults bleiben kompatibel.

## Frische Nachweise

| PrÃ¼fung | Ergebnis |
| --- | --- |
| PersÃ¶nliche Analyse, Store, Verbindungsfreigabe, Controller, Stream, API und CPU-Sperre |78PASS |
| Originalanalyse, API, Broadcast-Entropie und Target-API |88PASS |
| Bestehende UI und neue Modusauswahl |53PASS;29JS-SyntaxprÃ¼fungen |
| Feste Audioprofile als reiner Planer |5PASS; keine Wiedergabe integriert |
| Numerische ParitÃ¤t |Seed0, Seed17 und eingefrorene Stochastik: jeweils24 echte Raten exakt gleich zum bisherigen Worker |
| Vollkatalog |1382synthetische Raten vollstÃ¤ndig in186,220s; ein Worker, sÃ¤mtliche Indizes, Fortschritt und saubere Bereinigung geprÃ¼ft |
| Sichtbarer Chrome |8112: vier Auswahlkombinationen, GV/AutoAUS sichtbar, persÃ¶nliche Ansicht korrekt;1440/390px und Tastaturfokus;0PageErrors,0API-Schreibanfragen |
| Neustart und Datenerhalt |Alte8112 sauber beendet;8completed/2cancelled AuftragsdatensÃ¤tze und343 ausgewÃ¤hlte gespeicherte Dateien bytegleich; SQLite-IntegritÃ¤tok |

Gleiche eingefrorene24er-Eingaben, bisher zwei Worker gegenÃ¼ber jetzt einem: Seed0 15,247â†’9,037s; Seed17 15,344â†’8,569s; Stochastik17,617â†’10,703s. Alle Zeilen einschlieÃŸlich Scores, IntensitÃ¤ten und Matrizen sind identisch; PrÃ¤fixfortschritt und Prozess-/Threadabschluss geprÃ¼ft. Die Messungen garantieren keine allgemeine Laufzeit. Der historische Volllauf von etwa597s stammt aus einer anderen Messsituation; daraus wird keine genaue prozentuale Beschleunigung abgeleitet.

Stochastische ParitÃ¤t verwendet eingefrorene Kandidatenseeds, synthetischen WebcamFeed und einen temporÃ¤ren Fernet-SchlÃ¼ssel. Keine echte Kamera-, Linux-, DAC- oder HÃ¶rabnahme. Original-EW/GV und persÃ¶nliche Scores bleiben getrennt.

Evidenz unter `runtime/rw-performance-v2-20261007/evidence`: `independent-parity.json`, `full-catalog.json`, `personal-final-tests.xml`, `original-api-tests.xml`, `shared-budget-tests.xml`, `random-mode-browser.json`, `live-browser.json`, `promotion.json`. Implementierungshash: `ca51a4e954d3b1469f4f69bdd0435c411e2eba60909b2f7db0d36e9972270113`.

## Review und Grenzen

Luna6/max implementierte den begrenzten Worker und seine Tests. Astra6/medium prÃ¼fte wesentliche Fehlerpfade: Speicherfehler, doppelte SchlussblÃ¶cke, ungÃ¼ltige Fehlerwerte, Puffer nach Abbruch, Storeausfall vor Auftragstart und fehlende BestÃ¤tigung der Prozessbereinigung. Nach Korrektur meldet der begrenzte Nachreview keinen blockierenden Corebefund. Root fÃ¼hrte die unabhÃ¤ngigen numerischen und API-PrÃ¼fungen aus.

Alte Testdoubles unterstÃ¼tzten nur Text-`communicate()`; sie wurden gezielt auf binÃ¤re Pipes beziehungsweise echte Kinder mit kÃ¼nstlichen Zahlen umgestellt. Die API-SchutzprÃ¼fungen bleiben unverÃ¤ndert. Echte Numerik wurde separat verglichen. Eine5s-Fixture-Wartezeit scheiterte unter Last; Diagnose zeigte nach1,3s den korrekten Fehlerstatus. Nur synthetische Wartehilfen wurden auf10s gesetzt; produktiver Blocktimeout bleibt120s. Vorhandene Node-/Starlette-Warnungen wurden nicht durch neue ProduktionsabhÃ¤ngigkeiten kaschiert.

Bei dauerhaft unerreichbarem Store wird die Berechnung gesperrt. Ein nicht schreibbarer Fehlerstatus kann nicht als gespeichert zugesichert werden. Kein automatisches Replay. Neue Betreiberprobe und Kamera-/Windows-/Linux-Betriebsabnahmen bleiben offen.

## Audio und nÃ¤chste Phasen

BestÃ¤tigte Folge:174/285/396/417/528/639/741/852/963Hz. Einzelprofile:432/528/429,62Hz. Der feste Planer unterstÃ¼tzt1â€“600 ganze Sekunden je Stufe und optionale Wiederholung. Wiedergabe, Fallbindung, Rosa Rauschen/Phi/Fibonacci und fÃ¼nf Animationsbilder sind noch nicht integriert. Pulsparameterfrage offen. Vertrag: `docs/superpowers/plans/2026-10-07-radiworks-audio-layer-profile.md`.

| Paket | Stand dieses abgegrenzten Pakets |
| --- | --- |
| P1â€“P4 Laufzeitkorrektur und technische PrÃ¼fung |100% |
| P5 Ãœbernahme in Entwicklungsinstanz8112 |technisch100%; Betreiberprobe offen |
| AU1 feste Profilplanung |numerischer Teil100%; Audiointegration offen |
| AU2/AU3 Wiedergabe, Fallbindung, Rausch-/Phi-Adapter |0% integriert |
| BL1/BL2 fÃ¼nf Bildlayer je Fall |0% integriert |
| R6 und aktualisiertes Start5 |0% dieser ErgÃ¤nzungen Ã¼bernommen |
| AureliaS4.8 Integrationsfreigabe |0% |

Vorwechselpunkt `checkpoints/RadiWorks-CPU-Vorwechsel-20261007-224120`:525 Dateien hashgeprÃ¼ft,178 vorherige Produktdateien geschÃ¼tzt, beide SQLite-Kopien konsistent. SchlÃ¼ssel nicht kopiert; Wiederherstellung benÃ¶tigt den bestehenden gesicherten SchlÃ¼ssel. Keine neue vollstÃ¤ndige F:-Gesamtsicherung. Diese folgt nach gemeinsamer R6-/Start5-Abnahme.
Abschlusscheckpoint: `checkpoints/RadiWorks-CPU-Abschluss-20261007-224751`. Details und Hashliste: `CHECKPOINT.json`; Schlüssel nur als bestehende Referenz.

# RadiWorks VF2-B: persönliche Browserfelder und optionales Fokusbild

Stand: 2026-10-04T23:03:38.474694+02:00. **100 % des begrenzten VF2-B-Pakets im isolierten Kandidaten.** Keine Liveübernahme oder Aurelia-Integrationsfreigabe.

## Ergebnis
Vorname, Nachname, Geburtsdatum und Ort haben getrennte Felder. Fallbezeichnung, Beschreibung und Fokus bleiben erhalten. Der Nutzer speichert ausdrücklich; Kontextversion und Wirkung auf neue Aufträge werden erklärt. Es werden keine persönlichen Angaben aus bisherigen Dateinamen abgeleitet.

Das optionale Fokusbild akzeptiert PNG/JPEG/WebP bis 5 MB. Vor dem Decoder werden die Abmessungen begrenzt (4096 pro Seite, 16 Mio. Pixel). Der Browser erzeugt ein neues PNG mit längster Seite höchstens 1024. Originaldateiname und eingebettete Originalmetadaten werden nicht gespeichert; der Bildinhalt bleibt gegebenenfalls personenbezogen. Erst beim Fall-Speichern erfolgt die lokale Übertragung. Der Server prüft Bodygrenze, PNG-Chunks/CRC/Raster/zlib und SHA256 vor atomarem Schreiben in die nach festem Prozessscope getrennte Ablage.

Entfernen löst die Referenz nur aus dem neuen Kontext. Frühere Analysen behalten ihre Bildreferenz und ihren damaligen Kontext. Ein isolierter Prozessneustart erhält Kontext, Sitzungen und Bildbytes. Der partielle Kontextpatch verlangt den erwarteten Fallverweis und die Kontextversion; er erhält unberührte Originalwerte auch hinter CopyGuard-Platzhaltern.

Fehlgeschlagene Antworten erhalten den Eingabeentwurf. Fallwechsel während Upload oder Metadatenrequest erzeugen einen kontrollierten Konflikt; verspätete Antworten werden nicht übernommen. Eine unbestätigte Antwort bedeutet nicht, dass der Server sicher nichts gespeichert hat. Die neuen Felder nutzen vorhandene Design-Tokens, ein dunkles Datumsfeld, 44px-Ziele, sichtbaren Tastaturfokus und 320px-Reflow. Keine neue UI-/Decoder-Produktionsabhängigkeit oder externe Bild-/Modellübertragung.

## Frische Nachweise

| Prüfung | Ergebnis |
|---|---|
| Vollständige Engine, ausdrücklich an Kandidat gebunden | **494 bestanden**, 3 bekannte Windows-Symlink-Skips, 0 Fehler; 497 erfasst |
| Kontext und Bilder | 40 Kontextfälle; 23 Bildfälle einschließlich Scopewechsel, beschädigter Ablage, frischer Store-Instanz, Metadaten/Animation/CRC/Raster/Bodygrenze |
| Chrome/Playwright mit Import-Selbstprüfung | **28/28 Abschnitte**, darunter sechs neue VF2-B-Flows; keine JS-Seitenfehler |
| Upload-/Metadatenantwort gegen Fallwechsel | Beide Gegenproben zuerst RED, dann **2/2 GREEN**; Entwurf und Konflikt erhalten |
| Bilddecoder im Browser | Format-, Animations-, Größen- und Fehlerprüfungen bestanden; WebP-Headerkonflikte vor Decoderaufruf abgewiesen |
| JavaScript-Syntax | 18 Dateien bestanden |
| Quellenintegrität | VF2-A 105/105 und GV2 103/103 Elternhashes unverändert; Kandidat 109 Dateien, sechs geändert und vier neu |
| Originalkerne und Referenzen | Fünf Rechen-/Entropiekerne und sechs Aurelia/Modul_Templates/Radi144-Referenzen bytegleich |
| Geschützte Instanzen | 8103–8109 und 8110 auf Loopback, gleiche PIDs und pong; keine Start-/Stop-/Task-/Datenmutation |
| Astra-Review | Beide P2-Races und WebP-Punkt geschlossen; keine weiteren bestätigten Befunde im begrenzten Nachprüfumfang |

Belege unter runtime/rw-vf2b-20261004: engine-final.xml/log, browser-final.log, image-browser-final.log, race-metadata-red/green.log, js-syntax.log, FINAL_VERIFY.json, REVIEW.json, PRODUCT_MANIFEST.json, PRODUCT_DIFF.patch und Desktop-/Mobilbilder. Temporäre Testhomes sind ausgeschlossen.
Die Starlette/httpx-Deprecation bleibt. Kein neuer Linux-, Windows10-Zielgeräte-, Kamera-, Screenreader-, Echtzeit-21min- oder bezahlter Hermes-Modelllauf in diesem Block.

## Korrektur eines früheren Browsernachweises
Der VF2-A-Helfer importierte die installierte Engine statt des Backendkandidaten. Seine 22 grünen Browserabschnitte belegten daher **nicht** den VF2-A-Backendstand. Der damalige korrekt per PYTHONPATH gebundene Engine-Nachweis (468 PASS) bleibt gültig.

Der aktuelle 28er-Gegenlauf bindet an runtime/rw-vf2b-20261004/engine/src und prüft radiworks.main.__file__. Er ersetzt den unzureichenden Browsernachweis. Bericht, Plan und Wiedereinstieg sind korrigiert; der frühere Checkpoint bleibt unverändert historisch.

## Phasen und Grenzen

| Paket | Stand |
|---|---|
| VF2-A Backend-Kontext/ID/Version/Sessionbindung | 100 % des begrenzten Pakets; Regression im gebundenen VF2-B-Gegenlauf mitgeprüft |
| VF2-B Felder/Bildpfad/Browser-/Restartprüfung | **100 % des begrenzten Pakets** |
| VF3 erklärbare heuristische Datenbankvorschläge | 0 % Umsetzung; nächster Block |
| EXP1 separat wählbare Radi144-Heuristik | 0 % Umsetzung |
| Echtzeittrend/Kamera/Recovery/Area/Peggotty/Bedienabnahme | Offen; frühere Belege gelten für ihren jeweiligen Quellstand |
| Kanonische RadiWorks-/Modul_Templates-Synchronisierung | Delta vorbereitet, Übernahme offen |
| Versioniertes Windows10-Paket, bis fünf isolierte Instanzen | Offen; nach Prototyp-/Bedienabnahme |
| Vollständige Governors/Gedächtnis/Aurelia/Module/Configs/Codexhistorien-Sicherung auf F: | Noch nicht erneuert; nach Paketprüfung |
| Aurelia S4.8 | **0 % Freigabe** |

Persönlicher Kontext und Bild ändern im Originalmodus keine EW/Potenz/Level/GV. Direct/Auto/Bild-Broadcasts bleiben ohne separat implementierte Herkunft ungebunden. Kein uneingeschränkter paralleler Browserfallbetrieb innerhalb eines Prozesses und kein medizinischer Wirkungsnachweis.

Historische Bildreferenzen benötigen Assets im echten Datenbackup; Entfernen löscht keine Bilddateien. Bei fehlgeschlagenem Metadatensave kann ein unverknüpftes hochgeladenes Asset bestehen bleiben. Quoten, Archivierung, Berechtigungen und konsistenter Export müssen im Plattformadapter geregelt werden. Der feste lokale Prozessscope ist kein Nachweis von Aurelia-Mehrmandantensicherheit.

**Neue Felder und Bildfunktion sind noch nicht auf 8110 oder 8103–8109 ausgerollt.** Kein kanonischer Quellen-/Template-/F:-Abgleich in diesem Block.

## Modelle und Fortsetzung
Gewählte Leitung Sol6.1/high; Root integrierte UI/API/Store und führte die Tests aus. Tatsächlich verwendet: Luna6/max für Bildhelper und Decoder-Gegenproben, Astra6/medium für unabhängige Grenzprüfung. Keine gemessene Token-/Kostenersparnis; Hermes-Anwendungsroute unverändert.

Nächster Block VF3: erklärbare Wort-/Themen-/Katalogheuristik mit bestätigter Datenbankauswahl. Keine semantische KI/Embeddings oder verdeckte Änderung der Originalanalyse. Orientierung 1–2 Stunden einschließlich Gegenproben, bei Befunden länger; kein Zeitlimit.

## Begrenzter Wiederherstellungspunkt
[Wiederherstellungseinstieg](../../checkpoints/RadiWorks-VF2-B-20261004-230338/RESTORE.md): 109 Produktdateien plus ausgewählte Test-/Review-/Planungsbelege mit SHA256-Verifikation. Keine Laufzeitfälle, Bildablagen, Keys/Tokens, venv oder Testhomes. Lokale Codesicherung; kein Ersatz für die geplante vollständige F:-Sicherung.

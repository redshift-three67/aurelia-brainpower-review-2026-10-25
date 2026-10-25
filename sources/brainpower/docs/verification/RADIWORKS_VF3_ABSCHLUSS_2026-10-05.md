# RadiWorks VF3: erklärbare Katalogvorschläge

Stand: 05.10.2026. **100 % des begrenzten VF3-Pakets im isolierten Kandidaten.** Keine Liveübernahme oder Aurelia-Integrationsfreigabe.

## Ergebnis und Bedienung
Die bestehende Namens-/Gruppensuche bleibt erhalten. „Vorschläge aus Fokus/Themen“ ergänzt eine lokale Wortsuche in Datenbankname, bestehender Gruppe und erlaubten Ratenbezeichnungen. Nur gespeicherter Fokus und ausdrücklich eingegebene Themen werden verwendet; Name/Vorname, Datum, Ort und Bild sind ausgeschlossen.

Jeder Vorschlag erklärt die treffenden Wörter nach Quelle und nennt die Anzahl passender Ratenzeilen. Keine Rohbeispiele oder Wirksamkeitsbewertung. Regel catalog-lexical-v1 normalisiert Unicode, Groß-/Kleinschreibung und Trennzeichen, lässt kurze/numerische/allgemeine Wörter weg und begrenzt auf zwölf unterschiedliche Suchwörter. Mehr Wortabdeckung, danach Name/Gruppe/Inhalt und stabile Namenssortierung bestimmen die Reihenfolge. Wiederholte Raten erhöhen die Abdeckung nicht. Höchstens acht Vorschläge, zusätzlich Gesamtanzahl.

„Datenbank wählen“ prüft Katalog und Fallkontext erneut und wählt exakt die vorgeschlagene .txt-Datei. Namenspräfix-Geschwister werden dadurch nicht mitanalysiert. Auswahl bleibt beim Filtern/Neuladen erhalten. Anfordern/Bestätigen starten keine Analyse oder Broadcast-Freigabe und erhalten bestehende Ergebnisse, Sitzungen und Queue. „Analyse starten“ führt danach einen eigenen bestehenden Auftrag aus.

Fokus/Themen werden durch die Suchhilfe nicht in URLs, Browserpersistenz oder Anwendungslogs abgelegt und nicht an Modelle gesendet. CopyGuard weist gesperrte Suchtexte zurück und schließt gesperrte Datenbanknamen/Ratenzeilen aus. Verspätete Antworten werden bei Themenänderung, manueller Auswahl oder Fallwechsel verworfen. Fehler, Timeout und Quellenänderung erhalten die bisherige Auswahl und die manuelle Suche.

## Quellen- und Kontextvertrag
Read-only POST /database-suggestions und /database-suggestions/confirm verlangen bei aktivem Fall den erwarteten Fallverweis und die Kontextversion. Kontextaufnahme/-gegenprüfung unter bestehender Transaktionssperre; reine Katalogarbeit im Hintergrundthread. Body höchstens 4096 Bytes, Topics/Fokus höchstens 240 Zeichen.

Grenzen: 2048 Datenbanken, 4096 Baumeinträge, 32 Ebenen, 2 MiB pro Datei, 32 MiB insgesamt und 250000 auswählbare Ratenzeilen. Nur reguläre, innerhalb des Katalogs liegende, tatsächlich indexierte Pfade. Doppelte Datenbanknamen, Symlink/Reparsepfade, fehlende/geänderte Inventare und Quotenüberschreitungen führen zu kontrollierten Fehlern statt Teilresultaten. Gepinnte Releases werden einschließlich .rscript/FUNCTION-Dateien begrenzt gelesen, gegen Originalhashes und eine zweite Lesung geprüft. Legacy-Kataloge erhalten konservative Inventar-/Doppellesung.

Der Dateisnapshot-Digest belegt den Stand zum Prüfzeitpunkt. Er ist keine zukünftige Ausführungslease oder Garantie gegen Dateisystem-ABA eines vollberechtigten Angreifers. Der feste lokale Prozessscope ersetzt keine Aurelia-Host-/Tenantautorisierung. Originalanalyse und Entropiepfade bleiben unverändert.

Die Originalkataloge enthalten teilweise nicht UTF8-konforme Bytes. VF3 verwendet dieselbe UTF8-Ersatzregel wie RateRepository, bindet weiter die Originalbytes per Hash und meldet die Anzahl betroffener Datenbanken. Keine automatische Charsetannahme oder Quellenumschreibung. Einzelne Worttreffer an ersetzten Zeichen können fehlen.

## Frische Nachweise

| Prüfung | Ergebnis |
|---|---|
| Vollständige, ausdrücklich gebundene Engine | **551 bestanden**, 3 bekannte Windows-Symlink-Skips, 0 Fehler; 554 erfasst |
| Neue VF3-Prüfungen | **26 Ranking-/Queryfälle und 31 API-/Quellenfälle**; RED/GREEN gegen fehlende Funktionen |
| Tatsächlicher Chrome/Playwright-Gegenlauf | **36/36 Abschnitte**: 28 bestehende und 8 VF3; Import-Selbstprüfung, keine JS-Seitenfehler, Cleanup |
| Browserfälle | Erklärung/keine Nebenwirkung; exakte Auswahl/Filter/Reload/Analyse; Fehler/manuelle Suche; verspätete Themen-/Bestätigungsantwort; Fallwechsel; Katalogdrift/Retry; 320px/Tastatur/44px |
| Reviewkorrektur | Astra-P2 zur Releasevollständigkeit: RED, danach **2/2 GREEN** für Skript/FUNCTION |
| Originalcharset | Eigene RED/GREEN-Gegenprobe; gleiche Ersatzdekodierung mit sichtbarer Warnung |
| Echte Kataloge, nur lesend | 76/123 Datenbanken, 93930/116617 Zeilen, je 13 Ersatzdateien; Quelle und Ranking hier ca. 2,6/3,7 s für Pflanzen/Ruhe, keine Laufzeitgarantie |
| JavaScript-Syntax | **19 Dateien** bestanden |
| Integrität | **109 VF2-B / 105 VF2-A / 103 GV2 Elternhashes** unverändert; Kandidat 114 Dateien, sechs geändert und fünf neu |
| Originalkerne und Referenzen | Fünf Rechen-/Entropiekerne und sechs Aurelia/Modul_Templates/Radi144-Referenzen bytegleich |
| Dauerinstanzen | 8103–8109 und 8110: gleiche Loopback-PIDs und pong; keine Task-/Key-/Home-/Start-/Stopmutation |
| Astra | Releasebefund geschlossen; keine weiteren bestätigten Befunde im begrenzten Review; Laufzeittests durch Root |

Belege unter runtime/rw-vf3-20261004: engine-final.xml/log, api-green.xml/log, lexical-red/green.xml/log, browser-control-red.log, browser-final.log, release-integrity-/encoding-red/green.log, Katalogsummaries, REVIEW.json, FINAL_VERIFY.json, PRODUCT_MANIFEST.json, PRODUCT_DIFF.patch und Desktop-/Mobilbilder. Temporäre Testhomes sind ausgeschlossen.

Erste Diagnose-/Integrationsläufe bleiben nachvollziehbar: Der Browserstart vor vorhandenem Helper war kein Feature-RED. Die echte Control-RED-Probe verwendet den gebundenen Backendkandidaten und die frühere HTML-Datei. Ein API-Test nahm LF statt Windows-CRLF an; eine Bytefixture korrigiert diese Testannahme. Ein alter Persistenztest verglich den Render-Aufruf als Text; er ist an die zusätzliche exakte Dateiauswahl angepasst. Tatsächliche Wiederherstellung im Browser geprüft. Fokusprobe mit echter Tastaturnavigation; nach Reload wartet die Probe auf gespeicherte Fallhydration. Nach der visuellen Kontrolle erhielt das vorhandene Namenssuchfeld die gleichen Theme-/44px-Regeln. Der abschließende 36er-Lauf ist grün.

Starlette/httpx-Deprecation bleibt. Kein neuer Linux-, Windows10-Zielgeräte-, Kamera-, Screenreader-, Echtzeit-21min- oder bezahlter Hermeslauf. Kein pauschaler medizinischer, WCAG- oder Mehrmandantensicherheitsnachweis. Frühere fachliche Freigaben gelten für ihren jeweiligen Quellstand.

## Phasen und Fortsetzung

| Paket | Stand |
|---|---|
| VF2-A/B: Kontext, Felder, Bild | 100 % der begrenzten Pakete; Regression mitgeprüft |
| **VF3: erklärbare Katalogvorschläge** | **100 % des begrenzten Pakets im Kandidaten** |
| EXP1: separat wählbare Radi144-Heuristik | 0 % Umsetzung; nächster Block |
| Trend/Kamera/Recovery/Area/Peggotty/Bedienabnahme | Restpunkte offen; alte Belege nicht pauschal erneuert |
| Kanonische RadiWorks-/Modul_Templates-Synchronisierung | Delta aktualisiert, Übernahme offen |
| Versioniertes Windows10-Paket, bis fünf Instanzen | Offen, nach Prototyp-/Bedienabnahme |
| Vollständige F:-Gesamtsicherung | Noch nicht erneuert, nach Paketprüfung |
| Aurelia S4.8 | **0 % Freigabe** |

Neue VF2B-/VF3-Oberflächen **noch nicht auf 8110 oder 8103–8109 ausgerollt**. Keine kanonischen Modul-/Aureliaquellen verändert. Hermes-Anwendungsrouting/Gedächtnis unverändert. Als Nächstes EXP1: getrennt vergleichbare Radi144-Heuristik unter Erhalt des Originalmodus. Orientierung 1–3 Stunden einschließlich Gegenproben, bei Befunden länger; kein Zeitlimit.

## Modelle und Sicherung
Gewählte Chatleitung Sol6.1/high. Tatsächlich Luna6/max für begrenzte Schnittstellenberatung; Root übernahm und implementierte Helper, API, UI und Tests. Astra6/medium für unabhängigen Review und Nachprüfung. Keine gemessene Token-/Kostenersparnis. Die VF3-Suchfunktion selbst nutzt keine LLM-Aufrufe.

[Lokaler Wiederherstellungseinstieg](../../checkpoints/RadiWorks-VF3-20261005-001954/RESTORE.md): 114 Produktdateien plus ausgewählte Belege/Planung mit SHA256-Readback. Keine Homes, Keys, Bildablagen, venv oder Testtemp. **Codesicherung, kein Ersatz für die geplante vollständige F:-Sicherung.**

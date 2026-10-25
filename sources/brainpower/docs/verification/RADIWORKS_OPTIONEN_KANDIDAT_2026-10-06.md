# RadiWorks – Optionskandidat, 06.10.2026

## Status und Freigabegrenze

O1–O5 sind im isolierten Kandidaten technisch umgesetzt und geprüft. Die persönliche Nutzerabnahme ist offen. Neuer synthetischer Prüfstand: http://127.0.0.1:8112/. Live8103–8109, alter8110/8111, kanonischer RadiWorks-Quellordner, Modul_Templates und Portable5 bleiben auf ihrem bisherigen Stand. Keine Aurelia-Integrationsfreigabe (S4.8=0%).

Produkt: `runtime/rw-options-20261006`, 172 SHA-geprüfte Dateien. Manifest: `e457d2f5864f0711b96b1225d4cae1e3a375752b57b2f00ad3d77def27a7d60e`. Prüfhome: `runtime/rw-options-browser-8112/home`, ausschließlich synthetische Fälle, eigener Katalog und Journalschlüssel. Original-/EXP1-/persönliche Berechnungsalgorithmen bleiben erhalten.

| Paket | Ergebnis | Fortschritt innerhalb des genannten Pakets |
|---|---|---|
| O1 Einstellungen / lokale Abschlussmeldung | Nur unterstützte Einstellungen sichtbar; gespeicherte Altwerte erhalten; validierter atomarer Save; neue Verhaltensoptionen erst nach ausdrücklichem Save aktiviert | 100% technisch |
| O2 Queue / Dauer | Einzelbetrieb1 statt8 ohne Abbruch aktiver Jobs; belegte Original-Delta-Regel; Vorschau mit Driftprüfung und eingefrorener Auftragspolitik | 100% technisch |
| O3 Dynamic Adjustments | Begrenzt0–3 Folgeaufträge, Mindestdauer; eigene journalgesicherte GV-Ziehung nach normalem Abschluss; Entscheidung und tatsächliche Annahme getrennt | 100% technisch |
| O4 Watchlist | 1–100 gewählte Raten des aktiven Falls, seitenübergreifende Auswahl; eigene Vorschau/Start/Stop/Historie und Entropie; keine stillen Broadcasts | 100% technisch |
| O5 EW-Vorbelegung / Auswahlhilfen | Gespeicherter EW-Grenzwert100/1000 nur als Vorbelegung; „Persönliche Heuristik“; zwei unabhängige Auswahlachsen verständlich erklärt | 100% technisch |
| O6 reale Kamera | Synthetische Feedprüfungen vorhanden; neue reale Kameraabnahme fehlt | 0% dieser Hardwareabnahme |
| O7 bestehendes Start5 | Bestehendes Portable5 0.3.0-rc1 unverändert geprüft, fünf isolierte Instanzen und Neustarts | 100% Bestandsprobe |
| O8 Übernahme / Synchronisierung / neue Version | Technische Kandidatenprüfung fertig; Nutzerprobe, Live-/Quell-/Templateübernahme, neues Start5 und Gesamtsicherung offen | 0% Übernahme |

Prozente sind keine Aussage über klinische Wirksamkeit, Gesamtqualität oder Aurelia-Reife.

## Verhalten und Nachweise

837 Engine-/CPU-Tests bestanden, drei bekannte Windows-Linktests übersprungen (840 insgesamt; keine Fehler). 21 JavaScript-Tests bestanden. 19 funktionale synthetische Browserprüfpunkte, darunter alle vier Verfahrens-/Zufalls-Kombinationen, vollständige persönliche CPU-Berechnung, Journal-Watchlist, Idempotenz, Seitenwechsel, Stop, Kontextbindung und mobile390px-Ansicht. Fünf zusätzliche Abschluss-/Wiederanlaufprüfpunkte nach dem letzten Hilfetextabgleich bestanden. Geordneter Prozessneustart bewahrt beide synthetischen Falldateien bytegleich, zeigt Watchlist-Historie wieder an und startet keine Broadcasts erneut. Alle172Produktdateien abschließend verifiziert.

Evidenz unter `runtime/rw-options-20261006/evidence`: `options-verified.xml`, `options-js-final.log`, `options-browser.json`, `options-extra.json`, `options-final-smoke.json`, `final-restart-verified.json` sowie Screenshots. Der vollständige CPU-Lauf erforderte korrekt isolierte Testabhängigkeiten und ein Torch-Threadprofil1. Zuvor fehlerhafte Harness-Konfigurationen wurden korrigiert; sie sind kein bestandener Produktnachweis. Ebenfalls korrigiert: falscher Launcherpfad, Playwright-Top-Level-await und falscher API-Exportname.

Unabhängiger Astra-Grenzreview: vier konkrete Befunde korrigiert und durch gezielte Tests abgesichert: Entscheidung vor tatsächlicher Folgeannahme, gemischte Einstellungssnapshots, fehlendes Watchlist-Join bei Schreibfehler und fehlender Stochastic-Journalcommit vor Ergebnispersistenz. Statischer Nachreview ohne wesentlichen Restbefund im geprüften Umfang. Kein Ersatz für Betreiberabnahme.

Start5-Bestandsprobe: unverändertes ZIP `builds/RadiWorks-Portable5-0.3.0-rc1.zip`, SHA256 `249af06ede3065a70f3c295f6218784313317a0a449033e8e81fc01f0d03772d`; 18.505 Payload-Dateien geprüft. Fünf eigene Prüfports8120–8124: Start/ping, synthetischer Fall, Originalanalyse mit39Raten, geordneter Stop/Neustart, unveränderte Fall-ID und Fallinhalt, kein Broadcast-Replay. Danach alle fünf Prüfprozesse geordnet beendet. Kein neuer Zweit-PC-/Windows-Neustart-/Linux-/Real-Kamera-Nachweis.

Persönliche Matrixscores sind keine Original-EW/GV. Dynamic Adjustments nutzen ausschließlich einen belegten eingefrorenen Original-Fall-GV, keine persönliche neue Zahlenformel. Nicht belegte Auto-/Bild-/Ad-hoc-Aufträge erzeugen dadurch keine Folgejobs. Neue Delta- und Dynamic-Schalter im Prüfkandidaten stehen wieder AUS. Die Watchlist startet nur ausdrücklich; ein Neustart spielt unterbrochene Jobs nicht ab.

## Nutzerprobe und weitere Reihenfolge

Auf8112 mit synthetischen Fällen beide Auswahlachsen und Hilfen, gewählte Watchlist-Raten und Historie, verständliche Einstellungen sowie Broadcast-Vorschau/Abschluss prüfen. Danach Nutzerergebnis abgleichen. Erst bei erfolgreicher Nutzerprobe kontrollierter Fall-/Key-erhaltender Rollout samt vorherigem Checkpoint, Quell-/Modul_Templates-Abgleich, neue separat geprüfte Start5-Version und vollständige Sicherung. Kameraabnahme bleibt separat. Zentrale Datenbankstruktur anschließend besprechen.

Tatsächliche Helfer: GPT-6 Luna/max für Einstellungen/Abschlussmeldung; GPT-6 Astra/medium für unabhängigen Grenzreview. Betreibergewählte Chatleitung GPT-6.1 Sol/high; Hermes-Anwendungsrouting unverändert. Keine gemessene Tokenersparnis.

## Vorgemerkt: A-LAYER – fallbezogene Animationsbilder

Empfehlung, noch keine Implementierungsfreigabe: wenige optionale lokale Bildlayer als separates, gespeichertes Animationsprofil je Fall; Vorschlag höchstens5 normalisierte PNG/JPEG/WebP-Bilder mit begrenzter Größe. Reihenfolge, Transparenz, Vorschau und Entfernen anbieten. Keine Vermischung mit Fokusbild, persönlichem Vektor, Analyseformel oder Entropie. Für neue Broadcasts einen unveränderlichen Profilstand binden; spätere Falländerungen ändern laufende Aufträge nicht. Bei fehlenden Bildern auf bestehende Animation zurückfallen. Reduzierte Bewegung und statische Darstellung unterstützen; keine zusätzliche Blinkanimation. Bestehende Animation als Standard erhalten.

Priorität: nach aktueller Optionsabnahme besprechen, vor späterem Paketupdate bei ausdrücklicher Umsetzung aufnehmen. Stabilität ist durch Größen-/Formatprüfung, isolierte Speicherung, Fall-/Auftragszuordnung, Altfallmigration und Browser-/Neustart-/Reduced-Motion-Tests zu belegen. Ein Bildlayer erweitert die Darstellung; er belegt keine Veränderung von Harmonisierung oder Klientenreaktion.

## Nachkorrektur: Fall speichern, 06.10.2026

Der Betreiberfehler ist als Browserregression reproduziert: neues ungebundenes Formular bei bereits aktivem Serverfall wurde fälschlich als dessen Bearbeitung behandelt und mit „Aktiver Fall hat sich geändert“ gesperrt. Die Oberfläche trennt nun Neuanlage und gebundene Bearbeitung. „Neuen Fall vorbereiten“ leert nur das Formular; erst erfolgreiches Speichern aktiviert den neuen Fall. Vorhandene Fall-ID und Analysesitzungen werden nicht übernommen oder überschrieben. Bei einem tatsächlich geänderten aktiven Fall bleibt die Bearbeitung gesperrt und die Eingabe erhalten.

Wiederherstellung der gespeicherten Auswahl erfolgt lesend nur, wenn sie dem aktuellen Serverfall entspricht. Sonst bleibt die ausdrückliche Auswahl über „Laden“ erforderlich. Späte Antworten überschreiben weder neu eingegebene Felder noch eine vorgemerkte Bildentfernung. Der Geburtstexthinweis wurde an das bereits vorhandene persönliche Verfahren angepasst.

Nachweis: 57 gezielte Titel-/Kontext-/Fokus-/Persistenztests ohne Skip, 21 bestehende JS-Tests sowie finale Syntaxprüfung; sechs isolierte Browserregressionen mit künstlichen API-Antworten und acht Browserprüfungen über echten TCP-Speicher auf eigenem8113. Tatsächlich drei neue Fall-IDs, Neuanlage bei aktivem anderen Fall, Bearbeitung/Neuladen und Originalanalyse geprüft; erste Analysesitzungen nach weiteren Neuanlagen unverändert. Belege: evidence/case-save-regression.xml, case-save-browser.json, case-save-tcp.json und zugehörige Scripts/Logs. Backend-/Analysealgorithmen unverändert; die frühere volle Engine-Prüfung bleibt deren Grundlage. Ein zunächst falscher Analyse-Testselektor wurde im Harness korrigiert.

Nur Frontenddateien im Kandidaten geändert,172Manifestdateien verifiziert. 8112 wird ohne Neustart mit gleichemPID69156 weiterbetrieben; bestehende Benutzerformulare nicht automatisiert geladen/geändert. Der Service-Startbeleg behält seinen vorherigen Digest; der aktualisierte Produkt-/Config-Digest gilt für den nächsten kontrollierten Start. Kein Live-/Quell-/Templates-/Portable-Rollout. Vorherdateien: checkpoints/RadiWorks-CaseSave-20261006-190326.

Beim ersten eigenen8113-Stopp blieb der Prozess nach dem Schließen des Listeners hängen und wurde nach exakter Identitätsprüfung beendet. Windows-Proactor-ConnectionReset10054 protokolliert; Ursache nicht abschließend belegt. Ein erneuter vollständiger TCP-Lauf mit Stackdiagnose endete mit exitClean=true. Keine Shutdown-Codeänderung aus einer Vermutung; diese Auffälligkeit vor Liveübernahme erneut prüfen. Der eigene8113-Testserver ist beendet, Nutzer8112 wurde nicht neu gestartet. Kein allgemeiner Warmstartnachweis.

Aktueller nächster Schritt: erneute Nutzerprobe8112 mit künstlichem Fall. Bildlayerplanung weiterhin nur vorgeschlagen. Tatsächlicher Helfer dieser Korrektur: Luna6/max als begrenzter Quellen-/Vertragsprüfer; kein Astra-Aufruf nötig.

Harness-Isolationsnachtrag: Finale Mock-Probe ersetzt auch /analysis/sessions durch eine leere synthetische Liste. Frühe Mock-Proben ließen die Sitzungsnavigation noch durch und konnten damit den temporären GV-Anzeigestand auf8112 beeinflussen; kein Falldatei-Schreibauftrag daraus. Deshalb kein Anspruch, dass sämtliche flüchtigen Anzeigezustände des Nutzerprozesses unbeeinflusst blieben. Finale sechs Mockprüfungen nach Schließen dieses Harnesspfads erneut bestanden.

## Layoutnachkorrektur – 2026-10-06T20:25:22+02:00

Maßgeblich: [Layoutabgleich](RADIWORKS_LAYOUT_ABGLEICH_2026-10-06.md). Original-GV/AutoAUS bleiben im persönlichen Verfahren sichtbar; Originalstart/Freigabe sind getrennt gesperrt, Rückwechsel ohne neuen Auftrag, Stick-Pad-Folgeschritt Original-only. Alle10Ansichten,10isolierteBrowserchecks,21JS/28Syntaxdateien/41gezielteAPItests und Astra-Deltareview geprüft.172Produktdateien; neuerManifestdigest `615ffb32b98951f60ee206449b755071c2414abb82269b941ae0ee80543c22aa`. Nutzerprobe8112 offen; Dauerinstanzen/Quelle/Templates/Paket unverändert.

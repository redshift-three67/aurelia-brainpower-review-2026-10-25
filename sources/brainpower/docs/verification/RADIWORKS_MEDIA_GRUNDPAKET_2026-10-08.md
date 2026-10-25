# RadiWorks: Audio- und Bildlayer-Grundpaket

Stand 2026-10-08T00:16:47.328025+02:00. Technischer Kandidat `runtime/rw-media-20261007`, 194 Produktdateien; Manifest SHA256 `f5a3c838009ed8f11f41579c91c2a674ff9a8ea9c4fdbce21e43d63a80b45701`. Live8112 bleibt `runtime/rw-performance-v2-20261007`, PID45644 zuletzt frisch geprüft; alle184 manifestierten Baseline-Dateien weiterhin bytegleich. Keine Übernahme in Dauerinstanzen8103–8109, R6, Quellmodul, Modul_Templates oder Start5. Keine neue F:-Gesamtsicherung.

## Implementierter Umfang

| Schritt | Ergebnis | Abnahmegrenze |
| --- | --- | --- |
| AU1 Grundprofile | Original-Ereignistöne, Audio aus,432/528/429,62Hz, neun bestätigte Solfeggio-Stufen mit1–600s und optionaler Wiederholung; kontinuierliches ungepulstes Rosa Rauschen | Phi-/Fibonacci-/Pulsprofile noch offen; keine beliebige Score-zu-Hz-Formel |
| AU2 Browserausgabe | Bewusste Aktivierung, tatsächliche Samplerate, begrenzte Stimmen/Puffer, Rampen, zentraler Stopp, Offline/Hidden/Pagehide/Replay-Grenzen | Digitaler48kHz-Chrome-Test; keine Hör-/DAC-/Schalldruckabnahme |
| AU3 Auftragsbindung | Eigenes versioniertes Fallprofil; Companion-Digest beim zentralen Broadcast-Accept; alte Aufträge unverändert | Kein neuer ContextSnapshot-/BroadcastTarget-Schemawechsel, keine geänderten analytischen Zufallsziehungen |
| BL1 Speichern | Maximal fünf geordnete bereinigte PNG-Referenzen; eigene CAS-Version; nach Fallwechsel/Laden korrekt zugeordnet | Vom analytischen Fokusbild getrennt, Referenzen historischer Jobs bleiben erhalten |
| BL2 Darstellung | Layer im bestehenden Panel; reduced-motion statisch; Desktop1440 und Mobil390px | Begrenzte technische Probe, keine vollständige Barrierefreiheits-Zertifizierung |

## Frische Nachweise

- Backend 162 Tests, persönliche API separat 9 Tests: ohne Fehler/Failures. `evidence/backend-media.xml` und `personal-media.xml`.
-79 Frontendtests bestanden;35 JavaScript-Dateien syntaktisch geprüft. `evidence/frontend-tests.txt`.
- Chrome tatsächliche Fallanlage, fünf Bild-Uploads, Reihenfolge, Speichern/Reload, externer Fall-Metadatenwechsel, eingefrorenes altes Solfeggio-Profil trotz neuem Pinkprofil, ausdrückliche Aktivierung/Stopp.7s kontinuierlicher Pinkworker, finale12PCM-Blöcke,48kHz; keine Seiten-/HTTP-Fehler. `browser-media.json`.
- Leere/601s-Dauer zuerst im Browser reproduziert, danach korrigierbar und nicht speicherbar geprüft. `browser-duration.json`.
-429,62Hz tatsächlicher Oscillatorparameter, Tastatur-Tabfolge, reduced-motion, Offline schließt AudioContext; Rückkehr startet Audio nicht automatisch. `browser-device.json`.
- Eigene Testvorschau8113 beendet. Test-only Shutdownroute wurde vom statischen Catch-all verdeckt (405); ausschließlich anhand Kommandozeile bestätigter eigener PID59660 beendet. Kein sauberer Service-Shutdown behauptet; `browser-cleanup.json`.

## Rosa-Rauschen-Pegel: wesentlicher behobener Befund

Der gelieferte12dB-Crestguard garantiert keine Spitzenfreiheit. Reale Workerprobe stoppte nach4–7Blöcken mit der unveränderten Samplebereichsprüfung. Ein fester Seed reproduziert dies auch im Numeriktest.

Livevariante nutzt einen konstanten Gain aus der Dreiecksungleichung: IFFT-Betrag höchstens B=(2/N)·Summe(1/sqrt(k·fs/N)); nichtnegative Hann-Gewichte ergeben bei50%Überlappung die Summe1. Gain=min(Quellgain,0,95/B). Keine Sample-Clippingfunktion oder adaptive Normalisierung; Spektrum, Phasenfolge und analytische RNG unverändert. Bei48kHz rund23,60dB leiser als der Quellgain. Dies ist im UI erklärt und muss später gehört werden.

61,44s mit konstantem Gain/identischen Seeds geprüft; Geräte8/44,1/48/96/192kHz und Grenzen geprüft. Standard-/Goldenmodus bleibt unverändert:8192Float32-Frames SHA256 `8849e6005ffa1070789a1ddcd1d25bac14c18dd8e41343f97801fab8bb9c0234`. Live ist eine dokumentierte Pegelvariante, keine Behauptung gleicher Sampleamplituden zum Datei-Renderer. Herkunft: `AUDIO_PROVENANCE.json`; Nutzungs-/Lizenzmetadaten vor Weiterverteilung prüfen.

## Review, Bestandsschutz und nächste Schritte

Tatsächliche Helfer: GPT-6 Luna/max (Fallprofil-/Broadcast-Backend), GPT-6 Astra/medium (unabhängiger gezielter Vertrags-/Audio-/UI-Review). Leitung laut Betreiberwahl Sol6.1/high; aktive Runtime nicht aus Defaults bewiesen. Keine gemessene Tokenersparnis. Astra bestätigt fixe Spektralschranke, Dauer-/Fallbindungs-/Timerfixes und Offline-Stopp; letzter gezielter Review ohne verbleibende Befunde. Reviewer hat Root-Laufzeitergebnisse nicht selbst ausgeführt.

Unverändert: Originalanalyse/-broadcast samt Entropie, persönliche Formeln/80.000 Kandidaten und CPU-Worker, bestehende GV-/Auto-Bedienung. Kleine synthetische Tests ersetzen keinen erneuten1382er-Gesamtlauf; wegen unveränderter Formeln/Worker kein weiterer Vollkatalogbenchmark gestartet. Kamera/Windows10/Ubuntu/Mehrinstanz-Hörprobe bleiben gesondert.

Als Nächstes genaue Phi-/Fibonacci-/Pulsdefinition abschließen (Pulsparameterfrage weiterhin offen), gemeinsame Nutzer-/Hörprobe, anschließend R6-Übernahme mit Fall-/Keyerhalt, Quell-/Modul_Templates-Sync und Start5-Prüfung. Danach Gesamtsicherung und Datenbankstruktur-Besprechung. S4.8 bleibt0%Freigabe. Technisches AU/BL-Grundpaket100% des hier begrenzten Umfangs; nicht100% des gesamten Audioplans oder der Produktfreigabe.

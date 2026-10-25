# RadiWorks Audio-Diagnose und vereinfachte Analyseoberfläche

Freigegeben im Chat: Audio prüfen, bestätigte Funktionen erhalten, zusätzlichen Original-/Experimentalvergleich entfernen. Anwendung der Skills systematic-debugging, writing-plans, TDD und verification-before-completion. Isolierte manifestierte Kopie statt Git im fremden Profil-Repository.

- [x] A1 Vorher-Sicherung und überprüfte 198 Produktdateien.
- [x] A2 Regression zuerst RED: obsolete Vergleichsoberfläche fehlt; Original-GV/Auto und persönliche Analyse bleiben vorhanden. Nur Panel, Import, Initialisierung und Sichtbarkeitshook entfernen. Backend und gespeicherte Vergleichsbelege unverändert.
- [x] A3 Audio-Diagnose RED/GREEN: expliziter 432-Hz-Testton für 2 Sekunden, bestehende Gain-/Stimmengrenzen, kein Fall-/Broadcast-/Entropieauftrag. Gleichzeitiges Stapeln verhindern, Audio-Stopp und Seitenwechsel erhalten. Zugeordnete Profile und ausgeschöpfte Einmalfolgen verständlich anzeigen; Aktivierung bedeutet keine bestätigte Tonwiedergabe.
- [x] A4 Node-Tests/Syntax und reale Chrome-WebAudio-/OfflinePCM-Probe im eigenen synthetischen Server auf8113, physisch stumm; keine tatsächliche Hörbarkeit behaupten. Alle vier Analyseauswahlen, Original-/persönliche Bedienelemente, kein Vergleichs-API-Aufruf, Desktop/mobile.
- [x] A5 Manifest, Bericht und Wiederaufnahme. 8112 erst mit separater konsistenter Fallsicherung und bei ruhendem Betrieb oder expliziter Neustartfreigabe übernehmen. R6/Start5 weiterhin nach Benutzerabnahme.

Nachweis: Vorher aktive Broadcasts Profil original, play.binaural.sound=false. Dies erklärt deren Stille, aber die Nutzerprobe mit neuem Einzelton blieb ebenfalls stumm. Ursache der physischen Ausgabe ist weiterhin offen. Gerätezugriff des aktuellen IAB konnte wegen Windows-Sandbox-ACL nicht geprüft werden. Keine Pegelerhöhung auf Verdacht. Luna/max liest Pegelkette unabhängig, keine produktiven Änderungen.

Nutzerprobe: Feste/Solfeggio-Töne hörbar; alle Rauschprofile stumm. Ergänzung A3: nur Rausch-Wiedergabegain .125→2 (+24.08dB), kein adaptiver Gain/Limiter, unveränderter Rauschkern und Pulsplan. Der validierte Chunk-Grenzwert1 und maximal2 Rausch-/8 Gesamtstimmen begrenzen den Gesamtpeak am maximalen Master .2 auf .95. Separate RED/GREEN-Pegelprüfung und Astra/medium-Review. Hörprobe bleibt offen.

8112 nach expliziter Freigabe aktiviert und Datenbestand byte-/SQLite-logisch verifiziert. Abnahmegrenze: Pink-Hörprobe noch offen, keine R6-/Start5-Freigabe.

# RadiWorks Audio- und Bildprofil – bestätigter Umfang und Abnahmevertrag

Stand 2026-10-07. Folgt auf die persönliche Laufzeitkorrektur. Entwicklung ausschließlich im isolierten Kandidaten; Dauerinstanzen, R6, Quellmodul, Modul_Templates und Start5 erst nach gemeinsamer Abnahme aktualisieren.

## Bestätigt

- Feste Einzelfrequenzen: 432 Hz, 528 Hz, 429,62 Hz.
- Feste Folge: 174, 285, 396, 417, 528, 639, 741, 852, 963 Hz. Konfigurierbare Dauer je Stufe; Wiederholung optional. Betreiberantwort ausdrücklich bestätigt.
- Rosa Rauschen auf Grundlage des geprüften Generator-Numerikkerns. Phi-/Fibonacci-Profile getrennt und mit expliziter Index-/Hz-/Dauerdefinition. Keine neue automatische GV/EW/Matrixscore-zu-Hz-Formel.
- Bis zu fünf fallbezogene Animationsbilder speichern. Vom analytischen Fokusbild getrennt.
- Originale Analyse-, Entropie- und Broadcast-Ziehungen bleiben unverändert. Zusätzlicher Rauschseed gehört ausschließlich zum Audio.

## Abgrenzung und Implementierungsvertrag

1. Eigene versionierte Präsentationsprofile pro stabiler Fall-ID und Scope. Audioprofil, Dauer, Wiederholung und geordnete Bildreferenzen getrennt vom bestehenden strengen ContextSnapshot/BroadcastTarget-Schema1.
2. Neue Broadcasts erhalten einen unveränderlichen Profilstand mit Digest und Bezug zum BroadcastTarget. Änderungen am Fall ändern keine laufenden oder historischen Aufträge. Alle Annahmepfade prüfen: direkter Broadcast, Ratenliste, Auto, Bild und Prüfdraft.
3. Darstellung wird im Browser erzeugt. Der Server bleibt für Broadcast-Laufzeit/Belege maßgeblich. Audio startet ausschließlich nach bewusster Benutzeraktivierung; Rückkehr/Neustart setzt nicht automatisch Audio fort. Master-Stopp beendet alle Stimmen dieses Browsers, nicht den Broadcast.
4. Frequenzen gegen tatsächliche AudioContext-Samplerate prüfen. Begrenzter Summenpegel, Stimmenzahl und sanfte Anfangs-/Endrampen. Endliche Sequenzplanung oder begrenzte vorgerenderte Rauschabschnitte; kein minutenlanger Vollpuffer im UI-Thread.
5. Phi als dokumentierte Float64-Konstante/formelgerechte Berechnung. Digitale Rechenpräzision ist keine analoge DAC-Clock-/Wirkungszusage. Mono/Dual-Mono nicht als binaural bezeichnen.
6. Bilder einzeln lokal prüfen, verkleinern und als PNG ohne ursprüngliche Dateinamen/Metadaten speichern. Maximal5; Hashreferenzen statt personenbezogener Pfade. Bestehende Bildreferenzen historischer Jobs erhalten. Reduced-motion-Darstellung statisch; bestehende Animation bleibt nutzbar.
7. Keine neue Produktions-Node-/React-/Auth-Abhängigkeit. Quellherkunft/Versionsmetadaten des bereitgestellten Generators im Paket nennen. Linux-Renderer/Aurelia-Adapter später separat prüfen; Windows-Prüfung ersetzt keine Linux-Abnahme.

## Noch konkret zu entscheiden

Pulsprofil: vorgeschlagen zuerst weiche frei wählbare Pulsrate/Tiefe (1 Hz/50 % Vorbelegung), Phi-/Fibonacci-Stufen getrennt danach. Betreiberfrage pending; ohne Antwort keine Pulsparametrisierung als bestätigt behaupten. Feste Audiofolge ist hiervon unabhängig freigegeben.

## Abnahmeschritte

| Schritt | Nachweis | Stand |
| --- | --- | --- |
| AU1 | Numerik/Profile/Frequenzgrenzen und Stufendauer | Grundprofile geprüft; Phi/Fibonacci/Pulsdefinition offen |
| AU2 | Benutzeraktivierung, Fade, Summenpegel, Stop, Geräte-/Samplerate-Grenzen | Technische Chromeprobe bestanden; reale Hörprobe offen |
| AU3 | Unveränderliche Fall-/Auftragsbindung und RNG-Gleichheit Audio an/aus | Begrenztes Grundpaket technisch bestanden |
| BL1 | Fünf bereinigte Bilder, Speichern/Laden/Entfernen mit Versionsschutz | Technische Grundpaketprüfung bestanden; Nutzerprobe offen |
| BL2 | Darstellung, reduced-motion, keine Änderung alter Aufträge | Technische Grundpaketprüfung bestanden; Nutzerprobe offen |
| R6 | Vier-Modi-/Browser-/Mehrinstanzregression und Betreiberprobe | gesperrt bis AU/BL-Abnahme |
| START5 | Versioniertes Paket, fünf isolierte Starts, Fall-/Keyerhalt, Wiederanlauf, Hashmanifest | folgt nach R6 |

Referenzbefunde: docs/verification/RADIWORKS_AUDIO_PHI_REVIEW_2026-10-07.md. Dieses Dokument ist ein präziser Arbeitsvertrag, kein Nachweis fertiger Funktionen.
Technischer Nachweis: docs/verification/RADIWORKS_MEDIA_GRUNDPAKET_2026-10-08.md. Kandidat bleibt isoliert; keine R6-/Start5-Freigabe.

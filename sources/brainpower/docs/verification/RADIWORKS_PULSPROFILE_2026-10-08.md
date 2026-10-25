# RadiWorks: gekoppelte Pulsprofile und gemeinsame Medien-Abnahme

Stand 2026-10-08T01:08:00.859839+02:00. 8112 nutzt jetzt `runtime/rw-pulse-20261008`; zuletzt frisch geprüft PID4536, vollständiger Katalog123 Datenbanken, identischer Home/Scope/Schlüsselpfad. Produkt198 Dateien, Manifest SHA256 `965691dc3c7c98eb19c9decfdcf87fd0ef8dc48557f103ef594bae4fa0457384`. Die Bereitstellung ist eine Abnahmevorschau, keine R6- oder Aurelia-Integrationsfreigabe.

## Umgesetzt

| Phase/Schritt | Technischer Stand | Noch erforderlich |
| --- | --- | --- |
| Persönliche Laufzeit | bestätigter CPU-Pfad erhalten; Formeln und80.000 Kandidaten unverändert | Nutzerprobe im Gesamtkandidaten; Vollkatalogbenchmark nicht unnötig wiederholt |
| AU1 feste Profile | Original-Ereignistöne,432/528/429,62Hz, bestätigte neun Solfeggiofrequenzen; Basisdauer und Wiederholung | Hörprobe |
| AU1-P/P1–P7 |100% des begrenzten technischen Pulsprofil-Pakets | Nutzer-/Hörabnahme |
| AU2/AU3 | bewusste Browseraktivierung, tatsächliche Samplerate, Fades, begrenzte PCM-Puffer/Stimmen, Stop und immutable Companion | externe Geräte-/Ubuntu-/Mehrinstanz-Hörprüfung getrennt |
| BL1/BL2 | fünf geordnete bereinigte Animationsbilder je Fall, speichern/laden, frozen Jobprofil, reduced-motion | Nutzerprobe |
| R6/Quellmodul/Modul_Templates/Start5 | keine Übernahme in diesem Schritt | erst nach gemeinsamer Abnahme |
| S4.8 |0% Integrationsfreigabe | Host-/Mandanten-/Betriebsabnahme separat |

Drei neue Profile: gleichmäßiger Puls1Hz; Phi mit phi=(1+sqrt(5))/2, Faktoren phi^k für k0..4 und Rate1*FaktorHz; Fibonacci mit Faktoren1,2,3,5,8,13 und Rate0,5*FaktorHz. Bei Phi/Fibonacci multipliziert derselbe Faktor Pulsrate **und** Abschnittsdauer. Basis30s ergibt489,787137637s bzw.960s. Grenzen1–600/87/46s Basis schützen jeden Abschnitt vor mehr als600s. Modulationstiefe0–100%, initial50%; cosinusförmige Amplitudenhüllkurve, kein zusätzlicher Analyse-/Score-zu-Hz-Algorithmus. Darstellung ist technische Audioausgabe, keine gemessene Klientenreaktion.

Jeder Abschnitt wird einmal auf tatsächliche Samplerate quantisiert. Aufsummierte Phase läuft an Abschnitts- und Wiederholungsgrenzen kontinuierlich. Worker-Ready-Latenz und tatsächlich geplante Startzeit gehen in die Pulsposition ein; späte Aktivierung spielt nicht nach. Einmalfolge endet bei ihrer quantisierten Dauer, Repeat spätestens mit Broadcast. Maximal86400s;32768Frames je Block, höchstens zwei vorgeplante Blöcke und zwei Rauschworker. Bestehende Start-/Endfades und feste mathematische Pink-Pegelbegrenzung bleiben erhalten. Bei ratewechseln kann die Ableitung der Hüllkurve springen; keine C1-Glättung behauptet.

Neue IDs `pink-pulse-v1`, `pink-phi-v1`, `pink-fibonacci-v1` verwenden Profil-Schema2 mit `modulationDepthPercent`. Legacy-Schema1 bleibt mit exakt altem Feldsatz/Digest; neue Feldangabe bei alten IDs wird auch als null abgelehnt. Companion-Beleg bleibt Schema1 und friert das vollständige jeweilige Profil ein. Bereits bestehende Profile/Aufträge werden nicht umgeschrieben. Keine Änderungen an Original-EW/GV, persönlicher Heuristik, CPU-Worker oder analytischer Entropie. Gespeicherte Servervorgabe wird in der bereits vereinfachten Zufallsauswahl explizit vorbelegt; kein zusätzlicher 'Einstellung(Server)'-Wahlpunkt.

## Ausgeführte Nachweise

-168 gezielte Backendtests einschließlich Original-Java-Goldparität, Auto/Broadcast/Entropietrennung, Bild-/Profil-/Scope/CAS/Receipt-Verträge; separat9 persönliche APItests. Keine Fehler/Failures/Skips.
-93 Frontendtests;36 JavaScript-Produktdateien syntaktisch geprüft. Neue Tests zuerst RED, danach GREEN. Echte Nodeworker: ungepulste PCM bytegleich, pulsende PCM exakt gegen Float32(reference*gain), kontinuierlicher Phi-Wiederholungsübergang und abgelehnte Positionssprünge.
- Vollständige Standardfolgen bei48kHz: Phi23.509.783Frames/489,787145833s quantisiert; Fibonacci46.080.000Frames/960s. Jedes Sample endlich und begrenzt; nach Einmalende Gain0. Digital beschleunigt gerechnet, kein16-minütiger realer Hörlauf.
- Chrome: tatsächliche fünf Bild-Uploads/Reihenfolge/Save/Reload/externer Fallwechsel, immutable alter Solfeggio-Receipt nach Profiländerung; echte feste und ungepulste Ausgabe. Alle drei Pulsprofile jeweils6s,48kHz, je10PCM-Blöcke; keine JS-/HTTP-/Workerfehler. Ungültige Basis/Depth verhindert Speicherung, V2 Save/Reload und V1-Rückkehr ohne Zusatzfeld. Final1440/390px ohne Seitenüberlauf; Screenshots visuell geprüft.
- Browserbefund behoben: `.control` überlagerte `hidden`; Pulsdepth nun nur bei Pulsprofilen sichtbar. Vorschautabelle mit klar getrennten Spalten. Höreindruck, DAC-/Schalldruckwerte und vollständige Barrierefreiheit nicht daraus abgeleitet.
- Ein persönlicher Testlauf startete wegen falschem relativen PYTHONPATH gegen die installierte alte Engine und scheiterte an fehlendem `AppState.personal`; danach expliziter Kandidatenimport geprüft und9 Tests erfolgreich wiederholt. Fehlerlauf in `personal-wrong-path.txt` erhalten. Keine Produktionskorrektur aufgrund dieses falschen Imports.

## Betrieb und Sicherung

Vorbereitstellungssicherung `checkpoints/RadiWorks-Pulsprofile-Vorbereitstellung-20261008-010201/CHECKPOINT.json`:556 hashgeprüfte Dateien, zwei konsistente SQLite-Kopien, keine Schlüsselkopie. Bekannte gesperrte `.engine.lock`-Dateien und volatile Serviceprotokolle/-zustände ausdrücklich ausgeschlossen; vor Sicherung keine aktiven Broadcasts/Auto/persönlichen Aufträge. Die Sicherung enthält lokale Falldaten und gehört nicht in ein Verteilungspaket.

Eigener8112-Dienst sauber über Stopmarker beendet und datenwahrend gestartet; reine Tabellenabstandskorrektur ebenfalls kontrolliert und mit neuem Manifest. Finale352 statische Home-Dateien und Inhalte beider SQLite-Datenbanken unverändert. Alte184 CPU-Baseline-Produktdateien unverändert. Neuer Browserstand liefert geprüfte Produktbytes. Eigene synthetische8113-Vorschau über korrekt vor dem Catch-all eingehängte Test-only Stoproute beendet; diese Route gehört nicht zum Produkt. Dauerinstanzen8103–8109 nicht geändert.

Tatsächliche Helfer: GPT-6 Luna/max für Backend; GPT-6 Astra/medium für Plan- und Implementierungsreview. Unabhängiger enger Review ohne belegte materielle Restfehler; Reviewer hat Root-Testläufe nicht selbst ausgeführt und erteilt keine Produktfreigabe. Leitung gemäß Betreiberwahl Sol6.1/high; keine aus Defaults abgeleitete Runtimebehauptung oder gemessene Tokenersparnis. Audio-Provenienz und Livepegelvariante siehe `AUDIO_PROVENANCE.json` und vorherigen Medienbericht.

## Nächster freigegebener Ablauf

8112 Strg+F5, gespeicherten Testfall laden. Unter Fälle Audio/Animationsbilder wählen und **Medienprofil speichern**; erst danach neuen Broadcast starten. Audio unter Broadcast ausdrücklich aktivieren. Leiser beginnen; Lautstärke, Pulswechsel, Stopp und Bilddarstellung subjektiv prüfen. Alte Jobs behalten den alten Medienstand. Basisdauer regelt Stufenlängen, Broadcastdauer begrenzt die ganze Ausgabe.

Nach erfolgreicher gemeinsamer Abnahme: R6 mit Fall-/Keyerhalt, Quellmodul und Modul_Templates synchronisieren, versioniertes Start5 mit fünf isolierten Instanzen funktional prüfen/bereitstellen. Danach volle Projekt-/Konfigurationssicherung aufF: und Datenbankstruktur-Besprechung. Kamera/Ubuntu/Windows-Endabnahme und optionale Hardwaregrenzen bleiben getrennte Gates.

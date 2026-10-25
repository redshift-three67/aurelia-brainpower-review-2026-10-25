# RadiWorks Grundpaket – geprüfter Kandidat

Stand: 2026-10-06T15:30:47+02:00. Betreiberfreigabe zur Umsetzung M1–M6 liegt vor. M1–M4 und die technischen M5-Prüfungen sind abgeschlossen. Persönliche Nutzerabnahme und M6-Übernahme sind offen; keine Aurelia-S4.8-Freigabe.

## Funktionsumfang

| Bereich | Umsetzung und Grenze |
|---|---|
| Zwei getrennte Auswahlen | Original AetherOne / persönliche Radi144-Heuristik und unabhängig reproduzierbar / stochastisch. Original bleibt Standard. Umschalten verändert keine angenommenen Aufträge. |
| Falltitel | Kontexttitel aus Vorname, Nachname, Datum, ausdrücklich aktivem Ort und Fokus; neutrale stabile Fall-ID als Dateibezug. Alte manuelle Titel werden nicht still umbenannt. |
| Auftragsbezug BC1 | Direkter, Draft-, Auto-, Bild- und persönlicher Broadcast speichern ihren unveränderlichen Kontext und belegte Quelle. Keine neue persönliche Zahlenformel im Broadcast. Persönliche Zeilen werden mit Auftrags-ID und eindeutigem Eingabeindex gebunden. |
| Zufallsfolgen | Eigene Generatoren je neuem Auftrag, eigene dauerhafte Journale für stochastische Aufträge. Verwendete Quelle wird angegeben; OS-Fallback ist keine externe Hardware-Entropie. Fehlgeschlagene externe Abrufe erhalten die geprüfte 60-Sekunden-Pause. |
| Persönliche Analyse | Versionierte vorhandene CPU-Heuristik, vollständiger gewählter Einzelkatalog bis 4096 Raten, Berechnung in 21er-Blöcken, globale Sortierung erst nach vollständigem Abschluss. Größere Kataloge werden ausdrücklich abgewiesen, nicht gekürzt; Original bleibt dafür verfügbar. |
| Zahlen-/Kontextgrenze | Vorname, Geburtsdatum, ausdrücklich gewählter Geburtsort und bestehende wörtliche Fokusregeln nach EXP1-Vertrag. Nachname, Wohnort und Bild bleiben Auftragskontext ohne neue Formel. Seed 0 erhält den bestehenden EXP1-Vergleich. |
| Ergebnisanzeige | Persönliche Matrixscores/Intensitäten getrennt von Original EW/GV. Eigene paginierte Auftragshistorie, Status, expliziter Abbruch und Wiederanlauf ohne automatische Neuberechnung. |
| Prozessbetrieb | Persönliche Analyse und EXP1 teilen pro Instanz einen CPU-Ausführungsslot. Abschaltung wartet auf eigene Prozesse/Worker, hält Laufzeit-Lease bis zum Ende und verschluckt Persistenz-/Prozessfehler nicht. Kein zentraler Server-Quota-Nachweis. |

Original, bestätigte EXP1-Vergleiche, manuelle Legacy-Fälle und bestehende GV-/Stick-Pad-/Dock-Funktionen sind weiterhin Gegenstand der Regressionstests. Berechnete Matrix-/Zufallswerte sind heuristische Softwarewerte, kein Nachweis einer gemessenen Klientenreaktion.

## Verifikation am endgültigen Produktstand

Kandidat: `runtime/rw-basepackage-20261006`; 159 manifestierte Produktdateien. Manifest-SHA-256: `5879ddb9c4980a6440a1b43593f6607da6753f1029bfe5ae4a2e73b0d5853102`.

| Prüfung | Ergebnis |
|---|---|
| Engine-Gesamtlauf mit CPU-Abhängigkeiten | 814 Tests: 811 bestanden, 3 Windows-Symlink-Privilegien-Skips, 0 Fehler/Fehlschläge; 114,296 s |
| JavaScript | Alle Produkt-JS-Dateien Syntax geprüft; 11 fokussierte Tests bestanden |
| Sichtbarer Browserlauf | 12 Prüfungen bestanden: alle vier Kombinationen, echte CPU für 24 synthetische Raten, zweite Seite, Kontextbearbeitung/alte Sitzung, Historie, Abbruch, ausgewählter Broadcast, 390-px-Ansicht, keine JS-Fehler |
| Echter Prozessneustart auf 8111 | Zwei Original-Sitzungen, drei persönliche Aufträge und Falldatei-Hashes unverändert; kein automatischer Broadcast-Replay |
| Browser nach Neustart | Fall über aktuelle Liste geladen, zwei fertige und ein abgebrochener persönlicher Auftrag unverändert sichtbar; keine neuen Aufträge |
| Ausgangsprodukt/Liveports | Alle 131 C23-Produktdateien unverändert; sieben Ping-Antworten 8103–8109 mit HTTP 200. Keine Änderung an ihren Homes, Tasks, Fällen oder Schlüsseln durch diesen Block |

Die stochastischen Browserprüfungen verwenden einen ausdrücklich synthetischen Ganzzahlen-Feed, der den Webcam-Eingang testet; das ist kein realer Kameralanglauf. Windows-CPU-Profil lokal geprüft; kein neuer Linux-, Hardware-, Warmstart- oder Zweit-PC-Nachweis. Die bekannte Starlette/httpx-Deprecation-Warnung bleibt bestehen.

Testharness-Korrekturen: temporäre opaque Fallreferenzen gelten pro Prozess und werden beim Wiederanlauf aus der Liste erneuert; die dauerhafte Fall-ID bleibt gleich. Ein erster Browser-Laden-Selektor hatte die falsche Groß-/Kleinschreibung des zugänglichen Namens. Beide Testfehler wurden getrennt aufgeklärt; dafür wurde kein Produktverhalten geändert.

Nachweise im Kandidaten unter `evidence`: `m5-full-final.xml/log`, `m5-node-final.log`, `m5-browser.json`, `m5-browser-final.log`, `m5-personal-desktop.png`, `m5-personal-mobile.png`, `m5-restart.json`, `m5-restart-browser.json/log`, `m5-final-source-live.json`. RED/GREEN- und fokussierte Fehlerpfadbelege bleiben ebenfalls erhalten.

## Abnahme und Übernahme

Der synthetische Prüfstand läuft auf **http://127.0.0.1:8111/** mit eigener Home-/Scope-/Schlüsselumgebung. 8103–8109 laufen unverändert mit C23; 8110 wurde nicht umgestellt. 8111 ist ein Entwicklungsprüfdienst, keine Windows-Daueraufgabe oder Portable5-Aktualisierung. Dort ausschließlich künstliche Fälle verwenden.

Für die Betreiberabnahme: Kontextfall anlegen/laden, beide Verfahrensauswahlen und beide Zufallsmodi prüfen, persönliche Historie/Seiten ansehen und einen ausgewählten persönlichen Broadcast prüfen. Auf dem Prüfstand stehen ein synthetischer Katalog und gespeicherte Beispielsitzungen bereit. Keine reale Kamera für diesen Abnahmeschritt erforderlich; bei leerem Feed wird die tatsächlich verwendete Fallbackquelle ausgewiesen.

Danach M6: kanonische Quelle und Modul_Templates-Verträge/versionierte Referenzen synchronisieren, geprüfte Übernahme/Portable5-Version und zeitgestempelte Sicherung. Ein Daten-Rollback darf neue persönliche Aufträge nicht blind mit alten Lesern öffnen. Original- und persönliche Auftrags-/Score-/Zufallsverträge müssen in den Referenzen getrennt bleiben. Optionale Einstellungen, TXT-Nutzerimport und zentrale Datenbankstruktur werden anschließend separat entschieden. Keine neue optional-numerische Broadcastformel, kein Ego Cleaner und keine ungeprüfte Algorithmusersetzung.

## Phasenstand

| Phase | Stand des abgegrenzten Pakets |
|---|---|
| M1 Sicherung/Baseline | 100 % |
| M2 Falltitel/BC1 | 100 % technisch |
| M3 Auftragsentropie | 100 % technisch |
| M4 persönlicher Vollweg | 100 % technisch innerhalb der dokumentierten Grenzen |
| M5 Vier-Modi-Abnahme | Technische Prüfungen 100 %; Nutzerabnahme offen |
| M6 Quell-/Template-/Portable-Sync | 0 %, nach Kandidatenabnahme |
| Aurelia S4.8 | 0 %, keine Integrationsfreigabe |

Tatsächlich eingesetzte Helfer: GPT-6 Luna/max für begrenzte Backend-/Test-/Lifecycle-Arbeit und GPT-6 Astra/medium für unabhängige Identitäts-/Auftrags-/CPU-Fehlerpfadprüfung. Root integriert und prüft. Betreibergewählte Chatleitung GPT-6.1 Sol/high; daraus folgt kein technisch ausgelesener Runtime- oder Hermes-Routingnachweis. Astra-Nachprüfung der zuletzt korrigierten Poll-/Cleanup-Grenze ohne weiteren konkreten Befund; keine umfassende Modell-Abnahme oder Betreiberfreigabe. Keine gemessene Tokenkostenersparnis behauptet.

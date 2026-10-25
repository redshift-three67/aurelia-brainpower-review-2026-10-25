# RadiWorks – UX-/Katalogkorrekturen für Betreiberabnahme

Stand: 2026-10-06T21:47:15.686175+02:00. Freigabe: „OK, setze die Korrekturen um, dann prüfe ich die 8112 nochmals“.

8112 läuft aus runtime/rw-ux-20261006 mit 123 Datenbanken des unveränderlichen Release e33ea136d8ea448fada7524757385ee4 (126 Katalogdateien). Produktmanifest: 174 Dateien, SHA-256 9f7841c84ca7f8122efe5ebb9c9ddb353bf83802d878c358d06d4731d5bc362e. Home, Schlüsselpfad und Scope gegenüber vorher unverändert. Alte synthetische Katalogdateien und historische Sitzungen erhalten.

| Phase/Schritt | Stand | Nächster Schritt |
| --- | --- | --- |
| R3 – freigegebene Korrekturen | 100 % dieses begrenzten Pakets | UX01–06 / DS01 technisch umgesetzt und geprüft. |
| R4 – Vollkatalog / Wiederanlauf | 100 % technisch | Erhaltene Fälle, Historien, Aufträge und Schlüssel nachgewiesen. |
| R5 – Betreiberabnahme8112 | Offen | Strg+F5, Fallanlage/-laden, Katalogsuche und beide Verfahren prüfen. |
| R6 – Dauerinstanzen / Quellordner / Modul_Templates / Start5 | Keine Übernahme | Separat nach erfolgreicher Betreiberabnahme. |
| S4.8 – Aurelia-Integrationsfreigabe | 0 % – keine Freigabe | Weitere Host-/Daten-/Rechteverträge und Produktgates getrennt. |

Prozentwerte gelten für dieses Korrekturpaket, nicht für die gesamte Plattformreife.

## Änderungen

1. Additive /catalogs-Antwort trennt stabile technische Auswahl-IDs und CopyGuard-sichere Namen. Präfix-ID entspricht der bisherigen Namensauswahl; Exakt-ID genau einer TXT-Datei. Legacy /databases, Rohname-/Gruppen-/Dateiauswahl und JavaHashMap-Reihenfolge erhalten. Geschützter Name ist manuell auswählbar (149 Raten). Geschützte Namen bleiben wie zuvor aus automatischen Wortvorschlägen ausgeschlossen; CopyGuard nicht umgangen.
2. Analyse, Stick-Pad, Fokusvorschlagsbestätigung und Historienanzeigen verwenden IDs für Auswahl, Labels für Anzeige und Zwischenablage. Gespeicherte eindeutige Legacy-Namen und neue IDs werden wiederhergestellt. Original-/Personal-/EXP1-Algorithmen unverändert.
3. Lokales Frontend verweigert fremde API-/WS-Origins und URL-Zugangsdaten vor Verbindungsaufbau. Relative Pfade auf derselben Origin bleiben möglich. Spätere abweichende Aurelia-Adapterziele benötigen eine ausdrückliche vertrauenswürdige Konfiguration; freie URL-Parameter sind keine Adapterfreigabe. Backendprüfungen erhalten.
4. Broadcast-Dock scrollt verdeckten Tastaturfokus in den sichtbaren Bereich; Tabs bleiben auch bei 200 % Text intern scrollbar. Dockgröße, Queue und Berechnung unverändert.
5. Port, Prüfstand, Kataloganzahl/-release sichtbar; ergänzende sechs Schritte führen vom Fall zur bewussten virtuellen Broadcast-Freigabe. Expertenaktionen, Original-GV/Auto und getrennte persönliche Scores erhalten. Prüfentwurf/Aktionen verständlicher erklärt. Aurelia-Zusammenarbeit als geplant markiert; Über & Quellen erläutert Herkunft, Verfahren und Grenzen. Bestehende lokale Schrift-Fallbacks und Paletten erhalten.

## Verifikation

| Prüfung | Ergebnis |
| --- | --- |
| Vollständige Engine/CPU-Suite mit vorgesehenem Ein-Thread-Testprofil | 842 bestanden; 3 Windows-Symlink-Skips; 1 bekannte TestClient-Abkündigungswarnung. |
| JavaScript | 26 bestanden. |
| Alle123 Kataloge | 246/246 Präfix-/Exaktvergleiche haben identische geordnete Raten; alle nichtleer. |
| Originalanalyse Legacy/ID | Gleicher Seed ergibt exakt gleiche Ergebniswerte für Präfix und Exaktdatei. |
| Eigener8114-Browser | 13 Prüfpunkte: Vollkatalog, künstlicher Fall, Suche/Gruppen, Fokusbestätigung, Original seeded/stochastic, echte persönliche CPU seeded/stochastic mit vollständigen39Raten, Original-GV/21er-Runde, keine automatische Broadcast-Erzeugung, Hilfe, alle10Ansichten bei390px, keineJS-Fehler. |
| Dock / 200 % Text | Vorher verdeckte Watchlist-Knöpfe jetzt sichtbar; Dokument1265px bei1280px Fenster. |
| Tatsächlich aktivierter8112 | 6 schreibfreie Browserpunkte: Vollkatalog, geschützter Name, Legacy→ID und ID-Wiederladen, Original-GV/Personal-Gating/AutoAUS, Dock/Text; keineJS-Fehler. |
|8112-Datenerhalt | Fall-/Draft-/Watchlist-/Vergleichsquelldateien bytegleich; sechs persönliche SQL-Aufträge und Vergleichstabelle inhaltlich gleich; beide integrity_check=ok, Schlüsselhash gleich, Scope gleich; AutoAUS/Queueleer/keinReplay. |
| Dauerinstanzen8103–8109 | 7/7 erreichbar; 131/131 bestätigteC23-Produktdateien manifestgleich; keinRollout. |

Rote Regressionen belegten fehlende Katalogroute, unbekannten ID-Präfix-Decoy, fremde API-/WS-Ziele und Dock/Textprobleme. Erste Gesamtläufe enthielten eigene Testprofilfehler: global gesetzte Produktions-CPU-Konfiguration machte den absichtlichen „CPU fehlt“-Test ungültig; danach fehlte die Ein-Thread-Vorgabe. Nur Prüfumgebung korrigiert. Die veraltete Restore-Assertion wurde für Legacy→ID aktualisiert; Browserassert prüft tatsächlichen GV-Knopf statt Fieldset. Fehlversuche bleiben als Belege erhalten und zählen nicht als erfolgreiche Produktprüfung.

## Sicherung / Wiederanlauf

Vorhersicherung checkpoints/RadiWorks-UX-Korrekturen-20261006-210705:174Dateien mit Hash-/Bytevergleich. Konsistente Datensicherung nach sauberem8112-Stopp: C:\Users\Hubert111\Documents\Brainpower\checkpoints\RadiWorks-8112-Vollkatalog-20261006-214301,33Home-Dateien, SQLite-Prüfung und RESTORE_MANIFEST.json. Vorherige/neue Konfiguration dabei. Fernet-Schlüssel nicht erneut kopiert; bestehender Pfad erhalten. Kein neuer F:-Gesamt-/Warmstartnachweis.

Nur eigener8112 nach Leerlaufprüfung geordnet neu gestartet. Fälle und Aufträge nicht über alte Sicherungen zurückgesetzt. EigenerTestserver8114 anschließend sauber beendet;8112 bleibt aktiv. Historischer Startdigest des vorherigen Prozesses nicht verändert.

Belege in runtime/rw-ux-20261006/evidence: engine-cpu-profile-verified.txt, js-final.txt, all-catalog-selector-equality.json, ux-full-catalog-browser.json, ux-focus-text-final.txt, actual-8112-browser-smoke.json, 8112-before-restart.json, 8112-after-restart.json, 8112-activation.json, restart-backup.json, live-preservation.json, 8114-clean-stop.json.

## Offene Grenzen / Modelle

Kein vollständiger WCAG-/DSGVO-/regulatorischer Nachweis. Verantwortlichen-/Zweck-/Rechteangaben, Lösch-/Export-/Aufbewahrung, produktive Tenant-/Abo-/Datenarchitektur sowie weitere reale Assistenztechnik-/Kamera-/Linux-/Warmstartprüfungen bleiben getrennt. Keine semantische KI-Suche, neue Formeln, EgoCleaner oder Animationslayer eingeführt. Bereits bestätigte Algorithmen und eingefrorene Auftragskontexte bleiben Grundlage.

Beteiligt: Root gemäß BetreiberwahlSol6.1/high; Luna6/max für begrenzte Katalog-Backendarbeit; Astra6/medium für unabhängigen Grenzreview. Aktive Root-Einstellung nicht aus Defaults abgeleitet. Keine gemessene Tokenersparnis; Hermes-Anwendungsroute unverändert. Astra fand keinen neuen schweren Codebefund; seine offenen Testprofil-/Restore-Nachweise sind final geklärt. Modellreview erteilt keine Produktfreigabe.

Die automatische Freigabeprüfung lehnte das pauschale Abhaken sämtlicher Planpunkte ab, weil dadurch offene Abnahmen falsch als erledigt erscheinen könnten. Sichere Alternative: explizite Nachweise und diese getrennte Phasentabelle; R5/R6/S4.8 bleiben offen. Kein technischer Schritt dadurch blockiert.

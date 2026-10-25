# RadiWorks – Vier-Modi-Review und persönliche Ergebnissicht

Stand: 2026-10-06T22:50:42.021239+02:00. Betreiber meldet funktionierende Originalanalysen seeded/stochastic und persönliche Fall-/Broadcastabläufe in beiden Zufallsmodi, fragt aber nach der fehlenden Analyseliste. Vollständige Abnahme bleibt bis Klärung der persönlichen Ergebnisanzeige offen.

## Erwartete Anzeige und frischer Browsernachweis

| Verfahren | Zufallsmodus | Eigene isolierte Prüfung mit voller Bachflowers-Datenbank |
| --- | --- | --- |
| Original AetherOne | Reproduzierbar | Original-EW/GV-Ergebniszeilen sichtbar; Original-GV-/21er-Runde funktioniert |
| Original AetherOne | Stochastisch | Original-EW/GV-Ergebniszeilen sichtbar; eigener Journalbezug belegt |
| Persönliche Heuristik | Reproduzierbar |39 CPU-berechnete Raten,21 sichtbare Zeilen Seite1 und18 Seite2 |
| Persönliche Heuristik | Stochastisch |39 CPU-berechnete Raten,21 sichtbare Zeilen Seite1 und18 Seite2; eigene protokollierte Ziehungen |

15 Browserprüfpunkte bestanden, keine JavaScriptfehler; zusätzlich20 persönliche API-/Jobtests bestanden (bekannte TestClient-Abkündigungswarnung). Browserprüfung mit künstlichem Fall auf eigenem8114 und tatsächlicher vorgesehenerCPU, keine echten Klientendaten. Testscript und JSON/Screenshots: runtime/rw-ux-20261006/evidence/playwright-test-rw-fourmode-visible-review.js sowie ux-fourmode-visible-review-browser.json und persönliche seeded/stochastic Screenshots. Testdienst anschließendexitClean beendet, Port8114 geschlossen; Nutzerinstanz8112 und Dauerinstanzen nicht neu gestartet.

Die Original-EW/GV-Tabelle wird im persönlichen Verfahren absichtlich ausgeblendet. Dafür steht direkt unter den Verfahrenshilfen, oberhalb der Datenbanksuche, die eigene Tabelle „Persönliche Matrixscores“ mit Rang, Rate, Matrixscore, Intensität und Broadcast. Das vermeidet eine Vermischung von Original-GV und persönlichem Score. Während wartender/laufender persönlicher Berechnung gibt es absichtlich keine teilweise Ergebnistabelle; erst nach vollständigem Abschluss werden die Ergebnisse sortiert angezeigt. Status und Historie sind vorher verfügbar.

Quellen: webapp/js/views/analyze.js:44–60,128,370–374; webapp/js/views/personal_analysis.js:12–33,35–50,61–69; webapp/js/personal-selection.js; webapp/index.html:177–186,301–330; engine/src/radiworks/api/personal.py:30–42. Kein belegter pauschaler Sichtbarkeitsfehler in diesem Review.

## Grenzen und Prüflücke

Der ältere13-Punkte-Test belegte persönliche Zeilenzahl nur perAPI und Abschlussstatus, nicht die sichtbaren DOM-Zeilen. Die neue Prüfung schließt genau diese Prüflücke. Sie beweist nicht automatisch den Zustand des bestehenden Nutzertabs auf8112. CUA-Zugriff auf diesen Tab scheiterte zweimal am Kernelstart. Ein eigener neuer schreibfreier8112-Browserkontext hatte keine Fallbindung; dieser no-case-Status ist kein Befund über den Nutzertab.

Offene Betreiberfrage: bei geladenem Fall Persönliche Heuristik wählen, „Aufträge / Status aktualisieren“; ist die Matrixscore-/Intensitätstabelle im oberen Analysebereich sichtbar? Wenn ein abgeschlossener Auftrag dort leer bleibt, tatsächlichen Status/gewählten Katalog und gebundene Historie gezielt weiter prüfen. Keine neue Analyse erforderlich, um einen abgeschlossenen Auftrag anzuzeigen.

Vor erfolgreiche Nutzerklärung keineR6Dauerinstanz-/Quell-/Modul_Templates-/Start5Übernahme; O6Kamera und S4.8Integrationsfreigabe weiterhin getrennt offen.

Drei gescheiterte Vorläufe des neuen temporären Prüfharness wurden erhalten: erster Lauf wertete „Fall wird gespeichert“ wegen substringgespeichert zu früh als Abschluss; weitere Läufe enthielten falsch kodierte deutsche Statusliterale im übernommenen Evidenzscript. Tatsächliche Screenshots zeigten erfolgreiche Speicherung/Katalogauswahl. Nur temporäre Wartebedingungen korrigiert: endgültiger ASCII-Statuspräfix und tatsächliche Katalog-ID. Kein Produktcode zur Anpassung an den Test geändert. Belege: ux-fourmode-visible-review-harness-run1/2/3.json und .png.

## Phase und Bestandsschutz

| Schritt | Stand |
| --- | --- |
| R5 technischer Vier-Modi-/Sichtbarkeitsreview |100% dieses begrenzten Prüfpakets |
| R5 persönliche Betreiberabnahme |Teilbestätigung vorhanden; persönliche Ergebnisanzeige noch zu klären |
| R6 Übernahme / Modul_Templates / Start5 |Nicht erfolgt |
| A-LAYER |Machbarkeit geprüft, konkrete Umsetzung offen |
| AUDIO-PHI |Quellcode ausstehend; bestehende Audioformeln unverändert |
| S4.8 |0% Freigabe |

174 Produktdateien unverändert; Manifest9f7841c84ca7f8122efe5ebb9c9ddb353bf83802d878c358d06d4731d5bc362e. In dieser Fortsetzung nur eigene Prüfumgebung/Evidenz/Dokumentation verändert. Bestehende Fälle/Broadcasts der Nutzerinstanzen nicht verändert. Zusätzliche Audio-/Bildprüfung: docs/verification/RADIWORKS_BROADCAST_BILD_AUDIO_PLAN_2026-10-06.md mit84bestandenenTests.

Modelle: Leitung gemäß BetreiberwahlSol6.1/high; zwei begrenzte Luna6/max-Quellreviews (Audio und persönliche Ergebnisanzeige). Astra in diesem Paket nicht erforderlich/eingesetzt. Keine gemessene Tokenersparnis, keine Änderung der Hermes-Anwendungsroute.

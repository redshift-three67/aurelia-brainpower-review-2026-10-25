# RadiWorks UX-Korrekturen â€“ freigegebener Umsetzungsplan

**Goal:** Die konkret freigegebenen Reviewkorrekturen im isolierten Kandidaten abschlieÃŸen und 8112 mit vollstÃ¤ndigem Katalog zur BetreiberprÃ¼fung bereitstellen.
**Architecture:** Additive technische Katalog-IDs mit sicheren Labels; Original-PrÃ¤fix-/Dateiauswahl bleibt kompatibel. Frontend begrenzt API/WS auf die eigene Origin im lokalen Paket; Fokus/Navigation berÃ¼cksichtigen das Dock. Algorithmen, Auftragskontext und Live8103â€“8109 bleiben erhalten.
**Tech Stack:** Python/FastAPI bestehende Engine; Vanilla JS/CSS, bestehende Node-Test-/Playwrightwerkzeuge nur zur PrÃ¼fung.

Freigabe: Betreiber â€žOK, setze die Korrekturen um, dann prÃ¼fe ich die 8112 nochmalsâ€œ. Design/Spezifikation: docs/verification/RADIWORKS_UX_DATENSCHUTZ_REVIEW_2026-10-06.md (R3/R4, UX01â€“06/DS01). Keine neue allgemeine Datenbankarchitektur, VerschlÃ¼sselungsmigration, Aurelia-Autorisierung oder LiveÃ¼bernahme.

- [x] Vorhersicherung und Vertrags-/QuellprÃ¼fung.
- [ ] Luna/max: core/rates.py, api/routes.py und gezielte Engine-Tests. Additiver /catalogs-Index mit stabilen IDs, sicheren Labels und notwendiger kompatibler SelektorauflÃ¶sung; exakte Dateien und bisherige PrÃ¤fixreihenfolge getrennt erhalten. Erst rote Tests fÃ¼r geschÃ¼tzte Namen, unbekannte IDs und Legacyreihenfolge, dann Implementierung.
- [ ] Root: webapp/js/api.js sowie betroffene Katalogansichten; technische IDs separat von Namen/Gruppen, Backendlabel statt ID in Nutzeranzeigen. Sichere eigene API-/WS-Origin, keine freie Fremd-URL oder stiller Fallback. Vor Ã„nderung rote JS-/Browserregressionen.
- [ ] Root: Dock-Fokus sichtbar halten, Tabs intern scrollbar auch bei TextvergrÃ¶ÃŸerung. Vor Ã„nderung vorhandene Reproduktion als Regression mit Assertions.
- [ ] Root: PrÃ¼fstand/Kataloganzahl und verstÃ¤ndliche Schritte/Hilfen; geplante Aurelia-Pipeline und Ãœber/Quellen prÃ¤zisieren. Keine bestÃ¤tigten Controls entfernen.
- [ ] Tests: gezielte Engine/JS-Checks, vollstÃ¤ndige betroffene Engine-Suite; eigener isolierter Browser fÃ¼r 123 Kataloge, Original/Personal, Gruppen, Hilfe, Tastatur, schmale Ansicht, 200%Text. Kein Test mit personenbezogenen Daten.
- [ ] Astra/medium: unabhÃ¤ngiger Review der Katalog-/Origin-/Fokus-/Erhaltsgrenzen; Befunde vor Abnahme lÃ¶sen.
- [ ] Produktmanifest aktualisieren, 8112-AuftrÃ¤ge prÃ¼fen, Datenbestand/SQLite konsistent sichern; kontrolliert gleiche Home/SchlÃ¼ssel/Scope mit geprÃ¼ftem Vollkatalog neu starten, Wiederanlauf nachweisen. Keine unverifizierte Beendigung fremder Prozesse.
- [ ] Abschlussbericht/WIEDERAUFNAHME, Phase R3/R4 technisch vollstÃ¤ndig und Betreiberabnahme offen; anschlieÃŸend getrennte Live-/Quell-/Template-/Start5-Ãœbernahme.

AusfÃ¼hrung in dieser Sitzung; bereits isolierter runtime-Kandidat dient als Arbeitskopie. Kein globaler Git-Worktree aus dem Benutzerprofil, kein Commit fremder WIP. PrÃ¼fergebnisse sind keine Produktfreigabe. ProzentstÃ¤nde nur fÃ¼r dieses begrenzte Paket.

## Ausführungsnachweis 2026-10-06

Die ursprüngliche Checkliste oben bleibt als Plan erhalten. Konkrete Ausführung und Grenzen: docs/verification/RADIWORKS_UX_KORREKTUREN_2026-10-06.md. Backend- und UI-Korrekturen sowie Vollkatalog-/Origin-/Fokusprüfungen nachgewiesen;842Engine/CPU-,26JS-Testsgrün. Manifest174Dateien verifiziert,8112-Datenerhalt/Scope/Key/SQL und schreibfreier Browserabschluss nachgewiesen,8114 sauber beendet. Betreiberabnahme8112offen; keine Dauerinstanz-/Quell-/Modul_Templates-/Start5-Übernahme und keine S4.8-Freigabe. Kein pauschales Abhaken von Produktgates.

## R5-Nachkorrektur 2026-10-07

Gezielter Personal-Statusfix abgeschlossen und statisch in 8112 übernommen; Nachweise/Grenzen in docs/verification/RADIWORKS_PERSONAL_STATUS_FIX_2026-10-06.md. Veraltetes running nach fertigem Großkatalog, Poll-Wiederaufnahme, Startsperren und verspätete Antworten korrigiert. 41JS-/32Backendtests; vollständiger1382-Raten-Lauf und66Ergebnisseiten, finalallevierAuswahlkombinationengrün. UnerwarteterEntwicklungsprozessverlust/einzelnersynthetischerWorkerfehlerdokumentiert, Ursachennichtbelegt; gespeicherteNutzerergebnisseerhalten. Betreiberabnahmeoffen, R6undS4.8nichtfreigegeben; ursprünglichePlanchecklistenwerdennichtpauschalabgehakt.
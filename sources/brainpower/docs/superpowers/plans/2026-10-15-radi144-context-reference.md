# Radi144 – Kontext-/Zeitreferenz: Ausführungsplan

> Bestehende Betreiberentscheidung zur unveränderten Charakterisierung. Ausführung mit `superpowers:subagent-driven-development`, unabhängigen SPEC→QUALITY-Kontrollpunkten und `verification-before-completion`. Entwurf: `../specs/2026-10-15-radi144-context-reference-design.md`.

**Ziel:** Drei neue Vertragsbefunde mit zwölf festen synthetischen Gruppen an acht Originalfunktionskörpern charakterisieren. **Architektur:** Standardbibliothek, exakte AST-Auswahl, eigene In-Memory-Grenzen und äußerer Controller. **Technik:** vorhandenes Python3.11.12, `-I -S -B`, Auditguard, keine Produktänderung. Isolierter neuer Nachweisordner statt Änderungen/Commits in einem Produktworktree.

## Aufgaben und Zuständigkeit

- [x] Vorpunkt und drei Statusdokumente sichern;24 Dateien des vorigen Punkts frisch nachrechnen. Neue Betreiberentscheidung festhalten. Root besitzt Controller, Status/Pläne und Abschluss; kein CodeAgentSwarm verfügbar.
- [x] Luna/max besitzt ausschließlich `context_probe.py`, `test_context_probe.py` und eigene Rot-/Grünbelege im neuen Punkt `checkpoints/Aurelia-P3-Radi144-Context-20261015-062425Z`. Erst sinnvolle negative Werkzeugtests schreiben; Testbytes/Exitcode/Output für jede ausgeführte Fassung erhalten. Keine Originalfunktion vor Rootreview aufrufen; synthetische AST-Fixtures und Doubles für Werkzeugtests. Andere Arbeit nicht überschreiben.
- [x] Root erstellt neuen Controller und Werkzeugtests mit geschlossenem Gate. Quellen aus gehashtem `SOURCE-BASELINE.json`, einschließlich vorhandener AGENTS.md-Arbeit: exakten benannten Gitstatus einschließlich beider XY-Spalten erhalten. Frisch beobachtet: ` A AGENTS.md` (Index leer, Arbeitsbaum A); frühere mit `strip()` gekürzte Belege beweisen diese erste Spalte nicht. Clean-env, frische Labels, endliche Zeitgrenze und getrennte Fehler-/Nachprüfung sichern. Frühere Controller-/Probebelege nicht ändern oder wiederverwenden.
- [x] Werkzeugtests erfolgreich ausführen, Werkzeuge als Bytes und Hashes einfrieren. Astra/medium prüft SPEC zuerst, danach QUALITY; nur freigegebene eingefrorene Werkzeugfassung öffnen.
- [ ] Root führt genau `context-run-1`, danach nur bei erfolgreichem Ergebnis `context-run-2` aus. Je zwölf exakte Fallnamen/Erwartungen prüfen, vollständige Ergebnisse ausschließlich ohne Label vergleichen. Kein automatischer Retry bei neuem Fehler.
- [x] Gate schließen, unabhängigen Ergebnisreview durchführen; Quellen-/Werkzeug-/benannten Gitstand erneut abgleichen. Ergebnisse getrennt von Pydantic-/HTTP-/Store-/Engine-/Stochastikabnahme beschreiben.
- [x] Bericht, Hauptplan und Wiederaufnahme konsolidieren; Vorher-/Nachherkopien, Archivindex, Manifest und Rücklesen. Historischen Wiedereinstieg als Bytesuffix erhalten. P4-Bedarf: Feld-/Typ-/Herkunftsrevision, wirksamer Kontext versus Identitätsreferenz, Speicherungsversuch versus erfolgte Session getrennt. Kein P3-Gesamtabschluss oder normative Templateänderung.

## Kommandos

Aus dem neuen Prüfpunkt: `python -I -S -B -m unittest discover -s . -p test_context_probe.py -v`; Controller entsprechend `test_ROOT_controller.py`. Werkzeugtests dürfen nur eigene synthetische Definitions-/Double-/Guardgrenzen ausführen, keine gepinnten Originalkörper.

Originalreferenz erst nach eingefrorenem Vorreview: `python -I -S -B ROOT-controller.py --label context-run-1 --reviewed`, danach `context-run-2`. Nur neues Gate dieses Punkts öffnen; die alten API-/CPU-Gates bleiben geschlossen. Root speichert die vollständigen Kindoutputs und den präzisen Quellen-/Tool-/HEAD-/benannten Status vor/nach beiden Läufen. Keine produktiven Server-/Fall-/Audio-/Broadcastaktionen.

## Tatsächlicher Abschluss dieses Versuchs – Vorprüfung blockiert

20 aktuelle isolierte Werkzeugtests bestanden, keine Skips; eingefrorene vier Dateien unabhängig SPEC→QUALITY geprüft. `context-run-1` scheitert vor dem Start des Probe-Kindes an Git `dubious ownership` (Repository Hubert111, Testkonto CodexSandboxOffline). Originalaufrufe0; zweite Kennung nicht angelegt, kein numerischer Vergleich. Quellen-/Werkzeugbytes gleich; HEAD-/Gitstatus nicht bestätigt. Gate geschlossen, kein Retry oder Konfigurationswechsel. Fehler unabhängig nachgeprüft und begrenzter Punkt gesichert; Originalreferenz-Aufgabe bleibt ausdrücklich unerledigt.

Nächste Betreiberentscheidung: exakte prozesslokale Git-Pfadausnahme in neuer Controllerfassung mit eigenen Tests/Review und frischem Prüfpunkt; keine globale Ausnahme oder Änderung der Produkte. Bericht `../../verification/AURELIA_P3_RADI144_KONTEXT_REFERENZ_2026-10-15.md`. Erst der finale Rücklesebeleg bestätigt Sicherungsumfang.

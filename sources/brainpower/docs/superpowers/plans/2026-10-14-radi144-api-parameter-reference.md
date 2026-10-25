# Radi144 API-Parameterreferenz – Umsetzungsplan

> Ausführung mit begrenzter Subagentenarbeit und unabhängigen SPEC→QUALITY-Kontrollpunkten; bestehende Betreiberfreigabe zur unveränderten Ist-Referenz gilt. Entwurf: `../specs/2026-10-14-radi144-api-parameter-reference-design.md`.

**Ziel:** Den tatsächlichen Parameterfluss eines API-Analysepfads mit acht festen synthetischen Fallgruppen charakterisieren, ohne die bekannte Originalvertragslücke zu ändern.

**Architektur:** Acht genaue AST-Funktionskörper, Standardbibliothek und explizite Spy-/In-Memory-Grenzen; eigener äußerer Controller, frische Kindläufe und vollständiger Ergebnisvergleich. Kein Produktmodul-/Drittbibliotheksimport, keine Rechenengine oder echten Dienste.

**Technik:** vorhandenes Python3.11.12 mit `-I -S -B`, auditbasierte Aufrufsperre; Belege nur in `checkpoints/Aurelia-P3-Radi144-API-Parameter-20261014-213342Z`.

## Aufgaben

- [x] Vorherkopien und Manifest dreier Statusdokumente bytegleich geprüft; Betreiberentscheidung und begrenzten Entwurf festgehalten.
- [x] Luna/max erstellt zuerst negative Werkzeugtests; Rotfassung/Exitcode/Ausgabe als Bytes erhalten. Root besitzt ausschließlich Controller/Statusdokumente, Luna ausschließlich `parameter_probe.py` und `test_parameter_probe.py` plus deren Rot-/Grünbelege im Prüfpunkt. Keine rekursive Delegation.
- [x] Minimaler AST-/Quell-/Guard-/Coroutinevertrag mit acht festen Originalfallgruppen; Werkzeugtests bestehen, danach Dateien einfrieren. Unterschied zwischen Charakterisierung und Produktreparatur erhalten.
- [x] Root erstellt einen Controller mit geschlossenem Reviewgate, Quellen-/Werkzeug-/benanntem Gitvergleich vor/nach, sauberem Kindenv, frischen Kennungen `api-run-1/2` und120s technischer Grenze. Kein vorerstellter Ergebnislauf, keine Bibliotheks- oder Dienstinstallation.
- [x] Astra SPEC→QUALITY prüft vor Originalausführung. Beide Kindläufe mit unveränderten Werkzeugen und Quellen starten, Ursache/Nachprüffehler getrennt erhalten; bei unerwartetem Fehler kontrolliert stoppen.
- [x] Vollständige stabile Ergebnisse/AST/Quellen-/Werkzeugbindungen vergleichen. Unabhängiger Ergebnisreview; Scope-/Provenienz-/Teilabschlussanforderungen in P4 ergänzen.
- [x] Bericht, Hauptplan und Wiederaufnahme aktualisieren; Vorher-/Nachherkopien, Archivindex und finalen Rücklesebeleg prüfen. Bekannter Originalbefund erteilt keine Produktkorrektur-/P3-/P5-Freigabe. Danach nächste unabhängige P3-Arbeit innerhalb des bestehenden Plans auswählen.

## Konkrete Prüfkommandos

Werkzeugtest im Prüfpunkt: `python -I -S -B -m unittest discover -s . -p test_parameter_probe.py -v`; das kontrollierte Arbeitsverzeichnis erlaubt Discovery des eigenen Testmoduls, keine Installation.

Originalreferenz ausschließlich nach eingefrorenem Review: `python -I -S -B ROOT-controller.py --label api-run-1 --reviewed` und entsprechend `api-run-2`. Der Controller bindet konkrete Hashes der zwei Werkzeuge und seiner eigenen Datei. Die Known-Gap-Assertions erwarten ausdrücklich fehlendes Weiterreichen der drei Requestoptionen; keine stillschweigende Formel-/Geräte-/Quantumänderung.


## Tatsächlicher Abschluss15.10.2026

Sieben Harness- und sechs Controllertests erfolgreich, zwei unabhängige Original-API-Referenzläufe mit je8 Gruppen/36 Erwartungen bestanden; vollständige Ergebnisobjekte ausschließlich ohne Label identisch. Ein Reviewfehler im Session-Double vor Originalausführung korrigiert und mit eigener Rot-/Grünregression gebunden; vorhandene Originalalgorithmen unverändert. Frühe Testloader-/ast.dump-Zwischenbytefassungen nicht vollständig erhalten, offengelegt; keine vollständige historische Reproduzierbarkeit daraus ableiten.

Luna/max Werkzeugvorbereitung, Root unabhängige Ausführung/Korrekturen, Astra/medium unabhängiger Vor-/Ergebnisreview. Vollständige P3-/HTTP-/Engine-/Auth-/Persistenzabnahme bleibt offen. Sicherungsabschluss ausschließlich durch FINAL-READBACK im genannten Punkt bestätigt. Kein Produkt-/Live-/Template-/Routingeingriff.

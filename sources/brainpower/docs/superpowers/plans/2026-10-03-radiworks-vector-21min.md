# RadiWorks: drei isolierte Fälle und optionales Fokusbild

**Ziel:** Drei unterschiedliche synthetische Fallkontexte mit demselben Original-Ratenkatalog kontrolliert vergleichen und ihre virtuellen Broadcasts mindestens 1260 Sekunden gemeinsam beobachten. Bestehende Live-Instanzen und Algorithmen bleiben unverändert.

**Aufbau:** Eigene fest kopierte Kandidatenquelle, drei getrennte Prozesse, Ports 8111–8113, individuelle Laufzeitordner und Scopes. Ausschließlich die Datei `ESSENCES_BACHFLOWERS_RATES.txt` wird aus dem aktuellen Katalog hashgebunden in den Testkatalog kopiert. Fallname enthält die erfundenen Identitätsangaben; das vorhandene Fokusfeld enthält einen jeweils anderen neutralen Fokus. Optionale künstliche Bilder bleiben mit Hash und Fallzuordnung im Versuchsmanifest, da der normale Analysevertrag kein Fokusbildfeld kennt.

**Aussagegrenze:** Gleicher Seed/geordneter Katalog/Modus müssen trotz verschiedener Fallkontexte gleiche numerische Ergebnisse liefern, wenn der Kern diese Kontexte nicht verarbeitet. Jeder von drei Seeds wird bei jedem Fall geprüft; erst danach beginnt der parallele Langlauf mit einer ausgewählten Analyse pro Fall. Unterschiedliche Seed-Ergebnisse werden nicht als bewiesene Fallpassung bezeichnet. Der unveränderte Broadcast startet je Prozess mit Seed 0 und liefert simulierte Resonanzen, keine unabhängigen physikalischen Messungen.

## Schritte

- [x] Datenfluss und optionale Bildverwendung anhand der Quelle prüfen; unabhängige Luna-Prüfung und Astra-Grenzprüfung beauftragen.
- [x] Diagnosewerkzeug `tools/radiworks_vector_21m_probe.py` erstellen: fest begrenzte Ports, eigenständige Quelle/Katalog, drei synthetische Fälle, 3×3 Seed-Kontrolle, 21 Raten-GV, Draft-Freigabe, extern protokollierte Queue-/Resonanzzählungen und Fall-/Sitzungsidentität.
- [x] Werkzeug mit kurzem ausdrücklich gekennzeichnetem Funktionstest prüfen. Dieser zählt nicht als 21-Minuten-Nachweis.
- [x] Einen echten 1260-Sekunden-Lauf mit allen drei Fällen gemeinsam ausführen; bestehende Original-GV-Werte dabei nur lesen, keine automatischen GV-Ziehungen hinzufügen.
- [x] Gesamtlauf, Code-/Kataloghashes, Zuordnung, monotone Resonanzzähler, unveränderte Analysewerte, Stop und Cleanup auswerten. Kein Erfolg bei einer abgebrochenen/verkürzten Probe.
- [x] Optionales Fokusbild als Integrationsvorschlag dokumentieren: lokal validierter Bildtyp/Größenlimit, opake Bildreferenz, servergebundener Snapshot; keine heimliche Seedableitung oder behauptete Bild-/Fallpassung.
- [x] Ergebnisse und Fortsetzung dokumentieren. GV-2-Timer/Historie bleiben ein separater Kandidatenblock; keine automatische Übernahme in 8103–8109.

## Belege

Das Werkzeug muss Prozess-IDs, Ports, Runtimes, Scope, Fallreferenz, Session-/Draft-/Broadcast-IDs, Seeds, Katalog-/Codehash, UTC-Zeit und monotone Laufzeit festhalten. Polling erfasst kumulierte Zähler extern, da die aktuelle Ereignishistorie begrenzt ist. Gemeinsame Beobachtungsdauer mindestens 1260 Sekunden; alle gewählten Broadcasts bleiben bis zum letzten Messpunkt aktiv und werden anschließend ausschließlich im Testscope gestoppt. Rohdaten und komprimierte Zusammenfassung bleiben lokal.

## Abschluss

Echter Langlauf vollständig: 1260,067 Sekunden zwischen Start und letztem Messpunkt, drei Fälle, neun Kontrollanalysen, 249 Messpunkte. Der separat entdeckte Takt-Fix ist im Kandidaten engine-geprüft; seine volle Browserregression bleibt nach einem Node-Speicherfehler offen. Ergebnis: `docs/verification/RADIWORKS_VEKTOR_FOKUSBILD_21MIN_2026-10-03.md`. Keine Live-Übernahme.

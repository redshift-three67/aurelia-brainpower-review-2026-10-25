# GV-2 und Designnachtrag — Umsetzung 04.10.2026

Grundlage: bestätigter Folgeplan RADIWORKS_VEKTOR_GV2_FOLGEPLAN_2026-10-04.md und Betreiberauftrag, danach GV-2 umzusetzen; Dunkel als Standard, GV unter Resonated Rates, Zwischenablage-Label. Neue persönliche Auswahlalgorithmen nur empfehlen, nicht still implementieren.

## Grenzen und konkrete Entscheidungen
- Isolierter Kandidat runtime/rw-gv2-20261004, Herkunftsmanifest BASELINE.json. Original, 8103–8109, ihre Daten und Schlüssel unverändert. Kopie enthält engine/src, engine/tests, pyproject.toml, webapp; engine/tools existiert in der Grundlage nicht und wurde nicht kopiert.
- Zusätzliche abgeleitete Zahlen, keine Messung einer Behandlung oder Person. Eigener OS-Entropieprovider und eigenes verschlüsseltes Rohseedjournal je Beobachtung. Keine Mitbenutzung von Analyse-/Auto-/Resonanzströmen oder Webcam-/random.org-Pools. Fehlender Journalschlüssel sperrt Aktivierung; Quelle ausdrücklich sichtbar.
- Aktivierung pro serverseitig gebundenem aktivem Promotions-Broadcast, Standard aus, 1260 Sekunden bis zur ersten Baseline. Nach Neustart aus, kein Nachholen. Direct/Auto/ungebundene Einträge ohne erfundene Bindung.
- Eigener Beobachtungsworker; Ziehung außerhalb des Queue-Locks, danach Identität/Aktivität/Laufzeit unter kurzem Lock erneut prüfen und Historie atomar speichern. Stop/Ende während Ziehung verwirft Datensatz. Ein-Datei-Speicher je Broadcast mit unveränderlicher Scope-/Fall-/Session-/Ratenbindung. Analyse-/Falldateien unverändert. Schreibfehler ergeben keinen erfolgreichen Historieneintrag. Sichtbare Kapazitätsgrenze statt stiller Löschung.
- Fall-GV und Raten-GV separat. Tendenz nur zur letzten Beobachtung derselben Bindung; Baseline ohne Pfeil. Delta 0 = gleich, |Delta| ab 200 = stark. Reine Anzeigeschwelle, kein medizinischer Grenzwert. Text/Pfeile ergänzen Farbe.

## Pakete / Prüfungen
1. Tests zuerst: aus/1260s, mehrere Bindungen, Stop/Ende/Wechsel während Ziehung, Persistenzfehler, Restart aus, malformed history/Scope/IDs, unabhängiger Entropiestrom.
2. Engine: Speicher/Controller, Queue-Commitprüfung, App-Lebenszyklus, strikt typisierte Status-/Aktivierungs-/Historienrouten. Bestehende Suite.
3. UI: bewusste Aktivierung, Fehler, sessionweise Historie und zugängliche Tendenzen. GV unter Resonated Rates, sichtbare KI-Zwischenablage wird Zwischenablage, DOM-IDs/Aktionen erhalten.
4. Design: Dunkel ohne explizite Präferenz; Nutzer-/Hostwahl respektieren. Lokale Font-Fallbacks ohne externe Requests, tabellarische Ziffern, Kontrast, stabile Statusfarben. Versionierter Delta-Vertrag für Aurelia/Modul_Templates vorbereiten; keine ungeprüfte Aurelia-Codeübernahme.
5. Browser: bestehende Kernabläufe, Dock/Escape/letzte Zeile, Themes, 390px, Keyboard, Beobachtungssteuerung/History. FakeClock für 21-Minuten-Grenze, reale Langlaufprobe gesondert.
6. Astra-Review Zuordnung/Persistenz, Nachtests, Hashdelta und Wiederaufnahme. Kontrollierte Liveübernahme/Synchronisation erst später.

## Vektor / Design
Radi144 lesend vergleichen. Identität, explizite Fokus-Katalogsuche und unveränderlicher Auftragskontext trennen. Neue Scoring-/Vektorfunktionen und Innovationen bleiben Entscheidungspunkte.
WCAG 2.2 Accessibility-Ziel, keine pauschale Zertifizierung. E-E-A-T: Quellen, Grenzen, nachvollziehbare Ergebnisse; keine Farb-/Heilbewertung. Ruhige Salbei-/Petrol-/Sand-Akzente, geprüfte Kontraste und modulweise Auswahl. Historischen Template-Vertrag als Delta ergänzen, nicht unbemerkt überschreiben.

## Betreiberbestätigung: zusätzlicher Experimentalmodus

Am 04.10.2026 ausdrücklich bestätigt: Fokus-/Themensuche mit begründeten Katalogvorschlägen und Nutzerbestätigung; getrennte persönliche Kontextfelder mit stabiler Fall-ID; unveränderlicher Kontext je Analyse/Broadcast. Zusätzlich eigener vergleichbarer Experimentalmodus, Radi144-Formeln dürfen verwendet werden. Kein Ersatz des Originals. Dieser Nachtrag genehmigt die Vorbereitung/Umsetzung im eigenen Modus, nicht Liveaktivierung, wissenschaftliche Validierung oder Aurelia-Integration.

Reihenfolge nach GV-2: VF-2 strukturierte Kontextfelder/Snapshots → VF-3 erklärbare Suchvorschläge → EXP-1 deklarierter Radi144-Vektorvergleich. Status EXP-1: geplant, nicht auswählbar/ausführbar. Umstellung erst nach isolierten Eigen-/Vergleichstests und sichtbarer Betreiberentscheidung. Bestehende Fälle/Sitzungen niemals in den neuen Modus automatisch migrieren.

EXP-1 Vertrag: eigenständige mode_id/formula_version und getrennte Parameter, Quelle/Limitierungen sichtbar, PII bleibt lokal und scopegebunden. Identität nicht aus freiem Altfallnamen erraten. Für jede Vergleichsgruppe gleicher Kataloghash, identischer Ausgangsseed/Ziehungsstand, versionierter Kontext und Parameter. Zwei getrennte Resultate/Sitzungen; Umschaltung betrifft ausschließlich einen neuen Auftrag. Ergebnisse nachvollziehbar gegenüberstellen, keine Behauptung physiologischer/therapeutischer Genauigkeit.

Radi144-Formeln sind Rechenheuristiken: persönliche Signatur, Text-/Hashfrequenz, optional RGB/HSV-/Pixelentropie-Komponenten; nicht als semantisches KI-Embedding bezeichnen. Implizite aktuelle Uhrzeit/organ_clock wird standardmäßig nicht übernommen. Ein zeitabhängiger Bestandteil braucht einen ausdrücklich festgehaltenen Zeitpunkt und eine eigene Formelversion. SHA-1/MD5 dürfen allenfalls gekapselte Kompatibilitätsberechnungen liefern, nie persönliche öffentliche IDs, kryptografische Sicherung oder Datenschutzbeweis.

Vor Experimentalimplementierung genaue aktuelle Radi144-Parameter/Formelquelle und Datenfluss pinnen; getrenntes Eigentümer-/Tenant-/Client-/Jobmodell, Bildformat-/Decoder-/Löschvertrag, numerische Grenzen und Vergleichskriterien dokumentieren. Originalanalyse, Original-GV und ursprüngliche Signaturen nicht heimlich durch experimentelle Scores verändern. Schaltplan Original/Experiment klar, Rückwechsel ohne Datenverlust. Kamera-/Hardware-/CUDA-/Kozyrev-Abhängigkeiten entstehen dadurch nicht automatisch.


## Plattformweite Betreibergrenze — 04.10.2026

Bestehende stabile Algorithmen und Heuristiken bleiben die Grundlage für RadiWorks und sämtliche aktuellen/künftigen Aurelia-Module. Keine semantische KI-Suche, neuen Embeddings oder anderen Analyseverfahren ohne ausdrückliche vorherige Besprechung. VF-3 nutzt erklärbare Katalog-/Wort-/Themenheuristik; EXP-1 bleibt der ausdrücklich genehmigte, getrennte Radi144-Heuristikmodus. Nicht automatisch auf andere Module ausweiten. Änderungen ergänzen bestätigte Funktionen; keine verdeckte Ersetzung.

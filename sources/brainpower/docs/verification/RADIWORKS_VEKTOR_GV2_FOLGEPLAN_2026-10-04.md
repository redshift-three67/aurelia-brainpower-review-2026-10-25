> Aktualisierung 05.10.2026: GV-2/UI-2 sowie VF2-A/B und VF3 sind im isolierten Kandidaten geprüft. [VF3-Abschluss](RADIWORKS_VF3_ABSCHLUSS_2026-10-05.md). Die folgenden Befund-/0%-Stände dokumentieren den damaligen Vorplan. EXP1 und spätere Übernahme-/Integrationsgates bleiben offen.

# RadiWorks: Fokus-/Vektorprüfung und konsolidierter Folgeplan — 04.10.2026

## Gesicherter aktueller Stand

**Fall-/Sitzungszuordnung, vollständiger persönlicher Kontext und numerischer Algorithmuseingang sind drei unterschiedliche Dinge.** Fokus hilft aktuell nach ausdrücklichem Klick bei der Suche nach Katalognamen. Er bleibt bei der gewählten Datenbank als Fall-/Draftkontext erhalten, verändert aber nicht die Zahlenberechnung des normalen Ratenkerns. Name, Vorname, Geburtsdatum und Ort liegen derzeit nicht als gemeinsam typisierter vollständiger Vektorvertrag vor. Angaben im Fallnamen sind Freitext, kein automatisch zerlegtes Identitätsmodell. Das optionale Fokusbild ist noch keine implementierte fallgebundene Bildpersistenz und kein bestätigter Algorithmuseingang.

| RadiWorks-Pfad | Tatsächlicher Eingang / Bindung | Grenze |
|---|---|---|
| Datenbankanalyse | gewählte Ratenliste, Entropie, max_hits; danach Draft mit Fall, Sessionabsicht und case_focus | kein aus Fokus/Personendaten abgeleiteter Rechenseed oder automatisches inhaltliches Ratenranking |
| Fokus-Suchschaltfläche | Fokus als ausdrücklich übernommener Suchtext für Katalognamen | verändert keine Rateninhalte und keine Berechnungswerte |
| Prüfdraft → Freigabe → Broadcast | Signatur aus Rate + EW + Potenz; gültige Promotion erhält feste Scope-/Fall-/Sitzungs-/Ratenindex-/Analysehashbindung | Referenz ist kein vollständiger persönlicher Vektortext; bei ungültiger optionaler Beobachtungsbindung bleibt reguläre Promotion ohne Beobachtungsbindung möglich |
| Direkter Broadcast / Auto | ausdrückliche bzw. automatisch ausgewählte Signatur | keine geeignete Beobachtungsbindung ergänzt; nicht still aus aktuell geöffnetem Fall rekonstruieren |
| Virtuelle Resonanzziehung | eigener bestehender Broadcast-Entropieprovider, derzeit seeded0 | Fall-/Fokusdaten werden nicht in diese Zufallsziehung eingespeist; keine neue statistische Vektorwirkung behaupten |

**Synthetischer Nachweis auf dem aktuellen Journalkandidaten:** Drei unterschiedliche erfundene Fälle mit Datum/Ort im freien Namen, jeweils eigener Fokus und Sessionabsicht; gleicher Katalog und gleicher Seed. Ergebnis-Digests und promovierte Signaturen waren gleich; Fall-/Sitzungsreferenzen verschieden. Direkte Broadcasts hatten keine Beobachtungsbindung. Testscheduler ausschließlich in diesem Test deaktiviert, keine realen Broadcasts/Ports verändert. Dies bestätigt die geprüften Inputs und Pfade, keinen universellen Nachweis für sämtliche Appzustände. Eine erste Probe verlangte eine Absicht vor Existenz einer Sitzung und erhielt korrekt409; korrigierte Probe legt die Sitzung vorher an. 68 gezielte Beobachtungs-/Broadcastbindungstests bestanden,0Fehler/Skips.

Aktuelle Stellen im isolierten Kandidaten: `engine/src/radiworks/api/routes.py:667` Analyse/GV, `:684` Fokuszuordnung, `:1840` Promotionbindung, `:1952` direkter Broadcast; `core/analysis.py:158`, `core/draft.py:350`, `core/observation_binding.py:46`, `core/broadcast.py:181/228/465`, `main.py:146`; `webapp/js/views/analyze.js:229/247` Fokus-Suche. Zeilen sind lokale Orientierung, die Quellhashes im vorherigen PRODUCT_VERIFY.json bleiben unverändert.

## Abgleich mit tatsächlichem AetherOnePi2.9.0

Direkte `javap -c -p`-Ausgabe des lokalen JARs, nicht eine ungeprüft zugeordnete Java-Datei. JAR SHA-256: `24090abb6726ddf9a44a38f28f972c349d04311b7d35ef4e3d06bb6078e4d660`. JAR-/Klassenhashes und Werkzeugpfad: `runtime/rw-vector-audit-20261004/jar-bytecode/SOURCE.json`.

- `AetherOneEventHandler.analyzeDatabase`: lädt Raten anhand des gewählten Datenbanknamens und reicht diese an `AnalysisService.analyseRateList(Iterable<Rate>)`. Der geprüfte Aufruf übergibt keinen persönlichen Vektor. Entropie/Hotbits bestimmen die Ziehungen; dies ist keine Wirkungsaussage über Personen.
- `broadcastNow`: liest den Text aus `SIGNATURE` und die Laufzeit; `broadcast` reicht diesen Text an eingebettete GuiElements/BroadcastElement weiter. Diese geprüfte Konstruktor-/Weitergabekette fügt keinen Fallnamenspräfix und kein strukturiertes Datum-/Ort-/Fokusobjekt hinzu.
- In den zusätzlich geprüften SIGNATURE-Schreibstellen wird beim neuen Fall geleert bzw. auf ausdrücklichem Clipboardpfad Zwischenablagetext eingefügt. Enthält der eingegebene/kopierte Text Personendaten, gehören sie natürlich zu dieser Signatur. Das ist keine automatische vollständige Vektorbildung. Nicht alle Originalaufrufer oder möglichen globalen Zustände wurden geprüft.
- Der alternative `BroadcastUnit`-Pfad erhält zusätzlich Clipboardbilder. Deshalb keine appweite Aussage „das Original nutzt ausschließlich Text“. Eine beliebige Bildliste ist auch kein belegtes typisiertes Fokusbild samt vollständigem persönlichen Vektor.
- `BroadCastData` besitzt ein separates intention-Feld; dessen Existenz allein belegt keine Verwendung in den hier geprüften Berechnungspfaden. `BroadcastElement.target` ist im geprüften Konstruktor-/Berechnungspfad nicht gelesen; die Klassenkonstantenprüfung fand target-Getter/Setter nur in dieser Klasse.

**Wichtige Versionskorrektur:** Die vorhandene, nicht versionsgesicherte CFR-Dekompilation unter `Radiworks/decompiled` zeigt `case.name + SIGNATURE`. Das passt nicht zur geprüften2.9.0-Weitergabekette. Ihre Version bleibt unbekannt; daraus wird weder eine behauptete2.9-Funktion noch eine bestimmte ältere Version oder ein neuer Algorithmus abgeleitet.

Bytecodebelege: `AetherOneEventHandler.javap.txt:2003/2085/2395/2751`, `GuiElements.javap.txt:305`, `BroadcastElement.javap.txt:57/2342`, `BroadcastUnit.javap.txt:49`. Für die vorliegende Frage besteht daher keine belegte Pflicht, den bestehenden Originalanalysealgorithmus durch künstliches Hashen persönlicher Daten zu verändern. Ein neuer persönlicher Auswahl-/Scoringmodus wäre gesondert zu definieren und zu testen.

## Bestätigte Reihenfolge im Plan

| Priorität / Paket | Stand jetzt | Abschlusskriterium |
|---|---:|---|
| VF-1: Fokus-/Vektor-/Originalpfade prüfen | 100% des begrenzten Prüfpakets | JAR-gebundene Quellen, Dreifallprobe,68Bindungstests, Grenzabgrenzung |
| Journaloptimierung | 100% im geprüften Kandidaten | vorheriger Bericht:384PASS/2bekannteSkips,22Browser-PASS; weiterhin keine Liveübernahme |
| GV-2: getrennte Beobachtung und Sitzungshistorie | 0% Umsetzung, nächster Funktionsblock | unabhängiger Entropiestrom, ausdrückliche Aktivierung,1260s-Timer, immutable Zuordnung, additive persistierte Historie, Fehlertests |
| UI-2: GV unter Resonated Rates; „Zwischenablage“ | 0% Umsetzung, gemeinsam mit GV-2-Darstellung | bestehende DOM-IDs/Bedienwege, Dock/Escape/Fokus/Reflow und Clipboardfunktion erhalten |
| VF-2: vollständiger Kontextvektor / weitere Broadcastpfade | getrennte Erweiterung,0% | versionierter unveränderlicher Snapshot; keine heimliche algorithmische Änderung oder erfundene Fallzuordnung |
| Quellordner/Modul_Templates/F:-Abgleich | nach Kandidatenabnahme,0% für diesen Nachtrag | Hash-/Vertragsvergleich, klare Pfad- und Versionsreferenzen |
| Aurelia S4.8 |0% Freigabe| gesonderte Host-/Betreiber-/Integrationsgates |

Prozente beziehen sich nur auf die benannten Pakete, nicht auf die gesamte RadiWorks-Produktreife.

### GV-2: nächste Umsetzung auf bereits bestätigter Grundlage

- [ ] Neues isoliertes Arbeitsverzeichnis aus dem geprüften Journalkandidaten, mit Herkunftsmanifest; Entwicklungsport außerhalb8103–8109. Die laufenden sieben Prozesse und bestehenden Queues bleiben unverändert.
- [ ] Unabhängigen Beobachtungsprovider anlegen: Beobachtungen konsumieren weder den Entropiestrom der gespeicherten Analyse/21er-Runde noch den der bestehenden Broadcastresonanz. Bei Entropie-/Schlüsselproblemen kein stiller seeded-Ersatz unter Stochastic-Kennzeichnung.
- [ ] Ausdrücklich einschaltbare1260-Sekunden-Beobachtung für geeignete unveränderlich gebundene aktive Promotionsraten. Die21Minuten sind eine Betreiberanforderung, kein wissenschaftlich belegtes Wirkintervall. Direct/Auto/ungebundene Einträge sichtbar ausschließen, bis deren eigener Vertrag ergänzt und geprüft ist.
- [ ] Fall-GV und Raten-GV als separate neue Beobachtungswerte speichern; ursprüngliche Analyse/21er-Werte erhalten. Erste Beobachtung als Baseline kennzeichnen; numerische Tendenz aus vergleichbaren Vorgängerbeobachtungen, nicht aus EW oder Resonanzzählern ableiten.
- [ ] Historie anhand Scope, Fallreferenz, Session-ID, ursprünglichem Ratenindex, Analysehash und Broadcast-ID zuordnen. Bestehende atomare Persistenz-/Recoverygrenzen verwenden; Schreibfehler veröffentlichen keinen erfolgreichen Historieneintrag. Mehrere Broadcasts derselben Rate bleiben nachvollziehbar getrennt.
- [ ] Timergrenzen mit FakeClock prüfen:1260s, ausgeschaltet, Stop/Ende während Beobachtung, Fall-/Sitzungswechsel, gleichzeitig laufende Einträge, Neustart ohne blindes Nachholen. Keine Fortsetzung durch Übernahme des zuletzt im Browser ausgewählten Falls.
- [ ] Numerische Trendanzeige und sessionweise Historientabelle ergänzen. Steigend/grün, fallend/rot und stagnierend zugänglich auch mit Text/Pfeilen; „stark“ anhand explizit dokumentierter numerischer Schwelle, keine stillschweigende Gesundheits-/Harmonisierungsbewertung.
- [ ] Gezielte Fehler-/Entropie-/Isolationstests, vollständige Kandidaten-Suite und Browserprüfung. Unabhängiger Review bei materiellen Persistenz-/Zuordnungsentscheidungen. Erst danach gemeinsame Übernahmeplanung.

### UI-2: konkret eingeplante Änderungen

1. **General Vitality unterhalb der Resonated Rates** im Broadcastbereich und aufgeklappten Analysedock platzieren. Resonanzliste und GV bilden einen vertikalen Bereich; Queue bleibt separat sichtbar. Mini-GV-Canvas/Text/IDs und bestehende getrennte GV-Anzeigen nicht löschen oder semantisch vermischen. Dockgröße, Escape-Schließen und letzte erreichbare Analysezeile erhalten; Desktop/Mobil, Dark/Light und Scroll prüfen.
2. Sichtbare Bezeichnung **„Zwischenablage“**, Button **„Analyse → Zwischenablage“**. Hilfetext klar: kopiert lokal in die Betriebssystem-Zwischenablage, kein automatischer Modellaufruf/Upload. Tooltip, Meldungen und zugängliche Namen konsistent anpassen. Prüfdraft/Freigabe bleibt ein separater serverseitiger Ablauf; interne Endpunkte/Eventnamen nicht allein wegen des Labels umbenennen.

### VF-2: vollständiger Vektor als eigener Vertrag

Name/Vorname, Datum, Ort, Fokus/Absicht und optionales Bild nicht aus dem heute frei geschriebenen Fallnamen „erraten“. Für eine zukünftige strukturierte Kontextbindung optionale explizite Felder und einen versionierten Snapshot pro Auftrag vorsehen. Dieser muss auch beim Fall-/Fokus-/Bildwechsel unverändert bleiben; Rohdaten nicht automatisch in öffentliche Signaturen, Logs oder externe Modelle übernehmen. Fehlende Angaben sichtbar als fehlend kennzeichnen; Ref/Hash ist weder numerische Wirksamkeit noch Anonymisierung. Die bestätigte Originalberechnung bleibt erhalten. Ein erweiterter persönlicher Analysemodus oder ein originalversionsspezifischer Witness-Signaturmodus erfordert eigene Spezifikation, Vergleich und Entscheidung.

## Belege / Modelle / Grenzen

- `runtime/rw-vector-audit-20261004-02/RESULT.json`, `binding-tests.xml`, `REVIEW.json`: synthetische Probe,68Tests, Reviewgrenzen.
- `runtime/rw-vector-audit-20261004/jar-bytecode`: tatsächliche2.9-Klassen/Disassembly; ursprüngliche fehlgeschlagene Testanordnung alsRESULT.json im Elternverzeichnis behalten.
- Produktquellen unverändert zu `runtime/rw-journal-20261004/PRODUCT_VERIFY.json`; bestehender hashgeprüfter Checkpoint bleibt unangetastet. Keine Layout-/Clipboard-/GV-2-Implementierung, keine Quellordner-/Template-/F:-Übernahme durch diesen Planungsblock.
- Sol6.1/high als gewählte Chatleitung; tatsächlich Luna6/max für begrenzten Quellenabgleich, Astra6/medium für die unabhängige Beurteilung der Versions-/Vektorgrenze. Kein Token-/Kostenbenchmark.

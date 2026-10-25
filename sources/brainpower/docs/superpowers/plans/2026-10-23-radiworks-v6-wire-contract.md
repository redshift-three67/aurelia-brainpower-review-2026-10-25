# RadiWorks V6: Fehlerantwort und Beobachtungsbudget

**Goal:** Die drei bestätigten Integrationslücken lokal schließen, danach ein frisches gebundenes Paket vorbereiten; kein nativer Lauf.

**Architecture:** Neues Verzeichnis `runtime/rw-material-v6-20261023`, basierend auf eingefrorenen V5-Quellen und dem separat geprüften54-Test-Kandidaten. Ein gemeinsamer reiner Wire-Validator gilt serverseitig und bytegleich eingebettet im Clienttransport. Er erlaubt ausschließlich gebundene, typisierte und begrenzte Fehlerfelder. Ein separates Beobachtungsbudget beschreibt Transport-Warten, keine harte Gesamtlaufzeit.

**Tech Stack:** Python-Standardbibliothek, unittest, AST-/SHA-Prüfungen. Lokale Tests sperren reale Prozess- und Netzwerkstarts; synthetische IO-Grenzen sind ausdrücklich gekennzeichnet.

## Schutz und Identität

- Bestehende126 Dateieinträge aus fünf Indizes bleiben unverändert; `BASELINE.json` bindet Kopien und Ursprung.
- Neue Zielidentität erst bei Paketbildung: `material-intake-20261023-v6`, `rwmaterialdiagv6.service` und `.slice`. Keine Rücksetzung/Verwendung alter Marker oder Versuche.
- Keine Produkt-, Server-, Budget-, ACL-, Hermes- oder globale Profiländerung; kein kostenpflichtiger Scan. Materialstart bleibt separat konkret freizugeben.
- Die neue Betreiberabkürzung „Weiter nach Direktive“ wird in AGENTS dokumentiert; sie ersetzt keine dieser Grenzen.

## 1. Wire-Vertrag — Root besitzt Implementierung und Tests

- [x] RED: `test_failure_wire.py` prüft die echte Kette `Runtime.start → safe_worker → Fehlerheader → run_remote → transport.json`. Bereits vorhandene Kernel-/Bereinigungsfelder müssen fehlen und den Test gezielt scheitern lassen; keine Importfehler als RED akzeptieren.
- [x] Neues `failure_wire.py`: festes Fehlerschema, Paket-SHA, exit_code exakt Integer1, erlaubte Fehlerarten/Stufen/Gründe. Legacy-Basisfehler bleiben datenarm lesbar; neue Zusatzfelder ohne passenden Header/Paket werden abgewiesen.
- [x] Kernel: exakt fünf Dateinamen, feste erwartete Werte, begrenzte numerische/max-Texte oder ausdrücklich ungültiger beobachteter Wert; echte Booleans; keine behauptete Übereinstimmung bei Mismatch.
- [x] Cleanup: Command-Exit und Unit-Beobachtungen strikt getrennt. `cleanup_verified` muss ausdrücklich False bleiben. Enums, PID-Typ/Grenze, feste Zielmenge und kleine serialisierte Ausgabe; keine Pfade, freien Ausnahme-/stdout-/stderrtexte oder unbekannten Verschachtelungen.
- [x] In `Runtime.start` sichere Kopien der berechneten Cleanup-Metadaten an die ursprüngliche Exception binden. Metadaten-/Beobachtungsfehler dürfen den ursprünglichen Fehler nicht ersetzen. Keine weitere Stopaktion und kein Retry.
- [x] Generator setzt bei fehlgeschlagener Außenantwort Schema und exakten Paketbezug. Client prüft denselben Validator aus exakt gehashten eingebetteten Bytes; kein ungebundener Import oder Modulcache.
- [x] Transportpersistenz erhält nur validierte Fehlerdaten; accepted/launch_acknowledged/worker_completed/transport_succeeded bleiben False. Missgebildete, widersprüchliche oder falsche Paketdaten ergeben unbekannten Ausgang.

## 2. Beobachtungsbudget — separater begrenzter Worker

- [x] Pure `observation_budget.py` und Tests: nominale Befehlssummen preflight60/start165/status170 Sekunden mit Quellankern unabhängig prüfen. Die Summen sind weder Messwerte noch harte Gesamtgrenzen.
- [x] Geplante Warte-/Drainobergrenzen: preflight110, start240, status240 Sekunden. Diese begrenzten Beobachtungsfenster enthalten Puffer, garantieren aber keine rechtzeitige Fertigstellung regulärer IO/Spawn-/Persistenzschritte. Kein Timeoutwert verändert Worker-, CPU-, RAM- oder Speicherlimits.
- [x] Transport übergibt den operationseigenen Wert ausdrücklich an `_run_bounded`; globaler Legacy-Default110 bleibt für direkte Bestandsprüfungen erhalten. Werte und Einschränkungen stehen im Versuch/Ergebnis. Bool/NaN/unendliche/negative/unbekannte Werte werden vor Prozessstart abgewiesen.
- [x] Timeout bleibt `unknown`, verbrauchter Versuch bleibt verbraucht. Keine Aussage vollständiger Remote-Bereinigung; SSH-Kill ist kein Worker-/Unit-Stoppbeweis.

## 3. Gemeinsame Prüfung

- [x] Bestehende relevante Suiten mit den neuen lokalen Helfern ausführen. Neue Tests für Roundtrip, Einzel-Lese-Timeout, Ablehnung ungültiger Payloads, Quell-/Paketdrift und unveränderte Normalfälle.
- [x] Vor Paketbildung Wire-/Zeitvertrag samt echten Quellbindungen unabhängig Astra/medium prüfen. Materielle Befunde zuerst korrigieren.
- [x] Danach Generator/Transportpins/Tests im frischen Kandidaten auf V6 binden, reproduzierbare Remoteprogramme nur erzeugen/kompilieren, nicht ausführen.
- [x] Echte erzeugte Module und Einstiegsantwort mit begrenzten synthetischen IO-Grenzen gegen dieselben Verträge prüfen; alle relevanten Kandidatentests, alte Belege und Paketgrößen verifizieren.
- [x] Abschließender Review derselben Astra-Rolle, Belegindex und knapper Wiederaufnahmestand. Erst danach separate konkrete native Vorprüfung bzw. Materialstartentscheidung vorbereiten.

## Prüfbefehle und Grenzen

`python -I -S -B verify_v6.py RED` muss belegte Assertions der fehlenden neuen Felder zeigen. Ein frischer GREEN-Beleg muss keine Fehler/Skips, unveränderte Eingangsbytes und null reale Prozess-/Netzwerkversuche melden. Weitere Läufe erhalten eigene Belegnamen; fehlgeschlagene Belege werden nicht ersetzt.

Historische Kernelwerte und ursprüngliche Fehlerursache bleiben unbekannt. Lokale Testantworten ersetzen weder echte Backend-/Kernelwirkung noch Plattform-, Mehrmandanten-, Last- oder Produktionsabnahme. Bei offenem Befund bleibt der Kandidat nicht ausführungsreif.

## Abschluss dieses lokalen Blocks

190 Tests,0 Fehler/Failures/Skips;126 eingefrorene Eintraege unveraendert. Unabhaengiger Astra/medium-Paketreview ohne Blocker. Das Paket ist lokal vorbereitet; native Vorpruefung und Materiallauf sind nicht erfolgt. Neue Materialfreigabe bleibt erforderlich.

Der neue Generator kodiert einzelne Helfer per stdlib-zlib, um die bestehende262144-Byte-Grenze einzuhalten. Eingabe32768/Modulrohdaten65536Bytes, exakte Laenge, EOF, Restdaten und SHA werden vor Kompilierung geprueft; keine unbeschraenkte Dekompression oder flush. Groesstes erzeugtes Programm146362Bytes.

Reviewbefund zum JSON-Pfad: Die lokale2000-Ebenenprobe wurde vor der Korrektur noch geparst; ein realer RecursionError wurde dabei hier nicht reproduziert. Jetzt wird jede Antworttiefe ueber16 abgewiesen und ein separat injizierter Parser-RecursionError sicher in ValueError ueberfuehrt. Ein urspruenglicher Testbeleg mit alter Gesamtantwort-Erwartung und ein AST-Testfixturefehler bleiben als nicht akzeptierte Belege erhalten.

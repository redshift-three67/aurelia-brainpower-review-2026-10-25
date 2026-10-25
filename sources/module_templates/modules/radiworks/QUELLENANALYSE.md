# RadiWorks — Quellenanalyse (Zusammenfassung)

**Vollanalyse:** `C:\Users\Hubert111\Documents\Radiworks\docs\FUNKTIONSANALYSE.md` (verbindlich, bytecode-verifiziert)
**Quell-Snapshot:** `C:\Users\Hubert111\Documents\Radiworks` (Git-Repo, Baseline `4555c9f6`, dekompilierte Quellen in `decompiled/`)

## Kompaktprofil

| Aspekt | Befund |
|---|---|
| Identität | AetherOnePi 2.2.0 (`de.isuret.polos`), digitale Radionik, Open Source |
| Original-Stack | Java 24, Processing-GUI, Javalin 6 REST+WS, Jackson, Lucene, Nitrite, Pi4J |
| Rollenbezeichnung in Aurelia | **„Werkbank"** (`module.tsx:40-48`) |
| Kernfunktionen | Hotbits-Entropie (4 Quellen + Fallbacks), Raten-Analyse (Hotbit-Statistik), General Vitality, Potenz-Analyse, Broadcast (GUI-Resonanzästhetik mit Fibonacci-Schwellen + Pi-LED-Hardware), Stick-Pad, Case/Session-Persistenz (JSON), Materia-Medica-Suche (1008 Clarke-JSONs, Lucene), Raten-DBs (TXT + Git `radionics-rates`), RadionicScript-Interpreter, Essential Questions (GV-Orakel), Card/Image/Area-Module |
| REST-Endpunkte Original | 12 Routen + WebSocket `/analysisUpdate/{id}` (siehe FUNKTIONSANALYSE §8) |
| kritische Quirks | Regex-Injection im Such-Highlighting; toter Nitrite-Pfad; doppelter Hotbits-Code (Handler vs. Client) — Port bereinigt dies, Verhalten bleibt äquivalent |

## Portierungsrelevanz (kurz)

- **Direkt portierbar (niedrig):** Analyse/GV/Potenz-Algorithmen, Case-JSON-Contract, Raten-TXT-Format, REST-Routen.
- **Mit Abstraktion (mittel):** Entropie-Provider-Kette (`/dev/hwrng`, Webcam, AMD-DLL, random.org, SecureRandom → `EntropyProvider`), Materia-Medica-Suche (Lucene → FTS), Broadcast-Ästhetik (Canvas/WebAudio).
- **Ersatzentfällt (bewusst):** GPIO-LED-Hardware (Pi) → simulated Broadcast-Events über WebSocket; optional späterer Hardware-Layer.

## Reifegrad

Stufe 0 ✅ (Quellgesichert) · Stufe 1 ✅ (Portierungsbasis: FUNKTIONSANALYSE + PORT_PLAN) → weiter mit Stufe 2 (Engine-Prototyp).


## Betriebs- und Nachweisnachtrag 03.10.2026

Sieben getrennte lokale Runtime-/Fall-Scopes auf 8103–8109 sind über Windows-Aufgaben eingerichtet; Entwicklung ab 8110. Der Wiederanlauf nach Anmeldung ist konfiguriert, die Windows-Warmstartprobe noch offen. Mehrere Aufträge pro Fall innerhalb derselben Engine sind dadurch nicht freigegeben. Peggotty-Duplikatlabels werden live mit HTTP 422 abgewiesen; fünf gezielte Regressionstests bestanden. GV-RE zählt identische nicht-null Raten-GV im vollständigen Ergebnis und ist kein zeitlicher Trend. Periodische GV-Verläufe benötigen vor Aktivierung eine geprüfte Fall-/Sitzungs-/Broadcast-Zuordnung und getrennte Entropie. Kamera/Stochastic-Langlauf und S4.8 bleiben offen. Maßgeblicher Bericht: `C:\Users\Hubert111\Documents\Brainpower\docs\verification\RADIWORKS_SIEBEN_INSTANZEN_CHAT_NETZWERK_2026-10-03.md`. Gemeinsame ABI, Host-/Mandantenautorität und Reifegradregeln werden durch diesen Nachtrag nicht geändert.

# Phase 9 – Innovationen für Echtzeitfunktionalität und Quantum-Framework

## Ziel dieses Abschnitts

Dies ist die vom Nutzer explizit angeforderte Diskussionsgrundlage für "sinnvolle, stabile, zukunftsfähige und professionelle Innovationen im Umgang mit Echtzeitfunktionalitäten und Quanteframeworks". Die Vorschläge bauen auf den Befunden aus `docs/deep-audit-2026-07-04/PHASE_7` (Hardware/Echtzeit) und `PHASE_8` (Quantum, dieser Ordner) auf und sind bewusst konservativ-professionell statt spekulativ gehalten. Nichts hiervon ist bereits umgesetzt – es handelt sich um Empfehlungen zur Besprechung.

## Leitprinzip

Der aktuell größte Reifegrad-Hebel ist nicht "mehr Hardware- oder Quanten-Features hinzufügen", sondern **ehrlich und maschinenlesbar sichtbar machen, was in jedem Pfad tatsächlich real, simuliert oder klassisch-approximiert ist** – für Operatoren, Entwickler und zukünftige Audits gleichermaßen.

## 1. "Reality Badge" / Capability-Truth-Layer für UI und API

**Problem:** `use_driver_layer=True`, `use_quantum=True` oder ein sichtbarer "⚛️ Quantum"-Log bedeuten heute nicht zuverlässig "diese Komponente wirkt real". GPU-Modulation ist laut Code-Kommentar CPU-simuliert; Quantum läuft in dieser Umgebung immer klassisch; Quartz ist deaktiviert.

**Vorschlag:** Ein einheitliches, dreistufiges Label für jede realtime-/quantum-relevante Komponente, das konsequent aus dem Code abgeleitet (nicht manuell gepflegt) wird:

- `REAL` – Hardware/Algorithmus wirkt nachweisbar wie benannt (z. B. CPU-Timing-Jitter, klassischer Grover-Fallback).
- `SIMULATED` – Software bildet den Effekt nach, ohne die benannte physische/algorithmische Grundlage (z. B. GPU-Modulation via CPU, WebSocket-Harmonisierung).
- `UNAVAILABLE` – Deklariert, aber inaktiv (z. B. Quartz, echte Quanten-Hardware, QAOA).

**Nutzen:** Direkt anschlussfähig an die bereits geplante `apps/web/hardware_truth.py` aus dem laufenden Operator-Workbench-Umbau (`Entwicklung/04_AKTIVE_UMSETZUNG_OPERATOR_WORKBENCH.md`) – dort ließe sich dasselbe Label-Prinzip 1:1 auch für den Quantum-Status übernehmen (`/api/synergy/status` liefert bereits `qiskit_available`/`mode`, das nur konsequent in dieselbe Badge-Sprache übersetzt werden müsste).

## 2. Quantum-Pfad regelmäßig tatsächlich verifizieren statt nur zu deklarieren

**Problem:** Der reale Grover-Circuit-Code wird in dieser Umgebung nie ausgeführt und ist durch keinen Testlauf verifiziert (siehe `PHASE_8`, Abschnitt 7).

**Vorschlag (konkret, kostenarm, kein Cloud-QPU nötig):**

1. Eine separate, optionale Test-/CI-Spur mit `pip install .[quantum]`, die gezielt `_build_grover_circuit`, `_apply_oracle`, `_apply_diffusion` sowie einen echten `Sampler.run(...)`-Aufruf auf kleinen synthetischen Item-Mengen (z. B. 8–16 Items) ausführt.
2. Diese Spur muss nicht bei jedem Commit laufen, aber mindestens regelmäßig (z. B. wöchentlich oder vor Releases), damit "vorhandener Code" nicht zu "unbemerkt kaputtem Code" wird.
3. Ergebnis dieser Spur explizit im Runtime-Manifest/Health-Report vermerken ("Quantum-Pfad zuletzt real verifiziert am …"), statt nur "Qiskit verfügbar: ja/nein" zu zeigen.

## 3. Ehrlicher Nutzenrahmen für echte Quantenhardware

**Fachliche Einordnung:** Grovers Suchvorteil ist `O(√N)` gegenüber `O(N)`. Bei den heute dokumentierten Größenordnungen (`~3.300`–`~8.000` Items, siehe `PHASE_8`, Abschnitt 8) liegt die klassische Suche bereits im Sub-Sekunden-Bereich; ein `√N`-Vorteil auf Cloud-QPU-Hardware (aktuell NISQ-Geräte mit Rauschen, Warteschlangenzeiten und Netzwerklatenz) wäre **langsamer in der Wanduhrzeit**, nicht schneller. Ein Vorteil würde erst bei sehr viel größeren, kombinatorisch expandierenden Suchräumen relevant (z. B. tatsächlich Milliarden ungefilterter Kombinationen ohne Pre-Filter, was `hybrid_engine.py` aktuell ohnehin klassisch vermeidet).

**Empfehlung:** Die Produktkommunikation sollte "quantum-ready Architektur" und "quanteninspirierte Heuristik" von "operativer Quantenbeschleunigung" sprachlich klar trennen. Eine echte QPU-Anbindung (IBM Quantum Runtime, AWS Braket) ist als **Forschungsoption**, nicht als kurzfristige Roadmap-Priorität sinnvoll – die Kosten-Nutzen-Rechnung spricht bei aktueller Datenmenge dagegen.

## 4. Speicher-/OpenBLAS-Robustheit als Realtime-Voraussetzung

**Problem (heute live reproduziert, siehe `README.md` dieses Ordners):** numpy/SciPy-lastige Pfade brechen unter Host-Speicherdruck mit einer kryptischen `OpenBLAS error: Memory allocation still failed after 10 retries, giving up.`-Meldung ab, ohne Vorabprüfung, Backoff oder verständliche Nutzer-Fehlermeldung.

**Vorschlag:**

1. Ein leichter Preflight-Speichercheck (z. B. über `psutil`, das bereits Projektabhängigkeit ist) vor rechenintensiven Scans/Harmonisierungsläufen, der bei kritisch wenig freiem RAM eine klare, verständliche Warnung statt eines rohen BLAS-Stacktraces ausgibt.
2. Optionales Pinning von `OPENBLAS_NUM_THREADS`/`OMP_NUM_THREADS` auf einen konservativen Wert für CLI-Subprozesse, um Thread-Explosion bei vielen parallelen Kurzprozessen zu vermeiden (relevant für den produktiven Top-N-Pfad, der pro Profil eigene Subprozesse startet).
3. Dieser Preflight-Check passt inhaltlich exakt in die ohnehin geplante `hardware_truth.py`-Schicht der Operator Workbench – Speicherstatus ist eine Hardware-Wahrheit wie CPU/RAM/GPU-Status.

## 5. Event-Contract statt Text-Parsing für Echtzeit-Fortschritt

Ergänzt `PHASE_5` (07-04), Vorschlag 1, spezifisch für die Realtime-Kanäle: `apps/web/emf.py` und `apps/web/scan_live.py` bieten bereits WebSocket-Endpunkte, werden aber laut `PHASE_7` (07-04) im Haupt-UI kaum genutzt – die Web-Shell pollt stattdessen über HTTP und parst CLI-Stdout-Text (`apps/web/scan_jobs.py:29-151`). Ein strukturiertes Event-Schema (Scan-Fortschritt, Substep, Fehler, Harmonisierungs-Tick) über den bereits vorhandenen WebSocket-Kanal auszuspielen, ersetzt fragiles String-Parsing durch robuste, versionierbare Events und macht "Echtzeit" auch im Frontend tatsächlich echtzeitfähig statt Polling-basiert.

## 6. Gestufte Realtime-Kopplungsstufen statt binärem "Driver Layer an/aus"

Aufbauend auf `PHASE_7` (07-04), Abschnitt 7 ("Driver Layer ist eher Telemetrie als harte Steuerung"):

| Stufe | Bedeutung | Heutiger Stand |
| --- | --- | --- |
| Tier 0 – Telemetrie | Hardware wird gelesen/protokolliert, beeinflusst aber keine Analyseentscheidung | größtenteils aktueller Ist-Zustand |
| Tier 1 – Weich gekoppelt | Hardware-Signal fließt als Gewichtungs-/Kontextfaktor in Berechnung ein (z. B. EMF-Index, CPU-Jitter als Entropiequelle) | teilweise real (CPU, EMF) |
| Tier 2 – Hart gekoppelt | Hardware-Signal mit definierter Latenzgarantie/Reihenfolge zwingend Teil des Ergebnispfads | aktuell nicht vorhanden |

**Nutzen:** Diese explizite Stufung verhindert, dass Begriffe wie "Driver Layer" oder "Realtime" mehr versprechen, als der jeweilige Pfad hält, und gibt eine nachvollziehbare Zielarchitektur für schrittweisen Ausbau vor, ohne sofort "harte Realtime" (mit Latenzgarantien) versprechen zu müssen, die aktuell weder gebraucht noch vorbereitet ist.

## 7. Artefakt-Provenienz inklusive Quantum-/Hardware-Wahrheit

Erweiterung von `PHASE_5` (07-04), Vorschlag 7: Jedes Report-/Synergy-Artefakt sollte neben Zeitstempel/Session auch festhalten, mit welchem Wahrheitsgrad (`REAL`/`SIMULATED`/`UNAVAILABLE` aus Vorschlag 1) es erzeugt wurde – z. B. "Synergy-Ergebnis mit `mode: classical` erzeugt", "Harmonisierung mit `gpu: simulated` gelaufen". Das macht historische Berichte auch Monate später noch korrekt interpretierbar, statt implizit vorauszusetzen, dass der damalige Hardware-/Quantenzustand bekannt ist.

## 8. Priorisierungsvorschlag für die gemeinsame Besprechung

1. Reality-Badge-Prinzip (Vorschlag 1) – geringer Aufwand, hoher Vertrauens- und Klarheitsgewinn, passt in laufenden Workbench-Umbau.
2. Speicher-/OpenBLAS-Preflight (Vorschlag 4) – behebt ein heute akut reproduziertes Stabilitätsproblem.
3. Event-Contract für Realtime-Kanäle (Vorschlag 5) – Voraussetzung für alles Weitere im Realtime-Bereich.
4. Quantum-Verifikationsspur (Vorschlag 2) – schließt eine konkrete, unauffällige Testlücke.
5. Gestufte Realtime-Kopplung (Vorschlag 6) und Artefakt-Provenienz (Vorschlag 7) – mittelfristige Architekturarbeit.
6. Echte QPU-Anbindung – bewusst zurückgestellt, siehe Vorschlag 3.

## Schlussbemerkung

Keiner dieser Vorschläge erfordert, bestehende fachliche Substanz (Resonanzmodell, Bruce-Copen-Heuristik, Scan-Pipeline) zu verwerfen. Sie zielen ausschließlich darauf ab, das bereits vorhandene Echtzeit- und Quantum-Fundament ehrlicher sichtbar, robuster unter Last und leichter vertrauenswürdig auditierbar zu machen.

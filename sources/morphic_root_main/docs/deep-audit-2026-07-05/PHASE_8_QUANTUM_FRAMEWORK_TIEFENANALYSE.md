# Phase 8 – Quantum-Framework Tiefenanalyse

## Ziel dieses Abschnitts

`core/quantum_synergy/*` wurde in `docs/deep-audit-2026-07-04/PHASE_1` nur als "zentral" gelistet, aber nicht inhaltlich geprüft. Diese Phase schließt genau diese Lücke: Was ist real Quantum-Code, was ist "quanteninspiriert", was läuft in dieser Umgebung tatsächlich, und wo weicht Dokumentation vom Code ab.

## Kurzfazit

`core/quantum_synergy` enthält echten, syntaktisch korrekten Qiskit-2.x-Code für einen Grover-Suchalgorithmus – aber in der aktuell genutzten `.venv` ist Qiskit **nicht installiert**, wodurch jede Ausführung faktisch immer den klassischen Fallback-Pfad nimmt. Zusätzlich beschreibt die modulinterne `ARCHITECTURE.md` eine `qaoa_optimizer.py`-Komponente, die im Dateisystem **nicht existiert**. Das Framework ist damit ehrlich beschrieben: "quantum-ready", aber aktuell nicht quantum-operativ.

## 1. Reale Modulstruktur

| Datei | Rolle | Vorhanden |
| --- | --- | --- |
| `__init__.py` | Exportiert `QuantumSynergyEngine`, `get_item_database`, `ItemDatabase`, `SynergyCalculator` | ja |
| `grover_search.py` | Echte Grover-Circuit-Implementierung + klassischer Fallback | ja |
| `hybrid_engine.py` | Orchestriert Pre-Filter → Quantum/Quantum-inspired-Suche → Ranking | ja |
| `synergy_core.py` | Klassische Synergy-Score-Formel (Resonanz, Frequenzharmonie, Fokus-Relevanz) | ja |
| `database_manager.py` | Lädt/cached Items aus `core/subgroups/procedural_groups` | ja |
| `cache/items_cache.json` | Persistenter Item-Cache | ja |
| `ARCHITECTURE.md` | Architektur-Dokumentation | ja, aber driftend (siehe 3.) |
| `README.md` | Nutzungsanleitung | ja |
| `qaoa_optimizer.py` | In `ARCHITECTURE.md:24-28` als eigenes Modul beschrieben ("QAOA Implementation") | **nein – existiert nicht** |

Verifiziert per `grep` über das gesamte Repository: kein Treffer für `qaoa`/`QAOA` in irgendeiner `.py`-Datei. Der Begriff kommt ausschließlich in Dokumentation vor (`ARCHITECTURE.md`, `docs/archive/GROVER_LLM_SYNERGY_EMPFEHLUNGEN.md`, `docs/archive/QUANTUM_SYNERGY_STATUS.md` als "nächster Schritt" vom 2025-11-16).

## 2. Historische Einordnung (Dokumentationsspur)

`docs/archive/QUANTUM_SYNERGY_STATUS.md` (Stand `2025-11-16`) listete "Echte Quantum-Implementation (Qiskit, Grover, QAOA)" explizit als **empfohlene nächste Erweiterung**, nicht als vorhandenes Feature. Der heutige `grover_search.py` ist die Einlösung des Grover-Teils dieser Ankündigung. Der QAOA-Teil wurde nie umgesetzt, aber bereits in `ARCHITECTURE.md` so beschrieben, als existiere er. Das ist ein in sich konsistentes Muster mit den in `PHASE_0`/`PHASE_5` (07-04) beschriebenen Dokumentationsdrift-Befunden – hier eben lokal im Quantum-Modul statt projektweit.

## 3. Grover-Implementierung im Detail (`grover_search.py`)

### Was real ist

- Import-Guard mit `try/except ImportError`, kompatibel zu Qiskit 2.x (`qiskit.primitives.StatevectorSampler`, Fallback `Sampler`).
- Baut einen echten Circuit: Hadamard-Superposition → `n_iterations`-mal (Oracle + Diffusion) → Messung.
- Oracle: X-Gates zur Ziel-Zustands-Kodierung, Multi-Controlled-Z via `mcx` + `h` (Standard-Textbuch-Konstruktion), danach X-Gates zurück.
- Diffusion-Operator: klassische Grover-Diffusion (`H`, `X`, `MCZ`, `X`, `H`).
- Iterationszahl nach der Standardformel `⌊π/4 · √(N/M)⌉`, künstlich auf `1..10` begrenzt (`_optimal_iterations`).
- `n_qubits = ceil(log2(n_items))` – korrekt skaliert mit der Itemanzahl im Suchraum.

### Wo die Grenzen liegen

- Es handelt sich um einen **Simulator-Pfad** (`Sampler`/`StatevectorSampler` aus `qiskit.primitives`), nicht um Anbindung an echte Quantenhardware (kein IBM-Quantum-Runtime-Provider, kein AWS-Braket-Client im Code).
- Marked-States (`marked_states`) werden **klassisch** vorab berechnet (`oracle_func(item)` wird in Python für jedes Item ausgewertet), bevor der Circuit gebaut wird. Der eigentliche Suchraum-Vorteil von Grover (Oracle als Black-Box-Schaltung) wird damit didaktisch korrekt simuliert, aber der klassische Vorab-Schritt selbst ist bereits `O(N)` – der Aufbau des Circuits ist nicht "quanten-nativ unwissend" über die Lösung.
- Bei einem `Exception` während der Circuit-Ausführung greift automatisch `_classical_fallback` (Score/10 als Pseudo-Wahrscheinlichkeit).

### Laufzeitrealität in diesem Workspace (heute verifiziert)

```
> .venv\Scripts\python.exe -c "import qiskit"
ModuleNotFoundError: No module named 'qiskit'
```

- `requirements.txt:27` führt `qiskit>=1.0` nur **auskommentiert**.
- `pyproject.toml` führt `qiskit` nur als optionales Extra (`[project.optional-dependencies] quantum = ["qiskit>=1.0"]`), das nie installiert wurde.
- Damit gilt für diese Entwicklungsumgebung durchgängig: `QISKIT_AVAILABLE == False`.

**Konsequenz:** Der komplette Grover-Circuit-Code (`_build_grover_circuit`, `_apply_oracle`, `_apply_diffusion`) wird in dieser Umgebung **nie ausgeführt**. Er ist vorhanden, lesbar und plausibel korrekt, aber lokal unverifiziert (kein Testlauf, kein CI-Lauf mit echtem Qiskit gefunden).

## 4. Hybrid-Engine (`hybrid_engine.py`)

### Ablauf

1. **Pre-Filtering (klassisch):** `_classical_prefilter` reduziert die Item-Datenbank auf die relevantesten `prefilter_size` (Default `200`) Items nach Scan-Ergebnis- und Fokus-Score. Wenn `scan_results` übergeben wird, wird zusätzlich auf die im aktuellen Scan vorkommenden Labels eingeschränkt.
2. **Suche:**
   - Falls `use_quantum and QISKIT_AVAILABLE`: `_real_quantum_search` (nutzt `GroverRemedySearch`).
   - Sonst: `_quantum_inspired_search` – eine **klassische** Kombinatorik-Iteration über `itertools.combinations`, die ab `>10.000` möglichen Kombinationen auf zufälliges Sampling umschaltet (`_sample_combinations`). Das ist eine nachvollziehbare Heuristik, aber kein Quantenalgorithmus – der Name "quanteninspiriert" bezieht sich auf die Idee der Amplitudenverstärkung guter Lösungen, nicht auf eine tatsächliche Superposition.
3. **Ranking:** `SynergyCalculator.rank_combinations` sortiert nach Synergy-Score.
4. **Detailanreicherung:** je Kombination werden Zusatzdetails berechnet.

### Kritischer Punkt

`QuantumSynergyEngine(use_quantum=True)` (Default und auch der Aufrufparameter in `apps/cli/workflow/step09_quantum.py:22`) bedeutet **nicht** "nutzt garantiert Quantum" – die Klasse selbst degradiert intern über `self.use_quantum = use_quantum and QISKIT_AVAILABLE` (`hybrid_engine.py:30`). Der Aufrufer kann diesen stillen Fallback nicht ohne Weiteres unterscheiden, außer er inspiziert `engine.use_quantum` oder den Log-Output (`"[2/4] ⚛️ ECHTE Quantum-Suche"` vs. `"[2/4] Quantum-inspirierte Suche (klassisch)"`).

## 5. Synergy-Score-Formel (`synergy_core.py`)

Rein klassische, deterministische Formel:

```
synergy_score = w_individual · Einzelwirkung
              + w_resonance  · Resonanzverstärkung (Bruce-Copen-Prinzip)
              + w_harmony    · Frequenzharmonie (Phi-Verhältnis, Schumann-Resonanz-Obertöne)
              + w_relevance  · Fokus-Relevanz (inkl. Synonym-/Multi-Fokus-Erweiterung)
```

Die Gewichte (`weights`) sind entweder Standardwerte oder kommen fokusabhängig aus `core/adaptive_weights.get_adaptive_weights(focus)`.

**Fachliche Einordnung (technisch, wertfrei):** Resonanzverstärkung nach "Bruce Copen" sowie Frequenzharmonien zur Schumann-Resonanz sind Konzepte aus dem Bereich alternativer/esoterischer Energiemedizin, keine im Sinne der Physik gemessenen oder validierten Effekte. Der Code implementiert diese Konzepte konsistent und deterministisch als Bewertungsheuristik – das ist technisch sauber, aber die Grundlage der Formel selbst ist ein Domänen-/Weltbild-Constraint des Produkts und keine verifizierbare Naturkonstante. Das ist für Sicherheits-/Compliance-Betrachtungen relevant, falls Ergebnisse gegenüber Endnutzern als "wissenschaftlich gemessen" statt "modellbasiert" kommuniziert würden.

## 6. Integrationspunkte im Gesamtsystem

| Einstieg | Datei | Nutzung |
| --- | --- | --- |
| CLI `scan synergy` bzw. `--synergy` | `apps/cli/commands/synergy.py:37,55,174,182` | instanziiert `QuantumSynergyEngine`, reicht `quantum`-Flag durch |
| 12-Step-Workflow Step 9 | `apps/cli/workflow/step09_quantum.py:20-22` | ruft `QuantumSynergyEngine(use_quantum=True)` fest verdrahtet auf; Fehler werden pro Step abgefangen (`state.add_error(9, ...)`) |
| Web-API | `apps/web/synergy.py` | `GET /api/synergy/status` (liefert `qiskit_available`/`mode`), `POST /api/synergy/optimize`, `GET /api/synergy/stats` |

Der produktive Top-N-Scan-Pfad (`scan top3-scan`, siehe `PHASE_2` in 07-04) nutzt Quantum-Synergy nur optional über das `--synergy`-Flag, ist also nicht zwingend im Hauptpfad.

## 7. Testabdeckung

- `tests/test_quantum_synergy.py` (5 Tests): prüft `QISKIT_AVAILABLE`-Typ, klassischen Fallback, Oracle-Matching, `/api/synergy/status`, Auto-Detect von `use_quantum`.
- `tests/exploratory/test_quantum_synergy.py`: zusätzlicher explorativer Test außerhalb der Standardsuite (`norecursedirs` schließt `tests/exploratory` in `pyproject.toml:46` von der Standard-Testsammlung aus).

**Wichtiger Befund:** Da `QISKIT_AVAILABLE` in dieser Umgebung `False` ist, testet `test_grover_classical_fallback_returns_results` ausschließlich den `if not QISKIT_AVAILABLE:`-Zweig. Der echte Quanten-Circuit-Pfad (`_build_grover_circuit` inkl. Oracle/Diffusion-Gates und `Sampler.run(...)`) ist **im gesamten Repository durch keinen einzigen tatsächlich ausgeführten Test verifiziert** – weder lokal noch nachweislich in einer CI (es wurde keine CI-Konfiguration im Repository gefunden, siehe `PHASE_5` in 07-04). Das ist ein konkretes, bisher nicht dokumentiertes Risiko: Der "echte Quantum"-Code-Pfad ist unverifizierter Code in Produktion.

## 8. Skalierbarkeitsbehauptung vs. verifizierter Stand

`ARCHITECTURE.md:94` behauptet "Skaliert bis 10.000+ Items". `docs/archive/QUANTUM_SYNERGY_STATUS.md` (2025-11-16) dokumentiert dazu handfeste Benchmark-Zahlen für `200`–`3.324` Items. Der aktuelle Live-Datenbestand von `ItemDatabase` konnte in dieser Sitzung wegen der akuten Host-Speicherknappheit (siehe `README.md` dieses Ordners) nicht mehr neu ausgeführt werden; als Referenzgröße liegt weiterhin nur der Stand vom 2025-11-16 vor (`3.324` Items / `277` Gruppen). Die "10.000+"-Aussage ist damit aktuell **nicht durch einen frischen Lauf verifiziert**, sondern eine Skalierungserwartung.

## 9. Gesamtbewertung

| Aspekt | Bewertung |
| --- | --- |
| Code-Qualität des Grover-Pfads | solide, lehrbuchkonform, Qiskit-2.x-API-kompatibel |
| Tatsächliche Quanten-Ausführung in dieser Umgebung | nie – `qiskit` fehlt, reiner Fallback-Betrieb |
| Testabdeckung des echten Quanten-Pfads | keine |
| Dokumentation vs. Code | driftend (`qaoa_optimizer.py` dokumentiert, aber nicht vorhanden) |
| Fachlicher Nutzen der Grover-Suche bei aktueller Itemzahl (~3.300–8.000) | fraglich, siehe `PHASE_9`, Abschnitt 3 |
| Robustheit des Fallback-Verhaltens | gut – sauberer, getesteter klassischer Pfad, transparente Statusmeldung über `/api/synergy/status` |

Die ehrlichste Beschreibung des heutigen Zustands lautet: **"Quantum-ready classical system"** – die Architektur ist bereit für echtes Quantum-Computing, betreibt es aber aktuell nicht, und die eine dokumentierte Zusatzkomponente (QAOA) existiert nur als Ankündigung.

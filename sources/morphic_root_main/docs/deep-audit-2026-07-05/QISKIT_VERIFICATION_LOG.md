# Qiskit-Verifizierungslogbuch

> Zweck (Task 4 des Plans
> `docs/superpowers/plans/2026-07-05-morphic-v1-radiquant4-alignment.md`):
> ein Langzeitdokument, das dokumentiert, dass und wann der *echte*
> Qiskit-Quanten-Circuit-Pfad in `core/quantum_synergy/grover_search.py`
> (nicht nur der klassische Fallback) mindestens einmal end-to-end
> verifiziert wurde. Schliesst die in
> `docs/deep-audit-2026-07-05/PHASE_8_QUANTUM_FRAMEWORK_TIEFANALYSE.md`
> dokumentierte Luecke ("Real-Pfad nie ausgefuehrt/kein Test").

## Verifizierungslauf 1

- **Datum:** `2026-07-06`
- **Isolierte Umgebung:** `C:\morphic_v1\.venv-quantum-check` (separates
  Venv, *nicht* das shared dev `.venv` - gezielt so angelegt, um die
  bestaehende Testumgebung nicht zu destabilisieren; nicht Teil des
  produktiven Projekts, nur fuer Verifikationszwecke).
- **qiskit-Version:** `2.5.0`
- **Python:** `3.12.10` (CPython, Windows-10.0.19045)
- **Verifiziertes Modul:** `core.quantum_synergy.grover_search.GroverRemedySearch`
- **Aufrufskript:** `.quantum_check.py` (Ad-hoc-Verifikationsskript,
  bewusst nicht Teil der regulaeren Testsuite; wird manuell entfernt,
  nachdem es ausgewertet wurde).
- **Testszenario:** 8 Items, Oracle markiert *genau 1* Item (`item5`),
  4000 Shots. Bei korrektem Grover-Verstaerkungsverhalten muss das
  markierte Item das Top-Ergebnis sein.
- **Ergebnis:** `OK`
  - `QISKIT_AVAILABLE = True` im isolierten Venv
  - Top-Ergebnis: `item5` mit `94.38%` Wahrscheinlichkeit
  - Alle anderen Items bei unter `1%`
  - Real-Pfad laeuft end-to-end durch: Circuit-Aufbau
    (`_build_grover_circuit`), Oracle-Konstruktion (`_apply_oracle`),
    Diffusion (`_apply_diffusion`), `StatevectorSampler.run(...)`,
    Bitstring->Index-Mapping, Wahrscheinlichkeitsberechnung, Ranking
- **Folgerung:** Der in `PHASE_8` als "unverifiziert" markierte Real-Pfad
  ist mit `qiskit>=1.0` tatsaechlich lauffaehig und *fachlich korrekt*
  fuer den Standardfall (einzelne markierte Zustaende).

### Nebenbefund (kein Blocker, nur dokumentiert)

Bei einem frueheren, weniger scharfen Test (4 von 8 Zustaenden markiert
durch den score-basierten `create_focus_oracle`-Schwellwert) war das
Top-Ergebnis *nicht* eines der markierten Items. Das ist kein Bug des
Grover-Circuits, sondern eine numerische Eigenheit: wenn genau die
Haelfte aller Zustaende markiert ist (`N/2` markierte von `N`), ist die
optimale Grover-Iteration-Zahl `⌊π/4 · √(N/M)⌉ = ⌊π/4 · √2⌉ ≈ 1`, und die
Amplitudenverstaerkung verteilt sich statistisch ueber alle markierten
Zustaende, ohne ein einzelnes klar zu bevorzugen - das ist erwartetes
Grover-Verhalten, kein Implementationdefekt. Der scharfe Einzelmarkierungsstest
oben bestaetigt, dass die Amplitudenverstaerkung im Normalfall korrekt wirkt.

## Was als naechstes sinnvoll waere (Follow-up, ausserhalb Task 4)

- Den isolierten Qiskit-Pfad als separate, woechentliche/Release-Gate
  CI-Spur etablieren (statt nur einmalig manuell), damit Regressionen
  am Real-Pfad nicht unbemerkt bleiben.
- Den Test `tests/test_quantum_real_path.py` (in diesem Task erstellt)
  so erweitern, dass er bei verfuegbarem Qiskit auch *Ranking*-Assertions
  enthaelt, nicht nur "laeuft ohne Absturz".
- Optional: `qiskit` mit einer festen Version pinnen (`qiskit>=1.0,<3.0`
  in `pyproject.toml [project.optional-dependencies] quantum`), um
  semver-major-Spruenge in kuenftigen Releases abzufangen.

# Phase 4 – JSONL-Progress-Gate

`core/compliance/progress_events.py` erzeugt eine additive JSONL-Schicht aus einer strikten Allow-list: Job-ID, Status, Exitcode, Zeitstempel, Fortschritt, Phase, Substep und abgeschlossene Substeps. Commands und stdout/stderr werden nie serialisiert.

`tests/test_progress_events.py` bestätigt den synthetischen JSONL-Eintrag und die Abwesenheit eines Klarnamens. Die Schicht ist nicht an `LocalScanJobService` oder die UI verdrahtet; stdout bleibt unverändert der aktuelle Fallback.

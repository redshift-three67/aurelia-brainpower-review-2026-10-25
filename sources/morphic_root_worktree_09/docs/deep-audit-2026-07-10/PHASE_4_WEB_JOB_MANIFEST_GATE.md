# Phase 4 – Gate 4: Synthetisches Web-Jobmanifest

`core/compliance/web_job_manifest.py` ist eine unverdrahtete, atomare
Testschicht für redigierte Web-Jobmetadaten. Sie speichert Job-ID, Status,
Exitcode, Owner/Tenant, Zeitstempel und deklarierte Logpfade. Beim bekannten
`top3-scan`-Command werden alle Argumente nach dem Kommando redigiert.

Der Test verwendet ausschließlich `tmp_path`, bestätigt die Redaction und
belegt, dass `recover_read_only()` die Persistenzdatei nicht verändert.

Nicht geändert: `LocalScanJobService`, FastAPI, produktive Joblogs, Scanpfade
oder Reports. Eine Runtime-Anbindung bleibt ein späteres, separates Gate.

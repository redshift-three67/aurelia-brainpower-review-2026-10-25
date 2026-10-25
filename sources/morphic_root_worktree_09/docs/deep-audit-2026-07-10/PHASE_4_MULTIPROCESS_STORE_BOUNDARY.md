# Phase 4 – Mehrprozess- und Store-Grenze

**Status:** Entscheidung dokumentiert; keine Runtime-Anbindung implementiert.
**Betriebsprofil:** Variante A, lokaler Einoperator auf Loopback. Diese Grenze ist
keine Freigabe für Mehrprozess-, Mehrbenutzer- oder Netzwerkbetrieb.

## 1. Nachgewiesener Ist-Zustand

| Komponente | Persistenz-/Synchronisationsmodell | Nachgewiesene Grenze |
|---|---|---|
| `apps/web/scan_jobs.py:LocalScanJobService` | `_jobs` ist ein In-Memory-`dict`; `threading.Lock` schützt Zugriffe nur im aktuellen Prozess. stdout/stderr liegen als Dateien vor. | Nach App-Neustart oder zweitem Worker ist keine Job-Registry vorhanden. Ein zweiter Prozess kann keine Jobs des ersten Prozesses abfragen oder deren Lock teilen. |
| `apps/web/main.py:create_app` | Erzeugt standardmäßig einen neuen `LocalScanJobService(job_root)` pro App-Prozess. | Es gibt keine App-Start-Recovery und keinen persistenten Job-Store. Der Jobstart übergibt derzeit nur `owner_id`; `tenant_id` wird nicht an `LocalScanJobService` persistiert. |
| `apps/web/workbench_runtime.py:WorkbenchRuntimeStore` | JSON-Dateien mit temporärer Datei und `replace()`; `threading.RLock` nur im aktuellen Prozess. | Atomarer Einzeldatei-Ersatz ist kein Mehrprozess-Lock. Gleichzeitige Prozesse können einander beim Read-modify-write überschreiben. Beschädigtes JSON wird derzeit als leerer Default geladen. |
| `core/compliance/web_job_manifest.py:WebJobManifestStore` | Synthetische JSON-Datei mit atomarem `replace()`. | Nicht an FastAPI oder `LocalScanJobService` verdrahtet; kein Interprozess-Lock, keine Recovery-Policy für beschädigte Dateien. |
| `core/compliance/progress_events.py:append_progress_event` | Append einer JSONL-Zeile. | Nicht an Runtime/UI verdrahtet; kein Lock und keine Mehrwriter-/Zeilenintegritätsgarantie. |
| `core/compliance/run_manifest*.py` | Reiner Builder, explizite Hashquellen und Post-success-Writer. | Nicht an Scan, Reportwriter oder Runtime angeschlossen; kein Produktivlauf erzeugt derzeit ein Run-Manifest. |

Die bereits vorhandenen Tests belegen nur die jeweiligen isolierten,
synthetischen Eigenschaften: atomare Einzeldateischreibvorgänge,
Redaction/Allow-list und Thread-Serialisierung im selben Python-Prozess.
Sie belegen weder Recovery nach Prozessabsturz noch Prozess-übergreifende
Konsistenz.

## 2. Entscheidung

1. `LocalScanJobService` bleibt bis zu einem separaten Gate ausdrücklich ein
   **ephemerer Single-Process-Store**. `threading.Lock` wird nicht als
   Mehrprozess- oder Restart-Schutz interpretiert.
2. JSON-, JSONL- und Manifest-Hilfen bleiben **unverdrahtete synthetische
   Vorstufen**. Sie werden weder beim Jobstart/-status noch beim App-Start
   automatisch gelesen oder geschrieben.
3. stdout/stderr bleibt der unveränderte aktuelle Fortschritts- und
   Diagnosepfad. Die UI erhält keine JSONL-Präferenz, bevor ein eigener
   Fallback-Nachweis existiert.
4. Es gibt keine echte Job-Recovery. Nach Prozessende ist unbekannt, ob ein
   früherer Kindprozess noch lebt; ein neuer App-Prozess darf deshalb keine
   In-Memory-Jobs als recovered darstellen.
5. Eine künftige Store-Entscheidung muss einen eindeutig autoritativen,
   prozesssicheren Store festlegen (zum Beispiel eine transaktionale lokale
   Datenbank mit dokumentierter Lock-/Recovery-Semantik). Ein bloßer
   `threading.Lock`, Datei-`replace()` oder JSONL-Append genügt nicht.

## 3. Vorbedingte RED-Gates für jede spätere Runtime-Anbindung

Vor einer Verdrahtung sind separate RED-Tests erforderlich; erst nach ihrem
nachgewiesenen Fehlschlag darf eine minimale GREEN-Implementierung folgen.

| Risiko | Erforderlicher Testnachweis |
|---|---|
| PII-/Command-Leak | Persistierter Job-/Event-/Run-Datensatz enthält weder Klartext-Argumente noch stdout/stderr, Fokus, Bildpfade, Namen oder Geburtsdaten. Redaction muss auch unbekannte Command-Formen fail-closed behandeln. |
| Owner-/Tenant-Policy | Jobstart, Status, Recovery und Ergebniszugriff akzeptieren nur serverseitig abgeleitete Owner-/Tenant-Werte; falscher Owner/Tenant und ownerlose Legacydaten sind explizit getestet. |
| Prozessabsturz | Neustart nach gestarteten, laufenden, erfolgreichen und fehlgeschlagenen Kindprozessen unterscheidet belegbar zwischen recoverable metadata und unbekanntem Prozesszustand, ohne doppelte Ausführung. |
| Fehlende/beschädigte Storedatei | Start und Read-only-Recovery haben eine explizite Fail-closed-/Quarantäneentscheidung; sie dürfen beschädigte Daten nicht stillschweigend als leeren, erfolgreich recovered Store behandeln. |
| Mehrprozesszugriff | Zwei getrennte Prozesse testen konkurrierenden Start, Status-Update und Abschluss ohne Lost Update, doppelte Job-ID oder teilgeschriebenen Datensatz. |
| Event-/stdout-Fallback | Die UI bevorzugt nur vollständig valide, autorisierte Events; bei fehlender, leerer oder fehlerhafter Eventquelle bleibt der bestehende stdout-Fallback funktionsgleich. |
| Laufmanifest | Manifest entsteht ausschließlich nach erfolgreichem Lauf mit Exitcode 0, enthält nur pseudonyme Identifikatoren und explizite Hashquellen; Score, Launcher-Argumente und Legacy-Exporte bleiben äquivalent. |

## 4. Nicht mit diesem Gate erledigt

Dieses Dokument implementiert keine Runtime-Anbindung, keine Datenbank,
keine Recovery, keine UI-Änderung und keine Migration. Der Phase-4-Abschluss
bleibt offen, bis Restart-Smoke, Event-/Fallback-Test, Reporthashvergleich und
Vollsuite für eine später ausdrücklich freigegebene Implementierung real grün
sind.

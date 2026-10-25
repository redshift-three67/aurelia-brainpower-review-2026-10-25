## Zweites adversariales Freeze-v16-Review

**Verdikt: REQUEST CHANGES**  
**Konfidenz: HOCH**  
**Befunde:** `P0=0, P1=1, P2=1, P3=0`  
**Scope-Drift:** `0`

### Befunde

| Priorität | Befund | Ort |
|---|---|---|
| **P1** | Die Windows-Signalgrenzen bleiben PID-Reuse-/TOCTOU-gefährdet. Nach einer Creation-Time-Vorprüfung beziehungsweise einem `poll()` wird `taskkill /PID` mit der numerischen PID aufgerufen. Endet der Supervisor zwischen Prüfung und `taskkill` und wird seine PID wiederverwendet, kann ein fremder Prozessbaum beendet werden. Der Rollback-Pfad besitzt nicht einmal die strikte Identitätsprüfung. | `apps/web/scan_jobs.py:634-647`, `apps/web/scan_jobs.py:946-992` |
| **P2** | Die neue strikte Hilfsfunktion ist nicht als vollständige Verhaltensmatrix getestet: keine direkten Verträge für `NoSuchProcess`, `ProcessLookupError`, `OSError(ESRCH)`, Nicht-`ESRCH`, lesbaren Mismatch und fehlende erwartete Identität; ebenso fehlt ein Windows-Test für Exit/PID-Reuse zwischen Vorprüfung und `taskkill`. | `apps/web/scan_jobs.py:280-295`, `tests/test_web_scan_jobs.py:699-828` |

### P1 – Windows-Signalisierung ist nicht an ein stabiles Prozess-Handle gebunden

Im normalen Stop-Pfad geschieht:

1. `job.process.poll()` meldet den Supervisor aktiv.
2. `_strict_process_identity_matches()` bestätigt dessen Creation Time.
3. Der Supervisor endet unmittelbar danach.
4. Windows kann die numerische PID wiederverwenden.
5. `taskkill /PID <pid> /T /F` löst die PID erneut auf und kann den neuen, fremden Prozessbaum treffen.

Der Start-Rollback ist noch schwächer: Nach `process.poll()` folgt direkt das numerische `taskkill`, ohne strikte Creation-Time-Revalidierung. Die POSIX-Seite verwendet dagegen `pidfd` und schließt Handles systematisch.

**Erforderliche Korrektur:** Auch auf Windows muss die finale Beendigungsgrenze an die bereits geöffnete Prozess-/Job-Handle-Autorität gebunden sein. Eine Creation-Time-Prüfung vor einem späteren numerischen `taskkill` beseitigt das Check-to-use-Fenster nicht.

### Test- und Persistenzprüfung

Die vorhandenen v16-Tests belegen tatsächlich:

- bei post-open `AccessDenied` und `OSError(EIO)` **null Signale** (`sent == []`);
- **exakt einmaliges** Schließen des Supervisor-Handles (`closed.count(100) == 1`);
- `authority_ambiguous` sowohl im Speicher als auch in der dauerhaft neu gelesenen State-Datei;
- vollständige Handle-Cleanup-Versuche trotz einzelner Close-Fehler;
- durable Veröffentlichung über Temp-Datei, Datei-`fsync`, atomaren Replace/Move mit Write-through und POSIX-Parent-Directory-`fsync`;
- Erhalt vorheriger Authority-Bytes bei Publish-Fehlern.

Diese Assertions schließen jedoch weder die fehlenden direkten Tri-State-Zweige noch das Windows-TOCTOU-Fenster.

### Übriger Produkt-/Security-Scope

Erneut abgeglichen wurden die früheren Prozess-, Recovery-, Descendant-, Token-Provenienz-, Handle-Cleanup-, Rollback-, Ownership/Auth-, Hardware-Konvergenz-, Durable-Store-, Frontend-/Polling- und Accessibility-Befundklassen. Außer den oben genannten Punkten ergab die statische Rückverfolgung keinen weiteren P0–P3-Befund.

### Freeze-v16-Bindung

Start und reservierte Endbindung stimmen überein:

- Branch: `operator-workbench-phase1`
- HEAD: `3271ff9366ab3fecb2a158913a0cc19ed6a06726`
- Manifest-SHA-256: `211449e60904aa4ee8a6d84846fcecbd9a77ab770777765ade9278cdaa6a8782`
- Einzelhashes: **101/101 OK**
- Exaktes Hashzeilen-Aggregat: `5b2b1d42152043ac0c33c310786121dc3944ad945ef35427d6ff5ebdae64c2f4`
- Exakte Population: **102**
- Scope minus Dirty: `0`
- Dirty minus Scope plus Manifest: `0`
- End-Status-Fingerprint: `eb9ce960dac8e2e4acc856618ac4cb15121bf83172ac3be44e46266a0d1fccbe`
- Drift: **keine**

**Dateien erstellt oder verändert:** keine.  
**Ausführung:** keine Tests, Projektimporte oder Produktprozesse.
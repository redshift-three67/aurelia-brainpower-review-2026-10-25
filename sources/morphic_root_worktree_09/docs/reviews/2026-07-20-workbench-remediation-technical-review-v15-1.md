# **REQUEST CHANGES**

**Konfidenz:** hoch  
**Befundzählung:** `P0=0, P1=1, P2=0, P3=0`  
**Scope-Drift:** `0`

## P1 – Nicht-Exit-Fehler der post-open Supervisor-Identitätsprüfung werden als Exit/Mismatch verschluckt

| Priorität | Befund | Evidenz |
|---|---|---|
| P1 | Nach erfolgreichem `pidfd_open()` unterscheidet die Supervisor-Revalidierung bei der Creation-Time-Prüfung nicht zwischen einem echten Identitätsmismatch/Exit und einem nichtlokalen Fehler. `_process_create_time()` fängt pauschal `psutil.Error` und `OSError` und gibt `None` zurück; `_process_identity_matches()` macht daraus `False`. Damit erreichen etwa `psutil.AccessDenied` oder `OSError(EACCES/EPERM/EIO)` nicht die `except`-Klauseln in `_signal_posix_authority()`. Der Supervisor wird wie verschwunden/ungültig behandelt, statt vor jeder Signalisierung `ProcessAuthorityAmbiguousError` auszulösen und über `stop()` dauerhaft `authority_ambiguous` zu persistieren. | `apps/web/scan_jobs.py:266-277`, `apps/web/scan_jobs.py:533-551`, Persistenzgrenze `apps/web/scan_jobs.py:966-971` |

Das kann anschließend:

- tokengebundene Nachfahren trotz ungeklärter Supervisor-Identität signalisieren; oder
- bei leerer Enumeration als roher `RuntimeError("no stable POSIX process authority was found")` enden, ohne den geforderten dauerhaften Ambiguitätszustand zu setzen.

Der vorhandene post-open-Nicht-Exit-Test deckt nur `os.getpgid()` mit `EACCES` ab und monkeypatcht `_process_identity_matches()` ausdrücklich auf `True`; die fehlerhafte Creation-Time-Grenze bleibt daher ungetestet (`tests/test_web_scan_jobs.py:742-773`).

**Erforderliche Korrektur:** Post-open Creation-Time-Revalidierung muss eine tri-state-/exception-erhaltende Grenze verwenden:

1. bestätigter Exit (`ProcessLookupError`, `psutil.NoSuchProcess`, `OSError(ESRCH)`) → Supervisor-Handle exakt einmal schließen, Nachfahren weiter enumerieren;
2. bestätigter Identitätsmismatch → keine Supervisor-Autorität übernehmen;
3. jeder andere normale Fehler → `ProcessAuthorityAmbiguousError` vor jedem Signal; `stop()` persistiert `authority_ambiguous`.

Ein adversarialer Test muss nach erfolgreichem Supervisor-Open mindestens `psutil.AccessDenied` und einen Nicht-`ESRCH`-`OSError` aus der Creation-Time-Ermittlung injizieren und **kein Signal**, **exakt einmaliges Handle-Close** sowie den langlebig persistierten Zustand nachweisen.

## Weitere Prüfergebnisse

- Kandidaten- und Supervisor-pidfd-Erwerb klassifizieren generische normale `Exception` korrekt als `ProcessAuthorityAmbiguousError`; bestätigte `ProcessLookupError`/`ESRCH` bleiben lokale Exit-Races.
- Post-open `getpgid()` behandelt Exit/ESRCH und Nicht-Exit korrekt; Handles werden im geprüften Ablauf exakt einmal geschlossen.
- Der Startfehler bleibt im `BaseExceptionGroup` an erster Stelle und behält seinen realen ursprünglichen Traceback. Reine `Exception`-Elemente werden durch Python korrekt zu `ExceptionGroup` spezialisiert; direkte `BaseException`-Elemente bleiben im `BaseExceptionGroup`.
- Die v9–v14-Befundklassen sowie Auth/Authz, Session/Secrets, Ownership/Tenant-Bindung, Rate Limits, Durable Stores, „Neuer Fall“, Windows-Prozessbaum, Hardware-Konvergenz, Poll-Single-Flight und Accessibility wurden statisch rückverfolgt. Außer dem oben beschriebenen Restfehler ergab sich kein weiterer P0–P3-Befund.

## Freeze-v15-Bindung

Start und Ende waren identisch:

- Branch: `operator-workbench-phase1`
- HEAD: `3271ff9366ab3fecb2a158913a0cc19ed6a06726`
- Manifest-SHA-256: `de20792835dd7e68a7ef18e4aaf0cd3e76815f29dc950ab947bef751f6a009a6`
- Einzelhashes: `97/97 OK`
- Kanonisches Aggregat: `f39ec0f9c5522b194160c4b2ead5aacf20a5601d23fdc9231c9f9ccaf176d853`
- Exakte Population: `98`
- Scope minus Dirty: leer
- Dirty minus Scope: leer
- Status-Fingerprint Start/End: `a0e95cf1b753e3dbc2a10ca893aac920733eb900b668d06b0ae167e223361caf`
- Drift: **keine**

**Dateien erstellt oder verändert:** keine.  
**Ausführung:** keine Tests, Projekt-Imports, Server, Netzwerkzugriffe oder Installationen.  
**Hinweis:** Der erste Start-Parser berücksichtigte die 13 Kommentarzeilen des Manifests nicht korrekt. Die vollständige korrigierte Startbindung wurde unmittelbar wiederholt und ergab die oben dokumentierten stabilen Werte.
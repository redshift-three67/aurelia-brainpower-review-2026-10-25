# APPROVE

**Konfidenz:** HOCH  
**Befundzählung:** `P0=0, P1=0, P2=0, P3=0`  
**Scope-Drift:** `0`

## Prüfergebnis

- **PGID-/pidfd-Autorität:** Fremde Prozesse werden vor `pidfd_open()` anhand der vorläufigen PGID ausgeschlossen. Zielkandidaten werden nach Handle-Erwerb erneut auf PGID, Supervisoridentität und Token-Provenienz geprüft; die vorläufige numerische PID-Entscheidung wird nicht als Autorisierung übernommen (`apps/web/scan_jobs.py:429-506`).
- **Supervisor-Exit-Race:** `ProcessLookupError` und `OSError(ESRCH)` beim Supervisor-pidfd-Erwerb führen korrekt zur Enumeration tokengebundener Nachfahren. Andere Erwerbsfehler werden fail-closed als `ProcessAuthorityAmbiguousError` behandelt und im Stop-Pfad dauerhaft als `authority_ambiguous` gespeichert (`apps/web/scan_jobs.py:509-564`, `apps/web/scan_jobs.py:885-940`).
- **Handle-Cleanup:** Aktuelle, übertragene, Supervisor- und Consumer-Handles werden jeweils vollständig abgearbeitet. Cleanup erfasst `BaseException`, isoliert einzelne Close-Fehler, erhält aktive Originalausnahmen und schließt keinen erfolgreich übertragenen Handle doppelt (`apps/web/scan_jobs.py:419-426`, `apps/web/scan_jobs.py:437-506`, `apps/web/scan_jobs.py:509-564`).
- **Adversariale Abdeckung:** Fremd-PGID-Filterung vor Open, Supervisor-Exit beim Open, erster Close-Fehler sowie vorhandene Provenienz-, Ambiguitäts- und Re-Enumerationsverträge sind abgedeckt (`tests/test_web_scan_jobs.py:367-597`, weitere Prozessautoritätsfälle ab `tests/test_web_scan_jobs.py:623`).
- **Regressionen v9–v12:** Die früheren Befunde sind geschlossen. Bei der erneuten statischen Verfolgung von Auth/Authz, Sessions/Secrets, Ownership/Tenant-/Report-Bindung, Rate Limits, Durable Stores, „Neuer Fall“, Windows-Prozessbaum, Hardware-Konvergenz, Poll-Single-Flight und Accessibility ergaben sich keine weiteren P0–P3-Befunde.

## Freeze-v13-Bindung

Start- und reservierte Endbindung stimmen überein:

- Branch: `operator-workbench-phase1`
- HEAD: `3271ff9366ab3fecb2a158913a0cc19ed6a06726`
- Manifest-SHA-256: `34ffd894bc392c6edfa83660ae2652eafb64d1b7fec85b520c60e380a832e9fa`
- Einträge: `89`
- Einzelhashes: `89/89 OK`
- Aggregat: `eeae5c32adeccca03a58e5eb5f8bfa2fe994b89d629f9adfb87269ad1d333c77`
- Exakte Population: `90/90`
- Dirty minus Scope: leer
- Scope minus Dirty: leer
- End-Status-Fingerprint: `74f86bd5aaa9e036c6865a480eb03742c042474f23f697606790ec585ebe8989`
- Drift: **keine**

**Dateien erstellt oder verändert:** keine.  
**Tests/Imports/Server/Netzwerk/Installationen:** gemäß strikt read-only gesetztem Review-Scope nicht ausgeführt.  
**Probleme:** keine.
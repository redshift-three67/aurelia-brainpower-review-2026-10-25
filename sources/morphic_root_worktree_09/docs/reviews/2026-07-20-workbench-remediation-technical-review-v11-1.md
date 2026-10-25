# REQUEST CHANGES

**Konfidenz:** HOCH  
**Befundzählung:** `P0=0, P1=2, P2=0, P3=0`

## Befunde

| Priorität | Befund | Ort |
|---|---|---|
| P1 | Globale `AccessDenied`-Ambiguität ist für Recovery und Snapshot weiterhin reihenfolgeabhängig: Ein zuerst gefundenes, tokenvalides Mitglied führt zum sofortigen `True`, ohne spätere unlesbare Mitglieder derselben Ziel-PGID zu prüfen. | `apps/web/scan_jobs.py:292-311`, `apps/web/scan_jobs.py:652-661`, `apps/web/scan_jobs.py:801-808`, `apps/web/scan_jobs.py:847-855` |
| P1 | Bei einer Ambiguitätsausnahme schließt `_token_process_pidfds()` bereits gesammelte pidfds nicht. Gemischte Gruppen können dadurch pro fehlgeschlagenem Stop-/Rollback-Versuch Deskriptoren verlieren. | `apps/web/scan_jobs.py:405-437`; unzureichende Tests: `tests/test_web_scan_jobs.py:367-385`, `tests/test_web_scan_jobs.py:428-465` |

## Details

### P1 — Snapshot und Recovery übersehen spätere unlesbare Gruppenmitglieder

`_process_group_alive()` beendet die Enumeration beim ersten passenden Token:

```python
if token == process_group_token:
    return True
```

Bei der Reihenfolge „gültiges Mitglied, danach Zielgruppenmitglied mit `AccessDenied`“ wird das zweite Mitglied nie geprüft. Daraus folgen:

- `_recover_jobs()` übernimmt den Job als aktiv statt `authority_ambiguous`.
- `_snapshot()` veröffentlicht `running` statt `authority_ambiguous`.
- `stop()` erreicht zwar anschließend die vollständige pidfd-Enumeration, deren Ambiguitätsausnahme liegt aber außerhalb des Catch-Blocks `apps/web/scan_jobs.py:801-808`; daher wird `authority_ambiguous` nicht zuverlässig persistiert.
- Die Signalrunde selbst sendet in diesem Fall dank vollständiger `_token_process_pidfds()`-Enumeration noch kein Signal. Der geforderte globale Zustandsvertrag für Recovery/Snapshot/Stop ist dennoch nicht erfüllt.

**Erforderliche Korrektur:** Die gesamte Zielgruppe enumerieren, ein `found_valid`-Flag sammeln und erst nach vollständiger, nicht ambiger Enumeration zurückgeben. Jedes unlesbare Zielgruppenmitglied muss unabhängig von der Iterationsreihenfolge gewinnen. Mixed-Population-Tests müssen beide Reihenfolgen über Recovery, Snapshot und produktiven `stop()` abdecken.

### P1 — pidfd-Leak beim globalen Ambiguitätsabbruch

`_token_process_pidfds()` überträgt validierte Deskriptoren in `handles`. Wird bei einem späteren Mitglied `ProcessAuthorityAmbiguousError` ausgelöst, schließt `finally` nur den Deskriptor des aktuell geprüften Prozesses. Die zuvor in `handles` abgelegten pidfds verlassen die Funktion per Exception und bleiben offen.

Der Test `test_target_group_access_denied_aborts_entire_signal_round` beweist zwar `sent == []`, prüft aber die Deskriptorschließung nicht. Der separate Closure-Test enthält nur ein einziges sofort unlesbares Mitglied und kann den Leak daher nicht erkennen.

**Erforderliche Korrektur:** Bei jeder Ausnahme vor erfolgreicher Rückgabe sämtliche bereits gesammelten Handles schließen; idealerweise die Enumeration in einen äußeren `try/except` mit zentralem Cleanup legen. Testfall: gültiges Mitglied vor `AccessDenied`, anschließend exakt alle geöffneten pidfds als geschlossen nachweisen.

## Vorbefunde und weitere Grenzen

- **v9 Token in `argv`, produktive Gate-Umgebung, owner-only State, API-Ausschluss:** geschlossen.
- **v9 finales `killpg()`-TOCTOU:** geschlossen; produktiv wird pidfd-basiert signalisiert.
- **v9 Poll-Single-Flight:** geschlossen.
- **v10 pidfd-`ESRCH`:** pro Handle korrekt als konvergiert behandelt; spätere Handles werden weiter bearbeitet.
- **v10 sonstige Sendefehler:** alle Handles werden abgearbeitet, danach wird fail-closed ausgelöst.
- **v10 bounded TERM/KILL und Forks:** begrenzte KILL-Re-Enumeration und Timeout sind vorhanden; Fork-zwischen-Runden-Test vorhanden.
- **Reviewer-2 Delayed-Start/New-Case:** Gegenbehauptung bestätigt. `workbench-api.js:16-22` erhöht `pendingMutations` vor dem ersten `await`; `app.js:856-861` blockiert den Reset. Der neue Browservertrag `tests/browser/workbench.spec.js:202-248` erhält Generation und spätere Job-ID.
- Auth/Authz, Session/Secrets, Owner-/Tenant-/Reportbindung, Rate-Limit-Klassen, Durable Stores, New Case, Windows-Pfad, Hardware-Konvergenz, Polling und Accessibility wurden transitive statisch nachverfolgt; keine zusätzlichen P0–P3-Befunde.

## Freeze-/Driftbindung

Start und reservierte Endbindung stimmen überein:

- Branch: `operator-workbench-phase1`
- HEAD: `3271ff9366ab3fecb2a158913a0cc19ed6a06726`
- Manifest-SHA-256: `2a089645bcc6e6265e013b48f13f31181e65c7cc09191184a5a81d8320e9427a`
- Manifest-Einträge: `81`
- Einzelhashes: `81/81 OK`
- Aggregat: `802b19686a013a37e4e51e9a535579cd7d9e4b0253353a6947edec3c1d2c4f9d`
- Dirty-Population: `82`
- Dirty minus Scope+Manifest: leer
- Scope minus Dirty: leer
- End-Status-Fingerprint, `git status --porcelain=v1 -z`: `448af991734cfdee2d76fd87091df4805027f1428076cc49a9aaeaf0e4077a86`
- Drift: **keine**

**Dateien erstellt oder verändert:** keine.  
**Tests/Imports/Server/Netzwerk/Installationen:** entsprechend der Vorgabe nicht ausgeführt.  
**Problem:** Ein erster Start-Parserlauf hatte einen harmlosen Quotingfehler; die vollständige Prüfung wurde unmittelbar erfolgreich wiederholt.
## Zweitreview Freeze v19

**Verdikt:** **REQUEST CHANGES**  
**Konfidenz:** Hoch  
**Befunde:** **P0=0, P1=1, P2=0, P3=0**

### P1 — POSIX-Test verwendet weiterhin ein numerisches Cleanup-Signal

**Fundstelle:** `tests/test_web_scan_jobs.py:1627,1637`

Der Test speichert zuerst die numerische Supervisor-PID und ruft später:

```python
service._jobs[job_id].process.kill()
```

auf. Auf POSIX implementiert `subprocess.Popen.kill()` die Signalisierung anhand der PID (`SIGKILL`); ein `Popen`-Objekt ist dort kein stabiler Kernel-Prozesshandle. Endet der Supervisor zwischen letzter Zustandsbeobachtung und `kill()`, kann PID-Wiederverwendung theoretisch einen fremden Prozess treffen. Damit ist die v19-Aussage „all numeric test cleanup was removed“ adversarial nicht haltbar.

Dieselbe grundsätzliche Race-Klasse besteht im produktiven Fehlerpfad `apps/web/scan_jobs.py:1072-1075`: Wenn die Creation-Time-Ermittlung fehlschlägt, folgt auf POSIX unmittelbar `process.kill()` statt pidfd-/Token-Autorität.

**Erforderliche Korrektur:** Auch diese Pfade über stabile Autorität führen—POSIX über vorab erworbenes pidfd bzw. die bestehende Token/pidfd-Grenze; Windows weiterhin über Job-/Prozesshandle. Der Recovery-Test sollte den Supervisor ohne PID-basierte Signalisierung beenden.

### Verifizierte Punkte

- Windows-Recovery, Job-Open/Query/Terminate, Creation-Time-Mismatch, Ambiguitätsstatus und Handle-Cleanup geprüft.
- POSIX-Token-/pidfd-Erfassung, Revalidierung, gemischte Population, PID-Wiederverwendung und Signalgrenze geprüft.
- Relevante exakte Tests sowie dokumentierter früherer Workbench-Produktscope geprüft.
- Keine Tests, Imports, Netzwerkzugriffe oder Änderungen ausgeführt.
- Freeze-Bindung am Anfang und Ende:
  - Branch: `operator-workbench-phase1`
  - HEAD: `3271ff9366ab3fecb2a158913a0cc19ed6a06726`
  - Manifest: `068a6c3ccb07271dce21967661d1814accac02b708f3ca101ad8206aba3ba8bc`
  - **113/113 Hashes PASS**
  - Aggregate: `0a0a6dcada4ade826fdbd553f318787d01828b7bbe5ff110d6f4b8412773e636`
  - Population: **113 Manifestdateien + Freeze = 114**
  - **Zero drift**
- Dateien erstellt/geändert: **keine**.
## Freeze-v20-Review

**Verdikt: REQUEST CHANGES**  
**Konfidenz: HOCH**  
**Zählung: P0=0 · P1=1 · P2=3 · P3=0**

### Befunde

| Priorität | Befund | Ort |
|---|---|---|
| **P1** | `/api/privacy/clients` umgeht die konfigurierte API-Key-/Session-Authentifizierung. Anders als Reports, Scan- und Harmonisierungsendpunkte besitzt der personenbezogene Client-Index kein `Depends(verify_api_key)`. Bei gesetztem `MORPHIC_API_KEY` bleibt dieser Endpunkt daher anonym erreichbar. | `apps/web/main.py:549-553` |
| **P2** | Die POSIX-Startup-pidfd-Fehlerpfade besitzen keine vollständige Cleanup-Garantie: Ein Fehler von `pidfd_send_signal()` überspringt Close und Wait; ein Timeout von `process.wait(timeout=35)` kann den unreleased Gate-Prozess unbeaufsichtigt lassen und den Primärfehler verdecken. Entsprechende Signal-/Close-/Wait-Timeout-Injektionstests fehlen. | `apps/web/scan_jobs.py:1109-1141` |
| **P2** | Zwei produktive Signalpfade enthalten weiterhin numerische `SIGKILL`-Fallbacks (`9`). Das widerspricht der geforderten vollständigen Entfernung numerischer Signale; `signal.SIGKILL` ist auf dem hier vorausgesetzten pidfd-POSIX-Pfad bereits verbindlich verfügbar. | `apps/web/scan_jobs.py:838`, `apps/web/scan_jobs.py:1122` |
| **P2** | Der reale Separate-Owner-Prozess-Test belegt den erfolgreichen Windows-Lebensdauerpfad, falsifiziert aber nicht die exakten `DuplicateHandle`-Argumente oder den Retention-Fehlerpfad. Es fehlt ein deterministischer Test für Source Process = aktueller Prozess, Source Handle = Job, Target Process = Gate, `desired_access=0`, `inherit=False`, `DUPLICATE_SAME_ACCESS` sowie geordnetes Cleanup bei Duplicate-/Close-Doppelfehler. | `apps/web/scan_jobs.py:475-512`; `tests/test_web_scan_jobs.py:1346-1375` |

### Adversarielle Ergebnisse

- **DuplicateHandle:** Implementierung verwendet plausibel den aktuellen Prozess als Quelle, den lokalen Job-Handle als Quellhandle und den Gate-Prozess als Ziel; die erfolgreiche separate Prozesswiederherstellung bestätigt die Lebensdauer. Die behauptete vollständige Fehler- und Argumentmatrix ist jedoch nicht testgebunden.
- **POSIX-Autorität:** Stop und Recovery signalisieren über pidfds statt `killpg`; Token-Abweichungen und unlesbare Provenienz führen grundsätzlich fail-closed. Der Token ist eine Bearer-Provenienz innerhalb derselben OS-Account-Vertrauensgrenze, keine Abwehr gegen einen bereits kompromittierten Prozess desselben Kontos.
- **Numerische Signale:** Keine produktiven `killpg(..., Zahl)`- oder `taskkill /PID`-Fallbacks gefunden; verblieben sind die zwei genannten `SIGKILL=9`-Fallbacks.
- **Produkt-/Security-Scope:** Scan- und Harmonisierungsendpunkte sind authentifiziert und owner-/tenant-gebunden. Der Privacy-Client-Index ist die festgestellte Authentifizierungslücke.

### Freeze-Bindung

Start und Ende waren identisch:

- Manifest-SHA-256: `c3fd537a0671861a4fc3378a8baed8f3ab9003cefc10321608f60091272d333d`
- 117/117 Einträge gültig
- Aggregat: `10a5374277197a7f9c5b7e2b4ac6e9c419e7d29c62145a2a70540bfcbebd3087`
- Population: 118/118, bidirektional vollständig
- Branch: `operator-workbench-phase1`
- HEAD: `3271ff9366ab3fecb2a158913a0cc19ed6a06726`
- **Drift: 0**

**Dateien geändert/erstellt:** keine.  
Wegen `P1=1` und `P2=3` ist Freeze v20 nicht freigabefähig.
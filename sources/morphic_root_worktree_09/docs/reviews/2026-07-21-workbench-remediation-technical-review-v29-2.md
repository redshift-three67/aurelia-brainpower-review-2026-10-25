## Freeze-v29-Review 2

**Verdikt:** **REQUEST CHANGES**  
**Konfidenz:** **hoch**

### Severity-Zahlen

| P0 | P1 | P2 | P3 |
|---:|---:|---:|---:|
| 0 | 7 | 0 | 0 |

Die vorgeschriebene Freigabeschwelle `P0=P1=P2=P3=0` ist nicht erfüllt.

### Freeze-Bindung und Drift

- Manifest-SHA: `81cdcf084195b09084d763a76d009ef48f92254384d5412c236037775de15d21`
- Branch: `operator-workbench-phase1`
- HEAD: `3271ff9366ab3fecb2a158913a0cc19ed6a06726`
- Hashzeilen: **171**, alle erfolgreich verifiziert
- Hashzeilen-Aggregat: `6544a9f2c4267ff03cec3615a61769d8c45d771c864354d2f952c0b5b36c0ad6`
- Population einschließlich Manifest: **172**
- Status-Fingerprint-Rezept reproduziert als  
  `git status --porcelain=v1 --untracked-files=all | sha256sum`
- Fingerprint: `590cae645371305f2aad6db5363455cc31fd7235c18c7ffb4302d2317c68f2f2`
- Bidirektionale Scope-Differenz: leer
- Start-/End-Drift: **0**

## Findings

### P1 — EMF-Generation kann nach Verlust beider Autoritätsdateien ABA-revivieren

**Evidenz:** `apps/web/emf_authority.py:63-93`, insbesondere `:69-81`

Fehlen sowohl Hauptdatei als auch `.generation`-Sidecar, setzt `set_enabled()` die Generation wieder auf `1`. Ein früherer Lease der Generation 1 wird dadurch nach Delete → Re-enable erneut aktuell. Der Sidecar schützt nur gegen isolierten Verlust der Hauptdatei, nicht gegen gemeinsamen Verlust, Restore oder Cleanup beider Dateien.

**Testlücke:** `tests/test_emf_enable_authority.py:29-39` löscht nur die Hauptdatei, während der Generation-Sidecar erhalten bleibt. Der gemeinsame Verlust und kohärentes Restore-Tampering werden nicht geprüft.

---

### P1 — Windows überspringt bei lokal totem Supervisor die weiterhin existente Job-Autorität

**Evidenz:**  
- `apps/web/scan_jobs.py:603-609`
- `apps/web/scan_jobs.py:1000-1005`
- `apps/web/scan_jobs.py:1408-1410`
- `apps/web/scan_jobs.py:1496-1523`

Nach erfolgreichem Start wird der Service-Handle geschlossen. Stirbt danach der lokale `Popen`-Supervisor, liefert `_windows_job_active()` sofort `False`, ohne das tokengebundene Named Job Object erneut zu öffnen. Produktive Nachfahren können weiterhin dem Job angehören. Rollback kann dadurch vollständig ausfallen und Polling einen falschen Terminalstatus publizieren.

Der Sonderfall `_RecoveredProcess` verhindert diesen Shortcut erst nach Service-Neustart; er schützt nicht das laufende Serviceobjekt im Fenster Supervisor-dead/descendant-live.

**Testlücke:** Die Tests mocken `_windows_job_active()` oder prüfen Recovery, aber kein produktionsnahes lokales `Popen`-Objekt mit beendetem Supervisor und noch aktivem Named-Job-Nachfahren.

---

### P1 — POSIX-State ohne Provenienz-Token wird als inaktiv statt mehrdeutig behandelt

**Evidenz:**  
- `apps/web/scan_jobs.py:306-308`
- `apps/web/scan_jobs.py:355-361`
- `apps/web/scan_jobs.py:1154-1213`

`_process_group_alive()` gibt bei fehlendem `process_group_token` direkt `False` zurück. Recovery akzeptiert den Token dagegen über `payload.get(...)`, ohne sein Vorhandensein zu verlangen. Ist der Supervisor bereits beendet, kann ein beschädigter oder teilrestaurierter State deshalb als `failed` klassifiziert werden, obwohl nicht mehr bewiesen werden kann, ob tokengebundene Nachfahren weiterlaufen.

Das kann die globale Ressource freigeben, statt `authority_ambiguous` zu persistieren.

**Testlücke:** Umfangreiche Tests existieren für gemischte Tokenpopulationen und `AccessDenied`, nicht jedoch für einen syntaktisch ansonsten gültigen Recovery-State mit fehlendem Token und supervisorlosen Nachfahren.

---

### P1 — POSIX-KILL-Runden enden beim ersten generischen Signalfehler vorzeitig

**Evidenz:** `apps/web/scan_jobs.py:938-997`, insbesondere `:967-980`

Ein generischer Fehler in der ersten `SIGKILL`-Runde führt über `break` zum Abbruch aller weiteren erlaubten KILL-Runden. Die finale Aktivitätsprüfung verhindert zwar einen falschen Erfolgsstatus, aber die gemeinsame Stop-/Rollback-Konvergenz versucht nicht mehr alle bounded Cleanup-Möglichkeiten. Temporäre Sendefehler oder kombinierte Signal-/Closefehler können damit unnötig produktive Nachfahren zurücklassen.

**Testlücke:** Es gibt Fehlergruppierungsprüfungen für Signal- und Closefehler, aber keinen Nachweis, dass ein erster generischer KILL-Fehler akkumuliert und in einer späteren Runde erneut versucht wird.

---

### P1 — HTTP-Authentifizierung wird vor geschützter Response-/Dateiübertragung nicht erneut validiert

**Evidenz:**  
- Einmalige Dependency-Prüfung: `apps/web/security.py:111-136`
- PII-/Report-Oberflächen: `apps/web/main.py:596-636`
- Job-/Harmonisierungsantworten: `apps/web/main.py:638-718`
- Kein abschließendes Auth-Gate in den HTTP-Middlewares: `apps/web/main.py:414-485`

Abgesehen von EMF-Profil und Workbench-Hardware wird Auth nur beim Eintritt in den Handler geprüft. Widerruf oder Key-Rotation während Store-Zugriff, Stop/Start oder Report-Aufbereitung verhindert die anschließende Response nicht. Bei `FileResponse` liegt die eigentliche Übertragung sogar nach Rückgabe des Handlerobjekts; ein bereits widerrufener Client kann den Dateistream weiter erhalten.

**Testlücke:** Die Tests prüfen autorisiert versus nicht autorisiert vor Request-Beginn. Es fehlt Widerruf/Rotation aus dem produktiven Read bzw. unmittelbar vor ASGI-Response-Start und während eines Datei-Streams.

---

### P1 — Basic-Credentials werden in Diagnosen nur teilweise redigiert

**Evidenz:**  
- Regex: `apps/web/scan_diagnostics.py:12-17`
- Anwendung: `apps/web/scan_diagnostics.py:58-65`
- Vakuöser Test: `tests/test_web_scan_diagnostics.py:50-67`

Die Authorization-Regex behandelt optional nur `Bearer`. Bei

```text
Authorization: Basic dXNlcjpwYXNz
```

wird lediglich `Authorization: Basic` ersetzt; der Base64-Credentialwert nach dem Leerzeichen bleibt erhalten.

Der Test liefert bereits `Authorization: Bearer ***` und behauptet anschließend, `top-secret-token` sei nicht enthalten, obwohl dieser Wert nie in der Fixture vorkommt. Damit beweist er keine Credential-Redaktion.

---

### P1 — Malformed/non-string Ownership reserviert die globale Harmonisierung nicht

**Evidenz:**  
- Keine Laufzeit-Typvalidierung beim Laden: `services/harmonization_worker.py:150-153`
- Reservation: `services/harmonization_worker.py:762-786`

Die Vollständigkeitsprüfung stringifiziert Ownerwerte:

```python
str(existing.tenant_id or "").strip()
```

Der anschließende Identitätsvergleich benutzt dagegen die unveränderten Werte. Beispielsweise wird ein numerischer `tenant_id` als „vollständig“ behandelt, stimmt aber nicht mit dem angeforderten String überein. Der Dataclass-Loader erzwingt die annotierten Stringtypen nicht. Ein beschädigter oder Legacy-Datensatz kann daher aktiv bleiben, ohne global zu blockieren und ohne als gleicher Owner erkannt zu werden.

**Testlücke:** `tests/test_harmonization_worker_recovery.py:155-184` deckt Whitespace ab, nicht `int`, Container oder andere malformed non-string Ownerwerte.

## Coverage-Grenzen

- Strikt statische, read-only Prüfung; keine Tests, Imports, Dienste, Netzwerkaufrufe oder produktiven Prozesse ausgeführt.
- Statisch geprüft wurden insbesondere EMF-Leases und Call-Sites, HTTP-/WebSocket-Revalidierung, Harmonisierung und Hardware-Child-Cleanup, Windows Named Jobs, POSIX pidfds/Signal-/Closepfade, terminales Repolling, Ownership-Reservation sowie Diagnose-Redaktion.
- Vorhandene Testergebnisse im Manifest wurden nicht erneut ausgeführt oder unabhängig bestätigt; Tests wurden ausschließlich als Quelltext bewertet.
- Keine Dateien erstellt oder verändert; keine Repo-Artefakte erzeugt.
- Keine Tool- oder Zugriffsprobleme aufgetreten.
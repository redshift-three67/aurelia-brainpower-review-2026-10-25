## Freeze-v26 – unabhängiges technisches Review

**Verdikt: REQUEST CHANGES**  
**Konfidenz: HOCH**  
**Schweregrade: `P0=0 · P1=3 · P2=0 · P3=0`**  
**Drift: `0`**

Die Freigabeschwelle `P0=P1=P2=P3=0` ist trotz vollständig driftfreier Freeze-Bindung nicht erfüllt.

### Befunde

| Prio | Befund | Evidenz |
|---|---|---|
| **P1** | **Die EMF-Aktivierung ist nicht für alle produktiven Messpfade autoritativ.** Die HTTP-/Workbench-/EMF-WebSocket-Pfade prüfen `_emf_active`, aber der Harmonisierungs-Worker ruft `measure_realtime_emf_profile()` über `capture_realtime_context()` beim ersten und danach jedem zehnten Zyklus unabhängig von `/api/emf/enable` auf. Eine Harmonisierung kann daher bei deaktivierter EMF-Telemetrie Messungen durchführen und persistieren. | `apps/web/emf.py:18,30-56,106-119`; `services/harmonization_worker.py:321-328,343-348,638-640` |
| **P1** | **Harmonisierungs-Stop bestätigt nur den Worker, nicht dessen vollständigen Prozessbaum.** Hardware-Modulation startet separate nicht-dämonische CPU/GPU/RAM/WebSocket-Prozesse. Der Stop-Pfad terminiert lokal ausschließlich das `multiprocessing.Process`-Objekt des Workers beziehungsweise nach Neustart ausschließlich dessen PID. Bei erzwungenem Worker-Abbruch läuft dessen `finally` zur Kindkonvergenz nicht zuverlässig; es gibt weder ein POSIX-Prozessgruppen-/pidfd-Modell noch ein Windows-Job-Object für Worker und Nachkommen. Trotzdem wird anschließend `stopped` publiziert. | `services/hardware_modulation.py:342-365,422-423`; `services/harmonization_worker.py:801-842,845-873` |
| **P1** | **Die Harmonisierungs-Recovery unterscheidet „beendet“ nicht von „Autorität nicht lesbar“.** `_process_identity_matches()` wandelt alle `psutil.Error`/`OSError` – einschließlich `AccessDenied` – in `False` um. Bei abgelaufener Lease wird ein möglicherweise noch laufender Worker dadurch als `interrupted` publiziert; beim nächsten Start fällt er aus der aktiven Owner-Menge und eine zweite Harmonisierung kann für denselben Owner gestartet werden. Anders als der Scan-Pfad persistiert Harmonisierung keinen ambivalenten Autoritätszustand. | `services/harmonization_worker.py:886-893,896-916,738-746` |

### Authentifizierungs- und Ownership-Matrix

| Oberfläche | Authentifizierung | Ownership | Ergebnis |
|---|---|---|---|
| HTTP-Diagnostik einschließlich `/api/status`, Health, Hardware, Sources, Privacy | dynamisches `verify_api_key`; No-Key-Lokalmodus | soweit ressourcenlos nicht anwendbar | geschlossen |
| Browser-Session | an SHA-256-Generation des aktuell konfigurierten API-Keys gebunden | – | Rotation und Prozessneustart widerrufen bestehende Sessions |
| No-Key → konfigurierter Key | HTTP prüft pro Request; beide WebSockets prüfen vor jedem Zugriff/Frame erneut | – | fail-closed |
| EMF-WebSocket | vor `accept()`, vor Aktivierung/Messung und vor jedem Frame | keine Job-Ressource | geschlossen |
| Scan-WebSocket | Auth vor Store-Zugriff; strikter Owner vor `accept()` und erneut vor jedem Frame | `None`, leer, Whitespace und fremd fail-closed | geschlossen |
| Scan Status | API-Key/Session | strikter Owner | exakter reduzierter Payload |
| Scan Stop | API-Key/Session | Owner vor Stop-Seiteneffekt | exakter reduzierter Payload |
| Scan Sync-Trace | API-Key/Session | Owner vor Mutation; nur terminal und einmalig | geschlossen |
| Scan Results | API-Key/Session | strikter Owner | nur Artefakte des exakten Jobs und Export-Roots |
| Workbench Run-Trace | API-Key/Session | über zugehörigen Scan-Job | geschlossen |
| Harmonisierung Start | API-Key/Session | persistente Tenant-/Operator-Bindung | geschlossen |
| Harmonisierung Status/Stop | API-Key/Session | exakte Tenant- **und** Operator-Übereinstimmung | fehlend/leer/fremd fail-closed |
| Admin-Katalog | separater kurzlebiger Admin-Token mit Origin-/Host-Bindung | Katalogkontext | geschlossen |

API-Key-Rotation widerruft Browser-Sessions durch den in `SessionAuthority` gespeicherten Key-Hash (`apps/web/security.py:45-69`). Die WebSocket-Prüfung liest den aktuellen Key bei jeder Wiederholungsprüfung (`apps/web/security.py:83-92`).

### Weitere geprüfte Bereiche

- **Generische Fehler/sichere Ressourcen:** Scan-HTTP-Snapshots entfernen Befehl, Owner, Logs und interne Artefaktlisten; Harmonisierungs-Payloads entfernen Tenant/Operator/Worker-PID und maskieren Workerfehler (`apps/web/main.py:241-258`). Hardware-Fallbacks enthalten nur generische Fehlermeldungen (`apps/web/main.py:111-130`; `apps/web/hardware_truth.py:44-62`).
- **Scan-Prozessautorität:** POSIX verwendet pidfds, wiederholte Provenienzprüfung und TERM/KILL-Konvergenz; Windows verwendet tokenabgeleitete benannte Job Objects und bestätigt die Baumbeendigung. Keine zusätzliche Scan-Finding.
- **Single-Flight:** Scan- und Harmonisierungs-Polls teilen je `generation:jobId` eine Promise-Autorität mit Identity-Guard; manuelle und geplante Polls verschmelzen (`apps/web/static/app.js:399-407,697-705`).
- **Recovery/Persistenz:** Scan-Autoritätsambiguität wird persistent und fail-closed abgebildet. Workbench-, Scan- und Harmonisierungszustände verwenden atomare dauerhafte Veröffentlichung.
- **Reset/Datenschutz:** Reset stoppt aktive Serverarbeit vor Generationswechsel, schützt vor konkurrierenden Mutationen und leert Formular-, Consent-, Report-, Trace- und Jobreferenzen (`apps/web/static/app.js:868-1073`).
- **Accessibility:** Stepper-Zuordnungen, roving `tabindex`, Radio-/Radiogroup-Semantik, Tastatursteuerung, Progressbars, Live-Regionen und reduzierte Bewegung sind vorhanden.

### Freeze-Bindung

| Merkmal | Start | Ende |
|---|---:|---:|
| Worktree | `C:/morphic_v1/.worktrees/operator-workbench-phase1` | identisch |
| Branch | `operator-workbench-phase1` | identisch |
| HEAD | `3271ff9366ab3fecb2a158913a0cc19ed6a06726` | identisch |
| Manifest-SHA | `b978a8a028c4e7da65d276cbe350a8d0b2d30b5a00c213afab6fdb0dc632100c` | identisch |
| Manifest-Einträge | 151 | 151 |
| Einzelhash-Abweichungen | 0; `sha256sum -c`: **151 OK** | 0 |
| LF-Hashzeilen-Aggregat | `3c9f0835e7644394a1c4a3d10d470ffce16d7fe7d391586777c29d0d3122140c` | identisch |
| Dirty Population | 152 | 152 |
| Scope/Population-Symmetrie | `152/152`, fehlend 0, zusätzlich 0 | identisch |
| Status-Fingerprint | `4ee27890788a1d8f96cb857f528a7b2710198ff87b1edc42381afde1daa0cd19` | identisch |

### Review-Hygiene

- Strikt statisch und read-only.
- Keine Tests, Imports, Server, Netzwerkzugriffe oder Installationen ausgeführt.
- **Dateien erstellt oder verändert: keine.**
- Die angegebenen Gate-Ergebnisse wurden als Freeze-Metadaten geprüft, aufgrund des Ausführungsverbots jedoch nicht erneut ausgeführt.
# E5.10D – kurzlebiger serverseitiger Activation-Handle-Transport

**Stand:** 2026-07-12
**Branch:** `operator-workbench-phase1`
**Entscheidung:** **E5.10D technisch GO; E5.10 insgesamt weiterhin NO-GO**

## Ergebnis

E5.10D stellt einen isolierten serverseitigen Transport für bereits autorisierte In-Memory-Gruppenkandidaten bereit. Über die zukünftige Workergrenze darf ausschließlich ein zufälliger Handle übertragen werden. Rohidentitäten, pseudonyme Mitglieds-IDs, Raten und Zentroide bleiben innerhalb eines DPAPI-geschützten, kurzlebigen Records.

| Vertrag | Ergebnis |
|---|---:|
| zufälliger kanonischer Handle `gah-<32 hex>` | ✅ |
| TTL explizit ganzzahlig in `[1,300]` Sekunden | ✅ |
| Default-TTL 60 Sekunden | ✅ |
| Ablauf exakt bei `now >= expires_at` | ✅ |
| One-Time-Consume | ✅ |
| konkurrierende Consumer: exakt einer erfolgreich | ✅ |
| Owner-/Workspace-/Tenant-Bindung | ✅ |
| fremder Kontext konsumiert oder löscht nicht | ✅ |
| explizite Löschung mit exakter Handle-Bestätigung | ✅ |
| redigierter Retention-Dry-Run und Purge | ✅ |
| DPAPI-Schutz at rest | ✅ |
| atomarer Write mit Temp-Bereinigung | ✅ |
| manipulierte Records fail-closed | ✅ |
| Pfad- und nichtkanonische Handles fail-closed | ✅ |
| Workerpayload exakt `{activation_handle}` | ✅ |
| zusätzliche Identitäts-/Ratenfelder abgewiesen | ✅ |
| Audit enthält nur Version, Ereignis, Ausgang und Zeit | ✅ |
| kein Handle-Store-Import in produktiven Pfaden | ✅ |

## Zentrale Dateien

- `core/compliance/group_activation_handle_store.py`
- `tests/test_group_activation_handle_store.py`
- `tests/test_group_e510_release_gate.py`

## Sicherheitsgrenzen

Der Handle-Store akzeptiert nur einen bereits autorisierten `GroupAnalysisOptIn`. Beim Issue werden nochmals geprüft:

- `enabled is True`;
- `consent_verified is True`;
- endlicher eindimensionaler Zentroid;
- endliche Stärke in `[0,1]`;
- vollständiger Operator-/Workspace-/Tenant-Kontext.

Der geschützte Record enthält intern den Zentroid und die Kontextbindung. Nach erfolgreichem Consume wird die Datei vor Rückgabe des rekonstruierten In-Memory-Kandidaten gelöscht. Ablauf, explizite Löschung und Retention-Purge entfernen den Record ebenfalls zielgenau.

Der zulässige Workerpayload enthält ausschließlich:

```json
{"activation_handle":"gah-..."}
```

Zusätzliche Felder wie `group_member_rates` oder `subject_id` werden vor dem Consume abgewiesen.

## Bewusst nicht aktiviert

- keine FastAPI-Route zur Handle-Erzeugung;
- keine Einbindung in `apps/web/main.py`;
- kein Feld in `Phase1ScanRequest`;
- keine CLI-Option;
- kein Job-/Worker-Feld;
- keine Report-, Trace- oder Manifestausgabe;
- keine produktive Gruppenwirkung.

Deshalb war für E5.10D keine Browserabnahme erforderlich oder zulässig: Es existiert absichtlich keine UI- oder Webroute. Die reale Browserabnahme gehört zum separaten Produktivgate E5.10E/F.

## Verifikation

| Prüfung | Ergebnis |
|---|---:|
| Activation-Handle-Store isoliert | im erweiterten Fokus grün |
| E5.10D-/Policy-/Consent-/Resolver-/Release-Fokus | `43 passed` |
| Rest-Suite ohne Top-5 | `454 passed, 2 skipped`; sieben bekannte Rate-Limit-429-Ausreißer |
| alle sieben Ausreißer separat/frisch | jeweils `1 passed` |
| Top-5-Smoke | `1 passed in 154.76s` |
| Python-Compile | bestanden |
| JavaScript-Syntax | bestanden |
| `git diff --check` | bestanden; nur bestehende LF→CRLF-Hinweise |

## Freigabegrenze

E5.10D ist technisch abgeschlossen. Damit sind die vorbereitenden Sicherheitsgates A–D vorhanden; die produktive Einbindung ist weiterhin eine separate Entscheidung.

Weiter offen:

1. E5.10E – streng lokal begrenzte Produktivintegration mit vollständiger Rollback-Matrix;
2. E5.10F – Privacy-, Audit-, Browser- und Gesamtfreigabe.

**Finale Entscheidung:** `E5.10A/B/C/D GO`, `E5.10 weiterhin NO-GO`, `Geo separat NO-GO`.

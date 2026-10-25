# Feedback f – F2.4 Audit-Integritätsstufen und HMAC-Receipts

- **Stand:** 2026-07-13
- **Gate:** F2.4
- **Status:** GO
- **F2-Gesamtstatus:** GO
- **Gesamtfeature Feedback f:** NO-GO

## 1. Scope

F2.4 ergänzt ausschließlich reine, offline arbeitende Integritätsverträge:

- ehrliche Klassifizierung der bestehenden ungeschlüsselten DB-Hashkette als `consistency_only`;
- HMAC-SHA-256-signierte Audit-Head-Receipts mit explizit injiziertem Schlüssel;
- bindende Receipt-Metadaten für Tenant, letzte Sequenz, letzten Hash, Policy-Version, Zeitpunkt, Algorithmus und Schlüsselversion;
- versionierte Schlüsselrotation und Verifikation alter Receipts ohne stillen Fallback;
- fail-closed Auswahl für einen späteren Produktions-Adminmodus.

Nicht enthalten sind Store-Migration, produktive Adminmutationen, Runtime-, Web-, CLI-, Engine-, Key-Provider-, Environment-, Datei-, DB- oder Netzwerkverdrahtung. F6 muss später einen geschützten Key-Provider und die tatsächliche Mutationssperre separat anbinden.

## 2. Sicherheitsverträge

| Vertrag | Umsetzung |
|---|---|
| Ehrliche Stufe | Bestehende SHA-256-DB-Kette heißt `consistency_only`; `tamper_resistant=False`. |
| Signatur | HMAC-SHA-256 über deterministisches kanonisches JSON. |
| Feldbindung | Tenant, Sequenz, Head-Hash, Policy, UTC-Zeitpunkt, Algorithmus und Key-Version sind signiert. |
| Vergleich | Signaturen werden mit `hmac.compare_digest()` verglichen. |
| Schlüsselinjektion | Ausschließlich explizite `bytes`; keine Environment- oder Provider-Lookups. |
| Mindeststärke | Schlüssel müssen mindestens 32 Byte lang sein. |
| Fehlkonfiguration | Fehlende, leere, zu kurze und typfalsche Schlüssel scheitern geschlossen. |
| Rotation | Verifikation wählt ausschließlich die im Receipt deklarierte Key-Version; kein Fallback auf andere Schlüssel. |
| Secretfreiheit | Receipt enthält nur Key-Version, Algorithmus und Signatur; niemals den geheimen Schlüssel. |
| Produktionsgrenze | `production_mode=True` ohne gültigen HMAC-Schlüssel scheitert statt auf `consistency_only` zurückzufallen. |
| Reiner Offline-Baustein | Kein I/O, keine Persistenz und keine produktiven Aufrufer. |

## 3. TDD- und Review-Evidenz

### Initiales RED

```text
ModuleNotFoundError: No module named 'core.admin_catalog.audit_integrity'
```

### Finales GREEN

```text
F2.4-Fokus:          33 passed (-W error)
Admin-Catalog-Matrix: 182 passed, 2 skipped (-W error)
py_compile:           PASS
Top-5-Smoke:          1 passed in 107.42s
```

Die F2.4-Tests verwenden ausschließlich synthetische Schlüssel. Der unabhängige HMAC-SHA-256-Known-Answer-Vektor lautet:

```text
7300ef66659bbdc7bd404d61943fb3e71bad9cc4a53b6de105b90728810d602c
```

## 4. Breite Regression

```text
Gesamtsuite ohne Top-5: 662 passed, 4 skipped, 14 failed
Baseline ohne Admin-Catalog-Dateien: 480 passed, 2 skipped, 14 failed
Differenz: 182 neue grüne Admin-Catalog-Tests und 2 zusätzliche plattformabhängige Skips
```

Die 14 Fehler sind baseline-identisch:

- 13 bekannte prozessweite HTTP-429-/Rate-Limiter-Ausreißer;
- 1 zeitabhängig abgelaufene feste Consent-Fixture.

Keine Fehlerklasse stammt aus F2.4.

## 5. Unabhängiger Current-Snapshot-Review

Maßgeblicher hashgebundener finaler Re-Review:

```text
Delegation: deleg_8ddc03f8
Verdikt: APPROVE
Konfidenz: HOCH
Offene P0–P3: keine
```

Verifizierte Snapshot-Hashes:

```text
core/admin_catalog/audit_integrity.py
  db2dc01e9375264075f0e614e944ed886cf73fb9b995c9f5ae15cdee2a23334c
tests/test_admin_catalog_audit_integrity.py
  cfd88963eab154debe4e7fe141f344ac9dc6c6c221f0d79bb9b9ce875a2f9a59
```

Der vorherige Zwischenreview erteilte bereits APPROVE ohne P0–P2; seine drei P3-Testlücken wurden vor dem finalen Review vollständig geschlossen.

## 6. Nichtmutation

```text
data/remedies.db
c67d4e899dab9547a2171ec0d5604d9628721b6757a87d33ef8d34f0c0dadfa0
```

- Ports 8000 und 8090 blieben belegt und wurden nicht verändert.
- Auf Port 8090 waren weiterhin die bereits beobachteten PIDs 18240 und 9056 sichtbar; keiner wurde durch F2.4 gestartet oder beendet.
- Keine Runtime-, Web-, CLI-, Engine-, Store-, Key-Provider- oder Netzwerkverdrahtung.
- Keine Secrets in DB, Logs, Reports oder Receipts.
- Kein Commit, Push, Staging, Reset oder Clean.

## 7. Gateentscheidung

**GO.** F2.4 erfüllt die expliziten Audit-Integritäts- und HMAC-Receipt-Verträge im finalen hashgebundenen Snapshot ohne offene P0–P3.

Damit ist F2 vollständig GO. Feedback f bleibt als Gesamtfeature bis F8 NO-GO. Als nächster zulässiger Block folgt F3.1 – bestehende Legacy-Profile read-only, deterministisch und ohne Runtimewirkung normalisieren.
